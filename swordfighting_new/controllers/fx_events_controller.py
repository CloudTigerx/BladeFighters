from __future__ import annotations


class FXEventsController:
    def __init__(self, *, pygame):
        self._pygame = pygame

    def ingest_fx_events(self, client, snap: dict) -> None:
        pygame = self._pygame

        if not bool(getattr(client, '_fx_enabled', False)):
            # FX disabled: drop any queued events and clear active list.
            client._active_fx = []
            return

        now = int(getattr(client, '_now_ms', 0) or 0)
        if now <= 0:
            try:
                now = int(pygame.time.get_ticks())
            except Exception:
                now = 0

        # Prune expired.
        client._active_fx = [
            e
            for e in (getattr(client, '_active_fx', []) or [])
            if int(e.get('expires_ms', 0) or 0) > now
        ]

        events = (snap or {}).get('fx_events', []) or []
        if not events:
            return

        for ev in events:
            if not isinstance(ev, dict):
                continue
            et = str(ev.get('type', '') or '').strip().lower()
            if et != 'spark':
                continue

            try:
                duration_ms = int(ev.get('duration_ms', 220) or 220)
            except Exception:
                duration_ms = 220
            duration_ms = max(60, min(2000, int(duration_ms)))

            color = ev.get('color', (255, 240, 180))
            try:
                cr, cg, cb = int(color[0]), int(color[1]), int(color[2])
                rgb = (max(0, min(255, cr)), max(0, min(255, cg)), max(0, min(255, cb)))
            except Exception:
                rgb = (255, 240, 180)

            cells = ev.get('cells', []) or []
            for cell in cells:
                try:
                    side = None
                    x = y = None
                    if isinstance(cell, dict):
                        side = str(cell.get('side', '') or '').strip().lower() or None
                        x = int(cell.get('x', -1))
                        y = int(cell.get('y', -1))
                    elif isinstance(cell, (list, tuple)) and len(cell) >= 2:
                        x = int(cell[0])
                        y = int(cell[1])
                    if x is None or y is None:
                        continue
                    if x < 0 or y < 0:
                        continue
                    client._active_fx.append({
                        'side': side,
                        'x': int(x),
                        'y': int(y),
                        'rgb': rgb,
                        'expires_ms': int(now + duration_ms),
                    })
                except Exception:
                    continue

        # Keep bounded.
        try:
            if len(client._active_fx) > 800:
                client._active_fx = client._active_fx[-500:]
        except Exception:
            pass

    def draw_active_fx(self, client, snap: dict) -> None:
        pygame = self._pygame

        if not bool(getattr(client, '_fx_enabled', False)):
            return
        ex = getattr(client, '_active_fx', None)
        if not ex:
            return

        keep = []
        for e in ex:
            try:
                side = str(e.get('side', '') or '').strip().lower()
                x = int(e.get('x', -1))
                y = int(e.get('y', -1))
                if x < 0 or y < 0:
                    continue

                offset_x = int(client.player_offset_x)
                offset_y = int(getattr(client, '_content_offset_y', 0) or 0)
                if side in ('ai', 'enemy', 'right'):
                    offset_x = int(client.enemy_offset_x)
                rect = client._make_cell_rect(x, y, offset_x, offset_y).inflate(-6, -6)

                rgb = e.get('rgb', (255, 240, 180))
                try:
                    pygame.draw.rect(client.screen, rgb, rect, width=2, border_radius=6)
                except Exception:
                    pass
                keep.append(e)
            except Exception:
                continue
        client._active_fx = keep
