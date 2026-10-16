from __future__ import annotations

import os


class PuzzleSFXController:
    def __init__(self, *, pygame, assets_dir_fn):
        self._pygame = pygame
        self._assets_dir_fn = assets_dir_fn

    def init_puzzle_sfx(self, client) -> None:
        pygame = self._pygame

        if not getattr(client, '_sfx_enabled', True):
            return

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except Exception:
            client._sfx_enabled = False
            return

        try:
            pygame.mixer.set_num_channels(32)
        except Exception:
            pass

        try:
            base_dir = os.path.join(os.fspath(self._assets_dir_fn()), 'sounds')
        except Exception:
            base_dir = None

        def load_named(key: str, candidates: list[str]) -> None:
            if key in client._puzzle_sfx:
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
                s = pygame.mixer.Sound(chosen)
                try:
                    s.set_volume(float(client._sfx_volume))
                except Exception:
                    pass
                client._puzzle_sfx[key] = s
            except Exception:
                return

        load_named('gem_place1', ['gem_place1.mp3'])
        load_named('gem_place2', ['gem_place2.mp3', 'gem_place3.mp3'])
        load_named('gem_2x2', ['gem_2x2.mp3'])
        load_named('crystal_crash', ['crystal_crash.mp3'])

        for i in range(1, 13):
            load_named(
                client._gem_place1_row_sfx_keys[i],
                [f'gem_place1_s{i}.mp3', f'gem_place1_s{i}.wav', f'gem_place1_s{i}.ogg'],
            )

    def play_puzzle_sfx(self, client, key: str, *, stop_first: bool = True) -> None:
        if not getattr(client, '_sfx_enabled', True):
            return
        s = (getattr(client, '_puzzle_sfx', None) or {}).get(key)
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

    def compute_piece_avg_row_index(self, _client, piece, board, max_rows: int = 12):
        if piece is None or board is None:
            return None
        try:
            h = int(getattr(board, 'HEIGHT', max_rows) or max_rows)
        except Exception:
            h = int(max_rows)
        h = max(1, int(h))
        rows = []
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

    def play_gem_place1_row_sfx_for_piece(self, client, piece, board) -> None:
        idx = self.compute_piece_avg_row_index(client, piece, board, max_rows=12)
        if idx is None:
            self.play_puzzle_sfx(client, 'gem_place1')
            return
        key = client._gem_place1_row_sfx_keys.get(int(idx))
        if key:
            self.play_puzzle_sfx(client, key)
        else:
            self.play_puzzle_sfx(client, 'gem_place1')

    def count_2x2_clusters(self, _client, board) -> int:
        if board is None:
            return 0

        def cell_color(cell):
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

    def is_board_stable(self, _client, board) -> bool:
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

    def tick_puzzle_sfx(self, client, snap: dict, *, pre_player_piece, session_frame: int) -> None:
        if not getattr(client, '_sfx_enabled', True):
            return

        try:
            pending = int(getattr(client, '_sfx_pending_break_pops', 0) or 0)
            runner = getattr(getattr(client.session, 'player', None), 'chain_runner', None)

            added = 0
            bm = getattr(runner, 'breakers', None)
            seq = getattr(bm, 'last_wave_seq', None) if bm is not None else None
            if seq is not None:
                last_seq = getattr(client, '_sfx_last_break_seq', None)
                if last_seq is None:
                    last_seq = int(seq) - 1
                if int(seq) != int(last_seq):
                    try:
                        added = int(getattr(bm, 'last_wave_normal_cleared', 0) or 0)
                    except Exception:
                        added = 0
                    client._sfx_last_break_seq = int(seq)

            if added <= 0:
                total_now = int(getattr(runner, 'total_normal_cleared', getattr(runner, 'total_cleared', 0)) or 0)
                total_prev = int(getattr(client, '_sfx_last_normal_cleared', 0) or 0)
                if total_now > total_prev:
                    added = int(total_now - total_prev)
                client._sfx_last_normal_cleared = int(total_now)

            if added > 0:
                pending += int(added)

            try:
                max_per = int(os.getenv('BF_BREAK_SFX_MAX_PER_FRAME', '1') or 1)
            except Exception:
                max_per = 1
            max_per = max(1, min(64, int(max_per)))

            to_play = min(int(pending), int(max_per))
            for _ in range(int(to_play)):
                self.play_puzzle_sfx(client, 'crystal_crash', stop_first=False)
            pending = int(pending - to_play)

            client._sfx_pending_break_pops = int(pending)
        except Exception:
            pass

        try:
            ps = (snap or {}).get('player', {}) or {}
            chain_now = bool(ps.get('chain_active', False))
            chain_prev = client._sfx_last_chain_active
            if chain_prev is None:
                chain_prev = False
            client._sfx_last_chain_active = bool(chain_now)

            piece_now = ps.get('piece', None)
            piece_present_now = (piece_now is not None)
            piece_present_prev = client._sfx_last_piece_present
            if piece_present_prev is None:
                piece_present_prev = piece_present_now
            client._sfx_last_piece_present = bool(piece_present_now)

            board = ps.get('board', None)
            stable_now = bool(self.is_board_stable(client, board))

            lock_by_chain = (chain_prev is False and chain_now is True)
            lock_by_piece = (piece_present_prev is True and piece_present_now is False)
            locked_now = bool(lock_by_chain or lock_by_piece)

            if locked_now:
                try:
                    self.play_gem_place1_row_sfx_for_piece(client, pre_player_piece, board)
                except Exception:
                    self.play_puzzle_sfx(client, 'gem_place1')

                client._sfx_place2_armed = True
                client._sfx_place2_saw_unstable = (not stable_now)
                try:
                    client._sfx_place2_deadline_frame = int(session_frame) + int(client._sfx_place2_window_frames)
                except Exception:
                    client._sfx_place2_deadline_frame = None

                try:
                    now_cnt = self.count_2x2_clusters(client, board)
                    if int(now_cnt) > int(getattr(client, '_sfx_last_cluster_count', 0) or 0):
                        self.play_puzzle_sfx(client, 'gem_2x2')
                    client._sfx_last_cluster_count = int(now_cnt)
                except Exception:
                    pass
            else:
                try:
                    client._sfx_last_cluster_count = int(self.count_2x2_clusters(client, board))
                except Exception:
                    pass

            if bool(getattr(client, '_sfx_place2_armed', False)):
                if not stable_now:
                    client._sfx_place2_saw_unstable = True
                if bool(getattr(client, '_sfx_place2_saw_unstable', False)) and stable_now:
                    self.play_puzzle_sfx(client, 'gem_place2')
                    client._sfx_place2_armed = False
                    client._sfx_place2_saw_unstable = False
                    client._sfx_place2_deadline_frame = None
                else:
                    try:
                        dl = getattr(client, '_sfx_place2_deadline_frame', None)
                        if dl is not None and int(session_frame) > int(dl):
                            client._sfx_place2_armed = False
                            client._sfx_place2_saw_unstable = False
                            client._sfx_place2_deadline_frame = None
                    except Exception:
                        pass
        except Exception:
            pass
