from __future__ import annotations

import os


class ExplosionFXController:
    def __init__(self, *, pygame):
        self._pygame = pygame

    def init_explosion_fx_state(self, client) -> None:
        # --- Explosion sprite FX (per-color) ---------------------------
        # Break (clear) explosion sprites from assets/sprites.
        # Set BF_EXPLODE_SPRITES=0 to disable if you want a cleaner look.
        try:
            client._explode_enabled = str(os.getenv('BF_EXPLODE_SPRITES', '1') or '1').strip().lower() not in (
                '0',
                'false',
                'no',
                'off',
            )
        except Exception:
            client._explode_enabled = True
        try:
            client._explode_strip_frames = max(1, int(os.getenv('BF_PG_EXPLODE_STRIP_FRAMES', '9') or '9'))
        except Exception:
            client._explode_strip_frames = 9
        try:
            client._explode_frame_ms = max(10, int(os.getenv('BF_EXPLODE_FRAME_MS', '30') or '30'))
        except Exception:
            client._explode_frame_ms = 30
        try:
            client._explode_frames_by_color = {}
        except Exception:
            pass
        try:
            client._active_explosions = []
        except Exception:
            pass

    def load_explosion_sprites(self, client, *, cell_w: int, cell_h: int) -> None:
        try:
            client._assets.load_explosion_sprites(client, cell_w=int(cell_w), cell_h=int(cell_h))
        except Exception:
            pass

    def spawn_explosions_for_delta(
        self,
        client,
        *,
        board_id: int,
        last_snap: dict | None,
        curr_snap: dict,
        offset_x: int,
        offset_y: int,
    ) -> None:
        if not getattr(client, '_explode_enabled', True):
            return
        if not last_snap:
            return

        try:
            prev_blocks = (last_snap.get('blocks', {}) or {})
            curr_blocks = (curr_snap.get('blocks', {}) or {})
            prev_by_id = (last_snap.get('id_map', {}) or {})
        except Exception:
            return

        removed_ids = set(prev_blocks.keys()) - set(curr_blocks.keys())
        if not removed_ids:
            return

        now_ms = int(getattr(client, '_now_ms', 0) or 0)

        try:
            ex_list = getattr(client, '_active_explosions', None)
            if not isinstance(ex_list, list):
                client._active_explosions = []
        except Exception:
            try:
                client._active_explosions = []
            except Exception:
                return

        for bid in removed_ids:
            try:
                cell = prev_blocks.get(bid)
                if cell is None:
                    continue
                # Only animate colored normal/breaker blocks (skip garbage/special).
                if bool(getattr(cell, 'is_garbage', False)):
                    continue
                try:
                    color = str(getattr(cell, 'color', '') or '').strip().lower()
                except Exception:
                    color = ''
                if not color:
                    continue
                frames = (getattr(client, '_explode_frames_by_color', None) or {}).get(color)
                if not frames:
                    continue
                pos = prev_by_id.get(bid)
                if pos is None:
                    continue
                x, y = int(pos[0]), int(pos[1])
                if x < 0 or y < 0:
                    continue
                rect = client._make_cell_rect(x, y, offset_x, offset_y).inflate(-2, -2)
                client._active_explosions.append(
                    {
                        'board_id': int(board_id),
                        'rect': rect,
                        'frames': frames,
                        'start_ms': int(now_ms),
                        'frame_ms': int(getattr(client, '_explode_frame_ms', 30) or 30),
                    }
                )
            except Exception:
                continue

        # Keep bounded.
        try:
            if len(client._active_explosions) > 400:
                client._active_explosions = client._active_explosions[-250:]
        except Exception:
            pass

    def draw_active_explosions(self, client, *, board_id: int) -> None:
        if not getattr(client, '_explode_enabled', True):
            return
        ex = getattr(client, '_active_explosions', None)
        if not ex:
            return
        now_ms = int(getattr(client, '_now_ms', 0) or 0)

        keep = []
        for e in ex:
            try:
                if int(e.get('board_id', -1)) != int(board_id):
                    keep.append(e)
                    continue
                frames = e.get('frames') or []
                if not frames:
                    continue
                start = int(e.get('start_ms', 0) or 0)
                frame_ms = max(1, int(e.get('frame_ms', 30) or 30))
                idx = int((now_ms - start) // frame_ms)
                if idx < 0:
                    idx = 0
                if idx >= len(frames):
                    continue
                rect = e.get('rect')
                if rect is None:
                    continue
                client.screen.blit(frames[idx], (int(rect.x), int(rect.y)))
                keep.append(e)
            except Exception:
                continue

        client._active_explosions = keep
