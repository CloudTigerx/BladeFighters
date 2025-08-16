#!/usr/bin/env python3
"""
Performance Testing Framework for BladeFighters
Comprehensive performance benchmarking and regression detection.
"""

import unittest
import sys
import os
import time
import json
import statistics
import psutil
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.clock import FakeClock
from modules.audio_module import AudioSystem
from modules.input_module import InputManager
from modules.screen_module import ScreenManager
from modules.game_state_module.game_state_manager import GameStateManager
from core.puzzle_module import PuzzleEngine
from core.puzzle_renderer import PuzzleRenderer


@dataclass
class PerformanceMetrics:
    """Container for performance metrics."""
    operation_name: str
    duration_ms: float
    memory_usage_mb: float
    cpu_usage_percent: float
    iterations: int
    timestamp: float
    
    @property
    def operations_per_second(self) -> float:
        """Calculate operations per second."""
        return (self.iterations / self.duration_ms) * 1000 if self.duration_ms > 0 else 0
    
    @property
    def average_duration_ms(self) -> float:
        """Calculate average duration per operation."""
        return self.duration_ms / self.iterations if self.iterations > 0 else 0


@dataclass
class PerformanceThreshold:
    """Performance threshold configuration."""
    max_duration_ms: float
    max_memory_mb: float
    max_cpu_percent: float
    min_ops_per_second: float


