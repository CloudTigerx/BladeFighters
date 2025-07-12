"""
Simplified TestMode Implementation
Core puzzle battle functionality: 2 grids, piece previews, backgrounds.
Stripped of attack system complexity to focus on essential gameplay.
"""

import pygame
import os
import random
from typing import List, Dict, Optional, Any

# Try to import the interface contract
try:
    from contracts.testmode_interface_contract import TestModeInterface, validate_testmode_interface
    interface_available = True
except ImportError:
    # Create a dummy interface if not available
    class TestModeInterface:
        pass
    
    def validate_testmode_interface(cls):
        return cls
    
    interface_available = False
    print("⚠️  TestMode interface contract not found, running without validation")

# Import required game components
from core.puzzle_module import PuzzleEngine
from core.puzzle_renderer import PuzzleRenderer

@validate_testmode_interface
class TestMode(TestModeInterface):
    """Simplified TestMode focusing on core puzzle battle functionality."""
    
    def __init__(self, screen, font, audio, asset_path: str):
        """Initialize the test mode with core puzzle battle setup."""
        self.screen = screen
        self.font = font
        self.audio = audio
        self.asset_path = asset_path
        
        # Get screen dimensions
        self.width = screen.get_width()
        self.height = screen.get_height()
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GRAY = (100, 100, 100)
        self.LIGHT_BLUE = (100, 150, 255)
        
        # Create player puzzle engine
        self.player_engine = PuzzleEngine(screen, font, audio, asset_path)
        
        # Create enemy puzzle engine (no audio to avoid conflicts)
        self.enemy_engine = PuzzleEngine(screen, font, None, asset_path)
        
        # Create renderers for both engines
        self.player_renderer = PuzzleRenderer(self.player_engine)
        self.enemy_renderer = PuzzleRenderer(self.enemy_engine)
        
        # Load background images
        try:
            self.puzzle_background = pygame.image.load(os.path.join(asset_path, "puzzlebackground.jpg"))
        except pygame.error:
            self.puzzle_background = None
        
        # Set up board positions and dimensions
        self.setup_board_positions()
        
        # Initialize the puzzle battle
        self.initialize_test()
        
        print("✅ TestMode initialized with core functionality")
    
    def setup_board_positions(self):
        """Set up the positions for the player and enemy puzzle boards."""
        # Grid specifications
        grid_width = 6
        grid_height = 13
        cell_width = 68  # Match the cell width used in draw() method
        cell_height = 54  # Match the cell height used in draw() method
        border_size = 10  # Space between container edge and the actual grid
        
        # Calculate board dimensions
        board_width = grid_width * cell_width
        board_height = grid_height * cell_height
        
        # Calculate proper centered positions
        screen_width = self.width
        board_spacing = 40  # Space between boards
        
        # Center calculation - include borders in the total width
        total_width_needed = (board_width * 2) + board_spacing + (border_size * 4)
        start_x = (screen_width - total_width_needed) // 2
        
        # Player board position (left side)
        player_x = start_x + border_size
        player_y = 80
        
        # Enemy board position (right side) 
        enemy_x = start_x + board_width + board_spacing + (border_size * 3)
        enemy_y = 80
        
        # Store positions
        self.player_grid_position = {"x": player_x, "y": player_y}
        self.enemy_grid_position = {"x": enemy_x, "y": enemy_y}
        
        # Update engine grid offsets for proper rendering
        self.player_engine.grid_x_offset = player_x
        self.player_engine.grid_y_offset = player_y
        self.enemy_engine.grid_x_offset = enemy_x
        self.enemy_engine.grid_y_offset = enemy_y
    
    def initialize_test(self):
        """Initialize or reset the test mode game state."""
        # Reset piece movement state for both engines
        self.player_engine.current_fall_speed = self.player_engine.normal_fall_speed
        self.player_engine.last_fall_time = pygame.time.get_ticks()
        self.player_engine.micro_fall_time = self.player_engine._calculate_micro_fall_time(self.player_engine.current_fall_speed)
        
        self.enemy_engine.current_fall_speed = self.enemy_engine.normal_fall_speed
        self.enemy_engine.last_fall_time = pygame.time.get_ticks()
        self.enemy_engine.micro_fall_time = self.enemy_engine._calculate_micro_fall_time(self.enemy_engine.current_fall_speed)
        
        # Start both games
        self.player_engine.start_game()
        self.enemy_engine.start_game()
        
        # Update renderers
        self.player_renderer.update_visual_state()
        self.enemy_renderer.update_visual_state()
    
    def update(self) -> Optional[str]:
        """Update the test mode state."""
        # Update player engine
        self.player_engine.update()
        
        # Update enemy engine with simple AI
        self.enemy_engine.update()
        
        # Simple AI movement (much simpler than original)
        if random.random() < 0.05:  # 5% chance each frame
            move_choice = random.random()
            
            try:
                if move_choice < 0.4:  # 40% chance to move left/right
                    self.enemy_engine.move_piece(random.choice([-1, 1]), 0)
                elif move_choice < 0.6:  # 20% chance to rotate
                    self.enemy_engine.rotate_attached_piece(random.choice([-1, 1]))
                else:  # 40% chance to accelerate drop
                    self.enemy_engine.move_piece(0, 1)
            except Exception as e:
                # Ignore AI movement errors - not critical
                pass
        
        # Check for game over conditions
        if not self.player_engine.game_active or not self.enemy_engine.game_active:
            return "game_over"
        
        return None
    
    def process_events(self, events: List) -> Optional[str]:
        """Process input events for the test mode."""
        # Let the player engine handle its own events first
        self.player_engine.process_events(events)
        
        # Handle test mode specific events
        for event in events:
            if event.type == pygame.KEYDOWN:
                # Escape key to return to menu
                if event.key == pygame.K_ESCAPE:
                    return "back_to_menu"
        
        return None
    
    def draw(self):
        """Draw the complete test mode interface."""
        # Draw background
        self.screen.fill((10, 10, 30))  # Dark blue background
        
        # Add atmospheric gradient effect
        for i in range(20):
            alpha = 150 - (i * 7)
            if alpha < 0:
                alpha = 0
            gradient = pygame.Surface((self.width, 5), pygame.SRCALPHA)
            gradient.fill((50, 50, 80, alpha))
            self.screen.blit(gradient, (0, i * 20))
            self.screen.blit(gradient, (0, self.height - (i * 20)))
        
        # Draw title at top
        title_font = pygame.font.SysFont(None, 48)
        title_text = title_font.render("Puzzle Battle", True, self.WHITE)
        title_rect = title_text.get_rect(midtop=(self.width // 2, 20))
        # Add glow effect
        glow_text = title_font.render("Puzzle Battle", True, self.LIGHT_BLUE)
        glow_rect = glow_text.get_rect(midtop=(self.width // 2 + 2, 22))
        self.screen.blit(glow_text, glow_rect)
        self.screen.blit(title_text, title_rect)
        
        # Calculate dimensions
        cell_width = 68
        cell_height = 54
        border_size = 10
        board_width = 6 * cell_width
        board_height = 13 * cell_height
        
        # Draw player board container
        player_container = pygame.Rect(
            self.player_grid_position["x"] - border_size,
            self.player_grid_position["y"] - 35,
            board_width + (border_size * 2),
            board_height + 35 + border_size
        )
        pygame.draw.rect(self.screen, (30, 30, 60), player_container, border_radius=5)
        pygame.draw.rect(self.screen, (100, 100, 255), player_container, 3, border_radius=5)
        
        # Draw enemy board container
        enemy_container = pygame.Rect(
            self.enemy_grid_position["x"] - border_size,
            self.enemy_grid_position["y"] - 35,
            board_width + (border_size * 2),
            board_height + 35 + border_size
        )
        pygame.draw.rect(self.screen, (30, 30, 60), enemy_container, border_radius=5)
        pygame.draw.rect(self.screen, (255, 100, 100), enemy_container, 3, border_radius=5)  # Red for enemy
        
        # Draw puzzle backgrounds if available
        if self.puzzle_background:
            scaled_bg = pygame.transform.scale(self.puzzle_background, (board_width, board_height))
            
            # Player board background
            self.screen.blit(scaled_bg, (self.player_grid_position["x"], self.player_grid_position["y"]))
            
            # Enemy board background
            self.screen.blit(scaled_bg, (self.enemy_grid_position["x"], self.enemy_grid_position["y"]))
        
        # Draw player grid and pieces
        self.player_renderer.draw_grid_blocks(
            self.player_grid_position["x"], 
            self.player_grid_position["y"], 
            cell_width, 
            cell_height
        )
        
        self.player_renderer.draw_falling_piece(
            self.player_grid_position["x"], 
            self.player_grid_position["y"], 
            cell_width, 
            cell_height
        )
        
        # Draw player next piece preview
        self.player_renderer.current_x_offset = self.player_grid_position["x"]
        self.player_renderer.current_y_offset = self.player_grid_position["y"]
        self.player_renderer.engine = self.player_engine
        self.player_renderer.draw_next_piece_preview(cell_width, cell_height)
        
        # Draw enemy grid and pieces
        self.enemy_renderer.draw_grid_blocks(
            self.enemy_grid_position["x"], 
            self.enemy_grid_position["y"], 
            cell_width, 
            cell_height
        )
        
        self.enemy_renderer.draw_falling_piece(
            self.enemy_grid_position["x"], 
            self.enemy_grid_position["y"], 
            cell_width, 
            cell_height
        )
        
        # Draw enemy next piece preview
        self.enemy_renderer.current_x_offset = self.enemy_grid_position["x"]
        self.enemy_renderer.current_y_offset = self.enemy_grid_position["y"]
        self.enemy_renderer.engine = self.enemy_engine
        self.enemy_renderer.draw_next_piece_preview_right(cell_width, cell_height)
        
        # Draw player title
        player_title = pygame.font.SysFont(None, 28).render("Player", True, self.WHITE)
        player_title_rect = player_title.get_rect(midtop=(
            self.player_grid_position["x"] + (board_width / 2), 
            self.player_grid_position["y"] - 30
        ))
        self.screen.blit(player_title, player_title_rect)
        
        # Draw enemy title
        enemy_title = pygame.font.SysFont(None, 28).render("AI", True, (255, 100, 100))
        enemy_title_rect = enemy_title.get_rect(midtop=(
            self.enemy_grid_position["x"] + (board_width / 2), 
            self.enemy_grid_position["y"] - 30
        ))
        self.screen.blit(enemy_title, enemy_title_rect)
        
        # Draw simple controls instruction
        controls_font = pygame.font.SysFont(None, 20)
        controls_text = "Arrow Keys: Move | Z/X: Rotate | Space: Drop | ESC: Menu"
        controls_surface = controls_font.render(controls_text, True, self.GRAY)
        controls_rect = controls_surface.get_rect(center=(self.width // 2, self.height - 30))
        self.screen.blit(controls_surface, controls_rect) 