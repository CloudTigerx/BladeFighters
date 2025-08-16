"""
Comprehensive Test Automation Framework for BladeFighters
Provides integration testing, performance benchmarking, regression testing, and UI testing capabilities.
"""

import unittest
import sys
import os
import time
import json
import threading
import queue
import traceback
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from unittest.mock import Mock, patch, MagicMock
import pygame
import pytest

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from modules.game_state_module.game_state_manager import GameStateManager
from modules.game_state_module.state_schema import GameState, ScreenType, GameMode


@dataclass
class TestResult:
    """Represents the result of a single test."""
    test_name: str
    status: str  # 'passed', 'failed', 'skipped', 'error'
    duration: float
    error_message: Optional[str] = None
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    memory_usage: Optional[float] = None
    cpu_usage: Optional[float] = None


@dataclass
class TestSuiteResult:
    """Represents the result of a test suite."""
    suite_name: str
    total_tests: int
    passed: int
    failed: int
    skipped: int
    errors: int
    total_duration: float
    results: List[TestResult] = field(default_factory=list)
    performance_summary: Dict[str, Any] = field(default_factory=dict)


class PerformanceMonitor:
    """Monitors performance metrics during tests."""
    
    def __init__(self):
        self.start_time = None
        self.start_memory = None
        self.metrics = {}
    
    def start_monitoring(self):
        """Start monitoring performance."""
        self.start_time = time.time()
        self.start_memory = self._get_memory_usage()
    
    def stop_monitoring(self) -> Dict[str, Any]:
        """Stop monitoring and return metrics."""
        if self.start_time is None:
            return {}
        
        duration = time.time() - self.start_time
        end_memory = self._get_memory_usage()
        memory_delta = end_memory - self.start_memory if self.start_memory else 0
        
        return {
            'duration': duration,
            'memory_delta': memory_delta,
            'memory_peak': end_memory,
            'operations_per_second': 1.0 / duration if duration > 0 else 0
        }
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # Convert to MB
        except ImportError:
            return 0.0


class TestDataManager:
    """Manages test data and fixtures."""
    
    def __init__(self, fixtures_dir: str = "tests/fixtures"):
        self.fixtures_dir = fixtures_dir
        self.test_data = {}
        self._load_fixtures()
    
    def _load_fixtures(self):
        """Load test fixtures from files."""
        if not os.path.exists(self.fixtures_dir):
            os.makedirs(self.fixtures_dir)
            return
        
        for filename in os.listdir(self.fixtures_dir):
            if filename.endswith('.json'):
                fixture_name = filename[:-5]
                with open(os.path.join(self.fixtures_dir, filename), 'r') as f:
                    self.test_data[fixture_name] = json.load(f)
    
    def get_fixture(self, name: str) -> Dict[str, Any]:
        """Get a test fixture by name."""
        return self.test_data.get(name, {})
    
    def save_fixture(self, name: str, data: Dict[str, Any]):
        """Save a test fixture."""
        self.test_data[name] = data
        with open(os.path.join(self.fixtures_dir, f"{name}.json"), 'w') as f:
            json.dump(data, f, indent=2)
    
    def create_game_state_fixture(self, screen_type: ScreenType, game_mode: GameMode) -> Dict[str, Any]:
        """Create a game state fixture."""
        return {
            "screen": {
                "current_screen": screen_type.value,
                "transition_in_progress": False,
                "transition_duration": 0.5
            },
            "puzzle": {
                "game_active": True,
                "score": 0,
                "level": 1,
                "lines_cleared": 0,
                "game_mode": game_mode.value
            },
            "audio": {
                "master_volume": 0.7,
                "sfx_volume": 0.8,
                "music_volume": 0.6,
                "current_song": None
            }
        }


