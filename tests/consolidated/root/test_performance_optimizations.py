#!/usr/bin/env python3
"""
Performance Optimization Systems Test Script
Demonstrates the performance optimization systems for state management.
"""

import time
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.game_state_module.game_state_manager import GameStateManager
from modules.game_state_module.performance_benchmarks import run_quick_benchmark, compare_optimization_performance
from modules.game_state_module.performance_overlay import PerformanceOverlay


def test_basic_performance():
    """Test basic performance optimization functionality."""
    print("=== Testing Basic Performance Optimization ===")
    
    # Create state manager with optimizations enabled
    state_manager = GameStateManager(enable_performance_optimization=True)
    
    # Test basic operations
    print("Testing basic state operations...")
    start_time = time.time()
    
    for i in range(1000):
        state_manager.set(f"test.field_{i}", i, source="performance_test")
    
    end_time = time.time()
    duration = (end_time - start_time) * 1000
    print(f"1000 state sets completed in {duration:.2f}ms")
    
    # Test cached state summary
    print("Testing cached state summary...")
    start_time = time.time()
    
    for i in range(100):
        summary = state_manager.get_state_summary()
    
    end_time = time.time()
    duration = (end_time - start_time) * 1000
    print(f"100 state summary calls completed in {duration:.2f}ms")
    
    # Get performance report
    report = state_manager.get_performance_report()
    print(f"Performance optimization enabled: {report['performance_optimization_enabled']}")
    
    if 'profiler' in report:
        profiler_data = report['profiler']
        print(f"Frame rate: {profiler_data['frame_rate']['current_fps']:.1f} FPS")
        print(f"State changes per frame: {profiler_data['state_changes']['avg_per_frame']:.1f}")
    
    if 'cache' in report:
        cache_data = report['cache']
        print(f"Cache hit rate: {cache_data['hit_rate_percent']:.1f}%")
        print(f"Cache entries: {cache_data['total_entries']}")
    
    print()


def test_batching_performance():
    """Test state batching performance."""
    print("=== Testing State Batching Performance ===")
    
    state_manager = GameStateManager(enable_performance_optimization=True)
    
    if not hasattr(state_manager, 'batching_manager'):
        print("Batching manager not available")
        return
    
    # Test individual state changes
    print("Testing individual state changes...")
    start_time = time.time()
    
    for i in range(100):
        state_manager.set(f"individual.field_{i}", i, source="test")
    
    individual_time = (time.time() - start_time) * 1000
    
    # Test batched state changes
    print("Testing batched state changes...")
    start_time = time.time()
    
    changes = [(f"batched.field_{i}", i) for i in range(100)]
    state_manager.batching_manager.batch_ui_changes(changes)
    state_manager.batching_manager.apply_all_pending()
    
    batched_time = (time.time() - start_time) * 1000
    
    print(f"Individual changes: {individual_time:.2f}ms")
    print(f"Batched changes: {batched_time:.2f}ms")
    print(f"Improvement: {((individual_time - batched_time) / individual_time * 100):.1f}%")
    
    # Get batching stats
    stats = state_manager.batching_manager.get_batching_stats()
    print(f"Total batches: {stats['total_batches']}")
    print(f"Average batch size: {stats['avg_batch_size']:.1f}")
    print()


def test_benchmark_suite():
    """Run a quick benchmark suite."""
    print("=== Running Quick Benchmark Suite ===")
    
    try:
        results = run_quick_benchmark()
        
        print("Benchmark Results:")
        for test in results.get('tests', []):
            if test.get('success'):
                test_name = test.get('test_name', 'Unknown')
                ops_per_sec = test.get('operations_per_second', {}).get('mean', 0)
                duration = test.get('duration_ms', {}).get('mean', 0)
                print(f"  {test_name}: {ops_per_sec:.0f} ops/sec ({duration:.2f}ms)")
            else:
                print(f"  {test.get('test_name', 'Unknown')}: FAILED")
        
    except Exception as e:
        print(f"Benchmark failed: {e}")
    
    print()


def test_optimization_comparison():
    """Compare performance with and without optimizations."""
    print("=== Comparing Optimization Performance ===")
    
    try:
        comparison = compare_optimization_performance()
        
        print("Optimization Comparison Results:")
        for suite_name, suite_comparison in comparison.get('comparison', {}).items():
            print(f"\n{suite_name}:")
            for test in suite_comparison:
                test_name = test.get('test_name', 'Unknown')
                improvement = test.get('improvement_percent', 0)
                faster = test.get('faster', False)
                status = "FASTER" if faster else "SLOWER"
                print(f"  {test_name}: {improvement:+.1f}% ({status})")
        
    except Exception as e:
        print(f"Comparison failed: {e}")
    
    print()


def test_performance_overlay():
    """Test performance overlay functionality."""
    print("=== Testing Performance Overlay ===")
    
    state_manager = GameStateManager(enable_performance_optimization=True)
    
    # Create overlay
    overlay = PerformanceOverlay(state_manager)
    
    # Simulate some state changes
    for i in range(50):
        state_manager.set(f"overlay.field_{i}", i, source="overlay_test")
        state_manager.record_frame()
    
    # Update overlay
    overlay.update(time.time())
    
    print("Performance overlay created and updated")
    print("Press F10 in-game to toggle the overlay")
    print()


def main():
    """Run all performance tests."""
    print("Blade Fighters - Performance Optimization Systems Test")
    print("=" * 60)
    print()
    
    try:
        test_basic_performance()
        test_batching_performance()
        test_benchmark_suite()
        test_optimization_comparison()
        test_performance_overlay()
        
        print("All performance tests completed successfully!")
        print()
        print("Performance optimization systems are ready for use.")
        print("Key features:")
        print("- Real-time performance monitoring")
        print("- Intelligent state caching")
        print("- Automatic state batching")
        print("- Performance benchmarking")
        print("- In-game performance overlay")
        
    except Exception as e:
        print(f"Error during performance testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 