#!/usr/bin/env python3
"""Debug script to find JSON serialization errors."""

import sys
import json
import traceback

# Test protobuf-like object
class FakeUint32Array:
    def __init__(self):
        self.values = [1, 125]
    
    def __str__(self):
        return f"values: {self.values[0]}\nvalues: {self.values[1]}"

# Test standard JSON encoder (will fail)
print("Testing standard JSON encoder:")
try:
    obj = FakeUint32Array()
    result = json.dumps({"test": obj})
    print(f"Success: {result}")
except Exception as e:
    print(f"Error: {e}")

# Test with patch
print("\nApplying JSON patch...")
sys.path.insert(0, '/home/dev/ws/kuksa-syncer')
from json_array_patch import apply_global_patch, ArrayJSONEncoder

apply_global_patch()

print("Testing after patch:")
try:
    obj = FakeUint32Array()
    result = json.dumps({"test": obj})
    print(f"Success: {result}")
except Exception as e:
    print(f"Error: {e}")

# Direct test with encoder
print("\nTesting with explicit encoder:")
try:
    obj = FakeUint32Array()
    result = json.dumps({"test": obj}, cls=ArrayJSONEncoder)
    print(f"Success: {result}")
except Exception as e:
    print(f"Error: {e}")