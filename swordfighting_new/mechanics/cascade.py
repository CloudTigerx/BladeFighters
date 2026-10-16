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

    # NOTE: We intentionally use *per-cell* gravity here (not rigid components).
    # This means connected shapes can "drip" and split when only partially supported.

    def _is_held_block(self, cell) -> bool:
        """Blocks that should never be moved by cascade gravity."""
        if cell == self.board.EMPTY or cell is None:
            return False
        # Horizontal sword held blocks.
        if bool(getattr(cell, 'hsword_hold', False)):
            return True
        return False

    def _is_garbageish(self, cell) -> bool:
        if cell == self.board.EMPTY or cell is None:
            return False
        st = getattr(cell, 'attack_state', None)
        return bool(getattr(cell, 'is_garbage', False)) or (st in ('sprinkle', 'cgarbage'))

    def _apply_cell_fall_step(self) -> int:
        """Move all fallable non-held cells down by one row (simultaneously).

        Returns number of blocks moved.
        """
        moved_blocks = 0
        h = int(self.board.HEIGHT)
        w = int(self.board.WIDTH)

        # Compute fallable cells from a snapshot of the current board.
        moving_cells: dict[tuple[int, int], object] = {}
        for y in range(h - 2, -1, -1):
            for x in range(w):
                cell = self.board.get_piece(x, y)
                if cell == self.board.EMPTY or cell is None:
                    continue
                if self._is_held_block(cell):
                    continue
                if self.board.get_piece(x, y + 1) != self.board.EMPTY:
                    continue
                moving_cells[(x, y)] = cell

        if not moving_cells:
            return 0

        # Clear then re-place shifted down.
        for (x, y) in moving_cells.keys():
            self.board.set_piece(x, y, self.board.EMPTY)
        for (x, y), cell in moving_cells.items():
            self.board.set_piece(x, y + 1, cell)
            moved_blocks += 1

        return moved_blocks

    def apply_full(self) -> int:
        """Apply full gravity settlement instantly.

        Clears marked blocks, then repeatedly applies rigid-body component gravity
        until stable (or cap reached).
        """
        moved_or_cleared = 0
        h = int(self.board.HEIGHT)
        w = int(self.board.WIDTH)

        # First: clear marked blocks (respecting existing breaker marking).
        for x in range(w):
            for y in range(h):
                cell = self.board.get_piece(x, y)
                if cell != self.board.EMPTY and getattr(cell, 'marked_for_clearing', False):
                    self.board.set_piece(x, y, self.board.EMPTY)
                    moved_or_cleared += 1

        # Then: settle.
        # Small board => simple loop is fine.
        for _ in range(200):
            moved = self._apply_cell_fall_step()
            if moved == 0:
                break
            moved_or_cleared += moved

        return moved_or_cleared

    def apply_step(self) -> int:
        """Apply one step of gravity (one row) using per-cell falling.

        Clears marked blocks, then moves any non-held block with empty space below
        down by exactly one row.
        """
        moved_or_cleared = 0
        h = int(self.board.HEIGHT)
        w = int(self.board.WIDTH)

        # First: clear any marked blocks.
        for x in range(w):
            for y in range(h):
                cell = self.board.get_piece(x, y)
                if cell != self.board.EMPTY and getattr(cell, 'marked_for_clearing', False):
                    self.board.set_piece(x, y, self.board.EMPTY)
                    moved_or_cleared += 1

        # Then: one fall step.
        moved_or_cleared += self._apply_cell_fall_step()
        return moved_or_cleared

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
        """True if board has no non-held blocks that can fall by one."""
        h = int(self.board.HEIGHT)
        w = int(self.board.WIDTH)
        for y in range(h - 2, -1, -1):
            for x in range(w):
                cell = self.board.get_piece(x, y)
                if cell == self.board.EMPTY or cell is None:
                    continue
                if self._is_held_block(cell):
                    continue
                if self.board.get_piece(x, y + 1) == self.board.EMPTY:
                    return False
        return True
