#!/usr/bin/env python3
"""Simple test for VSS array support."""

from kuksa_client.grpc import VSSClient, Datapoint
import json

# Connect to databroker
client = VSSClient('127.0.0.1', 55555)
client.connect()
print("Connected to Kuksa databroker")

try:
    # Test setting array value
    print("\nSetting HornControl to [1, 125]...")
    
    # Try as JSON string (this is what kuksa expects for arrays)
    value = json.dumps([1, 125])
    client.set_current_values({
        'Vehicle.Body.Horn.HornControl': Datapoint(value)
    })
    print(f"✓ Set value: {value}")
    
    # Read back the value
    print("\nReading HornControl value...")
    response = client.get_current_values(['Vehicle.Body.Horn.HornControl'])
    for path, datapoint in response.items():
        print(f"  Path: {path}")
        print(f"  Value: {datapoint.value}")
        print(f"  Raw type: {type(datapoint.value)}")
    
    # Turn off
    print("\nSetting HornControl to [0, 125] (OFF)...")
    value = json.dumps([0, 125])
    client.set_current_values({
        'Vehicle.Body.Horn.HornControl': Datapoint(value)
    })
    print(f"✓ Set value: {value}")
    
except Exception as e:
    print(f"Error: {e}")
finally:
    client.disconnect()
    print("\nDisconnected from databroker")