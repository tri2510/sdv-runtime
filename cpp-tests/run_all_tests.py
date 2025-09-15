#!/usr/bin/env python3
"""
Master test runner for the unified C++ variable monitoring test suite
"""
import os
import sys
import asyncio
import subprocess
from pathlib import Path

# Add kuksa-syncer to path for imports
current_dir = Path(__file__).parent
kuksa_syncer_path = current_dir.parent / "kuksa-syncer"
sys.path.insert(0, str(kuksa_syncer_path))

class TestRunner:
    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.results = {
            'unit': {},
            'integration': {},
            'verification': {}
        }

    async def run_test_file(self, test_file):
        """Run a single test file and capture results"""
        print(f"🧪 Running: {test_file.name}")

        try:
            # Run the test file
            process = await asyncio.create_subprocess_exec(
                sys.executable, str(test_file),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(test_file.parent)
            )

            stdout, stderr = await process.communicate()

            success = process.returncode == 0
            output = stdout.decode('utf-8', errors='ignore')
            error_output = stderr.decode('utf-8', errors='ignore')

            # Look for success indicators in output
            if 'TEST PASSED' in output or 'SUCCESS' in output:
                status = '✅ PASSED'
            elif 'TEST FAILED' in output or 'FAILED' in output or process.returncode != 0:
                status = '❌ FAILED'
            else:
                status = '⚠️  UNKNOWN'

            print(f"   {status}")

            return {
                'success': success,
                'status': status,
                'output': output,
                'error': error_output,
                'return_code': process.returncode
            }

        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            return {
                'success': False,
                'status': '❌ ERROR',
                'output': '',
                'error': str(e),
                'return_code': -1
            }

    async def run_test_category(self, category):
        """Run all tests in a category"""
        print(f"\n🔍 Running {category.upper()} tests...")
        print("=" * 50)

        test_dir = self.test_dir / category
        if not test_dir.exists():
            print(f"❌ Category directory not found: {test_dir}")
            return

        test_files = list(test_dir.glob("*.py"))
        if not test_files:
            print(f"⚠️  No test files found in {category}/")
            return

        category_results = {}

        for test_file in sorted(test_files):
            result = await self.run_test_file(test_file)
            category_results[test_file.name] = result

        self.results[category] = category_results

    async def run_all_tests(self):
        """Run all test categories"""
        print("🎉 C++ VARIABLE MONITORING - UNIFIED TEST SUITE")
        print("=" * 60)
        print("Testing C++ tracing functionality without KUKSA databroker")
        print()

        # Run tests in order: unit -> integration -> verification
        categories = ['unit', 'integration', 'verification']

        for category in categories:
            await self.run_test_category(category)

    def generate_report(self):
        """Generate a comprehensive test report"""
        print("\n" + "=" * 60)
        print("🎯 TEST RESULTS SUMMARY")
        print("=" * 60)

        total_tests = 0
        total_passed = 0
        total_failed = 0

        for category, tests in self.results.items():
            if not tests:
                continue

            print(f"\n📊 {category.upper()} TESTS:")

            category_passed = 0
            category_failed = 0

            for test_name, result in tests.items():
                status = result['status']
                print(f"   {status} {test_name}")

                if result['success']:
                    category_passed += 1
                    total_passed += 1
                else:
                    category_failed += 1
                    total_failed += 1

                total_tests += 1

            print(f"   📈 Category Summary: {category_passed} passed, {category_failed} failed")

        print(f"\n🏆 OVERALL RESULTS:")
        print(f"   📊 Total Tests: {total_tests}")
        print(f"   ✅ Passed: {total_passed}")
        print(f"   ❌ Failed: {total_failed}")

        success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        print(f"   📈 Success Rate: {success_rate:.1f}%")

        if total_failed == 0:
            print("\n🎉 ALL TESTS PASSED!")
            print("✅ C++ variable monitoring system is fully functional")
            print("✅ System works independently of KUKSA databroker")
            return True
        else:
            print(f"\n⚠️  {total_failed} TEST(S) FAILED")
            print("🔍 Review individual test outputs for details")
            return False

async def main():
    """Main test execution function"""
    runner = TestRunner()

    try:
        await runner.run_all_tests()
        success = runner.generate_report()

        print(f"\n{'🏆 TEST SUITE PASSED' if success else '💥 TEST SUITE FAILED'}")
        return 0 if success else 1

    except Exception as e:
        print(f"\n💥 Test runner error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)