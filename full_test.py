#!/usr/bin/env python3
"""Comprehensive test for VSS array support and backward compatibility."""

from kuksa_client.grpc import VSSClient, Datapoint
import json
import time

def test_vss_compatibility():
    """Test both array and non-array signals for backward compatibility."""
    
    # Connect to databroker
    client = VSSClient('127.0.0.1', 55555)
    client.connect()
    print("✓ Connected to Kuksa databroker\n")
    
    all_tests_passed = True
    
    try:
        # Test 1: Array signal - HornControl
        print("=" * 50)
        print("TEST 1: Array Signal (HornControl)")
        print("=" * 50)
        try:
            # Set array value
            value = json.dumps([1, 125])
            client.set_current_values({
                'Vehicle.Body.Horn.HornControl': Datapoint(value)
            })
            print(f"✓ Set HornControl to {value}")
            
            # Read back
            response = client.get_current_values(['Vehicle.Body.Horn.HornControl'])
            for path, datapoint in response.items():
                if hasattr(datapoint.value, 'values'):
                    values = list(datapoint.value.values)
                    print(f"✓ Read HornControl: {values}")
                    if values != [1, 125]:
                        print("✗ ERROR: Values don't match!")
                        all_tests_passed = False
        except Exception as e:
            print(f"✗ Array signal test failed: {e}")
            all_tests_passed = False
        
        # Test 2: Backward compatibility - Speed (float)
        print("\n" + "=" * 50)
        print("TEST 2: Backward Compatibility - Float Signal (Speed)")
        print("=" * 50)
        try:
            # Set float value
            speed = 60.5
            client.set_current_values({
                'Vehicle.Speed': Datapoint(speed)
            })
            print(f"✓ Set Speed to {speed}")
            
            # Read back
            response = client.get_current_values(['Vehicle.Speed'])
            for path, datapoint in response.items():
                read_speed = datapoint.value
                print(f"✓ Read Speed: {read_speed}")
                if abs(float(read_speed) - speed) > 0.01:
                    print("✗ ERROR: Speed value doesn't match!")
                    all_tests_passed = False
        except Exception as e:
            print(f"✗ Float signal test failed: {e}")
            all_tests_passed = False
        
        # Test 3: Boolean signal - IsActive
        print("\n" + "=" * 50)
        print("TEST 3: Backward Compatibility - Boolean Signal")
        print("=" * 50)
        try:
            # Set boolean value
            client.set_current_values({
                'Vehicle.Body.Horn.IsActive': Datapoint(True)
            })
            print(f"✓ Set IsActive to True")
            
            # Read back
            response = client.get_current_values(['Vehicle.Body.Horn.IsActive'])
            for path, datapoint in response.items():
                value = datapoint.value
                print(f"✓ Read IsActive: {value}")
                if value != True:
                    print("✗ ERROR: Boolean value doesn't match!")
                    all_tests_passed = False
        except Exception as e:
            print(f"✗ Boolean signal test failed: {e}")
            all_tests_passed = False
        
        # Test 4: Multiple signals at once
        print("\n" + "=" * 50)
        print("TEST 4: Multiple Signals Simultaneously")
        print("=" * 50)
        try:
            # Set multiple values
            client.set_current_values({
                'Vehicle.Body.Horn.HornControl': Datapoint(json.dumps([0, 100])),
                'Vehicle.Speed': Datapoint(75.0),
                'Vehicle.Body.Horn.IsActive': Datapoint(False)
            })
            print("✓ Set multiple signals")
            
            # Read all back
            response = client.get_current_values([
                'Vehicle.Body.Horn.HornControl',
                'Vehicle.Speed',
                'Vehicle.Body.Horn.IsActive'
            ])
            
            print("✓ Read multiple signals:")
            for path, datapoint in response.items():
                if hasattr(datapoint.value, 'values'):
                    print(f"  - {path}: {list(datapoint.value.values)}")
                else:
                    print(f"  - {path}: {datapoint.value}")
        except Exception as e:
            print(f"✗ Multiple signals test failed: {e}")
            all_tests_passed = False
        
    finally:
        client.disconnect()
        print("\n" + "=" * 50)
        if all_tests_passed:
            print("✅ ALL TESTS PASSED - System is working correctly!")
        else:
            print("❌ SOME TESTS FAILED - Check the errors above")
        print("=" * 50)

if __name__ == "__main__":
    test_vss_compatibility()