import pygame
import sys
import os
import time
import math
import random
import traceback
from typing import Dict

# Import animation modules
from .Animations.Animation_Rendering import AnimationRenderer
from .Animations.AnimationStateManagement import AnimationStateManager

# GarbageBlockState removed - no longer needed

# Global exception handler for pygame drawing errors
def safe_pygame_draw(func, *args, **kwargs):
    """Wrapper to safely call pygame drawing functions with error reporting."""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        print(f"[DEBUG] Pygame draw error in {func.__name__}: args={args}, kwargs={kwargs}, error={e}")
        traceback.print_exc()
        return None

# Global exception handler for any pygame-related errors
import sys
original_excepthook = sys.excepthook

def custom_excepthook(exc_type, exc_value, exc_traceback):
    """Custom exception handler to catch pygame-related errors."""
    if "pygame" in str(exc_value).lower() or "color" in str(exc_value).lower():
        print(f"[DEBUG] Pygame-related error caught: {exc_type.__name__}: {exc_value}")
        print("[DEBUG] Full traceback:")
        traceback.print_exception(exc_type, exc_value, exc_traceback)
    else:
        # Call the original exception handler for non-pygame errors
        original_excepthook(exc_type, exc_value, exc_traceback)

sys.excepthook = custom_excepthook

# Global variable to fix error
update_regions = []

