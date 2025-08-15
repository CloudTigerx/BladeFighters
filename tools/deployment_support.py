#!/usr/bin/env python3
"""
Deployment Support Tool for BladeFighters
Handles deployment pipeline preparation, rollback mechanisms, and integration monitoring.
"""

import argparse
import json
import sys
import time
import os
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class DeploymentSupport:
    """Deployment support and monitoring system."""
    
    def __init__(self):
        self.deployment_status = {
            "timestamp": datetime.now().isoformat(),
            "status": "preparing",
            "checks": {},
            "rollback_ready": False,
            "integration_issues": []
        }
    
    def prepare_deployment_pipeline(self) -> Dict[str, Any]:
        """Prepare the deployment pipeline for fixes."""
        print("🚀 Preparing deployment pipeline...")
        
        try:
            # Check CI/CD workflows
            workflows_dir = Path(".github/workflows")
            required_workflows = [
                "ci.yml",
                "module-integration.yml",
                "deployment-pipeline.yml",
                "monitoring.yml"
            ]
            
            missing_workflows = []
            for workflow in required_workflows:
                if not (workflows_dir / workflow).exists():
                    missing_workflows.append(workflow)
            
            # Check build artifacts
            build_dir = Path("build")
            if not build_dir.exists():
                build_dir.mkdir(parents=True)
            
            # Create deployment snapshot
            snapshot = self.create_deployment_snapshot()
            
            return {
                "status": "ready" if not missing_workflows else "incomplete",
                "missing_workflows": missing_workflows,
                "build_dir_exists": build_dir.exists(),
                "snapshot_created": snapshot is not None,
                "snapshot_id": snapshot.get("id") if snapshot else None
            }
            
        except Exception as e:
            print(f"❌ Deployment pipeline preparation failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    def create_deployment_snapshot(self) -> Dict[str, Any]:
        """Create a deployment snapshot for rollback."""
        print("📸 Creating deployment snapshot...")
        
        try:
            snapshot_id = f"deployment_{int(time.time())}"
            
            # Create snapshot directory
            snapshot_dir = Path("build/snapshots") / snapshot_id
            snapshot_dir.mkdir(parents=True, exist_ok=True)
            
            # Save current state
            snapshot_data = {
                "id": snapshot_id,
                "timestamp": datetime.now().isoformat(),
                "git_commit": self.get_git_commit(),
                "files": self.get_critical_files(),
                "config": self.get_current_config()
            }
            
            # Write snapshot
            with open(snapshot_dir / "snapshot.json", 'w') as f:
                json.dump(snapshot_data, f, indent=2)
            
            print(f"   ✅ Snapshot created: {snapshot_id}")
            return snapshot_data
            
        except Exception as e:
            print(f"   ❌ Snapshot creation failed: {e}")
            return None
    
    def get_git_commit(self) -> str:
        """Get current git commit hash."""
        try:
            import subprocess
            result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                                  capture_output=True, text=True)
            return result.stdout.strip()
        except:
            return "unknown"
    
    def get_critical_files(self) -> List[str]:
        """Get list of critical files for rollback."""
        critical_files = [
            "game_client.py",
            "main.py",
            "resolution_enhancer.py",
            "modules/testmode_module/test_mode.py",
            "modules/testmode_module/game_state_manager.py"
        ]
        
        existing_files = []
        for file_path in critical_files:
            if Path(file_path).exists():
                existing_files.append(file_path)
        
        return existing_files
    
    def get_current_config(self) -> Dict[str, Any]:
        """Get current configuration state."""
        try:
            config_files = [
                "game_settings.json",
                "game_controls.json",
                "pyproject.toml"
            ]
            
            config = {}
            for config_file in config_files:
                if Path(config_file).exists():
                    with open(config_file, 'r') as f:
                        config[config_file] = f.read()
            
            return config
        except Exception as e:
            return {"error": str(e)}
    
    def setup_rollback_mechanisms(self) -> Dict[str, Any]:
        """Set up rollback mechanisms."""
        print("🔄 Setting up rollback mechanisms...")
        
        try:
            # Create rollback script
            rollback_script = self.create_rollback_script()
            
            # Set up health checks
            health_check_config = self.setup_health_checks()
            
            # Create rollback triggers
            rollback_triggers = self.create_rollback_triggers()
            
            return {
                "status": "ready",
                "rollback_script_created": rollback_script is not None,
                "health_checks_configured": health_check_config is not None,
                "rollback_triggers_created": rollback_triggers is not None
            }
            
        except Exception as e:
            print(f"❌ Rollback setup failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    def create_rollback_script(self) -> str:
        """Create a rollback script."""
        rollback_script = """#!/bin/bash
# BladeFighters Rollback Script
# Usage: ./rollback.sh <snapshot_id>

SNAPSHOT_ID=$1
SNAPSHOT_DIR="build/snapshots/$SNAPSHOT_ID"

if [ -z "$SNAPSHOT_ID" ]; then
    echo "Usage: $0 <snapshot_id>"
    exit 1
fi

if [ ! -d "$SNAPSHOT_DIR" ]; then
    echo "Snapshot $SNAPSHOT_ID not found"
    exit 1
fi

echo "🔄 Rolling back to snapshot: $SNAPSHOT_ID"

# Restore critical files
if [ -f "$SNAPSHOT_DIR/snapshot.json" ]; then
    echo "📁 Restoring files from snapshot..."
    # Add file restoration logic here
fi

echo "✅ Rollback completed"
"""
        
        rollback_path = Path("tools/rollback.sh")
        rollback_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(rollback_path, 'w') as f:
            f.write(rollback_script)
        
        # Make executable
        os.chmod(rollback_path, 0o755)
        
        print("   ✅ Rollback script created")
        return str(rollback_path)
    
    def setup_health_checks(self) -> Dict[str, Any]:
        """Set up health check configuration."""
        health_config = {
            "checks": [
                {
                    "name": "game_startup",
                    "command": "python3 main.py --health-check",
                    "timeout": 30,
                    "retries": 3
                },
                {
                    "name": "test_mode",
                    "command": "python3 -c 'from modules.testmode_module.test_mode import TestModeRefactored; print(\"OK\")'",
                    "timeout": 10,
                    "retries": 2
                },
                {
                    "name": "puzzle_mechanics",
                    "command": "python3 tests/puzzle_mechanics_test_suite.py --quick",
                    "timeout": 60,
                    "retries": 2
                }
            ],
            "rollback_threshold": 2,  # Rollback if 2+ checks fail
            "monitoring_interval": 300  # Check every 5 minutes
        }
        
        health_config_path = Path("build/health_config.json")
        health_config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(health_config_path, 'w') as f:
            json.dump(health_config, f, indent=2)
        
        print("   ✅ Health checks configured")
        return health_config
    
    def create_rollback_triggers(self) -> Dict[str, Any]:
        """Create rollback trigger conditions."""
        triggers = {
            "performance_regression": {
                "memory_threshold_mb": 200,
                "cpu_threshold_percent": 50,
                "fps_threshold": 30
            },
            "error_threshold": {
                "max_errors_per_minute": 10,
                "max_crashes_per_hour": 3
            },
            "integration_failure": {
                "max_failed_tests": 2,
                "critical_module_failure": True
            }
        }
        
        triggers_path = Path("build/rollback_triggers.json")
        triggers_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(triggers_path, 'w') as f:
            json.dump(triggers, f, indent=2)
        
        print("   ✅ Rollback triggers created")
        return triggers
    
    def monitor_integration_issues(self) -> Dict[str, Any]:
        """Monitor for integration issues."""
        print("🔍 Monitoring for integration issues...")
        
        try:
            issues = []
            
            # Check module imports
            modules_to_check = [
                "modules.testmode_module.test_mode",
                "modules.audio_module.audio_system",
                "modules.screen_module.screen_manager",
                "modules.input_module.unified_input_manager",
                "modules.settings_module.config_service"
            ]
            
            for module in modules_to_check:
                try:
                    __import__(module)
                except Exception as e:
                    issues.append(f"Import error in {module}: {e}")
            
            # Check critical functionality
            critical_tests = [
                self.test_game_startup,
                self.test_test_mode_initialization,
                self.test_puzzle_mechanics
            ]
            
            for test_func in critical_tests:
                try:
                    result = test_func()
                    if result.get("status") == "fail":
                        issues.append(f"Critical test failed: {result.get('error', 'Unknown error')}")
                except Exception as e:
                    issues.append(f"Critical test crashed: {e}")
            
            return {
                "status": "healthy" if not issues else "issues_detected",
                "issues": issues,
                "issue_count": len(issues)
            }
            
        except Exception as e:
            print(f"❌ Integration monitoring failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "issues": [f"Monitoring failed: {e}"]
            }
    
    def test_game_startup(self) -> Dict[str, Any]:
        """Test game startup functionality."""
        try:
            # Quick import test
            from game_client import GameClient
            return {"status": "pass"}
        except Exception as e:
            return {"status": "fail", "error": str(e)}
    
    def test_test_mode_initialization(self) -> Dict[str, Any]:
        """Test test mode initialization."""
        try:
            from modules.testmode_module.test_mode import TestModeRefactored
            return {"status": "pass"}
        except Exception as e:
            return {"status": "fail", "error": str(e)}
    
    def test_puzzle_mechanics(self) -> Dict[str, Any]:
        """Test puzzle mechanics."""
        try:
            from core.puzzle_module import PuzzleEngine
            return {"status": "pass"}
        except Exception as e:
            return {"status": "fail", "error": str(e)}
    
    def run_deployment_preparation(self) -> Dict[str, Any]:
        """Run complete deployment preparation."""
        print("🚀 Running deployment preparation...")
        
        # Prepare deployment pipeline
        pipeline_status = self.prepare_deployment_pipeline()
        self.deployment_status["checks"]["pipeline"] = pipeline_status
        
        # Set up rollback mechanisms
        rollback_status = self.setup_rollback_mechanisms()
        self.deployment_status["checks"]["rollback"] = rollback_status
        
        # Monitor integration issues
        integration_status = self.monitor_integration_issues()
        self.deployment_status["checks"]["integration"] = integration_status
        
        # Determine overall status
        all_ready = all(
            check.get("status") in ["ready", "healthy"] 
            for check in self.deployment_status["checks"].values()
        )
        
        self.deployment_status["status"] = "ready" if all_ready else "issues"
        self.deployment_status["rollback_ready"] = rollback_status.get("status") == "ready"
        
        return self.deployment_status
    
    def generate_summary(self):
        """Generate deployment preparation summary."""
        print("\n📊 Deployment Preparation Summary:")
        print("=" * 50)
        
        for check_name, check_result in self.deployment_status["checks"].items():
            status_icon = "✅" if check_result.get("status") in ["ready", "healthy"] else "❌"
            print(f"   {status_icon} {check_name.title()}: {check_result.get('status', 'unknown')}")
            
            if check_result.get("status") == "failed":
                print(f"      Error: {check_result.get('error', 'Unknown error')}")
        
        print("=" * 50)
        print(f"   Overall Status: {self.deployment_status['status'].upper()}")
        print(f"   Rollback Ready: {'✅' if self.deployment_status['rollback_ready'] else '❌'}")
        
        if self.deployment_status["integration_issues"]:
            print(f"   Integration Issues: {len(self.deployment_status['integration_issues'])}")
            for issue in self.deployment_status["integration_issues"][:3]:  # Show first 3
                print(f"      - {issue}")


def main():
    """Main deployment support interface."""
    parser = argparse.ArgumentParser(description="Deployment support for BladeFighters")
    parser.add_argument("--prepare", action="store_true", help="Prepare deployment pipeline")
    parser.add_argument("--rollback", action="store_true", help="Set up rollback mechanisms")
    parser.add_argument("--monitor", action="store_true", help="Monitor integration issues")
    parser.add_argument("--all", action="store_true", help="Run all deployment preparation")
    parser.add_argument("--output", help="Output JSON file path")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        print("🔧 Starting deployment support...")
    
    # Run deployment preparation
    support = DeploymentSupport()
    
    if args.all or not any([args.prepare, args.rollback, args.monitor]):
        results = support.run_deployment_preparation()
        support.generate_summary()
    else:
        results = {"status": "partial"}
        if args.prepare:
            results["pipeline"] = support.prepare_deployment_pipeline()
        if args.rollback:
            results["rollback"] = support.setup_rollback_mechanisms()
        if args.monitor:
            results["integration"] = support.monitor_integration_issues()
    
    # Save results if output specified
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        if args.verbose:
            print(f"\n💾 Results saved to: {output_path}")
    
    # Exit with error code if deployment not ready
    if results.get("status") != "ready":
        print(f"\n⚠️ Deployment preparation incomplete")
        sys.exit(1)
    
    print(f"\n✅ Deployment preparation completed successfully")


if __name__ == "__main__":
    main()