class UIStateTracker:
    """Tracks UI state changes for automated UI testing."""
    
    def __init__(self):
        self.screen_transitions = []
        self.ui_events = []
        self.current_screen = None
        self.screen_history = []
    
    def record_screen_transition(self, from_screen: str, to_screen: str, duration: float):
        """Record a screen transition."""
        transition = {
            'from': from_screen,
            'to': to_screen,
            'duration': duration,
            'timestamp': time.time()
        }
        self.screen_transitions.append(transition)
        self.screen_history.append(to_screen)
        self.current_screen = to_screen
    
    def record_ui_event(self, event_type: str, event_data: Dict[str, Any]):
        """Record a UI event."""
        event = {
            'type': event_type,
            'data': event_data,
            'timestamp': time.time(),
            'screen': self.current_screen
        }
        self.ui_events.append(event)
    
    def get_transition_summary(self) -> Dict[str, Any]:
        """Get a summary of screen transitions."""
        if not self.screen_transitions:
            return {}
        
        return {
            'total_transitions': len(self.screen_transitions),
            'average_duration': sum(t['duration'] for t in self.screen_transitions) / len(self.screen_transitions),
            'transitions': self.screen_transitions
        }


class BladeFightersTestSuite(unittest.TestCase):
    """Base test suite for BladeFighters with comprehensive testing capabilities."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment once for all test classes."""
        # Initialize pygame for testing
        pygame.init()
        
        # Create test screen
        cls.test_screen = pygame.display.set_mode((800, 600))
        cls.test_font = pygame.font.Font(None, 24)
        
        # Test configuration
        cls.test_config = {
            'screen_width': 800,
            'screen_height': 600,
            'asset_path': 'puzzleassets',
            'test_mode': True,
            'performance_threshold': 0.1,  # 100ms threshold
            'memory_threshold': 50.0  # 50MB threshold
        }
        
        # Initialize test infrastructure
        cls.performance_monitor = PerformanceMonitor()
        cls.test_data_manager = TestDataManager()
        cls.ui_tracker = UIStateTracker()
        
        print(f"\n🧪 Setting up BladeFighters test environment...")
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        pygame.quit()
        print(f"\n🧹 Cleaned up test environment.")
    
    def setUp(self):
        """Set up before each test."""
        self.start_time = time.time()
        self.performance_monitor.start_monitoring()
        
        # Initialize fresh game state manager for each test
        self.state_manager = GameStateManager()
        
        # Reset UI tracker
        self.ui_tracker = UIStateTracker()
    
    def tearDown(self):
        """Clean up after each test."""
        # Stop performance monitoring
        metrics = self.performance_monitor.stop_monitoring()
        test_duration = time.time() - self.start_time
        
        # Log performance issues
        if test_duration > self.test_config['performance_threshold']:
            print(f"⚠️  Slow test: {self._testMethodName} took {test_duration:.3f}s")
        
        if metrics.get('memory_delta', 0) > self.test_config['memory_threshold']:
            print(f"⚠️  High memory usage: {self._testMethodName} used {metrics['memory_delta']:.1f}MB")
    
    def assert_performance_acceptable(self, operation_name: str, max_duration: float = 0.1):
        """Assert that an operation completes within acceptable time."""
        start_time = time.time()
        yield  # This will be used as a context manager
        duration = time.time() - start_time
        self.assertLess(duration, max_duration, 
                       f"{operation_name} took {duration:.3f}s, should be < {max_duration}s")
    
    def assert_memory_usage_acceptable(self, operation_name: str, max_memory_mb: float = 50.0):
        """Assert that memory usage is within acceptable limits."""
        start_memory = self.performance_monitor._get_memory_usage()
        yield  # This will be used as a context manager
        end_memory = self.performance_monitor._get_memory_usage()
        memory_delta = end_memory - start_memory
        self.assertLess(memory_delta, max_memory_mb,
                       f"{operation_name} used {memory_delta:.1f}MB, should be < {max_memory_mb}MB")
    
    def simulate_screen_transition(self, from_screen: ScreenType, to_screen: ScreenType) -> float:
        """Simulate a screen transition and return duration."""
        start_time = time.time()
        
        # Set initial screen
        self.state_manager.set("screen.current_screen", from_screen, source="test")
        
        # Simulate transition
        self.state_manager.set("screen.transition_in_progress", True, source="test")
        time.sleep(0.1)  # Simulate transition time
        self.state_manager.set("screen.current_screen", to_screen, source="test")
        self.state_manager.set("screen.transition_in_progress", False, source="test")
        
        duration = time.time() - start_time
        self.ui_tracker.record_screen_transition(from_screen.value, to_screen.value, duration)
        
        return duration
    
    def create_test_game_state(self, screen_type: ScreenType = ScreenType.MAIN_MENU, 
                              game_mode: GameMode = GameMode.MENU) -> GameState:
        """Create a test game state."""
        fixture = self.test_data_manager.create_game_state_fixture(screen_type, game_mode)
        
        # Apply fixture to state manager
        for field_path, value in self._flatten_dict(fixture):
            self.state_manager.set(field_path, value, source="test")
        
        return self.state_manager.state
    
    def _flatten_dict(self, d: Dict[str, Any], parent_key: str = '') -> List[Tuple[str, Any]]:
        """Flatten a nested dictionary into field paths."""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}.{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key))
            else:
                items.append((new_key, v))
        return items