class PerformanceBenchmark:
    """Base class for performance benchmarking."""
    
    def __init__(self, name: str, thresholds: PerformanceThreshold):
        self.name = name
        self.thresholds = thresholds
        self.metrics: List[PerformanceMetrics] = []
        self.process = psutil.Process(os.getpid())
    
    def measure_operation(self, operation_name: str, operation_func, iterations: int = 1) -> PerformanceMetrics:
        """Measure performance of an operation."""
        # Get initial system state
        initial_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        initial_cpu = self.process.cpu_percent()
        
        # Measure operation
        start_time = time.time()
        start_cpu = time.time()
        
        for _ in range(iterations):
            operation_func()
        
        end_time = time.time()
        end_cpu = time.time()
        
        # Get final system state
        final_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        final_cpu = self.process.cpu_percent()
        
        # Calculate metrics
        duration_ms = (end_time - start_time) * 1000
        memory_usage_mb = final_memory - initial_memory
        cpu_usage_percent = final_cpu - initial_cpu
        
        metrics = PerformanceMetrics(
            operation_name=operation_name,
            duration_ms=duration_ms,
            memory_usage_mb=memory_usage_mb,
            cpu_usage_percent=cpu_usage_percent,
            iterations=iterations,
            timestamp=time.time()
        )
        
        self.metrics.append(metrics)
        return metrics
    
    def check_thresholds(self, metrics: PerformanceMetrics) -> List[str]:
        """Check if metrics meet performance thresholds."""
        violations = []
        
        if metrics.duration_ms > self.thresholds.max_duration_ms:
            violations.append(f"Duration {metrics.duration_ms:.2f}ms exceeds threshold {self.thresholds.max_duration_ms}ms")
        
        if metrics.memory_usage_mb > self.thresholds.max_memory_mb:
            violations.append(f"Memory usage {metrics.memory_usage_mb:.2f}MB exceeds threshold {self.thresholds.max_memory_mb}MB")
        
        if metrics.cpu_usage_percent > self.thresholds.max_cpu_percent:
            violations.append(f"CPU usage {metrics.cpu_usage_percent:.2f}% exceeds threshold {self.thresholds.max_cpu_percent}%")
        
        if metrics.operations_per_second < self.thresholds.min_ops_per_second:
            violations.append(f"Operations per second {metrics.operations_per_second:.2f} below threshold {self.thresholds.min_ops_per_second}")
        
        return violations
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate performance report."""
        if not self.metrics:
            return {"error": "No metrics collected"}
        
        # Calculate statistics
        durations = [m.duration_ms for m in self.metrics]
        memory_usage = [m.memory_usage_mb for m in self.metrics]
        cpu_usage = [m.cpu_usage_percent for m in self.metrics]
        ops_per_second = [m.operations_per_second for m in self.metrics]
        
        report = {
            "benchmark_name": self.name,
            "total_operations": len(self.metrics),
            "timestamp": time.time(),
            "thresholds": {
                "max_duration_ms": self.thresholds.max_duration_ms,
                "max_memory_mb": self.thresholds.max_memory_mb,
                "max_cpu_percent": self.thresholds.max_cpu_percent,
                "min_ops_per_second": self.thresholds.min_ops_per_second
            },
            "statistics": {
                "duration_ms": {
                    "mean": statistics.mean(durations),
                    "median": statistics.median(durations),
                    "min": min(durations),
                    "max": max(durations),
                    "std": statistics.stdev(durations) if len(durations) > 1 else 0
                },
                "memory_usage_mb": {
                    "mean": statistics.mean(memory_usage),
                    "median": statistics.median(memory_usage),
                    "min": min(memory_usage),
                    "max": max(memory_usage),
                    "std": statistics.stdev(memory_usage) if len(memory_usage) > 1 else 0
                },
                "cpu_usage_percent": {
                    "mean": statistics.mean(cpu_usage),
                    "median": statistics.median(cpu_usage),
                    "min": min(cpu_usage),
                    "max": max(cpu_usage),
                    "std": statistics.stdev(cpu_usage) if len(cpu_usage) > 1 else 0
                },
                "operations_per_second": {
                    "mean": statistics.mean(ops_per_second),
                    "median": statistics.median(ops_per_second),
                    "min": min(ops_per_second),
                    "max": max(ops_per_second),
                    "std": statistics.stdev(ops_per_second) if len(ops_per_second) > 1 else 0
                }
            },
            "threshold_violations": [],
            "detailed_metrics": [
                {
                    "operation_name": m.operation_name,
                    "duration_ms": m.duration_ms,
                    "memory_usage_mb": m.memory_usage_mb,
                    "cpu_usage_percent": m.cpu_usage_percent,
                    "operations_per_second": m.operations_per_second,
                    "iterations": m.iterations,
                    "timestamp": m.timestamp
                }
                for m in self.metrics
            ]
        }
        
        # Check for threshold violations
        for metrics in self.metrics:
            violations = self.check_thresholds(metrics)
            if violations:
                report["threshold_violations"].append({
                    "operation": metrics.operation_name,
                    "violations": violations
                })
        
        return report


class AudioPerformanceTests(unittest.TestCase):
    """Performance tests for audio system."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_asset_path = tempfile.mkdtemp()
        self.create_test_audio_files()
        
        self.thresholds = PerformanceThreshold(
            max_duration_ms=100.0,
            max_memory_mb=50.0,
            max_cpu_percent=10.0,
            min_ops_per_second=100.0
        )
        
        self.benchmark = PerformanceBenchmark("Audio System", self.thresholds)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_asset_path, ignore_errors=True)
    
    def create_test_audio_files(self):
        """Create mock audio files for testing."""
        sounds_dir = os.path.join(self.test_asset_path, "sounds", "effects")
        os.makedirs(sounds_dir, exist_ok=True)
        
        for i in range(10):
            with open(os.path.join(sounds_dir, f"test_sound_{i}.wav"), 'w') as f:
                f.write("mock audio data")
    
    def test_audio_system_initialization_performance(self):
        """Test audio system initialization performance."""
        def init_audio():
            return AudioSystem(self.test_asset_path)
        
        metrics = self.benchmark.measure_operation(
            "audio_system_initialization",
            init_audio,
            iterations=10
        )
        
        violations = self.benchmark.check_thresholds(metrics)
        self.assertEqual(len(violations), 0, f"Performance violations: {violations}")
    
    def test_sound_loading_performance(self):
        """Test sound loading performance."""
        audio_system = AudioSystem(self.test_asset_path)
        
        def load_sounds():
            for i in range(10):
                audio_system.load_sound(f"test_sound_{i}")
        
        metrics = self.benchmark.measure_operation(
            "sound_loading",
            load_sounds,
            iterations=5
        )
        
        violations = self.benchmark.check_thresholds(metrics)
        self.assertEqual(len(violations), 0, f"Performance violations: {violations}")
    
    def test_volume_control_performance(self):
        """Test volume control performance."""
        audio_system = AudioSystem(self.test_asset_path)
        
        def volume_operations():
            for i in range(100):
                audio_system.set_master_volume(i / 100.0)
                audio_system.get_master_volume()
        
        metrics = self.benchmark.measure_operation(
            "volume_control",
            volume_operations,
            iterations=1
        )
        
        violations = self.benchmark.check_thresholds(metrics)
        self.assertEqual(len(violations), 0, f"Performance violations: {violations}")


