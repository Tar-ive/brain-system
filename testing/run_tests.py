#!/usr/bin/env python3
"""
Brain System Test Runner
Provides command-line interface for running different test categories
"""

import argparse
import subprocess
import sys
import time
import os
from pathlib import Path
from typing import List, Optional

class BrainTestRunner:
    """Test runner for Brain System with parallel execution support"""

    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.core_dir = self.test_dir.parent / "core"

    def run_unit_tests(self, parallel: bool = True, coverage: bool = True) -> int:
        """Run unit tests with optional parallel execution and coverage"""
        print("🧪 Running Unit Tests...")

        cmd = ["python", "-m", "pytest", "tests/unit/", "-v"]

        if parallel:
            cmd.extend(["-n", "auto", "--dist=worksteal"])

        if coverage:
            cmd.extend([
                "--cov=../core",
                "--cov-report=term-missing",
                "--cov-report=html:htmlcov/unit",
                "--cov-report=xml:coverage-unit.xml"
            ])

        cmd.extend([
            "--junitxml=test-results/unit-tests.xml",
            "--timeout=300",
            "--tb=short"
        ])

        return self._run_command(cmd)

    def run_integration_tests(self, mcp_setup: bool = True) -> int:
        """Run integration tests with MCP server setup"""
        print("🔗 Running Integration Tests...")

        if mcp_setup:
            print("Setting up MCP servers...")
            self._setup_mcp_servers()

        cmd = [
            "python", "-m", "pytest", "tests/integration/", "-v",
            "--junitxml=test-results/integration-tests.xml",
            "--timeout=1800",  # 30 minutes for integration tests
            "--tb=short"
        ]

        return self._run_command(cmd)

    def run_system_tests(self) -> int:
        """Run system-level tests"""
        print("🏗️ Running System Tests...")

        cmd = [
            "python", "-m", "pytest", "tests/system/", "-v",
            "--junitxml=test-results/system-tests.xml",
            "--timeout=2400",  # 40 minutes for system tests
            "--tb=short"
        ]

        return self._run_command(cmd)

    def run_performance_tests(self, facebook_standards: bool = False) -> int:
        """Run performance tests"""
        print("⚡ Running Performance Tests...")

        cmd = [
            "python", "-m", "pytest", "tests/performance/", "-v",
            "--junitxml=test-results/performance-tests.xml",
            "--timeout=3600",  # 60 minutes for performance tests
            "--tb=short"
        ]

        if facebook_standards:
            cmd.append("--run-facebook-tests")

        return self._run_command(cmd)

    def run_parallel_tests(self, categories: List[str]) -> int:
        """Run multiple test categories in parallel"""
        print(f"🚀 Running Parallel Tests: {', '.join(categories)}")

        processes = []

        for category in categories:
            if category == "unit":
                cmd = ["python", "run_tests.py", "--unit", "--no-parallel"]
            elif category == "integration":
                cmd = ["python", "run_tests.py", "--integration"]
            elif category == "system":
                cmd = ["python", "run_tests.py", "--system"]
            elif category == "performance":
                cmd = ["python", "run_tests.py", "--performance"]
            else:
                print(f"Unknown test category: {category}")
                continue

            print(f"Starting {category} tests...")
            process = subprocess.Popen(
                cmd,
                cwd=self.test_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            processes.append((category, process))

        # Wait for all processes and collect results
        results = {}
        for category, process in processes:
            stdout, stderr = process.communicate()
            results[category] = {
                'returncode': process.returncode,
                'stdout': stdout,
                'stderr': stderr
            }

            if process.returncode == 0:
                print(f"✅ {category} tests passed")
            else:
                print(f"❌ {category} tests failed")
                print(f"Error output: {stderr}")

        # Return non-zero if any tests failed
        return max(result['returncode'] for result in results.values())

    def run_all_tests(self, parallel: bool = True) -> int:
        """Run all test categories"""
        print("🎯 Running All Tests...")

        if parallel:
            return self.run_parallel_tests(["unit", "integration", "system", "performance"])
        else:
            results = []
            results.append(self.run_unit_tests(parallel=False))
            results.append(self.run_integration_tests())
            results.append(self.run_system_tests())
            results.append(self.run_performance_tests())

            return max(results)

    def _setup_mcp_servers(self):
        """Setup MCP servers for integration testing"""
        try:
            # Check if basic-memory is available
            result = subprocess.run(
                ["which", "basic-memory"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                print("⚠️ basic-memory not found, installing...")
                subprocess.run(
                    ["npm", "install", "-g", "basic-memory"],
                    check=True,
                    timeout=60
                )
        except Exception as e:
            print(f"⚠️ MCP setup warning: {e}")

    def _run_command(self, cmd: List[str]) -> int:
        """Run command and return exit code"""
        # Ensure test results directory exists
        (self.test_dir / "test-results").mkdir(exist_ok=True)

        # Set environment variables
        env = os.environ.copy()
        env["PYTHONPATH"] = f"{env.get('PYTHONPATH', '')}:{self.core_dir}"

        try:
            result = subprocess.run(
                cmd,
                cwd=self.test_dir,
                env=env,
                check=False
            )
            return result.returncode
        except KeyboardInterrupt:
            print("\n⚠️ Tests interrupted by user")
            return 1
        except Exception as e:
            print(f"❌ Test execution failed: {e}")
            return 1

    def generate_report(self):
        """Generate comprehensive test report"""
        print("📊 Generating Test Report...")

        try:
            # Install reporting dependencies if needed
            subprocess.run([
                "pip", "install", "junitparser", "pytest-html"
            ], check=True, capture_output=True)

            # Generate HTML report from JUnit XML files
            subprocess.run([
                "python", "-c", """
import os
from pathlib import Path
from junitparser import JUnitXml

test_results_dir = Path('test-results')
if test_results_dir.exists():
    xml_files = list(test_results_dir.glob('*.xml'))
    if xml_files:
        print(f'Found {len(xml_files)} test result files')

        total_tests = 0
        total_failures = 0
        total_errors = 0
        total_skipped = 0

        for xml_file in xml_files:
            try:
                xml = JUnitXml.fromfile(str(xml_file))
                total_tests += xml.tests
                total_failures += xml.failures
                total_errors += xml.errors
                total_skipped += xml.skipped
            except Exception as e:
                print(f'Error parsing {xml_file}: {e}')

        success_rate = ((total_tests - total_failures - total_errors) / total_tests * 100) if total_tests > 0 else 0

        report = f'''
Brain System Test Summary
========================
Total Tests: {total_tests}
Passed: {total_tests - total_failures - total_errors}
Failed: {total_failures}
Errors: {total_errors}
Skipped: {total_skipped}
Success Rate: {success_rate:.2f}%
'''

        with open('test-results/summary.txt', 'w') as f:
            f.write(report)

        print(report)
    else:
        print('No test results found')
else:
    print('Test results directory not found')
"""
            ], cwd=self.test_dir)

        except Exception as e:
            print(f"⚠️ Report generation failed: {e}")


def main():
    parser = argparse.ArgumentParser(description="Brain System Test Runner")

    # Test category options
    parser.add_argument("--unit", action="store_true", help="Run unit tests")
    parser.add_argument("--integration", action="store_true", help="Run integration tests")
    parser.add_argument("--system", action="store_true", help="Run system tests")
    parser.add_argument("--performance", action="store_true", help="Run performance tests")
    parser.add_argument("--all", action="store_true", help="Run all tests")

    # Options
    parser.add_argument("--parallel", action="store_true", default=True, help="Enable parallel execution")
    parser.add_argument("--no-parallel", action="store_true", help="Disable parallel execution")
    parser.add_argument("--coverage", action="store_true", default=True, help="Enable coverage reporting")
    parser.add_argument("--facebook-tests", action="store_true", help="Include Facebook reliability tests")
    parser.add_argument("--report", action="store_true", help="Generate test report")
    parser.add_argument("--categories", nargs="+", choices=["unit", "integration", "system", "performance"], help="Run specific categories in parallel")

    args = parser.parse_args()

    runner = BrainTestRunner()

    # Handle parallel options
    parallel = args.parallel and not args.no_parallel

    exit_code = 0

    try:
        if args.categories:
            exit_code = runner.run_parallel_tests(args.categories)
        elif args.all:
            exit_code = runner.run_all_tests(parallel=parallel)
        elif args.unit:
            exit_code = runner.run_unit_tests(parallel=parallel, coverage=args.coverage)
        elif args.integration:
            exit_code = runner.run_integration_tests()
        elif args.system:
            exit_code = runner.run_system_tests()
        elif args.performance:
            exit_code = runner.run_performance_tests(facebook_standards=args.facebook_tests)
        else:
            # Default: run all tests
            exit_code = runner.run_all_tests(parallel=parallel)

        if args.report:
            runner.generate_report()

    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        exit_code = 1

    if exit_code == 0:
        print("\n✅ All tests completed successfully!")
    else:
        print("\n❌ Some tests failed. Check the output above for details.")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()