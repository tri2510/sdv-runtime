#!/usr/bin/env python3
"""
Replacement for cpp_debugger_util.py using direct memory inspection.
High-performance, no GDB overhead, works with pure C++ projects.
"""

import os
import subprocess
import asyncio
import time
import builtins
import shutil
from pathlib import Path
from typing import Tuple, Dict
from memory_monitor import ProcessMemoryMonitor, SmartVariableDetector
from ptrace_memory_reader import MemoryVariableMonitor
from auto_variable_detector import AutoVariableDetector, SmartMemoryReader
from universal_auto_detector import UniversalAutoDetector, create_variable_list_for_syncer

def _is_verbose() -> bool:
    return os.getenv('CPP_TRACE_VERBOSE', '1') == '1'

def _debug_print(*args, **kwargs):
    if _is_verbose():
        builtins.print(*args, **kwargs)

def _error_print(*args, **kwargs):
    builtins.print(*args, **kwargs)

print = _debug_print

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
    if build_dir.exists():
        try:
            shutil.rmtree(build_dir)
        except Exception as exc:
            print(f"⚠️  Failed to clean previous CMake build directory: {exc}", flush=True)
    build_dir.mkdir(parents=True, exist_ok=True)
    print(f"📁 Using build directory: {build_dir}", flush=True)
    
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

def auto_detect_project_variables() -> Tuple[str, Path]:
    """Auto-detect variables from the current project with ZERO hardcoded values."""
    print("🚀 Starting AUTOMATIC project variable detection...")

    # Try to detect project directory intelligently using repo-relative paths
    repo_root = APP_DIR.parent  # kuksa-syncer/
    possible_projects = [APP_DIR]

    # Add all cpp-projects/* directories dynamically
    projects_root = repo_root / "cpp-projects"
    if projects_root.exists():
        possible_projects.extend(sorted([path for path in projects_root.iterdir() if path.is_dir()]))

    detector = UniversalAutoDetector()
    
    for project_dir in possible_projects:
        if project_dir.exists():
            print(f"🔍 Checking project: {project_dir}")
            variables, binary_path = detector.auto_detect_project_variables(project_dir)
            
            # Filter to only variables found in binary
            monitorable_vars = [v for v in variables if v['found_in_binary']]
            
            if len(monitorable_vars) > 0 and binary_path:
                var_list = create_variable_list_for_syncer(monitorable_vars)
                print(f"✅ AUTO-DETECTED {len(monitorable_vars)} variables: {var_list}")
                print(f"✅ Using binary: {binary_path}")
                return var_list, binary_path
    
    _error_print("❌ No project with monitorable variables found")
    return "", None

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
    """Start high-performance ptrace-based memory monitoring with AUTOMATIC variable detection."""
    global ptrace_monitor
    
    # AUTOMATIC DETECTION: If no variables provided or contains hardcoded defaults, auto-detect
    auto_detect_needed = False
    
    if not watch_vars_str or not watch_vars_str.strip():
        print("🤖 No variables specified - using AUTOMATIC DETECTION")
        auto_detect_needed = True
    elif any(hardcoded in watch_vars_str for hardcoded in ['counter', 'sensor_value', 'collision_risk']):
        print("🤖 Hardcoded variables detected - switching to AUTOMATIC DETECTION")
        auto_detect_needed = True
    
    actual_binary = None
    
    if auto_detect_needed:
        # Use universal auto-detection
        auto_vars, auto_binary = auto_detect_project_variables()
        if auto_vars and auto_binary:
            watch_vars_str = auto_vars
            actual_binary = auto_binary
            print(f"🤖 AUTO-DETECTED variables: {watch_vars_str}")
            print(f"🤖 AUTO-DETECTED binary: {actual_binary}")
        else:
            print("❌ Automatic detection failed, falling back to manual search")
            actual_binary = find_executable_binary(APP_DIR)
    else:
        # Use provided variables with existing binary detection
        actual_binary = find_executable_binary(APP_DIR)
    
    if not actual_binary or not actual_binary.exists():
        return {"error": "Binary not found"}, f"Binary not found: {actual_binary}"
    
    # Parse watch variables - NO hardcoded type assumptions, use actual detection
    watch_vars = {}
    symbol_mappings: Dict[str, int] = {}
    if watch_vars_str:
        # Get variable types from the project detection using current directory
        detector = UniversalAutoDetector()
        project_vars, _ = detector.auto_detect_project_variables(APP_DIR)
        var_type_map = {v['name']: v['type'] for v in project_vars if v['found_in_binary']}
        
        # SMART ADAPTIVE FILTERING: Only setup variables that actually exist
        requested_vars = [v.strip() for v in watch_vars_str.split(',') if v.strip()]
        available_vars = list(var_type_map.keys())
        
        print(f"🔍 Initial setup - Available variables in project: {available_vars}")
        print(f"📋 Initial setup - Requested variables: {requested_vars}")
        
        for var_name in requested_vars:
            if var_name in var_type_map:
                watch_vars[var_name] = var_type_map[var_name]
                print(f"✅ Initial setup - Will monitor: {var_name} ({var_type_map[var_name]})")
            else:
                print(f"⚠️  Initial setup - Variable '{var_name}' requested but NOT FOUND in current project - skipping")
        
        # If no requested variables were found, auto-select available ones  
        if not watch_vars and available_vars:
            print(f"📍 Initial setup - No requested variables available, auto-selecting from available variables...")
            # Select up to 5 most relevant available variables
            for var_name in available_vars[:5]:
                watch_vars[var_name] = var_type_map[var_name]
                print(f"✅ Initial setup - Auto-selected: {var_name} ({var_type_map[var_name]})")
        
        print(f"🎯 Initial setup - Final monitoring variables: {list(watch_vars.keys())}")
        
        # Create symbol mappings from auto-detection results for memory monitor
        for var in project_vars:
            if var['found_in_binary'] and var['name'] in watch_vars:
                symbol_mappings[var['name']] = var['symbol_address']
                print(f"🔗 Mapping {var['name']} -> 0x{var['symbol_address']:x}")
    
    # Start ptrace-based monitor
    ptrace_monitor = MemoryVariableMonitor(str(actual_binary))
    ptrace_monitor.build_symbol_table()
    
    # Override symbol table with auto-detected mappings
    if symbol_mappings:
        ptrace_monitor.set_symbol_mappings(symbol_mappings)
    
    if not ptrace_monitor.start_process():
        return {"error": "Failed to start process"}, "Process start failed"
    
    print(f"Ptrace memory monitoring started for PID {ptrace_monitor.process.pid}")
    print(f"Watching variables: {list(watch_vars.keys())}")
    
    return {"status": "monitoring_started", "pid": ptrace_monitor.process.pid}, "Ptrace monitoring active"