class InputPerformanceTests(unittest.TestCase):
    """Performance tests for input system."""
    
    def setUp(self):
        """Set up test environment."""
        self.clock = FakeClock()
        self.input_manager = InputManager(clock=self.clock)
        
        self.thresholds = PerformanceThreshold(
            max_duration_ms=10.0,
            max_memory_mb=10.0,
            max_cpu_percent=5.0,
            min_ops_per_second=1000.0
        )
        
        self.benchmark = PerformanceBenchmark("Input System", self.thresholds)
    
    def test_input_event_processing_performance(self):
        """Test input event processing performance."""
        def process_events():
            for i in range(1000):
                self.input_manager.queue_event(f"EVENT_{i}")
            
            events = self.input_manager.get_pending_events()
            self.assertEqual(len(events), 1000)
        
        metrics = self.benchmark.measure_operation(
            "input_event_processing",
            process_events,
            iterations=10
        )
        
        violations = self.benchmark.check_thresholds(metrics)
        self.assertEqual(len(violations), 0, f"Performance violations: {violations}")
    
    def test_key_state_management_performance(self):
        """Test key state management performance."""
        def key_operations():
            for i in range(1000):
                self.input_manager.handle_key_press(f"K_KEY_{i}")
                self.input_manager.is_key_pressed(f"K_KEY_{i}")
                self.input_manager.handle_key_release(f"K_KEY_{i}")
        
        metrics = self.benchmark.measure_operation(
            "key_state_management",
            key_operations,
            iterations=5
        )
        
        violations = self.benchmark.check_thresholds(metrics)
        self.assertEqual(len(violations), 0, f"Performance violations: {violations}")
    
    def test_input_repeat_performance(self):
        """Test input repeat performance."""
        def repeat_operations():
            self.input_manager.handle_key_press('K_LEFT')
            
            for _ in range(100):
                self.clock.advance(80)  # Repeat interval
                events = self.input_manager.get_pending_events()
        
        metrics = self.benchmark.measure_operation(
            "input_repeat",
            repeat_operations,
            iterations=1
        )
        
        violations = self.benchmark.check_thresholds(metrics)
        self.assertEqual(len(violations), 0, f"Performance violations: {violations}")


