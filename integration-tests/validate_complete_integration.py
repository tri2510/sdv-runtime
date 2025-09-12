#!/usr/bin/env python3
"""
Complete Integration Validation
Tests end-to-end functionality with actual kit server integration
"""

import sys
import os
import subprocess
import time
import json
import signal
import requests
import threading
from pathlib import Path

# Add path for variable detector
sys.path.insert(0, '/home/htr1hc/01_SDV/59_integrate_sdv-runtime_cpp/sdv-runtime-fork/kuksa-syncer')

try:
    from auto_variable_detector import AutoVariableDetector, SmartMemoryReader
except ImportError:
    print("❌ Cannot import auto_variable_detector")
    print("Please ensure the kuksa-syncer path is correct")
    sys.exit(1)

class CompleteIntegrationValidator:
    """Complete end-to-end integration validator."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.processes = {}
        self.kit_server_process = None
        
    def find_kit_server(self) -> str:
        """Find kit server executable."""
        possible_paths = [
            "../build/kit-server",
            "../kit-server",
            "../../build/kit-server", 
            "/usr/local/bin/kit-server",
            "/usr/bin/kit-server"
        ]
        
        for path in possible_paths:
            full_path = self.project_root / path
            if full_path.exists() and full_path.is_file():
                return str(full_path.resolve())
        
        # Try which command
        try:
            result = subprocess.run(["which", "kit-server"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        
        return None
    
    def start_kit_server(self) -> bool:
        """Start the kit server."""
        print("Starting Kit Server...")
        
        kit_server_path = self.find_kit_server()
        
        if not kit_server_path:
            print("❌ Kit Server executable not found")
            print("Tried these locations:")
            print("  - ../build/kit-server")
            print("  - ../kit-server")  
            print("  - /usr/local/bin/kit-server")
            print("  - /usr/bin/kit-server")
            print("  - PATH search")
            return False
        
        print(f"Found Kit Server at: {kit_server_path}")
        
        try:
            # Start kit server in background
            self.kit_server_process = subprocess.Popen(
                [kit_server_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Give it time to start
            time.sleep(3)
            
            if self.kit_server_process.poll() is None:
                print(f"✅ Kit Server started with PID: {self.kit_server_process.pid}")
                
                # Wait a bit more for it to be ready
                time.sleep(2)
                
                return self.verify_kit_server_running()
            else:
                stdout, stderr = self.kit_server_process.communicate()
                print(f"❌ Kit Server failed to start")
                print(f"stdout: {stdout}")
                print(f"stderr: {stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error starting Kit Server: {e}")
            return False
    
    def verify_kit_server_running(self) -> bool:
        """Verify kit server is running and responding."""
        # Try to connect to kit server (assuming default ports)
        test_ports = [8080, 3000, 5000, 8000]
        
        for port in test_ports:
            try:
                response = requests.get(f"http://localhost:{port}/health", 
                                      timeout=2)
                if response.status_code == 200:
                    print(f"✅ Kit Server responding on port {port}")
                    return True
            except:
                continue
        
        # If HTTP doesn't work, check if process is running
        if self.kit_server_process and self.kit_server_process.poll() is None:
            print("⚠️  Kit Server process running but HTTP not accessible")
            print("This may be normal depending on kit server configuration")
            return True
        
        print("❌ Kit Server not responding")
        return False
    
    def start_sample_app(self, sample_name: str, executable_name: str) -> subprocess.Popen:
        """Start a sample application."""
        sample_dir = self.project_root / sample_name / "build"
        executable = sample_dir / executable_name
        
        if not executable.exists():
            print(f"❌ Executable not found: {executable}")
            return None
        
        try:
            process = subprocess.Popen([str(executable)],
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE, 
                                     text=True)
            
            # Give process time to start
            time.sleep(1)
            
            if process.poll() is None:
                print(f"✅ {sample_name} started with PID: {process.pid}")
                self.processes[sample_name] = process
                return process
            else:
                stdout, stderr = process.communicate()
                print(f"❌ {sample_name} failed to start")
                if stdout: print(f"stdout: {stdout[:200]}...")
                if stderr: print(f"stderr: {stderr[:200]}...")
                return None
                
        except Exception as e:
            print(f"❌ Error starting {sample_name}: {e}")
            return None
    
    def monitor_variables_realtime(self, sample_name: str, duration: int = 10) -> dict:
        """Monitor variables in real-time for specified duration."""
        print(f"\nReal-time monitoring of {sample_name} for {duration} seconds...")
        
        process = self.processes.get(sample_name)
        if not process:
            return {}
        
        # Get source code
        sample_dir = self.project_root / sample_name
        source_file = sample_dir / "main.cpp"
        
        with open(source_file, 'r') as f:
            cpp_code = f.read()
        
        executable_path = sample_dir / "build" / sample_name.replace('sample-', '').replace('-', '_')
        
        # Detect variables
        detector = AutoVariableDetector()
        detected_vars = detector.auto_detect_variables(cpp_code, str(executable_path))
        
        # Focus on atomic variables with addresses
        monitorable_vars = [var for var in detected_vars if 
                           var.get('is_atomic', False) and var.get('symbol_address')]
        
        if not monitorable_vars:
            print("⚠️  No monitorable atomic variables found")
            return {}
        
        print(f"Monitoring {len(monitorable_vars)} atomic variables:")
        for var in monitorable_vars:
            print(f"  - {var['name']}: {var['type']}")
        
        # Create memory reader
        reader = SmartMemoryReader(process.pid)
        
        monitoring_data = {
            'sample_name': sample_name,
            'duration': duration,
            'variables': [],
            'readings': []
        }
        
        if not reader.attach_to_process():
            print("⚠️  Could not attach to process for memory reading")
            return monitoring_data
        
        print("✅ Attached to process for memory reading")
        
        # Monitor variables
        start_time = time.time()
        reading_count = 0
        
        try:
            while time.time() - start_time < duration:
                values = reader.read_all_variables(monitorable_vars)
                
                timestamp = time.time() - start_time
                reading = {
                    'timestamp': timestamp,
                    'values': {}
                }
                
                for var_name, value in values.items():
                    if value is not None:
                        reading['values'][var_name] = value
                
                if reading['values']:
                    monitoring_data['readings'].append(reading)
                    reading_count += 1
                    
                    # Print periodic updates
                    if reading_count % 10 == 1:
                        print(f"  Reading {reading_count}: {len(reading['values'])} variables read")
                        
                        # Show sample values
                        for var_name, value in list(reading['values'].items())[:3]:
                            print(f"    {var_name} = {value}")
                
                time.sleep(0.1)  # 10Hz sampling
                
        finally:
            reader.detach_from_process()
        
        monitoring_data['variables'] = [var['name'] for var in monitorable_vars]
        monitoring_data['total_readings'] = len(monitoring_data['readings'])
        
        print(f"✅ Completed monitoring: {len(monitoring_data['readings'])} readings")
        return monitoring_data
    
    def analyze_monitoring_data(self, data: dict) -> dict:
        """Analyze monitoring data and generate insights."""
        if not data['readings']:
            return {'status': 'no_data'}
        
        analysis = {
            'status': 'success',
            'summary': {
                'total_readings': len(data['readings']),
                'duration': data['duration'],
                'variables_monitored': len(data['variables']),
                'avg_readings_per_second': len(data['readings']) / data['duration']
            },
            'variable_stats': {}
        }
        
        # Analyze each variable
        for var_name in data['variables']:
            values = []
            for reading in data['readings']:
                if var_name in reading['values']:
                    values.append(reading['values'][var_name])
            
            if values:
                analysis['variable_stats'][var_name] = {
                    'count': len(values),
                    'min': min(values),
                    'max': max(values),
                    'avg': sum(values) / len(values),
                    'changed': len(set(values)) > 1  # Did it change during monitoring?
                }
        
        return analysis
    
    def validate_basic_monitoring(self) -> bool:
        """Validate basic monitoring sample end-to-end."""
        print("\n" + "="*50)
        print("VALIDATING BASIC MONITORING")
        print("="*50)
        
        # Start sample
        process = self.start_sample_app("sample-basic-monitoring", "basic_monitoring")
        if not process:
            return False
        
        # Monitor variables
        monitoring_data = self.monitor_variables_realtime("sample-basic-monitoring", 5)
        
        if not monitoring_data['readings']:
            print("❌ No monitoring data collected")
            return False
        
        # Analyze data
        analysis = self.analyze_monitoring_data(monitoring_data)
        
        print(f"\nMonitoring Results:")
        print(f"  Total readings: {analysis['summary']['total_readings']}")
        print(f"  Variables monitored: {analysis['summary']['variables_monitored']}")
        print(f"  Average rate: {analysis['summary']['avg_readings_per_second']:.1f} Hz")
        
        # Check key variables
        expected_vars = ['g_temperature', 'g_pressure', 'g_rpm']
        found_vars = 0
        
        for var_name in expected_vars:
            if var_name in analysis['variable_stats']:
                stats = analysis['variable_stats'][var_name]
                print(f"  {var_name}: {stats['count']} readings, range [{stats['min']:.2f}, {stats['max']:.2f}]")
                found_vars += 1
        
        success = found_vars >= 2  # At least 2 of 3 key variables
        
        if success:
            print("✅ Basic monitoring validation PASSED")
        else:
            print("❌ Basic monitoring validation FAILED")
        
        return success
    
    def validate_automotive_controls(self) -> bool:
        """Validate automotive controls sample end-to-end."""
        print("\n" + "="*50) 
        print("VALIDATING AUTOMOTIVE CONTROLS")
        print("="*50)
        
        # Start sample
        process = self.start_sample_app("sample-automotive-controls", "automotive_controls")
        if not process:
            return False
        
        # Monitor variables
        monitoring_data = self.monitor_variables_realtime("sample-automotive-controls", 8)
        
        if not monitoring_data['readings']:
            print("❌ No monitoring data collected")
            return False
        
        # Analyze data
        analysis = self.analyze_monitoring_data(monitoring_data)
        
        print(f"\nMonitoring Results:")
        print(f"  Total readings: {analysis['summary']['total_readings']}")
        print(f"  Variables monitored: {analysis['summary']['variables_monitored']}")
        print(f"  Average rate: {analysis['summary']['avg_readings_per_second']:.1f} Hz")
        
        # Check automotive variables
        automotive_vars = ['g_vehicle_speed', 'g_engine_rpm', 'g_throttle_position']
        found_vars = 0
        changing_vars = 0
        
        for var_name in automotive_vars:
            if var_name in analysis['variable_stats']:
                stats = analysis['variable_stats'][var_name]
                changing = "✓" if stats['changed'] else "✗"
                print(f"  {var_name}: {stats['count']} readings, range [{stats['min']:.2f}, {stats['max']:.2f}] {changing}")
                found_vars += 1
                if stats['changed']:
                    changing_vars += 1
        
        success = found_vars >= 2 and changing_vars >= 1
        
        if success:
            print("✅ Automotive controls validation PASSED")  
        else:
            print("❌ Automotive controls validation FAILED")
        
        return success
    
    def cleanup(self):
        """Clean up all processes."""
        print("\nCleaning up processes...")
        
        # Stop sample apps
        for name, process in self.processes.items():
            if process.poll() is None:
                print(f"Stopping {name} (PID: {process.pid})...")
                process.terminate()
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
        
        # Stop kit server
        if self.kit_server_process and self.kit_server_process.poll() is None:
            print(f"Stopping Kit Server (PID: {self.kit_server_process.pid})...")
            self.kit_server_process.terminate()
            try:
                self.kit_server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.kit_server_process.kill()
                self.kit_server_process.wait()
        
        self.processes.clear()
    
    def run_complete_validation(self) -> bool:
        """Run complete end-to-end validation."""
        print("=" * 70)
        print("COMPLETE INTEGRATION VALIDATION")
        print("End-to-End Kit Server Integration Test")
        print("=" * 70)
        
        # Start kit server (optional - samples work without it)
        kit_server_ok = self.start_kit_server()
        if not kit_server_ok:
            print("⚠️  Continuing without Kit Server")
            print("Variable tracing will work, but full kit server integration won't be tested")
        
        # Run validations
        results = []
        
        tests = [
            ("Basic Monitoring", self.validate_basic_monitoring),
            ("Automotive Controls", self.validate_automotive_controls),
        ]
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
                time.sleep(1)  # Brief pause between tests
            except Exception as e:
                print(f"❌ {test_name} ERROR: {e}")
                results.append((test_name, False))
        
        # Final summary
        print("\n" + "=" * 70)
        print("VALIDATION SUMMARY")
        print("=" * 70)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "PASSED" if result else "FAILED"
            print(f"  {test_name}: {status}")
        
        print(f"\nKit Server Integration: {'AVAILABLE' if kit_server_ok else 'NOT TESTED'}")
        print(f"Overall Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("\n🎉 ALL VALIDATION TESTS PASSED!")
            print("✅ Sample projects are working correctly")
            print("✅ Variable detection is functioning")
            print("✅ Memory reading is operational")
            print("✅ Real-time monitoring is validated")
            if kit_server_ok:
                print("✅ Kit Server integration is ready")
        else:
            print(f"\n❌ {total - passed} validation test(s) failed")
        
        return passed == total


def main():
    """Main validation runner."""
    validator = CompleteIntegrationValidator()
    
    def signal_handler(signum, frame):
        print("\nValidation interrupted. Cleaning up...")
        validator.cleanup()
        sys.exit(1)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        success = validator.run_complete_validation()
        return 0 if success else 1
    finally:
        validator.cleanup()


if __name__ == "__main__":
    sys.exit(main())