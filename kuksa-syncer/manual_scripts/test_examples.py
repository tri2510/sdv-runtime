#!/usr/bin/env python3
"""
Test runner for C++ project examples.
Tests build and memory monitoring functionality across different build systems.
"""

import json
import asyncio
import sys
from pathlib import Path
from project_utils import ProjectUtils
import cpp_memory_debugger as cpp_debugger

async def test_example(example_file: Path):
    """Test a single C++ example."""
    print(f"\n{'=' * 60}")
    print(f"🧪 Testing: {example_file.name}")
    print('=' * 60)
    
    try:
        # Load example
        with open(example_file, 'r') as f:
            example_data = json.load(f)
        
        project_name = example_data.get("name", "Unknown")
        build_system = example_data.get("build_system", "auto")
        print(f"📋 Project: {project_name}")
        print(f"🔨 Build System: {build_system}")
        
        # Setup project
        project_utils = ProjectUtils()
        project_path = project_utils.save_from_json_project(example_data)
        print(f"📁 Project created in: {project_path}")
        
        # Test compilation
        print(f"\n🔨 Testing compilation...")
        compile_ok, compile_msg = await cpp_debugger.compile_cpp()
        print(compile_msg)
        
        if not compile_ok:
            print(f"❌ COMPILATION FAILED for {project_name}")
            return False
        
        # Test binary execution
        print(f"\n🚀 Testing binary execution...")
        binary_path, pid, run_msg = await cpp_debugger.run_binary()
        print(run_msg)
        
        if binary_path is None:
            print(f"❌ BINARY EXECUTION FAILED for {project_name}")
            return False
        
        print(f"✅ SUCCESS: {project_name} compiled and ran successfully")
        return True
        
    except Exception as e:
        print(f"💥 ERROR testing {example_file.name}: {str(e)}")
        return False

async def main():
    """Main test runner."""
    print("🚀 C++ Examples Test Suite")
    print("=" * 60)
    
    # Find all example files
    examples_dir = Path(__file__).parent / "cpp_projects"
    if not examples_dir.exists():
        print("❌ No cpp_projects directory found!")
        sys.exit(1)
    
    example_files = list(examples_dir.glob("*.json"))
    if not example_files:
        print("❌ No example JSON files found!")
        sys.exit(1)
    
    print(f"Found {len(example_files)} examples to test:")
    for f in example_files:
        print(f"  📄 {f.name}")
    
    # Test each example
    results = []
    for example_file in sorted(example_files):
        success = await test_example(example_file)
        results.append((example_file.name, success))
    
    # Print summary
    print(f"\n{'=' * 60}")
    print("📊 TEST SUMMARY")
    print('=' * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {name}")
    
    print(f"\nResults: {passed}/{total} examples passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("⚠️  Some tests failed")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())