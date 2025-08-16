"""
Test Automation Module - Integration Examples

This file provides comprehensive examples of how to use the Test Automation Framework
for testing BladeFighters modules. These examples demonstrate best practices and
common patterns for integration testing, performance testing, and regression testing.
"""

import sys
import os
import time
from typing import Dict, Any

# Add project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from tests.integration.test_suite_framework import (
    BladeFightersTestSuite, 
    PerformanceMonitor, 
    TestDataManager, 
    UIStateTracker
)
from modules.game_state_module.state_schema import ScreenType, GameMode


class TestAutomationIntegrationExamples:
    """
    Comprehensive examples of how to use the Test Automation Framework.
    
    This class demonstrates various testing patterns and best practices
    for testing BladeFighters modules.
    """
    
    def __init__(self):
        """Initialize the integration examples."""
        self.test_suite = None
        self.performance_monitor = None
        self.test_data_manager = None
        self.ui_tracker = None
    
    def setup_test_environment(self):
        """Set up the test environment for examples."""
        # Create test suite instance
        self.test_suite = BladeFightersTestSuite()
        self.test_suite.setUp()
        
        # Initialize components
        self.performance_monitor = PerformanceMonitor()
        self.test_data_manager = TestDataManager()
        self.ui_tracker = UIStateTracker()
    
    def cleanup_test_environment(self):
        """Clean up the test environment."""
        if self.test_suite:
            self.test_suite.tearDown()
    
    def example_basic_module_testing(self):
        """
        Example 1: Basic Module Testing
        
        Demonstrates how to create basic tests for a module.
        """
        print("=== Example 1: Basic Module Testing ===")
        
        # Example test class structure
        class BasicModuleTests(BladeFightersTestSuite):
            def setUp(self):
                super().setUp()
                # Initialize your module here
                try:
                    from modules.my_module import MyModule
                    self.my_module = MyModule()
                except ImportError:
                    self.skipTest("MyModule not available")
            
            def test_module_initialization(self):
                """Test that the module initializes correctly."""
                self.assertIsNotNone(self.my_module)
                self.assertTrue(hasattr(self.my_module, 'initialize'))
            
            def test_basic_functionality(self):
                """Test basic module functionality."""
                result = self.my_module.basic_operation()
                self.assertIsNotNone(result)
                self.assertEqual(result, "expected_value")
            
            def test_error_handling(self):
                """Test error handling."""
                with self.assertRaises(ValueError):
                    self.my_module.operation_with_invalid_input("invalid")
        
        print("✅ Basic module testing example completed")
    
    def example_integration_testing(self):
        """
        Example 2: Integration Testing
        
        Demonstrates how to test module interactions and state synchronization.
        """
        print("\n=== Example 2: Integration Testing ===")
        
        class IntegrationTests(BladeFightersTestSuite):
            def setUp(self):
                super().setUp()
                # Initialize multiple modules for integration testing
                try:
                    from modules.audio_module.audio_system import AudioSystem
                    from modules.screen_module.screen_manager import ScreenManager
                    self.audio_system = AudioSystem(self.test_config['asset_path'])
                    self.screen_manager = ScreenManager(
                        self.test_screen, 
                        self.test_font, 
                        self.state_manager, 
                        self.test_config['asset_path']
                    )
                except ImportError as e:
                    self.skipTest(f"Required modules not available: {e}")
            
            def test_audio_screen_integration(self):
                """Test integration between audio and screen modules."""
                # Set audio volume through state manager
                self.state_manager.set("audio.master_volume", 0.5, source="test")
                
                # Verify audio system reflects the change
                self.assertEqual(self.audio_system.get_master_volume(), 0.5)
                
                # Test screen transition with audio
                self.state_manager.set("screen.current_screen", ScreenType.GAME, source="test")
                self.screen_manager.update()
                
                # Verify both modules are in sync
                self.assertEqual(self.state_manager.get("screen.current_screen"), ScreenType.GAME)
                self.assertEqual(self.audio_system.get_master_volume(), 0.5)
            
            def test_state_synchronization(self):
                """Test that all modules stay synchronized with game state."""
                # Make changes through state manager
                updates = {
                    "puzzle.score": 1000,
                    "puzzle.level": 5,
                    "audio.master_volume": 0.8,
                    "screen.current_screen": ScreenType.PAUSE
                }
                
                results = self.state_manager.update(updates, source="test")
                self.assertTrue(all(results.values()))
                
                # Verify all modules reflect the changes
                self.assertEqual(self.state_manager.get("puzzle.score"), 1000)
                self.assertEqual(self.state_manager.get("puzzle.level"), 5)
                self.assertEqual(self.state_manager.get("audio.master_volume"), 0.8)
                self.assertEqual(self.state_manager.get("screen.current_screen"), ScreenType.PAUSE)
        
        print("✅ Integration testing example completed")
    
    def example_performance_testing(self):
        """
        Example 3: Performance Testing
        
        Demonstrates how to benchmark module performance and detect regressions.
        """
        print("\n=== Example 3: Performance Testing ===")
        
        class PerformanceTests(BladeFightersTestSuite):
            def setUp(self):
                super().setUp()
                try:
                    from modules.my_module import MyModule
                    self.my_module = MyModule()
                except ImportError:
                    self.skipTest("MyModule not available")
            
            def test_operation_performance(self):
                """Test that operations complete within acceptable time."""
                monitor = PerformanceMonitor()
                monitor.start_monitoring()
                
                # Perform operations
                for i in range(1000):
                    self.my_module.operation()
                
                metrics = monitor.stop_monitoring()
                
                # Assert performance requirements
                self.assertLess(metrics['duration'], 1.0, 
                              f"Operation took {metrics['duration']:.3f}s, should be < 1.0s")
                self.assertLess(metrics['memory_delta'], 50.0,
                              f"Memory usage {metrics['memory_delta']:.1f}MB, should be < 50MB")
                
                print(f"Performance: {metrics['operations_per_second']:.1f} ops/sec")
            
            def test_memory_usage_under_load(self):
                """Test memory usage under heavy load."""
                initial_memory = self.performance_monitor._get_memory_usage()
                
                # Perform many operations
                for i in range(10000):
                    self.my_module.operation()
                    if i % 1000 == 0:
                        # Create snapshots periodically
                        self.state_manager.snapshot(f"Checkpoint {i}")
                
                final_memory = self.performance_monitor._get_memory_usage()
                memory_increase = final_memory - initial_memory
                
                # Memory increase should be reasonable
                self.assertLess(memory_increase, 100.0,
                              f"Memory increased by {memory_increase:.1f}MB, should be < 100MB")
            
            def test_concurrent_access(self):
                """Test module performance under concurrent access."""
                import threading
                
                def worker():
                    for i in range(100):
                        self.my_module.operation()
                
                # Create multiple threads
                threads = []
                for i in range(5):
                    thread = threading.Thread(target=worker)
                    threads.append(thread)
                    thread.start()
                
                # Wait for all threads to complete
                for thread in threads:
                    thread.join()
                
                # Should complete without errors
                self.assertTrue(True)
        
        print("✅ Performance testing example completed")
    
    def example_regression_testing(self):
        """
        Example 4: Regression Testing
        
        Demonstrates how to ensure existing functionality is preserved.
        """
        print("\n=== Example 4: Regression Testing ===")
        
        class RegressionTests(BladeFightersTestSuite):
            def setUp(self):
                super().setUp()
                try:
                    from modules.my_module import MyModule
                    self.my_module = MyModule()
                except ImportError:
                    self.skipTest("MyModule not available")
            
            def test_core_functionality_regression(self):
                """Test that core functionality still works correctly."""
                # Test valid operations
                valid_inputs = ["input1", "input2", "input3"]
                for input_value in valid_inputs:
                    result = self.my_module.core_operation(input_value)
                    self.assertIsNotNone(result)
                    self.assertIsInstance(result, str)
                
                # Test invalid operations
                invalid_inputs = [None, "", -1]
                for input_value in invalid_inputs:
                    with self.assertRaises(ValueError):
                        self.my_module.core_operation(input_value)
            
            def test_state_validation_regression(self):
                """Test that state validation still works correctly."""
                # Test valid state changes
                valid_changes = [
                    ("puzzle.score", 1000),
                    ("puzzle.level", 5),
                    ("audio.master_volume", 0.8)
                ]
                
                for field_path, value in valid_changes:
                    success = self.state_manager.set(field_path, value, source="test")
                    self.assertTrue(success, f"Valid change failed: {field_path} = {value}")
                
                # Test invalid state changes
                invalid_changes = [
                    ("puzzle.score", -100),  # Negative score
                    ("puzzle.level", 0),     # Invalid level
                    ("audio.master_volume", 1.5)  # Volume > 1.0
                ]
                
                for field_path, value in invalid_changes:
                    success = self.state_manager.set(field_path, value, source="test")
                    self.assertFalse(success, f"Invalid change succeeded: {field_path} = {value}")
            
            def test_rollback_functionality_regression(self):
                """Test that rollback functionality still works correctly."""
                # Create initial state
                self.state_manager.set("puzzle.score", 1000, source="test")
                initial_snapshot = self.state_manager.snapshot("Initial state")
                
                # Make changes
                self.state_manager.set("puzzle.score", 2000, source="test")
                self.state_manager.set("puzzle.level", 10, source="test")
                
                # Rollback
                success = self.state_manager.rollback_to_snapshot(initial_snapshot)
                self.assertTrue(success)
                
                # Verify rollback
                self.assertEqual(self.state_manager.get("puzzle.score"), 1000)
                self.assertEqual(self.state_manager.get("puzzle.level"), 1)  # Default value
        
        print("✅ Regression testing example completed")
    
    def example_ui_testing(self):
        """
        Example 5: UI Testing
        
        Demonstrates how to test screen transitions and UI interactions.
        """
        print("\n=== Example 5: UI Testing ===")
        
        class UITests(BladeFightersTestSuite):
            def setUp(self):
                super().setUp()
                try:
                    from modules.screen_module.screen_manager import ScreenManager
                    self.screen_manager = ScreenManager(
                        self.test_screen, 
                        self.test_font, 
                        self.state_manager, 
                        self.test_config['asset_path']
                    )
                except ImportError:
                    self.skipTest("ScreenManager not available")
            
            def test_screen_transition_automation(self):
                """Test automated screen transitions."""
                screens = [ScreenType.LOADING, ScreenType.MAIN_MENU, ScreenType.GAME, 
                          ScreenType.PAUSE, ScreenType.SETTINGS]
                
                transition_times = []
                
                for i in range(len(screens) - 1):
                    duration = self.simulate_screen_transition(screens[i], screens[i + 1])
                    transition_times.append(duration)
                    
                    # Verify transition was recorded
                    self.assertLess(duration, 1.0, 
                                  f"Transition {screens[i]} -> {screens[i+1]} too slow")
                
                # Verify all transitions were recorded
                summary = self.ui_tracker.get_transition_summary()
                self.assertEqual(summary['total_transitions'], len(screens) - 1)
                
                # Verify average transition time is reasonable
                avg_duration = sum(transition_times) / len(transition_times)
                self.assertLess(avg_duration, 0.5, 
                              f"Average transition time {avg_duration:.3f}s too high")
            
            def test_ui_event_tracking(self):
                """Test UI event tracking."""
                # Simulate UI events
                self.ui_tracker.record_ui_event("button_click", {
                    "button": "start_game", 
                    "position": (100, 100)
                })
                self.ui_tracker.record_ui_event("key_press", {
                    "key": "space", 
                    "modifiers": []
                })
                self.ui_tracker.record_ui_event("mouse_move", {
                    "position": (200, 150)
                })
                
                # Verify events were recorded
                self.assertEqual(len(self.ui_tracker.ui_events), 3)
                
                # Verify event structure
                for event in self.ui_tracker.ui_events:
                    self.assertIn('type', event)
                    self.assertIn('data', event)
                    self.assertIn('timestamp', event)
            
            def test_ui_responsiveness(self):
                """Test UI responsiveness under load."""
                start_time = time.time()
                
                # Simulate rapid UI interactions
                for i in range(100):
                    self.ui_tracker.record_ui_event("button_click", {
                        "button": f"button_{i}"
                    })
                    if i % 10 == 0:
                        self.simulate_screen_transition(ScreenType.MAIN_MENU, ScreenType.GAME)
                
                total_time = time.time() - start_time
                
                # Should complete quickly
                self.assertLess(total_time, 5.0, 
                              f"UI responsiveness test took {total_time:.3f}s")
        
        print("✅ UI testing example completed")
    
    def example_test_data_management(self):
        """
        Example 6: Test Data Management
        
        Demonstrates how to use fixtures and test data effectively.
        """
        print("\n=== Example 6: Test Data Management ===")
        
        class TestDataExamples(BladeFightersTestSuite):
            def setUp(self):
                super().setUp()
                self.test_data_manager = TestDataManager()
            
            def test_using_fixtures(self):
                """Test using predefined fixtures."""
                # Get a fixture
                game_state = self.test_data_manager.get_fixture("game_active_state")
                
                # Apply fixture to state manager
                for field_path, value in self._flatten_dict(game_state):
                    self.state_manager.set(field_path, value, source="test")
                
                # Verify fixture was applied correctly
                self.assertEqual(self.state_manager.get("puzzle.score"), 1500)
                self.assertEqual(self.state_manager.get("puzzle.level"), 5)
                self.assertEqual(self.state_manager.get("screen.current_screen"), ScreenType.GAME)
            
            def test_creating_custom_fixtures(self):
                """Test creating custom fixtures."""
                # Create custom fixture
                custom_fixture = {
                    "puzzle": {
                        "score": 5000,
                        "level": 10,
                        "game_active": True
                    },
                    "audio": {
                        "master_volume": 0.9,
                        "sfx_volume": 1.0
                    }
                }
                
                # Save fixture
                self.test_data_manager.save_fixture("custom_test_state", custom_fixture)
                
                # Load and use fixture
                loaded_fixture = self.test_data_manager.get_fixture("custom_test_state")
                self.assertEqual(loaded_fixture["puzzle"]["score"], 5000)
            
            def test_fixture_validation(self):
                """Test fixture validation and error handling."""
                # Test with invalid fixture
                invalid_fixture = {
                    "puzzle": {
                        "score": "not_a_number",  # Invalid type
                        "level": -1  # Invalid value
                    }
                }
                
                # Apply fixture and test validation
                for field_path, value in self._flatten_dict(invalid_fixture):
                    success = self.state_manager.set(field_path, value, source="test")
                    # Should fail validation
                    self.assertFalse(success)
            
            def _flatten_dict(self, d: Dict[str, Any], parent_key: str = '') -> list:
                """Flatten a nested dictionary into field paths."""
                items = []
                for k, v in d.items():
                    new_key = f"{parent_key}.{k}" if parent_key else k
                    if isinstance(v, dict):
                        items.extend(self._flatten_dict(v, new_key))
                    else:
                        items.append((new_key, v))
                return items
        
        print("✅ Test data management example completed")
    
    def example_comprehensive_test_suite(self):
        """
        Example 7: Comprehensive Test Suite
        
        Demonstrates a complete test suite combining all testing approaches.
        """
        print("\n=== Example 7: Comprehensive Test Suite ===")
        
        class ComprehensiveModuleTests(BladeFightersTestSuite):
            def setUp(self):
                super().setUp()
                try:
                    from modules.my_module import MyModule
                    self.my_module = MyModule()
                except ImportError:
                    self.skipTest("MyModule not available")
            
            def test_complete_workflow(self):
                """Test complete module workflow with all aspects."""
                # 1. Basic functionality
                self.assertIsNotNone(self.my_module)
                
                # 2. Performance testing
                monitor = PerformanceMonitor()
                monitor.start_monitoring()
                
                # Perform workflow operations
                self.my_module.initialize()
                result = self.my_module.process_data("test_data")
                self.my_module.cleanup()
                
                metrics = monitor.stop_monitoring()
                
                # 3. Performance assertions
                self.assertLess(metrics['duration'], 0.5, 
                              f"Workflow took {metrics['duration']:.3f}s")
                self.assertLess(metrics['memory_delta'], 10.0,
                              f"Memory usage {metrics['memory_delta']:.1f}MB")
                
                # 4. State validation
                self.assertEqual(result, "expected_result")
                self.assertTrue(self.my_module.is_initialized())
                
                # 5. UI interaction (if applicable)
                if hasattr(self.my_module, 'ui_component'):
                    self.ui_tracker.record_ui_event("module_operation", {
                        "operation": "workflow_complete",
                        "result": result
                    })
            
            def test_error_scenarios(self):
                """Test error scenarios and recovery."""
                # Test invalid initialization
                with self.assertRaises(ValueError):
                    self.my_module.initialize_with_invalid_config({})
                
                # Test recovery after error
                self.my_module.reset()
                self.assertFalse(self.my_module.is_initialized())
                
                # Test successful recovery
                self.my_module.initialize()
                self.assertTrue(self.my_module.is_initialized())
            
            def test_integration_with_other_modules(self):
                """Test integration with other modules."""
                # Test state synchronization
                self.state_manager.set("my_module.enabled", True, source="test")
                self.assertTrue(self.my_module.is_enabled())
                
                # Test module interaction
                if hasattr(self.my_module, 'interact_with_audio'):
                    self.my_module.interact_with_audio()
                    # Verify audio state changed
                    self.assertNotEqual(
                        self.state_manager.get("audio.current_song"), 
                        None
                    )
        
        print("✅ Comprehensive test suite example completed")
    
    def run_all_examples(self):
        """Run all integration examples."""
        print("🧪 Test Automation Framework - Integration Examples")
        print("=" * 60)
        
        try:
            self.setup_test_environment()
            
            # Run all examples
            self.example_basic_module_testing()
            self.example_integration_testing()
            self.example_performance_testing()
            self.example_regression_testing()
            self.example_ui_testing()
            self.example_test_data_management()
            self.example_comprehensive_test_suite()
            
            print("\n" + "=" * 60)
            print("✅ All integration examples completed successfully!")
            print("\n📚 Next Steps:")
            print("1. Review the examples above")
            print("2. Adapt them to your specific module")
            print("3. Create your own test classes")
            print("4. Run tests with: make test-all")
            print("5. Check results with: make test-results")
            
        except Exception as e:
            print(f"\n❌ Error running examples: {e}")
            print("This is expected if modules are not available.")
            print("The examples demonstrate the patterns - adapt them to your modules.")
        
        finally:
            self.cleanup_test_environment()


def main():
    """Main entry point for running integration examples."""
    examples = TestAutomationIntegrationExamples()
    examples.run_all_examples()


if __name__ == "__main__":
    main()
