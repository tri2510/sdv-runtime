#!/usr/bin/env python3
"""
Test MATLAB/Simulink-style variable detection - simple, straightforward variables
"""
import sys
import os
from pathlib import Path

# Add kuksa-syncer to path
current_dir = Path(__file__).parent
kuksa_syncer_path = current_dir.parent.parent / "kuksa-syncer"
sys.path.insert(0, str(kuksa_syncer_path))

from auto_variable_detector import AutoVariableDetector

def test_matlab_style_detection():
    """Test detection of MATLAB-style straightforward variables"""
    print("🔬 TESTING MATLAB-STYLE VARIABLE DETECTION")
    print("=" * 55)

    # Test MATLAB-style project
    matlab_project = "/home/htr1hc/01_SDV/59_integrate_sdv-runtime_cpp/sdv-runtime-fork/cpp-projects/07-matlab-style"
    matlab_source = os.path.join(matlab_project, "matlab_generated_code.cpp")
    matlab_binary = os.path.join(matlab_project, "matlab_generated_code")

    print(f"📂 MATLAB Project: {matlab_project}")
    print(f"📄 Source: matlab_generated_code.cpp")
    print(f"🔧 Binary: matlab_generated_code")

    detector = AutoVariableDetector()

    # Read source code
    with open(matlab_source, 'r') as f:
        matlab_code = f.read()

    print("\n🔍 Running detection...")
    variables = detector.auto_detect_variables(matlab_code, matlab_binary)

    print(f"✅ Found {len(variables)} variables:")

    # Group by type
    var_by_type = {}
    for var in variables:
        var_type = var.get('type', 'unknown')
        if var_type not in var_by_type:
            var_by_type[var_type] = []
        var_by_type[var_type].append(var.get('name', 'unknown'))

    for var_type, var_names in sorted(var_by_type.items()):
        print(f"\n📊 {var_type} variables ({len(var_names)}):")
        for name in sorted(var_names):
            print(f"   • {name}")

    # Check for key MATLAB-style variables
    var_names = [v.get('name', '') for v in variables]

    matlab_key_vars = [
        'throttle_position',
        'brake_pressure',
        'steering_angle',
        'vehicle_speed',
        'engine_torque_cmd',
        'speed_error',
        'speed_integral',
        'kp_speed',
        'ki_speed',
        'engine_enable',
        'brake_enable',
        'control_cycle_count'
    ]

    print(f"\n🎯 MATLAB-STYLE VARIABLES DETECTION:")
    found_count = 0
    for var in matlab_key_vars:
        found = var in var_names
        status = "✅ FOUND" if found else "❌ MISSING"
        print(f"   {status}: {var}")
        if found:
            found_count += 1

    success_rate = found_count / len(matlab_key_vars) * 100
    print(f"\n📊 MATLAB DETECTION SUMMARY:")
    print(f"   Total variables detected: {len(variables)}")
    print(f"   Key MATLAB variables: {found_count}/{len(matlab_key_vars)}")
    print(f"   Detection rate: {success_rate:.1f}%")

    return success_rate >= 90.0

def test_simulink_style_detection():
    """Test detection of Simulink-style block variables"""
    print("\n🔧 TESTING SIMULINK-STYLE VARIABLE DETECTION")
    print("=" * 55)

    # Test Simulink-style project
    simulink_project = "/home/htr1hc/01_SDV/59_integrate_sdv-runtime_cpp/sdv-runtime-fork/cpp-projects/08-simulink-blocks"
    simulink_source = os.path.join(simulink_project, "simulink_vehicle_model.cpp")
    simulink_binary = os.path.join(simulink_project, "simulink_vehicle_model")

    print(f"📂 Simulink Project: {simulink_project}")
    print(f"📄 Source: simulink_vehicle_model.cpp")
    print(f"🔧 Binary: simulink_vehicle_model")

    detector = AutoVariableDetector()

    # Read source code
    with open(simulink_source, 'r') as f:
        simulink_code = f.read()

    print("\n🔍 Running detection...")
    variables = detector.auto_detect_variables(simulink_code, simulink_binary)

    print(f"✅ Found {len(variables)} variables:")

    # Check for key Simulink-style variables
    var_names = [v.get('name', '') for v in variables]

    simulink_key_vars = [
        'accelerator_pedal',
        'brake_pedal',
        'steering_input',
        'vehicle_velocity',
        'lateral_acceleration',
        'yaw_rate',
        'throttle_command',
        'brake_command',
        'engine_speed',
        'speed_sensor',
        'vehicle_mass',
        'wheel_radius',
        'cruise_control_active',
        'abs_intervention',
        'simulation_step'
    ]

    print(f"\n🎯 SIMULINK-STYLE VARIABLES DETECTION:")
    found_count = 0
    for var in simulink_key_vars:
        found = var in var_names
        status = "✅ FOUND" if found else "❌ MISSING"
        print(f"   {status}: {var}")
        if found:
            found_count += 1

    success_rate = found_count / len(simulink_key_vars) * 100
    print(f"\n📊 SIMULINK DETECTION SUMMARY:")
    print(f"   Total variables detected: {len(variables)}")
    print(f"   Key Simulink variables: {found_count}/{len(simulink_key_vars)}")
    print(f"   Detection rate: {success_rate:.1f}%")

    return success_rate >= 90.0

if __name__ == "__main__":
    print("🚗 MATLAB/SIMULINK VARIABLE DETECTION TEST")
    print("=" * 60)

    matlab_success = test_matlab_style_detection()
    simulink_success = test_simulink_style_detection()

    overall_success = matlab_success and simulink_success

    print(f"\n🏁 OVERALL RESULTS:")
    print(f"   MATLAB-style: {'✅ PASSED' if matlab_success else '❌ FAILED'}")
    print(f"   Simulink-style: {'✅ PASSED' if simulink_success else '❌ FAILED'}")

    if overall_success:
        print("\n🎉 SUCCESS: MATLAB/Simulink variable detection working!")
        print("✅ Simple double, bool, int variables detected correctly")
        print("✅ No complex typedefs required")
        print("✅ Ready for MATLAB C++ code generation output")
    else:
        print("\n❌ ISSUE: Some MATLAB/Simulink patterns not detected")

    print(f"\n{'🏆 TEST PASSED' if overall_success else '💥 TEST FAILED'}")
    exit(0 if overall_success else 1)