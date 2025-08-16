"""
True Resolution Scaler - Smart asset loading for different resolutions
Automatically loads the best quality assets for the current display resolution.
"""

import os
import pygame
from typing import Dict, Optional, Tuple
from .resolution_manager import ResolutionManager


class TrueResolutionScaler:
    """
    Smart asset loading system that automatically selects the best resolution assets.
    """
    
    def __init__(self, resolution_manager: ResolutionManager):
        self.resolution_manager = resolution_manager
        
        # Define resolution tiers and their target resolutions (only 4 we support)
        self.resolution_tiers = {
            'low': (800, 600),      # Low resolution assets
            'medium': (1536, 1024), # Medium resolution assets  
            'high': (1920, 1080),   # High resolution assets
            'ultra': (3840, 2160)   # Ultra resolution assets
        }
        
        # Asset naming patterns for different types
        self.asset_patterns = {
            'backgrounds': 'puzzleassets/menus/{name}_{res}.png',
            'blocks': 'puzzleassets/strikes/{name}_{res}.png',
            'puzzle_pieces': 'puzzleassets/strikes/{name}_{res}.png',
            'board_backgrounds': 'puzzleassets/{name}_{res}.png',
            'ui': 'puzzleassets/menus/{name}_{res}.png',
            'characters': 'puzzleassets/characters/{name}_{res}.png'
        }
        
        # Rectangular block dimensions by resolution tier
        self.block_dimensions = {
            'low': (48, 60),      # 4:5 aspect ratio
            'medium': (64, 80),   # 4:5 aspect ratio
            'high': (80, 100),    # 4:5 aspect ratio
            'ultra': (96, 120)    # 4:5 aspect ratio
        }
        
        # Board background dimensions by resolution tier (6×12 grid)
        self.board_dimensions = {
            'low': (288, 720),      # 6×48 × 12×60
            'medium': (384, 960),   # 6×64 × 12×80
            'high': (480, 1200),    # 6×80 × 12×100
            'ultra': (576, 1440)    # 6×96 × 12×120
        }
        
        # Cache for loaded assets
        self.asset_cache = {}
    
    def get_optimal_asset_resolution(self, target_resolution: Tuple[int, int]) -> str:
        """Choose the best asset resolution tier for the target resolution."""
        target_pixels = target_resolution[0] * target_resolution[1]
        
        # Find the smallest tier that can accommodate the target
        for tier, (width, height) in self.resolution_tiers.items():
            tier_pixels = width * height
            if tier_pixels >= target_pixels:
                return tier
        
        return 'ultra'  # Fallback to highest
    
    def load_resolution_appropriate_asset(self, base_name: str, asset_type: str, 
                                        fallback_path: str = None) -> Optional[pygame.Surface]:
        """
        Load the best asset for current resolution with smart fallback.
        
        Args:
            base_name: Base name of the asset (e.g., 'Official_mainmenu_background')
            asset_type: Type of asset ('backgrounds', 'blocks', 'ui', 'characters')
            fallback_path: Optional fallback path if no resolution-specific asset exists
            
        Returns:
            Loaded pygame Surface or None if failed
        """
        current_res = self.resolution_manager.get_current_resolution()
        optimal_tier = self.get_optimal_asset_resolution(
            (current_res.width, current_res.height)
        )
        
        # Create cache key
        cache_key = f"{base_name}_{optimal_tier}_{asset_type}"
        
        # Check cache first
        if cache_key in self.asset_cache:
            return self.asset_cache[cache_key]
        
        # Try loading the optimal resolution asset
        asset_path = self.asset_patterns[asset_type].format(
            name=base_name, 
            res=optimal_tier
        )
        
        if os.path.exists(asset_path):
            try:
                asset = pygame.image.load(asset_path)
                self.asset_cache[cache_key] = asset
                print(f"✅ Loaded {optimal_tier} asset: {asset_path}")
                return asset
            except Exception as e:
                print(f"⚠️ Failed to load {asset_path}: {e}")
        
        # Fallback chain: ultra -> high -> medium -> low
        fallback_chain = ['ultra', 'high', 'medium', 'low']
        current_index = fallback_chain.index(optimal_tier)
        
        for tier in fallback_chain[current_index:]:
            asset_path = self.asset_patterns[asset_type].format(
                name=base_name, 
                res=tier
            )
            if os.path.exists(asset_path):
                try:
                    asset = pygame.image.load(asset_path)
                    self.asset_cache[cache_key] = asset
                    print(f"✅ Loaded fallback {tier} asset: {asset_path}")
                    return asset
                except Exception as e:
                    print(f"⚠️ Failed to load fallback {asset_path}: {e}")
        
        # Final fallback to original asset path
        if fallback_path and os.path.exists(fallback_path):
            try:
                asset = pygame.image.load(fallback_path)
                self.asset_cache[cache_key] = asset
                print(f"✅ Loaded original fallback: {fallback_path}")
                return asset
            except Exception as e:
                print(f"⚠️ Failed to load original fallback {fallback_path}: {e}")
        
        print(f"❌ No asset found for {base_name} ({asset_type})")
        return None
    
    def load_background(self, base_name: str, fallback_path: str = None) -> Optional[pygame.Surface]:
        """Load a background asset with resolution-appropriate scaling."""
        return self.load_resolution_appropriate_asset(base_name, 'backgrounds', fallback_path)
    
    def load_block(self, base_name: str, fallback_path: str = None) -> Optional[pygame.Surface]:
        """Load a block asset with resolution-appropriate scaling."""
        return self.load_resolution_appropriate_asset(base_name, 'blocks', fallback_path)
    
    def load_puzzle_piece(self, base_name: str, fallback_path: str = None) -> Optional[pygame.Surface]:
        """Load a puzzle piece asset with resolution-appropriate scaling."""
        return self.load_resolution_appropriate_asset(base_name, 'puzzle_pieces', fallback_path)
    
    def load_board_background(self, base_name: str, fallback_path: str = None) -> Optional[pygame.Surface]:
        """Load a board background asset with resolution-appropriate scaling."""
        return self.load_resolution_appropriate_asset(base_name, 'board_backgrounds', fallback_path)
    
    def get_block_dimensions(self, resolution_tier: str = None) -> Tuple[int, int]:
        """Get the block dimensions for the specified resolution tier."""
        if resolution_tier is None:
            current_res = self.resolution_manager.get_current_resolution()
            resolution_tier = self.get_optimal_asset_resolution(
                (current_res.width, current_res.height)
            )
        return self.block_dimensions.get(resolution_tier, (64, 80))
    
    def get_board_dimensions(self, resolution_tier: str = None) -> Tuple[int, int]:
        """Get the board dimensions for the specified resolution tier."""
        if resolution_tier is None:
            current_res = self.resolution_manager.get_current_resolution()
            resolution_tier = self.get_optimal_asset_resolution(
                (current_res.width, current_res.height)
            )
        return self.board_dimensions.get(resolution_tier, (384, 960))
    
    def load_ui_element(self, base_name: str, fallback_path: str = None) -> Optional[pygame.Surface]:
        """Load a UI element with resolution-appropriate scaling."""
        return self.load_resolution_appropriate_asset(base_name, 'ui', fallback_path)
    
    def load_character(self, base_name: str, fallback_path: str = None) -> Optional[pygame.Surface]:
        """Load a character asset with resolution-appropriate scaling."""
        return self.load_resolution_appropriate_asset(base_name, 'characters', fallback_path)
    
    def clear_cache(self) -> None:
        """Clear the asset cache."""
        self.asset_cache.clear()
        print("🧹 Asset cache cleared")
    
    def get_cache_info(self) -> Dict[str, int]:
        """Get information about cached assets."""
        return {
            'total_assets': len(self.asset_cache),
            'cached_keys': list(self.asset_cache.keys())
        }
