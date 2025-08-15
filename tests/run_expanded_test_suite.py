#!/usr/bin/env python3
"""
Expanded Test Suite Runner for BladeFighters
Comprehensive test automation including unit tests, performance tests, and end-to-end tests.
"""

import unittest
import sys
import os
import time
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import test modules
from tests.unit.test_audio_module import run_audio_unit_tests
from tests.unit.test_input_module import run_input_unit_tests
from tests.performance.test_performance_framework import run_performance_tests
from tests.integration.test_end_to_end_framework import run_end_to_end_tests


class TestSuiteRunner:
    """Comprehensive test suite runner for BladeFighters."""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "test_suites": {},
            "summary": {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "errors": 0,
                "skipped": 0,
                "total_duration": 0.0
            }
        }
        
        self.test_suites = {
            "unit_tests": {
                "audio": run_audio_unit_tests,
                "input": run_input_unit_tests,
                "description": "Unit tests for individual modules"
            },
            "performance_tests": {
                "performance": run_performance_tests,
                "description": "Performance benchmarking and regression detection"
            },
            "integration_tests": {
                "end_to_end": run_end_to_end_tests,
                "description": "End-to-end testing of complete game flow"
            }
        }
    
    def run_test_suite(self, suite_name: str, test_name: str) -> Dict[str, Any]:
        """Run a specific test suite."""
        print(f"\n🧪 Running {suite_name}: {test_name}")
        print("=" * 60)
        
        start_time = time.time()
        
        try:
            # Run the test
            test_func = self.test_suites[suite_name][test_name]
            result = test_func()
            
            duration = time.time() - start_time
            
            # Compile results
            suite_result = {
                "name": test_name,
                "duration": duration,
                "success": True,
                "error": None
            }
            
            if hasattr(result, 'testsRun'):
                suite_result.update({
                    "tests_run": result.testsRun,
                    "passed": result.testsRun - len(result.failures) - len(result.errors),
                    "failed": len(result.failures),
                    "errors": len(result.errors),
                    "skipped": getattr(result, 'skipped', 0)
                })
            
            print(f"✅ {test_name} completed in {duration:.2f}s")
            
        except Exception as e:
            duration = time.time() - start_time
            suite_result = {
                "name": test_name,
                "duration": duration,
                "success": False,
                "error": str(e),
                "tests_run": 0,
                "passed": 0,
                "failed": 0,
                "errors": 1,
                "skipped": 0
            }
            
            print(f"❌ {test_name} failed: {e}")
        
        return suite_result
    
    def run_all_tests(self, include_performance: bool = True, include_integration: bool = True) -> Dict[str, Any]:
        """Run all test suites."""
        print("🚀 BladeFighters Expanded Test Suite")
        print("=" * 60)
        print(f"Started at: {self.results['timestamp']}")
        
        total_start_time = time.time()
        
        # Run unit tests
        print("\n📋 Unit Tests")
        print("-" * 30)
        
        self.results["test_suites"]["unit_tests"] = {}
        for test_name in self.test_suites["unit_tests"]:
            if test_name != "description":
                result = self.run_test_suite("unit_tests", test_name)
                self.results["test_suites"]["unit_tests"][test_name] = result
        
        # Run performance tests
        if include_performance:
            print("\n📋 Performance Tests")
            print("-" * 30)
            
            self.results["test_suites"]["performance_tests"] = {}
            for test_name in self.test_suites["performance_tests"]:
                if test_name != "description":
                    result = self.run_test_suite("performance_tests", test_name)
                    self.results["test_suites"]["performance_tests"][test_name] = result
        
        # Run integration tests
        if include_integration:
            print("\n📋 Integration Tests")
            print("-" * 30)
            
            self.results["test_suites"]["integration_tests"] = {}
            for test_name in self.test_suites["integration_tests"]:
                if test_name != "description":
                    result = self.run_test_suite("integration_tests", test_name)
                    self.results["test_suites"]["integration_tests"][test_name] = result
        
        # Calculate summary
        total_duration = time.time() - total_start_time
        self.results["summary"]["total_duration"] = total_duration
        
        # Compile overall statistics
        for suite_name, suite_results in self.results["test_suites"].items():
            for test_name, test_result in suite_results.items():
                if isinstance(test_result, dict) and "tests_run" in test_result:
                    self.results["summary"]["total_tests"] += test_result["tests_run"]
                    self.results["summary"]["passed"] += test_result["passed"]
                    self.results["summary"]["failed"] += test_result["failed"]
                    self.results["summary"]["errors"] += test_result["errors"]
                    self.results["summary"]["skipped"] += test_result.get("skipped", 0)
        
        return self.results
    
    def print_summary(self):
        """Print comprehensive test summary."""
        summary = self.results["summary"]
        
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST RESULTS SUMMARY")
        print("=" * 60)
        
        print(f"⏰ Duration: {summary['total_duration']:.2f}s")
        print(f"📋 Total Tests: {summary['total_tests']}")
        print(f"✅ Passed: {summary['passed']}")
        print(f"❌ Failed: {summary['failed']}")
        print(f"⚠️  Errors: {summary['errors']}")
        print(f"⏭️  Skipped: {summary['skipped']}")
        
        if summary['total_tests'] > 0:
            pass_rate = (summary['passed'] / summary['total_tests']) * 100
            print(f"📊 Pass Rate: {pass_rate:.1f}%")
        
        print("\n📋 Test Suite Breakdown:")
        print("-" * 30)
        
        for suite_name, suite_results in self.results["test_suites"].items():
            if suite_results:
                suite_total = 0
                suite_passed = 0
                suite_failed = 0
                
                for test_name, test_result in suite_results.items():
                    if isinstance(test_result, dict) and "tests_run" in test_result:
                        suite_total += test_result["tests_run"]
                        suite_passed += test_result["passed"]
                        suite_failed += test_result["failed"]
                
                if suite_total > 0:
                    suite_pass_rate = (suite_passed / suite_total) * 100
                    print(f"  {suite_name.replace('_', ' ').title()}: {suite_passed}/{suite_total} ({suite_pass_rate:.1f}%)")
        
        # Overall assessment
        print("\n🎯 Overall Assessment:")
        print("-" * 30)
        
        if summary['failed'] == 0 and summary['errors'] == 0:
            print("🎉 All tests passed! Excellent work!")
        elif summary['failed'] <= 2 and summary['errors'] == 0:
            print("✅ Good results with minor issues to address")
        elif summary['failed'] <= 5:
            print("⚠️  Some issues detected - review needed")
        else:
            print("❌ Significant issues detected - immediate attention required")
    
    def save_results(self, filename: str = "expanded_test_results.json"):
        """Save test results to file."""
        try:
            with open(filename, 'w') as f:
                json.dump(self.results, f, indent=2)
            print(f"\n💾 Test results saved to {filename}")
        except Exception as e:
            print(f"\n⚠️  Failed to save results: {e}")
    
    def generate_report(self, filename: str = "expanded_test_report.txt"):
        """Generate human-readable test report."""
        try:
            with open(filename, 'w') as f:
                f.write("BladeFighters Expanded Test Suite Report\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Generated: {self.results['timestamp']}\n")
                f.write(f"Duration: {self.results['summary']['total_duration']:.2f}s\n\n")
                
                f.write("SUMMARY\n")
                f.write("-" * 10 + "\n")
                summary = self.results["summary"]
                f.write(f"Total Tests: {summary['total_tests']}\n")
                f.write(f"Passed: {summary['passed']}\n")
                f.write(f"Failed: {summary['failed']}\n")
                f.write(f"Errors: {summary['errors']}\n")
                f.write(f"Skipped: {summary['skipped']}\n")
                
                if summary['total_tests'] > 0:
                    pass_rate = (summary['passed'] / summary['total_tests']) * 100
                    f.write(f"Pass Rate: {pass_rate:.1f}%\n")
                
                f.write("\nDETAILED RESULTS\n")
                f.write("-" * 20 + "\n")
                
                for suite_name, suite_results in self.results["test_suites"].items():
                    if suite_results:
                        f.write(f"\n{suite_name.replace('_', ' ').title()}:\n")
                        
                        for test_name, test_result in suite_results.items():
                            if isinstance(test_result, dict):
                                f.write(f"  {test_name}:\n")
                                f.write(f"    Duration: {test_result['duration']:.2f}s\n")
                                f.write(f"    Success: {test_result['success']}\n")
                                
                                if "tests_run" in test_result:
                                    f.write(f"    Tests: {test_result['tests_run']}\n")
                                    f.write(f"    Passed: {test_result['passed']}\n")
                                    f.write(f"    Failed: {test_result['failed']}\n")
                                    f.write(f"    Errors: {test_result['errors']}\n")
                                
                                if test_result.get("error"):
                                    f.write(f"    Error: {test_result['error']}\n")
                
                f.write("\nRECOMMENDATIONS\n")
                f.write("-" * 20 + "\n")
                
                if summary['failed'] == 0 and summary['errors'] == 0:
                    f.write("✅ All tests are passing! The codebase is in excellent condition.\n")
                elif summary['failed'] <= 2:
                    f.write("⚠️  Minor issues detected. Review failed tests and address them.\n")
                else:
                    f.write("❌ Significant issues detected. Prioritize fixing failed tests.\n")
                
                f.write("\nNext Steps:\n")
                f.write("1. Review any failed tests\n")
                f.write("2. Address performance regressions if any\n")
                f.write("3. Fix integration issues\n")
                f.write("4. Re-run tests to verify fixes\n")
            
            print(f"📄 Test report generated: {filename}")
        except Exception as e:
            print(f"⚠️  Failed to generate report: {e}")


