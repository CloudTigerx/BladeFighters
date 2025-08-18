"""
Performance Profiler for ClusterDetector

This tool profiles the performance of the ClusterDetector class to identify
optimization opportunities and measure performance improvements.

Author: Senior Dev 1 - Task 5B Performance Optimization
"""

import time
import cProfile
import pstats
import io
from typing import List, Set, Tuple, Optional
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.cluster_detection import ClusterDetector


class ClusterDetectorProfiler:
    """Performance profiler for ClusterDetector class."""

    def __init__(self, grid_width: int = 10, grid_height: int = 20, total_grid_height: int = 25):
        """Initialize the profiler with grid dimensions."""
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.total_grid_height = total_grid_height
        self.detector = ClusterDetector(grid_width, grid_height, total_grid_height)

    def create_test_grid(self, complexity: str = "medium") -> List[List[Optional[str]]]:
        """Create test grids of varying complexity."""
        grid = [[None for _ in range(self.grid_width)] for _ in range(self.total_grid_height)]
        
        if complexity == "empty":
            return grid
        elif complexity == "simple":
            # Simple 2x2 cluster
            grid[5][2] = "red"
            grid[5][3] = "red"
            grid[6][2] = "red"
            grid[6][3] = "red"
        elif complexity == "medium":
            # Multiple clusters
            # Red 2x2 cluster
            grid[5][2] = "red"
            grid[5][3] = "red"
            grid[6][2] = "red"
            grid[6][3] = "red"
            # Blue 3x2 cluster
            grid[8][1] = "blue"
            grid[8][2] = "blue"
            grid[8][3] = "blue"
            grid[9][1] = "blue"
            grid[9][2] = "blue"
            grid[9][3] = "blue"
            # Green 2x3 cluster
            grid[12][5] = "green"
            grid[12][6] = "green"
            grid[13][5] = "green"
            grid[13][6] = "green"
            grid[14][5] = "green"
            grid[14][6] = "green"
        elif complexity == "complex":
            # Dense grid with many clusters
            for y in range(10):
                for x in range(self.grid_width):
                    if (x + y) % 3 == 0:
                        grid[y][x] = "red"
                    elif (x + y) % 3 == 1:
                        grid[y][x] = "blue"
                    else:
                        grid[y][x] = "green"
        
        return grid

    def profile_method(self, method_name: str, grid: List[List[Optional[str]]], 
                      iterations: int = 1000, **kwargs) -> dict:
        """Profile a specific method of ClusterDetector."""
        method = getattr(self.detector, method_name)
        
        # Warm up
        for _ in range(10):
            if kwargs:
                method(grid, **kwargs)
            else:
                method(grid)
        
        # Profile
        start_time = time.time()
        for _ in range(iterations):
            if kwargs:
                result = method(grid, **kwargs)
            else:
                result = method(grid)
        end_time = time.time()
        
        total_time = end_time - start_time
        avg_time = total_time / iterations
        ops_per_second = iterations / total_time
        
        return {
            'method': method_name,
            'iterations': iterations,
            'total_time': total_time,
            'avg_time': avg_time,
            'ops_per_second': ops_per_second,
            'result_size': len(result) if hasattr(result, '__len__') else 'N/A'
        }

    def profile_all_methods(self, complexity: str = "medium", iterations: int = 1000) -> dict:
        """Profile all ClusterDetector methods."""
        grid = self.create_test_grid(complexity)
        results = {}
        
        # Profile each method
        methods_to_profile = [
            ('detect_clusters', {}),
            ('find_all_clusters', {}),
            ('find_rectangular_clusters_for_render', {}),
        ]
        
        for method_name, kwargs in methods_to_profile:
            try:
                result = self.profile_method(method_name, grid, iterations, **kwargs)
                results[method_name] = result
                print(f"Profiled {method_name}: {result['avg_time']:.6f}s avg, {result['ops_per_second']:.0f} ops/sec")
            except Exception as e:
                print(f"Error profiling {method_name}: {e}")
                results[method_name] = {'error': str(e)}
        
        # Profile find_connected_pieces separately with correct parameters
        try:
            result = self.profile_method('find_connected_pieces', grid, iterations, 
                                       start_x=2, start_y=5, target_color='red')
            results['find_connected_pieces'] = result
            print(f"Profiled find_connected_pieces: {result['avg_time']:.6f}s avg, {result['ops_per_second']:.0f} ops/sec")
        except Exception as e:
            print(f"Error profiling find_connected_pieces: {e}")
            results['find_connected_pieces'] = {'error': str(e)}
        
        return results

    def detailed_profile(self, method_name: str, grid: List[List[Optional[str]]], 
                        iterations: int = 100) -> dict:
        """Perform detailed profiling with cProfile."""
        method = getattr(self.detector, method_name)
        
        # Create profiler
        pr = cProfile.Profile()
        pr.enable()
        
        # Run method
        for _ in range(iterations):
            method(grid)
        
        pr.disable()
        
        # Get stats
        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
        ps.print_stats(10)  # Top 10 functions
        
        return {
            'method': method_name,
            'iterations': iterations,
            'profile_stats': s.getvalue()
        }

    def benchmark_complexity_scaling(self, iterations: int = 100) -> dict:
        """Benchmark performance across different grid complexities."""
        complexities = ["empty", "simple", "medium", "complex"]
        results = {}
        
        for complexity in complexities:
            print(f"\nBenchmarking {complexity} complexity...")
            grid = self.create_test_grid(complexity)
            
            complexity_results = {}
            for method_name in ['detect_clusters', 'find_all_clusters']:
                try:
                    result = self.profile_method(method_name, grid, iterations)
                    complexity_results[method_name] = result
                except Exception as e:
                    complexity_results[method_name] = {'error': str(e)}
            
            results[complexity] = complexity_results
        
        return results

    def generate_performance_report(self) -> str:
        """Generate a comprehensive performance report."""
        report = []
        report.append("=" * 60)
        report.append("CLUSTER DETECTOR PERFORMANCE REPORT")
        report.append("=" * 60)
        report.append(f"Grid Dimensions: {self.grid_width}x{self.grid_height} (total: {self.total_grid_height})")
        report.append("")
        
        # Profile all methods
        report.append("METHOD PERFORMANCE PROFILES")
        report.append("-" * 40)
        all_results = self.profile_all_methods("medium", 1000)
        
        for method_name, result in all_results.items():
            if 'error' not in result:
                report.append(f"{method_name}:")
                report.append(f"  Average Time: {result['avg_time']:.6f}s")
                report.append(f"  Operations/sec: {result['ops_per_second']:.0f}")
                report.append(f"  Result Size: {result['result_size']}")
                report.append("")
        
        # Complexity scaling
        report.append("COMPLEXITY SCALING ANALYSIS")
        report.append("-" * 40)
        scaling_results = self.benchmark_complexity_scaling(100)
        
        for complexity, methods in scaling_results.items():
            report.append(f"\n{complexity.upper()} COMPLEXITY:")
            for method_name, result in methods.items():
                if 'error' not in result:
                    report.append(f"  {method_name}: {result['avg_time']:.6f}s avg")
        
        # Optimization recommendations
        report.append("\n" + "=" * 60)
        report.append("OPTIMIZATION RECOMMENDATIONS")
        report.append("=" * 60)
        
        # Analyze results and provide recommendations
        detect_clusters_time = all_results.get('detect_clusters', {}).get('avg_time', 0)
        find_all_time = all_results.get('find_all_clusters', {}).get('avg_time', 0)
        
        if detect_clusters_time > 0.001:  # More than 1ms
            report.append("detect_clusters() optimization opportunities:")
            report.append("  - Consider caching visited cells")
            report.append("  - Optimize color comparison logic")
            report.append("  - Reduce redundant grid access")
        
        if find_all_time > 0.002:  # More than 2ms
            report.append("find_all_clusters() optimization opportunities:")
            report.append("  - Cache flood-fill results")
            report.append("  - Optimize cluster grouping algorithm")
            report.append("  - Consider spatial indexing")
        
        report.append("\nNEXT STEPS:")
        report.append("1. Implement caching for frequently accessed data")
        report.append("2. Optimize grid access patterns")
        report.append("3. Add performance monitoring hooks")
        report.append("4. Consider algorithm improvements for large grids")
        
        return "\n".join(report)


def main():
    """Main profiling function."""
    print("Starting ClusterDetector Performance Profiling...")
    
    # Create profiler
    profiler = ClusterDetectorProfiler(10, 20, 25)
    
    # Generate comprehensive report
    report = profiler.generate_performance_report()
    
    # Save report
    with open('performance_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("\n" + report)
    print(f"\nDetailed report saved to: performance_report.txt")
    
    # Quick performance check
    print("\nQUICK PERFORMANCE CHECK:")
    grid = profiler.create_test_grid("medium")
    
    # Test detect_clusters performance
    start_time = time.time()
    for _ in range(1000):
        clusters = profiler.detector.detect_clusters(grid)
    end_time = time.time()
    
    avg_time = (end_time - start_time) / 1000
    print(f"detect_clusters: {avg_time:.6f}s average (1000 iterations)")
    
    if avg_time < 0.001:
        print("Performance is excellent!")
    elif avg_time < 0.005:
        print("Performance is good")
    else:
        print("Performance needs optimization")


if __name__ == "__main__":
    main()
