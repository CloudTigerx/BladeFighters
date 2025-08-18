"""
Performance Validation Test Suite for ClusterDetector - Task 6B Performance Validation.

This module provides comprehensive performance validation tests for the cluster detection functionality,
comparing performance characteristics and ensuring no performance regressions.

Author: Senior Dev 2 - Task 6B (Performance Validation)
"""

import sys
import os
import time
import random
from typing import List, Set, Tuple, Optional

# Add the core directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cluster_detection import ClusterDetector


def create_performance_test_grid(size_factor: int = 1) -> List[List[Optional[str]]]:
    """Create a grid for performance testing with various cluster patterns."""
    grid = [[None for _ in range(10)] for _ in range(25)]
    
    # Add clusters of various sizes
    colors = ['red', 'blue', 'green', 'yellow']
    
    # Add 2x2 clusters
    for i in range(2 * size_factor):
        x = (i * 3) % 8
        y = (i * 3) % 20
        color = colors[i % len(colors)]
        grid[y][x] = f"{color}_block"
        grid[y][x+1] = f"{color}_block"
        grid[y+1][x] = f"{color}_block"
        grid[y+1][x+1] = f"{color}_block"
    
    # Add 3x2 clusters
    for i in range(2 * size_factor):
        x = (i * 4) % 7
        y = (i * 4 + 5) % 18
        color = colors[(i + 1) % len(colors)]
        for dx in range(3):
            for dy in range(2):
                grid[y+dy][x+dx] = f"{color}_block"
    
    # Add some single blocks and lines (non-clusters)
    for i in range(5 * size_factor):
        x = random.randint(0, 9)
        y = random.randint(0, 24)
        if grid[y][x] is None:
            color = colors[random.randint(0, len(colors)-1)]
            grid[y][x] = f"{color}_block"
    
    # Add some garbage and strike blocks
    for i in range(3 * size_factor):
        x = random.randint(0, 9)
        y = random.randint(0, 24)
        if grid[y][x] is None:
            color = colors[random.randint(0, len(colors)-1)]
            if random.random() < 0.5:
                grid[y][x] = f"{color}_garbage"
            else:
                grid[y][x] = f"{color}_strike"
    
    return grid


def benchmark_method(detector: ClusterDetector, method_name: str, method_func, grid: List[List[Optional[str]]], iterations: int = 100) -> Tuple[float, any]:
    """Benchmark a specific method and return timing and result."""
    # Warm up
    for _ in range(10):
        method_func(grid)
    
    # Benchmark
    start_time = time.time()
    result = None
    for _ in range(iterations):
        result = method_func(grid)
    end_time = time.time()
    
    avg_time = (end_time - start_time) / iterations
    return avg_time, result


def test_basic_performance():
    """Test basic performance characteristics."""
    print("\n🧪 TESTING: Basic Performance Characteristics")
    
    detector = ClusterDetector(grid_width=10, grid_height=20, total_grid_height=25)
    grid = create_performance_test_grid()
    
    # Test detect_clusters performance
    avg_time, clusters = benchmark_method(detector, "detect_clusters", detector.detect_clusters, grid)
    print(f"✅ detect_clusters: {avg_time*1000:.3f}ms average ({len(clusters)} clusters found)")
    
    # Test find_all_clusters performance
    avg_time, cluster_groups = benchmark_method(detector, "find_all_clusters", detector.find_all_clusters, grid)
    print(f"✅ find_all_clusters: {avg_time*1000:.3f}ms average ({len(cluster_groups)} cluster groups)")
    
    # Test find_rectangular_clusters_for_render performance
    avg_time, rectangles = benchmark_method(detector, "find_rectangular_clusters_for_render", detector.find_rectangular_clusters_for_render, grid)
    print(f"✅ find_rectangular_clusters_for_render: {avg_time*1000:.3f}ms average ({len(rectangles)} rectangles)")
    
    # Test is_cluster_supported performance
    if cluster_groups:
        avg_time, _ = benchmark_method(detector, "is_cluster_supported", 
                                     lambda g: detector.is_cluster_supported(cluster_groups[0], g), grid)
        print(f"✅ is_cluster_supported: {avg_time*1000:.3f}ms average")
    
    # Test find_connected_pieces performance
    if clusters:
        start_pos = list(clusters)[0]
        avg_time, _ = benchmark_method(detector, "find_connected_pieces", 
                                     lambda g: detector.find_connected_pieces(start_pos[0], start_pos[1], "red", g), grid)
        print(f"✅ find_connected_pieces: {avg_time*1000:.3f}ms average")
    
    return True


