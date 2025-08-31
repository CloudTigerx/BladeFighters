class Board:
    WIDTH = 12
    HEIGHT = 24
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
        if self.is_in_bounds(x, y):
            return self.grid[x][y]
        return None

    def set_piece(self, x, y, value):
        if self.is_in_bounds(x, y):
            self.grid[x][y] = value

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