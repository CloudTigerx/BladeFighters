"""movement.py - PieceMover handles movement & rotation with simple wall kicks.

Orientation mapping (bottom anchor):
    0: rotator above (0,-1)
    1: right (+1,0)
    2: below (0,+1)
    3: left (-1,0)
Rotation updates orientation modulo 4.
"""

from swordfighting_new.pieces.piece import Piece  # noqa: F401 (used indirectly)


class PieceMover:
    def __init__(self, board):
        self.board = board

    # --- Movement -----------------------------------------------------
    def can_move(self, piece, dx, dy):
        for x, y, _ in piece.get_block_positions():
            nx, ny = x + dx, y + dy
            # Allow negative y (hidden rows) during spawn descent
            if not (0 <= nx < self.board.WIDTH):
                return False
            if ny >= self.board.HEIGHT:
                return False
            # Ignore current cells of the piece (they will be vacated) -> gather set
        current_cells = {(x, y) for x, y, _ in piece.get_block_positions()}
        for x, y, _ in piece.get_block_positions():
            nx, ny = x + dx, y + dy
            if (nx, ny) not in current_cells and ny >= 0:
                # Only check occupancy once within visible grid
                if self.board.get_piece(nx, ny) != self.board.EMPTY:
                    return False
        return True

    def move(self, piece, dx, dy):
        if self.can_move(piece, dx, dy):
            piece.x += dx
            piece.y += dy
            return True
        return False

    # --- Rotation -----------------------------------------------------
    def _relative_second_block(self, piece):
        o = piece.orientation % 4
        if o == 0:  # above
            return (0, -1)
        if o == 1:  # right
            return (1, 0)
        if o == 2:  # below
            return (0, 1)
        return (-1, 0)  # left

    def can_rotate(self, piece, clockwise=True, dx=0):
        if len(piece.blocks) != 2:
            return False
        anchor_x = piece.x + dx
        anchor_y = piece.y
        rel_x, rel_y = self._relative_second_block(piece)
        if clockwise:
            new_rel_x, new_rel_y = -rel_y, rel_x
        else:
            new_rel_x, new_rel_y = rel_y, -rel_x
        new_top_x = anchor_x + new_rel_x
        new_top_y = anchor_y + new_rel_y
        # Bounds: allow negative y (hidden rows) but enforce x range; disallow y beyond bottom.
        for (tx, ty) in [(anchor_x, anchor_y), (new_top_x, new_top_y)]:
            if not (0 <= tx < self.board.WIDTH):
                return False
            if ty >= self.board.HEIGHT:
                return False
        current_cells = {(x, y) for x, y, _ in piece.get_block_positions()}
        for (tx, ty) in [(anchor_x, anchor_y), (new_top_x, new_top_y)]:
            if ty >= 0 and (tx, ty) not in current_cells and self.board.get_piece(tx, ty) != self.board.EMPTY:
                return False
        return True

    def rotate(self, piece, clockwise=True):
        # Standard rotate in place
        if self.can_rotate(piece, clockwise, dx=0):
            piece.orientation = (piece.orientation + (1 if clockwise else -1)) % 4
            return True
        # Limited wall kicks (±1 only) to avoid tunneling through narrow columns
        for dx in (-1, 1):
            if self.can_rotate(piece, clockwise, dx=dx):
                piece.x += dx
                piece.orientation = (piece.orientation + (1 if clockwise else -1)) % 4
                return True
        # Attempt vertical flip (0 <-> 2) if rotation impossible and piece is vertical
        if self._attempt_vertical_flip(piece):
            return True
        return False

    # --- Vertical flip ----------------------------------------------
    def _attempt_vertical_flip(self, piece):
        """Flip vertical orientation (0 <-> 2) without horizontal rotation.

        Used when a normal rotation is blocked but designer allows a direct
        vertical inversion if the destination cell for the rotator is free.
        Returns True if flip performed.
        """
        if len(piece.blocks) != 2:
            return False
        if piece.orientation not in (0, 2):
            return False
        # Determine target orientation and relative offset of rotator
        new_orientation = 2 if piece.orientation == 0 else 0
        # New relative position: orientation 0 => rotator above (0,-1); 2 => below (0,+1)
        rel_y = -1 if new_orientation == 0 else 1
        target_y = piece.y + rel_y
        target_x = piece.x
        # Bounds: allow hidden rows (y < 0); ensure inside horizontal and below top limit
        if not (0 <= target_x < self.board.WIDTH):
            return False
        if target_y >= self.board.HEIGHT:
            return False
        # Occupancy check only if entering visible grid
        if target_y >= 0 and self.board.get_piece(target_x, target_y) != self.board.EMPTY:
            return False
        piece.orientation = new_orientation
        return True

    # --- Hard drop (optional utility) ---------------------------------
    def hard_drop(self, piece):
        moved = False
        while self.move(piece, 0, 1):
            moved = True
        return moved


# Usage example (pseudo):
# mover = PieceMover(board)
# mover.move(piece, dx, dy)
# mover.rotate(piece, clockwise=True)
# mover.hard_drop(piece)
