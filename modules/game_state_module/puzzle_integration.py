"""
Puzzle State Integration
Handles integration of puzzle engine state with the unified GameStateManager.
This module provides a clean interface for migrating puzzle state variables.
"""

import time
from typing import Dict, Any, Optional, List, Tuple, Set
import pygame
from dataclasses import dataclass

from .game_state_manager import GameStateManager
from .state_schema import GameState, PuzzleState, GameMode
from modules.logging_module.logger import get_logger


@dataclass
class PuzzleStateMapping:
    """Maps puzzle engine variables to state manager paths."""
    engine_attr: str
    state_path: str
    description: str
    default_value: Any = None


class PuzzleStateIntegrator:
    """
    Integrates puzzle engine state with the unified GameStateManager.
    Provides methods to sync state between the puzzle engine and state manager.
    """
    
    def __init__(self, state_manager: GameStateManager, puzzle_engine):
        """Initialize the puzzle state integrator."""
        self.state_manager = state_manager
        self.puzzle_engine = puzzle_engine
        self.logger = get_logger(__name__)
        
        # Define state mappings
        self.state_mappings = self._create_state_mappings()
        
        # Track integration status
        self.integration_active = False
        self.last_sync_time = 0
        self.sync_interval = 0.016  # 60fps sync rate
        
        self.logger.info("PuzzleStateIntegrator initialized")
    
    def _create_state_mappings(self) -> List[PuzzleStateMapping]:
        """Create mappings between puzzle engine variables and state manager paths."""
        return [
            # Core game state
            PuzzleStateMapping("game_active", "puzzle.game_active", "Game active status"),
            PuzzleStateMapping("puzzle_grid", "puzzle.grid", "Puzzle grid state"),
            
            # Grid dimensions
            PuzzleStateMapping("grid_width", "puzzle.grid_width", "Grid width"),
            PuzzleStateMapping("grid_height", "puzzle.grid_height", "Grid height"),
            PuzzleStateMapping("total_grid_height", "puzzle.total_grid_height", "Total grid height"),
            PuzzleStateMapping("block_size", "puzzle.block_size", "Block size"),
            
            # Piece state
            PuzzleStateMapping("main_piece", "puzzle.current_piece", "Current main piece"),
            PuzzleStateMapping("attached_piece", "puzzle.attached_piece", "Current attached piece"),
            PuzzleStateMapping("next_main_piece", "puzzle.next_piece", "Next main piece"),
            PuzzleStateMapping("next_attached_piece", "puzzle.next_attached_piece", "Next attached piece"),
            PuzzleStateMapping("piece_position", "puzzle.piece_position", "Piece position"),
            PuzzleStateMapping("attached_position", "puzzle.attached_position", "Attached piece position"),
            
            # Game mechanics state
            PuzzleStateMapping("clusters", "puzzle.clusters", "Active clusters"),
            PuzzleStateMapping("breaking_blocks", "puzzle.breaking_blocks", "Blocks being broken"),
            PuzzleStateMapping("chain_reaction_in_progress", "puzzle.chain_reaction_in_progress", "Chain reaction status"),
            PuzzleStateMapping("chain_count", "puzzle.chain_count", "Chain count"),
            PuzzleStateMapping("chain_state", "puzzle.chain_state", "Chain state machine"),
            
            # Timing state
            PuzzleStateMapping("last_fall_time", "puzzle.last_fall_time", "Last fall time"),
            PuzzleStateMapping("current_fall_speed", "puzzle.current_fall_speed", "Current fall speed"),
            PuzzleStateMapping("normal_fall_speed", "puzzle.normal_fall_speed", "Normal fall speed"),
            PuzzleStateMapping("accelerated_fall_speed", "puzzle.accelerated_fall_speed", "Accelerated fall speed"),
            PuzzleStateMapping("micro_fall_time", "puzzle.micro_fall_time", "Micro fall time"),
            
            # Animation state
            PuzzleStateMapping("breaking_animation_start", "puzzle.breaking_animation_start", "Breaking animation start time"),
            PuzzleStateMapping("breaking_animation_duration", "puzzle.breaking_animation_duration", "Breaking animation duration"),
            
            # Debug state
            PuzzleStateMapping("debug_breaks", "puzzle.debug_breaks", "Debug breaks enabled"),
            PuzzleStateMapping("enable_debug_logs", "puzzle.enable_debug_logs", "Debug logs enabled"),
            
            # Wall kick state
            PuzzleStateMapping("last_wall_kick_time", "puzzle.last_wall_kick_time", "Last wall kick time"),
            PuzzleStateMapping("wall_kick_count", "puzzle.wall_kick_count", "Wall kick count"),
            PuzzleStateMapping("max_wall_kicks", "puzzle.max_wall_kicks", "Maximum wall kicks"),
            
            # Flip state
            PuzzleStateMapping("last_flip_time", "puzzle.last_flip_time", "Last flip time"),
            PuzzleStateMapping("flip_cooldown", "puzzle.flip_cooldown", "Flip cooldown"),
            
            # Sub-grid positioning
            PuzzleStateMapping("sub_grid_positions", "puzzle.sub_grid_positions", "Sub-grid positions"),
            PuzzleStateMapping("current_sub_position", "puzzle.current_sub_position", "Current sub-position"),
        ]
    
    def start_integration(self):
        """Start the state integration process."""
        self.integration_active = True
        self._initial_sync()
        self.logger.info("Puzzle state integration started")
    
    def stop_integration(self):
        """Stop the state integration process."""
        self.integration_active = False
        self.logger.info("Puzzle state integration stopped")
    
    def _initial_sync(self):
        """Perform initial sync of all state variables."""
        for mapping in self.state_mappings:
            try:
                if hasattr(self.puzzle_engine, mapping.engine_attr):
                    value = getattr(self.puzzle_engine, mapping.engine_attr)
                    self.state_manager.set(
                        mapping.state_path, 
                        value, 
                        source="puzzle_integration",
                        description=f"Initial sync: {mapping.description}"
                    )
            except Exception as e:
                self.logger.warning(f"Failed to sync {mapping.engine_attr}: {e}")
    
    def sync_to_state_manager(self):
        """Sync puzzle engine state to the state manager."""
        if not self.integration_active:
            return
        
        current_time = time.time()
        if current_time - self.last_sync_time < self.sync_interval:
            return
        
        self.last_sync_time = current_time
        
        for mapping in self.state_mappings:
            try:
                if hasattr(self.puzzle_engine, mapping.engine_attr):
                    value = getattr(self.puzzle_engine, mapping.engine_attr)
                    current_state_value = self.state_manager.get(mapping.state_path)
                    
                    # Only update if value has changed
                    if value != current_state_value:
                        self.state_manager.set(
                            mapping.state_path,
                            value,
                            source="puzzle_engine",
                            description=f"Sync: {mapping.description}"
                        )
            except Exception as e:
                self.logger.warning(f"Failed to sync {mapping.engine_attr}: {e}")
    
    def sync_from_state_manager(self):
        """Sync state manager values back to the puzzle engine."""
        if not self.integration_active:
            return
        
        for mapping in self.state_mappings:
            try:
                if hasattr(self.puzzle_engine, mapping.engine_attr):
                    state_value = self.state_manager.get(mapping.state_path)
                    if state_value is not None:
                        setattr(self.puzzle_engine, mapping.engine_attr, state_value)
            except Exception as e:
                self.logger.warning(f"Failed to sync from state manager: {mapping.engine_attr}: {e}")
    
    def update_puzzle_state(self, new_state: PuzzleState):
        """Update the puzzle state enum in the state manager."""
        self.state_manager.set(
            "puzzle.puzzle_state",
            new_state,
            source="puzzle_integration",
            description=f"Puzzle state changed to {new_state.value}"
        )
    
    def get_puzzle_state(self) -> PuzzleState:
        """Get the current puzzle state from the state manager."""
        return self.state_manager.get("puzzle.puzzle_state", PuzzleState.IDLE)
    
    def set_game_active(self, active: bool):
        """Set the game active status."""
        self.state_manager.set(
            "puzzle.game_active",
            active,
            source="puzzle_integration",
            description=f"Game active set to {active}"
        )
        # Also update the engine directly for immediate effect
        self.puzzle_engine.game_active = active
    
    def is_game_active(self) -> bool:
        """Check if the game is active."""
        return self.state_manager.get("puzzle.game_active", False)
    
    def get_clusters(self) -> Set[Tuple[int, int]]:
        """Get current clusters from state manager."""
        return self.state_manager.get("puzzle.clusters", set())
    
    def set_clusters(self, clusters: Set[Tuple[int, int]]):
        """Set clusters in state manager."""
        self.state_manager.set(
            "puzzle.clusters",
            clusters,
            source="puzzle_integration",
            description=f"Clusters updated: {len(clusters)} clusters"
        )
    
    def get_score(self) -> int:
        """Get current score from state manager."""
        return self.state_manager.get("puzzle.score", 0)
    
    def add_score(self, points: int):
        """Add points to the score."""
        current_score = self.get_score()
        new_score = current_score + points
        self.state_manager.set(
            "puzzle.score",
            new_score,
            source="puzzle_integration",
            description=f"Score increased by {points} to {new_score}"
        )
    
    def reset_game_state(self):
        """Reset all game state variables."""
        reset_values = {
            "puzzle.game_active": False,
            "puzzle.puzzle_state": PuzzleState.IDLE,
            "puzzle.clusters": set(),
            "puzzle.breaking_blocks": [],
            "puzzle.chain_reaction_in_progress": False,
            "puzzle.chain_count": 0,
            "puzzle.score": 0,
            "puzzle.lines_cleared": 0,
            "puzzle.level": 1,
            "puzzle.current_piece": None,
            "puzzle.attached_piece": None,
            "puzzle.next_piece": None,
            "puzzle.next_attached_piece": None,
        }
        
        for path, value in reset_values.items():
            self.state_manager.set(
                path,
                value,
                source="puzzle_integration",
                description="Game state reset"
            )
        
        self.logger.info("Puzzle game state reset")
    
    def register_state_callbacks(self):
        """Register callbacks for important state changes."""
        # Register callback for game active state changes
        self.state_manager.register_callback(
            "puzzle.game_active",
            self._on_game_active_changed,
            "Handle game active state changes"
        )
        
        # Register callback for puzzle state changes
        self.state_manager.register_callback(
            "puzzle.puzzle_state",
            self._on_puzzle_state_changed,
            "Handle puzzle state changes"
        )
        
        # Register callback for chain reaction changes
        self.state_manager.register_callback(
            "puzzle.chain_reaction_in_progress",
            self._on_chain_reaction_changed,
            "Handle chain reaction state changes"
        )
    
    def _on_game_active_changed(self, field_path: str, old_value: bool, new_value: bool):
        """Handle game active state changes."""
        self.logger.info(f"Game active changed: {old_value} -> {new_value}")
        if new_value:
            self.update_puzzle_state(PuzzleState.ACTIVE)
        else:
            self.update_puzzle_state(PuzzleState.IDLE)
    
    def _on_puzzle_state_changed(self, field_path: str, old_value: PuzzleState, new_value: PuzzleState):
        """Handle puzzle state changes."""
        self.logger.info(f"Puzzle state changed: {old_value.value} -> {new_value.value}")
    
    def _on_chain_reaction_changed(self, field_path: str, old_value: bool, new_value: bool):
        """Handle chain reaction state changes."""
        if new_value:
            self.update_puzzle_state(PuzzleState.CHAIN_REACTION)
        else:
            # Only change back to ACTIVE if game is still active
            if self.is_game_active():
                self.update_puzzle_state(PuzzleState.ACTIVE)
    
    def get_state_summary(self) -> Dict[str, Any]:
        """Get a summary of current puzzle state."""
        return {
            "game_active": self.is_game_active(),
            "puzzle_state": self.get_puzzle_state().value,
            "score": self.get_score(),
            "clusters": len(self.get_clusters()),
            "chain_reaction": self.state_manager.get("puzzle.chain_reaction_in_progress", False),
            "chain_count": self.state_manager.get("puzzle.chain_count", 0),
            "level": self.state_manager.get("puzzle.level", 1),
            "lines_cleared": self.state_manager.get("puzzle.lines_cleared", 0),
        } 