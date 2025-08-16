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
        # Renderer landing controls (read via settings if present)
        self.snap_on_land: bool = True
        self.landing_epsilon_px: float = 0.0
        # One-frame suppression window to avoid double-draw on land
        self.suppress_falling_draw_until_ms: int = 0
        try:
            settings = getattr(self.engine, 'settings_system', None)
            if settings is not None and hasattr(settings, 'get'):
                self.snap_on_land = bool(settings.get('renderer.snap_on_land', True))
                eps = settings.get('renderer.landing_epsilon_px', 1)
                try:
                    self.landing_epsilon_px = max(0.0, float(eps))
                except Exception:
                    self.landing_epsilon_px = 0.0
        except Exception:
            # Defaults already set
            pass
        
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
        # CRITICAL FIX: Initialize attached piece position properly
        self.visual_attached_piece_position = [0, 0]
        self.is_animating = False
        self.target_position = [0, 0]
        self.anim_start_time = 0
        self.anim_duration = 0.035  # Faster animation (35ms) for more responsive feel
        
    def _initialize_breaking_animation_state(self):
        """Initialize breaking animation state."""
        self.breaking_blocks_animations = {}  # Format: {(x, y): {start_time, progress, total_duration}}
        # Longer visual so sprite animations are visible (engine gate remains 100ms but will wait on renderer)
        self.breaking_animation_duration = 0.50  # seconds
        
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

        # Horizontal sliding animations (paced to breaking animation)
        # Format: {(x, y): {start_x, start_time, duration, block_type}}
        self.visual_sliding_blocks = {}
        
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

        # Lightning visual state removed (effects disabled)
        
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
        # CRITICAL FIX: Reset attached piece position properly
        self.visual_attached_piece_position = [0, 0]
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
        if not hasattr(self, 'visual_sliding_blocks'):
            self.visual_sliding_blocks = {}
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
            self.breaking_animation_duration = 0.35
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
            
    def update_breaking_animations(self, current_ms: int):
        """Update breaking block animations using millisecond timing (monotonic)."""
        # Skip if we don't have breaking animations
        if not hasattr(self, 'breaking_blocks_animations'):
            self.breaking_blocks_animations = {}
            return
            
        # Process each breaking animation
        for pos, block_data in list(self.breaking_blocks_animations.items()):
            # Resolve timing fields with backward compatibility
            try:
                start_ms = int(block_data.get('start_ms')) if 'start_ms' in block_data else int(float(block_data.get('start_time', 0)) * 1000.0)
            except Exception:
                start_ms = 0
            try:
                total_ms = int(block_data.get('total_duration_ms')) if 'total_duration_ms' in block_data else int(float(block_data.get('total_duration', self.breaking_animation_duration)) * 1000.0)
            except Exception:
                total_ms = int(self.breaking_animation_duration * 1000.0)

            # Calculate elapsed time in ms
            elapsed_ms = int(current_ms) - int(start_ms)

            # Check if the animation has expired
            if elapsed_ms > total_ms:
                # Remove expired animation
                self.breaking_blocks_animations.pop(pos)
                # Record the completion timestamp to avoid immediate replays
                try:
                    if hasattr(self, 'recent_break_timestamps'):
                        self.recent_break_timestamps[pos] = int(current_ms)
                        self.recently_broken_positions.add(pos)
                except Exception:
                    pass
                continue
                
            # Update progress
            try:
                block_data['progress'] = min(1.0, max(0.0, float(elapsed_ms) / float(max(1, total_ms))))
            except Exception:
                block_data['progress'] = 1.0
            
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
        # Prune stale recently_broken_positions so they don't block animations forever
        if hasattr(self, 'recent_break_timestamps') and self.recent_break_timestamps:
            stale_keys = []
            for pos, ts in list(self.recent_break_timestamps.items()):
                if current_time - ts > self.recent_break_history_time * 1000.0:
                    stale_keys.append(pos)
            for pos in stale_keys:
                self.recent_break_timestamps.pop(pos, None)
                self.recently_broken_positions.discard(pos)

        # Store a snapshot of the current grid state for the next frame's comparison
        current_grid_snapshot = [row[:] for row in self.engine.puzzle_grid]
        self.previous_grid_state = current_grid_snapshot
            
    def has_active_animations(self) -> bool:
        """Check if any animations are currently active."""
        return (
            bool(self.visual_falling_blocks) or 
            bool(getattr(self, 'visual_sliding_blocks', {})) or
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
        
    def cleanup_expired_animations(self, current_ms: int):
        """Remove expired animations using millisecond timing to prevent memory leaks."""
        # Clean up breaking animations
        for pos, data in list(self.breaking_blocks_animations.items()):
            try:
                start_ms = int(data.get('start_ms')) if 'start_ms' in data else int(float(data.get('start_time', 0)) * 1000.0)
                total_ms = int(data.get('total_duration_ms')) if 'total_duration_ms' in data else int(float(data.get('total_duration', self.breaking_animation_duration)) * 1000.0)
                if int(current_ms) - int(start_ms) > int(total_ms * 1.2):
                    self.breaking_blocks_animations.pop(pos, None)
            except Exception:
                pass
                    
        # Clean up recently broken positions
        for pos, timestamp in list(self.recent_break_timestamps.items()):
            try:
                if int(current_ms) - int(timestamp) > int(self.recent_break_history_time * 1000.0):
                    self.recent_break_timestamps.pop(pos, None)
                    self.recently_broken_positions.discard(pos)
            except Exception:
                pass
                
        # Clean up expired combo texts (combo_texts keep seconds-based start_time)
        try:
            now_s = float(current_ms) / 1000.0
            for combo_text in list(self.combo_texts):
                if now_s - combo_text.get('start_time', 0) > self.combo_text_duration:
                    self.combo_texts.remove(combo_text)
        except Exception:
            pass
                
        # Clean up expired dust particles (seconds-based fields)
        try:
            now_s = float(current_ms) / 1000.0
            for pos, particle in list(self.dust_particles.items()):
                if now_s - particle.get('start_time', 0) > particle.get('duration', 0):
                    self.dust_particles.pop(pos, None)
        except Exception:
            pass
                
        # Clean up expired cluster animations (seconds-based fields)
        try:
            now_s = float(current_ms) / 1000.0
            for cluster_id in list(self.cluster_animations.keys()):
                anim_data = self.cluster_animations[cluster_id]
                elapsed = now_s - anim_data['start_time']
                if elapsed > anim_data['duration']:
                    self.cluster_animations.pop(cluster_id, None)
        except Exception:
            pass
                
        # Clean up expired visual falling blocks (seconds-based fields)
        try:
            now_s = float(current_ms) / 1000.0
            for pos, data in list(self.visual_falling_blocks.items()):
                start_time = data.get('start_time', 0)
                duration = data.get('duration', 0.1)
                if now_s - start_time > duration:
                    self.visual_falling_blocks.pop(pos, None)
        except Exception:
            pass

        # Clean up expired visual sliding blocks (seconds-based fields)
        try:
            now_s = float(current_ms) / 1000.0
            for pos, data in list(getattr(self, 'visual_sliding_blocks', {}).items()):
                start_time = data.get('start_time', 0)
                duration = data.get('duration', 0.1)
                if now_s - start_time > duration:
                    self.visual_sliding_blocks.pop(pos, None)
        except Exception:
            pass
                
    def update_visual_piece_state(self):
        """Update visual piece position state."""
        if self.engine.main_piece:
            # Get pixel-perfect position from the engine
            self.visual_piece_position = self.engine.get_visual_position()
            self.visual_attached_position = self.engine.attached_position
            self.visual_attached_piece_position = self.engine.get_attached_visual_position()
            
            # Clear all animations in columns where the active piece is
            if hasattr(self, 'visual_falling_blocks'):
                main_x = int(self.visual_piece_position[0]) if self.visual_piece_position else 0
                # CRITICAL FIX: Safely handle attached piece position
                attached_x = int(self.visual_attached_piece_position[0]) if self.visual_attached_piece_position and len(self.visual_attached_piece_position) > 0 else main_x
                
                # Remove any animations in the same columns as active piece
                to_remove = []
                for pos in self.visual_falling_blocks:
                    if pos[0] == main_x or pos[0] == attached_x:
                        to_remove.append(pos)
                        
                for pos in to_remove:
                    self.visual_falling_blocks.pop(pos, None)

                # Also clear sliding animations in the same columns
                if hasattr(self, 'visual_sliding_blocks'):
                    to_remove_slide = []
                    for pos in self.visual_sliding_blocks:
                        if pos[0] == main_x or pos[0] == attached_x:
                            to_remove_slide.append(pos)
                    for pos in to_remove_slide:
                        self.visual_sliding_blocks.pop(pos, None)
                    
    def update_player_piece_state(self):
        """
        Updates the visual state of the player-controlled piece and clears
        any conflicting gravity-fall animations in the same columns.
        """
        if self.engine.main_piece:
            # Determine whether the piece would fit below right now
            can_move_down: bool = True
            try:
                if hasattr(self.engine, 'would_fit_below'):
                    can_move_down = bool(self.engine.would_fit_below())
            except Exception:
                can_move_down = True

            # Snap on the same frame we detect no-fit-below
            if self.snap_on_land and not can_move_down:
                # Use exact grid cell without sub-grid interpolation
                x, y = self.engine.piece_position
                iy = int(y)
                self.visual_piece_position = [float(x), float(iy)]
                # Also snap attached piece visual Y to grid to stop any easing carryover
                self.visual_attached_position = self.engine.attached_position
                att_vis = self.engine.get_attached_visual_position()
                if att_vis:
                    self.visual_attached_piece_position = [float(att_vis[0]), float(int(att_vis[1]))]
                else:
                    self.visual_attached_piece_position = att_vis
                # Start a short suppression window to prevent drawing the falling piece
                # in the same frame that placed grid blocks are drawn.
                try:
                    clk = getattr(self.engine, 'clock', None)
                    now_ms = int(clk.now_ms()) if clk and hasattr(clk, 'now_ms') else int(pygame.time.get_ticks())
                except Exception:
                    now_ms = int(pygame.time.get_ticks())
                # ~1/60s suppression is enough to skip one draw cycle
                self.suppress_falling_draw_until_ms = now_ms + 17
            else:
                # Get smooth position from engine
                self.visual_piece_position = self.engine.get_visual_position()
                self.visual_attached_position = self.engine.attached_position
                self.visual_attached_piece_position = self.engine.get_attached_visual_position()

            # Clear any gravity-fall animations in the columns where the active piece is
            # This prevents visual overlap and ensures the player's piece is unobstructed
            main_x = int(self.visual_piece_position[0]) if self.visual_piece_position else 0
            # CRITICAL FIX: Safely handle attached piece position
            attached_x = int(self.visual_attached_piece_position[0]) if self.visual_attached_piece_position and len(self.visual_attached_piece_position) > 0 else main_x
            
            # Remove any animations in the same columns as the active piece
            to_remove = [pos for pos in self.visual_falling_blocks if pos[0] in (main_x, attached_x)]
            for pos in to_remove:
                self.visual_falling_blocks.pop(pos, None)

            # Remove any sliding animations in the same columns as the active piece
            if hasattr(self, 'visual_sliding_blocks'):
                to_remove_slide = [pos for pos in self.visual_sliding_blocks if pos[0] in (main_x, attached_x)]
                for pos in to_remove_slide:
                    self.visual_sliding_blocks.pop(pos, None)
                
    def animations_in_progress(self):
        """Check if any core visual animations are currently active."""
        # Ensure collections exist before checking them
        self.ensure_state_initialized()
        
        # Return true if any animation collections are not empty
        return bool(self.breaking_blocks_animations or self.visual_falling_blocks or getattr(self, 'visual_sliding_blocks', {}))
                
    def clear_animations_if_no_piece(self):
        """Clear animations if there's no active piece (for debugging)."""
        if not self.engine.main_piece:
            self.breaking_blocks_animations.clear()
            self.visual_falling_blocks.clear()
            self.animated_garbage_blocks.clear()
    
    def update_animations(self):
        """Update all animations using a consistent millisecond time base."""
        # Prefer engine clock if available; fall back to pygame.get_ticks or perf counter
        now_ms = 0
        try:
            clk = getattr(self.engine, 'clock', None)
            if clk and hasattr(clk, 'now_ms'):
                now_ms = int(clk.now_ms())
            else:
                now_ms = int(pygame.time.get_ticks())
        except Exception:
            now_ms = int(time.perf_counter() * 1000.0)
        self.update_breaking_animations(now_ms)
        self.cleanup_expired_animations(now_ms)
