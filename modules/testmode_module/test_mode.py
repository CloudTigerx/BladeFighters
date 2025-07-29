"""
Simplified TestMode Implementation
Core puzzle battle functionality: 2 grids, piece previews, backgrounds.
Stripped of attack system complexity to focus on essential gameplay.
"""

import pygame
import os
import random
import time
from typing import List, Dict, Optional, Any

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
from modules.attack_module.attack_manager import AttackManager

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
        
        # Initialize attack system
        self.attack_manager = AttackManager()
        
        # Connect attack system handlers
        self.player_engine.blocks_broken_handler = self.handle_player_blocks_broken
        self.enemy_engine.blocks_broken_handler = self.handle_enemy_blocks_broken
        
        # Load background images
        try:
            self.puzzle_background = pygame.image.load(os.path.join(asset_path, "puzzlebackground.jpg"))
        except pygame.error:
            self.puzzle_background = None
        
        # Set up board positions and dimensions
        self.setup_board_positions()
        
        # Garbage block tracking for transformation system
        self.garbage_block_brightness = {}  # Format: {(x, y, player): {'landings': 0, 'color': 'red'}}
        
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
        # Reset piece movement state for both engines
        self.player_engine.current_fall_speed = self.player_engine.normal_fall_speed
        self.player_engine.last_fall_time = pygame.time.get_ticks()
        self.player_engine.micro_fall_time = self.player_engine._calculate_micro_fall_time(self.player_engine.current_fall_speed)
        self.enemy_engine.current_fall_speed = self.enemy_engine.normal_fall_speed
        self.enemy_engine.last_fall_time = pygame.time.get_ticks()
        self.enemy_engine.micro_fall_time = self.enemy_engine._calculate_micro_fall_time(self.enemy_engine.current_fall_speed)
        # Start both games
        self.player_engine.start_game()
        self.enemy_engine.start_game()
        
        # Update renderers
        self.player_renderer.update_visual_state()
        self.enemy_renderer.update_visual_state()
        # Reset garbage block state
        self.reset_garbage_block_state()

    def reset_garbage_block_state(self):
        """Reset all garbage block transformation state."""
        self.garbage_block_brightness.clear()

    def update(self) -> Optional[str]:
        """Update the test mode state."""
        # Update player engine
        self.player_engine.update()
        
        # Update enemy engine with simple AI
        self.enemy_engine.update()
        
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
        
        # ATTACK DELIVERY SYSTEM
        # Process attack queues and deliver ready attacks
        current_time = time.time()
        ready_attacks = self.attack_manager.process_attack_queue(current_time)
        
        # Apply ready attacks to player 1
        if ready_attacks['player1']:
            for attack in ready_attacks['player1']:
                self.apply_attack_to_player(attack, 1)
        
        # Apply ready attacks to player 2  
        if ready_attacks['player2']:
            for attack in ready_attacks['player2']:
                self.apply_attack_to_player(attack, 2)
        
        # Check for game over conditions
        if not self.player_engine.game_active or not self.enemy_engine.game_active:
            return "game_over"
        
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
        print(f"🎯 PLAYER COMBO DETECTED:")
        print(f"   Blocks broken: {len(broken_blocks)}")
        print(f"   Is cluster: {is_cluster}")
        print(f"   Combo multiplier: {combo_multiplier}")
        
        # Generate attacks using the attack manager
        result = self.attack_manager.process_combo(
            broken_blocks=broken_blocks,
            is_cluster=is_cluster,
            combo_multiplier=combo_multiplier,
            player_id=1  # Player is player 1
        )
        
        print(f"🎯 Generated attack: {result['garbage_blocks']} garbage blocks")
        print(f"🎯 Attack result: {result}")
        
        # If we have garbage blocks, place them immediately for testing
        if result['garbage_blocks'] > 0:
            print(f"🎯 PLACING GARBAGE BLOCKS: {result['garbage_blocks']} blocks")
            # Get a random column for placement
            column = random.randint(0, 5)  # 6 columns (0-5)
            print(f"🎯 Using column: {column}")
            self.place_garbage_blocks(self.enemy_engine, column, result['garbage_blocks'])
            print(f"🎯 Garbage blocks placed successfully!")
        else:
            print(f"🎯 No garbage blocks to place")
    
    def handle_enemy_blocks_broken(self, broken_blocks, is_cluster, combo_multiplier):
        """Handle blocks broken by enemy - generate attacks"""
        print(f"🎯 Enemy broke {len(broken_blocks)} blocks (cluster: {is_cluster}, combo: {combo_multiplier})")
        
        # Generate attacks using the attack manager
        result = self.attack_manager.process_combo(
            broken_blocks=broken_blocks,
            is_cluster=is_cluster,
            combo_multiplier=combo_multiplier,
            player_id=2  # Enemy is player 2
        )
        
        print(f"🎯 Generated attack: {result['garbage_blocks']} garbage blocks")
        print(f"🎯 Attack result: {result}")
        
        # If we have garbage blocks, place them immediately for testing
        if result['garbage_blocks'] > 0:
            print(f"🎯 PLACING GARBAGE BLOCKS: {result['garbage_blocks']} blocks")
            # Get a random column for placement
            column = random.randint(0, 5)  # 6 columns (0-5)
            print(f"🎯 Using column: {column}")
            self.place_garbage_blocks(self.player_engine, column, result['garbage_blocks'])
            print(f"🎯 Garbage blocks placed successfully!")
        else:
            print(f"🎯 No garbage blocks to place")
    
    def apply_attack_to_player(self, attack_payload, target_player: int):
        """Apply an attack to the specified player's puzzle grid."""
        engine = self.player_engine if target_player == 1 else self.enemy_engine
        print(f"🎯 DELIVERING ATTACK to Player {target_player}:")
        print(f"   Attack type: {attack_payload.attack_type.name}")
        if attack_payload.attack_type.name == "GARBAGE_BLOCKS":
            block_count = attack_payload.block_count
            # Place each garbage block in the next column in rotation
            for _ in range(block_count):
                column = self.attack_manager.get_next_column_for_attack(target_player)
                self.place_garbage_blocks(engine, column, 1)
        elif attack_payload.attack_type.name == "CLUSTER_STRIKE":
            # CLUSTER STRIKE SYSTEM DISABLED - Convert to garbage blocks instead
            print(f"   Cluster strike disabled - converting to garbage blocks")
            # Convert cluster strike to garbage blocks for simplicity
            block_count = 2  # Default conversion
            for _ in range(block_count):
                column = self.attack_manager.get_next_column_for_attack(target_player)
                self.place_garbage_blocks(engine, column, 1)
        print(f"   Attack delivered successfully!")
    
    def place_garbage_blocks(self, engine, column: int, count: int):
        """Place garbage blocks on the puzzle grid with landing-based transformation tracking."""
        grid = engine.puzzle_grid
        player = 1 if engine == self.player_engine else 2
        
        # Find the actual landing position (bottom-up search)
        # Use grid_height (15) instead of total_grid_height (16) to stay in visible area
        placement_row = engine.grid_height - 1  # Start at row 14 (bottom)
        
        # Find the first empty row from bottom up
        # Check for both 'empty' and None values (None is what the grid actually contains)
        while placement_row >= 0 and grid[placement_row][column] not in ['empty', None]:
            placement_row -= 1
        
        if placement_row < 0:
            print(f"[PLACEMENT DEBUG] Column {column} is full, cannot place garbage blocks")
            return
        
        # Place the garbage blocks
        colors = ['red', 'blue', 'green', 'yellow']
        for i in range(count):
            if placement_row - i >= 0:
                color = colors[i % len(colors)]
                block_type = f"{color}_garbage"
                grid[placement_row - i][column] = block_type
                
                # Track this garbage block for transformation
                tracking_key = (column, placement_row - i, player)
                self.garbage_block_brightness[tracking_key] = {
                    'landings': 0,
                    'color': color
                }
        
        print(f"[PLACEMENT DEBUG] Successfully placed {count} garbage blocks starting at row {placement_row}")

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
            if block_player == player and data['landings'] >= 2:
                # This garbage block should transform
                color = data['color']
                to_transform.append((pos_key, f"{color}_block"))
        
        if to_transform:
            print(f"[VISUAL DEBUG] Transforming {len(to_transform)} garbage blocks for player {player}")
            self.transform_garbage_blocks(to_transform)
        
        # Debug: Show all tracked blocks
        print(f"[VISUAL DEBUG] All tracked garbage blocks:")
        for pos_key, data in self.garbage_block_brightness.items():
            print(f"    {pos_key} for player {pos_key[2]}: landings={data['landings']}, color={data['color']}")
    
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