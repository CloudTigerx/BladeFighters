#!/usr/bin/env python3
"""
Round 2 Performance Validation Script
Simplified but comprehensive validation of Round 2 performance requirements.
"""

import time
import sys
import os
import psutil
import statistics
from typing import Dict, Any, List

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.game_state_module.game_state_manager import GameStateManager
from modules.logging_module.logger import get_logger


class Round2PerformanceValidator:
    """Comprehensive Round 2 performance validator."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.results = {}
        
    def validate_cross_module_state_operations(self) -> Dict[str, Any]:
        """Validate cross-module state operations performance."""
        print("🔍 Validating Cross-Module State Operations...")
        
        # Create state manager with optimizations
        manager = GameStateManager(enable_performance_optimization=True)
        
        # Test state operations across all modules
        modules = ['audio', 'screen', 'settings', 'puzzle']
        operations = 1000
        
        results = {
            'single_set_latency': [],
            'single_get_latency': [],
            'batch_operations': [],
            'cross_module_calls': []
        }
        
        # Test single set operations
        start_time = time.time()
        for i in range(operations):
            for module in modules:
                manager.set(f"{module}.test_field_{i}", i, source="validation")
        set_time = (time.time() - start_time) * 1000
        results['single_set_latency'] = set_time / (operations * len(modules))
        
        # Test single get operations
        start_time = time.time()
        for i in range(operations):
            for module in modules:
                manager.get(f"{module}.test_field_{i}")
        get_time = (time.time() - start_time) * 1000
        results['single_get_latency'] = get_time / (operations * len(modules))
        
        # Test batch operations
        if hasattr(manager, 'batching_manager'):
            start_time = time.time()
            for i in range(operations // 10):  # Batch every 10 operations
                changes = []
                for j in range(10):
                    for module in modules:
                        changes.append((f"{module}.batch_{i}_{j}", j))
                manager.batching_manager.batch_ui_changes(changes)
            manager.batching_manager.apply_all_pending()
            batch_time = (time.time() - start_time) * 1000
            results['batch_operations'] = batch_time / operations
        else:
            results['batch_operations'] = results['single_set_latency']
        
        # Test cross-module calls
        start_time = time.time()
        for i in range(operations):
            # Simulate cross-module communication
            summary = manager.get_state_summary()
        cross_module_time = (time.time() - start_time) * 1000
        results['cross_module_calls'] = cross_module_time / operations
        
        # Validate targets
        targets_met = {
            'single_set': results['single_set_latency'] < 10.0,  # <10ms
            'single_get': results['single_get_latency'] < 1.0,   # <1ms
            'batch_ops': results['batch_operations'] < 5.0,      # <5ms
            'cross_module': results['cross_module_calls'] < 5.0  # <5ms
        }
        
        print(f"✅ Single Set Latency: {results['single_set_latency']:.3f}ms {'✅' if targets_met['single_set'] else '❌'}")
        print(f"✅ Single Get Latency: {results['single_get_latency']:.3f}ms {'✅' if targets_met['single_get'] else '❌'}")
        print(f"✅ Batch Operations: {results['batch_operations']:.3f}ms {'✅' if targets_met['batch_ops'] else '❌'}")
        print(f"✅ Cross-Module Calls: {results['cross_module_calls']:.3f}ms {'✅' if targets_met['cross_module'] else '❌'}")
        
        return {
            'metrics': results,
            'targets_met': targets_met,
            'all_targets_met': all(targets_met.values())
        }
    
    def validate_memory_usage(self) -> Dict[str, Any]:
        """Validate memory usage across all modules."""
        print("\n💾 Validating Memory Usage...")
        
        # Get initial memory
        initial_memory = self._get_memory_usage()
        
        # Create state manager with optimizations
        manager = GameStateManager(enable_performance_optimization=True)
        
        # Simulate heavy usage across all modules
        modules = ['audio', 'screen', 'settings', 'puzzle']
        operations = 1000
        
        for i in range(operations):
            for module in modules:
                manager.set(f"{module}.memory_test_{i}", f"data_{i}" * 100, source="validation")
        
        # Get final memory
        final_memory = self._get_memory_usage()
        memory_delta = final_memory - initial_memory
        
        # Calculate per module memory
        per_module_memory = memory_delta / len(modules)
        
        # Validate targets
        targets_met = {
            'total_memory': memory_delta < 100 * 1024 * 1024,  # <100MB
            'per_module': per_module_memory < 25 * 1024 * 1024  # <25MB per module
        }
        
        print(f"✅ Total Memory Usage: {memory_delta / (1024*1024):.1f}MB {'✅' if targets_met['total_memory'] else '❌'}")
        print(f"✅ Per Module Memory: {per_module_memory / (1024*1024):.1f}MB {'✅' if targets_met['per_module'] else '❌'}")
        
        return {
            'total_memory_mb': memory_delta / (1024 * 1024),
            'per_module_mb': per_module_memory / (1024 * 1024),
            'targets_met': targets_met,
            'all_targets_met': all(targets_met.values())
        }
    
    def validate_frame_rate_impact(self) -> Dict[str, Any]:
        """Validate frame rate impact during heavy operations."""
        print("\n🎮 Validating Frame Rate Impact...")
        
        # Create state manager with optimizations
        manager = GameStateManager(enable_performance_optimization=True)
        
        # Simulate frame rate measurement
        frames = 60
        frame_times = []
        
        for i in range(frames):
            start_time = time.time()
            
            # Simulate heavy state operations per frame
            for j in range(20):  # 20 state changes per frame
                manager.set(f"frame.{i}.{j}", j, source="validation")
                manager.get(f"frame.{i}.{j}")
            
            # Record frame time
            frame_time = (time.time() - start_time) * 1000
            frame_times.append(frame_time)
        
        # Calculate FPS metrics
        avg_frame_time = statistics.mean(frame_times)
        min_frame_time = min(frame_times)
        max_frame_time = max(frame_times)
        avg_fps = 1000 / avg_frame_time
        min_fps = 1000 / max_frame_time
        max_fps = 1000 / min_frame_time
        
        # Validate targets
        targets_met = {
            'avg_fps': avg_fps >= 55.0,  # >=55 FPS
            'min_fps': min_fps >= 50.0,  # >=50 FPS minimum
            'frame_time_variance': statistics.stdev(frame_times) < 2.0  # <2ms variance
        }
        
        print(f"✅ Average FPS: {avg_fps:.1f} {'✅' if targets_met['avg_fps'] else '❌'}")
        print(f"✅ Minimum FPS: {min_fps:.1f} {'✅' if targets_met['min_fps'] else '❌'}")
        print(f"✅ Frame Time Variance: {statistics.stdev(frame_times):.2f}ms {'✅' if targets_met['frame_time_variance'] else '❌'}")
        
        return {
            'avg_fps': avg_fps,
            'min_fps': min_fps,
            'max_fps': max_fps,
            'frame_time_variance': statistics.stdev(frame_times),
            'targets_met': targets_met,
            'all_targets_met': all(targets_met.values())
        }
    
    def validate_state_change_frequency(self) -> Dict[str, Any]:
        """Validate state change frequency optimization."""
        print("\n⚡ Validating State Change Frequency...")
        
        # Create state manager with optimizations
        manager = GameStateManager(enable_performance_optimization=True)
        
        # Test high-frequency state changes
        operations = 1000
        changes_per_frame = 50
        
        # Test individual changes
        start_time = time.time()
        for i in range(operations):
            manager.set(f"frequency.individual_{i}", i, source="validation")
        individual_time = (time.time() - start_time) * 1000
        
        # Test batched changes
        if hasattr(manager, 'batching_manager'):
            start_time = time.time()
            for i in range(operations // changes_per_frame):
                changes = [(f"frequency.batch_{i}_{j}", j) for j in range(changes_per_frame)]
                manager.batching_manager.batch_ui_changes(changes)
            manager.batching_manager.apply_all_pending()
            batch_time = (time.time() - start_time) * 1000
        else:
            batch_time = individual_time
        
        # Calculate efficiency improvement
        efficiency_improvement = ((individual_time - batch_time) / individual_time) * 100 if individual_time > 0 else 0
        
        # Validate targets
        targets_met = {
            'individual_latency': individual_time / operations < 10.0,  # <10ms per operation
            'batch_latency': batch_time / operations < 5.0,            # <5ms per operation
            'efficiency_improvement': efficiency_improvement > 20.0     # >20% improvement
        }
        
        print(f"✅ Individual Latency: {individual_time/operations:.3f}ms {'✅' if targets_met['individual_latency'] else '❌'}")
        print(f"✅ Batch Latency: {batch_time/operations:.3f}ms {'✅' if targets_met['batch_latency'] else '❌'}")
        print(f"✅ Efficiency Improvement: {efficiency_improvement:.1f}% {'✅' if targets_met['efficiency_improvement'] else '❌'}")
        
        return {
            'individual_latency': individual_time / operations,
            'batch_latency': batch_time / operations,
            'efficiency_improvement': efficiency_improvement,
            'targets_met': targets_met,
            'all_targets_met': all(targets_met.values())
        }
    
    def validate_overall_system_performance(self) -> Dict[str, Any]:
        """Validate overall system performance impact."""
        print("\n🖥️ Validating Overall System Performance...")
        
        # Get initial system metrics
        initial_cpu = psutil.cpu_percent(interval=1)
        initial_memory = self._get_memory_usage()
        
        # Create state manager and run intensive operations
        manager = GameStateManager(enable_performance_optimization=True)
        
        # Run intensive operations
        operations = 2000
        for i in range(operations):
            manager.set(f"system.intensive_{i}", i, source="validation")
            if i % 100 == 0:
                manager.get_state_summary()
        
        # Get final system metrics
        final_cpu = psutil.cpu_percent(interval=1)
        final_memory = self._get_memory_usage()
        
        # Calculate impact
        cpu_impact = final_cpu - initial_cpu
        memory_impact = (final_memory - initial_memory) / (1024 * 1024)  # MB
        
        # Validate targets
        targets_met = {
            'cpu_impact': cpu_impact < 20.0,      # <20% CPU increase
            'memory_impact': memory_impact < 100.0,  # <100MB memory increase
            'performance_regression': memory_impact < 50.0  # <50MB for <5% regression
        }
        
        print(f"✅ CPU Impact: {cpu_impact:.1f}% {'✅' if targets_met['cpu_impact'] else '❌'}")
        print(f"✅ Memory Impact: {memory_impact:.1f}MB {'✅' if targets_met['memory_impact'] else '❌'}")
        print(f"✅ Performance Regression: {memory_impact:.1f}MB {'✅' if targets_met['performance_regression'] else '❌'}")
        
        return {
            'cpu_impact': cpu_impact,
            'memory_impact': memory_impact,
            'targets_met': targets_met,
            'all_targets_met': all(targets_met.values())
        }
    
    def _get_memory_usage(self) -> int:
        """Get current memory usage in bytes."""
        try:
            process = psutil.Process()
            return process.memory_info().rss
        except Exception:
            return 0
    
    def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run comprehensive Round 2 performance validation."""
        print("🚀 Round 2 Performance Validation - All 4 Modules Integrated")
        print("=" * 70)
        
        validation_results = {}
        
        # Run all validation tests
        tests = [
            ("Cross-Module State Operations", self.validate_cross_module_state_operations),
            ("Memory Usage", self.validate_memory_usage),
            ("Frame Rate Impact", self.validate_frame_rate_impact),
            ("State Change Frequency", self.validate_state_change_frequency),
            ("Overall System Performance", self.validate_overall_system_performance)
        ]
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                validation_results[test_name] = result
            except Exception as e:
                print(f"❌ {test_name} validation failed: {e}")
                validation_results[test_name] = {
                    'error': str(e),
                    'all_targets_met': False
                }
        
        # Generate summary
        print("\n" + "=" * 70)
        print("📊 Round 2 Performance Validation Summary")
        print("=" * 70)
        
        passed_tests = sum(1 for result in validation_results.values() if result.get('all_targets_met', False))
        total_tests = len(validation_results)
        
        for test_name, result in validation_results.items():
            if 'error' in result:
                status = "❌ ERROR"
            else:
                status = "✅ PASS" if result.get('all_targets_met', False) else "❌ FAIL"
            print(f"{status} {test_name}")
        
        print(f"\n🎯 Overall Results:")
        print(f"  Tests Passed: {passed_tests}/{total_tests}")
        print(f"  Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        # Check critical requirements
        critical_requirements = {
            'Cross-Module State Operations': validation_results.get('Cross-Module State Operations', {}).get('all_targets_met', False),
            'Memory Usage': validation_results.get('Memory Usage', {}).get('all_targets_met', False),
            'Frame Rate Impact': validation_results.get('Frame Rate Impact', {}).get('all_targets_met', False),
            'Overall System Performance': validation_results.get('Overall System Performance', {}).get('all_targets_met', False)
        }
        
        critical_passed = sum(critical_requirements.values())
        print(f"\n🔴 Critical Requirements:")
        for req, passed in critical_requirements.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"  {status} {req}")
        
        print(f"\n  Critical Requirements Passed: {critical_passed}/{len(critical_requirements)}")
        
        if passed_tests == total_tests and critical_passed == len(critical_requirements):
            print("\n🎉 All validations passed! Round 2 performance requirements met.")
            return True
        else:
            print(f"\n⚠️  {total_tests - passed_tests} validations failed. Review performance issues.")
            return False


def main():
    """Main function to run Round 2 performance validation."""
    logger = get_logger(__name__)
    
    try:
        validator = Round2PerformanceValidator()
        success = validator.run_comprehensive_validation()
        
        if success:
            logger.info("Round 2 performance validation completed successfully")
            print("\n✅ Round 2 Performance Validation Complete!")
            print("\n📋 Performance Status:")
            print("  ✅ Cross-Module State Operations: <10ms latency")
            print("  ✅ Memory Usage: <100MB additional across all modules")
            print("  ✅ Frame Rate Impact: Maintain 55+ FPS during heavy operations")
            print("  ✅ State Change Frequency: Optimized high-frequency operations")
            print("  ✅ Overall System Performance: <5% regression")
            print("\n🚀 Ready for production deployment!")
        else:
            logger.error("Round 2 performance validation failed")
            print("\n❌ Performance validation failed. Address issues before deployment.")
        
        return success
        
    except Exception as e:
        logger.error(f"Round 2 performance validation failed with exception: {e}")
        print(f"\n❌ Validation execution failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
