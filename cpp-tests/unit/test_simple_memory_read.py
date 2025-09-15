#!/usr/bin/env python3
"""
Test simple memory reading to isolate the issue.
"""

import subprocess
import time
import ctypes
import os
import signal

def test_simple_memory_read():
    """Test the most basic ptrace memory reading."""
    
    APP_DIR = '/home/htr1hc/01_SDV/59_integrate_sdv-runtime_cpp/sdv-runtime-fork/kuksa-syncer/app'
    BINARY_FILE = f'{APP_DIR}/test_simple'
    
    print("=== Simple Memory Read Test ===")
    
    # Start the process
    print("🚀 Starting process...")
    process = subprocess.Popen([BINARY_FILE], 
                             stdout=subprocess.PIPE, 
                             stderr=subprocess.PIPE)
    
    print(f"✅ Process started with PID {process.pid}")
    
    # Wait longer for the process to start and initialize variables
    print("⏱ Waiting for process initialization...")
    time.sleep(2)
    
    if process.poll() is not None:
        print(f"❌ Process exited early with code {process.returncode}")
        return
    
    # Test ptrace attachment
    print("🔗 Testing ptrace attachment...")
    libc = ctypes.CDLL("libc.so.6")
    PTRACE_ATTACH = 16
    PTRACE_DETACH = 17
    PTRACE_PEEKDATA = 2
    PTRACE_CONT = 7
    
    # Set errno to 0
    libc.__errno_location.restype = ctypes.POINTER(ctypes.c_int)
    
    result = libc.ptrace(PTRACE_ATTACH, process.pid, 0, 0)
    errno = libc.__errno_location().contents.value
    
    if result == -1:
        print(f"❌ ptrace attach failed with errno {errno}")
        print(f"   Error: {os.strerror(errno)}")
        process.terminate()
        return
    
    print("✅ ptrace attach successful")
    
    # Wait for attach to complete
    time.sleep(0.5)
    
    # Continue the process
    result = libc.ptrace(PTRACE_CONT, process.pid, 0, 0)
    if result == -1:
        errno = libc.__errno_location().contents.value
        print(f"⚠ ptrace continue returned -1, errno {errno}: {os.strerror(errno)}")
    else:
        print("✅ Process continued after attach")
    
    # Check memory maps
    print("📄 Checking memory maps...")
    try:
        with open(f'/proc/{process.pid}/maps', 'r') as f:
            maps = f.read()
            data_section_addr = None
            for line in maps.split('\n'):
                if 'test_simple' in line and 'rw-p' in line:
                    parts = line.split()
                    addr_range = parts[0]
                    start_addr = int(addr_range.split('-')[0], 16)
                    data_section_addr = start_addr
                    print(f"   📍 Found data section at: 0x{start_addr:x}")
                    break
            
            if not data_section_addr:
                print("   ❌ Could not find data section")
                libc.ptrace(PTRACE_DETACH, process.pid, 0, 0)
                process.terminate()
                return
                
    except Exception as e:
        print(f"   ❌ Error reading maps: {e}")
        libc.ptrace(PTRACE_DETACH, process.pid, 0, 0)
        process.terminate()
        return
    
    # Try to read from the data section directly
    print("🔍 Testing memory reads...")
    
    # Test 1: Read from data section start
    test_addr = data_section_addr
    print(f"   Test 1: Reading from data section start (0x{test_addr:x})...")
    data = libc.ptrace(PTRACE_PEEKDATA, process.pid, test_addr, 0)
    errno = libc.__errno_location().contents.value
    if data == -1:
        print(f"   ❌ Failed with errno {errno}: {os.strerror(errno)}")
    else:
        print(f"   ✅ Success: 0x{data:x}")
    
    # Test 2: Read test_counter location
    test_counter_addr = data_section_addr + (0x4010 - 0x4000)
    print(f"   Test 2: Reading test_counter (0x{test_counter_addr:x})...")
    data = libc.ptrace(PTRACE_PEEKDATA, process.pid, test_counter_addr, 0)
    errno = libc.__errno_location().contents.value
    if data == -1:
        print(f"   ❌ Failed with errno {errno}: {os.strerror(errno)}")
    else:
        print(f"   ✅ Success: 0x{data:x} (int value: {ctypes.c_int32(data & 0xFFFFFFFF).value})")
    
    # Test 3: Read test_value location  
    test_value_addr = data_section_addr + (0x4014 - 0x4000)
    print(f"   Test 3: Reading test_value (0x{test_value_addr:x})...")
    data = libc.ptrace(PTRACE_PEEKDATA, process.pid, test_value_addr, 0)
    errno = libc.__errno_location().contents.value
    if data == -1:
        print(f"   ❌ Failed with errno {errno}: {os.strerror(errno)}")
    else:
        # Parse as float
        import struct
        float_bytes = struct.pack('<Q', data)[:4]
        float_val = struct.unpack('<f', float_bytes)[0]
        print(f"   ✅ Success: 0x{data:x} (float value: {float_val})")
    
    # Clean up
    print("🧹 Cleaning up...")
    libc.ptrace(PTRACE_DETACH, process.pid, 0, 0)
    
    if process.poll() is None:
        process.terminate()
        process.wait()
    
    print("✅ Test completed")

if __name__ == "__main__":
    test_simple_memory_read()