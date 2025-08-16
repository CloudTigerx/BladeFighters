"""
Tests for Puzzle Engine State Integration
Tests the integration between puzzle engine and unified state management.
"""

import pytest
import time
from unittest.mock import Mock, MagicMock
from typing import Dict, Any

from ..game_state_manager import GameStateManager
from ..state_schema import GameState, PuzzleState, GameMode
from ..puzzle_integration import PuzzleStateIntegrator, PuzzleStateMapping


class MockPuzzleEngine:
    """Mock puzzle engine for testing."""
    
    def __init__(self):
        # Core game state
        self.game_active = False
        self.score = 0
        self.clusters = set()
        self.chain_reaction_in_progress = False
        self.chain_count = 0
        
        # Grid state
        self.grid_width = 6
        self.grid_height = 15
        self.total_grid_height = 16
        self.block_size = 40
        self.puzzle_grid = [[None for _ in range(6)] for _ in range(16)]
        
        # Piece state
        self.main_piece = None
        self.attached_piece = None
        self.next_main_piece = None
        self.next_attached_piece = None
        self.piece_position = [0, 0]
        self.attached_position = 0
        
        # Timing state
        self.last_fall_time = 0.0
        self.current_fall_speed = 640000
        self.normal_fall_speed = 640000
        self.accelerated_fall_speed = 2400
        self.micro_fall_time = 0.016
        
        # Animation state
        self.breaking_animation_start = 0.0
        self.breaking_animation_duration = 0.16
        
        # Debug state
        self.debug_breaks = True
        self.enable_debug_logs = False
        
        # Wall kick state
        self.last_wall_kick_time = 0.0
        self.wall_kick_count = 0
        self.max_wall_kicks = 2
        
        # Flip state
        self.last_flip_time = 0.0
        self.flip_cooldown = 50
        
        # Sub-grid positioning
        self.sub_grid_positions = 20
        self.current_sub_position = 0
        
        # Game mechanics state
        self.breaking_blocks = []
        self.chain_state = "idle"


