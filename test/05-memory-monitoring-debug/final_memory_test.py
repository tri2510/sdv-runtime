#!/usr/bin/env python3
"""
Final test to get memory reading working by checking process state carefully.
"""

import subprocess
import time
import ctypes
import os
import signal

def test_process_state():
    """Test step by step to identify the issue."""
    
    APP_DIR = '/home/htr1hc/01_SDV/59_integrate_sdv-runtime_cpp/sdv-runtime-fork/kuksa-syncer/app'
    BINARY_FILE = f'{APP_DIR}/test_simple'
    
    print("=== Final Memory Reading Test ===")
    
    # Start the process
    print("🚀 Starting process...")
    process = subprocess.Popen([BINARY_FILE])
    
    print(f"✅ Process started with PID {process.pid}")
    
    # Wait for process to start
    time.sleep(1)
    
    # Check if process is still running
    if process.poll() is not None:
        print(f"❌ Process already exited with code {process.returncode}")
        return False
    
    print("✅ Process is still running")
    
    # Check process status before ptrace
    try:
        with open(f'/proc/{process.pid}/stat', 'r') as f:
            stat_info = f.read().split()
            state = stat_info[2]  # Process state
            print(f"📊 Process state before ptrace: {state}")
    except:
        print("⚠ Could not read process state")
    
    # Try ptrace attach
    print("🔗 Attaching ptrace...")
    libc = ctypes.CDLL("libc.so.6")
    PTRACE_ATTACH = 16
    PTRACE_DETACH = 17
    PTRACE_PEEKDATA = 2
    
    # Set up errno checking
    libc.__errno_location.restype = ctypes.POINTER(ctypes.c_int)
    
    result = libc.ptrace(PTRACE_ATTACH, process.pid, 0, 0)
    errno_val = libc.__errno_location().contents.value
    
    if result == -1:
        print(f"❌ ptrace attach failed: errno {errno_val} - {os.strerror(errno_val)}")
        process.terminate()
        return False
    
    print("✅ ptrace attach successful")
    
    # Wait for attach to complete and check process state
    time.sleep(0.5)
    
    # Check process state after attach
    try:
        with open(f'/proc/{process.pid}/stat', 'r') as f:
            stat_info = f.read().split()
            state = stat_info[2]
            print(f"📊 Process state after ptrace attach: {state}")
    except Exception as e:
        print(f"⚠ Could not read process state after attach: {e}")
        # Process might be gone
        if process.poll() is not None:
            print(f"❌ Process exited during ptrace with code {process.returncode}")
            return False
    
    # Check if process is still alive
    if process.poll() is not None:
        print(f"❌ Process died during ptrace attach (exit code: {process.returncode})")
        return False
    
    # Don't continue the process yet - try to read memory while it's stopped
    print("🔍 Attempting memory read while process is stopped...")
    
    # Get data section address
    try:
        with open(f'/proc/{process.pid}/maps', 'r') as f:
            maps_content = f.read()
            data_section_addr = None
            print("📄 Memory maps:")
            for line in maps_content.split('\n')[:10]:  # Show first 10 lines
                if line.strip():
                    print(f"   {line}")
                if 'test_simple' in line and 'rw-p' in line:
                    parts = line.split()
                    addr_range = parts[0]
                    start_addr = int(addr_range.split('-')[0], 16)
                    data_section_addr = start_addr
                    print(f"   ✅ Found data section at: 0x{start_addr:x}")
                    break
    except Exception as e:
        print(f"❌ Error reading memory maps: {e}")
        libc.ptrace(PTRACE_DETACH, process.pid, 0, 0)
        process.terminate()
        return False
    
    if not data_section_addr:
        print("❌ Could not find data section")
        libc.ptrace(PTRACE_DETACH, process.pid, 0, 0)
        process.terminate()
        return False
    
    # Try reading memory while process is stopped
    test_counter_addr = data_section_addr + (0x4010 - 0x4000)
    print(f"🎯 Attempting to read test_counter at 0x{test_counter_addr:x}")
    
    data = libc.ptrace(PTRACE_PEEKDATA, process.pid, test_counter_addr, 0)
    errno_val = libc.__errno_location().contents.value
    
    if data == -1:
        print(f"❌ Memory read failed: errno {errno_val} - {os.strerror(errno_val)}")
        libc.ptrace(PTRACE_DETACH, process.pid, 0, 0)
        process.terminate()
        return False
    
    # Success!
    int_val = ctypes.c_int32(data & 0xFFFFFFFF).value
    print(f"🎉 SUCCESS! Read test_counter: 0x{data:x} (int value: {int_val})")
    
    # Try reading the float value too
    test_value_addr = data_section_addr + (0x4014 - 0x4000)
    print(f"🎯 Attempting to read test_value at 0x{test_value_addr:x}")
    
    data = libc.ptrace(PTRACE_PEEKDATA, process.pid, test_value_addr, 0)
    errno_val = libc.__errno_location().contents.value
    
    if data == -1:
        print(f"❌ Memory read failed: errno {errno_val} - {os.strerror(errno_val)}")
    else:
        import struct
        float_bytes = struct.pack('<Q', data)[:4]
        float_val = struct.unpack('<f', float_bytes)[0]
        print(f"🎉 SUCCESS! Read test_value: 0x{data:x} (float value: {float_val})")
    
    # Clean up
    print("🧹 Detaching and cleaning up...")
    libc.ptrace(PTRACE_DETACH, process.pid, 0, 0)
    process.terminate()
    process.wait()
    
    return True

if __name__ == "__main__":
    success = test_process_state()
    if success:
        print("\n✅ Memory reading works! The issue was continuing the process too early.")
    else:
        print("\n❌ Still having issues with memory reading.")