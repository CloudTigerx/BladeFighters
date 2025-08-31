# gravity.py

"""
Gravity and piece locking logic for Blade Fighters.
Handles:
- Standard gravity (piece falls by 1 each tick)
- Piece locking (when piece can't move down)
- Extension points for advanced mechanics:
    - Horizontal piece split gravity (uneven columns)
    - Wallflip mechanic (rotation at grid edges)
"""

class GravityManager:
    def __init__(self, board, mover=None, timing=None):
        self.board = board
        if mover is None:
            from swordfighting_new.mechanics.movement import PieceMover
            self.mover = PieceMover(board)
        else:
            self.mover = mover
        # Get timing config for autonomous fall interval
        if timing is None:
            from swordfighting_new.mechanics.timing import DEFAULT_TIMING
            timing = DEFAULT_TIMING
        self.autonomous_fall_interval = timing.autonomous_fall_interval_frames
    def should_lock(self, piece):
        """
        Returns True if the piece cannot move down (should be locked).
        """
        return not self.apply_gravity(piece)

    def can_fall(self, piece):
        """
        Returns True if the piece can move down without actually moving it.
        This is a non-destructive check used to prevent input on pieces about to lock.
        """
        # Handle autonomous pieces with their own timing
        if not piece.controllable:
            if piece.autonomous_fall_timer + 1 < piece.autonomous_fall_interval:
                return True  # Still falling, just not this frame

        if len(piece.blocks) == 2 and piece.orientation in (1, 3):  # horizontal
            pos = piece.get_block_positions()
            # Normalize left/right ordering
            if pos[0][0] <= pos[1][0]:
                left = pos[0]
                right = pos[1]
            else:
                left = pos[1]
                right = pos[0]
            (lx, ly, lblock) = left
            (rx, ry, rblock) = right
            can_left = self._cell_empty(lx, ly + 1)
            can_right = self._cell_empty(rx, ry + 1)
            # Can fall if either side can move down or if split is possible
            return can_left or can_right

        # Vertical or single-block: check if can move down
        return self.mover.can_move(piece, 0, 1)

    def apply_gravity(self, piece):
        """Apply gravity with split behavior for horizontal pieces.

        Returns True if the piece moved/changed form, False if it should lock.
                Split gravity:
                    If horizontal (orientations 1 or 3 with bottom anchor model) and only one side can descend,
                    lock supported side and let unsupported side continue as autonomous single.
        """
        # Handle autonomous pieces (from splits) with their own timing
        if not piece.controllable:
            piece.autonomous_fall_timer += 1
            if piece.autonomous_fall_timer < piece.autonomous_fall_interval:
                return True  # Still falling, just not this frame
            piece.autonomous_fall_timer = 0  # Reset timer for next fall

        if len(piece.blocks) == 2 and piece.orientation in (1, 3):  # horizontal
            pos = piece.get_block_positions()
            # Normalize left/right ordering
            if pos[0][0] <= pos[1][0]:
                left = pos[0]
                right = pos[1]
            else:
                left = pos[1]
                right = pos[0]
            (lx, ly, lblock) = left
            (rx, ry, rblock) = right
            can_left = self._cell_empty(lx, ly + 1)
            can_right = self._cell_empty(rx, ry + 1)
            if can_left and can_right:
                return self.mover.move(piece, 0, 1)
            if (can_left and not can_right) or (can_right and not can_left):
                # True split: the supported side locks in place; unsupported side keeps falling solo.
                blocked_cell = right if (can_left and not can_right) else left
                falling_cell = left if (can_left and not can_right) else right
                bx, by, bblock = blocked_cell
                fx, fy, fblock = falling_cell
                # Lock blocked block immediately into board
                if self._cell_empty(bx, by):  # Should always be empty since piece not yet locked
                    self.board.set_piece(bx, by, bblock)
                else:
                    # Collision safety; abort split and lock whole piece
                    self.lock_piece(piece)
                    return False
                # Transform piece into single falling block
                piece.blocks = [fblock]
                piece.x, piece.y = fx, fy
                piece.orientation = 0  # orientation irrelevant for single
                piece.controllable = False  # player can no longer manipulate this autonomous faller
                # Set up autonomous timing for consistent fall speed
                piece.autonomous_fall_timer = 0
                piece.autonomous_fall_interval = self.autonomous_fall_interval
                # Attempt to move single block down one (consume gravity step if possible)
                if self._cell_empty(piece.x, piece.y + 1):
                    piece.y += 1
                return True
            # Neither can fall
            return False
        # Vertical or single-block: normal gravity
        if self.mover.move(piece, 0, 1):
            return True
        return False

    def _cell_empty(self, x, y):
        # Treat hidden spawn rows (y < 0) as empty so pieces can descend into the field.
        if y < 0:
            return True
        return self.board.is_in_bounds(x, y) and self.board.get_piece(x, y) == self.board.EMPTY

    def lock_piece(self, piece):
        """
        Locks the piece into the board at its current position.
        """
        for x, y, block in piece.get_block_positions():
            if self.board.is_in_bounds(x, y):
                self.board.set_piece(x, y, block)

    # TODO: Wallflip mechanic (rotation at grid edges)
    # This should be handled in the movement/rotation logic, but gravity may need to trigger it if piece is stuck at wall

# Usage:
# gravity = GravityManager(board, mover)
# if not gravity.apply_gravity(piece):
#     gravity.lock_piece(piece)
#     # Spawn next piece
