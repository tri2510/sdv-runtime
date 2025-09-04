#!/usr/bin/env python3
"""
Automatic Memory Monitoring System
Automatically detects and monitors any C++ atomic variables without hardcoding.
"""

import os
import subprocess
import asyncio
import time
import argparse
import threading
from pathlib import Path
from auto_variable_detector import AutoVariableDetector, SmartMemoryReader

# Configuration
APP_DIR = Path(os.path.dirname(__file__)) / 'app'
BINARY_FILE = APP_DIR / 'main_bin'
CLIENT_ID = "RunTime-TriCPP"

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

class AutoMemoryMonitor:
    """Automatic memory monitoring system."""
    
    def __init__(self):
        self.detector = AutoVariableDetector()
        self.memory_reader = None
        self.process = None
        self.monitorable_vars = []
        self.socketio = None
        self.kit_id = None
    
    def discover_variables(self, cpp_code: str, binary_path: str) -> bool:
        """Discover all monitorable variables automatically."""
        print("🔍 Auto-discovering C++ variables...")
        
        self.monitorable_vars = self.detector.auto_detect_variables(cpp_code, binary_path)
        
        if not self.monitorable_vars:
            print("❌ No monitorable variables found")
            return False
        
        print(f"✅ Found {len(self.monitorable_vars)} monitorable variables:")
        for var in self.monitorable_vars:
            if var['found_in_binary']:
                print(f"   📊 {var['name']}: {var['type']} @ 0x{var['symbol_address']:x}")
        
        return True
    
    def filter_requested_variables(self, watch_vars_str: str) -> list:
        """Filter to only requested variables, or return all if none specified."""
        if not watch_vars_str or not watch_vars_str.strip():
            # Monitor all discovered variables
            filtered = [var for var in self.monitorable_vars if var['found_in_binary']]
            print(f"📈 Monitoring ALL {len(filtered)} detected variables")
            return filtered
        
        # Monitor only requested variables (case-insensitive)
        requested_names = [v.strip().lower() for v in watch_vars_str.split(',')]
        filtered = []
        not_found = []
        
        for req_name in requested_names:
            found = False
            # First try exact match (case-insensitive)
            for var in self.monitorable_vars:
                if var['found_in_binary'] and var['name'].lower() == req_name:
                    if var not in filtered:
                        filtered.append(var)
                        found = True
                        break
            
            # If not found, try partial match
            if not found:
                for var in self.monitorable_vars:
                    if var['found_in_binary'] and req_name in var['name'].lower():
                        if var not in filtered:
                            filtered.append(var)
                            found = True
                            break
            
            if not found:
                not_found.append(req_name)
        
        if not_found:
            print(f"⚠️ Variables not found: {', '.join(not_found)}")
        
        if filtered:
            print(f"📈 Monitoring {len(filtered)} variables: {[v['name'] for v in filtered]}")
        
        return filtered
    
    def set_console_forwarding(self, socketio, kit_id, event_loop=None):
        """Set up console output forwarding to kit server."""
        self.socketio = socketio
        self.kit_id = kit_id
        self.event_loop = event_loop or asyncio.get_event_loop()
        
        # Start stdout forwarding thread if process is already running
        if self.process and self.process.stdout:
            stdout_thread = threading.Thread(target=self._forward_stdout, daemon=True)
            stdout_thread.start()
            print("📺 Console output forwarding enabled for existing process")
    
    def _forward_stdout(self):
        """Thread function to forward stdout to kit server console."""
        if not self.process or not self.socketio or not self.kit_id:
            return
        
        try:
            # Use the event loop passed from the main thread
            loop = getattr(self, 'event_loop', None)
            if not loop:
                return
            
            while self.process.poll() is None:
                try:
                    line = self.process.stdout.readline()
                    if line:
                        # Send line to console asynchronously
                        asyncio.run_coroutine_threadsafe(
                            send_console_output(self.socketio, self.kit_id, line.strip() + '\r\n'),
                            loop
                        )
                except Exception as readline_error:
                    # Don't spam errors, just continue
                    break
                    
        except Exception as e:
            print(f"Error in stdout forwarding thread: {e}")
    
    def start_process(self) -> bool:
        """Start the C++ process for monitoring."""
        try:
            # Find the actual binary (handles CMake builds)
            actual_binary = find_executable_binary(APP_DIR)
            print(f"🚀 Starting C++ binary: {actual_binary}")
            self.process = subprocess.Popen([str(actual_binary)], 
                                         stdout=subprocess.PIPE, 
                                         stderr=subprocess.PIPE,
                                         universal_newlines=True,
                                         bufsize=1)
            
            # Wait for process to initialize
            time.sleep(0.5)
            
            if self.process.poll() is not None:
                print(f"❌ Process exited immediately with code {self.process.returncode}")
                return False
            
            print(f"✅ Process started with PID {self.process.pid}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start process: {e}")
            return False
    
    def attach_memory_reader(self) -> bool:
        """Attach memory reader to the process."""
        try:
            self.memory_reader = SmartMemoryReader(self.process.pid)
            if self.memory_reader.attach():
                print(f"✅ Memory reader attached to PID {self.process.pid}")
                return True
            else:
                print("❌ Failed to attach memory reader")
                return False
        except Exception as e:
            print(f"❌ Memory reader attachment failed: {e}")
            return False
    
    def read_all_variables(self) -> dict:
        """Read all monitored variables."""
        if not self.memory_reader or not self.vars_to_monitor:
            return {}
        
        return self.memory_reader.read_all_variables(self.vars_to_monitor)
    
    def cleanup(self):
        """Clean up resources."""
        if self.memory_reader:
            self.memory_reader.detach()
        if self.process and self.process.poll() is None:
            self.process.terminate()
            
        print("🧹 Auto memory monitor cleaned up")

