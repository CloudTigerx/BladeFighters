"""
Character Sprite Manager - Handles character sprite loading, caching, and positioning
Professional sprite management system for BladeFighters characters with resolution-aware scaling.
"""

import pygame
import os
from typing import Dict, Optional, Tuple
from ..logging_module.error_handler import safe_file_operation
from ..logging_module.logger import get_logger
from core.scaling import true_resolution_scaler

logger = get_logger(__name__)


class CharacterSpriteManager:
    """
    Manages character sprites with professional caching and positioning.
    Handles sprite loading, scaling, and positioning relative to game boards.
    """
    
    def __init__(self, asset_path: str, screen_width: int, screen_height: int):
        """Initialize the character sprite manager with resolution-aware scaling."""
        self.asset_path = asset_path
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Sprite cache to avoid reloading
        self.sprite_cache: Dict[str, pygame.Surface] = {}
        
        # Character configurations with resolution-aware scaling
        self.characters = {
            'yuki': {
                'idle_sprite': 'Yuki_idle_sprite',  # Base name for resolution-aware loading
                'base_scale_factor': 0.7,  # Base scale factor for 1080p
                'position_offset': {'x': 0, 'y': 15},
                'animation_speed': 1000,  # Animation speed
                'frames_per_row': 3,  # 3 frames per row in the sprite sheet
                'total_frames': 9  # Total 9 frames (3x3 grid)
            }
        }
        
        # Load all character sprites
        self._load_character_sprites()
        
    @safe_file_operation("load character sprites", {}, "WARNING")
    def _load_character_sprites(self) -> None:
        """Load and cache all character sprites with resolution-aware scaling."""
        for character_name, config in self.characters.items():
            try:
                # Try resolution-aware loading first
                sprite_sheet = true_resolution_scaler.load_character(
                    config['idle_sprite'],
                    fallback_path=os.path.join(self.asset_path, 'characters', f"{config['idle_sprite']}.png")
                )
                
                if sprite_sheet:
                    logger.info(f"✅ Loaded resolution-aware character sprite: {character_name}")
                else:
                    # Fallback to old method
                    sprite_path = os.path.join(self.asset_path, 'characters', f"{config['idle_sprite']}.png")
                    if os.path.exists(sprite_path):
                        sprite_sheet = pygame.image.load(sprite_path).convert_alpha()
                        logger.info(f"✅ Loaded fallback character sprite: {character_name}")
                    else:
                        logger.warning(f"⚠️ Character sprite not found: {sprite_path}")
                        continue
                
                # Process sprite sheet (both resolution-aware and fallback)
                if sprite_sheet:
                    # Get sprite sheet dimensions
                    sheet_width = sprite_sheet.get_width()
                    sheet_height = sprite_sheet.get_height()
                    
                    # Calculate frame dimensions
                    frames_per_row = config.get('frames_per_row', 1)
                    total_frames = config.get('total_frames', 1)
                    frames_per_col = (total_frames + frames_per_row - 1) // frames_per_row
                    
                    frame_width = sheet_width // frames_per_row
                    frame_height = sheet_height // frames_per_col
                    
                    # First pass: analyze all frames to find consistent dimensions
                    frame_bounds = []
                    for frame_index in range(total_frames):
                        row = frame_index // frames_per_row
                        col = frame_index % frames_per_row
                        
                        frame_rect = pygame.Rect(
                            col * frame_width, 
                            row * frame_height, 
                            frame_width, 
                            frame_height
                        )
                        frame_surface = sprite_sheet.subsurface(frame_rect)
                        
                        # Find the actual character bounds in this frame
                        bounds = self._find_character_bounds(frame_surface)
                        frame_bounds.append(bounds)
                    
                    # Calculate consistent dimensions across all frames
                    consistent_bounds = self._calculate_consistent_bounds(frame_bounds)
                    
                    # Second pass: extract frames with consistent alignment
                    for frame_index in range(total_frames):
                        row = frame_index // frames_per_row
                        col = frame_index % frames_per_row
                        
                        frame_rect = pygame.Rect(
                            col * frame_width, 
                            row * frame_height, 
                            frame_width, 
                            frame_height
                        )
                        frame_surface = sprite_sheet.subsurface(frame_rect)
                        
                        # Align frame to consistent bounds
                        aligned_frame = self._align_frame_to_bounds(frame_surface, frame_bounds[frame_index], consistent_bounds)
                        
                        # Scale the aligned frame with resolution-aware scaling
                        base_scale_factor = config['base_scale_factor']
                        
                        # Get current resolution tier for additional scaling
                        current_res = true_resolution_scaler.resolution_manager.get_current_resolution()
                        optimal_tier = true_resolution_scaler.get_optimal_asset_resolution(
                            (current_res.width, current_res.height)
                        )
                        
                        # Apply resolution-specific scaling
                        resolution_scale = {
                            'low': 0.5,      # 800x600
                            'medium': 0.7,   # 1920x1080 (base)
                            'high': 0.9,     # 2560x1440
                            'ultra': 1.1     # 3840x2160
                        }.get(optimal_tier, 0.7)
                        
                        final_scale = base_scale_factor * resolution_scale
                        new_width = int(consistent_bounds[2] * final_scale)
                        new_height = int(consistent_bounds[3] * final_scale)
                        scaled_frame = pygame.transform.scale(aligned_frame, (new_width, new_height))
                        
                        # Cache the scaled frame
                        cache_key = f"{character_name}_idle_{frame_index}"
                        self.sprite_cache[cache_key] = scaled_frame
                    
                    logger.info(f"✅ Loaded character sprite sheet: {character_name} ({total_frames} frames) - aligned")
                    
            except Exception as e:
                logger.error(f"❌ Failed to load character sprite {character_name}: {str(e)}")
    
    def _find_character_bounds(self, surface: pygame.Surface) -> tuple:
        """Find the bounds of the character in a frame (excluding transparent pixels)."""
        width, height = surface.get_size()
        
        # Get pixel array for analysis
        pixel_array = pygame.PixelArray(surface)
        
        min_x, min_y = width, height
        max_x, max_y = 0, 0
        
        # Find bounds of non-transparent pixels
        for y in range(height):
            for x in range(width):
                pixel = pixel_array[x, y]
                # Check if pixel is not transparent (alpha > 0)
                if pixel != 0:  # Assuming 0 is transparent
                    min_x = min(min_x, x)
                    min_y = min(min_y, y)
                    max_x = max(max_x, x)
                    max_y = max(max_y, y)
        
        # Return bounds as (x, y, width, height)
        return (min_x, min_y, max_x - min_x + 1, max_y - min_y + 1)
    
    def _calculate_consistent_bounds(self, frame_bounds: list) -> tuple:
        """Calculate consistent bounds that work for all frames."""
        if not frame_bounds:
            return (0, 0, 100, 100)  # Default fallback
        
        # Find the maximum width and height needed
        max_width = max(bounds[2] for bounds in frame_bounds)
        max_height = max(bounds[3] for bounds in frame_bounds)
        
        # Use the minimum y position as TOP baseline (head position) to prevent rising
        # This ensures the character doesn't "grow" upward during animation
        top_y = min(bounds[1] for bounds in frame_bounds)
        
        # Calculate consistent bounds with top alignment
        consistent_width = max_width
        consistent_height = max_height
        
        return (0, top_y, consistent_width, consistent_height)
    
    def _align_frame_to_bounds(self, frame_surface: pygame.Surface, frame_bounds: tuple, consistent_bounds: tuple) -> pygame.Surface:
        """Align a frame to consistent bounds to prevent hovering."""
        # Create a new surface with consistent dimensions
        consistent_surface = pygame.Surface((consistent_bounds[2], consistent_bounds[3]), pygame.SRCALPHA)
        
        # Calculate offset to align character to baseline
        offset_x = consistent_bounds[0] - frame_bounds[0]
        offset_y = consistent_bounds[1] - frame_bounds[1]
        
        # Blit the character onto the consistent surface
        consistent_surface.blit(frame_surface, (offset_x, offset_y))
        
        return consistent_surface
    
    def get_character_sprite(self, character_name: str, animation_type: str = 'idle', frame_index: int = 0) -> Optional[pygame.Surface]:
        """Get a character sprite from cache."""
        # Try to get the specific frame first
        cache_key = f"{character_name}_{animation_type}_{frame_index}"
        sprite = self.sprite_cache.get(cache_key)
        
        # If not found, fall back to frame 0 (for backward compatibility)
        if not sprite:
            cache_key = f"{character_name}_{animation_type}_0"
            sprite = self.sprite_cache.get(cache_key)
            
        # If still not found, try the old format (for backward compatibility)
        if not sprite:
            cache_key = f"{character_name}_{animation_type}"
            sprite = self.sprite_cache.get(cache_key)
            
        return sprite
    
    def calculate_character_position(self, board_position: Dict[str, int], 
                                   board_dimensions: Tuple[int, int, int, int],
                                   character_name: str = 'yuki') -> Tuple[int, int]:
        """
        Calculate character position relative to a puzzle board.
        
        Args:
            board_position: Dict with 'x' and 'y' coordinates of the board
            board_dimensions: Tuple of (cell_width, cell_height, board_width, board_height)
            character_name: Name of the character to position
            
        Returns:
            Tuple of (x, y) coordinates for character placement
        """
        if character_name not in self.characters:
            logger.warning(f"⚠️ Unknown character: {character_name}")
            return (0, 0)
        
        # Get board dimensions
        _, _, board_width, board_height = board_dimensions
        
        # Get character config
        char_config = self.characters[character_name]
        offset = char_config['position_offset']
        
        # Get sprite dimensions
        sprite = self.get_character_sprite(character_name, 'idle')
        if not sprite:
            return (0, 0)
        
        sprite_width = sprite.get_width()
        sprite_height = sprite.get_height()
        
        # Calculate position: center horizontally, place below board
        char_x = board_position['x'] + (board_width // 2) - (sprite_width // 2) + offset['x']
        char_y = board_position['y'] + board_height + offset['y']
        
        return (char_x, char_y)
    
    def get_character_config(self, character_name: str) -> Optional[Dict]:
        """Get character configuration."""
        return self.characters.get(character_name)
    
    def add_character(self, character_name: str, config: Dict) -> bool:
        """
        Add a new character configuration and load its sprites.
        
        Args:
            character_name: Name of the character
            config: Character configuration dictionary
            
        Returns:
            True if character was added successfully
        """
        try:
            self.characters[character_name] = config
            self._load_character_sprites()
            logger.info(f"✅ Added character: {character_name}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to add character {character_name}: {str(e)}")
            return False
    
    def get_available_characters(self) -> list:
        """Get list of available character names."""
        return list(self.characters.keys())
    
    def clear_cache(self) -> None:
        """Clear the sprite cache."""
        self.sprite_cache.clear()
        logger.info("🧹 Character sprite cache cleared")
