"""
Performance Benchmarks for State Management
Comprehensive benchmark suite to test optimization systems and measure performance improvements.
"""

import time
import statistics
import threading
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
import json
import os

from .game_state_manager import GameStateManager
from .state_schema import GameState
from modules.logging_module.logger import get_logger


@dataclass
class BenchmarkResult:
    """Results from a single benchmark test."""
    test_name: str
    duration_ms: float
    operations_per_second: float
    memory_usage_mb: float
    cpu_usage_percent: float
    success: bool
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BenchmarkSuite:
    """A collection of related benchmark tests."""
    name: str
    description: str
    tests: List[Callable[[GameStateManager], BenchmarkResult]] = field(default_factory=list)
    iterations: int = 10
    warmup_iterations: int = 3


class PerformanceBenchmarker:
    """
    Comprehensive benchmark suite for testing state management performance.
    """
    
    def __init__(self, output_dir: str = "benchmark_results"):
        self.output_dir = output_dir
        self.logger = get_logger(__name__)
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Benchmark suites
        self.suites: Dict[str, BenchmarkSuite] = {}
        self._register_default_suites()
    
    def _register_default_suites(self) -> None:
        """Register default benchmark suites."""
        
        # Basic state operations
        basic_suite = BenchmarkSuite(
            name="basic_operations",
            description="Basic state get/set operations",
            iterations=20,
            warmup_iterations=5
        )
        basic_suite.tests = [
            self._benchmark_single_set,
            self._benchmark_single_get,
            self._benchmark_multiple_sets,
            self._benchmark_nested_access,
        ]
        self.suites["basic"] = basic_suite
        
        # State change frequency
        frequency_suite = BenchmarkSuite(
            name="state_change_frequency",
            description="High-frequency state changes",
            iterations=15,
            warmup_iterations=3
        )
        frequency_suite.tests = [
            self._benchmark_rapid_changes,
            self._benchmark_batched_changes,
            self._benchmark_concurrent_changes,
        ]
        self.suites["frequency"] = frequency_suite
        
        # Memory usage
        memory_suite = BenchmarkSuite(
            name="memory_usage",
            description="Memory usage patterns",
            iterations=10,
            warmup_iterations=2
        )
        memory_suite.tests = [
            self._benchmark_history_growth,
            self._benchmark_cache_efficiency,
            self._benchmark_snapshot_creation,
        ]
        self.suites["memory"] = memory_suite
        
        # Cache performance
        cache_suite = BenchmarkSuite(
            name="cache_performance",
            description="Cache hit/miss performance",
            iterations=12,
            warmup_iterations=3
        )
        cache_suite.tests = [
            self._benchmark_cache_hits,
            self._benchmark_cache_misses,
            self._benchmark_cache_invalidation,
        ]
        self.suites["cache"] = cache_suite
    
    def run_suite(self, suite_name: str, enable_optimizations: bool = True) -> Dict[str, Any]:
        """Run a specific benchmark suite."""
        if suite_name not in self.suites:
            raise ValueError(f"Unknown benchmark suite: {suite_name}")
        
        suite = self.suites[suite_name]
        self.logger.info(f"Running benchmark suite: {suite.name}")
        
        # Create state manager with/without optimizations
        state_manager = GameStateManager(enable_performance_optimization=enable_optimizations)
        
        results = {
            'suite_name': suite.name,
            'description': suite.description,
            'optimizations_enabled': enable_optimizations,
            'timestamp': time.time(),
            'tests': []
        }
        
        # Run each test
        for test_func in suite.tests:
            test_results = []
            
            # Warmup iterations
            for _ in range(suite.warmup_iterations):
                try:
                    test_func(state_manager)
                except Exception:
                    pass
            
            # Actual benchmark iterations
            for i in range(suite.iterations):
                try:
                    result = test_func(state_manager)
                    test_results.append(result)
                except Exception as e:
                    self.logger.error(f"Test {test_func.__name__} failed: {e}")
                    result = BenchmarkResult(
                        test_name=test_func.__name__,
                        duration_ms=0.0,
                        operations_per_second=0.0,
                        memory_usage_mb=0.0,
                        cpu_usage_percent=0.0,
                        success=False,
                        error_message=str(e)
                    )
                    test_results.append(result)
            
            # Aggregate results
            successful_results = [r for r in test_results if r.success]
            if successful_results:
                aggregated = self._aggregate_results(successful_results)
                aggregated['test_name'] = test_func.__name__
                aggregated['total_iterations'] = len(test_results)
                aggregated['successful_iterations'] = len(successful_results)
                results['tests'].append(aggregated)
            else:
                results['tests'].append({
                    'test_name': test_func.__name__,
                    'success': False,
                    'error': 'All iterations failed'
                })
        
        return results
    
    def run_all_suites(self, enable_optimizations: bool = True) -> Dict[str, Any]:
        """Run all benchmark suites."""
        all_results = {
            'timestamp': time.time(),
            'optimizations_enabled': enable_optimizations,
            'suites': {}
        }
        
        for suite_name in self.suites:
            try:
                suite_results = self.run_suite(suite_name, enable_optimizations)
                all_results['suites'][suite_name] = suite_results
            except Exception as e:
                self.logger.error(f"Suite {suite_name} failed: {e}")
                all_results['suites'][suite_name] = {
                    'error': str(e),
                    'success': False
                }
        
        return all_results
    
    def compare_optimizations(self) -> Dict[str, Any]:
        """Compare performance with and without optimizations."""
        self.logger.info("Running benchmarks with optimizations disabled...")
        without_opt = self.run_all_suites(enable_optimizations=False)
        
        self.logger.info("Running benchmarks with optimizations enabled...")
        with_opt = self.run_all_suites(enable_optimizations=True)
        
        comparison = {
            'timestamp': time.time(),
            'comparison': self._compare_results(without_opt, with_opt)
        }
        
        return comparison
    
    def save_results(self, results: Dict[str, Any], filename: str) -> str:
        """Save benchmark results to file."""
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)
        
        self.logger.info(f"Results saved to: {filepath}")
        return filepath
    
    def _benchmark_single_set(self, state_manager: GameStateManager) -> BenchmarkResult:
        """Benchmark single state set operations."""
        start_time = time.time()
        start_memory = self._get_memory_usage()
        
        operations = 1000
        for i in range(operations):
            state_manager.set(f"test.field_{i}", i, source="benchmark")
        
        end_time = time.time()
        end_memory = self._get_memory_usage()
        
        duration = (end_time - start_time) * 1000
        ops_per_second = operations / (end_time - start_time)
        memory_delta = (end_memory - start_memory) / (1024 * 1024)
        
        return BenchmarkResult(
            test_name="single_set",
            duration_ms=duration,
            operations_per_second=ops_per_second,
            memory_usage_mb=memory_delta,
            cpu_usage_percent=0.0,  # Would need psutil for accurate measurement
            success=True,
            metadata={'operations': operations}
        )
    
    def _benchmark_single_get(self, state_manager: GameStateManager) -> BenchmarkResult:
        """Benchmark single state get operations."""
        # Setup some test data
        for i in range(100):
            state_manager.set(f"test.field_{i}", i, source="benchmark")
        
        start_time = time.time()
        start_memory = self._get_memory_usage()
        
        operations = 1000
        for i in range(operations):
            state_manager.get(f"test.field_{i % 100}")
        
        end_time = time.time()
        end_memory = self._get_memory_usage()
        
        duration = (end_time - start_time) * 1000
        ops_per_second = operations / (end_time - start_time)
        memory_delta = (end_memory - start_memory) / (1024 * 1024)
        
        return BenchmarkResult(
            test_name="single_get",
            duration_ms=duration,
            operations_per_second=ops_per_second,
            memory_usage_mb=memory_delta,
            cpu_usage_percent=0.0,
            success=True,
            metadata={'operations': operations}
        )
    
    def _benchmark_multiple_sets(self, state_manager: GameStateManager) -> BenchmarkResult:
        """Benchmark multiple state sets at once."""
        start_time = time.time()
        start_memory = self._get_memory_usage()
        
        operations = 100
        for i in range(operations):
            updates = {
                f"test.field_{i}_1": i * 1,
                f"test.field_{i}_2": i * 2,
                f"test.field_{i}_3": i * 3,
                f"test.field_{i}_4": i * 4,
                f"test.field_{i}_5": i * 5,
            }
            state_manager.update(updates, source="benchmark")
        
        end_time = time.time()
        end_memory = self._get_memory_usage()
        
        duration = (end_time - start_time) * 1000
        ops_per_second = operations / (end_time - start_time)
        memory_delta = (end_memory - start_memory) / (1024 * 1024)
        
        return BenchmarkResult(
            test_name="multiple_sets",
            duration_ms=duration,
            operations_per_second=ops_per_second,
            memory_usage_mb=memory_delta,
            cpu_usage_percent=0.0,
            success=True,
            metadata={'operations': operations, 'fields_per_operation': 5}
        )
    
    def _benchmark_nested_access(self, state_manager: GameStateManager) -> BenchmarkResult:
        """Benchmark nested state access patterns."""
        # Setup nested data
        state_manager.set("nested.level1.level2.level3", "test_value", source="benchmark")
        
        start_time = time.time()
        start_memory = self._get_memory_usage()
        
        operations = 1000
        for i in range(operations):
            state_manager.get("nested.level1.level2.level3")
        
        end_time = time.time()
        end_memory = self._get_memory_usage()
        
        duration = (end_time - start_time) * 1000
        ops_per_second = operations / (end_time - start_time)
        memory_delta = (end_memory - start_memory) / (1024 * 1024)
        
        return BenchmarkResult(
            test_name="nested_access",
            duration_ms=duration,
            operations_per_second=ops_per_second,
            memory_usage_mb=memory_delta,
            cpu_usage_percent=0.0,
            success=True,
            metadata={'operations': operations, 'nesting_levels': 3}
        )
    
    def _benchmark_rapid_changes(self, state_manager: GameStateManager) -> BenchmarkResult:
        """Benchmark rapid state changes."""
        start_time = time.time()
        start_memory = self._get_memory_usage()
        
        operations = 5000
        for i in range(operations):
            state_manager.set("rapid.field", i, source="benchmark")
        
        end_time = time.time()
        end_memory = self._get_memory_usage()
        
        duration = (end_time - start_time) * 1000
        ops_per_second = operations / (end_time - start_time)
        memory_delta = (end_memory - start_memory) / (1024 * 1024)
        
        return BenchmarkResult(
            test_name="rapid_changes",
            duration_ms=duration,
            operations_per_second=ops_per_second,
            memory_usage_mb=memory_delta,
            cpu_usage_percent=0.0,
            success=True,
            metadata={'operations': operations}
        )
    
    def _benchmark_batched_changes(self, state_manager: GameStateManager) -> BenchmarkResult:
        """Benchmark batched state changes."""
        if not hasattr(state_manager, 'batching_manager'):
            return BenchmarkResult(
                test_name="batched_changes",
                duration_ms=0.0,
                operations_per_second=0.0,
                memory_usage_mb=0.0,
                cpu_usage_percent=0.0,
                success=False,
                error_message="Batching manager not available"
            )
        
        start_time = time.time()
        start_memory = self._get_memory_usage()
        
        operations = 100
        for i in range(operations):
            changes = [
                (f"batch.field_{i}_1", i * 1),
                (f"batch.field_{i}_2", i * 2),
                (f"batch.field_{i}_3", i * 3),
            ]
            state_manager.batching_manager.batch_ui_changes(changes)
        
        # Apply all pending batches
        state_manager.batching_manager.apply_all_pending()
        
        end_time = time.time()
        end_memory = self._get_memory_usage()
        
        duration = (end_time - start_time) * 1000
        ops_per_second = operations / (end_time - start_time)
        memory_delta = (end_memory - start_memory) / (1024 * 1024)
        
        return BenchmarkResult(
            test_name="batched_changes",
            duration_ms=duration,
            operations_per_second=ops_per_second,
            memory_usage_mb=memory_delta,
            cpu_usage_percent=0.0,
            success=True,
            metadata={'operations': operations, 'changes_per_batch': 3}
        )
    
    def _benchmark_concurrent_changes(self, state_manager: GameStateManager) -> BenchmarkResult:
        """Benchmark concurrent state changes."""
        start_time = time.time()
        start_memory = self._get_memory_usage()
        
        def worker(worker_id: int):
            for i in range(100):
                state_manager.set(f"concurrent.worker_{worker_id}.field_{i}", i, source=f"worker_{worker_id}")
        
        # Create multiple threads
        threads = []
        for i in range(4):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        end_memory = self._get_memory_usage()
        
        duration = (end_time - start_time) * 1000
        ops_per_second = 400 / (end_time - start_time)  # 4 workers * 100 operations each
        memory_delta = (end_memory - start_memory) / (1024 * 1024)
        
        return BenchmarkResult(
            test_name="concurrent_changes",
            duration_ms=duration,
            operations_per_second=ops_per_second,
            memory_usage_mb=memory_delta,
            cpu_usage_percent=0.0,
            success=True,
            metadata={'workers': 4, 'operations_per_worker': 100}
        )
    
    def _benchmark_history_growth(self, state_manager: GameStateManager) -> BenchmarkResult:
        """Benchmark state history growth."""
        start_time = time.time()
        start_memory = self._get_memory_usage()
        
        operations = 1000
        for i in range(operations):
            state_manager.set(f"history.field_{i}", i, source="benchmark")
            if i % 100 == 0:
                state_manager.snapshot(f"Snapshot {i}")
        
        end_time = time.time()
        end_memory = self._get_memory_usage()
        
        duration = (end_time - start_time) * 1000
        ops_per_second = operations / (end_time - start_time)
        memory_delta = (end_memory - start_memory) / (1024 * 1024)
        
        return BenchmarkResult(
            test_name="history_growth",
            duration_ms=duration,
            operations_per_second=ops_per_second,
            memory_usage_mb=memory_delta,
            cpu_usage_percent=0.0,
            success=True,
            metadata={'operations': operations, 'snapshots': operations // 100}
        )
    
    def _benchmark_cache_efficiency(self, state_manager: GameStateManager) -> BenchmarkResult:
        """Benchmark cache efficiency."""
        if not hasattr(state_manager, 'cache_manager'):
            return BenchmarkResult(
                test_name="cache_efficiency",
                duration_ms=0.0,
                operations_per_second=0.0,
                memory_usage_mb=0.0,
                cpu_usage_percent=0.0,
                success=False,
                error_message="Cache manager not available"
            )
        
        # Setup some data
        for i in range(100):
            state_manager.set(f"cache.field_{i}", i, source="benchmark")
        
        start_time = time.time()
        start_memory = self._get_memory_usage()
        
        operations = 1000
        for i in range(operations):
            state_manager.get_state_summary()  # This should use cache
        
        end_time = time.time()
        end_memory = self._get_memory_usage()
        
        duration = (end_time - start_time) * 1000
        ops_per_second = operations / (end_time - start_time)
        memory_delta = (end_memory - start_memory) / (1024 * 1024)
        
        cache_stats = state_manager.cache_manager.get_cache_stats()
        
        return BenchmarkResult(
            test_name="cache_efficiency",
            duration_ms=duration,
            operations_per_second=ops_per_second,
            memory_usage_mb=memory_delta,
            cpu_usage_percent=0.0,
            success=True,
            metadata={
                'operations': operations,
                'cache_hit_rate': cache_stats.get('hit_rate_percent', 0),
                'cache_entries': cache_stats.get('total_entries', 0)
            }
        )
    
    def _benchmark_snapshot_creation(self, state_manager: GameStateManager) -> BenchmarkResult:
        """Benchmark snapshot creation performance."""
        # Setup some data
        for i in range(500):
            state_manager.set(f"snapshot.field_{i}", i, source="benchmark")
        
        start_time = time.time()
        start_memory = self._get_memory_usage()
        
        operations = 50
        for i in range(operations):
            state_manager.snapshot(f"Benchmark snapshot {i}")
        
        end_time = time.time()
        end_memory = self._get_memory_usage()
        
        duration = (end_time - start_time) * 1000
        ops_per_second = operations / (end_time - start_time)
        memory_delta = (end_memory - start_memory) / (1024 * 1024)
        
        return BenchmarkResult(
            test_name="snapshot_creation",
            duration_ms=duration,
            operations_per_second=ops_per_second,
            memory_usage_mb=memory_delta,
            cpu_usage_percent=0.0,
            success=True,
            metadata={'operations': operations, 'state_fields': 500}
        )
    
    def _benchmark_cache_hits(self, state_manager: GameStateManager) -> BenchmarkResult:
        """Benchmark cache hit performance."""
        if not hasattr(state_manager, 'cache_manager'):
            return BenchmarkResult(
                test_name="cache_hits",
                duration_ms=0.0,
                operations_per_second=0.0,
                memory_usage_mb=0.0,
                cpu_usage_percent=0.0,
                success=False,
                error_message="Cache manager not available"
            )
        
        # Prime the cache
        state_manager.get_state_summary()
        
        start_time = time.time()
        start_memory = self._get_memory_usage()
        
        operations = 2000
        for i in range(operations):
            state_manager.get_state_summary()
        
        end_time = time.time()
        end_memory = self._get_memory_usage()
        
        duration = (end_time - start_time) * 1000
        ops_per_second = operations / (end_time - start_time)
        memory_delta = (end_memory - start_memory) / (1024 * 1024)
        
        return BenchmarkResult(
            test_name="cache_hits",
            duration_ms=duration,
            operations_per_second=ops_per_second,
            memory_usage_mb=memory_delta,
            cpu_usage_percent=0.0,
            success=True,
            metadata={'operations': operations, 'expected_cache_hits': operations}
        )
    
    def _benchmark_cache_misses(self, state_manager: GameStateManager) -> BenchmarkResult:
        """Benchmark cache miss performance."""
        if not hasattr(state_manager, 'cache_manager'):
            return BenchmarkResult(
                test_name="cache_misses",
                duration_ms=0.0,
                operations_per_second=0.0,
                memory_usage_mb=0.0,
                cpu_usage_percent=0.0,
                success=False,
                error_message="Cache manager not available"
            )
        
        start_time = time.time()
        start_memory = self._get_memory_usage()
        
        operations = 1000
        for i in range(operations):
            # Invalidate cache by changing state
            state_manager.set(f"cache_miss.field_{i}", i, source="benchmark")
            state_manager.get_state_summary()
        
        end_time = time.time()
        end_memory = self._get_memory_usage()
        
        duration = (end_time - start_time) * 1000
        ops_per_second = operations / (end_time - start_time)
        memory_delta = (end_memory - start_memory) / (1024 * 1024)
        
        return BenchmarkResult(
            test_name="cache_misses",
            duration_ms=duration,
            operations_per_second=ops_per_second,
            memory_usage_mb=memory_delta,
            cpu_usage_percent=0.0,
            success=True,
            metadata={'operations': operations, 'expected_cache_misses': operations}
        )
    
    def _benchmark_cache_invalidation(self, state_manager: GameStateManager) -> BenchmarkResult:
        """Benchmark cache invalidation performance."""
        if not hasattr(state_manager, 'cache_manager'):
            return BenchmarkResult(
                test_name="cache_invalidation",
                duration_ms=0.0,
                operations_per_second=0.0,
                memory_usage_mb=0.0,
                cpu_usage_percent=0.0,
                success=False,
                error_message="Cache manager not available"
            )
        
        # Prime the cache
        state_manager.get_state_summary()
        
        start_time = time.time()
        start_memory = self._get_memory_usage()
        
        operations = 500
        for i in range(operations):
            # Invalidate cache
            state_manager.cache_manager.invalidate_pattern("game_state_summary")
            state_manager.get_state_summary()
        
        end_time = time.time()
        end_memory = self._get_memory_usage()
        
        duration = (end_time - start_time) * 1000
        ops_per_second = operations / (end_time - start_time)
        memory_delta = (end_memory - start_memory) / (1024 * 1024)
        
        return BenchmarkResult(
            test_name="cache_invalidation",
            duration_ms=duration,
            operations_per_second=ops_per_second,
            memory_usage_mb=memory_delta,
            cpu_usage_percent=0.0,
            success=True,
            metadata={'operations': operations}
        )
    
    def _aggregate_results(self, results: List[BenchmarkResult]) -> Dict[str, Any]:
        """Aggregate multiple benchmark results."""
        durations = [r.duration_ms for r in results]
        ops_per_sec = [r.operations_per_second for r in results]
        memory_usage = [r.memory_usage_mb for r in results]
        
        return {
            'duration_ms': {
                'mean': statistics.mean(durations),
                'median': statistics.median(durations),
                'min': min(durations),
                'max': max(durations),
                'stdev': statistics.stdev(durations) if len(durations) > 1 else 0
            },
            'operations_per_second': {
                'mean': statistics.mean(ops_per_sec),
                'median': statistics.median(ops_per_sec),
                'min': min(ops_per_sec),
                'max': max(ops_per_sec),
                'stdev': statistics.stdev(ops_per_sec) if len(ops_per_sec) > 1 else 0
            },
            'memory_usage_mb': {
                'mean': statistics.mean(memory_usage),
                'median': statistics.median(memory_usage),
                'min': min(memory_usage),
                'max': max(memory_usage),
                'stdev': statistics.stdev(memory_usage) if len(memory_usage) > 1 else 0
            },
            'success': True
        }
    
    def _compare_results(self, without_opt: Dict[str, Any], with_opt: Dict[str, Any]) -> Dict[str, Any]:
        """Compare results with and without optimizations."""
        comparison = {}
        
        for suite_name in without_opt.get('suites', {}):
            if suite_name not in with_opt.get('suites', {}):
                continue
            
            without_suite = without_opt['suites'][suite_name]
            with_suite = with_opt['suites'][suite_name]
            
            if 'tests' not in without_suite or 'tests' not in with_suite:
                continue
            
            suite_comparison = []
            
            for without_test in without_suite['tests']:
                test_name = without_test.get('test_name')
                with_test = next((t for t in with_suite['tests'] if t.get('test_name') == test_name), None)
                
                if with_test and 'duration_ms' in without_test and 'duration_ms' in with_test:
                    without_duration = without_test['duration_ms']['mean']
                    with_duration = with_test['duration_ms']['mean']
                    
                    improvement = ((without_duration - with_duration) / without_duration) * 100
                    
                    suite_comparison.append({
                        'test_name': test_name,
                        'without_optimization_ms': without_duration,
                        'with_optimization_ms': with_duration,
                        'improvement_percent': improvement,
                        'faster': improvement > 0
                    })
            
            comparison[suite_name] = suite_comparison
        
        return comparison
    
    def _get_memory_usage(self) -> int:
        """Get current memory usage in bytes."""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss
        except ImportError:
            return 0


# Convenience functions
def run_quick_benchmark() -> Dict[str, Any]:
    """Run a quick benchmark to test basic functionality."""
    benchmarker = PerformanceBenchmarker()
    return benchmarker.run_suite("basic", enable_optimizations=True)


def run_full_benchmark() -> Dict[str, Any]:
    """Run a full benchmark suite."""
    benchmarker = PerformanceBenchmarker()
    return benchmarker.run_all_suites(enable_optimizations=True)


def compare_optimization_performance() -> Dict[str, Any]:
    """Compare performance with and without optimizations."""
    benchmarker = PerformanceBenchmarker()
    return benchmarker.compare_optimizations() 