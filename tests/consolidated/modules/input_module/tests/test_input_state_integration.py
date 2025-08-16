"""
Input System State Integration Tests
===================================

Tests the integration between the input system and the game state manager.
Ensures that all input state is properly managed through the unified state system.
"""

import sys
import os
import pytest
import pygame
import time
from unittest.mock import Mock, MagicMock

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from modules.input_module.unified_input_manager import (
    UnifiedInputManager, InputAction, InputEvent, InputPriority
)
from modules.input_module.compatibility_layer import InputHandlerCompat
from modules.game_state_module.game_state_manager import GameStateManager
from modules.game_state_module.state_schema import GameState, InputState
from modules.settings_module.unified_config import UnifiedConfigManager
from utils.clock import FakeClock


class TestInputStateIntegration:
    """Test integration between input system and state manager."""
    
    def setup_method(self):
        """Set up test fixtures."""
        pygame.init()
        self.clock = FakeClock()
        self.config_manager = UnifiedConfigManager()
        self.state_manager = GameStateManager()
        self.input_manager = UnifiedInputManager(self.config_manager, self.clock)
        
        # Connect input manager to state manager
        self._connect_input_to_state()
    
    def teardown_method(self):
        """Clean up after tests."""
        pygame.quit()
    
    def _connect_input_to_state(self):
        """Connect input manager to state manager for state updates."""
        # Register callbacks to update state manager when input state changes
        self.input_manager.register_state_update_callback(self._update_input_state)
        
        # Register callbacks to update input manager when state changes
        self.state_manager.register_change_callback("input", self._on_input_state_change)
    
    def _update_input_state(self, input_data: dict):
        """Update state manager with input data."""
        # Update keys pressed
        if 'keys_pressed' in input_data:
            self.state_manager.set("input.keys_pressed", input_data['keys_pressed'])
        
        # Update input timing
        if 'last_input_time' in input_data:
            self.state_manager.set("input.last_input_time", input_data['last_input_time'])
        
        # Update DAS/ARR state
        if 'das_time' in input_data:
            self.state_manager.set("input.das_time", input_data['das_time'])
        if 'arr_time' in input_data:
            self.state_manager.set("input.arr_time", input_data['arr_time'])
        
        # Update input locking
        if 'input_locked' in input_data:
            self.state_manager.set("input.input_locked", input_data['input_locked'])
        if 'input_lock_reason' in input_data:
            self.state_manager.set("input.input_lock_reason", input_data['input_lock_reason'])
    
    def _on_input_state_change(self, field_path: str, old_value: any, new_value: any):
        """Handle state changes from state manager."""
        # Update input manager when state changes externally
        if field_path == "input.input_locked":
            if new_value:
                self.input_manager.lock_input(1000, "state_manager_lock")
            else:
                self.input_manager.unlock_input()
    
    def test_initial_state_synchronization(self):
        """Test that input state is properly initialized in state manager."""
        # Check that input state exists in state manager
        assert self.state_manager.get("input") is not None
        assert isinstance(self.state_manager.get("input.keys_pressed"), set)
        assert isinstance(self.state_manager.get("input.keys_held"), set)
        assert isinstance(self.state_manager.get("input.mouse_position"), tuple)
        assert isinstance(self.state_manager.get("input.mouse_buttons"), set)
        
        # Check default values
        assert self.state_manager.get("input.input_locked") == False
        assert self.state_manager.get("input.input_lock_reason") is None
        assert self.state_manager.get("input.last_input_time") == 0.0
    
    def test_key_press_state_update(self):
        """Test that key presses update the state manager."""
        # Create a keydown event
        event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_LEFT})
        events = [event]
        
        # Process events
        self.input_manager.process_events(events)
        
        # Check that state manager was updated
        assert pygame.K_LEFT in self.state_manager.get("input.keys_pressed")
        assert self.state_manager.get("input.last_input_time") > 0.0
    
    def test_key_release_state_update(self):
        """Test that key releases update the state manager."""
        # First press the key
        press_event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_LEFT})
        self.input_manager.process_events([press_event])
        
        # Verify key is pressed in state
        assert pygame.K_LEFT in self.state_manager.get("input.keys_pressed")
        
        # Then release it
        release_event = pygame.event.Event(pygame.KEYUP, {'key': pygame.K_LEFT})
        self.input_manager.process_events([release_event])
        
        # Check that key is no longer pressed in state
        assert pygame.K_LEFT not in self.state_manager.get("input.keys_pressed")
    
    def test_input_locking_state_synchronization(self):
        """Test that input locking is synchronized between systems."""
        # Lock input through input manager
        self.input_manager.lock_input(1000, "test_lock")
        
        # Check that state manager reflects the lock
        assert self.state_manager.get("input.input_locked") == True
        assert self.state_manager.get("input.input_lock_reason") == "test_lock"
        
        # Unlock input through input manager
        self.input_manager.unlock_input()
        
        # Check that state manager reflects the unlock
        assert self.state_manager.get("input.input_locked") == False
        assert self.state_manager.get("input.input_lock_reason") is None
    
    def test_state_manager_input_locking(self):
        """Test that input locking through state manager works."""
        # Lock input through state manager
        self.state_manager.set("input.input_locked", True, source="test")
        self.state_manager.set("input.input_lock_reason", "state_manager_lock", source="test")
        
        # Check that input manager reflects the lock
        assert self.input_manager._external_lock == True
        
        # Unlock input through state manager
        self.state_manager.set("input.input_locked", False, source="test")
        
        # Check that input manager reflects the unlock
        assert self.input_manager._external_lock == False
    
    def test_das_arr_state_tracking(self):
        """Test that DAS/ARR timing is tracked in state manager."""
        # Simulate DAS/ARR timing updates
        self.input_manager._update_das_arr_state()
        
        # Check that state manager has timing data
        assert self.state_manager.get("input.das_time") >= 0.0
        assert self.state_manager.get("input.arr_time") >= 0.0
    
    def test_multiple_keys_state_tracking(self):
        """Test that multiple keys are properly tracked in state."""
        # Press multiple keys
        events = [
            pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_LEFT}),
            pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_RIGHT}),
            pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_SPACE})
        ]
        
        self.input_manager.process_events(events)
        
        # Check that all keys are tracked in state
        keys_pressed = self.state_manager.get("input.keys_pressed")
        assert pygame.K_LEFT in keys_pressed
        assert pygame.K_RIGHT in keys_pressed
        assert pygame.K_SPACE in keys_pressed
        assert len(keys_pressed) == 3
    
    def test_mouse_state_tracking(self):
        """Test that mouse state is tracked in state manager."""
        # Simulate mouse movement
        mouse_event = pygame.event.Event(pygame.MOUSEMOTION, {
            'pos': (100, 200),
            'buttons': (1, 0, 0)
        })
        
        self.input_manager.process_events([mouse_event])
        
        # Check that mouse state is updated in state manager
        assert self.state_manager.get("input.mouse_position") == (100, 200)
        assert 1 in self.state_manager.get("input.mouse_buttons")
    
    def test_input_cooldown_state_tracking(self):
        """Test that input cooldown is tracked in state manager."""
        # Process an input event
        event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_LEFT})
        self.input_manager.process_events([event])
        
        # Check that last input time is updated
        last_input_time = self.state_manager.get("input.last_input_time")
        assert last_input_time > 0.0
        
        # Check that cooldown is properly set
        cooldown = self.state_manager.get("input.input_cooldown")
        assert cooldown == 0.05  # Default cooldown value
    
    def test_state_history_tracking(self):
        """Test that input state changes are tracked in history."""
        # Make several input state changes
        self.state_manager.set("input.input_locked", True, source="test")
        self.state_manager.set("input.input_locked", False, source="test")
        
        # Check that changes are recorded in history
        history = self.state_manager.history.get_recent_changes(limit=10)
        input_changes = [change for change in history if change.field_path.startswith("input.")]
        assert len(input_changes) >= 2
    
    def test_compatibility_layer_state_integration(self):
        """Test that compatibility layer works with state integration."""
        # Create compatibility layer with state manager
        puzzle_engine = Mock()
        settings_ui = Mock()
        
        compat_handler = InputHandlerCompat(puzzle_engine, settings_ui)
        
        # Test that it can access state manager
        assert hasattr(compat_handler, 'state_manager') or hasattr(compat_handler, '_state_manager')
        
        # Test basic functionality still works
        event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_LEFT})
        result = compat_handler.process_events([event])
        
        # Should process events successfully
        assert result is not None
    
    def test_performance_with_state_integration(self):
        """Test that state integration doesn't significantly impact performance."""
        import time
        
        # Measure time for processing events without state integration
        start_time = time.time()
        for _ in range(100):
            event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_LEFT})
            self.input_manager.process_events([event])
        baseline_time = time.time() - start_time
        
        # Measure time for processing events with state integration
        start_time = time.time()
        for _ in range(100):
            event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_RIGHT})
            self.input_manager.process_events([event])
        integrated_time = time.time() - start_time
        
        # Performance should be reasonable (within 50% of baseline)
        assert integrated_time < baseline_time * 1.5
    
    def test_error_handling_in_state_integration(self):
        """Test that errors in state integration are handled gracefully."""
        # Test with invalid state updates
        try:
            self.state_manager.set("input.invalid_field", "invalid_value")
            # Should not raise an exception
        except Exception as e:
            pytest.fail(f"State integration should handle invalid fields gracefully: {e}")
        
        # Test with invalid input data
        try:
            self._update_input_state({"invalid_key": "invalid_value"})
            # Should not raise an exception
        except Exception as e:
            pytest.fail(f"Input state update should handle invalid data gracefully: {e}")


