"""
Responsive Coordinate System - True responsive scaling without zooming
Provides coordinate transformations that adapt to different screen sizes while maintaining aspect ratios.
"""

import pygame
from typing import Tuple, Optional
from dataclasses import dataclass
from .resolution_manager import ResolutionManager

@dataclass
class ResponsivePosition:
    """Position in responsive coordinates."""
    x: int
    y: int
    
    def to_tuple(self) -> Tuple[int, int]:
        return (self.x, self.y)

class ResponsiveCoordinateSystem:
    """
    Responsive coordinate transformation system.
    Handles true scaling without zooming by using minimum scale factors and proper centering.
    """
    
    def __init__(self, resolution_manager: ResolutionManager):
        self.resolution_manager = resolution_manager
        self.base_resolution = (1920, 1080)  # Base resolution for calculations
        self.current_resolution = resolution_manager.get_current_resolution()
        
        # Calculate responsive scale factors
        self._calculate_scale_factors()
        
        # Grid settings
        self.grid_offset = (0, 0)
        self.block_size = 65  # Will be updated by asset scaler
        
    def _calculate_scale_factors(self) -> None:
        """Calculate scale factors that prevent overflow and maintain aspect ratios."""
        current_width = self.current_resolution.width
        current_height = self.current_resolution.height
        base_width, base_height = self.base_resolution
        
        # Calculate individual scale factors
        self.scale_x = current_width / base_width
        self.scale_y = current_height / base_height
        
        # Use the MINIMUM scale factor to prevent overflow
        # This ensures content fits within the screen bounds
        self.scale_factor = min(self.scale_x, self.scale_y)
        
        # Calculate padding to center content
        scaled_width = int(base_width * self.scale_factor)
        scaled_height = int(base_height * self.scale_factor)
        
        self.padding_x = (current_width - scaled_width) // 2
        self.padding_y = (current_height - scaled_height) // 2
        
        print(f"📏 Responsive scaling: {self.scale_factor:.2f} (min of {self.scale_x:.2f}, {self.scale_y:.2f})")
        print(f"📐 Padding: ({self.padding_x}, {self.padding_y})")
    
    def get_scale_factor(self) -> float:
        """Get the responsive scale factor."""
        return self.scale_factor
    
    def scale_value(self, base_value: int) -> int:
        """Scale a base value using the responsive scale factor."""
        return int(base_value * self.scale_factor)
    
    def scale_tuple(self, base_tuple: Tuple[int, int]) -> Tuple[int, int]:
        """Scale a tuple using the responsive scale factor."""
        return (self.scale_value(base_tuple[0]), self.scale_value(base_tuple[1]))
    
    def scale_rect(self, base_rect: pygame.Rect) -> pygame.Rect:
        """Scale a pygame Rect using responsive scaling."""
        return pygame.Rect(
            self.padding_x + self.scale_value(base_rect.x),
            self.padding_y + self.scale_value(base_rect.y),
            self.scale_value(base_rect.width),
            self.scale_value(base_rect.height)
        )
    
    def screen_to_base(self, screen_pos: Tuple[int, int]) -> Tuple[int, int]:
        """Convert screen coordinates to base resolution coordinates."""
        screen_x, screen_y = screen_pos
        
        # Remove padding
        base_x = screen_x - self.padding_x
        base_y = screen_y - self.padding_y
        
        # Convert to base resolution
        base_x = int(base_x / self.scale_factor)
        base_y = int(base_y / self.scale_factor)
        
        return (base_x, base_y)
    
    def base_to_screen(self, base_pos: Tuple[int, int]) -> Tuple[int, int]:
        """Convert base resolution coordinates to screen coordinates."""
        base_x, base_y = base_pos
        
        # Scale to current resolution
        screen_x = int(base_x * self.scale_factor)
        screen_y = int(base_y * self.scale_factor)
        
        # Add padding
        screen_x += self.padding_x
        screen_y += self.padding_y
        
        return (screen_x, screen_y)
    
    def get_game_area_rect(self) -> pygame.Rect:
        """Get the game area rectangle (base resolution scaled and centered)."""
        scaled_width = int(self.base_resolution[0] * self.scale_factor)
        scaled_height = int(self.base_resolution[1] * self.scale_factor)
        
        return pygame.Rect(
            self.padding_x,
            self.padding_y,
            scaled_width,
            scaled_height
        )
    
    def is_point_in_game_area(self, screen_pos: Tuple[int, int]) -> bool:
        """Check if a screen point is within the game area."""
        game_area = self.get_game_area_rect()
        return game_area.collidepoint(screen_pos)
    
    def update_resolution(self) -> None:
        """Update the coordinate system when resolution changes."""
        self.current_resolution = self.resolution_manager.get_current_resolution()
        self._calculate_scale_factors()
    
    def get_ui_scale_factor(self) -> float:
        """Get the UI scale factor for responsive UI elements."""
        return self.scale_factor
    
    def scale_font_size(self, base_font_size: int) -> int:
        """Scale a font size responsively."""
        return self.scale_value(base_font_size)
    
    def scale_button_size(self, base_width: int, base_height: int) -> Tuple[int, int]:
        """Scale button dimensions responsively."""
        return self.scale_tuple((base_width, base_height))
    
    def center_element(self, element_size: Tuple[int, int], container_size: Tuple[int, int] = None) -> Tuple[int, int]:
        """Center an element within the game area or specified container."""
        if container_size is None:
            # Use the game area
            game_area = self.get_game_area_rect()
            container_size = (game_area.width, game_area.height)
            offset_x, offset_y = game_area.x, game_area.y
        else:
            offset_x, offset_y = 0, 0
        
        element_width, element_height = element_size
        container_width, container_height = container_size
        
        x = offset_x + (container_width - element_width) // 2
        y = offset_y + (container_height - element_height) // 2
        
        return (x, y)
    
    def create_responsive_layout(self, base_positions: list[Tuple[int, int]], 
                               base_sizes: list[Tuple[int, int]]) -> list[pygame.Rect]:
        """Create a responsive layout from base positions and sizes."""
        responsive_rects = []
        
        for base_pos, base_size in zip(base_positions, base_sizes):
            # Scale position and size
            scaled_pos = self.base_to_screen(base_pos)
            scaled_size = self.scale_tuple(base_size)
            
            # Create rect
            rect = pygame.Rect(scaled_pos[0], scaled_pos[1], scaled_size[0], scaled_size[1])
            responsive_rects.append(rect)
        
        return responsive_rects