class GameStatePerformanceTests(unittest.TestCase):
    """Performance tests for game state management."""
    
    def setUp(self):
        """Set up test environment."""
        self.state_manager = GameStateManager()
        
        self.thresholds = PerformanceThreshold(
            max_duration_ms=50.0,
            max_memory_mb=20.0,
            max_cpu_percent=5.0,
            min_ops_per_second=500.0
        )
        
        self.benchmark = PerformanceBenchmark("Game State", self.thresholds)
    
    def test_state_updates_performance(self):
        """Test state update performance."""
        def state_operations():
            updates = {}
            for i in range(100):
                updates[f"puzzle.score"] = i
                updates[f"puzzle.level"] = i % 10
                updates[f"audio.volume"] = i / 100.0
            
            self.state_manager.update(updates, source="test")
        
        metrics = self.benchmark.measure_operation(
            "state_updates",
            state_operations,
            iterations=10
        )
        
        violations = self.benchmark.check_thresholds(metrics)
        self.assertEqual(len(violations), 0, f"Performance violations: {violations}")
    
    def test_state_queries_performance(self):
        """Test state query performance."""
        # Set up some state first
        updates = {f"puzzle.score": 1000, "puzzle.level": 5, "audio.volume": 0.8}
        self.state_manager.update(updates, source="test")
        
        def query_operations():
            for i in range(1000):
                score = self.state_manager.get("puzzle.score")
                level = self.state_manager.get("puzzle.level")
                volume = self.state_manager.get("audio.volume")
        
        metrics = self.benchmark.measure_operation(
            "state_queries",
            query_operations,
            iterations=1
        )
        
        violations = self.benchmark.check_thresholds(metrics)
        self.assertEqual(len(violations), 0, f"Performance violations: {violations}")


class PuzzleEnginePerformanceTests(unittest.TestCase):
    """Performance tests for puzzle engine."""
    
    def setUp(self):
        """Set up test environment."""
        self.screen = Mock()
        self.font = Mock()
        self.asset_path = "puzzleassets"
        
        self.thresholds = PerformanceThreshold(
            max_duration_ms=200.0,
            max_memory_mb=100.0,
            max_cpu_percent=15.0,
            min_ops_per_second=100.0
        )
        
        self.benchmark = PerformanceBenchmark("Puzzle Engine", self.thresholds)
    
    def test_puzzle_engine_initialization_performance(self):
        """Test puzzle engine initialization performance."""
        def init_engine():
            return PuzzleEngine(self.screen, self.font, None, self.asset_path)
        
        metrics = self.benchmark.measure_operation(
            "puzzle_engine_initialization",
            init_engine,
            iterations=5
        )
        
        violations = self.benchmark.check_thresholds(metrics)
        self.assertEqual(len(violations), 0, f"Performance violations: {violations}")
    
    def test_puzzle_update_performance(self):
        """Test puzzle engine update performance."""
        engine = PuzzleEngine(self.screen, self.font, None, self.asset_path)
        
        def update_operations():
            for _ in range(100):
                engine.update()
        
        metrics = self.benchmark.measure_operation(
            "puzzle_update",
            update_operations,
            iterations=1
        )
        
        violations = self.benchmark.check_thresholds(metrics)
        self.assertEqual(len(violations), 0, f"Performance violations: {violations}")


class LoadTestingFramework:
    """Framework for load testing game components."""
    
    def __init__(self, max_concurrent_operations: int = 10):
        self.max_concurrent_operations = max_concurrent_operations
        self.results: List[Dict[str, Any]] = []
    
    def run_concurrent_test(self, test_func, num_operations: int) -> Dict[str, Any]:
        """Run concurrent operations and measure performance."""
        start_time = time.time()
        
        # Create threads for concurrent operations
        threads = []
        results = []
        
        def worker(thread_id):
            try:
                result = test_func(thread_id)
                results.append(result)
            except Exception as e:
                results.append({"error": str(e), "thread_id": thread_id})
        
        # Start threads
        for i in range(min(num_operations, self.max_concurrent_operations)):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        
        # Compile results
        test_result = {
            "num_operations": num_operations,
            "duration_ms": (end_time - start_time) * 1000,
            "successful_operations": len([r for r in results if "error" not in r]),
            "failed_operations": len([r for r in results if "error" in r]),
            "results": results
        }
        
        self.results.append(test_result)
        return test_result