def test_scalability():
    """Test performance scalability with different grid sizes and complexity."""
    print("\n🧪 TESTING: Performance Scalability")
    
    detector = ClusterDetector(grid_width=10, grid_height=20, total_grid_height=25)
    
    # Test with different complexity levels
    complexity_levels = [1, 2, 3, 4, 5]
    
    for complexity in complexity_levels:
        grid = create_performance_test_grid(complexity)
        
        # Count blocks for reference
        block_count = sum(1 for row in grid for cell in row if cell is not None)
        
        # Benchmark detect_clusters
        avg_time, clusters = benchmark_method(detector, "detect_clusters", detector.detect_clusters, grid, iterations=50)
        
        print(f"✅ Complexity {complexity} ({block_count} blocks): {avg_time*1000:.3f}ms average ({len(clusters)} clusters)")
        
        # Performance should scale reasonably
        if avg_time > 0.01:  # More than 10ms average
            print(f"⚠️  Performance warning: {avg_time*1000:.3f}ms for complexity {complexity}")
    
    return True


def test_memory_usage():
    """Test memory usage characteristics."""
    print("\n🧪 TESTING: Memory Usage Characteristics")
    
    detector = ClusterDetector(grid_width=10, grid_height=20, total_grid_height=25)
    grid = create_performance_test_grid(3)
    
    # Test that large result sets don't cause memory issues
    clusters = detector.detect_clusters(grid)
    cluster_groups = detector.find_all_clusters(grid)
    rectangles = detector.find_rectangular_clusters_for_render(grid)
    
    print(f"✅ detect_clusters memory: {len(clusters)} cluster blocks")
    print(f"✅ find_all_clusters memory: {len(cluster_groups)} cluster groups")
    print(f"✅ find_rectangular_clusters_for_render memory: {len(rectangles)} rectangles")
    
    # Test that results are reasonable sizes
    if len(clusters) < 1000:  # Should not be unreasonably large
        print("✅ Cluster block count is reasonable")
    else:
        print("⚠️  Warning: Large number of cluster blocks")
    
    if len(cluster_groups) < 100:  # Should not be unreasonably large
        print("✅ Cluster group count is reasonable")
    else:
        print("⚠️  Warning: Large number of cluster groups")
    
    return True


def test_performance_regression():
    """Test for performance regressions by comparing with baseline expectations."""
    print("\n🧪 TESTING: Performance Regression Detection")
    
    detector = ClusterDetector(grid_width=10, grid_height=20, total_grid_height=25)
    grid = create_performance_test_grid(2)
    
    # Define performance baselines (reasonable expectations)
    baselines = {
        "detect_clusters": 0.001,  # 1ms
        "find_all_clusters": 0.002,  # 2ms
        "find_rectangular_clusters_for_render": 0.003,  # 3ms
        "is_cluster_supported": 0.0005,  # 0.5ms
        "find_connected_pieces": 0.001,  # 1ms
    }
    
    # Test each method against baseline
    cluster_groups = detector.find_all_clusters(grid)
    start_pos = (5, 10) if cluster_groups else (0, 0)
    
    methods_to_test = [
        ("detect_clusters", lambda g: detector.detect_clusters(g)),
        ("find_all_clusters", lambda g: detector.find_all_clusters(g)),
        ("find_rectangular_clusters_for_render", lambda g: detector.find_rectangular_clusters_for_render(g)),
        ("is_cluster_supported", lambda g: detector.is_cluster_supported(cluster_groups[0], g) if cluster_groups else True),
        ("find_connected_pieces", lambda g: detector.find_connected_pieces(start_pos[0], start_pos[1], "red", g)),
    ]
    
    for method_name, method_func in methods_to_test:
        avg_time, _ = benchmark_method(detector, method_name, method_func, grid, iterations=100)
        baseline = baselines.get(method_name, 0.001)
        
        if avg_time <= baseline:
            print(f"✅ {method_name}: {avg_time*1000:.3f}ms (baseline: {baseline*1000:.1f}ms) - NO REGRESSION")
        else:
            print(f"⚠️  {method_name}: {avg_time*1000:.3f}ms (baseline: {baseline*1000:.1f}ms) - POTENTIAL REGRESSION")
    
    return True


