#!/usr/bin/env python3
"""
End-to-end integration test for trace_vars command validation
Tests the complete flow: Kit Server -> Syncer -> C++ Memory Monitoring -> Kit Server
"""
import asyncio
import socketio

# Global variables to track events
events_received = []

async def test_trace_vars_integration():
    """Test the complete end-to-end trace_vars integration"""
    print("🧪 Starting end-to-end trace_vars integration test...")
    
    # Create socket client to simulate Kit Server
    sio = socketio.AsyncClient(logger=False, engineio_logger=False)
    
    @sio.event
    async def connect():
        print("✅ Connected to syncer")
        
        # Send trace_vars command for cmake-multidir project
        cpp_project_data = {
            "cmd": "trace_vars",
            "request_from": "test_client",
            "project_type": "cmake",
            "project_path": "/home/htr1hc/01_SDV/59_integrate_sdv-runtime_cpp/sdv-runtime-fork/cpp-projects/cmake-multidir",
            "binary_name": "multidir_system", 
            "trace_vars": ["ego_speed", "throttle_position", "steering_angle", "rpm", "brake_applied"],
            "duration": 10  # Test for 10 seconds
        }
        
        print(f"🎯 Sending trace_vars command...")
        print(f"   Target variables: {cpp_project_data['trace_vars']}")
        print(f"   Project path: {cpp_project_data['project_path']}")
        print(f"   Binary: {cpp_project_data['binary_name']}")
        
        await sio.emit("messageToKit", cpp_project_data)
    
    @sio.event
    async def messageToKit_kitReply(data):
        """Handle replies from the syncer"""
        events_received.append(('trace_vars_reply', data))
        
        if data.get('cmd') == 'trace_vars':
            variables = data.get('data', {})
            if variables and isinstance(variables, dict):
                print(f"🔥 Received trace_vars data: {variables}")
                
                # Check if ego_speed is present and has a valid value
                if 'ego_speed' in variables:
                    ego_speed = variables['ego_speed']
                    if isinstance(ego_speed, (int, float)) and not (ego_speed != ego_speed):  # Check for NaN
                        print(f"✅ ego_speed validation PASSED: {ego_speed}")
                    else:
                        print(f"❌ ego_speed validation FAILED: {ego_speed} (NaN or invalid)")
            else:
                print(f"📊 Other trace_vars response: {data}")
    
    @sio.event
    async def disconnect():
        print("❌ Disconnected from syncer")
    
    try:
        # Connect to syncer
        print("🔌 Connecting to syncer at http://localhost:8000...")
        await sio.connect('http://localhost:8000')
        
        # Wait for trace_vars events
        print("⏱️  Waiting for trace_vars events for 15 seconds...")
        await asyncio.sleep(15)
        
        # Analyze results
        print(f"\n📊 Test Results:")
        print(f"   Events received: {len(events_received)}")
        
        # Check for trace_vars events with ego_speed
        ego_speed_events = []
        for event in events_received:
            if (event[0] == 'trace_vars_reply' and 
                event[1].get('cmd') == 'trace_vars' and 
                isinstance(event[1].get('data'), dict) and
                'ego_speed' in event[1]['data']):
                ego_speed_events.append(event[1]['data']['ego_speed'])
        
        print(f"   ego_speed events captured: {len(ego_speed_events)}")
        
        if len(ego_speed_events) > 0:
            print(f"   ego_speed values: {ego_speed_events[:5]}..." if len(ego_speed_events) > 5 else f"   ego_speed values: {ego_speed_events}")
            valid_values = [v for v in ego_speed_events if isinstance(v, (int, float)) and v == v]  # Filter out NaN
            
            if len(valid_values) >= 3:
                print("✅ END-TO-END INTEGRATION TEST PASSED")
                print(f"   ✓ Successfully captured {len(valid_values)} valid ego_speed readings")
                print(f"   ✓ C++ memory monitoring is working correctly")
                print(f"   ✓ Kit server integration is functional")
                return True
            else:
                print("❌ END-TO-END INTEGRATION TEST FAILED")
                print(f"   Only {len(valid_values)} valid ego_speed values received")
                return False
        else:
            print("❌ END-TO-END INTEGRATION TEST FAILED")
            print("   No ego_speed events received")
            return False
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if sio.connected:
            await sio.disconnect()

if __name__ == "__main__":
    result = asyncio.run(test_trace_vars_integration())
    exit(0 if result else 1)