class TestPuzzleStateIntegrator:
    """Test the PuzzleStateIntegrator class."""
    
    @pytest.fixture
    def state_manager(self):
        """Create a fresh state manager for each test."""
        return GameStateManager()
    
    @pytest.fixture
    def puzzle_engine(self):
        """Create a mock puzzle engine for each test."""
        return MockPuzzleEngine()
    
    @pytest.fixture
    def integrator(self, state_manager, puzzle_engine):
        """Create a puzzle state integrator for each test."""
        return PuzzleStateIntegrator(state_manager, puzzle_engine)
    
    def test_initialization(self, integrator, state_manager, puzzle_engine):
        """Test that the integrator initializes correctly."""
        assert integrator.state_manager == state_manager
        assert integrator.puzzle_engine == puzzle_engine
        assert integrator.integration_active == False
        assert len(integrator.state_mappings) > 0
        
        # Check that mappings are properly structured
        for mapping in integrator.state_mappings:
            assert hasattr(mapping, 'engine_attr')
            assert hasattr(mapping, 'state_path')
            assert hasattr(mapping, 'description')
    
    def test_start_integration(self, integrator):
        """Test starting the integration process."""
        integrator.start_integration()
        assert integrator.integration_active == True
    
    def test_stop_integration(self, integrator):
        """Test stopping the integration process."""
        integrator.start_integration()
        integrator.stop_integration()
        assert integrator.integration_active == False
    
    def test_initial_sync(self, integrator, state_manager, puzzle_engine):
        """Test initial synchronization of state."""
        # Set some values in the puzzle engine
        puzzle_engine.game_active = True
        puzzle_engine.score = 100
        puzzle_engine.clusters = {(1, 1), (2, 2)}
        
        integrator.start_integration()
        
        # Check that values were synced to state manager
        assert state_manager.get("puzzle.game_active") == True
        assert state_manager.get("puzzle.score") == 100
        assert state_manager.get("puzzle.clusters") == {(1, 1), (2, 2)}
    
    def test_sync_to_state_manager(self, integrator, state_manager, puzzle_engine):
        """Test syncing puzzle engine state to state manager."""
        integrator.start_integration()
        
        # Change values in puzzle engine
        puzzle_engine.game_active = True
        puzzle_engine.score = 200
        
        # Sync to state manager
        integrator.sync_to_state_manager()
        
        # Check that values were synced
        assert state_manager.get("puzzle.game_active") == True
        assert state_manager.get("puzzle.score") == 200
    
    def test_sync_from_state_manager(self, integrator, state_manager, puzzle_engine):
        """Test syncing state manager values back to puzzle engine."""
        integrator.start_integration()
        
        # Set values in state manager
        state_manager.set("puzzle.game_active", True)
        state_manager.set("puzzle.score", 300)
        
        # Sync from state manager
        integrator.sync_from_state_manager()
        
        # Check that values were synced to puzzle engine
        assert puzzle_engine.game_active == True
        assert puzzle_engine.score == 300
    
    def test_update_puzzle_state(self, integrator, state_manager):
        """Test updating puzzle state enum."""
        integrator.update_puzzle_state(PuzzleState.ACTIVE)
        assert state_manager.get("puzzle.puzzle_state") == PuzzleState.ACTIVE
        
        integrator.update_puzzle_state(PuzzleState.CHAIN_REACTION)
        assert state_manager.get("puzzle.puzzle_state") == PuzzleState.CHAIN_REACTION
    
    def test_get_puzzle_state(self, integrator, state_manager):
        """Test getting puzzle state from state manager."""
        # Default state should be IDLE
        assert integrator.get_puzzle_state() == PuzzleState.IDLE
        
        # Set state and check
        state_manager.set("puzzle.puzzle_state", PuzzleState.ACTIVE)
        assert integrator.get_puzzle_state() == PuzzleState.ACTIVE
    
    def test_set_game_active(self, integrator, state_manager, puzzle_engine):
        """Test setting game active status."""
        integrator.set_game_active(True)
        assert state_manager.get("puzzle.game_active") == True
        assert puzzle_engine.game_active == True
        
        integrator.set_game_active(False)
        assert state_manager.get("puzzle.game_active") == False
        assert puzzle_engine.game_active == False
    
    def test_is_game_active(self, integrator, state_manager):
        """Test checking if game is active."""
        assert integrator.is_game_active() == False
        
        state_manager.set("puzzle.game_active", True)
        assert integrator.is_game_active() == True
    
    def test_cluster_management(self, integrator, state_manager):
        """Test cluster management methods."""
        clusters = {(1, 1), (2, 2), (3, 3)}
        
        integrator.set_clusters(clusters)
        assert integrator.get_clusters() == clusters
        assert state_manager.get("puzzle.clusters") == clusters
    
    def test_score_management(self, integrator, state_manager):
        """Test score management methods."""
        # Initial score should be 0
        assert integrator.get_score() == 0
        
        # Add score
        integrator.add_score(100)
        assert integrator.get_score() == 100
        
        # Add more score
        integrator.add_score(50)
        assert integrator.get_score() == 150
    
    def test_reset_game_state(self, integrator, state_manager):
        """Test resetting game state."""
        # Set some initial state
        state_manager.set("puzzle.game_active", True)
        state_manager.set("puzzle.score", 1000)
        state_manager.set("puzzle.clusters", {(1, 1)})
        state_manager.set("puzzle.chain_count", 5)
        
        # Reset game state
        integrator.reset_game_state()
        
        # Check that state was reset
        assert state_manager.get("puzzle.game_active") == False
        assert state_manager.get("puzzle.score") == 0
        assert state_manager.get("puzzle.clusters") == set()
        assert state_manager.get("puzzle.chain_count") == 0
        assert state_manager.get("puzzle.puzzle_state") == PuzzleState.IDLE
    
    def test_state_callbacks(self, integrator, state_manager):
        """Test state change callbacks."""
        integrator.register_state_callbacks()
        
        # Test game active callback
        callback_called = False
        callback_values = {}
        
        def test_callback(field_path, old_value, new_value):
            nonlocal callback_called, callback_values
            callback_called = True
            callback_values = {
                'field_path': field_path,
                'old_value': old_value,
                'new_value': new_value
            }
        
        # Register test callback
        state_manager.register_callback("puzzle.game_active", test_callback)
        
        # Trigger state change
        integrator.set_game_active(True)
        
        # Check that callback was called
        assert callback_called == True
        assert callback_values['field_path'] == "puzzle.game_active"
        assert callback_values['old_value'] == False
        assert callback_values['new_value'] == True
    
    def test_get_state_summary(self, integrator, state_manager):
        """Test getting state summary."""
        # Set some state
        state_manager.set("puzzle.game_active", True)
        state_manager.set("puzzle.score", 500)
        state_manager.set("puzzle.clusters", {(1, 1), (2, 2)})
        state_manager.set("puzzle.chain_count", 3)
        state_manager.set("puzzle.level", 5)
        state_manager.set("puzzle.lines_cleared", 10)
        
        summary = integrator.get_state_summary()
        
        assert summary['game_active'] == True
        assert summary['score'] == 500
        assert summary['clusters'] == 2
        assert summary['chain_count'] == 3
        assert summary['level'] == 5
        assert summary['lines_cleared'] == 10
    
    def test_sync_interval_throttling(self, integrator, puzzle_engine):
        """Test that sync is throttled by interval."""
        integrator.start_integration()
        
        # First sync should work
        puzzle_engine.game_active = True
        integrator.sync_to_state_manager()
        assert integrator.state_manager.get("puzzle.game_active") == True
        
        # Change value again immediately
        puzzle_engine.game_active = False
        
        # Second sync within interval should be ignored
        integrator.sync_to_state_manager()
        assert integrator.state_manager.get("puzzle.game_active") == True  # Should still be True
        
        # Wait for interval to pass
        time.sleep(0.02)  # Longer than 0.016 interval
        
        # Now sync should work
        integrator.sync_to_state_manager()
        assert integrator.state_manager.get("puzzle.game_active") == False
    
    def test_error_handling(self, integrator, puzzle_engine):
        """Test error handling during sync."""
        integrator.start_integration()
        
        # Try to sync with a non-existent attribute
        # This should not raise an exception
        integrator.sync_to_state_manager()
        
        # The integrator should continue working
        assert integrator.integration_active == True


