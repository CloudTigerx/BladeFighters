#!/usr/bin/env python3
"""
Animation State Management Module
Handles all animation state variables and their initialization/management
Extracted from puzzle_renderer.py for modular architecture
"""

import pygame
import time
from typing import Dict, List, Set, Any, Optional, Tuple


class AnimationStateManager:
    """
    Manages all animation state variables and their lifecycle.
    This class centralizes animation state to improve maintainability and testing.
    """
    
    def __init__(self, puzzle_engine):
        """Initialize all animation state variables."""
        self.engine = puzzle_engine
        self.screen = puzzle_engine.screen
        
        # Get screen dimensions for calculations
        self.width = self.screen.get_width()
        self.height = self.screen.get_height()
        
        # Initialize all animation state variables
        self._initialize_animation_settings()
        self._initialize_combo_text_state()
        self._initialize_visual_piece_state()
        self._initialize_breaking_animation_state()
        self._initialize_falling_block_state()
        self._initialize_particle_state()
        self._initialize_cluster_state()
        self._initialize_game_over_state()
        self._initialize_timing_state()
        
    def _initialize_animation_settings(self):
        """Initialize core animation settings."""
        self.enable_animation = True
        self.animation_frame_rate = 240  # Optimized for performance
        self.animation_timer = 0
        self.animation_frame_duration = 1.0 / self.animation_frame_rate
        self.animation_update_counter = 0  # Counter to skip frames
        self.animation_update_frequency = 1  # Only update animations every 2 frames
        
    def _initialize_combo_text_state(self):
        """Initialize combo text display state."""
        self.combo_texts = []  # List of active combo text displays
        self.combo_font = None  # Will be initialized when first needed
        self.combo_font_path = "puzzleassets/fonts/PermanentMarker-Regular.ttf"
        self.combo_font_size = 36
        self.combo_text_duration = 2.0  # How long combo text stays on screen
        self.combo_text_messages = {
            2: "2x Duo Combo!",
            3: "3x Trio Combo!",
            4: "4x Quad-tonic Combo!",
            5: "5x Destroyer Combo!",
            6: "6x Transcendant Combo!",
            7: "7x Overkill Combo!",
            8: "8x Ultimate Combo!",
            9: "9x Epic Combo!",
            10: "10x Legendary Combo!"
            # For higher values, we'll generate them dynamically
        }
        
        # Particle settings for combo text
        self.combo_particle_count = 30
        self.combo_particle_lifespan = 1.5  # seconds
        
    def _initialize_visual_piece_state(self):
        """Initialize visual piece position tracking."""
        self.visual_piece_position = [0, 0]
        self.visual_attached_position = 0
        self.is_animating = False
        self.target_position = [0, 0]
        self.anim_start_time = 0
        self.anim_duration = 0.035  # Faster animation (35ms) for more responsive feel
        
    def _initialize_breaking_animation_state(self):
        """Initialize breaking animation state."""
        self.breaking_blocks_animations = {}  # Format: {(x, y): {start_time, progress, total_duration}}
        self.breaking_animation_duration = 0.3  # 300ms for breaking animation
        
        # Track recently broken blocks to prevent unwanted cluster animations
        self.recently_broken_positions = set()
        self.recent_break_history_time = 1.0  # How long to remember broken blocks (in seconds)
        self.recent_break_timestamps = {}  # Format: {(x, y): timestamp}
        
    def _initialize_falling_block_state(self):
        """Initialize falling block animation state."""
        self.visual_falling_blocks = {}  # Format: {(x, y): {start_y, target_y, progress, start_time}}
        # Set fall speed to achieve 1.1 seconds from top to bottom of grid (13 rows)
        # For a single row drop, we need 1.1/13 = ~0.0846 seconds
        self.fall_animation_duration = 0.085  # 85ms per row of fall
        
        # Track garbage block animations
        self.animated_garbage_blocks = set()
        
    def _initialize_particle_state(self):
        """Initialize particle system state."""
        # Particle cache for better performance
        self.particle_surfaces = {}
        
        # Enhanced particle settings for breaking animations
        self.particle_count_per_block = 20  # Increased from 8 to 20 for more particles
        self.particle_max_speed = 4.0  # Increased from 2.0 to 4.0 for faster particles
        self.particle_min_speed = 1.0  # Increased from 0.5 to 1.0 for faster minimum speed
        self.particle_max_size = 5  # Increased from 3 to 5 for larger particles
        self.particle_min_size = 2  # Increased from 1 to 2 for larger minimum size
        self.particle_lifespan = 0.8  # Increased from 0.5 to 0.8 for longer-lasting particles
        
        # Dust particles tracking
        self.dust_particles = {}
        
        # Keep empty particles list for possible future use
        self.cluster_glow_particles = []
        
        # New rainbow trail effect settings
        self.rainbow_trail_enabled = True  # Enable/disable the effect
        self.rainbow_trail_threshold = 4   # Minimum combo size to show rainbow trails
        self.rainbow_trail_length = 5      # Number of positions to remember per particle
        self.rainbow_trail_fade = 0.85     # How quickly the trail fades (0-1)
        self.rainbow_colors = [
            (255, 0, 0),      # Red
            (255, 127, 0),    # Orange
            (255, 255, 0),    # Yellow
            (0, 255, 0),      # Green
            (0, 0, 255),      # Blue
            (75, 0, 130),     # Indigo
            (148, 0, 211)     # Violet
        ]
        
    def _initialize_cluster_state(self):
        """Initialize cluster animation state."""
        self.previous_clusters = []
        self.cluster_animations = {}  # Format: {cluster_id: {start_time, duration, blocks}}
        self.cluster_animation_duration = 1.0  # 1 second for cluster formation animation
        self.next_cluster_id = 0  # Unique ID for each cluster animation
        
        # Cluster spark particle settings
        self.cluster_particles = {}  # Format: {cluster_id: [particle_data]}
        self.sparks_per_block = 5  # Number of spark particles per block in cluster
        self.spark_speed = 0.5  # Base speed for spark movement
        self.spark_size = 2  # Size of spark particles
        self.spark_brightness = 1.2  # Multiplier for particle color brightness
        
    def _initialize_game_over_state(self):
        """Initialize game over animation state."""
        self.game_over_start_time = None
        self.game_over_duration = 2.0  # Duration of the fade in animation
        self.game_over_particles = []
        self.game_over_font = None
        self.game_over_font_size = 72
        self.game_over_text_color = (255, 50, 50)  # Red color for game over
        self.game_over_glow_color = (255, 100, 100, 180)  # Glow effect color
        
    def _initialize_timing_state(self):
        """Initialize animation timing and buffer state."""
        # Animation buffer setup
        self.current_animation_buffer = {}
        self.next_animation_buffer = {}
        self.buffer_swap_time = time.time()
        self.buffer_swap_interval = 1.0 / 240.0  # 240Hz update rate
        
        # Fixed timestep for logic updates
        self.fixed_timestep = 1.0 / 240.0  # 240Hz logic updates
        self.accumulator = 0.0
        self.last_frame_time = time.time()
        
        # Internal state for detecting falling blocks
        self.previous_grid_state = []

        # Clock for frame rate limiting
        self.clock = pygame.time.Clock()
        
    def reset_animation_state(self):
        """Reset all animation state to initial values."""
        # Reset collections
        self.combo_texts.clear()
        self.breaking_blocks_animations.clear()
        self.visual_falling_blocks.clear()
        self.dust_particles.clear()
        self.cluster_animations.clear()
        self.game_over_particles.clear()
        self.recently_broken_positions.clear()
        self.recent_break_timestamps.clear()
        self.animated_garbage_blocks.clear()
        
        # Reset state variables
        self.animation_timer = 0
        self.animation_update_counter = 0
        self.visual_piece_position = [0, 0]
        self.visual_attached_position = 0
        self.is_animating = False
        self.target_position = [0, 0]
        self.anim_start_time = 0
        self.next_cluster_id = 0
        self.game_over_start_time = None
        
        # Reset timing state
        self.accumulator = 0.0
        self.last_frame_time = time.time()
        self.buffer_swap_time = time.time()
        
    def ensure_state_initialized(self):
        """Ensure all animation state variables are properly initialized."""
        # Initialize collections if they don't exist
        if not hasattr(self, 'visual_falling_blocks'):
            self.visual_falling_blocks = {}
        if not hasattr(self, 'breaking_blocks_animations'):
            self.breaking_blocks_animations = {}
        if not hasattr(self, 'cluster_animations'):
            self.cluster_animations = {}
        if not hasattr(self, 'next_cluster_id'):
            self.next_cluster_id = 0
        if not hasattr(self, 'previous_clusters'):
            self.previous_clusters = []
        if not hasattr(self, 'cluster_animation_duration'):
            self.cluster_animation_duration = 0.5
        if not hasattr(self, 'breaking_animation_duration'):
            self.breaking_animation_duration = 0.3
        if not hasattr(self, 'dust_particles'):
            self.dust_particles = {}
        if not hasattr(self, 'combo_texts'):
            self.combo_texts = []
        if not hasattr(self, 'game_over_particles'):
            self.game_over_particles = []
        if not hasattr(self, 'recently_broken_positions'):
            self.recently_broken_positions = set()
        if not hasattr(self, 'recent_break_timestamps'):
            self.recent_break_timestamps = {}
        if not hasattr(self, 'animated_garbage_blocks'):
            self.animated_garbage_blocks = set()
            
    def update_breaking_animations(self, current_time):
        """Update and render any active breaking block animations."""
        # Skip if we don't have breaking animations
        if not hasattr(self, 'breaking_blocks_animations'):
            self.breaking_blocks_animations = {}
            return
            
        # Process each breaking animation
        for pos, block_data in list(self.breaking_blocks_animations.items()):
            # Calculate elapsed time
            elapsed = current_time - block_data['start_time']
            
            # Check if the animation has expired
            if elapsed > block_data['total_duration']:
                # Remove expired animation
                self.breaking_blocks_animations.pop(pos)
                continue
                
            # Update progress
            block_data['progress'] = min(1.0, elapsed / block_data['total_duration'])
            
            # Update particles for this breaking block
            if 'particles' in block_data:
                for particle in block_data['particles'][:]:
                    # Update position with gravity
                    particle['x'] += particle['vx'] * 0.016  # Assuming 60fps
                    particle['y'] += particle['vy'] * 0.016
                    
                    # Apply gravity
                    particle['vy'] += 0.1  # Increased gravity for faster falling
                    
                    # Update life but don't remove based on life
                    particle['life'] -= 0.016
                    
                    # Only remove particles that are off screen
                    if hasattr(self.engine, 'grid_y_offset') and hasattr(self.engine, 'block_height'):
                        screen_y = self.engine.grid_y_offset + (particle['y'] * self.engine.block_height)
                        if screen_y > self.engine.height + 100:  # Remove when well off screen
                            block_data['particles'].remove(particle)
            
    def update_falling_block_state(self, current_time, supported_cluster_positions, recently_broken_positions):
        """Update the state of falling blocks based on grid changes."""
        # Track current grid state to detect blocks that have been moved by gravity
        # This is a simple approach that only looks at the previous and current frame
        if self.previous_grid_state:
            # Compare previous grid with current grid to detect falling blocks
            for y in range(self.engine.grid_height - 1):  # Skip bottom row
                for x in range(self.engine.grid_width):
                    # If this cell was empty and now has a block, check if it fell from above
                    if (self.previous_grid_state[y][x] is None and
                        self.engine.puzzle_grid[y][x] is not None and
                        (x, y) not in supported_cluster_positions and
                        (x, y) not in recently_broken_positions):
                        
                        # Check above to see if it fell from there
                        if y > 0 and self.previous_grid_state[y-1][x] is not None:
                            # This block likely fell one step
                            pos = (x, y)
                            if pos not in self.visual_falling_blocks:
                                self.visual_falling_blocks[pos] = {
                                    'start_time': current_time,
                                    'duration': self.fall_animation_duration,
                                    'start_y': y - 1, # It fell from the block above
                                    'block_type': self.engine.puzzle_grid[y][x]
                                }

        # Store a snapshot of the current grid state for the next frame's comparison
        current_grid_snapshot = [row[:] for row in self.engine.puzzle_grid]
        self.previous_grid_state = current_grid_snapshot
            
    def has_active_animations(self) -> bool:
        """Check if any animations are currently active."""
        return (
            bool(self.visual_falling_blocks) or 
            bool(self.breaking_blocks_animations) or
            bool(self.cluster_animations) or
            bool(self.combo_texts) or
            bool(self.dust_particles) or
            bool(self.game_over_particles) or
            self.is_animating
        )
        
    def get_animation_state_summary(self) -> Dict[str, Any]:
        """Get a summary of current animation state for debugging."""
        return {
            'enable_animation': self.enable_animation,
            'animation_timer': self.animation_timer,
            'active_falling_blocks': len(self.visual_falling_blocks),
            'active_breaking_blocks': len(self.breaking_blocks_animations),
            'active_cluster_animations': len(self.cluster_animations),
            'active_combo_texts': len(self.combo_texts),
            'active_dust_particles': len(self.dust_particles),
            'active_game_over_particles': len(self.game_over_particles),
            'is_animating': self.is_animating,
            'next_cluster_id': self.next_cluster_id,
            'has_active_animations': self.has_active_animations()
        }
        
    def cleanup_expired_animations(self, current_time: float):
        """Remove expired animations to prevent memory leaks."""
        # Clean up breaking animations
        for pos, data in list(self.breaking_blocks_animations.items()):
            if 'start_time' in data and 'total_duration' in data:
                if current_time - data['start_time'] > data['total_duration'] * 1.2:
                    self.breaking_blocks_animations.pop(pos, None)
                    
        # Clean up recently broken positions
        for pos, timestamp in list(self.recent_break_timestamps.items()):
            if current_time - timestamp > self.recent_break_history_time:
                self.recent_break_timestamps.pop(pos, None)
                self.recently_broken_positions.discard(pos)
                
        # Clean up expired combo texts
        for combo_text in list(self.combo_texts):
            if current_time - combo_text.get('start_time', 0) > self.combo_text_duration:
                self.combo_texts.remove(combo_text)
                
        # Clean up expired dust particles
        for pos, particle in list(self.dust_particles.items()):
            if current_time - particle.get('start_time', 0) > particle.get('duration', 0):
                self.dust_particles.pop(pos, None)
                
        # Clean up expired cluster animations
        for cluster_id in list(self.cluster_animations.keys()):
            anim_data = self.cluster_animations[cluster_id]
            elapsed = current_time - anim_data['start_time']
            if elapsed > anim_data['duration']:
                self.cluster_animations.pop(cluster_id, None)
                
    def update_visual_piece_state(self):
        """Update visual piece position state."""
        if self.engine.main_piece:
            # Get pixel-perfect position from the engine
            self.visual_piece_position = self.engine.get_visual_position()
            self.visual_attached_position = self.engine.attached_position
            self.visual_attached_piece_position = self.engine.get_attached_visual_position()
            
            # Clear all animations in columns where the active piece is
            if hasattr(self, 'visual_falling_blocks'):
                main_x = int(self.visual_piece_position[0])
                attached_x = int(self.visual_attached_piece_position[0])
                
                # Remove any animations in the same columns as active piece
                to_remove = []
                for pos in self.visual_falling_blocks:
                    if pos[0] == main_x or pos[0] == attached_x:
                        to_remove.append(pos)
                        
                for pos in to_remove:
                    self.visual_falling_blocks.pop(pos, None)
                    
    def update_player_piece_state(self):
        """
        Updates the visual state of the player-controlled piece and clears
        any conflicting gravity-fall animations in the same columns.
        """
        if self.engine.main_piece:
            # Get pixel-perfect position from the engine
            self.visual_piece_position = self.engine.get_visual_position()
            self.visual_attached_position = self.engine.attached_position
            self.visual_attached_piece_position = self.engine.get_attached_visual_position()

            # Clear any gravity-fall animations in the columns where the active piece is
            # This prevents visual overlap and ensures the player's piece is unobstructed
            main_x = int(self.visual_piece_position[0])
            attached_x = int(self.visual_attached_piece_position[0])
            
            # Remove any animations in the same columns as the active piece
            to_remove = [pos for pos in self.visual_falling_blocks if pos[0] in (main_x, attached_x)]
            for pos in to_remove:
                self.visual_falling_blocks.pop(pos, None)
                
    def animations_in_progress(self):
        """Check if any core visual animations are currently active."""
        # Ensure collections exist before checking them
        self.ensure_state_initialized()
        
        # Return true if any animation collections are not empty
        return bool(self.breaking_blocks_animations or self.visual_falling_blocks)
                
    def clear_animations_if_no_piece(self):
        """Clear animations if no active piece and no chain reaction."""
        if not self.engine.main_piece and not self.engine.chain_reaction_in_progress:
            # Only clear animations if there's no chain reaction in progress
            # This allows animations to complete properly
            if hasattr(self, 'visual_falling_blocks'):
                self.visual_falling_blocks.clear()
            if hasattr(self, 'breaking_blocks_animations'):
                self.breaking_blocks_animations.clear()