def main():
    """Main entry point for the test suite runner."""
    parser = argparse.ArgumentParser(description="BladeFighters Expanded Test Suite Runner")
    parser.add_argument("--unit-only", action="store_true", help="Run only unit tests")
    parser.add_argument("--performance-only", action="store_true", help="Run only performance tests")
    parser.add_argument("--integration-only", action="store_true", help="Run only integration tests")
    parser.add_argument("--no-performance", action="store_true", help="Skip performance tests")
    parser.add_argument("--no-integration", action="store_true", help="Skip integration tests")
    parser.add_argument("--save-results", action="store_true", help="Save results to file")
    parser.add_argument("--generate-report", action="store_true", help="Generate human-readable report")
    parser.add_argument("--output-dir", default="test_results", help="Output directory for results")
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Initialize runner
    runner = TestSuiteRunner()
    
    # Determine which tests to run
    include_performance = not args.no_performance and not args.unit_only
    include_integration = not args.no_integration and not args.unit_only and not args.performance_only
    
    if args.performance_only:
        include_performance = True
        include_integration = False
    
    if args.integration_only:
        include_performance = False
        include_integration = True
    
    # Run tests
    results = runner.run_all_tests(
        include_performance=include_performance,
        include_integration=include_integration
    )
    
    # Print summary
    runner.print_summary()
    
    # Save results if requested
    if args.save_results:
        results_file = os.path.join(args.output_dir, "expanded_test_results.json")
        runner.save_results(results_file)
    
    # Generate report if requested
    if args.generate_report:
        report_file = os.path.join(args.output_dir, "expanded_test_report.txt")
        runner.generate_report(report_file)
    
    # Exit with appropriate code
    summary = results["summary"]
    if summary['failed'] > 0 or summary['errors'] > 0:
        print(f"\n❌ Test suite completed with {summary['failed']} failures and {summary['errors']} errors")
        sys.exit(1)
    else:
        print(f"\n✅ Test suite completed successfully!")
        sys.exit(0)


if __name__ == "__main__":
    main()
