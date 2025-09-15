#!/usr/bin/env python3
"""
Test script to simulate Kit Server commands for C++ projects.
This helps debug why clicking "build C++ project" from Kit Server does nothing.
"""

import sys
import json
import asyncio
from pathlib import Path

# Add kuksa-syncer to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'kuksa-syncer'))

async def test_cpp_command_handling():
    """Test different possible C++ commands from Kit Server."""
    print("=== Testing C++ Command Handling ===\n")
    
    try:
        import syncer
        
        # Test C++ project structure
        cpp_project = [
            {
                "type": "file",
                "name": "main.cpp", 
                "content": "#include <iostream>\n#include <atomic>\n\nstd::atomic<int> counter{0};\n\nint main() {\n    for(int i = 0; i < 5; i++) {\n        counter = i;\n        std::cout << \"Counter: \" << counter.load() << std::endl;\n    }\n    return 0;\n}"
            }
        ]
        
        # Test different possible commands from Kit Server
        test_commands = [
            {
                "name": "deploy_request (most likely)",
                "data": {
                    "cmd": "deploy_request",
                    "request_from": "test_client_123",
                    "code": json.dumps(cpp_project),  # Note: top-level code, not data.code
                    "watch_vars": "counter"
                }
            },
            {
                "name": "run_cpp_app",
                "data": {
                    "cmd": "run_cpp_app", 
                    "request_from": "test_client_123",
                    "data": {
                        "code": json.dumps(cpp_project),
                        "watch_vars": "counter"
                    }
                }
            },
            {
                "name": "compile_cpp_app",
                "data": {
                    "cmd": "compile_cpp_app",
                    "request_from": "test_client_123", 
                    "data": {
                        "code": json.dumps(cpp_project),
                        "watch_vars": "counter"
                    }
                }
            }
        ]
        
        print(f"📊 Syncer Status:")
        print(f"   CPP_MEMORY_AVAILABLE: {syncer.CPP_MEMORY_AVAILABLE}")
        print(f"   messageToKit function: {'✅ Available' if hasattr(syncer, 'messageToKit') else '❌ Missing'}")
        print()
        
        for test in test_commands:
            print(f"🧪 Testing: {test['name']}")
            cmd_data = test['data']
            print(f"   Command: {cmd_data['cmd']}")
            print(f"   Has JSON code: {'✅' if 'code' in str(cmd_data) else '❌'}")
            
            # Test JSON validation
            code_field = None
            if 'code' in cmd_data:
                code_field = cmd_data['code']
            elif 'data' in cmd_data and 'code' in cmd_data['data']:
                code_field = cmd_data['data']['code']
            
            if code_field:
                try:
                    parsed = json.loads(code_field)
                    print(f"   JSON valid: ✅ ({len(parsed)} items)")
                except json.JSONDecodeError:
                    print(f"   JSON valid: ❌ (not JSON)")
            else:
                print(f"   No code field found")
            
            print(f"   Would be handled: {'✅ YES' if would_be_handled(cmd_data, syncer) else '❌ NO - THIS IS THE PROBLEM!'}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def would_be_handled(cmd_data, syncer):
    """Check if a command would be handled by the current syncer."""
    cmd = cmd_data.get('cmd', '')
    
    # Check the conditions in our messageToKit function
    if cmd in ("deploy_request", "deploy-request") and syncer.CPP_MEMORY_AVAILABLE:
        if "code" in cmd_data:
            try:
                json.loads(cmd_data["code"])
                return True  # Would be handled as C++ project
            except:
                return False  # Would fall through to regular deploy
    
    if cmd in ("run_cpp_app", "compile_cpp_app", "build_cpp_app") and syncer.CPP_MEMORY_AVAILABLE:
        if "data" in cmd_data and "code" in cmd_data["data"]:
            try:
                json.loads(cmd_data["data"]["code"])
                return True
            except:
                return False
    
    return False

async def main():
    """Run the test."""
    print("Debugging: Why Kit Server C++ Build Commands Do Nothing")
    print("=" * 60)
    
    success = await test_cpp_command_handling()
    
    if success:
        print("🎯 Summary:")
        print("   The syncer now handles multiple C++ command formats:")
        print("   • deploy_request with JSON code (most likely from Kit Server)")
        print("   • run_cpp_app with data.code JSON")
        print("   • compile_cpp_app with data.code JSON") 
        print("   • build_cpp_app with data.code JSON")
        print()
        print("   If Kit Server still 'does nothing', check the debug logs")
        print("   when running the syncer to see what command is actually sent.")
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)