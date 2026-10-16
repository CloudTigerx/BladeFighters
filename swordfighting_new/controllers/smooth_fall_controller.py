from __future__ import annotations

import os


class SmoothFallController:
    def compute_y_offset_pixels(
        self,
        client,
        board,
        piece,
        is_current_piece: bool,
        *,
        faller_occupied: set | None = None,
        ignore_piece=None,
        cell_h: int,
    ) -> int:
        # Do not smooth special horizontal-sword rendering (custom cadence)
        if getattr(piece, 'horizontal_sword', False):
            return 0

        # Smooth fall interpolation can read as a "magnetic snap" at row boundaries,
        # especially when pieces enter from the hidden spawn row.
        # Default ON; disable via BF_PG_SMOOTH_FALL=0.
        try:
            smooth_fall = str(os.getenv('BF_PG_SMOOTH_FALL', '1') or '1').strip().lower() in ('1', 'true', 'yes', 'on')
        except Exception:
            smooth_fall = True
        if is_current_piece and getattr(piece, 'controllable', True) and not bool(smooth_fall):
            return 0

        def _anchor_row() -> int:
            # Use a stable integer row anchor for smoothing resets.
            try:
                y_val = getattr(piece, 'y', None)
                if y_val is not None:
                    return int(y_val)
            except Exception:
                pass
            try:
                return int(min(y for _x, y, _c in piece.get_block_positions()))
            except Exception:
                return 0

        fighter = client._get_fighter_for_board(board)
        key = id(piece)
        # Treat non-controllable current piece (e.g., split faller) as autonomous for visuals
        treat_as_autonomous = bool(is_current_piece and not getattr(piece, 'controllable', True))
        if is_current_piece and not treat_as_autonomous:
            interval = fighter.movement.timing.interval_for_level(level=1, fast=fighter.movement.is_fast_falling())
            # Require all blocks to have empty cell below for interpolation to avoid half-overlap on horizontals
            can_fall = True
            for x, y, _ in piece.get_block_positions():
                ny = y + 1
                if ny >= board.HEIGHT or board.get_piece(x, ny) != board.EMPTY:
                    can_fall = False
                    break
            # Visual clamp: if another faller sits directly below, do not interpolate into it
            if can_fall and faller_occupied:
                for x, y, _ in piece.get_block_positions():
                    if (x, y + 1) in faller_occupied:
                        can_fall = False
                        break
        else:
            # Autonomous fallers / garbage pieces (including split fallers)
            interval = getattr(piece, 'autonomous_fall_interval', fighter.movement.gravity.autonomous_fall_interval)
            can_fall = True
            # Treat only board as obstacle for interpolation (avoid jitter from fellow fallers)
            for x, y, _ in piece.get_block_positions():
                ny = y + 1
                if ny >= board.HEIGHT or board.get_piece(x, ny) != board.EMPTY:
                    can_fall = False
                    break

        frame = int(getattr(client.session, 'frame', 0) or 0)
        row = _anchor_row()

        state = client._last_offsets.get(key)
        if not isinstance(state, dict):
            state = {}

        if state.get('row') != row:
            state = {'row': row, 'progress': 0.0, 'last_frame': frame}

        if not can_fall or interval <= 1:
            # Snap to grid when locked / not falling.
            client._last_offsets[key] = {'row': row, 'progress': 0.0, 'last_frame': frame}
            return 0

        # Monotonic per-row interpolation: avoids 'bounce' when fall interval changes mid-row (e.g., fast-fall toggle).
        if state.get('last_frame') != frame:
            max_px = float(max(0, int(cell_h) - 1))
            if is_current_piece and not treat_as_autonomous:
                step = float(int(cell_h)) / float(max(1, interval))
                state['progress'] = min(max_px, float(state.get('progress', 0.0) or 0.0) + step)
            else:
                timer_val = float(getattr(piece, 'autonomous_fall_timer', 0.0) or 0.0)
                phase = max(0.0, min(1.0, timer_val / float(max(1, interval))))
                state['progress'] = min(max_px, float(int(cell_h)) * phase)
            state['last_frame'] = frame

        y_off = int(float(state.get('progress', 0.0) or 0.0))
        client._last_offsets[key] = state
        return y_off
