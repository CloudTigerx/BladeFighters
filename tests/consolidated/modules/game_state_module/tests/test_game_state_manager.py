"""
Tests for the Game State Management System
"""

import pytest
import time
import sys
import os
from unittest.mock import Mock, patch

# Add the project root to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from modules.game_state_module.game_state_manager import GameStateManager
from modules.game_state_module.state_schema import GameState, ScreenType, GameMode, PuzzleState
from modules.game_state_module.state_validator import ValidationError


class TestGameStateManager:
    """Test the GameStateManager class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.state_manager = GameStateManager()
    
    def test_initialization(self):
        """Test that the state manager initializes correctly."""
        assert self.state_manager.state is not None
        assert self.state_manager.state.game_running is True
        assert self.state_manager.state.screen.current_screen == ScreenType.LOADING
        assert self.state_manager.validator is not None
        assert self.state_manager.history is not None
    
    def test_get_set_basic(self):
        """Test basic get and set operations."""
        # Test setting a simple field
        success = self.state_manager.set("game_running", False, source="test")
        assert success is True
        assert self.state_manager.get("game_running") is False
        
        # Test getting with default
        assert self.state_manager.get("nonexistent_field", "default") == "default"
    
    def test_get_set_nested(self):
        """Test getting and setting nested fields."""
        # Test setting nested field
        success = self.state_manager.set("screen.current_screen", ScreenType.MAIN_MENU, source="test")
        assert success is True
        assert self.state_manager.get("screen.current_screen") == ScreenType.MAIN_MENU
        
        # Test setting another nested field
        success = self.state_manager.set("puzzle.score", 1000, source="test")
        assert success is True
        assert self.state_manager.get("puzzle.score") == 1000
    
    def test_validation(self):
        """Test state validation."""
        # Test valid change
        success = self.state_manager.set("puzzle.score", 500, source="test")
        assert success is True
        
        # Test invalid change (negative score)
        success = self.state_manager.set("puzzle.score", -100, source="test")
        assert success is False
        
        # Test invalid change (wrong type)
        success = self.state_manager.set("puzzle.score", "not_a_number", source="test")
        assert success is False
    
    def test_update_multiple(self):
        """Test updating multiple fields at once."""
        updates = {
            "puzzle.score": 2000,
            "puzzle.level": 5,
            "audio.master_volume": 0.8
        }
        
        results = self.state_manager.update(updates, source="test", description="Multiple updates")
        
        assert all(results.values())  # All updates should succeed
        assert self.state_manager.get("puzzle.score") == 2000
        assert self.state_manager.get("puzzle.level") == 5
        assert self.state_manager.get("audio.master_volume") == 0.8
    
    def test_snapshot_creation(self):
        """Test snapshot creation."""
        # Make some changes
        self.state_manager.set("puzzle.score", 1500, source="test")
        self.state_manager.set("screen.current_screen", ScreenType.GAME, source="test")
        
        # Create snapshot
        snapshot = self.state_manager.snapshot("Test snapshot", ["test"], {"test_data": "value"})
        
        assert snapshot is not None
        assert snapshot.description == "Test snapshot"
        assert "test" in snapshot.tags
        assert snapshot.metadata["test_data"] == "value"
        assert snapshot.state.puzzle.score == 1500
        assert snapshot.state.screen.current_screen == ScreenType.GAME
    
    def test_rollback_to_snapshot(self):
        """Test rolling back to a snapshot."""
        # Create initial state
        self.state_manager.set("puzzle.score", 1000, source="test")
        snapshot = self.state_manager.snapshot("Initial state")
        
        # Make changes
        self.state_manager.set("puzzle.score", 2000, source="test")
        self.state_manager.set("puzzle.level", 10, source="test")
        
        # Rollback
        success = self.state_manager.rollback_to_snapshot(snapshot)
        assert success is True
        
        # Check state is rolled back
        assert self.state_manager.get("puzzle.score") == 1000
        assert self.state_manager.get("puzzle.level") == 1  # Default value
    
    def test_callbacks(self):
        """Test state change callbacks."""
        callback_called = False
        callback_field = None
        callback_old_value = None
        callback_new_value = None
        
        def test_callback(field_path, old_value, new_value):
            nonlocal callback_called, callback_field, callback_old_value, callback_new_value
            callback_called = True
            callback_field = field_path
            callback_old_value = old_value
            callback_new_value = new_value
        
        # Add callback
        self.state_manager.add_change_callback("puzzle.score", test_callback)
        
        # Make change
        self.state_manager.set("puzzle.score", 3000, source="test")
        
        # Check callback was called
        assert callback_called is True
        assert callback_field == "puzzle.score"
        assert callback_old_value == 0  # Default value
        assert callback_new_value == 3000
    
    def test_global_callbacks(self):
        """Test global state change callbacks."""
        callback_called = False
        
        def global_callback(old_state, new_state):
            nonlocal callback_called
            callback_called = True
        
        # Add global callback
        self.state_manager.add_global_callback(global_callback)
        
        # Make change
        self.state_manager.set("puzzle.score", 4000, source="test")
        
        # Check callback was called
        assert callback_called is True
    
    def test_state_summary(self):
        """Test state summary generation."""
        # Set some values
        self.state_manager.set("puzzle.score", 5000, source="test")
        self.state_manager.set("puzzle.level", 15, source="test")
        self.state_manager.set("audio.master_volume", 0.9, source="test")
        
        summary = self.state_manager.get_state_summary()
        
        assert summary["score"] == 5000
        assert summary["level"] == 15
        assert summary["master_volume"] == 0.9
        assert summary["game_running"] is True
        assert "current_screen" in summary
        assert "fps" in summary
    
    def test_history_summary(self):
        """Test history summary generation."""
        # Make some changes to generate history
        self.state_manager.set("puzzle.score", 1000, source="test")
        self.state_manager.set("puzzle.score", 2000, source="test")
        self.state_manager.set("puzzle.score", 3000, source="test")
        
        summary = self.state_manager.get_history_summary()
        
        assert "total_snapshots" in summary
        assert "total_changes" in summary
        assert summary["total_changes"] >= 3  # At least our 3 changes
    
    def test_validation_errors(self):
        """Test validation error handling."""
        errors = self.state_manager.validate_state()
        
        # Initial state should be valid
        assert len(errors) == 0
        assert self.state_manager.is_state_valid() is True
    
    def test_export_state(self):
        """Test state export functionality."""
        export = self.state_manager.export_state()
        
        assert "state_summary" in export
        assert "history_summary" in export
        assert "validation_errors" in export
        assert "change_callbacks" in export
        assert "global_callbacks" in export
    
    def test_invalid_field_path(self):
        """Test handling of invalid field paths."""
        # Test setting invalid field
        success = self.state_manager.set("nonexistent.field", "value", source="test")
        assert success is False
        
        # Test getting invalid field
        value = self.state_manager.get("nonexistent.field", "default")
        assert value == "default"
    
    def test_performance_tracking(self):
        """Test that performance tracking works."""
        # Make several changes
        for i in range(10):
            self.state_manager.set("puzzle.score", i * 100, source="test")
        
        # Check that snapshots are created periodically
        summary = self.state_manager.get_history_summary()
        assert summary["total_changes"] >= 10


class TestStateValidator:
    """Test the StateValidator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.state_manager = GameStateManager()
        self.validator = self.state_manager.validator
    
    def test_screen_transition_validation(self):
        """Test screen transition validation."""
        # Valid transition
        errors = self.validator.validate_state_change(
            self.state_manager.state, 
            "screen.current_screen", 
            ScreenType.MAIN_MENU
        )
        assert len(errors) == 0
        
        # Invalid transition (loading to game)
        self.state_manager.set("screen.current_screen", ScreenType.LOADING, source="test")
        errors = self.validator.validate_state_change(
            self.state_manager.state,
            "screen.current_screen",
            ScreenType.GAME
        )
        assert len(errors) > 0
    
    def test_range_validation(self):
        """Test range validation."""
        # Valid range
        errors = self.validator.validate_state_change(
            self.state_manager.state,
            "puzzle.score",
            1000
        )
        assert len(errors) == 0
        
        # Invalid range (negative)
        errors = self.validator.validate_state_change(
            self.state_manager.state,
            "puzzle.score",
            -100
        )
        assert len(errors) > 0
    
    def test_type_validation(self):
        """Test type validation."""
        # Valid type
        errors = self.validator.validate_state_change(
            self.state_manager.state,
            "puzzle.game_active",
            True
        )
        assert len(errors) == 0
        
        # Invalid type
        errors = self.validator.validate_state_change(
            self.state_manager.state,
            "puzzle.game_active",
            "not_a_boolean"
        )
        assert len(errors) > 0