async def get_global_variables(watch_vars_str, pid=None):
    """Read variables directly from process memory using ptrace with AUTOMATIC type detection."""
    global ptrace_monitor
    
    if not ptrace_monitor or not ptrace_monitor.process:
        return {"error": "No active monitoring"}, "Monitor not running"
    
    # Parse variables to monitor with AUTOMATIC type detection
    variables = {}
    symbol_mappings: Dict[str, int] = {}
    if watch_vars_str:
        # Get variable types from automatic project detection
        try:
            detector = UniversalAutoDetector()
            # Find the project directory from the binary path
            binary_path = Path(ptrace_monitor.binary_path)
            # Use APP_DIR which is now correctly set to the project directory
            project_vars, _ = detector.auto_detect_project_variables(APP_DIR)
            var_type_map = {v['name']: v['type'] for v in project_vars if v['found_in_binary']}
            
            # SMART ADAPTIVE FILTERING: Only monitor variables that actually exist
            requested_vars = [v.strip() for v in watch_vars_str.split(',') if v.strip()]
            available_vars = list(var_type_map.keys())
            
            print(f"🔍 Available variables in project: {available_vars}")
            print(f"📋 Requested variables: {requested_vars}")
            
            for var_name in requested_vars:
                if var_name in var_type_map:
                    variables[var_name] = var_type_map[var_name]
                    print(f"✅ Will monitor: {var_name} ({var_type_map[var_name]})")
                else:
                    print(f"⚠️  Variable '{var_name}' requested but NOT FOUND in current project - skipping")
            
            # If no requested variables were found, auto-select available ones  
            if not variables and available_vars:
                print(f"📍 No requested variables available, auto-selecting from available variables...")
                # Select up to 5 most relevant available variables
                for var_name in available_vars[:5]:
                    variables[var_name] = var_type_map[var_name]
                    print(f"✅ Auto-selected: {var_name} ({var_type_map[var_name]})")
            
            print(f"🎯 Final monitoring variables: {list(variables.keys())}")
            
            # Create symbol mappings for the variables we're actually monitoring
            for var in project_vars:
                if var['found_in_binary'] and var['name'] in variables:
                    symbol_mappings[var['name']] = var['symbol_address']
                    print(f"🔗 Runtime mapping {var['name']} -> 0x{var['symbol_address']:x}")
            
            # Update memory monitor symbol table with correct mappings
            if symbol_mappings:
                ptrace_monitor.set_symbol_mappings(symbol_mappings)
                
        except Exception as e:
            print(f"Warning: Automatic type detection failed: {e}")
            # Fallback to basic parsing without hardcoded assumptions
            for var in watch_vars_str.split(','):
                var_name = var.strip()
                variables[var_name] = 'int'  # Simple fallback
    
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

