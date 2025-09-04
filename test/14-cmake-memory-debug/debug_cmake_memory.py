#!/usr/bin/env python3
"""
Debug memory reading issues with CMake-built binaries.
"""

import sys
import subprocess
import time
from pathlib import Path

# Add kuksa-syncer to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'kuksa-syncer'))

def debug_cmake_memory_reading():
    """Debug why memory reading fails for CMake binaries."""
    
    print("🔍 CMake Memory Reading Debug")
    print("=" * 50)
    
    try:
        from auto_variable_detector import AutoVariableDetector
        
        # Path to CMake binary
        cmake_binary = Path(__file__).parent.parent.parent / 'kuksa-syncer' / 'app' / 'build' / 'autonomous_vehicle_system'
        main_cpp = Path(__file__).parent.parent.parent / 'kuksa-syncer' / 'app' / 'main.cpp'
        
        if not cmake_binary.exists():
            print(f"❌ CMake binary not found: {cmake_binary}")
            return False
            
        if not main_cpp.exists():
            print(f"❌ main.cpp not found: {main_cpp}")
            return False
            
        print(f"📁 CMake binary: {cmake_binary}")
        print(f"📄 Source file: {main_cpp}")
        
        # Read source code
        with open(main_cpp, 'r') as f:
            cpp_code = f.read()
        
        # Test variable detection
        detector = AutoVariableDetector()
        detected_vars = detector.auto_detect_variables(cpp_code, str(cmake_binary))
        
        if not detected_vars:
            print("❌ No variables detected")
            return False
            
        print(f"\n🔍 Detected {len(detected_vars)} variables:")
        for var in detected_vars:
            if var['found_in_binary']:
                print(f"   ✅ {var['name']}: {var['type']} @ 0x{var['symbol_address']:x}")
            else:
                print(f"   ❌ {var['name']}: {var['type']} (not found in binary)")
        
        # Filter to specific test variables
        test_vars = [var for var in detected_vars if var['found_in_binary'] and var['name'] in ['vehicle_speed', 'current_gear']]
        
        if not test_vars:
            print("❌ No test variables found")
            return False
            
        print(f"\n🎯 Testing memory reading with {len(test_vars)} variables...")
        
        # Start the process manually for debugging
        print(f"🚀 Starting CMake binary: {cmake_binary}")
        process = subprocess.Popen([str(cmake_binary)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Give it time to initialize
        time.sleep(1.0)
        
        if process.poll() is not None:
            print(f"❌ Process exited immediately with code {process.returncode}")
            return False
            
        print(f"✅ Process started with PID {process.pid}")
        
        # Check /proc/pid/maps
        with open(f'/proc/{process.pid}/maps', 'r') as f:
            maps = f.read()
        
        print(f"\n📄 Memory maps for PID {process.pid}:")
        for line in maps.split('\n'):
            if 'autonomous_vehicle_system' in line and 'rw-p' in line:
                print(f"   🏠 {line}")
        
        # Now test memory reading
        print(f"\n🧪 Testing memory reader...")
        from auto_variable_detector import SmartMemoryReader
        
        # Find data section base
        base_address = None
        for line in maps.split('\n'):
            if 'autonomous_vehicle_system' in line and 'rw-p' in line:
                parts = line.split()
                if len(parts) >= 6:
                    addr_range = parts[0]
                    start_addr = addr_range.split('-')[0]
                    base_address = int(start_addr, 16)
                    print(f"   🏠 Found data section base: 0x{base_address:x}")
                    break
        
        if not base_address:
            print("❌ Could not find data section base address")
            process.terminate()
            return False
        
        # Create memory reader (let attach() calculate base address automatically)
        memory_reader = SmartMemoryReader(process.pid)
        
        if not memory_reader.attach():
            print("❌ Failed to attach memory reader")
            process.terminate()
            return False
            
        print(f"✅ Memory reader attached successfully (base: 0x{memory_reader.base_address:x})")
        
        # Test reading each variable with detailed address calculation
        print(f"\n📊 Testing variable reads:")
        success_count = 0
        
        for var in test_vars:
            symbol_offset = var['symbol_address']
            final_address = memory_reader.base_address + symbol_offset
            print(f"\n🔍 Testing {var['name']} ({var['type']})")
            print(f"   📍 Symbol offset: 0x{symbol_offset:x}")
            print(f"   🏠 Base address: 0x{memory_reader.base_address:x}")
            print(f"   🎯 Final address: 0x{final_address:x}")
            
            # Check if the address is within valid memory ranges
            valid_range = False
            for line in maps.split('\n'):
                if line.strip() and '-' in line:
                    parts = line.split()
                    if len(parts) >= 1:
                        addr_range = parts[0]
                        if '-' in addr_range:
                            start_str, end_str = addr_range.split('-')
                            start_addr = int(start_str, 16)
                            end_addr = int(end_str, 16)
                            if start_addr <= final_address < end_addr:
                                valid_range = True
                                print(f"   ✅ Address is within valid range: {line.strip()}")
                                break
            
            if not valid_range:
                print(f"   ❌ Address 0x{final_address:x} is NOT within any valid memory range")
                continue
            
            # Try multiple read attempts
            for attempt in range(3):
                value = memory_reader.read_variable_value(var)
                if value is not None:
                    print(f"   ✅ Attempt {attempt+1}: {var['name']} = {value}")
                    success_count += 1
                    break
                else:
                    print(f"   ❌ Attempt {attempt+1}: Failed to read {var['name']}")
                
                time.sleep(0.5)
        
        # Clean up
        memory_reader.detach()
        process.terminate()
        process.wait()
        
        print(f"\n📊 Results: {success_count}/{len(test_vars) * 3} successful reads")
        
        return success_count > 0
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting CMake Memory Reading Debug...")
    
    success = debug_cmake_memory_reading()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ DEBUG SUCCESS: Found working memory reads")
    else:
        print("❌ DEBUG FAILED: Memory reading not working")