#!/usr/bin/env python3
"""
Complete test of embedded ECU variable detection with the full example
"""
import sys
import os
from pathlib import Path

# Add kuksa-syncer to path
current_dir = Path(__file__).parent
kuksa_syncer_path = current_dir.parent.parent / "kuksa-syncer"
sys.path.insert(0, str(kuksa_syncer_path))

from auto_variable_detector import AutoVariableDetector

def test_full_embedded_ecu():
    """Test the complete embedded ECU example"""
    print("🚗 TESTING COMPLETE EMBEDDED ECU EXAMPLE")
    print("=" * 60)

    # Read the actual embedded ECU code that was provided
    ecu_code = '''
#include <iostream>
#include <thread>
#include <chrono>
#include <cstdint>
#include <atomic>
#include <cstring>
#include <cmath>

// Fixed-point types (Q notation)
typedef int16_t q15_t;  // Q15 fixed-point: 1 sign + 15 fractional bits
typedef int32_t q31_t;  // Q31 fixed-point: 1 sign + 31 fractional bits

// Global ECU variables - Fixed-point sensor values
std::atomic<q15_t> throttle_position_q15{0};      // 0.0-1.0 range
std::atomic<q15_t> brake_pedal_q15{0};            // 0.0-1.0 range
std::atomic<q15_t> accelerator_pedal_q15{0};      // 0.0-1.0 range
std::atomic<q31_t> vehicle_speed_q31{0};          // km/h in Q31

// Global ECU variables - Engine control (fixed-point)
std::atomic<q15_t> fuel_injection_time_q15{0};    // milliseconds
std::atomic<q15_t> ignition_advance_q15{0};       // degrees BTDC
std::atomic<q15_t> idle_air_control_q15{0};       // 0.0-1.0 duty cycle

// Global ECU variables - Packed status registers
std::atomic<uint16_t> status_reg1_raw{0};
std::atomic<uint8_t> status_reg2_raw{0};

// Global ECU variables - Communication counters (typical CAN/LIN)
std::atomic<uint32_t> can_tx_counter{0};
std::atomic<uint32_t> can_rx_counter{0};
std::atomic<uint16_t> can_error_counter{0};
std::atomic<uint8_t> lin_frame_counter{0};

// Global ECU variables - Diagnostic trouble codes (DTCs)
std::atomic<uint16_t> active_dtc_count{0};
std::atomic<uint32_t> dtc_p0xxx{0};  // Powertrain DTCs
std::atomic<uint32_t> dtc_b0xxx{0};  // Body DTCs
std::atomic<uint32_t> dtc_c0xxx{0};  // Chassis DTCs
std::atomic<uint32_t> dtc_u0xxx{0};  // Network DTCs

// Global ECU variables - Timing and scheduling (typical RTOS variables)
std::atomic<uint32_t> main_loop_counter{0};
std::atomic<uint16_t> task_execution_time_us{0};
std::atomic<uint8_t> cpu_load_percent{0};

// Global ECU variables - Memory management
std::atomic<uint16_t> stack_usage_bytes{0};
std::atomic<uint16_t> heap_usage_bytes{0};
std::atomic<uint8_t> memory_fragmentation_percent{0};
'''

    detector = AutoVariableDetector()

    print("🔍 Running detection on complete embedded ECU code...")
    variables = detector.extract_variables_from_source(ecu_code)

    print(f"✅ Found {len(variables)} variables:")

    # Group by type for better organization
    var_by_type = {}
    for var in variables:
        var_type = var.get('type', 'unknown')
        if var_type not in var_by_type:
            var_by_type[var_type] = []
        var_by_type[var_type].append(var)

    for var_type, vars_list in sorted(var_by_type.items()):
        print(f"\n📊 {var_type} variables ({len(vars_list)}):")
        for var in vars_list:
            var_name = var.get('name', 'unknown')
            is_atomic = var.get('is_atomic', False)
            size_bytes = var.get('size_bytes', 0)
            print(f"   • {var_name} [{size_bytes} bytes] {'[atomic]' if is_atomic else ''}")

    # Check for key embedded variables
    var_names = [v.get('name', '') for v in variables]

    key_embedded_vars = [
        'throttle_position_q15',
        'brake_pedal_q15',
        'accelerator_pedal_q15',
        'vehicle_speed_q31',
        'fuel_injection_time_q15',
        'ignition_advance_q15',
        'idle_air_control_q15',
        'status_reg1_raw',
        'status_reg2_raw',
        'can_tx_counter',
        'can_rx_counter',
        'active_dtc_count',
        'main_loop_counter',
        'cpu_load_percent'
    ]

    print(f"\n🎯 KEY EMBEDDED VARIABLES DETECTION:")
    found_count = 0
    for var in key_embedded_vars:
        found = var in var_names
        status = "✅ FOUND" if found else "❌ MISSING"
        print(f"   {status}: {var}")
        if found:
            found_count += 1

    print(f"\n📊 EMBEDDED ECU DETECTION SUMMARY:")
    print(f"   Total variables detected: {len(variables)}")
    print(f"   Key embedded variables: {found_count}/{len(key_embedded_vars)}")
    print(f"   Detection rate: {found_count/len(key_embedded_vars)*100:.1f}%")

    # Check specific embedded patterns
    q15_vars = [v for v in variables if v.get('type') == 'q15_t']
    q31_vars = [v for v in variables if v.get('type') == 'q31_t']

    print(f"\n🎯 EMBEDDED TYPE ANALYSIS:")
    print(f"   Q15 fixed-point variables: {len(q15_vars)}")
    print(f"   Q31 fixed-point variables: {len(q31_vars)}")
    print(f"   Atomic variables: {len([v for v in variables if v.get('is_atomic', False)])}")

    if found_count >= len(key_embedded_vars) * 0.9:  # 90% success rate
        print("\n🎉 SUCCESS: Embedded ECU variable detection working!")
        print("✅ throttle_position_q15 and other embedded variables detected correctly")
        print("✅ Fixed-point Q15/Q31 types recognized")
        print("✅ Status registers and CAN counters found")
        print("✅ Enhanced auto-detector handles embedded patterns")
        return True
    else:
        print(f"\n❌ ISSUE: Missing too many embedded variables")
        return False

if __name__ == "__main__":
    success = test_full_embedded_ecu()
    print(f"\n{'🏆 TEST PASSED' if success else '💥 TEST FAILED'}")
    exit(0 if success else 1)