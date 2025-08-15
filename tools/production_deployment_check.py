#!/usr/bin/env python3
"""
Production Deployment Readiness Check for BladeFighters

This script validates all critical requirements before production deployment,
ensuring the CI/CD pipeline is ready for Round 2 deployment.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class ProductionDeploymentChecker:
    """Validates production deployment readiness."""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "checks": {},
            "overall_status": "pending",
            "critical_issues": [],
            "warnings": [],
            "recommendations": []
        }
    
    def check_module_integrations(self) -> Dict[str, Any]:
        """Check that all 4 modules are properly integrated."""
        print("🔗 Checking module integrations...")
        
        modules = ['audio_module', 'screen_module', 'input_module', 'settings_module']
        integration_status = {
            "modules_checked": len(modules),
            "integrated_modules": [],
            "missing_modules": [],
            "integration_issues": []
        }
        
        for module in modules:
            module_path = Path(f"modules/{module}")
            if module_path.exists():
                # Check for GameStateManager integration
                integration_file = module_path / "game_state_integration.py"
                if integration_file.exists():
                    integration_status["integrated_modules"].append(module)
                else:
                    integration_status["integration_issues"].append(f"Missing GameStateManager integration in {module}")
            else:
                integration_status["missing_modules"].append(module)
        
        integration_status["status"] = "pass" if len(integration_status["integrated_modules"]) == len(modules) else "fail"
        return integration_status
    
    def check_ci_cd_pipeline(self) -> Dict[str, Any]:
        """Check that CI/CD pipeline is properly configured."""
        print("🚀 Checking CI/CD pipeline...")
        
        pipeline_status = {
            "workflows_found": [],
            "missing_workflows": [],
            "pipeline_issues": []
        }
        
        workflows_dir = Path(".github/workflows")
        required_workflows = [
            "ci.yml",
            "module-integration.yml", 
            "deployment-pipeline.yml",
            "monitoring.yml"
        ]
        
        for workflow in required_workflows:
            workflow_path = workflows_dir / workflow
            if workflow_path.exists():
                pipeline_status["workflows_found"].append(workflow)
            else:
                pipeline_status["missing_workflows"].append(workflow)
        
        pipeline_status["status"] = "pass" if len(pipeline_status["missing_workflows"]) == 0 else "fail"
        return pipeline_status
    
    def check_performance_benchmarks(self) -> Dict[str, Any]:
        """Check that performance benchmarks are available."""
        print("⚡ Checking performance benchmarks...")
        
        benchmark_status = {
            "benchmarks_found": [],
            "missing_benchmarks": [],
            "performance_issues": []
        }
        
        build_dir = Path("build/benchmarks")
        if build_dir.exists():
            benchmark_files = list(build_dir.glob("*.json"))
            for benchmark_file in benchmark_files:
                module_name = benchmark_file.stem
                benchmark_status["benchmarks_found"].append(module_name)
                
                # Check performance score
                try:
                    with open(benchmark_file, 'r') as f:
                        data = json.load(f)
                        score = data.get("performance_score", 0)
                        if score < 70:
                            benchmark_status["performance_issues"].append(f"Low performance score for {module_name}: {score}")
                except Exception as e:
                    benchmark_status["performance_issues"].append(f"Error reading benchmark for {module_name}: {e}")
        else:
            benchmark_status["missing_benchmarks"].append("build/benchmarks directory")
        
        benchmark_status["status"] = "pass" if len(benchmark_status["performance_issues"]) == 0 else "fail"
        return benchmark_status
    
    def check_dependency_validation(self) -> Dict[str, Any]:
        """Check that dependency validation is complete."""
        print("🔍 Checking dependency validation...")
        
        dependency_status = {
            "validations_found": [],
            "missing_validations": [],
            "dependency_issues": []
        }
        
        deps_dir = Path("build/deps")
        if deps_dir.exists():
            dep_files = list(deps_dir.glob("*.json"))
            for dep_file in dep_files:
                module_name = dep_file.stem
                dependency_status["validations_found"].append(module_name)
                
                # Check validation score
                try:
                    with open(dep_file, 'r') as f:
                        data = json.load(f)
                        score = data.get("validation_score", 0)
                        conflicts = data.get("conflicts", [])
                        if score < 70:
                            dependency_status["dependency_issues"].append(f"Low validation score for {module_name}: {score}")
                        if conflicts:
                            dependency_status["dependency_issues"].append(f"Conflicts found in {module_name}: {len(conflicts)} conflicts")
                except Exception as e:
                    dependency_status["dependency_issues"].append(f"Error reading validation for {module_name}: {e}")
        else:
            dependency_status["missing_validations"].append("build/deps directory")
        
        dependency_status["status"] = "pass" if len(dependency_status["dependency_issues"]) == 0 else "fail"
        return dependency_status
    
    def check_monitoring_setup(self) -> Dict[str, Any]:
        """Check that monitoring is properly configured."""
        print("📊 Checking monitoring setup...")
        
        monitoring_status = {
            "monitoring_tools": [],
            "missing_tools": [],
            "monitoring_issues": []
        }
        
        monitoring_dir = Path("tools/monitoring")
        required_tools = [
            "state_monitor.py",
            "memory_monitor.py", 
            "communication_monitor.py",
            "error_monitor.py"
        ]
        
        if monitoring_dir.exists():
            for tool in required_tools:
                tool_path = monitoring_dir / tool
                if tool_path.exists():
                    monitoring_status["monitoring_tools"].append(tool)
                else:
                    monitoring_status["missing_tools"].append(tool)
        else:
            monitoring_status["missing_tools"].extend(required_tools)
        
        monitoring_status["status"] = "pass" if len(monitoring_status["missing_tools"]) == 0 else "fail"
        return monitoring_status
    
    def check_rollback_capability(self) -> Dict[str, Any]:
        """Check that rollback capability is available."""
        print("🔄 Checking rollback capability...")
        
        rollback_status = {
            "rollback_components": [],
            "missing_components": [],
            "rollback_issues": []
        }
        
        # Check for rollback-related tools
        rollback_tools = [
            "tools/snapshot_creator.py",
            "tools/rollback_trigger.py",
            "tools/health_checker.py"
        ]
        
        for tool in rollback_tools:
            tool_path = Path(tool)
            if tool_path.exists():
                rollback_status["rollback_components"].append(tool)
            else:
                rollback_status["missing_components"].append(tool)
        
        # Check deployment pipeline for rollback steps
        deployment_workflow = Path(".github/workflows/deployment-pipeline.yml")
        if deployment_workflow.exists():
            with open(deployment_workflow, 'r') as f:
                content = f.read()
                if "rollback" in content.lower():
                    rollback_status["rollback_components"].append("deployment-pipeline.yml")
                else:
                    rollback_status["rollback_issues"].append("Rollback steps not found in deployment pipeline")
        
        rollback_status["status"] = "pass" if len(rollback_status["missing_components"]) == 0 else "fail"
        return rollback_status
    
    def run_all_checks(self) -> Dict[str, Any]:
        """Run all production deployment checks."""
        print("🚀 Running production deployment readiness checks...")
        
        # Run all checks
        self.results["checks"]["module_integrations"] = self.check_module_integrations()
        self.results["checks"]["ci_cd_pipeline"] = self.check_ci_cd_pipeline()
        self.results["checks"]["performance_benchmarks"] = self.check_performance_benchmarks()
        self.results["checks"]["dependency_validation"] = self.check_dependency_validation()
        self.results["checks"]["monitoring_setup"] = self.check_monitoring_setup()
        self.results["checks"]["rollback_capability"] = self.check_rollback_capability()
        
        # Determine overall status
        failed_checks = []
        for check_name, check_result in self.results["checks"].items():
            if check_result.get("status") == "fail":
                failed_checks.append(check_name)
        
        if failed_checks:
            self.results["overall_status"] = "fail"
            self.results["critical_issues"] = failed_checks
        else:
            self.results["overall_status"] = "pass"
        
        # Generate recommendations
        self.results["recommendations"] = self.generate_recommendations()
        
        return self.results
    
    def generate_recommendations(self) -> List[str]:
        """Generate recommendations based on check results."""
        recommendations = []
        
        for check_name, check_result in self.results["checks"].items():
            if check_result.get("status") == "fail":
                if check_name == "module_integrations":
                    recommendations.append("Complete GameStateManager integration for all modules")
                elif check_name == "ci_cd_pipeline":
                    recommendations.append("Set up missing CI/CD workflows")
                elif check_name == "performance_benchmarks":
                    recommendations.append("Run performance benchmarks and address low scores")
                elif check_name == "dependency_validation":
                    recommendations.append("Resolve dependency conflicts and improve validation scores")
                elif check_name == "monitoring_setup":
                    recommendations.append("Set up monitoring tools")
                elif check_name == "rollback_capability":
                    recommendations.append("Implement rollback mechanisms")
        
        if not recommendations:
            recommendations.append("All checks passed - ready for production deployment!")
        
        return recommendations


def main():
    """Main CLI interface for production deployment check."""
    parser = argparse.ArgumentParser(description="Production deployment readiness check")
    parser.add_argument("--output", help="Output JSON file path")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        print("🔧 Starting production deployment readiness check...")
    
    # Run checks
    checker = ProductionDeploymentChecker()
    results = checker.run_all_checks()
    
    # Print summary
    print(f"\n📊 Production Deployment Readiness Summary:")
    print(f"   Overall Status: {results['overall_status'].upper()}")
    print(f"   Checks Passed: {len([c for c in results['checks'].values() if c.get('status') == 'pass'])}")
    print(f"   Checks Failed: {len([c for c in results['checks'].values() if c.get('status') == 'fail'])}")
    
    if results['critical_issues']:
        print(f"   Critical Issues: {', '.join(results['critical_issues'])}")
    
    # Print recommendations
    print(f"\n💡 Recommendations:")
    for rec in results['recommendations']:
        print(f"   - {rec}")
    
    # Save results if output specified
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        if args.verbose:
            print(f"\n💾 Results saved to: {output_path}")
    
    # Exit with error code if checks failed
    if results['overall_status'] == 'fail':
        print("\n❌ Production deployment readiness check failed")
        sys.exit(1)
    
    print("\n✅ Production deployment readiness check passed!")


if __name__ == "__main__":
    main()
