"""
Comprehensive tests for the Unified Input Management System
==========================================================

Tests the unified input manager, compatibility layer, and integration
with the existing game systems.
"""

import sys
import os
import pytest
import pygame
import time
from unittest.mock import Mock, MagicMock

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

# Use absolute imports to avoid relative import issues
from modules.input_module.unified_input_manager import (
    UnifiedInputManager, InputAction, InputEvent, InputPriority
)
from modules.input_module.compatibility_layer import InputHandlerCompat
from modules.settings_module.unified_config import UnifiedConfigManager
from utils.clock import FakeClock


class TestUnifiedInputManager:
    """Test the core UnifiedInputManager functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        pygame.init()
        self.clock = FakeClock()
        self.config_manager = UnifiedConfigManager()
        self.input_manager = UnifiedInputManager(self.config_manager, self.clock)
    
    def teardown_method(self):
        """Clean up after tests."""
        pygame.quit()
    
    def test_initialization(self):
        """Test that the input manager initializes correctly."""
        assert self.input_manager is not None
        assert self.input_manager.clock == self.clock
        assert self.input_manager.config_manager == self.config_manager
        assert len(self.input_manager._keys_pressed) == 0
        assert not self.input_manager._external_lock
    
    def test_event_registration(self):
        """Test event handler registration."""
        handler = Mock()
        self.input_manager.register_event_handler(InputPriority.NORMAL, handler)
        assert handler in self.input_manager._event_handlers[InputPriority.NORMAL]
    
    def test_action_registration(self):
        """Test action handler registration."""
        handler = Mock()
        self.input_manager.register_action_handler(InputAction.MOVE_LEFT, handler)
        assert handler in self.input_manager._action_handlers[InputAction.MOVE_LEFT]
    
    def test_key_mapping(self):
        """Test key to action mapping."""
        # Test fallback mappings
        assert self.input_manager._map_key_to_action(pygame.K_LEFT) == InputAction.MOVE_LEFT
        assert self.input_manager._map_key_to_action(pygame.K_RIGHT) == InputAction.MOVE_RIGHT
        assert self.input_manager._map_key_to_action(pygame.K_UP) == InputAction.MOVE_UP
        assert self.input_manager._map_key_to_action(pygame.K_DOWN) == InputAction.MOVE_DOWN
        assert self.input_manager._map_key_to_action(pygame.K_SPACE) == InputAction.ACTION
        assert self.input_manager._map_key_to_action(pygame.K_ESCAPE) == InputAction.MENU_CANCEL
    
    def test_key_press_processing(self):
        """Test key press event processing."""
        # Create a keydown event
        event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_LEFT})
        events = [event]
        
        # Process events
        processed_events = self.input_manager.process_events(events)
        
        # Check that the event was processed
        assert len(processed_events) == 1
        assert processed_events[0].action == InputAction.MOVE_LEFT
        assert processed_events[0].is_pressed
        assert not processed_events[0].is_repeat
        assert processed_events[0].key_code == pygame.K_LEFT
    
    def test_key_release_processing(self):
        """Test key release event processing."""
        # First press the key
        press_event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_LEFT})
        self.input_manager.process_events([press_event])
        
        # Then release it
        release_event = pygame.event.Event(pygame.KEYUP, {'key': pygame.K_LEFT})
        processed_events = self.input_manager.process_events([release_event])
        
        # Check that the key is no longer pressed
        assert not self.input_manager.is_key_pressed(pygame.K_LEFT)
        assert len(processed_events) == 1
        assert not processed_events[0].is_pressed
    
    def test_key_repeat(self):
        """Test key repeat functionality."""
        # Press a key
        event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_LEFT})
        self.input_manager.process_events([event])
        
        # Advance time to trigger repeat
        self.clock.advance(150)  # More than DAS delay
        
        # Process events again to trigger repeat
        processed_events = self.input_manager.process_events([])
        
        # Should have a repeat event
        assert len(processed_events) == 1
        assert processed_events[0].is_repeat
        assert processed_events[0].action == InputAction.MOVE_LEFT
    
    def test_input_locking(self):
        """Test input locking functionality."""
        # Lock input
        self.input_manager.lock_input(1000, "test_lock")
        
        # Try to process events
        event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_LEFT})
        processed_events = self.input_manager.process_events([event])
        
        # Should be no events due to lock
        assert len(processed_events) == 0
        
        # Advance time past lock
        self.clock.advance(1100)
        
        # Try again
        processed_events = self.input_manager.process_events([event])
        assert len(processed_events) == 1
    
    def test_movement_gate(self):
        """Test movement gate functionality."""
        # Disable movement gate
        self.input_manager.set_movement_gate(False)
        
        # Press a movement key
        event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_LEFT})
        self.input_manager.process_events([event])
        
        # Advance time to trigger repeat
        self.clock.advance(150)
        
        # Process events - should not repeat due to gate
        processed_events = self.input_manager.process_events([])
        assert len(processed_events) == 0
    
    def test_system_events(self):
        """Test system event processing."""
        # Test quit event
        quit_event = pygame.event.Event(pygame.QUIT)
        processed_events = self.input_manager.process_events([quit_event])
        
        assert len(processed_events) == 1
        assert processed_events[0].action == InputAction.MENU_CANCEL
        assert processed_events[0].data.get("system_quit") is True
    
    def test_mouse_click_processing(self):
        """Test mouse click processing."""
        # Create a mouse click event
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {
            'button': 1,
            'pos': (100, 100)
        })
        processed_events = self.input_manager.process_events([event])
        
        assert len(processed_events) == 1
        assert processed_events[0].action == InputAction.ACTION
        assert processed_events[0].data.get("mouse_pos") == (100, 100)
    
    def test_configuration_reload(self):
        """Test configuration reloading."""
        # Set a configuration value
        self.config_manager.set("repeat_initial_delay_ms", 200)
        
        # Reload config
        self.input_manager.reload_config()
        
        # Check that the value was updated
        assert self.input_manager._repeat_config.das_ms == 200
    
    def test_event_logging(self):
        """Test event logging functionality."""
        # Enable logging
        self.input_manager.set_event_logging(True)
        
        # Process some events
        event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_LEFT})
        self.input_manager.process_events([event])
        
        # Check log
        log = self.input_manager.get_event_log()
        assert len(log) > 0
        assert log[-1]["action"] == "move_left"
    
    def test_status_reporting(self):
        """Test status reporting functionality."""
        status = self.input_manager.get_status()
        
        assert "pressed_keys_count" in status
        assert "external_lock" in status
        assert "movement_gate_enabled" in status
        assert "repeat_config" in status
        assert "is_input_locked" in status


class TestInputHandlerCompat:
    """Test the compatibility layer."""
    
    def setup_method(self):
        """Set up test fixtures."""
        pygame.init()
        self.clock = FakeClock()
        self.engine = Mock()
        self.engine.clock = self.clock
        self.engine.game_active = True
        self.engine.move_piece = Mock()
        self.engine.rotate_attached_piece = Mock()
        self.engine.flip_pieces_vertically = Mock()
        self.engine.place_piece_on_grid = Mock()
        
        self.input_handler = InputHandlerCompat(self.engine)
    
    def teardown_method(self):
        """Clean up after tests."""
        pygame.quit()
    
    def test_initialization(self):
        """Test that the compatibility layer initializes correctly."""
        assert self.input_handler is not None
        assert self.input_handler.engine == self.engine
        assert self.input_handler.unified_input is not None
        assert self.input_handler.is_falling is True
    
    def test_legacy_interface(self):
        """Test that the legacy interface still works."""
        # Test get_control
        key_code = self.input_handler.get_control('move_left')
        assert key_code == pygame.K_LEFT
        
        # Test is_key_pressed
        assert not self.input_handler.is_key_pressed('move_left')
    
    def test_event_processing(self):
        """Test event processing through the compatibility layer."""
        # Process a movement event
        event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_LEFT})
        result = self.input_handler.process_events([event])
        
        # Should call engine method
        self.engine.move_piece.assert_called_with(-1, 0)
        
        # Should return None (no menu action)
        assert result is None
    
    def test_menu_action(self):
        """Test menu action processing."""
        # Process escape key
        event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_ESCAPE})
        result = self.input_handler.process_events([event])
        
        # Should return menu action
        assert result == "back_to_menu"
    
    def test_movement_gate_callback(self):
        """Test movement gate callback integration."""
        # Disable movement gate
        self.input_handler.unified_input.set_movement_gate(False)
        
        # Check that the callback was called
        assert self.input_handler.is_falling is False
    
    def test_external_lock(self):
        """Test external lock functionality."""
        # Apply external lock
        self.input_handler.apply_external_lock(True)
        
        # Check that the unified input manager is locked
        assert self.input_handler.unified_input._external_lock is True
    
    def test_clear_key(self):
        """Test clearing specific keys."""
        # Press a key
        event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_SPACE})
        self.input_handler.process_events([event])
        
        # Clear the key
        self.input_handler.clear_spacebar_from_keys()
        
        # Check that the key is cleared
        assert not self.input_handler.is_key_pressed('action')
    
    def test_status_reporting(self):
        """Test status reporting through compatibility layer."""
        status = self.input_handler.get_status()
        
        # Should include both unified and legacy status
        assert "pressed_keys_count" in status
        assert "legacy_keys_pressed" in status
        assert "is_falling" in status
        assert "debug_spacebar" in status


class TestTestModeInputHandler:
    """Test the TestMode input handler integration."""
    
    def setup_method(self):
        """Set up test fixtures."""
        pygame.init()
        self.clock = FakeClock()
        self.ai_manager = Mock()
        self.game_state_manager = Mock()
        self.player_engine = Mock()
        self.player_engine.process_events = Mock()
        
        from modules.testmode_module.input_handler import InputHandler
        self.input_handler = InputHandler(
            self.ai_manager, 
            self.game_state_manager,
            config_manager=UnifiedConfigManager(),
            clock=self.clock
        )
    
    def teardown_method(self):
        """Clean up after tests."""
        pygame.quit()
    
    def test_initialization(self):
        """Test that the TestMode input handler initializes correctly."""
        assert self.input_handler is not None
        assert self.input_handler.unified_input is not None
        assert self.input_handler.ai_manager == self.ai_manager
        assert self.input_handler.game_state_manager == self.game_state_manager
    
    def test_ai_difficulty_controls(self):
        """Test AI difficulty control handling."""
        # Test number key 1
        event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_1})
        events = [event]
        
        # Process events
        result = self.input_handler.process_events(events, self.player_engine, 1000)
        
        # Should call AI manager
        self.ai_manager.set_difficulty.assert_called_with(1)
        assert result is None
    
    def test_ai_difficulty_adjustment(self):
        """Test AI difficulty adjustment."""
        # Test minus key
        event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_MINUS})
        events = [event]
        
        # Process events
        result = self.input_handler.process_events(events, self.player_engine, 1000)
        
        # Should call AI manager
        self.ai_manager.adjust_difficulty.assert_called_with(-1)
        assert result is None
    
    def test_menu_action(self):
        """Test menu action processing."""
        # Test escape key
        event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_ESCAPE})
        events = [event]
        
        # Process events
        result = self.input_handler.process_events(events, self.player_engine, 1000)
        
        # Should return menu action
        assert result == "back_to_menu"
    
    def test_input_lock_application(self):
        """Test input lock application."""
        # Mock game state manager to return locked state
        self.game_state_manager.is_player_input_locked.return_value = True
        
        # Process events
        events = []
        self.input_handler.process_events(events, self.player_engine, 1000)
        
        # Should apply lock to player engine
        self.player_engine.process_events.assert_called_with(events)


def test_integration_with_existing_systems():
    """Test integration with existing game systems."""
    pygame.init()
    clock = FakeClock()
    
    try:
        # Create unified input manager
        config_manager = UnifiedConfigManager()
        input_manager = UnifiedInputManager(config_manager, clock)
        
        # Test that it can process basic events
        event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_SPACE})
        processed_events = input_manager.process_events([event])
        
        assert len(processed_events) == 1
        assert processed_events[0].action == InputAction.ACTION
        
        # Test that it integrates with configuration
        config_manager.set("repeat_initial_delay_ms", 150)
        input_manager.reload_config()
        
        assert input_manager._repeat_config.das_ms == 150
        
    finally:
        pygame.quit()


if __name__ == "__main__":
    pytest.main([__file__]) 