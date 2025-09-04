#!/usr/bin/env python3
"""
Automatic Memory Monitoring System
Automatically detects and monitors any C++ atomic variables without hardcoding.
"""

import os
import subprocess
import asyncio
import time
from pathlib import Path
from auto_variable_detector import AutoVariableDetector, SmartMemoryReader

# Configuration
APP_DIR = Path(os.path.dirname(__file__)) / 'app'
BINARY_FILE = APP_DIR / 'main_bin'
CLIENT_ID = "RunTime-TriCPP"

class AutoMemoryMonitor:
    """Automatic memory monitoring system."""
    
    def __init__(self):
        self.detector = AutoVariableDetector()
        self.memory_reader = None
        self.process = None
        self.monitorable_vars = []
    
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
        
        # Monitor only requested variables
        requested_names = [v.strip() for v in watch_vars_str.split(',')]
        filtered = []
        
        for var in self.monitorable_vars:
            if var['name'] in requested_names and var['found_in_binary']:
                filtered.append(var)
        
        # Also check for partial matches
        if len(filtered) < len(requested_names):
            for var in self.monitorable_vars:
                if var['found_in_binary']:
                    for req_name in requested_names:
                        if req_name in var['name'] and var not in filtered:
                            filtered.append(var)
                            break
        
        print(f"📈 Monitoring {len(filtered)} requested variables: {[v['name'] for v in filtered]}")
        return filtered
    
    def start_process(self) -> bool:
        """Start the C++ process for monitoring."""
        try:
            print(f"🚀 Starting C++ binary: {BINARY_FILE}")
            self.process = subprocess.Popen([str(BINARY_FILE)], 
                                         stdout=subprocess.PIPE, 
                                         stderr=subprocess.PIPE)
            
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
        
        # Step 3: Discover variables
        if not auto_monitor.discover_variables(cpp_code, str(BINARY_FILE)):
            return ("error", "No variables discovered in C++ code")
        
        # Step 4: Filter to requested variables
        auto_monitor.vars_to_monitor = auto_monitor.filter_requested_variables(watch_vars_str)
        
        if not auto_monitor.vars_to_monitor:
            return ("error", f"No requested variables found: {watch_vars_str}")
        
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

async def periodic_auto_memory_report(socketio, kit_id, watch_vars_str):
    """Generate periodic memory variable reports using auto-detection."""
    global auto_monitor
    
    print(f"🎯 Starting automatic variable monitoring for kit {kit_id}")
    
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
        
        # Monitoring loop with conservative timing to avoid killing process
        report_count = 0
        max_reports = 60  # Reduced from 300 to 60 reports (1 minute)
        failed_reads = 0
        max_failed_reads = 3
        
        # Give process time to fully initialize
        await asyncio.sleep(2)
        
        while report_count < max_reports and auto_monitor.process.poll() is None:
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
                print(f"Variable read error ({failed_reads}/{max_failed_reads}): {values['error']}")
                
                if failed_reads >= max_failed_reads:
                    print(f"Too many consecutive failures ({failed_reads}), stopping monitoring")
                    break
            
            # Conservative 2-second intervals to reduce ptrace pressure
            await asyncio.sleep(2)
        
        print(f"Auto-monitoring completed after {report_count} reports")
        
    except Exception as e:
        print(f"Error in auto memory monitoring: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        cleanup_auto_monitoring()

# Test function
async def test_auto_monitoring():
    """Test the automatic monitoring system."""
    print("=== Testing Automatic Memory Monitoring ===")
    
    result, msg = await start_auto_monitoring("ego_speed,current_lane")
    print(f"Setup result: {result} - {msg}")
    
    if "success" in result:
        # Test a few reads
        for i in range(5):
            values, status = await get_auto_variables()
            print(f"Read {i+1}: {values} (status: {status})")
            await asyncio.sleep(1)
    
    cleanup_auto_monitoring()

if __name__ == "__main__":
    asyncio.run(test_auto_monitoring())