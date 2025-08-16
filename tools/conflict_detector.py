#!/usr/bin/env python3
"""
Conflict Detector for BladeFighters Modules

This tool analyzes test results, performance benchmarks, and dependencies to detect
potential conflicts between modules and integration issues.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class ConflictDetector:
    """Detects conflicts between modules based on test results and benchmarks."""
    
    def __init__(self, test_results_path: str, benchmarks_path: str, deps_path: str):
        self.test_results_path = Path(test_results_path)
        self.benchmarks_path = Path(benchmarks_path)
        self.deps_path = Path(deps_path)
        self.conflicts = []
        self.analysis = {
            "timestamp": datetime.now().isoformat(),
            "conflicts": [],
            "warnings": [],
            "recommendations": [],
            "severity_summary": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0
            }
        }
    
    def load_data(self) -> Dict[str, Any]:
        """Load test results, benchmarks, and dependency data."""
        data = {
            "test_results": {},
            "benchmarks": {},
            "dependencies": {}
        }
        
        # Load test results
        if self.test_results_path.exists():
            for result_file in self.test_results_path.glob("*.json"):
                try:
                    with open(result_file, 'r') as f:
                        module_name = result_file.stem.replace("test-results-", "")
                        data["test_results"][module_name] = json.load(f)
                except Exception as e:
                    print(f"⚠️ Warning: Failed to load test results from {result_file}: {e}")
        
        # Load benchmarks
        if self.benchmarks_path.exists():
            for benchmark_file in self.benchmarks_path.glob("*.json"):
                try:
                    with open(benchmark_file, 'r') as f:
                        module_name = benchmark_file.stem.replace("benchmark-", "")
                        data["benchmarks"][module_name] = json.load(f)
                except Exception as e:
                    print(f"⚠️ Warning: Failed to load benchmark from {benchmark_file}: {e}")
        
        # Load dependencies
        if self.deps_path.exists():
            for dep_file in self.deps_path.glob("*.json"):
                try:
                    with open(dep_file, 'r') as f:
                        module_name = dep_file.stem.replace("deps-", "")
                        data["dependencies"][module_name] = json.load(f)
                except Exception as e:
                    print(f"⚠️ Warning: Failed to load dependencies from {dep_file}: {e}")
        
        return data
    
    def detect_test_conflicts(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect conflicts based on test results."""
        conflicts = []
        
        # Check for test failures
        for module, test_data in data["test_results"].items():
            if "summary" in test_data:
                summary = test_data["summary"]
                if summary.get("failed", 0) > 0:
                    conflicts.append({
                        "type": "test_failure",
                        "module": module,
                        "severity": "high",
                        "description": f"Module {module} has {summary['failed']} test failures",
                        "details": {
                            "failed": summary.get("failed", 0),
                            "passed": summary.get("passed", 0),
                            "total": summary.get("total", 0)
                        }
                    })
        
        # Check for integration test conflicts
        integration_failures = []
        for module, test_data in data["test_results"].items():
            if "tests" in test_data:
                for test in test_data["tests"]:
                    if "integration" in test.get("name", "").lower():
                        if test.get("outcome") == "failed":
                            integration_failures.append({
                                "module": module,
                                "test": test.get("name", "Unknown"),
                                "error": test.get("call", {}).get("longrepr", "Unknown error")
                            })
        
        if integration_failures:
            conflicts.append({
                "type": "integration_failure",
                "severity": "critical",
                "description": f"Found {len(integration_failures)} integration test failures",
                "details": {
                    "failures": integration_failures
                }
            })
        
        return conflicts
    
    def detect_performance_conflicts(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect conflicts based on performance benchmarks."""
        conflicts = []
        
        # Check for performance regressions
        performance_scores = {}
        for module, benchmark_data in data["benchmarks"].items():
            if "performance_score" in benchmark_data:
                performance_scores[module] = benchmark_data["performance_score"]
        
        # Identify modules with low performance scores
        low_performance_modules = []
        for module, score in performance_scores.items():
            if score < 70:
                low_performance_modules.append({
                    "module": module,
                    "score": score
                })
        
        if low_performance_modules:
            conflicts.append({
                "type": "performance_regression",
                "severity": "high",
                "description": f"Found {len(low_performance_modules)} modules with low performance scores",
                "details": {
                    "modules": low_performance_modules
                }
            })
        
        # Check for memory usage conflicts
        memory_conflicts = []
        for module, benchmark_data in data["benchmarks"].items():
            if "memory_usage" in benchmark_data:
                memory_data = benchmark_data["memory_usage"]
                if "memory_increase_mb" in memory_data:
                    increase = memory_data["memory_increase_mb"]
                    if increase > 100:  # More than 100MB increase
                        memory_conflicts.append({
                            "module": module,
                            "increase_mb": increase
                        })
        
        if memory_conflicts:
            conflicts.append({
                "type": "memory_usage",
                "severity": "medium",
                "description": f"Found {len(memory_conflicts)} modules with high memory usage",
                "details": {
                    "modules": memory_conflicts
                }
            })
        
        return conflicts
    
    def detect_dependency_conflicts(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect conflicts based on dependency analysis."""
        conflicts = []
        
        # Check for circular dependencies
        circular_deps = []
        for module, dep_data in data["dependencies"].items():
            if "dependencies" in dep_data and "cross_module_deps" in dep_data["dependencies"]:
                cross_deps = dep_data["dependencies"]["cross_module_deps"]
                for dep in cross_deps:
                    # Check if there's a circular dependency
                    if dep in data["dependencies"]:
                        dep_module_data = data["dependencies"][dep]
                        if "dependencies" in dep_module_data and "cross_module_deps" in dep_module_data["dependencies"]:
                            if module in dep_module_data["dependencies"]["cross_module_deps"]:
                                circular_deps.append({
                                    "module1": module,
                                    "module2": dep
                                })
        
        if circular_deps:
            conflicts.append({
                "type": "circular_dependency",
                "severity": "critical",
                "description": f"Found {len(circular_deps)} circular dependencies",
                "details": {
                    "circular_deps": circular_deps
                }
            })
        
        # Check for dependency conflicts
        dependency_conflicts = []
        for module, dep_data in data["dependencies"].items():
            if "conflicts" in dep_data and dep_data["conflicts"]:
                dependency_conflicts.append({
                    "module": module,
                    "conflicts": dep_data["conflicts"]
                })
        
        if dependency_conflicts:
            conflicts.append({
                "type": "dependency_conflict",
                "severity": "high",
                "description": f"Found dependency conflicts in {len(dependency_conflicts)} modules",
                "details": {
                    "modules": dependency_conflicts
                }
            })
        
        return conflicts
    
    def detect_integration_conflicts(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect conflicts in module integration."""
        conflicts = []
        
        # Check for GameStateManager integration issues
        integration_issues = []
        for module, dep_data in data["dependencies"].items():
            if "integration_points" in dep_data:
                integration = dep_data["integration_points"]
                if "integration_score" in integration:
                    score = integration["integration_score"]
                    if score < 50:
                        integration_issues.append({
                            "module": module,
                            "score": score
                        })
        
        if integration_issues:
            conflicts.append({
                "type": "integration_issue",
                "severity": "high",
                "description": f"Found {len(integration_issues)} modules with poor GameStateManager integration",
                "details": {
                    "modules": integration_issues
                }
            })
        
        # Check for state operation conflicts
        state_conflicts = []
        for module, benchmark_data in data["benchmarks"].items():
            if "state_operations" in benchmark_data:
                state_ops = benchmark_data["state_operations"]
                if "success_rate" in state_ops and state_ops["success_rate"] < 0.95:
                    state_conflicts.append({
                        "module": module,
                        "success_rate": state_ops["success_rate"]
                    })
        
        if state_conflicts:
            conflicts.append({
                "type": "state_operation_failure",
                "severity": "critical",
                "description": f"Found {len(state_conflicts)} modules with state operation failures",
                "details": {
                    "modules": state_conflicts
                }
            })
        
        return conflicts
    
    def generate_recommendations(self, conflicts: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on detected conflicts."""
        recommendations = []
        
        # Count conflict types
        conflict_types = {}
        for conflict in conflicts:
            conflict_type = conflict["type"]
            conflict_types[conflict_type] = conflict_types.get(conflict_type, 0) + 1
        
        # Generate specific recommendations
        if "test_failure" in conflict_types:
            recommendations.append("Fix failing tests before deployment")
        
        if "integration_failure" in conflict_types:
            recommendations.append("Review and fix integration test failures")
        
        if "performance_regression" in conflict_types:
            recommendations.append("Optimize modules with low performance scores")
        
        if "memory_usage" in conflict_types:
            recommendations.append("Investigate and reduce memory usage in affected modules")
        
        if "circular_dependency" in conflict_types:
            recommendations.append("Resolve circular dependencies between modules")
        
        if "dependency_conflict" in conflict_types:
            recommendations.append("Resolve naming conflicts and dependency issues")
        
        if "integration_issue" in conflict_types:
            recommendations.append("Improve GameStateManager integration in affected modules")
        
        if "state_operation_failure" in conflict_types:
            recommendations.append("Fix state operation failures in affected modules")
        
        # General recommendations
        if len(conflicts) > 5:
            recommendations.append("Consider postponing deployment due to multiple critical issues")
        
        if not recommendations:
            recommendations.append("No critical conflicts detected - deployment can proceed")
        
        return recommendations
    
    def run_detection(self) -> Dict[str, Any]:
        """Run complete conflict detection."""
        print("🔍 Loading data for conflict detection...")
        data = self.load_data()
        
        print("🧪 Detecting test conflicts...")
        test_conflicts = self.detect_test_conflicts(data)
        self.conflicts.extend(test_conflicts)
        
        print("⚡ Detecting performance conflicts...")
        perf_conflicts = self.detect_performance_conflicts(data)
        self.conflicts.extend(perf_conflicts)
        
        print("🔗 Detecting dependency conflicts...")
        dep_conflicts = self.detect_dependency_conflicts(data)
        self.conflicts.extend(dep_conflicts)
        
        print("🔗 Detecting integration conflicts...")
        int_conflicts = self.detect_integration_conflicts(data)
        self.conflicts.extend(int_conflicts)
        
        # Update analysis
        self.analysis["conflicts"] = self.conflicts
        
        # Count severities
        for conflict in self.conflicts:
            severity = conflict.get("severity", "low")
            self.analysis["severity_summary"][severity] += 1
        
        # Generate recommendations
        self.analysis["recommendations"] = self.generate_recommendations(self.conflicts)
        
        return self.analysis


def main():
    """Main CLI interface for conflict detection."""
    parser = argparse.ArgumentParser(description="Conflict detection for BladeFighters modules")
    parser.add_argument("--test-results", required=True, help="Path to test results directory")
    parser.add_argument("--benchmarks", required=True, help="Path to benchmarks directory")
    parser.add_argument("--deps", required=True, help="Path to dependencies directory")
    parser.add_argument("--output", help="Output JSON file path")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        print(f"🔧 Starting conflict detection...")
    
    # Run detection
    detector = ConflictDetector(args.test_results, args.benchmarks, args.deps)
    analysis = detector.run_detection()
    
    # Print summary
    print(f"📊 Conflict Detection Summary:")
    print(f"   Total conflicts: {len(analysis['conflicts'])}")
    print(f"   Critical: {analysis['severity_summary']['critical']}")
    print(f"   High: {analysis['severity_summary']['high']}")
    print(f"   Medium: {analysis['severity_summary']['medium']}")
    print(f"   Low: {analysis['severity_summary']['low']}")
    
    # Print recommendations
    print(f"💡 Recommendations:")
    for rec in analysis['recommendations']:
        print(f"   - {rec}")
    
    # Save results if output specified
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        if args.verbose:
            print(f"💾 Results saved to: {output_path}")
    
    # Exit with error code if critical conflicts exist
    if analysis['severity_summary']['critical'] > 0:
        print("❌ Critical conflicts detected - deployment blocked")
        sys.exit(1)
    
    if analysis['severity_summary']['high'] > 3:
        print("⚠️ Multiple high-severity conflicts detected - review required")
        sys.exit(1)
    
    print("✅ Conflict detection completed")


if __name__ == "__main__":
    main()
