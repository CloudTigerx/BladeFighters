"""
Round 2 Performance Optimization Benchmarks
Comprehensive benchmark suite for Round 2 performance optimization framework.
"""

import time
import statistics
import threading
import gc
import psutil
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
import json
import os

from .game_state_manager import GameStateManager
from .performance_profiler import get_performance_profiler
from modules.logging_module.logger import get_logger


@dataclass
class Round2BenchmarkResult:
    """Results from Round 2 benchmark tests."""
    test_name: str
    category: str
    baseline_metrics: Dict[str, Any]
    optimized_metrics: Dict[str, Any]
    improvement_percent: float
    regression_percent: float
    passed_targets: bool
    recommendations: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceTarget:
    """Performance targets for Round 2 optimization."""
    name: str
    target_value: float
    unit: str
    threshold: float  # Maximum acceptable value
    critical: bool = False  # Whether this is a critical target


class Round2PerformanceBenchmarker:
    """
    Comprehensive benchmark suite for Round 2 performance optimization.
    Implements all critical performance areas and coordination requirements.
    """
    
    def __init__(self, output_dir: str = "round2_benchmark_results"):
        self.output_dir = output_dir
        self.logger = get_logger(__name__)
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Performance targets for Round 2
        self.performance_targets = self._define_performance_targets()
        
        # Benchmark categories
        self.benchmark_categories = {
            'state_operations': self._benchmark_state_operations,
            'memory_usage': self._benchmark_memory_usage,
            'cross_module_communication': self._benchmark_cross_module_communication,
            'frame_rate_impact': self._benchmark_frame_rate_impact,
            'system_performance': self._benchmark_system_performance
        }
        
        # Baseline metrics
        self.baseline_metrics = {}
        
    def _define_performance_targets(self) -> Dict[str, PerformanceTarget]:
        """Define performance targets for Round 2 optimization."""
        return {
            'fps_minimum': PerformanceTarget(
                name="Minimum FPS",
                target_value=55.0,
                unit="FPS",
                threshold=55.0,
                critical=True
            ),
            'fps_target': PerformanceTarget(
                name="Target FPS",
                target_value=60.0,
                unit="FPS",
                threshold=60.0,
                critical=True
            ),
            'memory_additional': PerformanceTarget(
                name="Additional Memory Usage",
                target_value=50.0,
                unit="MB",
                threshold=50.0,
                critical=True
            ),
            'state_operation_latency': PerformanceTarget(
                name="State Operation Latency",
                target_value=10.0,
                unit="ms",
                threshold=10.0,
                critical=True
            ),
            'cross_module_latency': PerformanceTarget(
                name="Cross-Module Communication Latency",
                target_value=5.0,
                unit="ms",
                threshold=5.0,
                critical=False
            ),
            'event_processing_latency': PerformanceTarget(
                name="Event Processing Latency",
                target_value=2.0,
                unit="ms",
                threshold=2.0,
                critical=False
            ),
            'cache_operation_latency': PerformanceTarget(
                name="Cache Operation Latency",
                target_value=1.0,
                unit="ms",
                threshold=1.0,
                critical=False
            ),
            'performance_regression': PerformanceTarget(
                name="Performance Regression",
                target_value=5.0,
                unit="%",
                threshold=5.0,
                critical=True
            )
        }
    
    def establish_baseline(self) -> Dict[str, Any]:
        """Establish baseline performance metrics."""
        self.logger.info("Establishing performance baseline...")
        
        # Create baseline state manager without optimizations
        baseline_manager = GameStateManager(enable_performance_optimization=False)
        
        # Run baseline tests
        baseline_metrics = {}
        
        # State operations baseline
        baseline_metrics['state_operations'] = self._measure_baseline_state_operations(baseline_manager)
        
        # Memory usage baseline
        baseline_metrics['memory_usage'] = self._measure_baseline_memory_usage(baseline_manager)
        
        # Cross-module communication baseline
        baseline_metrics['cross_module_communication'] = self._measure_baseline_communication(baseline_manager)
        
        # Frame rate baseline
        baseline_metrics['frame_rate'] = self._measure_baseline_frame_rate(baseline_manager)
        
        # System performance baseline
        baseline_metrics['system_performance'] = self._measure_baseline_system_performance(baseline_manager)
        
        self.baseline_metrics = baseline_metrics
        
        self.logger.info("Baseline established successfully")
        return baseline_metrics
    
    def run_round2_benchmarks(self) -> Dict[str, Round2BenchmarkResult]:
        """Run comprehensive Round 2 benchmarks."""
        self.logger.info("Starting Round 2 performance benchmarks...")
        
        # Ensure baseline is established
        if not self.baseline_metrics:
            self.establish_baseline()
        
        # Create optimized state manager
        optimized_manager = GameStateManager(enable_performance_optimization=True)
        
        results = {}
        
        # Run all benchmark categories
        for category_name, benchmark_func in self.benchmark_categories.items():
            try:
                self.logger.info(f"Running {category_name} benchmarks...")
                result = benchmark_func(optimized_manager)
                results[category_name] = result
            except Exception as e:
                self.logger.error(f"Error in {category_name} benchmark: {e}")
                results[category_name] = Round2BenchmarkResult(
                    test_name=category_name,
                    category=category_name,
                    baseline_metrics={},
                    optimized_metrics={},
                    improvement_percent=0.0,
                    regression_percent=0.0,
                    passed_targets=False,
                    recommendations=[f"Benchmark failed: {e}"]
                )
        
        return results
    
    def _benchmark_state_operations(self, optimized_manager: GameStateManager) -> Round2BenchmarkResult:
        """Benchmark state operation latency and throughput."""
        
        # Baseline metrics
        baseline = self.baseline_metrics['state_operations']
        
        # Optimized metrics
        optimized = self._measure_optimized_state_operations(optimized_manager)
        
        # Calculate improvements/regressions
        improvements = {}
        regressions = {}
        
        for metric in ['single_set_latency', 'single_get_latency', 'batch_latency', 'throughput']:
            if metric in baseline and metric in optimized:
                baseline_val = baseline[metric]
                optimized_val = optimized[metric]
                
                if baseline_val > 0:
                    if metric == 'latency':
                        # Lower is better for latency
                        improvement = ((baseline_val - optimized_val) / baseline_val) * 100
                        if improvement > 0:
                            improvements[metric] = improvement
                        else:
                            regressions[metric] = abs(improvement)
                    else:
                        # Higher is better for throughput
                        improvement = ((optimized_val - baseline_val) / baseline_val) * 100
                        if improvement > 0:
                            improvements[metric] = improvement
                        else:
                            regressions[metric] = abs(improvement)
        
        # Check if targets are met
        passed_targets = self._check_state_operation_targets(optimized)
        
        # Generate recommendations
        recommendations = self._generate_state_operation_recommendations(optimized, improvements, regressions)
        
        return Round2BenchmarkResult(
            test_name="State Operations Benchmark",
            category="state_operations",
            baseline_metrics=baseline,
            optimized_metrics=optimized,
            improvement_percent=statistics.mean(improvements.values()) if improvements else 0.0,
            regression_percent=statistics.mean(regressions.values()) if regressions else 0.0,
            passed_targets=passed_targets,
            recommendations=recommendations
        )
    
    def _benchmark_memory_usage(self, optimized_manager: GameStateManager) -> Round2BenchmarkResult:
        """Benchmark memory usage per module integration."""
        
        # Baseline metrics
        baseline = self.baseline_metrics['memory_usage']
        
        # Optimized metrics
        optimized = self._measure_optimized_memory_usage(optimized_manager)
        
        # Calculate memory impact
        memory_impact = {}
        for module in ['audio', 'screen', 'settings', 'puzzle']:
            if f'{module}_memory' in baseline and f'{module}_memory' in optimized:
                baseline_memory = baseline[f'{module}_memory']
                optimized_memory = optimized[f'{module}_memory']
                memory_impact[module] = optimized_memory - baseline_memory
        
        # Check if targets are met
        passed_targets = self._check_memory_targets(optimized)
        
        # Generate recommendations
        recommendations = self._generate_memory_recommendations(optimized, memory_impact)
        
        return Round2BenchmarkResult(
            test_name="Memory Usage Benchmark",
            category="memory_usage",
            baseline_metrics=baseline,
            optimized_metrics=optimized,
            improvement_percent=0.0,  # Memory is about staying under limits
            regression_percent=statistics.mean(memory_impact.values()) if memory_impact else 0.0,
            passed_targets=passed_targets,
            recommendations=recommendations
        )
    
    def _benchmark_cross_module_communication(self, optimized_manager: GameStateManager) -> Round2BenchmarkResult:
        """Benchmark cross-module communication overhead."""
        
        # Baseline metrics
        baseline = self.baseline_metrics['cross_module_communication']
        
        # Optimized metrics
        optimized = self._measure_optimized_communication(optimized_manager)
        
        # Calculate improvements
        improvements = {}
        for metric in ['event_processing_latency', 'data_transfer_latency', 'cross_module_latency']:
            if metric in baseline and metric in optimized:
                baseline_val = baseline[metric]
                optimized_val = optimized[metric]
                
                if baseline_val > 0:
                    improvement = ((baseline_val - optimized_val) / baseline_val) * 100
                    if improvement > 0:
                        improvements[metric] = improvement
        
        # Check if targets are met
        passed_targets = self._check_communication_targets(optimized)
        
        # Generate recommendations
        recommendations = self._generate_communication_recommendations(optimized, improvements)
        
        return Round2BenchmarkResult(
            test_name="Cross-Module Communication Benchmark",
            category="cross_module_communication",
            baseline_metrics=baseline,
            optimized_metrics=optimized,
            improvement_percent=statistics.mean(improvements.values()) if improvements else 0.0,
            regression_percent=0.0,
            passed_targets=passed_targets,
            recommendations=recommendations
        )
    
    def _benchmark_frame_rate_impact(self, optimized_manager: GameStateManager) -> Round2BenchmarkResult:
        """Benchmark frame rate impact during state-heavy operations."""
        
        # Baseline metrics
        baseline = self.baseline_metrics['frame_rate']
        
        # Optimized metrics
        optimized = self._measure_optimized_frame_rate(optimized_manager)
        
        # Calculate FPS improvements
        fps_improvement = 0.0
        if 'average_fps' in baseline and 'average_fps' in optimized:
            baseline_fps = baseline['average_fps']
            optimized_fps = optimized['average_fps']
            
            if baseline_fps > 0:
                fps_improvement = ((optimized_fps - baseline_fps) / baseline_fps) * 100
        
        # Check if targets are met
        passed_targets = self._check_frame_rate_targets(optimized)
        
        # Generate recommendations
        recommendations = self._generate_frame_rate_recommendations(optimized, fps_improvement)
        
        return Round2BenchmarkResult(
            test_name="Frame Rate Impact Benchmark",
            category="frame_rate_impact",
            baseline_metrics=baseline,
            optimized_metrics=optimized,
            improvement_percent=fps_improvement,
            regression_percent=0.0,
            passed_targets=passed_targets,
            recommendations=recommendations
        )
    
    def _benchmark_system_performance(self, optimized_manager: GameStateManager) -> Round2BenchmarkResult:
        """Benchmark overall system performance impact."""
        
        # Baseline metrics
        baseline = self.baseline_metrics['system_performance']
        
        # Optimized metrics
        optimized = self._measure_optimized_system_performance(optimized_manager)
        
        # Calculate overall impact
        performance_impact = {}
        for metric in ['cpu_usage', 'memory_usage', 'response_time']:
            if metric in baseline and metric in optimized:
                baseline_val = baseline[metric]
                optimized_val = optimized[metric]
                
                if baseline_val > 0:
                    impact = ((optimized_val - baseline_val) / baseline_val) * 100
                    performance_impact[metric] = impact
        
        # Check if targets are met
        passed_targets = self._check_system_performance_targets(optimized)
        
        # Generate recommendations
        recommendations = self._generate_system_performance_recommendations(optimized, performance_impact)
        
        return Round2BenchmarkResult(
            test_name="System Performance Benchmark",
            category="system_performance",
            baseline_metrics=baseline,
            optimized_metrics=optimized,
            improvement_percent=0.0,
            regression_percent=statistics.mean([abs(v) for v in performance_impact.values()]) if performance_impact else 0.0,
            passed_targets=passed_targets,
            recommendations=recommendations
        )
    
    def _measure_baseline_state_operations(self, manager: GameStateManager) -> Dict[str, Any]:
        """Measure baseline state operation performance."""
        results = {}
        
        # Single set operations
        operations = 1000
        start_time = time.time()
        for i in range(operations):
            manager.set(f"baseline.field_{i}", i, source="benchmark")
        set_time = (time.time() - start_time) * 1000
        results['single_set_latency'] = set_time / operations
        
        # Single get operations
        start_time = time.time()
        for i in range(operations):
            manager.get(f"baseline.field_{i}")
        get_time = (time.time() - start_time) * 1000
        results['single_get_latency'] = get_time / operations
        
        # Batch operations
        batch_size = 50
        batches = operations // batch_size
        start_time = time.time()
        for i in range(batches):
            updates = {f"baseline.batch_{i}_{j}": j for j in range(batch_size)}
            manager.update(updates, source="benchmark")
        batch_time = (time.time() - start_time) * 1000
        results['batch_latency'] = batch_time / operations
        
        # Throughput
        results['throughput'] = operations / (set_time / 1000)
        
        return results
    
    def _measure_optimized_state_operations(self, manager: GameStateManager) -> Dict[str, Any]:
        """Measure optimized state operation performance."""
        results = {}
        
        # Single set operations
        operations = 1000
        start_time = time.time()
        for i in range(operations):
            manager.set(f"optimized.field_{i}", i, source="benchmark")
        set_time = (time.time() - start_time) * 1000
        results['single_set_latency'] = set_time / operations
        
        # Single get operations
        start_time = time.time()
        for i in range(operations):
            manager.get(f"optimized.field_{i}")
        get_time = (time.time() - start_time) * 1000
        results['single_get_latency'] = get_time / operations
        
        # Batch operations using batching manager
        if hasattr(manager, 'batching_manager'):
            batch_size = 50
            batches = operations // batch_size
            start_time = time.time()
            for i in range(batches):
                changes = [(f"optimized.batch_{i}_{j}", j) for j in range(batch_size)]
                manager.batching_manager.batch_ui_changes(changes)
            manager.batching_manager.apply_all_pending()
            batch_time = (time.time() - start_time) * 1000
            results['batch_latency'] = batch_time / operations
        else:
            results['batch_latency'] = results['single_set_latency']
        
        # Throughput
        results['throughput'] = operations / (set_time / 1000)
        
        return results
    
    def _measure_baseline_memory_usage(self, manager: GameStateManager) -> Dict[str, Any]:
        """Measure baseline memory usage."""
        results = {}
        
        # Initial memory
        initial_memory = self._get_memory_usage()
        
        # Simulate module operations
        modules = ['audio', 'screen', 'settings', 'puzzle']
        for module in modules:
            # Simulate module integration
            for i in range(100):
                manager.set(f"{module}.field_{i}", i, source="benchmark")
            
            # Measure memory after module operations
            current_memory = self._get_memory_usage()
            results[f'{module}_memory'] = current_memory - initial_memory
        
        return results
    
    def _measure_optimized_memory_usage(self, manager: GameStateManager) -> Dict[str, Any]:
        """Measure optimized memory usage."""
        results = {}
        
        # Initial memory
        initial_memory = self._get_memory_usage()
        
        # Simulate module operations with optimizations
        modules = ['audio', 'screen', 'settings', 'puzzle']
        for module in modules:
            # Simulate module integration with batching
            if hasattr(manager, 'batching_manager'):
                changes = [(f"{module}.field_{i}", i) for i in range(100)]
                manager.batching_manager.batch_ui_changes(changes)
                manager.batching_manager.apply_all_pending()
            else:
                for i in range(100):
                    manager.set(f"{module}.field_{i}", i, source="benchmark")
            
            # Measure memory after module operations
            current_memory = self._get_memory_usage()
            results[f'{module}_memory'] = current_memory - initial_memory
        
        return results
    
    def _measure_baseline_communication(self, manager: GameStateManager) -> Dict[str, Any]:
        """Measure baseline cross-module communication."""
        results = {}
        
        # Simulate cross-module communication
        communications = 100
        
        # Event processing
        start_time = time.time()
        for i in range(communications):
            # Simulate event processing
            manager.set("communication.event", i, source="benchmark")
        event_time = (time.time() - start_time) * 1000
        results['event_processing_latency'] = event_time / communications
        
        # Data transfer
        start_time = time.time()
        for i in range(communications):
            # Simulate data transfer
            data = {"module": "test", "data": "x" * 1024}  # 1KB data
            manager.set("communication.data", data, source="benchmark")
        transfer_time = (time.time() - start_time) * 1000
        results['data_transfer_latency'] = transfer_time / communications
        
        # Cross-module calls
        start_time = time.time()
        for i in range(communications):
            # Simulate cross-module call
            manager.get("communication.call")
        call_time = (time.time() - start_time) * 1000
        results['cross_module_latency'] = call_time / communications
        
        return results
    
    def _measure_optimized_communication(self, manager: GameStateManager) -> Dict[str, Any]:
        """Measure optimized cross-module communication."""
        results = {}
        
        # Simulate optimized cross-module communication
        communications = 100
        
        # Event processing with caching
        start_time = time.time()
        for i in range(communications):
            # Use cached state summary
            summary = manager.get_state_summary()
        event_time = (time.time() - start_time) * 1000
        results['event_processing_latency'] = event_time / communications
        
        # Data transfer with batching
        if hasattr(manager, 'batching_manager'):
            start_time = time.time()
            changes = []
            for i in range(communications):
                data = {"module": "test", "data": "x" * 1024}  # 1KB data
                changes.append(("communication.data", data))
            manager.batching_manager.batch_ui_changes(changes)
            manager.batching_manager.apply_all_pending()
            transfer_time = (time.time() - start_time) * 1000
            results['data_transfer_latency'] = transfer_time / communications
        else:
            results['data_transfer_latency'] = results['event_processing_latency']
        
        # Cross-module calls with optimization
        start_time = time.time()
        for i in range(communications):
            # Use optimized get with caching
            manager.get("communication.call")
        call_time = (time.time() - start_time) * 1000
        results['cross_module_latency'] = call_time / communications
        
        return results
    
    def _measure_baseline_frame_rate(self, manager: GameStateManager) -> Dict[str, Any]:
        """Measure baseline frame rate during state-heavy operations."""
        results = {}
        
        # Simulate frame rate measurement
        frames = 60
        frame_times = []
        
        for i in range(frames):
            start_time = time.time()
            
            # Simulate state-heavy frame
            for j in range(10):  # 10 state changes per frame
                manager.set(f"frame.{i}.{j}", j, source="benchmark")
            
            frame_time = (time.time() - start_time) * 1000
            frame_times.append(frame_time)
        
        results['average_fps'] = 1000 / statistics.mean(frame_times)
        results['min_fps'] = 1000 / max(frame_times)
        results['max_fps'] = 1000 / min(frame_times)
        results['frame_time_variance'] = statistics.stdev(frame_times)
        
        return results
    
    def _measure_optimized_frame_rate(self, manager: GameStateManager) -> Dict[str, Any]:
        """Measure optimized frame rate during state-heavy operations."""
        results = {}
        
        # Simulate frame rate measurement with optimizations
        frames = 60
        frame_times = []
        
        for i in range(frames):
            start_time = time.time()
            
            # Simulate state-heavy frame with batching
            if hasattr(manager, 'batching_manager'):
                changes = [(f"frame.{i}.{j}", j) for j in range(10)]
                manager.batching_manager.batch_ui_changes(changes)
                manager.batching_manager.apply_all_pending()
            else:
                for j in range(10):  # 10 state changes per frame
                    manager.set(f"frame.{i}.{j}", j, source="benchmark")
            
            frame_time = (time.time() - start_time) * 1000
            frame_times.append(frame_time)
        
        results['average_fps'] = 1000 / statistics.mean(frame_times)
        results['min_fps'] = 1000 / max(frame_times)
        results['max_fps'] = 1000 / min(frame_times)
        results['frame_time_variance'] = statistics.stdev(frame_times)
        
        return results
    
    def _measure_baseline_system_performance(self, manager: GameStateManager) -> Dict[str, Any]:
        """Measure baseline system performance."""
        results = {}
        
        # CPU usage
        cpu_start = psutil.cpu_percent(interval=1)
        
        # Memory usage
        memory_start = self._get_memory_usage()
        
        # Simulate intensive operations
        for i in range(1000):
            manager.set(f"system.{i}", i, source="benchmark")
        
        # CPU usage after
        cpu_end = psutil.cpu_percent(interval=1)
        
        # Memory usage after
        memory_end = self._get_memory_usage()
        
        results['cpu_usage'] = (cpu_start + cpu_end) / 2
        results['memory_usage'] = (memory_end - memory_start) / (1024 * 1024)  # MB
        results['response_time'] = 0.0  # Will be measured in specific tests
        
        return results
    
    def _measure_optimized_system_performance(self, manager: GameStateManager) -> Dict[str, Any]:
        """Measure optimized system performance."""
        results = {}
        
        # CPU usage
        cpu_start = psutil.cpu_percent(interval=1)
        
        # Memory usage
        memory_start = self._get_memory_usage()
        
        # Simulate intensive operations with optimizations
        if hasattr(manager, 'batching_manager'):
            changes = [(f"system.{i}", i) for i in range(1000)]
            manager.batching_manager.batch_ui_changes(changes)
            manager.batching_manager.apply_all_pending()
        else:
            for i in range(1000):
                manager.set(f"system.{i}", i, source="benchmark")
        
        # CPU usage after
        cpu_end = psutil.cpu_percent(interval=1)
        
        # Memory usage after
        memory_end = self._get_memory_usage()
        
        results['cpu_usage'] = (cpu_start + cpu_end) / 2
        results['memory_usage'] = (memory_end - memory_start) / (1024 * 1024)  # MB
        results['response_time'] = 0.0  # Will be measured in specific tests
        
        return results
    
    def _check_state_operation_targets(self, metrics: Dict[str, Any]) -> bool:
        """Check if state operation targets are met."""
        targets = [
            ('single_set_latency', 10.0),  # 10ms target
            ('single_get_latency', 1.0),   # 1ms target
            ('batch_latency', 5.0),        # 5ms target
        ]
        
        for metric, target in targets:
            if metric in metrics and metrics[metric] > target:
                return False
        
        return True
    
    def _check_memory_targets(self, metrics: Dict[str, Any]) -> bool:
        """Check if memory targets are met."""
        total_memory = sum(metrics.get(f'{module}_memory', 0) for module in ['audio', 'screen', 'settings', 'puzzle'])
        return total_memory <= 50.0  # 50MB target
    
    def _check_communication_targets(self, metrics: Dict[str, Any]) -> bool:
        """Check if communication targets are met."""
        targets = [
            ('event_processing_latency', 2.0),  # 2ms target
            ('cross_module_latency', 5.0),      # 5ms target
        ]
        
        for metric, target in targets:
            if metric in metrics and metrics[metric] > target:
                return False
        
        return True
    
    def _check_frame_rate_targets(self, metrics: Dict[str, Any]) -> bool:
        """Check if frame rate targets are met."""
        if 'average_fps' in metrics:
            return metrics['average_fps'] >= 55.0  # 55 FPS minimum
        return False
    
    def _check_system_performance_targets(self, metrics: Dict[str, Any]) -> bool:
        """Check if system performance targets are met."""
        if 'memory_usage' in metrics:
            return metrics['memory_usage'] <= 50.0  # 50MB additional memory
        return True
    
    def _generate_state_operation_recommendations(self, metrics: Dict[str, Any], improvements: Dict[str, float], regressions: Dict[str, float]) -> List[str]:
        """Generate recommendations for state operations."""
        recommendations = []
        
        if improvements:
            recommendations.append(f"State operations improved by {statistics.mean(improvements.values()):.1f}% on average")
        
        if regressions:
            recommendations.append(f"State operations regressed by {statistics.mean(regressions.values()):.1f}% on average - needs optimization")
        
        if 'single_set_latency' in metrics and metrics['single_set_latency'] > 10.0:
            recommendations.append("Single set latency exceeds 10ms target - consider batching")
        
        if 'batch_latency' in metrics and metrics['batch_latency'] > 5.0:
            recommendations.append("Batch latency exceeds 5ms target - optimize batching strategy")
        
        return recommendations
    
    def _generate_memory_recommendations(self, metrics: Dict[str, Any], memory_impact: Dict[str, float]) -> List[str]:
        """Generate recommendations for memory usage."""
        recommendations = []
        
        total_memory = sum(memory_impact.values())
        if total_memory > 50.0:
            recommendations.append(f"Total memory impact {total_memory:.1f}MB exceeds 50MB target")
        
        for module, impact in memory_impact.items():
            if impact > 10.0:
                recommendations.append(f"{module} module memory impact {impact:.1f}MB exceeds 10MB target")
        
        if not recommendations:
            recommendations.append("Memory usage within acceptable limits")
        
        return recommendations
    
    def _generate_communication_recommendations(self, metrics: Dict[str, Any], improvements: Dict[str, float]) -> List[str]:
        """Generate recommendations for communication."""
        recommendations = []
        
        if improvements:
            recommendations.append(f"Communication improved by {statistics.mean(improvements.values()):.1f}% on average")
        
        if 'event_processing_latency' in metrics and metrics['event_processing_latency'] > 2.0:
            recommendations.append("Event processing latency exceeds 2ms target")
        
        if 'cross_module_latency' in metrics and metrics['cross_module_latency'] > 5.0:
            recommendations.append("Cross-module latency exceeds 5ms target")
        
        return recommendations
    
    def _generate_frame_rate_recommendations(self, metrics: Dict[str, Any], fps_improvement: float) -> List[str]:
        """Generate recommendations for frame rate."""
        recommendations = []
        
        if fps_improvement > 0:
            recommendations.append(f"Frame rate improved by {fps_improvement:.1f}%")
        elif fps_improvement < 0:
            recommendations.append(f"Frame rate regressed by {abs(fps_improvement):.1f}% - needs optimization")
        
        if 'average_fps' in metrics:
            if metrics['average_fps'] < 55.0:
                recommendations.append("Average FPS below 55 FPS minimum target")
            elif metrics['average_fps'] >= 60.0:
                recommendations.append("Frame rate target achieved")
        
        return recommendations
    
    def _generate_system_performance_recommendations(self, metrics: Dict[str, Any], performance_impact: Dict[str, float]) -> List[str]:
        """Generate recommendations for system performance."""
        recommendations = []
        
        if 'memory_usage' in metrics and metrics['memory_usage'] > 50.0:
            recommendations.append(f"Memory usage {metrics['memory_usage']:.1f}MB exceeds 50MB target")
        
        if 'cpu_usage' in metrics and metrics['cpu_usage'] > 80.0:
            recommendations.append(f"CPU usage {metrics['cpu_usage']:.1f}% exceeds 80% threshold")
        
        if not recommendations:
            recommendations.append("System performance within acceptable limits")
        
        return recommendations
    
    def _get_memory_usage(self) -> int:
        """Get current memory usage in bytes."""
        try:
            process = psutil.Process()
            return process.memory_info().rss
        except Exception:
            return 0
    
    def generate_round2_report(self, results: Dict[str, Round2BenchmarkResult]) -> Dict[str, Any]:
        """Generate comprehensive Round 2 performance report."""
        report = {
            'timestamp': time.time(),
            'framework_version': '1.0',
            'baseline_metrics': self.baseline_metrics,
            'benchmark_results': {},
            'summary': {
                'total_tests': len(results),
                'passed_targets': sum(1 for r in results.values() if r.passed_targets),
                'failed_targets': sum(1 for r in results.values() if not r.passed_targets),
                'average_improvement': 0.0,
                'average_regression': 0.0
            },
            'recommendations': []
        }
        
        # Process results
        improvements = []
        regressions = []
        all_recommendations = []
        
        for category, result in results.items():
            report['benchmark_results'][category] = {
                'test_name': result.test_name,
                'baseline_metrics': result.baseline_metrics,
                'optimized_metrics': result.optimized_metrics,
                'improvement_percent': result.improvement_percent,
                'regression_percent': result.regression_percent,
                'passed_targets': result.passed_targets,
                'recommendations': result.recommendations
            }
            
            if result.improvement_percent > 0:
                improvements.append(result.improvement_percent)
            if result.regression_percent > 0:
                regressions.append(result.regression_percent)
            
            all_recommendations.extend(result.recommendations)
        
        # Calculate summary
        if improvements:
            report['summary']['average_improvement'] = statistics.mean(improvements)
        if regressions:
            report['summary']['average_regression'] = statistics.mean(regressions)
        
        report['recommendations'] = list(set(all_recommendations))  # Remove duplicates
        
        return report
    
    def save_round2_report(self, report: Dict[str, Any], filename: str = None) -> str:
        """Save Round 2 performance report to file."""
        if filename is None:
            timestamp = int(time.time())
            filename = f"round2_performance_report_{timestamp}.json"
        
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.logger.info(f"Round 2 performance report saved to: {filepath}")
        return filepath


# Convenience functions for Round 2 benchmarks
def run_round2_benchmarks() -> Dict[str, Any]:
    """Run comprehensive Round 2 performance benchmarks."""
    benchmarker = Round2PerformanceBenchmarker()
    results = benchmarker.run_round2_benchmarks()
    report = benchmarker.generate_round2_report(results)
    return report


def establish_round2_baseline() -> Dict[str, Any]:
    """Establish Round 2 performance baseline."""
    benchmarker = Round2PerformanceBenchmarker()
    baseline = benchmarker.establish_baseline()
    return baseline


def generate_round2_report() -> str:
    """Generate and save Round 2 performance report."""
    benchmarker = Round2PerformanceBenchmarker()
    results = benchmarker.run_round2_benchmarks()
    report = benchmarker.generate_round2_report(results)
    return benchmarker.save_round2_report(report)
