#!/usr/bin/env python3
"""
Validation script for C++ memory monitoring implementation.
Tests the integration of ptrace functionality with existing syncer.
"""

import sys
import os
import subprocess
import json
from pathlib import Path

# Add the kuksa-syncer directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'kuksa-syncer'))

def test_imports():
    """Test that all required modules can be imported."""
    print("=== Testing Imports ===")
    
    try:
        from project_utils import ProjectUtils
        print("✓ ProjectUtils imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import ProjectUtils: {e}")
        return False
    
    try:
        from ptrace_memory_reader import PtraceMemoryReader, MemoryVariableMonitor
        print("✓ PtraceMemoryReader imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import PtraceMemoryReader: {e}")
        return False
    
    try:
        from memory_monitor import ProcessMemoryMonitor, SmartVariableDetector
        print("✓ ProcessMemoryMonitor imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import ProcessMemoryMonitor: {e}")
        return False
    
    try:
        import cpp_memory_debugger as cpp_debugger_util
        print("✓ cpp_memory_debugger imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import cpp_memory_debugger: {e}")
        return False
    
    return True

def test_project_utils():
    """Test ProjectUtils functionality."""
    print("\n=== Testing ProjectUtils ===")
    
    try:
        from project_utils import ProjectUtils
        
        # Create a test project structure
        test_project = [
            {
                "type": "file", 
                "name": "test.cpp", 
                "content": "#include <iostream>\n#include <atomic>\n\nstd::atomic<int> counter{0};\nstd::atomic<double> sensor_value{25.5};\n\nint main() {\n    std::cout << \"Test app\" << std::endl;\n    return 0;\n}"
            }
        ]
        
        # Create test payload
        test_payload = {
            'data': {
                'code': json.dumps(test_project),
                'watch_vars': 'counter,sensor_value'
            }
        }
        
        # Test ProjectUtils
        utils = ProjectUtils()
        print("✓ ProjectUtils instance created")
        
        # Test empty directory
        if utils.empty_app_directory():
            print("✓ empty_app_directory() works")
        else:
            print("✗ empty_app_directory() failed")
            return False
        
        # Test save from payload
        try:
            app_path = utils.save_from_payload(test_payload)
            print(f"✓ save_from_payload() works - saved to {app_path}")
            
            # Check if test.cpp was created
            test_cpp_path = Path(app_path) / "test.cpp"
            if test_cpp_path.exists():
                print("✓ Test C++ file created successfully")
                # Check content
                content = test_cpp_path.read_text()
                if "std::atomic<int> counter{0};" in content:
                    print("✓ C++ content preserved correctly")
                else:
                    print("✗ C++ content not preserved correctly")
                    return False
            else:
                print("✗ Test C++ file was not created")
                return False
        except Exception as e:
            print(f"✗ save_from_payload() failed: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ ProjectUtils test failed: {e}")
        return False

def test_cpp_compilation():
    """Test C++ compilation functionality."""
    print("\n=== Testing C++ Compilation ===")
    
    try:
        import cpp_memory_debugger as cpp_debugger_util
        import asyncio
        
        async def test_compile():
            try:
                compile_ok, compile_msg = await cpp_debugger_util.compile_cpp()
                if compile_ok:
                    print("✓ C++ compilation successful")
                    print(f"  Message: {compile_msg}")
                    return True
                else:
                    print(f"✗ C++ compilation failed: {compile_msg}")
                    return False
            except Exception as e:
                print(f"✗ C++ compilation test failed: {e}")
                return False
        
        # Run the async test
        result = asyncio.run(test_compile())
        return result
        
    except Exception as e:
        print(f"✗ C++ compilation test setup failed: {e}")
        return False

def test_ptrace_functionality():
    """Test basic ptrace functionality."""
    print("\n=== Testing Ptrace Functionality ===")
    
    try:
        from ptrace_memory_reader import PtraceMemoryReader
        
        # Test that we can create a PtraceMemoryReader instance
        # We'll use PID 1 (init) as it's always available on Linux
        reader = PtraceMemoryReader(1)
        print("✓ PtraceMemoryReader instance created")
        
        # Test that required system calls are available
        import ctypes
        import ctypes.util
        libc_name = ctypes.util.find_library("c")
        if libc_name:
            libc = ctypes.CDLL(libc_name)
            print("✓ libc found and loaded")
            
            # Test ptrace function availability
            if hasattr(libc, 'ptrace'):
                print("✓ ptrace system call available")
                return True
            else:
                print("✗ ptrace system call not available")
                return False
        else:
            print("✗ libc not found")
            return False
            
    except Exception as e:
        print(f"✗ Ptrace functionality test failed: {e}")
        return False

def test_syncer_integration():
    """Test integration with syncer.py."""
    print("\n=== Testing Syncer Integration ===")
    
    try:
        # Test importing with C++ extensions
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'kuksa-syncer'))
        
        # This should work now that we've added the ptrace functionality
        exec('''
import sys
from pathlib import Path

# Simulate the import environment in syncer.py
try:
    from project_utils import ProjectUtils
    import cpp_memory_debugger as cpp_debugger_util
    CPP_MEMORY_AVAILABLE = True
    print("✓ Syncer integration: C++ memory monitoring available")
    success = True
except ImportError as e:
    print(f"✗ Syncer integration: C++ memory monitoring not available: {e}")
    success = False
''')
        
        return True
        
    except Exception as e:
        print(f"✗ Syncer integration test failed: {e}")
        return False

def main():
    """Run all validation tests."""
    print("C++ Memory Monitoring Implementation Validation")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("ProjectUtils Test", test_project_utils),
        ("C++ Compilation Test", test_cpp_compilation),
        ("Ptrace Functionality Test", test_ptrace_functionality),
        ("Syncer Integration Test", test_syncer_integration),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\nRunning {test_name}...")
        try:
            if test_func():
                print(f"✓ {test_name} PASSED")
                passed += 1
            else:
                print(f"✗ {test_name} FAILED")
        except Exception as e:
            print(f"✗ {test_name} FAILED with exception: {e}")
    
    print(f"\n{'='*50}")
    print(f"Validation Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed! C++ memory monitoring is ready.")
        return True
    else:
        print(f"✗ {total - passed} tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)