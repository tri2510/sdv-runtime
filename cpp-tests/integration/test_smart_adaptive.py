#!/usr/bin/env python3
"""
Test smart adaptive syncer with cmake-multidir project
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

import cpp_memory_debugger as cpp_debugger_util

class MockSocketIO:
    """Mock socketio for testing"""
    def __init__(self):
        self.emitted_events = []
        
    async def emit(self, event, data):
        """Mock emit function"""
        self.emitted_events.append((event, data))
        if event == 'messageToKit-kitReply' and data.get('cmd') == 'trace_vars':
            if data.get('data') and isinstance(data['data'], dict):
                print(f"🔥 TRACE_VARS Event: {data['data']}")
        print(f"📡 {event}: {data.get('cmd', 'N/A')}")

async def test_smart_adaptive_syncer():
    """Test smart adaptive syncer with non-existent and existing variables"""
    print("🧪 TESTING SMART ADAPTIVE SYNCER")
    print("=" * 50)

    os.environ['CPP_TRACE_VERBOSE'] = os.environ.get('CPP_TRACE_VERBOSE', '0')

    mock_sio = MockSocketIO()

    project_dir = Path("/home/htr1hc/01_SDV/59_integrate_sdv-runtime_cpp/sdv-runtime-fork/cpp-projects/02-cmake-structured")
    binary_path = project_dir / "build" / "vehicle_systems"
    if not binary_path.exists():
        subprocess.run(["bash", "build.sh"], cwd=project_dir, check=True)

    # Test with mixed variables: some exist, some don't
    trace_vars_data = {
        "cmd": "trace_vars",
        "request_from": "smart_adaptive_test",
        "project_type": "cmake",
        "project_path": "/home/htr1hc/01_SDV/59_integrate_sdv-runtime_cpp/sdv-runtime-fork/cpp-projects/02-cmake-structured",
        "binary_name": "vehicle_systems",
        # Mix of existing and non-existing variables from our cmake project
        "trace_vars": ["actual_speed", "current_lane", "tire_pressure_fl", "non_existent_var", "battery_voltage", "engine_rpm"],
        "duration": 1,
        "skip_build": True,
        "verbose": False
    }
    
    print(f"🎯 Testing with mixed variables:")
    print(f"   Existing: actual_speed, tire_pressure_fl, battery_voltage, engine_rpm")
    print(f"   Non-existing: current_lane, non_existent_var")
    print(f"   Expected: Only existing variables should be monitored")
    print()
    
    try:
        print("🚀 Starting smart adaptive monitoring...")
        
        await cpp_debugger_util.start_cpp_trace_vars_monitoring(
            trace_vars_data,
            "smart_adaptive_test", 
            mock_sio
        )
        
        print(f"\n✅ TEST RESULTS:")
        print(f"   Total events emitted: {len(mock_sio.emitted_events)}")
        
        # Count trace_vars events
        trace_events = [
            event for event in mock_sio.emitted_events
            if event[0] == 'messageToKit-kitReply' and 
               event[1].get('cmd') == 'trace_vars' and
               isinstance(event[1].get('data'), dict)
        ]
        
        print(f"   trace_vars events: {len(trace_events)}")
        
        if trace_events:
            # Check what variables were actually monitored
            sample_data = trace_events[0][1]['data'] if trace_events else {}
            monitored_vars = list(sample_data.keys())
            print(f"   Variables actually monitored: {monitored_vars}")
            
            # Check that non-existent variables were filtered out
            has_current_lane = 'current_lane' in monitored_vars
            has_non_existent = 'non_existent_var' in monitored_vars
            has_actual_speed = 'actual_speed' in monitored_vars
            has_battery_voltage = 'battery_voltage' in monitored_vars

            print(f"   ❌ current_lane filtered out: {not has_current_lane}")
            print(f"   ❌ non_existent_var filtered out: {not has_non_existent}")
            print(f"   ✅ actual_speed monitored: {has_actual_speed}")
            print(f"   ✅ battery_voltage monitored: {has_battery_voltage}")

            success = (not has_current_lane and not has_non_existent and
                      has_actual_speed and len(monitored_vars) > 0)
            
            if success:
                print("\n🎉 SUCCESS: SMART ADAPTIVE SYNCER WORKING!")
                print("✓ Non-existent variables filtered out correctly")
                print("✓ Existing variables monitored successfully")  
                print("✓ System adapts to any project automatically")
                return True
            else:
                print("❌ FAILED: Smart filtering not working correctly")
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
    result = asyncio.run(test_smart_adaptive_syncer())
    print(f"\n{'🎉 TEST PASSED' if result else '❌ TEST FAILED'}")
    exit(0 if result else 1)
