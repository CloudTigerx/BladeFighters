"""movement_controller.py - Handles all piece movement, rotation, and locking logic.

Responsibilities:
- Current piece management (current piece, next piece)
- Processing movement and rotation intents
- Gravity application timing and logic
- Piece locking determination and execution
- New piece spawning after chains or locks
"""
from __future__ import annotations
import os
from typing import Dict, Any, Tuple, Optional

from swordfighting_new.core.board import Board
from swordfighting_new.pieces.piece import Piece
from swordfighting_new.pieces.shared_piece_queue import SharedPieceQueue
from swordfighting_new.mechanics.movement import PieceMover
from swordfighting_new.mechanics.gravity import GravityManager
from swordfighting_new.mechanics.timing import TimingConfig


class MovementController:
    """Handles all piece movement, rotation, gravity, and locking logic."""
    
    def __init__(self, board: Board, piece_mover: PieceMover, gravity_manager: GravityManager, 
                 timing: TimingConfig, spawn_x: int = 3, piece_queue: SharedPieceQueue | None = None):
        self.board = board
        self.mover = piece_mover
        self.gravity = gravity_manager
        self.timing = timing
        self.spawn_x = spawn_x

        # Defeat mode (opt-in experimentation).
        #
        # Default behavior:
        # - game over on spawn overlap / above-board topout (plus optional full-column defeat if BF_GAME_OVER_COLUMN is set)
        #
        # Mode B (BF_DEFEAT_MODE=b):
        # - always enable the full-column defeat check on the spawn column
        # - skip the "top row full" defeat guard
        try:
            self.defeat_mode = str(os.getenv('BF_DEFEAT_MODE', '') or '').strip().lower()
        except Exception:
            self.defeat_mode = ''

        # Optional full-column defeat rule.
        # Enabled only when BF_GAME_OVER_COLUMN is explicitly provided.
        # (Default gameplay rule remains: game over only on spawn overlap / above-board topout.)
        if str(getattr(self, 'defeat_mode', '') or '') in ('b', 'mode_b', 'spawn_column_full'):
            # Mode B: always monitor the spawn column.
            self.game_over_x = int(spawn_x)
        else:
            env_game_over = os.getenv('BF_GAME_OVER_COLUMN', None)
            if env_game_over is None or str(env_game_over).strip() == '':
                self.game_over_x = None
            else:
                try:
                    game_over_col_1b = int(str(env_game_over).strip())
                except Exception:
                    game_over_col_1b = int(spawn_x) + 1
                # Clamp to valid 1-based range then convert to 0-based x.
                try:
                    w = int(getattr(self.board, 'WIDTH', 6) or 6)
                except Exception:
                    w = 6
                game_over_col_1b = max(1, min(int(w), int(game_over_col_1b)))
                self.game_over_x = int(game_over_col_1b) - 1

            # Deterministic shared sequence support
        self.piece_queue = piece_queue
        self.piece_index = 0  # index into shared queue if provided

        if self.piece_queue is not None:
            # Pull two specs deterministically (index 0,1)
            spec0 = self.piece_queue.get(self.piece_index)
            spec1 = self.piece_queue.get(self.piece_index + 1)
            self.current_piece = Piece.from_spec(spec0, self.spawn_x)
            self.next_piece = Piece.from_spec(spec1, self.spawn_x)
            self.piece_index += 2
        else:
            # Legacy random spawning
            self.current_piece = Piece.spawn_random(self.spawn_x)
            self.next_piece = Piece.spawn_random(self.spawn_x)

        # Allow per-board spawn rows.
        try:
            spawn_y = getattr(self.board, 'spawn_y', None)
            if spawn_y is None:
                raise ValueError('no board.spawn_y')
            spawn_y = int(spawn_y)
        except Exception:
            try:
                spawn_y = int(os.getenv('BF_SPAWN_Y', '-2'))
            except Exception:
                spawn_y = -2
        try:
            self.current_piece.y = int(spawn_y)
        except Exception:
            pass
        try:
            self.next_piece.y = int(spawn_y)
        except Exception:
            pass
        self.fast = False

        # Lock grace: frames the player can still move/rotate after landing.
        # This is disabled while any block is above the visible board (y < 0),
        # and also disabled when the piece touches the top row (y == 0).
        self._grounded_frames: int = 0

        # Entry/top-out grace: if a piece is blocked while still above the visible
        # board, give the player a short window to slide/rotate into a valid entry.
        # If they cannot (or the timer expires), it's game over.
        self._blocked_above_frames: int = 0
        # Tracks how many frames the player is actively trying to move/rotate while
        # stuck above-board. Used to make force-settle trigger sooner only when
        # the player is spamming inputs (anti-stall abuse), not during normal play.
        self._blocked_above_input_frames: int = 0

        # When a piece becomes grounded while entirely above-board, we allow a
        # one-time snap-settle pass before starting the entry grace window.
        # This avoids premature defeat when the settled board can still fall.
        self._blocked_above_settle_attempted: bool = False
        
        # Game state
        self.defeated = False

        # Defeat instrumentation (used for postgame debugging).
        # last_defeat_reason: short stable identifier (e.g. 'inbound_overflow', 'spawn_overlap').
        # last_defeat_context: small JSON-serializable dict with useful details.
        self.last_defeat_reason: str | None = None
        self.last_defeat_context: dict[str, Any] = {}

    def _mode_b_enabled(self) -> bool:
        return str(getattr(self, 'defeat_mode', '') or '') in ('b', 'mode_b', 'spawn_column_full')

    def _mark_defeat(self, reason: str, context: dict[str, Any] | None = None) -> None:
        """Mark defeated and store the first defeat reason/context.

        This is best-effort only; it must never raise.
        """
        try:
            self.defeated = True
        except Exception:
            return
        try:
            if getattr(self, 'last_defeat_reason', None) is None:
                self.last_defeat_reason = str(reason or '').strip().lower() or None
                self.last_defeat_context = dict(context or {})
        except Exception:
            # Never crash in debug instrumentation.
            pass

    def _pre_defeat_settle_board(self, transient_piece: Piece | None = None) -> None:
        """Best-effort snap-settle before declaring defeat.

        This avoids premature game-over when the settled board can still fall.

        We treat *empty* transient cells (from the falling/spawned piece) as solid
        blockers for the snap-settle pass, so the board doesn't teleport into them.
        If a transient cell is already occupied on the board, we do NOT include it
        as an occupied cell, because doing so would prevent that block from moving
        during the settle pass.
        """
        occupied: set[tuple[int, int]] = set()
        if transient_piece is not None:
            try:
                for x, y, _b in transient_piece.get_block_positions():
                    xi = int(x)
                    yi = int(y)
                    if yi < 0:
                        continue
                    if not self.board.is_in_bounds(xi, yi):
                        continue
                    try:
                        if self.board.get_piece(xi, yi) == self.board.EMPTY:
                            occupied.add((xi, yi))
                    except Exception:
                        continue
            except Exception:
                occupied = set()

        try:
            self.gravity.apply_global_gravity(occupied_cells=occupied)
        except Exception:
            # Never crash while trying to be lenient.
            pass

    def _is_game_over_column_full(self) -> bool:
        if getattr(self, 'game_over_x', None) is None:
            return False
        try:
            x = int(getattr(self, 'game_over_x', 0) or 0)
        except Exception:
            x = 0
        try:
            w = int(getattr(self.board, 'WIDTH', 6) or 6)
            h = int(getattr(self.board, 'HEIGHT', 12) or 12)
        except Exception:
            w, h = 6, 12

        if not (0 <= int(x) < int(w)):
            return False

        # "Full" means no empty cells anywhere in the designated column.
        for y in range(int(h)):
            try:
                if self.board.get_piece(int(x), int(y)) == self.board.EMPTY:
                    return False
            except Exception:
                # If we can't safely read a cell, be conservative (not full).
                return False
        return True

    def check_game_over_column_full_defeat(self, transient_piece: Piece | None = None) -> bool:
        """Mark defeat if the configured game-over column is fully filled.

        This is intentionally separate from spawn-overlap defeat: it ensures we
        don't miss defeat when the monitored column becomes completely full
        (e.g., due to inbound/garbage) even if the spawn column remains clear.
        """
        if self.defeated:
            return True

        # Rule disabled unless explicitly configured.
        if getattr(self, 'game_over_x', None) is None:
            return False

        if not self._is_game_over_column_full():
            return False

        # Best-effort settle pass before finalizing defeat.
        self._pre_defeat_settle_board(transient_piece=transient_piece)
        if self._is_game_over_column_full():
            try:
                if os.getenv('BF_MOVEMENT_DEBUG', '0') == '1':
                    print(
                        "[MOVEMENT] GAME OVER! "
                        f"Game-over column full (col={int(getattr(self, 'game_over_x', 0) or 0) + 1})."
                    )
            except Exception:
                pass
            self._mark_defeat('game_over_column_full', {'col_1b': int(getattr(self, 'game_over_x', 0) or 0) + 1})
            return True
        return False

    def _is_top_row_full(self) -> bool:
        """Return True if the visible top row (y=0) contains no empty cells."""
        try:
            w = int(getattr(self.board, 'WIDTH', 6) or 6)
        except Exception:
            w = 6

        for x in range(int(w)):
            try:
                if self.board.get_piece(int(x), 0) == self.board.EMPTY:
                    return False
            except Exception:
                # If we can't safely read a cell, be conservative (not full).
                return False
        return True

    def check_top_row_full_defeat(self, transient_piece: Piece | None = None) -> bool:
        """Mark defeat if the visible top row is completely filled.

        This is the intuitive "top out" condition when inbound/garbage covers the
        entire top of the board. We apply a best-effort snap-settle first and then
        re-check to avoid false defeats from floating blocks.
        """
        if self.defeated:
            return True

        if not self._is_top_row_full():
            return False

        # Best-effort settle pass before finalizing defeat.
        self._pre_defeat_settle_board(transient_piece=transient_piece)
        if self._is_top_row_full():
            try:
                if os.getenv('BF_MOVEMENT_DEBUG', '0') == '1':
                    print('[MOVEMENT] GAME OVER! Top row full (y=0).')
            except Exception:
                pass
            self._mark_defeat('top_row_full', {'row': 0})
            return True

        return False
        
    def update(self, intents: Dict[str, Any], frame: int) -> Tuple[bool, bool]:
        """
        Update piece movement, gravity, and locking.
        
        Args:
            intents: Input intents (move, rotate_cw, rotate_ccw, fast)
            frame: Current game frame
            
        Returns:
            Tuple of (should_lock_piece, gravity_applied)
        """
        if self.defeated:
            return False, False

        if self.current_piece is None:
            return False, False

        # Hard defeat guard: if the top row is fully filled, end immediately.
        # Mode B: skip this guard and rely on the configured full-column rule.
        if (not self._mode_b_enabled()) and self.check_top_row_full_defeat(transient_piece=self.current_piece):
            return False, False

        # Hard defeat guard: if the designated game-over column is completely full,
        # end immediately (regardless of spawn-overlap rule).
        if self.check_game_over_column_full_defeat(transient_piece=self.current_piece):
            return False, False
            
        p = self.current_piece
        should_apply_gravity = False
        should_lock = False

        debug_enabled = os.getenv('BF_MOVEMENT_DEBUG', '0') == '1'

        def _dbg(msg: str) -> None:
            if not debug_enabled:
                return
            try:
                print(f"[MOVEMENT][DBG] {msg}")
            except Exception:
                pass

        def _positions(piece: Piece):
            try:
                return list(piece.get_block_positions())
            except Exception:
                return []

        def _any_above_board(pos) -> bool:
            return any(int(y) < 0 for _x, y, _b in pos)

        def _touches_top_row(pos) -> bool:
            return any(int(y) == 0 for _x, y, _b in pos)

        def _any_in_bounds(pos) -> bool:
            try:
                for x, y, _b in pos:
                    if self.board.is_in_bounds(int(x), int(y)):
                        return True
            except Exception:
                return False
            return False

        def _has_escape_move(piece: Piece) -> bool:
            # Any legal move/rotation counts as an escape opportunity.
            try:
                if self.mover.can_move(piece, -1, 0) or self.mover.can_move(piece, 1, 0):
                    return True
            except Exception:
                pass
            try:
                if self.mover.can_rotate(piece, clockwise=True, dx=0) or self.mover.can_rotate(piece, clockwise=False, dx=0):
                    return True
            except Exception:
                pass
            return False

        def _in_bounds_and_free(pos) -> bool:
            try:
                w = int(getattr(self.board, 'WIDTH', 6) or 6)
                h = int(getattr(self.board, 'HEIGHT', 12) or 12)
            except Exception:
                w, h = 6, 12
            for x, y, _b in pos:
                xi = int(x)
                yi = int(y)
                if not (0 <= xi < w):
                    return False
                if yi >= h:
                    return False
                # Allow negative y (hidden rows); only enforce occupancy in visible grid.
                if yi >= 0:
                    try:
                        if self.board.get_piece(xi, yi) != self.board.EMPTY:
                            return False
                    except Exception:
                        return False
            return True

        block_positions = _positions(p)
        any_above_board = _any_above_board(block_positions)
        touches_top_row = _touches_top_row(block_positions)

        # Determine current lock grace window.
        # Top row should not allow the grace timing (immediate lock once grounded).
        try:
            lock_grace_frames = int(getattr(self.timing, 'lock_delay_frames', 0) or 0)
        except Exception:
            lock_grace_frames = 0
        lock_grace_frames = max(0, lock_grace_frames)
        if touches_top_row:
            lock_grace_frames = 0

        # Track grounded frames for controllable pieces.
        grounded_now = False
        try:
            # IMPORTANT: use GravityManager.can_fall() so horizontal pieces
            # resting on uneven columns are NOT considered grounded when one
            # side can still descend (split-fall behavior).
            g = getattr(self, 'gravity', None)
            if g is not None and hasattr(g, 'can_fall'):
                grounded_now = (not bool(g.can_fall(p)))
            else:
                grounded_now = (not self.mover.can_move(p, 0, 1))
        except Exception:
            grounded_now = False

        if p.controllable and grounded_now and (not any_above_board):
            self._grounded_frames += 1
        else:
            self._grounded_frames = 0

        # Entry/top-out grace window (only relevant while above the board).
        # We intentionally allow a longer window here than lock delay to avoid
        # the force-settle/slide feeling like an immediate "jolt" during normal
        # near-top play, while still preventing indefinite stalling.
        try:
            base_lock = int(getattr(self.timing, 'lock_delay_frames', 0) or 0)
        except Exception:
            base_lock = 0
        base_lock = max(0, int(base_lock))
        entry_grace_frames = max(90, base_lock * 6)
        entry_grace_frames = min(240, int(entry_grace_frames))

        # If the player is repeatedly trying to move/rotate while stuck above-board,
        # resolve sooner so the game can't be stalled out via spam.
        spam_grace_frames = max(20, min(60, int(entry_grace_frames // 3)))
        spam_threshold_frames = 8

        # Check gravity timing and locking conditions
        if p.controllable:
            # If the piece is above the visible board, never allow locking.
            # This prevents the invisible-row exploit while still letting the player slide/rotate to a valid drop.
            if any_above_board:
                should_lock = False
            else:
                # If grounded and lock grace expired, lock now.
                if grounded_now and (lock_grace_frames == 0 or self._grounded_frames > lock_grace_frames):
                    p.controllable = False
                    should_lock = True

            interval = self.timing.interval_for_level(level=1, fast=bool(intents.get('fast')))

            # Spawn/top-row slowdown: while the piece is in the top visible row (y == 0),
            # apply gravity 3x slower to give a little extra reaction time.
            # This automatically reverts once the piece enters the next row (max y becomes 1).
            try:
                # Default to 1 (disabled). Enable via env var when desired.
                top_row_slow_mult = float(os.getenv('BF_TOP_ROW_FALL_SLOW_MULT', '1') or '1')
            except Exception:
                top_row_slow_mult = 1.0
            try:
                max_y = max(int(y) for _x, y, _b in block_positions) if block_positions else 999
            except Exception:
                max_y = 999
            if (not bool(intents.get('fast'))) and top_row_slow_mult > 1 and int(max_y) == 0:
                interval = int(max(1, round(float(interval) * float(top_row_slow_mult))))

            should_apply_gravity = (frame % max(1, interval) == 0)
        elif not p.controllable:
            # Autonomous piece - will be handled in gravity application
            pass

        # Handle intents (movement / rotation) only if piece is still controllable
        if p.controllable:
            move = intents.get('move', 0)
            if move != 0:
                moved = self.mover.move(p, move, 0)
                if moved:
                    self._grounded_frames = 0
                    self._blocked_above_frames = 0
                    self._blocked_above_input_frames = 0
            if intents.get('rotate_cw'):
                rotated = self.mover.rotate(p, clockwise=True)
                if rotated:
                    self._grounded_frames = 0
                    self._blocked_above_frames = 0
                    self._blocked_above_input_frames = 0
            if intents.get('rotate_ccw'):
                rotated = self.mover.rotate(p, clockwise=False)
                if rotated:
                    self._grounded_frames = 0
                    self._blocked_above_frames = 0
                    self._blocked_above_input_frames = 0

        self.fast = bool(intents.get('fast'))

        # Recompute after inputs.
        block_positions = _positions(p)
        any_above_board = _any_above_board(block_positions)
        touches_top_row = _touches_top_row(block_positions)
        any_in_bounds = _any_in_bounds(block_positions)
        try:
            g = getattr(self, 'gravity', None)
            if g is not None and hasattr(g, 'can_fall'):
                grounded_now = (not bool(g.can_fall(p)))
            else:
                grounded_now = (not self.mover.can_move(p, 0, 1))
        except Exception:
            grounded_now = False

        # Legit near-top case: allow locking if at least one block is actually in the board.
        # Example: column is 11/12 high and a vertical piece lands with one block at y=0 and
        # the other at y=-1. The y=-1 block should have no effect (ignored), while the y=0
        # block locks normally. This avoids an unnecessary force-settle "jolt".
        if p.controllable and grounded_now and any_above_board and any_in_bounds:
            p.controllable = False
            self._grounded_frames = 0
            self._blocked_above_frames = 0
            self._blocked_above_input_frames = 0
            return True, False

        # Update above-board stall counter after inputs as well.
        if p.controllable and grounded_now and any_above_board:
            self._blocked_above_frames += 1
            try:
                had_adjust_intent = bool(intents.get('move', 0)) or bool(intents.get('rotate_cw')) or bool(intents.get('rotate_ccw'))
            except Exception:
                had_adjust_intent = False
            if had_adjust_intent:
                self._blocked_above_input_frames += 1
        else:
            self._blocked_above_frames = 0
            self._blocked_above_input_frames = 0
            self._blocked_above_settle_attempted = False

        # Above-board entry grace: if the piece becomes grounded while still entirely
        # above the visible board, allow a short window to slide/rotate into a valid
        # entry column. Before starting the grace timer, attempt a one-time snap-settle
        # so floating blocks don't cause premature top-outs.
        if p.controllable and any_above_board and grounded_now and (not any_in_bounds):
            if not bool(getattr(self, '_blocked_above_settle_attempted', False)):
                self._blocked_above_settle_attempted = True
                self._pre_defeat_settle_board(transient_piece=None)

                # Recompute after settle: if we can now fall (or any block enters bounds),
                # do not top-out.
                block_positions = _positions(p)
                any_above_board = _any_above_board(block_positions)
                any_in_bounds = _any_in_bounds(block_positions)
                try:
                    g = getattr(self, 'gravity', None)
                    if g is not None and hasattr(g, 'can_fall'):
                        grounded_now = (not bool(g.can_fall(p)))
                    else:
                        grounded_now = (not self.mover.can_move(p, 0, 1))
                except Exception:
                    grounded_now = False

                if (not grounded_now) or (not any_above_board) or any_in_bounds:
                    self._blocked_above_frames = 0
                    self._blocked_above_input_frames = 0
                    return False, False

            escape_possible = _has_escape_move(p)
            if not escape_possible:
                # No legal move exists to enter the board: defeat.
                self._mark_defeat(
                    'above_board_no_escape',
                    {
                        'blocked_above_frames': int(getattr(self, '_blocked_above_frames', 0) or 0),
                        'spawn_x_1b': int(getattr(self, 'spawn_x', 0) or 0) + 1,
                    },
                )
                return False, False

            # Grace window: shorter if the player is actively spamming inputs while stuck.
            try:
                allowed = int(entry_grace_frames)
            except Exception:
                allowed = 120
            try:
                if int(self._blocked_above_input_frames) >= int(spam_threshold_frames):
                    allowed = int(spam_grace_frames)
            except Exception:
                pass
            allowed = max(1, int(allowed))

            if int(self._blocked_above_frames) <= int(allowed):
                # Stay alive, but do not apply gravity this frame (it would immediately fail
                # and could trigger defeat via the gravity branch).
                return False, False

            # Grace expired: one last snap-settle + re-check, then defeat.
            self._pre_defeat_settle_board(transient_piece=None)
            block_positions = _positions(p)
            any_above_board = _any_above_board(block_positions)
            any_in_bounds = _any_in_bounds(block_positions)
            try:
                g = getattr(self, 'gravity', None)
                if g is not None and hasattr(g, 'can_fall'):
                    grounded_now = (not bool(g.can_fall(p)))
                else:
                    grounded_now = (not self.mover.can_move(p, 0, 1))
            except Exception:
                grounded_now = False
            if (not grounded_now) or (not any_above_board) or any_in_bounds:
                self._blocked_above_frames = 0
                self._blocked_above_input_frames = 0
                return False, False
            self._mark_defeat(
                'above_board_grace_expired',
                {
                    'blocked_above_frames': int(getattr(self, '_blocked_above_frames', 0) or 0),
                    'spawn_x_1b': int(getattr(self, 'spawn_x', 0) or 0) + 1,
                },
            )
            return False, False

        # Apply gravity or lock piece
        gravity_applied = False
        if should_lock:
            return True, False  # Signal that piece should be locked
        elif should_apply_gravity:
            # Apply gravity normally (piece can fall)
            if not self.gravity.apply_gravity(self.current_piece):
                # If we're still above the visible board, this is an immediate top-out
                # (entry grace is disabled).
                if any_above_board:
                    self._mark_defeat(
                        'above_board_gravity_topout',
                        {
                            'spawn_x_1b': int(getattr(self, 'spawn_x', 0) or 0) + 1,
                        },
                    )
                    return False, False
                return True, False  # Piece hit bottom, should lock
            else:
                gravity_applied = True
                self._grounded_frames = 0
                self._blocked_above_frames = 0
        elif not p.controllable:
            # Autonomous piece - apply gravity every frame, let the piece handle its own timing
            if not self.gravity.apply_gravity(self.current_piece):
                return True, False  # Piece hit bottom, should lock
            else:
                gravity_applied = True

        return False, gravity_applied

    def lock_current_piece(self) -> bool:
        """
        Lock the current piece to the board.
        
        Returns:
            True if piece was successfully locked, False if game over
        """
        if self.current_piece is None:
            return False

        # Allow "partial" locks when a piece is grounded and at least one block is
        # in-bounds (e.g., vertical piece in an 11/12 column). Above-board blocks
        # (y < 0) are ignored by GravityManager.lock_piece.
        # Still disallow locking a piece that is entirely above the board, to avoid
        # disappearing pieces / invisible-row abuse.
        try:
            pos = list(self.current_piece.get_block_positions())
        except Exception:
            return False
        try:
            any_in_bounds = any(self.board.is_in_bounds(int(x), int(y)) for x, y, _b in pos)
        except Exception:
            any_in_bounds = False
        if not any_in_bounds:
            return False

        # Lock current piece
        self.gravity.lock_piece(self.current_piece)
        
        # Reset fast flag
        self.fast = False
        
        return True

    def spawn_new_piece_post_chain(self) -> bool:
        """
        Spawn a new piece after a chain completes.
        
        Returns:
            True if successful, False if game over (spawn column blocked)
        """
        # Use the next piece as current, generate new next piece
        self.current_piece = self.next_piece
        self.current_piece.x = self.spawn_x
        try:
            spawn_y = getattr(self.board, 'spawn_y', None)
            if spawn_y is None:
                raise ValueError('no board.spawn_y')
            spawn_y = int(spawn_y)
        except Exception:
            try:
                spawn_y = int(os.getenv('BF_SPAWN_Y', '-2'))
            except Exception:
                spawn_y = -2
        self.current_piece.y = int(spawn_y)

        if self.piece_queue is not None:
            # Get next spec at current index, then advance
            spec = self.piece_queue.get(self.piece_index)
            self.next_piece = Piece.from_spec(spec, self.spawn_x)
            self.piece_index += 1
        else:
            self.next_piece = Piece.spawn_random(self.spawn_x)

        # Keep preview piece spawn row consistent (doesn't affect preview render, but keeps state sane).
        try:
            self.next_piece.y = int(spawn_y)
        except Exception:
            pass

        # If the monitored game-over column is already completely full, defeat now.
        if self.check_game_over_column_full_defeat(transient_piece=self.current_piece):
            return False
        
        # Game over only if the newly spawned piece overlaps occupied cells.
        # This matches the intended rule described in `swordfighting_new/pygame_client.py`.
        try:
            pos = list(self.current_piece.get_block_positions())
        except Exception:
            pos = []

        spawn_overlaps = []
        for x, y, _b in pos:
            try:
                xi = int(x)
                yi = int(y)
            except Exception:
                continue
            if yi < 0:
                continue
            try:
                if self.board.get_piece(xi, yi) != self.board.EMPTY:
                    spawn_overlaps.append((xi, yi))
            except Exception:
                continue

        if spawn_overlaps:
            # Before declaring defeat, give the settled board one snap-settle.
            self._pre_defeat_settle_board(transient_piece=self.current_piece)

            # Re-check overlaps after settling.
            spawn_overlaps = []
            try:
                pos2 = list(self.current_piece.get_block_positions())
            except Exception:
                pos2 = []
            for x, y, _b in pos2:
                try:
                    xi = int(x)
                    yi = int(y)
                except Exception:
                    continue
                if yi < 0:
                    continue
                try:
                    if self.board.get_piece(xi, yi) != self.board.EMPTY:
                        spawn_overlaps.append((xi, yi))
                except Exception:
                    continue

        if spawn_overlaps:
            try:
                if os.getenv('BF_MOVEMENT_DEBUG', '0') == '1':
                    print(
                        "[MOVEMENT] GAME OVER! "
                        f"Spawn overlap at {spawn_overlaps}; "
                        f"spawn_x={int(getattr(self, 'spawn_x', 0)) + 1}"
                    )
                    try:
                        print("[MOVEMENT][DBG] Board at defeat:\n" + str(self.board))
                    except Exception:
                        pass
            except Exception:
                pass
            self._mark_defeat(
                'spawn_overlap',
                {
                    'cells': list(spawn_overlaps),
                    'spawn_x_1b': int(getattr(self, 'spawn_x', 0) or 0) + 1,
                },
            )
            return False

        # Reset lock grace for the new piece.
        self._grounded_frames = 0
        self._blocked_above_frames = 0
            
        return True

    # Accessors
    def get_current_piece(self) -> Piece:
        """Get the current controllable piece."""
        return self.current_piece
        
    def get_next_piece(self) -> Piece:
        """Get the next piece (for preview)."""
        return self.next_piece
        
    def is_defeated(self) -> bool:
        """Check if player is defeated (game over)."""
        return self.defeated
        
    def is_fast_falling(self) -> bool:
        """Check if current piece is fast falling."""
        return self.fast

    def reset_fast_fall(self):
        """Reset fast fall flag (called after piece locks)."""
        self.fast = False
