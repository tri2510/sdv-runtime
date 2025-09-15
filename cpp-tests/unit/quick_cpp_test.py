#!/usr/bin/env python3
"""
Quick test to verify C++ tracing works without KUKSA databroker
"""
import asyncio
import sys
import os
from pathlib import Path

# Add kuksa-syncer to path for imports
current_dir = Path(__file__).parent
kuksa_syncer_path = current_dir.parent.parent / "kuksa-syncer"
sys.path.insert(0, str(kuksa_syncer_path))

import cpp_memory_debugger as cpp_debugger_util

async def quick_cpp_test():
    """Quick test to verify C++ global variable detection and monitoring"""
    print("🧪 QUICK C++ TRACING TEST")
    print("=" * 40)

    # Test 1: Auto-detection on cmake project
    print("🔍 Test 1: Auto-detecting variables in cmake project")
    project_path = "/home/htr1hc/01_SDV/59_integrate_sdv-runtime_cpp/sdv-runtime-fork/cpp-projects/02-cmake-structured"

    print(f"📂 Project: {project_path}")
    print(f"🎯 Looking for variables like: actual_speed, battery_voltage, engine_rpm")

    # Use auto-detection to find variables
    try:
        from auto_variable_detector import AutoVariableDetector

        detector = AutoVariableDetector()

        # Read the main.cpp file
        main_cpp_path = os.path.join(project_path, "src", "main.cpp")
        with open(main_cpp_path, 'r') as f:
            cpp_code = f.read()

        # Find the binary
        binary_path = os.path.join(project_path, "build", "vehicle_systems")

        # Auto-detect variables
        print(f"🔍 Analyzing source code: {main_cpp_path}")
        print(f"🔍 Analyzing binary: {binary_path}")

        variables = detector.auto_detect_variables(cpp_code, binary_path)
        print(f"✅ Found {len(variables)} variables:")

        # Show first 10 variables
        for i, var in enumerate(variables[:10]):
            var_name = var.get('name', 'unknown')
            var_type = var.get('type', 'unknown')
            memory_addr = var.get('address', 'unknown')
            print(f"   {i+1}. {var_name} ({var_type}) @ {hex(memory_addr) if isinstance(memory_addr, int) else memory_addr}")

        if len(variables) > 10:
            print(f"   ... and {len(variables) - 10} more variables")

        # Check for our expected variables
        var_names = [v.get('name', '') for v in variables]

        expected_vars = ['actual_speed', 'battery_voltage', 'engine_rpm', 'tire_pressure_fl']
        found_vars = [var for var in expected_vars if var in var_names]

        print(f"\n🎯 Expected variables found: {found_vars}")

        if len(found_vars) >= 3:
            print("✅ SUCCESS: Auto-detection found expected automotive variables!")
            print("✅ C++ tracing system can detect global variables without KUKSA databroker")
            return True
        else:
            print("❌ FAILED: Not enough expected variables found")
            return False

    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(quick_cpp_test())
    print(f"\n{'🎉 TEST PASSED' if result else '❌ TEST FAILED'}")
    exit(0 if result else 1)