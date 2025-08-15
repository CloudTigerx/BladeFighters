"""
Column Rotator

Handles column rotation for attack placement.
"""


class ColumnRotator:
    """Rotates through columns for attack placement."""
    
    def __init__(self, grid_width=6):
        """
        Initialize column rotator.
        
        Args:
            grid_width: Width of the grid (default 6)
        """
        self.grid_width = grid_width
        # Rotation pattern: 1→6→2→5→3→4 (1-based, then convert to 0-based)
        self.rotation = [0, 5, 1, 4, 2, 3]  # 0-based columns
        self.current_index = 0
    
    def get_next_column(self):
        """
        Get the next column in rotation.
        
        Returns:
            Column index (0-based)
        """
        column = self.rotation[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.rotation)
        return column
    
    def reset_rotation(self):
        """Reset rotation to start."""
        self.current_index = 0
    
    def set_rotation_pattern(self, pattern):
        """
        Set a custom rotation pattern.
        
        Args:
            pattern: List of column indices (0-based)
        """
        if len(pattern) != self.grid_width:
            raise ValueError(f"Pattern must have {self.grid_width} columns")
        
        self.rotation = pattern.copy()
        self.current_index = 0
    
    def get_current_column(self):
        """
        Get the current column without advancing.
        
        Returns:
            Current column index (0-based)
        """
        return self.rotation[self.current_index]
    
    def get_rotation_info(self):
        """
        Get information about the current rotation state.
        
        Returns:
            Dictionary with rotation information
        """
        return {
            'current_column': self.get_current_column(),
            'current_index': self.current_index,
            'rotation_pattern': self.rotation.copy(),
            'grid_width': self.grid_width
        } 