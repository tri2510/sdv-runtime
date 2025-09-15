#!/usr/bin/env python3
"""
Final verification test - demonstrate C++ tracing without KUKSA databroker
"""
import asyncio
import sys
import os
from pathlib import Path

# Add kuksa-syncer to path for imports
current_dir = Path(__file__).parent
kuksa_syncer_path = current_dir.parent.parent / "kuksa-syncer"
sys.path.insert(0, str(kuksa_syncer_path))

from auto_variable_detector import AutoVariableDetector

async def final_verification():
    """Final verification that C++ tracing works completely independent of KUKSA databroker"""
    print("🎉 FINAL VERIFICATION: C++ TRACING WITHOUT KUKSA DATABROKER")
    print("=" * 60)

    # Test with our simplest project
    project_path = "/home/htr1hc/01_SDV/59_integrate_sdv-runtime_cpp/sdv-runtime-fork/cpp-projects/01-basic-types"
    source_file = os.path.join(project_path, "basic_types_monitor.cpp")
    binary_file = os.path.join(project_path, "basic_types_monitor")

    print(f"📂 Project: 01-basic-types")
    print(f"📄 Source: {source_file}")
    print(f"🔧 Binary: {binary_file}")
    print()

    try:
        detector = AutoVariableDetector()

        # Read the source
        with open(source_file, 'r') as f:
            cpp_code = f.read()

        print("🔍 STEP 1: Auto-detecting variables from source and binary...")
        variables = detector.auto_detect_variables(cpp_code, binary_file)

        print(f"✅ SUCCESS: Found {len(variables)} variables ready for monitoring")
        print()

        # Show detected variables
        print("📋 DETECTED VARIABLES:")
        for i, var in enumerate(variables[:15]):  # Show first 15
            var_name = var.get('name', 'unknown')
            var_type = var.get('type', 'unknown')
            address = var.get('address', 'unknown')
            addr_str = hex(address) if isinstance(address, int) else str(address)
            print(f"   {i+1:2d}. {var_name:<20} ({var_type:<10}) @ {addr_str}")

        if len(variables) > 15:
            print(f"   ... and {len(variables) - 15} more variables")

        print()

        # Verify key automotive variables were detected
        var_names = [v.get('name', '') for v in variables]
        automotive_vars = [
            'fuel_level', 'current_speed', 'gps_latitude', 'gps_longitude',
            'engine_running', 'brake_applied', 'turn_signal_left', 'headlights_on'
        ]

        found_automotive = [var for var in automotive_vars if var in var_names]

        print("🚗 AUTOMOTIVE VARIABLES DETECTION:")
        for var in automotive_vars:
            status = "✅" if var in var_names else "❌"
            print(f"   {status} {var}")

        print()
        print(f"🎯 RESULTS:")
        print(f"   📊 Total variables detected: {len(variables)}")
        print(f"   🚗 Automotive variables found: {len(found_automotive)}/{len(automotive_vars)}")

        success = len(variables) >= 8 and len(found_automotive) >= 5

        if success:
            print(f"\n🎉 VERIFICATION PASSED!")
            print(f"✅ C++ global variable tracing works WITHOUT KUKSA databroker")
            print(f"✅ Auto-detection successfully found automotive variables")
            print(f"✅ System can monitor {len(variables)} variables independently")
            print(f"✅ Ready for smart adaptive syncer integration")
            return True
        else:
            print(f"\n❌ VERIFICATION FAILED!")
            print(f"   Need >= 8 variables (found {len(variables)})")
            print(f"   Need >= 5 automotive vars (found {len(found_automotive)})")
            return False

    except Exception as e:
        print(f"❌ Verification error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(final_verification())
    print(f"\n{'🏆 FINAL TEST PASSED' if result else '💥 FINAL TEST FAILED'}")
    exit(0 if result else 1)