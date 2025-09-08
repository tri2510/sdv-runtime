#!/usr/bin/env python3
"""
Test script to verify stdout forwarding functionality from C++ applications to kit server frontend.
This simulates what happens in the syncer.py when a C++ application is run.
"""

import asyncio
import sys
import time
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

import cpp_memory_debugger as cpp_debugger


class MockSocketIO:
    """Mock Socket.IO client to capture emitted messages instead of sending to server."""
    
    def __init__(self):
        self.messages = []
    
    async def emit(self, event, data):
        """Capture emitted messages for testing."""
        self.messages.append({
            'event': event,
            'data': data,
            'timestamp': time.time()
        })
        print(f"📡 SOCKET.IO EMIT: {event}")
        print(f"   Data: {data}")
        print(f"   Content: {data.get('data', '')} / Result: {data.get('result', '')}")
        print()

async def mock_send_reply(content, is_error=False):
    """Mock send_reply function that simulates stdout forwarding to kit server."""
    print(f"📤 STDOUT FORWARD: {'[ERROR]' if is_error else '[STDOUT]'} {content.strip()}")
    return True

async def test_stdout_forwarding():
    """Test the complete stdout forwarding flow."""
    print("=== Testing C++ Application Stdout Forwarding ===")
    print()
    
    # Initialize mock components
    mock_sio = MockSocketIO()
    test_kit_id = "test-kit-12345"
    watch_vars = "counter,sensor_value,system_active"
    
    print(f"🔧 Test Parameters:")
    print(f"   Kit ID: {test_kit_id}")
    print(f"   Watch Variables: {watch_vars}")
    print()
    
    # Step 1: Verify compilation
    print("🔨 Step 1: Testing C++ compilation...")
    success, msg = await cpp_debugger.compile_cpp()
    if not success:
        print(f"❌ Compilation failed: {msg}")
        return False
    print(f"✅ Compilation successful")
    print()
    
    # Step 2: Verify binary detection
    print("🔍 Step 2: Testing binary detection...")
    binary_path, pid, run_msg = await cpp_debugger.run_binary()
    if not binary_path:
        print(f"❌ Binary detection failed: {run_msg}")
        return False
    print(f"✅ Binary found: {binary_path}")
    print()
    
    # Step 3: Test the actual stdout monitoring
    print("🚀 Step 3: Testing stdout monitoring and forwarding...")
    print("   This will run the C++ application and capture its stdout...")
    print()
    
    # Create a timeout to prevent infinite running
    timeout_task = asyncio.create_task(asyncio.sleep(10))  # 10 second timeout
    monitoring_task = asyncio.create_task(
        cpp_debugger.periodic_memory_var_report(
            mock_sio, 
            test_kit_id, 
            watch_vars, 
            send_reply_func=mock_send_reply
        )
    )
    
    try:
        # Wait for either the monitoring to complete or timeout
        done, pending = await asyncio.wait(
            [monitoring_task, timeout_task],
            return_when=asyncio.FIRST_COMPLETED
        )
        
        # Cancel any pending tasks
        for task in pending:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
    
    except Exception as e:
        print(f"❌ Error during monitoring: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 4: Analyze results
    print("📊 Step 4: Analyzing captured output...")
    
    stdout_messages = []
    variable_messages = []
    
    for msg in mock_sio.messages:
        data = msg['data']
        if data.get('cmd') == 'run_cpp_app' and 'data' in data:
            content = data['data']
            if not content.startswith('{'):  # Not JSON variable data
                stdout_messages.append(content)
        elif data.get('cmd') == 'trace_vars':
            variable_messages.append(data.get('data', {}))
    
    print(f"📈 Results Summary:")
    print(f"   Total Socket.IO messages: {len(mock_sio.messages)}")
    print(f"   Stdout messages captured: {len(stdout_messages)}")
    print(f"   Variable reports captured: {len(variable_messages)}")
    print()
    
    # Show sample stdout messages
    if stdout_messages:
        print("📝 Sample stdout messages:")
        for i, msg in enumerate(stdout_messages[:5]):  # Show first 5
            print(f"   {i+1}: {msg.strip()}")
        if len(stdout_messages) > 5:
            print(f"   ... and {len(stdout_messages) - 5} more messages")
        print()
    else:
        print("⚠️  No stdout messages captured!")
        print()
    
    # Show sample variable data
    if variable_messages:
        print("🔢 Sample variable data:")
        for i, vars_data in enumerate(variable_messages[:3]):
            print(f"   Report {i+1}: {vars_data}")
        print()
    else:
        print("⚠️  No variable data captured!")
        print()
    
    # Cleanup
    cpp_debugger.cleanup_memory_monitor()
    
    # Final assessment
    success = len(stdout_messages) > 0
    if success:
        print("✅ STDOUT FORWARDING TEST PASSED")
        print("   C++ application stdout is being properly captured and forwarded!")
    else:
        print("❌ STDOUT FORWARDING TEST FAILED") 
        print("   C++ application stdout is NOT being captured properly!")
    
    return success

async def main():
    """Main test function."""
    print("C++ Application Stdout Forwarding Test")
    print("=" * 50)
    print()
    
    success = await test_stdout_forwarding()
    
    print()
    print("=" * 50)
    if success:
        print("🎉 All tests passed! Stdout forwarding is working correctly.")
    else:
        print("💥 Tests failed! Stdout forwarding needs debugging.")
    
    return 0 if success else 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)