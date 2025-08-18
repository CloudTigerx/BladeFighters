#!/usr/bin/env python3
"""
New Clean Puzzle Engine - Proof of Concept

This demonstrates how much cleaner and more reliable the puzzle system can be
with a proper architecture design.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Tuple, Set
from enum import Enum
import pygame

# ============================================================================
# CLEAN DATA STRUCTURES
# ============================================================================

class PieceType(Enum):
    """Clean piece type definitions"""
    I = "I"
    O = "O"
    T = "T"
    S = "S"
    Z = "Z"
    J = "J"
    L = "L"

@dataclass
class Position:
    """Clean position representation"""
    x: int
    y: int
    
    def __add__(self, other):
        return Position(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        return Position(self.x - other.x, self.y - other.y)

@dataclass
class Piece:
    """Clean piece representation"""
    piece_type: PieceType
    position: Position
    rotation: int = 0  # 0, 1, 2, 3 for 0°, 90°, 180°, 270°
    
    def get_blocks(self) -> List[Position]:
        """Get all block positions for this piece"""
        # Simple, clear piece definitions
        piece_definitions = {
            PieceType.I: [(0, 0), (0, 1), (0, 2), (0, 3)],
            PieceType.O: [(0, 0), (1, 0), (0, 1), (1, 1)],
            PieceType.T: [(1, 0), (0, 1), (1, 1), (2, 1)],
            # ... other pieces
        }
        
        blocks = piece_definitions.get(self.piece_type, [])
        rotated_blocks = self._rotate_blocks(blocks, self.rotation)
        return [self.position + Position(x, y) for x, y in rotated_blocks]
    
    def _rotate_blocks(self, blocks: List[Tuple[int, int]], rotation: int) -> List[Tuple[int, int]]:
        """Rotate block positions"""
        for _ in range(rotation):
            blocks = [(-y, x) for x, y in blocks]
        return blocks
    
    def move(self, dx: int, dy: int):
        """Move piece by delta"""
        self.position.x += dx
        self.position.y += dy
    
    def rotate(self):
        """Rotate piece clockwise"""
        self.rotation = (self.rotation + 1) % 4

@dataclass
class Grid:
    """Clean grid representation"""
    width: int
    height: int
    cells: List[List[Optional[PieceType]]] = field(init=False)
    
    def __post_init__(self):
        self.cells = [[None for _ in range(self.width)] for _ in range(self.height)]
    
    def is_valid_position(self, position: Position) -> bool:
        """Check if position is valid"""
        return (0 <= position.x < self.width and 
                0 <= position.y < self.height and
                self.cells[position.y][position.x] is None)
    
    def can_place_piece(self, piece: Piece) -> bool:
        """Check if piece can be placed"""
        for block_pos in piece.get_blocks():
            if not self.is_valid_position(block_pos):
                return False
        return True
    
    def place_piece(self, piece: Piece):
        """Place piece on grid"""
        for block_pos in piece.get_blocks():
            if 0 <= block_pos.x < self.width and 0 <= block_pos.y < self.height:
                self.cells[block_pos.y][block_pos.x] = piece.piece_type
    
    def clear_lines(self) -> int:
        """Clear completed lines and return count"""
        lines_cleared = 0
        y = self.height - 1
        while y >= 0:
            if all(cell is not None for cell in self.cells[y]):
                # Remove this line
                del self.cells[y]
                # Add new empty line at top
                self.cells.insert(0, [None for _ in range(self.width)])
                lines_cleared += 1
            else:
                y -= 1
        return lines_cleared

@dataclass
class GameState:
    """Clean game state"""
    score: int = 0
    level: int = 1
    lines_cleared: int = 0
    game_active: bool = False
    current_piece: Optional[Piece] = None
    next_piece: Optional[Piece] = None
    fall_time: float = 0.0
    fall_speed: float = 1.0  # seconds per fall

# ============================================================================
# CLEAN PUZZLE ENGINE
# ============================================================================

class PuzzleEngine:
    """
    Clean, simple puzzle engine with clear responsibilities.
    
    This engine handles ONLY game logic - no rendering, no input, no audio.
    """
    
    def __init__(self, width: int = 6, height: int = 12):
        self.grid = Grid(width, height)
        self.state = GameState()
        self._last_fall_time = 0.0
        
    def start_game(self):
        """Start a new game"""
        self.state.game_active = True
        self.state.score = 0
        self.state.level = 1
        self.state.lines_cleared = 0
        self.grid = Grid(self.grid.width, self.grid.height)
        self._spawn_new_piece()
        
    def update(self, dt: float):
        """Update game logic"""
        if not self.state.game_active:
            return
            
        # Update fall timer
        self._last_fall_time += dt
        
        # Handle piece falling
        if self._last_fall_time >= self.state.fall_speed:
            self._last_fall_time = 0.0
            self._fall_piece()
    
    def move_piece(self, dx: int, dy: int) -> bool:
        """Move current piece and return success"""
        if not self.state.current_piece:
            return False
            
        # Try to move
        original_pos = Position(self.state.current_piece.position.x, 
                               self.state.current_piece.position.y)
        self.state.current_piece.move(dx, dy)
        
        # Check if move is valid
        if not self.grid.can_place_piece(self.state.current_piece):
            # Revert move
            self.state.current_piece.position = original_pos
            return False
            
        return True
    
    def rotate_piece(self) -> bool:
        """Rotate current piece and return success"""
        if not self.state.current_piece:
            return False
            
        # Try to rotate
        original_rotation = self.state.current_piece.rotation
        self.state.current_piece.rotate()
        
        # Check if rotation is valid
        if not self.grid.can_place_piece(self.state.current_piece):
            # Revert rotation
            self.state.current_piece.rotation = original_rotation
            return False
            
        return True
    
    def hard_drop(self):
        """Drop piece to bottom"""
        if not self.state.current_piece:
            return
            
        # Move piece down until it can't move anymore
        while self.move_piece(0, 1):
            pass
        
        # Place piece
        self._place_piece()
    
    def _fall_piece(self):
        """Handle automatic piece falling"""
        if not self.state.current_piece:
            return
            
        # Try to move piece down
        if not self.move_piece(0, 1):
            # Can't move down, place piece
            self._place_piece()
    
    def _place_piece(self):
        """Place current piece on grid"""
        if not self.state.current_piece:
            return
            
        # Place piece on grid
        self.grid.place_piece(self.state.current_piece)
        
        # Clear completed lines
        lines_cleared = self.grid.clear_lines()
        if lines_cleared > 0:
            self._handle_lines_cleared(lines_cleared)
        
        # Spawn new piece
        self._spawn_new_piece()
        
        # Check for game over
        if not self.grid.can_place_piece(self.state.current_piece):
            self.state.game_active = False
    
    def _spawn_new_piece(self):
        """Spawn a new piece"""
        import random
        
        # Move next piece to current
        self.state.current_piece = self.state.next_piece
        
        # Create new next piece
        piece_types = list(PieceType)
        new_type = random.choice(piece_types)
        self.state.next_piece = Piece(
            piece_type=new_type,
            position=Position(self.grid.width // 2, 0)
        )
    
    def _handle_lines_cleared(self, lines: int):
        """Handle lines being cleared"""
        # Update score (simple scoring system)
        line_scores = {1: 100, 2: 300, 3: 500, 4: 800}
        self.state.score += line_scores.get(lines, 0) * self.state.level
        
        # Update lines cleared
        self.state.lines_cleared += lines
        
        # Update level
        self.state.level = (self.state.lines_cleared // 10) + 1
        
        # Update fall speed
        self.state.fall_speed = max(0.1, 1.0 - (self.state.level - 1) * 0.1)
    
    def get_state(self) -> GameState:
        """Get current game state"""
        return self.state
    
    def get_grid(self) -> Grid:
        """Get current grid"""
        return self.grid

# ============================================================================
# USAGE EXAMPLE
# ============================================================================

def example_usage():
    """Example of how clean and simple the new system is"""
    
    # Create engine
    engine = PuzzleEngine(6, 12)
    
    # Start game
    engine.start_game()
    
    # Game loop (simplified)
    dt = 1.0 / 60.0  # 60 FPS
    
    # Update game
    engine.update(dt)
    
    # Handle input (simplified)
    # engine.move_piece(-1, 0)  # Move left
    # engine.move_piece(1, 0)   # Move right
    # engine.rotate_piece()     # Rotate
    # engine.hard_drop()        # Hard drop
    
    # Get state for rendering
    state = engine.get_state()
    grid = engine.get_grid()
    
    print(f"Score: {state.score}")
    print(f"Level: {state.level}")
    print(f"Game Active: {state.game_active}")

if __name__ == "__main__":
    example_usage()
