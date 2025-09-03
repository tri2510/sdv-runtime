#!/usr/bin/env python3
"""
Test script to simulate frontend communication with the syncer
"""

import asyncio
import json
import socketio

async def test_frontend_communication():
    """Test the complete frontend-backend communication flow"""
    print("=== Testing Frontend Communication ===")
    
    # Create SocketIO client
    sio = socketio.AsyncClient()
    
    # Track received messages
    received_messages = []
    
    @sio.event
    async def connect():
        print("✓ Connected to syncer")
        
    @sio.event 
    async def messageToClient(data):
        received_messages.append(data)
        print(f"📨 Received: {data}")
    
    @sio.event
    async def disconnect():
        print("✓ Disconnected from syncer")
    
    try:
        # Connect to local syncer
        await sio.connect('http://localhost:8766')
        await asyncio.sleep(1)
        
        # Create test C++ project payload (simulating frontend)
        project_payload = {
            "cmd": "run_cpp_app",
            "data": {
                "code": json.dumps({
                    "files": {
                        "main.cpp": """#include <iostream>
#include <chrono>
#include <thread>
#include <atomic>

// Global variables for monitoring
std::atomic<float> ego_speed{60.0f};
std::atomic<int> collision_risk{0};

int main() {
    std::cout << "FCW Test App Starting..." << std::endl;
    
    for(int i = 0; i < 10; i++) {
        std::cout << "Iteration " << i << std::endl;
        ego_speed = 60.0f + (i * 5.0f);
        collision_risk = i * 10;
        std::this_thread::sleep_for(std::chrono::seconds(1));
    }
    
    std::cout << "FCW Test App Completed" << std::endl;
    return 0;
}"""
                    }
                }),
                "watch_vars": "ego_speed,collision_risk"
            }
        }
        
        print("🚀 Sending C++ project to syncer...")
        await sio.emit('messageFromClient', project_payload)
        
        # Wait for process to complete 
        print("⏳ Waiting for memory monitoring to complete...")
        await asyncio.sleep(15)  # Give enough time for the 10-second app
        
        print(f"\n📊 Received {len(received_messages)} messages")
        
        # Check for expected message types
        compile_messages = [msg for msg in received_messages if 'Compiling' in str(msg)]
        variable_messages = [msg for msg in received_messages if 'trace_vars' in str(msg.get('cmd', ''))]
        completion_messages = [msg for msg in received_messages if 'process_complete' in str(msg.get('cmd', ''))]
        
        print(f"✓ Compile messages: {len(compile_messages)}")
        print(f"✓ Variable update messages: {len(variable_messages)}")  
        print(f"✓ Completion messages: {len(completion_messages)}")
        
        # Show some variable updates
        if variable_messages:
            print("\n📈 Sample variable updates:")
            for i, msg in enumerate(variable_messages[:3]):
                data = msg.get('data', {})
                print(f"  Update {i+1}: {data}")
        
        await sio.disconnect()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_frontend_communication())