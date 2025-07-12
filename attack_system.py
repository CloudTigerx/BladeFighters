import pygame
import random
from enum import Enum
import time

class AttackType(Enum):
    GARBAGE_BLOCK = "garbage_block"
    STRIKE = "strike"  # New attack type for strikes

class GarbageBlockState(Enum):
    SOLID_GRAY = 0
    COLORED_GRAY = 1
    NORMAL = 2

class AttackSystem:
    def __init__(self, grid_width, grid_height):
        self.grid_width = grid_width
        self.grid_height = grid_height
        
        # Attack queues for both players
        self.player1_attacks = []
        self.player2_attacks = []
        
        # Column placement pattern (2,3,4,5,6,1)
        self.column_pattern = [1, 2, 3, 4, 5, 0]
        self.current_column_index = 0
        
        # Track garbage blocks and their transformation timers
        self.garbage_blocks = {}  # (x, y) -> (start_time, color)
        
        # Track strike blocks and their transformation timers
        self.strike_blocks = {}  # (x, y) -> (start_time, color, height_index)
        
        # Pending garbage blocks (gathered until ready to drop all at once)
        self.pending_player1_garbage = []  # List of (column, color) tuples
        self.pending_player2_garbage = []  # List of (column, color) tuples
        
        # Track whether we're ready to process the next batch of garbage
        self.player1_garbage_ready = False
        self.player2_garbage_ready = False
        
        # Attack delay based on player speed
        self.attack_delay = 0.5  # seconds
        self.batch_timer = 0  # Used to time when to drop garbage batches
        
        # Transformation timer (3.2 seconds)
        self.transformation_time = 3.2  # seconds
        
        # Strike transformation timer (half the time of garbage blocks)
        self.strike_transformation_time = self.transformation_time / 2
    
    def generate_attack(self, broken_blocks, is_cluster, combo_multiplier, color):
        """Generate garbage block attacks based on broken blocks."""
        attacks = []
        
        # Check for 2x2 cluster without combo (which generates a strike)
        if is_cluster and len(broken_blocks) == 4 and combo_multiplier <= 1:
            # Create strike attack
            attacks.append({
                "type": AttackType.STRIKE,
                "color": color,
                "size": "1x4"  # Size of the strike (one column wide, four blocks high)
            })
            print(f"Generated 1x4 strike attack with color {color}")
        else:
            # Regular garbage block attacks
            # Convert broken blocks to garbage blocks (2 blocks = 1 garbage block)
            garbage_blocks = len(broken_blocks) // 2
            
            # Add combo multiplier
            garbage_blocks *= max(1, combo_multiplier)
            
            # Add cluster bonus
            if is_cluster:
                garbage_blocks += 1
            
            # Create attack objects
            for _ in range(garbage_blocks):
                attacks.append({
                    "type": AttackType.GARBAGE_BLOCK,
                    "color": color
                })
            
            print(f"Generated {len(attacks)} garbage block attacks with color {color}")
        
        return attacks
    
    def add_attacks_to_queue(self, attacks, target_player):
        """Add generated attacks to the appropriate player's queue."""
        if not attacks:
            return
            
        if target_player == 1:
            self.player1_attacks.extend(attacks)
            print(f"Added {len(attacks)} attacks to player 1's queue")
        else:
            self.player2_attacks.extend(attacks)
            print(f"Added {len(attacks)} attacks to player 2's queue")
    
    def get_next_attack_position(self):
        """Get the next column for placing a garbage block based on the pattern."""
        column = self.column_pattern[self.current_column_index]
        
        # Update pattern index
        self.current_column_index = (self.current_column_index + 1) % len(self.column_pattern)
        
        return column
    
    def update_garbage_blocks(self):
        """Update the state of all garbage blocks."""
        current_time = time.time()
        blocks_to_update = []
        
        # Check each garbage block
        for pos, (start_time, color) in list(self.garbage_blocks.items()):
            elapsed_time = current_time - start_time
            if elapsed_time >= self.transformation_time:
                # Block is ready to transform
                blocks_to_update.append((pos, color))
                del self.garbage_blocks[pos]
        
        return blocks_to_update
    
    def decrement_garbage_block_turns(self, player_number=1):
        """This method is kept for compatibility but no longer decrements turns."""
        # Instead, we just check for blocks that need to transform based on time
        return self.update_garbage_blocks()
    
    def process_attack_queue(self, target_grid, target_player):
        """Process all pending attacks for a player."""
        # Get the appropriate attack queue
        attack_queue = self.player1_attacks if target_player == 1 else self.player2_attacks
        
        if not attack_queue:
            return False
            
        # Process each attack
        for attack in attack_queue:
            if attack["type"] == AttackType.GARBAGE_BLOCK:
                # Get the next column from the pattern
                column = self.get_next_attack_position()
                color = attack["color"]
                block_type = f"{color}_garbage"  # Add _garbage suffix
                
                # Find the highest empty position in the column
                highest_empty = -1  # Start above the grid
                while highest_empty + 1 < len(target_grid) and target_grid[highest_empty + 1][column] is None:
                    highest_empty += 1
                
                # Place the block at the highest empty position
                if highest_empty >= -1:  # Allow placement at or above row 0
                    target_y = highest_empty
                    if target_y < 0:
                        target_y = 0  # Place at row 0 if above grid
                    
                    # Place the block
                    target_grid[target_y][column] = block_type
                    
                    # Store the garbage block state with current time for transformation
                    current_time = time.time()
                    self.garbage_blocks[(column, target_y)] = (current_time, color)
            
            elif attack["type"] == AttackType.STRIKE:
                # Get the next column from the pattern
                column = self.get_next_attack_position()
                color = attack["color"]
                block_type = "strike_1x4"  # Using the strike type
                
                # For a 1x4 strike, we need to place 4 blocks in the same column
                strike_height = 4
                
                # Find the highest empty position in the column
                highest_empty = -1  # Start above the grid
                while highest_empty + 1 < len(target_grid) and target_grid[highest_empty + 1][column] is None:
                    highest_empty += 1
                
                # Place the strike blocks at the highest empty positions
                current_time = time.time()
                
                for i in range(strike_height):
                    if highest_empty - i >= -1:  # Allow placement at or above row 0
                        target_y = highest_empty - i
                        if target_y < 0:
                            target_y = 0  # Place at row 0 if above grid
                        
                        # Make sure there's space to place the block
                        if target_y < len(target_grid) and target_grid[target_y][column] is None:
                            # Place the strike block
                            target_grid[target_y][column] = block_type
                            
                            # Store the strike block state with current time for transformation
                            # Include the height index so we know which part of the strike this is
                            self.strike_blocks[(column, target_y)] = (current_time, color, i)
        
        # Clear the processed queue
        if target_player == 1:
            self.player1_attacks.clear()
        else:
            self.player2_attacks.clear()
            
        return True
    
    def update_strike_blocks(self):
        """Update the state of all strike blocks, transforming them to garbage blocks if ready."""
        current_time = time.time()
        blocks_to_transform = []
        
        # Check each strike block
        for pos, (start_time, color, height_index) in list(self.strike_blocks.items()):
            elapsed_time = current_time - start_time
            if elapsed_time >= self.strike_transformation_time:
                # Strike is ready to transform into a garbage block
                blocks_to_transform.append((pos, color))
                del self.strike_blocks[pos]
        
        return blocks_to_transform
    
    def process_strike_to_garbage_transformation(self, target_grid):
        """Transform strike blocks into garbage blocks after their time has elapsed."""
        blocks_to_transform = self.update_strike_blocks()
        
        # Transform each block
        for (x, y), color in blocks_to_transform:
            # Only process if the position is still a strike block
            if y < len(target_grid) and x < len(target_grid[0]) and target_grid[y][x] == "strike_1x4":
                # Transform to garbage block
                block_type = f"{color}_garbage"
                target_grid[y][x] = block_type
                
                # Store as a garbage block with current time for transformation
                current_time = time.time()
                self.garbage_blocks[(x, y)] = (current_time, color)
                
                print(f"Transformed strike at ({x}, {y}) to garbage block")
        
        return blocks_to_transform 