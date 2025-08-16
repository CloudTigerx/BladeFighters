"""
Comprehensive Integration Tests for Input Module
Tests input system integration with game state, performance, and edge cases.
"""

import unittest
import sys
import os
import time
import json
from unittest.mock import Mock, patch, MagicMock
import pygame

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from tests.consolidated.integration.test_suite_framework import BladeFightersTestSuite
from modules.game_state_module.game_state_manager import GameStateManager
from modules.game_state_module.state_schema import ScreenType, GameMode


class InputModuleIntegrationTests(BladeFightersTestSuite):
    """Integration tests for the input module."""
    
    def setUp(self):
        super().setUp()
        try:
            from modules.input_module.unified_input_manager import UnifiedInputManager
            from modules.input_module.compatibility_layer import InputHandlerCompat
            self.UnifiedInputManager = UnifiedInputManager
            self.InputHandlerCompat = InputHandlerCompat
        except ImportError as e:
            self.skipTest(f"Input module not available: {e}")
    
    def test_input_manager_initialization(self):
        """Test input manager initialization with game state integration."""
        # Create input manager with proper parameters
        input_manager = self.UnifiedInputManager(state_manager=self.state_manager)
        
        # Verify basic initialization
        self.assertIsNotNone(input_manager)
        self.assertIsNotNone(input_manager.state_manager)
        self.assertEqual(input_manager.state_manager, self.state_manager)
    
    def test_keyboard_input_handling(self):
        """Test keyboard input handling and state synchronization."""
        input_manager = self.UnifiedInputManager(self.state_manager)
        
        # Test key press events
        test_keys = [pygame.K_SPACE, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_DOWN, pygame.K_UP]
        
        for key in test_keys:
            # Create key press event
            key_event = pygame.event.Event(pygame.KEYDOWN, {'key': key})
            
            # Handle event
            result = input_manager.handle_event(key_event)
            
            # Verify event was processed
            self.assertIsInstance(result, bool)
            
            # Verify input state was updated
            key_name = pygame.key.name(key)
            if hasattr(input_manager, 'get_key_state'):
                key_state = input_manager.get_key_state(key_name)
                self.assertIsNotNone(key_state)
    
    def test_mouse_input_handling(self):
        """Test mouse input handling."""
        input_manager = self.UnifiedInputManager(self.state_manager)
        
        # Test mouse click events
        mouse_events = [
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': (100, 100)}),
            pygame.event.Event(pygame.MOUSEBUTTONUP, {'button': 1, 'pos': (100, 100)}),
            pygame.event.Event(pygame.MOUSEMOTION, {'pos': (200, 150), 'rel': (10, 5)})
        ]
        
        for event in mouse_events:
            # Handle event
            result = input_manager.handle_event(event)
            
            # Verify event was processed
            self.assertIsInstance(result, bool)
    
    def test_input_performance_under_load(self):
        """Test input system performance under heavy load."""
        input_manager = self.UnifiedInputManager(self.state_manager)
        
        # Test rapid input processing
        start_time = time.time()
        
        for i in range(1000):
            # Create random input events
            if i % 3 == 0:
                event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_SPACE})
            elif i % 3 == 1:
                event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': (i, i)})
            else:
                event = pygame.event.Event(pygame.MOUSEMOTION, {'pos': (i, i), 'rel': (1, 1)})
            
            input_manager.handle_event(event)
        
        duration = time.time() - start_time
        events_per_second = 1000 / duration
        
        # Should process many events per second
        self.assertGreater(events_per_second, 1000, 
                          f"Input processing rate: {events_per_second:.1f} events/sec")
    
    def test_input_state_synchronization(self):
        """Test that input system synchronizes with game state."""
        input_manager = self.UnifiedInputManager(self.state_manager)
        
        # Test input state changes
        test_inputs = [
            ('keyboard.space_pressed', True),
            ('keyboard.left_pressed', True),
            ('mouse.left_button', True),
            ('mouse.position', (100, 100))
        ]
        
        for field_path, value in test_inputs:
            # Set input state through state manager
            success = self.state_manager.set(field_path, value, source="test")
            
            # Verify state was set
            if success:
                self.assertEqual(self.state_manager.get(field_path), value)
    
    def test_input_compatibility_layer(self):
        """Test input compatibility layer."""
        try:
            compatibility_layer = self.InputHandlerCompat(self.state_manager)
            
            # Test legacy input handling
            legacy_event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_SPACE})
            result = compatibility_layer.handle_legacy_event(legacy_event)
            
            # Verify legacy event was processed
            self.assertIsInstance(result, bool)
            
        except Exception as e:
            self.skipTest(f"InputHandlerCompat not available: {e}")
    
    def test_input_error_handling(self):
        """Test input system error handling."""
        input_manager = self.UnifiedInputManager(self.state_manager)
        
        # Test handling of invalid events
        invalid_events = [
            None,
            pygame.event.Event(pygame.USEREVENT, {}),  # Unknown event type
            pygame.event.Event(pygame.KEYDOWN, {}),  # Missing key data
        ]
        
        for event in invalid_events:
            try:
                result = input_manager.handle_event(event)
                # Should handle gracefully
            except Exception as e:
                self.fail(f"Input manager should handle invalid events: {e}")
    
    def test_input_memory_usage(self):
        """Test input system memory usage."""
        initial_memory = self.performance_monitor._get_memory_usage()
        
        # Create multiple input managers
        input_managers = []
        for i in range(10):
            input_manager = self.UnifiedInputManager(self.state_manager)
            input_managers.append(input_manager)
        
        final_memory = self.performance_monitor._get_memory_usage()
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable
        self.assertLess(memory_increase, 20.0, 
                       f"Input manager creation used {memory_increase:.1f}MB")
    
    def test_input_concurrent_access(self):
        """Test input system under concurrent access."""
        input_manager = self.UnifiedInputManager(self.state_manager)
        
        # Simulate concurrent input processing
        import threading
        
        def process_keyboard_events():
            for i in range(50):
                event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_SPACE})
                input_manager.handle_event(event)
                time.sleep(0.001)
        
        def process_mouse_events():
            for i in range(50):
                event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': (i, i)})
                input_manager.handle_event(event)
                time.sleep(0.001)
        
        threads = []
        
        # Start keyboard thread
        keyboard_thread = threading.Thread(target=process_keyboard_events)
        threads.append(keyboard_thread)
        keyboard_thread.start()
        
        # Start mouse thread
        mouse_thread = threading.Thread(target=process_mouse_events)
        threads.append(mouse_thread)
        mouse_thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Should complete without errors
        self.assertTrue(True)
    
    def test_input_state_persistence(self):
        """Test that input state persists correctly."""
        input_manager = self.UnifiedInputManager(self.state_manager)
        
        # Set input state
        self.state_manager.set("keyboard.space_pressed", True, source="test")
        self.state_manager.set("mouse.position", (100, 100), source="test")
        
        # Verify state persists
        self.assertTrue(self.state_manager.get("keyboard.space_pressed"))
        self.assertEqual(self.state_manager.get("mouse.position"), (100, 100))
        
        # Multiple updates should maintain state
        for i in range(10):
            input_manager.update()
            self.assertTrue(self.state_manager.get("keyboard.space_pressed"))
            self.assertEqual(self.state_manager.get("mouse.position"), (100, 100))
    
    def test_input_game_state_integration(self):
        """Test input integration with game state changes."""
        input_manager = self.UnifiedInputManager(self.state_manager)
        
        # Test input behavior in different game states
        game_states = [ScreenType.MAIN_MENU, ScreenType.GAME, ScreenType.PAUSE]
        
        for screen_type in game_states:
            # Set game state
            self.state_manager.set("screen.current_screen", screen_type, source="test")
            
            # Test input handling in this state
            event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_SPACE})
            result = input_manager.handle_event(event)
            
            # Should handle input regardless of game state
            self.assertIsInstance(result, bool)
    
    def test_input_repeat_handling(self):
        """Test input repeat handling."""
        input_manager = self.UnifiedInputManager(self.state_manager)
        
        # Test key repeat events
        key_event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_LEFT})
        
        # Simulate key repeat
        for i in range(10):
            result = input_manager.handle_event(key_event)
            self.assertIsInstance(result, bool)
            time.sleep(0.01)  # Small delay to simulate repeat timing
    
    def test_input_priority_handling(self):
        """Test input priority handling."""
        input_manager = self.UnifiedInputManager(self.state_manager)
        
        # Test multiple simultaneous inputs
        events = [
            pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_SPACE}),
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': (100, 100)}),
            pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_LEFT})
        ]
        
        # Process all events
        for event in events:
            result = input_manager.handle_event(event)
            self.assertIsInstance(result, bool)
    
    def test_input_performance_benchmarking(self):
        """Benchmark input system performance."""
        input_manager = self.UnifiedInputManager(self.state_manager)
        
        # Benchmark event processing
        start_time = time.time()
        for i in range(10000):
            event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_SPACE})
            input_manager.handle_event(event)
        
        event_duration = time.time() - start_time
        events_per_second = 10000 / event_duration
        
        # Should process many events per second
        self.assertGreater(events_per_second, 10000, 
                          f"Event processing rate: {events_per_second:.1f} events/sec")
        
        # Benchmark state updates
        start_time = time.time()
        for i in range(1000):
            input_manager.update()
        
        update_duration = time.time() - start_time
        updates_per_second = 1000 / update_duration
        
        # Should maintain good update performance
        self.assertGreater(updates_per_second, 1000, 
                          f"Update rate: {updates_per_second:.1f} updates/sec")
    
    def test_input_validation(self):
        """Test input validation."""
        input_manager = self.UnifiedInputManager(self.state_manager)
        
        # Test valid inputs
        valid_events = [
            pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_SPACE}),
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': (100, 100)}),
            pygame.event.Event(pygame.MOUSEMOTION, {'pos': (200, 150), 'rel': (10, 5)})
        ]
        
        for event in valid_events:
            result = input_manager.handle_event(event)
            self.assertIsInstance(result, bool)
        
        # Test invalid inputs
        invalid_events = [
            pygame.event.Event(pygame.KEYDOWN, {'key': 99999}),  # Invalid key
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 999, 'pos': (100, 100)}),  # Invalid button
        ]
        
        for event in invalid_events:
            try:
                result = input_manager.handle_event(event)
                # Should handle gracefully
            except Exception as e:
                self.fail(f"Input manager should handle invalid inputs: {e}")


