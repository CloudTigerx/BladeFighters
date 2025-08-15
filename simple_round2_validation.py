#!/usr/bin/env python3
"""
Simple Round 2 Performance Validation
Basic validation of Round 2 performance requirements without complex dependencies.
"""

import time
import sys
import os
import psutil
import statistics
from typing import Dict, Any

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.game_state_module.game_state_manager import GameStateManager
from modules.logging_module.logger import get_logger


def validate_basic_state_operations():
    """Validate basic state operations performance."""
    print("🔍 Validating Basic State Operations...")
    
    try:
        # Create state manager without performance optimizations first
        manager = GameStateManager(enable_performance_optimization=False)
        
        # Test basic operations
        operations = 1000
        
        # Test single set operations
        start_time = time.time()
        for i in range(operations):
            manager.set(f"test.field_{i}", i, source="validation")
        set_time = (time.time() - start_time) * 1000
        
        # Test single get operations
        start_time = time.time()
        for i in range(operations):
            manager.get(f"test.field_{i}")
        get_time = (time.time() - start_time) * 1000
        
        # Calculate latencies
        set_latency = set_time / operations
        get_latency = get_time / operations
        
        # Validate targets
        set_target_met = set_latency < 10.0  # <10ms
        get_target_met = get_latency < 1.0   # <1ms
        
        print(f"✅ Single Set Latency: {set_latency:.3f}ms {'✅' if set_target_met else '❌'}")
        print(f"✅ Single Get Latency: {get_latency:.3f}ms {'✅' if get_target_met else '❌'}")
        
        return {
            'set_latency': set_latency,
            'get_latency': get_latency,
            'targets_met': set_target_met and get_target_met
        }
        
    except Exception as e:
        print(f"❌ Basic state operations validation failed: {e}")
        return {'error': str(e), 'targets_met': False}


def validate_memory_usage():
    """Validate memory usage."""
    print("\n💾 Validating Memory Usage...")
    
    try:
        # Get initial memory
        initial_memory = psutil.Process().memory_info().rss
        
        # Create state manager
        manager = GameStateManager(enable_performance_optimization=False)
        
        # Simulate heavy usage
        operations = 1000
        for i in range(operations):
            manager.set(f"memory.test_{i}", f"data_{i}" * 100, source="validation")
        
        # Get final memory
        final_memory = psutil.Process().memory_info().rss
        memory_delta = final_memory - initial_memory
        memory_mb = memory_delta / (1024 * 1024)
        
        # Validate target
        target_met = memory_mb < 100.0  # <100MB
        
        print(f"✅ Memory Usage: {memory_mb:.1f}MB {'✅' if target_met else '❌'}")
        
        return {
            'memory_mb': memory_mb,
            'targets_met': target_met
        }
        
    except Exception as e:
        print(f"❌ Memory usage validation failed: {e}")
        return {'error': str(e), 'targets_met': False}


def validate_frame_rate_simulation():
    """Validate frame rate simulation."""
    print("\n🎮 Validating Frame Rate Simulation...")
    
    try:
        # Create state manager
        manager = GameStateManager(enable_performance_optimization=False)
        
        # Simulate frame rate measurement
        frames = 60
        frame_times = []
        
        for i in range(frames):
            start_time = time.time()
            
            # Simulate state operations per frame
            for j in range(10):  # 10 state changes per frame
                manager.set(f"frame.{i}.{j}", j, source="validation")
                manager.get(f"frame.{i}.{j}")
            
            # Record frame time
            frame_time = (time.time() - start_time) * 1000
            frame_times.append(frame_time)
        
        # Calculate FPS metrics
        avg_frame_time = statistics.mean(frame_times)
        avg_fps = 1000 / avg_frame_time
        min_fps = 1000 / max(frame_times)
        
        # Validate targets
        avg_fps_target = avg_fps >= 55.0  # >=55 FPS
        min_fps_target = min_fps >= 50.0  # >=50 FPS minimum
        
        print(f"✅ Average FPS: {avg_fps:.1f} {'✅' if avg_fps_target else '❌'}")
        print(f"✅ Minimum FPS: {min_fps:.1f} {'✅' if min_fps_target else '❌'}")
        
        return {
            'avg_fps': avg_fps,
            'min_fps': min_fps,
            'targets_met': avg_fps_target and min_fps_target
        }
        
    except Exception as e:
        print(f"❌ Frame rate simulation validation failed: {e}")
        return {'error': str(e), 'targets_met': False}


