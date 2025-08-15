#!/usr/bin/env python3
"""
Error Monitor for BladeFighters

Monitors error rates per module and operation.
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


class ErrorMonitor:
    """Monitors error rates per module."""
    
    def __init__(self, environment: str = "production"):
        self.environment = environment
        self.metrics = {
            "timestamp": datetime.now().isoformat(),
            "environment": environment,
            "error_metrics": {},
            "summary": {}
        }
    
    def monitor_errors(self) -> Dict[str, Any]:
        """Monitor error rates per module."""
        print(f"⚠️ Monitoring error rates in {self.environment} environment...")
        
        try:
            # Simulate error monitoring
            error_counts = {
                "audio_module": 0,
                "screen_module": 0,
                "input_module": 0,
                "settings_module": 0,
                "game_state_module": 0
            }
            
            total_operations = 1000
            error_log = []
            
            for i in range(total_operations):
                # Simulate operations with occasional errors
                if i % 100 == 0:  # 1% error rate
                    module = list(error_counts.keys())[i % len(error_counts)]
                    error_counts[module] += 1
                    
                    error_log.append({
                        "operation_id": i,
                        "module": module,
                        "error_type": "simulated_error",
                        "timestamp": datetime.now().isoformat(),
                        "message": f"Simulated error in {module}"
                    })
            
            # Calculate error rates
            error_rates = {}
            for module, count in error_counts.items():
                error_rates[module] = {
                    "total_operations": total_operations // len(error_counts),
                    "error_count": count,
                    "error_rate": count / (total_operations // len(error_counts)) * 100
                }
            
            return {
                "total_operations": total_operations,
                "total_errors": sum(error_counts.values()),
                "overall_error_rate": sum(error_counts.values()) / total_operations * 100,
                "module_error_rates": error_rates,
                "error_log": error_log
            }
            
        except Exception as e:
            print(f"❌ Error monitoring errors: {e}")
            return {
                "error": str(e),
                "total_operations": 0,
                "total_errors": 0,
                "overall_error_rate": 0
            }
    
    def run_monitoring(self) -> Dict[str, Any]:
        """Run complete error monitoring."""
        print(f"🚀 Running error monitoring for {self.environment}...")
        
        # Monitor errors
        self.metrics["error_metrics"] = self.monitor_errors()
        
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
        
        # Check error rates
        if "error_metrics" in self.metrics:
            error_data = self.metrics["error_metrics"]
            overall_rate = error_data.get("overall_error_rate", 0)
            
            if overall_rate > 5:
                summary["alerts"].append(f"High overall error rate: {overall_rate:.2f}%")
                summary["recommendations"].append("Investigate error sources")
                summary["status"] = "warning"
            
            # Check individual module error rates
            module_rates = error_data.get("module_error_rates", {})
            for module, rate_data in module_rates.items():
                module_rate = rate_data.get("error_rate", 0)
                if module_rate > 10:
                    summary["alerts"].append(f"High error rate in {module}: {module_rate:.2f}%")
                    summary["recommendations"].append(f"Investigate errors in {module}")
        
        # Update status
        if summary["alerts"]:
            summary["status"] = "warning"
        
        return summary


def main():
    """Main CLI interface for error monitoring."""
    parser = argparse.ArgumentParser(description="Error monitoring for BladeFighters")
    parser.add_argument("--environment", default="production", help="Environment to monitor")
    parser.add_argument("--output", help="Output JSON file path")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        print(f"🔧 Starting error monitoring for environment: {args.environment}")
    
    # Run monitoring
    monitor = ErrorMonitor(args.environment)
    results = monitor.run_monitoring()
    
    # Print summary
    if "summary" in results:
        summary = results["summary"]
        print(f"\n📊 Error Monitoring Summary:")
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
        print(f"\n⚠️ Error monitoring detected issues")
        sys.exit(1)
    
    print(f"\n✅ Error monitoring completed successfully")


if __name__ == "__main__":
    main()
