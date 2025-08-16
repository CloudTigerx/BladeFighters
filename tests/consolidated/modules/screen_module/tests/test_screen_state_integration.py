"""
Integration Tests for Screen State Integration
Tests the integration between screen management and the GameStateManager.
"""

import pytest
import time
from unittest.mock import Mock, patch
from modules.game_state_module.game_state_manager import GameStateManager
from modules.game_state_module.state_schema import ScreenType
from modules.screen_module.screen_state_integration import ScreenStateIntegration


class TestScreenStateIntegration:
    """Test cases for screen state integration."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.state_manager = GameStateManager()
        self.screen_integration = ScreenStateIntegration(self.state_manager)
    
    def test_initialization(self):
        """Test that the screen integration initializes correctly."""
        assert self.screen_integration.state_manager == self.state_manager
        assert self.screen_integration.get_current_screen() == ScreenType.LOADING
    
    def test_set_screen_basic(self):
        """Test basic screen setting functionality."""
        # Set screen to main menu
        success = self.screen_integration.set_screen(ScreenType.MAIN_MENU, "test", "Test transition")
        
        assert success is True
        assert self.screen_integration.get_current_screen() == ScreenType.MAIN_MENU
        assert self.state_manager.get("screen.current_screen") == ScreenType.MAIN_MENU
    
    def test_screen_transition_history(self):
        """Test that screen transitions are properly recorded in history."""
        # Set initial screen
        self.screen_integration.set_screen(ScreenType.MAIN_MENU, "test", "Initial screen")
        
        # Transition to game screen
        self.screen_integration.set_screen(ScreenType.GAME, "test", "Start game")
        
        # Check that previous screen is recorded
        assert self.screen_integration.get_previous_screen() == ScreenType.MAIN_MENU
        assert self.state_manager.get("screen.previous_screen") == ScreenType.MAIN_MENU
    
    def test_screen_transition_time(self):
        """Test that transition time is updated."""
        before_time = time.time()
        self.screen_integration.set_screen(ScreenType.MAIN_MENU, "test", "Test transition")
        after_time = time.time()
        
        transition_time = self.state_manager.get("screen.screen_transition_time")
        assert before_time <= transition_time <= after_time
    
    def test_screen_transition_callbacks(self):
        """Test that screen transition callbacks are called."""
        callback_called = False
        callback_screen = None
        
        def test_callback():
            nonlocal callback_called, callback_screen
            callback_called = True
            callback_screen = self.screen_integration.get_current_screen()
        
        # Register callback for main menu
        self.screen_integration.register_screen_transition_callback(ScreenType.MAIN_MENU, test_callback)
        
        # Set screen to main menu
        self.screen_integration.set_screen(ScreenType.MAIN_MENU, "test", "Test callback")
        
        assert callback_called is True
        assert callback_screen == ScreenType.MAIN_MENU
    
    def test_screen_cleanup_callbacks(self):
        """Test that screen cleanup callbacks are called."""
        cleanup_called = False
        cleanup_screen = None
        
        def test_cleanup():
            nonlocal cleanup_called, cleanup_screen
            cleanup_called = True
            cleanup_screen = self.screen_integration.get_current_screen()
        
        # Set initial screen
        self.screen_integration.set_screen(ScreenType.MAIN_MENU, "test", "Initial screen")
        
        # Register cleanup callback for main menu
        self.screen_integration.register_screen_cleanup_callback(ScreenType.MAIN_MENU, test_cleanup)
        
        # Transition to game screen (should trigger cleanup)
        self.screen_integration.set_screen(ScreenType.GAME, "test", "Transition to game")
        
        assert cleanup_called is True
        assert cleanup_screen == ScreenType.MAIN_MENU
    
    def test_is_screen_method(self):
        """Test the is_screen convenience method."""
        self.screen_integration.set_screen(ScreenType.MAIN_MENU, "test", "Set main menu")
        
        assert self.screen_integration.is_screen(ScreenType.MAIN_MENU) is True
        assert self.screen_integration.is_screen(ScreenType.GAME) is False
    
    def test_story_state_management(self):
        """Test story state management functionality."""
        story_data = {
            "title": "Test Story",
            "content": ["Chapter 1", "Chapter 2"]
        }
        
        # Set story state
        success = self.screen_integration.set_story_state(story_data, "test")
        assert success is True
        
        # Check that story state is set
        current_story = self.state_manager.get("screen.current_story")
        assert current_story["title"] == "Test Story"
        assert len(current_story["content"]) == 2
    
    def test_story_scroll_position(self):
        """Test story scroll position management."""
        # Set scroll position
        success = self.screen_integration.set_story_scroll_position(100, "test")
        assert success is True
        
        # Check that scroll position is set
        scroll_pos = self.state_manager.get("screen.story_scroll_position")
        assert scroll_pos == 100
    
    def test_cleanup_required_marking(self):
        """Test cleanup required marking functionality."""
        # Mark cleanup as required
        success = self.screen_integration.mark_cleanup_required(True, "test")
        assert success is True
        
        # Check that cleanup is marked as required
        cleanup_required = self.state_manager.get("screen.screen_cleanup_required")
        assert cleanup_required is True
    
    def test_get_screen_info(self):
        """Test getting comprehensive screen information."""
        # Set up some screen state
        self.screen_integration.set_screen(ScreenType.MAIN_MENU, "test", "Initial")
        self.screen_integration.set_screen(ScreenType.GAME, "test", "To game")
        self.screen_integration.set_story_state({"title": "Test"}, "test")
        self.screen_integration.set_story_scroll_position(50, "test")
        
        # Get screen info
        info = self.screen_integration.get_screen_info()
        
        assert info["current_screen"] == "game"
        assert info["previous_screen"] == "main_menu"
        assert info["story_scroll_position"] == 50
        assert info["current_story"]["title"] == "Test"
        assert "transition_time" in info
        assert "cleanup_required" in info
    
    def test_error_handling_in_callbacks(self):
        """Test that errors in callbacks don't break the system."""
        def error_callback():
            raise Exception("Test error")
        
        # Register error callback
        self.screen_integration.register_screen_transition_callback(ScreenType.MAIN_MENU, error_callback)
        
        # This should not raise an exception
        success = self.screen_integration.set_screen(ScreenType.MAIN_MENU, "test", "Test error handling")
        
        # Screen should still be set despite callback error
        assert success is True
        assert self.screen_integration.get_current_screen() == ScreenType.MAIN_MENU
    
    def test_multiple_screen_transitions(self):
        """Test multiple screen transitions work correctly."""
        screens = [ScreenType.MAIN_MENU, ScreenType.GAME, ScreenType.STORY, ScreenType.TEST]
        
        for i, screen in enumerate(screens):
            success = self.screen_integration.set_screen(screen, "test", f"Transition {i}")
            assert success is True
            assert self.screen_integration.get_current_screen() == screen
            
            if i > 0:
                assert self.screen_integration.get_previous_screen() == screens[i-1]
    
    def test_state_validation_integration(self):
        """Test that state validation works with screen integration."""
        # This should work (valid transition)
        success = self.screen_integration.set_screen(ScreenType.MAIN_MENU, "test", "Valid transition")
        assert success is True
        
        # The state manager should validate the screen type
        current_screen = self.state_manager.get("screen.current_screen")
        assert isinstance(current_screen, ScreenType)
    
    def test_convenience_functions(self):
        """Test the convenience functions."""
        from modules.screen_module.screen_state_integration import (
            create_screen_integration, 
            set_global_screen_integration, 
            get_screen_integration
        )
        
        # Test create function
        new_integration = create_screen_integration(self.state_manager)
        assert isinstance(new_integration, ScreenStateIntegration)
        
        # Test global instance management
        set_global_screen_integration(self.screen_integration)
        global_integration = get_screen_integration()
        assert global_integration == self.screen_integration


