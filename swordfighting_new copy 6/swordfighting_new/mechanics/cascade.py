"""cascade.py - Clean gravity/cascade system for Blade Fighters.

Handles block falling after clears or piece locks.
Coordinate system: Y=0 is top, Y=HEIGHT-1 is bottom.
Blocks fall from lower Y values to higher Y values.

Based on the superior algorithm from src/core.py with two distinct modes:
- apply_full(): instant gravity compression (RowByRowFast mode)
- apply_step(): incremental gravity (BlockSlow mode)
- apply_until_stable(): repeatedly apply_step() until nothing moves

The algorithm counts empty spaces from bottom up, then moves blocks down
by the appropriate amount in a single pass per column.
"""

class CascadeManager:
    def __init__(self, board):
        self.board = board

    def apply_full(self) -> int:
        """Apply full gravity compression instantly (RowByRowFast mode).
        Also clears any blocks marked for clearing.

        Returns:
            int: Total number of blocks that moved to new positions or were cleared.
        """
        collapsed_blocks = 0
        h = self.board.HEIGHT
        w = self.board.WIDTH

        # First pass: clear marked blocks
        for x in range(w):
            for y in range(h):
                cell = self.board.get_piece(x, y)
                if cell != self.board.EMPTY and getattr(cell, 'marked_for_clearing', False):
                    self.board.set_piece(x, y, self.board.EMPTY)
                    collapsed_blocks += 1

        # Second pass: apply gravity
        for x in range(w):
            spaces = 0
            # Iterate from bottom to top (HEIGHT-1 down to 0)
            for y in range(h - 1, -1, -1):
                cell = self.board.get_piece(x, y)

                if cell == self.board.EMPTY:
                    spaces += 1
                elif spaces > 0:
                    # Non-empty block with spaces below - move it down
                    self.board.set_piece(x, y, self.board.EMPTY)
                    self.board.set_piece(x, y + spaces, cell)
                    collapsed_blocks += 1

        return collapsed_blocks

    def apply_step(self) -> int:
        """Apply one step of gravity - blocks fall one row if possible (BlockSlow mode).
        Also clears any blocks marked for clearing.

        Returns:
            int: Number of blocks that moved down one row or were cleared.
        """
        collapsed_blocks = 0
        h = self.board.HEIGHT
        w = self.board.WIDTH

        # First: clear any marked blocks
        for x in range(w):
            for y in range(h):
                cell = self.board.get_piece(x, y)
                if cell != self.board.EMPTY and getattr(cell, 'marked_for_clearing', False):
                    self.board.set_piece(x, y, self.board.EMPTY)
                    collapsed_blocks += 1

        # Second: Create a list of moves to make, then apply them all at once
        # This prevents chain reactions within a single step
        moves = []

        for x in range(w):
            # Check from bottom to top which blocks can move
            for y in range(h - 2, -1, -1):  # from second-to-last row up to top
                cell = self.board.get_piece(x, y)

                if cell != self.board.EMPTY:
                    # Check if space below is empty
                    below = self.board.get_piece(x, y + 1)
                    if below == self.board.EMPTY:
                        # Don't move if another block is already moving to this position
                        target_occupied = any(mx == x and my + 1 == y + 1 for mx, my, _ in moves)
                        if not target_occupied:
                            moves.append((x, y, cell))

        # Apply all moves
        for x, y, cell in moves:
            self.board.set_piece(x, y, self.board.EMPTY)
            self.board.set_piece(x, y + 1, cell)
            collapsed_blocks += 1

        return collapsed_blocks

    def apply_until_stable(self, max_iterations: int = 100) -> int:
        """Apply step gravity repeatedly until nothing moves.

        Args:
            max_iterations: Safety limit to prevent infinite loops.

        Returns:
            int: Total number of blocks that moved across all steps.
        """
        total_moved = 0
        iterations = 0

        while iterations < max_iterations:
            moved = self.apply_step()
            if moved == 0:
                break
            total_moved += moved
            iterations += 1

        return total_moved

    def is_stable(self) -> bool:
        """Check if the board is stable (no blocks can fall further).

        Returns:
            bool: True if no blocks can move down.
        """
        h = self.board.HEIGHT
        w = self.board.WIDTH

        for x in range(w):
            for y in range(h-2, -1, -1):  # from second-to-last row upward
                cell = self.board.get_piece(x, y)
                if cell == self.board.EMPTY:
                    continue
                below = self.board.get_piece(x, y+1)
                if below == self.board.EMPTY:
                    return False

        return True