class IntegrationTestSuite(BladeFightersTestSuite):
    """Integration tests for module interactions."""
    
    def test_game_state_audio_integration(self):
        """Test integration between game state and audio system."""
        try:
            from modules.audio_module.audio_system import AudioSystem
            
            # Create audio system
            audio_system = AudioSystem(self.test_config['asset_path'])
            
            # Test volume changes through state manager
            self.state_manager.set("audio.master_volume", 0.5, source="test")
            self.state_manager.set("audio.sfx_volume", 0.8, source="test")
            
            # Verify state changes
            self.assertEqual(self.state_manager.get("audio.master_volume"), 0.5)
            self.assertEqual(self.state_manager.get("audio.sfx_volume"), 0.8)
            
        except ImportError:
            self.skipTest("AudioSystem not available")
    
    def test_screen_state_integration(self):
        """Test integration between screen manager and state manager."""
        try:
            from modules.screen_module.screen_manager import ScreenManager
            
            # Create screen manager
            screen_manager = ScreenManager(self.test_screen, self.test_font, 
                                         self.state_manager, self.test_config['asset_path'])
            
            # Test screen transitions
            transition_duration = self.simulate_screen_transition(
                ScreenType.MAIN_MENU, ScreenType.GAME
            )
            
            # Verify transition was recorded
            self.assertLess(transition_duration, 1.0)  # Should be quick
            self.assertEqual(self.state_manager.get("screen.current_screen"), ScreenType.GAME)
            
        except ImportError:
            self.skipTest("ScreenManager not available")
    
    def test_input_state_integration(self):
        """Test integration between input system and state manager."""
        try:
            from modules.input_module.unified_input_manager import UnifiedInputManager
            
            # Create input manager
            input_manager = UnifiedInputManager(self.state_manager)
            
            # Simulate input events
            mock_event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_SPACE})
            input_manager.handle_event(mock_event)
            
            # Verify input was processed
            # Add specific assertions based on your input system
            
        except ImportError:
            self.skipTest("UnifiedInputManager not available")


