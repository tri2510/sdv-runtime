#!/usr/bin/env python3
"""
Debug memory reading issues.
"""

import subprocess
import time
from pathlib import Path
import sys

# Add kuksa-syncer to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'kuksa-syncer'))

def debug_process_and_memory():
    """Debug why memory reading is not working."""
    
    APP_DIR = Path(__file__).parent / 'kuksa-syncer' / 'app'
    BINARY_FILE = APP_DIR / 'main_bin'
    
    print("=== Debug Memory Reading ===")
    print(f"Binary: {BINARY_FILE}")
    print(f"Binary exists: {BINARY_FILE.exists()}")
    
    # Test 1: Run binary standalone
    print("\n1️⃣ Testing binary standalone:")
    try:
        result = subprocess.run([str(BINARY_FILE)], capture_output=True, text=True, timeout=3)
        print(f"   Exit code: {result.returncode}")
        print(f"   Stdout: {result.stdout[:200]}...")
        if result.stderr:
            print(f"   Stderr: {result.stderr}")
    except subprocess.TimeoutExpired:
        print("   ✅ Binary runs (timed out as expected)")
    
    # Test 2: Start process and check memory maps
    print("\n2️⃣ Testing process memory maps:")
    process = subprocess.Popen([str(BINARY_FILE)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(0.5)
    
    if process.poll() is not None:
        print(f"   ❌ Process exited immediately with code {process.returncode}")
        stdout, stderr = process.communicate()
        print(f"   Stdout: {stdout.decode()}")
        print(f"   Stderr: {stderr.decode()}")
        return
    
    print(f"   ✅ Process running with PID {process.pid}")
    
    # Check memory maps
    try:
        with open(f'/proc/{process.pid}/maps', 'r') as f:
            maps = f.read()
            print("   📄 Memory maps:")
            for line in maps.split('\n')[:5]:  # Show first 5 lines
                if line.strip():
                    print(f"      {line}")
            print("      ...")
    except Exception as e:
        print(f"   ❌ Failed to read memory maps: {e}")
    
    # Test 3: Test ptrace attach
    print("\n3️⃣ Testing ptrace attach:")
    try:
        from auto_variable_detector import SmartMemoryReader
        
        reader = SmartMemoryReader(process.pid)
        attach_result = reader.attach()
        print(f"   Ptrace attach result: {'✅ Success' if attach_result else '❌ Failed'}")
        
        if attach_result:
            # Test 4: Test variable reading
            print("\n4️⃣ Testing variable reading:")
            
            # Get detected variables  
            from auto_variable_detector import AutoVariableDetector
            cpp_file = APP_DIR / "main.cpp"
            with open(cpp_file, 'r') as f:
                cpp_code = f.read()
            
            detector = AutoVariableDetector()
            all_vars = detector.auto_detect_variables(cpp_code, str(BINARY_FILE))
            monitorable_vars = [var for var in all_vars if var['found_in_binary']]
            
            print(f"   Variables to test: {len(monitorable_vars)}")
            
            # Try reading each variable
            for var in monitorable_vars[:4]:  # Test first 4 variables
                try:
                    value = reader.read_variable_value(var)
                    print(f"   📊 {var['name']}: {value} (type: {var['type']})")
                except Exception as e:
                    print(f"   ❌ {var['name']}: Error - {e}")
            
            # Test reading all variables
            values = reader.read_all_variables(monitorable_vars)
            print(f"   📋 All variables: {values}")
            
            reader.detach()
        
    except Exception as e:
        print(f"   ❌ Ptrace test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if process.poll() is None:
            process.terminate()
        print("\n🧹 Process terminated")

if __name__ == "__main__":
    debug_process_and_memory()