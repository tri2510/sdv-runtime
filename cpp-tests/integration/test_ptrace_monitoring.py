#!/usr/bin/env python3
"""
Quick test of the ptrace memory monitoring functionality.
This script runs the test app and monitors its variables.
"""

import sys
import os
import time
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from support.build_support import ensure_ptrace_test_binary, PTRACE_TEST_BINARY

# Add kuksa-syncer to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'kuksa-syncer'))

from ptrace_memory_reader import MemoryVariableMonitor

def test_ptrace_monitoring():
    """Test the ptrace-based monitoring with the test app."""
    
    ensure_ptrace_test_binary()
    test_binary = str(PTRACE_TEST_BINARY)
    
    print(f"Testing ptrace memory monitoring with {test_binary}")
    
    monitor = MemoryVariableMonitor(test_binary)
    monitor.build_symbol_table()
    
    if not monitor.start_process():
        print("Failed to start monitoring")
        return False
    
    # Define variables to monitor (from test_app.cpp)
    variables = {
        'counter': 'int',
        'sensor_value': 'double'
    }
    
    print(f"\n=== Starting variable monitoring ===")
    print(f"Monitoring PID: {monitor.process.pid}")
    print(f"Variables: {list(variables.keys())}")
    
    try:
        for i in range(15):  # Monitor for 15 iterations
            # Try both memory reading and stdout parsing
            memory_values = monitor.monitor_variables(variables)
            stdout_values = monitor.parse_stdout_variables()
            
            print(f"[{i+1:2d}] Memory: {memory_values} | Stdout: {stdout_values}")
            
            # Check if process is still running
            if monitor.process.poll() is not None:
                print(f"Process has exited with code {monitor.process.returncode}")
                break
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        monitor.cleanup()
        print("Monitoring completed successfully!")
    
    return True

if __name__ == "__main__":
    success = test_ptrace_monitoring()
    sys.exit(0 if success else 1)
