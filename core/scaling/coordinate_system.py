"""
Coordinate System - Handles coordinate transformations
Provides utilities for converting between screen, grid, and world coordinates.
"""

import pygame
from typing import Tuple, Optional
from dataclasses import dataclass
from .resolution_manager import ResolutionManager

@dataclass
class GridPosition:
    """Grid position in block coordinates."""
    x: int
    y: int
    
    def to_tuple(self) -> Tuple[int, int]:
        return (self.x, self.y)

@dataclass
class ScreenPosition:
    """Screen position in pixels."""
    x: int
    y: int
    
    def to_tuple(self) -> Tuple[int, int]:
        return (self.x, self.y)

class CoordinateSystem:
    """
    Coordinate transformation system.
    Handles conversions between screen, grid, and world coordinates.
    """
    
    def __init__(self, resolution_manager: ResolutionManager):
        self.resolution_manager = resolution_manager
        self.grid_offset = (0, 0)  # Grid position on screen
        self.block_size = 65  # Will be updated by asset scaler
        
    def set_grid_offset(self, offset: Tuple[int, int]) -> None:
        """Set the grid offset on screen."""
        self.grid_offset = offset
    
    def set_block_size(self, block_size: int) -> None:
        """Set the block size for coordinate calculations."""
        self.block_size = block_size
    
    def screen_to_grid(self, screen_pos: Tuple[int, int]) -> Optional[GridPosition]:
        """Convert screen coordinates to grid coordinates."""
        screen_x, screen_y = screen_pos
        grid_x, grid_y = self.grid_offset
        
        # Calculate relative position
        rel_x = screen_x - grid_x
        rel_y = screen_y - grid_y
        
        # Convert to grid coordinates
        grid_col = rel_x // self.block_size
        grid_row = rel_y // self.block_size
        
        # Check bounds
        if 0 <= grid_col < 6 and 0 <= grid_row < 15:
            return GridPosition(grid_col, grid_row)
        
        return None
    
    def grid_to_screen(self, grid_pos: GridPosition) -> ScreenPosition:
        """Convert grid coordinates to screen coordinates."""
        grid_x, grid_y = self.grid_offset
        
        screen_x = grid_x + (grid_pos.x * self.block_size)
        screen_y = grid_y + (grid_pos.y * self.block_size)
        
        return ScreenPosition(screen_x, screen_y)
    
    def grid_to_screen_center(self, grid_pos: GridPosition) -> ScreenPosition:
        """Convert grid coordinates to screen coordinates (center of block)."""
        base_pos = self.grid_to_screen(grid_pos)
        
        center_x = base_pos.x + (self.block_size // 2)
        center_y = base_pos.y + (self.block_size // 2)
        
        return ScreenPosition(center_x, center_y)
    
    def get_grid_bounds(self) -> pygame.Rect:
        """Get the grid bounds as a pygame Rect."""
        grid_x, grid_y = self.grid_offset
        grid_width = 6 * self.block_size
        grid_height = 15 * self.block_size
        
        return pygame.Rect(grid_x, grid_y, grid_width, grid_height)
    
    def is_point_in_grid(self, screen_pos: Tuple[int, int]) -> bool:
        """Check if a screen point is within the grid bounds."""
        grid_rect = self.get_grid_bounds()
        return grid_rect.collidepoint(screen_pos)
    
    def get_grid_cell_rect(self, grid_pos: GridPosition) -> pygame.Rect:
        """Get the screen rectangle for a grid cell."""
        screen_pos = self.grid_to_screen(grid_pos)
        return pygame.Rect(screen_pos.x, screen_pos.y, self.block_size, self.block_size)
    
    def get_sub_grid_position(self, grid_pos: GridPosition, sub_x: int, sub_y: int, 
                            sub_divisions: int = 20) -> ScreenPosition:
        """Get screen position for a sub-grid position (for smooth movement)."""
        base_pos = self.grid_to_screen(grid_pos)
        
        sub_offset_x = (sub_x * self.block_size) // sub_divisions
        sub_offset_y = (sub_y * self.block_size) // sub_divisions
        
        screen_x = base_pos.x + sub_offset_x
        screen_y = base_pos.y + sub_offset_y
        
        return ScreenPosition(screen_x, screen_y)
    
    def calculate_preview_position(self, grid_pos: GridPosition, preview_side: str = 'right') -> ScreenPosition:
        """Calculate position for piece preview."""
        grid_rect = self.get_grid_bounds()
        
        if preview_side == 'left':
            # Preview to the left of the grid
            preview_x = grid_rect.x - (3 * self.block_size)  # 3 blocks to the left
            preview_y = grid_rect.y + (grid_pos.y * self.block_size)
        else:
            # Preview to the right of the grid
            preview_x = grid_rect.right + self.block_size  # 1 block to the right
            preview_y = grid_rect.y + (grid_pos.y * self.block_size)
        
        return ScreenPosition(preview_x, preview_y)
    
    def calculate_dual_grid_positions(self, screen_size: Tuple[int, int]) -> dict:
        """Calculate positions for dual grid layout (player vs enemy)."""
        screen_width, screen_height = screen_size
        grid_width = 6 * self.block_size
        grid_height = 15 * self.block_size
        
        # Calculate spacing
        spacing = 40
        total_width = grid_width * 2 + spacing
        
        # Center the dual grid
        start_x = (screen_width - total_width) // 2
        y = (screen_height - grid_height) // 2
        
        return {
            'player': (start_x, y),
            'enemy': (start_x + grid_width + spacing, y),
            'grid_size': (grid_width, grid_height),
            'spacing': spacing
        }
    
    def get_visible_grid_range(self, screen_size: Tuple[int, int]) -> Tuple[int, int, int, int]:
        """Get the range of visible grid cells."""
        grid_rect = self.get_grid_bounds()
        screen_width, screen_height = screen_size
        
        # Calculate visible range
        start_col = max(0, (0 - grid_rect.x) // self.block_size)
        end_col = min(6, (screen_width - grid_rect.x) // self.block_size + 1)
        start_row = max(0, (0 - grid_rect.y) // self.block_size)
        end_row = min(15, (screen_height - grid_rect.y) // self.block_size + 1)
        
        return (start_col, end_col, start_row, end_row)
    
    def update_block_size(self, new_block_size: int) -> None:
        """Update the block size and recalculate coordinates."""
        self.block_size = new_block_size 