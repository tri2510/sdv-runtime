#!/usr/bin/env python3
"""Test script to verify VSS array support."""

import asyncio
import json
from kuksa_client.grpc import VSSClient, Datapoint

async def test_array_support():
    """Test array datapoints with Kuksa databroker."""
    
    # Connect to databroker
    client = VSSClient('127.0.0.1', 55555)
    await client.connect()
    print("Connected to Kuksa databroker")
    
    try:
        
        # Test 1: Set array value as list
        print("\nTest 1: Setting HornControl to [1, 125] (Horn ON with priority 125)")
        try:
            # Try different formats
            test_values = [
                [1, 125],                    # Python list
                "[1, 125]",                  # JSON string
                json.dumps([1, 125]),        # JSON serialized
            ]
            
            for i, value in enumerate(test_values, 1):
                print(f"  Attempt {i}: Setting value as {type(value).__name__}: {value}")
                try:
                    await client.set_current_values({
                        'Vehicle.Body.Horn.HornControl': Datapoint(value)
                    })
                    print(f"    ✓ Success with format: {type(value).__name__}")
                    break
                except Exception as e:
                    print(f"    ✗ Failed: {e}")
        except Exception as e:
            print(f"Failed to set array value: {e}")
        
        # Test 2: Read array value
        print("\nTest 2: Reading HornControl value")
        try:
            response = await client.get_current_values(['Vehicle.Body.Horn.HornControl'])
            for path, datapoint in response.items():
                print(f"  Path: {path}")
                print(f"  Value: {datapoint.value}")
                print(f"  Type: {type(datapoint.value)}")
        except Exception as e:
            print(f"Failed to read array value: {e}")
        
        # Test 3: Set array to OFF
        print("\nTest 3: Setting HornControl to [0, 125] (Horn OFF)")
        try:
            await client.set_current_values({
                'Vehicle.Body.Horn.HornControl': Datapoint([0, 125])
            })
            print("  ✓ Successfully set to OFF")
        except Exception as e:
            print(f"  ✗ Failed: {e}")
        
        # Test 4: Check metadata
        print("\nTest 4: Checking metadata for HornControl")
        try:
            metadata = await client.get_metadata(['Vehicle.Body.Horn.HornControl'])
            for path, meta in metadata.items():
                print(f"  Path: {path}")
                print(f"  Data type: {meta.data_type}")
                print(f"  Description: {meta.description}")
        except Exception as e:
            print(f"Failed to get metadata: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(test_array_support())