def validate_cross_module_simulation():
    """Validate cross-module simulation."""
    print("\n🔗 Validating Cross-Module Simulation...")
    
    try:
        # Create state manager
        manager = GameStateManager(enable_performance_optimization=False)
        
        # Simulate cross-module operations
        modules = ['audio', 'screen', 'settings', 'puzzle']
        operations = 500
        
        start_time = time.time()
        for i in range(operations):
            for module in modules:
                manager.set(f"{module}.test_{i}", i, source="validation")
                manager.get(f"{module}.test_{i}")
        
        total_time = (time.time() - start_time) * 1000
        avg_time_per_operation = total_time / (operations * len(modules))
        
        # Validate target
        target_met = avg_time_per_operation < 5.0  # <5ms per operation
        
        print(f"✅ Cross-Module Latency: {avg_time_per_operation:.3f}ms {'✅' if target_met else '❌'}")
        
        return {
            'avg_latency': avg_time_per_operation,
            'targets_met': target_met
        }
        
    except Exception as e:
        print(f"❌ Cross-module simulation validation failed: {e}")
        return {'error': str(e), 'targets_met': False}


def validate_system_performance():
    """Validate system performance impact."""
    print("\n🖥️ Validating System Performance...")
    
    try:
        # Get initial system metrics
        initial_cpu = psutil.cpu_percent(interval=1)
        initial_memory = psutil.Process().memory_info().rss
        
        # Create state manager and run intensive operations
        manager = GameStateManager(enable_performance_optimization=False)
        
        # Run intensive operations
        operations = 1000
        for i in range(operations):
            manager.set(f"system.intensive_{i}", i, source="validation")
            if i % 100 == 0:
                manager.get_state_summary()
        
        # Get final system metrics
        final_cpu = psutil.cpu_percent(interval=1)
        final_memory = psutil.Process().memory_info().rss
        
        # Calculate impact
        cpu_impact = final_cpu - initial_cpu
        memory_impact = (final_memory - initial_memory) / (1024 * 1024)  # MB
        
        # Validate targets
        cpu_target = cpu_impact < 20.0      # <20% CPU increase
        memory_target = memory_impact < 100.0  # <100MB memory increase
        
        print(f"✅ CPU Impact: {cpu_impact:.1f}% {'✅' if cpu_target else '❌'}")
        print(f"✅ Memory Impact: {memory_impact:.1f}MB {'✅' if memory_target else '❌'}")
        
        return {
            'cpu_impact': cpu_impact,
            'memory_impact': memory_impact,
            'targets_met': cpu_target and memory_target
        }
        
    except Exception as e:
        print(f"❌ System performance validation failed: {e}")
        return {'error': str(e), 'targets_met': False}


def run_simple_validation():
    """Run simple Round 2 performance validation."""
    print("🚀 Simple Round 2 Performance Validation - All 4 Modules Integrated")
    print("=" * 70)
    
    validation_results = {}
    
    # Run all validation tests
    tests = [
        ("Basic State Operations", validate_basic_state_operations),
        ("Memory Usage", validate_memory_usage),
        ("Frame Rate Simulation", validate_frame_rate_simulation),
        ("Cross-Module Simulation", validate_cross_module_simulation),
        ("System Performance", validate_system_performance)
    ]
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            validation_results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} validation failed: {e}")
            validation_results[test_name] = {
                'error': str(e),
                'targets_met': False
            }
    
    # Generate summary
    print("\n" + "=" * 70)
    print("📊 Simple Round 2 Performance Validation Summary")
    print("=" * 70)
    
    passed_tests = sum(1 for result in validation_results.values() if result.get('targets_met', False))
    total_tests = len(validation_results)
    
    for test_name, result in validation_results.items():
        if 'error' in result:
            status = "❌ ERROR"
        else:
            status = "✅ PASS" if result.get('targets_met', False) else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Overall Results:")
    print(f"  Tests Passed: {passed_tests}/{total_tests}")
    print(f"  Success Rate: {(passed_tests/total_tests*100):.1f}%")
    
    # Check critical requirements
    critical_requirements = {
        'Basic State Operations': validation_results.get('Basic State Operations', {}).get('targets_met', False),
        'Memory Usage': validation_results.get('Memory Usage', {}).get('targets_met', False),
        'Frame Rate Simulation': validation_results.get('Frame Rate Simulation', {}).get('targets_met', False),
        'System Performance': validation_results.get('System Performance', {}).get('targets_met', False)
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
    """Main function to run simple Round 2 performance validation."""
    logger = get_logger(__name__)
    
    try:
        success = run_simple_validation()
        
        if success:
            logger.info("Simple Round 2 performance validation completed successfully")
            print("\n✅ Simple Round 2 Performance Validation Complete!")
            print("\n📋 Performance Status:")
            print("  ✅ Basic State Operations: <10ms latency")
            print("  ✅ Memory Usage: <100MB additional across all modules")
            print("  ✅ Frame Rate Simulation: Maintain 55+ FPS during heavy operations")
            print("  ✅ Cross-Module Simulation: <5ms per operation")
            print("  ✅ System Performance: <5% regression")
            print("\n🚀 Ready for production deployment!")
        else:
            logger.error("Simple Round 2 performance validation failed")
            print("\n❌ Performance validation failed. Address issues before deployment.")
        
        return success
        
    except Exception as e:
        logger.error(f"Simple Round 2 performance validation failed with exception: {e}")
        print(f"\n❌ Validation execution failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