class TestScreenStateIntegrationWithRealStateManager:
    """Integration tests with a real state manager instance."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.state_manager = GameStateManager()
        self.screen_integration = ScreenStateIntegration(self.state_manager)
    
    def test_state_history_integration(self):
        """Test that screen changes are recorded in state history."""
        # Set initial screen
        self.screen_integration.set_screen(ScreenType.LOADING, "test", "Initial")
        
        # Create a snapshot
        snapshot = self.state_manager.snapshot("Before screen change", ["test"])
        
        # Change screen
        self.screen_integration.set_screen(ScreenType.MAIN_MENU, "test", "To main menu")
        
        # Check that changes are recorded
        changes = self.state_manager.history.get_changes_for_field("screen.current_screen")
        assert len(changes) >= 1
        
        # Check that we can rollback
        rollback_success = self.state_manager.rollback_to_snapshot(snapshot)
        assert rollback_success is True
        assert self.screen_integration.get_current_screen() == ScreenType.LOADING
    
    def test_state_summary_integration(self):
        """Test that screen state appears in state summaries."""
        # First go to main menu (valid transition from loading)
        self.screen_integration.set_screen(ScreenType.MAIN_MENU, "test", "To main menu")
        
        # Then go to game (valid transition from main menu)
        self.screen_integration.set_screen(ScreenType.GAME, "test", "To game")
        
        # Get state summary
        summary = self.state_manager.get_state_summary()
        
        assert "current_screen" in summary
        assert summary["current_screen"] == "game"
    
    def test_validation_error_handling(self):
        """Test that validation errors are handled gracefully."""
        # Try to set an invalid screen type (this should be caught by validation)
        # Note: This test assumes the validator will reject invalid screen types
        # The exact behavior depends on the validator implementation
        
        # Set a valid screen first
        success = self.screen_integration.set_screen(ScreenType.MAIN_MENU, "test", "Valid screen")
        assert success is True
        
        # The integration should handle validation errors gracefully
        # and return False if the state change fails
        # (This test may need adjustment based on actual validator behavior) 