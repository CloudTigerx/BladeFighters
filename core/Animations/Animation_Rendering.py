#!/usr/bin/env python3
"""
Animation Rendering Module
Handles the actual rendering of animations for the puzzle game
Extracted from puzzle_renderer.py for modular architecture
"""

import pygame
import time
import math
import random
from typing import Dict, List, Set, Any, Optional, Tuple

class AnimationRenderer:
    """
    Handles the actual rendering of all animation effects.
    This class separates rendering logic from state management for better modularity.
    """
    
    def __init__(self, screen: pygame.Surface, puzzle_engine, animation_state_manager):
        """Initialize animation renderer with dependencies."""
        self.screen = screen
        self.engine = puzzle_engine
        self.state_manager = animation_state_manager
        
        # Cache references to frequently used state variables
        self.update_animation_refs()
        
        # Initialize rendering assets
        self._initialize_rendering_assets()
        
    def update_animation_refs(self):
        """Update references to animation state variables for performance."""
        # Cache frequently accessed state variables
        self.breaking_blocks_animations = self.state_manager.breaking_blocks_animations
        self.visual_falling_blocks = self.state_manager.visual_falling_blocks
        self.dust_particles = self.state_manager.dust_particles
        self.combo_texts = self.state_manager.combo_texts
        self.cluster_animations = self.state_manager.cluster_animations
        self.particle_surfaces = self.state_manager.particle_surfaces
        
    def _initialize_rendering_assets(self):
        """Initialize assets needed for rendering animations."""
        # Load explosion sprite sheets if available
        try:
            # Get explosion sprites from the asset loader instead of engine
            if hasattr(self.engine, 'asset_loader'):
                explosion_sprites = self.engine.asset_loader.preload_explosion_sprites()
                self.explosion_frames = explosion_sprites.get('blue_explode', [])
                self.green_explosion_frames = explosion_sprites.get('blue_explode_alt', [])
                self.red_explosion_frames = explosion_sprites.get('yellow_explode', [])
                self.yellow_explosion_frames = explosion_sprites.get('orange_explode', [])
                
                print(f"DEBUG: Loaded explosion sprites - Blue: {len(self.explosion_frames)}, Green: {len(self.green_explosion_frames)}, Red: {len(self.red_explosion_frames)}, Yellow: {len(self.yellow_explosion_frames)}")
            else:
                self.explosion_frames = []
                self.green_explosion_frames = []
                self.red_explosion_frames = []
                self.yellow_explosion_frames = []
                
            # Explosion animation settings
            self.explosion_repeat_frames = 3
            self.explosion_initial_frames = 2
            self.explosion_scale_start = 0.8
            self.explosion_scale_end = 1.5
            
        except Exception as e:
            print(f"Warning: Could not load explosion sprites: {e}")
            self.explosion_frames = []
            self.green_explosion_frames = []
            self.red_explosion_frames = []
            self.yellow_explosion_frames = []
    
    def render_breaking_block(self, pos: Tuple[int, int], block_data: Dict[str, Any], 
                            x_offset: int, y_offset: int, block_width: int, block_height: int):
        """
        Render a single breaking block animation with particles and explosion effects.
        
        Args:
            pos: (x, y) grid position of the breaking block
            block_data: Animation data including progress, particles, etc.
            x_offset: X offset for grid positioning
            y_offset: Y offset for grid positioning
            block_width: Width of each block in pixels
            block_height: Height of each block in pixels
        """
        x, y = pos
        block_type = block_data['block_type']
        progress = block_data['progress']
        
        # Calculate screen position
        block_x = x_offset + (x * block_width)
        block_y = y_offset + (y * block_height)
        
        # Draw the block with shrinking effect in early animation stages
        if progress < 0.3:
            self._render_shrinking_block(block_data, block_x, block_y, block_width, block_height, progress)
        
        # Draw particles
        if 'particles' in block_data and block_data['particles']:
            self._render_breaking_particles(block_data, block_x, block_y, block_width, block_height)
        
        # Draw explosion sprite effects for different block types
        if progress < 0.5:
            self._render_explosion_effects(block_type, block_x, block_y, block_width, block_height, progress)
    
    def _render_shrinking_block(self, block_data: Dict[str, Any], block_x: int, block_y: int, 
                               block_width: int, block_height: int, progress: float):
        """Render a block with shrinking effect during breaking animation."""
        # Scale factor decreases as animation progresses
        scale = 1.0 - (progress / 0.3)
        
        # Use stored block surface if available
        if 'block_surface' in block_data:
            # Create a copy to avoid modifying the original
            block_copy = block_data['block_surface'].copy()
            
            # Calculate new size
            new_width = int(block_width * scale)
            new_height = int(block_height * scale)
            
            # Only scale if needed - avoid scaling if almost the same size
            if abs(new_width - block_width) > 1 or abs(new_height - block_height) > 1:
                try:
                    block_copy = pygame.transform.scale(block_copy, (new_width, new_height))
                except Exception:
                    # If scaling fails, just use original surface
                    pass
            
            # Center the scaled block
            center_x = block_x + (block_width - new_width) // 2
            center_y = block_y + (block_height - new_height) // 2
            
            # Draw scaled block
            self.screen.blit(block_copy, (center_x, center_y))
    
    def _render_breaking_particles(self, block_data: Dict[str, Any], block_x: int, block_y: int, 
                                 block_width: int, block_height: int):
        """Render particle effects for breaking blocks with optimized batch rendering."""
        particles = block_data['particles']
        
        # Only draw if particles are on screen
        if not (0 <= block_x <= self.engine.width and 0 <= block_y <= self.engine.height):
            return
            
        # Batch particles by surface properties to minimize draw calls
        particle_batches = {}
        
        for particle in particles:
            # Calculate alpha based on remaining life
            alpha = int(255 * (particle['life'] / particle['max_life']))
            
            # Calculate screen position
            px = block_x + (particle['x'] * block_width)
            py = block_y + (particle['y'] * block_height)
            
            # Skip off-screen particles
            if px < -10 or px > self.engine.width + 10 or py < -10 or py > self.engine.height + 10:
                continue
            
            # Create surface cache key
            color = particle['color']
            glow_color = particle.get('glow_color', color)
            length = int(particle['length'])
            width = int(particle['width'])
            
            particle_key = f"spark_{color[0]}_{color[1]}_{color[2]}_{glow_color[0]}_{glow_color[1]}_{glow_color[2]}_{length}_{width}_{alpha}"
            
            # Group particles by surface key for batch rendering
            if particle_key not in particle_batches:
                particle_batches[particle_key] = []
            
            rotation = particle.get('rotation', 0)
            particle_batches[particle_key].append((px, py, rotation))
        
        # Render batched particles
        self._render_particle_batches(particle_batches)
    
    def _render_particle_batches(self, particle_batches: Dict[str, List[Tuple[int, int, float]]]):
        """Render batched particles efficiently."""
        for particle_key, positions in particle_batches.items():
            # Get or create particle surface
            surf = self._get_or_create_particle_surface(particle_key)
            if surf is None:
                continue
                
            # Parse key for dimensions
            key_parts = particle_key.split('_')
            length = int(key_parts[7])
            width = int(key_parts[8])
            
            # Batch render all particles with this surface
            for pos_x, pos_y, rotation in positions:
                # Create rotated surface if needed
                if rotation != 0:
                    rotated_surf = pygame.transform.rotate(surf, rotation)
                    rect = rotated_surf.get_rect(center=(pos_x + length, pos_y + width))
                    self.screen.blit(rotated_surf, rect)
                else:
                    self.screen.blit(surf, (pos_x, pos_y))
    
    def _get_or_create_particle_surface(self, particle_key: str) -> Optional[pygame.Surface]:
        """Get cached particle surface or create new one."""
        if particle_key in self.particle_surfaces:
            return self.particle_surfaces[particle_key]
        
        # Parse particle key
        try:
            parts = particle_key.split('_')
            r, g, b = int(parts[1]), int(parts[2]), int(parts[3])
            gr, gg, gb = int(parts[4]), int(parts[5]), int(parts[6])
            length, width = int(parts[7]), int(parts[8])
            alpha = int(parts[9])
            
            # Create particle surface
            particle_surf = pygame.Surface((length * 2, width * 2), pygame.SRCALPHA)
            
            # Draw particle with glow effect
            core_color = (r, g, b, alpha)
            glow_color = (gr, gg, gb, alpha // 2)
            
            # Draw glow (larger, more transparent)
            pygame.draw.ellipse(particle_surf, glow_color, 
                              (0, 0, length * 2, width * 2))
            
            # Draw core (smaller, more opaque)
            core_rect = (length // 2, width // 2, length, width)
            pygame.draw.ellipse(particle_surf, core_color, core_rect)
            
            # Cache the surface
            self.particle_surfaces[particle_key] = particle_surf
            return particle_surf
            
        except (ValueError, IndexError):
            return None
    
    def _render_explosion_effects(self, block_type: str, block_x: int, block_y: int, 
                                block_width: int, block_height: int, progress: float):
        """Render explosion sprite effects for different block types."""
        explosion_frames = None
        
        # Select appropriate explosion frames based on block type
        if 'blue' in block_type and self.explosion_frames:
            explosion_frames = self.explosion_frames
        elif 'green' in block_type and self.green_explosion_frames:
            explosion_frames = self.green_explosion_frames
        elif 'red' in block_type and self.red_explosion_frames:
            explosion_frames = self.red_explosion_frames
        elif 'yellow' in block_type and self.yellow_explosion_frames:
            explosion_frames = self.yellow_explosion_frames
        
        if not explosion_frames or len(explosion_frames) == 0:
            print(f"DEBUG: No explosion frames found for block type: {block_type}")
            return
        
        # Calculate frame to display
        frame_count = len(explosion_frames)
        explosion_progress = progress / 0.5  # Convert to 0-1 range
        
        # Calculate frame index with repetition for initial frames
        if explosion_progress < 0.3:
            frame_index = (int(explosion_progress * self.explosion_repeat_frames * self.explosion_initial_frames)) % self.explosion_initial_frames
        else:
            remaining_frames = frame_count - self.explosion_initial_frames
            frame_progress = (explosion_progress - 0.3) / 0.7
            frame_index = self.explosion_initial_frames + int(frame_progress * remaining_frames)
        
        # Get current frame
        current_frame = explosion_frames[frame_index]
        
        # Calculate scale
        scale_progress = min(1.0, explosion_progress * 2)
        current_scale = self.explosion_scale_start + (self.explosion_scale_end - self.explosion_scale_start) * scale_progress
        
        # Scale and draw explosion
        scaled_width = int(block_width * current_scale)
        scaled_height = int(block_height * current_scale)
        scaled_frame = pygame.transform.scale(current_frame, (scaled_width, scaled_height))
        
        # Center explosion on block
        explosion_x = block_x + (block_width - scaled_width) // 2
        explosion_y = block_y + (block_height - scaled_height) // 2
        
        self.screen.blit(scaled_frame, (explosion_x, explosion_y))
    
    def render_falling_blocks(self, x_offset: int, y_offset: int, block_width: int, block_height: int):
        """Render all falling block animations."""
        current_time = time.time()
        
        for pos, block_data in list(self.state_manager.visual_falling_blocks.items()):
            x, y = pos
            
            # Calculate progress with easing
            elapsed = current_time - block_data['start_time']
            progress = min(1.0, elapsed / block_data['duration'])
            eased_progress = 1 - (1 - progress) ** 3  # Ease-out cubic

            # Interpolate position
            start_screen_y = y_offset + block_data['start_y'] * block_height
            end_screen_y = y_offset + y * block_height
            interp_y = start_screen_y + (end_screen_y - start_screen_y) * eased_progress
            
            screen_x = x_offset + x * block_width
            
            # Draw the block
            self._draw_block(screen_x, interp_y, block_width, block_height, block_data['block_type'])

            # Remove completed animations
            if progress >= 1.0:
                self.state_manager.visual_falling_blocks.pop(pos)
    
    def render_player_piece(self, x_offset: int, y_offset: int, block_width: int, block_height: int):
        """Renders the player-controlled piece (main and attached) using state from the state manager."""
        if not self.state_manager.visual_piece_position or not self.engine.main_piece:
            return

        # Draw the main piece
        main_pos = self.state_manager.visual_piece_position
        main_block_type = self.engine.main_piece  # Get the actual falling piece type
        
        if main_block_type:
            screen_x = x_offset + main_pos[0] * block_width
            screen_y = y_offset + main_pos[1] * block_height
            self._draw_block(screen_x, screen_y, block_width, block_height, main_block_type)

        # Draw the attached piece using smooth visual positioning
        attached_pos = self.engine.get_attached_visual_position()
        if attached_pos and self.engine.attached_piece:
            attached_block_type = self.engine.attached_piece  # Get the actual falling piece type
            
            if attached_block_type:
                screen_x = x_offset + attached_pos[0] * block_width
                screen_y = y_offset + attached_pos[1] * block_height
                self._draw_block(screen_x, screen_y, block_width, block_height, attached_block_type)

    def render_combo_texts(self):
        """Render combo text animations."""
        current_time = time.time()
        
        for combo_text in self.combo_texts[:]:  # Use slice to avoid modification during iteration
            elapsed = current_time - combo_text['start_time']
            
            if elapsed > combo_text['duration']:
                self.combo_texts.remove(combo_text)
                continue
            
            # Calculate text position with animation
            progress = elapsed / combo_text['duration']
            
            # Text rises and fades
            y_offset = -50 * progress  # Move up 50 pixels
            alpha = int(255 * (1.0 - progress))  # Fade out
            
            # Create text surface
            if combo_text['font']:
                text_surface = combo_text['font'].render(combo_text['text'], True, combo_text['color'])
                text_surface.set_alpha(alpha)
                
                # Calculate position
                text_x = combo_text['x'] - text_surface.get_width() // 2
                text_y = combo_text['y'] + y_offset
                
                self.screen.blit(text_surface, (text_x, text_y))
    
    def render_dust_particles(self):
        """Render dust particle effects."""
        current_time = time.time()
        
        for pos, particle in list(self.dust_particles.items()):
            elapsed = current_time - particle['start_time']
            
            if elapsed >= particle['duration']:
                self.dust_particles.pop(pos)
                continue
            
            # Calculate particle properties
            progress = elapsed / particle['duration']
            alpha = int(255 * (1.0 - progress))
            size = max(1, int(particle['size'] * (1.0 - progress)))
            
            # Calculate position
            x = int(particle['x'] + particle['vx'] * elapsed)
            y = int(particle['y'] + particle['vy'] * elapsed)
            
            # Draw particle
            color = (*particle['color'][:3], alpha)
            self._draw_particle(x, y, size, color)
    
    def _draw_block(self, x: float, y: float, width: int, height: int, block_type: str, brightness: float = 1.0):
        """Draws a single block to the screen."""
        if not block_type or block_type == 'empty':
            return
        asset_key = ''
        block_image = None
        
        if '_garbage' in block_type:
            # Use the colored garbage block images for better visual distinction
            asset_key = block_type  # e.g., 'red_garbage', 'blue_garbage'
            block_image = self.engine.puzzle_pieces.get(asset_key)
        elif '_breaker' in block_type:
            asset_key = block_type.replace('_breaker', 'breaker')
            block_image = self.engine.puzzle_pieces.get(asset_key)
        else:
            # Normal blocks
            asset_key = block_type.replace('_block', 'block')
            block_image = self.engine.puzzle_pieces.get(asset_key)
        
        if block_image:
            # Scale the image to fit the block size
            scaled_image = pygame.transform.scale(block_image, (width, height))
            self.screen.blit(scaled_image, (x, y))
        else:
            # Fallback: draw colored rectangle
            color_map = {
                'red_block': (255, 0, 0),
                'blue_block': (0, 0, 255),
                'green_block': (0, 255, 0),
                'yellow_block': (255, 255, 0),
                'red_garbage': (255, 100, 100),
                'blue_garbage': (100, 100, 255),
                'green_garbage': (100, 255, 100),
                'yellow_garbage': (255, 255, 100)
            }
            color = color_map.get(block_type, (128, 128, 128))
            pygame.draw.rect(self.screen, color, (x, y, width, height))
    
    def _apply_brightness(self, surface: pygame.Surface, brightness: float) -> pygame.Surface:
        """Apply brightness adjustment to a surface."""
        # Create a copy of the surface to avoid modifying the original
        darkened_surface = surface.copy()
        
        # Create a brightness overlay
        brightness_overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        
        # Calculate the darkness level (1.0 = no change, 0.0 = completely black)
        darkness = 1.0 - brightness
        alpha = int(255 * darkness)
        
        # Fill with black with appropriate alpha for darkening
        brightness_overlay.fill((0, 0, 0, alpha))
        
        # Apply the overlay using BLEND_MULT for darkening effect
        darkened_surface.blit(brightness_overlay, (0, 0), special_flags=pygame.BLEND_MULT)
        
        return darkened_surface
    
    def _draw_particle(self, x: int, y: int, size: int, color: Tuple[int, int, int, int]):
        """Draw a single particle."""
        if size <= 0:
            return
            
        # Create surface for particle with alpha
        particle_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        pygame.draw.circle(particle_surf, color, (size, size), size)
        
        self.screen.blit(particle_surf, (x - size, y - size))
    
    def _ease_out_quad(self, progress: float) -> float:
        """Quadratic easing out - decelerating to zero velocity."""
        return -progress * (progress - 2)
    
    def manage_particle_cache(self):
        """Manage the particle surface cache to prevent memory leaks."""
        # Limit cache size to prevent memory issues
        max_cache_size = 50
        if len(self.particle_surfaces) > max_cache_size:
            # Remove oldest entries
            keys_to_remove = list(self.particle_surfaces.keys())[:len(self.particle_surfaces) - max_cache_size]
            for key in keys_to_remove:
                del self.particle_surfaces[key]
    
    def update_animations(self):
        """Update all animations."""
        # Update animation references
        self.update_animation_refs()
        
        # Manage particle cache
        self.manage_particle_cache()
