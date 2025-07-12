import pygame
import sys
import os
import time
import math
import random
from attack_system import GarbageBlockState

class PuzzleRenderer:
    """
    Handles rendering and visual effects for the puzzle game.
    This class separates rendering logic from game mechanics.
    """
    def __init__(self, puzzle_engine):
        """
        Initialize the renderer with a reference to the puzzle engine.
        
        Args:
            puzzle_engine: The PuzzleEngine instance that contains game state
        """
        self.engine = puzzle_engine
        self.screen = puzzle_engine.screen
        
        # Set a reference to this renderer in the engine
        self.engine.renderer = self
        
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
        self.cluster_glow_particles = []
        
        # Particle cache for better performance
        self.particle_surfaces = {}
        
        # Enhanced particle settings for breaking animations
        self.particle_count_per_block = 8  # REDUCED from 20 to 8 for better performance
        self.particle_max_speed = 2.0  # Slightly slower particles for better performance
        self.particle_min_speed = 0.5  # Slower minimum speed
        self.particle_max_size = 3  # Smaller maximum size for better performance
        self.particle_min_size = 1  # Minimum particle size
        self.particle_lifespan = 0.5  # Shorter lifespan for better performance
        
        # Track recently broken blocks to prevent unwanted cluster animations
        self.recently_broken_positions = set()
        self.recent_break_history_time = 1.0  # How long to remember broken blocks (in seconds)
        self.recent_break_timestamps = {}  # Format: {(x, y): timestamp}
        
        # Track clusters for animations - MOVED UP before update_visual_state call
        self.previous_clusters = []  # List of sets containing (x,y) coordinates from last frame
        self.cluster_animations = {}  # Format: {cluster_id: {start_time, duration, blocks}}
        self.cluster_animation_duration = 1.0  # 1 second for cluster formation animation
        self.next_cluster_id = 0  # Unique ID for each cluster animation
        
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
    
    def update_visual_state(self):
        """Update the visual state to match the current game state."""
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
                if current_time - data['start_time'] > data['total_duration'] * 1.2:
                    self.breaking_blocks_animations.pop(pos, None)
            
        # Add new breaking animations
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
            
            # Store the actual block surface for animation consistency
            block_surface = None
            
            # Try to get the block surface from the engine (same logic as in _draw_block)
            # Strip any suffixes when checking for base image
            clean_type = block_type.replace('_breaker', '').replace('_garbage', '')
            is_garbage = '_garbage' in block_type
            
            if clean_type == 'red' and hasattr(self.engine, 'red_block'):
                block_surface = self.engine.red_block
            elif clean_type == 'blue' and hasattr(self.engine, 'blue_block'):
                block_surface = self.engine.blue_block
            elif clean_type == 'green' and hasattr(self.engine, 'green_block'):
                block_surface = self.engine.green_block
            elif clean_type == 'yellow' and hasattr(self.engine, 'yellow_block'):
                block_surface = self.engine.yellow_block
            elif '_breaker' in block_type:
                if 'red' in clean_type and hasattr(self.engine, 'red_breaker'):
                    block_surface = self.engine.red_breaker
                elif 'blue' in clean_type and hasattr(self.engine, 'blue_breaker'):
                    block_surface = self.engine.blue_breaker
                elif 'green' in clean_type and hasattr(self.engine, 'green_breaker'):
                    block_surface = self.engine.green_breaker
                elif 'yellow' in clean_type and hasattr(self.engine, 'yellow_breaker'):
                    block_surface = self.engine.yellow_breaker
            elif hasattr(self.engine, 'gray_block'):
                # Use gray block if available
                block_surface = self.engine.gray_block
            
            # If we couldn't find a block surface, create a fallback surface
            if block_surface is None:
                block_surface = pygame.Surface((30, 30))  # Default size
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
                
                # Add breaker marker if needed
                if '_breaker' in block_type:
                    pygame.draw.line(block_surface, (255, 255, 255), (5, 5), (25, 25), 2)
                    pygame.draw.line(block_surface, (255, 255, 255), (25, 5), (5, 25), 2)
            
            # Create detailed breaking animation with particles
            try:
                # Create all required animation attributes
                if not hasattr(self, 'breaking_blocks_animations'):
                    self.breaking_blocks_animations = {}
                if not hasattr(self, 'recently_broken_positions'):
                    self.recently_broken_positions = set()
                if not hasattr(self, 'recent_break_timestamps'):
                    self.recent_break_timestamps = {}
                
                # Initialize breaking animation
                self.breaking_blocks_animations[pos_key] = {
                    'start_time': current_time,
                    'progress': 0.0,
                    'total_duration': self.breaking_animation_duration,
                    'block_type': block_type,
                    'block_surface': block_surface,  # Store the actual surface for consistent animation
                }
                
                # Add particles if possible
                if hasattr(self, 'create_dust_particles'):
                    # Make sure position is valid before creating particles
                    if isinstance(x, (int, float)) and isinstance(y, (int, float)):
                        self.breaking_blocks_animations[pos_key]['particles'] = self.create_dust_particles(x, y, block_color)
                    else:
                        # Empty particles list if coordinates aren't valid
                        self.breaking_blocks_animations[pos_key]['particles'] = []
                else:
                    # Empty particles list if function doesn't exist
                    self.breaking_blocks_animations[pos_key]['particles'] = []
                
                # Add to tracking of broken positions
                self.recently_broken_positions.add(pos_key)
                self.recent_break_timestamps[pos_key] = current_time
            except Exception as e:
                print(f"Error creating breaking animation: {e}")
                # Create minimum viable animation without particles
                self.breaking_blocks_animations[pos_key] = {
                    'start_time': current_time,
                    'progress': 0.0,
                    'total_duration': self.breaking_animation_duration,
                    'block_type': block_type,
                    'block_surface': block_surface,
                    'particles': []
                }
        
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
        """Update animation states with delta-time for frame-rate independence."""
        # Get current time once
        current_time = time.time()
        
        # Only swap buffers at fixed intervals for consistent timing
        if current_time - self.buffer_swap_time >= self.buffer_swap_interval:
            self.current_animation_buffer = self.next_animation_buffer.copy()
            self.buffer_swap_time = current_time
        
        # Update next animation buffer
        # Create a new empty dictionary for the next animation buffer
        self.next_animation_buffer = {}
        
        # Initialize particles_affected_by_gravity if it doesn't exist
        if not hasattr(self, 'particles_affected_by_gravity'):
            self.particles_affected_by_gravity = True
        
        # Update combo text animations
        for combo_text in list(self.combo_texts):
            # Calculate new progress
            elapsed = current_time - combo_text['start_time']
            progress = min(1.0, elapsed / combo_text['duration'])
            
            # If animation is complete, remove it
            if progress >= 1.0:
                self.combo_texts.remove(combo_text)
                continue
            
            # Update progress
            combo_text['progress'] = progress
            
            # Update particle positions if particles exist
            if 'particles' in combo_text:
                # Check if this combo has rainbow mode enabled
                combo_has_rainbow = combo_text.get('rainbow_mode', False)
                
                for particle in combo_text['particles'][:]:
                    # Store previous position for trail effect if needed
                    if self.rainbow_trail_enabled and combo_has_rainbow and particle.get('rainbow', False):
                        if 'trail' not in particle:
                            particle['trail'] = []
                        
                        # Add current position to trail
                        particle['trail'].insert(0, {'x': particle['x'], 'y': particle['y']})
                        
                        # Limit trail length
                        if len(particle['trail']) > self.rainbow_trail_length:
                            particle['trail'].pop()
                    
                    # Update particle position
                    particle['x'] += particle['vx']
                    particle['y'] += particle['vy']
                    
                    # Apply gravity
                    particle['vy'] += 0.05
                    
                    # Reduce particle lifespan
                    particle['life'] -= 0.016  # Assuming ~60fps
                    
                    # Remove dead particles
                    if particle['life'] <= 0:
                        combo_text['particles'].remove(particle)
        
        # Update visual_falling_blocks animations
        removed_falling_blocks = []
        
        for pos, block_data in list(self.visual_falling_blocks.items()):
            # Calculate progress based on elapsed time and duration
            elapsed = current_time - block_data['start_time']
            
            # Make sure duration exists and is valid
            if 'duration' not in block_data or block_data['duration'] <= 0:
                block_data['duration'] = 0.2  # Default duration if missing
                
            progress = min(1.0, elapsed / block_data['duration'])
            
            # Update progress in the data
            block_data['progress'] = progress
            
            # Update visual_y for smooth rendering
            start_y = block_data['start_y'] 
            target_y = block_data['target_y']
            
            # Use easing function for smoother animation
            eased_progress = self._ease_out_quad(progress)
            
            # Calculate interpolated position
            block_data['visual_y'] = start_y + (target_y - start_y) * eased_progress
            
            # Mark for removal if complete
            if progress >= 1.0:
                removed_falling_blocks.append(pos)
        
        # Remove completed animations
        for pos in removed_falling_blocks:
            self.visual_falling_blocks.pop(pos)
            
        # Update breaking block animations
        for pos, block_data in list(self.breaking_blocks_animations.items()):
            # Calculate progress based on elapsed time and duration
            elapsed = current_time - block_data['start_time']
            
            # Get total duration from the animation data
            total_duration = block_data.get('total_duration', 0.5)  # Default to 0.5 seconds
            
            # Make sure duration is valid
            if total_duration <= 0:
                total_duration = 0.5  # Default duration if invalid
                
            progress = min(1.0, elapsed / total_duration)
            
            # Update progress in the data
            block_data['progress'] = progress
            
            # Update particles for this breaking block
            if 'particles' in block_data:
                for particle in block_data['particles'][:]:
                    # Update position
                    particle['x'] += particle['vx'] * 0.016  # Assuming 60fps
                    particle['y'] += particle['vy'] * 0.016
                    
                    # Update life
                    particle['life'] -= 0.016
                    
                    # Remove dead particles (only remove, don't draw here - prevents double rendering)
                    if particle['life'] <= 0:
                        block_data['particles'].remove(particle)
            
            # Remove animation data if complete and all particles are gone
            if progress >= 1.0 and (
                'particles' not in block_data or 
                not block_data['particles']
            ):
                self.breaking_blocks_animations.pop(pos)
        
        # Cap the number of particles to maintain performance
        self._limit_particle_count()
        
        # Update any engine falling animations if we have an engine reference
        if hasattr(self.engine, 'update_gravity_animations'):
            self.engine.update_gravity_animations()
    
    def animate_gravity_movements(self, gravity_movements):
        """
        Create animations for blocks falling due to gravity.
        
        Args:
            gravity_movements: List of movement data with x, start_y, end_y, and block_type
        """
        # Get the current time
        current_time = time.time()
        
        # Initialize visual_falling_blocks if not already
        if not hasattr(self, 'visual_falling_blocks'):
            self.visual_falling_blocks = {}
        
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
        
        # Create animation entries for each movement
        for move in gravity_movements:
            x = move['x']
            start_y = move['start_y']
            end_y = move['end_y']
            block_type = move['block_type']
            
            # Skip animation if this block is in a supported cluster or its target position is
            pos_key = (x, end_y)
            start_key = (x, start_y)
            if pos_key in supported_cluster_positions or start_key in supported_cluster_positions:
                continue
            
            # Only animate if the block moved
            if end_y > start_y:
                # Calculate fall distance
                fall_distance = end_y - start_y
                
                # Skip if we already have an animation in progress for this position
                # that hasn't completed more than 90% of its progress
                if pos_key in self.visual_falling_blocks and self.visual_falling_blocks[pos_key]['progress'] < 0.9:
                    continue
                
                # Still use quadratic easing for all animations
                use_bounce = False
                
                # Calculate duration based on fall distance to maintain consistent speed
                # For a 13-row grid with 1.1 seconds total fall time, each row should take ~0.085 seconds
                duration = fall_distance * 0.085  # 85ms per row of fall
                
                self.visual_falling_blocks[pos_key] = {
                    'start_y': start_y,
                    'target_y': end_y,
                    'progress': 0.0,
                    'start_time': current_time,
                    'block_type': block_type,
                    'duration': duration,
                    'use_bounce': use_bounce,
                    'visual_y': start_y  # Starting visual position
                }
    
    def animations_in_progress(self):
        """Check if there are any animations currently in progress."""
        # Use more strict timing checks to prevent getting stuck
        current_time = time.time()
        
        # Check for falling block animations first
        if hasattr(self, 'visual_falling_blocks') and self.visual_falling_blocks:
            # Apply timeout logic to prevent stuck animations
            valid_animations = False
            
            for pos, block_data in list(self.visual_falling_blocks.items()):
                # More aggressive timeout (1.0 second instead of 1.3)
                if current_time - block_data['start_time'] > 1.0:
                    # Animation has been running too long, remove it
                    self.visual_falling_blocks.pop(pos, None)
                else:
                    valid_animations = True
            
            if valid_animations:
                return True
        
        # Check for breaking animations
        if hasattr(self, 'breaking_blocks_animations') and self.breaking_blocks_animations:
            # Apply timeout logic to prevent stuck animations
            valid_animations = False
            
            for pos, block_data in list(self.breaking_blocks_animations.items()):
                # Use a shorter timeout multiplier (1.2 instead of 1.5)
                if current_time - block_data['start_time'] > block_data['total_duration'] * 1.2:
                    # Animation has been running too long, remove it
                    self.breaking_blocks_animations.pop(pos, None)
                else:
                    valid_animations = True
            
            if valid_animations:
                return True
        
        return False

    def has_falling_animations(self):
        """Check if there are any falling block animations currently in progress."""
        # Check for falling block animations
        if hasattr(self, 'visual_falling_blocks') and self.visual_falling_blocks:
            # Apply timeout logic to prevent stuck animations
            current_time = time.time()
            valid_animations = False
            
            for pos, block_data in list(self.visual_falling_blocks.items()):
                if current_time - block_data['start_time'] > 1.3:  # 1.3 second timeout (slightly longer than max fall time)
                    # Animation has been running too long, remove it
                    self.visual_falling_blocks.pop(pos, None)
                else:
                    valid_animations = True
                    
            return valid_animations
        return False

    def has_breaking_animations(self):
        """Check if there are any breaking block animations currently in progress."""
        # Actually check for breaking animations
        if hasattr(self, 'breaking_blocks_animations') and self.breaking_blocks_animations:
            current_time = time.time()
            valid_animations = False
            
            for pos, block_data in list(self.breaking_blocks_animations.items()):
                if current_time - block_data['start_time'] > block_data['total_duration'] * 1.2:
                    # Animation has been running too long, remove it
                    self.breaking_blocks_animations.pop(pos, None)
                else:
                    valid_animations = True
            
            return valid_animations
        return False
    
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
                    particle_key = f"combo_{color[0]}_{color[1]}_{color[2]}_{particle_size}_{particle_alpha}"
                    
                    # Use cached surface or create new one
                    if particle_key not in self.particle_surfaces:
                        particle_surf = pygame.Surface((particle_size*2, particle_size*2), pygame.SRCALPHA)
                        pygame.draw.circle(particle_surf, (*color, particle_alpha), 
                                        (particle_size, particle_size), particle_size)
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
        max_particles = 300  # Maximum allowed particles system-wide
        
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