#!/usr/bin/env python3
"""
Test embedded ECU variable detection - check why throttle_position isn't working
"""
import sys
import os
from pathlib import Path

# Add kuksa-syncer to path
current_dir = Path(__file__).parent
kuksa_syncer_path = current_dir.parent.parent / "kuksa-syncer"
sys.path.insert(0, str(kuksa_syncer_path))

from auto_variable_detector import AutoVariableDetector

def test_embedded_variable_detection():
    """Test detection of embedded ECU variables like throttle_position_q15"""
    print("🔍 TESTING EMBEDDED ECU VARIABLE DETECTION")
    print("=" * 50)

    # Sample embedded ECU code (simplified)
    embedded_code = """
typedef int16_t q15_t;
typedef int32_t q31_t;

// These should be detected
std::atomic<q15_t> throttle_position_q15{0};
std::atomic<q15_t> brake_pedal_q15{0};
std::atomic<q31_t> vehicle_speed_q31{0};
std::atomic<uint16_t> status_reg1_raw{0};
std::atomic<uint8_t> status_reg2_raw{0};
std::atomic<uint32_t> can_tx_counter{0};
"""

    detector = AutoVariableDetector()

    print("📄 Testing embedded ECU code:")
    print(embedded_code)
    print()

    print("🔍 Running detection...")
    variables = detector.extract_variables_from_source(embedded_code)

    print(f"✅ Found {len(variables)} variables:")
    for i, var in enumerate(variables, 1):
        var_name = var.get('name', 'unknown')
        var_type = var.get('type', 'unknown')
        is_atomic = var.get('is_atomic', False)
        pattern = var.get('pattern', 'unknown')

        print(f"   {i}. {var_name} ({var_type}) [{'atomic' if is_atomic else 'regular'}] - {pattern}")

    # Check for specific variables
    var_names = [v.get('name', '') for v in variables]

    expected_vars = [
        'throttle_position_q15',
        'brake_pedal_q15',
        'vehicle_speed_q31',
        'status_reg1_raw',
        'can_tx_counter'
    ]

    print(f"\n🎯 DETECTION RESULTS:")
    found_count = 0
    for var in expected_vars:
        found = var in var_names
        status = "✅ FOUND" if found else "❌ MISSING"
        print(f"   {status}: {var}")
        if found:
            found_count += 1

    print(f"\n📊 SUMMARY:")
    print(f"   Expected variables: {len(expected_vars)}")
    print(f"   Variables found: {found_count}")
    print(f"   Detection rate: {found_count/len(expected_vars)*100:.1f}%")

    if found_count == len(expected_vars):
        print("\n🎉 SUCCESS: All embedded ECU variables detected!")
        return True
    else:
        print(f"\n❌ ISSUE: Missing {len(expected_vars) - found_count} variables")
        print("   Problem: Auto-detector missing patterns for custom typedef types")
        print("   Solution: Need to add q15_t, q31_t atomic patterns")
        return False

def test_detection_patterns():
    """Test what patterns are currently supported"""
    print("\n🔍 CURRENT DETECTION PATTERNS:")
    print("=" * 50)

    detector = AutoVariableDetector()

    for pattern_name, (regex, var_type, size_bytes) in detector.variable_patterns.items():
        print(f"   {pattern_name}: {regex} → {var_type} ({size_bytes} bytes)")

    print(f"\n📊 Total patterns: {len(detector.variable_patterns)}")

if __name__ == "__main__":
    success = test_embedded_variable_detection()
    test_detection_patterns()

    print(f"\n{'🎉 TEST PASSED' if success else '❌ TEST FAILED'}")
    exit(0 if success else 1)