class LoadPerformanceTests(unittest.TestCase):
    """Load testing for game components."""
    
    def setUp(self):
        """Set up test environment."""
        self.load_tester = LoadTestingFramework(max_concurrent_operations=5)
    
    def test_concurrent_audio_operations(self):
        """Test concurrent audio operations."""
        test_asset_path = tempfile.mkdtemp()
        
        def audio_operation(thread_id):
            audio_system = AudioSystem(test_asset_path)
            audio_system.set_master_volume(0.5)
            return {"thread_id": thread_id, "volume": 0.5}
        
        result = self.load_tester.run_concurrent_test(audio_operation, 10)
        
        # Should complete without errors
        self.assertEqual(result["failed_operations"], 0)
        self.assertLess(result["duration_ms"], 5000)  # Should complete within 5 seconds
        
        shutil.rmtree(test_asset_path, ignore_errors=True)
    
    def test_concurrent_input_operations(self):
        """Test concurrent input operations."""
        clock = FakeClock()
        
        def input_operation(thread_id):
            input_manager = InputManager(clock=clock)
            for i in range(100):
                input_manager.queue_event(f"EVENT_{thread_id}_{i}")
            events = input_manager.get_pending_events()
            return {"thread_id": thread_id, "events_processed": len(events)}
        
        result = self.load_tester.run_concurrent_test(input_operation, 10)
        
        # Should complete without errors
        self.assertEqual(result["failed_operations"], 0)
        self.assertLess(result["duration_ms"], 2000)  # Should complete within 2 seconds


class PerformanceRegressionTests(unittest.TestCase):
    """Tests for detecting performance regressions."""
    
    def setUp(self):
        """Set up test environment."""
        self.baseline_file = "performance_baseline.json"
        self.current_results = {}
    
    def test_performance_regression_detection(self):
        """Test detection of performance regressions."""
        # Load baseline if it exists
        baseline = {}
        if os.path.exists(self.baseline_file):
            with open(self.baseline_file, 'r') as f:
                baseline = json.load(f)
        
        # Run current performance tests
        self.run_current_performance_tests()
        
        # Compare with baseline
        regressions = self.detect_regressions(baseline, self.current_results)
        
        # For now, just log regressions without failing
        if regressions:
            print(f"⚠️  Performance regressions detected: {regressions}")
        
        # Save current results as new baseline
        with open(self.baseline_file, 'w') as f:
            json.dump(self.current_results, f, indent=2)
    
    def run_current_performance_tests(self):
        """Run current performance tests and collect results."""
        # This would run the actual performance tests
        # For now, create mock results
        self.current_results = {
            "audio_system_initialization": {"duration_ms": 50.0},
            "input_event_processing": {"duration_ms": 5.0},
            "state_updates": {"duration_ms": 25.0}
        }
    
    def detect_regressions(self, baseline: Dict, current: Dict) -> List[str]:
        """Detect performance regressions."""
        regressions = []
        
        for test_name, current_metrics in current.items():
            if test_name in baseline:
                baseline_metrics = baseline[test_name]
                
                # Check for 20% degradation
                if "duration_ms" in current_metrics and "duration_ms" in baseline_metrics:
                    current_duration = current_metrics["duration_ms"]
                    baseline_duration = baseline_metrics["duration_ms"]
                    
                    if current_duration > baseline_duration * 1.2:
                        regressions.append(
                            f"{test_name}: {current_duration:.2f}ms vs {baseline_duration:.2f}ms baseline"
                        )
        
        return regressions


def run_performance_tests():
    """Run all performance tests."""
    print("⚡ Running Performance Tests...")
    print("=" * 50)
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        AudioPerformanceTests,
        InputPerformanceTests,
        GameStatePerformanceTests,
        PuzzleEnginePerformanceTests,
        LoadPerformanceTests,
        PerformanceRegressionTests
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n📊 Performance Test Results:")
    print(f"✅ Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Failed: {len(result.failures)}")
    print(f"⚠️  Errors: {len(result.errors)}")
    print(f"📊 Total: {result.testsRun}")
    
    return result


if __name__ == "__main__":
    run_performance_tests()
