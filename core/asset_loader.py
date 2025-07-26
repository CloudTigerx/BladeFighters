import pygame
import os
from typing import Dict, Optional, Tuple

class AssetLoader:
    """
    Handles all asset loading and management for the puzzle game.
    This class centralizes image loading, scaling, and caching for better organization.
    """
    
    def __init__(self, asset_path: str = "puzzleassets", block_size: int = 65):
        """
        Initialize the asset loader.
        
        Args:
            asset_path: Path to the assets directory
            block_size: Size for scaling block images
        """
        self.asset_path = asset_path
        self.block_size = block_size
        
        # Color constants for fallback rendering
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        
        # Initialize asset storage
        self.block_images = {}
        self.background_images = {}
        self.sprite_sheets = {}
        self.puzzle_pieces = {}
        
        # Load all standard assets
        self._load_standard_assets()
    
    def _load_standard_assets(self):
        """Load all standard game assets."""
        # Load standard block types
        self.block_images.update({
            'red_block': self.load_block("redblock.png"),
            'blue_block': self.load_block("blueblock.png"),
            'green_block': self.load_block("greenblock.png"),
            'yellow_block': self.load_block("yellowblock.png"),
            'garbage_block': self.load_block("strikes/garbage_block.png"),
            'strike_block': self.load_block("strikes/1x4.png")
        })
        
        # Load breaker blocks (using dedicated breaker images without X overlay)
        self.block_images.update({
            'red_breaker': self.load_block("redbreaker.png", "redblock.png", False),
            'blue_breaker': self.load_block("bluebreaker.png", "blueblock.png", False),
            'green_breaker': self.load_block("greenbreaker.png", "greenblock.png", False),
            'yellow_breaker': self.load_block("yellowbreaker.png", "yellowblock.png", False)
        })
        
        # Create colored garbage blocks for better visual distinction
        # These will be tinted versions of the garbage block texture
        self.block_images.update({
            'red_garbage': self._create_colored_garbage_block("red"),
            'blue_garbage': self._create_colored_garbage_block("blue"), 
            'green_garbage': self._create_colored_garbage_block("green"),
            'yellow_garbage': self._create_colored_garbage_block("yellow")
        })
        
        # Populate puzzle_pieces dictionary for compatibility
        self.puzzle_pieces = {
            'redblock': self.block_images.get('red_block'),
            'blueblock': self.block_images.get('blue_block'),
            'greenblock': self.block_images.get('green_block'),
            'yellowblock': self.block_images.get('yellow_block'),
            'garbage_block': self.block_images.get('garbage_block'),
            'red_garbage': self.block_images.get('red_garbage'),
            'blue_garbage': self.block_images.get('blue_garbage'),
            'green_garbage': self.block_images.get('green_garbage'),
            'yellow_garbage': self.block_images.get('yellow_garbage'),
            'redbreaker': self.block_images.get('red_breaker'),
            'bluebreaker': self.block_images.get('blue_breaker'),
            'greenbreaker': self.block_images.get('green_breaker'),
            'yellowbreaker': self.block_images.get('yellow_breaker'),
            'strikeblock': self.block_images.get('strike_block')
        }
        
        # Load background images
        self.background_images['puzzle_background'] = self.load_background("puzzlebackground.jpg")
    
    def load_block(self, filename: str, fallback_filename: Optional[str] = None, is_breaker: bool = False) -> Optional[pygame.Surface]:
        """
        Load and scale a block image.
        
        Args:
            filename: Primary image filename
            fallback_filename: Fallback image filename if primary fails
            is_breaker: Whether to add breaker visual indicator
            
        Returns:
            Loaded and scaled pygame Surface or None if failed
        """
        try:
            # Try primary image
            image_path = os.path.join(self.asset_path, filename)
            if os.path.exists(image_path):
                original_img = pygame.image.load(image_path)
                scaled_img = pygame.transform.scale(original_img, (self.block_size, self.block_size))
                
                # Add breaker indicator if needed
                if is_breaker:
                    scaled_img = self._add_breaker_indicator(scaled_img)
                
                return scaled_img
            
            # Try fallback image
            elif fallback_filename:
                fallback_path = os.path.join(self.asset_path, fallback_filename)
                if os.path.exists(fallback_path):
                    original_img = pygame.image.load(fallback_path)
                    scaled_img = pygame.transform.scale(original_img, (self.block_size, self.block_size))
                    
                    # Add breaker indicator if needed
                    if is_breaker:
                        scaled_img = self._add_breaker_indicator(scaled_img)
                    
                    return scaled_img
                    
        except pygame.error as e:
            print(f"Error loading block image {filename}: {e}")
        
        # If all loading attempts fail, raise an error
        raise ValueError(f"Could not load block image: {filename}")
    
    def _add_breaker_indicator(self, surface: pygame.Surface) -> pygame.Surface:
        """Add a visual indicator to breaker blocks."""
        # Create a copy of the surface
        result = surface.copy()
        
        # Add a simple X overlay
        width, height = result.get_size()
        pygame.draw.line(result, (255, 255, 255), (width//4, height//4), (3*width//4, 3*height//4), 3)
        pygame.draw.line(result, (255, 255, 255), (width//4, 3*height//4), (3*width//4, height//4), 3)
        
        return result
    
    def _create_colored_garbage_block(self, color: str) -> pygame.Surface:
        """Create a colored garbage block by tinting the base garbage block texture."""
        base_garbage = self.block_images.get('garbage_block')
        if base_garbage is None:
            # Fallback to a colored rectangle if no base texture
            surface = pygame.Surface((self.block_size, self.block_size))
            color_map = {
                'red': (255, 100, 100),
                'blue': (100, 100, 255), 
                'green': (100, 255, 100),
                'yellow': (255, 255, 100)
            }
            surface.fill(color_map.get(color, (128, 128, 128)))
            return surface
        
        # Create a copy and tint it
        result = base_garbage.copy()
        
        # Define color tints (RGB values)
        color_tints = {
            'red': (255, 150, 150),
            'blue': (150, 150, 255),
            'green': (150, 255, 150), 
            'yellow': (255, 255, 150)
        }
        
        tint_color = color_tints.get(color, (255, 255, 255))
        
        # Apply tint by blending with the tint color
        tint_surface = pygame.Surface(result.get_size())
        tint_surface.fill(tint_color)
        result.blit(tint_surface, (0, 0), special_flags=pygame.BLEND_MULT)
        
        return result
    
    def load_background(self, filename: str, target_size: Optional[Tuple[int, int]] = None) -> Optional[pygame.Surface]:
        """
        Load and optionally scale a background image.
        
        Args:
            filename: Background image filename
            target_size: Optional target size for scaling (width, height)
            
        Returns:
            Loaded pygame Surface or None if failed
        """
        try:
            image_path = os.path.join(self.asset_path, filename)
            if os.path.exists(image_path):
                background = pygame.image.load(image_path)
                
                if target_size:
                    background = pygame.transform.scale(background, target_size)
                
                print(f"Loaded background image: {filename}")
                return background
                
        except pygame.error as e:
            print(f"Could not load background image {filename}: {e}")
        
        return None
    
    def load_sprite_sheet(self, filename: str, frame_count: int = 8) -> Optional[list]:
        """
        Load and slice a sprite sheet into individual frames.
        
        Args:
            filename: Sprite sheet filename
            frame_count: Number of frames to extract
            
        Returns:
            List of pygame Surfaces representing frames, or None if failed
        """
        try:
            image_path = os.path.join(self.asset_path, filename)
            if os.path.exists(image_path):
                sprite_sheet = pygame.image.load(image_path).convert_alpha()
                width = sprite_sheet.get_width()
                height = sprite_sheet.get_height()
                frame_width = width // frame_count
                
                frames = []
                for i in range(frame_count):
                    frame = pygame.Surface((frame_width, height), pygame.SRCALPHA)
                    frame.blit(sprite_sheet, (0, 0), 
                              (i * frame_width, 0, frame_width, height))
                    frames.append(frame)
                
                print(f"Loaded sprite sheet: {filename} ({frame_count} frames)")
                return frames
                
        except pygame.error as e:
            print(f"Could not load sprite sheet {filename}: {e}")
        
        return None
    
    def get_block_image(self, block_type: str) -> Optional[pygame.Surface]:
        """
        Get a block image by type.
        
        Args:
            block_type: Block type identifier (e.g., 'red_block', 'blue_breaker')
            
        Returns:
            pygame Surface or None if not found
        """
        return self.block_images.get(block_type)
    
    def get_puzzle_piece(self, piece_key: str) -> Optional[pygame.Surface]:
        """
        Get a puzzle piece by key (for compatibility with existing code).
        
        Args:
            piece_key: Piece key (e.g., 'redblock', 'bluebreaker')
            
        Returns:
            pygame Surface or None if not found
        """
        return self.puzzle_pieces.get(piece_key)
    
    def get_background(self, background_name: str) -> Optional[pygame.Surface]:
        """
        Get a background image by name.
        
        Args:
            background_name: Background identifier
            
        Returns:
            pygame Surface or None if not found
        """
        return self.background_images.get(background_name)
    
    def update_block_size(self, new_block_size: int):
        """
        Update the block size and reload all block images.
        
        Args:
            new_block_size: New size for blocks
        """
        if new_block_size != self.block_size:
            self.block_size = new_block_size
            # Clear existing images
            self.block_images.clear()
            self.puzzle_pieces.clear()
            # Reload with new size
            self._load_standard_assets()
    
    def scale_background_for_grid(self, background_name: str, grid_width: int, grid_height: int, block_size: int) -> Optional[pygame.Surface]:
        """
        Scale a background image to fit a specific grid size.
        
        Args:
            background_name: Background identifier
            grid_width: Number of blocks wide
            grid_height: Number of blocks high
            block_size: Size of each block
            
        Returns:
            Scaled background or None if not found
        """
        background = self.background_images.get(background_name)
        if background:
            target_width = grid_width * block_size
            target_height = grid_height * block_size
            return pygame.transform.scale(background, (target_width, target_height))
        return None
    
    def preload_explosion_sprites(self) -> Dict[str, list]:
        """
        Preload explosion sprite sheets for animations.
        
        Returns:
            Dictionary mapping explosion types to frame lists
        """
        explosion_sprites = {}
        
        # Load different explosion types
        explosion_files = [
            ("blue_explode", "blue_explode.png"),
            ("orange_explode", "sprite_sheet_orange_cleaned.png"),
            ("yellow_explode", "sprite_sheet_yellow.png"),
            ("blue_explode_alt", "sprite_sheet_blue.png")
        ]
        
        for explosion_type, filename in explosion_files:
            frames = self.load_sprite_sheet(filename)
            if frames:
                explosion_sprites[explosion_type] = frames
        
        return explosion_sprites
    
    def get_asset_info(self) -> Dict[str, int]:
        """
        Get information about loaded assets.
        
        Returns:
            Dictionary with asset counts
        """
        return {
            'block_images': len(self.block_images),
            'background_images': len(self.background_images),
            'sprite_sheets': len(self.sprite_sheets),
            'puzzle_pieces': len(self.puzzle_pieces)
        } 