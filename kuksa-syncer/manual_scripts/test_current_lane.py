#!/usr/bin/env python3
"""
Test specifically for current_lane updates in FCW system
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import cpp_memory_debugger as cpp_debugger_util

class LaneTrackingSocketIO:
    """Mock socketio specifically for tracking lane changes"""
    def __init__(self):
        self.lane_values = []
        self.update_count = 0
        
    async def emit(self, event, data):
        """Track current_lane value changes"""
        if event == 'messageToKit-kitReply' and data.get('cmd') == 'trace_vars':
            if data.get('data') and isinstance(data['data'], dict):
                fcw_data = data['data']
                if 'current_lane' in fcw_data:
                    lane_value = fcw_data['current_lane']
                    self.lane_values.append(lane_value)
                    self.update_count += 1
                    
                    print(f"🛣️  Update #{self.update_count}: current_lane = {lane_value}")
                    
                    # Show other key values for context
                    if self.update_count % 5 == 0:  # Every 5th update
                        print(f"   Context: warning_level={fcw_data.get('warning_level', 'N/A')}, "
                              f"ego_speed={fcw_data.get('ego_speed', 'N/A'):.1f}")

async def test_current_lane():
    """Test current_lane specifically"""
    print("🛣️  TESTING CURRENT_LANE UPDATES IN FCW SYSTEM")
    print("=" * 50)
    
    mock_sio = LaneTrackingSocketIO()
    
    # Focus test on current_lane
    trace_vars_data = {
        "cmd": "trace_vars", 
        "request_from": "lane_change_test",
        "project_type": "g++",
        "project_path": "/home/htr1hc/01_SDV/59_integrate_sdv-runtime_cpp/sdv-runtime-fork/cpp-projects/fcw-system",
        "binary_name": "fcw_advanced",
        "trace_vars": ["current_lane", "warning_level", "ego_speed"],  # Just key vars
        "duration": 8  # 8 seconds
    }
    
    print(f"🎯 Monitoring: current_lane (should change from 2→1 at cycle 35)")
    print(f"📊 Lane change timing: cycle 35 = 35×200ms = 7 seconds")
    print(f"📊 Monitoring duration: 8 seconds - should capture the change!")
    print()
    
    try:
        print("🚀 Starting lane monitoring...")
        
        await cpp_debugger_util.start_cpp_trace_vars_monitoring(
            trace_vars_data,
            "lane_change_test", 
            mock_sio
        )
        
        print(f"\n✅ LANE MONITORING RESULTS:")
        print(f"   Total updates: {mock_sio.update_count}")
        print(f"   Lane values captured: {mock_sio.lane_values}")
        
        if len(mock_sio.lane_values) > 0:
            initial_lane = mock_sio.lane_values[0]
            final_lane = mock_sio.lane_values[-1]
            unique_lanes = list(set(mock_sio.lane_values))
            
            print(f"   Initial lane: {initial_lane}")
            print(f"   Final lane: {final_lane}")  
            print(f"   Unique lanes seen: {unique_lanes}")
            
            # Check for lane change
            lane_changed = len(unique_lanes) > 1
            has_lane_1 = 1 in unique_lanes
            
            print(f"\n📊 LANE CHANGE ANALYSIS:")
            print(f"   Lane change detected: {lane_changed}")
            print(f"   Contains lane 1 (left): {has_lane_1}")
            
            if lane_changed and has_lane_1:
                change_index = mock_sio.lane_values.index(1)
                print(f"   Lane change occurred at update #{change_index + 1}")
                print("\n🎉 SUCCESS: CURRENT_LANE UPDATES WORKING!")
                print("✓ Lane changes are properly monitored from kit server")
                return True
            else:
                print("\n❌ ISSUE: Lane change not captured within monitoring window")
                return False
        else:
            print("❌ FAILED: No lane data captured")
            return False
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_current_lane())
    print(f"\n{'🎉 LANE TEST PASSED' if result else '❌ LANE TEST FAILED'}")
    exit(0 if result else 1)