class PerformanceTestSuite(BladeFightersTestSuite):
    """Performance benchmarking tests."""
    
    def test_state_manager_performance(self):
        """Benchmark state manager operations."""
        # Test bulk updates
        updates = {f"puzzle.score": i for i in range(100)}
        
        start_time = time.time()
        results = self.state_manager.update(updates, source="test", description="Bulk update test")
        duration = time.time() - start_time
        
        self.assertLess(duration, 0.1, f"Bulk update took {duration:.3f}s, should be < 0.1s")
        self.assertTrue(all(results.values()))
    
    def test_snapshot_performance(self):
        """Benchmark snapshot creation and retrieval."""
        # Create many snapshots
        start_time = time.time()
        for i in range(50):
            self.state_manager.set("puzzle.score", i, source="test")
            snapshot = self.state_manager.snapshot(f"Snapshot {i}")
        
        creation_duration = time.time() - start_time
        self.assertLess(creation_duration, 1.0, f"Snapshot creation took {creation_duration:.3f}s")
        
        # Test snapshot retrieval
        start_time = time.time()
        latest = self.state_manager.get_latest_snapshot()
        retrieval_duration = time.time() - start_time
        
        self.assertLess(retrieval_duration, 0.01, f"Snapshot retrieval took {retrieval_duration:.3f}s")
        self.assertIsNotNone(latest)
    
    def test_memory_usage_under_load(self):
        """Test memory usage under heavy load."""
        initial_memory = self.performance_monitor._get_memory_usage()
        
        # Perform many operations
        for i in range(1000):
            self.state_manager.set("puzzle.score", i, source="test")
            if i % 100 == 0:
                self.state_manager.snapshot(f"Checkpoint {i}")
        
        final_memory = self.performance_monitor._get_memory_usage()
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB)
        self.assertLess(memory_increase, 100.0, 
                       f"Memory increased by {memory_increase:.1f}MB, should be < 100MB")


class RegressionTestSuite(BladeFightersTestSuite):
    """Regression tests to ensure existing functionality is preserved."""
    
    def test_state_validation_regression(self):
        """Test that state validation still works correctly."""
        # Test valid state changes
        valid_changes = [
            ("puzzle.score", 1000),
            ("puzzle.level", 5),
            ("audio.master_volume", 0.8),
            ("screen.current_screen", ScreenType.GAME)
        ]
        
        for field_path, value in valid_changes:
            success = self.state_manager.set(field_path, value, source="test")
            self.assertTrue(success, f"Valid change failed: {field_path} = {value}")
        
        # Test invalid state changes
        invalid_changes = [
            ("puzzle.score", -100),  # Negative score
            ("puzzle.level", 0),     # Invalid level
            ("audio.master_volume", 1.5),  # Volume > 1.0
        ]
        
        for field_path, value in invalid_changes:
            success = self.state_manager.set(field_path, value, source="test")
            self.assertFalse(success, f"Invalid change succeeded: {field_path} = {value}")
    
    def test_screen_transition_regression(self):
        """Test that screen transitions work correctly."""
        # Test valid transitions
        valid_transitions = [
            (ScreenType.LOADING, ScreenType.MAIN_MENU),
            (ScreenType.MAIN_MENU, ScreenType.GAME),
            (ScreenType.GAME, ScreenType.PAUSE),
            (ScreenType.PAUSE, ScreenType.GAME),
        ]
        
        for from_screen, to_screen in valid_transitions:
            self.state_manager.set("screen.current_screen", from_screen, source="test")
            success = self.state_manager.set("screen.current_screen", to_screen, source="test")
            self.assertTrue(success, f"Transition failed: {from_screen} -> {to_screen}")
    
    def test_rollback_regression(self):
        """Test that rollback functionality works correctly."""
        # Create initial state
        self.state_manager.set("puzzle.score", 1000, source="test")
        self.state_manager.set("puzzle.level", 5, source="test")
        initial_snapshot = self.state_manager.snapshot("Initial state")
        
        # Make changes
        self.state_manager.set("puzzle.score", 2000, source="test")
        self.state_manager.set("puzzle.level", 10, source="test")
        
        # Rollback
        success = self.state_manager.rollback_to_snapshot(initial_snapshot)
        self.assertTrue(success)
        
        # Verify rollback
        self.assertEqual(self.state_manager.get("puzzle.score"), 1000)
        self.assertEqual(self.state_manager.get("puzzle.level"), 5)


