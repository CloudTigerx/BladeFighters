from __future__ import annotations


class EnemyHPPanelRenderController:
    def __init__(self, *, pygame):
        self._pygame = pygame

    def draw_enemy_hp_panel(self, client, snap: dict, *, margin: int) -> None:
        hp = snap.get('hp') or None
        if not isinstance(hp, dict):
            return
        try:
            enemy_hp = int(hp.get('enemy', 0) or 0)
            enemy_hp_max = max(1, int(hp.get('enemy_max', 1) or 1))
        except Exception:
            return

        try:
            style = str(snap.get('enemy_style', '') or '').strip().lower()
        except Exception:
            style = ''

        ratio = float(enemy_hp) / float(max(1, enemy_hp_max))
        ratio = max(0.0, min(1.0, ratio))

        y0 = int(getattr(client, '_content_offset_y', 0) or 0)
        panel_w = int(getattr(client, 'enemy_panel_px_w', 0) or 0)
        if panel_w <= 0:
            panel_w = int(client.board_px_w)

        margin = int(margin)
        x = int(client.enemy_offset_x + margin + 8)
        y = int(y0 + margin + 52)
        w = int(panel_w - (margin * 2) - 16)
        h = max(14, int(round(22 * float(getattr(client, 'ui_scale', 1.0) or 1.0))))

        # Background panel area (where the enemy board would be)
        try:
            panel = self._pygame.Rect(int(client.enemy_offset_x), int(y0), int(panel_w), int(client.board_px_h))
            self._pygame.draw.rect(client.screen, (24, 24, 36), panel, border_radius=10)
            self._pygame.draw.rect(client.screen, (70, 70, 95), panel, width=2, border_radius=10)
        except Exception:
            pass

        # Bar
        try:
            bg = self._pygame.Rect(x, y, w, h)
            self._pygame.draw.rect(client.screen, (45, 45, 65), bg, border_radius=8)
            fill_w = int(round(w * ratio))
            fill = self._pygame.Rect(x, y, max(0, fill_w), h)
            col = (220, 80, 80) if style != 'mirror' else (160, 160, 210)
            self._pygame.draw.rect(client.screen, col, fill, border_radius=8)
            self._pygame.draw.rect(client.screen, (230, 230, 245), bg, width=2, border_radius=8)
        except Exception:
            pass

        # Label
        try:
            label = f"HP {enemy_hp}/{enemy_hp_max}"
            if style == 'mirror':
                label = 'HP (INVINCIBLE)'
            txt = client.ui_font.render(label, True, (235, 235, 245))
            client.screen.blit(txt, (x, y + h + 8))
        except Exception:
            pass
