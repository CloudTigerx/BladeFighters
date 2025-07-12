import pygame
import sys
import os
import time
import math
import random
import traceback

# Define GarbageBlockState since attack_system is not available
class GarbageBlockState:
    """Placeholder for GarbageBlockState when attack_system is not available."""
    pass

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
    def __init__(self, puzzle_engine):
        print(f"[DEBUG] PuzzleRenderer initialized for engine: {puzzle_engine}")
        self.engine = puzzle_engine
        self.screen = puzzle_engine.screen
        print(f"[DEBUG] Renderer screen size: {self.screen.get_width()}x{self.screen.get_height()}")
        
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
        
        # Load explosion sprite for blue pieces
        try:
            self.blue_explosion_sprite = pygame.image.load("puzzleassets/blue_explode.png").convert_alpha()
            # Get sprite dimensions
            sprite_width = self.blue_explosion_sprite.get_width()
            sprite_height = self.blue_explosion_sprite.get_height()
            # Assuming frames are arranged horizontally, calculate frame width
            self.explosion_frame_width = sprite_width // 8  # Assuming 8 frames
            self.explosion_frame_height = sprite_height
            # Create list of frame surfaces
            self.explosion_frames = []
            for i in range(8):  # Assuming 8 frames
                frame = pygame.Surface((self.explosion_frame_width, self.explosion_frame_height), pygame.SRCALPHA)
                frame.blit(self.blue_explosion_sprite, (0, 0), 
                         (i * self.explosion_frame_width, 0, self.explosion_frame_width, self.explosion_frame_height))
                self.explosion_frames.append(frame)
            
            # Load yellow explosion sprite sheet
            self.yellow_explosion_sprite = pygame.image.load("puzzleassets/sprite_sheet_orange_cleaned.png").convert_alpha()
            # Get sprite dimensions
            yellow_sprite_width = self.yellow_explosion_sprite.get_width()
            yellow_sprite_height = self.yellow_explosion_sprite.get_height()
            # Assuming frames are arranged horizontally, calculate frame width
            self.yellow_explosion_frame_width = yellow_sprite_width // 8  # Assuming 8 frames
            self.yellow_explosion_frame_height = yellow_sprite_height
            # Create list of frame surfaces
            self.yellow_explosion_frames = []
            for i in range(8):  # Assuming 8 frames
                frame = pygame.Surface((self.yellow_explosion_frame_width, self.yellow_explosion_frame_height), pygame.SRCALPHA)
                frame.blit(self.yellow_explosion_sprite, (0, 0), 
                         (i * self.yellow_explosion_frame_width, 0, self.yellow_explosion_frame_width, self.yellow_explosion_frame_height))
                self.yellow_explosion_frames.append(frame)
            
            # Load red explosion sprite sheet
            self.red_explosion_sprite = pygame.image.load("puzzleassets/sprite_sheet_yellow.png").convert_alpha()
            # Get sprite dimensions
            red_sprite_width = self.red_explosion_sprite.get_width()
            red_sprite_height = self.red_explosion_sprite.get_height()
            # Assuming frames are arranged horizontally, calculate frame width
            self.red_explosion_frame_width = red_sprite_width // 8  # Assuming 8 frames
            self.red_explosion_frame_height = red_sprite_height
            # Create list of frame surfaces
            self.red_explosion_frames = []
            for i in range(8):  # Assuming 8 frames
                frame = pygame.Surface((self.red_explosion_frame_width, self.red_explosion_frame_height), pygame.SRCALPHA)
                frame.blit(self.red_explosion_sprite, (0, 0), 
                         (i * self.red_explosion_frame_width, 0, self.red_explosion_frame_width, self.red_explosion_frame_height))
                self.red_explosion_frames.append(frame)
            
            # Load green explosion sprite sheet
            self.green_explosion_sprite = pygame.image.load("puzzleassets/sprite_sheet_blue.png").convert_alpha()
            # Get sprite dimensions
            green_sprite_width = self.green_explosion_sprite.get_width()
            green_sprite_height = self.green_explosion_sprite.get_height()
            # Assuming frames are arranged horizontally, calculate frame width
            self.green_explosion_frame_width = green_sprite_width // 8  # Assuming 8 frames
            self.green_explosion_frame_height = green_sprite_height
            # Create list of frame surfaces
            self.green_explosion_frames = []
            for i in range(8):  # Assuming 8 frames
                frame = pygame.Surface((self.green_explosion_frame_width, self.green_explosion_frame_height), pygame.SRCALPHA)
                frame.blit(self.green_explosion_sprite, (0, 0), 
                         (i * self.green_explosion_frame_width, 0, self.green_explosion_frame_width, self.green_explosion_frame_height))
                self.green_explosion_frames.append(frame)
            
            # Explosion animation settings
            self.explosion_duration = 0.3  # How long the explosion lasts (in seconds)
            self.explosion_repeat_frames = 2  # How many times to repeat the first few frames
            self.explosion_initial_frames = 3  # How many frames to repeat at the start
            self.explosion_scale_start = 0.5  # Starting scale (0.5 = half size)
            self.explosion_scale_end = 1.2    # Ending scale (1.2 = 20% larger than block)
        except:
            print("Warning: Could not load explosion sprites")
            self.explosion_frames = None
            self.yellow_explosion_frames = None
            self.red_explosion_frames = None
            self.green_explosion_frames = None
        
        # Calculate grid position to center it on screen
        grid_width_pixels = self.engine.grid_width * self.block_width
        grid_height_pixels = self.engine.grid_height * self.block_height
        self.current_x_offset = (self.screen.get_width() - grid_width_pixels) // 2
        self.current_y_offset = (self.screen.get_height() - grid_height_pixels) // 2
        
        # Ensure we can access the attack system through the engine
        if not hasattr(self.engine, 'attack_system'):
            print("DEBUG: No attack system found during renderer initialization")
            self.engine.attack_system = None
        else:
            print(f"DEBUG: Attack system found during renderer initialization with transformation time {self.engine.attack_system.transformation_time}s")
        
        # Optimized animation settings - reduced from 120 to 60 fps
        self.enable_animation = True
        self.animation_frame_rate = 240  # Reduced from 120 to 60 for better performance
        self.animation_timer = 0
        self.animation_frame_duration = 1.0 / self.animation_frame_rate
        self.animation_update_counter = 0  # Counter to skip frames
        self.animation_update_frequency = 1  # Only update animations every 2 frames
        
        # Combo text display settings
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
        
        # Visual state for smooth falling animation
        self.visual_piece_position = [0, 0]
        self.visual_attached_position = 0
        self.is_animating = False
        self.target_position = [0, 0]
        self.anim_start_time = 0
        self.anim_duration = 0.035  # Faster animation (35ms) for more responsive feel while still smooth
        
        # Smooth breaking animation tracking
        self.breaking_blocks_animations = {}  # Format: {(x, y): {start_time, progress, total_duration}}
        self.breaking_animation_duration = 0.3  # 300ms for breaking animation
        
        # Visual-only falling blocks tracking (won't affect game mechanics)
        self.visual_falling_blocks = {}  # Format: {(x, y): {start_y, target_y, progress, start_time}}
        # Set fall speed to achieve 1.1 seconds from top to bottom of grid (13 rows)
        # For a single row drop, we need 1.1/13 = ~0.0846 seconds
        self.fall_animation_duration = 0.085  # 85ms per row of fall
        
        # Keep empty particles list for possible future use
        self.cluster_glow_particles = []  # Remove this line
        
        # Particle cache for better performance
        self.particle_surfaces = {}
        
        # Enhanced particle settings for breaking animations
        self.particle_count_per_block = 20  # Increased from 8 to 20 for more particles
        self.particle_max_speed = 4.0  # Increased from 2.0 to 4.0 for faster particles
        self.particle_min_speed = 1.0  # Increased from 0.5 to 1.0 for faster minimum speed
        self.particle_max_size = 5  # Increased from 3 to 5 for larger particles
        self.particle_min_size = 2  # Increased from 1 to 2 for larger minimum size
        self.particle_lifespan = 0.8  # Increased from 0.5 to 0.8 for longer-lasting particles
        
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
        
        # Animation buffer setup
        self.current_animation_buffer = {}
        self.next_animation_buffer = {}
        self.buffer_swap_time = time.time()
        self.buffer_swap_interval = 1.0 / 240.0  # 240Hz update rate
        
        # Fixed timestep for logic updates
        self.fixed_timestep = 1.0 / 240.0  # 240Hz logic updates
        self.accumulator = 0.0
        self.last_frame_time = time.time()
        
        # Initialize piece visuals
        self.update_visual_state()
        
        # At the beginning of the main game loop
        pygame.display.set_mode((self.engine.width, self.engine.height), pygame.HWSURFACE | pygame.DOUBLEBUF)
        
        # Or manually implement frame limiting
        self.clock = pygame.time.Clock()
        
        # Game over animation properties
        self.game_over_start_time = None
        self.game_over_duration = 2.0  # Duration of the fade in animation
        self.game_over_particles = []
        self.game_over_font = None
        self.game_over_font_size = 72
        self.game_over_text_color = (255, 50, 50)  # Red color for game over
        self.game_over_glow_color = (255, 100, 100, 180)  # Glow effect color
    
    def update_visual_state(self):
        """Update the visual state to match the current game state."""
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
            
        # Get the visual position with micro-movement interpolation
        if self.engine.main_piece:
            # Get pixel-perfect position from the engine
            self.visual_piece_position = self.engine.get_visual_position()
            self.visual_attached_position = self.engine.attached_position
            
            # Clear all animations in columns where the active piece is
            if hasattr(self, 'visual_falling_blocks'):
                main_x = int(self.visual_piece_position[0])
                attached_x = -1  # Initialize to an invalid value
                
                # Determine attached piece x-coordinate
                if self.visual_attached_position == 1:  # Right
                    attached_x = main_x + 1
                elif self.visual_attached_position == 3:  # Left
                    attached_x = main_x - 1
                else:
                    attached_x = main_x  # Same column (top or bottom)
                
                # Remove any animations in the same columns as active piece
                to_remove = []
                for pos in self.visual_falling_blocks:
                    if pos[0] == main_x or pos[0] == attached_x:
                        to_remove.append(pos)
                        
                for pos in to_remove:
                    self.visual_falling_blocks.pop(pos, None)
        
        # Reset animation state if no active piece - prevents animations without active piece
        if not self.engine.main_piece and not self.engine.chain_reaction_in_progress:
            # Only clear animations if there's no chain reaction in progress
            # This allows animations to complete properly
            if hasattr(self, 'visual_falling_blocks') and not self.animations_in_progress():
                self.visual_falling_blocks.clear()
            if hasattr(self, 'breaking_blocks_animations'):
                self.breaking_blocks_animations.clear()
        
        # Check for new clusters and create animations
        current_time = time.time()
        
        # Get current clusters
        current_clusters = []
        if hasattr(self.engine, 'find_all_clusters'):
            current_clusters = self.engine.find_all_clusters()
        
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
        
        # Update cluster animations
        for cluster_id in list(self.cluster_animations.keys()):
            anim_data = self.cluster_animations[cluster_id]
            elapsed = current_time - anim_data['start_time']
            
            # Remove completed animations
            if elapsed > anim_data['duration']:
                self.cluster_animations.pop(cluster_id, None)
        
        # Store current clusters for next frame comparison
        self.previous_clusters = current_clusters
        
        # ENABLE BREAKING ANIMATIONS AND ENHANCE THEM
        current_time = time.time()
        
        # Clear any expired breaking animations
        if hasattr(self, 'breaking_blocks_animations'):
            for pos, data in list(self.breaking_blocks_animations.items()):
                if 'start_time' in data and 'total_duration' in data:
                    if current_time - data['start_time'] > data['total_duration'] * 1.2:
                        self.breaking_blocks_animations.pop(pos, None)
            
        # Add new breaking animations
        if hasattr(self.engine, 'breaking_blocks'):
            for x, y, start_time, delay, block_color, is_breaker in self.engine.breaking_blocks:
                pos_key = (x, y)
                # Skip if we already have an animation for this position
                if pos_key in self.breaking_blocks_animations:
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
                    self.breaking_blocks_animations[pos_key] = {
                        'start_time': current_time,
                        'progress': 0.0,
                        'total_duration': self.breaking_animation_duration,
                        'block_type': block_type
                    }
                    
                    # Add particles if possible
                    if hasattr(self, 'create_dust_particles'):
                        # Make sure position is valid before creating particles
                        if isinstance(x, (int, float)) and isinstance(y, (int, float)):
                            try:
                                self.breaking_blocks_animations[pos_key]['particles'] = self.create_dust_particles(x, y, block_color)
                            except Exception as e:
                                print(f"Error creating dust particles: {e}")
                                self.breaking_blocks_animations[pos_key]['particles'] = []
                        else:
                            # Empty particles list if coordinates aren't valid
                            self.breaking_blocks_animations[pos_key]['particles'] = []
                except Exception as e:
                    print(f"Error creating breaking animation: {e}")
        
        # Get current clusters from the engine to avoid animating supported clusters
        supported_cluster_positions = set()
        if hasattr(self.engine, 'find_all_clusters'):
            clusters = self.engine.find_all_clusters()
            
            # Now identify which columns in each cluster have support
            for cluster in clusters:
                # Group blocks by column
                columns = {}
                for x, y in cluster:
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
                        if (below_pos not in cluster and 
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
        
        # Track current grid state to detect blocks that have been moved by gravity
        # This is a simple approach that only looks at the previous and current frame
        if hasattr(self, 'previous_grid_state'):
            # Compare previous grid with current grid to detect falling blocks
            for y in range(self.engine.grid_height - 1):  # Skip bottom row
                for x in range(self.engine.grid_width):
                    # If this cell was empty and now has a block, check if it fell from above
                    if (self.previous_grid_state[y][x] is None and 
                        self.engine.puzzle_grid[y+1][x] is not None):
                        
                        # Look for the same block type above in the previous state
                        for prev_y in range(y, -1, -1):
                            if (self.previous_grid_state[prev_y][x] == self.engine.puzzle_grid[y+1][x]):
                                # Found the block that fell - add to visual falling blocks
                                pos_key = (x, y+1)
                                
                                # Skip if animation already exists for this position to prevent flickering
                                if pos_key in self.visual_falling_blocks and self.visual_falling_blocks[pos_key]['progress'] < 0.9:
                                    continue
                                
                                # Don't add animation if this column has recently broken blocks
                                # This prevents the issue with clusters visually moving when they shouldn't
                                should_add_animation = True
                                for check_y in range(y+1, self.engine.grid_height):
                                    if (x, check_y) in self.recently_broken_positions:
                                        should_add_animation = False
                                        break
                                
                                # Skip animation if this position is in a supported cluster
                                if pos_key in supported_cluster_positions:
                                    should_add_animation = False
                                
                                if should_add_animation:
                                    # Calculate duration based on fall distance
                                    fall_distance = y + 1 - prev_y
                                    
                                    # Calculate duration based on fall distance to maintain consistent speed
                                    # For a 13-row grid with 1.1 seconds total fall time, each row should take ~0.085 seconds
                                    duration = fall_distance * 0.085  # 85ms per row of fall
                                    
                                    self.visual_falling_blocks[pos_key] = {
                                        'start_y': prev_y,
                                        'target_y': y+1,
                                        'progress': 0.0,
                                        'start_time': current_time,
                                        'block_type': self.engine.puzzle_grid[y+1][x],
                                        'duration': duration  # Store the calculated duration
                                    }
                                break
                    
                    # Check for clusters that moved together, but don't animate clusters that should stay still
                    # Only animate if the grid positions actually changed logically, not just visually
                    elif (self.engine.puzzle_grid[y][x] is not None and
                          y > 0 and self.previous_grid_state[y-1][x] == self.engine.puzzle_grid[y][x] and
                          self.previous_grid_state[y][x] is None):
                        
                        # This appears to be a block that moved down as part of a cluster
                        # Check if this is due to a breaking block beneath the cluster
                        is_from_breaking = False
                        
                        # Check current breaking blocks
                        for bx, by, _, _, _, _ in self.engine.breaking_blocks:
                            # If there was a breaking block in this column below current position
                            if bx == x and by > y:
                                is_from_breaking = True
                                break
                        
                        # Also check recently broken positions anywhere below this position
                        for check_y in range(y+1, self.engine.grid_height):
                            if (x, check_y) in self.recently_broken_positions:
                                is_from_breaking = True
                                break
                        
                        # Skip animation if this position is in a supported cluster
                        is_in_supported_cluster = (x, y) in supported_cluster_positions
                        
                        # Only animate if it's not due to a breaking block beneath
                        # AND it's not part of a supported cluster
                        pos_key = (x, y)
                        
                        # Skip if animation already exists for this position to prevent flickering
                        if pos_key in self.visual_falling_blocks and self.visual_falling_blocks[pos_key]['progress'] < 0.9:
                            continue
                            
                        if not is_from_breaking and not is_in_supported_cluster:
                            self.visual_falling_blocks[pos_key] = {
                                'start_y': y-1,
                                'target_y': y,
                                'progress': 0.0,
                                'start_time': current_time,
                                'block_type': self.engine.puzzle_grid[y][x],
                                'duration': 0.085  # 85ms per row of fall - consistent with other animations
                            }
        
        # Store current grid state for next frame comparison
        self.previous_grid_state = []
        for y in range(self.engine.grid_height):
            row = []
            for x in range(self.engine.grid_width):
                row.append(self.engine.puzzle_grid[y][x])
            self.previous_grid_state.append(row)
        
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
                        if current_pos in self.visual_falling_blocks:
                            self.visual_falling_blocks.pop(current_pos, None)
    
    def update_animations(self):
        """Update all animations for the puzzle grid."""
        current_time = time.time()
        
        # Update dust particles
        self.update_dust_particles(current_time)
        
        # Update combo text animations
        self.update_combo_texts(current_time)
        
        # Update breaking block animations
        self.update_breaking_animations(current_time)
        
        # Update cluster effects
        self.update_cluster_effects(current_time)
        
        # Update strike effects if any are active
        self.update_strike_effects(current_time)
        
        # Limit total particles
        self._limit_particle_count()
    
    def update_dust_particles(self, current_time):
        """Update and render any active dust particles."""
        # Skip if we don't have dust particles
        if not hasattr(self, 'dust_particles'):
            self.dust_particles = {}
            return
            
        # Process each dust particle
        for pos, particle in list(self.dust_particles.items()):
            # Calculate elapsed time
            elapsed = current_time - particle['start_time']
            
            # Check if the particle has expired
            if elapsed >= particle['duration']:
                # Remove expired particle
                self.dust_particles.pop(pos)
                continue
                
            # Update position based on elapsed time
            particle['x'] += particle['vx'] * elapsed
            particle['y'] += particle['vy'] * elapsed
            
            # Update size based on elapsed time
            particle['size'] = max(0.1, particle['size'] - particle['decay'] * elapsed)
            
            # Update color based on elapsed time - use existing color
            # Color is already set when particle is created, no need to update
            
            # Render the particle
            self.render_dust_particle(pos, particle)
    
    def render_dust_particle(self, pos, particle):
        """Render a single dust particle."""
        size = int(particle['size'])
        color = particle['color']
        # Safety check: ensure color is a valid RGB tuple
        if not color or not isinstance(color, (tuple, list)) or len(color) < 3:
            color = (255, 255, 255)  # Fallback to white
        try:
            pygame.draw.circle(self.screen, color, (int(pos[0]), int(pos[1])), size)
        except Exception as e:
            print(f"[DEBUG] Error in render_dust_particle: color={color}, size={size}, pos={pos}, error={e}")
            traceback.print_exc()
    
    def update_combo_texts(self, current_time):
        """Update and render any active combo text animations."""
        # Skip if we don't have combo texts
        if not hasattr(self, 'combo_texts'):
            self.combo_texts = []
            return
            
        # Process each combo text
        for combo_text in self.combo_texts:
            # Calculate elapsed time
            elapsed = current_time - combo_text['start_time']
            
            # Check if the combo text has expired
            if elapsed >= combo_text['duration']:
                # Remove expired combo text
                self.combo_texts.remove(combo_text)
                continue
                
            # Update progress
            combo_text['progress'] = min(1.0, elapsed / combo_text['duration'])
            
            # Update particle positions if particles exist
            if 'particles' in combo_text:
                # Check if this combo has rainbow mode enabled
                combo_has_rainbow = combo_text.get('rainbow_mode', False)
                
                for particle in combo_text['particles'][:]:
                    # Skip dead particles
                    if particle['life'] <= 0:
                        continue
                        
                    # Update position with combo size scaling
                    combo_scale = 1 + (combo_text['combo_size'] - 2) * 0.1
                    particle['x'] += combo_scale * particle['vx'] * elapsed
                    particle['y'] += combo_scale * particle['vy'] * elapsed
                    
                    # Update size based on elapsed time
                    particle['size'] = max(0.1, particle['size'] - 0.5 * elapsed)
                    
                    # Update life
                    particle['life'] -= elapsed
                    
                    # Update alpha based on remaining life
                    life_ratio = max(0, particle['life'] / particle.get('max_life', 1.0))
                    particle['alpha'] = int(255 * life_ratio)
                    
                    # Update color based on combo size
                    # Color is already set when particle is created, no need to update
                    
                    # Draw rainbow trail if enabled for this specific particle
                    if combo_has_rainbow and particle.get('rainbow', False) and 'trail' in particle and particle['trail']:
                        # Draw trail segments from oldest to newest
                        for i, pos in enumerate(reversed(particle['trail'])):
                            # Get rainbow color based on position in trail
                            color_idx = (i + int(current_time * 7)) % len(self.rainbow_colors)
                            rainbow_color = self.rainbow_colors[color_idx]
                            
                            # Calculate trail segment size (smaller for older segments)
                            segment_size = max(1, int(particle['size'] * (1.0 - (i / len(particle['trail'])))))
                            
                            # Calculate trail alpha (more transparent for older segments)
                            trail_alpha = int(particle['alpha'] * (self.rainbow_trail_fade ** i))
                            
                            if segment_size <= 0 or trail_alpha <= 0:
                                continue
                                
                            # Create trail segment surface
                            trail_key = f"trail_{rainbow_color[0]}_{rainbow_color[1]}_{rainbow_color[2]}_{segment_size}_{trail_alpha}"
                            
                            if trail_key not in self.particle_surfaces:
                                trail_surf = pygame.Surface((segment_size*2, segment_size*2), pygame.SRCALPHA)
                                pygame.draw.circle(trail_surf, (*rainbow_color, trail_alpha),
                                                (segment_size, segment_size), segment_size)
                                self.particle_surfaces[trail_key] = trail_surf
                            
                            # Draw the trail segment
                            segment_x = int(pos['x'] - segment_size)
                            segment_y = int(pos['y'] - segment_size)
                            
                            # Apply screen shake to trail too
                            if self.screen_shake:
                                segment_x += self.shake_offset_x
                                segment_y += self.shake_offset_y
                                
                            self.screen.blit(self.particle_surfaces[trail_key], (segment_x, segment_y))
                    
                    # Draw particle
                    particle_size = int(particle['size'])  # Remove scale factor from particle size
                    if particle_size <= 0:
                        continue
                        
                    # Create key for particle surface cache
                    color = particle['color']
                    particle_key = f"combo_{color[0]}_{color[1]}_{color[2]}_{particle_size}_{particle['alpha']}"
                    
                    # Use cached surface or create new one
                    if particle_key not in self.particle_surfaces:
                        particle_surf = pygame.Surface((particle_size*2, particle_size*2), pygame.SRCALPHA)
                        # Ensure color is RGB (3-tuple) before adding alpha
                        rgb_color = color[:3] if len(color) >= 3 else color
                        alpha = max(0, min(255, particle['alpha']))
                        try:
                            pygame.draw.circle(particle_surf, (*rgb_color, alpha), 
                                            (particle_size, particle_size), particle_size)
                        except Exception as e:
                            print(f"[DEBUG] Error in update_combo_texts particle: color={color}, rgb_color={rgb_color}, alpha={alpha}, error={e}")
                            traceback.print_exc()
                        self.particle_surfaces[particle_key] = particle_surf
                    
                    # Draw the particle
                    particle_x = int(particle['x'] - particle_size)
                    particle_y = int(particle['y'] - particle_size)
                    
                    # Apply screen shake to particles too for consistent effect
                    if self.screen_shake:
                        particle_x += self.shake_offset_x
                        particle_y += self.shake_offset_y
                        
                    self.screen.blit(self.particle_surfaces[particle_key], (particle_x, particle_y))
    
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
                    screen_y = self.engine.grid_y_offset + (particle['y'] * self.block_height)
                    if screen_y > self.engine.height + 100:  # Remove when well off screen
                        block_data['particles'].remove(particle)
            
            # Call render_breaking_block directly without assigning its return value
            self.render_breaking_block(pos, block_data)
    
    def render_breaking_block(self, pos, block_data):
        """Render a single breaking block animation."""
        # Initialize update_regions to track areas that need updating
        temp_update_regions = []
        
        x, y = pos
        block_type = block_data['block_type']
        progress = block_data['progress']
        
        # Calculate position
        block_x = self.current_x_offset + (x * self.block_width)
        block_y = self.current_y_offset + (y * self.block_height)
        
        # Draw the appropriate block type
        self._draw_block(block_type, block_x, block_y, self.block_width, self.block_height)
        
        # Draw particles - optimize with batch rendering
        if 'particles' in block_data:
            # Only draw if we have particles and they're on screen
            if block_data['particles'] and 0 <= block_x <= self.engine.width and 0 <= block_y <= self.engine.height:
                # Batch particles by size and color to minimize surface creation and blits
                particle_batches = {}
                
                for particle in block_data['particles']:
                    # Calculate alpha based on remaining life
                    alpha = int(255 * (particle['life'] / particle['max_life']))
                    
                    # Calculate screen position
                    px = self.current_x_offset + (x * self.block_width) + (particle['x'] * self.block_width)
                    py = self.current_y_offset + (y * self.block_height) + (particle['y'] * self.block_height)
                    
                    # Skip particles that are off-screen
                    if px < -10 or px > self.engine.width + 10 or py < -10 or py > self.engine.height + 10:
                        continue
                    
                    # Create key for particle surface cache
                    color = particle['color']
                    glow_color = particle.get('glow_color', color)
                    particle_key = f"spark_{color[0]}_{color[1]}_{color[2]}_{glow_color[0]}_{glow_color[1]}_{glow_color[2]}_{int(particle['length'])}_{int(particle['width'])}_{alpha}"
                    
                    # Group particles by surface key
                    if particle_key not in particle_batches:
                        particle_batches[particle_key] = []
                    
                    # Calculate rotation
                    rotation = particle.get('rotation', 0)
                    rotation_speed = particle.get('rotation_speed', 0)
                    particle['rotation'] = (rotation + rotation_speed * 0.016) % 360
                    
                    # Store position and rotation to batch render later
                    particle_batches[particle_key].append((
                        int(px - particle['length']/2), 
                        int(py - particle['width']/2),
                        particle['rotation']
                    ))
                
                # Now render each batch with minimal surface creation
                for particle_key, positions in particle_batches.items():
                    # Use cached surface or create new one
                    if particle_key not in self.particle_surfaces:
                        # Parse key back to components
                        key_parts = particle_key.split('_')
                        r, g, b = int(key_parts[1]), int(key_parts[2]), int(key_parts[3])
                        gr, gg, gb = int(key_parts[4]), int(key_parts[5]), int(key_parts[6])
                        length = int(key_parts[7])
                        width = int(key_parts[8])
                        alpha = int(key_parts[9])
                        
                        # Create surface with extra size for glow
                        glow_size = max(length, width) * 2
                        particle_surf = pygame.Surface((glow_size*2, glow_size*2), pygame.SRCALPHA)
                        
                        # Draw sharp spark shape
                        # Draw outer glow
                        for i in range(3):
                            glow_alpha = int(alpha * 0.3 * (1 - i/3))
                            glow_radius = max(length, width) + i*2
                            # Draw elongated glow
                            try:
                                pygame.draw.ellipse(particle_surf, (gr, gg, gb, glow_alpha), 
                                                  (glow_size - length, glow_size - width, length*2, width*2))
                            except Exception as e:
                                print(f"[DEBUG] Error in spark glow: gr={gr}, gg={gg}, gb={gb}, glow_alpha={glow_alpha}, error={e}")
                                traceback.print_exc()
                        
                        # Draw main spark with sharp edges
                        # Draw the main spark body
                        try:
                            pygame.draw.ellipse(particle_surf, (r, g, b, alpha), 
                                              (glow_size - length, glow_size - width, length*2, width*2))
                        except Exception as e:
                            print(f"[DEBUG] Error in spark body: r={r}, g={g}, b={b}, alpha={alpha}, error={e}")
                            traceback.print_exc()
                        
                        # Add sharp tips to the spark
                        tip_length = length // 2
                        tip_width = width // 2
                        # Left tip
                        try:
                            pygame.draw.ellipse(particle_surf, (r, g, b, alpha),
                                              (glow_size - length - tip_length, glow_size - tip_width,
                                               tip_length*2, tip_width*2))
                        except Exception as e:
                            print(f"[DEBUG] Error in spark left tip: r={r}, g={g}, b={b}, alpha={alpha}, error={e}")
                            traceback.print_exc()
                        # Right tip
                        try:
                            pygame.draw.ellipse(particle_surf, (r, g, b, alpha),
                                              (glow_size + length - tip_length, glow_size - tip_width,
                                               tip_length*2, tip_width*2))
                        except Exception as e:
                            print(f"[DEBUG] Error in spark right tip: r={r}, g={g}, b={b}, alpha={alpha}, error={e}")
                            traceback.print_exc()
                        
                        self.particle_surfaces[particle_key] = particle_surf
                    
                    # Get cached surface
                    surf = self.particle_surfaces[particle_key]
                    
                    # Parse key to get length and width for positioning
                    key_parts = particle_key.split('_')
                    length = int(key_parts[7])
                    width = int(key_parts[8])
                    
                    # Batch blit all particles with this surface
                    for pos_x, pos_y, rotation in positions:
                        # Create a rotated copy of the surface
                        rotated_surf = pygame.transform.rotate(surf, rotation)
                        # Get the rect for centering
                        rect = rotated_surf.get_rect(center=(pos_x + length, pos_y + width))
                        # Draw the rotated particle
                        self.screen.blit(rotated_surf, rect)
        
        # Draw explosion sprite for blue pieces if available (moved after particles)
        if 'blue' in block_type and self.explosion_frames is not None and progress < 0.5:
            # Calculate which frame to show based on progress
            frame_count = len(self.explosion_frames)
            
            # Calculate normalized progress within the explosion duration
            explosion_progress = progress / 0.5  # Convert to 0-1 range
            
            # Calculate frame index with repetition for initial frames
            if explosion_progress < 0.3:  # First 30% of animation
                # Repeat the first few frames
                frame_index = (int(explosion_progress * self.explosion_repeat_frames * self.explosion_initial_frames)) % self.explosion_initial_frames
            else:
                # Play remaining frames normally
                remaining_frames = frame_count - self.explosion_initial_frames
                frame_progress = (explosion_progress - 0.3) / 0.7  # Normalize remaining progress
                frame_index = self.explosion_initial_frames + int(frame_progress * remaining_frames)
            
            # Get the current frame
            current_frame = self.explosion_frames[frame_index]
            
            # Calculate scale based on progress
            scale_progress = min(1.0, explosion_progress * 2)  # Scale up faster
            current_scale = self.explosion_scale_start + (self.explosion_scale_end - self.explosion_scale_start) * scale_progress
            
            # Scale frame to match block size
            scaled_width = int(self.block_width * current_scale)
            scaled_height = int(self.block_height * current_scale)
            scaled_frame = pygame.transform.scale(current_frame, (scaled_width, scaled_height))
            
            # Center the explosion on the block
            explosion_x = block_x + (self.block_width - scaled_width) // 2
            explosion_y = block_y + (self.block_height - scaled_height) // 2
            
            # Draw the explosion frame
            self.screen.blit(scaled_frame, (explosion_x, explosion_y))
        # Draw explosion sprite for yellow pieces if available
        elif 'yellow' in block_type and self.yellow_explosion_frames is not None and progress < 0.5:
            # Calculate which frame to show based on progress
            frame_count = len(self.yellow_explosion_frames)
            
            # Calculate normalized progress within the explosion duration
            explosion_progress = progress / 0.5  # Convert to 0-1 range
            
            # Calculate frame index with repetition for initial frames
            if explosion_progress < 0.3:  # First 30% of animation
                # Repeat the first few frames
                frame_index = (int(explosion_progress * self.explosion_repeat_frames * self.explosion_initial_frames)) % self.explosion_initial_frames
            else:
                # Play remaining frames normally
                remaining_frames = frame_count - self.explosion_initial_frames
                frame_progress = (explosion_progress - 0.3) / 0.7  # Normalize remaining progress
                frame_index = self.explosion_initial_frames + int(frame_progress * remaining_frames)
            
            # Get the current frame
            current_frame = self.yellow_explosion_frames[frame_index]
            
            # Calculate scale based on progress
            scale_progress = min(1.0, explosion_progress * 2)  # Scale up faster
            current_scale = self.explosion_scale_start + (self.explosion_scale_end - self.explosion_scale_start) * scale_progress
            
            # Scale frame to match block size
            scaled_width = int(self.block_width * current_scale)
            scaled_height = int(self.block_height * current_scale)
            scaled_frame = pygame.transform.scale(current_frame, (scaled_width, scaled_height))
            
            # Center the explosion on the block
            explosion_x = block_x + (self.block_width - scaled_width) // 2
            explosion_y = block_y + (self.block_height - scaled_height) // 2
            
            # Draw the explosion frame
            self.screen.blit(scaled_frame, (explosion_x, explosion_y))
        # Draw explosion sprite for red pieces if available
        elif 'red' in block_type and self.red_explosion_frames is not None and progress < 0.5:
            # Calculate which frame to show based on progress
            frame_count = len(self.red_explosion_frames)
            
            # Calculate normalized progress within the explosion duration
            explosion_progress = progress / 0.5  # Convert to 0-1 range
            
            # Calculate frame index with repetition for initial frames
            if explosion_progress < 0.3:  # First 30% of animation
                # Repeat the first few frames
                frame_index = (int(explosion_progress * self.explosion_repeat_frames * self.explosion_initial_frames)) % self.explosion_initial_frames
            else:
                # Play remaining frames normally
                remaining_frames = frame_count - self.explosion_initial_frames
                frame_progress = (explosion_progress - 0.3) / 0.7  # Normalize remaining progress
                frame_index = self.explosion_initial_frames + int(frame_progress * remaining_frames)
            
            # Get the current frame
            current_frame = self.red_explosion_frames[frame_index]
            
            # Calculate scale based on progress
            scale_progress = min(1.0, explosion_progress * 2)  # Scale up faster
            current_scale = self.explosion_scale_start + (self.explosion_scale_end - self.explosion_scale_start) * scale_progress
            
            # Scale frame to match block size
            scaled_width = int(self.block_width * current_scale)
            scaled_height = int(self.block_height * current_scale)
            scaled_frame = pygame.transform.scale(current_frame, (scaled_width, scaled_height))
            
            # Center the explosion on the block
            explosion_x = block_x + (self.block_width - scaled_width) // 2
            explosion_y = block_y + (self.block_height - scaled_height) // 2
            
            # Draw the explosion frame
            self.screen.blit(scaled_frame, (explosion_x, explosion_y))
        # Draw explosion sprite for green pieces if available
        elif 'green' in block_type and self.green_explosion_frames is not None and progress < 0.5:
            # Calculate which frame to show based on progress
            frame_count = len(self.green_explosion_frames)
            
            # Calculate normalized progress within the explosion duration
            explosion_progress = progress / 0.5  # Convert to 0-1 range
            
            # Calculate frame index with repetition for initial frames
            if explosion_progress < 0.3:  # First 30% of animation
                # Repeat the first few frames
                frame_index = (int(explosion_progress * self.explosion_repeat_frames * self.explosion_initial_frames)) % self.explosion_initial_frames
            else:
                # Play remaining frames normally
                remaining_frames = frame_count - self.explosion_initial_frames
                frame_progress = (explosion_progress - 0.3) / 0.7  # Normalize remaining progress
                frame_index = self.explosion_initial_frames + int(frame_progress * remaining_frames)
            
            # Get the current frame
            current_frame = self.green_explosion_frames[frame_index]
            
            # Calculate scale based on progress
            scale_progress = min(1.0, explosion_progress * 2)  # Scale up faster
            current_scale = self.explosion_scale_start + (self.explosion_scale_end - self.explosion_scale_start) * scale_progress
            
            # Scale frame to match block size
            scaled_width = int(self.block_width * current_scale)
            scaled_height = int(self.block_height * current_scale)
            scaled_frame = pygame.transform.scale(current_frame, (scaled_width, scaled_height))
            
            # Center the explosion on the block
            explosion_x = block_x + (self.block_width - scaled_width) // 2
            explosion_y = block_y + (self.block_height - scaled_height) // 2
            
            # Draw the explosion frame
            self.screen.blit(scaled_frame, (explosion_x, explosion_y))
        
        # Track this region for updates
        temp_update_regions.append(pygame.Rect(
            block_x - self.block_width, 
            block_y - self.block_height, 
            self.block_width * 3, 
            self.block_height * 3
        ))
        
        # Return the update regions
        return temp_update_regions
    
    def update_cluster_effects(self, current_time):
        """Update and render any active cluster effects."""
        # Skip if we don't have cluster effects
        if not hasattr(self, 'cluster_animations'):
            self.cluster_animations = {}
            return
            
        # Process each cluster animation
        for cluster_id, anim_data in list(self.cluster_animations.items()):
            # Calculate elapsed time
            elapsed = current_time - anim_data['start_time']
            
            # Check if the animation has expired
            if elapsed > anim_data['duration']:
                # Remove expired animation
                self.cluster_animations.pop(cluster_id)
                continue
                
            # Update progress
            anim_data['progress'] = min(1.0, elapsed / anim_data['duration'])
            
            # Update cluster particles
            if cluster_id in self.cluster_particles:
                for particle in self.cluster_particles[cluster_id]:
                    # Update position
                    particle['x'] += particle['vx'] * elapsed
                    particle['y'] += particle['vy'] * elapsed
                    
                    # Update rotation
                    particle['rotation'] = (particle['rotation'] + particle['rotation_speed'] * elapsed) % 360
                    
                    # Bounce off cluster boundaries
                    if particle['x'] < min(x for x, y in anim_data['blocks']):
                        particle['x'] = min(x for x, y in anim_data['blocks'])
                        particle['vx'] *= -1
                    elif particle['x'] > max(x for x, y in anim_data['blocks']) + 1:
                        particle['x'] = max(x for x, y in anim_data['blocks']) + 1
                        particle['vx'] *= -1
                        
                    if particle['y'] < min(y for x, y in anim_data['blocks']):
                        particle['y'] = min(y for x, y in anim_data['blocks'])
                        particle['vy'] *= -1
                    elif particle['y'] > max(y for x, y in anim_data['blocks']) + 1:
                        particle['y'] = max(y for x, y in anim_data['blocks']) + 1
                        particle['vy'] *= -1
                    
                    # Calculate screen position
                    screen_x = int(min(x for x, y in anim_data['blocks']) * self.block_width)
                    screen_y = int(min(y for x, y in anim_data['blocks']) * self.block_height)
                    
                    # Create spark surface
                    spark_surf = pygame.Surface((particle['length'] * 2, particle['width'] * 2), pygame.SRCALPHA)
                    
                    # Draw spark shape
                    # Draw outer glow
                    rgb_color = particle['color'][:3] if len(particle['color']) >= 3 else particle['color']
                    glow_color = (*rgb_color, 100)  # More transparent for glow
                    pygame.draw.ellipse(spark_surf, glow_color, 
                                      (0, 0, particle['length'] * 2, particle['width'] * 2))
                    
                    # Draw main spark
                    pygame.draw.ellipse(spark_surf, (*rgb_color, 255), 
                                      (0, 0, particle['length'] * 2, particle['width'] * 2))
                    
                    # Rotate spark
                    rotated_spark = pygame.transform.rotate(spark_surf, particle['rotation'])
                    
                    # Draw the rotated spark
                    self.screen.blit(rotated_spark, 
                                   (screen_x - rotated_spark.get_width()//2,
                                    screen_y - rotated_spark.get_height()//2))
            
            # Render the cluster
            self.render_cluster(cluster_id, anim_data['blocks'])
    
    def render_cluster(self, cluster_id, blocks):
        """Render a single cluster animation."""
        x_offset = min(x for x, y in blocks) * self.block_width
        y_offset = min(y for x, y in blocks) * self.block_height
        width = (max(x for x, y in blocks) - min(x for x, y in blocks) + 1) * self.block_width
        height = (max(y for x, y in blocks) - min(y for x, y in blocks) + 1) * self.block_height
        
        # Create a unique identifier for this cluster based on its blocks
        cluster_id = tuple(sorted(blocks))
        
        # Get the base color for particles from the first block
        first_block = next(iter(blocks))
        base_color = self._get_block_color(first_block)
        
        # Initialize particles for this cluster if not already done
        if cluster_id not in self.cluster_particles:
            self.cluster_particles[cluster_id] = []
            # Create particles for each block in the cluster
            for block_x, block_y in blocks:
                for _ in range(self.sparks_per_block):
                    # Random position within the block
                    px = block_x + random.random()
                    py = block_y + random.random()
                    # Random direction
                    angle = random.uniform(0, 2 * math.pi)
                    speed = self.spark_speed * random.uniform(0.7, 1.3)
                    # Create particle with brighter color
                    r = min(255, int(base_color[0] * self.spark_brightness))
                    g = min(255, int(base_color[1] * self.spark_brightness))
                    b = min(255, int(base_color[2] * self.spark_brightness))
                    
                    # Add spark-specific properties
                    length = random.uniform(1, 2)  # Reduced length for smaller sparks
                    width = random.uniform(0.3, 0.8)   # Reduced width for smaller sparks
                    rotation = random.uniform(0, 360)  # Random initial rotation
                    rotation_speed = random.uniform(-180, 180)  # Random rotation speed
                    
                    self.cluster_particles[cluster_id].append({
                        'x': px,
                        'y': py,
                        'vx': math.cos(angle) * speed,
                        'vy': math.sin(angle) * speed,
                        'color': (r, g, b),
                        'length': length,
                        'width': width,
                        'rotation': rotation,
                        'rotation_speed': rotation_speed
                    })
        
        # Draw each block in the cluster with their correct texture
        for x, y in blocks:
            block_x = x_offset + (x * self.block_width)
            block_y = y_offset + (y * self.block_height)
            block_type = self.engine.puzzle_grid[y][x]
            
            # Draw the appropriate block type
            self._draw_block(block_type, block_x, block_y, self.block_width, self.block_height)
        
        # Update and draw particles
        current_time = time.time()
        dt = 1/60  # Assume 60fps for smooth movement
        
        for particle in self.cluster_particles[cluster_id]:
            # Update particle position
            particle['x'] += particle['vx'] * dt
            particle['y'] += particle['vy'] * dt
            
            # Update rotation
            particle['rotation'] = (particle['rotation'] + particle['rotation_speed'] * dt) % 360
            
            # Bounce off cluster boundaries
            if particle['x'] < min(x for x, y in blocks):
                particle['x'] = min(x for x, y in blocks)
                particle['vx'] *= -1
            elif particle['x'] > max(x for x, y in blocks) + 1:
                particle['x'] = max(x for x, y in blocks) + 1
                particle['vx'] *= -1
                
            if particle['y'] < min(y for x, y in blocks):
                particle['y'] = min(y for x, y in blocks)
                particle['vy'] *= -1
            elif particle['y'] > max(y for x, y in blocks) + 1:
                particle['y'] = max(y for x, y in blocks) + 1
                particle['vy'] *= -1
            
            # Calculate screen position
            screen_x = int(min(x for x, y in blocks) * self.block_width)
            screen_y = int(min(y for x, y in blocks) * self.block_height)
            
            # Create spark surface
            spark_surf = pygame.Surface((particle['length'] * 2, particle['width'] * 2), pygame.SRCALPHA)
            
            # Draw spark shape
            # Draw outer glow
            rgb_color = particle['color'][:3] if len(particle['color']) >= 3 else particle['color']
            glow_color = (*rgb_color, 100)  # More transparent for glow
            pygame.draw.ellipse(spark_surf, glow_color, 
                              (0, 0, particle['length'] * 2, particle['width'] * 2))
            
            # Draw main spark
            pygame.draw.ellipse(spark_surf, (*rgb_color, 255), 
                              (0, 0, particle['length'] * 2, particle['width'] * 2))
            
            # Rotate spark
            rotated_spark = pygame.transform.rotate(spark_surf, particle['rotation'])
            
            # Draw the rotated spark
            self.screen.blit(rotated_spark, 
                           (screen_x - rotated_spark.get_width()//2,
                            screen_y - rotated_spark.get_height()//2))
        
        # Clean up particles for clusters that no longer exist
        for old_cluster_id in list(self.cluster_particles.keys()):
            if old_cluster_id not in [tuple(sorted(c)) for c in self.previous_clusters]:
                del self.cluster_particles[old_cluster_id]
        
        # Track the entire cluster area for updates
        update_regions.append(pygame.Rect(
            x_offset - self.block_width,  # Add margin for particles that might move outside
            y_offset - self.block_height,
            width + self.block_width * 2,
            height + self.block_height * 2
        ))
    
    def update_strike_effects(self, current_time):
        """Update and render any active strike lightning effects."""
        # Skip if we don't have active strike effects
        if not hasattr(self, 'active_strike_effects'):
            self.active_strike_effects = {}
            return
            
        # Process each active strike effect
        for pos, effect_data in list(self.active_strike_effects.items()):
            # Calculate elapsed time
            elapsed = current_time - effect_data['start_time']
            
            # Check if the effect has expired
            if elapsed >= effect_data['duration']:
                # Remove expired effect
                self.active_strike_effects.pop(pos)
                continue
                
            # Calculate current intensity (fade out over time)
            effect_data['intensity'] = max(0.0, 1.0 - (elapsed / effect_data['duration']))
            
            # Only create new sparks periodically to avoid overwhelming particles
            if current_time - effect_data.get('last_spark_time', 0) > 0.1:  # Every 100ms
                # Create lightning bolt particles at random points around the strike
                for _ in range(3):  # Create 3 new lightning bolts each time
                    grid_x, grid_y = pos
                    
                    # Create lightning-like effect
                    self.create_lightning_bolt(grid_x, grid_y, effect_data['intensity'])
                    
                # Update last spark time
                effect_data['last_spark_time'] = current_time
    
    def create_lightning_bolt(self, grid_x, grid_y, intensity=1.0):
        """Create a lightning bolt effect at the specified grid position."""
        # Define electric colors with varying intensity
        base_colors = [
            (255, 255, 0),    # Yellow
            (200, 200, 255),  # Light blue
            (255, 255, 255)   # White
        ]
        
        # Choose random color
        base_color = random.choice(base_colors)
        
        # Apply intensity
        color = tuple(int(c * intensity) for c in base_color)
        
        # Create a longer, thinner particle with higher velocity
        # This will make it look more like electricity/lightning
        particle = {
            'x': 0.5 + random.uniform(-0.3, 0.3),  # Start near center with some variance
            'y': 0.5 + random.uniform(-0.3, 0.3),
            'vx': random.uniform(-0.1, 0.1) * 0.05,  # Slower horizontal movement
            'vy': random.uniform(-0.1, 0.1) * 0.05,  # Slower vertical movement
            'length': random.uniform(2.0, 4.0),  # Longer particles
            'width': random.uniform(0.1, 0.3),   # Thinner particles
            'color': color,
            'glow_color': (min(255, color[0] + 50), min(255, color[1] + 50), min(255, color[2] + 50)),
            'alpha': 255,
            'life': 0.4 * random.uniform(0.7, 1.0),  # Shorter lifespan for rapid flicker effect
            'max_life': 0.4,
            'rotation': random.uniform(0, 360),
            'rotation_speed': random.uniform(-360, 360),  # Faster rotation for electric look
            'is_lightning': True,  # Mark as lightning for special rendering
            'branches': [],  # Store branching bolts
            'fork_probability': 0.3  # Chance to fork into branches
        }
        
        # Add lightning-specific attributes for branching effect
        if random.random() < particle['fork_probability']:
            # Create 1-2 branches
            for _ in range(random.randint(1, 2)):
                branch = {
                    'x': particle['x'],
                    'y': particle['y'],
                    'angle': random.uniform(0, 360),
                    'length': particle['length'] * random.uniform(0.5, 0.8),
                    'width': particle['width'] * random.uniform(0.5, 0.8),
                    'color': color
                }
                particle['branches'].append(branch)
        
        # Add to block_breaking_animation if not present
        pos_key = (grid_x, grid_y)
        if pos_key not in self.breaking_blocks_animations:
            self.breaking_blocks_animations[pos_key] = {
                'particles': [],
                'start_time': time.time(),
                'progress': 0.0,
                'total_duration': 0.8,  # Longer duration for lightning effects
                'block_type': 'strike_1x4'  # Default to strike block type
            }
            
        # Add particle to this position
        self.breaking_blocks_animations[pos_key]['particles'].append(particle)
        
        return particle
    
    def draw_game_screen(self):
        print(f"[DEBUG] draw_game_screen called for engine: {self.engine}")
        try:
            # Clear screen with a dark background
            self.screen.fill((10, 10, 20))  # Very dark blue/black
            
            # Draw the background image if available
            if self.engine.puzzle_background:
                background_x = self.current_x_offset
                background_y = self.current_y_offset
                self.screen.blit(self.engine.puzzle_background, (background_x, background_y))
            
            # Draw the regular game elements
            self.draw_grid_blocks(self.current_x_offset, self.current_y_offset, self.block_width, self.block_height)
            if self.engine.game_active and self.engine.main_piece:
                self.draw_falling_piece(self.current_x_offset, self.current_y_offset, self.block_width, self.block_height)
            if self.engine.next_main_piece and self.engine.next_attached_piece:
                self.draw_next_piece_preview(self.block_width, self.block_height)
            self.draw_ui_elements()
            self.draw_combo_texts()

            # Draw game over animation if game is not active
            if not self.engine.game_active:
                self.draw_game_over_animation()
        except Exception as e:
            print(f"[DEBUG] Error in draw_game_screen: {e}")
            print(f"[DEBUG] Engine state: game_active={getattr(self.engine, 'game_active', 'N/A')}")
            print(f"[DEBUG] Chain reaction: {getattr(self.engine, 'chain_reaction_in_progress', 'N/A')}")
            print(f"[DEBUG] Breaking blocks: {getattr(self.engine, 'breaking_blocks', 'N/A')}")
            traceback.print_exc()
            # Try to continue with a minimal display
            try:
                self.screen.fill((10, 10, 20))
                if hasattr(self, 'engine') and hasattr(self.engine, 'font'):
                    error_text = self.engine.font.render("Rendering Error", True, (255, 255, 255))
                    self.screen.blit(error_text, (10, 10))
            except:
                pass  # If even the error display fails, just continue
    
    def draw_game_over_animation(self):
        """Draw the game over animation with fade in effect and particles."""
        current_time = time.time()

        # Initialize game over animation if not started
        if self.game_over_start_time is None:
            self.game_over_start_time = current_time
            # Create initial particles
            self.create_game_over_particles()
            # Initialize font if needed
            if self.game_over_font is None:
                try:
                    self.game_over_font = pygame.font.Font(self.combo_font_path, self.game_over_font_size)
                except:
                    self.game_over_font = pygame.font.SysFont(None, self.game_over_font_size)

        # Calculate animation progress
        progress = min(1.0, (current_time - self.game_over_start_time) / self.game_over_duration)
        alpha = int(255 * progress)

        # Create semi-transparent overlay
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, int(128 * progress)))  # Semi-transparent black
        self.screen.blit(overlay, (0, 0))

        # Update and draw particles
        self.update_game_over_particles(progress)
        self.draw_game_over_particles(progress)

        # Draw "GAME OVER" text with glow effect
        if self.game_over_font:
            text = "GAME OVER"
            text_surface = self.game_over_font.render(text, True, self.game_over_text_color)
            text_rect = text_surface.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))

            # Create glow effect
            glow_size = 20
            glow_surf = pygame.Surface((text_surface.get_width() + glow_size * 2,
                                      text_surface.get_height() + glow_size * 2), pygame.SRCALPHA)

            # Apply multi-layer glow
            for i in range(3):
                glow_alpha = int(alpha * (0.5 - i * 0.15))  # Decreasing alpha for outer layers
                glow_color = (*self.game_over_glow_color[:3], glow_alpha)
                size = (3 - i) * glow_size // 3
                pygame.draw.rect(glow_surf, glow_color,
                               pygame.Rect(glow_size - size, glow_size - size,
                                         text_surface.get_width() + size * 2,
                                         text_surface.get_height() + size * 2),
                               0, glow_size)

            # Draw glow and text
            self.screen.blit(glow_surf, (text_rect.x - glow_size, text_rect.y - glow_size))
            self.screen.blit(text_surface, text_rect)

    def create_game_over_particles(self):
        """Create particles for the game over animation."""
        self.game_over_particles = []
        num_particles = 50

        for _ in range(num_particles):
            # Create particles that move outward from the center
            center_x = self.screen.get_width() // 2
            center_y = self.screen.get_height() // 2
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 5)
            size = random.uniform(3, 8)
            
            particle = {
                'x': center_x,
                'y': center_y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'size': size,
                'color': self.game_over_text_color,
                'alpha': 255,
                'life': 1.0,
                'rotation': random.uniform(0, 360),
                'rotation_speed': random.uniform(-180, 180)
            }
            self.game_over_particles.append(particle)

    def update_game_over_particles(self, progress):
        """Update game over particle positions and properties."""
        for particle in self.game_over_particles[:]:
            # Update position
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            
            # Update rotation
            particle['rotation'] += particle['rotation_speed'] * 0.016
            
            # Update life and alpha
            particle['life'] -= 0.016
            particle['alpha'] = int(255 * particle['life'] * progress)
            
            # Remove dead particles
            if particle['life'] <= 0:
                self.game_over_particles.remove(particle)

    def draw_game_over_particles(self, progress):
        """Draw particles for the game over animation."""
        for particle in self.game_over_particles:
            if particle['alpha'] <= 0:
                continue

            # Create particle surface
            size = int(particle['size'])
            particle_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            
            # Draw particle with alpha
            rgb_color = particle['color'][:3] if len(particle['color']) >= 3 else particle['color']
            color_with_alpha = (*rgb_color, particle['alpha'])
            pygame.draw.circle(particle_surf, color_with_alpha, (size, size), size)
            
            # Rotate particle
            rotated_surf = pygame.transform.rotate(particle_surf, particle['rotation'])
            rect = rotated_surf.get_rect(center=(particle['x'], particle['y']))
            
            # Draw particle
            self.screen.blit(rotated_surf, rect)
    
    def draw_grid_blocks(self, x_offset, y_offset, block_width, block_height):
        """Draw the blocks that are placed on the grid, with performance optimizations"""
        # Initialize update_regions to track areas that need updating
        self.update_regions = []
        
        # Store current offsets for use in other methods
        self.current_x_offset = x_offset
        self.current_y_offset = y_offset
        self.block_width = block_width
        self.block_height = block_height
        
        # Get current clusters
        clusters = []
        cluster_positions = set()
        
        if hasattr(self.engine, 'find_all_clusters'):
            clusters = self.engine.find_all_clusters()
            
            # Create a set of all positions in clusters for faster lookups
            for cluster in clusters:
                for pos in cluster:
                    cluster_positions.add(pos)
        
        # Track garbage blocks that need to fall
        newly_detected_garbage = set()
        for y in range(self.engine.grid_height):
            for x in range(self.engine.grid_width):
                block_type = self.engine.puzzle_grid[y][x]
                if block_type and '_garbage' in block_type:
                    pos_key = (x, y)
                    newly_detected_garbage.add(pos_key)
        
        # Track previously seen garbage blocks to avoid re-animating constantly
        if not hasattr(self, 'previously_seen_garbage'):
            self.previously_seen_garbage = set()
        
        # Only animate garbage blocks that were not seen in the previous frame
        new_garbage_blocks = newly_detected_garbage - self.previously_seen_garbage
        
        # Create animations only for newly added garbage blocks
        for pos_key in new_garbage_blocks:
            x, y = pos_key
            block_type = self.engine.puzzle_grid[y][x]
            
            # Only create animation if this block hasn't been animated before
            if pos_key not in self.animated_garbage_blocks and pos_key not in self.visual_falling_blocks:
                # New garbage block - start it at the top of the screen
                self.visual_falling_blocks[pos_key] = {
                    'start_y': -1,  # Start above the grid
                    'target_y': y,
                    'progress': 0.0,
                    'start_time': time.time(),
                    'block_type': block_type,
                    'duration': 0.5,  # Half second fall duration
                    'visual_y': -1
                }
        
        # Update the set of previously seen garbage blocks for the next frame
        self.previously_seen_garbage = newly_detected_garbage.copy()
        
        # First, draw regular blocks (except those that are visually falling or breaking or in clusters)
        for y in range(self.engine.grid_height):
            for x in range(self.engine.grid_width):
                if self.engine.puzzle_grid[y][x] is not None:
                    # Skip if this is a breaking block
                    is_breaking = False
                    pos_key = (x, y)
                    
                    # Check engine breaking blocks
                    for bx, by, _, _, _, _ in self.engine.breaking_blocks:
                        if bx == x and by == y:
                            is_breaking = True
                            break
                    
                    # Also check our animation list
                    if pos_key in self.breaking_blocks_animations:
                        is_breaking = True
                    
                    if is_breaking:
                        continue
                        
                    # Skip if this block is visually falling
                    if pos_key in self.visual_falling_blocks:
                        continue
                
                    # Skip if this block is part of a cluster
                    if pos_key in cluster_positions:
                        continue
                    
                    block_type = self.engine.puzzle_grid[y][x]
                    
                    # Calculate position
                    block_x = x_offset + (x * block_width)
                    block_y = y_offset + (y * block_height)
                    
                    # Draw the appropriate block type
                    self._draw_block(block_type, block_x, block_y, block_width, block_height)
                    
                    # Track this region for updates
                    self.update_regions.append(pygame.Rect(block_x, block_y, block_width, block_height))
        
        # Draw clusters as cohesive units with glow effects
        for cluster in clusters:
            self.update_regions.extend(self._draw_cluster(cluster, x_offset, y_offset, block_width, block_height))
        
        # Remember engine grid offset for garbage block detection
        self.engine.grid_x_offset = x_offset
        self.engine.grid_y_offset = y_offset
        self.block_width = block_width
        self.block_height = block_height
        
        # Draw blocks that are visually falling with pixel-perfect animation
        current_time = time.time()
        for pos, block_data in list(self.visual_falling_blocks.items()):
            x, y = pos
            
            # Calculate progress
            elapsed = current_time - block_data['start_time']
            progress = min(1.0, elapsed / block_data['duration'])
            block_data['progress'] = progress
            
            # Calculate visual position with easing
            start_y = block_data['start_y']
            target_y = block_data['target_y']
            eased_progress = self._ease_out_quad(progress)
            visual_y = start_y + (target_y - start_y) * eased_progress
            block_data['visual_y'] = visual_y
            
            # Debug info for potentially stuck animations
            is_garbage = block_data['block_type'] and '_garbage' in block_data['block_type']
            
            # Calculate screen coordinates
            block_x = x_offset + (x * block_width)
            block_y = y_offset + int(visual_y * block_height)
            
            # Draw the block
            self._draw_block(block_data['block_type'], block_x, block_y, block_width, block_height)
            
            # Track this region for updates
            update_regions.append(pygame.Rect(block_x, block_y, block_width, block_height))
            
            # Remove completed animations and mark block as animated
            if progress >= 1.0:
                self.visual_falling_blocks.pop(pos)
                # Only add to animated_garbage_blocks if it's a garbage block
                if is_garbage:
                    self.animated_garbage_blocks.add(pos)
        
        # Clean up animated_garbage_blocks set when blocks are removed
        for pos in list(self.animated_garbage_blocks):
            x, y = pos
            if y >= 0 and y < self.engine.grid_height and x >= 0 and x < self.engine.grid_width:
                block_type = self.engine.puzzle_grid[y][x]
                if not block_type or '_garbage' not in block_type:
                    self.animated_garbage_blocks.remove(pos)
            else:
                # Position is out of bounds, remove it
                self.animated_garbage_blocks.remove(pos)
        
        # Draw breaking blocks with their spark particle effect
        for pos, block_data in self.breaking_blocks_animations.items():
            x, y = pos
            progress = block_data['progress']
            block_type = block_data['block_type']
            
            # Calculate position
            block_x = x_offset + (x * block_width)
            block_y = y_offset + (y * block_height)
            
            # Draw actual block with shrinking effect if early in animation
            if progress < 0.3:
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
                            # Avoid expensive scaling if not needed
                            block_copy = pygame.transform.scale(block_copy, (new_width, new_height))
                        except Exception:
                            # If scaling fails, just use original surface
                            pass
                    
                    # Center the scaled block
                    center_x = block_x + (block_width - new_width) // 2
                    center_y = block_y + (block_height - new_height) // 2
                    
                    # Draw scaled block
                    self.screen.blit(block_copy, (center_x, center_y))
            
            # Draw particles - optimize with batch rendering
            if 'particles' in block_data:
                # Only draw if we have particles and they're on screen
                if block_data['particles'] and 0 <= block_x <= self.engine.width and 0 <= block_y <= self.engine.height:
                    # Batch particles by size and color to minimize surface creation and blits
                    particle_batches = {}
                    
                    for particle in block_data['particles']:
                        # Calculate alpha based on remaining life
                        alpha = int(255 * (particle['life'] / particle['max_life']))
                        
                        # Calculate screen position
                        px = x_offset + (x * block_width) + (particle['x'] * block_width)
                        py = y_offset + (y * block_height) + (particle['y'] * block_height)
                        
                        # Skip particles that are off-screen
                        if px < -10 or px > self.engine.width + 10 or py < -10 or py > self.engine.height + 10:
                            continue
                        
                        # Create key for particle surface cache
                        color = particle['color']
                        glow_color = particle.get('glow_color', color)
                        particle_key = f"spark_{color[0]}_{color[1]}_{color[2]}_{glow_color[0]}_{glow_color[1]}_{glow_color[2]}_{int(particle['length'])}_{int(particle['width'])}_{alpha}"
                        
                        # Group particles by surface key
                        if particle_key not in particle_batches:
                            particle_batches[particle_key] = []
                        
                        # Calculate rotation
                        rotation = particle.get('rotation', 0)
                        rotation_speed = particle.get('rotation_speed', 0)
                        particle['rotation'] = (rotation + rotation_speed * 0.016) % 360
                        
                        # Store position and rotation to batch render later
                        particle_batches[particle_key].append((
                            int(px - particle['length']/2), 
                            int(py - particle['width']/2),
                            particle['rotation']
                        ))
                    
                    # Now render each batch with minimal surface creation
                    for particle_key, positions in particle_batches.items():
                        # Use cached surface or create new one
                        if particle_key not in self.particle_surfaces:
                            # Parse key back to components
                            key_parts = particle_key.split('_')
                            r, g, b = int(key_parts[1]), int(key_parts[2]), int(key_parts[3])
                            gr, gg, gb = int(key_parts[4]), int(key_parts[5]), int(key_parts[6])
                            length = int(key_parts[7])
                            width = int(key_parts[8])
                            alpha = int(key_parts[9])
                            
                            # Create surface with extra size for glow
                            glow_size = max(length, width) * 2
                            particle_surf = pygame.Surface((glow_size*2, glow_size*2), pygame.SRCALPHA)
                            
                            # Draw sharp spark shape
                            # Draw outer glow
                            for i in range(3):
                                glow_alpha = int(alpha * 0.3 * (1 - i/3))
                                glow_radius = max(length, width) + i*2
                                # Draw elongated glow
                                pygame.draw.ellipse(particle_surf, (gr, gg, gb, glow_alpha), 
                                                  (glow_size - length, glow_size - width, length*2, width*2))
                            
                            # Draw main spark with sharp edges
                            # Draw the main spark body
                            pygame.draw.ellipse(particle_surf, (r, g, b, alpha), 
                                              (glow_size - length, glow_size - width, length*2, width*2))
                            
                            # Add sharp tips to the spark
                            tip_length = length // 2
                            tip_width = width // 2
                            # Left tip
                            pygame.draw.ellipse(particle_surf, (r, g, b, alpha),
                                              (glow_size - length - tip_length, glow_size - tip_width,
                                               tip_length*2, tip_width*2))
                            # Right tip
                            pygame.draw.ellipse(particle_surf, (r, g, b, alpha),
                                              (glow_size + length - tip_length, glow_size - tip_width,
                                               tip_length*2, tip_width*2))
                            
                            self.particle_surfaces[particle_key] = particle_surf
                        
                        # Get cached surface
                        surf = self.particle_surfaces[particle_key]
                        
                        # Parse key to get length and width for positioning
                        key_parts = particle_key.split('_')
                        length = int(key_parts[7])
                        width = int(key_parts[8])
                        
                        # Batch blit all particles with this surface
                        for pos_x, pos_y, rotation in positions:
                            # Create a rotated copy of the surface
                            rotated_surf = pygame.transform.rotate(surf, rotation)
                            # Get the rect for centering
                            rect = rotated_surf.get_rect(center=(pos_x + length, pos_y + width))
                            # Draw the rotated particle
                            self.screen.blit(rotated_surf, rect)
            
            # Draw explosion sprite for blue pieces if available (moved after particles)
            if 'blue' in block_type and self.explosion_frames is not None and progress < 0.5:
                # Calculate which frame to show based on progress
                frame_count = len(self.explosion_frames)
                
                # Calculate normalized progress within the explosion duration
                explosion_progress = progress / 0.5  # Convert to 0-1 range
                
                # Calculate frame index with repetition for initial frames
                if explosion_progress < 0.3:  # First 30% of animation
                    # Repeat the first few frames
                    frame_index = (int(explosion_progress * self.explosion_repeat_frames * self.explosion_initial_frames)) % self.explosion_initial_frames
                else:
                    # Play remaining frames normally
                    remaining_frames = frame_count - self.explosion_initial_frames
                    frame_progress = (explosion_progress - 0.3) / 0.7  # Normalize remaining progress
                    frame_index = self.explosion_initial_frames + int(frame_progress * remaining_frames)
                
                # Get the current frame
                current_frame = self.explosion_frames[frame_index]
                
                # Calculate scale based on progress
                scale_progress = min(1.0, explosion_progress * 2)  # Scale up faster
                current_scale = self.explosion_scale_start + (self.explosion_scale_end - self.explosion_scale_start) * scale_progress
                
                # Scale frame to match block size
                scaled_width = int(block_width * current_scale)
                scaled_height = int(block_height * current_scale)
                scaled_frame = pygame.transform.scale(current_frame, (scaled_width, scaled_height))
                
                # Center the explosion on the block
                explosion_x = block_x + (block_width - scaled_width) // 2
                explosion_y = block_y + (block_height - scaled_height) // 2
                
                # Draw the explosion frame
                self.screen.blit(scaled_frame, (explosion_x, explosion_y))
            # Draw explosion sprite for yellow pieces if available
            elif 'yellow' in block_type and self.yellow_explosion_frames is not None and progress < 0.5:
                # Calculate which frame to show based on progress
                frame_count = len(self.yellow_explosion_frames)
                
                # Calculate normalized progress within the explosion duration
                explosion_progress = progress / 0.5  # Convert to 0-1 range
                
                # Calculate frame index with repetition for initial frames
                if explosion_progress < 0.3:  # First 30% of animation
                    # Repeat the first few frames
                    frame_index = (int(explosion_progress * self.explosion_repeat_frames * self.explosion_initial_frames)) % self.explosion_initial_frames
                else:
                    # Play remaining frames normally
                    remaining_frames = frame_count - self.explosion_initial_frames
                    frame_progress = (explosion_progress - 0.3) / 0.7  # Normalize remaining progress
                    frame_index = self.explosion_initial_frames + int(frame_progress * remaining_frames)
                
                # Get the current frame
                current_frame = self.yellow_explosion_frames[frame_index]
                
                # Calculate scale based on progress
                scale_progress = min(1.0, explosion_progress * 2)  # Scale up faster
                current_scale = self.explosion_scale_start + (self.explosion_scale_end - self.explosion_scale_start) * scale_progress
                
                # Scale frame to match block size
                scaled_width = int(block_width * current_scale)
                scaled_height = int(block_height * current_scale)
                scaled_frame = pygame.transform.scale(current_frame, (scaled_width, scaled_height))
                
                # Center the explosion on the block
                explosion_x = block_x + (block_width - scaled_width) // 2
                explosion_y = block_y + (block_height - scaled_height) // 2
                
                # Draw the explosion frame
                self.screen.blit(scaled_frame, (explosion_x, explosion_y))
            # Draw explosion sprite for red pieces if available
            elif 'red' in block_type and self.red_explosion_frames is not None and progress < 0.5:
                # Calculate which frame to show based on progress
                frame_count = len(self.red_explosion_frames)
                
                # Calculate normalized progress within the explosion duration
                explosion_progress = progress / 0.5  # Convert to 0-1 range
                
                # Calculate frame index with repetition for initial frames
                if explosion_progress < 0.3:  # First 30% of animation
                    # Repeat the first few frames
                    frame_index = (int(explosion_progress * self.explosion_repeat_frames * self.explosion_initial_frames)) % self.explosion_initial_frames
                else:
                    # Play remaining frames normally
                    remaining_frames = frame_count - self.explosion_initial_frames
                    frame_progress = (explosion_progress - 0.3) / 0.7  # Normalize remaining progress
                    frame_index = self.explosion_initial_frames + int(frame_progress * remaining_frames)
                
                # Get the current frame
                current_frame = self.red_explosion_frames[frame_index]
                
                # Calculate scale based on progress
                scale_progress = min(1.0, explosion_progress * 2)  # Scale up faster
                current_scale = self.explosion_scale_start + (self.explosion_scale_end - self.explosion_scale_start) * scale_progress
                
                # Scale frame to match block size
                scaled_width = int(block_width * current_scale)
                scaled_height = int(block_height * current_scale)
                scaled_frame = pygame.transform.scale(current_frame, (scaled_width, scaled_height))
                
                # Center the explosion on the block
                explosion_x = block_x + (block_width - scaled_width) // 2
                explosion_y = block_y + (block_height - scaled_height) // 2
                
                # Draw the explosion frame
                self.screen.blit(scaled_frame, (explosion_x, explosion_y))
            # Draw explosion sprite for green pieces if available
            elif 'green' in block_type and self.green_explosion_frames is not None and progress < 0.5:
                # Calculate which frame to show based on progress
                frame_count = len(self.green_explosion_frames)
                
                # Calculate normalized progress within the explosion duration
                explosion_progress = progress / 0.5  # Convert to 0-1 range
                
                # Calculate frame index with repetition for initial frames
                if explosion_progress < 0.3:  # First 30% of animation
                    # Repeat the first few frames
                    frame_index = (int(explosion_progress * self.explosion_repeat_frames * self.explosion_initial_frames)) % self.explosion_initial_frames
                else:
                    # Play remaining frames normally
                    remaining_frames = frame_count - self.explosion_initial_frames
                    frame_progress = (explosion_progress - 0.3) / 0.7  # Normalize remaining progress
                    frame_index = self.explosion_initial_frames + int(frame_progress * remaining_frames)
                
                # Get the current frame
                current_frame = self.green_explosion_frames[frame_index]
                
                # Calculate scale based on progress
                scale_progress = min(1.0, explosion_progress * 2)  # Scale up faster
                current_scale = self.explosion_scale_start + (self.explosion_scale_end - self.explosion_scale_start) * scale_progress
                
                # Scale frame to match block size
                scaled_width = int(block_width * current_scale)
                scaled_height = int(block_height * current_scale)
                scaled_frame = pygame.transform.scale(current_frame, (scaled_width, scaled_height))
                
                # Center the explosion on the block
                explosion_x = block_x + (block_width - scaled_width) // 2
                explosion_y = block_y + (block_height - scaled_height) // 2
                
                # Draw the explosion frame
                self.screen.blit(scaled_frame, (explosion_x, explosion_y))
            
            # Track this region for updates
            update_regions.append(pygame.Rect(
                block_x - block_width, 
                block_y - block_height, 
                block_width * 3, 
                block_height * 3
            ))
        
        # Return updated regions for efficient screen updates
        return update_regions
    
    def _draw_cluster(self, cluster, x_offset, y_offset, block_width, block_height):
        """Draw a cluster of connected blocks with visual effects."""
        # Initialize update regions
        temp_update_regions = []
        
        # Calculate cluster bounds for optimization
        min_x = min(x for x, y in cluster)
        min_y = min(y for x, y in cluster)
        max_x = max(x for x, y in cluster)
        max_y = max(y for x, y in cluster)
        
        cluster_x = x_offset + (min_x * block_width)
        cluster_y = y_offset + (min_y * block_height)
        cluster_width = (max_x - min_x + 1) * block_width
        cluster_height = (max_y - min_y + 1) * block_height
        
        # Check if cluster is worth drawing (offscreen detection)
        if cluster_x > self.screen.get_width() or cluster_y > self.screen.get_height() or \
           cluster_x + cluster_width < 0 or cluster_y + cluster_height < 0:
            return temp_update_regions  # Empty list for offscreen clusters
        
        # Draw each block in the cluster with glow effect
        for x, y in cluster:
            # Calculate position
            block_x = x_offset + (x * block_width)
            block_y = y_offset + (y * block_height)
            
            # Only draw blocks that exist in the grid
            if 0 <= y < self.engine.grid_height and 0 <= x < self.engine.grid_width:
                block_type = self.engine.puzzle_grid[y][x]
                
                if block_type:
                    # Draw block with glow effect for clusters
                    self._draw_block(block_type, block_x, block_y, block_width, block_height)
                    
                    # Track drawn regions for update
                    temp_update_regions.append(pygame.Rect(
                        block_x, block_y, block_width, block_height
                    ))
        
        # Add the overall cluster region for updates
        temp_update_regions.append(pygame.Rect(
            cluster_x - block_width,
            cluster_y - block_height,
            cluster_width + block_width * 2,
            cluster_height + block_height * 2
        ))
        
        return temp_update_regions
    
    def draw_falling_piece(self, x_offset, y_offset, block_width, block_height):
        """
        Draw the currently falling piece with pixel-perfect positioning and its attached piece.
        
        Args:
            x_offset: X coordinate of the grid's top-left corner
            y_offset: Y coordinate of the grid's top-left corner
            block_width: Width of each block in pixels
            block_height: Height of each block in pixels
        """
        if not self.engine.main_piece or not self.engine.attached_piece:
            return  # No active pieces to draw
            
        # Get the visual position of the piece (may include sub-grid positioning)
        visual_pos = self.engine.get_visual_position()
        
        # Get the attached piece coordinates based on its relative position
        attached_pos = None
        if hasattr(self.engine, 'get_attached_position_coords'):
            attached_pos = self.engine.get_attached_position_coords()
        
        # If position data is missing, bail out
        if not visual_pos or not attached_pos:
            return
            
        # Calculate the visual position of the attached piece
        main_x, main_y = visual_pos
        attached_x, attached_y = attached_pos
        
        # Special handling for pieces at the top of the board to keep them visually connected
        if main_y < 0:
            # Handle any rotation position when at the top of the board
            if self.engine.attached_position == 0:  # Top position
                attached_smooth_y = main_y - 1
            elif self.engine.attached_position == 1:  # Right position
                attached_smooth_y = main_y  # Same y-position for horizontal orientations
            elif self.engine.attached_position == 2:  # Bottom position
                attached_smooth_y = main_y + 1
            elif self.engine.attached_position == 3:  # Left position
                attached_smooth_y = main_y  # Same y-position for horizontal orientations
        else:
            # For normal cases, use the same smooth y-position offset as main piece
            attached_smooth_y = attached_y + (main_y - int(main_y))
        
        # Convert to screen coordinates
        main_screen_x = x_offset + (main_x * block_width)
        main_screen_y = y_offset + (main_y * block_height)
        attached_screen_x = x_offset + (attached_x * block_width)
        attached_screen_y = y_offset + (attached_smooth_y * block_height)
        
        # Draw both pieces with proper block types
        self._draw_block(self.engine.main_piece, main_screen_x, main_screen_y, block_width, block_height)
        self._draw_block(self.engine.attached_piece, attached_screen_x, attached_screen_y, block_width, block_height)
    
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # CRITICAL: DO NOT REMOVE THIS METHOD
    # This method has been accidentally removed multiple times. It is REQUIRED for gameplay.
    # The preview shows the next piece that will appear for the player.
    # Removing this will break the game's core functionality.
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    def draw_next_piece_preview(self, block_width, block_height):
        """
        Draw a preview of the next piece that will appear.
        CRITICAL: This method is required for gameplay and should not be removed.
        
        Args:
            block_width: Width of each block in pixels
            block_height: Height of each block in pixels
        """
        # Position preview box to the left of the board with increased spacing
        preview_x = self.current_x_offset - (block_width * 3)  # Three blocks left of the board
        preview_y = self.current_y_offset  # Align with top of board
        
        # Size the preview area for just two blocks vertically with increased padding
        preview_width = block_width + 20  # More padding for larger blocks
        preview_height = (block_height * 2) + 30  # More room for larger blocks
        
        # Draw a preview box with a golden border
        preview_rect = pygame.Rect(
            preview_x - 10, 
            preview_y - 10, 
            preview_width + 20, 
            preview_height + 20
        )
        
        # Draw background (dark blue like the main grid)
        pygame.draw.rect(self.screen, (15, 15, 35), preview_rect)
        
        # Draw golden border to match main grid
        pygame.draw.rect(self.screen, (220, 180, 60), preview_rect, 3)
        
        # Draw "NEXT" text with larger font
        next_text = self.engine.font.render("NEXT", True, (255, 255, 255))
        text_x = preview_x + (preview_width - next_text.get_width()) // 2
        text_y = preview_y - 35  # Moved up slightly
        self.screen.blit(next_text, (text_x, text_y))
        
        # Draw the next piece preview in its initial orientation
        # Center the blocks horizontally in the preview box
        block_x = preview_x + 10  # More padding from left edge
        
        # Draw the attached piece (top)
        attached_y = preview_y + 10  # More padding from top
        self._draw_block(self.engine.next_attached_piece, block_x, attached_y, block_width, block_height)
        
        # Draw the main piece (bottom)
        main_y = preview_y + block_height + 15  # More spacing between blocks
        self._draw_block(self.engine.next_main_piece, block_x, main_y, block_width, block_height)
    
    def draw_next_piece_preview_right(self, block_width, block_height):
        """
        Draw a preview of the next piece that will appear, positioned to the right of the board.
        Used for enemy board to mirror the player's preview.
        
        Args:
            block_width: Width of each block in pixels
            block_height: Height of each block in pixels
        """
        # Calculate grid width
        grid_width = self.engine.grid_width
        
        # Position preview box to the right of the board with increased spacing
        preview_x = self.current_x_offset + (grid_width * block_width) + block_width  # One block right of the board
        preview_y = self.current_y_offset  # Align with top of board
        
        # Size the preview area for just two blocks vertically with increased padding
        preview_width = block_width + 20  # More padding for larger blocks
        preview_height = (block_height * 2) + 30  # More room for larger blocks
        
        # Draw a preview box with a golden border
        preview_rect = pygame.Rect(
            preview_x - 10, 
            preview_y - 10, 
            preview_width + 20, 
            preview_height + 20
        )
        
        # Draw background (dark blue like the main grid)
        pygame.draw.rect(self.screen, (15, 15, 35), preview_rect)
        
        # Draw golden border to match main grid
        pygame.draw.rect(self.screen, (220, 180, 60), preview_rect, 3)
        
        # Draw "NEXT" text with larger font
        next_text = self.engine.font.render("NEXT", True, (255, 255, 255))
        text_x = preview_x + (preview_width - next_text.get_width()) // 2
        text_y = preview_y - 35  # Moved up slightly
        self.screen.blit(next_text, (text_x, text_y))
        
        # Draw the next piece preview in its initial orientation
        # Center the blocks horizontally in the preview box
        block_x = preview_x + 10  # More padding from left edge
        
        # Draw the attached piece (top)
        attached_y = preview_y + 10  # More padding from top
        self._draw_block(self.engine.next_attached_piece, block_x, attached_y, block_width, block_height)
        
        # Draw the main piece (bottom)
        main_y = preview_y + block_height + 15  # More spacing between blocks
        self._draw_block(self.engine.next_main_piece, block_x, main_y, block_width, block_height)
    
    def draw_ui_elements(self):
        """Draw UI elements like the back button."""
        # Draw back button (top left corner)
        button_width = 120
        button_height = 35
        button_x = 20
        button_y = 20
        
        back_button = {
            "rect": pygame.Rect(button_x, button_y, button_width, button_height),
            "text": "Back",
            "action": "back_to_menu"
        }
        
        # Draw the button with a clean, minimalist style
        pygame.draw.rect(self.screen, (30, 30, 50), back_button["rect"])
        pygame.draw.rect(self.screen, (180, 180, 200), back_button["rect"], 1)
        
        # Store in game buttons list for event handling
        self.engine.game_buttons = [back_button]
        
        # Draw button text
        button_font = pygame.font.SysFont(None, 24) if not self.engine.font else self.engine.font
        button_text = button_font.render(back_button["text"], True, (220, 220, 240))
        text_x = button_x + (button_width - button_text.get_width()) // 2
        text_y = button_y + (button_height - button_text.get_height()) // 2
        self.screen.blit(button_text, (text_x, text_y))
    
    def _draw_block(self, block_type, x, y, width, height):
        """
        Helper method to draw a specific block type at the given position with pixel-perfect positioning.
        
        Args:
            block_type: Type of block to draw
            x: X coordinate of the block's top-left corner (integer for pixel-perfect positioning)
            y: Y coordinate of the block's top-left corner (integer for pixel-perfect positioning)
            width: Width of the block in pixels
            height: Height of the block in pixels
        """
        # Handle None block type
        if block_type is None:
            # Create an empty transparent surface
            empty_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            self.screen.blit(empty_surface, (int(x), int(y)))
            return
        
        # Get the appropriate block surface
        block_surface = None
        
        # Check if this is a strike block
        if block_type == "strike_1x4":
            if hasattr(self.engine, 'strike_block'):
                block_surface = self.engine.strike_block.copy()
            else:
                # Fallback for strike block if image is missing
                block_surface = pygame.Surface((width, height))
                block_surface.fill((255, 165, 0))  # Orange color as fallback for strike
                # Add a distinctive pattern for strike
                pygame.draw.line(block_surface, (255, 255, 0), (0, 0), (width, height), 3)
                pygame.draw.line(block_surface, (255, 255, 0), (0, height), (width, 0), 3)
        
        # Check if this is a breaker or garbage block type
        is_breaker = '_breaker' in block_type
        is_garbage = '_garbage' in block_type
        
        # Strip any suffixes when checking for base image
        clean_type = block_type.replace('_breaker', '').replace('_garbage', '')
        
        # For garbage blocks, check if they're ready to transform
        if is_garbage:
            # Get the current time
            current_time = time.time()
            
            # Check if the block is ready to transform
            if hasattr(self.engine, 'attack_system') and self.engine.attack_system:
                # Get the block's position in grid coordinates
                grid_x = int((x - self.engine.grid_x_offset) / width)
                grid_y = int((y - self.engine.grid_y_offset) / height)
                
                # Check if this block is in the garbage blocks dictionary
                if (grid_x, grid_y) in self.engine.attack_system.garbage_blocks:
                    start_time, color = self.engine.attack_system.garbage_blocks[(grid_x, grid_y)]
                    elapsed_time = current_time - start_time
                    
                    # If enough time has passed, use the colored block
                    if elapsed_time >= self.engine.attack_system.transformation_time:
                        if 'red' in clean_type and hasattr(self.engine, 'red_block'):
                            block_surface = self.engine.red_block.copy()
                        elif 'blue' in clean_type and hasattr(self.engine, 'blue_block'):
                            block_surface = self.engine.blue_block.copy()
                        elif 'green' in clean_type and hasattr(self.engine, 'green_block'):
                            block_surface = self.engine.green_block.copy()
                        elif 'yellow' in clean_type and hasattr(self.engine, 'yellow_block'):
                            block_surface = self.engine.yellow_block.copy()
                    else:
                        # Still transforming, use gray block
                        block_surface = self.engine.gray_block.copy()
                else:
                    # Fallback to gray block if garbage block info not found
                    block_surface = self.engine.gray_block.copy()
            else:
                # Fallback to gray block if attack system not found
                block_surface = self.engine.gray_block.copy()
        # For breaker blocks, try to get the specific breaker image
        elif is_breaker:
            if 'red' in clean_type and hasattr(self.engine, 'red_breaker'):
                block_surface = self.engine.red_breaker.copy()
            elif 'blue' in clean_type and hasattr(self.engine, 'blue_breaker'):
                block_surface = self.engine.blue_breaker.copy()
            elif 'green' in clean_type and hasattr(self.engine, 'green_breaker'):
                block_surface = self.engine.green_breaker.copy()
            elif 'yellow' in clean_type and hasattr(self.engine, 'yellow_breaker'):
                block_surface = self.engine.yellow_breaker.copy()
        # For regular blocks, try to get the specific block image
        else:
            if 'red' in clean_type and hasattr(self.engine, 'red_block'):
                block_surface = self.engine.red_block.copy()
            elif 'blue' in clean_type and hasattr(self.engine, 'blue_block'):
                block_surface = self.engine.blue_block.copy()
            elif 'green' in clean_type and hasattr(self.engine, 'green_block'):
                block_surface = self.engine.green_block.copy()
            elif 'yellow' in clean_type and hasattr(self.engine, 'yellow_block'):
                block_surface = self.engine.yellow_block.copy()
            elif hasattr(self.engine, 'gray_block'):
                block_surface = self.engine.gray_block.copy()
        
        # If block surface is still None, create a fallback surface
        if block_surface is None:
            block_surface = pygame.Surface((width, height))
            if 'red' in clean_type:
                block_surface.fill((255, 0, 0))
            elif 'blue' in clean_type:
                block_surface.fill((0, 0, 255))
            elif 'green' in clean_type:
                block_surface.fill((0, 255, 0))
            elif 'yellow' in clean_type:
                block_surface.fill((255, 255, 0))
            else:
                block_surface.fill((150, 150, 150))
            
            # For fallback, manually add breaker indicator
            if is_breaker:
                pygame.draw.line(block_surface, (255, 255, 255), (5, 5), 
                               (width - 5, height - 5), 2)
                pygame.draw.line(block_surface, (255, 255, 255), (width - 5, 5), 
                               (5, height - 5), 2)
        
        # Scale the surface if needed
        if block_surface.get_width() != width or block_surface.get_height() != height:
            block_surface = pygame.transform.scale(block_surface, (width, height))
        
        # Draw the block
        self.screen.blit(block_surface, (int(x), int(y)))
    
    def _draw_block_with_effects(self, block_type, x, y, width, height, scale=1.0, rotation=0.0, progress=0.0):
        """Draw a block with visual effects."""
        # Get the appropriate block surface
        block_surface = None
        
        # Initialize block surface attributes if they don't exist
        if not hasattr(self, 'red_block_surface'):
            self.red_block_surface = getattr(self.engine, 'red_block', None)
        if not hasattr(self, 'blue_block_surface'):
            self.blue_block_surface = getattr(self.engine, 'blue_block', None)
        if not hasattr(self, 'green_block_surface'):
            self.green_block_surface = getattr(self.engine, 'green_block', None)
        if not hasattr(self, 'yellow_block_surface'):
            self.yellow_block_surface = getattr(self.engine, 'yellow_block', None)
        if not hasattr(self, 'gray_block_surface'):
            self.gray_block_surface = getattr(self.engine, 'gray_block', None)
            
        # Select the appropriate block surface based on type
        if 'red' in block_type:
            block_surface = self.red_block_surface
        elif 'blue' in block_type:
            block_surface = self.blue_block_surface
        elif 'green' in block_type:
            block_surface = self.green_block_surface
        elif 'yellow' in block_type:
            block_surface = self.yellow_block_surface
        else:
            block_surface = self.gray_block_surface
            
        if block_surface is None:
            # Create a fallback surface if no image is available
            block_surface = pygame.Surface((width, height))
            if 'red' in block_type:
                block_surface.fill((255, 0, 0))
            elif 'blue' in block_type:
                block_surface.fill((0, 0, 255))
            elif 'green' in block_type:
                block_surface.fill((0, 255, 0))
            elif 'yellow' in block_type:
                block_surface.fill((255, 255, 0))
            else:
                block_surface.fill((150, 150, 150))
            
        # Calculate new size based on scale
        new_width = int(width * scale)
        new_height = int(height * scale)
        
        # Skip if too small to see
        if new_width <= 0 or new_height <= 0:
            return
            
        # Scale the surface
        scaled_surface = pygame.transform.scale(block_surface, (new_width, new_height))
        
        # Apply rotation if needed
        if rotation != 0:
            scaled_surface = pygame.transform.rotate(scaled_surface, rotation)
            
        # Calculate position to keep block centered
        center_offset_x = (width - scaled_surface.get_width()) // 2
        center_offset_y = (height - scaled_surface.get_height()) // 2
        
        # Draw the block
        self.screen.blit(scaled_surface, (x + center_offset_x, y + center_offset_y))
        
        # No additional effects here - all breaking animations are handled in the main system

    def create_dust_particles(self, x, y, block_color):
        """Create spark-like particles for a breaking block."""
        print(f"DEBUG: Creating spark particles for block at ({x}, {y}) with color {block_color}")
        particles = []
        
        # Initialize required particle attributes if they don't exist
        if not hasattr(self, 'particle_count_per_block'):
            self.particle_count_per_block = 20  # Increased for more particles
        if not hasattr(self, 'particle_max_speed'):
            self.particle_max_speed = 4.0  # Increased for faster particles
        if not hasattr(self, 'particle_min_speed'):
            self.particle_min_speed = 1.0  # Increased for faster minimum speed
        if not hasattr(self, 'particle_max_size'):
            self.particle_max_size = 5  # Increased for larger particles
        if not hasattr(self, 'particle_min_size'):
            self.particle_min_size = 2
        if not hasattr(self, 'particle_lifespan'):
            self.particle_lifespan = 0.8  # Increased for longer-lasting particles
        if not hasattr(self, 'particle_surfaces'):
            self.particle_surfaces = {}
        if not hasattr(self, 'breaking_blocks_animations'):
            self.breaking_blocks_animations = {}
        
        # Determine particle color based on block color
        if 'red' in block_color:
            particle_color = (255, 100, 100)
            glow_color = (255, 50, 50)
        elif 'blue' in block_color:
            particle_color = (80, 200, 255)
            glow_color = (50, 150, 255)
        elif 'green' in block_color:
            particle_color = (100, 255, 140)
            glow_color = (50, 255, 100)
        elif 'yellow' in block_color:
            particle_color = (255, 230, 100)
            glow_color = (255, 200, 50)
        else:
            particle_color = (200, 200, 200)
            glow_color = (180, 180, 180)
        
        print(f"DEBUG: Particle colors - main: {particle_color}, glow: {glow_color}")
        
        # Create particles with random velocities and varying sizes
        for _ in range(self.particle_count_per_block):
            # Random angle for velocity with some bias towards outward direction
            angle = random.uniform(0, 2 * math.pi)
            # Add some randomness to speed for more natural look
            speed = random.uniform(self.particle_min_speed, self.particle_max_speed)
            
            # Create particle with varying size
            life_value = self.particle_lifespan * random.uniform(0.7, 1.0)
            
            # Create spark-like particle with length and width
            length = random.uniform(0.4, 2)  # Increased length for more elongated sparks
            width = random.uniform(0.5, 2)    # Decreased width for sharper sparks
            
            # Add initial upward velocity for explosion effect
            initial_vy = -random.uniform(0.5, 1.5)  # Initial upward velocity
            
            particle = {
                'x': 0.5,  # Center of block (normalized coordinates)
                'y': 0.5,  # Center of block (normalized coordinates)
                'vx': math.cos(angle) * speed * 0.02,  # Scale velocity to match grid coordinates
                'vy': initial_vy * 0.02,  # Initial upward velocity
                'length': length,
                'width': width,
                'color': particle_color,
                'glow_color': glow_color,
                'alpha': 255,
                'life': life_value,
                'max_life': life_value,
                'rotation': random.uniform(0, 360),  # Add rotation for more dynamic look
                'rotation_speed': random.uniform(-180, 180),  # Random rotation speed
                'trail': []  # Store previous positions for trail effect
            }
            particles.append(particle)
            
        print(f"DEBUG: Created {len(particles)} spark particles")
        return particles

    def manage_particle_cache(self):
        """Manage the particle surface cache to prevent memory leaks."""
        # Limit cache size to 100 entries
        if len(self.particle_surfaces) > 100:
            # Only keep the first 50 entries (simple approach)
            keys_to_remove = list(self.particle_surfaces.keys())[50:]
            for key in keys_to_remove:
                del self.particle_surfaces[key]

    def update(self):
        current_time = time.time()
        frame_time = current_time - self.last_frame_time
        self.last_frame_time = current_time
        
        # Cap frame time to prevent spiral of death
        if frame_time > 0.25:
            frame_time = 0.25
        
        # Accumulate time
        self.accumulator += frame_time
        
        # Run fixed updates
        while self.accumulator >= self.fixed_timestep:
            self.fixed_update(self.fixed_timestep)
            self.accumulator -= self.fixed_timestep
        
        # Calculate alpha for interpolation
        alpha = self.accumulator / self.fixed_timestep
        
        # Periodically manage particle cache (every ~2 seconds)
        if random.random() < 0.01:  # ~1% chance per frame
            self.manage_particle_cache()
        
        # Render with interpolation
        self.render(alpha)

    def fixed_update(self, dt):
        # Update animation logic with fixed timestep
        # Update all animations at precise intervals 
        pass  # Add a pass statement to create a valid function body

    def limit_fps(self, fps):
        self.clock.tick(fps) 

    def render(self, alpha):
        """Render the game with interpolation between fixed updates."""
        # This method should handle rendering with interpolation
        # For now, just call draw_game_screen which handles all rendering
        self.draw_game_screen() 

    def _get_block_color(self, block_pos):
        """
        Get the RGB color values for a block at the given position.
        
        Args:
            block_pos: Tuple of (x, y) coordinates
            
        Returns:
            Tuple of RGB values (r, g, b)
        """
        x, y = block_pos
        
        if not (0 <= x < self.engine.grid_width and 0 <= y < self.engine.grid_height):
            return (200, 200, 200)  # Default gray
        
        if self.engine.puzzle_grid[y][x] is None:
            return (200, 200, 200)  # Default gray
        
        block_type = self.engine.puzzle_grid[y][x]
        color_name = block_type.split('_')[0]  # Remove any suffix like "_breaker"
        
        if color_name == 'red':
            return (255, 100, 100)
        elif color_name == 'blue':
            return (100, 100, 255)
        elif color_name == 'green':
            return (100, 255, 100)
        elif color_name == 'yellow':
            return (255, 255, 100)
        else:
            return (200, 200, 200)  # Default gray 

    def show_combo_text(self, combo_count, screen_pos=None):
        """
        Display combo text animation when combos occur.
        
        Args:
            combo_count: Number of blocks broken in the combo
            screen_pos: Optional position for the text (x, y), defaults to center screen
        """
        # Skip if combo is only 1 block (not really a combo)
        if combo_count <= 1:
            return
            
        # Initialize font if not already done
        if self.combo_font is None:
            try:
                self.combo_font = pygame.font.Font(self.combo_font_path, self.combo_font_size)
            except:
                # Fallback to default font if custom font fails to load
                self.combo_font = pygame.font.SysFont(None, self.combo_font_size)
        
        # Get the appropriate combo message
        if combo_count in self.combo_text_messages:
            combo_message = self.combo_text_messages[combo_count]
        elif combo_count > 10:
            # For higher values, generate a direct message with the actual count
            combo_message = f"{combo_count}x Cosmic Combo!"
        else:
            # Fallback for unexpected values
            combo_message = f"{combo_count}x Combo!"
        
        # Determine text color and effects based on combo size
        if combo_count <= 3:
            text_color = (255, 80, 80)  # Red for smaller combos
            glow_color = (255, 120, 120, 180)
            particle_color = (255, 100, 100)
            particle_count = self.combo_particle_count
            rainbow_mode = False
        elif combo_count <= 5:
            text_color = (255, 180, 50)  # Orange/yellow for medium combos
            glow_color = (255, 200, 80, 180)
            particle_color = (255, 220, 100)
            particle_count = self.combo_particle_count * 2
            rainbow_mode = combo_count >= self.rainbow_trail_threshold
        else:
            text_color = (120, 220, 255)  # Blue for large combos
            glow_color = (150, 240, 255, 180)
            particle_color = (100, 200, 255)
            particle_count = self.combo_particle_count * 3
            rainbow_mode = True  # Always enable rainbow mode for large combos
        
        # Render the text
        text_surface = self.combo_font.render(combo_message, True, text_color)
        
        # Apply glow effect
        glow_size = 10
        glow_surface = pygame.Surface((
            text_surface.get_width() + glow_size * 2, 
            text_surface.get_height() + glow_size * 2
        ), pygame.SRCALPHA)
        
        # Calculate position
        if screen_pos is None:
            # Default to center screen, slightly above middle
            x = (self.engine.width - text_surface.get_width()) // 2
            y = (self.engine.height - text_surface.get_height()) // 2 - 50
        else:
            x, y = screen_pos
        
        # Create particle effects
        particles = []
        for _ in range(particle_count):
            # Random angle for velocity
            angle = random.uniform(0, 2 * math.pi)
            
            # Speed increases with combo size for more explosive effect
            base_speed = 0.5 + (combo_count * 0.2)
            speed = random.uniform(base_speed, base_speed * 2.0)
            
            # Select particle color - for rainbow mode, assign a random rainbow color
            current_particle_color = particle_color  # Start with the default color
            if rainbow_mode and random.random() < 0.6:  # 60% chance of rainbow particles
                current_particle_color = random.choice(self.rainbow_colors)
            print(f"[DEBUG] Creating combo particle with color: {current_particle_color}")
            
            # Create particle
            life_value = self.combo_particle_lifespan * random.uniform(0.7, 1.0)  # Calculate lifespan once
            particle = {
                'x': x + text_surface.get_width() // 2,  # Center of text
                'y': y + text_surface.get_height() // 2,  # Center of text
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'size': random.uniform(2, 4 + combo_count/2),  # Larger particles for bigger combos
                'color': current_particle_color,
                'alpha': 255,
                'life': life_value,  # Use the calculated lifespan
                'rainbow': rainbow_mode and random.random() < 0.8  # 80% chance of rainbow trail for eligible particles
            }
            particles.append(particle)
        
        # Add combo text entry with all details
        self.combo_texts.append({
            'text': combo_message,
            'surface': text_surface,
            'glow_surface': glow_surface,
            'x': x,
            'y': y,
            'particles': particles,
            'color': text_color,
            'glow_color': glow_color,
            'start_time': time.time(),
            'duration': self.combo_text_duration,
            'progress': 0.0,
            'combo_size': combo_count,  # Store combo size for potential additional effects
            'screen_shake': combo_count >= 5,  # Add screen shake for large combos
            'shake_amount': min(5, combo_count - 3) if combo_count >= 5 else 0,  # Scale shake with combo size
            'shake_duration': 0.3,  # Seconds
            'rainbow_mode': rainbow_mode  # Track if this combo uses rainbow effects
        })
    
    def draw_combo_texts(self):
        """Draw active combo text animations"""
        current_time = time.time()
        
        # Track if we need to apply screen shake
        active_shake = False
        shake_offset_x = 0
        shake_offset_y = 0
        
        for combo_text in self.combo_texts:
            # Calculate animation progress
            elapsed = current_time - combo_text['start_time']
            progress = min(1.0, elapsed / combo_text['duration'])
            
            # Apply animation effects based on progress - only fade in/out, no scaling
            if progress < 0.2:
                # Fade in (0.0 - 0.2)
                scale = 1.0  # Keep constant scale
                alpha = int(255 * (progress / 0.2))
            elif progress > 0.8:
                # Fade out (0.8 - 1.0)
                scale = 1.0  # Keep constant scale
                alpha = int(255 * (1.0 - (progress - 0.8) / 0.2))
            else:
                # Hold (0.2 - 0.8)
                scale = 1.0
                alpha = 255
                
                # Remove pulsing effect
                # Remove scale explosion effect
            
            # Handle screen shake
            if combo_text.get('screen_shake', False):
                shake_progress = min(1.0, elapsed / combo_text.get('shake_duration', 0.3))
                if shake_progress < 1.0:
                    shake_amount = combo_text.get('shake_amount', 0) * (1.0 - shake_progress)
                    shake_offset_x = random.uniform(-shake_amount, shake_amount)
                    shake_offset_y = random.uniform(-shake_amount, shake_amount)
                    active_shake = True
            
            # Skip rendering if alpha is too low
            if alpha <= 5:
                continue
            
            # Use original surface without scaling
            scaled_surface = combo_text['surface']
            scaled_width = scaled_surface.get_width()
            scaled_height = scaled_surface.get_height()
            
            # Position without adjusting for scaling (since we're not scaling)
            centered_x = combo_text['x']
            centered_y = combo_text['y']
            
            # Apply screen shake offset if active
            if active_shake:
                centered_x += shake_offset_x
                centered_y += shake_offset_y
            
            # Draw glow effect first (larger for bigger combos)
            glow_size = 10 + (combo_text['combo_size'] // 2)
            glow_surf = pygame.Surface((
                scaled_width + glow_size * 2, 
                scaled_height + glow_size * 2
            ), pygame.SRCALPHA)
            
            # Get glow color with adjusted alpha
            glow_color = list(combo_text['glow_color'])
            glow_color[3] = int(glow_color[3] * (alpha / 255))
            
            # Apply glow based on combo size
            if combo_text['combo_size'] >= 6:
                # For large combos, use multiple layers of glow for an intense effect
                for i in range(3):
                    size = (3 - i) * glow_size // 3
                    intensity = glow_color[3] // (i + 1)
                    temp_color = (glow_color[0], glow_color[1], glow_color[2], intensity)
                    pygame.draw.rect(glow_surf, temp_color, 
                                    pygame.Rect(glow_size - size, glow_size - size, 
                                                scaled_width + size * 2, scaled_height + size * 2),
                                    0, glow_size)
            else:
                # Simple glow for smaller combos
                pygame.draw.rect(glow_surf, tuple(glow_color), 
                                pygame.Rect(glow_size//2, glow_size//2, 
                                            scaled_width + glow_size, scaled_height + glow_size), 
                                0, glow_size)
            
            # Draw the glow
            self.screen.blit(glow_surf, (centered_x - glow_size, centered_y - glow_size))
            
            # Draw the text
            self.screen.blit(scaled_surface, (centered_x, centered_y))
            
            # Draw particles
            if 'particles' in combo_text:
                # Check if this combo has rainbow mode enabled
                combo_has_rainbow = combo_text.get('rainbow_mode', False)
                    
                for particle in combo_text['particles']:
                    # Skip dead particles
                    if particle['life'] <= 0:
                        continue
                        
                    # Calculate alpha based on remaining life
                    particle_alpha = int(255 * (particle['life'] / self.combo_particle_lifespan) * (alpha / 255))
                    
                    # Draw rainbow trail if enabled for this specific particle
                    if combo_has_rainbow and particle.get('rainbow', False) and 'trail' in particle and particle['trail']:
                        # Draw trail segments from oldest to newest
                        for i, pos in enumerate(reversed(particle['trail'])):
                            # Get rainbow color based on position in trail
                            color_idx = (i + int(current_time * 7)) % len(self.rainbow_colors)
                            rainbow_color = self.rainbow_colors[color_idx]
                            
                            # Calculate trail segment size (smaller for older segments)
                            segment_size = max(1, int(particle['size'] * (1.0 - (i / len(particle['trail'])))))
                            
                            # Calculate trail alpha (more transparent for older segments)
                            trail_alpha = int(particle_alpha * (self.rainbow_trail_fade ** i))
                            
                            if segment_size <= 0 or trail_alpha <= 0:
                                continue
                                
                            # Create trail segment surface
                            trail_key = f"trail_{rainbow_color[0]}_{rainbow_color[1]}_{rainbow_color[2]}_{segment_size}_{trail_alpha}"
                            
                            if trail_key not in self.particle_surfaces:
                                trail_surf = pygame.Surface((segment_size*2, segment_size*2), pygame.SRCALPHA)
                                pygame.draw.circle(trail_surf, (*rainbow_color, trail_alpha),
                                                (segment_size, segment_size), segment_size)
                                self.particle_surfaces[trail_key] = trail_surf
                            
                            # Draw the trail segment
                            segment_x = int(pos['x'] - segment_size)
                            segment_y = int(pos['y'] - segment_size)
                            
                            # Apply screen shake to trail too
                            if active_shake:
                                segment_x += shake_offset_x
                                segment_y += shake_offset_y
                                
                            self.screen.blit(self.particle_surfaces[trail_key], (segment_x, segment_y))
                    
                    # Draw particle
                    particle_size = int(particle['size'])  # Remove scale factor from particle size
                    if particle_size <= 0:
                        continue
                        
                    # Create key for particle surface cache
                    color = particle['color']
                    # Safety check: ensure color is a valid RGB tuple
                    if not color or not isinstance(color, (tuple, list)) or len(color) < 3:
                        # Fallback to a safe color if invalid
                        color = (255, 255, 255)  # White as fallback
                        particle['color'] = color
                    particle_key = f"combo_{color[0]}_{color[1]}_{color[2]}_{particle_size}_{particle_alpha}"
                    
                    # Use cached surface or create new one
                    if particle_key not in self.particle_surfaces:
                        particle_surf = pygame.Surface((particle_size*2, particle_size*2), pygame.SRCALPHA)
                        rgb_color = color[:3] if len(color) >= 3 else color
                        alpha = max(0, min(255, particle['alpha']))
                        try:
                            pygame.draw.circle(particle_surf, (*rgb_color, alpha), 
                                            (particle_size, particle_size), particle_size)
                        except Exception as e:
                            print(f"[DEBUG] Error in update_combo_texts particle: color={color}, rgb_color={rgb_color}, alpha={alpha}, error={e}")
                            traceback.print_exc()
                        self.particle_surfaces[particle_key] = particle_surf
                    
                    # Draw the particle
                    particle_x = int(particle['x'] - particle_size)
                    particle_y = int(particle['y'] - particle_size)
                    
                    # Apply screen shake to particles too for consistent effect
                    if active_shake:
                        particle_x += shake_offset_x
                        particle_y += shake_offset_y
                        
                    self.screen.blit(self.particle_surfaces[particle_key], (particle_x, particle_y))

    def _limit_particle_count(self):
        """Limit the total number of particles in the system for performance reasons."""
        # Track total particles for limiting
        total_particles = 0
        max_particles = 500  # Increased from 300 to 500 to allow more particles
        
        # Count particles from breaking animations
        for block_data in self.breaking_blocks_animations.values():
            if 'particles' in block_data:
                total_particles += len(block_data['particles'])
        
        # Count particles from combo texts
        for combo_text in self.combo_texts:
            if 'particles' in combo_text:
                total_particles += len(combo_text['particles'])
        
        # If we have too many particles, remove some from the oldest animations
        if total_particles > max_particles:
            # First try removing from breaking blocks
            if self.breaking_blocks_animations:
                # Sort animations by start time (oldest first)
                sorted_animations = sorted(
                    self.breaking_blocks_animations.items(),
                    key=lambda x: x[1].get('start_time', 0)
                )
                
                # Remove particles from oldest animations until we're under the limit
                particles_to_remove = total_particles - max_particles
                for pos_key, block_data in sorted_animations:
                    if 'particles' in block_data and block_data['particles']:
                        # Remove particles proportionally (up to half of this animation's particles)
                        remove_count = min(
                            particles_to_remove,
                            len(block_data['particles']) // 2
                        )
                        if remove_count > 0:
                            # Remove oldest particles (first in list)
                            block_data['particles'] = block_data['particles'][remove_count:]
                            particles_to_remove -= remove_count
                    
                    # Stop if we've removed enough
                    if particles_to_remove <= 0:
                        break
            
            # If we still have too many, try removing from combo texts
            if total_particles - max_particles > 0 and self.combo_texts:
                # Sort combo texts by start time (oldest first)
                sorted_combos = sorted(
                    self.combo_texts,
                    key=lambda x: x.get('start_time', 0)
                )
                
                # Remove particles from oldest combo texts until we're under the limit
                particles_to_remove = total_particles - max_particles
                for combo_text in sorted_combos:
                    if 'particles' in combo_text and combo_text['particles']:
                        # Remove particles proportionally
                        remove_count = min(
                            particles_to_remove,
                            len(combo_text['particles']) // 2
                        )
                        if remove_count > 0:
                            # Remove oldest particles (first in list)
                            combo_text['particles'] = combo_text['particles'][remove_count:]
                            particles_to_remove -= remove_count
                    
                    # Stop if we've removed enough
                    if particles_to_remove <= 0:
                        break

    def has_falling_animations(self):
        """Check if there are any falling block animations currently in progress."""
        # Check for falling block animations
        if hasattr(self, 'visual_falling_blocks') and self.visual_falling_blocks:
            # Apply timeout logic to prevent stuck animations
            current_time = time.time()
            valid_animations = False
            
            for pos, block_data in list(self.visual_falling_blocks.items()):
                x, y = pos
                block_type = block_data.get('block_type', None)
                is_garbage = block_type and '_garbage' in block_type
                elapsed_time = current_time - block_data['start_time']
                
                if is_garbage:
                    # More aggressive timeout for garbage blocks
                    if elapsed_time > 0.8:  # 800ms for garbage blocks
                        self.visual_falling_blocks.pop(pos, None)
                        
                        # Mark it as animated to prevent re-animation
                        if not hasattr(self, 'animated_garbage_blocks'):
                            self.animated_garbage_blocks = set()
                        self.animated_garbage_blocks.add(pos)
                    else:
                        valid_animations = True
                else:
                    # Regular timeout for non-garbage blocks
                    if elapsed_time > 1.3:  # 1.3 second timeout (slightly longer than max fall time)
                        self.visual_falling_blocks.pop(pos, None)
                    else:
                        valid_animations = True
                    
            return valid_animations
        return False

    def animations_in_progress(self):
        """Check if there are any animations currently in progress."""
        # Check for falling block animations
        if hasattr(self, 'visual_falling_blocks') and self.visual_falling_blocks:
            return True
            
        # Check for breaking animations
        if hasattr(self, 'breaking_blocks_animations') and self.breaking_blocks_animations:
            return True
            
        # Check for strike effects
        if hasattr(self, 'active_strike_effects') and self.active_strike_effects:
            return True
            
        return False
        
    def _lerp(self, start, end, progress):
        """Linear interpolation between start and end values."""
        return start + (end - start) * progress
        
    def _ease_out_quad(self, progress):
        """Quadratic easing out - decelerating to zero velocity."""
        return -progress * (progress - 2)