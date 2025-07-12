import pygame
import sys
import os
import math
import random
import time
import argparse
import json

from blade_fighter_lessons import LessonManager

# Try importing the AudioSystem if available
try:
    from audio_system import AudioSystem
    audio_system_available = True
except ImportError:
    audio_system_available = False
    print("AudioSystem not available, running without audio")

from menu_system import MenuSystem
from settings_system import SettingsSystem
from puzzle_module import PuzzleEngine
from puzzle_renderer import PuzzleRenderer
from attack_system import AttackSystem, AttackType

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
ASSET_PATH = "puzzleassets"
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

class TestMode:
    """A test mode for evaluating AI puzzle battle mechanics with real puzzle engine components."""
    def __init__(self, screen, font, audio, asset_path):
        self.screen = screen
        self.font = font
        self.audio = audio
        self.asset_path = asset_path
        
        # Get screen dimensions
        self.width = screen.get_width()
        self.height = screen.get_height()
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GRAY = (100, 100, 100)
        self.LIGHT_BLUE = (100, 150, 255)
        
        # AI difficulty (1-10)
        self.ai_difficulty = 5
        
        # AI style ("water", "fire", "earth", "lightning")
        self.ai_style = "fire"
        
        # Create player puzzle engine
        self.player_engine = PuzzleEngine(screen, font, audio, asset_path)
        
        # Create enemy puzzle engine (with AI controller) - no audio
        self.enemy_engine = PuzzleEngine(screen, font, None, asset_path)
        
        # Create renderers for both engines
        self.player_renderer = PuzzleRenderer(self.player_engine)
        self.enemy_renderer = PuzzleRenderer(self.enemy_engine)
        
        # Set renderer references in the engines
        self.player_engine.renderer = self.player_renderer
        self.enemy_engine.renderer = self.enemy_renderer
        
        # Load background images
        try:
            self.puzzle_background = pygame.image.load(os.path.join(asset_path, "puzzlebackground.jpg"))
        except pygame.error:
            self.puzzle_background = None
        
        # Initialize attack system with grid dimensions
        self.attack_system = AttackSystem(grid_width=6, grid_height=13)
        
        # Set up board positions and dimensions
        self.setup_board_positions()
        
        # Initialize the player and enemy game boards
        self.initialize_test()
        
        # Set up references for attack generation
        self.setup_attack_handlers()
    
    def setup_attack_handlers(self):
        """Set up the attack generation handlers for both engines."""
        # Create a reference to this TestMode instance in each engine
        self.player_engine.test_mode = self
        self.enemy_engine.test_mode = self
        
        # Define the method that engines will call when blocks are broken
        def player_blocks_broken_handler(broken_blocks, is_cluster, combo_multiplier):
            return self.handle_player_blocks_broken(broken_blocks, is_cluster, combo_multiplier)
            
        def enemy_blocks_broken_handler(broken_blocks, is_cluster, combo_multiplier):
            return self.handle_enemy_blocks_broken(broken_blocks, is_cluster, combo_multiplier)
            
        # Attach handlers to the engines
        self.player_engine.blocks_broken_handler = player_blocks_broken_handler
        self.enemy_engine.blocks_broken_handler = enemy_blocks_broken_handler
        
        # Initialize piece tracking for detecting when pieces land
        self.previous_player_has_piece = bool(self.player_engine.main_piece)
        self.previous_enemy_has_piece = bool(self.enemy_engine.main_piece)
    
    def handle_player_blocks_broken(self, broken_blocks, is_cluster, combo_multiplier):
        """Handle attack generation when player breaks blocks."""
        if not broken_blocks:
            return
        
        # Only increment chain count for subsequent breaks
        if self.player_engine.chain_count > 0:
            self.player_engine.chain_count += 1
        
        attack_color = "blue"  # Player color is blue
        
        # Calculate garbage blocks based on combo
        blocks_destroyed = len(broken_blocks)
        if self.player_engine.chain_count == 1:
            # First combo - send half the blocks destroyed (rounded down)
            garbage_blocks = blocks_destroyed // 2
        else:
            # Subsequent combos - multiply blocks by combo multiplier and add previous amounts
            garbage_blocks = (blocks_destroyed * combo_multiplier) // 2
        
        # Generate attacks
        attacks = self.attack_system.generate_attack(
            broken_blocks,
            is_cluster,
            combo_multiplier,  # Pass the original combo_multiplier, not garbage_blocks
            attack_color
        )
        
        if attacks:
            # Add attacks to queue targeting enemy (player 2)
            self.attack_system.add_attacks_to_queue(attacks, 2)
    
    def handle_enemy_blocks_broken(self, broken_blocks, is_cluster, combo_multiplier):
        """Handle attack generation when enemy breaks blocks."""
        if not broken_blocks:
            return
            
        # Only increment chain count for subsequent breaks
        if self.enemy_engine.chain_count > 0:
            self.enemy_engine.chain_count += 1
            
        # Get attack color based on AI style
        attack_color = {
            "water": "blue",
            "fire": "red",
            "earth": "green",
            "lightning": "yellow"
        }.get(self.ai_style, "red")
        
        # Calculate garbage blocks based on combo
        blocks_destroyed = len(broken_blocks)
        if self.enemy_engine.chain_count == 1:
            # First combo - send half the blocks destroyed (rounded down)
            garbage_blocks = blocks_destroyed // 2
        else:
            # Subsequent combos - multiply blocks by combo multiplier and add previous amounts
            garbage_blocks = (blocks_destroyed * combo_multiplier) // 2
        
        # Scale attack generation based on AI difficulty
        difficulty_scale = self.ai_difficulty / 5.0
        
        # Generate attacks
        attacks = self.attack_system.generate_attack(
            broken_blocks,
            is_cluster,
            combo_multiplier,  # Pass the original combo_multiplier, not garbage_blocks
            attack_color
        )
        
        # Potentially modify attack count based on difficulty
        if difficulty_scale > 1.0 and attacks:
            # Higher difficulties might generate additional attacks
            extra_attacks = []
            for _ in range(int((difficulty_scale - 1.0) * len(attacks))):
                extra_attacks.append({
                    "type": AttackType.GARBAGE_BLOCK,
                    "color": attack_color  # Use the same attack color for extra attacks
                })
            attacks.extend(extra_attacks)
        
        if attacks:
            # Add attacks to queue targeting player (player 1)
            self.attack_system.add_attacks_to_queue(attacks, 1)
    
    def setup_board_positions(self):
        """Set up the positions for the player and enemy boards."""
        # Calculate board dimensions - ensure consistent dimensions
        grid_width = 6
        grid_height = 13
        
        # Using consistent sizing to eliminate gaps
        cell_width = 68  # Match the cell width used in draw() method
        cell_height = 54  # Match the cell height used in draw() method
        
        # Border size - space between container edge and the actual grid
        border_size = 10
        
        # Calculate total board size
        board_width = grid_width * cell_width
        board_height = grid_height * cell_height
        
        # Calculate proper centered positions
        # 1/3 from left edge for player board, 1/3 from right edge for enemy board
        screen_width = self.width
        board_spacing = 40  # Space between boards
        
        # Center calculation with proper spacing - include borders in the total width
        total_width_needed = (board_width * 2) + board_spacing + (border_size * 4)  # Add borders for both boards
        start_x = (screen_width - total_width_needed) // 2
        
        # Add border offset to starting positions
        player_x = start_x + border_size  # Add border on left side
        enemy_x = start_x + board_width + board_spacing + (border_size * 3)  # Account for both borders
        
        # Vertical position - centered with some offset from top
        board_y = 80
        
        # Try to load positions from JSON file if available
        loaded_positions = None
        try:
            if os.path.exists('ui_positions.json'):
                with open('ui_positions.json', 'r') as f:
                    loaded_positions = json.load(f)
                print("Successfully loaded UI positions from file")
        except Exception as e:
            print(f"Error loading UI positions: {e}")
        
        # Use loaded positions if available, otherwise use defaults
        if loaded_positions:
            self.player_background_position = loaded_positions.get("player_board_background", 
                {"x": player_x, "y": board_y})
            self.player_grid_position = loaded_positions.get("player_puzzle_grid", 
                {"x": player_x, "y": board_y})
            self.enemy_background_position = loaded_positions.get("enemy_board_background", 
                {"x": enemy_x, "y": board_y})
            self.enemy_grid_position = loaded_positions.get("enemy_puzzle_grid", 
                {"x": enemy_x, "y": board_y})
        else:
            # Set positions directly without loading from file
            self.player_background_position = {
                "x": player_x,
                "y": board_y
            }
            
            self.player_grid_position = {
                "x": player_x,
                "y": board_y
            }
            
            self.enemy_background_position = {
                "x": enemy_x,
                "y": board_y
            }
            
            self.enemy_grid_position = {
                "x": enemy_x,
                "y": board_y
            }
            
            # Still save positions to JSON for consistency
            default_positions = {
                "player_board_background": self.player_background_position,
                "player_puzzle_grid": self.player_grid_position,
                "enemy_board_background": self.enemy_background_position,
                "enemy_puzzle_grid": self.enemy_grid_position
            }
            
            try:
                with open('ui_positions.json', 'w') as f:
                    json.dump(default_positions, f)
            except:
                print("Could not save UI positions")
        
        # Set up the grid sizes
        self.player_engine.grid_width = grid_width
        self.player_engine.grid_height = grid_height
        self.enemy_engine.grid_width = grid_width
        self.enemy_engine.grid_height = grid_height
        
        # Initialize grid offsets for rendering - using exact positions where pieces land
        if not hasattr(self.player_engine, 'grid_x_offset'):
            self.player_engine.grid_x_offset = self.player_grid_position["x"]
            self.player_engine.grid_y_offset = self.player_grid_position["y"]
            
        if not hasattr(self.enemy_engine, 'grid_x_offset'):
            self.enemy_engine.grid_x_offset = self.enemy_grid_position["x"]
            self.enemy_engine.grid_y_offset = self.enemy_grid_position["y"]
    
    def initialize_test(self):
        """Initialize the player and enemy puzzle engines."""
        # Reset attack system
        self.attack_system = AttackSystem(grid_width=6, grid_height=13)
        
        # Reset piece tracking
        self.previous_player_has_piece = False
        self.previous_enemy_has_piece = False
        
        # Reset chain reaction state
        self.player_engine.chain_reaction_in_progress = False
        self.player_engine.chain_state = "idle"
        self.player_engine.chain_count = 0
        self.player_engine.breaking_blocks = []
        self.player_engine.clusters = set()
        
        self.enemy_engine.chain_reaction_in_progress = False
        self.enemy_engine.chain_state = "idle"
        self.enemy_engine.chain_count = 0
        self.enemy_engine.breaking_blocks = []
        self.enemy_engine.clusters = set()
        
        # Reset piece movement state
        self.player_engine.current_fall_speed = self.player_engine.normal_fall_speed
        self.player_engine.last_fall_time = pygame.time.get_ticks()
        self.player_engine.micro_fall_time = self.player_engine._calculate_micro_fall_time(self.player_engine.current_fall_speed)
        self.player_engine.current_sub_position = float(self.player_engine.sub_grid_positions * 0.3)
        
        self.enemy_engine.current_fall_speed = self.enemy_engine.normal_fall_speed
        self.enemy_engine.last_fall_time = pygame.time.get_ticks()
        self.enemy_engine.micro_fall_time = self.enemy_engine._calculate_micro_fall_time(self.enemy_engine.current_fall_speed)
        self.enemy_engine.current_sub_position = float(self.enemy_engine.sub_grid_positions * 0.3)
        
        # Start both games
        self.player_engine.start_game()
        self.enemy_engine.start_game()
        
        # Flag the player's grid to enable attack generation
        self.player_engine._is_player_grid = True
        self.enemy_engine._is_player_grid = False
        
        # Set up attack system references
        self.player_engine.attack_system = self.attack_system
        self.enemy_engine.attack_system = self.attack_system
        
        # Reset renderers
        self.player_renderer.update_visual_state()
        self.enemy_renderer.update_visual_state()
    
    def process_transformed_garbage_blocks(self, blocks_to_update):
        """Process any garbage blocks that have been fully transformed."""
        if not blocks_to_update:
            return
            
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
            
            # Check enemy grid
            if 0 <= x < self.enemy_engine.grid_width and 0 <= y < self.enemy_engine.grid_height:
                # Update enemy grid - convert from garbage to normal block
                current_block = self.enemy_engine.puzzle_grid[y][x]
                if current_block and '_garbage' in current_block:
                    # Replace with normal block of the same color
                    self.enemy_engine.puzzle_grid[y][x] = block_type
                    
        # Make sure these changes are visible immediately
        self.player_renderer.update_visual_state()
        self.enemy_renderer.update_visual_state()
    
    def process_strike_to_garbage_transformation(self, blocks_to_transform):
        """Process any strike blocks that have been transformed to garbage blocks."""
        if not blocks_to_transform:
            return
            
        # Process each transformed block
        for (x, y), color in blocks_to_transform:
            # Determine which grid this position belongs to
            if 0 <= x < self.player_engine.grid_width and 0 <= y < self.player_engine.grid_height:
                # Update player grid - convert from strike to garbage block
                current_block = self.player_engine.puzzle_grid[y][x]
                if current_block and current_block == "strike_1x4":
                    # Replace with garbage block of the same color
                    garbage_block_type = f"{color}_garbage"
                    self.player_engine.puzzle_grid[y][x] = garbage_block_type
            
            # Check enemy grid
            if 0 <= x < self.enemy_engine.grid_width and 0 <= y < self.enemy_engine.grid_height:
                # Update enemy grid - convert from strike to garbage block
                current_block = self.enemy_engine.puzzle_grid[y][x]
                if current_block and current_block == "strike_1x4":
                    # Replace with garbage block of the same color
                    garbage_block_type = f"{color}_garbage"
                    self.enemy_engine.puzzle_grid[y][x] = garbage_block_type
                    
        # Make sure these changes are visible immediately
        self.player_renderer.update_visual_state()
        self.enemy_renderer.update_visual_state()
    
    def create_strike_spark_particles(self, grid_x, grid_y, is_player_grid=True):
        """Create spark particles when a strike lands on the board."""
        if not hasattr(self.player_renderer, 'create_dust_particles'):
            return  # Can't create particles if method doesn't exist
            
        try:
            # Use the appropriate renderer based on which grid the strike is in
            renderer = self.player_renderer if is_player_grid else self.enemy_renderer
            
            # Get the actual screen position for this grid cell
            x_offset = self.player_grid_position["x"] if is_player_grid else self.enemy_grid_position["x"]
            y_offset = self.player_grid_position["y"] if is_player_grid else self.enemy_grid_position["y"]
            
            # Create many more spark particles for strikes (10x more than normal dust particles)
            # Use a mix of colors for a more electric effect
            strike_colors = ["yellow", "white", "blue"]
            
            # Create a burst of particles in all directions
            for _ in range(10):
                # Mix of colors for electric effect
                color = random.choice(strike_colors)
                renderer.create_dust_particles(grid_x, grid_y, color)
                
            # Add special attribute to the renderer to indicate a strike effect is active
            if not hasattr(renderer, 'active_strike_effects'):
                renderer.active_strike_effects = {}
                
            # Record this position as having an active strike effect
            position_key = (grid_x, grid_y)
            renderer.active_strike_effects[position_key] = {
                'start_time': time.time(),
                'duration': 2.0,  # 2 seconds of electric effect
                'intensity': 1.0,  # Start at full intensity
                'last_spark_time': 0
            }
                
            print(f"Created enhanced strike spark particles at ({grid_x}, {grid_y})")
        except Exception as e:
            print(f"Error creating strike spark particles: {e}")
    
    def update(self):
        """Update the test scene state."""
        # Update player engine
        player_piece_landed = self.player_engine.update()
        
        # Update enemy engine
        enemy_piece_landed = self.enemy_engine.update()
        
        # Check for game over conditions
        if not self.player_engine.game_active or not self.enemy_engine.game_active:
            return "game_over"
        
        # Track current piece states
        current_player_has_piece = self.player_engine.main_piece is not None
        current_enemy_has_piece = self.enemy_engine.main_piece is not None
        
        # If either piece landed, process garbage blocks and strikes
        if player_piece_landed or enemy_piece_landed:
            # Process strikes transformation to garbage blocks
            strike_blocks = self.attack_system.update_strike_blocks()
            if strike_blocks:
                self.process_strike_to_garbage_transformation(strike_blocks)
            
            # Decrement turns on garbage blocks and get any that need to transform
            blocks_to_update = self.attack_system.decrement_garbage_block_turns()
            
            # Process any fully transformed blocks
            self.process_transformed_garbage_blocks(blocks_to_update)
        
        # Store current piece states for next frame
        self.previous_player_has_piece = current_player_has_piece
        self.previous_enemy_has_piece = current_enemy_has_piece
        
        # Process any pending attacks
        try:
            # Process attacks against player
            player_attacks_processed = self.attack_system.process_attack_queue(self.player_engine.puzzle_grid, 1)
            
            # Process attacks against enemy
            enemy_attacks_processed = self.attack_system.process_attack_queue(self.enemy_engine.puzzle_grid, 2)
            
            # Create spark effects for strikes if attacks were processed
            if player_attacks_processed or enemy_attacks_processed:
                # Check for newly placed strikes in player grid
                for y in range(self.player_engine.grid_height):
                    for x in range(self.player_engine.grid_width):
                        if self.player_engine.puzzle_grid[y][x] == "strike_1x4":
                            self.create_strike_spark_particles(x, y, True)
                
                # Check for newly placed strikes in enemy grid
                for y in range(self.enemy_engine.grid_height):
                    for x in range(self.enemy_engine.grid_width):
                        if self.enemy_engine.puzzle_grid[y][x] == "strike_1x4":
                            self.create_strike_spark_particles(x, y, False)
            
            # After placing garbage blocks, ensure the puzzle engine applies gravity
            if hasattr(self.player_engine, 'apply_gravity'):
                self.player_engine.apply_gravity()
            if hasattr(self.enemy_engine, 'apply_gravity'):
                self.enemy_engine.apply_gravity()
                
        except Exception as e:
            print(f"Error processing attack queue: {e}")
            
        # Update visual states and animations
        self.player_renderer.update_visual_state()
        self.enemy_renderer.update_visual_state()
        self.player_renderer.update_animations()
        self.enemy_renderer.update_animations()
        
        # Basic AI movement
        try:
            # Scale AI update frequency with difficulty
            if random.random() < 0.1 * (self.ai_difficulty / 5.0):  # Increased frequency with difficulty
                # Random movement
                move_choice = random.random()
                
                if move_choice < 0.4:  # 40% chance to move left/right
                    self.enemy_engine.move_piece(random.choice([-1, 1]), 0)
                elif move_choice < 0.6:  # 20% chance to rotate
                    self.enemy_engine.rotate_attached_piece(random.choice([-1, 1]))
                else:  # 40% chance to accelerate drop
                    self.enemy_engine.move_piece(0, 1)
                    
        except Exception as e:
            print(f"Error in AI movement: {e}")
        
        # Return None to indicate no game over
        return None
    
    def process_events(self, events):
        """Process events for the test scene."""
        # First let the player engine handle its own events
        self.player_engine.process_events(events)
        
        # Then handle test mode specific events
        for event in events:
            if event.type == pygame.KEYDOWN:
                # Escape key to return to menu
                if event.key == pygame.K_ESCAPE:
                    return "back_to_menu"
                
                # Difficulty adjustment with number keys
                if pygame.K_1 <= event.key <= pygame.K_9:
                    self.ai_difficulty = event.key - pygame.K_0  # Convert key to number
                elif event.key == pygame.K_0:
                    self.ai_difficulty = 10
                
                # Style selection
                elif event.key == pygame.K_b:
                    self.ai_style = "water"  # Blue
                elif event.key == pygame.K_r:
                    self.ai_style = "fire"   # Red
                elif event.key == pygame.K_g:
                    self.ai_style = "earth"  # Green
                elif event.key == pygame.K_y:
                    self.ai_style = "lightning"  # Yellow      
        return None  # No specific action
    
    def draw(self):
        print("[DEBUG] TestMode.draw() called")
        """Draw the battle test mode interface with proper sizing and positioning."""
        # Draw background
        self.screen.fill((10, 10, 30))
            
        # Add some atmospheric effects
        for i in range(20):
            alpha = 150 - (i * 7)
            if alpha < 0:
                alpha = 0
            gradient = pygame.Surface((self.width, 5), pygame.SRCALPHA)
            gradient.fill((50, 50, 80, alpha))
            self.screen.blit(gradient, (0, i * 20))
            self.screen.blit(gradient, (0, self.height - (i * 20)))
        
        # Add semi-transparent overlay for better contrast
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        
        # Draw title at top
        title_font = pygame.font.SysFont(None, 48)
        title_text = title_font.render("AI Battle Test Mode", True, (255, 255, 255))
        title_rect = title_text.get_rect(midtop=(self.width // 2, 20))
        # Add glow effect
        glow_text = title_font.render("AI Battle Test Mode", True, (100, 100, 255))
        glow_rect = glow_text.get_rect(midtop=(self.width // 2 + 2, 22))
        self.screen.blit(glow_text, glow_rect)
        self.screen.blit(title_text, title_rect)
        
        # Set up cell size for blocks
        cell_width = 68  # Width of each block
        cell_height = 54  # Height of each block
        
        # Border size - this is the space between container edge and the actual grid
        border_size = 10
        
        # Calculate board dimensions
        board_width = self.player_engine.grid_width * cell_width
        board_height = self.player_engine.grid_height * cell_height
        
        # Player board container - with adjusted padding for borders
        player_container_width = board_width + (border_size * 2)  # Add border on both sides
        player_container_height = board_height + (border_size * 2)  # Add border on top and bottom
        player_container = pygame.Rect(
            self.player_grid_position["x"] - border_size,  # Adjust for left border
            self.player_grid_position["y"] - 35,  # Keep the top padding for title/labels
            player_container_width,
            player_container_height + 35  # Keep extra bottom padding
        )
        
        # Draw player container with border
        pygame.draw.rect(self.screen, (30, 30, 60), player_container, border_radius=5)
        pygame.draw.rect(self.screen, (100, 100, 255), player_container, 3, border_radius=5)
        
        # Enemy board container - with adjusted padding for borders
        enemy_container_width = board_width + (border_size * 2)  # Add border on both sides
        enemy_container_height = board_height + (border_size * 2)  # Add border on top and bottom
        enemy_container = pygame.Rect(
            self.enemy_grid_position["x"] - border_size,  # Adjust for left border
            self.enemy_grid_position["y"] - 35,  # Keep the top padding for title/labels
            enemy_container_width,
            enemy_container_height + 35  # Keep extra bottom padding
        )
        
        # Draw enemy container with border
        pygame.draw.rect(self.screen, (30, 30, 60), enemy_container, border_radius=5)
        
        # Choose AI color based on style
        if self.ai_style == "water":
            ai_color = (0, 0, 200)
            ai_border = (100, 100, 255)
        elif self.ai_style == "fire":
            ai_color = (200, 0, 0) 
            ai_border = (255, 100, 100)
        elif self.ai_style == "earth": 
            ai_color = (0, 150, 0)
            ai_border = (100, 255, 100)
        else:  # Lightning
            ai_color = (200, 200, 0)
            ai_border = (255, 255, 100)
        
        # Draw enemy container border with AI style color
        pygame.draw.rect(self.screen, ai_border, enemy_container, 3, border_radius=5)
            
        # Draw backgrounds if available
        if self.puzzle_background:
            # Scale background to match actual gameplay area (not including borders)
            scaled_bg = pygame.transform.scale(
                self.puzzle_background,
                (board_width, board_height)
            )
            # Draw player board background - position inside border
            self.screen.blit(scaled_bg, 
                (self.player_grid_position["x"], 
                 self.player_grid_position["y"]))
            
            # Draw enemy board background - position inside border
            self.screen.blit(scaled_bg, 
                (self.enemy_grid_position["x"], 
                 self.enemy_grid_position["y"]))
        
        # Draw player grid blocks
        self.player_renderer.draw_grid_blocks(
            self.player_grid_position["x"], 
            self.player_grid_position["y"], 
            cell_width, 
            cell_height
        )
        
        # Draw player falling piece
        self.player_renderer.draw_falling_piece(
            self.player_grid_position["x"], 
            self.player_grid_position["y"], 
            cell_width, 
            cell_height
        )
        
        # Draw player next piece preview
        self.player_renderer.current_x_offset = self.player_grid_position["x"]
        self.player_renderer.current_y_offset = self.player_grid_position["y"]
        self.player_renderer.engine = self.player_engine
        self.player_renderer.draw_next_piece_preview(cell_width, cell_height)
        
        # Draw player title
        player_title = pygame.font.SysFont(None, 28).render("Player", True, (255, 255, 255))
        player_title_rect = player_title.get_rect(midtop=(
            self.player_grid_position["x"] + (board_width / 2), 
            self.player_grid_position["y"] - 30
        ))
        self.screen.blit(player_title, player_title_rect)
        
        # Draw player combo texts
        self.player_renderer.draw_combo_texts()
        
        # Draw enemy grid blocks
        self.enemy_renderer.draw_grid_blocks(
            self.enemy_grid_position["x"], 
            self.enemy_grid_position["y"], 
            cell_width, 
            cell_height
        )
        
        # Draw enemy falling piece
        self.enemy_renderer.draw_falling_piece(
            self.enemy_grid_position["x"], 
            self.enemy_grid_position["y"], 
            cell_width, 
            cell_height
        )
        
        # Draw enemy next piece preview
        self.enemy_renderer.current_x_offset = self.enemy_grid_position["x"]
        self.enemy_renderer.current_y_offset = self.enemy_grid_position["y"]
        self.enemy_renderer.engine = self.enemy_engine
        self.enemy_renderer.draw_next_piece_preview_right(cell_width, cell_height)
        
        # Draw enemy title
        enemy_title = pygame.font.SysFont(None, 28).render(f"AI ({self.ai_style.capitalize()})", True, ai_border)
        enemy_title_rect = enemy_title.get_rect(midtop=(
            self.enemy_grid_position["x"] + (board_width / 2), 
            self.enemy_grid_position["y"] - 30
        ))
        self.screen.blit(enemy_title, enemy_title_rect)
        
        # Draw enemy combo texts
        self.enemy_renderer.draw_combo_texts()
        
        # Draw controls explanation
        controls_font = pygame.font.SysFont(None, 20)
        controls = [
            {"key": "[ESC]", "action": "Back to menu"},
            {"key": "[1-0]", "action": "Set difficulty"},
            {"key": "[B]", "action": "Blue/Water style"},
            {"key": "[R]", "action": "Red/Fire style"},
            {"key": "[G]", "action": "Green/Earth style"},
            {"key": "[Y]", "action": "Yellow/Lightning style"}
        ]
        
        # Calculate total width of all controls
        total_width = 0
        for control in controls:
            key_text = controls_font.render(control["key"], True, self.WHITE)
            action_text = controls_font.render(control["action"], True, self.GRAY)
            total_width += key_text.get_width() + action_text.get_width() + 20  # 20px spacing
        
        # Draw controls centered at bottom
        x_pos = (self.width - total_width) // 2
        y_pos = self.height - 30
        for control in controls:
            # Draw key with background
            key_text = controls_font.render(control["key"], True, self.WHITE)
            key_bg = pygame.Rect(x_pos, y_pos, key_text.get_width() + 6, key_text.get_height() + 2)
            pygame.draw.rect(self.screen, (60, 60, 100), key_bg, border_radius=3)
            pygame.draw.rect(self.screen, self.WHITE, key_bg, 1, border_radius=3)
            self.screen.blit(key_text, (x_pos + 3, y_pos))
            
            x_pos += key_text.get_width() + 6
            
            # Draw action text
            action_text = controls_font.render(control["action"], True, self.GRAY)
            self.screen.blit(action_text, (x_pos, y_pos))
            
            x_pos += action_text.get_width() + 14  # Add spacing between controls

class GameClient:
    def __init__(self):
        """Initialize the game client."""
        # Initialize pygame
        pygame.init()
        
        # Set the asset path
        self.asset_path = ASSET_PATH
        
        # Define available resolutions (width, height)
        self.resolutions = [
            (800, 600),
            (1024, 768),
            (1280, 720),
            (1366, 768),
            (1600, 900),
            (1920, 1080)
        ]
        
        # Get desktop info for default resolution
        desktop_info = pygame.display.Info()
        desktop_width, desktop_height = desktop_info.current_w, desktop_info.current_h
        
        # Choose best resolution based on desktop size
        self.width, self.height = self.resolutions[0]  # Default to lowest
        for res in self.resolutions:
            if res[0] <= desktop_width and res[1] <= desktop_height:
                self.width, self.height = res  # Use the largest resolution that fits
        
        # Create window with default resolution
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Blade Fighters")
        
        # Create font
        self.font = pygame.font.SysFont(None, 36)
        
        # Initialize audio system
        if audio_system_available:
            self.audio = AudioSystem(ASSET_PATH)
        else:
            # Create a placeholder audio system
            self.audio = None
        
        # Create menu system
        self.menu_system = MenuSystem(self.screen, self.font, self.audio, self.asset_path)
        
        # Create test mode first
        self.test_mode = TestMode(self.screen, self.font, self.audio, self.asset_path)
        
        # Create settings system
        self.settings_system = SettingsSystem(self.screen, self.font, self.audio, self.asset_path)
        self.settings_system.test_mode = self.test_mode  # Add reference to test_mode
        
        # Create puzzle engine
        parser = argparse.ArgumentParser()
        parser.add_argument('--debug', action='store_true', help='Enable debugging mode')
        args = parser.parse_args()

        if args.debug:
            self.puzzle_engine = DebuggingPuzzleEngine(self.screen, self.font, self.audio, self.asset_path)
        else:
            self.puzzle_engine = PuzzleEngine(self.screen, self.font, self.audio, self.asset_path)
        
        # Create puzzle renderer
        self.puzzle_renderer = PuzzleRenderer(self.puzzle_engine)
        
        # Current screen (main_menu, settings, game)
        self.current_screen = "main_menu"
        
        # Game state
        self.game_running = True
        
        # Game version
        self.version = "1.0.0"
        
        # Story content view variables
        self.story_scroll_position = 0
        self.current_story = {"title": "No Story Selected", "content": []}
        
        # Load background images
        try:
            self.main_background = pygame.image.load(os.path.join(ASSET_PATH, "colorful.png"))
        except pygame.error:
            self.main_background = None
            
        try:
            self.settings_background = pygame.image.load(os.path.join(ROOT_PATH, "settingsbcg.jfif"))
        except pygame.error:
            self.settings_background = None
            
        try:
            self.puzzle_background = pygame.image.load(os.path.join(ASSET_PATH, "bkg.png"))
        except pygame.error:
            self.puzzle_background = None
            
        try:
            self.story_background = pygame.image.load(os.path.join(ASSET_PATH, "storybackground.png"))
        except pygame.error:
            self.story_background = None
        
        # Menu particles for visual effects
        self.menu_particles = []
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GRAY = (100, 100, 100)
        self.LIGHT_GRAY = (200, 200, 200)
        self.BLUE = (0, 100, 255)
        self.LIGHT_BLUE = (100, 150, 255)
        
        # Border glow colors
        self.GLOW_COLORS = [
            (210, 100, 240),  # Bright Purple
            (180, 60, 220),   # Medium Purple
            (150, 40, 200),   # Dark Purple
            (220, 120, 255)   # Pink-Purple
        ]
        self.glow_index = 0
        self.glow_direction = 1
        self.glow_intensity = 0.6
        self.glow_speed = 0.03
        
    def create_button(self, x, y, width, height, text, action=None, params=None):
        """Create a button with text and optional action."""
        button = {
            "rect": pygame.Rect(x, y, width, height),
            "text": text,
            "action": action,
            "params": params,
            "hover": False
        }
        
        # Draw the button
        pygame.draw.rect(self.screen, self.GRAY, button["rect"])
        pygame.draw.rect(self.screen, self.LIGHT_GRAY, button["rect"], 2)
        
        # Draw button text
        text_surf = self.font.render(text, True, self.WHITE)
        text_rect = text_surf.get_rect(center=button["rect"].center)
        self.screen.blit(text_surf, text_rect)
        
        return button
    
    def set_screen(self, screen_name):
        """Set the current screen."""
        print(f"Game Client: Setting screen to {screen_name}")
        self.current_screen = screen_name
        if screen_name == "settings":
            print("Game Client: Initializing settings system")
            self.settings_system = SettingsSystem(self.screen, self.font, self.audio, self.asset_path)
        elif screen_name == "ui_editor":
            print("Game Client: Switching to UI editor")
            if hasattr(self, 'settings_system'):
                self.settings_system.set_screen("ui_editor")
        elif screen_name == "test":
            self.test_mode.initialize_test()
            # Reload UI positions to ensure the latest positions are used
            self.test_mode.setup_board_positions()
        elif screen_name == "main_menu" and hasattr(self, 'test_mode'):
            # Make sure the test mode has the latest UI positions when going back to main menu
            self.test_mode.setup_board_positions()
        
        print(f"Changing screen to: {screen_name}")
        
        # Initialize the new screen
        if screen_name == "game":
            self.puzzle_engine.start_game()
    
    def update_menu_particles(self):
        """Update the menu particles position and life."""
        # Create new particles occasionally
        if random.random() < 0.1 and len(self.menu_particles) < 50:
            particle = {
                "x": random.randint(0, self.width),
                "y": random.randint(0, self.height),
                "size": random.randint(2, 5),
                "speed": random.uniform(0.5, 2.0),
                "angle": random.uniform(0, 2 * math.pi),
                "color": random.choice(self.GLOW_COLORS),
                "life": random.randint(60, 180)  # Frames of life
            }
            self.menu_particles.append(particle)
        
        # Update existing particles
        for particle in self.menu_particles[:]:
            # Move the particle
            particle["x"] += math.cos(particle["angle"]) * particle["speed"]
            particle["y"] += math.sin(particle["angle"]) * particle["speed"]
            
            # Reduce life
            particle["life"] -= 1
            
            # Remove if it's off-screen or dead
            if (particle["x"] < 0 or particle["x"] > self.width or
                particle["y"] < 0 or particle["y"] > self.height or
                particle["life"] <= 0):
                self.menu_particles.remove(particle)
    
    def draw_menu_particles(self):
        """Draw menu particles on the screen."""
        for particle in self.menu_particles:
            # Calculate opacity based on remaining life
            alpha = int(255 * (particle["life"] / 180.0))
            color = list(particle["color"])
            
            # Create a surface with per-pixel alpha
            surf = pygame.Surface((particle["size"], particle["size"]), pygame.SRCALPHA)
            surf.fill((color[0], color[1], color[2], alpha))
            
            # Draw the particle
            self.screen.blit(surf, (int(particle["x"]), int(particle["y"])))
    
    def draw_main_menu(self):
        """Draw the main menu screen."""
        # Draw background
        if self.main_background:
            # Scale to fit screen
            scaled_bg = pygame.transform.scale(self.main_background, (self.width, self.height))
            self.screen.blit(scaled_bg, (0, 0))
        else:
            # Use a solid color if no background image
            gradient_rect = pygame.Rect(0, 0, self.width, self.height)
            pygame.draw.rect(self.screen, (20, 20, 50), gradient_rect)
        
        # Add some animated particles in the background
        self.draw_menu_particles()
        
        # Calculate button positions based on screen size
        button_width = 300
        button_height = 50
        button_margin = 20
        start_y = self.height // 3
        
        # Create buttons if they don't exist
        if not hasattr(self, 'main_menu_buttons'):
            self.main_menu_buttons = []
            
            # Clear any existing buttons
            self.main_menu_buttons = []
            
            # Center buttons horizontally
            button_x = (self.width - button_width) // 2
            
            # Play Game button
            play_button = self.create_button(
                button_x, start_y,
                button_width, button_height,
                "Play Game", self.start_quickplay
            )
            self.main_menu_buttons.append(play_button)
            
            # Settings button
            settings_button = self.create_button(
                button_x, start_y + button_height + button_margin,
                button_width, button_height,
                "Settings", self.set_screen, ["settings"]
            )
            self.main_menu_buttons.append(settings_button)
            
            # Story button
            story_button = self.create_button(
                button_x, start_y + (button_height + button_margin) * 2,
                button_width, button_height,
                "Story", self.set_screen, ["story"]
            )
            self.main_menu_buttons.append(story_button)
            
            # Test button
            test_button = self.create_button(
                button_x, start_y + (button_height + button_margin) * 3,
                button_width, button_height,
                "Test", self.set_screen, ["test"]
            )
            self.main_menu_buttons.append(test_button)
            
            # Quit button
            quit_button = self.create_button(
                button_x, start_y + (button_height + button_margin) * 4,
                button_width, button_height,
                "Quit", sys.exit
            )
            self.main_menu_buttons.append(quit_button)
        
        # Draw each button and check for hover
        mouse_pos = pygame.mouse.get_pos()
        for button in self.main_menu_buttons:
            # Determine if the mouse is hovering over this button
            button["hover"] = button["rect"].collidepoint(mouse_pos)
            
            # Change color based on hover state
            color = self.LIGHT_BLUE if button["hover"] else self.BLUE
            
            # Draw button background
            pygame.draw.rect(self.screen, color, button["rect"])
            
            # Draw border with glow effect if hovering
            if button["hover"]:
                # Draw glowing border
                glow_color = self.GLOW_COLORS[self.glow_index]
                pygame.draw.rect(self.screen, glow_color, button["rect"], 3)
            else:
                # Draw normal border
                pygame.draw.rect(self.screen, self.WHITE, button["rect"], 2)
            
            # Draw button text
            text_surf = self.font.render(button["text"], True, self.WHITE)
            text_rect = text_surf.get_rect(center=button["rect"].center)
            self.screen.blit(text_surf, text_rect)
        
        # Draw title
        title_font = pygame.font.SysFont(None, 72)
        title_surf = title_font.render("Blade Fighters", True, self.WHITE)
        title_rect = title_surf.get_rect(midtop=(self.width // 2, 50))
        self.screen.blit(title_surf, title_rect)
        
        # Draw version number
        version_font = pygame.font.SysFont(None, 20)
        version_surf = version_font.render(f"v{self.version}", True, self.LIGHT_GRAY)
        version_rect = version_surf.get_rect(bottomright=(self.width - 10, self.height - 10))
        self.screen.blit(version_surf, version_rect)
        
        # Animate the glow colors
        self.glow_intensity += self.glow_speed * self.glow_direction
        if self.glow_intensity >= 1.0:
            self.glow_intensity = 1.0
            self.glow_direction = -1
            self.glow_index = (self.glow_index + 1) % len(self.GLOW_COLORS)
        elif self.glow_intensity <= 0.3:
            self.glow_intensity = 0.3
            self.glow_direction = 1
    
    def draw_settings_menu(self):
        """Draw the settings menu screen using the MenuSystem."""
        # Use the MenuSystem to draw the settings menu
        settings_buttons = self.menu_system.draw_settings_menu(
            on_back_action=lambda: self.set_screen("main_menu"),
            current_resolution=(self.width, self.height),
            resolutions=self.resolutions,
            on_resolution_change=self.change_resolution
        )
        
        # Check for hover on buttons
        mouse_pos = pygame.mouse.get_pos()
        for button in settings_buttons:
            if button["rect"].collidepoint(mouse_pos):
                button["hover"] = True
            else:
                button["hover"] = False
        
        # Instead, use the custom MP3 player display method
        if audio_system_available and self.audio:
            self.display_custom_mp3_player()
        
        return settings_buttons
    
    def change_resolution(self, width, height):
        """Change the game's resolution."""
        # Update the screen dimensions
        self.width = width
        self.height = height
        
        # Update the display mode
        self.screen = pygame.display.set_mode((self.width, self.height))
        
        # Update menu system with new screen
        self.menu_system.screen = self.screen
        
        # Update settings system with new screen
        self.settings_system.screen = self.screen
        
        # If we're in test mode, update the board positions
        if hasattr(self, 'test_mode'):
            self.test_mode.setup_board_positions()
        
        # Play click sound if available
        if audio_system_available and hasattr(self.audio, 'sounds') and 'click' in self.audio.sounds:
            self.audio.sounds['click'].play()
    
    def start_quickplay(self):
        """Start the game in quickplay mode."""
        print("Starting quickplay mode")
        self.set_screen("game")
        self.puzzle_engine.start_game()
    
    def draw_game_screen(self):
        """Draw the game screen. Placeholder for now."""
        # Draw background
        if self.puzzle_background:
            # Scale to fit screen
            scaled_bg = pygame.transform.scale(self.puzzle_background, (self.width, self.height))
            self.screen.blit(scaled_bg, (0, 0))
        else:
            # Use a solid color if no background image
            self.screen.fill((20, 20, 50))
            
        # Draw game placeholder text
        title_font = pygame.font.SysFont(None, 72)
        title_surf = title_font.render("Game Screen", True, self.WHITE)
        title_rect = title_surf.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(title_surf, title_rect)
        
        # Draw instruction
        instruction_font = pygame.font.SysFont(None, 36)
        instruction_surf = instruction_font.render("Press ESC to return to menu", True, self.WHITE)
        instruction_rect = instruction_surf.get_rect(center=(self.width // 2, self.height // 2 + 60))
        self.screen.blit(instruction_surf, instruction_rect)
        
        # Instead, use the custom MP3 player display method
        if audio_system_available and self.audio:
            self.display_custom_mp3_player()
    
    def display_custom_mp3_player(self):
        """Display only the custom MP3 player image with functional buttons."""
        if not hasattr(self.audio, 'mp3_player') or not self.audio.mp3_player:
            return
        
        # Simply use the MP3 player's own draw method
        # This will draw the MP3 player with consistent button positioning
        self.mp3_player_buttons = self.audio.mp3_player.draw(self.screen, self.width, self.height)
        
        return self.mp3_player_buttons
    
    def handle_mp3_player_click(self, pos):
        """Handle clicks on the custom MP3 player buttons."""
        if not hasattr(self, 'mp3_player_buttons') or not self.mp3_player_buttons:
            return False
        
        # Check if any button was clicked
        for btn_name, btn_rect in self.mp3_player_buttons.items():
            if btn_rect.collidepoint(pos):
                # Play click sound if available
                if audio_system_available and self.audio and hasattr(self.audio, 'sounds') and 'click' in self.audio.sounds:
                    self.audio.sounds['click'].play()
                
                # Handle button actions using the audio system's MP3 player
                if hasattr(self.audio, 'mp3_player'):
                    if btn_name == 'play':
                        self.audio.mp3_player.pause_song()  # Toggle play/pause
                    elif btn_name == 'prev':
                        self.audio.mp3_player.prev_song()
                    elif btn_name == 'next':
                        self.audio.mp3_player.next_song()
                        
                return True  # Click was handled
                
        return False  # Click was not on any MP3 player button
    
    def show_game_over_screen(self):
        """Display a dramatic game over screen."""
        # Create a semi-transparent black overlay
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Black with 180/255 alpha
        self.screen.blit(overlay, (0, 0))
        
        # Create a dramatic "GAME OVER" text with red glow effect
        game_over_font = pygame.font.SysFont(None, 72)
        game_over_text = game_over_font.render("GAME OVER", True, (255, 0, 0))
        game_over_rect = game_over_text.get_rect(center=(self.width // 2, self.height // 2))
        
        # Draw glow effect
        glow_surface = pygame.Surface((game_over_text.get_width() + 20, game_over_text.get_height() + 20), pygame.SRCALPHA)
        for i in range(10):
            alpha = 100 - (i * 10)
            glow_text = game_over_font.render("GAME OVER", True, (255, 0, 0))
            glow_rect = glow_text.get_rect(center=(glow_surface.get_width() // 2, glow_surface.get_height() // 2))
            glow_surface.blit(glow_text, glow_rect)
        self.screen.blit(glow_surface, (game_over_rect.x - 10, game_over_rect.y - 10))
        
        # Draw the main text
        self.screen.blit(game_over_text, game_over_rect)
        
        # Draw instruction text
        instruction_font = pygame.font.SysFont(None, 36)
        instruction_text = instruction_font.render("Press ESC to return to main menu", True, self.WHITE)
        instruction_rect = instruction_text.get_rect(center=(self.width // 2, self.height // 2 + 60))
        self.screen.blit(instruction_text, instruction_rect)
        
        # Update the display
        pygame.display.flip()
        
        # Wait for 2 seconds before returning to main menu
        pygame.time.wait(2000)
        
        # Return to main menu
        self.set_screen("main_menu")

    def run(self):
        """Main loop for the application."""
        # Set up the clock
        clock = pygame.time.Clock()
        
        try:
            # Main game loop
            while self.game_running:
                # Get all events
                events = pygame.event.get()
                
                # Process window close events
                for event in events:
                    if event.type == pygame.QUIT:
                        # Save UI positions before closing
                        if hasattr(self, 'settings_system') and hasattr(self.settings_system, 'ui_editor') and self.settings_system.ui_editor:
                            self.settings_system.ui_editor.save_positions()
                        self.game_running = False
                    elif event.type == pygame.VIDEORESIZE:
                        # Update resolution if the window is resized
                        self.change_resolution(event.w, event.h)
                    # Handle mouse clicks for MP3 player buttons
                    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
                        # Check if click was on MP3 player buttons
                        if hasattr(self, 'mp3_player_buttons') and self.mp3_player_buttons:
                            if self.handle_mp3_player_click(event.pos):
                                # Click was handled by MP3 player, no need to process it further
                                continue
                    # Prevent escape from closing the game in main menu
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and self.current_screen == "main_menu":
                        continue
                    
                    # Let the audio system handle any audio-related events
                    if audio_system_available and self.audio:
                        self.audio.handle_audio_events(event)
                
                # Process events and update/draw the current screen
                if self.current_screen == "main_menu":
                    # Filter out escape key events in main menu BEFORE processing any events
                    filtered_events = []
                    for event in events:
                        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                            continue
                        filtered_events.append(event)
                    events = filtered_events
                    
                    # Process menu events with filtered event list
                    menu_action = self.menu_system.process_main_menu_events(events)
                    
                    # Handle menu actions
                    if menu_action == "quickplay":
                        self.set_screen("game")
                    elif menu_action == "settings":
                        self.set_screen("settings")
                    elif menu_action == "story":
                        self.set_screen("story")
                    elif menu_action == "test":
                        self.set_screen("test")
                    elif menu_action == "quit":
                        self.game_running = False
                    
                    # Draw the main menu
                    self.main_menu_buttons = self.menu_system.draw_main_menu(
                        on_start_action=self.start_quickplay,
                        on_settings_action=lambda: self.set_screen("settings"),
                        on_story_action=lambda: self.set_screen("story"),
                        on_test_action=lambda: self.set_screen("test"),
                        version=self.version
                    )
                    
                    # Display MP3 player
                    if audio_system_available and self.audio:
                        self.display_custom_mp3_player()
                
                elif self.current_screen == "test":
                    # Process test mode events
                    test_action = self.test_mode.process_events(events)
                    
                    # Handle test mode actions
                    if test_action == "back_to_menu":
                        self.set_screen("main_menu")
                    
                    # Update the test mode
                    test_update_result = self.test_mode.update()
                    
                    # Handle game over state
                    if test_update_result == "game_over":
                        self.show_game_over_screen()
                        continue
                    
                    # Draw the test mode
                    self.test_mode.draw()
                    
                    # Display MP3 player in test mode too
                    if audio_system_available and self.audio:
                        self.display_custom_mp3_player()
                
                elif self.current_screen == "story":
                    # Process story menu events
                    story_action = self.menu_system.process_story_menu_events(events)
                    
                    # Handle story menu actions
                    if story_action == "back":
                        self.set_screen("main_menu")
                    elif isinstance(story_action, str) and story_action.startswith("story:"):
                        # Extract story ID from action string
                        story_id = int(story_action.split(":")[1])
                        print(f"Selected story {story_id}")
                        # Load and display the selected story
                        self.load_story(story_id)
                        self.set_screen("story_content")
                    
                    # Draw the story menu
                    self.menu_system.draw_story_menu(
                        on_back_action=lambda: self.set_screen("main_menu")
                    )
                    
                    # Display MP3 player in story menu too
                    if audio_system_available and self.audio:
                        self.display_custom_mp3_player()
                
                elif self.current_screen == "story_content":
                    # Process events for the story content view
                    for event in events:
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_ESCAPE:
                                self.set_screen("story")
                            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                                # Scroll down
                                self.story_scroll_position += 20
                            elif event.key == pygame.K_UP or event.key == pygame.K_w:
                                # Scroll up (with limit to prevent scrolling above the top)
                                self.story_scroll_position = max(0, self.story_scroll_position - 20)
                        elif event.type == pygame.MOUSEBUTTONDOWN:
                            if event.button == 4:  # Mouse wheel up
                                self.story_scroll_position = max(0, self.story_scroll_position - 40)
                            elif event.button == 5:  # Mouse wheel down
                                self.story_scroll_position += 40
                    
                    # Display the story content
                    self.display_story_content()
                    
                    # Display MP3 player in story content view too
                    if audio_system_available and self.audio:
                        self.display_custom_mp3_player()
                
                elif self.current_screen == "settings":
                    # Process settings events using the settings system
                    settings_action = self.settings_system.process_settings_events(events)
                    
                    # Handle settings actions
                    if settings_action == "back":
                        self.set_screen("main_menu")
                    elif isinstance(settings_action, str) and settings_action.startswith("resolution:"):
                        # Extract resolution from action string
                        parts = settings_action.split(":")
                        if len(parts) == 3:
                            width, height = int(parts[1]), int(parts[2])
                            self.change_resolution(width, height)
                    
                    # Draw the settings menu using the settings system
                    self.settings_buttons = self.settings_system.draw_settings_menu(
                        on_back_action=lambda: self.set_screen("main_menu"),
                        current_resolution=(self.width, self.height),
                        resolutions=self.resolutions,
                        on_resolution_change=self.change_resolution
                    )
                    
                    # Display MP3 player in settings too
                    if audio_system_available and self.audio:
                        self.display_custom_mp3_player()
                
                elif self.current_screen == "game":
                    # Process game events
                    game_action = self.puzzle_engine.process_events(events)
                    
                    # Handle game actions
                    if game_action == "back_to_menu":
                        self.set_screen("main_menu")
                    
                    # Calculate delta time for smooth animations
                    current_time = time.time()
                    if not hasattr(self, 'last_frame_time'):
                        self.last_frame_time = current_time
                    delta_time = current_time - self.last_frame_time
                    self.last_frame_time = current_time
                    
                    # Update game state
                    self.puzzle_engine.update()
                    
                    # Update renderer animations
                    self.puzzle_renderer.update_visual_state()
                    self.puzzle_renderer.update_animations()
                    
                    # Draw the game using our renderer
                    self.puzzle_renderer.draw_game_screen()
                    
                    # Instead, use the custom MP3 player display method
                    if audio_system_available and self.audio:
                        self.display_custom_mp3_player()
                
                # Update the display
                pygame.display.flip()
                
                # Cap the frame rate
                clock.tick(60)
        except KeyboardInterrupt:
            print("Game interrupted by user")
        except Exception as e:
            print(f"Error occurred: {e}")
        finally:
            # Clean up
            pygame.quit()
            sys.exit()
            
    def load_story(self, story_id):
        """Load story content from file based on story ID."""
        # Map story IDs to filenames
        story_files = {
            1: "stories/saga1_the_forge_keepers_legacy.txt",
            2: "stories/saga2_crimson_dawn.txt",
            3: "stories/saga3_azure_storm.txt",
            4: "stories/saga4_emerald_shadows.txt",
            5: "stories/saga5_golden_ascension.txt",
            6: "stories/saga6_twilight_vendetta.txt",
            7: "stories/saga7_crystal_prophecy.txt",
            8: "stories/saga8_obsidian_heart.txt",
            9: "stories/saga9_silver_alliance.txt",
            10: "stories/saga10_radiant_finale.txt"
        }
        
        # Default content if file not found
        self.current_story = {
            "title": f"Story {story_id}",
            "content": ["No story content available yet.", "Check back later for updates!"]
        }
        
        # Try to load the story file
        if story_id in story_files:
            try:
                with open(story_files[story_id], "r") as f:
                    lines = f.readlines()
                    
                # Parse the content
                title = "Unknown Story"
                content = []
                in_chapter = False
                
                for line in lines:
                    line = line.strip()
                    if line.startswith("# "):
                        # This is the title
                        title = line[2:]
                    elif line.startswith("## "):
                        # This is a chapter title
                        in_chapter = True
                        content.append(line)
                    elif line or in_chapter:
                        # Only add non-empty lines or lines after we've started a chapter
                        # This skips any blank lines at the beginning
                        content.append(line)
                
                self.current_story = {
                    "title": title,
                    "content": content
                }
                
                print(f"Loaded story: {title}")
            except Exception as e:
                print(f"Error loading story {story_id}: {e}")
        
        # Reset scroll position
        self.story_scroll_position = 0
        
    def display_story_content(self):
        """Display the current story content with scrolling."""
        # Clear the screen
        self.screen.fill(self.BLACK)
        
        # Draw a nice background
        if hasattr(self, 'story_background') and self.story_background:
            # Scale to fit screen
            scaled_bg = pygame.transform.scale(self.story_background, (self.width, self.height))
            self.screen.blit(scaled_bg, (0, 0))
        
        # Add a semi-transparent overlay for better readability
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Black with 180/255 alpha
        self.screen.blit(overlay, (0, 0))
        
        # Draw some menu particles for visual appeal
        self.menu_system.draw_menu_particles()
        
        # Create a surface for the content
        content_width = int(self.width * 0.8)
        content_x = (self.width - content_width) // 2
        padding = 20
        
        # Initialize fonts
        title_font = pygame.font.SysFont(None, 56)
        chapter_font = pygame.font.SysFont(None, 36)
        text_font = pygame.font.SysFont(None, 24)
        
        # Render the title
        title_surf = title_font.render(self.current_story["title"], True, self.WHITE)
        title_rect = title_surf.get_rect(midtop=(self.width // 2, padding))
        self.screen.blit(title_surf, title_rect)
        
        # Calculate total content height (for scrolling limits)
        total_height = title_rect.height + padding * 2
        content_surfaces = []
        
        # Render all content lines
        y_offset = title_rect.bottom + padding
        for line in self.current_story["content"]:
            if not line:
                # Add spacing for empty lines
                y_offset += 15
                continue
                
            if line.startswith("## "):
                # Chapter title
                surf = chapter_font.render(line[3:], True, (220, 180, 255))
                y_offset += 30  # Extra space before chapters
            else:
                # Regular text
                surf = text_font.render(line, True, self.WHITE)
            
            rect = surf.get_rect(topleft=(content_x, y_offset - self.story_scroll_position))
            content_surfaces.append((surf, rect, y_offset))
            y_offset += surf.get_height() + 5
        
        total_height = y_offset + padding
        
        # Draw only visible content
        visible_area = pygame.Rect(0, 0, self.width, self.height)
        for surf, rect, original_y in content_surfaces:
            if original_y - self.story_scroll_position < 0:
                continue  # Skip if above the view
            if original_y - self.story_scroll_position > self.height:
                continue  # Skip if below the view
                
            self.screen.blit(surf, rect)
        
        # Limit scrolling
        max_scroll = max(0, total_height - self.height)
        self.story_scroll_position = min(self.story_scroll_position, max_scroll)
        
        # Draw scroll indicators if needed
        if total_height > self.height:
            # Up indicator
            if self.story_scroll_position > 0:
                pygame.draw.polygon(self.screen, (180, 180, 255), [
                    (self.width // 2, 15),
                    (self.width // 2 - 10, 25),
                    (self.width // 2 + 10, 25)
                ])
            
            # Down indicator
            if self.story_scroll_position < max_scroll:
                pygame.draw.polygon(self.screen, (180, 180, 255), [
                    (self.width // 2, self.height - 15),
                    (self.width // 2 - 10, self.height - 25),
                    (self.width // 2 + 10, self.height - 25)
                ])
                
        # Draw instruction
        instruction_font = pygame.font.SysFont(None, 20)
        instruction_text = "Use arrow keys or mouse wheel to scroll. Press ESC to return to story menu."
        instruction_surf = instruction_font.render(instruction_text, True, self.LIGHT_GRAY)
        instruction_rect = instruction_surf.get_rect(midbottom=(self.width // 2, self.height - 10))
        self.screen.blit(instruction_surf, instruction_rect)

if __name__ == "__main__":
    client = GameClient()
    client.run() 