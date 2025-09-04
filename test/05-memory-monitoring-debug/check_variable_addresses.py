#!/usr/bin/env python3
"""
Check where variables actually are in memory vs. symbol table.
"""

import subprocess
from pathlib import Path

def analyze_addresses():
    """Analyze the actual memory layout vs symbol addresses."""
    
    APP_DIR = Path(__file__).parent / 'kuksa-syncer' / 'app'
    BINARY_FILE = APP_DIR / 'main_bin'
    
    print("=== Analyzing Variable Address Layout ===")
    
    # 1. Check symbol table addresses
    print("\n1️⃣ Symbol table addresses (nm output):")
    result = subprocess.run(['nm', '-C', str(BINARY_FILE)], capture_output=True, text=True)
    for line in result.stdout.split('\n'):
        if any(var in line for var in ['current_lane', 'ego_speed', 'steering_angle', 'collision_risk']):
            print(f"   {line}")
    
    # 2. Check memory layout with objdump
    print("\n2️⃣ Section headers (objdump):")
    result = subprocess.run(['objdump', '-h', str(BINARY_FILE)], capture_output=True, text=True)
    for line in result.stdout.split('\n'):
        if any(section in line.lower() for section in ['data', 'bss', 'text']):
            print(f"   {line}")
    
    # 3. Check readelf sections
    print("\n3️⃣ ELF sections (readelf):")
    result = subprocess.run(['readelf', '-S', str(BINARY_FILE)], capture_output=True, text=True)
    for line in result.stdout.split('\n'):
        if any(section in line for section in ['.data', '.bss', '.text']):
            print(f"   {line.strip()}")
    
    # 4. Check if we can get variable addresses from gdb
    print("\n4️⃣ Testing variable addresses with objdump:")
    result = subprocess.run(['objdump', '-t', str(BINARY_FILE)], capture_output=True, text=True)
    for line in result.stdout.split('\n'):
        if any(var in line for var in ['current_lane', 'ego_speed', 'steering_angle', 'collision_risk']):
            print(f"   {line}")

if __name__ == "__main__":
    analyze_addresses()