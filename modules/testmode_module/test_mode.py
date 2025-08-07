"""
Simplified TestMode Implementation
Core puzzle battle functionality: 2 grids, piece previews, backgrounds.
Stripped of attack system complexity to focus on essential gameplay.
"""

import pygame
import os
import random
import time
from typing import List, Dict, Optional, Any, Tuple

# Try to import the interface contract
try:
    from contracts.testmode_interface_contract import TestModeInterface, validate_testmode_interface
    interface_available = True
except ImportError:
    # Create a dummy interface if not available
    class TestModeInterface:
        pass
    
    def validate_testmode_interface(cls):
        return cls
    
    interface_available = False
    print("⚠️  TestMode interface contract not found, running without validation")

# Import required game components
from core.puzzle_module import PuzzleEngine
from core.puzzle_renderer import PuzzleRenderer

# Import the simple attack system
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from modules.attack_module import SimpleAttackSystem, AttackData, ComboData
from modules.attack_module.column_rotator import ColumnRotator
from .attack_flow_tracker import AttackFlowTracker

@validate_testmode_interface
class TestMode(TestModeInterface):
    """Simplified TestMode focusing on core puzzle battle functionality."""
    
    def __init__(self, screen, font, audio, asset_path: str, settings_system=None):
        """Initialize the test mode with core puzzle battle setup."""
        self.screen = screen
        self.font = font
        self.audio = audio
        self.asset_path = asset_path
        self.settings_system = settings_system
        
        # Get screen dimensions
        self.width = screen.get_width()
        self.height = screen.get_height()
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GRAY = (100, 100, 100)
        self.LIGHT_BLUE = (100, 150, 255)
        
        # Create player puzzle engine
        self.player_engine = PuzzleEngine(screen, font, audio, asset_path, settings_system)
        # Create enemy puzzle engine (no audio to avoid conflicts)
        self.enemy_engine = PuzzleEngine(screen, font, None, asset_path, settings_system)
        
        # Set test_mode attribute so puzzle module knows to use landing-based transformation
        self.player_engine.test_mode = self
        self.enemy_engine.test_mode = self
        
        # Set player-specific on_piece_landed callbacks
        self.player_engine.on_piece_landed = lambda: self.on_piece_landed(1)
        self.enemy_engine.on_piece_landed = lambda: self.on_piece_landed(2)
        # Ensure both engines can call back to TestMode
        
        # Create renderers for both engines
        self.player_renderer = PuzzleRenderer(self.player_engine)
        self.enemy_renderer = PuzzleRenderer(self.enemy_engine)
        
        # Configure preview sides for both renderers
        self.player_renderer.preview_side = 'left'  # Player on the left
        self.enemy_renderer.preview_side = 'right'  # Enemy on the right
        
        # Initialize attack systems for BOTH players
        self.player_attack_system = SimpleAttackSystem(grid_width=6)
        self.enemy_attack_system = SimpleAttackSystem(grid_width=6)  # ENABLED - Enemy attacks now work!
        
        # ENABLE ATTACK DATABASE with fixed values
        print("🔧 ENABLING FIXED ATTACK DATABASE")
        self.player_attack_system.enable_database("attack_database.json")  # Re-enabled
        self.enemy_attack_system.enable_database("attack_database.json")   # Re-enabled
        
        # DEBUG: Check if databases are enabled
        print(f"🔍 PLAYER DATABASE STATUS: use_database={self.player_attack_system.use_database}")
        print(f"🔍 ENEMY DATABASE STATUS: use_database={self.enemy_attack_system.use_database}")
        print("🔧 Using fixed database with proper strike dimensions")
        
        # Store database status for UI display (enabled with fix)
        self.database_enabled = True
        
        # Chain tracking
        self.player_chain_position = 0
        self.enemy_chain_position = 0
        self.player_chain_active = False
        self.enemy_chain_active = False
        self.chain_window_duration = 2000  # 2 seconds to continue chain
        self.last_player_combo_time = 0
        self.last_enemy_combo_time = 0
        
        # Connect attack system handlers for BOTH players
        self.player_engine.blocks_broken_handler = self.handle_player_blocks_broken
        self.enemy_engine.blocks_broken_handler = self.handle_enemy_blocks_broken  # ENABLED - Enemy attacks now work!
        
        # Load background images
        try:
            self.puzzle_background = pygame.image.load(os.path.join(asset_path, "puzzlebackground.jpg"))
        except pygame.error:
            self.puzzle_background = None
        
        # Set up board positions and dimensions
        self.setup_board_positions()
        
        # Initialize garbage block tracking
        self.garbage_block_brightness = {}
        
        # Initialize persistent column rotators for each player
        self.player_column_rotator = ColumnRotator(grid_width=6)
        self.enemy_column_rotator = ColumnRotator(grid_width=6)
        
        # Initialize attack flow tracker for clean debug output
        self.attack_tracker = AttackFlowTracker()
        
        # UNIFIED ATTACK SPAWNING SYSTEM
        self.pending_attacks = {
            'player': [],  # Attacks waiting to spawn above player board
            'enemy': []    # Attacks waiting to spawn above enemy board
        }
        self.attack_spawn_delay = 1000  # 1 second delay before attacks start falling
        self.attack_fall_speed = 200   # 200ms between each attack block falling (faster for better visual)
        self.last_attack_spawn_time = 0
        self.last_attack_fall_time = 0
        
        # Initialize the puzzle battle
        self.initialize_test()
        
        print("✅ TestMode initialized with core functionality")
    
    def setup_board_positions(self):
        """Set up the positions for the player and enemy puzzle boards."""
        # Grid specifications
        grid_width = 6
        grid_height = 13
        
        # Use the actual block sizes from the engines instead of hardcoded values
        cell_width = self.player_engine.block_size
        cell_height = self.player_engine.block_size
        border_size = 10  # Space between container edge and the actual grid
        
        # Calculate board dimensions
        board_width = grid_width * cell_width
        board_height = grid_height * cell_height
        
        # Calculate proper centered positions
        screen_width = self.width
        board_spacing = 40  # Space between boards
        
        # Center calculation - include borders in the total width
        total_width_needed = (board_width * 2) + board_spacing + (border_size * 4)
        start_x = (screen_width - total_width_needed) // 2
        
        # Player board position (left side)
        player_x = start_x + border_size
        player_y = 80
        
        # Enemy board position (right side) 
        enemy_x = start_x + board_width + board_spacing + (border_size * 3)
        enemy_y = 80
        
        # Store positions
        self.player_grid_position = {"x": player_x, "y": player_y}
        self.enemy_grid_position = {"x": enemy_x, "y": enemy_y}
        
        # Update engine grid offsets for proper rendering
        self.player_engine.grid_x_offset = player_x
        self.player_engine.grid_y_offset = player_y
        self.enemy_engine.grid_x_offset = enemy_x
        self.enemy_engine.grid_y_offset = enemy_y
        
        # Update renderer coordinate offsets to match the new positions
        self.player_renderer.update_coordinate_offsets()
        self.enemy_renderer.update_coordinate_offsets()
        
        # Store cell dimensions for use in drawing
        self.cell_width = cell_width
        self.cell_height = cell_height
        self.board_width = board_width
        self.board_height = board_height
    
    def initialize_test(self):
        """Initialize or reset the test mode game state."""
        print("🔄 COMPREHENSIVE GAME RESET INITIATED...")
        
        # Reset chain states
        self.player_chain_position = 0
        self.enemy_chain_position = 0
        self.player_chain_active = False
        self.enemy_chain_active = False
        self.last_player_combo_time = 0
        self.last_enemy_combo_time = 0
        
        # Reset attack systems - PLAYER ONLY
        self.player_attack_system.clear_attacks()
        # Enemy attack system is disabled
        
        # Reset piece movement state for both engines
        self.player_engine.current_fall_speed = self.player_engine.normal_fall_speed
        self.player_engine.last_fall_time = pygame.time.get_ticks()
        self.player_engine.micro_fall_time = self.player_engine._calculate_micro_fall_time(self.player_engine.current_fall_speed)
        self.enemy_engine.current_fall_speed = self.enemy_engine.normal_fall_speed
        self.enemy_engine.last_fall_time = pygame.time.get_ticks()
        self.enemy_engine.micro_fall_time = self.enemy_engine._calculate_micro_fall_time(self.enemy_engine.current_fall_speed)
        
        # Reset engine state completely
        self.reset_engine_state(self.player_engine)
        self.reset_engine_state(self.enemy_engine)
        
        # Start both games
        self.player_engine.start_game()
        self.enemy_engine.start_game()
        
        # Reset renderer animation states
        self.reset_renderer_state(self.player_renderer)
        self.reset_renderer_state(self.enemy_renderer)
        
        # Update renderers
        self.player_renderer.update_visual_state()
        self.player_renderer.update_animations()
        self.enemy_renderer.update_visual_state()
        self.enemy_renderer.update_animations()
        
        # Reset garbage block state
        self.reset_garbage_block_state()
        
        # Reset unified attack spawning system
        self.pending_attacks = {'player': [], 'enemy': []}
        self.last_attack_spawn_time = 0
        self.last_attack_fall_time = 0
        
        # Clear any stuck alternators
        for player_key in ['player', 'enemy']:
            if hasattr(self, f'{player_key}_side_column_alternator'):
                delattr(self, f'{player_key}_side_column_alternator')
            if hasattr(self, f'{player_key}_side_layer_alternator'):
                delattr(self, f'{player_key}_side_layer_alternator')
        
        # Reset column rotators to ensure proper distribution
        self.player_column_rotator.reset_rotation()
        self.enemy_column_rotator.reset_rotation()
        
        print("✅ COMPREHENSIVE GAME RESET COMPLETED")
    
    def reset_engine_state(self, engine):
        """Reset all engine state including breakers, clusters, and animations."""
        # Reset core game state
        engine.chain_reaction_in_progress = False
        engine.breaking_blocks = []
        engine.clusters = set()
        engine.chain_state = "idle"
        engine.chain_count = 0
        engine.last_state_change = 0
        
        # Reset breaker detection state
        if hasattr(engine, 'last_cluster_check_time'):
            engine.last_cluster_check_time = 0
        
        # Reset animation state if renderer exists
        if hasattr(engine, 'renderer') and engine.renderer:
            if hasattr(engine.renderer, 'animation_manager'):
                engine.renderer.animation_manager.reset_animation_state()
        
        # Clear any pending animations
        if hasattr(engine, 'renderer') and engine.renderer:
            engine.renderer.clear_all_animations()
    
    def reset_renderer_state(self, renderer):
        """Reset renderer animation and visual state."""
        if hasattr(renderer, 'animation_manager'):
            renderer.animation_manager.reset_animation_state()
        
        # Clear any cluster highlights or visual effects
        if hasattr(renderer, 'cluster_highlights'):
            renderer.cluster_highlights.clear()
        
        # Reset visual state
        renderer.update_visual_state()
        renderer.update_animations()

    def reset_garbage_block_state(self):
        """Reset all garbage block transformation state."""
        self.garbage_block_brightness.clear()

    # UNIFIED ATTACK SPAWNING SYSTEM METHODS
    def queue_attack_spawn(self, target_player: str, attack_type: str, count: int, strike_details=None):
        """Queue an attack to spawn above the target player's board."""
        attack_data = {
            'type': attack_type,
            'count': count,
            'strike_details': strike_details,
            'spawn_time': pygame.time.get_ticks(),
            'blocks_remaining': count,
            'current_column': None,
            'current_row': -1  # Start above the board
        }
        
        self.pending_attacks[target_player].append(attack_data)
    
    def update_attack_spawning(self):
        """Update the attack spawning system - handle falling attacks."""
        current_time = pygame.time.get_ticks()
        
        # Process attacks for both players
        for player_key in ['player', 'enemy']:
            engine = self.player_engine if player_key == 'player' else self.enemy_engine
            column_rotator = self.player_column_rotator if player_key == 'player' else self.enemy_column_rotator
            
            # Process each pending attack
            attacks_to_remove = []
            for attack in self.pending_attacks[player_key]:
                # Check if it's time to start falling
                if current_time - attack['spawn_time'] < self.attack_spawn_delay:
                    continue  # Still waiting for spawn delay
                
                # Check if it's time for the next block to fall
                if current_time - self.last_attack_fall_time < self.attack_fall_speed:
                    continue  # Wait for fall timing
                
                # Safety check: if attack is too old, remove it to prevent infinite loops
                if current_time - attack['spawn_time'] > 10000:  # 10 seconds
                    print(f"[SPAWN DEBUG] Removing stuck attack for {player_key} (too old)")
                    attacks_to_remove.append(attack)
                    continue
                
                # Processing attack (debug output reduced)
                
                # Try to place the next block(s)
                blocks_placed = self.try_place_falling_attack_block(engine, attack, player_key)
                if blocks_placed:
                    # Track placed blocks
                    attack_type = 'strikes' if attack['type'] == 'strike' else 'garbage'
                    self.attack_tracker.track_placed(player_key, attack_type, blocks_placed)
                    
                    # For strikes, blocks_placed might be > 1, for garbage it's always 1
                    if attack['type'] == 'strike':
                        attack['blocks_remaining'] -= blocks_placed
                    else:
                        attack['blocks_remaining'] -= 1
                    
                    self.last_attack_fall_time = current_time
                    
                    # If all blocks placed, mark for removal
                    if attack['blocks_remaining'] <= 0:
                        attacks_to_remove.append(attack)
            
            # Remove completed attacks
            for attack in attacks_to_remove:
                self.pending_attacks[player_key].remove(attack)
    
    def try_place_falling_attack_block(self, engine, attack, player_key):
        """Try to place attack blocks with proper falling animation from above the board."""
        grid = engine.puzzle_grid
        player = 1 if player_key == 'player' else 2
        column_rotator = self.player_column_rotator if player_key == 'player' else self.enemy_column_rotator
        
        # Handle strike attacks with proper dimensions and falling
        if attack['type'] == 'strike':
            return self.place_strike_with_falling(engine, attack, player_key, column_rotator)
        
        # Handle garbage attacks with falling animation
        return self.place_garbage_with_falling(engine, attack, player_key, column_rotator)
    
    def place_garbage_with_falling(self, engine, attack, player_key, column_rotator):
        """Place garbage blocks as a single payload (not individual falling blocks)."""
        grid = engine.puzzle_grid
        player = 1 if player_key == 'player' else 2
        blocks_remaining = attack['blocks_remaining']
        
        print(f"[SPAWN DEBUG] Placing {blocks_remaining} garbage blocks for {player_key} as single payload")
        
        # Place all garbage blocks instantly as a group (like classic puzzle games)
        return self.place_garbage_payload(engine, attack, player_key, column_rotator)
    
    def place_garbage_payload(self, engine, attack, player_key, column_rotator):
        """Place all garbage blocks at once as a single payload."""
        grid = engine.puzzle_grid
        player = 1 if player_key == 'player' else 2
        blocks_to_place = attack['blocks_remaining']
        
        colors = ['red', 'blue', 'green', 'yellow']
        color = colors[blocks_to_place % len(colors)]
        
        blocks_placed = 0
        columns_to_use = [0, 1, 2, 3, 4, 5]  # Use all columns
        
        # Place blocks across multiple columns
        for block_num in range(blocks_to_place):
            placed = False
            
            # Try each column until we find space
            for column in columns_to_use:
                # Find the lowest available position in this column
                for row in range(engine.grid_height - 1, -1, -1):
                    if grid[row][column] in ['empty', None]:
                        # Place the garbage block
                        block_type = f"{color}_garbage"
                        grid[row][column] = block_type
                        
                        # Track for transformation
                        tracking_key = (column, row, player)
                        self.garbage_block_brightness[tracking_key] = {
                            'landings': 0,
                            'color': color,
                            'is_strike': False
                        }
                        
                        blocks_placed += 1
                        placed = True
                        break
                
                if placed:
                    break
            
            if not placed:
                # No more space available
                break
        
        print(f"[SPAWN DEBUG] Placed {blocks_placed}/{blocks_to_place} garbage blocks as payload for {player_key}")
        
        # Mark attack as completed
        attack['blocks_remaining'] = 0
        return blocks_placed
    
    def place_single_garbage_with_falling(self, engine, attack, player_key, column_rotator):
        """Place a single garbage block with proper falling animation from above the board."""
        grid = engine.puzzle_grid
        player = 1 if player_key == 'player' else 2
        
        # Use proper column rotation for attacks
        if attack.get('current_column') is None:
            # First time placing - get next column from rotator
            attack['current_column'] = column_rotator.get_next_column()
            attack['current_row'] = -1  # Start above the visible grid
            print(f"[SPAWN DEBUG] Starting new garbage block at column {attack['current_column']} (above board)")
        
        column = attack['current_column']
        current_row = attack['current_row']
        
        # Find the landing position for this column
        landing_row = -1
        for row in range(engine.grid_height - 1, -1, -1):  # Start from bottom
            if grid[row][column] in ['empty', None]:
                landing_row = row
                break
        
        # Check if column is full
        if landing_row == -1:
            print(f"[SPAWN DEBUG] Column {column} is full, trying next column")
            # Try next column
            attack['current_column'] = column_rotator.get_next_column()
            attack['current_row'] = -1
            return 0  # Try again next frame
        
        # Move the block down one row
        next_row = current_row + 1
        
        # Check if we've reached the landing position
        if next_row >= landing_row:
            # Place the garbage block at the landing position
            colors = ['red', 'blue', 'green', 'yellow']
            color = colors[attack['count'] % len(colors)]
            block_type = f"{color}_garbage"
            
            grid[landing_row][column] = block_type
            
            # Track for transformation
            tracking_key = (column, landing_row, player)
            self.garbage_block_brightness[tracking_key] = {
                'landings': 0,
                'color': color,
                'is_strike': False
            }
            
            print(f"[SPAWN DEBUG] Garbage block landed at ({column}, {landing_row}) for {player_key}")
            return 1  # Return 1 block placed
        
        # Update the falling position
        attack['current_row'] = next_row
        
        # If block is now visible on the grid, show it falling
        if next_row >= 0 and next_row < engine.grid_height:
            # Clear previous position if it was on the grid
            if current_row >= 0 and current_row < engine.grid_height:
                if grid[current_row][column] and 'falling' in str(grid[current_row][column]):
                    grid[current_row][column] = 'empty'
            
            # Place falling block at new position
            colors = ['red', 'blue', 'green', 'yellow']
            color = colors[attack['count'] % len(colors)]
            block_type = f"{color}_garbage_falling"  # Mark as falling
            
            grid[next_row][column] = block_type
            print(f"[SPAWN DEBUG] Garbage block falling at ({column}, {next_row}) for {player_key}")
        
        return 0  # Block is still falling, not placed yet
    
    def place_garbage_layer_with_falling(self, engine, attack, player_key, column_rotator):
        """Place multiple garbage blocks as individual falling blocks from above."""
        # For larger attacks, we'll place them one at a time to ensure proper falling animation
        # This simplifies the logic and ensures all blocks fall from above
        print(f"[SPAWN DEBUG] Using single-block falling for {attack['blocks_remaining']} blocks to ensure proper animation")
        return self.place_single_garbage_with_falling(engine, attack, player_key, column_rotator)
    
    def place_strike_with_falling(self, engine, attack, player_key, column_rotator):
        """Place a strike attack with proper dimensions and falling animation from above the board."""
        grid = engine.puzzle_grid
        player = 1 if player_key == 'player' else 2
        strike_details = attack.get('strike_details', [])
        strike_count = attack['count']
        
        # If no strike details provided, create default pattern based on strike count
        if not strike_details:
            # Create strike patterns: 1x8 for most strikes (classic puzzle style)
            width, height = 1, min(8, strike_count)  # Max 1x8 strikes
            print(f"[SPAWN DEBUG] Creating default 1x{height} strike pattern for {strike_count} strikes")
        else:
            # Parse strike dimensions (e.g., "3x4" -> width=3, height=4)
            try:
                dimensions = strike_details[0]  # Take the first dimension if multiple
                if 'x' in dimensions:
                    width, height = map(int, dimensions.split('x'))
                else:
                    # Fallback for single dimension
                    width, height = 1, int(dimensions)
            except (ValueError, IndexError):
                print(f"[SPAWN DEBUG] Invalid strike dimensions: {strike_details}, using default")
                width, height = 1, min(8, strike_count)
        
        print(f"[SPAWN DEBUG] Placing strike with dimensions {width}x{height} (fell from above)")
        
        # Find a suitable starting column that can accommodate the strike width
        # Use column rotator properly for strikes
        start_column = self.find_strike_starting_column(engine, width, column_rotator)
        if start_column is None:
            print(f"[SPAWN DEBUG] No suitable column found for strike {width}x{height}")
            return False
        
        # Find the highest landing position for the entire strike
        max_placement_row = engine.grid_height - 1
        for col in range(start_column, start_column + width):
            placement_row = engine.grid_height - 1
            while placement_row >= 0 and grid[placement_row][col] not in ['empty', None]:
                placement_row -= 1
            max_placement_row = min(max_placement_row, placement_row)
        
        # Check if we have enough vertical space, and truncate if necessary
        if max_placement_row - height + 1 < 0:
            # Truncate the strike height to fit
            original_height = height
            height = max_placement_row + 1
            print(f"[SPAWN DEBUG] Strike height truncated from {original_height} to {height} to fit")
        
        # Place the strike blocks (they appear to fall from above)
        colors = ['red', 'blue', 'green', 'yellow']
        color = colors[attack['count'] % len(colors)]
        
        blocks_placed = 0
        for col in range(start_column, start_column + width):
            for row in range(max_placement_row - height + 1, max_placement_row + 1):
                if grid[row][col] in ['empty', None]:
                    block_type = f"{color}_strike"  # Use distinct strike visual
                    grid[row][col] = block_type
                    
                    # Track for transformation
                    tracking_key = (col, row, player)
                    self.garbage_block_brightness[tracking_key] = {
                        'landings': 0,
                        'color': color,
                        'is_strike': True
                    }
                    
                    blocks_placed += 1
        
        side = "left" if start_column < 3 else "right"
        print(f"[SPAWN DEBUG] Placed strike {width}x{height} ({blocks_placed} blocks) starting at ({start_column}, {max_placement_row - height + 1}) for {player_key} (fell from {side} side)")
        return blocks_placed > 0

    def find_strike_starting_column(self, engine, strike_width, column_rotator):
        """Find a suitable starting column for a strike that can accommodate its width using column rotation."""
        grid = engine.puzzle_grid
        
        # Use column rotator to get the next column, then check if strike fits
        base_column = column_rotator.get_next_column()
        
        # Try the rotated column first, then nearby columns if it doesn't fit
        column_options = []
        
        # Add the rotated column
        if base_column + strike_width <= engine.grid_width:
            column_options.append(base_column)
        
        # If strike doesn't fit at rotated column, try adjacent columns
        for offset in [-1, 1, -2, 2]:
            start_col = base_column + offset
            if 0 <= start_col and start_col + strike_width <= engine.grid_width:
                column_options.append(start_col)
        
        # Try each column option
        for start_col in column_options:
            # Check if there's at least some space in these columns
            has_space = False
            for col in range(start_col, start_col + strike_width):
                for row in range(engine.grid_height):
                    if grid[row][col] in ['empty', None]:
                        has_space = True
                        break
                if has_space:
                    break
            
            if has_space:
                return start_col
        
        return None

    def update(self) -> Optional[str]:
        """Update the test mode state."""
        current_time = pygame.time.get_ticks()
        
        # Update player engine
        self.player_engine.update()
        
        # Update enemy engine with simple AI
        self.enemy_engine.update()
        
        # Update unified attack spawning system
        self.update_attack_spawning()
        
        # Print attack flow summary periodically
        if self.attack_tracker.should_print_summary():
            self.attack_tracker.print_summary()
        
        # Simple AI movement (much simpler than original)
        if random.random() < 0.05:  # 5% chance each frame
            move_choice = random.random()
            
            try:
                if move_choice < 0.4:  # 40% chance to move left/right
                    self.enemy_engine.move_piece(random.choice([-1, 1]), 0)
                elif move_choice < 0.6:  # 20% chance to rotate
                    self.enemy_engine.rotate_attached_piece(random.choice([-1, 1]))
                else:  # 40% chance to accelerate drop
                    self.enemy_engine.move_piece(0, 1)
            except Exception as e:
                # Ignore AI movement errors - not critical
                pass
        
        # Check for chain timeouts for BOTH players
        if self.player_chain_active and (current_time - self.last_player_combo_time) > self.chain_window_duration:
            self.end_player_chain()
        
        if self.enemy_chain_active and (current_time - self.last_enemy_combo_time) > self.chain_window_duration:
            self.end_enemy_chain()
        
        # Check for game over conditions
        if not self.player_engine.game_active or not self.enemy_engine.game_active:
            print("🎮 GAME OVER DETECTED - AUTO-RESETTING...")
            # Automatically reset the game after a short delay
            self.initialize_test()
            return None  # Continue playing instead of returning game_over
        
        return None
    
    def process_events(self, events: List) -> Optional[str]:
        """Process input events for the test mode."""
        # Let the player engine handle its own events first
        self.player_engine.process_events(events)
        
        # Handle test mode specific events
        for event in events:
            if event.type == pygame.KEYDOWN:
                # Escape key to return to menu
                if event.key == pygame.K_ESCAPE:
                    return "back_to_menu"
        
        return None
    
    def handle_player_blocks_broken(self, broken_blocks, is_cluster, combo_multiplier):
        """Handle blocks broken by player - generate attacks"""
        current_time = pygame.time.get_ticks()
        
        # Detect clusters in the broken blocks
        clusters = self.player_attack_system.detect_clusters(broken_blocks)
        
        # Determine chain position
        if not self.player_chain_active:
            self.player_chain_position = 1
            self.player_chain_active = True
        else:
            self.player_chain_position += 1
        
        # Process the combo and generate attacks
        new_attacks = self.player_attack_system.process_combo(
            broken_blocks, clusters, self.player_chain_position
        )
        
        # Update chain timing
        self.last_player_combo_time = current_time
        
        # Track and display clean combo results
        attacks = self.player_attack_system.get_pending_attacks()
        strikes = sum(a.count for a in attacks if a.attack_type == "strike")
        garbage = sum(a.count for a in attacks if a.attack_type == "garbage")
        
        if strikes > 0 or garbage > 0:
            combo_info = {
                'chain_pos': self.player_chain_position,
                'strikes': strikes,
                'garbage': garbage
            }
            self.attack_tracker.track_combo_result('player', combo_info)
            
            # Track sent attacks
            if strikes > 0:
                self.attack_tracker.track_sent('player', 'strikes', strikes)
            if garbage > 0:
                self.attack_tracker.track_sent('player', 'garbage', garbage)
        
        # Send attacks to enemy immediately
        self.send_player_attacks_to_enemy()
    
    def handle_enemy_blocks_broken(self, broken_blocks, is_cluster, combo_multiplier):
        """Handle blocks broken by enemy - generate attacks"""
        current_time = pygame.time.get_ticks()
        
        # Detect clusters in the broken blocks
        clusters = self.enemy_attack_system.detect_clusters(broken_blocks)
        
        # Determine chain position
        if not self.enemy_chain_active:
            self.enemy_chain_position = 1
            self.enemy_chain_active = True
        else:
            self.enemy_chain_position += 1
        
        # Process the combo and generate attacks
        new_attacks = self.enemy_attack_system.process_combo(
            broken_blocks, clusters, self.enemy_chain_position
        )
        
        # Update chain timing
        self.last_enemy_combo_time = current_time
        
        # Track and display clean combo results
        attacks = self.enemy_attack_system.get_pending_attacks()
        strikes = sum(a.count for a in attacks if a.attack_type == "strike")
        garbage = sum(a.count for a in attacks if a.attack_type == "garbage")
        
        if strikes > 0 or garbage > 0:
            combo_info = {
                'chain_pos': self.enemy_chain_position,
                'strikes': strikes,
                'garbage': garbage
            }
            self.attack_tracker.track_combo_result('enemy', combo_info)
            
            # Track sent attacks
            if strikes > 0:
                self.attack_tracker.track_sent('enemy', 'strikes', strikes)
            if garbage > 0:
                self.attack_tracker.track_sent('enemy', 'garbage', garbage)
        
        # Send attacks to player immediately
        self.send_enemy_attacks_to_player()
    
    def end_player_chain(self):
        """End the player's chain and send final attacks."""
        if self.player_chain_active:
            print(f"🎯 Player chain ended at {self.player_chain_position}x")
            self.send_player_attacks_to_enemy()
            self.player_chain_active = False
            self.player_chain_position = 0
    
    def end_enemy_chain(self):
        """End the enemy's chain and send final attacks."""
        if self.enemy_chain_active:
            print(f"🎯 Enemy chain ended at {self.enemy_chain_position}x")
            self.send_enemy_attacks_to_player()
            self.enemy_chain_active = False
            self.enemy_chain_position = 0
    
    def send_player_attacks_to_enemy(self):
        """Send player's pending attacks to enemy using unified spawning system."""
        attacks = self.player_attack_system.get_pending_attacks()
        if not attacks:
            return
        
        # Queue attacks to spawn above enemy board
        for attack in attacks:
            if attack.attack_type == "garbage":
                self.queue_attack_spawn('enemy', 'garbage', attack.count)
                self.attack_tracker.track_queued('enemy', 'garbage', attack.count)
            elif attack.attack_type == "strike":
                strike_details = getattr(attack, 'strike_details', None)
                self.queue_attack_spawn('enemy', 'strike', attack.count, strike_details)
                self.attack_tracker.track_queued('enemy', 'strikes', attack.count)
        
        # Clear the attacks after queuing
        self.player_attack_system.clear_attacks()
    
    def send_enemy_attacks_to_player(self):
        """Send enemy's pending attacks to player using unified spawning system."""
        attacks = self.enemy_attack_system.get_pending_attacks()
        if not attacks:
            return
        
        # Queue attacks to spawn above player board
        for attack in attacks:
            if attack.attack_type == "garbage":
                self.queue_attack_spawn('player', 'garbage', attack.count)
                self.attack_tracker.track_queued('player', 'garbage', attack.count)
            elif attack.attack_type == "strike":
                strike_details = getattr(attack, 'strike_details', None)
                self.queue_attack_spawn('player', 'strike', attack.count, strike_details)
                self.attack_tracker.track_queued('player', 'strikes', attack.count)
        
        # Clear the attacks after queuing
        self.enemy_attack_system.clear_attacks()

    # OLD DIRECT PLACEMENT METHODS REMOVED - Now using unified spawning system

    def on_piece_landed(self, player):
        """Called when a piece lands - increment landing counters for nearby garbage blocks."""
        print(f"[CALLBACK DEBUG] on_piece_landed called for player {player}")
        
        # Get the engine for this player
        engine = self.player_engine if player == 1 else self.enemy_engine
        grid = engine.puzzle_grid
        
        # Find all garbage blocks for this player and increment their landing counters
        blocks_to_increment = []
        for pos_key, data in self.garbage_block_brightness.items():
            x, y, block_player = pos_key
            if block_player == player:
                # Check if this garbage block is still in the grid
                if 0 <= y < len(grid) and 0 <= x < len(grid[0]) and grid[y][x] and '_garbage' in grid[y][x]:
                    blocks_to_increment.append(pos_key)
        
        print(f"[VISUAL DEBUG] on_piece_landed called for player {player}. Tracked blocks: {len(blocks_to_increment)}")
        
        # Increment landing counters
        for pos_key in blocks_to_increment:
            self.garbage_block_brightness[pos_key]['landings'] += 1
            print(f"[VISUAL DEBUG] Incremented landing counter for {pos_key}: {self.garbage_block_brightness[pos_key]['landings']} landings")
        
        # Check for transformations
        to_transform = []
        for pos_key, data in self.garbage_block_brightness.items():
            x, y, block_player = pos_key
            if block_player == player:
                # Check if this block should transform
                is_strike = data.get('is_strike', False)
                required_landings = 3 if is_strike else 2  # Strikes take 1 turn longer
                
                if data['landings'] >= required_landings:
                    # This block should transform
                    color = data['color']
                    to_transform.append((pos_key, f"{color}_block"))
        
        if to_transform:
            print(f"[VISUAL DEBUG] Transforming {len(to_transform)} blocks for player {player}")
            self.transform_garbage_blocks(to_transform)
        
        # Debug: Show all tracked blocks
        print(f"[VISUAL DEBUG] All tracked garbage blocks:")
        for pos_key, data in self.garbage_block_brightness.items():
            block_type = "strike" if data.get('is_strike', False) else "garbage"
            print(f"    {pos_key} for player {pos_key[2]}: landings={data['landings']}, color={data['color']}, type={block_type}")
    
    # place_cluster_strike method removed - cluster strike system disabled

    def transform_garbage_blocks(self, to_transform):
        """Transform garbage blocks to normal colored blocks."""
        for pos_key, new_block_type in to_transform:
            x, y, player = pos_key
            engine = self.player_engine if player == 1 else self.enemy_engine
            grid = engine.puzzle_grid
            
            # Transform the block
            if y < len(grid) and x < len(grid[0]):
                old_block_type = grid[y][x]
                grid[y][x] = new_block_type
                print(f"[VISUAL DEBUG] TRANSFORMED: ({x}, {y}) from {old_block_type} to {new_block_type} for player {player}")
                
                # Remove from tracking
                if pos_key in self.garbage_block_brightness:
                    del self.garbage_block_brightness[pos_key]

    def _create_player_engine(self):
        """Creates a puzzle engine instance for the player."""
        engine = PuzzleEngine(self.screen, self.font, self.audio, self.asset_path)
        engine.renderer = PuzzleRenderer(engine)
        engine.renderer.preview_side = 'left'  # Player on the left
        return engine

    def _create_enemy_engine(self):
        """Creates a puzzle engine instance for the enemy."""
        engine = PuzzleEngine(self.screen, self.font, self.audio, self.asset_path)
        engine.renderer = PuzzleRenderer(engine)
        engine.renderer.preview_side = 'right'  # Enemy on the right
        return engine

    def draw(self):
        """Draws the test mode screen, including both puzzle grids."""
        # Draw background
        self.screen.fill((10, 10, 30))  # Dark blue background
        
        # Add atmospheric gradient effect
        for i in range(20):
            alpha = 150 - (i * 7)
            if alpha < 0:
                alpha = 0
            gradient = pygame.Surface((self.width, 5), pygame.SRCALPHA)
            gradient.fill((50, 50, 80, alpha))
            self.screen.blit(gradient, (0, i * 20))
            self.screen.blit(gradient, (0, self.height - (i * 20)))
        
        # Draw title at top
        title_font = pygame.font.SysFont(None, 48)
        title_text = title_font.render("Puzzle Battle", True, self.WHITE)
        title_rect = title_text.get_rect(midtop=(self.width // 2, 20))
        # Add glow effect
        glow_text = title_font.render("Puzzle Battle", True, self.LIGHT_BLUE)
        glow_rect = glow_text.get_rect(midtop=(self.width // 2 + 2, 22))
        self.screen.blit(glow_text, glow_rect)
        self.screen.blit(title_text, title_rect)
        
        # Use stored dimensions from setup_board_positions
        cell_width = self.cell_width
        cell_height = self.cell_height
        border_size = 10
        board_width = self.board_width
        board_height = self.board_height
        
        # Draw player board container
        player_container = pygame.Rect(
            self.player_grid_position["x"] - border_size,
            self.player_grid_position["y"] - 35,
            board_width + (border_size * 2),
            board_height + 35 + border_size
        )
        pygame.draw.rect(self.screen, (30, 30, 60), player_container, border_radius=5)
        pygame.draw.rect(self.screen, (100, 100, 255), player_container, 3, border_radius=5)
        
        # Draw enemy board container
        enemy_container = pygame.Rect(
            self.enemy_grid_position["x"] - border_size,
            self.enemy_grid_position["y"] - 35,
            board_width + (border_size * 2),
            board_height + 35 + border_size
        )
        pygame.draw.rect(self.screen, (30, 30, 60), enemy_container, border_radius=5)
        pygame.draw.rect(self.screen, (255, 100, 100), enemy_container, 3, border_radius=5)  # Red for enemy
        
        # Draw puzzle backgrounds if available
        if self.puzzle_background:
            scaled_bg = pygame.transform.scale(self.puzzle_background, (board_width, board_height))
            
            # Player board background
            self.screen.blit(scaled_bg, (self.player_grid_position["x"], self.player_grid_position["y"]))
            
            # Enemy board background
            self.screen.blit(scaled_bg, (self.enemy_grid_position["x"], self.enemy_grid_position["y"]))
        
        # Update animations before drawing
        self.player_renderer.update_visual_state()
        self.player_renderer.update_animations()
        self.enemy_renderer.update_visual_state()
        self.enemy_renderer.update_animations()
        
        # Draw player grid and pieces using the new coordinated method
        self.player_renderer.draw_game_content()

        # Draw Player 2's (Enemy) grid using the new coordinated method
        self.enemy_renderer.draw_game_content()

        # Draw player title
        player_title = self.font.render("Player 1", True, (255, 255, 255))
        self.screen.blit(player_title, (self.player_grid_position["x"], self.player_grid_position["y"] - 30))
        
        # Draw enemy title
        enemy_title = pygame.font.SysFont(None, 28).render("AI", True, (255, 100, 100))
        enemy_title_rect = enemy_title.get_rect(midtop=(
            self.enemy_grid_position["x"] + (board_width / 2), 
            self.enemy_grid_position["y"] - 30
        ))
        self.screen.blit(enemy_title, enemy_title_rect)
        
        # Draw simple controls instruction
        controls_font = pygame.font.SysFont(None, 20)
        controls_text = "Arrow Keys: Move | Z/X: Rotate | Space: Drop | ESC: Menu"
        controls_surface = controls_font.render(controls_text, True, self.GRAY)
        controls_rect = controls_surface.get_rect(center=(self.width // 2, self.height - 30))
        self.screen.blit(controls_surface, controls_rect)
        
        # Draw database status indicator
        if hasattr(self, 'database_enabled'):
            db_color = (0, 255, 0) if self.database_enabled else (255, 0, 0)
            db_text = "DATABASE: ON" if self.database_enabled else "DATABASE: OFF"
            db_surface = controls_font.render(db_text, True, db_color)
            db_rect = db_surface.get_rect(center=(self.width // 2, self.height - 50))
            self.screen.blit(db_surface, db_rect)
        
        # Draw pending attack indicators
        self.draw_pending_attack_indicators() 

    def draw_pending_attack_indicators(self):
        """Draw visual indicators for pending attacks above the boards."""
        current_time = pygame.time.get_ticks()
        
        # Draw indicators for player board (enemy attacks)
        if self.pending_attacks['player']:
            self.draw_attack_indicator(self.player_grid_position, self.pending_attacks['player'], current_time)
        
        # Draw indicators for enemy board (player attacks)
        if self.pending_attacks['enemy']:
            self.draw_attack_indicator(self.enemy_grid_position, self.pending_attacks['enemy'], current_time)
    
    def draw_attack_indicator(self, board_position, attacks, current_time):
        """Draw attack indicators above a specific board."""
        indicator_y = board_position["y"] - 20  # Above the board
        
        for i, attack in enumerate(attacks):
            # Calculate time until spawn
            time_until_spawn = max(0, self.attack_spawn_delay - (current_time - attack['spawn_time']))
            
            if time_until_spawn > 0:
                # Show countdown
                countdown_text = f"Attack in {time_until_spawn // 1000}s"
                color = (255, 255, 0) if time_until_spawn < 1000 else (255, 100, 100)  # Yellow then red
            else:
                # Show falling indicator
                countdown_text = f"Falling: {attack['blocks_remaining']} blocks"
                color = (100, 255, 100)  # Green
            
            # Draw the indicator
            indicator_font = pygame.font.SysFont(None, 16)
            indicator_surface = indicator_font.render(countdown_text, True, color)
            indicator_rect = indicator_surface.get_rect(
                center=(board_position["x"] + self.board_width // 2, indicator_y + i * 15)
            )
            self.screen.blit(indicator_surface, indicator_rect) 