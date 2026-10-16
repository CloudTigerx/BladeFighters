import os


class Board:
    WIDTH = 6
    HEIGHT = 12
    EMPTY = -1

    def place_piece(self, piece):
        """Place all blocks of a piece onto the board at their positions."""
        for x, y, block in piece.get_block_positions():
            if self.is_in_bounds(x, y):
                self.set_piece(x, y, block)

    def __init__(self):
        self.grid = [[self.EMPTY for _ in range(self.HEIGHT)] for _ in range(self.WIDTH)]

    def is_in_bounds(self, x, y):
        return 0 <= x < self.WIDTH and 0 <= y < self.HEIGHT

    def get_piece(self, x, y):
        # Defensive: occasionally upstream code passes non-int indices (e.g., list) due to mutation bugs.
        # Coerce to int and log once per session if that happens to avoid hard crashes during long self-play.
        try:
            xi = int(x)
            yi = int(y)
        except Exception:
            # Log lightweight warning only once (attach flag on instance)
            if (os.getenv('BF_BOARD_WARN_BAD_INDEX', '0') == '1') and (not getattr(self, '_warn_bad_index', False)):
                try:
                    print(f"[Board][WARN] Non-integer index get_piece(x={x!r}, y={y!r}) -> returning EMPTY")
                except Exception:
                    pass
                self._warn_bad_index = True  # type: ignore
            return self.EMPTY
        if self.is_in_bounds(xi, yi):
            val = self.grid[xi][yi]
            return self.EMPTY if val is None else val
        return self.EMPTY

    def set_piece(self, x, y, value):
        if self.is_in_bounds(x, y):
            # Defensive: treat None as EMPTY so renderer and logic stay consistent
            self.grid[x][y] = self.EMPTY if value is None else value

    def get_block(self, x, y):
        """Get block at position (x, y) - alias for get_piece for consistency."""
        return self.get_piece(x, y)
    
    def get_column_heights(self):
        """Get the height of each column.

        Height is measured as the number of occupied rows from the bottom up to
        the highest occupied cell in that column.

        Examples (HEIGHT=12):
        - empty column => 0
        - only bottom cell filled (y=11) => 1
        - top cell filled (y=0) => 12 (column is full)
        """
        heights = []
        for x in range(self.WIDTH):
            height = 0
            # Find the highest occupied cell (smallest y).
            for y in range(self.HEIGHT):
                if self.get_piece(x, y) != self.EMPTY:
                    height = self.HEIGHT - y
                    break
            heights.append(height)
        return heights

    def clear(self):
        for x in range(self.WIDTH):
            for y in range(self.HEIGHT):
                self.grid[x][y] = self.EMPTY

    def copy(self):
        new_board = Board()
        for x in range(self.WIDTH):
            for y in range(self.HEIGHT):
                new_board.grid[x][y] = self.grid[x][y]
        return new_board

    def __str__(self):
        return self.render_ascii()

    def render_ascii(self, falling_piece=None):
        """Return an ASCII representation. Optionally overlay a falling piece (not yet locked)."""
        overlay = {}
        if falling_piece is not None:
            for x, y, block in falling_piece.get_block_positions():
                overlay[(x, y)] = block
        lines = []
        for y in range(self.HEIGHT):
            row_chars = []
            for x in range(self.WIDTH):
                cell = overlay.get((x, y), self.get_piece(x, y))
                if cell == self.EMPTY or cell is None:
                    ch = '.'
                else:
                    if hasattr(cell, 'is_garbage') and cell.is_garbage:
                        ch = '#'
                    elif hasattr(cell, 'is_breaker') and cell.is_breaker:
                        # Breakers: distinct symbol for clarity
                        ch = '*'
                    elif hasattr(cell, 'color'):
                        ch = cell.color[0]
                    else:
                        ch = str(cell)[0]
                row_chars.append(ch)
            lines.append(''.join(row_chars))
        return '\n'.join(lines)