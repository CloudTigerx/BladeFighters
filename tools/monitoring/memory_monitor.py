#!/usr/bin/env python3
"""
Memory Monitor for BladeFighters

Monitors memory usage for state operations across all modules.
"""

import argparse
import json
import time
import sys
import psutil
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class MemoryMonitor:
    """Monitors memory usage for state operations."""
    
    def __init__(self, environment: str = "production"):
        self.environment = environment
        self.metrics = {
            "timestamp": datetime.now().isoformat(),
            "environment": environment,
            "memory_usage": {},
            "leak_detection": {},
            "summary": {}
        }
    
    def monitor_memory_usage(self) -> Dict[str, Any]:
        """Monitor memory usage for state operations."""
        print(f"💾 Monitoring memory usage in {self.environment} environment...")
        
        try:
            process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Import and initialize GameStateManager
            from modules.game_state_module.game_state_manager import GameStateManager
            state_manager = GameStateManager()
            
            # Simulate state operations
            memory_samples = []
            for i in range(50):
                # Perform state operations
                for j in range(10):
                    state_manager.set(f"memory_test_{i}_{j}", f"value_{i}_{j}" * 100, source="memory_test")
                
                # Record memory usage
                current_memory = process.memory_info().rss / 1024 / 1024
                memory_samples.append({
                    "iteration": i,
                    "memory_mb": round(current_memory, 2),
                    "timestamp": datetime.now().isoformat()
                })
                
                time.sleep(0.01)  # Small delay
            
            peak_memory = max(sample["memory_mb"] for sample in memory_samples)
            final_memory = memory_samples[-1]["memory_mb"]
            
            return {
                "initial_memory_mb": round(initial_memory, 2),
                "peak_memory_mb": round(peak_memory, 2),
                "final_memory_mb": round(final_memory, 2),
                "memory_increase_mb": round(peak_memory - initial_memory, 2),
                "memory_cleanup_mb": round(peak_memory - final_memory, 2),
                "samples": memory_samples
            }
            
        except Exception as e:
            print(f"❌ Error monitoring memory usage: {e}")
            return {
                "error": str(e),
                "initial_memory_mb": 0,
                "peak_memory_mb": 0,
                "final_memory_mb": 0,
                "memory_increase_mb": 0,
                "memory_cleanup_mb": 0
            }
    
    def detect_memory_leaks(self) -> Dict[str, Any]:
        """Detect potential memory leaks."""
        print(f"🔍 Detecting memory leaks in {self.environment} environment...")
        
        try:
            process = psutil.Process()
            
            # Baseline memory
            baseline_memory = process.memory_info().rss / 1024 / 1024
            
            # Simulate operations that might cause leaks
            from modules.game_state_module.game_state_manager import GameStateManager
            
            # Create multiple state managers (potential leak scenario)
            state_managers = []
            for i in range(10):
                state_manager = GameStateManager()
                for j in range(100):
                    state_manager.set(f"leak_test_{i}_{j}", f"data_{i}_{j}" * 1000, source="leak_test")
                state_managers.append(state_manager)
            
            # Force garbage collection
            import gc
            gc.collect()
            
            # Check memory after operations
            final_memory = process.memory_info().rss / 1024 / 1024
            memory_increase = final_memory - baseline_memory
            
            # Clean up
            del state_managers
            gc.collect()
            
            cleanup_memory = process.memory_info().rss / 1024 / 1024
            cleanup_amount = final_memory - cleanup_memory
            
            return {
                "baseline_memory_mb": round(baseline_memory, 2),
                "peak_memory_mb": round(final_memory, 2),
                "cleanup_memory_mb": round(cleanup_memory, 2),
                "memory_increase_mb": round(memory_increase, 2),
                "cleanup_amount_mb": round(cleanup_amount, 2),
                "potential_leak_mb": round(memory_increase - cleanup_amount, 2),
                "leak_detected": memory_increase - cleanup_amount > 10  # 10MB threshold
            }
            
        except Exception as e:
            print(f"❌ Error detecting memory leaks: {e}")
            return {
                "error": str(e),
                "leak_detected": False
            }
    
    def run_monitoring(self) -> Dict[str, Any]:
        """Run complete memory monitoring."""
        print(f"🚀 Running memory monitoring for {self.environment}...")
        
        # Monitor memory usage
        self.metrics["memory_usage"] = self.monitor_memory_usage()
        
        # Detect memory leaks
        self.metrics["leak_detection"] = self.detect_memory_leaks()
        
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
        
        # Check memory usage
        if "memory_usage" in self.metrics:
            memory_data = self.metrics["memory_usage"]
            memory_increase = memory_data.get("memory_increase_mb", 0)
            
            if memory_increase > 100:
                summary["alerts"].append(f"High memory increase: {memory_increase:.2f}MB")
                summary["recommendations"].append("Investigate memory usage patterns")
            
            if memory_increase > 50:
                summary["recommendations"].append("Consider memory optimization")
        
        # Check for memory leaks
        if "leak_detection" in self.metrics:
            leak_data = self.metrics["leak_detection"]
            if leak_data.get("leak_detected", False):
                summary["alerts"].append("Potential memory leak detected")
                summary["recommendations"].append("Investigate memory leak sources")
                summary["status"] = "warning"
            
            potential_leak = leak_data.get("potential_leak_mb", 0)
            if potential_leak > 5:
                summary["alerts"].append(f"Potential memory leak: {potential_leak:.2f}MB")
                summary["recommendations"].append("Review object lifecycle management")
        
        # Update status
        if summary["alerts"]:
            summary["status"] = "warning"
        
        return summary


def main():
    """Main CLI interface for memory monitoring."""
    parser = argparse.ArgumentParser(description="Memory monitoring for BladeFighters")
    parser.add_argument("--environment", default="production", help="Environment to monitor")
    parser.add_argument("--output", help="Output JSON file path")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        print(f"🔧 Starting memory monitoring for environment: {args.environment}")
    
    # Run monitoring
    monitor = MemoryMonitor(args.environment)
    results = monitor.run_monitoring()
    
    # Print summary
    if "summary" in results:
        summary = results["summary"]
        print(f"\n📊 Memory Monitoring Summary:")
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
        print(f"\n⚠️ Memory monitoring detected issues")
        sys.exit(1)
    
    print(f"\n✅ Memory monitoring completed successfully")


if __name__ == "__main__":
    main()
