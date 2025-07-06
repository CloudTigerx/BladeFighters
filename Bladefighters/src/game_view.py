#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Game View - Handles all visual rendering and animations
This is completely separate from game logic
"""

import pygame
import math
from collections import defaultdict

class VisualPosition:
    """Represents a visual position with smooth transitions."""
    
    def __init__(self, x, y):
        """Initialize with starting positions."""
        self.x = float(x)
        self.y = float(y)
        self.target_x = float(x)
        self.target_y = float(y)
    
    def set_target(self, x, y):
        """Set the target position to interpolate towards."""
        self.target_x = float(x)
        self.target_y = float(y)
    
    def update(self, lerp_factor):
        """Interpolate towards the target position."""
        self.x += (self.target_x - self.x) * lerp_factor
        self.y += (self.target_y - self.y) * lerp_factor
    
    def is_at_target(self, threshold=0.01):
        """Check if the position is very close to the target."""
        return (abs(self.x - self.target_x) < threshold and 
                abs(self.y - self.target_y) < threshold)
    
    def snap_to_target(self):
        """Snap immediately to target position."""
        self.x = self.target_x
        self.y = self.target_y

class VisualPiece:
    """Visual representation of a game piece with animations."""
    
    def __init__(self, piece_type, position):
        """Initialize with piece type and starting position."""
        self.piece_type = piece_type
        self.position = VisualPosition(position.x, position.y)
        self.scale = 1.0
        self.rotation = 0.0
        self.alpha = 255
        self.animating = False
        
        # Animation properties
        self.animation_type = None
        self.animation_progress = 0.0
        self.animation_duration = 0.0
    
    def start_breaking_animation(self):
        """Start an animation for a piece being broken."""
        self.animating = True
        self.animation_type = "breaking"
        self.animation_progress = 0.0
        self.animation_duration = 0.5  # seconds
    
    def start_appearing_animation(self):
        """Start an animation for a piece appearing."""
        self.animating = True
        self.animation_type = "appearing"
        self.animation_progress = 0.0
        self.animation_duration = 0.3  # seconds
        self.scale = 0.0
        self.alpha = 0
    
    def update_animation(self, delta_time):
        """Update animation progress based on time."""
        if not self.animating:
            return False
            
        self.animation_progress += delta_time / self.animation_duration
        
        if self.animation_progress >= 1.0:
            self.animation_progress = 1.0
            self.animating = False
            return True  # Animation complete
        
        # Update visual properties based on animation type
        if self.animation_type == "breaking":
            # Scale down and fade out
            self.scale = 1.0 - self.animation_progress
            self.alpha = int(255 * (1.0 - self.animation_progress))
            self.rotation = self.animation_progress * 90.0  # Rotate 90 degrees
            
        elif self.animation_type == "appearing":
            # Scale up and fade in
            self.scale = min(1.0, self.animation_progress * 1.2)  # Overshoot a bit
            self.alpha = min(255, int(255 * self.animation_progress * 1.2))
        
        return False  # Animation still in progress

class GameView:
    """Handles all visual aspects of the game."""
    
    def __init__(self, model, screen):
        """Initialize with game model and screen."""
        self.model = model
        self.screen = screen
        self.width, self.height = screen.get_size()
        
        # Colors
        self.BG_COLOR = (30, 30, 50)
        self.GRID_COLOR = (50, 50, 70)
        self.TEXT_COLOR = (220, 220, 220)
        self.PIECE_COLORS = {
            'red': (220, 60, 60),
            'blue': (60, 100, 220),
            'green': (60, 180, 60),
            'yellow': (220, 180, 40),
        }
        self.BREAKER_COLORS = {
            'red_breaker': (240, 80, 80),
            'blue_breaker': (80, 120, 240),
            'green_breaker': (80, 200, 80),
            'yellow_breaker': (240, 200, 60),
        }
        
        # Calculate grid dimensions and position
        self.calculate_grid_dimensions()
        
        # Visual state for game pieces (separate from logical grid)
        self.visual_grid = {}  # (x, y) -> VisualPiece
        self.visual_falling_piece = None
        
        # Animation settings
        self.lerp_factor = 10.0  # Higher values make animations faster
        self.particle_systems = []  # For break effects
        
        # Font setup
        pygame.font.init()
        self.font = pygame.font.SysFont(None, 36)
        self.large_font = pygame.font.SysFont(None, 48)
        
        # Load any necessary assets
        self.load_assets()
    
    def load_assets(self):
        """Load game assets like images and sounds."""
        # For now, we'll just use simple shapes, but in a real game
        # you would load sprite sheets, textures, etc.
        self.block_images = {}
        self.block_images_breaker = {}
    
    def calculate_grid_dimensions(self):
        """Calculate the grid dimensions and position based on screen size."""
        # We want the grid to fit nicely on screen with room for UI
        max_grid_width = self.width * 0.6
        max_grid_height = self.height * 0.85
        
        # Calculate the cell size based on grid dimensions
        cell_width = max_grid_width / self.model.GRID_WIDTH
        cell_height = max_grid_height / self.model.GRID_HEIGHT
        
        # Use the smaller dimension to ensure square cells
        self.cell_size = min(cell_width, cell_height)
        
        # Calculate grid dimensions
        self.grid_width = self.cell_size * self.model.GRID_WIDTH
        self.grid_height = self.cell_size * self.model.GRID_HEIGHT
        
        # Calculate grid position (centered)
        self.grid_x = (self.width - self.grid_width) * 0.4  # Offset to left
        self.grid_y = (self.height - self.grid_height) * 0.5  # Centered vertically
    
    def update(self, delta_time):
        """Update visual state based on the logical state."""
        # Update grid visuals
        self.update_grid_visuals(delta_time)
        
        # Update falling piece visuals
        self.update_falling_piece_visuals(delta_time)
        
        # Update animations
        self.update_animations(delta_time)
    
    def update_grid_visuals(self, delta_time):
        """Update visual representation of the grid."""
        # Check logical grid for changes
        for y in range(self.model.GRID_HEIGHT):
            for x in range(self.model.GRID_WIDTH):
                grid_pos = (x, y)
                logical_piece = self.model.grid.grid[y][x]
                
                # Handle piece that exists in the logical grid
                if logical_piece:
                    # If this piece isn't represented visually yet, add it
                    if grid_pos not in self.visual_grid:
                        visual_piece = VisualPiece(logical_piece.piece_type, GridPosition(x, y))
                        visual_piece.start_appearing_animation()
                        self.visual_grid[grid_pos] = visual_piece
                    
                    # Otherwise, ensure the visual piece matches the logical piece
                    elif self.visual_grid[grid_pos].piece_type != logical_piece.piece_type:
                        # Replace with new visual piece
                        visual_piece = VisualPiece(logical_piece.piece_type, GridPosition(x, y))
                        visual_piece.start_appearing_animation()
                        self.visual_grid[grid_pos] = visual_piece
                
                # Handle piece that is in visual grid but not in logical grid
                elif grid_pos in self.visual_grid:
                    # If not already breaking, start break animation
                    if not self.visual_grid[grid_pos].animating:
                        self.visual_grid[grid_pos].start_breaking_animation()
        
        # Update visual positions
        for pos, visual_piece in list(self.visual_grid.items()):
            x, y = pos
            
            # Update animations
            if visual_piece.animating:
                animation_complete = visual_piece.update_animation(delta_time)
                
                # Remove completed breaking animations
                if animation_complete and visual_piece.animation_type == "breaking":
                    del self.visual_grid[pos]
                    continue
            
            # Update interpolated position
            visual_piece.position.set_target(x, y)
            visual_piece.position.update(self.lerp_factor * delta_time)
    
    def update_falling_piece_visuals(self, delta_time):
        """Update visual representation of the falling piece."""
        logical_piece = self.model.current_piece
        
        # If no logical piece exists, clear the visual piece
        if not logical_piece:
            self.visual_falling_piece = None
            return
        
        # If there's a new falling piece, create a visual representation
        if not self.visual_falling_piece or self.visual_falling_piece[0].piece_type != logical_piece.main_piece.piece_type:
            main_visual = VisualPiece(
                logical_piece.main_piece.piece_type, 
                logical_piece.position
            )
            attached_visual = VisualPiece(
                logical_piece.attached_piece.piece_type, 
                logical_piece.get_attached_position()
            )
            
            self.visual_falling_piece = (main_visual, attached_visual)
            
            # Start appear animation
            main_visual.start_appearing_animation()
            attached_visual.start_appearing_animation()
        
        # Update the visual positions
        if self.visual_falling_piece:
            main_visual, attached_visual = self.visual_falling_piece
            
            # Update animations
            main_visual.update_animation(delta_time)
            attached_visual.update_animation(delta_time)
            
            # Calculate logical positions
            logical_main_pos = logical_piece.position
            logical_attached_pos = logical_piece.get_attached_position()
            
            # Calculate visual position including fractional part for smooth falling
            visual_y_offset = logical_piece.fall_distance
            
            # Set targets with smooth falling
            main_visual.position.set_target(
                logical_main_pos.x,
                logical_main_pos.y + visual_y_offset
            )
            
            attached_visual.position.set_target(
                logical_attached_pos.x,
                logical_attached_pos.y + visual_y_offset
            )
            
            # Update interpolation
            main_visual.position.update(self.lerp_factor * delta_time)
            attached_visual.position.update(self.lerp_factor * delta_time)
    
    def update_animations(self, delta_time):
        """Update all other animations."""
        # Update particle systems
        for particle_system in list(self.particle_systems):
            particle_system.update(delta_time)
            if particle_system.is_complete():
                self.particle_systems.remove(particle_system)
    
    def render(self):
        """Render the game screen."""
        # Clear the screen
        self.screen.fill(self.BG_COLOR)
        
        # Draw the game elements
        self.draw_grid()
        self.draw_pieces()
        self.draw_falling_piece()
        self.draw_ui()
        
        # Draw particle effects on top
        for particle_system in self.particle_systems:
            particle_system.draw(self.screen)
    
    def draw_grid(self):
        """Draw the game grid."""
        # Draw background
        grid_rect = pygame.Rect(
            self.grid_x, self.grid_y, 
            self.grid_width, self.grid_height
        )
        pygame.draw.rect(self.screen, (40, 40, 60), grid_rect)
        
        # Draw grid lines
        for x in range(self.model.GRID_WIDTH + 1):
            pygame.draw.line(
                self.screen, 
                self.GRID_COLOR,
                (self.grid_x + x * self.cell_size, self.grid_y),
                (self.grid_x + x * self.cell_size, self.grid_y + self.grid_height),
                1
            )
        
        for y in range(self.model.GRID_HEIGHT + 1):
            pygame.draw.line(
                self.screen, 
                self.GRID_COLOR,
                (self.grid_x, self.grid_y + y * self.cell_size),
                (self.grid_x + self.grid_width, self.grid_y + y * self.cell_size),
                1
            )
    
    def draw_pieces(self):
        """Draw all pieces on the grid."""
        # Draw each visual piece
        for pos, visual_piece in self.visual_grid.items():
            self.draw_single_piece(visual_piece)
    
    def draw_falling_piece(self):
        """Draw the currently falling piece."""
        if self.visual_falling_piece:
            main_visual, attached_visual = self.visual_falling_piece
            self.draw_single_piece(main_visual)
            self.draw_single_piece(attached_visual)
    
    def draw_single_piece(self, visual_piece):
        """Draw a single piece with its current visual properties."""
        # Get piece color
        is_breaker = 'breaker' in visual_piece.piece_type
        if is_breaker:
            color = self.BREAKER_COLORS.get(visual_piece.piece_type, (200, 200, 200))
        else:
            base_type = visual_piece.piece_type.split('_')[0]  # Get base color
            color = self.PIECE_COLORS.get(base_type, (200, 200, 200))
        
        # Apply alpha
        color = (*color, visual_piece.alpha)
        
        # Calculate screen position
        screen_x = self.grid_x + visual_piece.position.x * self.cell_size
        screen_y = self.grid_y + visual_piece.position.y * self.cell_size
        
        # Calculate size with scale
        scaled_size = self.cell_size * visual_piece.scale
        offset = (self.cell_size - scaled_size) / 2
        
        # Create rectangle
        rect = pygame.Rect(
            screen_x + offset,
            screen_y + offset,
            scaled_size,
            scaled_size
        )
        
        # Draw piece
        if is_breaker:
            # Draw breaker piece (special style)
            pygame.draw.rect(self.screen, color, rect, border_radius=int(scaled_size * 0.25))
            
            # Add breaker symbol (X)
            if visual_piece.scale > 0.5:  # Only if large enough to see
                line_color = (255, 255, 255, visual_piece.alpha)
                margin = scaled_size * 0.2
                
                # Draw X
                pygame.draw.line(
                    self.screen,
                    line_color,
                    (screen_x + offset + margin, screen_y + offset + margin),
                    (screen_x + offset + scaled_size - margin, screen_y + offset + scaled_size - margin),
                    max(1, int(scaled_size * 0.1))
                )
                pygame.draw.line(
                    self.screen,
                    line_color,
                    (screen_x + offset + scaled_size - margin, screen_y + offset + margin),
                    (screen_x + offset + margin, screen_y + offset + scaled_size - margin),
                    max(1, int(scaled_size * 0.1))
                )
        else:
            # Draw regular piece
            pygame.draw.rect(self.screen, color, rect, border_radius=int(scaled_size * 0.15))
    
    def draw_ui(self):
        """Draw the game UI elements."""
        # Draw score
        score_text = self.font.render(f"Score: {self.model.score}", True, self.TEXT_COLOR)
        self.screen.blit(score_text, (20, 20))
        
        # Draw level
        level_text = self.font.render(f"Level: {self.model.level}", True, self.TEXT_COLOR)
        self.screen.blit(level_text, (20, 60))
        
        # Draw next pieces preview
        next_text = self.font.render("Next:", True, self.TEXT_COLOR)
        self.screen.blit(next_text, (self.width - 150, 20))
        
        # Draw next pieces
        if self.model.next_pieces:
            next_size = self.cell_size * 0.8
            for i, piece in enumerate(self.model.next_pieces[:2]):  # Show first 2 pieces
                # Determine color
                is_breaker = 'breaker' in piece.piece_type
                if is_breaker:
                    color = self.BREAKER_COLORS.get(piece.piece_type, (200, 200, 200))
                else:
                    base_type = piece.piece_type.split('_')[0]  # Get base color
                    color = self.PIECE_COLORS.get(base_type, (200, 200, 200))
                
                # Draw piece
                rect = pygame.Rect(
                    self.width - 120, 
                    60 + i * (next_size + 10),
                    next_size,
                    next_size
                )
                pygame.draw.rect(self.screen, color, rect, 
                    border_radius=int(next_size * (0.25 if is_breaker else 0.15)))
                
                # Draw breaker symbol if needed
                if is_breaker:
                    margin = next_size * 0.2
                    pygame.draw.line(
                        self.screen,
                        (255, 255, 255),
                        (rect.left + margin, rect.top + margin),
                        (rect.right - margin, rect.bottom - margin),
                        max(1, int(next_size * 0.1))
                    )
                    pygame.draw.line(
                        self.screen,
                        (255, 255, 255),
                        (rect.right - margin, rect.top + margin),
                        (rect.left + margin, rect.bottom - margin),
                        max(1, int(next_size * 0.1))
                    )
        
        # Game over message
        if not self.model.game_active:
            game_over_text = self.large_font.render("GAME OVER", True, (255, 50, 50))
            game_over_rect = game_over_text.get_rect(center=(self.width/2, self.height/2 - 50))
            
            # Draw with shadow for better visibility
            shadow_text = self.large_font.render("GAME OVER", True, (20, 20, 20))
            shadow_rect = shadow_text.get_rect(center=(self.width/2 + 2, self.height/2 - 48))
            
            self.screen.blit(shadow_text, shadow_rect)
            self.screen.blit(game_over_text, game_over_rect)
            
            # Restart message
            restart_text = self.font.render("Press SPACE to restart", True, self.TEXT_COLOR)
            restart_rect = restart_text.get_rect(center=(self.width/2, self.height/2 + 20))
            self.screen.blit(restart_text, restart_rect)

# Add this for compatibility with the model code
class GridPosition:
    """Utility class for grid positions."""
    def __init__(self, x, y):
        self.x = x
        self.y = y 