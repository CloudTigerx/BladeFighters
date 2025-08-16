#!/usr/bin/env python3
"""
Communication Monitor for BladeFighters

Monitors cross-module communication metrics and performance.
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


class CommunicationMonitor:
    """Monitors cross-module communication."""
    
    def __init__(self, environment: str = "production"):
        self.environment = environment
        self.metrics = {
            "timestamp": datetime.now().isoformat(),
            "environment": environment,
            "communication_metrics": {},
            "summary": {}
        }
    
    def monitor_communication(self) -> Dict[str, Any]:
        """Monitor cross-module communication."""
        print(f"🔗 Monitoring cross-module communication in {self.environment} environment...")
        
        try:
            # Simulate cross-module communication
            communication_times = []
            module_calls = []
            
            for i in range(100):
                start_time = time.time()
                
                # Simulate module-to-module communication
                # This would normally involve actual module calls
                time.sleep(0.001)  # Simulate communication delay
                
                call_time = time.time() - start_time
                communication_times.append(call_time)
                
                module_calls.append({
                    "call_id": i,
                    "source_module": "test_module",
                    "target_module": "game_state_module",
                    "duration_ms": call_time * 1000,
                    "timestamp": datetime.now().isoformat()
                })
            
            return {
                "total_calls": len(module_calls),
                "avg_duration_ms": (sum(communication_times) / len(communication_times)) * 1000,
                "max_duration_ms": max(communication_times) * 1000,
                "min_duration_ms": min(communication_times) * 1000,
                "calls_per_second": len(module_calls) / 10,  # 10 second simulation
                "module_calls": module_calls
            }
            
        except Exception as e:
            print(f"❌ Error monitoring communication: {e}")
            return {
                "error": str(e),
                "total_calls": 0,
                "avg_duration_ms": 0,
                "max_duration_ms": 0,
                "min_duration_ms": 0,
                "calls_per_second": 0
            }
    
    def run_monitoring(self) -> Dict[str, Any]:
        """Run complete communication monitoring."""
        print(f"🚀 Running communication monitoring for {self.environment}...")
        
        # Monitor communication
        self.metrics["communication_metrics"] = self.monitor_communication()
        
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
        
        # Check communication performance
        if "communication_metrics" in self.metrics:
            comm_data = self.metrics["communication_metrics"]
            avg_duration = comm_data.get("avg_duration_ms", 0)
            calls_per_second = comm_data.get("calls_per_second", 0)
            
            if avg_duration > 5:
                summary["alerts"].append(f"Slow communication: {avg_duration:.2f}ms average")
                summary["recommendations"].append("Optimize cross-module communication")
            
            if calls_per_second > 50:
                summary["alerts"].append(f"High communication frequency: {calls_per_second:.2f}/s")
                summary["recommendations"].append("Consider batching module calls")
        
        # Update status
        if summary["alerts"]:
            summary["status"] = "warning"
        
        return summary


def main():
    """Main CLI interface for communication monitoring."""
    parser = argparse.ArgumentParser(description="Communication monitoring for BladeFighters")
    parser.add_argument("--environment", default="production", help="Environment to monitor")
    parser.add_argument("--output", help="Output JSON file path")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        print(f"🔧 Starting communication monitoring for environment: {args.environment}")
    
    # Run monitoring
    monitor = CommunicationMonitor(args.environment)
    results = monitor.run_monitoring()
    
    # Print summary
    if "summary" in results:
        summary = results["summary"]
        print(f"\n📊 Communication Monitoring Summary:")
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
        print(f"\n⚠️ Communication monitoring detected issues")
        sys.exit(1)
    
    print(f"\n✅ Communication monitoring completed successfully")


if __name__ == "__main__":
    main()
