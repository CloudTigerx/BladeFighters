import pygame
import math
from typing import List, Tuple, Optional, Set

class BasicPhysics:
    """
    Handles basic physics operations for the puzzle game.
    This class provides safe utilities for position validation, collision detection,
    and movement calculations without interfering with the chain reaction system.
    """
    
    def __init__(self, puzzle_engine):
        """
        Initialize basic physics with reference to puzzle engine.
        
        Args:
            puzzle_engine: Reference to the main puzzle engine
        """
        self.engine = puzzle_engine
        
        # Cache frequently used values
        self.grid_width = puzzle_engine.grid_width
        self.grid_height = puzzle_engine.grid_height
        self.total_grid_height = puzzle_engine.total_grid_height
        self.block_size = puzzle_engine.block_size
        
        # Movement timing constants
        self.wall_kick_cooldown = 500  # ms cooldown for wall kicks
        self.flip_cooldown = 50  # ms cooldown between flip attempts
        self.max_wall_kicks = 2  # Maximum number of consecutive wall kicks allowed
    
    def is_valid_position(self, x: int, y: int) -> bool:
        """
        Check if a position is valid (within grid bounds and not occupied).
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            bool: True if position is valid, False otherwise
        """
        # Out of bounds check
        if x < 0 or x >= self.grid_width or y >= self.total_grid_height:
            return False
        
        # If above the grid, it's valid
        if y < 0:
            return True
        
        # Check if the space is already occupied
        return self.engine.puzzle_grid[y][x] is None
    
    def get_attached_position_coords(self, piece_position: List[int], attached_position: int) -> List[int]:
        """
        Get the grid coordinates of the attached piece based on its position.
        
        Args:
            piece_position: [x, y] coordinates of main piece
            attached_position: Orientation (0: top, 1: right, 2: bottom, 3: left)
            
        Returns:
            List[int]: [x, y] coordinates of attached piece
        """
        x, y = piece_position
        
        if attached_position == 0:  # Top
            return [x, y - 1]
        elif attached_position == 1:  # Right
            return [x + 1, y]
        elif attached_position == 2:  # Bottom
            return [x, y + 1]
        elif attached_position == 3:  # Left
            return [x - 1, y]
    
    def would_fit_below(self, piece_position: List[int], attached_position: int) -> bool:
        """
        Check if the piece would fit in the position below its current position.
        
        Args:
            piece_position: [x, y] coordinates of main piece
            attached_position: Orientation of attached piece
            
        Returns:
            bool: True if piece would fit below, False otherwise
        """
        # Get current positions
        main_x, main_y = piece_position
        attached_x, attached_y = self.get_attached_position_coords(piece_position, attached_position)
        
        # Check for bottom boundary collision
        if main_y + 1 >= self.grid_height or attached_y + 1 >= self.grid_height:
            return False  # Would be out of bounds
        
        # Smart cluster collision detection
        # Only block movement if there's actually a solid obstacle below
        # Don't block for same-color clusters unless they form a solid barrier
            
        # Check for collision with placed blocks - handle negative Y values properly
        if (main_y + 1 >= 0 and main_x >= 0 and main_x < self.grid_width and 
            self.engine.puzzle_grid[main_y + 1][main_x] is not None):
            return False  # Would collide with a block below
            
        if (attached_y + 1 >= 0 and attached_x >= 0 and attached_x < self.grid_width and 
            self.engine.puzzle_grid[attached_y + 1][attached_x] is not None):
            return False  # Would collide with a block below for attached piece
        
        # Regular validity check to ensure both pieces can fit
        return (self.is_valid_position(main_x, main_y + 1) and 
                self.is_valid_position(attached_x, attached_y + 1))
    
    def can_move_piece(self, piece_position: List[int], attached_position: int, dx: int, dy: int) -> bool:
        """
        Check if a piece can move by the given delta.
        
        Args:
            piece_position: [x, y] coordinates of main piece
            attached_position: Orientation of attached piece
            dx: Change in x direction
            dy: Change in y direction
            
        Returns:
            bool: True if piece can move, False otherwise
        """
        # Calculate new position
        new_x = piece_position[0] + dx
        new_y = piece_position[1] + dy
        
        # Get attached piece coordinates for new position
        attached_x, attached_y = self.get_attached_position_coords([new_x, new_y], attached_position)
        
        # Check if the new position is valid for both pieces
        return (self.is_valid_position(new_x, new_y) and 
                self.is_valid_position(attached_x, attached_y))
    
    def calculate_micro_fall_time(self, fall_speed: int) -> int:
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
        sub_grid_positions = getattr(self.engine, 'sub_grid_positions', 20)
        time_per_sub_position = time_per_pixel / (self.block_size / sub_grid_positions)
        
        # Ensure we never return 0
        return max(1, int(time_per_sub_position))
    
    def can_rotate_piece(self, piece_position: List[int], attached_position: int, direction: int) -> Tuple[bool, int]:
        """
        Check if a piece can rotate and return the new orientation.
        
        Args:
            piece_position: [x, y] coordinates of main piece
            attached_position: Current orientation
            direction: Rotation direction (-1 for counter-clockwise, 1 for clockwise)
            
        Returns:
            Tuple[bool, int]: (can_rotate, new_orientation)
        """
        # Calculate new position (0: top, 1: right, 2: bottom, 3: left)
        new_position = (attached_position + direction) % 4
        
        # Get current piece coordinates
        main_x, main_y = piece_position
        
        # Calculate the position where the attached piece would be after rotation
        attached_x, attached_y = self.get_attached_position_coords(piece_position, new_position)
        
        # Check if this position is valid
        if self.is_valid_position(attached_x, attached_y):
            return True, new_position
        
        return False, attached_position
    
    def check_wall_kick_rotation(self, piece_position: List[int], attached_position: int, direction: int, 
                                current_time: int, last_wall_kick_time: int, wall_kick_count: int) -> Tuple[bool, int, List[int]]:
        """
        Check if a wall kick rotation is possible.
        
        Args:
            piece_position: [x, y] coordinates of main piece
            attached_position: Current orientation
            direction: Rotation direction
            current_time: Current time in milliseconds
            last_wall_kick_time: Time of last wall kick
            wall_kick_count: Number of consecutive wall kicks
            
        Returns:
            Tuple[bool, int, List[int]]: (success, new_orientation, new_position)
        """
        # Check if we've exceeded wall kick limits
        if wall_kick_count >= self.max_wall_kicks and current_time - last_wall_kick_time < self.wall_kick_cooldown:
            return False, attached_position, piece_position
        
        # Calculate new orientation
        new_position = (attached_position + direction) % 4
        
        # Try wall kicks - attempt to move the piece to make rotation possible
        main_x, main_y = piece_position
        
        # Try different kick directions
        kick_attempts = [
            (-1, 0),  # Left
            (1, 0),   # Right
            (0, -1),  # Up
            (-1, -1), # Left-Up
            (1, -1),  # Right-Up
        ]
        
        for dx, dy in kick_attempts:
            test_position = [main_x + dx, main_y + dy]
            
            # Check if the piece can fit in this position with the new orientation
            if self.can_move_piece(test_position, new_position, 0, 0):
                return True, new_position, test_position
        
        return False, attached_position, piece_position
    
    def can_flip_vertically(self, piece_position: List[int], attached_position: int) -> bool:
        """
        Check if the pieces can be flipped vertically.
        
        Args:
            piece_position: [x, y] coordinates of main piece
            attached_position: Current orientation
            
        Returns:
            bool: True if pieces can be flipped vertically
        """
        # Only allow flipping when pieces are vertically aligned
        if attached_position not in [0, 2]:  # Not top or bottom
            return False
        
        main_x, main_y = piece_position
        
        # Calculate the new position after flipping
        if attached_position == 0:  # Top -> Bottom
            new_attached_position = 2
        else:  # Bottom -> Top
            new_attached_position = 0
        
        # Check if the new configuration is valid
        attached_x, attached_y = self.get_attached_position_coords(piece_position, new_attached_position)
        
        return self.is_valid_position(attached_x, attached_y)
    
    def apply_basic_gravity(self, grid: List[List[Optional[str]]]) -> bool:
        """
        Apply basic gravity to make pieces fall into empty spaces.
        This is the SAFE version that doesn't trigger chain reactions.
        
        Args:
            grid: The puzzle grid to apply gravity to
            
        Returns:
            bool: True if any blocks were moved, False otherwise
        """
        blocks_moved = False
        
        # First, check for any blocks in row 0 that need to fall
        for x in range(self.grid_width):
            if grid[0][x] is not None:
                # Find how far this block can fall
                fall_distance = 0
                for check_y in range(1, self.grid_height):
                    if grid[check_y][x] is None:
                        fall_distance += 1
                    else:
                        break
                
                if fall_distance > 0:
                    # Move the block down
                    new_y = fall_distance
                    grid[new_y][x] = grid[0][x]
                    grid[0][x] = None
                    blocks_moved = True
        
        # Then apply gravity to the rest of the grid from bottom to top
        for y in range(self.grid_height - 2, 0, -1):  # Start from second-to-last row
            for x in range(self.grid_width):
                if grid[y][x] is not None:
                    # Check if there's an empty space below
                    fall_distance = 0
                    for check_y in range(y + 1, self.grid_height):
                        if grid[check_y][x] is None:
                            fall_distance += 1
                        else:
                            break
                    
                    if fall_distance > 0:
                        # Move the block down
                        new_y = y + fall_distance
                        grid[new_y][x] = grid[y][x]
                        grid[y][x] = None
                        blocks_moved = True
        
        return blocks_moved
    
    def get_visual_position_with_offset(self, grid_x: int, grid_y: int, sub_position: float = 0.0) -> Tuple[float, float]:
        """
        Get the visual position of a block with sub-grid positioning.
        
        Args:
            grid_x: Grid X coordinate
            grid_y: Grid Y coordinate
            sub_position: Sub-grid position (0.0 to 1.0)
            
        Returns:
            Tuple[float, float]: (visual_x, visual_y)
        """
        visual_x = float(grid_x)
        visual_y = float(grid_y) + sub_position
        
        return visual_x, visual_y
    
    def check_collision_with_buffer(self, main_pos: Tuple[float, float], attached_pos: Tuple[float, float], 
                                   buffer_cells: float = 0.1) -> bool:
        """
        Check for potential collisions with a visual buffer.
        
        Args:
            main_pos: (x, y) position of main piece
            attached_pos: (x, y) position of attached piece
            buffer_cells: Buffer size in grid cells
            
        Returns:
            bool: True if collision would occur, False otherwise
        """
        main_x, main_y = main_pos
        attached_x, attached_y = attached_pos
        
        # Check for potential collisions with the buffer
        main_would_collide = (math.ceil(main_y + buffer_cells) < self.total_grid_height and 
                             math.ceil(main_y + buffer_cells) >= 0 and
                             int(main_x) < self.grid_width and int(main_x) >= 0 and
                             self.engine.puzzle_grid[math.ceil(main_y + buffer_cells)][int(main_x)] is not None)
                             
        attached_would_collide = (math.ceil(attached_y + buffer_cells) < self.total_grid_height and 
                                 math.ceil(attached_y + buffer_cells) >= 0 and
                                 int(attached_x) >= 0 and int(attached_x) < self.grid_width and
                                 self.engine.puzzle_grid[math.ceil(attached_y + buffer_cells)][int(attached_x)] is not None)
        
        return main_would_collide or attached_would_collide
    
    def get_physics_info(self) -> dict:
        """
        Get information about the physics system.
        
        Returns:
            dict: Physics system information
        """
        return {
            'grid_width': self.grid_width,
            'grid_height': self.grid_height,
            'total_grid_height': self.total_grid_height,
            'block_size': self.block_size,
            'wall_kick_cooldown': self.wall_kick_cooldown,
            'flip_cooldown': self.flip_cooldown,
            'max_wall_kicks': self.max_wall_kicks
        } 