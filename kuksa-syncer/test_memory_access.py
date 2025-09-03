#!/usr/bin/env python3
"""
Test memory access methods to find working solution.
"""

import subprocess
import time
import os
import sys

def test_gdb_access(binary_path, pid, var_name):
    """Test GDB-based variable reading."""
    print(f"\n=== Testing GDB access for PID {pid} ===")
    
    try:
        cmd = [
            'gdb', '--batch', '--quiet',
            '--eval-command', f'attach {pid}',
            '--eval-command', f'print {var_name}',
            '--eval-command', 'detach',
            '--eval-command', 'quit'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        
        print(f"GDB stdout: {result.stdout}")
        print(f"GDB stderr: {result.stderr}")
        print(f"Return code: {result.returncode}")
        
        # Parse result
        for line in result.stdout.split('\n'):
            if '$1 = ' in line:
                value = line.split('$1 = ')[1].strip()
                print(f"✓ Successfully read {var_name} = {value}")
                return value
                
    except Exception as e:
        print(f"✗ GDB test failed: {e}")
    
    return None

def test_direct_memory_access(pid, address):
    """Test direct /proc/pid/mem access."""
    print(f"\n=== Testing direct memory access for PID {pid} at 0x{address:x} ===")
    
    try:
        with open(f'/proc/{pid}/mem', 'rb') as mem_file:
            mem_file.seek(address)
            data = mem_file.read(4)
            
            if len(data) == 4:
                import struct
                value = struct.unpack('i', data)[0]
                print(f"✓ Successfully read memory: {value}")
                return value
            else:
                print(f"✗ Insufficient data read: {len(data)} bytes")
                
    except Exception as e:
        print(f"✗ Direct memory access failed: {e}")
    
    return None

def run_and_test_cpp_app():
    """Run C++ app and test different memory reading methods."""
    
    binary_path = "/home/htr1hc/01_SDV/59_integrate_sdv-runtime_cpp/sdv-runtime-fork/kuksa-syncer/app/main_bin"
    
    if not os.path.exists(binary_path):
        print(f"✗ Binary not found: {binary_path}")
        return
    
    print(f"Starting C++ application: {binary_path}")
    
    # Start the C++ application
    process = subprocess.Popen([binary_path], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE,
                               text=True)
    
    pid = process.pid
    print(f"✓ Started process PID: {pid}")
    
    # Let it initialize
    time.sleep(2)
    
    # Get symbol addresses
    print(f"\n=== Getting symbol addresses ===")
    nm_result = subprocess.run(['nm', binary_path], capture_output=True, text=True)
    
    symbols = {}
    for line in nm_result.stdout.split('\n'):
        if 'ego_speed' in line:
            parts = line.split()
            if len(parts) >= 3:
                address = int(parts[0], 16)
                symbols['ego_speed'] = address
                print(f"Found ego_speed at address: 0x{address:x}")
    
    if not symbols:
        print("✗ No symbols found")
        process.terminate()
        return
    
    # Test different methods
    methods_working = []
    
    # Method 1: GDB
    gdb_result = test_gdb_access(binary_path, pid, 'ego_speed')
    if gdb_result:
        methods_working.append("GDB")
    
    # Method 2: Direct memory access
    if 'ego_speed' in symbols:
        mem_result = test_direct_memory_access(pid, symbols['ego_speed'])
        if mem_result:
            methods_working.append("Direct Memory")
    
    # Method 3: Test stdout parsing
    print(f"\n=== Testing stdout parsing ===")
    try:
        stdout_data = process.stdout.read()
        if stdout_data:
            print(f"✓ Stdout available: {stdout_data[:200]}...")
            methods_working.append("Stdout Parsing")
    except:
        print("✗ Stdout parsing failed")
    
    # Cleanup
    process.terminate()
    process.wait()
    
    print(f"\n=== Results ===")
    print(f"Working methods: {methods_working}")
    
    if "GDB" in methods_working:
        print("✅ GDB method works - can use for production")
    elif "Direct Memory" in methods_working:
        print("✅ Direct memory method works")
    elif "Stdout Parsing" in methods_working:
        print("✅ Stdout parsing works - most reliable method")
    else:
        print("⚠️  Need to implement stdout-based monitoring")

if __name__ == "__main__":
    run_and_test_cpp_app()