#!/usr/bin/env python3
"""
Test script to verify automatic variable detection is working
"""
import asyncio
from cpp_memory_debugger import start_memory_monitoring, get_global_variables

async def test_automatic_detection():
    print("=== TESTING AUTOMATIC VARIABLE DETECTION ===")
    
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