class UITestSuite(BladeFightersTestSuite):
    """Automated UI testing for screen transitions and interactions."""
    
    def test_screen_transition_automation(self):
        """Test automated screen transitions."""
        screens = [ScreenType.LOADING, ScreenType.MAIN_MENU, ScreenType.GAME, 
                  ScreenType.PAUSE, ScreenType.SETTINGS]
        
        transition_times = []
        
        for i in range(len(screens) - 1):
            duration = self.simulate_screen_transition(screens[i], screens[i + 1])
            transition_times.append(duration)
            
            # Verify transition was recorded
            self.assertLess(duration, 1.0, f"Transition {screens[i]} -> {screens[i+1]} too slow")
        
        # Verify all transitions were recorded
        summary = self.ui_tracker.get_transition_summary()
        self.assertEqual(summary['total_transitions'], len(screens) - 1)
        
        # Verify average transition time is reasonable
        avg_duration = sum(transition_times) / len(transition_times)
        self.assertLess(avg_duration, 0.5, f"Average transition time {avg_duration:.3f}s too high")
    
    def test_ui_event_tracking(self):
        """Test UI event tracking."""
        # Simulate UI events
        self.ui_tracker.record_ui_event("button_click", {"button": "start_game", "position": (100, 100)})
        self.ui_tracker.record_ui_event("key_press", {"key": "space", "modifiers": []})
        self.ui_tracker.record_ui_event("mouse_move", {"position": (200, 150)})
        
        # Verify events were recorded
        self.assertEqual(len(self.ui_tracker.ui_events), 3)
        
        # Verify event structure
        for event in self.ui_tracker.ui_events:
            self.assertIn('type', event)
            self.assertIn('data', event)
            self.assertIn('timestamp', event)
    
    def test_ui_responsiveness(self):
        """Test UI responsiveness under load."""
        # Simulate rapid UI interactions
        start_time = time.time()
        
        for i in range(100):
            self.ui_tracker.record_ui_event("button_click", {"button": f"button_{i}"})
            if i % 10 == 0:
                self.simulate_screen_transition(ScreenType.MAIN_MENU, ScreenType.GAME)
        
        total_time = time.time() - start_time
        
        # Should complete quickly
        self.assertLess(total_time, 5.0, f"UI responsiveness test took {total_time:.3f}s")


