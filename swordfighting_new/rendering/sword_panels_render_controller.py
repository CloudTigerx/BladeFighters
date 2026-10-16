from __future__ import annotations

from typing import Any

from swordfighting_new.attacks.garbage_pattern import SWORD_PATTERNS, SwordType


class SwordPanelsRenderController:
    def __init__(self, *, pygame: Any):
        self._pygame = pygame

    def draw_quickplay_sword_panels(
        self,
        client: Any,
        *,
        mouse_pos: tuple[int, int],
        color_map: dict[str, tuple[int, int, int]],
    ) -> None:
        """Draw Quickplay (enemy_select) left/right sword selection panels."""
        try:
            left_panel, right_panel, _mid = client._get_quickplay_sword_panel_rects()
        except Exception:
            return

        def _draw_panel(rect: Any) -> None:
            try:
                surf = self._pygame.Surface((int(rect.w), int(rect.h)), flags=self._pygame.SRCALPHA)
                surf.fill((40, 40, 60, 150))
                client.screen.blit(surf, (int(rect.x), int(rect.y)))
                self._pygame.draw.rect(client.screen, (255, 255, 255), rect, width=2, border_radius=12)
            except Exception:
                pass

        _draw_panel(left_panel)
        _draw_panel(right_panel)

        try:
            sel_a = str(getattr(client, '_equipped_sword_value', 'rusty_sword') or 'rusty_sword').strip().lower()
        except Exception:
            sel_a = 'rusty_sword'
        try:
            sel_b = str(getattr(client, '_enemy_sword_value', 'rusty_sword') or 'rusty_sword').strip().lower()
        except Exception:
            sel_b = 'rusty_sword'

        lay_a = client._quickplay_sword_layout('left')
        lay_b = client._quickplay_sword_layout('right')
        hdr_a = lay_a.get('header_rect')
        hdr_b = lay_b.get('header_rect')

        try:
            ui = getattr(client, '_ui', None)
            ui_scale = float(getattr(ui, 'scale', getattr(client, 'ui_scale', 1.0) or 1.0) or 1.0)
        except Exception:
            ui_scale = 1.0

        def _draw_header(rect: Any, label: str) -> None:
            if rect is None:
                return
            try:
                surf = self._pygame.Surface((int(rect.w), int(rect.h)), flags=self._pygame.SRCALPHA)
                surf.fill((0, 0, 0, 140))
                client.screen.blit(surf, (int(rect.x), int(rect.y)))
                self._pygame.draw.rect(client.screen, (255, 255, 255), rect, width=2, border_radius=10)
                if str(label or '').strip():
                    client._blit_fitted_text(
                        label,
                        rect,
                        color=(245, 245, 245),
                        pad=6,
                        base_px=int(max(14, round(20 * ui_scale))),
                        max_lines=1,
                    )
            except Exception:
                pass

        # No header text for Quickplay panels (requested).
        _draw_header(hdr_a, '')
        _draw_header(hdr_b, '')

        hovered_tile = None

        def _draw_tiles(selected_value: str, layout: dict) -> None:
            nonlocal hovered_tile
            try:
                sword_rect = layout.get('swords_rect')
                tiles = list(layout.get('tiles') or [])
            except Exception:
                sword_rect = None
                tiles = []
            if sword_rect is None:
                return

            try:
                client.screen.set_clip(sword_rect)
            except Exception:
                pass

            for t in tiles:
                rect = t.get('rect')
                if rect is None:
                    continue
                try:
                    if not sword_rect.colliderect(rect):
                        continue
                except Exception:
                    pass

                try:
                    hovered = bool(rect.collidepoint(mouse_pos))
                except Exception:
                    hovered = False
                value = str(t.get('value', '') or '').strip().lower()
                is_selected = (value == str(selected_value or '').strip().lower())

                if hovered and sword_rect.collidepoint(mouse_pos):
                    hovered_tile = t

                try:
                    if is_selected:
                        self._pygame.draw.rect(client.screen, (240, 240, 200), rect, width=3, border_radius=10)
                    elif hovered:
                        self._pygame.draw.rect(client.screen, (220, 220, 220), rect, width=2, border_radius=10)
                    else:
                        self._pygame.draw.rect(client.screen, (120, 120, 150), rect, width=1, border_radius=10)
                except Exception:
                    pass

                try:
                    name_h = int(max(16, min(30, round(rect.h * 0.26))))
                except Exception:
                    name_h = 22
                name_rect = self._pygame.Rect(int(rect.x + 4), int(rect.y + 4), int(max(1, rect.w - 8)), int(max(1, name_h)))
                img_rect = self._pygame.Rect(
                    int(rect.x + 6),
                    int(name_rect.bottom + 2),
                    int(max(1, rect.w - 12)),
                    int(max(1, rect.bottom - (name_rect.bottom + 6))),
                )

                try:
                    client._blit_fitted_text(
                        str(t.get('name', '') or value),
                        name_rect,
                        color=(245, 245, 245),
                        pad=2,
                        base_px=int(max(12, round(16 * ui_scale))),
                        max_lines=1,
                    )
                except Exception:
                    pass

                try:
                    st = t.get('sword_type')
                    art = client._get_weapon_art_scaled_preview(st, max_w=int(img_rect.w), max_h=int(img_rect.h))
                except Exception:
                    art = None
                if art is not None:
                    try:
                        ax = int(img_rect.centerx - int(art.get_width()) / 2)
                        ay = int(img_rect.centery - int(art.get_height()) / 2)
                        client.screen.blit(art, (ax, ay))
                    except Exception:
                        pass

            try:
                client.screen.set_clip(None)
            except Exception:
                pass

        _draw_tiles(sel_a, lay_a)
        _draw_tiles(sel_b, lay_b)

        if hovered_tile is not None:
            try:
                rr = hovered_tile.get('rect')
                st = hovered_tile.get('sword_type')
                if rr is not None and st is not None:
                    self.draw_bot_battle_hover_pattern(client, sword_type=st, anchor_rect=rr, color_map=color_map)
            except Exception:
                pass

    def draw_bot_battle_hover_pattern(
        self,
        client: Any,
        *,
        sword_type: SwordType,
        anchor_rect: Any,
        color_map: dict[str, tuple[int, int, int]] | None,
    ) -> None:
        """Draw a small pattern preview panel near the hovered sword tile."""
        patt = None
        try:
            patt = SWORD_PATTERNS.get(sword_type)
        except Exception:
            patt = None
        if patt is None:
            return

        try:
            ui_scale = float(getattr(client, 'ui_scale', 1.0) or 1.0)
        except Exception:
            ui_scale = 1.0

        try:
            w, h = int(client.screen.get_width()), int(client.screen.get_height())
        except Exception:
            w, h = 1920, 1080

        pad = int(max(8, round(10 * ui_scale)))
        rows = 12

        note_text = ''
        note_h = 0
        try:
            if sword_type == SwordType.FISTS:
                note_text = 'randomizes per game'
        except Exception:
            note_text = ''
        if note_text:
            try:
                note_h = int(max(14, round(18 * ui_scale)))
            except Exception:
                note_h = 16

        # Larger preview: size is primarily driven by UI scale, not tile size.
        # Keep a safety shrink loop so it always fits on screen.
        try:
            desired_cell = int(round(22 * ui_scale))
        except Exception:
            desired_cell = 18
        cell = int(max(10, min(28, desired_cell)))

        def _dims_for(cell_px: int) -> tuple[int, int, int, int, int]:
            grid_w0 = int(cell_px * 6)
            grid_h0 = int(cell_px * rows)
            title_h0 = int(max(20, round(26 * ui_scale))) + int(note_h)
            box_w0 = int(grid_w0 + pad * 2)
            box_h0 = int(grid_h0 + pad * 2 + title_h0)
            return (grid_w0, grid_h0, title_h0, box_w0, box_h0)

        grid_w, grid_h, title_h, box_w, box_h = _dims_for(cell)
        try:
            max_w = int(max(120, w - 12))
            max_h = int(max(120, h - 12))
        except Exception:
            max_w, max_h = 1200, 800
        while cell > 6 and (box_w > max_w or box_h > max_h):
            cell -= 1
            grid_w, grid_h, title_h, box_w, box_h = _dims_for(cell)

        # Prefer to the right; if clipped, fall back to the left.
        x = int(anchor_rect.right + int(max(8, round(10 * ui_scale))))
        y = int(anchor_rect.y)
        if x + box_w > w - 6:
            x = int(anchor_rect.left - box_w - int(max(8, round(10 * ui_scale))))
        x = int(max(6, min(int(w - box_w - 6), int(x))))
        y = int(max(6, min(int(h - box_h - 6), int(y))))
        rect = self._pygame.Rect(int(x), int(y), int(box_w), int(box_h))

        # Panel
        try:
            surf = self._pygame.Surface((int(rect.w), int(rect.h)), flags=self._pygame.SRCALPHA)
            surf.fill((0, 0, 0, 185))
            client.screen.blit(surf, (int(rect.x), int(rect.y)))
            self._pygame.draw.rect(client.screen, (255, 255, 255), rect, width=2, border_radius=10)
        except Exception:
            pass

        # Title
        try:
            nm = str(getattr(patt, 'name', '') or 'Pattern')
        except Exception:
            nm = 'Pattern'
        try:
            title_main_h = int(max(20, round(26 * ui_scale)))
            title_rect = self._pygame.Rect(int(rect.x + pad), int(rect.y + pad), int(rect.w - 2 * pad), int(title_main_h))
            client._blit_fitted_text(
                nm,
                title_rect,
                color=(245, 245, 245),
                pad=1,
                base_px=int(max(12, round(16 * ui_scale))),
                max_lines=1,
            )

            if note_text:
                note_rect = self._pygame.Rect(int(rect.x + pad), int(title_rect.bottom), int(rect.w - 2 * pad), int(note_h))
                client._blit_fitted_text(
                    note_text,
                    note_rect,
                    color=(210, 210, 210),
                    pad=1,
                    base_px=int(max(10, round(13 * ui_scale))),
                    max_lines=1,
                )
        except Exception:
            pass

        gx = int(rect.x + pad)
        gy = int(rect.y + pad + title_h)

        # Build effective colors using strike fold rules.
        effective: list[list[str]] = []
        for row1 in range(1, rows + 1):
            row_colors: list[str] = []
            for c in range(6):
                ck = 'yellow'
                try:
                    ck = str(
                        patt.get_strike_color(
                            x=0,
                            y=0,
                            strike_width=6,
                            strike_height=rows,
                            block_x_offset=int(c),
                            block_y_offset=int(row1 - 1),
                            is_horizontal=False,
                            from_right=False,
                        )
                    ).strip().lower()
                except Exception:
                    try:
                        raw = getattr(patt, 'pattern', None) or []
                        if raw and 0 <= (row1 - 1) < len(raw) and 0 <= c < len(raw[row1 - 1]):
                            ck = str(raw[row1 - 1][c]).strip().lower()
                    except Exception:
                        ck = 'yellow'
                row_colors.append(ck)
            effective.append(row_colors)

        if not isinstance(color_map, dict):
            color_map = {}

        for r in range(rows - 1, -1, -1):
            row = effective[r]
            for c in range(6):
                try:
                    ck = str(row[c]).strip().lower()
                except Exception:
                    ck = 'yellow'
                rgb = color_map.get(ck, (200, 200, 200))
                rr = self._pygame.Rect(int(gx + c * cell), int(gy + (rows - 1 - r) * cell), int(cell), int(cell))
                try:
                    self._pygame.draw.rect(client.screen, rgb, rr)
                    self._pygame.draw.rect(client.screen, (15, 15, 20), rr, width=1)
                except Exception:
                    pass

    def draw_bot_battle_sword_panels(
        self,
        client: Any,
        *,
        mouse_pos: tuple[int, int],
        color_map: dict[str, tuple[int, int, int]],
    ) -> None:
        """Draw the Bot Battle left/right sword selection panels."""
        try:
            left_panel, right_panel, _mid = client._get_bot_battle_sword_panel_rects()
        except Exception:
            return

        # Panel background style (dark gray, semi-transparent)
        def _draw_panel(rect: Any) -> None:
            try:
                surf = self._pygame.Surface((int(rect.w), int(rect.h)), flags=self._pygame.SRCALPHA)
                surf.fill((40, 40, 60, 150))
                client.screen.blit(surf, (int(rect.x), int(rect.y)))
                self._pygame.draw.rect(client.screen, (255, 255, 255), rect, width=2, border_radius=12)
            except Exception:
                pass

        _draw_panel(left_panel)
        _draw_panel(right_panel)

        # Bot dropdowns (above swords)
        try:
            a_style = str(getattr(client, '_bot_battle_a_style', 'rubix3') or 'rubix3').strip().lower()
        except Exception:
            a_style = 'rubix3'
        try:
            b_style = str(getattr(client, '_bot_battle_b_style', 'rubix4') or 'rubix4').strip().lower()
        except Exception:
            b_style = 'rubix4'

        lay_a = client._bot_battle_sword_layout('left')
        lay_b = client._bot_battle_sword_layout('right')
        dd_a = lay_a.get('dropdown_rect')
        dd_b = lay_b.get('dropdown_rect')

        def _draw_dropdown(rect: Any, label: str, *, open_now: bool) -> None:
            if rect is None:
                return
            try:
                surf = self._pygame.Surface((int(rect.w), int(rect.h)), flags=self._pygame.SRCALPHA)
                surf.fill((0, 0, 0, 120) if (not open_now) else (0, 0, 0, 165))
                client.screen.blit(surf, (int(rect.x), int(rect.y)))
                self._pygame.draw.rect(client.screen, (255, 255, 255), rect, width=2, border_radius=10)
                client._blit_fitted_text(
                    label,
                    rect,
                    color=(245, 245, 245),
                    pad=6,
                    base_px=int(max(14, round(20 * float(getattr(client, 'ui_scale', 1.0) or 1.0)))),
                    max_lines=1,
                )
            except Exception:
                pass

        open_side = str(getattr(client, '_bot_battle_dropdown_open', None) or '').strip().lower()
        _draw_dropdown(dd_a, f"Bot A: {client._fmt_bot_battle_style(a_style)}", open_now=(open_side == 'a'))
        _draw_dropdown(dd_b, f"Bot B: {client._fmt_bot_battle_style(b_style)}", open_now=(open_side == 'b'))

        def _draw_dropdown_options(side: str) -> None:
            rects = client._get_bot_battle_dropdown_option_rects('left' if side == 'a' else 'right')
            if not rects:
                return
            cur = a_style if side == 'a' else b_style
            for st, rr in rects:
                try:
                    is_cur = (str(st).strip().lower() == str(cur).strip().lower())
                    # Opaque dropdown items so they remain readable over the sword grid.
                    bg = (30, 30, 45) if is_cur else (20, 20, 32)
                    self._pygame.draw.rect(client.screen, bg, rr, border_radius=8)
                    self._pygame.draw.rect(client.screen, (200, 200, 220), rr, width=1, border_radius=8)
                    client._blit_fitted_text(
                        client._fmt_bot_battle_style(st),
                        rr,
                        color=(245, 245, 245),
                        pad=6,
                        base_px=int(max(12, round(18 * float(getattr(client, 'ui_scale', 1.0) or 1.0)))),
                        max_lines=1,
                    )
                except Exception:
                    pass

        try:
            sel_a = str(getattr(client, '_equipped_sword_value', 'rusty_sword') or 'rusty_sword').strip().lower()
        except Exception:
            sel_a = 'rusty_sword'
        try:
            sel_b = str(getattr(client, '_enemy_sword_value', 'rusty_sword') or 'rusty_sword').strip().lower()
        except Exception:
            sel_b = 'rusty_sword'

        hovered_tile = None

        def _draw_tiles(selected_value: str, layout: dict) -> None:
            nonlocal hovered_tile
            try:
                sword_rect = layout.get('swords_rect')
                tiles = list(layout.get('tiles') or [])
            except Exception:
                sword_rect = None
                tiles = []
            if sword_rect is None:
                return

            # Clip so tiles can scroll without drawing outside the panel.
            try:
                client.screen.set_clip(sword_rect)
            except Exception:
                pass

            for t in tiles:
                rect = t.get('rect')
                if rect is None:
                    continue

                # Skip offscreen tiles for perf.
                try:
                    if not sword_rect.colliderect(rect):
                        continue
                except Exception:
                    pass

                try:
                    hovered = bool(rect.collidepoint(mouse_pos))
                except Exception:
                    hovered = False
                value = str(t.get('value', '') or '').strip().lower()
                is_selected = (value == str(selected_value or '').strip().lower())

                if hovered and sword_rect.collidepoint(mouse_pos):
                    hovered_tile = t

                # Tile outline
                try:
                    if is_selected:
                        self._pygame.draw.rect(client.screen, (240, 240, 200), rect, width=3, border_radius=10)
                    elif hovered:
                        self._pygame.draw.rect(client.screen, (220, 220, 220), rect, width=2, border_radius=10)
                    else:
                        self._pygame.draw.rect(client.screen, (120, 120, 150), rect, width=1, border_radius=10)
                except Exception:
                    pass

                # Name above image
                try:
                    name_h = int(max(16, min(30, round(rect.h * 0.26))))
                except Exception:
                    name_h = 22
                name_rect = self._pygame.Rect(int(rect.x + 4), int(rect.y + 4), int(max(1, rect.w - 8)), int(max(1, name_h)))
                img_rect = self._pygame.Rect(
                    int(rect.x + 6),
                    int(name_rect.bottom + 2),
                    int(max(1, rect.w - 12)),
                    int(max(1, rect.bottom - (name_rect.bottom + 6))),
                )

                try:
                    client._blit_fitted_text(
                        str(t.get('name', '') or value),
                        name_rect,
                        color=(245, 245, 245),
                        pad=2,
                        base_px=int(max(12, round(16 * float(getattr(client, 'ui_scale', 1.0) or 1.0)))),
                        max_lines=1,
                    )
                except Exception:
                    pass

                # Sword art
                try:
                    st = t.get('sword_type')
                    art = client._get_weapon_art_scaled_preview(st, max_w=int(img_rect.w), max_h=int(img_rect.h))
                except Exception:
                    art = None
                if art is not None:
                    try:
                        ax = int(img_rect.centerx - int(art.get_width()) / 2)
                        ay = int(img_rect.centery - int(art.get_height()) / 2)
                        client.screen.blit(art, (ax, ay))
                    except Exception:
                        pass

            try:
                client.screen.set_clip(None)
            except Exception:
                pass

        _draw_tiles(sel_a, lay_a)
        _draw_tiles(sel_b, lay_b)

        # Draw dropdown options last so they appear on top of the sword grid.
        if open_side == 'a':
            _draw_dropdown_options('a')
        elif open_side == 'b':
            _draw_dropdown_options('b')

        # Hover pattern preview (slightly to the right of hovered sword)
        if hovered_tile is not None and open_side not in ('a', 'b'):
            try:
                rr = hovered_tile.get('rect')
                st = hovered_tile.get('sword_type')
                if rr is not None and st is not None:
                    self.draw_bot_battle_hover_pattern(client, sword_type=st, anchor_rect=rr, color_map=color_map)
            except Exception:
                pass
