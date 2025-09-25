#!/usr/bin/env python3
import socketio
import asyncio
import json

sio = socketio.AsyncClient()

@sio.event
async def connect():
    print('Connected to server')

@sio.event
async def disconnect():
    print('Disconnected from server')

@sio.event 
async def messageToKit_kitReply(data):
    print(f"Received reply: {data}")

async def test_cpp_project():
    """Test C++ project via Socket.IO"""
    await sio.connect('http://localhost:3000')
    
    # Test 1: Basic monitoring project
    cpp_project_data = {
        "project_path": "/home/htr1hc/01_SDV/59_integrate_sdv-runtime_cpp/sdv-runtime-fork/cpp_projects/01-basic-monitoring",
        "executable_path": "build/basic_monitor",
        "trace_vars": ["counter", "sensor_value", "system_active"]
    }
    
    message = {
        "cmd": "run_cpp_app",
        "request_from": "test_client",
        "data": {
            "code": json.dumps(cpp_project_data)
        }
    }
    
    print("Testing basic-monitoring project...")
    await sio.emit('messageToKit', message)
    await asyncio.sleep(8)  # Wait for execution
    
    # Test 2: Python app (to verify Python still works)
    python_code = '''
import time
print("Testing Python functionality")
for i in range(5):
    print(f"Python cycle {i+1}")
    time.sleep(0.5)
print("Python test completed")
'''
    
    python_message = {
        "cmd": "run_python_app", 
        "request_from": "test_client",
        "data": {
            "code": python_code
        }
    }
    
    print("\nTesting Python functionality...")
    await sio.emit('messageToKit', python_message)
    await asyncio.sleep(5)  # Wait for execution
    
    await sio.disconnect()

if __name__ == "__main__":
    asyncio.run(test_cpp_project())