# Global monitor instance
auto_monitor = None

async def start_auto_monitoring(watch_vars_str: str = "") -> tuple:
    """Start automatic memory monitoring."""
    global auto_monitor
    
    try:
        # Step 1: Read C++ source code
        cpp_file = APP_DIR / "main.cpp"
        if not cpp_file.exists():
            return ("error", "C++ source file not found")
        
        with open(cpp_file, 'r') as f:
            cpp_code = f.read()
        
        # Step 2: Initialize monitor
        auto_monitor = AutoMemoryMonitor()
        
        # Step 3: Discover variables (use dynamic binary detection)
        actual_binary = find_executable_binary(APP_DIR)
        if not auto_monitor.discover_variables(cpp_code, str(actual_binary)):
            return ("error", "No variables discovered in C++ code")
        
        # Step 4: Filter to requested variables
        auto_monitor.vars_to_monitor = auto_monitor.filter_requested_variables(watch_vars_str)
        
        if not auto_monitor.vars_to_monitor:
            # If no requested variables found, use all available variables
            print(f"⚠️ Warning: No requested variables found: {watch_vars_str}")
            print("📊 Proceeding with ALL detected variables instead...")
            auto_monitor.vars_to_monitor = [var for var in auto_monitor.monitorable_vars if var['found_in_binary']]
            
            if not auto_monitor.vars_to_monitor:
                return ("error", "No monitorable variables found in binary")
            
            monitored_names = [v['name'] for v in auto_monitor.vars_to_monitor]
            print(f"✅ Monitoring ALL {len(monitored_names)} variables: {', '.join(monitored_names)}")
        
        # Step 5: Start process
        if not auto_monitor.start_process():
            return ("error", "Failed to start C++ process")
        
        # Step 6: Attach memory reader
        if not auto_monitor.attach_memory_reader():
            return ("error", "Failed to attach memory reader")
        
        monitored_vars = [v['name'] for v in auto_monitor.vars_to_monitor]
        return ("success", f"Auto-monitoring started for: {', '.join(monitored_vars)}")
        
    except Exception as e:
        return ("error", f"Auto-monitoring setup failed: {e}")

