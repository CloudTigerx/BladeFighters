import pygame
import sys
import os
import math
import random
import time
import inspect
import json
from enum import Enum, auto

# Global variable to fix error
update_regions = []

# Define block types
class BlockType(Enum):
    EMPTY = auto()
    RED = auto()
    BLUE = auto()
    GREEN = auto()
    YELLOW = auto()

class PuzzleEngine:
    """
    Puzzle game engine for the Blade Fighters game.
    This module handles the puzzle game mechanics and rendering.
    """
    def __init__(self, screen, font, audio=None, asset_path="puzzleassets"):
        """
        Initialize the puzzle engine.
        
        Args:
            screen: Pygame display surface
            font: Pygame font for text rendering
            audio: Audio system for sound effects (optional)
            asset_path: Path to puzzle assets directory
        """
        self.screen = screen
        self.font = font
        self.audio = audio
        self.asset_path = asset_path
        
        # Get screen dimensions
        self.width = screen.get_width()
        self.height = screen.get_height()
        
        # Grid dimensions
        self.grid_width = 6
        self.grid_height = 15  # Increased visible grid height
        self.total_grid_height = 16  # Including invisible row
        self.block_size = 65  # Increased by 5px
        
        # Game state variables
        self.game_active = False
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GRAY = (100, 100, 100)
        self.LIGHT_GRAY = (200, 200, 200)
        self.BLUE = (0, 100, 255)
        self.LIGHT_BLUE = (100, 150, 255)
        self.DARK_GRAY = (50, 50, 50)
        
        # Load background images
        try:
            self.puzzle_background = pygame.image.load(os.path.join(asset_path, "puzzlebackground.jpg"))
            # Scale the background to match the grid size
            grid_width_pixels = self.grid_width * self.block_size
            grid_height_pixels = self.grid_height * self.block_size
            self.puzzle_background = pygame.transform.scale(self.puzzle_background, (grid_width_pixels, grid_height_pixels))
            print("Loaded puzzle background image")
        except pygame.error as e:
            print(f"Could not load puzzle background image: {e}. Using solid color instead.")
            self.puzzle_background = None
        
        # Load puzzle pieces
        self.puzzle_pieces = {}
        
        # Load standard block types
        self.red_block = self.load_block("redblock.png")
        self.blue_block = self.load_block("blueblock.png")
        self.green_block = self.load_block("greenblock.png")
        self.yellow_block = self.load_block("yellowblock.png")
        
        # Load gray block for garbage blocks
        self.gray_block = self.load_block("grayblock.png")
        
        # Load strike block
        self.strike_block = self.load_block("strikes/1x4.png")
        
        # Load breaker blocks
        self.red_breaker = self.load_block("redbreaker.png", "redblock.png", True)
        self.blue_breaker = self.load_block("bluebreaker.png", "blueblock.png", True)
        self.green_breaker = self.load_block("greenbreaker.png", "greenblock.png", True)
        self.yellow_breaker = self.load_block("yellowbreaker.png", "yellowblock.png", True)
        
        # Initialize the puzzle grid
        self.puzzle_grid = self.create_empty_grid(self.grid_width, self.total_grid_height)
        
        # Falling piece properties
        self.main_piece = None
        self.attached_piece = None
        self.piece_position = [0, 0]  # [x, y] in grid coordinates
        self.attached_position = 0  # 0: top, 1: right, 2: bottom, 3: left
        
        # Add sub-grid positioning for smoother movement
        self.sub_grid_positions = 20  # Doubled from 5 to 10 for smoother animation
        self.current_sub_position = 0  # Current sub-position (0 to sub_grid_positions-1)
        
        # Piece fall timing
        self.normal_fall_speed = 64000  # my speeds
        self.accelerated_fall_speed = 3600  # my speeds
        self.current_fall_speed = self.normal_fall_speed
        self.last_fall_time = 0
        self.micro_fall_time = self._calculate_micro_fall_time(self.current_fall_speed)
        self.last_wall_kick_time = 0
        self.wall_kick_cooldown = 500  # ms cooldown for wall kicks
        self.wall_kick_count = 0
        self.max_wall_kicks = 2  # Maximum number of consecutive wall kicks allowed
        
        # Flip cooldown
        self.last_flip_time = 0
        self.flip_cooldown = 50  # ms cooldown between flip attempts
        
        # Piece generation
        self.next_main_piece = None
        self.next_attached_piece = None
        self.piece_types = ['red', 'blue', 'green', 'yellow', 
                           'red_breaker', 'blue_breaker', 'green_breaker', 'yellow_breaker']
        
        # Game state tracking
        self.clusters = set()  # Tracks positions of blocks in clusters
        self.breaking_blocks = []  # Tracks blocks currently being destroyed
        self.breaking_animation_start = 0
        self.breaking_animation_duration = 300  # 300ms (0.3s) for breaking animations - longer for more dramatic effects
        
        # Chain reaction state machine
        self.chain_reaction_in_progress = False
        self.chain_state = "idle"  # States: idle, breaking, waiting_for_breaking, applying_gravity, waiting_for_gravity
        self.last_state_change = 0
        self.state_delay = 50  # ms between state transitions (reduced for smoother combos)
        self.chain_count = 0  # Track consecutive chain reactions
        
        self.chain_delay = 30
        self.last_cluster_check_time = 0
        self.cluster_check_interval = 250
        
        # Key tracking for movement
        self.keys_pressed = {}
        self.key_repeat_delay = 120  # ms before the first repeat
        self.key_repeat_interval = 80  # ms between repeats after the first one
        self.last_key_action_time = {}
        
        # Game buttons for back button etc.
        self.game_buttons = []
        
        # Fixed colors for blocks
        self.particle_colors = {
            'red': (255, 0, 0),
            'blue': (0, 0, 255),
            'green': (0, 255, 0),
            'yellow': (255, 255, 0),
            'white': (255, 255, 255)
        }
        
        # Create a larger font for titles and game over text
        try:
            self.large_font = pygame.font.Font(None, 64)
        except:
            self.large_font = self.font
            
        # Calculate grid placement
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        self.grid_offset_x = 0  # Align grid to the left edge
        self.grid_offset_y = (screen_height - (self.grid_height * self.block_size)) // 3
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.cell_size = self.block_size
        
    def load_block(self, filename, fallback_filename=None, is_breaker=False):
        """Load and scale a block image."""
        try:
            image_path = os.path.join(self.asset_path, filename)
            if os.path.exists(image_path):
                original_img = pygame.image.load(image_path)
                # Scale down to appropriate size for game
                return pygame.transform.scale(original_img, (self.block_size, self.block_size))
            elif fallback_filename:
                # Try fallback file
                fallback_path = os.path.join(self.asset_path, fallback_filename)
                if os.path.exists(fallback_path):
                    original_img = pygame.image.load(fallback_path)
                    scaled_img = pygame.transform.scale(original_img, (self.block_size, self.block_size))
                    
                    if is_breaker:
                        # Add an X to indicate it's a breaker
                        pygame.draw.line(scaled_img, self.WHITE, (5, 5), 
                                       (self.block_size - 5, self.block_size - 5), 3)
                        pygame.draw.line(scaled_img, self.WHITE, (self.block_size - 5, 5), 
                                       (5, self.block_size - 5), 3)
                    
                    return scaled_img
        except pygame.error:
            pass
        
        # Remove fallback to colored rectangles
        raise ValueError(f"Could not load block image: {filename}")
    
    def create_empty_grid(self, width, height):
        """Create an empty grid with None values."""
        return [[None for _ in range(width)] for _ in range(height)]  # Use the height parameter
    
    def create_test_grid(self, width, height):
        """Create a test grid with random colors and breakers."""
        # Regular colors and breaker colors (for better distribution)
        regular_colors = ['red', 'blue', 'green', 'yellow']
        breaker_colors = ['red_breaker', 'blue_breaker', 'green_breaker', 'yellow_breaker']
        
        grid = []
        for y in range(height):
            row = []
            for x in range(width):
                # 25% chance of spawning a breaker block
                if random.random() < 0.25:
                    # Choose a random breaker color
                    piece = random.choice(breaker_colors)
                else:
                    # Choose a random regular color
                    piece = random.choice(regular_colors)
                row.append(piece)
            grid.append(row)
        return grid
        
    def get_glow_color(self):
        """Return a fixed color for glow effects."""
        return (180, 60, 220)  # Medium Purple
        
    # Core game mechanics methods
    
    def start_game(self):
        """Start a new puzzle game."""
        self.game_active = True
        self.puzzle_grid = self.create_empty_grid(self.grid_width, self.total_grid_height)
        self.generate_new_piece()
        # Reset game state
        self.chain_reaction_in_progress = False
        self.breaking_blocks = []
        self.clusters = set()
        
    def would_fit_below(self):
        """
        Check if the piece would fit in the position below its current position.
        Takes into account the current micro-position to prevent visual phasing.
        """
        # Get current positions
        main_x, main_y = self.piece_position
        attached_x, attached_y = self.get_attached_position_coords()
        
        # Get current clusters for collision checking
        cluster_positions = self.detect_clusters()  # This returns a set of positions
        
        # Always check for collision regardless of micro-position
        # This prevents any clipping through pieces or the bottom
        
        # Check for bottom boundary collision
        if main_y + 1 >= self.grid_height or attached_y + 1 >= self.grid_height:
            return False  # Would be out of bounds
        
        # Check for cluster collisions
        if ((main_x, main_y + 1) in cluster_positions or 
            (attached_x, attached_y + 1) in cluster_positions):
            return False
            
        # Check for collision with placed blocks - handle negative Y values properly
        if (main_y + 1 >= 0 and main_x >= 0 and main_x < self.grid_width and 
            self.puzzle_grid[main_y + 1][main_x] is not None):
            return False  # Would collide with a block below
            
        if (attached_y + 1 >= 0 and attached_x >= 0 and attached_x < self.grid_width and 
            self.puzzle_grid[attached_y + 1][attached_x] is not None):
            return False  # Would collide with a block below for attached piece
        
        # Regular validity check to ensure both pieces can fit
        return (self.is_valid_position(main_x, main_y + 1) and 
                self.is_valid_position(attached_x, attached_y + 1))
    
    def update_falling_piece(self):
        """Update the position of the falling piece based on time, using micro-movements."""
        # If there's an ongoing chain reaction, process that first before doing anything else
        if self.chain_reaction_in_progress:
            self.activate_breaker_blocks()
            return  # Don't generate new piece or update falling until chain reaction is done
        
        # Make sure all animations are complete before generating a new piece
        animation_wait = False
        if hasattr(self, 'renderer') and self.renderer.animations_in_progress():
            animation_wait = True
            
            # FAILSAFE: Check if animations are potentially stuck
            if not self.main_piece and hasattr(self, 'last_animation_wait_time'):
                current_time = pygame.time.get_ticks()
                # If we've been waiting more than 2 seconds for animations with no piece, force a new piece
                if current_time - self.last_animation_wait_time > 2000:
                    animation_wait = False  # Override animation wait
                    # Log this event if possible
                    if hasattr(self, 'logger') and self.logger:
                        self.logger.warning("FAILSAFE: Forced piece generation due to stuck animations")
            
            # Update or initialize the animation wait timestamp
            if not hasattr(self, 'last_animation_wait_time'):
                self.last_animation_wait_time = pygame.time.get_ticks()
            
            # If still waiting, return
            if animation_wait:
                return  # Wait for animations to complete
        else:
            # Reset the animation wait time since animations are complete
            if hasattr(self, 'last_animation_wait_time'):
                del self.last_animation_wait_time
            
        # Only generate new piece if we don't have one and there's no chain reaction
        if not self.main_piece:
            self.generate_new_piece()
            
            # Set a timestamp for when the piece was generated to detect stalls
            self.piece_generation_time = pygame.time.get_ticks()
            return
        
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.last_fall_time
        
        # STALL DETECTION: If a piece exists but hasn't moved from its starting position for too long
        if hasattr(self, 'piece_generation_time') and self.piece_position[1] <= -1:
            stall_time = current_time - self.piece_generation_time
            if stall_time > 500:  # Reduced from 1000ms to 500ms for faster response at top edge
                # Force the piece to start falling by advancing its position
                self.current_sub_position = 0
                self.piece_position[1] = 0
                self.last_fall_time = current_time
                # Log this if possible
                if hasattr(self, 'logger') and self.logger:
                    self.logger.warning(f"STALL DETECTED: Piece was stuck at top for {stall_time}ms, forcing movement")
        
        # Get current positions
        main_x, main_y = self.piece_position
        attached_x, attached_y = self.get_attached_position_coords()
        
        # Check if we can move down - do this outside the loop 
        # so it's available for the check at the end of this function
        can_move_down = self.would_fit_below()
        
        # For very fast fall speeds, allow multiple movements in a single frame
        # This ensures temporal smoothness by maintaining correct movement speed
        max_steps = 1
        if self.micro_fall_time < 10:  # Very fast fall speed
            max_steps = min(10, elapsed // max(1, self.micro_fall_time))
        
        # Process movement multiple times if needed for fast fall speeds
        steps_taken = 0
        while elapsed > self.micro_fall_time and steps_taken < max_steps:
            # We already checked if we can move down before entering the loop
            
            # Update the micro-position
            next_sub_position = self.current_sub_position + 1
            
            # If we've reached the next grid cell
            if next_sub_position >= self.sub_grid_positions:
                if can_move_down:
                    # Move to the next grid cell
                    self.current_sub_position = 0
                    self.piece_position[1] += 1
                    # Update can_move_down for next iteration
                    can_move_down = self.would_fit_below()
                else:
                    # We can't move down, place the piece
                    self.place_piece_on_grid()
                    return  # Exit after placing piece
            else:
                # Check for potential collisions with the buffer
                next_main_visual_y = main_y + (next_sub_position / self.sub_grid_positions)
                next_attached_visual_y = attached_y + (next_sub_position / self.sub_grid_positions)
                
                # Calculate the visual "buffer" - how close we can get to an occupied cell
                # This prevents any visual overlap
                buffer_cells = 0.1  # Small buffer to prevent phasing
                
                # Check for potential collisions with the buffer
                main_would_collide = (math.ceil(next_main_visual_y + buffer_cells) < self.total_grid_height and 
                                     math.ceil(next_main_visual_y + buffer_cells) >= 0 and
                                     self.puzzle_grid[math.ceil(next_main_visual_y + buffer_cells)][main_x] is not None)
                                     
                attached_would_collide = (math.ceil(next_attached_visual_y + buffer_cells) < self.total_grid_height and 
                                         math.ceil(next_attached_visual_y + buffer_cells) >= 0 and
                                         attached_x >= 0 and attached_x < self.grid_width and
                                         self.puzzle_grid[math.ceil(next_attached_visual_y + buffer_cells)][attached_x] is not None)
                
                if main_would_collide or attached_would_collide or not can_move_down:
                    # We're about to visually collide, place the piece now
                    self.place_piece_on_grid()
                    return  # Exit after placing piece
                else:
                    # Safe to update the sub-position
                    self.current_sub_position = next_sub_position
            
            # Update elapsed time to account for the time used
            elapsed -= self.micro_fall_time
            steps_taken += 1
        
        # Only update last_fall_time if we made at least one step
        if steps_taken > 0:
            self.last_fall_time = current_time - elapsed  # Account for any remaining time
        
        # Additional check for pieces near the top of the board
        # If the piece is at the top and we're trying to move but can't, force placement
        if ((main_y <= 0 or attached_y <= 0) and 
            not can_move_down and steps_taken == 0 and 
            current_time - self.last_fall_time > 250):  # Add a small timeout to prevent immediate placement
            self.place_piece_on_grid()
            return
    
    def get_visual_position(self):
        """Get the visual position of the piece, including sub-grid positioning."""
        x, y = self.piece_position
        
        # Calculate smooth y-position using sub-grid position
        smooth_y = y + (self.current_sub_position / self.sub_grid_positions)
        
        return [x, smooth_y]
    
    def place_piece_on_grid(self):
        """Place the falling piece onto the grid."""
        # Reset sub-position when placing
        self.current_sub_position = 0
        
        # Get positions
        main_x, main_y = self.piece_position
        attached_x, attached_y = self.get_attached_position_coords()
        
        # Store pieces that need to be placed
        pieces_to_place = []
        
        # Handle main piece placement
        if 0 <= main_y < self.grid_height and 0 <= main_x < self.grid_width:
            pieces_to_place.append((main_x, main_y, self.main_piece))
        # Handle pieces at the top edge that are partially visible
        elif main_y == -1 and 0 <= main_x < self.grid_width:
            # If we're at the top edge, force the piece to be placed in row 0
            pieces_to_place.append((main_x, 0, self.main_piece))
        
        # Handle attached piece placement
        if 0 <= attached_y < self.grid_height and 0 <= attached_x < self.grid_width:
            pieces_to_place.append((attached_x, attached_y, self.attached_piece))
        # Handle attached piece at top edge
        elif attached_y == -1 and 0 <= attached_x < self.grid_width:
            # Force attached piece to be placed in row 0
            pieces_to_place.append((attached_x, 0, self.attached_piece))
        
        # Determine which piece has priority when they would occupy the same position
        # This happens when both pieces would be placed in row 0
        unique_positions = {}
        
        # Place pieces in order of priority
        for x, y, piece in pieces_to_place:
            # If this position is already taken, skip it
            if (x, y) in unique_positions:
                continue
                
            # Place the piece
            self.puzzle_grid[y][x] = piece
            unique_positions[(x, y)] = piece
            
            # Play the placed sound when a piece is placed
            if self.audio:
                self.audio.play_sound("placed")
        
        # Apply gravity to make pieces fall into empty spaces
        gravity_applied = self.apply_gravity()
        
        # Trigger garbage block state transitions if we have an attack system reference
        # Check if we have access to the attack system through test_mode
        if hasattr(self, 'test_mode') and hasattr(self.test_mode, 'attack_system'):
            # Determine which player's grid this is (1 or 2)
            player_number = 1
            if hasattr(self.test_mode, 'player_engine') and self.test_mode.player_engine != self:
                player_number = 2
            
            # Decrement turns for garbage blocks when a piece is placed
            updated_blocks = self.test_mode.attack_system.decrement_garbage_block_turns(player_number)
            
            # Update any transformed blocks
            if updated_blocks:
                for (x, y), color in updated_blocks:
                    if 0 <= y < self.grid_height and 0 <= x < self.grid_width:
                        # Update the block to its normal color
                        self.puzzle_grid[y][x] = color
        
        # Always start the chain reaction process
        self.chain_reaction_in_progress = True
        self.chain_count = 0  # Reset chain counter when starting a new chain reaction
        
        # Choose appropriate state based on gravity status
        if gravity_applied and hasattr(self, 'renderer') and self.renderer.animations_in_progress():
            # If gravity was applied and there are animations, wait for them to complete
            self.chain_state = "waiting_for_gravity"
            self.last_state_change = pygame.time.get_ticks()
        else:
            # Otherwise just activate breaker blocks directly
            self.chain_state = "idle"
            self.update_chain_reaction()
        
        # Clear the current piece (but don't generate a new one yet - will happen in update_falling_piece)
        self.main_piece = None
        self.attached_piece = None
    
    def apply_gravity(self):
        """Apply gravity to make pieces fall into empty spaces."""
        blocks_moved = False
        
        # Track garbage block movements
        garbage_movements = {}  # (old_x, old_y) -> (new_x, new_y)
        
        # First, check for any blocks in row 0 that need to fall
        for x in range(self.grid_width):
            if self.puzzle_grid[0][x] is not None:
                # Find how far this block can fall
                fall_distance = 0
                for check_y in range(1, self.grid_height):
                    if self.puzzle_grid[check_y][x] is None:
                        fall_distance += 1
                    else:
                        break
                
                if fall_distance > 0:
                    # Move the block down
                    new_y = fall_distance
                    self.puzzle_grid[new_y][x] = self.puzzle_grid[0][x]
                    self.puzzle_grid[0][x] = None
                    blocks_moved = True
                    
                    # If this is a garbage block, track its movement
                    if '_garbage' in self.puzzle_grid[new_y][x]:
                        garbage_movements[(x, 0)] = (x, new_y)
        
        # Then apply gravity to the rest of the grid from bottom to top
        for y in range(self.grid_height - 2, 0, -1):  # Start from second-to-last row
            for x in range(self.grid_width):
                if self.puzzle_grid[y][x] is not None:
                    # Check if there's an empty space below
                    fall_distance = 0
                    for check_y in range(y + 1, self.grid_height):
                        if self.puzzle_grid[check_y][x] is None:
                            fall_distance += 1
                        else:
                            break
                    
                    if fall_distance > 0:
                        # Move the block down
                        new_y = y + fall_distance
                        self.puzzle_grid[new_y][x] = self.puzzle_grid[y][x]
                        self.puzzle_grid[y][x] = None
                        blocks_moved = True
                        
                        # If this is a garbage block, track its movement
                        if '_garbage' in self.puzzle_grid[new_y][x]:
                            garbage_movements[(x, y)] = (x, new_y)
        
        # Update garbage block positions in the attack system
        if blocks_moved and hasattr(self, 'test_mode') and hasattr(self.test_mode, 'attack_system'):
            attack_system = self.test_mode.attack_system
            
            # Create a new dictionary for updated positions
            updated_garbage_blocks = {}
            
            # Update positions of garbage blocks
            for old_pos, (start_time, color) in list(attack_system.garbage_blocks.items()):
                old_x, old_y = old_pos
                if (old_x, old_y) in garbage_movements:
                    new_x, new_y = garbage_movements[(old_x, old_y)]
                    updated_garbage_blocks[(new_x, new_y)] = (start_time, color)
                else:
                    updated_garbage_blocks[old_pos] = (start_time, color)
            
            # Replace the old dictionary with the updated one
            attack_system.garbage_blocks = updated_garbage_blocks
            
        return blocks_moved
    
    def generate_new_piece(self):
        """Generate a new main and attached piece."""
        # Check for game over condition - if column 4 is filled up to the invisible row
        # Only check column 4 (index 3) for game over
        if self.puzzle_grid[0][3] is not None:
            print(f"Game Over: Column 4 has reached the invisible row")
            self.game_active = False
            return False

        # Use the pre-generated pieces if available
        if self.next_main_piece and self.next_attached_piece:
            self.main_piece = self.next_main_piece
            self.attached_piece = self.next_attached_piece
        else:
            # Generate random pieces
            self.main_piece = self.generate_random_piece()
            self.attached_piece = self.generate_random_piece()
        
        # Generate the next pieces
        self.next_main_piece = self.generate_random_piece()
        self.next_attached_piece = self.generate_random_piece()
        
        # Set starting position (middle column, just above the grid)
        self.piece_position = [self.grid_width // 2, -1]  # Start at -1 for smoother entry
        
        # Initialize sub-position properly - ensure this is a float value
        self.current_sub_position = float(self.sub_grid_positions * 0.3)  # 30% into sub-position

        # Set the attached piece to top orientation
        self.attached_position = 0
        
        # Always start with normal fall speed
        self.current_fall_speed = self.normal_fall_speed
        self.micro_fall_time = self._calculate_micro_fall_time(self.current_fall_speed)
        
        # Ensure fall timing is properly initialized
        self.last_fall_time = pygame.time.get_ticks()
        
        # For detecting stalls
        self.piece_generation_time = pygame.time.get_ticks()
        
        # Clear any stuck visual state in the renderer if available
        if hasattr(self, 'renderer'):
            self.renderer.update_visual_state()
        
        # Clear spacebar from pressed keys to require a new press
        if pygame.K_SPACE in self.keys_pressed:
            del self.keys_pressed[pygame.K_SPACE]
        if pygame.K_SPACE in self.last_key_action_time:
            del self.last_key_action_time[pygame.K_SPACE]
            
        return True
    
    def generate_random_piece(self):
        """Generate a random piece, with 25% chance of being a breaker."""
        if random.random() < 0.25:
            # Generate a breaker piece
            color = random.choice(['red', 'blue', 'green', 'yellow'])
            return f"{color}_breaker"
        else:
            # Generate a regular piece
            return random.choice(['red', 'blue', 'green', 'yellow'])
            
    def get_attached_position_coords(self):
        """Get the grid coordinates of the attached piece based on its position."""
        x, y = self.piece_position
        
        if self.attached_position == 0:  # Top
            return [x, y - 1]
        elif self.attached_position == 1:  # Right
            return [x + 1, y]
        elif self.attached_position == 2:  # Bottom
            return [x, y + 1]
        elif self.attached_position == 3:  # Left
            return [x - 1, y]
    
    def is_valid_position(self, x, y):
        """Check if a position is valid (within grid and not occupied)."""
        # Out of bounds check
        if x < 0 or x >= self.grid_width or y >= self.total_grid_height:
            return False
        
        # If above the grid, it's valid
        if y < 0:
            return True
        
        # Check if the space is already occupied
        return self.puzzle_grid[y][x] is None
    
    def move_piece(self, dx, dy):
        """Attempt to move the piece by the given delta."""
        # Calculate new position
        new_x = self.piece_position[0] + dx
        new_y = self.piece_position[1] + dy
        
        # Get attached piece coordinates for new position
        attached_x = new_x
        attached_y = new_y
        
        if self.attached_position == 0:  # Top
            attached_y -= 1
        elif self.attached_position == 1:  # Right
            attached_x += 1
        elif self.attached_position == 2:  # Bottom
            attached_y += 1
        elif self.attached_position == 3:  # Left
            attached_x -= 1
        
        # Check if the new position is valid for both pieces
        if self.is_valid_position(new_x, new_y) and self.is_valid_position(attached_x, attached_y):
            self.piece_position = [new_x, new_y]
            return True
        
        return False
        
    def rotate_attached_piece(self, direction):
        """
        Rotate the attached piece around the main piece.
        Allows for wall kicks when at edge of board or next to towers of blocks.
        Direction: -1 for counter-clockwise, 1 for clockwise
        """
        # Calculate new position (0: top, 1: right, 2: bottom, 3: left)
        new_position = (self.attached_position + direction) % 4
        
        # Get current piece coordinates
        main_x, main_y = self.piece_position
        
        # For edge cases (outside columns)
        is_left_edge = (main_x == 0)
        is_right_edge = (main_x == self.grid_width - 1)
        
        # Standard position checks with omni movement support
        valid_position = False
        
        # Calculate the position where the attached piece would be after rotation
        attached_x, attached_y = main_x, main_y
        if new_position == 0:  # Top
            attached_y -= 1
        elif new_position == 1:  # Right
            attached_x += 1
        elif new_position == 2:  # Bottom
            attached_y += 1
        elif new_position == 3:  # Left
            attached_x -= 1
        
        # Check if this position is valid
        valid_position = self.is_valid_position(attached_x, attached_y)
        
        # Apply the rotation if valid
        if valid_position:
            self.attached_position = new_position
            # Reset wall kick count when normal rotation occurs
            self.wall_kick_count = 0
            return True
        
        # Check if we've exceeded wall kick limits
        current_time = pygame.time.get_ticks()
        if self.wall_kick_count >= self.max_wall_kicks and current_time - self.last_wall_kick_time < self.wall_kick_cooldown:
            return False
        
        # Wall kick logic - try to move the piece to make room for rotation
        # NEW: This now handles both board edges and towers of blocks
        
        # Trying to rotate to right position (but blocked)
        if new_position == 1:
            # Try moving left to make room
            if self.is_valid_position(main_x - 1, main_y) and self.is_valid_position(main_x - 1 + 1, main_y):
                # Move main piece left
                self.piece_position[0] -= 1
                # Set attached to right
                self.attached_position = 1
                
                # Update wall kick tracking
                self.wall_kick_count += 1
                self.last_wall_kick_time = current_time
                
                return True
        
        # Trying to rotate to left position (but blocked)
        elif new_position == 3:
            # Try moving right to make room
            if self.is_valid_position(main_x + 1, main_y) and self.is_valid_position(main_x + 1 - 1, main_y):
                # Move main piece right
                self.piece_position[0] += 1
                # Set attached to left
                self.attached_position = 3
                
                # Update wall kick tracking
                self.wall_kick_count += 1
                self.last_wall_kick_time = current_time
                
                return True
        
        # Trying to rotate to top position (but blocked)
        elif new_position == 0:
            # Try moving down to make room (if not at bottom)
            if main_y + 1 < self.grid_height and self.is_valid_position(main_x, main_y + 1) and self.is_valid_position(main_x, main_y + 1 - 1):
                # Move main piece down
                self.piece_position[1] += 1
                # Set attached to top
                self.attached_position = 0
                
                # Update wall kick tracking
                self.wall_kick_count += 1
                self.last_wall_kick_time = current_time
                
                return True
        
        # Trying to rotate to bottom position (but blocked)
        elif new_position == 2:
            # Try moving up to make room (if not at top)
            if main_y > 0 and self.is_valid_position(main_x, main_y - 1) and self.is_valid_position(main_x, main_y - 1 + 1):
                # Move main piece up
                self.piece_position[1] -= 1
                # Set attached to bottom
                self.attached_position = 2
                
                # Update wall kick tracking
                self.wall_kick_count += 1
                self.last_wall_kick_time = current_time
                
                return True
        
        return False
    
    def flip_pieces_vertically(self):
        """
        Flip the main and attached pieces vertically if they're in a valid position
        for flipping (between towers or at board edge).
        Returns True if the flip was successful, False otherwise.
        """
        # Check if on cooldown
        current_time = pygame.time.get_ticks()
        if current_time - self.last_flip_time < self.flip_cooldown:
            return False
            
        # Get current positions
        main_x, main_y = self.piece_position
        attached_x, attached_y = self.get_attached_position_coords()
        
        # Track if the flip was successful
        flip_successful = False
        
        # Simple vertical flipping logic - only for vertical pieces
        if self.attached_position == 0:  # Attached is above
            # Flip to attached below if valid
            if self.is_valid_position(main_x, main_y) and self.is_valid_position(main_x, main_y + 1):
                self.attached_position = 2  # Set to below
                flip_successful = True
        elif self.attached_position == 2:  # Attached is below
            # Flip to attached above if valid
            if self.is_valid_position(main_x, main_y) and self.is_valid_position(main_x, main_y - 1):
                self.attached_position = 0  # Set to above
                flip_successful = True
        
        # Only update cooldown and reset wall kick tracking if flip was successful
        if flip_successful:
            # Reset wall kick tracking when flipping
            self.wall_kick_count = 0
            
            # Update the cooldown timer
            self.last_flip_time = current_time
            
        return flip_successful
    
    def can_flip_vertically(self):
        """
        Check if the pieces are in a valid position for vertical flipping.
        Allows flipping when falling between columns or when wedged between obstacles.
        """
        # This method is not needed anymore since we've simplified the
        # vertical flipping logic in the flip_pieces_vertically method
        # to only handle vertical pieces.
        return False
    
    def detect_clusters(self):
        """
        Detect clusters of blocks that are 2+ blocks wide and 2+ blocks high.
        Returns a set of (x, y) coordinates of blocks in clusters.
        """
        # Performance optimization - use a more efficient algorithm
        clusters = set()
        visited = set()
        
        # Go through each cell in the grid
        for y in range(self.total_grid_height):
            for x in range(self.grid_width):
                # Skip if already visited or if empty
                if (x, y) in visited or self.puzzle_grid[y][x] is None:
                    continue
                
                # Get the color of the current block
                current_color = self.puzzle_grid[y][x].split('_')[0]
                
                # Check for minimum 2x2 cluster at this position
                if (x + 1 < self.grid_width and 
                    y + 1 < self.total_grid_height and
                    self.puzzle_grid[y][x+1] is not None and
                    self.puzzle_grid[y+1][x] is not None and
                    self.puzzle_grid[y+1][x+1] is not None):
                    
                    # Check if all are the same color
                    if (self.puzzle_grid[y][x+1].split('_')[0] == current_color and
                        self.puzzle_grid[y+1][x].split('_')[0] == current_color and
                        self.puzzle_grid[y+1][x+1].split('_')[0] == current_color):
                        
                        # We've found a 2x2 cluster of the same color
                        clusters.add((x, y))
                        clusters.add((x+1, y))
                        clusters.add((x, y+1))
                        clusters.add((x+1, y+1))
                        
                        # Mark all as visited
                        visited.add((x, y))
                        visited.add((x+1, y))
                        visited.add((x, y+1))
                        visited.add((x+1, y+1))
                        
                        # Try to extend the cluster if possible (but limit to avoid excessive computation)
                        self._extend_cluster(clusters, visited, x, y, current_color, 5, 5)
        
        return clusters
    
    def _extend_cluster(self, clusters, visited, start_x, start_y, color, max_width, max_height):
        """Helper method to extend clusters efficiently with size limits"""
        # Find how far right and down we can extend
        width = 2  # Already verified 2x2
        height = 2
        
        # Try to extend right
        for x in range(start_x + 2, min(start_x + max_width, self.grid_width)):
            # Check if entire column has same color
            valid_column = True
            for y in range(start_y, min(start_y + height, self.total_grid_height)):
                if (y >= self.total_grid_height or 
                    self.puzzle_grid[y][x] is None or
                    self.puzzle_grid[y][x].split('_')[0] != color):
                    valid_column = False
                    break
            
            if valid_column:
                # Add all blocks in this column to the cluster
                for y in range(start_y, start_y + height):
                    clusters.add((x, y))
                    visited.add((x, y))
                width += 1
            else:
                break
                
        # Try to extend down
        for y in range(start_y + 2, min(start_y + max_height, self.total_grid_height)):
            # Check if entire row has same color
            valid_row = True
            for x in range(start_x, start_x + width):
                if (x >= self.grid_width or 
                    self.puzzle_grid[y][x] is None or
                    self.puzzle_grid[y][x].split('_')[0] != color):
                    valid_row = False
                    break
            
            if valid_row:
                # Add all blocks in this row to the cluster
                for x in range(start_x, start_x + width):
                    clusters.add((x, y))
                    visited.add((x, y))
                height += 1
            else:
                break
    
    def is_cluster_supported(self, cluster_blocks):
        """
        Check if a cluster has any support beneath it.
        A cluster is supported if any block in its bottom row has a non-cluster block below it.
        
        Args:
            cluster_blocks: Set of (x, y) coordinates that form the cluster
            
        Returns:
            bool: True if the cluster is supported, False otherwise
        """
        # First identify the bottom row of blocks in the cluster
        if not cluster_blocks:
            return True  # Empty clusters are trivially supported
            
        # Group blocks by x-coordinate
        columns = {}
        for x, y in cluster_blocks:
            if x not in columns:
                columns[x] = []
            columns[x].append(y)
        
        # For each column in the cluster, check if the bottom-most block has direct support
        for x, y_values in columns.items():
            # Find the bottom-most block in this column
            bottom_y = max(y_values)
            
            # Skip if at the bottom of the grid (already supported)
            if bottom_y >= self.grid_height - 1:
                continue  # This column is supported, but others might not be
            
            # Check if there's a block directly below that's not part of the cluster
            below_pos = (x, bottom_y + 1)
            if below_pos not in cluster and self.puzzle_grid[bottom_y + 1][x] is not None:
                continue  # This column has support, check others
            else:
                # This column has no support - the cluster can fall in this column
                return False
        
        # All columns have direct support - the cluster is fully supported
        return True
    
    def find_all_clusters(self):
        """
        Find all clusters in the grid and return them as separate groups.
        
        Returns:
            list: A list of sets, where each set contains the (x, y) coordinates of a cluster
        """
        # Get all cluster blocks
        all_cluster_blocks = self.detect_clusters()
        
        # If no clusters, return empty list
        if not all_cluster_blocks:
            return []
        
        # Group clusters by connectivity
        clusters = []
        visited = set()
        
        for x, y in all_cluster_blocks:
            if (x, y) in visited:
                continue
                
            # Start a new cluster
            if self.puzzle_grid[y][x] is None:
                continue
                
            color = self.puzzle_grid[y][x].split('_')[0]
            current_cluster = set()
            
            # Use a flood-fill approach to find all connected blocks of the same color
            queue = [(x, y)]
            cluster_visited = set(queue)
            
            while queue:
                cx, cy = queue.pop(0)
                if (cx, cy) in all_cluster_blocks:  # Only include blocks that are in clusters
                    current_cluster.add((cx, cy))
                    
                    # Check adjacent positions
                    for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:  # Up, right, down, left
                        nx, ny = cx + dx, cy + dy
                        
                        if ((nx, ny) not in cluster_visited and
                            (nx, ny) in all_cluster_blocks and
                            0 <= nx < self.grid_width and
                            0 <= ny < self.grid_height and
                            self.puzzle_grid[ny][nx] is not None and
                            self.puzzle_grid[ny][nx].split('_')[0] == color):
                            
                            queue.append((nx, ny))
                            cluster_visited.add((nx, ny))
            
            # Add the current cluster if it's non-empty
            if current_cluster:
                clusters.append(current_cluster)
                visited.update(current_cluster)
        
        return clusters
    
    def find_connected_pieces(self, start_x, start_y, target_color):
        """
        Use flood fill to find all connected pieces of the same color.
        Returns a set of (x, y) coordinates.
        """
        if not (0 <= start_x < self.grid_width and 0 <= start_y < self.grid_height):
            return set()
            
        if self.puzzle_grid[start_y][start_x] is None:
            return set()
            
        # Get color of the starting piece without any suffix
        piece_color = self.puzzle_grid[start_y][start_x].split('_')[0]
        if piece_color != target_color:
            return set()
        
        # Initialize the search
        connected = set()
        queue = [(start_x, start_y)]
        visited = set(queue)
        
        # Breadth-first search to find all connected pieces
        while queue:
            x, y = queue.pop(0)
            connected.add((x, y))
            
            # Check all four adjacent positions
            for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:  # Up, right, down, left
                nx, ny = x + dx, y + dy
                
                # Check if the new position is valid and has the same color
                if ((nx, ny) not in visited and 
                    0 <= nx < self.grid_width and 
                    0 <= ny < self.grid_height and 
                    self.puzzle_grid[ny][nx] is not None):
                    
                    # Check if the color matches (ignoring suffixes like "_breaker")
                    next_color = self.puzzle_grid[ny][nx].split('_')[0]
                    if next_color == target_color:
                        queue.append((nx, ny))
                        visited.add((nx, ny))
        
        return connected
    
    # Particle effects and drawing functions
    
    def get_grid_screen_params(self):
        """
        Calculate and return the grid rendering parameters (x_offset, y_offset, cell_size).
        This method is used by the renderer and should remain in the engine.
        """
        # Calculate margins as percentage of screen
        side_margin = int(self.width * 0.30)  # 30% of screen width as margin
        top_margin = int(self.height * 0.02)  # 2% of screen height as top margin - reduced to move grid up
        
        # Calculate available area
        available_width = self.width - (side_margin * 2)
        available_height = self.height - (top_margin * 2)
        
        # Calculate cell size based on available space
        cell_width = available_width / self.grid_width
        cell_height = available_height / self.grid_height
        
        # Use the smaller dimension to maintain square cells
        cell_size = min(cell_width, cell_height)
        
        # Calculate total grid size
        grid_width_pixels = cell_size * self.grid_width
        grid_height_pixels = cell_size * self.grid_height
        
        # Center the grid within the available area
        x_offset = side_margin + (available_width - grid_width_pixels) / 2
        y_offset = top_margin + (available_height - grid_height_pixels) / 2
        
        return x_offset, y_offset, cell_size
    
    def draw_grid_blocks(self, x_offset, y_offset, cell_size):
        """
        DEPRECATED: Use PuzzleRenderer.draw_grid_blocks() instead.
        This method is kept for backward compatibility but will be removed in future versions.
        
        Draw the blocks that are placed on the grid.
        """
        
    def draw_falling_piece(self, x_offset, y_offset, cell_size):
        """
        DEPRECATED: Use PuzzleRenderer.draw_falling_piece() instead.
        This method is kept for backward compatibility but will be removed in future versions.
        
        Draw the currently falling piece.
        """
        pass
    
    def draw_next_piece_preview(self, cell_size):
        """
        DEPRECATED: Use PuzzleRenderer.draw_next_piece_preview() instead.
        This method is kept for backward compatibility but will be removed in future versions.
        
        Draw a preview of the next piece that will appear.
        """
        pass
    
    def draw_ui_elements(self):
        """
        DEPRECATED: Use PuzzleRenderer.draw_ui_elements() instead.
        This method is kept for backward compatibility but will be removed in future versions.
        
        Draw UI elements like the back button.
        """
        pass
    
    def process_events(self, events):
        """
        Process pygame events for the puzzle game.
        Returns the action to perform (e.g., 'back_to_menu') or None.
        """
        action = None
        
        for event in events:
            # Mouse events
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
                # Check for button clicks
                mouse_pos = pygame.mouse.get_pos()
                for button in self.game_buttons:
                    if button["rect"].collidepoint(mouse_pos):
                        action = button["action"]
                        break
            
            # Keyboard events
            elif event.type == pygame.KEYDOWN:
                # Track key press
                self.keys_pressed[event.key] = True
                self.last_key_action_time[event.key] = pygame.time.get_ticks()
                
                # Handle one-time key presses
                if self.game_active:
                    # Handle rotation with UP key (counter-clockwise)
                    if event.key == pygame.K_UP:
                        # First try to rotate, if that fails, try to flip
                        if not self.rotate_attached_piece(-1):
                            self.flip_pieces_vertically()
                    # Handle rotation with DOWN key (clockwise)
                    elif event.key == pygame.K_DOWN:
                        # First try to rotate, if that fails, try to flip
                        if not self.rotate_attached_piece(1):
                            self.flip_pieces_vertically()
                    # Handle immediate left/right movement on initial press
                    elif event.key == pygame.K_LEFT:
                        self.move_piece(-1, 0)  # Move left
                    elif event.key == pygame.K_RIGHT:
                        self.move_piece(1, 0)  # Move right
                    # Handle immediate acceleration when space is first pressed
                    elif event.key == pygame.K_SPACE:
                        # DEBUG: Print values when space is first pressed
                        print(f"SPACE PRESSED: normal_speed={self.normal_fall_speed}, accel_speed={self.accelerated_fall_speed}")
                        
                        # Increase fall speed for micro-movements too
                        self.current_fall_speed = self.accelerated_fall_speed
                        self.micro_fall_time = self._calculate_micro_fall_time(self.current_fall_speed)
                        
                        # DEBUG: Print values after updating
                        print(f"AFTER SPACE: current_speed={self.current_fall_speed}, micro_time={self.micro_fall_time}")
                        
                        # Remove sound from here since it should play when piece lands
                
                # Escape key - go back to menu
                if event.key == pygame.K_ESCAPE:
                    action = "back_to_menu"
            
            # Track key releases
            elif event.type == pygame.KEYUP:
                if event.key in self.keys_pressed:
                    del self.keys_pressed[event.key]
                
                if event.key in self.last_key_action_time:
                    del self.last_key_action_time[event.key]
                
                # Reset speed when spacebar is released
                if event.key == pygame.K_SPACE:
                    # DEBUG: Print values when space is released
                    print(f"SPACE RELEASED: Setting speed back to normal={self.normal_fall_speed}")
                    
                    self.current_fall_speed = self.normal_fall_speed
                    self.micro_fall_time = self._calculate_micro_fall_time(self.current_fall_speed)
                    
                    # DEBUG: Print values after resetting
                    print(f"AFTER RELEASE: current_speed={self.current_fall_speed}, micro_time={self.micro_fall_time}")
        
        # Handle continuous key presses
        if self.game_active:
            current_time = pygame.time.get_ticks()
            for key in self.keys_pressed:
                # Check if it's time for a repeat action
                time_since_last_action = current_time - self.last_key_action_time.get(key, 0)
                
                # Initial delay for first repeat
                initial_delay_passed = time_since_last_action >= self.key_repeat_delay
                
                # For subsequent repeats, check if interval time has passed
                repeat_ready = (initial_delay_passed and 
                              (time_since_last_action - self.key_repeat_delay) % self.key_repeat_interval <= 16)
                
                # Arrow keys have no delay for first press, but slow repeats for held keys
                if key in [pygame.K_LEFT, pygame.K_RIGHT]:
                    # For arrow keys, use a much slower repeat rate
                    arrow_repeat_interval = 500  # Much slower repeat rate (500ms between repeats)
                    
                    # Immediate response for first press or if enough time has passed
                    if time_since_last_action >= arrow_repeat_interval:
                        if key == pygame.K_LEFT:
                            self.move_piece(-1, 0)  # Move left
                        elif key == pygame.K_RIGHT:
                            self.move_piece(1, 0)  # Move right
                        # Update last action time to control repeat rate
                        self.last_key_action_time[key] = current_time
                # Handle UP and DOWN for rotations with slow repeats
                elif key in [pygame.K_UP, pygame.K_DOWN]:
                    # Rotation needs an even slower repeat rate
                    rotate_repeat_interval = 600  # Slower repeat rate for rotations
                    
                    if time_since_last_action >= rotate_repeat_interval:
                        if key == pygame.K_UP:
                            self.rotate_attached_piece(-1)  # Counter-clockwise
                        elif key == pygame.K_DOWN:
                            self.rotate_attached_piece(1)   # Clockwise
                        # Update last action time
                        self.last_key_action_time[key] = current_time
                # Handle spacebar for immediate acceleration with no delay
                elif key == pygame.K_SPACE:
                    # DEBUG: Print values during continuous space press every second
                    if current_time % 1000 < 20:  # Only print once per second approximately
                        print(f"SPACE HELD: current_speed={self.current_fall_speed}, micro_time={self.micro_fall_time}")
                    
                    # Always apply acceleration immediately with no delay
                    self.current_fall_speed = self.accelerated_fall_speed
                    self.micro_fall_time = self._calculate_micro_fall_time(self.current_fall_speed)
                # Other keys use the timing system
                elif repeat_ready:
                    # Update the last action time for this key
                    self.last_key_action_time[key] = current_time - (
                        self.key_repeat_delay + 
                        ((time_since_last_action - self.key_repeat_delay) // self.key_repeat_interval) 
                        * self.key_repeat_interval
                    )
                    
                    # Non-arrow movement keys (other than spacebar which is handled above)
                    # if key == pygame.K_SPACE:
                    #     self.current_fall_speed = self.accelerated_fall_speed  # Speed up falling
        
        return action
    
    def update(self):
        """Update game state for one frame."""
        if self.game_active:
            # Check if chain reaction is in progress
            if self.chain_reaction_in_progress:
                # Update the chain reaction state machine
                self.update_chain_reaction()
            else:
                # Update falling piece
                self.update_falling_piece()
        
        # Return whether the game is still active
        return self.game_active
    
    def draw_game_screen(self):
        """
        DEPRECATED: Use PuzzleRenderer.draw_game_screen() instead.
        This method is kept for backward compatibility but will be removed in future versions.
        
        Draw the puzzle game screen.
        """
        pass
    
    def draw_grid_blocks(self, x_offset, y_offset, cell_size):
        """
        DEPRECATED: Use PuzzleRenderer.draw_grid_blocks() instead.
        This method is kept for backward compatibility but will be removed in future versions.
        
        Draw the blocks that are placed on the grid.
        """
        pass
    
    def _calculate_micro_fall_time(self, fall_speed):
        """
        Calculate the micro_fall_time based on the fall speed to ensure pixel-perfect movement.
        
        Args:
            fall_speed: The fall speed in milliseconds
            
        Returns:
            int: The calculated micro_fall_time with a minimum value of 1
        """
        # Calculate pixels per second based on fall speed
        # The fall speed is how long it takes to traverse the entire grid height
        pixels_per_second = (self.grid_height * self.block_size) / (fall_speed / 1000.0)
        
        # Calculate time needed for 1 pixel movement (in milliseconds)
        time_per_pixel = 1000.0 / pixels_per_second if pixels_per_second > 0 else 1000.0
        
        # Calculate time needed for 1 sub-grid position (might be less than 1 pixel)
        time_per_sub_position = time_per_pixel / (self.block_size / self.sub_grid_positions)
        
        # Ensure we never return 0
        return max(1, int(time_per_sub_position))

    def update_gravity_animations(self):
        """Update the animation of blocks falling due to gravity."""
        if not hasattr(self, 'animating_gravity_blocks') or not self.animating_gravity_blocks:
            return
            
        # How many blocks have completed their animation
        completed = 0
        
        # Update each falling block
        for block in self.animating_gravity_blocks:
            # Update progress
            block['progress'] += block['speed']
            
            # If animation complete, place block at final position
            if block['progress'] >= 1.0:
                # Place the block at its target position
                self.puzzle_grid[block['target_y']][block['x']] = block['block_type']
                completed += 1
            
        # Remove completed blocks
        if completed > 0:
            self.animating_gravity_blocks = [b for b in self.animating_gravity_blocks if b['progress'] < 1.0]
            
        # If all animations complete, check for more gravity or breaker block effects
        if not self.animating_gravity_blocks:
            # Check if any more blocks need to fall
            has_more_gravity = False
            for y in range(self.grid_height - 2, -1, -1):
                for x in range(self.grid_width):
                    if self.puzzle_grid[y][x] is not None and self.puzzle_grid[y + 1][x] is None:
                        has_more_gravity = True
                        break
                if has_more_gravity:
                    break
                    
            if has_more_gravity:
                self.apply_gravity()
            else:
                # After gravity is fully applied, check for breaker blocks
                self.chain_reaction_in_progress = True
                self.activate_breaker_blocks()
                
    def get_block_visual_position(self, grid_x, grid_y):
        """Get the visual position of a block, considering gravity animations."""
        # If we have no falling blocks or this position isn't animating, return the grid position
        if not hasattr(self, 'animating_gravity_blocks') or not self.animating_gravity_blocks:
            return (grid_x, grid_y)
            
        # Check if this position is currently animating
        for block in self.animating_gravity_blocks:
            if block['x'] == grid_x and block['y'] == grid_y:
                # Calculate smooth y position based on animation progress
                animated_y = block['y'] + (block['target_y'] - block['y']) * block['progress']
                return (grid_x, animated_y)
                
        # If not animating, return the grid position
        return (grid_x, grid_y)
    
    def update_chain_reaction(self):
        """Update the chain reaction state machine."""
        current_time = pygame.time.get_ticks()
        
        # Add a global timeout for entire chain reaction
        # If chain has been active too long, force it to complete
        if hasattr(self, 'chain_start_time'):
            if current_time - self.chain_start_time > 3000:  # 3 second global timeout (reduced from 6s)
                # Before ending, apply gravity one final time to prevent floating pieces
                self.apply_gravity()
                self.chain_reaction_in_progress = False
                self.chain_state = "idle"
                self.chain_count = 0  # Reset chain counter on timeout
                return
        else:
            # Initialize chain start time if not set
            self.chain_start_time = current_time
        
        # State machine for chain reactions
        if self.chain_state == "idle":
            # Start by looking for breakers to activate
            breakers_found = self.find_and_activate_breakers()
            
            # If no breakers found, apply gravity one more time to catch any floating pieces
            if not breakers_found:
                final_gravity_applied = self.apply_gravity()
                
                # Only end chain reaction if no more gravity was applied
                if not final_gravity_applied:
                    self.chain_reaction_in_progress = False
                    # Reset chain start time when chain completes
                    if hasattr(self, 'chain_start_time'):
                        del self.chain_start_time
                    self.chain_count = 0  # Reset chain counter when reaction ends
                else:
                    # If gravity was applied, stay in chain reaction mode to process the results
                    self.chain_state = "waiting_for_gravity"
                    self.last_state_change = current_time
        
        elif self.chain_state == "breaking":
            # Even though breaking animations are disabled, we still want the 1-second delay
            # to create the impression of breaking before proceeding
            elapsed_time = current_time - self.breaking_animation_start
            if elapsed_time >= self.breaking_animation_duration:
                # After the 1-second delay, clear the blocks and move to next state
                self.clear_breaking_blocks()
                self.chain_state = "applying_gravity"
                self.last_state_change = current_time
                
        elif self.chain_state == "waiting_for_breaking":
            # Even though breaking animations are disabled, we still want to wait for the full duration
            elapsed_time = current_time - self.breaking_animation_start
            if elapsed_time >= self.breaking_animation_duration:
                # After the 1-second delay, proceed to the next state
                self.chain_state = "applying_gravity"
                self.last_state_change = current_time
                
        elif self.chain_state == "applying_gravity":
            # Small delay before applying gravity (feels better)
            if current_time - self.last_state_change >= self.state_delay:
                # Apply gravity to blocks
                gravity_applied = self.apply_gravity()
                self.chain_state = "waiting_for_gravity"
                self.last_state_change = current_time
                
                # If no gravity was applied, skip directly to checking for more breakers
                if not gravity_applied:
                    if self.find_breakers_to_activate():
                        self.chain_state = "breaking"
                        self.breaking_animation_start = current_time
                    else:
                        # One more final gravity check before ending
                        final_gravity_applied = self.apply_gravity()
                        if not final_gravity_applied:
                            self.chain_reaction_in_progress = False
                            self.chain_state = "idle"
                            # Reset chain start time when chain completes
                            if hasattr(self, 'chain_start_time'):
                                del self.chain_start_time
                            self.chain_count = 0  # Reset chain counter when reaction ends
                        else:
                            # If gravity was applied in the final check, stay in the state machine
                            self.chain_state = "waiting_for_gravity"
            
        elif self.chain_state == "waiting_for_gravity":
            # Check if renderer has finished the gravity animations
            if not hasattr(self, 'renderer') or not self.renderer.animations_in_progress():
                # Gravity animations complete, check for more breakers
                if self.find_breakers_to_activate():
                    # Found more breakers, continue the chain
                    self.chain_state = "breaking"
                    self.breaking_animation_start = current_time
                    self.chain_count += 1  # Increment chain counter when new breakers are activated
                else:
                    # No more breakers, do one final gravity check
                    final_gravity_applied = self.apply_gravity()
                    if not final_gravity_applied:
                        # No more gravity, end the chain reaction
                        self.chain_reaction_in_progress = False
                        self.chain_state = "idle"
                        # Reset chain start time when chain completes
                        if hasattr(self, 'chain_start_time'):
                            del self.chain_start_time
                        self.chain_count = 0  # Reset chain counter when reaction ends
                    else:
                        # If gravity was applied, stay in waiting_for_gravity state
                        self.last_state_change = current_time
            # Shorter timeout - if animations take too long, force completion sooner
            elif current_time - self.last_state_change > 200:  # Reduced from 500ms to 200ms to match breaking animation duration
                if self.find_breakers_to_activate():
                    self.chain_state = "breaking"
                    self.breaking_animation_start = current_time
                    self.chain_count += 1  # Increment chain counter when new breakers are activated
                else:
                    # Apply gravity one final time before ending
                    final_gravity_applied = self.apply_gravity()
                    if not final_gravity_applied:
                        self.chain_reaction_in_progress = False 
                        self.chain_state = "idle"
                        # Reset chain start time when chain completes
                        if hasattr(self, 'chain_start_time'):
                            del self.chain_start_time
                        self.chain_count = 0  # Reset chain counter when reaction ends
                    else:
                        # If gravity was applied, stay in waiting_for_gravity state
                        self.last_state_change = current_time
    
    def find_and_activate_breakers(self):
        """Find and activate breaker blocks to start the chain reaction."""
        current_time = pygame.time.get_ticks()
        
        # Find blocks to break
        breakers_found = self.find_breakers_to_activate()
        if breakers_found:
            self.chain_state = "breaking"
            self.breaking_animation_start = current_time
            # Don't set chain counter here - it will be incremented after the first break
        else:
            # No breakers found, end the chain reaction
            self.chain_reaction_in_progress = False
            self.chain_state = "idle"
            self.chain_count = 0  # Reset chain counter
            
        return breakers_found

    def find_breakers_to_activate(self):
        """
        Find breaker blocks to activate and add them to the breaking_blocks list.
        Returns True if any breakers were found, False otherwise.
        """
        # Track if any activation occurred this cycle
        activation_occurred = False
        
        # Collect all breakers to activate in this cycle
        breakers_to_activate = []
        
        # Scan the entire grid for breaker blocks
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                # Check if current position contains a breaker block
                if self.puzzle_grid[y][x] is not None and "_breaker" in self.puzzle_grid[y][x]:
                    breaker_color = self.puzzle_grid[y][x].split('_')[0]
                    
                    # Check adjacent positions (up, right, down, left)
                    adjacent_positions = [
                        (x, y - 1),  # up
                        (x + 1, y),  # right
                        (x, y + 1),  # down
                        (x - 1, y)   # left
                    ]
                    
                    # Check if any adjacent position has matching color
                    breaker_activated = False
                    for adj_x, adj_y in adjacent_positions:
                        if (0 <= adj_x < self.grid_width and 0 <= adj_y < self.grid_height and
                                self.puzzle_grid[adj_y][adj_x] is not None):
                            # Get the color without any suffix
                            adjacent_block = self.puzzle_grid[adj_y][adj_x]
                            adjacent_color = adjacent_block.split('_')[0]
                            
                            # Skip if this is a garbage block (gray block in transformation)
                            if '_garbage' in adjacent_block:
                                continue
                            
                            # Check if colors match and it's not a breaker of the same color
                            if adjacent_color == breaker_color:
                                breaker_activated = True
                                print(f"DEBUG: Breaker at ({x},{y}) [{breaker_color}] activated by adjacent block at ({adj_x},{adj_y}) [{adjacent_color}]")
                                break
                    
                    # If the breaker is activated, add it to list of breakers to activate
                    if breaker_activated:
                        breakers_to_activate.append((x, y, self.puzzle_grid[y][x]))
        
        # If any breakers were activated, start the breaking animation
        if breakers_to_activate:
            activation_occurred = True
            current_time = pygame.time.get_ticks()
            self.breaking_animation_start = current_time
            print(f"DEBUG: Found {len(breakers_to_activate)} breakers to activate")
            
            # Process all activated breakers and find connected blocks of the same color
            for x, y, breaker_type in breakers_to_activate:
                # Add the breaker itself to breaking blocks
                self.breaking_blocks.append((x, y, current_time, 0, breaker_type, True))
                
                # The breaker will destroy all connected blocks of the same color
                breaker_color = breaker_type.split('_')[0]
                connected_blocks = self.find_connected_pieces(x, y, breaker_color)
                
                # Add all connected blocks to breaking blocks with a small delay for cascade effect
                delay = 0
                for block_x, block_y in connected_blocks:
                    delay += self.chain_delay
                    # Check if the position is still valid and not already in breaking blocks
                    if (0 <= block_y < self.grid_height and 0 <= block_x < self.grid_width and
                            self.puzzle_grid[block_y][block_x] is not None):
                        
                        # Skip if this block is already in breaking_blocks
                        already_breaking = False
                        for bx, by, _, _, _, _ in self.breaking_blocks:
                            if bx == block_x and by == block_y:
                                already_breaking = True
                                break
                        
                        if not already_breaking:
                            block_type = self.puzzle_grid[block_y][block_x]
                            self.breaking_blocks.append((block_x, block_y, current_time, delay, block_type, False))
        else:
            print("DEBUG: No breakers found to activate")
            
        return activation_occurred

    def clear_breaking_blocks(self):
        """Clear breaking blocks from the grid."""
        if self.breaking_blocks:
            # Count the number of blocks being broken for combo tracking
            combo_count = len(self.breaking_blocks)
            print(f"DEBUG: Clearing {combo_count} breaking blocks")
            
            # Get broken blocks for attack generation
            broken_blocks = []
            for x, y, _, _, block_type, _ in self.breaking_blocks:
                if 0 <= y < self.grid_height and 0 <= x < self.grid_width:
                    # Add to broken blocks list for attack generation
                    broken_blocks.append((x, y, block_type))
                    # Remove the block from the grid
                    self.puzzle_grid[y][x] = None
            
            # Play single break sound if this is not part of a combo
            if self.chain_count == 0 and self.audio and broken_blocks:
                print("DEBUG: Playing single break sound - not part of combo")
                self.audio.play_sound("singlebreak")
                # Now increment chain count for subsequent breaks
                self.chain_count = 1
            # Show combo text for subsequent breaks
            elif hasattr(self, 'renderer') and self.chain_count > 0:
                # Play appropriate combo sound
                if self.audio:
                    if self.chain_count == 2:
                        print("DEBUG: Playing double combo sound")
                        self.audio.play_sound("double")
                    elif self.chain_count == 3:
                        print("DEBUG: Playing triple combo sound")
                        self.audio.play_sound("triple")
                    elif self.chain_count > 3:
                        print(f"DEBUG: Playing tripormore combo sound for {self.chain_count}x combo")
                        self.audio.play_sound("tripormore")

                # Calculate position in the middle of the broken blocks for the combo text
                sum_x, sum_y = 0, 0
                for x, y, _, _, _, _ in self.breaking_blocks:
                    sum_x += x
                    sum_y += y
                avg_x = sum_x / combo_count
                avg_y = sum_y / combo_count
                
                # Convert to screen coordinates
                if hasattr(self.renderer, 'current_x_offset') and hasattr(self.renderer, 'current_y_offset') and \
                   hasattr(self.renderer, 'block_width') and hasattr(self.renderer, 'block_height'):
                    screen_x = self.renderer.current_x_offset + (avg_x * self.renderer.block_width)
                    screen_y = self.renderer.current_y_offset + (avg_y * self.renderer.block_height)
                    self.renderer.show_combo_text(self.chain_count, (screen_x, screen_y))
                else:
                    # If we can't get exact position, use default center position
                    self.renderer.show_combo_text(self.chain_count)
            
            # Generate attacks based on broken blocks if we have a handler
            if hasattr(self, 'blocks_broken_handler') and broken_blocks:
                # Call the handler with the broken blocks
                is_cluster = self.chain_count > 1
                combo_multiplier = max(1, self.chain_count)
                
                # This will call back to the TestMode which manages the attack system
                self.blocks_broken_handler(broken_blocks, is_cluster, combo_multiplier)
            
            # Clear the breaking blocks list
            self.breaking_blocks = []
            print("DEBUG: Breaking blocks list cleared")
    
    def activate_breaker_blocks(self):
        """Legacy method for backward compatibility - use the state machine instead."""
        # This method is kept for compatibility but should no longer be called directly
        self.chain_reaction_in_progress = True
        self.chain_state = "idle"
        self.update_chain_reaction()

    def process_transformed_garbage_blocks(self, blocks_to_update):
        """Process any garbage blocks that have been fully transformed."""
        if not blocks_to_update:
            return
            
        print(f"Processing {len(blocks_to_update)} fully transformed garbage blocks")
            
        # Convert fully transformed garbage blocks to normal blocks
        for (x, y), color in blocks_to_update:
            # Create the proper block type with the color name
            block_type = f"{color}_block"  # Convert "blue" to "blue_block", etc.
            
            # Determine which grid this position belongs to
            if 0 <= x < self.player_engine.grid_width and 0 <= y < self.player_engine.grid_height:
                # Update player grid - convert from garbage to normal block
                current_block = self.player_engine.puzzle_grid[y][x]
                if current_block and '_garbage' in current_block:
                    # Replace with normal block of the same color
                    self.player_engine.puzzle_grid[y][x] = block_type
                    print(f"Transformed player garbage block at ({x}, {y}) to {block_type}")
            
            # Check enemy grid
            if 0 <= x < self.enemy_engine.grid_width and 0 <= y < self.enemy_engine.grid_height:
                # Update enemy grid - convert from garbage to normal block
                current_block = self.enemy_engine.puzzle_grid[y][x]
                if current_block and '_garbage' in current_block:
                    # Replace with normal block of the same color
                    self.enemy_engine.puzzle_grid[y][x] = block_type
                    print(f"Transformed enemy garbage block at ({x}, {y}) to {block_type}")
                    
        # Make sure these changes are visible immediately
        self.player_renderer.update_visual_state()
        self.enemy_renderer.update_visual_state()
        
        # Check for breaker activation after transforming blocks
        if hasattr(self, 'chain_reaction_in_progress'):
            self.chain_reaction_in_progress = True
            self.chain_state = "idle"
            self.update_chain_reaction() 

    def place_pieces(self, pieces_to_place):
        """Place multiple pieces on the grid, handling overlaps and applying gravity."""
        # Track unique positions to handle overlaps
        unique_positions = {}
        
        for x, y, piece in pieces_to_place:
            # Prioritize breaker pieces, then by position (lower pieces have priority)
            is_breaker = "_breaker" in piece
            priority = (is_breaker, y)  # Breakers first, then by y position
            
            if (x, y) in unique_positions:
                existing_piece = unique_positions[(x, y)][0]
                existing_priority = unique_positions[(x, y)][1]
                
                # Only replace if new piece has higher priority
                if priority > existing_priority:
                    unique_positions[(x, y)] = (piece, priority)
            else:
                unique_positions[(x, y)] = (piece, priority)
        
        # Now place the pieces on the grid based on resolved positions
        for (x, y), (piece, _) in unique_positions.items():
            self.puzzle_grid[y][x] = piece
        
        # Apply gravity to make pieces fall into empty spaces
        gravity_applied = self.apply_gravity()
        
        return gravity_applied