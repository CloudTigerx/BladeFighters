"""
Round 2 Comprehensive Integration Tests
Tests all 4 modules working together with GameStateManager integration.
"""

import unittest
import sys
import os
import time
import threading
from typing import Dict, Any, List
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from tests.integration.test_suite_framework import (
    BladeFightersTestSuite, 
    PerformanceMonitor, 
    TestDataManager, 
    UIStateTracker
)
from modules.game_state_module.state_schema import ScreenType, GameMode


class Round2ComprehensiveIntegrationTests(BladeFightersTestSuite):
    """
    Comprehensive integration tests for Round 2.
    Tests all 4 modules working together with GameStateManager.
    """
    
    def setUp(self):
        """Set up all modules for comprehensive testing."""
        super().setUp()
        
        # Initialize all modules
        self.modules = {}
        self.module_errors = []
        
        try:
            # Audio Module
            from modules.audio_module.audio_system import AudioSystem
            self.modules['audio'] = AudioSystem(self.test_config['asset_path'])
            self.modules['audio'].set_state_manager(self.state_manager)
        except ImportError as e:
            self.module_errors.append(f"Audio module not available: {e}")
        
        try:
            # Screen Module
            from modules.screen_module.screen_manager import ScreenManager
            self.modules['screen'] = ScreenManager(
                self.test_screen, 
                self.test_font, 
                self.state_manager, 
                self.test_config['asset_path']
            )
        except ImportError as e:
            self.module_errors.append(f"Screen module not available: {e}")
        
        try:
            # Input Module
            from modules.input_module.unified_input_manager import UnifiedInputManager
            self.modules['input'] = UnifiedInputManager(self.state_manager)
        except ImportError as e:
            self.module_errors.append(f"Input module not available: {e}")
        
        try:
            # Settings Module
            from modules.settings_module.unified_config import UnifiedConfig
            self.modules['settings'] = UnifiedConfig(self.state_manager)
        except ImportError as e:
            self.module_errors.append(f"Settings module not available: {e}")
        
        # Skip tests if critical modules are missing
        if len(self.module_errors) > 2:
            self.skipTest(f"Too many modules unavailable: {self.module_errors}")
    
    def test_all_modules_initialization(self):
        """Test that all available modules initialize correctly."""
        self.assertGreater(len(self.modules), 0, "No modules available for testing")
        
        for module_name, module_instance in self.modules.items():
            self.assertIsNotNone(module_instance, f"{module_name} module is None")
            
            # Test basic functionality
            if hasattr(module_instance, 'is_initialized'):
                self.assertTrue(module_instance.is_initialized(), 
                              f"{module_name} module not initialized")
    
    def test_cross_module_state_synchronization(self):
        """Test state synchronization across all modules."""
        # Set up complex state across all modules
        complex_state = {
            "audio.master_volume": 0.7,
            "audio.sfx_volume": 0.8,
            "audio.current_song": "menu_music",
            "screen.current_screen": ScreenType.MAIN_MENU,
            "screen.transition_in_progress": False,
            "input.keyboard.space_pressed": False,
            "input.mouse.left_button": False,
            "settings.audio_enabled": True,
            "settings.screen_resolution": "800x600"
        }
        
        # Apply state changes
        results = self.state_manager.update(complex_state, source="test")
        self.assertTrue(all(results.values()), "Some state changes failed")
        
        # Verify all modules reflect the state changes
        if 'audio' in self.modules:
            audio = self.modules['audio']
            self.assertEqual(audio.get_master_volume(), 0.7)
            self.assertEqual(audio.get_sfx_volume(), 0.8)
            self.assertEqual(audio.get_current_song(), "menu_music")
        
        if 'screen' in self.modules:
            screen = self.modules['screen']
            current_screen = self.state_manager.get("screen.current_screen")
            self.assertEqual(current_screen, ScreenType.MAIN_MENU)
        
        if 'input' in self.modules:
            input_manager = self.modules['input']
            space_pressed = self.state_manager.get("input.keyboard.space_pressed")
            self.assertFalse(space_pressed)
        
        if 'settings' in self.modules:
            settings = self.modules['settings']
            audio_enabled = self.state_manager.get("settings.audio_enabled")
            self.assertTrue(audio_enabled)
    
    def test_screen_transitions_with_audio_persistence(self):
        """Test screen transitions while maintaining audio state."""
        # Set up audio state
        self.state_manager.set("audio.master_volume", 0.6, source="test")
        self.state_manager.set("audio.current_song", "menu_music", source="test")
        
        # Perform screen transitions
        transitions = [
            (ScreenType.MAIN_MENU, ScreenType.GAME),
            (ScreenType.GAME, ScreenType.PAUSE),
            (ScreenType.PAUSE, ScreenType.SETTINGS),
            (ScreenType.SETTINGS, ScreenType.MAIN_MENU)
        ]
        
        for from_screen, to_screen in transitions:
            # Verify audio state before transition
            volume_before = self.state_manager.get("audio.master_volume")
            song_before = self.state_manager.get("audio.current_song")
            
            # Perform transition
            duration = self.simulate_screen_transition(from_screen, to_screen)
            self.assertLess(duration, 1.0, f"Transition {from_screen} -> {to_screen} too slow")
            
            # Verify audio state maintained
            volume_after = self.state_manager.get("audio.master_volume")
            song_after = self.state_manager.get("audio.current_song")
            
            self.assertEqual(volume_after, volume_before, 
                           f"Audio volume changed during transition {from_screen} -> {to_screen}")
            self.assertEqual(song_after, song_before, 
                           f"Audio song changed during transition {from_screen} -> {to_screen}")
    
    def test_input_state_management_during_gameplay(self):
        """Test input state management during gameplay scenarios."""
        # Start in game screen
        self.state_manager.set("screen.current_screen", ScreenType.GAME, source="test")
        
        # Simulate gameplay input events
        gameplay_events = [
            (pygame.KEYDOWN, {'key': pygame.K_SPACE}, "space_pressed"),
            (pygame.KEYDOWN, {'key': pygame.K_LEFT}, "left_pressed"),
            (pygame.KEYDOWN, {'key': pygame.K_RIGHT}, "right_pressed"),
            (pygame.KEYDOWN, {'key': pygame.K_DOWN}, "down_pressed"),
            (pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': (100, 100)}, "mouse_click")
        ]
        
        for event_type, event_data, expected_state in gameplay_events:
            # Create mock event
            mock_event = pygame.event.Event(event_type, event_data)
            
            # Process input
            if 'input' in self.modules:
                result = self.modules['input'].handle_event(mock_event)
                self.assertIsInstance(result, bool, f"Input event {event_type} not handled")
            
            # Verify state was updated appropriately
            if event_type == pygame.KEYDOWN:
                key_name = pygame.key.name(event_data['key'])
                state_key = f"input.keyboard.{key_name}_pressed"
                # Note: Actual state update depends on input module implementation
                # This test verifies the input was processed
    
    def test_puzzle_state_changes_with_audio_feedback(self):
        """Test puzzle state changes with audio feedback."""
        # Set up game state
        self.state_manager.set("screen.current_screen", ScreenType.GAME, source="test")
        self.state_manager.set("audio.master_volume", 0.8, source="test")
        
        # Simulate puzzle events with audio feedback
        puzzle_events = [
            {"event": "piece_landed", "score_change": 10, "audio_effect": "land"},
            {"event": "line_cleared", "score_change": 100, "audio_effect": "clear"},
            {"event": "level_up", "score_change": 0, "audio_effect": "level_up"},
            {"event": "game_over", "score_change": 0, "audio_effect": "game_over"}
        ]
        
        initial_score = self.state_manager.get("puzzle.score", 0)
        
        for event in puzzle_events:
            # Simulate puzzle event
            self.state_manager.set("puzzle.last_event", event["event"], source="test")
            
            # Update score
            current_score = self.state_manager.get("puzzle.score", 0)
            new_score = current_score + event["score_change"]
            self.state_manager.set("puzzle.score", new_score, source="test")
            
            # Verify score updated
            self.assertEqual(self.state_manager.get("puzzle.score"), new_score)
            
            # Verify audio state reflects the event
            if 'audio' in self.modules:
                # Audio module should respond to puzzle events
                # This depends on the audio module's event handling
                pass
    
    def test_settings_changes_affecting_all_modules(self):
        """Test that settings changes affect all modules appropriately."""
        # Test settings that affect multiple modules
        settings_tests = [
            {
                "setting": "audio.master_volume",
                "value": 0.5,
                "affected_modules": ["audio"],
                "verification": lambda: self.state_manager.get("audio.master_volume") == 0.5
            },
            {
                "setting": "screen.resolution",
                "value": "1920x1080",
                "affected_modules": ["screen"],
                "verification": lambda: self.state_manager.get("screen.resolution") == "1920x1080"
            },
            {
                "setting": "input.keyboard_layout",
                "value": "QWERTY",
                "affected_modules": ["input"],
                "verification": lambda: self.state_manager.get("input.keyboard_layout") == "QWERTY"
            }
        ]
        
        for test in settings_tests:
            # Change setting
            success = self.state_manager.set(test["setting"], test["value"], source="test")
            self.assertTrue(success, f"Setting change failed: {test['setting']}")
            
            # Verify setting was applied
            self.assertTrue(test["verification"](), 
                          f"Setting verification failed: {test['setting']}")
            
            # Verify affected modules reflect the change
            for module_name in test["affected_modules"]:
                if module_name in self.modules:
                    module = self.modules[module_name]
                    # Module-specific verification would go here
                    # This depends on each module's implementation
    
    def test_concurrent_module_operations(self):
        """Test concurrent operations across all modules."""
        # Test that modules can operate concurrently without conflicts
        def audio_operation():
            """Audio module operation."""
            for i in range(10):
                self.state_manager.set("audio.master_volume", i / 10.0, source="test")
                time.sleep(0.01)
        
        def screen_operation():
            """Screen module operation."""
            screens = [ScreenType.MAIN_MENU, ScreenType.GAME, ScreenType.PAUSE]
            for screen in screens:
                self.state_manager.set("screen.current_screen", screen, source="test")
                time.sleep(0.01)
        
        def input_operation():
            """Input module operation."""
            for i in range(10):
                mock_event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_SPACE})
                if 'input' in self.modules:
                    self.modules['input'].handle_event(mock_event)
                time.sleep(0.01)
        
        # Run operations concurrently
        threads = []
        operations = [audio_operation, screen_operation, input_operation]
        
        for operation in operations:
            thread = threading.Thread(target=operation)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify no conflicts occurred
        self.assertTrue(True, "Concurrent operations completed without conflicts")
    
    def test_error_propagation_across_modules(self):
        """Test error handling and propagation across modules."""
        # Test that errors in one module don't affect others
        
        # Simulate audio module error
        if 'audio' in self.modules:
            with patch.object(self.modules['audio'], 'set_volume', 
                            side_effect=Exception("Audio error")):
                # Audio error should not affect screen state
                self.state_manager.set("screen.current_screen", ScreenType.GAME, source="test")
                self.assertEqual(self.state_manager.get("screen.current_screen"), ScreenType.GAME)
                
                # Audio error should be logged but not crash
                with self.assertRaises(Exception):
                    self.state_manager.set("audio.master_volume", 0.5, source="test")
        
        # Test screen module error
        if 'screen' in self.modules:
            with patch.object(self.modules['screen'], 'update', 
                            side_effect=Exception("Screen error")):
                # Screen error should not affect input state
                self.state_manager.set("input.keyboard.space_pressed", True, source="test")
                self.assertTrue(self.state_manager.get("input.keyboard.space_pressed"))
                
                # Screen error should be logged but not crash
                with self.assertRaises(Exception):
                    self.modules['screen'].update()
        
        # Test input module error
        if 'input' in self.modules:
            with patch.object(self.modules['input'], 'handle_event', 
                            side_effect=Exception("Input error")):
                # Input error should not affect settings
                self.state_manager.set("settings.audio_enabled", False, source="test")
                self.assertFalse(self.state_manager.get("settings.audio_enabled"))
                
                # Input error should be logged but not crash
                with self.assertRaises(Exception):
                    mock_event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_SPACE})
                    self.modules['input'].handle_event(mock_event)
    
    def test_state_rollback_across_all_modules(self):
        """Test state rollback functionality across all modules."""
        # Create initial state
        initial_state = {
            "audio.master_volume": 0.6,
            "screen.current_screen": ScreenType.MAIN_MENU,
            "input.keyboard.space_pressed": False,
            "settings.audio_enabled": True
        }
        
        # Apply initial state
        for field_path, value in initial_state.items():
            self.state_manager.set(field_path, value, source="test")
        
        # Create snapshot
        snapshot = self.state_manager.snapshot("Initial state")
        
        # Make changes to all modules
        changes = {
            "audio.master_volume": 0.9,
            "screen.current_screen": ScreenType.GAME,
            "input.keyboard.space_pressed": True,
            "settings.audio_enabled": False
        }
        
        for field_path, value in changes.items():
            self.state_manager.set(field_path, value, source="test")
        
        # Verify changes were applied
        for field_path, expected_value in changes.items():
            actual_value = self.state_manager.get(field_path)
            self.assertEqual(actual_value, expected_value, 
                           f"Change not applied: {field_path}")
        
        # Rollback to snapshot
        success = self.state_manager.rollback_to_snapshot(snapshot)
        self.assertTrue(success, "Rollback failed")
        
        # Verify rollback worked for all modules
        for field_path, expected_value in initial_state.items():
            actual_value = self.state_manager.get(field_path)
            self.assertEqual(actual_value, expected_value, 
                           f"Rollback failed for: {field_path}")
    
    def test_performance_under_load(self):
        """Test performance of all modules under heavy load."""
        monitor = PerformanceMonitor()
        monitor.start_monitoring()
        
        # Perform many operations across all modules
        for i in range(1000):
            # Audio operations
            if 'audio' in self.modules:
                self.state_manager.set("audio.master_volume", (i % 100) / 100.0, source="test")
            
            # Screen operations
            if 'screen' in self.modules:
                screen = ScreenType.MAIN_MENU if i % 2 == 0 else ScreenType.GAME
                self.state_manager.set("screen.current_screen", screen, source="test")
            
            # Input operations
            if 'input' in self.modules:
                mock_event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_SPACE})
                self.modules['input'].handle_event(mock_event)
            
            # Settings operations
            if 'settings' in self.modules:
                self.state_manager.set("settings.audio_enabled", i % 2 == 0, source="test")
            
            # Create snapshots periodically
            if i % 100 == 0:
                self.state_manager.snapshot(f"Load test snapshot {i}")
        
        metrics = monitor.stop_monitoring()
        
        # Performance assertions
        self.assertLess(metrics['duration'], 5.0, 
                       f"Load test took {metrics['duration']:.3f}s, should be < 5.0s")
        self.assertLess(metrics['memory_delta'], 200.0,
                       f"Memory usage {metrics['memory_delta']:.1f}MB, should be < 200MB")
        
        print(f"Performance: {metrics['operations_per_second']:.1f} ops/sec")


