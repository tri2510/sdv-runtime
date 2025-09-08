#!/usr/bin/env python3
"""
Test FCW Advanced System signal monitoring from kit server
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import cpp_memory_debugger as cpp_debugger_util

class MockSocketIO:
    """Mock socketio for testing FCW monitoring"""
    def __init__(self):
        self.emitted_events = []
        self.fcw_data_count = 0
        
    async def emit(self, event, data):
        """Mock emit function"""
        self.emitted_events.append((event, data))
        
        if event == 'messageToKit-kitReply' and data.get('cmd') == 'trace_vars':
            if data.get('data') and isinstance(data['data'], dict):
                self.fcw_data_count += 1
                fcw_vars = data['data']
                
                # Print every 3rd update to avoid spam but show progress
                if self.fcw_data_count % 3 == 0:
                    print(f"🚨 FCW Update #{self.fcw_data_count}:")
                    
                    # Core FCW variables
                    if 'ego_speed' in fcw_vars:
                        print(f"   🚗 Ego Speed: {fcw_vars['ego_speed']:.1f} km/h")
                    if 'distance_to_front' in fcw_vars:
                        print(f"   📏 Distance: {fcw_vars['distance_to_front']:.1f}m")
                    if 'warning_level' in fcw_vars:
                        level = int(fcw_vars['warning_level'])
                        warning_text = ["None", "Caution", "Warning", "CRITICAL"][level]
                        print(f"   ⚠️  Warning: Level {level} ({warning_text})")
                    if 'brake_assist_active' in fcw_vars:
                        brake_status = "ACTIVE" if fcw_vars['brake_assist_active'] else "OFF"
                        print(f"   🛑 Brake Assist: {brake_status}")
                    if 'collision_probability' in fcw_vars:
                        risk = fcw_vars['collision_probability'] * 100
                        print(f"   🎯 Collision Risk: {risk:.1f}%")
                        
        print(f"📡 {event}: {data.get('cmd', 'N/A')}")

async def test_fcw_monitoring():
    """Test FCW advanced system monitoring from kit server"""
    print("🚨 TESTING FCW ADVANCED SYSTEM MONITORING")
    print("=" * 60)
    
    mock_sio = MockSocketIO()
    
    # Test with FCW system variables
    trace_vars_data = {
        "cmd": "trace_vars", 
        "request_from": "fcw_monitoring_test",
        "project_type": "g++",
        "project_path": "/home/htr1hc/01_SDV/59_integrate_sdv-runtime_cpp/sdv-runtime-fork/cpp-projects/fcw-system",
        "binary_name": "fcw_advanced",
        # Key FCW monitoring variables
        "trace_vars": [
            "ego_speed", 
            "front_vehicle_speed", 
            "distance_to_front", 
            "time_to_collision",
            "warning_level", 
            "brake_assist_active", 
            "deceleration_rate",
            "current_lane", 
            "collision_probability",
            "adaptive_cruise_active",
            "target_following_distance",
            "detected_objects"
        ],
        "duration": 8  # 8 seconds of monitoring
    }
    
    print(f"🎯 Testing FCW variables:")
    for var in trace_vars_data["trace_vars"]:
        print(f"   - {var}")
    print(f"📊 Expected: Real-time ADAS data with collision warnings")
    print()
    
    try:
        print("🚀 Starting FCW monitoring from kit server...")
        
        await cpp_debugger_util.start_cpp_trace_vars_monitoring(
            trace_vars_data,
            "fcw_monitoring_test", 
            mock_sio
        )
        
        print(f"\n✅ FCW MONITORING RESULTS:")
        print(f"   Total events emitted: {len(mock_sio.emitted_events)}")
        
        # Count FCW trace_vars events
        fcw_events = [
            event for event in mock_sio.emitted_events
            if event[0] == 'messageToKit-kitReply' and 
               event[1].get('cmd') == 'trace_vars' and
               isinstance(event[1].get('data'), dict)
        ]
        
        print(f"   FCW data updates: {len(fcw_events)}")
        
        if fcw_events:
            # Analyze the FCW data
            sample_data = fcw_events[0][1]['data']
            monitored_vars = list(sample_data.keys())
            print(f"   Variables monitored: {len(monitored_vars)}")
            
            # Check key FCW variables
            key_vars = ['ego_speed', 'distance_to_front', 'warning_level', 'collision_probability']
            detected_key_vars = [var for var in key_vars if var in monitored_vars]
            
            print(f"   Core FCW vars detected: {len(detected_key_vars)}/{len(key_vars)}")
            
            # Show final status
            if len(fcw_events) > 1:
                final_data = fcw_events[-1][1]['data']
                print(f"\n🏁 FINAL FCW STATUS:")
                for var in ['ego_speed', 'warning_level', 'brake_assist_active', 'collision_probability']:
                    if var in final_data:
                        value = final_data[var]
                        if var == 'collision_probability':
                            print(f"   {var}: {value*100:.1f}%")
                        elif var == 'brake_assist_active':
                            print(f"   {var}: {'ACTIVE' if value else 'OFF'}")
                        else:
                            print(f"   {var}: {value}")
            
            success = (len(detected_key_vars) >= 3 and len(fcw_events) > 5)
            
            if success:
                print("\n🎉 SUCCESS: FCW MONITORING FROM KIT SERVER WORKING!")
                print("✓ Advanced FCW system variables monitored successfully")
                print("✓ Real-time collision warning data captured")  
                print("✓ ADAS monitoring system fully operational")
                return True
            else:
                print("❌ FAILED: Not enough FCW variables detected or insufficient data")
                return False
        else:
            print("❌ FAILED: No FCW data events captured")
            return False
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_fcw_monitoring())
    print(f"\n{'🎉 FCW TEST PASSED' if result else '❌ FCW TEST FAILED'}")
    exit(0 if result else 1)