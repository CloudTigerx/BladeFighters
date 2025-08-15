#!/usr/bin/env python3
"""
State Monitor for BladeFighters

Monitors state change frequency and performance across all modules.
"""

import argparse
import json
import time
import sys
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class StateMonitor:
    """Monitors state changes and performance."""
    
    def __init__(self, environment: str = "production"):
        self.environment = environment
        self.metrics = {
            "timestamp": datetime.now().isoformat(),
            "environment": environment,
            "state_changes": [],
            "performance_metrics": {},
            "summary": {}
        }
    
    def monitor_state_changes(self) -> Dict[str, Any]:
        """Monitor state change frequency."""
        print(f"📊 Monitoring state changes in {self.environment} environment...")
        
        try:
            # Import GameStateManager
            from modules.game_state_module.game_state_manager import GameStateManager
            
            # Initialize state manager
            state_manager = GameStateManager()
            
            # Simulate state changes
            state_changes = []
            for i in range(10):
                start_time = time.time()
                
                # Simulate different types of state changes
                state_manager.set(f"test_field_{i}", f"value_{i}", source="monitor")
                
                change_time = time.time() - start_time
                state_changes.append({
                    "field": f"test_field_{i}",
                    "timestamp": datetime.now().isoformat(),
                    "duration_ms": change_time * 1000,
                    "source": "monitor"
                })
            
            return {
                "total_changes": len(state_changes),
                "avg_duration_ms": sum(c["duration_ms"] for c in state_changes) / len(state_changes),
                "changes_per_second": len(state_changes) / 10,  # 10 second simulation
                "changes": state_changes
            }
            
        except Exception as e:
            print(f"❌ Error monitoring state changes: {e}")
            return {
                "error": str(e),
                "total_changes": 0,
                "avg_duration_ms": 0,
                "changes_per_second": 0
            }
    
    def monitor_performance(self) -> Dict[str, Any]:
        """Monitor state operation performance."""
        print(f"⚡ Monitoring state performance in {self.environment} environment...")
        
        try:
            from modules.game_state_module.game_state_manager import GameStateManager
            
            state_manager = GameStateManager()
            
            # Performance metrics
            get_times = []
            set_times = []
            validation_times = []
            
            for i in range(100):
                # Test get operations
                start_time = time.time()
                state_manager.get(f"perf_test_{i}", "default")
                get_times.append(time.time() - start_time)
                
                # Test set operations
                start_time = time.time()
                state_manager.set(f"perf_test_{i}", f"value_{i}", source="performance_test")
                set_times.append(time.time() - start_time)
                
                # Test validation
                start_time = time.time()
                state_manager.validate_state()
                validation_times.append(time.time() - start_time)
            
            return {
                "get_operations": {
                    "count": len(get_times),
                    "avg_duration_ms": (sum(get_times) / len(get_times)) * 1000,
                    "max_duration_ms": max(get_times) * 1000,
                    "min_duration_ms": min(get_times) * 1000
                },
                "set_operations": {
                    "count": len(set_times),
                    "avg_duration_ms": (sum(set_times) / len(set_times)) * 1000,
                    "max_duration_ms": max(set_times) * 1000,
                    "min_duration_ms": min(set_times) * 1000
                },
                "validation_operations": {
                    "count": len(validation_times),
                    "avg_duration_ms": (sum(validation_times) / len(validation_times)) * 1000,
                    "max_duration_ms": max(validation_times) * 1000,
                    "min_duration_ms": min(validation_times) * 1000
                }
            }
            
        except Exception as e:
            print(f"❌ Error monitoring performance: {e}")
            return {"error": str(e)}
    
    def run_monitoring(self) -> Dict[str, Any]:
        """Run complete state monitoring."""
        print(f"🚀 Running state monitoring for {self.environment}...")
        
        # Monitor state changes
        self.metrics["state_changes"] = self.monitor_state_changes()
        
        # Monitor performance
        self.metrics["performance_metrics"] = self.monitor_performance()
        
        # Generate summary
        self.metrics["summary"] = self.generate_summary()
        
        return self.metrics
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate monitoring summary."""
        summary = {
            "status": "healthy",
            "alerts": [],
            "recommendations": []
        }
        
        # Check state change frequency
        if "state_changes" in self.metrics:
            changes_per_second = self.metrics["state_changes"].get("changes_per_second", 0)
            if changes_per_second > 10:
                summary["alerts"].append(f"High state change frequency: {changes_per_second:.2f}/s")
                summary["recommendations"].append("Consider batching state changes")
        
        # Check performance
        if "performance_metrics" in self.metrics:
            perf = self.metrics["performance_metrics"]
            if "set_operations" in perf:
                avg_set_time = perf["set_operations"].get("avg_duration_ms", 0)
                if avg_set_time > 10:
                    summary["alerts"].append(f"Slow set operations: {avg_set_time:.2f}ms")
                    summary["recommendations"].append("Optimize state set operations")
            
            if "get_operations" in perf:
                avg_get_time = perf["get_operations"].get("avg_duration_ms", 0)
                if avg_get_time > 5:
                    summary["alerts"].append(f"Slow get operations: {avg_get_time:.2f}ms")
                    summary["recommendations"].append("Optimize state get operations")
        
        # Update status
        if summary["alerts"]:
            summary["status"] = "warning"
        
        return summary


def main():
    """Main CLI interface for state monitoring."""
    parser = argparse.ArgumentParser(description="State monitoring for BladeFighters")
    parser.add_argument("--environment", default="production", help="Environment to monitor")
    parser.add_argument("--output", help="Output JSON file path")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        print(f"🔧 Starting state monitoring for environment: {args.environment}")
    
    # Run monitoring
    monitor = StateMonitor(args.environment)
    results = monitor.run_monitoring()
    
    # Print summary
    if "summary" in results:
        summary = results["summary"]
        print(f"\n📊 State Monitoring Summary:")
        print(f"   Status: {summary['status'].upper()}")
        print(f"   Alerts: {len(summary['alerts'])}")
        print(f"   Recommendations: {len(summary['recommendations'])}")
        
        if summary['alerts']:
            print(f"\n⚠️ Alerts:")
            for alert in summary['alerts']:
                print(f"   - {alert}")
        
        if summary['recommendations']:
            print(f"\n💡 Recommendations:")
            for rec in summary['recommendations']:
                print(f"   - {rec}")
    
    # Save results if output specified
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        if args.verbose:
            print(f"\n💾 Results saved to: {output_path}")
    
    # Exit with error code if status is not healthy
    if results.get("summary", {}).get("status") != "healthy":
        print(f"\n⚠️ State monitoring detected issues")
        sys.exit(1)
    
    print(f"\n✅ State monitoring completed successfully")


if __name__ == "__main__":
    main()