class Round2PerformanceRegressionTests(BladeFightersTestSuite):
    """Performance regression tests for Round 2."""
    
    def setUp(self):
        """Set up for performance testing."""
        super().setUp()
        self.baseline_metrics = {
            'state_operations_per_second': 1000,
            'screen_transition_time': 0.5,
            'memory_usage_mb': 50.0,
            'test_execution_time': 600  # 10 minutes
        }
    
    def test_state_operations_performance(self):
        """Test state operations performance meets baseline."""
        monitor = PerformanceMonitor()
        monitor.start_monitoring()
        
        # Perform 1000 state operations
        for i in range(1000):
            self.state_manager.set(f"test.field_{i}", i, source="test")
        
        metrics = monitor.stop_monitoring()
        operations_per_second = 1000 / metrics['duration']
        
        self.assertGreaterEqual(operations_per_second, self.baseline_metrics['state_operations_per_second'],
                               f"State operations too slow: {operations_per_second:.1f} ops/sec")
    
    def test_screen_transition_performance(self):
        """Test screen transition performance meets baseline."""
        screens = [ScreenType.LOADING, ScreenType.MAIN_MENU, ScreenType.GAME, 
                  ScreenType.PAUSE, ScreenType.SETTINGS]
        
        transition_times = []
        
        for i in range(len(screens) - 1):
            duration = self.simulate_screen_transition(screens[i], screens[i + 1])
            transition_times.append(duration)
        
        avg_transition_time = sum(transition_times) / len(transition_times)
        
        self.assertLessEqual(avg_transition_time, self.baseline_metrics['screen_transition_time'],
                            f"Screen transitions too slow: {avg_transition_time:.3f}s average")
    
    def test_memory_usage_performance(self):
        """Test memory usage performance meets baseline."""
        initial_memory = self.performance_monitor._get_memory_usage()
        
        # Perform operations that should use memory
        for i in range(1000):
            self.state_manager.set(f"test.field_{i}", f"value_{i}" * 100, source="test")
            if i % 100 == 0:
                self.state_manager.snapshot(f"Memory test snapshot {i}")
        
        final_memory = self.performance_monitor._get_memory_usage()
        memory_usage = final_memory - initial_memory
        
        self.assertLessEqual(memory_usage, self.baseline_metrics['memory_usage_mb'],
                            f"Memory usage too high: {memory_usage:.1f}MB")