class TestPuzzleStateMapping:
    """Test the PuzzleStateMapping dataclass."""
    
    def test_mapping_creation(self):
        """Test creating a state mapping."""
        mapping = PuzzleStateMapping(
            engine_attr="game_active",
            state_path="puzzle.game_active",
            description="Game active status",
            default_value=False
        )
        
        assert mapping.engine_attr == "game_active"
        assert mapping.state_path == "puzzle.game_active"
        assert mapping.description == "Game active status"
        assert mapping.default_value == False
    
    def test_mapping_without_default(self):
        """Test creating a mapping without default value."""
        mapping = PuzzleStateMapping(
            engine_attr="score",
            state_path="puzzle.score",
            description="Player score"
        )
        
        assert mapping.engine_attr == "score"
        assert mapping.state_path == "puzzle.score"
        assert mapping.description == "Player score"
        assert mapping.default_value is None


class TestIntegrationWithRealStateManager:
    """Test integration with a real GameStateManager."""
    
    def test_full_integration_workflow(self):
        """Test a complete integration workflow."""
        # Create real components
        state_manager = GameStateManager()
        puzzle_engine = MockPuzzleEngine()
        integrator = PuzzleStateIntegrator(state_manager, puzzle_engine)
        
        # Start integration
        integrator.start_integration()
        integrator.register_state_callbacks()
        
        # Simulate game start
        integrator.set_game_active(True)
        integrator.update_puzzle_state(PuzzleState.ACTIVE)
        
        # Simulate gameplay
        integrator.add_score(100)
        integrator.set_clusters({(1, 1), (2, 2)})
        
        # Simulate chain reaction
        integrator.update_puzzle_state(PuzzleState.CHAIN_REACTION)
        state_manager.set("puzzle.chain_count", 1)
        
        # Check final state
        summary = integrator.get_state_summary()
        assert summary['game_active'] == True
        assert summary['score'] == 100
        assert summary['clusters'] == 2
        assert summary['chain_count'] == 1
        assert summary['puzzle_state'] == 'chain_reaction'
        
        # Simulate game over
        integrator.set_game_active(False)
        integrator.update_puzzle_state(PuzzleState.GAME_OVER)
        
        # Check game over state
        assert integrator.is_game_active() == False
        assert integrator.get_puzzle_state() == PuzzleState.GAME_OVER


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"]) 