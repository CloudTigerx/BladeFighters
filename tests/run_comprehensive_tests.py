#!/usr/bin/env python3
"""
Comprehensive Test Runner for BladeFighters
Executes all test suites and generates detailed reports.
"""

import sys
import os
import time
import json
import argparse
import subprocess
from typing import Dict, List, Any, Optional
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tests.integration.test_suite_framework import TestAutomationRunner, BladeFightersTestSuite


class ComprehensiveTestRunner:
    """Comprehensive test runner with detailed reporting and analysis."""
    
    def __init__(self, output_dir: str = "test_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.results = {}
        self.start_time = None
        
    def run_all_tests(self, include_performance: bool = True, include_regression: bool = True) -> Dict[str, Any]:
        """Run all comprehensive tests."""
        self.start_time = time.time()
        
        print("\n" + "="*80)
        print("🧪 BLADE FIGHTERS COMPREHENSIVE TEST AUTOMATION")
        print("="*80)
        
        # Run main test automation framework
        print("\n📋 Running main test automation framework...")
        automation_runner = TestAutomationRunner()
        automation_results = automation_runner.run_all_tests()
        self.results['automation_framework'] = automation_results
        
        # Run module-specific integration tests
        print("\n📋 Running module integration tests...")
        module_results = self._run_module_tests()
        self.results['module_integration'] = module_results
        
        # Run performance tests if requested
        if include_performance:
            print("\n📋 Running performance benchmarks...")
            performance_results = self._run_performance_tests()
            self.results['performance'] = performance_results
        
        # Run regression tests if requested
        if include_regression:
            print("\n📋 Running regression tests...")
            regression_results = self._run_regression_tests()
            self.results['regression'] = regression_results
        
        # Generate comprehensive report
        comprehensive_report = self._generate_comprehensive_report()
        
        # Save results
        self._save_results(comprehensive_report)
        
        # Print summary
        self._print_summary(comprehensive_report)
        
        return comprehensive_report
    
    def _run_module_tests(self) -> Dict[str, Any]:
        """Run module-specific integration tests."""
        module_tests = [
            ('audio_module', 'tests/integration/test_audio_module_integration.py'),
            ('screen_module', 'tests/integration/test_screen_module_integration.py'),
            ('input_module', 'tests/integration/test_input_module_integration.py'),
        ]
        
        results = {}
        
        for module_name, test_file in module_tests:
            if os.path.exists(test_file):
                print(f"  Running {module_name} tests...")
                try:
                    result = self._run_pytest_file(test_file)
                    results[module_name] = result
                except Exception as e:
                    results[module_name] = {
                        'error': str(e),
                        'status': 'failed'
                    }
            else:
                print(f"  Skipping {module_name} tests (file not found)")
                results[module_name] = {
                    'error': 'Test file not found',
                    'status': 'skipped'
                }
        
        return results
    
    def _run_performance_tests(self) -> Dict[str, Any]:
        """Run performance benchmarking tests."""
        performance_tests = [
            'tests/integration/test_suite_framework.py::PerformanceTestSuite',
        ]
        
        results = {}
        
        for test_path in performance_tests:
            test_name = test_path.split('::')[-1]
            print(f"  Running {test_name}...")
            try:
                result = self._run_pytest_file(test_path)
                results[test_name] = result
            except Exception as e:
                results[test_name] = {
                    'error': str(e),
                    'status': 'failed'
                }
        
        return results
    
    def _run_regression_tests(self) -> Dict[str, Any]:
        """Run regression tests."""
        regression_tests = [
            'tests/integration/test_suite_framework.py::RegressionTestSuite',
            'tests/integration/test_audio_module_integration.py::AudioModuleRegressionTests',
            'tests/integration/test_screen_module_integration.py::ScreenModuleRegressionTests',
            'tests/integration/test_input_module_integration.py::InputModuleRegressionTests',
        ]
        
        results = {}
        
        for test_path in regression_tests:
            test_name = test_path.split('::')[-1]
            print(f"  Running {test_name}...")
            try:
                result = self._run_pytest_file(test_path)
                results[test_name] = result
            except Exception as e:
                results[test_name] = {
                    'error': str(e),
                    'status': 'failed'
                }
        
        return results
    
    def _run_pytest_file(self, test_path: str) -> Dict[str, Any]:
        """Run a pytest file and return results."""
        try:
            # Run pytest with JSON output
            cmd = [
                sys.executable, '-m', 'pytest', 
                test_path,
                '--json-report',
                '--json-report-file=none',
                '-v'
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            # Parse results
            if result.returncode == 0:
                return {
                    'status': 'passed',
                    'stdout': result.stdout,
                    'stderr': result.stderr
                }
            else:
                return {
                    'status': 'failed',
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'returncode': result.returncode
                }
                
        except subprocess.TimeoutExpired:
            return {
                'status': 'timeout',
                'error': 'Test execution timed out'
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate a comprehensive test report."""
        total_duration = time.time() - self.start_time
        
        # Aggregate results
        total_tests = 0
        total_passed = 0
        total_failed = 0
        total_errors = 0
        total_skipped = 0
        
        # Process automation framework results
        if 'automation_framework' in self.results:
            af_results = self.results['automation_framework']
            if 'summary' in af_results:
                summary = af_results['summary']
                total_tests += summary.get('total_tests', 0)
                total_passed += summary.get('total_passed', 0)
                total_failed += summary.get('total_failed', 0)
                total_errors += summary.get('total_errors', 0)
        
        # Process module integration results
        if 'module_integration' in self.results:
            for module_name, result in self.results['module_integration'].items():
                if result.get('status') == 'passed':
                    total_passed += 1
                elif result.get('status') == 'failed':
                    total_failed += 1
                elif result.get('status') == 'skipped':
                    total_skipped += 1
                else:
                    total_errors += 1
                total_tests += 1
        
        # Calculate overall pass rate
        overall_pass_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        return {
            'summary': {
                'total_tests': total_tests,
                'total_passed': total_passed,
                'total_failed': total_failed,
                'total_errors': total_errors,
                'total_skipped': total_skipped,
                'overall_pass_rate': overall_pass_rate,
                'total_duration': total_duration,
                'timestamp': time.time()
            },
            'detailed_results': self.results,
            'recommendations': self._generate_recommendations(),
            'performance_metrics': self._extract_performance_metrics(),
            'regression_analysis': self._analyze_regression_results()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results."""
        recommendations = []
        
        # Check overall pass rate
        if 'automation_framework' in self.results:
            af_results = self.results['automation_framework']
            if 'summary' in af_results:
                pass_rate = af_results['summary'].get('overall_pass_rate', 0)
                if pass_rate < 80:
                    recommendations.append(f"⚠️  Overall pass rate is {pass_rate:.1f}% - needs attention")
                elif pass_rate < 90:
                    recommendations.append(f"👍 Pass rate is {pass_rate:.1f}% - minor issues to address")
                else:
                    recommendations.append(f"🎉 Excellent pass rate of {pass_rate:.1f}%")
        
        # Check module-specific issues
        if 'module_integration' in self.results:
            for module_name, result in self.results['module_integration'].items():
                if result.get('status') == 'failed':
                    recommendations.append(f"🔧 {module_name} tests failed - review module")
                elif result.get('status') == 'error':
                    recommendations.append(f"🚨 {module_name} tests errored - critical issue")
        
        # Check performance issues
        if 'performance' in self.results:
            for test_name, result in self.results['performance'].items():
                if result.get('status') == 'failed':
                    recommendations.append(f"⚡ {test_name} performance test failed - check performance")
        
        # Check regression issues
        if 'regression' in self.results:
            for test_name, result in self.results['regression'].items():
                if result.get('status') == 'failed':
                    recommendations.append(f"🔄 {test_name} regression test failed - functionality may be broken")
        
        if not recommendations:
            recommendations.append("🎉 All tests are passing! Great job!")
        
        return recommendations
    
    def _extract_performance_metrics(self) -> Dict[str, Any]:
        """Extract performance metrics from test results."""
        metrics = {
            'slow_tests': [],
            'memory_issues': [],
            'performance_degradations': []
        }
        
        # Extract performance data from automation framework
        if 'automation_framework' in self.results:
            af_results = self.results['automation_framework']
            if 'suite_results' in af_results:
                for suite_name, suite_result in af_results['suite_results'].items():
                    if suite_name == 'PerformanceTestSuite':
                        if suite_result.get('failed', 0) > 0:
                            metrics['performance_degradations'].append(suite_name)
        
        return metrics
    
    def _analyze_regression_results(self) -> Dict[str, Any]:
        """Analyze regression test results."""
        analysis = {
            'regression_failures': [],
            'functionality_impact': 'none',
            'critical_issues': []
        }
        
        # Analyze regression test results
        if 'regression' in self.results:
            for test_name, result in self.results['regression'].items():
                if result.get('status') == 'failed':
                    analysis['regression_failures'].append(test_name)
                    
                    # Determine impact level
                    if 'critical' in test_name.lower() or 'core' in test_name.lower():
                        analysis['critical_issues'].append(test_name)
        
        # Determine overall functionality impact
        if analysis['critical_issues']:
            analysis['functionality_impact'] = 'critical'
        elif analysis['regression_failures']:
            analysis['functionality_impact'] = 'moderate'
        else:
            analysis['functionality_impact'] = 'none'
        
        return analysis
    
    def _save_results(self, report: Dict[str, Any]):
        """Save test results to files."""
        # Save comprehensive JSON report
        json_file = self.output_dir / 'comprehensive_test_results.json'
        with open(json_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Save human-readable report
        txt_file = self.output_dir / 'comprehensive_test_report.txt'
        with open(txt_file, 'w') as f:
            f.write("BLADE FIGHTERS COMPREHENSIVE TEST REPORT\n")
            f.write("=" * 60 + "\n\n")
            
            summary = report['summary']
            f.write(f"Overall Results:\n")
            f.write(f"  Total Tests: {summary['total_tests']}\n")
            f.write(f"  Passed: {summary['total_passed']}\n")
            f.write(f"  Failed: {summary['total_failed']}\n")
            f.write(f"  Errors: {summary['total_errors']}\n")
            f.write(f"  Skipped: {summary['total_skipped']}\n")
            f.write(f"  Pass Rate: {summary['overall_pass_rate']:.1f}%\n")
            f.write(f"  Duration: {summary['total_duration']:.2f}s\n\n")
            
            f.write("Module Integration Results:\n")
            if 'module_integration' in report['detailed_results']:
                for module_name, result in report['detailed_results']['module_integration'].items():
                    status = result.get('status', 'unknown')
                    f.write(f"  {module_name}: {status}\n")
            f.write("\n")
            
            f.write("Performance Analysis:\n")
            metrics = report['performance_metrics']
            if metrics['slow_tests']:
                f.write(f"  Slow Tests: {', '.join(metrics['slow_tests'])}\n")
            if metrics['memory_issues']:
                f.write(f"  Memory Issues: {', '.join(metrics['memory_issues'])}\n")
            if metrics['performance_degradations']:
                f.write(f"  Performance Degradations: {', '.join(metrics['performance_degradations'])}\n")
            f.write("\n")
            
            f.write("Regression Analysis:\n")
            analysis = report['regression_analysis']
            f.write(f"  Functionality Impact: {analysis['functionality_impact']}\n")
            if analysis['regression_failures']:
                f.write(f"  Regression Failures: {', '.join(analysis['regression_failures'])}\n")
            if analysis['critical_issues']:
                f.write(f"  Critical Issues: {', '.join(analysis['critical_issues'])}\n")
            f.write("\n")
            
            f.write("Recommendations:\n")
            for rec in report['recommendations']:
                f.write(f"  {rec}\n")
        
        print(f"\n💾 Test results saved to {json_file} and {txt_file}")
    
    def _print_summary(self, report: Dict[str, Any]):
        """Print a summary of test results."""
        summary = report['summary']
        
        print("\n" + "="*80)
        print("📊 COMPREHENSIVE TEST RESULTS SUMMARY")
        print("="*80)
        
        print(f"✅ Passed: {summary['total_passed']}")
        print(f"❌ Failed: {summary['total_failed']}")
        print(f"⚠️  Errors: {summary['total_errors']}")
        print(f"⏭️  Skipped: {summary['total_skipped']}")
        print(f"📊 Pass Rate: {summary['overall_pass_rate']:.1f}%")
        print(f"⏱️  Duration: {summary['total_duration']:.2f}s")
        
        print(f"\n🔍 DETAILED ANALYSIS:")
        
        # Module results
        if 'module_integration' in report['detailed_results']:
            print(f"\n📦 Module Integration:")
            for module_name, result in report['detailed_results']['module_integration'].items():
                status = result.get('status', 'unknown')
                status_icon = "✅" if status == "passed" else "❌" if status == "failed" else "⚠️"
                print(f"  {status_icon} {module_name}: {status}")
        
        # Performance results
        metrics = report['performance_metrics']
        if any(metrics.values()):
            print(f"\n⚡ Performance:")
            if metrics['slow_tests']:
                print(f"  ⚠️  Slow tests: {len(metrics['slow_tests'])}")
            if metrics['memory_issues']:
                print(f"  💾 Memory issues: {len(metrics['memory_issues'])}")
            if metrics['performance_degradations']:
                print(f"  📉 Performance degradations: {len(metrics['performance_degradations'])}")
        
        # Regression results
        analysis = report['regression_analysis']
        if analysis['regression_failures']:
            print(f"\n🔄 Regression:")
            print(f"  Impact: {analysis['functionality_impact']}")
            print(f"  Failures: {len(analysis['regression_failures'])}")
            if analysis['critical_issues']:
                print(f"  Critical issues: {len(analysis['critical_issues'])}")
        
        print(f"\n💡 RECOMMENDATIONS:")
        for rec in report['recommendations']:
            print(f"  {rec}")
        
        print("\n" + "="*80)


def main():
    """Main entry point for the test runner."""
    parser = argparse.ArgumentParser(description='Run comprehensive BladeFighters tests')
    parser.add_argument('--no-performance', action='store_true', 
                       help='Skip performance tests')
    parser.add_argument('--no-regression', action='store_true', 
                       help='Skip regression tests')
    parser.add_argument('--output-dir', default='test_results',
                       help='Output directory for test results')
    parser.add_argument('--module', choices=['audio', 'screen', 'input', 'all'],
                       default='all', help='Run tests for specific module only')
    
    args = parser.parse_args()
    
    # Create test runner
    runner = ComprehensiveTestRunner(args.output_dir)
    
    # Run tests
    try:
        results = runner.run_all_tests(
            include_performance=not args.no_performance,
            include_regression=not args.no_regression
        )
        
        # Exit with appropriate code
        summary = results['summary']
        if summary['total_failed'] > 0 or summary['total_errors'] > 0:
            sys.exit(1)
        else:
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n⚠️  Test execution interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 