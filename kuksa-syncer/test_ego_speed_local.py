#!/usr/bin/env python3
import socketio
import asyncio
import json
import time

sio = socketio.AsyncClient()

@sio.event
async def connect():
    print('✅ Connected to local syncer server')

@sio.event
async def disconnect():
    print('❌ Disconnected from syncer server')

@sio.event 
async def messageToKit_kitReply(data):
    print(f"📨 Received reply: {data}")

@sio.event
async def trace_vars(data):
    print(f"📊 VARIABLE TRACE: {data}")
    if 'ego_speed' in str(data):
        print(f"🎯 EGO_SPEED DETECTED: {data}")

@sio.event
async def cpp_output(data):
    print(f"⚡ C++ output: {data}")

@sio.event
async def debug_info(data):
    print(f"🔍 Debug info: {data}")

async def test_cmake_multidir_local():
    """Test cmake-multidir project with ego_speed monitoring on local server"""
    try:
        # Connect to local syncer
        await sio.connect('http://localhost:5000')
        
        # Test cmake-multidir project
        cpp_project_data = {
            "project_path": "/home/htr1hc/01_SDV/59_integrate_sdv-runtime_cpp/sdv-runtime-fork/cpp-projects/cmake-multidir",
            "executable_path": "build/multidir_system",
            "trace_vars": ["ego_speed", "throttle_position", "steering_angle"]
        }
        
        message = {
            "cmd": "run_cpp_app",
            "request_from": "debug_client",
            "data": {
                "code": json.dumps(cpp_project_data)
            }
        }
        
        print("🚀 Testing cmake-multidir project with ego_speed monitoring...")
        print(f"📂 Project data: {json.dumps(cpp_project_data, indent=2)}")
        
        await sio.emit('messageToKit', message)
        
        # Wait and listen for responses
        print("⏳ Waiting for variable traces (ego_speed should appear)...")
        await asyncio.sleep(20)  # Wait for execution and monitoring
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await sio.disconnect()

if __name__ == "__main__":
    asyncio.run(test_cmake_multidir_local())
