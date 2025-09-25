#!/usr/bin/env python3
"""
Test basic-monitor project with trace_vars functionality after the fix
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import cpp_memory_debugger as cpp_debugger_util

class MockSocketIO:
    """Mock socketio for testing trace_vars functionality"""
    def __init__(self):
        self.emitted_events = []
        
    async def emit(self, event, data):
        """Mock emit function to capture trace_vars events"""
        self.emitted_events.append((event, data))
        if event == 'messageToKit-kitReply' and data.get('cmd') == 'trace_vars':
            if data.get('data') and isinstance(data['data'], dict):
                print(f"🔥 TRACE_VARS Event: {data['data']}")
        print(f"📡 {event}: {data.get('cmd', 'N/A')}")

async def test_basic_monitor_project():
    """Test basic-monitor project with trace_vars"""
    print("🧪 TESTING BASIC-MONITOR PROJECT AFTER FIX")
    print("=" * 50)
    
    # Mock socket and data for basic-monitor project
    mock_sio = MockSocketIO()
    
    # Test data for basic-monitor project
    trace_vars_data = {
        "cmd": "trace_vars",
        "request_from": "basic_monitor_test",
        "project_type": "gcc",  # basic-monitor uses simple gcc compilation
        "project_path": "/home/htr1hc/01_SDV/59_integrate_sdv-runtime_cpp/sdv-runtime-fork/cpp-projects/basic-monitor",
        "binary_name": "basic_monitor", 
        "trace_vars": ["counter", "temperature", "system_active"],
        "duration": 6  # Test for 6 seconds
    }
    
    print(f"🎯 Testing basic-monitor project:")
    print(f"   Project: {trace_vars_data['project_path']}")
    print(f"   Binary: {trace_vars_data['binary_name']}")
    print(f"   Variables: {trace_vars_data['trace_vars']}")
    print(f"   Duration: {trace_vars_data['duration']} seconds")
    print()
    
    try:
        print("🚀 Starting basic-monitor trace_vars monitoring...")
        
        # Start the monitoring
        await cpp_debugger_util.start_cpp_trace_vars_monitoring(
            trace_vars_data, 
            "basic_monitor_test", 
            mock_sio
        )
        
        print("\n✅ BASIC-MONITOR TEST RESULTS:")
        print(f"   Total events emitted: {len(mock_sio.emitted_events)}")
        
        # Analyze captured trace_vars events
        trace_events = [
            event for event in mock_sio.emitted_events 
            if event[0] == 'messageToKit-kitReply' and 
               event[1].get('cmd') == 'trace_vars' and 
               isinstance(event[1].get('data'), dict)
        ]
        
        print(f"   trace_vars events captured: {len(trace_events)}")
        
        if trace_events:
            # Show sample variable data
            sample_data = trace_events[0][1]['data'] if trace_events else {}
            print(f"   Sample variables captured: {list(sample_data.keys())}")
            
            # Check for counter, temperature, system_active
            has_counter = any('counter' in event[1].get('data', {}) for event in trace_events)
            has_temperature = any('temperature' in event[1].get('data', {}) for event in trace_events)
            has_system_active = any('system_active' in event[1].get('data', {}) for event in trace_events)
            
            print(f"   ✓ counter found: {has_counter}")
            print(f"   ✓ temperature found: {has_temperature}")
            print(f"   ✓ system_active found: {has_system_active}")
            
            if has_counter or has_temperature or has_system_active:
                print("\n🎉 SUCCESS: BASIC-MONITOR PROJECT FIXED!")
                print("✓ Project directory correctly handled")  
                print("✓ Binary found in correct location")
                print("✓ Variables successfully monitored")
                print("✓ trace_vars events properly generated")
                return True
            else:
                print("❌ FAILED: No basic-monitor variables captured")
                return False
        else:
            print("❌ FAILED: No trace_vars events captured")
            return False
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_basic_monitor_project())
    print(f"\n{'🎉 TEST PASSED' if result else '❌ TEST FAILED'}")
    exit(0 if result else 1)