"""
Board Manager - Handles dual grid setup and positioning
Extracted from TestMode to manage board lifecycle and positioning.
"""

import pygame
import os
from typing import Dict, Tuple, Optional
from core.puzzle_module import PuzzleEngine
from core.puzzle_renderer import PuzzleRenderer
from ..logging_module.error_handler import (
    safe_operation,
    safe_file_operation
)
from ..logging_module.logger import get_logger

logger = get_logger(__name__)


class BoardManager:
    """
    Manages dual puzzle board setup, positioning, and lifecycle.
    Handles player and enemy boards with proper scaling and positioning.
    """
    
    def __init__(self, screen: pygame.Surface, font, audio, asset_path: str, settings_system=None, clock=None):
        """Initialize the board manager with dual grid setup."""
        self.screen = screen
        self.font = font
        self.audio = audio
        self.asset_path = asset_path
        self.settings_system = settings_system
        self.clock = clock
        
        # Get screen dimensions
        self.width = screen.get_width()
        self.height = screen.get_height()
        
        # Board positioning and dimensions
        self.player_grid_position = {"x": 0, "y": 0}
        self.enemy_grid_position = {"x": 0, "y": 0}
        self.cell_width = 0
        self.cell_height = 0
        self.board_width = 0
        self.board_height = 0
        
        # Create puzzle engines
        self.player_engine = None
        self.enemy_engine = None
        self.player_renderer = None
        self.enemy_renderer = None
        
        # Background image
        self.puzzle_background = None
        
        # Initialize boards
        self._create_engines()
        self._load_background()
        # Move _setup_board_positions() to after renderers are created
        # self._setup_board_positions()
        
    def _create_engines(self):
        """Create player and enemy puzzle engines."""
        # Create player puzzle engine
        self.player_engine = PuzzleEngine(
            self.screen, self.font, self.audio, self.asset_path, self.settings_system
        )
        
        # Create enemy puzzle engine (no audio to avoid conflicts)
        self.enemy_engine = PuzzleEngine(
            self.screen, self.font, None, self.asset_path, self.settings_system
        )
        
        # Set test_mode attribute so puzzle module knows to use landing-based transformation
        self.player_engine.test_mode = self
        self.enemy_engine.test_mode = self
        
        # Create renderers for both engines
        self.player_renderer = PuzzleRenderer(self.player_engine, clock=self.clock)
        self.enemy_renderer = PuzzleRenderer(self.enemy_engine, clock=self.clock)
        
        # Configure preview sides for both renderers
        self.player_renderer.preview_side = 'left'  # Player on the left
        self.enemy_renderer.preview_side = 'right'  # Enemy on the right
        
        # Provide clock to engines so subsystems can consume it
        self._set_engine_clocks()
        
        # Set up board positions after renderers are created
        self._setup_board_positions()

    @safe_operation("set engine clocks", None, "WARNING")
    def _set_engine_clocks(self) -> None:
        """Set clock attribute on engines."""
        try:
            setattr(self.player_engine, 'clock', self.clock)
            setattr(self.enemy_engine, 'clock', self.clock)
        except Exception as e:
            logger.warning(f"Failed to set engine clocks: {str(e)}")
    
    @safe_file_operation("load background", None, "WARNING")
    def _load_background(self) -> None:
        """Load background image for the boards."""
        try:
            self.puzzle_background = pygame.image.load(
                os.path.join(self.asset_path, "puzzlebackground.png")
            )
        except pygame.error as e:
            logger.warning(f"Failed to load puzzle background: {str(e)}")
            self.puzzle_background = None
    
    def _setup_board_positions(self):
        """Set up the positions for the player and enemy puzzle boards."""
        # Ensure both engines have the same grid dimensions
        player_grid_width = getattr(self.player_engine, 'grid_width', 6)
        player_grid_height = getattr(self.player_engine, 'grid_height', 12)
        enemy_grid_width = getattr(self.enemy_engine, 'grid_width', 6)
        enemy_grid_height = getattr(self.enemy_engine, 'grid_height', 12)
        
        # Use consistent grid dimensions for both boards
        grid_width = max(player_grid_width, enemy_grid_width)
        grid_height = max(player_grid_height, enemy_grid_height)
        
        # Ensure both engines use the same grid dimensions
        self.player_engine.grid_width = grid_width
        self.player_engine.grid_height = grid_height
        self.enemy_engine.grid_width = grid_width
        self.enemy_engine.grid_height = grid_height
        
        # Use the actual block sizes from the engines instead of hardcoded values
        cell_width = self.player_engine.block_width
        cell_height = self.player_engine.block_height

        # Prefer centralized asset/coordinate layout for positions
        try:
            from core.scaling import asset_scaler, coordinate_system
            coordinate_system.set_block_size(cell_width)
            layout = asset_scaler.calculate_dual_grid_layout((self.width, self.height))
            player_x, player_y = layout['player']
            enemy_x, enemy_y = layout['enemy']
            # Ensure attached pieces visible across resolutions
            extra_height_for_attached = int(cell_height * 2.5)
            player_y = player_y + extra_height_for_attached
            enemy_y = enemy_y + extra_height_for_attached
        except Exception:
            # Fallback manual layout
            border_size = 10
            board_width = grid_width * cell_width
            board_spacing = 60
            screen_width = self.width
            total_width_needed = (board_width * 2) + board_spacing + (border_size * 4)
            start_x = (screen_width - total_width_needed) // 2
            player_x = start_x + border_size
            extra_height_for_attached = int(cell_height * 2.5)
            player_y = 100 + extra_height_for_attached
            enemy_x = start_x + board_width + board_spacing + (border_size * 3)
            enemy_y = 100 + extra_height_for_attached
        
        # Store positions
        self.player_grid_position = {"x": player_x, "y": player_y}
        self.enemy_grid_position = {"x": enemy_x, "y": enemy_y}
        
        # Update engine grid offsets for proper rendering
        self.player_engine.grid_x_offset = player_x
        self.player_engine.grid_y_offset = player_y
        self.enemy_engine.grid_x_offset = enemy_x
        self.enemy_engine.grid_y_offset = enemy_y
        
        # Update renderer coordinate offsets to match the new positions
        self.player_renderer.update_coordinate_offsets()
        self.enemy_renderer.update_coordinate_offsets()
        
        # Store cell dimensions for use in drawing
        self.cell_width = cell_width
        self.cell_height = cell_height
        self.board_width = grid_width * cell_width
        self.board_height = grid_height * cell_height
    
    def set_piece_landed_callbacks(self, player_callback, enemy_callback):
        """Set callbacks for when pieces land on each board."""
        self.player_engine.on_piece_landed = player_callback
        self.enemy_engine.on_piece_landed = enemy_callback
    
    def set_blocks_broken_handlers(self, player_handler, enemy_handler):
        """Set handlers for when blocks are broken on each board."""
        self.player_engine.blocks_broken_handler = player_handler
        self.enemy_engine.blocks_broken_handler = enemy_handler
    
    def mark_boards_for_side_mapping(self):
        """Mark engines for side mapping (player vs enemy)."""
        setattr(self.player_engine, 'is_player_board', True)
        setattr(self.enemy_engine, 'is_player_board', False)
    
    def start_games(self):
        """Start games on both boards."""
        self.player_engine.start_game()
        self.enemy_engine.start_game()
    
    def reset_engine_states(self):
        """Reset both engine states completely."""
        self._reset_engine_state(self.player_engine)
        self._reset_engine_state(self.enemy_engine)
    
    def _reset_engine_state(self, engine):
        """Reset a single engine's state."""
        # Reset piece movement state
        engine.current_fall_speed = engine.normal_fall_speed
        engine.last_fall_time = self._now_ms()
        engine.micro_fall_time = engine._calculate_micro_fall_time(engine.current_fall_speed)
        
        # Reset other engine state as needed
        if hasattr(engine, 'reset_state'):
            engine.reset_state()
    
    def reset_renderer_states(self):
        """Reset both renderer states."""
        self._reset_renderer_state(self.player_renderer)
        self._reset_renderer_state(self.enemy_renderer)
    
    def _reset_renderer_state(self, renderer):
        """Reset a single renderer's state."""
        # Reset renderer animation states
        if hasattr(renderer, 'reset_animations'):
            renderer.reset_animations()
    
    def update_renderers(self):
        """Update both renderers."""
        self.player_renderer.update_visual_state()
        self.player_renderer.update_animations()
        self.enemy_renderer.update_visual_state()
        self.enemy_renderer.update_animations()
    
    def update_engines(self, current_time: int, player_spawn_pause_until: int = 0, enemy_spawn_pause_until: int = 0):
        """Update both engines with spawn pause support."""
        # Update player engine (respect spawn pause)
        if current_time >= player_spawn_pause_until:
            self.player_engine.update()
        
        # Update enemy engine (respect spawn pause)
        if current_time >= enemy_spawn_pause_until:
            self.enemy_engine.update()
    
    def draw_boards(self):
        """Draw both boards with containers and backgrounds."""
        # Draw background
        self.screen.fill((10, 10, 30))  # Dark blue background
        
        # Use stored dimensions from setup_board_positions
        cell_width = self.cell_width
        cell_height = self.cell_height
        border_size = 10
        board_width = self.board_width
        board_height = self.board_height
        
        # Draw player board container
        player_container = pygame.Rect(
            self.player_grid_position["x"] - border_size,
            self.player_grid_position["y"] - 35,
            board_width + (border_size * 2),
            board_height + 35 + border_size
        )
        pygame.draw.rect(self.screen, (30, 30, 60), player_container, border_radius=5)
        
        # Draw enemy board container
        enemy_container = pygame.Rect(
            self.enemy_grid_position["x"] - border_size,
            self.enemy_grid_position["y"] - 35,
            board_width + (border_size * 2),
            board_height + 35 + border_size
        )
        pygame.draw.rect(self.screen, (30, 30, 60), enemy_container, border_radius=5)
        
        # Draw puzzle backgrounds if available
        if self.puzzle_background:
            scaled_bg = pygame.transform.scale(self.puzzle_background, (board_width, board_height))
            
            # Player board background
            self.screen.blit(scaled_bg, (self.player_grid_position["x"], self.player_grid_position["y"]))
            
            # Enemy board background
            self.screen.blit(scaled_bg, (self.enemy_grid_position["x"], self.enemy_grid_position["y"]))
        
        # Update animations before drawing
        self.update_renderers()
        
        # Draw player grid and pieces using the coordinated method
        self.player_renderer.draw_game_content()

        # Draw Player 2's (Enemy) grid using the coordinated method
        self.enemy_renderer.draw_game_content()
    
    def get_board_positions(self) -> Tuple[Dict, Dict]:
        """Get the positions of both boards."""
        return self.player_grid_position, self.enemy_grid_position
    
    def get_board_dimensions(self) -> Tuple[int, int, int, int]:
        """Get board dimensions (cell_width, cell_height, board_width, board_height)."""
        return self.cell_width, self.cell_height, self.board_width, self.board_height
    
    def get_engines(self) -> Tuple[PuzzleEngine, PuzzleEngine]:
        """Get both puzzle engines."""
        return self.player_engine, self.enemy_engine
    
    def get_renderers(self) -> Tuple[PuzzleRenderer, PuzzleRenderer]:
        """Get both puzzle renderers."""
        return self.player_renderer, self.enemy_renderer
    
    def _now_ms(self) -> int:
        """Get current time in milliseconds."""
        if self.clock:
            return self.clock.now_ms()
        return pygame.time.get_ticks() 