#!/usr/bin/env python3
"""
Test script for memory monitoring integration with syncer.
Tests the complete flow: compile -> run -> monitor variables -> send to frontend
"""

import asyncio
import sys
import os
import json
from pathlib import Path

# Add current directory to path
sys.path.append('.')

import cpp_memory_debugger as cpp_debugger_util
from project_utils import ProjectUtils

class MockSocketIO:
    """Mock SocketIO for testing WebSocket communication"""
    
    def __init__(self):
        self.messages = []
    
    async def emit(self, event, data):
        """Mock emit that just stores messages"""
        print(f"[WebSocket] {event}: {data}")
        self.messages.append({"event": event, "data": data})
        return True

async def test_complete_flow():
    """Test the complete memory monitoring flow"""
    print("=== Testing Memory Monitoring Integration ===\n")
    
    # Step 1: Simulate project creation (like frontend would send)
    print("Step 1: Creating test project...")
    with open('/home/htr1hc/Downloads/project (3)/fcw-adas-demo/src/main.cpp', 'r') as f:
        cpp_code = f.read()
    
    # Create project payload (like frontend sends)
    project_structure = [
        {"type": "file", "name": "main.cpp", "content": cpp_code}
    ]
    
    # Copy include files
    include_files = [
        "environment.h", "fcw_controller.h", "types.h", 
        "v2x_communication.h", "vehicle_system.h"
    ]
    
    for header in include_files:
        with open(f'/home/htr1hc/Downloads/project (3)/fcw-adas-demo/include/{header}', 'r') as f:
            content = f.read()
        project_structure.append({"type": "file", "name": f"include/{header}", "content": content})
    
    # Add source files
    source_files = [
        "environment.cpp", "fcw_controller.cpp", 
        "v2x_communication.cpp", "vehicle_system.cpp"
    ]
    
    for source in source_files:
        with open(f'/home/htr1hc/Downloads/project (3)/fcw-adas-demo/src/{source}', 'r') as f:
            content = f.read()
        project_structure.append({"type": "file", "name": f"src/{source}", "content": content})
    
    payload = {
        'data': {
            'code': json.dumps(project_structure),
            'watch_vars': 'ego_speed,collision_risk,current_lane,warning_active,brake_pressure'
        }
    }
    
    # Step 2: Process project like syncer would
    print("Step 2: Processing project...")
    project_utils = ProjectUtils()
    
    try:
        project_path = project_utils.save_from_payload(payload)
        print(f"✓ Project saved to: {project_path}")
    except Exception as e:
        print(f"✗ Project creation failed: {e}")
        return False
    
    # Step 3: Test compilation
    print("\nStep 3: Testing compilation...")
    compile_ok, compile_msg = await cpp_debugger_util.compile_cpp()
    print(f"Compilation result: {compile_ok}")
    print(f"Compilation message: {compile_msg}")
    
    if not compile_ok:
        print("✗ Compilation failed")
        return False
    
    # Step 4: Test memory monitoring setup
    print("\nStep 4: Testing memory monitoring...")
    binary_path, pid, run_msg = await cpp_debugger_util.run_binary()
    print(f"Binary path: {binary_path}")
    print(f"Run message: {run_msg}")
    
    # Step 5: Test WebSocket communication
    print("\nStep 5: Testing WebSocket communication...")
    mock_sio = MockSocketIO()
    
    # Test short monitoring session
    watch_vars = "ego_speed,collision_risk,current_lane,warning_active,brake_pressure"
    kit_id = "test_kit_123"
    
    print(f"Starting monitoring task for 10 seconds...")
    
    # Create monitoring task with timeout
    monitoring_task = asyncio.create_task(
        cpp_debugger_util.periodic_memory_var_report(mock_sio, kit_id, watch_vars)
    )
    
    # Let it run for a few seconds
    try:
        await asyncio.wait_for(monitoring_task, timeout=10.0)
    except asyncio.TimeoutError:
        print("Monitoring timeout reached (expected)")
        monitoring_task.cancel()
    
    # Step 6: Check results
    print("\nStep 6: Results summary...")
    print(f"WebSocket messages sent: {len(mock_sio.messages)}")
    
    if mock_sio.messages:
        latest_msg = mock_sio.messages[-1]
        print(f"Latest message: {latest_msg}")
        
        if latest_msg['event'] == 'messageToClient' and latest_msg['data']['cmd'] == 'trace_vars':
            print("✅ Memory monitoring working correctly!")
            print(f"Variables monitored: {latest_msg['data']['data']}")
            return True
    
    print("⚠️  No variable data received - check monitoring setup")
    return False

async def main():
    """Main test function"""
    try:
        success = await test_complete_flow()
        if success:
            print("\n🎉 Integration test PASSED!")
            print("Memory monitoring is ready for frontend testing!")
        else:
            print("\n❌ Integration test FAILED!")
            print("Check the issues above and fix before frontend testing.")
            
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        cpp_debugger_util.cleanup_memory_monitor()
        print("Cleanup completed")

if __name__ == "__main__":
    asyncio.run(main())