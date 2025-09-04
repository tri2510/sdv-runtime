#!/usr/bin/env python3
"""
Replacement for cpp_debugger_util.py using direct memory inspection.
High-performance, no GDB overhead, works with pure C++ projects.
"""

import os
import subprocess
import asyncio
import time
from pathlib import Path
from memory_monitor import ProcessMemoryMonitor, SmartVariableDetector
from ptrace_memory_reader import MemoryVariableMonitor
from auto_variable_detector import AutoVariableDetector, SmartMemoryReader

# Import CLIENT_ID from syncer context
CLIENT_ID = "RunTime-TriCPP"

APP_DIR = Path(os.path.dirname(__file__)) / 'app'
BINARY_FILE = APP_DIR / 'main_bin'

# Global monitor instance
monitor = None
ptrace_monitor = None

async def compile_cpp():
    """Compile C++ project with debug symbols - supports CMake, Makefile, and direct G++ builds."""
    if not APP_DIR.exists():
        return False, 'App directory not found.'

    # Check for CMakeLists.txt first (CMake project)
    cmake_file = APP_DIR / 'CMakeLists.txt'
    if cmake_file.exists():
        print(f"📦 Detected CMake project, using CMake build system", flush=True)
        return await compile_with_cmake()
    
    # Check for Makefile (Makefile project)
    makefile = APP_DIR / 'Makefile'
    if makefile.exists():
        print(f"📦 Detected Makefile project, using Make build system", flush=True)
        return await compile_with_makefile()
    
    # Fallback to direct G++ compilation
    print(f"🔨 Using direct G++ compilation", flush=True)
    return await compile_with_gcc()