async def get_auto_variables() -> tuple:
    """Get current values of all auto-detected variables."""
    global auto_monitor
    
    if not auto_monitor or not auto_monitor.process:
        return ({"error": "Auto-monitoring not active"}, "error")
    
    # Check if process is still running
    if auto_monitor.process.poll() is not None:
        return ({"error": f"Process exited with code {auto_monitor.process.returncode}"}, "error")
    
    try:
        values = auto_monitor.read_all_variables()
        return (values, "success" if values else "no_data")
    except Exception as e:
        return ({"error": f"Variable read failed: {e}"}, "error")

def cleanup_auto_monitoring():
    """Clean up auto-monitoring resources."""
    global auto_monitor
    
    if auto_monitor:
        auto_monitor.cleanup()
        auto_monitor = None
        print("Auto-monitoring cleanup completed")

async def send_console_output(socketio, kit_id, message):
    """Send console output to kit server (similar to send_app_run_reply in syncer.py)."""
    await socketio.emit('messageToKit-kitReply', {
        'kit_id': CLIENT_ID,
        'request_from': kit_id,
        'cmd': 'run_app',
        'data': message,
        'isDone': False,
        'code': 0
    })

async def periodic_auto_memory_report(socketio, kit_id, watch_vars_str, 
                                     monitoring_interval=0.1, 
                                     max_duration_seconds=300,
                                     max_reports=10000):
    """Generate periodic memory variable reports using auto-detection.
    
    Args:
        socketio: Socket.IO instance for communication
        kit_id: Kit identifier for messaging
        watch_vars_str: Comma-separated list of variables to watch
        monitoring_interval: Time between reads in seconds (default: 0.1s for real-time)
        max_duration_seconds: Maximum monitoring duration in seconds (default: 300s = 5 minutes)
        max_reports: Maximum number of reports to send (default: 10000)
    """
    global auto_monitor
    
    # Configuration macros - easy to customize
    MONITORING_INTERVAL = monitoring_interval  # 0.1s for real-time, 1s for normal, 2s for conservative
    MAX_DURATION_SECONDS = max_duration_seconds  # 5 minutes default
    MAX_REPORTS = max_reports  # 10000 reports max
    MAX_FAILED_READS = 5  # Allow more failures before stopping
    INIT_DELAY = 2  # Initial delay for process startup
    
    # Calculate effective max reports based on duration and interval
    duration_based_reports = int(MAX_DURATION_SECONDS / MONITORING_INTERVAL)
    effective_max_reports = min(MAX_REPORTS, duration_based_reports)
    
    print(f"🎯 Starting automatic variable monitoring for kit {kit_id}")
    print(f"📊 Config: interval={MONITORING_INTERVAL}s, max_duration={MAX_DURATION_SECONDS}s, max_reports={effective_max_reports}")
    
    try:
        # Start auto-monitoring
        result, msg = await start_auto_monitoring(watch_vars_str)
        
        if "error" in result:
            print(f"❌ Auto-monitoring setup failed: {msg}")
            await socketio.emit('messageToKit-kitReply', {
                'kit_id': CLIENT_ID,
                'request_from': kit_id,
                'cmd': 'trace_vars',
                'data': {"error": msg},
                'isDone': True,
                'isError': True
            })
            return
        
        print(f"✅ Auto-monitoring setup: {msg}")
        
        # Set up stdout forwarding for the existing monitor
        if auto_monitor and auto_monitor.process:
            auto_monitor.set_console_forwarding(socketio, kit_id, asyncio.get_event_loop())
            # Send setup status to console
            await send_console_output(socketio, kit_id, f"✅ {msg}\r\n")
            await send_console_output(socketio, kit_id, f"📊 Config: interval={MONITORING_INTERVAL}s, max_duration={MAX_DURATION_SECONDS}s\r\n")
        
        # Monitoring loop with configurable timing
        report_count = 0
        failed_reads = 0
        start_time = time.time()
        
        # Give process time to fully initialize
        await asyncio.sleep(INIT_DELAY)
        
        while report_count < effective_max_reports and auto_monitor.process.poll() is None:
            values, status = await get_auto_variables()
            
            if status == "success" and values and not isinstance(values.get("error"), str):
                # Send successful variable update
                await socketio.emit('messageToKit-kitReply', {
                    'kit_id': CLIENT_ID,
                    'request_from': kit_id,
                    'cmd': 'trace_vars',
                    'data': values,
                    'isDone': False,
                    'code': 0
                })
                
                report_count += 1
                failed_reads = 0  # Reset failure counter on success
                
                # Show every successful read for debugging
                print(f"[Auto-Report #{report_count}] Variables: {values}")
            
            elif "error" in values:
                failed_reads += 1
                print(f"Variable read error ({failed_reads}/{MAX_FAILED_READS}): {values['error']}")
                
                if failed_reads >= MAX_FAILED_READS:
                    print(f"Too many consecutive failures ({failed_reads}), stopping monitoring")
                    break
            
            # Check if max duration exceeded
            elapsed_time = time.time() - start_time
            if elapsed_time >= MAX_DURATION_SECONDS:
                print(f"⏱️ Max duration reached ({MAX_DURATION_SECONDS}s), stopping monitoring")
                break
            
            # Configurable monitoring interval
            await asyncio.sleep(MONITORING_INTERVAL)
        
        # Final statistics
        final_time = time.time() - start_time
        print(f"Auto-monitoring completed: {report_count} reports in {final_time:.1f}s")
        
    except Exception as e:
        print(f"Error in auto memory monitoring: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        cleanup_auto_monitoring()

# Test function with configurable parameters
async def test_auto_monitoring(variables="", interval=0.1, duration=300, max_reports=10000):
    """Test the automatic monitoring system with configurable parameters.
    
    Args:
        variables: Comma-separated list of variables to monitor (empty = all)
        interval: Monitoring interval in seconds
        duration: Max monitoring duration in seconds
        max_reports: Maximum number of reports
    """
    print("=== Testing Automatic Memory Monitoring ===")
    print(f"Configuration: interval={interval}s, duration={duration}s, max_reports={max_reports}")
    
    # Use provided variables or default ones
    watch_vars = variables if variables else "ego_speed,current_lane,tri_value"
    
    result, msg = await start_auto_monitoring(watch_vars)
    print(f"Setup result: {result} - {msg}")
    
    if "success" in result:
        # Calculate how many reads to do based on duration and interval
        num_reads = min(int(duration / interval), max_reports, 100)  # Cap at 100 for test
        
        print(f"Performing {num_reads} test reads...")
        for i in range(num_reads):
            values, status = await get_auto_variables()
            print(f"Read {i+1}: {values} (status: {status})")
            await asyncio.sleep(interval)
            
            # Stop if process died
            if status == "error" and "exited" in str(values.get("error", "")):
                print("Process exited, stopping test")
                break
    
    cleanup_auto_monitoring()
    print("=== Test completed ===")

def parse_arguments():
    """Parse command-line arguments for monitoring configuration."""
    parser = argparse.ArgumentParser(
        description='Automatic C++ Memory Monitoring System',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        '--interval', '-i',
        type=float,
        default=0.1,
        help='Monitoring interval in seconds (e.g., 0.1 for real-time, 1 for normal, 2 for conservative)'
    )
    
    parser.add_argument(
        '--duration', '-d',
        type=float,
        default=300,
        help='Maximum monitoring duration in seconds'
    )
    
    parser.add_argument(
        '--max-reports', '-m',
        type=int,
        default=10000,
        help='Maximum number of reports to generate'
    )
    
    parser.add_argument(
        '--variables', '-v',
        type=str,
        default="",
        help='Comma-separated list of variables to monitor (empty = monitor all)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output for debugging'
    )
    
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    
    # Print configuration if verbose
    if args.verbose:
        print("🔧 Monitoring Configuration:")
        print(f"   Interval: {args.interval}s")
        print(f"   Duration: {args.duration}s")
        print(f"   Max Reports: {args.max_reports}")
        print(f"   Variables: {args.variables if args.variables else 'All detected variables'}")
    
    # Run the monitoring test with provided arguments
    asyncio.run(test_auto_monitoring(
        variables=args.variables,
        interval=args.interval,
        duration=args.duration,
        max_reports=args.max_reports
    ))