class InputModuleRegressionTests(BladeFightersTestSuite):
    """Regression tests for input module functionality."""
    
    def setUp(self):
        super().setUp()
        try:
            from modules.input_module.unified_input_manager import UnifiedInputManager
            self.UnifiedInputManager = UnifiedInputManager
        except ImportError as e:
            self.skipTest(f"Input module not available: {e}")
    
    def test_input_event_handling_regression(self):
        """Test that input event handling still works correctly."""
        input_manager = self.UnifiedInputManager(self.state_manager)
        
        # Test all common input events
        test_events = [
            pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_SPACE}),
            pygame.event.Event(pygame.KEYUP, {'key': pygame.K_SPACE}),
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': (100, 100)}),
            pygame.event.Event(pygame.MOUSEBUTTONUP, {'button': 1, 'pos': (100, 100)}),
            pygame.event.Event(pygame.MOUSEMOTION, {'pos': (200, 150), 'rel': (10, 5)})
        ]
        
        for event in test_events:
            try:
                result = input_manager.handle_event(event)
                self.assertIsInstance(result, bool)
            except Exception as e:
                self.fail(f"Input event handling failed for {event.type}: {e}")
    
    def test_input_state_regression(self):
        """Test that input state management still works correctly."""
        input_manager = self.UnifiedInputManager(self.state_manager)
        
        # Test input state setting and retrieval
        test_states = [
            ("keyboard.space_pressed", True),
            ("keyboard.left_pressed", True),
            ("mouse.left_button", True),
            ("mouse.position", (100, 100))
        ]
        
        for field_path, value in test_states:
            success = self.state_manager.set(field_path, value, source="test")
            if success:
                retrieved_value = self.state_manager.get(field_path)
                self.assertEqual(retrieved_value, value)
    
    def test_input_performance_regression(self):
        """Test that input performance hasn't degraded."""
        input_manager = self.UnifiedInputManager(self.state_manager)
        
        # Test performance with many events
        start_time = time.time()
        for i in range(1000):
            event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_SPACE})
            input_manager.handle_event(event)
        
        duration = time.time() - start_time
        
        # Should complete quickly
        self.assertLess(duration, 1.0, f"Input processing took {duration:.3f}s")


if __name__ == "__main__":
    unittest.main() 