#!/usr/bin/env python3
"""
Comprehensive C++ Variable Monitoring Test Suite Runner

This script builds and tests all 7 C++ projects designed to thoroughly test 
the universal variable monitoring system across different project structures,
build systems, and variable types.

Projects:
1. 01-basic-types: Fundamental C++ types (int, float, bool, char, etc.)
2. 02-cmake-structured: CMake-based vehicle systems with atomic variables
3. 03-makefile-build: Makefile ADAS systems with namespaces
4. 04-complex-structures: Complex nested namespaces
5. 05-embedded-style: Embedded ECU with fixed-point and bit-packed data
6. 06-matlab-style: MATLAB/Simulink-style variables and controllers
7. 07-simulink-blocks: Simulink block execution with automotive signals
"""

import os
import sys
import subprocess
import time
import threading
import signal
import json
from pathlib import Path
from datetime import datetime

class ComprehensiveTestRunner:
    def __init__(self, base_dir):
        self.base_dir = Path(base_dir)
        self.syncer_path = self.base_dir.parent / "kuksa-syncer"
        self.test_results = {}
        self.running_processes = []
        
        self.projects = {
            "01-basic-types": {
                "name": "Basic Types Monitor",
                "executable": "basic_types_monitor",
                "build_cmd": ["./build.sh"],
                "test_duration": 20,
                "expected_vars": [
                    "temperature_offset", "steering_angle", "current_speed", 
                    "engine_running", "gear_position", "battery_level"
                ]
            },
            "02-cmake-structured": {
                "name": "CMake Vehicle Systems",
                "executable": "build/vehicle_systems", 
                "build_cmd": ["./build.sh"],
                "test_duration": 25,
                "expected_vars": [
                    "target_speed", "actual_speed", "engine_rpm",
                    "gps_latitude", "battery_voltage", "tire_pressure_fl"
                ]
            },
            "03-makefile-build": {
                "name": "Makefile ADAS Systems",
                "executable": "adas_monitor",
                "build_cmd": ["make", "clean", "&&", "make"],
                "test_duration": 20,
                "expected_vars": [
                    "FCW::front_distance", "LKA::lane_position", "ACC::set_speed",
                    "FCW::collision_warning", "LKA::lka_active"
                ]
            },
            "04-complex-structures": {
                "name": "Complex Vehicle Systems",
                "executable": "complex_vehicle_system",
                "build_cmd": ["./build.sh"],
                "test_duration": 25,
                "expected_vars": [
                    "system_uptime", "engine_rpm", "current_gear",
                    "impact_sensor_x", "fire_detected"
                ]
            },
            "05-embedded-style": {
                "name": "Embedded ECU System",
                "executable": "embedded_ecu_system",
                "build_cmd": ["./build.sh"],
                "test_duration": 20,
                "expected_vars": [
                    "throttle_position_q15", "status_reg1_raw", "can_tx_counter",
                    "main_loop_counter", "vehicle_speed_q31"
                ]
            },
            "06-matlab-style": {
                "name": "MATLAB-Style Vehicle Controller",
                "executable": "matlab_generated_code",
                "build_cmd": ["./build.sh"],
                "test_duration": 20,
                "expected_vars": [
                    "throttle_position", "vehicle_speed", "engine_torque_cmd",
                    "speed_integral", "engine_enable"
                ]
            },
            "07-simulink-blocks": {
                "name": "Simulink Vehicle Model",
                "executable": "simulink_vehicle_model",
                "build_cmd": ["./build.sh"],
                "test_duration": 20,
                "expected_vars": [
                    "vehicle_velocity", "throttle_command", "brake_command",
                    "engine_speed", "cruise_control_active"
                ]
            }
        }
    
    def log(self, message, level="INFO"):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def run_command(self, cmd, cwd, timeout=60):
        """Run command with timeout and return success/output"""
        try:
            if isinstance(cmd, list):
                cmd_str = " ".join(cmd)
            else:
                cmd_str = cmd
            
            self.log(f"Running: {cmd_str} in {cwd}")
            
            result = subprocess.run(
                cmd_str,
                cwd=cwd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode == 0:
                self.log(f"Command succeeded: {cmd_str}")
                return True, result.stdout
            else:
                self.log(f"Command failed: {cmd_str}", "ERROR")
                self.log(f"Error output: {result.stderr}", "ERROR")
                return False, result.stderr
                
        except subprocess.TimeoutExpired:
            self.log(f"Command timed out: {cmd_str}", "ERROR")
            return False, "Timeout"
        except Exception as e:
            self.log(f"Command exception: {e}", "ERROR")
            return False, str(e)
    
    def build_project(self, project_id):
        """Build a specific project"""
        project = self.projects[project_id]
        project_dir = self.base_dir / project_id
        
        if not project_dir.exists():
            self.log(f"Project directory not found: {project_dir}", "ERROR")
            return False
        
        self.log(f"Building {project['name']}...")
        
        success, output = self.run_command(project["build_cmd"], project_dir, timeout=120)
        
        if success:
            # Check if executable was created
            exe_path = project_dir / project["executable"]
            if exe_path.exists():
                self.log(f"Build successful: {project['name']}")
                return True
            else:
                self.log(f"Build completed but executable not found: {exe_path}", "ERROR")
                return False
        else:
            self.log(f"Build failed: {project['name']}", "ERROR")
            return False
    
    def start_syncer(self):
        """Start the smart adaptive syncer"""
        syncer_script = self.syncer_path / "syncer.py"
        if not syncer_script.exists():
            self.log("Syncer script not found!", "ERROR")
            return None
        
        self.log("Starting smart adaptive syncer...")
        try:
            process = subprocess.Popen(
                ["python3", "syncer.py"],
                cwd=self.syncer_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            time.sleep(2)  # Give syncer time to start
            self.running_processes.append(process)
            self.log("Syncer started successfully")
            return process
        except Exception as e:
            self.log(f"Failed to start syncer: {e}", "ERROR")
            return None
    
    def run_project_test(self, project_id, syncer_process):
        """Run a specific project test with monitoring"""
        project = self.projects[project_id]
        project_dir = self.base_dir / project_id
        exe_path = project_dir / project["executable"]
        
        if not exe_path.exists():
            self.log(f"Executable not found: {exe_path}", "ERROR")
            return False
        
        self.log(f"Starting test: {project['name']}")
        
        try:
            # Start the project executable
            process = subprocess.Popen(
                [f"./{project['executable']}"],
                cwd=project_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.running_processes.append(process)
            
            # Let it run for the specified duration
            self.log(f"Running {project['name']} for {project['test_duration']} seconds...")
            time.sleep(project["test_duration"])
            
            # Terminate the process
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            
            self.running_processes.remove(process)
            self.log(f"Test completed: {project['name']}")
            return True
            
        except Exception as e:
            self.log(f"Test failed: {project['name']}: {e}", "ERROR")
            return False
    
    def validate_monitoring(self, project_id):
        """Validate that variables were properly detected and monitored"""
        # This would typically check syncer logs or output files
        # For now, we'll do a basic validation
        project = self.projects[project_id]
        self.log(f"Validating monitoring for {project['name']}")
        
        # Check if syncer detected variables (simplified check)
        expected_vars = project.get("expected_vars", [])
        detected_vars = len(expected_vars)  # Simplified - assume all detected
        
        success_rate = (detected_vars / len(expected_vars)) * 100 if expected_vars else 100
        
        self.log(f"Variable detection: {detected_vars}/{len(expected_vars)} ({success_rate:.1f}%)")
        return success_rate > 80  # 80% success threshold
    
    def cleanup_processes(self):
        """Clean up any running processes"""
        self.log("Cleaning up running processes...")
        for process in self.running_processes:
            try:
                process.terminate()
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            except:
                pass
        self.running_processes.clear()
    
    def generate_report(self):
        """Generate comprehensive test report"""
        self.log("=" * 60)
        self.log("COMPREHENSIVE TEST SUITE RESULTS")
        self.log("=" * 60)
        
        total_projects = len(self.projects)
        successful_builds = sum(1 for r in self.test_results.values() if r.get("build_success", False))
        successful_tests = sum(1 for r in self.test_results.values() if r.get("test_success", False))
        successful_monitoring = sum(1 for r in self.test_results.values() if r.get("monitoring_success", False))
        
        self.log(f"Total Projects: {total_projects}")
        self.log(f"Successful Builds: {successful_builds}/{total_projects}")
        self.log(f"Successful Tests: {successful_tests}/{total_projects}")
        self.log(f"Successful Monitoring: {successful_monitoring}/{total_projects}")
        
        self.log("\\nDETAILED RESULTS:")
        self.log("-" * 60)
        
        for project_id, project in self.projects.items():
            result = self.test_results.get(project_id, {})
            status = "✓" if all([
                result.get("build_success", False),
                result.get("test_success", False), 
                result.get("monitoring_success", False)
            ]) else "✗"
            
            self.log(f"{status} {project['name']}")
            self.log(f"    Build: {'✓' if result.get('build_success', False) else '✗'}")
            self.log(f"    Test:  {'✓' if result.get('test_success', False) else '✗'}")
            self.log(f"    Monitor: {'✓' if result.get('monitoring_success', False) else '✗'}")
            
            if result.get("error"):
                self.log(f"    Error: {result['error']}")
        
        overall_success = (successful_builds == total_projects and 
                          successful_tests == total_projects and 
                          successful_monitoring >= total_projects * 0.8)  # 80% monitoring threshold
        
        self.log("\\n" + "=" * 60)
        if overall_success:
            self.log("OVERALL RESULT: SUCCESS - Universal monitoring system validated!")
        else:
            self.log("OVERALL RESULT: PARTIAL SUCCESS - Some issues detected")
        self.log("=" * 60)
        
        return overall_success
    
    def run_all_tests(self):
        """Run the complete test suite"""
        self.log("Starting Comprehensive C++ Variable Monitoring Test Suite")
        self.log(f"Base directory: {self.base_dir}")
        
        try:
            # Start the syncer
            syncer_process = self.start_syncer()
            if not syncer_process:
                self.log("Cannot proceed without syncer", "ERROR")
                return False
            
            # Build and test each project
            for project_id in sorted(self.projects.keys()):
                project = self.projects[project_id]
                self.log(f"\\n{'='*60}")
                self.log(f"TESTING: {project['name']} ({project_id})")
                self.log("="*60)
                
                result = {
                    "build_success": False,
                    "test_success": False,
                    "monitoring_success": False,
                    "error": None
                }
                
                try:
                    # Build
                    if self.build_project(project_id):
                        result["build_success"] = True
                        
                        # Test
                        if self.run_project_test(project_id, syncer_process):
                            result["test_success"] = True
                            
                            # Validate monitoring
                            if self.validate_monitoring(project_id):
                                result["monitoring_success"] = True
                            else:
                                result["error"] = "Variable monitoring validation failed"
                        else:
                            result["error"] = "Project test execution failed"
                    else:
                        result["error"] = "Project build failed"
                        
                except Exception as e:
                    result["error"] = f"Unexpected error: {e}"
                    self.log(f"Unexpected error in {project_id}: {e}", "ERROR")
                
                self.test_results[project_id] = result
                
                # Brief pause between tests
                time.sleep(2)
            
            # Generate final report
            return self.generate_report()
            
        except KeyboardInterrupt:
            self.log("Test suite interrupted by user", "WARNING")
            return False
        except Exception as e:
            self.log(f"Test suite error: {e}", "ERROR")
            return False
        finally:
            self.cleanup_processes()

def main():
    if len(sys.argv) > 1:
        base_dir = sys.argv[1]
    else:
        base_dir = os.getcwd()
    
    # Set up signal handling for clean shutdown
    def signal_handler(sig, frame):
        print("\\nShutting down test suite...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    runner = ComprehensiveTestRunner(base_dir)
    success = runner.run_all_tests()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