class TestAutomationRunner:
    """Main test automation runner with comprehensive reporting."""
    
    def __init__(self):
        self.results = {}
        self.performance_data = {}
        self.regression_data = {}
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all test suites and return comprehensive results."""
        test_suites = [
            IntegrationTestSuite,
            PerformanceTestSuite,
            RegressionTestSuite,
            UITestSuite
        ]
        
        print("\n" + "="*80)
        print("🧪 BLADE FIGHTERS COMPREHENSIVE TEST AUTOMATION")
        print("="*80)
        
        all_results = {}
        
        for suite_class in test_suites:
            print(f"\n📋 Running {suite_class.__name__}...")
            suite_result = self._run_test_suite(suite_class)
            all_results[suite_class.__name__] = suite_result
            
            # Print suite summary
            self._print_suite_summary(suite_result)
        
        # Generate comprehensive report
        comprehensive_report = self._generate_comprehensive_report(all_results)
        
        # Save results
        self._save_results(comprehensive_report)
        
        return comprehensive_report
    
    def _run_test_suite(self, suite_class) -> TestSuiteResult:
        """Run a specific test suite."""
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromTestCase(suite_class)
        
        runner = unittest.TextTestRunner(verbosity=1)
        result = runner.run(suite)
        
        # Convert to our result format
        test_results = []
        for test, traceback in result.failures + result.errors:
            test_results.append(TestResult(
                test_name=str(test),
                status='failed' if test in result.failures else 'error',
                duration=0.0,  # Would need to track this separately
                error_message=traceback
            ))
        
        return TestSuiteResult(
            suite_name=suite_class.__name__,
            total_tests=result.testsRun,
            passed=result.testsRun - len(result.failures) - len(result.errors),
            failed=len(result.failures),
            skipped=0,  # Would need to track this separately
            errors=len(result.errors),
            total_duration=0.0,  # Would need to track this separately
            results=test_results
        )
    
    def _print_suite_summary(self, suite_result: TestSuiteResult):
        """Print a summary for a test suite."""
        pass_rate = (suite_result.passed / suite_result.total_tests * 100) if suite_result.total_tests > 0 else 0
        
        print(f"   ✅ Passed: {suite_result.passed}")
        print(f"   ❌ Failed: {suite_result.failed}")
        print(f"   ⚠️  Errors: {suite_result.errors}")
        print(f"   📊 Pass Rate: {pass_rate:.1f}%")
    
    def _generate_comprehensive_report(self, all_results: Dict[str, TestSuiteResult]) -> Dict[str, Any]:
        """Generate a comprehensive test report."""
        total_tests = sum(r.total_tests for r in all_results.values())
        total_passed = sum(r.passed for r in all_results.values())
        total_failed = sum(r.failed for r in all_results.values())
        total_errors = sum(r.errors for r in all_results.values())
        
        overall_pass_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        return {
            'summary': {
                'total_tests': total_tests,
                'total_passed': total_passed,
                'total_failed': total_failed,
                'total_errors': total_errors,
                'overall_pass_rate': overall_pass_rate,
                'timestamp': time.time()
            },
            'suite_results': {
                name: {
                    'total_tests': result.total_tests,
                    'passed': result.passed,
                    'failed': result.failed,
                    'errors': result.errors,
                    'pass_rate': (result.passed / result.total_tests * 100) if result.total_tests > 0 else 0
                }
                for name, result in all_results.items()
            },
            'recommendations': self._generate_recommendations(all_results)
        }
    
    def _generate_recommendations(self, all_results: Dict[str, TestSuiteResult]) -> List[str]:
        """Generate recommendations based on test results."""
        recommendations = []
        
        for suite_name, result in all_results.items():
            pass_rate = (result.passed / result.total_tests * 100) if result.total_tests > 0 else 0
            
            if pass_rate < 80:
                recommendations.append(f"⚠️  {suite_name} has low pass rate ({pass_rate:.1f}%) - needs attention")
            
            if result.failed > 0:
                recommendations.append(f"🔧 {suite_name} has {result.failed} failed tests - review failures")
            
            if result.errors > 0:
                recommendations.append(f"🚨 {suite_name} has {result.errors} errors - critical issues found")
        
        if not recommendations:
            recommendations.append("🎉 All test suites are performing well!")
        
        return recommendations
    
    def _save_results(self, report: Dict[str, Any]):
        """Save test results to files."""
        # Save JSON report
        with open('test_automation_results.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        # Save human-readable report
        with open('test_automation_report.txt', 'w') as f:
            f.write("BLADE FIGHTERS TEST AUTOMATION REPORT\n")
            f.write("=" * 50 + "\n\n")
            
            summary = report['summary']
            f.write(f"Overall Results:\n")
            f.write(f"  Total Tests: {summary['total_tests']}\n")
            f.write(f"  Passed: {summary['total_passed']}\n")
            f.write(f"  Failed: {summary['total_failed']}\n")
            f.write(f"  Errors: {summary['total_errors']}\n")
            f.write(f"  Pass Rate: {summary['overall_pass_rate']:.1f}%\n\n")
            
            f.write("Suite Results:\n")
            for suite_name, suite_result in report['suite_results'].items():
                f.write(f"  {suite_name}: {suite_result['pass_rate']:.1f}% ({suite_result['passed']}/{suite_result['total_tests']})\n")
            
            f.write("\nRecommendations:\n")
            for rec in report['recommendations']:
                f.write(f"  {rec}\n")
        
        print(f"\n💾 Test results saved to test_automation_results.json and test_automation_report.txt")


def run_comprehensive_tests():
    """Run all comprehensive tests."""
    runner = TestAutomationRunner()
    return runner.run_all_tests()


if __name__ == "__main__":
    run_comprehensive_tests() 