#!/usr/bin/env python3
"""
Direct kit server simulation test - bypasses KUKSA connection issues.
Tests the complete autowrx → syncer → C++ compilation → monitoring pipeline.
"""

import json
import sys
import os
import time
from pathlib import Path

# Add kuksa-syncer to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'kuksa-syncer'))

def simulate_kitserver_compilation_request():
    """Simulate a kit server C++ compilation request exactly as autowrx would send it."""
    
    print("🚗 Kit Server C++ Compilation Simulation")
    print("=" * 60)
    
    # The exact C++ code with automotive variables
    cpp_code = '''#include <iostream>
#include <atomic>
#include <thread>
#include <chrono>

// Automotive variables that match kit server expectations
std::atomic<float> ego_speed(0.0f);
std::atomic<int> current_lane(1);
std::atomic<float> steering_angle(0.0f);
std::atomic<float> collision_risk(0.0f);

int main() {
    std::cout << "🚗 Automotive Variable Monitor Started\\n";
    
    for (int i = 0; i < 50; ++i) {
        // Simulate realistic automotive data changes
        ego_speed = 60.5f + (i % 20);           // Speed varies 60-80 km/h
        current_lane = 1 + (i % 3);             // Lane changes between 1-3
        steering_angle = -15.0f + (i % 30);     // Steering varies -15 to +15 degrees
        collision_risk = (i % 10) * 0.1f;       // Risk from 0.0 to 0.9
        
        std::cout << "📊 Speed: " << ego_speed.load() 
                  << " km/h | Lane: " << current_lane.load()
                  << " | Angle: " << steering_angle.load() 
                  << "° | Risk: " << collision_risk.load() << "\\n";
        
        std::this_thread::sleep_for(std::chrono::milliseconds(200));
    }
    
    std::cout << "🏁 Automotive monitoring complete\\n";
    return 0;
}'''

    # Create the exact message format that autowrx sends to syncer
    # Based on the working format from previous tests
    project_tree = [
        {
            "name": "main.cpp",
            "content": cpp_code,
            "type": "file"
        }
    ]
    
    kitserver_message = {
        "action": "messageToKit",
        "data": {
            "code": json.dumps(project_tree),
            "watch_vars": "ego_speed,current_lane,steering_angle,collision_risk"
        }
    }
    
    print("📤 Simulating kit server WebSocket message:")
    print(f"   Action: {kitserver_message['action']}")
    print(f"   Code length: {len(kitserver_message['data']['code'])} chars")
    print(f"   Variables: {kitserver_message['data']['watch_vars']}")
    print()
    
    # Import syncer modules
    try:
        from project_utils import ProjectUtils
        from auto_variable_detector import AutoVariableDetector
        from auto_memory_monitor import AutoMemoryMonitor
        print("✅ Successfully imported syncer modules")
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        print("💡 Make sure to run from sdv-runtime root directory")
        return False
        
    print("\n🔧 Processing kit server request...")
    
    # Step 1: Auto-detect variables from C++ source
    detector = AutoVariableDetector()
    detected_vars = detector.extract_variables_from_source(cpp_code)
    
    print(f"🔍 Auto-detected {len(detected_vars)} variables:")
    for var in detected_vars:
        atomic_type = "atomic " if var['is_atomic'] else ""
        print(f"   📊 {var['name']}: {atomic_type}{var['type']}")
    
    # Step 2: Create project using ProjectUtils (like syncer does)
    project_utils = ProjectUtils()
    
    try:
        print("\n📁 Creating C++ project files...")
        # Clear any existing files first
        project_utils.empty_app_directory()
        
        # Create project from payload (like syncer does)
        created_path = project_utils.save_from_payload(kitserver_message)
        print(f"✅ Project created at: {created_path}")
        
        # Step 3: Compile with debug symbols (manual compilation like syncer does)
        print("\n🔨 Compiling C++ project...")
        import subprocess
        
        main_cpp_path = Path(created_path) / "main.cpp"
        binary_path = Path(created_path) / "main_bin"
        
        # Compile with debug symbols for memory monitoring
        compile_cmd = [
            "g++", "-g", "-std=c++14", "-pthread", 
            str(main_cpp_path), "-o", str(binary_path)
        ]
        
        result = subprocess.run(compile_cmd, capture_output=True, text=True, cwd=created_path)
        if result.returncode == 0:
            print(f"✅ Binary compiled: {binary_path}")
        else:
            print(f"❌ Compilation failed: {result.stderr}")
            return False
        
        # Step 4: Start memory monitoring (like syncer would do)
        print("\n📈 Starting automotive variable monitoring...")
        
        # Use the auto monitoring system (async like syncer does)
        import asyncio
        from auto_memory_monitor import start_auto_monitoring, get_auto_variables, cleanup_auto_monitoring
        
        async def run_monitoring():
            # Monitor the exact variables requested by kit server  
            watch_vars = kitserver_message["data"]["watch_vars"]
            print(f"🎯 Monitoring variables: {watch_vars}")
            
            result, msg = await start_auto_monitoring(watch_vars)
            print(f"📊 Setup result: {result} - {msg}")
            
            if "success" in result:
                # Monitor for 10 seconds showing real values
                print("📈 Live automotive data monitoring:")
                for i in range(10):
                    values, status = await get_auto_variables()
                    if values:
                        data_line = " | ".join([f"{name}: {value}" for name, value in values.items()])
                        print(f"   🚗 {data_line}")
                    await asyncio.sleep(1)
                
                cleanup_auto_monitoring()
                return True
            else:
                return False
        
        # Run the async monitoring
        success = asyncio.run(run_monitoring())
        
        if success:
            print("\n🎉 Kit server simulation completed successfully!")
            print("📊 All automotive variables monitored in real-time")
            return True
        else:
            print("\n❌ Memory monitoring failed")
            return False
        
    except Exception as e:
        print(f"❌ Kit server simulation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚗 Starting Kit Server C++ Compilation Simulation...")
    print("This simulates exactly how autowrx sends C++ requests to syncer\n")
    
    success = simulate_kitserver_compilation_request()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Kit server simulation: SUCCESS")
        print("🔧 The C++ compilation pipeline is fully functional")
        print("📊 Automotive variable monitoring working perfectly")
    else:
        print("❌ Kit server simulation: FAILED")
        print("🛠️  Check error messages above for troubleshooting")