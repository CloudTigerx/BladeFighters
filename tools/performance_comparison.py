"""
Performance Comparison Tool

This tool compares the performance of the original ClusterDetector vs the
optimized version to measure improvements.

Author: Senior Dev 1 - Task 5B Performance Optimization
"""

import time
import sys
import os
from typing import List, Optional

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.cluster_detection import ClusterDetector
from core.cluster_detection_optimized import OptimizedClusterDetector


class PerformanceComparator:
    """Compare performance between original and optimized ClusterDetector."""

    def __init__(self, grid_width: int = 10, grid_height: int = 20, total_grid_height: int = 25):
        """Initialize the comparator."""
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.total_grid_height = total_grid_height
        
        self.original_detector = ClusterDetector(grid_width, grid_height, total_grid_height)
        self.optimized_detector = OptimizedClusterDetector(grid_width, grid_height, total_grid_height)

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

    def benchmark_method(self, method_name: str, grid: List[List[Optional[str]]], 
                        iterations: int = 1000, **kwargs) -> dict:
        """Benchmark a specific method on both detectors."""
        
        # Test original detector
        original_method = getattr(self.original_detector, method_name)
        
        # Warm up
        for _ in range(10):
            if kwargs:
                original_method(grid, **kwargs)
            else:
                original_method(grid)
        
        # Benchmark original
        start_time = time.time()
        for _ in range(iterations):
            if kwargs:
                original_result = original_method(grid, **kwargs)
            else:
                original_result = original_method(grid)
        original_time = time.time() - start_time
        
        # Test optimized detector
        optimized_method = getattr(self.optimized_detector, method_name)
        
        # Warm up
        for _ in range(10):
            if kwargs:
                optimized_method(grid, **kwargs)
            else:
                optimized_method(grid)
        
        # Benchmark optimized
        start_time = time.time()
        for _ in range(iterations):
            if kwargs:
                optimized_result = optimized_method(grid, **kwargs)
            else:
                optimized_result = optimized_method(grid)
        optimized_time = time.time() - start_time
        
        # Calculate improvement
        improvement = ((original_time - optimized_time) / original_time) * 100 if original_time > 0 else 0
        
        return {
            'method': method_name,
            'iterations': iterations,
            'original_time': original_time,
            'optimized_time': optimized_time,
            'improvement_percent': improvement,
            'original_ops_per_sec': iterations / original_time if original_time > 0 else 0,
            'optimized_ops_per_sec': iterations / optimized_time if optimized_time > 0 else 0,
            'results_match': original_result == optimized_result
        }

    def run_comprehensive_comparison(self) -> dict:
        """Run comprehensive performance comparison."""
        print("Starting comprehensive performance comparison...")
        
        results = {}
        complexities = ["empty", "simple", "medium", "complex"]
        
        for complexity in complexities:
            print(f"\nTesting {complexity} complexity...")
            grid = self.create_test_grid(complexity)
            
            complexity_results = {}
            
            # Test all methods
            methods_to_test = [
                ('detect_clusters', {}),
                ('find_all_clusters', {}),
                ('find_rectangular_clusters_for_render', {}),
            ]
            
            for method_name, kwargs in methods_to_test:
                try:
                    result = self.benchmark_method(method_name, grid, 1000, **kwargs)
                    complexity_results[method_name] = result
                    
                    print(f"  {method_name}:")
                    print(f"    Original: {result['original_time']:.6f}s ({result['original_ops_per_sec']:.0f} ops/sec)")
                    print(f"    Optimized: {result['optimized_time']:.6f}s ({result['optimized_ops_per_sec']:.0f} ops/sec)")
                    print(f"    Improvement: {result['improvement_percent']:.1f}%")
                    print(f"    Results match: {result['results_match']}")
                    
                except Exception as e:
                    print(f"  Error testing {method_name}: {e}")
                    complexity_results[method_name] = {'error': str(e)}
            
            results[complexity] = complexity_results
        
        return results

    def generate_comparison_report(self) -> str:
        """Generate a comprehensive comparison report."""
        results = self.run_comprehensive_comparison()
        
        report = []
        report.append("=" * 80)
        report.append("CLUSTER DETECTOR PERFORMANCE COMPARISON REPORT")
        report.append("=" * 80)
        report.append(f"Grid Dimensions: {self.grid_width}x{self.grid_height} (total: {self.total_grid_height})")
        report.append("")
        
        # Summary statistics
        total_improvements = []
        total_original_time = 0
        total_optimized_time = 0
        
        for complexity, methods in results.items():
            report.append(f"{complexity.upper()} COMPLEXITY:")
            report.append("-" * 40)
            
            for method_name, result in methods.items():
                if 'error' not in result:
                    report.append(f"{method_name}:")
                    report.append(f"  Original: {result['original_time']:.6f}s ({result['original_ops_per_sec']:.0f} ops/sec)")
                    report.append(f"  Optimized: {result['optimized_time']:.6f}s ({result['optimized_ops_per_sec']:.0f} ops/sec)")
                    report.append(f"  Improvement: {result['improvement_percent']:.1f}%")
                    report.append(f"  Results match: {result['results_match']}")
                    report.append("")
                    
                    total_improvements.append(result['improvement_percent'])
                    total_original_time += result['original_time']
                    total_optimized_time += result['optimized_time']
        
        # Overall statistics
        report.append("=" * 80)
        report.append("OVERALL PERFORMANCE SUMMARY")
        report.append("=" * 80)
        
        if total_improvements:
            avg_improvement = sum(total_improvements) / len(total_improvements)
            overall_improvement = ((total_original_time - total_optimized_time) / total_original_time) * 100
            
            report.append(f"Average improvement across all tests: {avg_improvement:.1f}%")
            report.append(f"Overall time improvement: {overall_improvement:.1f}%")
            report.append(f"Total original time: {total_original_time:.6f}s")
            report.append(f"Total optimized time: {total_optimized_time:.6f}s")
            report.append(f"Time saved: {total_original_time - total_optimized_time:.6f}s")
        
        # Performance statistics from optimized detector
        stats = self.optimized_detector.get_performance_stats()
        report.append("")
        report.append("OPTIMIZED DETECTOR STATISTICS:")
        report.append(f"  detect_clusters calls: {stats['detect_clusters_calls']}")
        report.append(f"  find_all_clusters calls: {stats['find_all_clusters_calls']}")
        report.append(f"  Cache hits: {stats['cache_hits']}")
        report.append(f"  Cache misses: {stats['cache_misses']}")
        if stats['cache_hits'] + stats['cache_misses'] > 0:
            cache_hit_rate = (stats['cache_hits'] / (stats['cache_hits'] + stats['cache_misses'])) * 100
            report.append(f"  Cache hit rate: {cache_hit_rate:.1f}%")
        report.append(f"  Total time: {stats['total_time']:.6f}s")
        
        # Recommendations
        report.append("")
        report.append("=" * 80)
        report.append("RECOMMENDATIONS")
        report.append("=" * 80)
        
        if avg_improvement > 20:
            report.append("EXCELLENT: Significant performance improvements achieved!")
            report.append("- The optimized version shows substantial gains")
            report.append("- Consider deploying the optimized version")
        elif avg_improvement > 10:
            report.append("GOOD: Notable performance improvements achieved")
            report.append("- The optimized version shows good gains")
            report.append("- Worth deploying for performance-critical scenarios")
        elif avg_improvement > 0:
            report.append("MINOR: Small performance improvements achieved")
            report.append("- The optimized version shows modest gains")
            report.append("- May be worth deploying for consistency")
        else:
            report.append("NO IMPROVEMENT: Performance is similar or worse")
            report.append("- The optimized version doesn't show significant gains")
            report.append("- Consider investigating optimization strategies")
        
        report.append("")
        report.append("NEXT STEPS:")
        report.append("1. Deploy optimized version if improvements are significant")
        report.append("2. Monitor performance in production")
        report.append("3. Consider additional optimizations if needed")
        report.append("4. Update documentation with performance improvements")
        
        return "\n".join(report)


def main():
    """Main comparison function."""
    print("Starting ClusterDetector Performance Comparison...")
    
    # Create comparator
    comparator = PerformanceComparator(10, 20, 25)
    
    # Generate comprehensive report
    report = comparator.generate_comparison_report()
    
    # Save report
    with open('performance_comparison_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("\n" + report)
    print(f"\nDetailed comparison report saved to: performance_comparison_report.txt")
    
    # Quick summary
    print("\nQUICK SUMMARY:")
    print("Performance comparison completed successfully!")
    print("Check the detailed report for specific improvements.")


if __name__ == "__main__":
    main()
