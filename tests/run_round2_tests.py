#!/usr/bin/env python3
"""
Round 2 Comprehensive Test Runner
Orchestrates all integration tests, performance tests, and error handling tests for Round 2.
"""

import sys
import os
import time
import json
import argparse
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tests.integration.test_suite_framework import (
    TestResult, 
    TestSuiteResult, 
    PerformanceMonitor
)


class Round2TestRunner:
    """Comprehensive test runner for Round 2 integration testing."""
    
    def __init__(self, output_dir: str = "test_results/round2"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results = {}
        self.start_time = None
        self.performance_monitor = PerformanceMonitor()
        
        # Test suites to run
        self.test_suites = [
            "tests.integration.round2_comprehensive_tests.Round2ComprehensiveIntegrationTests",
            "tests.integration.round2_comprehensive_tests.Round2PerformanceRegressionTests",
            "tests.integration.round2_comprehensive_tests.Round2ErrorHandlingTests"
        ]
        
        # Module-specific integration tests
        self.module_tests = [
            "tests.integration.test_audio_module_integration",
            "tests.integration.test_screen_module_integration", 
            "tests.integration.test_input_module_integration"
        ]
    
    def run_all_tests(self, include_performance: bool = True, include_regression: bool = True) -> Dict[str, Any]:
        """Run all Round 2 tests."""
        print("🧪 Round 2 Comprehensive Test Suite")
        print("=" * 60)
        
        self.start_time = time.time()
        self.performance_monitor.start_monitoring()
        
        # Run comprehensive integration tests
        print("\n📋 Running Comprehensive Integration Tests...")
        integration_results = self._run_comprehensive_tests()
        
        # Run module-specific tests
        print("\n🔧 Running Module-Specific Integration Tests...")
        module_results = self._run_module_tests()
        
        # Run performance tests
        performance_results = {}
        if include_performance:
            print("\n📊 Running Performance Regression Tests...")
            performance_results = self._run_performance_tests()
        
        # Run regression tests
        regression_results = {}
        if include_regression:
            print("\n🔄 Running Regression Tests...")
            regression_results = self._run_regression_tests()
        
        # Stop monitoring and collect metrics
        metrics = self.performance_monitor.stop_monitoring()
        total_duration = time.time() - self.start_time
        
        # Aggregate results
        comprehensive_results = {
            'timestamp': datetime.now().isoformat(),
            'total_duration': total_duration,
            'performance_metrics': metrics,
            'test_suites': {
                'comprehensive_integration': integration_results,
                'module_specific': module_results,
                'performance': performance_results,
                'regression': regression_results
            },
            'summary': self._generate_summary({
                'integration': integration_results,
                'modules': module_results,
                'performance': performance_results,
                'regression': regression_results
            })
        }
        
        # Save results
        self._save_results(comprehensive_results)
        
        # Print summary
        self._print_summary(comprehensive_results)
        
        return comprehensive_results
    
    def _run_comprehensive_tests(self) -> Dict[str, Any]:
        """Run comprehensive integration tests."""
        results = {
            'tests': [],
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'errors': 0,
            'duration': 0
        }
        
        try:
            # Run comprehensive tests using pytest
            cmd = [
                sys.executable, '-m', 'pytest',
                'tests/integration/round2_comprehensive_tests.py::Round2ComprehensiveIntegrationTests',
                '-v', '--tb=short', '--json-report',
                f'--json-report-file={self.output_dir}/comprehensive_tests.json'
            ]
            
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            duration = time.time() - start_time
            
            results['duration'] = duration
            results['return_code'] = result.returncode
            
            # Parse test results
            if result.returncode == 0:
                results['status'] = 'passed'
                # Count passed tests (simplified parsing)
                passed_count = result.stdout.count('PASSED')
                results['passed'] = passed_count
                results['total_tests'] = passed_count
            else:
                results['status'] = 'failed'
                # Count failed tests
                failed_count = result.stdout.count('FAILED')
                error_count = result.stdout.count('ERROR')
                results['failed'] = failed_count
                results['errors'] = error_count
                results['total_tests'] = failed_count + error_count
            
            results['stdout'] = result.stdout
            results['stderr'] = result.stderr
            
        except subprocess.TimeoutExpired:
            results['status'] = 'timeout'
            results['error'] = 'Test execution timed out'
        except Exception as e:
            results['status'] = 'error'
            results['error'] = str(e)
        
        return results
    
    def _run_module_tests(self) -> Dict[str, Any]:
        """Run module-specific integration tests."""
        results = {
            'modules': {},
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'errors': 0
        }
        
        for module_test in self.module_tests:
            module_name = module_test.split('.')[-1].replace('test_', '').replace('_integration', '')
            
            try:
                cmd = [
                    sys.executable, '-m', 'pytest',
                    f'{module_test}.py',
                    '-v', '--tb=short'
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
                
                module_result = {
                    'status': 'passed' if result.returncode == 0 else 'failed',
                    'return_code': result.returncode,
                    'passed': result.stdout.count('PASSED'),
                    'failed': result.stdout.count('FAILED'),
                    'errors': result.stdout.count('ERROR'),
                    'stdout': result.stdout,
                    'stderr': result.stderr
                }
                
                results['modules'][module_name] = module_result
                results['total_tests'] += module_result['passed'] + module_result['failed'] + module_result['errors']
                results['passed'] += module_result['passed']
                results['failed'] += module_result['failed']
                results['errors'] += module_result['errors']
                
            except subprocess.TimeoutExpired:
                results['modules'][module_name] = {
                    'status': 'timeout',
                    'error': 'Test execution timed out'
                }
            except Exception as e:
                results['modules'][module_name] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        return results
    
    def _run_performance_tests(self) -> Dict[str, Any]:
        """Run performance regression tests."""
        results = {
            'tests': [],
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'baseline_comparison': {}
        }
        
        try:
            cmd = [
                sys.executable, '-m', 'pytest',
                'tests/integration/round2_comprehensive_tests.py::Round2PerformanceRegressionTests',
                '-v', '--tb=short'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            
            results['return_code'] = result.returncode
            results['status'] = 'passed' if result.returncode == 0 else 'failed'
            
            # Parse performance results
            if result.returncode == 0:
                results['passed'] = result.stdout.count('PASSED')
                results['total_tests'] = results['passed']
            else:
                results['failed'] = result.stdout.count('FAILED')
                results['total_tests'] = results['failed']
            
            results['stdout'] = result.stdout
            results['stderr'] = result.stderr
            
        except subprocess.TimeoutExpired:
            results['status'] = 'timeout'
            results['error'] = 'Performance tests timed out'
        except Exception as e:
            results['status'] = 'error'
            results['error'] = str(e)
        
        return results
    
    def _run_regression_tests(self) -> Dict[str, Any]:
        """Run regression tests."""
        results = {
            'tests': [],
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'regressions_detected': 0
        }
        
        try:
            cmd = [
                sys.executable, '-m', 'pytest',
                'tests/integration/round2_comprehensive_tests.py::Round2ErrorHandlingTests',
                '-v', '--tb=short'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            results['return_code'] = result.returncode
            results['status'] = 'passed' if result.returncode == 0 else 'failed'
            
            # Parse regression results
            if result.returncode == 0:
                results['passed'] = result.stdout.count('PASSED')
                results['total_tests'] = results['passed']
            else:
                results['failed'] = result.stdout.count('FAILED')
                results['regressions_detected'] = results['failed']
                results['total_tests'] = results['failed']
            
            results['stdout'] = result.stdout
            results['stderr'] = result.stderr
            
        except subprocess.TimeoutExpired:
            results['status'] = 'timeout'
            results['error'] = 'Regression tests timed out'
        except Exception as e:
            results['status'] = 'error'
            results['error'] = str(e)
        
        return results
    
    def _generate_summary(self, all_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive test summary."""
        total_tests = 0
        total_passed = 0
        total_failed = 0
        total_skipped = 0
        total_errors = 0
        
        # Aggregate results from all test suites
        for suite_name, results in all_results.items():
            if isinstance(results, dict):
                total_tests += results.get('total_tests', 0)
                total_passed += results.get('passed', 0)
                total_failed += results.get('failed', 0)
                total_skipped += results.get('skipped', 0)
                total_errors += results.get('errors', 0)
        
        success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        return {
            'total_tests': total_tests,
            'passed': total_passed,
            'failed': total_failed,
            'skipped': total_skipped,
            'errors': total_errors,
            'success_rate': success_rate,
            'overall_status': 'passed' if total_failed == 0 and total_errors == 0 else 'failed'
        }
    
    def _save_results(self, results: Dict[str, Any]):
        """Save test results to files."""
        # Save comprehensive results
        results_file = self.output_dir / "round2_comprehensive_results.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Save human-readable report
        report_file = self.output_dir / "round2_test_report.txt"
        with open(report_file, 'w') as f:
            f.write(self._generate_human_readable_report(results))
        
        print(f"\n📁 Results saved to: {self.output_dir}")
    
    def _generate_human_readable_report(self, results: Dict[str, Any]) -> str:
        """Generate human-readable test report."""
        report = []
        report.append("Round 2 Comprehensive Test Report")
        report.append("=" * 50)
        report.append(f"Generated: {results['timestamp']}")
        report.append(f"Total Duration: {results['total_duration']:.2f}s")
        report.append("")
        
        # Summary
        summary = results['summary']
        report.append("📊 SUMMARY")
        report.append("-" * 20)
        report.append(f"Total Tests: {summary['total_tests']}")
        report.append(f"Passed: {summary['passed']} ✅")
        report.append(f"Failed: {summary['failed']} ❌")
        report.append(f"Skipped: {summary['skipped']} ⏭️")
        report.append(f"Errors: {summary['errors']} 💥")
        report.append(f"Success Rate: {summary['success_rate']:.1f}%")
        report.append(f"Overall Status: {summary['overall_status'].upper()}")
        report.append("")
        
        # Performance metrics
        if 'performance_metrics' in results:
            metrics = results['performance_metrics']
            report.append("📈 PERFORMANCE METRICS")
            report.append("-" * 20)
            report.append(f"Memory Usage: {metrics.get('memory_delta', 0):.1f}MB")
            report.append(f"Operations/sec: {metrics.get('operations_per_second', 0):.1f}")
            report.append("")
        
        # Test suite details
        test_suites = results['test_suites']
        report.append("🧪 TEST SUITE DETAILS")
        report.append("-" * 20)
        
        for suite_name, suite_results in test_suites.items():
            if isinstance(suite_results, dict):
                status = suite_results.get('status', 'unknown')
                total = suite_results.get('total_tests', 0)
                passed = suite_results.get('passed', 0)
                failed = suite_results.get('failed', 0)
                
                report.append(f"{suite_name.replace('_', ' ').title()}:")
                report.append(f"  Status: {status}")
                report.append(f"  Tests: {passed}/{total} passed")
                if failed > 0:
                    report.append(f"  Failed: {failed}")
                report.append("")
        
        # Recommendations
        report.append("💡 RECOMMENDATIONS")
        report.append("-" * 20)
        
        if summary['failed'] > 0:
            report.append("❌ Failed tests detected - review and fix issues")
        if summary['errors'] > 0:
            report.append("💥 Errors detected - check module availability and configuration")
        if summary['success_rate'] < 95:
            report.append("⚠️  Success rate below 95% - investigate test failures")
        if summary['success_rate'] >= 95:
            report.append("✅ All tests passing - ready for production")
        
        return "\n".join(report)
    
    def _print_summary(self, results: Dict[str, Any]):
        """Print test summary to console."""
        summary = results['summary']
        
        print("\n" + "=" * 60)
        print("📊 ROUND 2 TEST SUMMARY")
        print("=" * 60)
        
        # Overall status
        status_emoji = "✅" if summary['overall_status'] == 'passed' else "❌"
        print(f"{status_emoji} Overall Status: {summary['overall_status'].upper()}")
        
        # Test counts
        print(f"📋 Total Tests: {summary['total_tests']}")
        print(f"✅ Passed: {summary['passed']}")
        print(f"❌ Failed: {summary['failed']}")
        print(f"⏭️  Skipped: {summary['skipped']}")
        print(f"💥 Errors: {summary['errors']}")
        
        # Success rate
        print(f"📈 Success Rate: {summary['success_rate']:.1f}%")
        
        # Performance
        if 'performance_metrics' in results:
            metrics = results['performance_metrics']
            print(f"⏱️  Total Duration: {results['total_duration']:.2f}s")
            print(f"💾 Memory Usage: {metrics.get('memory_delta', 0):.1f}MB")
        
        # Recommendations
        print("\n💡 RECOMMENDATIONS:")
        if summary['failed'] > 0:
            print("  ❌ Review failed tests and fix issues")
        if summary['errors'] > 0:
            print("  💥 Check module availability and configuration")
        if summary['success_rate'] < 95:
            print("  ⚠️  Success rate below 95% - investigate")
        if summary['success_rate'] >= 95:
            print("  ✅ All tests passing - ready for production")
        
        print("\n📁 Detailed results saved to:", self.output_dir)


def main():
    """Main entry point for Round 2 test runner."""
    parser = argparse.ArgumentParser(description="Round 2 Comprehensive Test Runner")
    parser.add_argument("--output-dir", default="test_results/round2", 
                       help="Output directory for test results")
    parser.add_argument("--no-performance", action="store_true",
                       help="Skip performance tests")
    parser.add_argument("--no-regression", action="store_true",
                       help="Skip regression tests")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output")
    
    args = parser.parse_args()
    
    # Create test runner
    runner = Round2TestRunner(output_dir=args.output_dir)
    
    # Run tests
    try:
        results = runner.run_all_tests(
            include_performance=not args.no_performance,
            include_regression=not args.no_regression
        )
        
        # Exit with appropriate code
        if results['summary']['overall_status'] == 'passed':
            sys.exit(0)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  Test execution interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Test execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
