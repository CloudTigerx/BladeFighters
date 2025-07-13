import pygame
from typing import List, Tuple, Optional

class PieceMovement:
    """
    Handles advanced piece movement operations including rotation and flipping.
    This class manages complex movement logic like wall kicks and cooldowns.
    """
    
    def __init__(self, puzzle_engine):
        """
        Initialize piece movement with reference to puzzle engine.
        
        Args:
            puzzle_engine: Reference to the main puzzle engine
        """
        self.engine = puzzle_engine
        
        # Cache frequently used values
        self.grid_width = puzzle_engine.grid_width
        self.grid_height = puzzle_engine.grid_height
        
        # Wall kick settings
        self.wall_kick_cooldown = 500  # ms cooldown for wall kicks
        self.max_wall_kicks = 2  # Maximum number of consecutive wall kicks allowed
        
        # Flip settings
        self.flip_cooldown = 50  # ms cooldown between flip attempts
        
        # Track state
        self.last_wall_kick_time = 0
        self.wall_kick_count = 0
        self.last_flip_time = 0
    
    def rotate_attached_piece(self, direction: int) -> bool:
        """
        Rotate the attached piece around the main piece.
        Allows for wall kicks when at edge of board or next to towers of blocks.
        
        Args:
            direction: -1 for counter-clockwise, 1 for clockwise
            
        Returns:
            bool: True if rotation was successful, False otherwise
        """
        # Calculate new position (0: top, 1: right, 2: bottom, 3: left)
        new_position = (self.engine.attached_position + direction) % 4
        
        # Get current piece coordinates
        main_x, main_y = self.engine.piece_position
        
        # Calculate the position where the attached piece would be after rotation
        attached_x, attached_y = self._calculate_attached_position(main_x, main_y, new_position)
        
        # Check if this position is valid
        if self.engine.is_valid_position(attached_x, attached_y):
            self.engine.attached_position = new_position
            # Reset wall kick count when normal rotation occurs
            self.wall_kick_count = 0
            return True
        
        # Try wall kick if normal rotation failed
        return self._attempt_wall_kick(direction, new_position)
    
    def _calculate_attached_position(self, main_x: int, main_y: int, attached_position: int) -> Tuple[int, int]:
        """
        Calculate the attached piece position for a given orientation.
        
        Args:
            main_x: Main piece X coordinate
            main_y: Main piece Y coordinate
            attached_position: Orientation (0: top, 1: right, 2: bottom, 3: left)
            
        Returns:
            Tuple[int, int]: (attached_x, attached_y)
        """
        if attached_position == 0:  # Top
            return main_x, main_y - 1
        elif attached_position == 1:  # Right
            return main_x + 1, main_y
        elif attached_position == 2:  # Bottom
            return main_x, main_y + 1
        elif attached_position == 3:  # Left
            return main_x - 1, main_y
        
        return main_x, main_y  # Fallback
    
    def _attempt_wall_kick(self, direction: int, new_position: int) -> bool:
        """
        Attempt wall kick rotation when normal rotation fails.
        
        Args:
            direction: Rotation direction
            new_position: Target orientation
            
        Returns:
            bool: True if wall kick was successful, False otherwise
        """
        # Check if we've exceeded wall kick limits
        current_time = pygame.time.get_ticks()
        if (self.wall_kick_count >= self.max_wall_kicks and 
            current_time - self.last_wall_kick_time < self.wall_kick_cooldown):
            return False
        
        # Get current piece coordinates
        main_x, main_y = self.engine.piece_position
        
        # Try wall kick logic for different orientations
        kick_successful = False
        
        if new_position == 1:  # Trying to rotate to right position (but blocked)
            kick_successful = self._try_kick_for_right_rotation(main_x, main_y)
        elif new_position == 3:  # Trying to rotate to left position (but blocked)
            kick_successful = self._try_kick_for_left_rotation(main_x, main_y)
        elif new_position == 0:  # Trying to rotate to top position (but blocked)
            kick_successful = self._try_kick_for_top_rotation(main_x, main_y)
        elif new_position == 2:  # Trying to rotate to bottom position (but blocked)
            kick_successful = self._try_kick_for_bottom_rotation(main_x, main_y)
        
        if kick_successful:
            self.engine.attached_position = new_position
            self.wall_kick_count += 1
            self.last_wall_kick_time = current_time
            return True
        
        return False
    
    def _try_kick_for_right_rotation(self, main_x: int, main_y: int) -> bool:
        """Try wall kick for right rotation."""
        # Try moving left to make room
        if (self.engine.is_valid_position(main_x - 1, main_y) and 
            self.engine.is_valid_position(main_x - 1 + 1, main_y)):
            # Move main piece left
            self.engine.piece_position[0] -= 1
            return True
        return False
    
    def _try_kick_for_left_rotation(self, main_x: int, main_y: int) -> bool:
        """Try wall kick for left rotation."""
        # Try moving right to make room
        if (self.engine.is_valid_position(main_x + 1, main_y) and 
            self.engine.is_valid_position(main_x + 1 - 1, main_y)):
            # Move main piece right
            self.engine.piece_position[0] += 1
            return True
        return False
    
    def _try_kick_for_top_rotation(self, main_x: int, main_y: int) -> bool:
        """Try wall kick for top rotation."""
        # Try moving down to make room (if not at bottom)
        if (main_y + 1 < self.grid_height and 
            self.engine.is_valid_position(main_x, main_y + 1) and 
            self.engine.is_valid_position(main_x, main_y + 1 - 1)):
            # Move main piece down
            self.engine.piece_position[1] += 1
            return True
        return False
    
    def _try_kick_for_bottom_rotation(self, main_x: int, main_y: int) -> bool:
        """Try wall kick for bottom rotation."""
        # Try moving up to make room (if not at top)
        if (main_y > 0 and 
            self.engine.is_valid_position(main_x, main_y - 1) and 
            self.engine.is_valid_position(main_x, main_y - 1 + 1)):
            # Move main piece up
            self.engine.piece_position[1] -= 1
            return True
        return False
    
    def flip_pieces_vertically(self) -> bool:
        """
        Flip the main and attached pieces vertically if they're in a valid position.
        
        Returns:
            bool: True if the flip was successful, False otherwise
        """
        # Check if on cooldown
        current_time = pygame.time.get_ticks()
        if current_time - self.last_flip_time < self.flip_cooldown:
            return False
        
        # Get current positions
        main_x, main_y = self.engine.piece_position
        
        # Track if the flip was successful
        flip_successful = False
        
        # Simple vertical flipping logic - only for vertical pieces
        if self.engine.attached_position == 0:  # Attached is above
            # Flip to attached below if valid
            if (self.engine.is_valid_position(main_x, main_y) and 
                self.engine.is_valid_position(main_x, main_y + 1)):
                self.engine.attached_position = 2  # Set to below
                flip_successful = True
        elif self.engine.attached_position == 2:  # Attached is below
            # Flip to attached above if valid
            if (self.engine.is_valid_position(main_x, main_y) and 
                self.engine.is_valid_position(main_x, main_y - 1)):
                self.engine.attached_position = 0  # Set to above
                flip_successful = True
        
        # Only update cooldown and reset wall kick tracking if flip was successful
        if flip_successful:
            # Reset wall kick tracking when flipping
            self.wall_kick_count = 0
            
            # Update the cooldown timer
            self.last_flip_time = current_time
        
        return flip_successful
    
    def can_flip_vertically(self) -> bool:
        """
        Check if the pieces can be flipped vertically.
        
        Returns:
            bool: True if pieces can be flipped vertically
        """
        # Only allow flipping when pieces are vertically aligned
        if self.engine.attached_position not in [0, 2]:  # Not top or bottom
            return False
        
        main_x, main_y = self.engine.piece_position
        
        # Calculate the new position after flipping
        if self.engine.attached_position == 0:  # Top -> Bottom
            new_attached_y = main_y + 1
        else:  # Bottom -> Top
            new_attached_y = main_y - 1
        
        # Check if the new configuration is valid
        return self.engine.is_valid_position(main_x, new_attached_y)
    
    def reset_wall_kick_tracking(self):
        """Reset wall kick tracking (called when piece lands)."""
        self.wall_kick_count = 0
        self.last_wall_kick_time = 0
    
    def update_timing_from_engine(self):
        """Update timing values from the engine (for compatibility)."""
        if hasattr(self.engine, 'last_wall_kick_time'):
            self.last_wall_kick_time = self.engine.last_wall_kick_time
        if hasattr(self.engine, 'wall_kick_count'):
            self.wall_kick_count = self.engine.wall_kick_count
        if hasattr(self.engine, 'last_flip_time'):
            self.last_flip_time = self.engine.last_flip_time
    
    def sync_timing_to_engine(self):
        """Sync timing values back to the engine (for compatibility)."""
        self.engine.last_wall_kick_time = self.last_wall_kick_time
        self.engine.wall_kick_count = self.wall_kick_count
        self.engine.last_flip_time = self.last_flip_time
    
    def get_movement_info(self) -> dict:
        """
        Get information about the piece movement system.
        
        Returns:
            dict: Movement system information
        """
        return {
            'wall_kick_cooldown': self.wall_kick_cooldown,
            'max_wall_kicks': self.max_wall_kicks,
            'flip_cooldown': self.flip_cooldown,
            'current_wall_kick_count': self.wall_kick_count,
            'last_wall_kick_time': self.last_wall_kick_time,
            'last_flip_time': self.last_flip_time,
            'wall_kick_ready': pygame.time.get_ticks() - self.last_wall_kick_time >= self.wall_kick_cooldown,
            'flip_ready': pygame.time.get_ticks() - self.last_flip_time >= self.flip_cooldown
        } 