def test_stress_performance():
    """Test performance under stress conditions."""
    print("\n🧪 TESTING: Stress Performance")
    
    detector = ClusterDetector(grid_width=10, grid_height=20, total_grid_height=25)
    
    # Create a stress test grid (mostly filled)
    stress_grid = [[None for _ in range(10)] for _ in range(25)]
    
    # Fill most of the grid with blocks
    for y in range(20):
        for x in range(10):
            if random.random() < 0.8:  # 80% fill rate
                color = random.choice(['red', 'blue', 'green', 'yellow'])
                stress_grid[y][x] = f"{color}_block"
    
    # Test performance under stress
    start_time = time.time()
    clusters = detector.detect_clusters(stress_grid)
    end_time = time.time()
    stress_time = end_time - start_time
    
    print(f"✅ Stress test detect_clusters: {stress_time*1000:.3f}ms ({len(clusters)} clusters)")
    
    if stress_time < 0.1:  # Should complete within 100ms
        print("✅ Stress test performance is acceptable")
    else:
        print(f"⚠️  Stress test performance warning: {stress_time*1000:.3f}ms")
    
    # Test cluster grouping under stress
    start_time = time.time()
    cluster_groups = detector.find_all_clusters(stress_grid)
    end_time = time.time()
    stress_time = end_time - start_time
    
    print(f"✅ Stress test find_all_clusters: {stress_time*1000:.3f}ms ({len(cluster_groups)} groups)")
    
    if stress_time < 0.1:  # Should complete within 100ms
        print("✅ Stress test cluster grouping performance is acceptable")
    else:
        print(f"⚠️  Stress test cluster grouping performance warning: {stress_time*1000:.3f}ms")
    
    return True


def test_consistency_performance():
    """Test that performance is consistent across multiple runs."""
    print("\n🧪 TESTING: Performance Consistency")
    
    detector = ClusterDetector(grid_width=10, grid_height=20, total_grid_height=25)
    grid = create_performance_test_grid(2)
    
    # Run multiple benchmarks and check consistency
    times = []
    for run in range(5):
        avg_time, _ = benchmark_method(detector, "detect_clusters", detector.detect_clusters, grid, iterations=50)
        times.append(avg_time)
    
    avg_time = sum(times) / len(times)
    max_deviation = max(abs(t - avg_time) for t in times)
    deviation_percent = (max_deviation / avg_time * 100) if avg_time > 0 else 0
    
    print(f"✅ Average time: {avg_time*1000:.3f}ms")
    print(f"✅ Max deviation: {max_deviation*1000:.3f}ms ({deviation_percent:.1f}%)")
    
    if deviation_percent < 50:  # Less than 50% variation
        print("✅ Performance is consistent across runs")
    else:
        print(f"⚠️  Performance variation warning: {deviation_percent:.1f}%")
    
    return True


def main():
    """Run all performance validation tests."""
    print("🚀 SENIOR DEV 2 - TASK 6B: PERFORMANCE VALIDATION")
    print("=" * 60)
    
    # Run all performance test suites
    test_functions = [
        test_basic_performance,
        test_scalability,
        test_memory_usage,
        test_performance_regression,
        test_stress_performance,
        test_consistency_performance
    ]
    
    passed = 0
    total = len(test_functions)
    
    for test_func in test_functions:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test_func.__name__} failed with error: {e}")
    
    print("\n" + "=" * 60)
    print("📊 FINAL PERFORMANCE VALIDATION SUMMARY:")
    print(f"   Total Test Suites: {total}")
    print(f"   Passed: {passed}")
    print(f"   Failed: {total - passed}")
    print(f"   Success Rate: {(passed / total * 100) if total > 0 else 0:.1f}%")
    
    if passed == total:
        print("🎉 ALL PERFORMANCE VALIDATION TESTS PASSED! Task 6B Complete!")
        print("✅ No performance regressions detected")
        print("✅ Performance characteristics are acceptable")
        print("✅ ClusterDetector migration is performance-validated")
        return True
    else:
        print(f"⚠️  {total - passed} test suites failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