class PuzzleRenderer:
    """
    Handles rendering and visual effects for the puzzle game.
    This class separates rendering logic from game mechanics.
    """
    def __init__(self, engine):
        """Initialize the puzzle renderer with an engine."""
        self.engine = engine
        self.screen = engine.screen
        print(f"[DEBUG] Renderer screen size: {self.screen.get_width()}x{self.screen.get_height()}")
        
        # Visual state tracking
        self.visual_state = {
            'grid_blocks': {},
            'falling_pieces': {},
            'breaking_animations': {},
            'last_update_time': 0
        }
        
        # Initialize animation manager
        self.animation_state_manager = AnimationStateManager(engine)
        self.animation_renderer = AnimationRenderer(self.screen, engine, self.animation_state_manager)
        
        # Get dimensions from engine
        self.block_width = self.engine.block_size
        self.block_height = self.engine.block_size
        
        # Initialize coordinate offsets
        self.current_x_offset = 0
        self.current_y_offset = 0
        
        # Update coordinate offsets based on engine settings
        self.update_coordinate_offsets()
        
        print(f"[DEBUG] PuzzleRenderer initialized with block size: {self.block_width}x{self.block_height}")
        print(f"[DEBUG] PuzzleRenderer offset: ({self.current_x_offset}, {self.current_y_offset})")
        
        # Set a reference to this renderer in the engine
        self.engine.renderer = self
        
        # Initialize screen shake attributes
        self.screen_shake = False
        self.shake_offset_x = 0
        self.shake_offset_y = 0
        
        # Get screen dimensions
        self.width = self.screen.get_width()
        self.height = self.screen.get_height()
        
        # Initialize block dimensions
        self.block_width = self.engine.block_size
        self.block_height = self.engine.block_size
        
        # Load explosion sprites using the engine's asset loader
        explosion_sprites = self.engine.asset_loader.preload_explosion_sprites()
        self.explosion_frames = explosion_sprites.get('blue_explode')
        self.yellow_explosion_frames = explosion_sprites.get('orange_explode')
        self.red_explosion_frames = explosion_sprites.get('yellow_explode')
        self.green_explosion_frames = explosion_sprites.get('blue_explode_alt')

        # Explosion animation settings
        if self.explosion_frames:
            self.explosion_duration = 0.3  # How long the explosion lasts (in seconds)
            self.explosion_repeat_frames = 2  # How many times to repeat the first few frames
            self.explosion_initial_frames = 3  # How many frames to repeat at the start
            self.explosion_scale_start = 0.5  # Starting scale (0.5 = half size)
            self.explosion_scale_end = 1.2    # Ending scale (1.2 = 20% larger than block)
        
        # Calculate grid position to center it on screen
        grid_width_pixels = self.engine.grid_width * self.block_width
        grid_height_pixels = self.engine.grid_height * self.block_height
        
        # Use engine-specific offsets if available (for TestMode), otherwise center on screen
        if hasattr(self.engine, 'grid_x_offset') and hasattr(self.engine, 'grid_y_offset'):
            self.current_x_offset = self.engine.grid_x_offset
            self.current_y_offset = self.engine.grid_y_offset
        else:
            self.current_x_offset = (self.screen.get_width() - grid_width_pixels) // 2
            self.current_y_offset = (self.screen.get_height() - grid_height_pixels) // 2
        
        # Ensure we can access the attack system through the engine
        # Attack system reference removed - no longer needed
        
        # Optimized animation settings - reduced from 120 to 60 fps
        self.enable_animation = True
        self.animation_frame_rate = 240  # Reduced from 120 to 60 for better performance
        self.animation_timer = 0
        self.animation_frame_duration = 1.0 / self.animation_frame_rate
        self.animation_update_counter = 0  # Counter to skip frames
        self.animation_update_frequency = 1  # Only update animations every 2 frames
        
        # Track recently broken blocks to prevent unwanted cluster animations
        self.recently_broken_positions = set()
        self.recent_break_history_time = 1.0  # How long to remember broken blocks (in seconds)
        self.recent_break_timestamps = {}  # Format: {(x, y): timestamp}
        
        # Track clusters for animations - MOVED UP before update_visual_state call
        self.previous_clusters = []
        self.cluster_animations = {}  # Format: {cluster_id: {start_time, duration, blocks}}
        self.cluster_animation_duration = 1.0  # 1 second for cluster formation animation
        self.next_cluster_id = 0  # Unique ID for each cluster animation
        
        # Initialize animated_garbage_blocks set to track garbage block animations
        self.animated_garbage_blocks = set()
        
        # Cluster spark particle settings
        self.cluster_particles = {}  # Format: {cluster_id: [particle_data]}
        self.sparks_per_block = 5  # Number of spark particles per block in cluster
        self.spark_speed = 0.5  # Base speed for spark movement
        self.spark_size = 2  # Size of spark particles
        self.spark_brightness = 1.2  # Multiplier for particle color brightness
        
        # Cluster glow effect settings
        self.cluster_glow_effects = {}  # Format: {cluster_id: {blocks, color, start_time, intensity}}
        self.cluster_glow_duration = 2.0  # How long each glow cycle lasts
        self.cluster_glow_intensity = 0.8  # Base glow intensity (0.0 to 1.0)
        self.cluster_glow_pulse_speed = 3.0  # How fast the pulse effect cycles
        self.cluster_glow_fade_time = 0.5  # How long it takes for glow to fade when cluster breaks
        
        # Animation buffer setup
        self.current_animation_buffer = {}
        self.next_animation_buffer = {}
        self.buffer_swap_time = time.time()
        self.buffer_swap_interval = 1.0 / 240.0  # 240Hz update rate
        
        # Fixed timestep for logic updates
        self.fixed_timestep = 1.0 / 240.0  # 240Hz logic updates
        self.accumulator = 0.0
        self.last_frame_time = time.time()
        
        # At the beginning of the main game loop
        pygame.display.set_mode((self.engine.width, self.engine.height), pygame.HWSURFACE | pygame.DOUBLEBUF)
        
        # Or manually implement frame limiting
        self.clock = pygame.time.Clock()
        
        # Initialize modular animation system
        self.animation_state_manager = AnimationStateManager(engine)
        self.animation_renderer = AnimationRenderer(self.screen, engine, self.animation_state_manager)
        
        # Initialize piece visuals now that the animation system is ready
        self.update_visual_state()
    
    def animations_in_progress(self):
        """Pass-through method to check animation status from the state manager."""
        if not hasattr(self, 'animation_state_manager'):
            return False
        return self.animation_state_manager.animations_in_progress()
    
    def update_coordinate_offsets(self):
        """Update coordinate offsets, useful when screen changes or TestMode repositions grids."""
        grid_width_pixels = self.engine.grid_width * self.block_width
        grid_height_pixels = self.engine.grid_height * self.block_height
        
        # Use engine-specific offsets if available (for TestMode), otherwise center on screen
        if hasattr(self.engine, 'grid_x_offset') and hasattr(self.engine, 'grid_y_offset'):
            self.current_x_offset = self.engine.grid_x_offset
            self.current_y_offset = self.engine.grid_y_offset
        else:
            self.current_x_offset = (self.screen.get_width() - grid_width_pixels) // 2
            self.current_y_offset = (self.screen.get_height() - grid_height_pixels) // 2
    
    def _get_block_color(self, position):
        """Get the color of a block at a given position (x, y)."""
        x, y = position
        
        # Check if position is valid
        if not (0 <= x < self.engine.grid_width and 0 <= y < self.engine.total_grid_height):
            return 'white'  # Default color for invalid positions
        
        # Get block type at position
        block_type = self.engine.puzzle_grid[y][x]
        if not block_type:
            return 'white'  # Default color for empty blocks
        
        # Extract color from block type (e.g., "red_breaker" -> "red")
        color = block_type.split('_')[0]
        
        # Map color names to RGB values
        color_map = {
            'red': (255, 0, 0),
            'blue': (0, 0, 255),
            'green': (0, 255, 0),
            'yellow': (255, 255, 0),
            'gray': (128, 128, 128),
            'white': (255, 255, 255)
        }
        
        return color_map.get(color, (255, 255, 255))  # Default to white if color not found
    


    def update_visual_state(self):
        """Update the visual state to match the current game state."""
        # Initialize collections if they don't exist
        self.animation_state_manager.ensure_state_initialized()
            
        # Get the visual position with micro-movement interpolation
        self.animation_state_manager.update_player_piece_state()
        
        # Reset animation state if no active piece - prevents animations without active piece
        if not self.engine.main_piece and not self.engine.chain_reaction_in_progress:
            # Only clear animations if there's no chain reaction in progress
            # and no animations are currently playing.
            if not self.animations_in_progress():
                self.animation_state_manager.visual_falling_blocks.clear()
                self.animation_state_manager.breaking_blocks_animations.clear()
        
        # CRITICAL FIX: Only check for clusters when NO piece is falling
        # This prevents cluster detection from interfering with falling pieces
        current_time = time.time()
        
        # Add frame throttling for cluster detection
        if not hasattr(self, 'last_cluster_check_time'):
            self.last_cluster_check_time = 0
        
        cluster_check_interval = 0.016  # Check every ~16ms (60fps rate)
        
        # Get current clusters (ONLY if no piece is falling and no chain reaction)
        current_clusters = []
        should_check_clusters = (
            not self.engine.main_piece and  # No falling piece
            not self.engine.chain_reaction_in_progress and  # No chain reaction
            current_time - self.last_cluster_check_time >= cluster_check_interval
        )
        
        if should_check_clusters:
            if hasattr(self.engine, 'find_all_clusters'):
                current_clusters = self.engine.find_all_clusters()
            self.last_cluster_check_time = current_time
        elif hasattr(self, 'previous_clusters'):
            # Use cached clusters from previous frame
            current_clusters = self.previous_clusters
        
        # Only process cluster animations if we're not interfering with falling pieces
        if not self.engine.main_piece and not self.engine.chain_reaction_in_progress:
            # Detect newly formed clusters by comparing with previous frame
            if hasattr(self, 'previous_clusters'):
                # Find clusters that are in current_clusters but weren't in previous_clusters
                for new_cluster in current_clusters:
                    # Check if this cluster is new
                    is_new_cluster = True
                    for old_cluster in self.previous_clusters:
                        # If more than 80% of blocks match, consider it the same cluster
                        intersection = new_cluster.intersection(old_cluster)
                        if len(intersection) >= 0.8 * len(new_cluster):
                            is_new_cluster = False
                            break
                    
                    # If it's a new cluster, create an animation for it
                    if is_new_cluster and len(new_cluster) >= 4:  # Only animate clusters of 4+ blocks
                        cluster_id = self.next_cluster_id
                        self.next_cluster_id += 1
                        
                        self.cluster_animations[cluster_id] = {
                            'start_time': current_time,
                            'duration': self.cluster_animation_duration,
                            'blocks': new_cluster.copy(),
                            'color': self._get_block_color(next(iter(new_cluster)))  # Get color from first block
                        }
                        
                        # RE-ENABLE CLUSTER GLOW EFFECTS
                        # Add cluster glow effect for new cluster
                        self.cluster_glow_effects[cluster_id] = {
                            'blocks': new_cluster.copy(),
                            'color': self._get_block_color(next(iter(new_cluster))),
                            'start_time': current_time,
                            'intensity': self.cluster_glow_intensity
                        }
        
        # Update cluster animations
        for cluster_id in list(self.cluster_animations.keys()):
            anim_data = self.cluster_animations[cluster_id]
            elapsed = current_time - anim_data['start_time']
            
            # Remove completed animations
            if elapsed > anim_data['duration']:
                self.cluster_animations.pop(cluster_id, None)
        
        # RE-ENABLE CLUSTER GLOW EFFECTS
        # Update cluster glow effects
        for cluster_id in list(self.cluster_glow_effects.keys()):
            glow_data = self.cluster_glow_effects[cluster_id]
            cluster_blocks = glow_data['blocks']
            
            # IMMEDIATE FIX: Remove glow effect if any block is currently breaking
            cluster_has_breaking_blocks = False
            for block_pos in cluster_blocks:
                if block_pos in self.animation_state_manager.breaking_blocks_animations:
                    cluster_has_breaking_blocks = True
                    break
            
            # Remove glow immediately when blocks start breaking
            if cluster_has_breaking_blocks:
                self.cluster_glow_effects.pop(cluster_id, None)
                continue  # Skip to next cluster
            
            # Check if this cluster still exists
            cluster_still_exists = False
            for current_cluster in current_clusters:
                # Check if more than 80% of blocks still match
                intersection = cluster_blocks.intersection(current_cluster)
                if len(intersection) >= 0.8 * len(cluster_blocks):
                    cluster_still_exists = True
                    # Update the glow effect with current cluster blocks
                    glow_data['blocks'] = current_cluster.copy()
                    break
            
            # Remove glow effect if cluster no longer exists
            if not cluster_still_exists:
                self.cluster_glow_effects.pop(cluster_id, None)
        
        # Store current clusters for next frame comparison
        self.previous_clusters = current_clusters
        
        # ENABLE BREAKING ANIMATIONS AND ENHANCE THEM
        current_time = time.time()
        
        # Clear any expired breaking animations
        if hasattr(self, 'breaking_blocks_animations'):
            for pos, data in list(self.animation_state_manager.breaking_blocks_animations.items()):
                if 'start_time' in data and 'total_duration' in data:
                    if current_time - data['start_time'] > data['total_duration'] * 1.2:
                        self.animation_state_manager.breaking_blocks_animations.pop(pos, None)
            
        # Add new breaking animations
        if hasattr(self.engine, 'breaking_blocks'):
            for x, y, start_time, delay, block_color, is_breaker in self.engine.breaking_blocks:
                pos_key = (x, y)
                # Skip if we already have an animation for this position
                if pos_key in self.animation_state_manager.breaking_blocks_animations:
                    continue
                
                # Get the actual block type with breaker suffix if needed
                # FIX: Only add suffix if it's not already there
                if "_breaker" in block_color:
                    # The block is already a breaker type, don't add suffix again
                    block_type = block_color
                else:
                    # Only add suffix for non-breaker types that need to become breakers
                    block_type = block_color + ('_breaker' if is_breaker else '')
                
                # Try to get the block surface from the engine (same logic as in _draw_block)
                # Strip any suffixes when checking for base image
                clean_type = block_type.replace('_breaker', '').replace('_garbage', '')
                is_garbage = '_garbage' in block_type
                
                # Create detailed breaking animation with particles
                try:
                    # Initialize breaking animation
                    self.animation_state_manager.breaking_blocks_animations[pos_key] = {
                        'start_time': current_time,
                        'progress': 0.0,
                        'total_duration': self.animation_state_manager.breaking_animation_duration,
                        'block_type': block_type
                    }
                    
                    # Add particles if possible
                    if hasattr(self, 'create_dust_particles'):
                        # Make sure position is valid before creating particles
                        if isinstance(x, (int, float)) and isinstance(y, (int, float)):
                            try:
                                self.animation_state_manager.breaking_blocks_animations[pos_key]['particles'] = self.create_dust_particles(x, y, block_color)
                            except Exception as e:
                                print(f"Error creating dust particles: {e}")
                                self.animation_state_manager.breaking_blocks_animations[pos_key]['particles'] = []
                        else:
                            # Empty particles list if coordinates aren't valid
                            self.animation_state_manager.breaking_blocks_animations[pos_key]['particles'] = []
                except Exception as e:
                    print(f"Error creating breaking animation: {e}")
        
        # OPTIMIZE: Only calculate cluster support when no piece is falling
        supported_cluster_positions = set()
        
        # Only recalculate supported positions if no piece is falling
        if not self.engine.main_piece and not self.engine.chain_reaction_in_progress:
            if (current_time - self.last_cluster_check_time < cluster_check_interval and 
                hasattr(self, 'cached_supported_positions')):
                supported_cluster_positions = self.cached_supported_positions
            else:
                # Recalculate supported positions
                if hasattr(self.engine, 'find_all_clusters'):
                    clusters = current_clusters  # Use already calculated clusters
                    
                    # Now identify which columns in each cluster have support
                    for cluster_blocks in clusters:
                        # Group blocks by column
                        columns = {}
                        for x, y in cluster_blocks:
                            if x not in columns:
                                columns[x] = []
                            columns[x].append(y)
                        
                        # Check each column for support
                        for x, y_values in columns.items():
                            bottom_y = max(y_values)
                            
                            # Check if bottom of grid or has support
                            has_support = False
                            if bottom_y >= self.engine.grid_height - 1:
                                has_support = True
                            else:
                                # Check for block below bottom block
                                below_pos = (x, bottom_y + 1)
                                if (below_pos not in cluster_blocks and 
                                    bottom_y + 1 < self.engine.grid_height and 
                                    self.engine.puzzle_grid[bottom_y + 1][x] is not None):
                                    has_support = True
                            
                            # If this column has support, add all blocks in this column to supported set
                            if has_support:
                                for y in y_values:
                                    supported_cluster_positions.add((x, y))
                                    # Also consider one position below to prevent animations starting below supported clusters
                                    if y + 1 < self.engine.grid_height:
                                        supported_cluster_positions.add((x, y + 1))
                
                # Cache the results
                self.cached_supported_positions = supported_cluster_positions
        
        self.animation_state_manager.update_falling_block_state(current_time, supported_cluster_positions, self.recently_broken_positions)
        
        # IMPORTANT: Improve the check for whether a block is part of a supported cluster
        # Make this check more strict to ensure clusters don't fall inappropriately
        if hasattr(self, 'previous_grid_state'):
            for y in range(self.engine.grid_height - 1):  # Skip bottom row
                for x in range(self.engine.grid_width):
                    # Add this improved check for clusters:
                    # For any block, check if it's part of a supported cluster
                    # If it is, NEVER animate it falling - this ensures cluster integrity
                    current_pos = (x, y)
                    if current_pos in supported_cluster_positions:
                        # If this position is in a supported cluster, remove any animation
                        if current_pos in self.animation_state_manager.visual_falling_blocks:
                            self.animation_state_manager.visual_falling_blocks.pop(current_pos, None)
    
    def update_animations(self):
        """Update all animations."""
        self.animation_state_manager.update_animations()
        self.animation_renderer.update_animations()
    
    def draw_game_screen(self):
        """Draw the complete game screen with display management (for standalone use)."""
        print(f"[DEBUG] draw_game_screen called for engine: {self.engine}")
        try:
            # Clear the screen
            self.screen.fill((0, 0, 0))
            
            # Draw the game content
            self.draw_game_content()
            
            # Update the display
            pygame.display.flip()
            
            # Limit frame rate
            self.clock.tick(self.animation_frame_rate)
        except Exception as e:
            print(f"[DEBUG] Error in draw_game_screen: {e}")
            traceback.print_exc()
    
    def draw_game_content(self):
        """Draw the game content without display management (for use in TestMode)."""
        try:
            # Update coordinate offsets in case they changed
            self.update_coordinate_offsets()
            
            # Draw the grid background
            self.draw_grid_background()
            
            # Draw the grid blocks
            self.draw_grid_blocks()
            
            # Draw the falling piece
            self.draw_falling_piece()
            
            # Draw the next piece preview if configured
            if hasattr(self, 'preview_side'):
                if self.preview_side == 'left':
                    self.draw_next_piece_preview()
                elif self.preview_side == 'right':
                    self.draw_next_piece_preview_right()
            
            # Draw the score and level
            self.draw_score_and_level()
            
            # Draw the game over screen if the game is over
            self.draw_game_over_screen()
            
        except Exception as e:
            print(f"[DEBUG] Error in draw_game_content: {e}")
            traceback.print_exc()
    
    def draw_grid_background(self):
        """Draws the background of the puzzle grid."""
        # Calculate the starting position to center the grid
        start_x = self.current_x_offset
        start_y = self.current_y_offset
    
        # Draw the background image if it exists
        if hasattr(self.engine, 'puzzle_background') and self.engine.puzzle_background:
            self.screen.blit(self.engine.puzzle_background, (start_x, start_y))
        else:
            # Fallback to a solid color if no background image
            grid_width = self.engine.grid_width * self.block_width
            grid_height = self.engine.grid_height * self.block_height
            pygame.draw.rect(self.screen, (100, 100, 100), (start_x, start_y, grid_width, grid_height))

        # Draw grid lines
        grid_width = self.engine.grid_width * self.block_width
        grid_height = self.engine.grid_height * self.block_height
        
        # Draw horizontal lines
        for i in range(self.engine.grid_height + 1):
            pygame.draw.line(self.screen, (50, 50, 50), (start_x, start_y + i * self.block_height),
                             (start_x + grid_width, start_y + i * self.block_height))
        
        # Draw vertical lines
        for i in range(self.engine.grid_width + 1):
            pygame.draw.line(self.screen, (50, 50, 50), (start_x + i * self.block_width, start_y),
                             (start_x + i * self.block_width, start_y + grid_height))
    
    def draw_grid_blocks(self):
        """Draws all blocks in the puzzle grid."""
        # Calculate the starting position to center the grid
        start_x = self.current_x_offset
        start_y = self.current_y_offset

        # Draw the static blocks from the grid
        for y in range(self.engine.grid_height):
            for x in range(self.engine.grid_width):
                block_type = self.engine.puzzle_grid[y][x]
                if block_type:
                    # Do not draw blocks that are currently part of an animation
                    pos = (x, y)
                    if pos in self.animation_state_manager.breaking_blocks_animations or pos in self.animation_state_manager.visual_falling_blocks:
                        continue
                    
                    # Draw the static block
                    block_x = start_x + x * self.block_width
                    block_y = start_y + y * self.block_height
                    self.animation_renderer._draw_block(block_x, block_y, self.block_width, self.block_height, block_type)
        
        # Draw blocks that are visually falling with pixel-perfect animation
        self.animation_renderer.render_falling_blocks(start_x, start_y, self.block_width, self.block_height)
        
        # Use new animation renderer for breaking blocks
        for pos, block_data in self.animation_state_manager.breaking_blocks_animations.items():
            self.animation_renderer.render_breaking_block(pos, block_data, start_x, start_y, self.block_width, self.block_height)
        
        # Draw cluster glow effects
        self.draw_cluster_glow_effects()
        
        # Return updated regions for efficient screen updates
    
    def draw_falling_piece(self):
        """
        Draw the currently falling piece with pixel-perfect positioning and its attached piece.
        """
        # Use the same offsets as grid background and blocks for consistency
        x_offset = self.current_x_offset
        y_offset = self.current_y_offset
        
        # Delegate rendering to the animation renderer
        self.animation_renderer.render_player_piece(x_offset, y_offset, self.block_width, self.block_height)
    
    def draw_next_piece_preview(self):
        """Draws the preview for the next piece on the left side."""
        # Define preview area
        preview_x = self.current_x_offset - self.block_width * 3
        preview_y = self.current_y_offset
        preview_width = self.block_width * 2
        preview_height = self.block_height * 4

        # Draw border
        pygame.draw.rect(self.screen, (200, 200, 200), (preview_x, preview_y, preview_width, preview_height), 2)

        if self.engine.next_main_piece and self.engine.next_attached_piece:
            # Draw main piece
            main_piece_x = preview_x + (preview_width - self.block_width) / 2
            main_piece_y = preview_y + self.block_height
            self.animation_renderer._draw_block(main_piece_x, main_piece_y, self.block_width, self.block_height, self.engine.next_main_piece)
            
            # Draw attached piece above it
            attached_piece_y = preview_y
            self.animation_renderer._draw_block(main_piece_x, attached_piece_y, self.block_width, self.block_height, self.engine.next_attached_piece)

    def draw_next_piece_preview_right(self):
        """Draws the preview for the next piece on the right side."""
        # Define preview area
        preview_x = self.current_x_offset + self.engine.grid_width * self.block_width + self.block_width
        preview_y = self.current_y_offset
        preview_width = self.block_width * 2
        preview_height = self.block_height * 4

        # Draw border
        pygame.draw.rect(self.screen, (200, 200, 200), (preview_x, preview_y, preview_width, preview_height), 2)

        if self.engine.next_main_piece and self.engine.next_attached_piece:
            # Draw main piece
            main_piece_x = preview_x + (preview_width - self.block_width) / 2
            main_piece_y = preview_y + self.block_height
            self.animation_renderer._draw_block(main_piece_x, main_piece_y, self.block_width, self.block_height, self.engine.next_main_piece)
            
            # Draw attached piece above it
            attached_piece_y = preview_y
            self.animation_renderer._draw_block(main_piece_x, attached_piece_y, self.block_width, self.block_height, self.engine.next_attached_piece)

    def draw_score_and_level(self):
        """Draws the score and level on the screen."""
        # This method is no longer needed as score and level are handled by the engine
        # and rendered by the game_over_screen or elsewhere.
        pass

    def draw_game_over_screen(self):
        """Draws the game over screen if the game is over."""
        if not self.engine.game_active:  # Game is over when game_active is False
            # Draw a semi-transparent overlay
            overlay_surface = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
            overlay_surface.fill((0, 0, 0, 150))
            self.screen.blit(overlay_surface, (0, 0))

            # Draw game over text
            font = pygame.font.Font(None, 72)
            text = font.render("Game Over", True, (255, 255, 255))
            text_rect = text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
            self.screen.blit(text, text_rect)

            # Draw score and level if they exist
            if hasattr(self.engine, 'score'):
                score_text = pygame.font.Font(None, 48).render(f"Score: {self.engine.score}", True, (255, 255, 255))
                score_rect = score_text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 + 50))
                self.screen.blit(score_text, score_rect)

            if hasattr(self.engine, 'level'):
                level_text = pygame.font.Font(None, 48).render(f"Level: {self.engine.level}", True, (255, 255, 255))
                level_rect = level_text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 + 100))
                self.screen.blit(level_text, level_rect)

            # Draw restart button
            restart_text = pygame.font.Font(None, 36).render("Press R to Restart", True, (255, 255, 255))
            restart_rect = restart_text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 + 150))
            pygame.draw.rect(self.screen, (100, 100, 100), restart_rect.inflate(20, 10))
            self.screen.blit(restart_text, restart_rect)

            # Draw cursor
            cursor_pos = pygame.mouse.get_pos()
            cursor_rect = pygame.Rect(cursor_pos, (10, 10))
            pygame.draw.rect(self.screen, (255, 255, 255), cursor_rect)

            # Check for restart input
            if pygame.key.get_pressed()[pygame.K_r]:
                if hasattr(self.engine, 'restart_game'):
                    self.engine.restart_game()
                else:
                    # Fallback: restart by starting a new game
                    self.engine.start_game()
    
    def show_combo_text(self, combo_count, position=None):
        """Display combo text on screen when chain reactions occur."""
        if not hasattr(self, 'combo_text_font'):
            try:
                self.combo_text_font = pygame.font.Font(None, 48)
            except:
                self.combo_text_font = pygame.font.Font(None, 36)
        
        if combo_count > 1:
            # Create combo text
            combo_text = f"COMBO x{combo_count}!"
            color = (255, 255, 0)  # Yellow for combo text
            
            # Render text
            text_surface = self.combo_text_font.render(combo_text, True, color)
            
            # Determine position
            if position:
                text_x, text_y = position
                # Adjust position to center the text
                text_x -= text_surface.get_width() // 2
                text_y -= text_surface.get_height() // 2
            else:
                # Default to center of screen
                text_x = (self.screen.get_width() - text_surface.get_width()) // 2
                text_y = (self.screen.get_height() - text_surface.get_height()) // 2
            
            # Draw background rectangle for better visibility
            padding = 10
            bg_rect = pygame.Rect(text_x - padding, text_y - padding, 
                                text_surface.get_width() + 2 * padding, 
                                text_surface.get_height() + 2 * padding)
            pygame.draw.rect(self.screen, (0, 0, 0), bg_rect)
            pygame.draw.rect(self.screen, (255, 255, 255), bg_rect, 2)
            
            # Draw the text
            self.screen.blit(text_surface, (text_x, text_y))
    
    def draw_cluster_glow_effects(self):
        """Draw glow effects for all active clusters."""
        if not self.cluster_glow_effects:
            return
            
        current_time = time.time()
        
        # Calculate grid offset
        start_x = self.current_x_offset
        start_y = self.current_y_offset
        
        for cluster_id, glow_data in self.cluster_glow_effects.items():
            cluster_blocks = glow_data['blocks']
            base_color = glow_data['color']
            start_time = glow_data['start_time']
            base_intensity = glow_data['intensity']
            
            # Calculate pulsing intensity using sine wave
            elapsed = current_time - start_time
            pulse_phase = elapsed * self.cluster_glow_pulse_speed
            pulse_intensity = (math.sin(pulse_phase) + 1) / 2  # Normalize to 0-1
            
            # Combine base intensity with pulse
            current_intensity = base_intensity * (0.5 + 0.5 * pulse_intensity)
            
            # Calculate glow color with current intensity
            if isinstance(base_color, tuple) and len(base_color) == 3:
                r, g, b = base_color
            else:
                r, g, b = (255, 255, 255)  # Default to white if color parsing fails
            
            # Create brighter glow color
            glow_r = min(255, int(r * (1 + current_intensity)))
            glow_g = min(255, int(g * (1 + current_intensity)))
            glow_b = min(255, int(b * (1 + current_intensity)))
            glow_color = (glow_r, glow_g, glow_b)
            
            # Draw glow effect for each block in the cluster
            for block_x, block_y in cluster_blocks:
                # Calculate screen position
                screen_x = start_x + block_x * self.block_width
                screen_y = start_y + block_y * self.block_height
                
                # Draw multiple glow layers for better effect
                glow_sizes = [8, 12, 16]  # Different glow radii
                glow_alphas = [80, 50, 30]  # Different alpha values
                
                for glow_size, alpha in zip(glow_sizes, glow_alphas):
                    # Create glow surface with alpha
                    glow_surface = pygame.Surface((self.block_width + glow_size * 2, 
                                                 self.block_height + glow_size * 2), 
                                                pygame.SRCALPHA)
                    
                    # Calculate glow alpha based on intensity
                    current_alpha = int(alpha * current_intensity)
                    
                    # Draw glow rectangle
                    glow_rect = pygame.Rect(glow_size, glow_size, self.block_width, self.block_height)
                    pygame.draw.rect(glow_surface, (*glow_color, current_alpha), glow_rect)
                    
                    # Draw glow border
                    for i in range(glow_size):
                        border_alpha = max(0, current_alpha - i * 10)
                        border_rect = pygame.Rect(glow_size - i, glow_size - i, 
                                                self.block_width + i * 2, self.block_height + i * 2)
                        pygame.draw.rect(glow_surface, (*glow_color, border_alpha), border_rect, 1)
                    
                    # Blit glow surface to screen
                    self.screen.blit(glow_surface, (screen_x - glow_size, screen_y - glow_size))