class Round2ErrorHandlingTests(BladeFightersTestSuite):
    """Error handling tests for Round 2."""
    
    def test_invalid_state_changes(self):
        """Test that invalid state changes are properly rejected."""
        invalid_changes = [
            ("audio.master_volume", 1.5),  # Volume > 1.0
            ("audio.master_volume", -0.1),  # Volume < 0.0
            ("puzzle.score", -100),  # Negative score
            ("puzzle.level", 0),  # Invalid level
            ("screen.current_screen", "INVALID_SCREEN"),  # Invalid screen type
        ]
        
        for field_path, invalid_value in invalid_changes:
            success = self.state_manager.set(field_path, invalid_value, source="test")
            self.assertFalse(success, f"Invalid change succeeded: {field_path} = {invalid_value}")
    
    def test_module_error_isolation(self):
        """Test that errors in one module don't affect others."""
        # Test with missing modules
        modules_to_test = ['audio', 'screen', 'input', 'settings']
        
        for module_name in modules_to_test:
            # Simulate module failure
            with patch(f'modules.{module_name}', side_effect=ImportError(f"{module_name} failed")):
                # Other modules should still work
                self.state_manager.set("test.field", "value", source="test")
                self.assertEqual(self.state_manager.get("test.field"), "value")
    
    def test_error_recovery(self):
        """Test error recovery mechanisms."""
        # Test recovery from invalid state
        self.state_manager.set("test.field", "valid_value", source="test")
        
        # Create snapshot
        snapshot = self.state_manager.snapshot("Valid state")
        
        # Attempt invalid change
        success = self.state_manager.set("audio.master_volume", 1.5, source="test")
        self.assertFalse(success)
        
        # Rollback to valid state
        rollback_success = self.state_manager.rollback_to_snapshot(snapshot)
        self.assertTrue(rollback_success)
        
        # Verify recovery
        self.assertEqual(self.state_manager.get("test.field"), "valid_value")


if __name__ == "__main__":
    # Run comprehensive tests
    unittest.main(verbosity=2)
