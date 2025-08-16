#!/usr/bin/env python3
"""
Performance Test Runner for BladeFighters
=========================================

Runs performance tests with configuration management and detailed reporting.
"""

import json
import os
import sys
import time
import argparse
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import the test framework directly
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Now import the test framework
from test_performance_framework import run_performance_tests


class PerformanceTestRunner:
    """Manages performance test execution with configuration."""
    
    def __init__(self, config_path: str = "performance_config.json"):
        self.config_path = config_path
        self.config = self.load_config()
        self.results = {}
        self.start_time = None
        self.end_time = None
    
    def load_config(self) -> Dict[str, Any]:
        """Load performance test configuration."""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️  Configuration file {self.config_path} not found. Using defaults.")
            return self.get_default_config()
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing configuration file: {e}")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "performance_test_config": {
                "benchmark_settings": {
                    "audio_system": {
                        "max_duration_ms": 100.0,
                        "max_memory_mb": 50.0,
                        "max_cpu_percent": 10.0,
                        "min_ops_per_second": 100.0
                    },
                    "input_system": {
                        "max_duration_ms": 100.0,
                        "max_memory_mb": 50.0,
                        "max_cpu_percent": 5.0,
                        "min_ops_per_second": 100.0
                    },
                    "game_state": {
                        "max_duration_ms": 50.0,
                        "max_memory_mb": 20.0,
                        "max_cpu_percent": 5.0,
                        "min_ops_per_second": 500.0
                    },
                    "puzzle_engine": {
                        "max_duration_ms": 500.0,
                        "max_memory_mb": 200.0,
                        "min_ops_per_second": 10.0
                    }
                }
            }
        }
    
    def run_tests(self) -> Dict[str, Any]:
        """Run performance tests."""
        self.start_time = time.time()
        print("⚡ Starting Performance Test Suite")
        print("=" * 50)
        
        # Run the main performance test framework
        result = run_performance_tests()
        
        self.end_time = time.time()
        
        # Compile results
        self.results = {
            "test_framework": {
                "status": "completed",
                "tests_run": result.testsRun,
                "tests_passed": result.testsRun - len(result.failures) - len(result.errors),
                "tests_failed": len(result.failures),
                "tests_errors": len(result.errors),
                "duration_ms": (self.end_time - self.start_time) * 1000
            }
        }
        
        return self.results
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report."""
        if not self.results:
            return {"error": "No test results available"}
        
        total_duration = (self.end_time - self.start_time) * 1000 if self.end_time else 0
        
        report = {
            "test_suite_info": {
                "name": "BladeFighters Performance Test Suite",
                "version": "1.0.0",
                "timestamp": datetime.now().isoformat(),
                "total_duration_ms": total_duration,
                "config_file": self.config_path
            },
            "summary": {
                "categories_tested": len(self.results),
                "total_tests": sum(r.get("tests_run", 0) for r in self.results.values()),
                "passed_tests": sum(r.get("tests_passed", 0) for r in self.results.values()),
                "failed_tests": sum(r.get("tests_failed", 0) for r in self.results.values()),
                "success_rate": 0.0
            },
            "category_results": self.results,
            "recommendations": self.generate_recommendations()
        }
        
        # Calculate success rate
        total_tests = report["summary"]["total_tests"]
        if total_tests > 0:
            report["summary"]["success_rate"] = (report["summary"]["passed_tests"] / total_tests) * 100
        
        return report
    
    def generate_recommendations(self) -> List[str]:
        """Generate performance recommendations based on results."""
        recommendations = []
        
        # Analyze results and provide recommendations
        for category, result in self.results.items():
            if result.get("tests_failed", 0) > 0:
                recommendations.append(f"Investigate {category} performance issues")
            elif result.get("tests_errors", 0) > 0:
                recommendations.append(f"Fix {category} test setup errors")
        
        if not recommendations:
            recommendations.append("All performance tests passed - system performing well")
        
        return recommendations
    
    def save_report(self, report: Dict[str, Any], output_file: str = None) -> str:
        """Save performance report to file."""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"performance_report_{timestamp}.json"
        
        try:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"📊 Performance report saved to: {output_file}")
            return output_file
        except Exception as e:
            print(f"❌ Error saving report: {e}")
            return None
    
    def print_summary(self, report: Dict[str, Any]):
        """Print performance test summary."""
        print("\n" + "=" * 50)
        print("📊 PERFORMANCE TEST SUMMARY")
        print("=" * 50)
        
        summary = report["summary"]
        print(f"Categories Tested: {summary['categories_tested']}")
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed_tests']}")
        print(f"Failed: {summary['failed_tests']}")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        print(f"Total Duration: {report['test_suite_info']['total_duration_ms']:.1f}ms")
        
        print("\n🔍 Category Results:")
        for category, result in report["category_results"].items():
            status = "✅" if result.get("tests_failed", 0) == 0 else "⚠️"
            print(f"  {status} {category}: {result.get('tests_passed', 0)}/{result.get('tests_run', 0)} passed")
        
        if report["recommendations"]:
            print("\n💡 Recommendations:")
            for rec in report["recommendations"]:
                print(f"  • {rec}")


def main():
    """Main entry point for performance test runner."""
    parser = argparse.ArgumentParser(description="Run BladeFighters performance tests")
    parser.add_argument("--config", "-c", default="performance_config.json",
                       help="Path to performance test configuration file")
    parser.add_argument("--output", "-o", help="Output file for performance report")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Initialize test runner
    runner = PerformanceTestRunner(args.config)
    
    # Run tests
    results = runner.run_tests()
    
    # Generate and save report
    report = runner.generate_report()
    output_file = runner.save_report(report, args.output)
    
    # Print summary
    runner.print_summary(report)
    
    # Exit with appropriate code
    if report["summary"]["failed_tests"] > 0:
        print("\n❌ Performance tests failed")
        sys.exit(1)
    else:
        print("\n✅ All performance tests passed")
        sys.exit(0)


if __name__ == "__main__":
    main()
