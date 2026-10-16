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
        # Timing knobs
        self.autonomous_fall_interval = timing.autonomous_fall_interval_frames
        # Split fall (after horizontal split) runs at its own interval (can be slower)
        self.split_fall_interval = getattr(timing, 'split_fall_interval_frames', self.autonomous_fall_interval)
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
                # Use split-specific interval (can be tuned slower than generic autonomous)
                piece.autonomous_fall_interval = self.split_fall_interval
                # Attempt to move single block down one (consume gravity step if possible)
                # Instead of just checking piece.x, piece.y + 1
                # Check all block positions like the mover does
                can_move_all = True
                for x, y, block in piece.get_block_positions():
                    # Check if the destination would be out of bounds
                    if y + 1 >= self.board.HEIGHT:
                        can_move_all = False
                        break
                    if not self._cell_empty(x, y + 1):
                        can_move_all = False
                        break

                if can_move_all:
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
        # IMPORTANT: Return False if out of bounds to prevent pieces from falling too far
        if not self.board.is_in_bounds(x, y):
            return False
        return self.board.get_piece(x, y) == self.board.EMPTY

    def lock_piece(self, piece):
        """
        Locks the piece into the board at its current position.
        Only locks blocks that are within board bounds.
        """
        for x, y, block in piece.get_block_positions():
            if self.board.is_in_bounds(x, y):
                self.board.set_piece(x, y, block)
            # Silently ignore out-of-bounds blocks (normal for spawning pieces)

    def apply_global_gravity(self, occupied_cells: set[tuple[int, int]] | None = None):
        """Snap-settle gravity for settled board blocks.

        Design intent:
        - Breaker/cascade uses stepwise gravity (visual cascading) after clears.
        - *Global gravity* should settle floating blocks as a unit (no ticking).

        This pass compresses each column segment instantly, treating:
        - held cells (hsword_hold) as immovable blockers
        - transient occupied cells (current falling piece, in-flight garbage fallers)
          as solid blockers (prevents the settled board from teleporting into them)

        Returns:
            List[Piece] (kept for backward-compatibility). Global gravity no longer
            spawns per-cell fallers; it mutates the board directly and returns [].
        """
        occupied_cells = set(occupied_cells or set())

        def _is_held(b) -> bool:
            if b is None or b == self.board.EMPTY:
                return False
            if bool(getattr(b, 'hsword_hold', False)):
                return True
            return False

        # Global gravity policy:
        # - Column-local: blocks fall straight down within their column.
        # - No multi-frame dripping/cascading: compress to the lowest available cells now.
        h = int(self.board.HEIGHT)
        w = int(self.board.WIDTH)
        moved_any = False
        for x in range(w):
            write_y = h - 1
            for y in range(h - 1, -1, -1):
                # Treat transient occupied cells (not represented on the board) as solid.
                if (x, y) in occupied_cells:
                    write_y = y - 1
                    continue

                block = self.board.get_piece(x, y)
                if block == self.board.EMPTY or block is None:
                    continue

                # Held blocks are immovable blockers that segment the column.
                if _is_held(block):
                    write_y = y - 1
                    continue

                if y != write_y:
                    self.board.set_piece(x, write_y, block)
                    self.board.set_piece(x, y, self.board.EMPTY)
                    moved_any = True
                write_y -= 1

        # Optional diagnostics: if enabled, report any non-held block that can fall
        # but was not converted into a faller (should be extremely rare).
        try:
            import os
            if os.getenv('BF_GRAVITY_DEBUG', '0') == '1' and moved_any:
                print(f"[GRAVITY] Global snap-settle moved blocks")
        except Exception:
            pass

        return []

    # TODO: Wallflip mechanic (rotation at grid edges)
    # This should be handled in the movement/rotation logic, but gravity may need to trigger it if piece is stuck at wall

# Usage:
# gravity = GravityManager(board, mover)
# if not gravity.apply_gravity(piece):
#     gravity.lock_piece(piece)
#     # Spawn next piece
