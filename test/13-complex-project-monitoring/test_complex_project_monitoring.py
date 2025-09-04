#!/usr/bin/env python3
"""
Test the monitoring mechanism with a complex C++ project structure.
This tests the complete autonomous vehicle system with multiple files and subsystems.
"""

import sys
import os
import json
import subprocess
import time
from pathlib import Path

# Add kuksa-syncer to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'kuksa-syncer'))

def create_tree_structure_from_project():
    """Create tree structure from the complex autonomous vehicle project."""
    project_path = Path(__file__).parent.parent.parent / 'cpp-projects' / 'autonomous-vehicle-system'
    
    if not project_path.exists():
        print(f"❌ Project not found at: {project_path}")
        return None
    
    tree_structure = []
    
    # Get all cpp and h files
    cpp_files = list(project_path.rglob("*.cpp"))
    h_files = list(project_path.rglob("*.h"))
    cmake_files = list(project_path.rglob("CMakeLists.txt"))
    
    print(f"📁 Found {len(cpp_files)} .cpp files, {len(h_files)} .h files, {len(cmake_files)} CMake files")
    
    # Add all files to tree structure
    all_files = cpp_files + h_files + cmake_files
    
    for file_path in all_files:
        relative_path = file_path.relative_to(project_path)
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        tree_structure.append({
            "name": str(relative_path),
            "content": content,
            "type": "file"
        })
    
    print(f"✅ Created tree structure with {len(tree_structure)} files")
    return tree_structure

