#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Game Model - Contains all game logic with no visual concerns
This represents the state and rules of the game
"""

class GridPosition:
    """Represents a position on the game grid."""
    
    def __init__(self, x, y):
        """Initialize with grid coordinates."""
        self.x = x
        self.y = y
    
    def __eq__(self, other):
        """Check if two positions are equal."""
        if isinstance(other, GridPosition):
            return self.x == other.x and self.y == other.y
        return False
    
    def __repr__(self):
        """String representation."""
        return f"GridPosition({self.x}, {self.y})"

class GamePiece:
    """Represents a game piece with a type and no visual properties."""
    
    def __init__(self, piece_type):
        """Initialize with a type (color or special type)."""
        self.piece_type = piece_type  # e.g., 'red', 'blue', 'breaker', etc.
        self.is_breaker = 'breaker' in piece_type
    
    def __repr__(self):
        """String representation."""
        return f"GamePiece({self.piece_type})"

class FallingPiece:
    """Represents a piece that is currently falling."""
    
    def __init__(self, main_piece, attached_piece=None, position=None):
        """Initialize with main piece, optional attached piece, and position."""
        self.main_piece = main_piece
        self.attached_piece = attached_piece
        self.position = position or GridPosition(5, 0)  # Default to middle-top
        self.attached_position = 0  # 0: top, 1: right, 2: bottom, 3: left
        self.fall_distance = 0.0  # Fractional distance for smooth falling
    
    def get_attached_position(self):
        """Calculate the position of the attached piece based on main position and attachment point."""
        x, y = self.position.x, self.position.y
        
        if self.attached_position == 0:  # Top
            return GridPosition(x, y - 1)
        elif self.attached_position == 1:  # Right
            return GridPosition(x + 1, y)
        elif self.attached_position == 2:  # Bottom
            return GridPosition(x, y + 1)
        elif self.attached_position == 3:  # Left
            return GridPosition(x - 1, y)
    
    def rotate_clockwise(self):
        """Rotate the attached piece clockwise."""
        self.attached_position = (self.attached_position + 1) % 4
    
    def rotate_counterclockwise(self):
        """Rotate the attached piece counterclockwise."""
        self.attached_position = (self.attached_position - 1) % 4

class GameGrid:
    """Represents the game grid with no visual properties."""
    
    def __init__(self, width=10, height=20):
        """Initialize an empty grid with specified dimensions."""
        self.width = width
        self.height = height
        self.grid = [[None for _ in range(width)] for _ in range(height)]
    
    def is_valid_position(self, position):
        """Check if a position is within grid bounds."""
        return (0 <= position.x < self.width and 
                0 <= position.y < self.height)
    
    def is_position_empty(self, position):
        """Check if a position is empty."""
        if not self.is_valid_position(position):
            return False
        return self.grid[position.y][position.x] is None
    
    def place_piece(self, position, piece):
        """Place a piece on the grid at the specified position."""
        if self.is_valid_position(position):
            self.grid[position.y][position.x] = piece
            return True
        return False
    
    def remove_piece(self, position):
        """Remove a piece from the grid at the specified position."""
        if self.is_valid_position(position):
            self.grid[position.y][position.x] = None
            return True
        return False
    
    def get_piece(self, position):
        """Get the piece at a specified position."""
        if self.is_valid_position(position):
            return self.grid[position.y][position.x]
        return None

class GameModel:
    """Main model class that contains all game logic."""
    
    def __init__(self):
        """Initialize the game model."""
        # Constants
        self.GRID_WIDTH = 6
        self.GRID_HEIGHT = 13
        self.NORMAL_FALL_SPEED = 1.0  # Grid cells per second
        self.FAST_FALL_SPEED = 5.0    # Grid cells per second
        
        # Game state
        self.grid = GameGrid(self.GRID_WIDTH, self.GRID_HEIGHT)
        self.current_piece = None
        self.next_pieces = []
        self.game_active = False
        self.score = 0
        self.level = 1
        
        # Falling state
        self.current_fall_speed = self.NORMAL_FALL_SPEED
        
        # Game mechanics flags
        self.gravity_pending = False
        self.chain_reaction_active = False
        
        # Initialize for a new game
        self.start_game()
    
    def start_game(self):
        """Start a new game."""
        # Clear the grid
        self.grid = GameGrid(self.GRID_WIDTH, self.GRID_HEIGHT)
        
        # Generate initial pieces
        self.generate_next_pieces()
        self.spawn_new_piece()
        
        # Reset game state
        self.game_active = True
        self.score = 0
        self.level = 1
        self.current_fall_speed = self.NORMAL_FALL_SPEED
    
    def generate_next_pieces(self):
        """Generate the next pieces to be used."""
        import random
        piece_types = ['red', 'blue', 'green', 'yellow']
        breaker_types = [f"{color}_breaker" for color in piece_types]
        
        # Ensure at least 2 pieces in the queue
        while len(self.next_pieces) < 2:
            piece_type = random.choice(piece_types)
            
            # 25% chance for a breaker piece
            if random.random() < 0.25:
                piece_type = random.choice(breaker_types)
                
            self.next_pieces.append(GamePiece(piece_type))
    
    def spawn_new_piece(self):
        """Spawn a new falling piece at the top of the grid."""
        if not self.next_pieces:
            self.generate_next_pieces()
        
        # Get the next pieces
        main_piece = self.next_pieces.pop(0)
        attached_piece = self.next_pieces.pop(0)
        
        # Create the falling piece
        self.current_piece = FallingPiece(
            main_piece, 
            attached_piece,
            GridPosition(self.GRID_WIDTH // 2, 0)
        )
        
        # Reset fall variables
        self.current_fall_speed = self.NORMAL_FALL_SPEED
        
        # Generate new next pieces
        self.generate_next_pieces()
        
        # Check if the new piece can fit (game over condition)
        if not self.can_piece_fit(self.current_piece):
            self.game_active = False
            return False
            
        return True
    
    def can_piece_fit(self, piece):
        """Check if a piece can fit at its current position."""
        # Check main piece position
        if not self.grid.is_position_empty(piece.position):
            return False
            
        # Check attached piece position
        attached_pos = piece.get_attached_position()
        if not self.grid.is_position_empty(attached_pos):
            return False
            
        return True
    
    def move_piece(self, dx, dy):
        """Try to move the current piece by the given delta."""
        if not self.current_piece or not self.game_active:
            return False
            
        # Calculate new positions
        new_pos = GridPosition(
            self.current_piece.position.x + dx,
            self.current_piece.position.y + dy
        )
        
        # Save old position
        old_pos = self.current_piece.position
        
        # Try the move
        self.current_piece.position = new_pos
        
        # Check if the new position is valid
        if not self.can_piece_fit(self.current_piece):
            # Revert if invalid
            self.current_piece.position = old_pos
            
            # If we tried to move down and couldn't, place the piece
            if dy > 0:
                self.place_current_piece()
                
            return False
            
        return True
    
    def rotate_piece(self, direction=1):
        """Try to rotate the current piece in the given direction (1=clockwise, -1=counterclockwise)."""
        if not self.current_piece or not self.game_active:
            return False
            
        # Save old rotation
        old_rotation = self.current_piece.attached_position
        
        # Try to rotate
        if direction > 0:
            self.current_piece.rotate_clockwise()
        else:
            self.current_piece.rotate_counterclockwise()
            
        # Check if the new rotation is valid
        if not self.can_piece_fit(self.current_piece):
            # Revert if invalid
            self.current_piece.attached_position = old_rotation
            return False
            
        return True
    
    def hard_drop(self):
        """Drop the piece to the bottom instantly."""
        if not self.current_piece or not self.game_active:
            return False
            
        # Keep moving down until blocked
        drop_distance = 0
        while self.move_piece(0, 1):
            drop_distance += 1
            
        # Add score for the drop
        self.score += drop_distance * 2
            
        # The move_piece method will call place_current_piece when it can't move down
        return True
    
    def place_current_piece(self):
        """Place the current piece on the grid and handle consequences."""
        if not self.current_piece or not self.game_active:
            return False
            
        # Place main piece
        self.grid.place_piece(self.current_piece.position, self.current_piece.main_piece)
        
        # Place attached piece
        attached_pos = self.current_piece.get_attached_position()
        self.grid.place_piece(attached_pos, self.current_piece.attached_piece)
        
        # Clear the current piece
        self.current_piece = None
        
        # Mark that gravity needs to be applied
        self.gravity_pending = True
        
        return True
    
    def apply_gravity(self):
        """Apply gravity to make pieces fall to fill gaps."""
        if not self.game_active:
            return False
            
        # Track if any pieces actually moved
        pieces_moved = False
        
        # Start from the bottom-up (except bottom row)
        for y in range(self.grid.height - 2, -1, -1):
            for x in range(self.grid.width):
                # Skip empty cells
                if not self.grid.grid[y][x]:
                    continue
                
                # Look for empty space below this piece
                fall_distance = 0
                for check_y in range(y + 1, self.grid.height):
                    if self.grid.grid[check_y][x] is None:
                        fall_distance += 1
                    else:
                        break
                
                # If there's space below, move the piece down
                if fall_distance > 0:
                    piece = self.grid.grid[y][x]
                    self.grid.grid[y][x] = None
                    self.grid.grid[y + fall_distance][x] = piece
                    pieces_moved = True
        
        # Clear the gravity pending flag
        self.gravity_pending = False
        
        # If pieces moved, check for chains
        if pieces_moved:
            self.check_for_chains()
            
        return pieces_moved
    
    def check_for_chains(self):
        """Check for chains of pieces that can be eliminated."""
        # Find all clusters of same-colored pieces
        clusters = self.find_clusters()
        
        # If there are clusters, mark them for elimination
        if clusters:
            # Mark chain reaction as active
            self.chain_reaction_active = True
            
            # Add score
            for cluster in clusters:
                self.score += len(cluster) * 10
            
            # Activate breaker pieces (in a real implementation)
            self.activate_breaker_blocks()
    
    def find_clusters(self):
        """Find all clusters of 3+ same-colored pieces."""
        clusters = []
        visited = [[False for _ in range(self.grid.width)] for _ in range(self.grid.height)]
        
        # Check each cell
        for y in range(self.grid.height):
            for x in range(self.grid.width):
                # Skip if already visited or empty
                if visited[y][x] or not self.grid.grid[y][x]:
                    continue
                
                # Get the piece type
                piece = self.grid.grid[y][x]
                piece_type = piece.piece_type
                
                # Skip breaker pieces for cluster detection
                if piece.is_breaker:
                    continue
                
                # Find all connected pieces of the same type
                cluster = []
                self._extend_cluster(cluster, visited, x, y, piece_type)
                
                # If cluster has 3+ pieces, add it
                if len(cluster) >= 3:
                    clusters.append(cluster)
        
        return clusters
    
    def _extend_cluster(self, cluster, visited, x, y, piece_type):
        """Recursively extend a cluster from a starting position."""
        # Check bounds
        if not (0 <= x < self.grid.width and 0 <= y < self.grid.height):
            return
        
        # Check if visited or empty
        if visited[y][x] or not self.grid.grid[y][x]:
            return
        
        # Check if same type
        piece = self.grid.grid[y][x]
        if piece.is_breaker or piece.piece_type != piece_type:
            return
        
        # Add to cluster and mark as visited
        cluster.append(GridPosition(x, y))
        visited[y][x] = True
        
        # Check neighbors
        self._extend_cluster(cluster, visited, x+1, y, piece_type)  # Right
        self._extend_cluster(cluster, visited, x-1, y, piece_type)  # Left
        self._extend_cluster(cluster, visited, x, y+1, piece_type)  # Down
        self._extend_cluster(cluster, visited, x, y-1, piece_type)  # Up
    
    def activate_breaker_blocks(self):
        """Activate breaker blocks to destroy pieces."""
        # This would be implemented in a real game
        # For now, just clear the chain reaction flag
        self.chain_reaction_active = False
        
        # After activation, spawn a new piece
        if not self.current_piece:
            self.spawn_new_piece()
    
    def update(self, delta_time):
        """Update game state based on time passed."""
        if not self.game_active:
            return
        
        # Handle piece falling
        if self.current_piece:
            # Update fall distance
            self.current_piece.fall_distance += self.current_fall_speed * delta_time
            
            # If fall distance exceeds 1, move down
            if self.current_piece.fall_distance >= 1.0:
                # Calculate whole cells to move
                whole_cells = int(self.current_piece.fall_distance)
                self.current_piece.fall_distance -= whole_cells
                
                # Try to move down
                for _ in range(whole_cells):
                    if not self.move_piece(0, 1):
                        break
        
        # Handle gravity
        elif self.gravity_pending:
            self.apply_gravity()
        
        # Handle chain reactions
        elif self.chain_reaction_active:
            # In a real implementation, this would animate and check for more chains
            self.activate_breaker_blocks()
        
        # Spawn new piece if needed
        elif not self.current_piece and not self.chain_reaction_active:
            self.spawn_new_piece() 
