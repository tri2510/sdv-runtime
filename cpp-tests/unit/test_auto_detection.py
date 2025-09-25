#!/usr/bin/env python3
"""
Test script to verify automatic variable detection is working
"""
import asyncio
import sys
import os
import subprocess
from pathlib import Path

# Add kuksa-syncer to path for imports
current_dir = Path(__file__).parent
kuksa_syncer_path = current_dir.parent.parent / "kuksa-syncer"
sys.path.insert(0, str(kuksa_syncer_path))

# Add support utilities for ensuring fixtures are present
sys.path.insert(0, str(current_dir.parent))

from support.build_support import restore_app_fixture

from cpp_memory_debugger import start_memory_monitoring, get_global_variables

async def test_automatic_detection():
    print("=== TESTING AUTOMATIC VARIABLE DETECTION ===")

    # Ensure the embedded ECU sample is restored and compiled
    app_dir = restore_app_fixture()
    subprocess.run(["bash", "build.sh"], cwd=app_dir, check=True)
    
    # Test 1: Empty watch_vars should trigger automatic detection
    print("\n🔍 Test 1: Empty watch_vars (should auto-detect)")
    result, msg = await start_memory_monitoring("")
    print(f"Result: {result}")
    print(f"Message: {msg}")
    
    if "error" not in result:
        print("✅ Automatic detection started successfully")
        
        # Wait a moment for process to start
        await asyncio.sleep(2)
        
        # Try to read variables
        print("\n📊 Test 2: Reading auto-detected variables")
        values, status = await get_global_variables("")
        print(f"Values: {values}")
        print(f"Status: {status}")
        
        # Check if ego_speed is detected
        if isinstance(values, dict) and 'ego_speed' in values:
            print(f"✅ ego_speed detected with value: {values['ego_speed']}")
        else:
            print("❌ ego_speed not found in auto-detected variables")
        
        # Clean up
        from cpp_memory_debugger import cleanup_memory_monitor
        cleanup_memory_monitor()
    else:
        print(f"❌ Automatic detection failed: {msg}")

if __name__ == "__main__":
    asyncio.run(test_automatic_detection())