async def compile_with_cmake():
    """Compile C++ project using CMake build system."""
    build_dir = APP_DIR / 'build'
    
    # Clean and recreate build directory to avoid cache conflicts
    if build_dir.exists():
        import shutil
        shutil.rmtree(build_dir)
        print(f"🧹 Cleaned existing build directory: {build_dir}", flush=True)
    
    build_dir.mkdir(exist_ok=True)
    print(f"📁 Created fresh build directory: {build_dir}", flush=True)
    
    all_output = "=== CMake Build Process ===\n"
    
    # Step 1: Run cmake configure
    cmake_cmd = ['cmake', '..', '-DCMAKE_BUILD_TYPE=Debug']
    print(f"CMake configure command: {' '.join(cmake_cmd)}", flush=True)
    
    proc = await asyncio.create_subprocess_exec(
        *cmake_cmd,
        cwd=str(build_dir),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    
    cmake_stdout = stdout.decode().strip()
    cmake_stderr = stderr.decode().strip()
    
    all_output += f"📋 CMake Configure Command: {' '.join(cmake_cmd)}\n"
    if cmake_stdout:
        all_output += f"CMake Configure Output:\n{cmake_stdout}\n\n"
    if cmake_stderr:
        all_output += f"CMake Configure Warnings/Info:\n{cmake_stderr}\n\n"
    
    if proc.returncode != 0:
        error_msg = f"❌ CMake configuration failed (exit code {proc.returncode})\n{all_output}"
        return False, error_msg
    
    # Step 2: Run cmake build
    build_cmd = ['cmake', '--build', '.', '--config', 'Debug', '--parallel']
    print(f"CMake build command: {' '.join(build_cmd)}", flush=True)
    
    proc = await asyncio.create_subprocess_exec(
        *build_cmd,
        cwd=str(build_dir),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    
    build_stdout = stdout.decode().strip()
    build_stderr = stderr.decode().strip()
    
    all_output += f"🔨 CMake Build Command: {' '.join(build_cmd)}\n"
    if build_stdout:
        all_output += f"CMake Build Output:\n{build_stdout}\n\n"
    if build_stderr:
        all_output += f"CMake Build Warnings/Info:\n{build_stderr}\n\n"
    
    if proc.returncode != 0:
        error_msg = f"❌ CMake build failed (exit code {proc.returncode})\n{all_output}"
        return False, error_msg
    
    # Success message
    success_msg = f"✅ CMake compilation successful with debug symbols\n{all_output}"
    success_msg += "✅ CMake build completed successfully!"
    return True, success_msg

async def compile_with_gcc():
    """Compile C++ project using direct G++ compilation."""
    # Smart file selection - avoid duplicates and prefer src/ directory structure
    cpp_files = []
    
    # Check if we have a src/ directory structure
    src_dir = APP_DIR / 'src'
    if src_dir.exists():
        # Use src/ directory files only
        cpp_files = list(src_dir.glob('*.cpp'))
        print(f"Using src/ directory structure: {len(cpp_files)} files")
    else:
        # Fall back to all cpp files in project
        cpp_files = list(APP_DIR.rglob('*.cpp'))
        print(f"Using flat structure: {len(cpp_files)} files")
    
    if not cpp_files:
        return False, 'No .cpp files found in the project.'

    # Convert Path objects to strings for the command
    cpp_file_paths = [str(f) for f in cpp_files]
    
    # Pure compilation with debug symbols - NO injection
    include_dir = APP_DIR / 'include'
    cmd = ['g++', '-g', '-O0', '-I', str(include_dir), '-o', str(BINARY_FILE)] + cpp_file_paths
    
    print(f"Pure compilation command: {' '.join(cmd)}", flush=True)

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    
    # Decode outputs
    stdout_text = stdout.decode().strip()
    stderr_text = stderr.decode().strip()
    
    if proc.returncode != 0:
        # Return detailed compilation error
        error_msg = f"Compilation failed (exit code {proc.returncode})\n"
        if stderr_text:
            error_msg += f"GCC Errors:\n{stderr_text}\n"
        if stdout_text:
            error_msg += f"GCC Output:\n{stdout_text}\n"
        return False, error_msg
    
    # Return detailed successful compilation output
    success_msg = f"✅ Compilation successful with debug symbols\n"
    success_msg += f"Command: {' '.join(cmd)}\n"
    
    if stdout_text:
        success_msg += f"\nGCC Output:\n{stdout_text}\n"
    if stderr_text:
        success_msg += f"\nGCC Warnings/Info:\n{stderr_text}\n"
    
    # If no output, show basic info
    if not stdout_text and not stderr_text:
        success_msg += "No additional compilation output.\n"
        
    return True, success_msg

async def compile_with_makefile():
    """Compile C++ project using Makefile build system."""
    if not (APP_DIR / 'Makefile').exists():
        return False, 'Makefile not found'
    
    all_output = "=== Makefile Build Process ===\n"
    
    # Clean previous builds
    clean_cmd = ['make', 'clean']
    print(f"🧹 Cleaning previous build: {' '.join(clean_cmd)}", flush=True)
    
    proc = await asyncio.create_subprocess_exec(
        *clean_cmd,
        cwd=str(APP_DIR),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    
    clean_stdout = stdout.decode().strip()
    clean_stderr = stderr.decode().strip()
    
    all_output += f"🧹 Make Clean Command: {' '.join(clean_cmd)}\n"
    if clean_stdout:
        all_output += f"Clean Output:\n{clean_stdout}\n\n"
    if clean_stderr:
        all_output += f"Clean Messages:\n{clean_stderr}\n\n"
    
    # Build the project with debug symbols
    build_cmd = ['make', 'debug'] if (APP_DIR / 'Makefile').read_text().find('debug:') != -1 else ['make']
    print(f"🔨 Building with Make: {' '.join(build_cmd)}", flush=True)
    
    proc = await asyncio.create_subprocess_exec(
        *build_cmd,
        cwd=str(APP_DIR),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    
    build_stdout = stdout.decode().strip()
    build_stderr = stderr.decode().strip()
    
    all_output += f"🔨 Make Build Command: {' '.join(build_cmd)}\n"
    if build_stdout:
        all_output += f"Build Output:\n{build_stdout}\n\n"
    if build_stderr:
        all_output += f"Build Messages:\n{build_stderr}\n\n"
    
    if proc.returncode != 0:
        error_msg = f"❌ Make build failed (exit code {proc.returncode})\n{all_output}"
        return False, error_msg
    
    # Success message
    success_msg = f"✅ Makefile compilation successful with debug symbols\n{all_output}"
    success_msg += "✅ Make build completed successfully!"
    return True, success_msg

def find_executable_binary(app_dir: Path) -> Path:
    """Find the executable binary, handling both simple builds and CMake builds."""
    # Check for simple build (main_bin)
    simple_binary = app_dir / 'main_bin'
    if simple_binary.exists() and simple_binary.is_file():
        return simple_binary
    
    # Check for CMake build directory
    cmake_build_dir = app_dir / 'build'
    if cmake_build_dir.exists() and cmake_build_dir.is_dir():
        # Look for executable files in build directory
        for file_path in cmake_build_dir.glob('*'):
            if file_path.is_file() and os.access(file_path, os.X_OK):
                # Check if it's an ELF binary by looking for executable bit and reasonable size
                if file_path.stat().st_size > 1000:  # At least 1KB
                    print(f"🔍 Found CMake binary: {file_path}")
                    return file_path
    
    # Check for direct executable in app directory (other build systems)
    for file_path in app_dir.glob('*'):
        if file_path.is_file() and os.access(file_path, os.X_OK) and file_path.name != 'main_bin':
            if file_path.stat().st_size > 1000:
                print(f"🔍 Found executable: {file_path}")
                return file_path
    
    # Fallback to original
    return simple_binary

async def run_binary():
    """Run the compiled binary - handles both G++ and CMake builds."""
    # Find the actual binary using smart detection
    actual_binary = find_executable_binary(APP_DIR)
    
    if not actual_binary.exists():
        return None, None, f'Binary not found. Looked for: {actual_binary}'
    
    print(f"🚀 Found executable binary: {actual_binary}")
    # Just return the binary path - memory monitor will handle execution
    return str(actual_binary), None, f'Ready to run with memory monitoring: {actual_binary.name}'

async def start_memory_monitoring(watch_vars_str: str, callback=None):
    """Start high-performance ptrace-based memory monitoring."""
    global ptrace_monitor
    
    # Find the actual executable binary
    actual_binary = find_executable_binary(APP_DIR)
    
    if not actual_binary.exists():
        return {"error": "Binary not found"}, f"Binary not found: {actual_binary}"
    
    # Parse watch variables with better type detection
    watch_vars = {}
    if watch_vars_str:
        for var in watch_vars_str.split(','):
            var_name = var.strip()
            # Smart type detection for common FCW ADAS variables
            if 'speed' in var_name.lower():
                watch_vars[var_name] = 'float'
            elif 'risk' in var_name.lower() or 'lane' in var_name.lower():
                watch_vars[var_name] = 'int'
            elif 'active' in var_name.lower() or 'warning' in var_name.lower():
                watch_vars[var_name] = 'bool'
            elif 'pressure' in var_name.lower() or 'temp' in var_name.lower():
                watch_vars[var_name] = 'float'
            else:
                watch_vars[var_name] = 'int'  # Default
    
    # Start ptrace-based monitor
    ptrace_monitor = MemoryVariableMonitor(str(actual_binary))
    ptrace_monitor.build_symbol_table()
    
    if not ptrace_monitor.start_process():
        return {"error": "Failed to start process"}, "Process start failed"
    
    print(f"Ptrace memory monitoring started for PID {ptrace_monitor.process.pid}")
    print(f"Watching variables: {list(watch_vars.keys())}")
    
    return {"status": "monitoring_started", "pid": ptrace_monitor.process.pid}, "Ptrace monitoring active"

async def get_global_variables(watch_vars_str, pid=None):
    """Read variables directly from process memory using ptrace."""
    global ptrace_monitor
    
    if not ptrace_monitor or not ptrace_monitor.process:
        return {"error": "No active monitoring"}, "Monitor not running"
    
    # Parse variables to monitor with type detection
    variables = {}
    if watch_vars_str:
        for var in watch_vars_str.split(','):
            var_name = var.strip()
            # Smart type detection
            if 'speed' in var_name.lower():
                variables[var_name] = 'float'
            elif 'risk' in var_name.lower() or 'lane' in var_name.lower():
                variables[var_name] = 'int'
            elif 'active' in var_name.lower() or 'warning' in var_name.lower():
                variables[var_name] = 'bool'
            elif 'pressure' in var_name.lower():
                variables[var_name] = 'float'
            else:
                variables[var_name] = 'int'
    
    # Read variables using ptrace
    values = ptrace_monitor.monitor_variables(variables)
    
    if not values:
        return {"warning": "No variables read"}, "No data available"
    
    return values, "Success"

def cleanup_memory_monitor():
    """Clean up memory monitor resources."""
    global monitor, ptrace_monitor
    if monitor:
        monitor.cleanup()
        monitor = None
    if ptrace_monitor:
        ptrace_monitor.cleanup()
        ptrace_monitor = None
    
    # Also cleanup auto memory monitor
    try:
        from auto_memory_monitor import cleanup_auto_monitoring
        cleanup_auto_monitoring()
        print("Auto memory monitor cleaned up")
    except Exception as e:
        print(f"Error cleaning up auto memory monitor: {e}")

async def periodic_memory_var_report(socketio, kit_id, watch_vars_str, send_reply_func=None):
    """Send periodic variable reports and stdout forwarding via ptrace memory inspection with stdout capture."""
    global ptrace_monitor
    
    # Start monitoring if not already active
    if not ptrace_monitor:
        print(f"🔥 Starting ptrace memory monitoring for kit {kit_id}")
        result, msg = await start_memory_monitoring(watch_vars_str)
        if "error" in result:
            print(f"🔥 Failed to start monitoring: {msg}")
            return
    
    if not ptrace_monitor or not ptrace_monitor.process:
        print("🔥 Ptrace memory monitoring not active")
        return
    
    # Check if process is still running
    if ptrace_monitor.process.poll() is not None:
        print(f"🔥 Process has exited with code {ptrace_monitor.process.returncode}")
        return
    
    print(f"🔥 Starting periodic memory variable reporting with stdout capture for kit {kit_id}")
    print(f"🔥 Variables to monitor: {watch_vars_str}")
    
    # Set up stdout capture from the ptrace monitored process
    import select
    import os
    import fcntl
    
    # Initialize buffers outside try block so they're accessible in finally
    stdout_buffer = ""
    stderr_buffer = ""
    
    try:
        # Get process stdout/stderr file descriptors
        process_stdout = ptrace_monitor.process.stdout
        process_stderr = ptrace_monitor.process.stderr
        
        if process_stdout:
            # Make stdout non-blocking for select()
            fd_stdout = process_stdout.fileno()
            flags = fcntl.fcntl(fd_stdout, fcntl.F_GETFL)
            fcntl.fcntl(fd_stdout, fcntl.F_SETFL, flags | os.O_NONBLOCK)
            print(f"🔥 Set up non-blocking stdout capture for PID {ptrace_monitor.process.pid}")
        
        report_count = 0
        lines_read = 0
        
        while ptrace_monitor.process.poll() is None:  # Check if process is still running
            # Read stdout/stderr from the C++ process and forward to kit server
            try:
                # Check if there's data available for reading
                ready, _, _ = select.select([ptrace_monitor.process.stdout, ptrace_monitor.process.stderr], [], [], 0.1)
                
                for stream in ready:
                    if stream == ptrace_monitor.process.stdout:
                        chunk = stream.read(1024)
                        if chunk:
                            stdout_buffer += chunk
                            # Send stdout lines to kit server
                            while '\n' in stdout_buffer:
                                line, stdout_buffer = stdout_buffer.split('\n', 1)
                                if line.strip():  # Only send non-empty lines
                                    lines_read += 1
                                    print(f"🔥 Captured stdout line {lines_read}: {line}")
                                    await socketio.emit('messageToKit-kitReply', {
                                        'kit_id': CLIENT_ID,
                                        'request_from': kit_id,
                                        'cmd': 'run_cpp_app',
                                        'data': line,
                                        'result': line,
                                        'isError': False,
                                        'isDone': False,
                                        'code': 0
                                    })
                    
                    elif stream == ptrace_monitor.process.stderr:
                        chunk = stream.read(1024)
                        if chunk:
                            stderr_buffer += chunk
                            # Send stderr lines to kit server
                            while '\n' in stderr_buffer:
                                line, stderr_buffer = stderr_buffer.split('\n', 1)
                                if line.strip():  # Only send non-empty lines
                                    lines_read += 1
                                    print(f"🔥 Captured stderr line {lines_read}: {line}")
                                    await socketio.emit('messageToKit-kitReply', {
                                        'kit_id': CLIENT_ID,
                                        'request_from': kit_id,
                                        'cmd': 'run_cpp_app',
                                        'data': f"[STDERR] {line}",
                                        'result': f"[STDERR] {line}",
                                        'isError': False,
                                        'isDone': False,
                                        'code': 0
                                    })
                                    
            except Exception as stdout_error:
                # Don't let stdout reading errors break the monitoring
                print(f"🔥 Stdout/stderr read error: {stdout_error}")
            
            # Get memory variables
            values, status = await get_global_variables(watch_vars_str)
            
            if isinstance(values, dict) and "error" not in values and values:
                # Send to frontend via WebSocket using correct channel
                await socketio.emit('messageToKit-kitReply', {
                    'kit_id': CLIENT_ID,
                    'request_from': kit_id,
                    'cmd': 'trace_vars',
                    'data': values,
                    'isDone': False,
                    'code': 0
                })
                
                report_count += 1
                if report_count % 20 == 0:  # Log every 20th report to reduce spam
                    print(f"🔥 [Report #{report_count}] Variables: {values}, Stdout lines: {lines_read}")
                    
            await asyncio.sleep(0.3)  # 300ms for better stdout responsiveness
            
    except Exception as e:
        print(f"🔥 Memory monitoring error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print(f"🔥 Stopping memory monitoring - captured {lines_read} stdout lines")
        
        # Flush any remaining stdout/stderr content
        try:
            if ptrace_monitor and ptrace_monitor.process and ptrace_monitor.process.stdout and ptrace_monitor.process.stderr:
                import select
                # Final read of any remaining output with short timeout
                ready, _, _ = select.select([ptrace_monitor.process.stdout, ptrace_monitor.process.stderr], [], [], 0.1)
                
                for stream in ready:
                    try:
                        if stream == ptrace_monitor.process.stdout:
                            remaining_data = stream.read()
                            if remaining_data and remaining_data.strip():
                                # Send any remaining stdout buffer + final data
                                final_stdout = stdout_buffer + remaining_data
                                for line in final_stdout.strip().split('\n'):
                                    if line.strip():
                                        await socketio.emit('messageToKit-kitReply', {
                                            'kit_id': CLIENT_ID,
                                            'request_from': kit_id,
                                            'cmd': 'run_cpp_app',
                                            'data': line,
                                            'isDone': False,
                                            'code': 0
                                        })
                        
                        elif stream == ptrace_monitor.process.stderr:
                            remaining_data = stream.read()
                            if remaining_data and remaining_data.strip():
                                # Send any remaining stderr buffer + final data
                                final_stderr = stderr_buffer + remaining_data
                                for line in final_stderr.strip().split('\n'):
                                    if line.strip():
                                        await socketio.emit('messageToKit-kitReply', {
                                            'kit_id': CLIENT_ID,
                                            'request_from': kit_id,
                                            'cmd': 'run_cpp_app',
                                            'data': f"[STDERR] {line}",
                                            'isDone': False,
                                            'code': 0
                                        })
                    except:
                        # Ignore errors in final cleanup
                        pass
                        
        except Exception as flush_error:
            print(f"Error flushing final output: {flush_error}")
        
        # Send final completion status to frontend
        await socketio.emit('messageToKit-kitReply', {
            'kit_id': CLIENT_ID,
            'request_from': kit_id,
            'cmd': 'run_cpp_app',  # Use the original command
            'data': f'Memory monitoring completed - {lines_read} stdout lines captured',
            'result': f'Memory monitoring completed successfully - {lines_read} stdout lines captured',
            'isError': False,
            'isDone': True,
            'code': 0
        })
        
        cleanup_memory_monitor()

def is_process_running(pid=None):
    """Check if monitored process is running."""
    global ptrace_monitor
    return ptrace_monitor and ptrace_monitor.process and ptrace_monitor.process.poll() is None

# Compatibility functions for existing syncer
def set_global_variable(var_name, value):
    """Set variable in monitored process (future enhancement)."""
    # Could be implemented using ptrace or /proc/pid/mem write
    print(f"Variable setting not yet implemented: {var_name} = {value}")
    return True

def validate_variable_setting(var_name, value):
    """Validate variable setting operation."""
    return True, "Memory-based setting not yet implemented"