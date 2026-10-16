from __future__ import annotations


class UILabelsRenderController:
    def draw_ui_labels(self, client, snap: dict, *, cell_h: int) -> None:
        y0 = int(getattr(client, '_content_offset_y', 0) or 0)
        try:
            headroom_px = int(getattr(client, '_spawn_headroom_rows', 0) or 0) * int(cell_h)
        except Exception:
            headroom_px = 0

        # Draw labels above each board.
        label_y = max(2, int(y0 - headroom_px + 2))
        board_w = int(getattr(client, 'board_px_w', 0) or 0)

        def _blit_centered(text: str, color: tuple[int, int, int], ox: int) -> None:
            if not text:
                return
            try:
                surf = client.ui_font.render(str(text), True, color)
            except Exception:
                return
            try:
                tw = int(surf.get_width())
            except Exception:
                tw = 0
            x = int(ox + (board_w // 2) - (tw // 2))
            try:
                x = max(int(ox + 2), min(int(ox + max(0, board_w - tw - 2)), int(x)))
            except Exception:
                pass
            client.screen.blit(surf, (int(x), int(label_y)))

        try:
            p_name = str((snap.get('player', {}) or {}).get('fighter_name', 'Player') or 'Player')
        except Exception:
            p_name = 'Player'
        try:
            if bool((snap.get('player', {}) or {}).get('defeated', False)):
                p_name = f"{p_name} (KO)"
        except Exception:
            pass
        _blit_centered(p_name, (220, 220, 220), int(getattr(client, 'player_offset_x', 0) or 0))

        if snap.get('ai') is not None:
            enemy_style = ''
            try:
                enemy_style = str(getattr(client.session, 'enemy_style', '') or '').strip().lower()
            except Exception:
                enemy_style = ''

            # Prefer showing the resolved rubix level (from the AI instance) so
            # "rubix3" always reflects the actual tier.
            if enemy_style.startswith('rubix'):
                try:
                    lv = int(getattr(getattr(client.session, 'ai', None), '_rubix_level', 0) or 0)
                    if lv > 0:
                        enemy_style = f"rubix{lv}"
                except Exception:
                    pass

            try:
                e_name = str((snap.get('ai', {}) or {}).get('fighter_name', 'Enemy') or 'Enemy')
            except Exception:
                e_name = 'Enemy'
            suffix = f" ({enemy_style})" if enemy_style and enemy_style not in ('passive',) else ''
            enemy_title = e_name + suffix + (" (KO)" if bool((snap.get('ai', {}) or {}).get('defeated', False)) else "")
            _blit_centered(enemy_title, (220, 180, 180), int(getattr(client, 'enemy_offset_x', 0) or 0))
