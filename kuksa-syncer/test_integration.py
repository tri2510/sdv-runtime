#!/usr/bin/env python3
"""
Test script to verify the complete C++ memory monitoring integration
"""

import asyncio
import json
from cpp_memory_debugger import start_memory_monitoring, get_global_variables, cleanup_memory_monitor

async def test_cpp_memory_integration():
    """Test the complete C++ memory monitoring pipeline"""
    print("=== Testing C++ Memory Monitoring Integration ===")
    
    # Define FCW ADAS variables to monitor
    watch_vars = "ego_speed,collision_risk,current_lane,warning_active,brake_pressure"
    
    print(f"1. Starting memory monitoring for variables: {watch_vars}")
    result, msg = await start_memory_monitoring(watch_vars)
    
    if "error" in result:
        print(f"Failed to start monitoring: {msg}")
        return
        
    print(f"2. Monitoring started successfully: {msg}")
    print(f"   PID: {result.get('pid')}")
    
    # Monitor variables for 30 seconds
    print("3. Reading variables for 30 seconds...")
    
    try:
        for i in range(60):  # 30 seconds at 0.5s intervals
            values, status = await get_global_variables(watch_vars)
            
            if isinstance(values, dict) and "error" not in values and values:
                print(f"[{i+1:2d}] Variables: {json.dumps(values, indent=2)}")
            else:
                print(f"[{i+1:2d}] No data: {values}")
                
            await asyncio.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\nStopped by user")
    except Exception as e:
        print(f"Error during monitoring: {e}")
    finally:
        print("4. Cleaning up...")
        cleanup_memory_monitor()
        print("Test completed!")

if __name__ == "__main__":
    asyncio.run(test_cpp_memory_integration())