class TestStateHistory:
    """Test the StateHistory class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.state_manager = GameStateManager()
        self.history = self.state_manager.history
    
    def test_change_recording(self):
        """Test that changes are recorded."""
        # Make a change
        self.state_manager.set("puzzle.score", 1000, source="test")
        
        # Check that change was recorded
        changes = self.history.get_changes_for_field("puzzle.score")
        assert len(changes) >= 1
        assert changes[-1].new_value == 1000
        assert changes[-1].source == "test"
    
    def test_snapshot_retrieval(self):
        """Test snapshot retrieval methods."""
        # Create snapshots with different tags
        self.history.create_snapshot(self.state_manager.state, "Test 1", ["test1"])
        self.history.create_snapshot(self.state_manager.state, "Test 2", ["test2"])
        
        # Test retrieval by tag
        snapshot = self.history.get_snapshot_by_tag("test1")
        assert snapshot is not None
        assert "test1" in snapshot.tags
        
        # Test retrieval by description
        snapshot = self.history.get_snapshot_by_description("Test 2")
        assert snapshot is not None
        assert "Test 2" in snapshot.description
    
    def test_change_frequency(self):
        """Test change frequency calculation."""
        # Make several changes quickly
        for i in range(5):
            self.state_manager.set("puzzle.score", i * 100, source="test")
        
        summary = self.history.get_state_summary()
        assert "change_frequency" in summary
        assert summary["change_frequency"] > 0


if __name__ == "__main__":
    pytest.main([__file__]) 