async def periodic_memory_var_report(socketio, kit_id, watch_vars_str, send_reply_func=None, completion_callback=None, duration_seconds=None):
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
    print(f"🔥 Process PID: {ptrace_monitor.process.pid}")
    print(f"🔥 Process stdout: {ptrace_monitor.process.stdout}")
    print(f"🔥 Process stderr: {ptrace_monitor.process.stderr}")
    
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
        start_time = time.time()
        
        while ptrace_monitor.process.poll() is None:  # Check if process is still running
            # Read stdout/stderr from the C++ process and forward to kit server
            try:
                # Check if there's data available for reading
                ready, _, _ = select.select([ptrace_monitor.process.stdout, ptrace_monitor.process.stderr], [], [], 0.1)
                
                if ready:
                    print(f"🔥 Select found {len(ready)} streams with data available")
                
                for stream in ready:
                    if stream == ptrace_monitor.process.stdout:
                        chunk = stream.read(1024)
                        print(f"🔥 Read stdout chunk: {chunk!r}")
                        if chunk:
                            stdout_buffer += chunk
                            # Send stdout lines to kit server
                            while '\n' in stdout_buffer:
                                line, stdout_buffer = stdout_buffer.split('\n', 1)
                                if line.strip():  # Only send non-empty lines
                                    lines_read += 1
                                    print(f"🔥 Captured stdout line {lines_read}: {line}")
                                    # Use send_reply_func if provided (for better compatibility with Kit server)
                                    if send_reply_func:
                                        await send_reply_func(line + '\r\n', is_error=False)
                                    else:
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
                                    # Use send_reply_func if provided (for better compatibility with Kit server)
                                    if send_reply_func:
                                        await send_reply_func(f"[STDERR] {line}\r\n", is_error=True)
                                    else:
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

            if duration_seconds is not None and (time.time() - start_time) >= duration_seconds:
                if _is_verbose():
                    builtins.print(f"🔥 Duration limit reached ({duration_seconds}s), stopping monitoring loop")
                break
            
    except Exception as e:
        _error_print(f"🔥 Memory monitoring error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if _is_verbose():
            builtins.print(f"🔥 Stopping memory monitoring - captured {lines_read} stdout lines")
        
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
            _error_print(f"Error flushing final output: {flush_error}")
        
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
        
        # Execute completion callback if provided (e.g., remove from running list)
        if completion_callback:
            try:
                completion_callback(kit_id)
                print(f"✅ Completion callback executed for kit {kit_id}")
            except Exception as e:
                print(f"Error in completion callback: {e}")

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

async def start_cpp_trace_vars_monitoring(data, request_from, socketio):
    """
    Start C++ trace_vars monitoring - entry point for trace_vars command from Kit Server
    This function handles the complete trace_vars workflow:
    1. Parse trace_vars command data
    2. Setup C++ project and compilation
    3. Start memory monitoring for specified variables
    4. Send trace_vars events back to Kit Server via socketio
    """
    print(f"🔥 Starting trace_vars monitoring for {request_from}")
    
    try:
        # Extract trace_vars parameters
        project_path = data.get('project_path')
        binary_name = data.get('binary_name')
        trace_vars = data.get('trace_vars', [])
        duration = data.get('duration', 10)  # Default 10 seconds
        project_type = data.get('project_type', 'cmake')
        
        print(f"🎯 trace_vars parameters:")
        print(f"   Project: {project_path}")
        print(f"   Binary: {binary_name}")
        print(f"   Variables: {trace_vars}")
        print(f"   Duration: {duration}s")
        print(f"   Type: {project_type}")
        
        # Store original directory
        original_dir = os.getcwd()
        
        # Change to project directory and update APP_DIR
        if project_path:
            os.chdir(project_path)
            global APP_DIR
            APP_DIR = Path(project_path)
            print(f"📂 Changed to project directory: {project_path}")
        
        # Compile the project unless caller requested to skip
        if not data.get('skip_build', False):
            print("🔨 Compiling C++ project...")
            if project_type == 'cmake':
                await compile_with_cmake()
            else:
                await compile_cpp()
            print("✅ Compilation completed")
        else:
            print("⏩ Skipping build step (pre-built binary assumed)")
        
        # Start memory monitoring with trace_vars
        watch_vars_str = ','.join(trace_vars)
        print(f"🔍 Starting memory monitoring for variables: {watch_vars_str}")
        
        # Use periodic_memory_var_report which handles the socketio events
        await periodic_memory_var_report(
            socketio=socketio,
            kit_id=request_from, 
            watch_vars_str=watch_vars_str,
            send_reply_func=None,
            duration_seconds=duration
        )
        
        print(f"✅ trace_vars monitoring completed for {request_from}")
        
        # Restore original directory
        os.chdir(original_dir)
        
    except Exception as e:
        print(f"❌ trace_vars monitoring error: {e}")
        import traceback
        traceback.print_exc()
        # Restore original directory on error
        try:
            os.chdir(original_dir)
        except:
            pass
        raise