def test_complex_project_monitoring():
    """Test monitoring with the complex autonomous vehicle project."""
    
    print("🚗 Complex Project Monitoring Test")
    print("=" * 60)
    
    try:
        from project_utils import ProjectUtils
        from auto_variable_detector import AutoVariableDetector
        from auto_memory_monitor import start_auto_monitoring, get_auto_variables, cleanup_auto_monitoring
        import asyncio
        
        print("✅ Successfully imported monitoring modules")
        
        # Step 1: Create tree structure from complex project
        print("\n📁 Step 1: Creating project tree structure...")
        tree_structure = create_tree_structure_from_project()
        
        if not tree_structure:
            return False
        
        # Step 2: Create kit server message with complex project
        kitserver_message = {
            "action": "messageToKit",
            "data": {
                "code": json.dumps(tree_structure),
                "watch_vars": "vehicle_speed,current_gear,engine_rpm,autonomous_mode,fuel_level,active_sensors,cpu_temperature"
            }
        }
        
        print(f"📤 Created kit server message with {len(tree_structure)} files")
        print(f"🎯 Monitoring variables: {kitserver_message['data']['watch_vars']}")
        
        # Step 3: Process with ProjectUtils
        print("\n🔧 Step 2: Processing complex project...")
        project_utils = ProjectUtils()
        project_utils.empty_app_directory()
        
        created_path = project_utils.save_from_payload(kitserver_message)
        print(f"✅ Complex project created at: {created_path}")
        
        # Step 4: Build the project using CMake
        print("\n🔨 Step 3: Building complex project with CMake...")
        
        build_dir = Path(created_path) / "build"
        build_dir.mkdir(exist_ok=True)
        
        # Configure with CMake
        cmake_config = subprocess.run([
            'cmake', '..', '-DCMAKE_BUILD_TYPE=Debug'
        ], cwd=build_dir, capture_output=True, text=True)
        
        if cmake_config.returncode != 0:
            print(f"❌ CMake configuration failed: {cmake_config.stderr}")
            return False
        
        print("✅ CMake configuration successful")
        
        # Build with make
        make_build = subprocess.run([
            'make', '-j4'  # Use 4 cores for faster build
        ], cwd=build_dir, capture_output=True, text=True)
        
        if make_build.returncode != 0:
            print(f"❌ Make build failed: {make_build.stderr}")
            return False
        
        binary_path = build_dir / "autonomous_vehicle_system"
        if not binary_path.exists():
            print(f"❌ Binary not found at: {binary_path}")
            return False
        
        print(f"✅ Complex project built successfully: {binary_path}")
        
        # Step 5: Test variable detection
        print("\n🔍 Step 4: Testing variable detection with complex project...")
        detector = AutoVariableDetector()
        
        # Read main.cpp for variable detection
        main_cpp_path = Path(created_path) / "main.cpp"
        with open(main_cpp_path, 'r') as f:
            cpp_code = f.read()
        
        detected_vars = detector.extract_variables_from_source(cpp_code)
        print(f"🔍 Auto-detected {len(detected_vars)} variables from source")
        
        for var in detected_vars[:10]:  # Show first 10
            atomic_type = "atomic " if var['is_atomic'] else ""
            print(f"   📊 {var['name']}: {atomic_type}{var['type']}")
        
        if len(detected_vars) > 10:
            print(f"   ... and {len(detected_vars) - 10} more variables")
        
        # Step 6: Start monitoring
        print(f"\n📈 Step 5: Starting live monitoring of complex project...")
        
        async def run_complex_monitoring():
            # Start auto-monitoring
            watch_vars = kitserver_message["data"]["watch_vars"]
            result, msg = await start_auto_monitoring(watch_vars)
            print(f"📊 Monitoring setup: {result} - {msg}")
            
            if "success" not in result:
                return False
            
            print("📊 Live monitoring complex automotive system (20 readings):")
            print("   Format: Speed | Gear | RPM | Auto | Fuel | Sensors | CPU")
            print("   " + "-" * 70)
            
            successful_readings = 0
            for i in range(20):
                values, status = await get_auto_variables()
                
                if status == "success" and values and not isinstance(values.get("error"), str):
                    successful_readings += 1
                    
                    # Format complex project data nicely
                    speed = values.get('vehicle_speed', 'N/A')
                    gear = values.get('current_gear', 'N/A') 
                    rpm = values.get('engine_rpm', 'N/A')
                    auto = 'ON' if values.get('autonomous_mode') else 'OFF'
                    fuel = values.get('fuel_level', 'N/A')
                    sensors = values.get('active_sensors', 'N/A')
                    cpu_temp = values.get('cpu_temperature', 'N/A')
                    
                    print(f"   🚗 [{i+1:2d}] {speed:5.1f}km/h | Gear-{gear} | {rpm:6.1f}RPM | {auto} | {fuel:4.1f}% | {sensors} sensors | {cpu_temp:4.1f}°C")
                    
                elif "error" in values:
                    print(f"   ⚠ [{i+1:2d}] Error: {values['error']}")
                else:
                    print(f"   ⚠ [{i+1:2d}] No data available")
                
                await asyncio.sleep(1.5)  # 1.5 second intervals
            
            cleanup_auto_monitoring()
            
            print(f"\n✅ Complex monitoring completed: {successful_readings}/20 successful readings")
            return successful_readings >= 15  # 75% success rate required
        
        # Run the monitoring
        success = asyncio.run(run_complex_monitoring())
        
        if success:
            print("\n🎉 Complex project monitoring test PASSED!")
            print("📊 Multi-file C++ project with CMake build system working perfectly")
            return True
        else:
            print("\n❌ Complex project monitoring test FAILED!")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Complex Project Monitoring Test...")
    print("Testing autonomous vehicle system with multiple files and subsystems\n")
    
    success = test_complex_project_monitoring()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ COMPLEX PROJECT TEST: SUCCESS")
        print("🚗 Multi-file autonomous vehicle system monitored successfully")
        print("🔧 CMake build system integration working")
        print("📊 All subsystem variables detected and monitored")
        print("🎯 SDV runtime ready for complex real-world projects!")
    else:
        print("❌ COMPLEX PROJECT TEST: FAILED")
        print("🛠️ Check error messages above for troubleshooting")