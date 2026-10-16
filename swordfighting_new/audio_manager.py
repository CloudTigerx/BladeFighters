from __future__ import annotations

import os
from typing import Any, Callable


class AudioManager:
    def __init__(
        self,
        *,
        pygame: Any,
        assets_dir_fn: Callable[[], os.PathLike | str],
        enabled: bool = True,
        volume: float = 0.65,
    ) -> None:
        self._pygame = pygame
        self._assets_dir_fn = assets_dir_fn

        self.enabled = bool(enabled)
        try:
            self.volume = float(volume)
        except Exception:
            self.volume = 0.65
        self.volume = max(0.0, min(1.0, float(self.volume)))

        # Loaded SFX assets
        self._puzzle_sfx: dict[str, Any] = {}
        self._gem_place1_row_sfx_keys = {i: f"gem_place1_row_{i}" for i in range(1, 13)}

        # Runtime state for the puzzle SFX tick
        try:
            self._place2_window_frames = max(1, int(os.getenv('BF_SFX_PLACE2_WINDOW_FRAMES', '180') or '180'))
        except Exception:
            self._place2_window_frames = 180

        self.reset_runtime_state()

    def reset_runtime_state(self) -> None:
        self._sfx_last_chain_active: bool | None = None
        self._sfx_last_piece_present: bool | None = None
        self._sfx_last_cluster_count: int = 0
        self._sfx_place2_armed: bool = False
        self._sfx_place2_saw_unstable: bool = False
        self._sfx_place2_deadline_frame: int | None = None
        self._sfx_last_normal_cleared: int = 0
        self._sfx_pending_break_pops: int = 0
        self._sfx_last_break_seq: int | None = None
        self._sfx_last_pending_by_side: dict[str, dict[str, int]] = {
            'player': {'strike': 0, 'sprinkle': 0},
            'ai': {'strike': 0, 'sprinkle': 0},
        }
        self._sfx_last_strike_land_seq_by_side: dict[str, int] = {'player': 0, 'ai': 0}

    def set_volume(self, v: float) -> None:
        try:
            v = float(v)
        except Exception:
            v = float(getattr(self, 'volume', 0.65) or 0.65)
        v = max(0.0, min(1.0, float(v)))
        self.volume = float(v)

        for s in (self._puzzle_sfx or {}).values():
            try:
                s.set_volume(float(self.volume))
            except Exception:
                pass

    def set_enabled(self, enabled: bool) -> None:
        self.enabled = bool(enabled)
        if self.enabled:
            self.init_puzzle_sfx()
        else:
            self.stop_all()

    def stop_all(self) -> None:
        # Best-effort stop any playing sounds.
        try:
            for s in (self._puzzle_sfx or {}).values():
                try:
                    s.stop()
                except Exception:
                    pass
        except Exception:
            pass

    # --- Puzzle SFX (pygame) --------------------------------------
    def init_puzzle_sfx(self) -> None:
        if not bool(self.enabled):
            return

        try:
            if not self._pygame.mixer.get_init():
                self._pygame.mixer.init()
        except Exception:
            self.enabled = False
            return

        # More channels so rapid per-block break SFX can overlap.
        try:
            self._pygame.mixer.set_num_channels(32)
        except Exception:
            pass

        try:
            base_dir = os.path.join(os.fspath(self._assets_dir_fn()), 'sounds')
        except Exception:
            base_dir = None

        def load_named(key: str, candidates: list[str]) -> None:
            if key in self._puzzle_sfx:
                return
            if not base_dir:
                return
            chosen = None
            for fn in candidates:
                try:
                    p = os.path.join(base_dir, str(fn))
                    if os.path.exists(p):
                        chosen = p
                        break
                except Exception:
                    continue
            if not chosen:
                return
            try:
                s = self._pygame.mixer.Sound(chosen)
                try:
                    s.set_volume(float(self.volume))
                except Exception:
                    pass
                self._puzzle_sfx[key] = s
            except Exception:
                return

        # Match Panda puzzle overlay sound keys.
        load_named('gem_place1', ['gem_place1.mp3'])
        load_named('gem_place2', ['gem_place2.mp3', 'gem_place3.mp3'])
        load_named('gem_2x2', ['gem_2x2.mp3'])
        load_named('crystal_crash', ['crystal_crash.mp3'])

        # Optional inbound warning SFX.
        # Played on the receiving side when inbound becomes pending (0 -> >0).
        load_named(
            'warn_strike',
            [
                'strike_alert.mp3',
                'strike_alert.wav',
                'strike_alert.ogg',
                'warn_strike.mp3',
                'warn_strike.wav',
                'warn_strike.ogg',
            ],
        )
        load_named(
            'warn_sprinkle',
            [
                'sprinkle_alert.mp3',
                'sprinkle_alert.wav',
                'sprinkle_alert.ogg',
                'warn_sprinkle.mp3',
                'warn_sprinkle.wav',
                'warn_sprinkle.ogg',
            ],
        )

        # Optional strike contact SFX (when a strike first hits blocks and begins piercing).
        load_named('strike_land', ['strike_land.mp3', 'strike_land.wav', 'strike_land.ogg'])

        for i in range(1, 13):
            load_named(
                self._gem_place1_row_sfx_keys[i],
                [f'gem_place1_s{i}.mp3', f'gem_place1_s{i}.wav', f'gem_place1_s{i}.ogg'],
            )

    def play_puzzle_sfx(self, key: str, *, stop_first: bool = True) -> None:
        if not bool(self.enabled):
            return
        s = (self._puzzle_sfx or {}).get(str(key))
        if s is None:
            return
        try:
            if stop_first:
                try:
                    s.stop()
                except Exception:
                    pass
            s.play()
        except Exception:
            pass

    def _compute_piece_avg_row_index(self, piece: Any, board: Any, max_rows: int = 12) -> int | None:
        if piece is None or board is None:
            return None
        try:
            h = int(getattr(board, 'HEIGHT', max_rows) or max_rows)
        except Exception:
            h = int(max_rows)
        h = max(1, int(h))
        rows: list[float] = []
        try:
            positions = piece.get_block_positions()
        except Exception:
            positions = []
        for _x, y, _b in positions:
            try:
                yi = int(y)
            except Exception:
                continue
            if 0 <= yi < h:
                rows.append(float(yi + 1))
        if not rows:
            return None
        avg_row = sum(rows) / float(len(rows))
        raw_idx = int(avg_row)
        raw_idx = max(1, min(int(max_rows), raw_idx))
        return int(raw_idx)

    def play_gem_place1_row_sfx_for_piece(self, piece: Any, board: Any) -> None:
        idx = self._compute_piece_avg_row_index(piece, board, max_rows=12)
        if idx is None:
            self.play_puzzle_sfx('gem_place1')
            return
        key = self._gem_place1_row_sfx_keys.get(int(idx))
        if key:
            self.play_puzzle_sfx(key)
        else:
            self.play_puzzle_sfx('gem_place1')

    def _count_2x2_clusters(self, board: Any) -> int:
        if board is None:
            return 0

        def cell_color(cell: Any) -> str | None:
            try:
                from swordfighting_new.core.board import Board

                if cell is None or cell == Board.EMPTY:
                    return None
            except Exception:
                if cell is None:
                    return None
            try:
                if bool(getattr(cell, 'is_garbage', False)):
                    return None
            except Exception:
                pass
            try:
                if bool(getattr(cell, 'is_breaker', False)):
                    return None
            except Exception:
                pass
            c = getattr(cell, 'color', None)
            if c is None:
                return None
            if isinstance(c, str):
                return c.strip().lower() or None
            try:
                if isinstance(c, (list, tuple)) and c and isinstance(c[0], str):
                    return str(c[0]).strip().lower() or None
            except Exception:
                pass
            try:
                return str(c).strip().lower() or None
            except Exception:
                return None

        w = max(1, int(getattr(board, 'WIDTH', 6) or 6))
        h = max(1, int(getattr(board, 'HEIGHT', 12) or 12))

        total = 0
        for x in range(0, max(0, w - 1)):
            for y in range(0, max(0, h - 1)):
                try:
                    a = cell_color(board.get_piece(x, y))
                    if not a:
                        continue
                    if a == cell_color(board.get_piece(x + 1, y)) and a == cell_color(board.get_piece(x, y + 1)) and a == cell_color(board.get_piece(x + 1, y + 1)):
                        total += 1
                except Exception:
                    continue
        return int(total)

    def _is_board_stable(self, board: Any) -> bool:
        if board is None:
            return True
        try:
            h = int(getattr(board, 'HEIGHT', 12) or 12)
            w = int(getattr(board, 'WIDTH', 6) or 6)
        except Exception:
            h, w = 12, 6
        h = max(1, h)
        w = max(1, w)
        try:
            empty = getattr(board, 'EMPTY')
        except Exception:
            empty = None
        for x in range(w):
            for y in range(h - 2, -1, -1):
                try:
                    cell = board.get_piece(x, y)
                    if empty is not None:
                        if cell == empty:
                            continue
                    else:
                        if cell is None:
                            continue
                    below = board.get_piece(x, y + 1)
                    if empty is not None:
                        if below == empty:
                            return False
                    else:
                        if below is None:
                            return False
                except Exception:
                    continue
        return True

    def tick_puzzle_sfx(self, snap: dict, *, pre_player_piece: Any, session_frame: int, session: Any) -> None:
        if not bool(self.enabled):
            return

        # Break SFX: play once per *normal* block cleared.
        # Prefer per-cascade-wave clears for better sync; fall back to cumulative totals.
        try:
            pending = int(getattr(self, '_sfx_pending_break_pops', 0) or 0)
            runner = getattr(getattr(session, 'player', None), 'chain_runner', None)

            # First choice: breaker manager exposes per-wave normal clears.
            added = 0
            bm = getattr(runner, 'breakers', None)
            seq = getattr(bm, 'last_wave_seq', None) if bm is not None else None
            if seq is not None:
                last_seq = getattr(self, '_sfx_last_break_seq', None)
                # If we've never seen a wave seq before, treat it as "one behind"
                # so the first observed wave still contributes pops.
                if last_seq is None:
                    last_seq = int(seq) - 1
                if int(seq) != int(last_seq):
                    try:
                        added = int(getattr(bm, 'last_wave_normal_cleared', 0) or 0)
                    except Exception:
                        added = 0
                    self._sfx_last_break_seq = int(seq)

            # Fallback: diff cumulative totals (may lump, but still correct count).
            if added <= 0:
                total_now = int(getattr(runner, 'total_normal_cleared', getattr(runner, 'total_cleared', 0)) or 0)
                total_prev = int(getattr(self, '_sfx_last_normal_cleared', 0) or 0)
                if total_now > total_prev:
                    added = int(total_now - total_prev)
                self._sfx_last_normal_cleared = int(total_now)

            if added > 0:
                pending += int(added)

            # Drain some pops per frame (fast, but not an instant audio wall).
            try:
                max_per = int(os.getenv('BF_BREAK_SFX_MAX_PER_FRAME', '1') or 1)
            except Exception:
                max_per = 1
            max_per = max(1, min(64, int(max_per)))

            to_play = min(int(pending), int(max_per))
            for _ in range(int(to_play)):
                # IMPORTANT: allow overlap; stop_first=False.
                self.play_puzzle_sfx('crystal_crash', stop_first=False)
            pending = int(pending - to_play)

            self._sfx_pending_break_pops = int(pending)
        except Exception:
            pass

        try:
            ps = (snap or {}).get('player', {}) or {}

            # Inbound warning SFX: play once when pending transitions 0 -> >0.
            try:
                accepts_input = True
                try:
                    accepts_input = bool(getattr(session, 'accepts_player_input', True))
                except Exception:
                    accepts_input = True

                sides_to_warn = ['player'] if accepts_input else ['player', 'ai']
                last_by_side = getattr(self, '_sfx_last_pending_by_side', None)
                if not isinstance(last_by_side, dict):
                    last_by_side = {
                        'player': {'strike': 0, 'sprinkle': 0},
                        'ai': {'strike': 0, 'sprinkle': 0},
                    }
                    self._sfx_last_pending_by_side = last_by_side

                for side_key in sides_to_warn:
                    side_snap = (snap or {}).get(side_key, {}) or {}
                    pending_strike = int(side_snap.get('pending_strike', 0) or 0)
                    pending_sprinkle = int(side_snap.get('pending_sprinkle', 0) or 0)
                    strike_land_seq = int(side_snap.get('strike_land_seq', 0) or 0)

                    last = last_by_side.get(side_key)
                    if not isinstance(last, dict):
                        last = {'strike': 0, 'sprinkle': 0}
                        last_by_side[side_key] = last

                    if pending_strike > 0 and int(last.get('strike', 0) or 0) <= 0:
                        self.play_puzzle_sfx('warn_strike', stop_first=False)
                    if pending_sprinkle > 0 and int(last.get('sprinkle', 0) or 0) <= 0:
                        self.play_puzzle_sfx('warn_sprinkle', stop_first=False)

                    last['strike'] = int(pending_strike)
                    last['sprinkle'] = int(pending_sprinkle)

                    # Strike-land SFX: play once when the sequence advances.
                    try:
                        last_seq_map = getattr(self, '_sfx_last_strike_land_seq_by_side', None)
                        if not isinstance(last_seq_map, dict):
                            last_seq_map = {'player': 0, 'ai': 0}
                            self._sfx_last_strike_land_seq_by_side = last_seq_map
                        last_seq = int(last_seq_map.get(side_key, 0) or 0)
                        if int(strike_land_seq) > int(last_seq):
                            self.play_puzzle_sfx('strike_land', stop_first=False)
                        last_seq_map[side_key] = int(strike_land_seq)
                    except Exception:
                        pass
            except Exception:
                pass

            chain_now = bool(ps.get('chain_active', False))
            chain_prev = self._sfx_last_chain_active
            if chain_prev is None:
                chain_prev = False
            self._sfx_last_chain_active = bool(chain_now)

            piece_now = ps.get('piece', None)
            piece_present_now = (piece_now is not None)
            piece_present_prev = self._sfx_last_piece_present
            if piece_present_prev is None:
                piece_present_prev = piece_present_now
            self._sfx_last_piece_present = bool(piece_present_now)

            board = ps.get('board', None)
            stable_now = bool(self._is_board_stable(board))

            lock_by_chain = (chain_prev is False and chain_now is True)
            lock_by_piece = (piece_present_prev is True and piece_present_now is False)
            locked_now = bool(lock_by_chain or lock_by_piece)

            if locked_now:
                try:
                    self.play_gem_place1_row_sfx_for_piece(pre_player_piece, board)
                except Exception:
                    self.play_puzzle_sfx('gem_place1')

                self._sfx_place2_armed = True
                self._sfx_place2_saw_unstable = (not stable_now)
                try:
                    self._sfx_place2_deadline_frame = int(session_frame) + int(self._place2_window_frames)
                except Exception:
                    self._sfx_place2_deadline_frame = None

                try:
                    now_cnt = self._count_2x2_clusters(board)
                    if int(now_cnt) > int(getattr(self, '_sfx_last_cluster_count', 0) or 0):
                        self.play_puzzle_sfx('gem_2x2')
                    self._sfx_last_cluster_count = int(now_cnt)
                except Exception:
                    pass
            else:
                try:
                    self._sfx_last_cluster_count = int(self._count_2x2_clusters(board))
                except Exception:
                    pass

            if bool(getattr(self, '_sfx_place2_armed', False)):
                if not stable_now:
                    self._sfx_place2_saw_unstable = True
                if bool(getattr(self, '_sfx_place2_saw_unstable', False)) and stable_now:
                    self.play_puzzle_sfx('gem_place2')
                    self._sfx_place2_armed = False
                    self._sfx_place2_saw_unstable = False
                    self._sfx_place2_deadline_frame = None
                else:
                    try:
                        dl = getattr(self, '_sfx_place2_deadline_frame', None)
                        if dl is not None and int(session_frame) > int(dl):
                            self._sfx_place2_armed = False
                            self._sfx_place2_saw_unstable = False
                            self._sfx_place2_deadline_frame = None
                    except Exception:
                        pass
        except Exception:
            pass
