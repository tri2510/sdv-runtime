#!/usr/bin/env python3
"""
Kit Server Integration Test with Variable Detector
Tests sample projects using the auto_variable_detector system
"""

import sys
import os
import subprocess
import time
import json
import signal
from pathlib import Path

# Add path for variable detector
sys.path.insert(0, '/home/htr1hc/01_SDV/59_integrate_sdv-runtime_cpp/sdv-runtime-fork/kuksa-syncer')

try:
    from auto_variable_detector import AutoVariableDetector, SmartMemoryReader
except ImportError:
    print("❌ Cannot import auto_variable_detector")
    print("Please ensure the kuksa-syncer path is correct")
    sys.exit(1)

class KitServerIntegrationTester:
    """Test integration with kit server using variable detector."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.processes = {}
        
    def build_sample(self, sample_name: str) -> bool:
        """Build a specific sample project."""
        print(f"Building {sample_name}...")
        
        sample_dir = self.project_root / sample_name
        build_dir = sample_dir / "build"
        
        if not sample_dir.exists():
            print(f"❌ Sample directory not found: {sample_dir}")
            return False
        
        # Create build directory
        build_dir.mkdir(exist_ok=True)
        
        try:
            # CMake configure
            result = subprocess.run([
                "cmake", "..", "-DCMAKE_BUILD_TYPE=Release"
            ], cwd=build_dir, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ CMake failed: {result.stderr}")
                return False
            
            # Build
            result = subprocess.run([
                "make", "-j4"
            ], cwd=build_dir, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ Build failed: {result.stderr}")
                return False
            
            print(f"✅ {sample_name} built successfully")
            return True
            
        except Exception as e:
            print(f"❌ Build error: {e}")
            return False
    
    def start_sample(self, sample_name: str, executable_name: str) -> subprocess.Popen:
        """Start a sample application."""
        sample_dir = self.project_root / sample_name / "build"
        executable = sample_dir / executable_name
        
        if not executable.exists():
            print(f"❌ Executable not found: {executable}")
            return None
        
        print(f"Starting {sample_name}...")
        
        try:
            process = subprocess.Popen([str(executable)], 
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     text=True)
            
            # Give process time to start
            time.sleep(2)
            
            if process.poll() is None:
                print(f"✅ {sample_name} started with PID: {process.pid}")
                self.processes[sample_name] = process
                return process
            else:
                stdout, stderr = process.communicate()
                print(f"❌ {sample_name} failed to start")
                print(f"stdout: {stdout}")
                print(f"stderr: {stderr}")
                return None
                
        except Exception as e:
            print(f"❌ Error starting {sample_name}: {e}")
            return None
    
    def test_variable_detection(self, sample_name: str, expected_vars: list) -> bool:
        """Test variable detection on running sample."""
        print(f"\nTesting variable detection for {sample_name}...")
        
        process = self.processes.get(sample_name)
        if not process:
            print(f"❌ No running process for {sample_name}")
            return False
        
        pid = process.pid
        print(f"Analyzing process PID: {pid}")
        
        # Get source code for analysis
        sample_dir = self.project_root / sample_name
        source_file = sample_dir / "main.cpp"
        
        if not source_file.exists():
            print(f"❌ Source file not found: {source_file}")
            return False
        
        with open(source_file, 'r') as f:
            cpp_code = f.read()
        
        # Try to find the executable for binary analysis
        executable_path = sample_dir / "build" / sample_name.replace('sample-', '').replace('-', '_')
        
        # Create detector and analyze
        detector = AutoVariableDetector()
        
        try:
            detected_vars = detector.auto_detect_variables(cpp_code, str(executable_path))
            
            print(f"Detected {len(detected_vars)} variables:")
            for var in detected_vars:
                print(f"  - {var['name']}: {var['type']} ({'atomic' if var.get('is_atomic', False) else 'regular'})")
            
            # Check if expected variables were found
            found_vars = [var['name'] for var in detected_vars]
            missing_vars = [var for var in expected_vars if var not in found_vars]
            
            if missing_vars:
                print(f"⚠️  Missing expected variables: {missing_vars}")
            else:
                print(f"✅ All expected variables detected")
            
            # Test memory reading if we have variables with addresses
            addressable_vars = [var for var in detected_vars if var.get('symbol_address')]
            
            if addressable_vars:
                print(f"\nTesting memory reading for {len(addressable_vars)} variables...")
                
                reader = SmartMemoryReader(pid)
                
                if reader.attach_to_process():
                    print("✅ Successfully attached to process")
                    
                    # Try to read some variables
                    values = reader.read_all_variables(addressable_vars[:5])  # Test first 5
                    
                    print("Sample variable values:")
                    for var_name, value in values.items():
                        if value is not None:
                            print(f"  {var_name} = {value}")
                        else:
                            print(f"  {var_name} = <unable to read>")
                    
                    reader.detach_from_process()
                else:
                    print("⚠️  Could not attach to process (may need root privileges)")
            
            return len(detected_vars) > 0
            
        except Exception as e:
            print(f"❌ Variable detection failed: {e}")
            return False
    
    def test_basic_monitoring(self) -> bool:
        """Test the basic monitoring sample."""
        sample_name = "sample-basic-monitoring"
        executable_name = "basic_monitoring"
        
        expected_vars = [
            "g_temperature", "g_pressure", "g_humidity", "g_rpm",
            "g_system_active", "g_error_count", "g_voltage", "g_current"
        ]
        
        # Build and start
        if not self.build_sample(sample_name):
            return False
        
        process = self.start_sample(sample_name, executable_name)
        if not process:
            return False
        
        # Test variable detection
        result = self.test_variable_detection(sample_name, expected_vars)
        
        return result
    
    def test_automotive_controls(self) -> bool:
        """Test the automotive controls sample."""
        sample_name = "sample-automotive-controls"
        executable_name = "automotive_controls"
        
        expected_vars = [
            "g_vehicle_speed", "g_engine_rpm", "g_throttle_position", 
            "g_brake_pressure", "g_steering_angle", "g_target_speed",
            "g_engine_load", "g_fuel_consumption", "g_cruise_control",
            "g_abs_active", "g_gear_position", "g_coolant_temp"
        ]
        
        # Build and start
        if not self.build_sample(sample_name):
            return False
        
        process = self.start_sample(sample_name, executable_name)
        if not process:
            return False
        
        # Test variable detection  
        result = self.test_variable_detection(sample_name, expected_vars)
        
        return result
    
    def cleanup(self):
        """Clean up running processes."""
        print("\nCleaning up processes...")
        
        for name, process in self.processes.items():
            if process.poll() is None:
                print(f"Stopping {name} (PID: {process.pid})...")
                process.terminate()
                
                # Wait for graceful shutdown
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    print(f"Force killing {name}")
                    process.kill()
                    process.wait()
        
        self.processes.clear()
    
    def run_all_tests(self) -> bool:
        """Run all integration tests."""
        print("=" * 60)
        print("KIT SERVER INTEGRATION TESTS")
        print("Variable Detection and Memory Reading")
        print("=" * 60)
        
        tests = [
            ("Basic Monitoring", self.test_basic_monitoring),
            ("Automotive Controls", self.test_automotive_controls),
        ]
        
        results = []
        
        for test_name, test_func in tests:
            print(f"\n{'='*20} {test_name} {'='*20}")
            
            try:
                result = test_func()
                results.append((test_name, result))
                
                if result:
                    print(f"✅ {test_name} PASSED")
                else:
                    print(f"❌ {test_name} FAILED")
                    
                # Wait a bit between tests
                time.sleep(2)
                
            except Exception as e:
                print(f"❌ {test_name} ERROR: {e}")
                results.append((test_name, False))
        
        # Summary
        print("\n" + "=" * 60)
        print("INTEGRATION TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "PASSED" if result else "FAILED"
            print(f"  {test_name}: {status}")
        
        print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        success = passed == total
        
        if success:
            print("🎉 ALL INTEGRATION TESTS PASSED!")
        else:
            print("❌ Some integration tests failed")
        
        return success


def main():
    """Main test runner."""
    tester = KitServerIntegrationTester()
    
    def signal_handler(signum, frame):
        print("\nTest interrupted. Cleaning up...")
        tester.cleanup()
        sys.exit(1)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        success = tester.run_all_tests()
        return 0 if success else 1
        
    finally:
        tester.cleanup()


if __name__ == "__main__":
    sys.exit(main())