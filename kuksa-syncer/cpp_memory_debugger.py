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
    """Compile C++ project with debug symbols - no injection needed."""
    if not APP_DIR.exists():
        return False, 'App directory not found.'

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
    
    if proc.returncode != 0:
        return False, stderr.decode()
        
    return True, 'Compiled successfully with debug symbols.'

async def run_binary():
    """Run the compiled binary - pure execution."""
    if not os.path.exists(BINARY_FILE):
        return None, None, 'Binary not found.'
    
    # Just return the binary path - memory monitor will handle execution
    return str(BINARY_FILE), None, 'Ready to run with memory monitoring.'

async def start_memory_monitoring(watch_vars_str: str, callback=None):
    """Start high-performance ptrace-based memory monitoring."""
    global ptrace_monitor
    
    if not os.path.exists(BINARY_FILE):
        return {"error": "Binary not found"}, "Binary not found"
    
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
    ptrace_monitor = MemoryVariableMonitor(str(BINARY_FILE))
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
    """Send periodic variable reports via ptrace memory inspection."""
    global ptrace_monitor
    
    # Start monitoring if not already active
    if not ptrace_monitor:
        print(f"Starting ptrace memory monitoring for kit {kit_id}")
        result, msg = await start_memory_monitoring(watch_vars_str)
        if "error" in result:
            print(f"Failed to start monitoring: {msg}")
            return
    
    if not ptrace_monitor or not ptrace_monitor.process:
        print("Ptrace memory monitoring not active")
        return
    
    # Check if process is still running
    if ptrace_monitor.process.poll() is not None:
        print(f"Process has exited with code {ptrace_monitor.process.returncode}")
        return
    
    print(f"Starting periodic memory variable reporting for kit {kit_id}")
    print(f"Variables to monitor: {watch_vars_str}")
    
    try:
        report_count = 0
        while ptrace_monitor.process.poll() is None:  # Check if process is still running
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
                if report_count % 10 == 0:  # Log every 10th report to avoid spam
                    print(f"[Report #{report_count}] Variables: {values}")
                    
            await asyncio.sleep(0.5)  # 500ms for good balance of performance and updates
            
    except Exception as e:
        print(f"Memory monitoring error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("Stopping memory monitoring")
        
        # Send final completion status to frontend
        await socketio.emit('messageToKit-kitReply', {
            'kit_id': CLIENT_ID,
            'request_from': kit_id,
            'cmd': 'run_cpp_app',  # Use the original command
            'data': '',
            'result': 'Memory monitoring completed successfully',
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