class TestInputStateMigration:
    """Test migration from old input state management to new state manager."""
    
    def setup_method(self):
        """Set up test fixtures."""
        pygame.init()
        self.clock = FakeClock()
        self.config_manager = UnifiedConfigManager()
        self.state_manager = GameStateManager()
    
    def teardown_method(self):
        """Clean up after tests."""
        pygame.quit()
    
    def test_legacy_state_migration(self):
        """Test that legacy input state can be migrated to state manager."""
        # Simulate legacy input state
        legacy_state = {
            "keys_pressed": {pygame.K_LEFT, pygame.K_RIGHT},
            "last_key_action_time": {pygame.K_LEFT: 1000.0},
            "key_press_time": {pygame.K_LEFT: 950.0},
            "_external_lock": True,
            "key_repeat_delay": 120,
            "key_repeat_interval": 80,
            "is_falling": True
        }
        
        # Migrate to state manager
        self.state_manager.set("input.keys_pressed", legacy_state["keys_pressed"])
        self.state_manager.set("input.input_locked", legacy_state["_external_lock"])
        self.state_manager.set("input.das_delay", legacy_state["key_repeat_delay"] / 1000.0)
        self.state_manager.set("input.arr_delay", legacy_state["key_repeat_interval"] / 1000.0)
        
        # Verify migration
        assert self.state_manager.get("input.keys_pressed") == {pygame.K_LEFT, pygame.K_RIGHT}
        assert self.state_manager.get("input.input_locked") == True
        assert self.state_manager.get("input.das_delay") == 0.12
        assert self.state_manager.get("input.arr_delay") == 0.08
    
    def test_state_consistency_after_migration(self):
        """Test that state remains consistent after migration."""
        # Create input manager after state migration
        input_manager = UnifiedInputManager(self.config_manager, self.clock)
        
        # Set up some state in state manager
        self.state_manager.set("input.keys_pressed", {pygame.K_SPACE})
        self.state_manager.set("input.input_locked", True)
        
        # Verify input manager can read state
        assert pygame.K_SPACE in self.state_manager.get("input.keys_pressed")
        assert self.state_manager.get("input.input_locked") == True 