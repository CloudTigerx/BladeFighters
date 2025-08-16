"""
UI Scaler - Handles UI element scaling and positioning
Provides consistent scaling for all UI elements across different resolutions.
"""

import pygame
from typing import Tuple, Union, Optional
from dataclasses import dataclass
from .resolution_manager import ResolutionManager

@dataclass
class UIScale:
    """UI scaling configuration for different element types."""
    font_size: int
    padding: int
    margin: int
    border_radius: int
    icon_size: int

class UIScaler:
    """
    Comprehensive UI scaling system.
    Handles fonts, buttons, panels, and other UI elements.
    """
    
    def __init__(self, resolution_manager: ResolutionManager):
        self.resolution_manager = resolution_manager
        self.base_resolution = (1920, 1080)
        
        # Use simplified scaling system
        self.scale_factor = resolution_manager.get_ui_scale_factor()
        
        # Base UI sizes (for 1920x1080) - Optimized for responsive scaling
        self.base_sizes = {
            'title_font': 80,    # Reduced for better responsive scaling
            'heading_font': 48,  # Reduced for better responsive scaling
            'body_font': 32,     # Reduced for better responsive scaling
            'small_font': 24,    # Reduced for better responsive scaling
            'tiny_font': 18,     # Reduced for better responsive scaling
            'button_height': 60, # Reduced for better responsive scaling
            'button_padding': 20, # Reduced for better responsive scaling
            'panel_padding': 30, # Reduced for better responsive scaling
            'margin': 20,        # Reduced for better responsive scaling
            'border_radius': 10, # Reduced for better responsive scaling
            'icon_size': 40,     # Reduced for better responsive scaling
        }
        
        # Cache for scaled fonts
        self.font_cache = {}
    
    def get_scale_factor(self) -> float:
        """Get the current UI scale factor."""
        return self.scale_factor
    
    def scale_value(self, base_value: Union[int, float]) -> int:
        """Scale a base value using simplified scaling."""
        return int(base_value * self.scale_factor)
    
    def scale_tuple(self, base_tuple: Tuple[int, int]) -> Tuple[int, int]:
        """Scale a tuple using simplified scaling."""
        return (int(base_tuple[0] * self.scale_factor), int(base_tuple[1] * self.scale_factor))
    
    def scale_rect(self, base_rect: pygame.Rect) -> pygame.Rect:
        """Scale a pygame Rect using simplified scaling."""
        return pygame.Rect(
            int(base_rect.x * self.scale_factor),
            int(base_rect.y * self.scale_factor),
            int(base_rect.width * self.scale_factor),
            int(base_rect.height * self.scale_factor)
        )
    
    def get_font(self, font_type: str, size_override: Optional[int] = None) -> pygame.font.Font:
        """Get a scaled font."""
        base_size = self.base_sizes.get(font_type, 24)
        if size_override:
            base_size = size_override
        
        scaled_size = self.scale_value(base_size)
        
        # Cache key
        cache_key = f"{font_type}_{scaled_size}"
        
        if cache_key not in self.font_cache:
            try:
                # Try to load custom font first
                font_path = "puzzleassets/fonts/PermanentMarker-Regular.ttf"
                self.font_cache[cache_key] = pygame.font.Font(font_path, scaled_size)
            except:
                # Fallback to system font
                self.font_cache[cache_key] = pygame.font.SysFont(None, scaled_size)
        
        return self.font_cache[cache_key]
    
    def get_ui_scale(self, element_type: str) -> UIScale:
        """Get UI scale configuration for a specific element type."""
        if element_type == "button":
            return UIScale(
                font_size=self.scale_value(self.base_sizes['body_font']),
                padding=self.scale_value(self.base_sizes['button_padding']),
                margin=self.scale_value(self.base_sizes['margin']),
                border_radius=self.scale_value(self.base_sizes['border_radius']),
                icon_size=self.scale_value(self.base_sizes['icon_size'])
            )
        elif element_type == "panel":
            return UIScale(
                font_size=self.scale_value(self.base_sizes['heading_font']),
                padding=self.scale_value(self.base_sizes['panel_padding']),
                margin=self.scale_value(self.base_sizes['margin']),
                border_radius=self.scale_value(self.base_sizes['border_radius']),
                icon_size=self.scale_value(self.base_sizes['icon_size'])
            )
        elif element_type == "title":
            return UIScale(
                font_size=self.scale_value(self.base_sizes['title_font']),
                padding=self.scale_value(self.base_sizes['panel_padding']),
                margin=self.scale_value(self.base_sizes['margin']),
                border_radius=self.scale_value(self.base_sizes['border_radius']),
                icon_size=self.scale_value(self.base_sizes['icon_size'])
            )
        else:
            # Default scale
            return UIScale(
                font_size=self.scale_value(self.base_sizes['body_font']),
                padding=self.scale_value(self.base_sizes['button_padding']),
                margin=self.scale_value(self.base_sizes['margin']),
                border_radius=self.scale_value(self.base_sizes['border_radius']),
                icon_size=self.scale_value(self.base_sizes['icon_size'])
            )
    
    def create_button_rect(self, x: int, y: int, width: int, height: int) -> pygame.Rect:
        """Create a scaled button rectangle."""
        # Don't scale x and y as they're already calculated for the current screen
        # Only scale the width and height
        return pygame.Rect(
            x,
            y,
            self.scale_value(width),
            self.scale_value(height)
        )
    
    def create_panel_rect(self, x: int, y: int, width: int, height: int) -> pygame.Rect:
        """Create a scaled panel rectangle."""
        return pygame.Rect(
            self.scale_value(x),
            self.scale_value(y),
            self.scale_value(width),
            self.scale_value(height)
        )
    
    def center_element(self, element_size: Tuple[int, int], container_size: Tuple[int, int] = None) -> Tuple[int, int]:
        """Center an element within the game area or specified container."""
        return self.responsive_system.center_element(element_size, container_size)
    
    def grid_layout(self, container_rect: pygame.Rect, element_size: Tuple[int, int], 
                   columns: int, rows: int, spacing: int = 0) -> list[pygame.Rect]:
        """Create a grid layout of elements."""
        element_width, element_height = element_size
        spacing = self.scale_value(spacing)
        
        # Calculate total grid size
        grid_width = columns * element_width + (columns - 1) * spacing
        grid_height = rows * element_height + (rows - 1) * spacing
        
        # Center the grid in the container
        start_x = container_rect.x + (container_rect.width - grid_width) // 2
        start_y = container_rect.y + (container_rect.height - grid_height) // 2
        
        elements = []
        for row in range(rows):
            for col in range(columns):
                x = start_x + col * (element_width + spacing)
                y = start_y + row * (element_height + spacing)
                elements.append(pygame.Rect(x, y, element_width, element_height))
        
        return elements
    
    def flex_layout(self, container_rect: pygame.Rect, element_size: Tuple[int, int], 
                   count: int, direction: str = "horizontal", spacing: int = 0) -> list[pygame.Rect]:
        """Create a flexible layout of elements."""
        element_width, element_height = element_size
        spacing = self.scale_value(spacing)
        
        if direction == "horizontal":
            total_width = count * element_width + (count - 1) * spacing
            start_x = container_rect.x + (container_rect.width - total_width) // 2
            start_y = container_rect.y + (container_rect.height - element_height) // 2
            
            elements = []
            for i in range(count):
                x = start_x + i * (element_width + spacing)
                elements.append(pygame.Rect(x, start_y, element_width, element_height))
            return elements
        
        else:  # vertical
            total_height = count * element_height + (count - 1) * spacing
            start_x = container_rect.x + (container_rect.width - element_width) // 2
            start_y = container_rect.y + (container_rect.height - total_height) // 2
            
            elements = []
            for i in range(count):
                y = start_y + i * (element_height + spacing)
                elements.append(pygame.Rect(start_x, y, element_width, element_height))
            return elements
    
    def update_scale(self) -> None:
        """Update the scale factor when resolution changes."""
        # Update the responsive system
        self.responsive_system.update_resolution()
        self.scale_factor = self.responsive_system.get_scale_factor()
        # Clear font cache to force regeneration with new scale
        self.font_cache.clear() 