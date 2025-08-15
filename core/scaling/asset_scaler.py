"""
Asset Scaler - Handles game asset scaling
Provides consistent scaling for blocks, backgrounds, sprites, and other game assets.
"""

import pygame
import os
from typing import Dict, Optional, Tuple, Union
from .resolution_manager import ResolutionManager

class AssetScaler:
    """
    Comprehensive asset scaling system.
    Handles blocks, backgrounds, sprites, and other game assets.
    """
    
    def __init__(self, resolution_manager: ResolutionManager):
        self.resolution_manager = resolution_manager
        self.scale_factor = resolution_manager.get_ui_scale_factor()
        
        # Base asset sizes (for 1920x1080)
        self.base_sizes = {
            'block_size': 65,
            'grid_width': 6,
            'grid_height': 15,
            'preview_size': 40,
            'icon_size': 32,
            'background_margin': 100,
        }
        
        # Asset cache
        self.scaled_assets = {}
        self.asset_path = "puzzleassets"
    
    def get_scale_factor(self) -> float:
        """Get the current asset scale factor."""
        return self.scale_factor
    
    def scale_value(self, base_value: Union[int, float]) -> int:
        """Scale a base value by the current scale factor."""
        return int(base_value * self.scale_factor)
    
    def get_block_size(self) -> int:
        """Get the scaled block size for the current resolution."""
        return self.scale_value(self.base_sizes['block_size'])
    
    def get_grid_dimensions(self) -> Tuple[int, int]:
        """Get the grid dimensions (width, height in blocks)."""
        return (self.base_sizes['grid_width'], self.base_sizes['grid_height'])
    
    def get_grid_pixel_size(self) -> Tuple[int, int]:
        """Get the grid size in pixels."""
        block_size = self.get_block_size()
        grid_width, grid_height = self.get_grid_dimensions()
        return (grid_width * block_size, grid_height * block_size)
    
    def calculate_grid_position(self, screen_size: Tuple[int, int]) -> Tuple[int, int]:
        """Calculate the position to center the grid on screen."""
        screen_width, screen_height = screen_size
        grid_width, grid_height = self.get_grid_pixel_size()
        
        x = (screen_width - grid_width) // 2
        y = (screen_height - grid_height) // 2
        
        return (x, y)
    
    def scale_image(self, image: pygame.Surface, target_size: Tuple[int, int]) -> pygame.Surface:
        """Scale an image to target size with smooth scaling."""
        if image.get_size() == target_size:
            return image
        
        # Use smooth scaling for better quality
        return pygame.transform.smoothscale(image, target_size)
    
    def load_and_scale_image(self, filename: str, target_size: Optional[Tuple[int, int]] = None) -> Optional[pygame.Surface]:
        """Load and scale an image from the assets directory."""
        cache_key = f"{filename}_{target_size}"
        
        if cache_key in self.scaled_assets:
            return self.scaled_assets[cache_key]
        
        try:
            filepath = os.path.join(self.asset_path, filename)
            if not os.path.exists(filepath):
                print(f"⚠️ Asset not found: {filepath}")
                return None
            
            image = pygame.image.load(filepath).convert_alpha()
            
            if target_size:
                image = self.scale_image(image, target_size)
            
            self.scaled_assets[cache_key] = image
            return image
            
        except Exception as e:
            print(f"⚠️ Error loading asset {filename}: {e}")
            return None
    
    def get_block_image(self, block_type: str) -> Optional[pygame.Surface]:
        """Get a scaled block image."""
        block_size = self.get_block_size()
        
        # Map block types to filenames
        block_files = {
            'red_block': 'redblock.png',
            'blue_block': 'blueblock.png',
            'green_block': 'greenblock.png',
            'yellow_block': 'yellowblock.png',
            'garbage_block': 'strikes/garbage_block.png',
            'strike_block': 'strikes/1x4.png',
            'red_breaker': 'redbreaker.png',
            'blue_breaker': 'bluebreaker.png',
            'green_breaker': 'greenbreaker.png',
            'yellow_breaker': 'yellowbreaker.png',
        }
        
        filename = block_files.get(block_type)
        if not filename:
            return None
        
        return self.load_and_scale_image(filename, (block_size, block_size))
    
    def get_background_image(self, background_type: str = 'puzzle') -> Optional[pygame.Surface]:
        """Get a scaled background image."""
        background_files = {
            'puzzle': 'puzzlebackground.jpg',
            'menu': 'menus/bg_noise_tile.png',
            'story': 'storybackground.png',
        }
        
        filename = background_files.get(background_type)
        if not filename:
            return None
        
        # For backgrounds, scale to fit the grid
        grid_width, grid_height = self.get_grid_pixel_size()
        return self.load_and_scale_image(filename, (grid_width, grid_height))
    
    def get_ui_image(self, ui_type: str) -> Optional[pygame.Surface]:
        """Get a scaled UI image."""
        ui_files = {
            'button_normal': 'menus/button_normal.png',
            'button_hover': 'menus/button_hover.png',
            'button_pressed': 'menus/button_pressed.png',
            'panel': 'menus/panel_9slice.png',
            'slider_track': 'menus/slider_track.png',
            'slider_knob': 'menus/slider_knob.png',
        }
        
        filename = ui_files.get(ui_type)
        if not filename:
            return None
        
        # UI elements scale with UI scale factor
        base_size = self.base_sizes.get('icon_size', 32)
        scaled_size = self.scale_value(base_size)
        
        return self.load_and_scale_image(filename, (scaled_size, scaled_size))
    
    def create_scaled_sprite_sheet(self, sheet_filename: str, frame_size: Tuple[int, int]) -> Dict[str, pygame.Surface]:
        """Create scaled sprites from a sprite sheet."""
        sheet = self.load_and_scale_image(sheet_filename)
        if not sheet:
            return {}
        
        # Scale the frame size
        scaled_frame_size = self.scale_tuple(frame_size)
        
        # Extract frames (simplified - assumes uniform grid)
        frames = {}
        sheet_width, sheet_height = sheet.get_size()
        frame_width, frame_height = scaled_frame_size
        
        frame_count = 0
        for y in range(0, sheet_height, frame_height):
            for x in range(0, sheet_width, frame_width):
                frame_rect = pygame.Rect(x, y, frame_width, frame_height)
                frame_surface = sheet.subsurface(frame_rect)
                frames[f"frame_{frame_count}"] = frame_surface
                frame_count += 1
        
        return frames
    
    def scale_tuple(self, base_tuple: Tuple[int, int]) -> Tuple[int, int]:
        """Scale a tuple of values."""
        return (self.scale_value(base_tuple[0]), self.scale_value(base_tuple[1]))
    
    def get_preview_size(self) -> int:
        """Get the scaled preview size."""
        return self.scale_value(self.base_sizes['preview_size'])
    
    def calculate_dual_grid_layout(self, screen_size: Tuple[int, int]) -> Dict[str, Tuple[int, int]]:
        """Calculate positions for dual grid layout (player vs enemy)."""
        screen_width, screen_height = screen_size
        grid_width, grid_height = self.get_grid_pixel_size()
        
        # Calculate spacing between grids
        spacing = self.scale_value(40)
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
    
    def clear_cache(self) -> None:
        """Clear the asset cache."""
        self.scaled_assets.clear()
    
    def update_scale(self) -> None:
        """Update the scale factor when resolution changes."""
        self.scale_factor = self.resolution_manager.get_ui_scale_factor()
        # Clear cache to force regeneration with new scale
        self.clear_cache() 