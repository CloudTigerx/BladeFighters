"""menu_controller.py - Menu UI control logic for Blade Fighters.

This module is part of the staged modularization of `pygame_client.py`.
It keeps `PygameClient` as the orchestrator while extracting menu-specific
state transitions, button building/hit-testing, and overlay rendering.

Initial extraction scope: the menu pause overlay subsystem and menu status text.
"""

from __future__ import annotations

from typing import Any

import pygame

from swordfighting_new.attacks.garbage_pattern import SWORD_PATTERNS, get_available_swords
from swordfighting_new.sword_menu_layout import (
    build_sword_tiles,
    compute_sword_grid,
    get_and_clamp_scroll,
    sword_tile_at_from_layouts,
)


class MenuController:
    def set_menu_status(self, client: Any, msg: str) -> None:
        try:
            client._menu_status_text = str(msg or '')
        except Exception:
            client._menu_status_text = ''

    def enter_menu_pause(self, client: Any) -> None:
        client._menu_pause_active = True
        try:
            client._menu_pause_selected = int(getattr(client, '_menu_pause_selected', 0) or 0)
        except Exception:
            client._menu_pause_selected = 0
        client._menu_pause_buttons = []

    def exit_menu_pause(self, client: Any) -> None:
        client._menu_pause_active = False
        client._menu_pause_buttons = []

    def build_menu_pause_buttons(self, client: Any) -> list[dict]:
        w = int(client.screen.get_width())
        h = int(client.screen.get_height())

        btn = getattr(client, '_menu_button_scaled', None)
        if btn is not None:
            bw, bh = int(btn.get_width()), int(btn.get_height())
        else:
            bw, bh = int(min(w * 0.34, 520)), 84
            bw = max(220, int(bw))
            bh = max(60, int(bh))

        gap = max(12, int(round(bh * 0.28)))
        total_h = 3 * bh + 2 * gap
        start_y = int(h * 0.58 - total_h / 2)
        bx = int((w - bw) / 2)

        return [
            {'id': 'resume', 'label': 'Resume', 'rect': pygame.Rect(bx, int(start_y), bw, bh)},
            {'id': 'back', 'label': 'Back', 'rect': pygame.Rect(bx, int(start_y + bh + gap), bw, bh)},
            {'id': 'exit', 'label': 'Exit Game', 'rect': pygame.Rect(bx, int(start_y + 2 * (bh + gap)), bw, bh)},
        ]

    def menu_pause_button_at(self, client: Any, pos) -> int | None:
        try:
            x, y = int(pos[0]), int(pos[1])
        except Exception:
            return None
        for i, b in enumerate(getattr(client, '_menu_pause_buttons', []) or []):
            rect = b.get('rect', None)
            if rect is not None and rect.collidepoint((x, y)):
                return int(i)
        return None

    def menu_pause_action(self, client: Any, action_id: str) -> None:
        aid = (action_id or '').strip().lower()
        if aid == 'resume':
            self.exit_menu_pause(client)
            return
        if aid == 'back':
            self.exit_menu_pause(client)
            client._menu_view = 'main'
            self.set_menu_status(client, '')
            return
        if aid == 'exit':
            client.running = False
            return

    def draw_menu_pause_overlay(self, client: Any) -> None:
        # Dim overlay
        try:
            w, h = int(client.screen.get_width()), int(client.screen.get_height())
            overlay = pygame.Surface((w, h), flags=pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            client.screen.blit(overlay, (0, 0))
        except Exception:
            pass

    def handle_menu_pause_event(self, client: Any, event) -> bool:
        """Handle input for the menu pause overlay.

        Returns True if the event was consumed.
        """
        if not bool(getattr(client, '_menu_pause_active', False)):
            return False

        if event.type == pygame.KEYDOWN:
            try:
                key = event.key
            except Exception:
                key = None

            try:
                if key is not None and (client._event_is_action(key, 'pause') or client._event_is_action(key, 'ui_back')):
                    self.menu_pause_action(client, 'resume')
                    return True
            except Exception:
                pass

            try:
                if key is not None and client._event_is_action(key, 'ui_confirm'):
                    try:
                        idx = int(getattr(client, '_menu_pause_selected', 0) or 0)
                    except Exception:
                        idx = 0
                    btns = getattr(client, '_menu_pause_buttons', None) or self.build_menu_pause_buttons(client)
                    if 0 <= idx < len(btns):
                        try:
                            client._ui_flash_button('menu_pause', str(btns[idx].get('id')))
                        except Exception:
                            pass
                        self.menu_pause_action(client, str(btns[idx].get('id')))
                    return True
            except Exception:
                pass

            try:
                if key is not None and (client._event_is_action(key, 'ui_up') or key == pygame.K_LEFT):
                    try:
                        _btns = getattr(client, '_menu_pause_buttons', None) or self.build_menu_pause_buttons(client)
                        client._menu_pause_selected = max(0, int(getattr(client, '_menu_pause_selected', 0) or 0) - 1)
                    except Exception:
                        client._menu_pause_selected = 0
                    return True
            except Exception:
                pass

            try:
                if key is not None and (client._event_is_action(key, 'ui_down') or key == pygame.K_RIGHT):
                    try:
                        btns = getattr(client, '_menu_pause_buttons', None) or self.build_menu_pause_buttons(client)
                        client._menu_pause_selected = min(
                            max(0, len(btns) - 1),
                            int(getattr(client, '_menu_pause_selected', 0) or 0) + 1,
                        )
                    except Exception:
                        client._menu_pause_selected = 1
                    return True
            except Exception:
                pass

            return False

        if event.type == pygame.MOUSEBUTTONDOWN and getattr(event, 'button', None) == 1:
            if not getattr(client, '_menu_pause_buttons', None):
                client._menu_pause_buttons = self.build_menu_pause_buttons(client)
            hit = self.menu_pause_button_at(client, getattr(event, 'pos', (0, 0)))
            if hit is not None:
                try:
                    client._menu_pause_selected = int(hit)
                except Exception:
                    client._menu_pause_selected = 0
                try:
                    b = client._menu_pause_buttons[int(hit)]
                    try:
                        client._ui_flash_button('menu_pause', str(b.get('id')))
                    except Exception:
                        pass
                    self.menu_pause_action(client, str(b.get('id')))
                except Exception:
                    pass
            # Consume any left click while the overlay is active.
            return True

        return False

    def handle_menu_state_event(self, client: Any, event) -> bool:
        """Handle events while the client is in menu state.

        This wraps the pause-overlay input handling, transition gating, and the
        normal menu event dispatch.

        Returns True if the event was consumed (caller should `continue`).
        """
        try:
            if self.handle_menu_pause_event(client, event):
                return True
        except Exception:
            pass

        # During fade transitions, ignore menu inputs.
        try:
            if bool(getattr(client, '_menu_transition_active', False)):
                return True
        except Exception:
            pass

        try:
            if self.handle_menu_event(client, event):
                return True
        except Exception:
            pass

        return False

        w = int(client.screen.get_width())
        h = int(client.screen.get_height())

        # Title
        try:
            title = client._menu_title_font.render('Paused', True, (245, 245, 245))
            client.screen.blit(title, (int((w - title.get_width()) / 2), int(h * 0.20)))
        except Exception:
            pass

        if not getattr(client, '_menu_pause_buttons', None):
            client._menu_pause_buttons = self.build_menu_pause_buttons(client)

        btn_img_normal = getattr(client, '_menu_button_scaled', None)
        btn_img_hover = getattr(client, '_menu_button_hover_scaled', None) or btn_img_normal
        btn_img_pressed = getattr(client, '_menu_button_pressed_scaled', None) or btn_img_hover or btn_img_normal

        sel = int(getattr(client, '_menu_pause_selected', 0) or 0)

        try:
            mouse_pos = pygame.mouse.get_pos()
        except Exception:
            mouse_pos = (0, 0)
        try:
            mouse_down = bool(pygame.mouse.get_pressed()[0])
        except Exception:
            mouse_down = False

        for i, b in enumerate(client._menu_pause_buttons):
            rect = b.get('rect')
            if rect is None:
                continue

            hovered = False
            try:
                hovered = bool(rect.collidepoint(mouse_pos))
            except Exception:
                hovered = False
            pressed = bool(mouse_down and hovered)
            try:
                if client._ui_is_button_flashed('menu_pause', str(b.get('id'))):
                    pressed = True
            except Exception:
                pass

            if btn_img_normal is None:
                pygame.draw.rect(client.screen, (40, 40, 60), rect, border_radius=12)
                pygame.draw.rect(client.screen, (180, 180, 200), rect, width=2, border_radius=12)
            else:
                src = btn_img_pressed if pressed else (btn_img_hover if (hovered or i == sel) else btn_img_normal)
                client.screen.blit(src, (int(rect.x), int(rect.y)))

            if i == sel:
                try:
                    pygame.draw.rect(
                        client.screen,
                        (255, 220, 120),
                        rect,
                        width=max(2, int(round(3 * float(getattr(client, 'ui_scale', 1.0) or 1.0)))),
                        border_radius=12,
                    )
                except Exception:
                    pass

            try:
                client._blit_fitted_text(
                    str(b.get('label', '')),
                    rect,
                    color=(255, 255, 255),
                    base_px=int(getattr(client, '_menu_button_font_px', 40) or 40),
                    max_lines=2,
                )
            except Exception:
                pass

        # Hint
        try:
            hint = client.ui_font.render('Esc/P = Resume   Enter/Click = Select', True, (230, 230, 230))
            client.screen.blit(hint, (int(w * 0.06), int(h * 0.14)))
        except Exception:
            pass

    def menu_button_at(self, client: Any, pos) -> str | None:
        try:
            x, y = int(pos[0]), int(pos[1])
        except Exception:
            return None
        for b in getattr(client, '_menu_buttons', []) or []:
            try:
                rect = b.get('rect', None)
                if rect is not None and rect.collidepoint((x, y)):
                    return str(b.get('id'))
            except Exception:
                continue
        return None

    def story_char_button_at(self, client: Any, pos) -> str | None:
        try:
            x, y = int(pos[0]), int(pos[1])
        except Exception:
            return None
        for b in getattr(client, '_story_char_buttons', []) or []:
            try:
                rect = b.get('rect', None)
                if rect is not None and rect.collidepoint((x, y)):
                    return str(b.get('id'))
            except Exception:
                continue
        return None

    def get_menu_safe_bounds(self, client: Any, view: str) -> tuple[int, int]:
        """Return (safe_top, safe_bottom_y) for menu content under the title/header."""
        h = int(client.screen.get_height())

        try:
            view_norm = (view or 'main').strip().lower()
        except Exception:
            view_norm = 'main'

        header_bottom = int(h * 0.06)
        try:
            use_wordmark = (
                view_norm != 'options'
                and view_norm not in ('enemy_select', 'controls', 'inventory', 'enemy_pattern')
                and getattr(client, '_menu_title_wordmark_scaled', None) is not None
            )
        except Exception:
            use_wordmark = False

        if use_wordmark:
            try:
                img = getattr(client, '_menu_title_wordmark_scaled', None)
                y = int(h * 0.035)
                header_bottom = int(y + int(img.get_height()))
            except Exception:
                header_bottom = int(h * 0.06)
        else:
            try:
                title_h = int(getattr(client, '_menu_title_font', client.ui_font).get_height())
            except Exception:
                title_h = 54
            header_bottom = int(h * 0.06 + max(1, title_h))

        top_margin = int(max(10, round(h * 0.03)))
        bottom_margin = int(max(18, round(h * 0.06)))
        safe_top = int(header_bottom + top_margin)
        safe_bottom_y = int(h - bottom_margin)
        safe_top = max(0, min(int(h), int(safe_top)))
        safe_bottom_y = max(0, min(int(h), int(safe_bottom_y)))
        if safe_bottom_y < safe_top:
            safe_bottom_y = safe_top
        return (safe_top, safe_bottom_y)

    def get_two_panel_rects(self, client: Any, *, view: str) -> tuple['pygame.Rect', 'pygame.Rect', 'pygame.Rect']:
        """Shared 2-side-panel + middle-column menu layout.

        Returns (left_panel, right_panel, mid_rect) sized to fit within the view's safe bounds.
        """
        w = int(client.screen.get_width())

        safe_top, safe_bottom_y = self.get_menu_safe_bounds(client, str(view))
        panel_h = int(max(1, safe_bottom_y - safe_top))

        gap_x = int(max(14, round(w * 0.03)))
        pad_x = int(max(10, round(w * 0.04)))

        mid_min_w = int(max(240, round(w * 0.22)))
        desired_panel_w = int(max(220, round(w * 0.28)))
        max_panel_w = int(max(160, (w - mid_min_w - 2 * pad_x - 2 * gap_x) / 2))
        panel_w = int(max(140, min(desired_panel_w, max_panel_w)))

        left_x = int(pad_x)
        right_x = int(w - pad_x - panel_w)
        mid_x = int(left_x + panel_w + gap_x)
        mid_w = int(right_x - gap_x - mid_x)

        # If the window is tiny, squeeze panels to preserve a usable middle column.
        if mid_w < 200:
            try:
                panel_w2 = int(max(120, (w - 200 - 2 * pad_x - 2 * gap_x) / 2))
                panel_w = int(max(120, min(panel_w, panel_w2)))
                right_x = int(w - pad_x - panel_w)
                mid_x = int(left_x + panel_w + gap_x)
                mid_w = int(right_x - gap_x - mid_x)
            except Exception:
                pass
            mid_w = int(max(1, mid_w))

        left = pygame.Rect(int(left_x), int(safe_top), int(panel_w), int(panel_h))
        right = pygame.Rect(int(right_x), int(safe_top), int(panel_w), int(panel_h))
        mid = pygame.Rect(int(mid_x), int(safe_top), int(max(1, mid_w)), int(panel_h))
        return (left, right, mid)

    def get_bot_battle_sword_panel_rects(self, client: Any) -> tuple['pygame.Rect', 'pygame.Rect', 'pygame.Rect']:
        """Return (left_panel, right_panel, mid_rect) for Bot Battle menu layout."""
        return self.get_two_panel_rects(client, view='bot_battle')

    def get_quickplay_sword_panel_rects(self, client: Any) -> tuple['pygame.Rect', 'pygame.Rect', 'pygame.Rect']:
        """Return (left_panel, right_panel, mid_rect) for Quickplay enemy_select layout."""
        return self.get_two_panel_rects(client, view='enemy_select')

    def get_quickplay_panel_inner_rects(self, client: Any, side: str) -> tuple['pygame.Rect', 'pygame.Rect', 'pygame.Rect']:
        """Return (panel_rect, header_rect, swords_rect) for a Quickplay side."""
        try:
            ui = getattr(client, '_ui', None)
            ui_scale = float(getattr(ui, 'scale', getattr(client, 'ui_scale', 1.0) or 1.0) or 1.0)
        except Exception:
            ui_scale = 1.0

        left_panel, right_panel, _mid = self.get_quickplay_sword_panel_rects(client)
        panel = left_panel if str(side).lower() in ('left', 'a', 'bot_a') else right_panel

        pad = int(max(8, round(12 * ui_scale)))
        gap = int(max(8, round(10 * ui_scale)))
        inner = pygame.Rect(int(panel.x + pad), int(panel.y + pad), int(max(1, panel.w - 2 * pad)), int(max(1, panel.h - 2 * pad)))

        header_h = int(max(40, round(54 * ui_scale)))
        header_h = int(min(header_h, max(40, int(inner.h * 0.18))))
        header_rect = pygame.Rect(int(inner.x), int(inner.y), int(inner.w), int(max(1, header_h)))
        swords_rect = pygame.Rect(int(inner.x), int(header_rect.bottom + gap), int(inner.w), int(max(1, inner.bottom - (header_rect.bottom + gap))))
        return (panel, header_rect, swords_rect)

    def quickplay_sword_layout(self, client: Any, side: str) -> dict:
        """Compute sword tile layout for Quickplay enemy_select side, including scrolling bounds."""
        try:
            ui = getattr(client, '_ui', None)
            ui_scale = float(getattr(ui, 'scale', getattr(client, 'ui_scale', 1.0) or 1.0) or 1.0)
        except Exception:
            ui_scale = 1.0

        try:
            swords = list(get_available_swords() or [])
        except Exception:
            swords = []

        panel, header_rect, swords_rect = self.get_quickplay_panel_inner_rects(client, side)
        n = int(len(swords))
        if n <= 0 or swords_rect.w <= 1 or swords_rect.h <= 1:
            return {
                'panel': panel,
                'header_rect': header_rect,
                'swords_rect': swords_rect,
                'tiles': [],
                'max_scroll': 0,
                'gap': 0,
            }

        grid = compute_sword_grid(swords_rect=swords_rect, n=n, ui_scale=ui_scale)
        gap = int(grid.get('gap', 0) or 0)
        cols = int(grid.get('cols', 1) or 1)
        tile_w = int(grid.get('tile_w', 40) or 40)
        tile_h = int(grid.get('tile_h', 66) or 66)
        max_scroll = int(grid.get('max_scroll', 0) or 0)

        try:
            scroll_dict = getattr(client, '_quickplay_sword_scroll_y', None) or {}
        except Exception:
            scroll_dict = {}
        cur_scroll = get_and_clamp_scroll(scroll_dict=scroll_dict, side=side, max_scroll=max_scroll)

        try:
            friendly_name_fn = getattr(client, '_friendly_sword_name', None)
        except Exception:
            friendly_name_fn = None
        if friendly_name_fn is None:
            def friendly_name_fn(v: str) -> str:
                return str(v or '')

        tiles = build_sword_tiles(
            swords=swords,
            swords_rect=swords_rect,
            cols=cols,
            tile_w=tile_w,
            tile_h=tile_h,
            gap=gap,
            cur_scroll=cur_scroll,
            friendly_name_fn=friendly_name_fn,
            rect_factory=pygame.Rect,
        )

        return {
            'panel': panel,
            'header_rect': header_rect,
            'swords_rect': swords_rect,
            'tiles': tiles,
            'max_scroll': max_scroll,
            'gap': gap,
        }

    def quickplay_sword_tile_at(self, client: Any, pos) -> tuple[str, str] | None:
        """Return ('a'|'b', sword_value) if a Quickplay sword tile was clicked."""
        try:
            lay_a = self.quickplay_sword_layout(client, 'left')
        except Exception:
            lay_a = {}
        try:
            lay_b = self.quickplay_sword_layout(client, 'right')
        except Exception:
            lay_b = {}
        return sword_tile_at_from_layouts(pos=pos, lay_a=lay_a, lay_b=lay_b)

    def bot_battle_bot_styles(self) -> list[str]:
        return ['rubix1', 'rubix2', 'rubix3', 'rubix4', 'rubix5', 'rubix6']

    def fmt_bot_battle_style(self, style: str) -> str:
        s = str(style or '').strip().lower()
        if s in self.bot_battle_bot_styles():
            return 'Rubix ' + s.replace('rubix', '')
        return s or 'Rubix 1'

    def get_bot_battle_panel_inner_rects(self, client: Any, side: str) -> tuple['pygame.Rect', 'pygame.Rect', 'pygame.Rect']:
        """Return (panel_rect, dropdown_rect, swords_rect) for a side."""
        try:
            ui = getattr(client, '_ui', None)
            ui_scale = float(getattr(ui, 'scale', getattr(client, 'ui_scale', 1.0) or 1.0) or 1.0)
        except Exception:
            ui_scale = 1.0

        left_panel, right_panel, _mid = self.get_bot_battle_sword_panel_rects(client)
        panel = left_panel if str(side).lower() in ('left', 'a', 'bot_a') else right_panel

        pad = int(max(8, round(12 * ui_scale)))
        gap = int(max(8, round(10 * ui_scale)))
        inner = pygame.Rect(int(panel.x + pad), int(panel.y + pad), int(max(1, panel.w - 2 * pad)), int(max(1, panel.h - 2 * pad)))

        dropdown_h = int(max(44, round(64 * ui_scale)))
        dropdown_h = int(min(dropdown_h, max(44, int(inner.h * 0.22))))
        dropdown_rect = pygame.Rect(int(inner.x), int(inner.y), int(inner.w), int(max(1, dropdown_h)))

        swords_rect = pygame.Rect(int(inner.x), int(dropdown_rect.bottom + gap), int(inner.w), int(max(1, inner.bottom - (dropdown_rect.bottom + gap))))
        return (panel, dropdown_rect, swords_rect)

    def get_bot_battle_dropdown_option_rects(self, client: Any, side: str) -> list[tuple[str, 'pygame.Rect']]:
        """If dropdown is open for this side, return list of (style, rect)."""
        open_side = str(getattr(client, '_bot_battle_dropdown_open', None) or '').strip().lower()
        if open_side not in ('a', 'b'):
            return []
        want = 'a' if str(side).lower() in ('left', 'a', 'bot_a') else 'b'
        if open_side != want:
            return []

        try:
            ui = getattr(client, '_ui', None)
            ui_scale = float(getattr(ui, 'scale', getattr(client, 'ui_scale', 1.0) or 1.0) or 1.0)
        except Exception:
            ui_scale = 1.0

        _panel, dropdown_rect, swords_rect = self.get_bot_battle_panel_inner_rects(client, 'left' if want == 'a' else 'right')

        styles = self.bot_battle_bot_styles()
        item_h = int(max(34, round(44 * ui_scale)))
        item_gap = int(max(6, round(6 * ui_scale)))
        max_items = int(max(1, (swords_rect.y - dropdown_rect.bottom - item_gap) // max(1, (item_h + item_gap))))
        # If there isn't vertical room above the swords, render dropdown into the swords area.
        if max_items <= 0:
            max_items = len(styles)

        out: list[tuple[str, pygame.Rect]] = []
        x = int(dropdown_rect.x)
        y0 = int(dropdown_rect.bottom + item_gap)
        w = int(dropdown_rect.w)
        for i, st in enumerate(styles):
            rr = pygame.Rect(int(x), int(y0 + i * (item_h + item_gap)), int(w), int(item_h))
            out.append((str(st), rr))
        return out

    def bot_battle_dropdown_header_at(self, client: Any, pos) -> str | None:
        """Return 'a' or 'b' if pos hits a dropdown header."""
        try:
            x, y = int(pos[0]), int(pos[1])
        except Exception:
            return None
        p = (x, y)
        try:
            _panel, dd_a, _s_a = self.get_bot_battle_panel_inner_rects(client, 'left')
            if dd_a.collidepoint(p):
                return 'a'
        except Exception:
            pass
        try:
            _panel, dd_b, _s_b = self.get_bot_battle_panel_inner_rects(client, 'right')
            if dd_b.collidepoint(p):
                return 'b'
        except Exception:
            pass
        return None

    def bot_battle_dropdown_option_at(self, client: Any, pos) -> tuple[str, str] | None:
        """Return (side, style) if pos hits an open dropdown option."""
        try:
            x, y = int(pos[0]), int(pos[1])
        except Exception:
            return None
        p = (x, y)

        open_side = str(getattr(client, '_bot_battle_dropdown_open', None) or '').strip().lower()
        if open_side not in ('a', 'b'):
            return None
        side = 'a' if open_side == 'a' else 'b'

        try:
            rects = self.get_bot_battle_dropdown_option_rects(client, 'left' if side == 'a' else 'right')
            for st, rr in rects:
                if rr.collidepoint(p):
                    return (side, str(st))
        except Exception:
            return None
        return None

    def bot_battle_sword_layout(self, client: Any, side: str) -> dict:
        """Compute sword tile layout for a side, including scrolling bounds."""
        try:
            ui = getattr(client, '_ui', None)
            ui_scale = float(getattr(ui, 'scale', getattr(client, 'ui_scale', 1.0) or 1.0) or 1.0)
        except Exception:
            ui_scale = 1.0

        try:
            swords = list(get_available_swords() or [])
        except Exception:
            swords = []

        panel, dropdown_rect, swords_rect = self.get_bot_battle_panel_inner_rects(client, side)
        n = int(len(swords))
        if n <= 0 or swords_rect.w <= 1 or swords_rect.h <= 1:
            return {
                'panel': panel,
                'dropdown_rect': dropdown_rect,
                'swords_rect': swords_rect,
                'tiles': [],
                'max_scroll': 0,
                'gap': 0,
            }

        grid = compute_sword_grid(swords_rect=swords_rect, n=n, ui_scale=ui_scale)
        gap = int(grid.get('gap', 0) or 0)
        cols = int(grid.get('cols', 1) or 1)
        tile_w = int(grid.get('tile_w', 40) or 40)
        tile_h = int(grid.get('tile_h', 66) or 66)
        max_scroll = int(grid.get('max_scroll', 0) or 0)

        try:
            scroll_dict = getattr(client, '_bot_battle_sword_scroll_y', None) or {}
        except Exception:
            scroll_dict = {}
        cur_scroll = get_and_clamp_scroll(scroll_dict=scroll_dict, side=side, max_scroll=max_scroll)

        try:
            friendly_name_fn = getattr(client, '_friendly_sword_name', None)
        except Exception:
            friendly_name_fn = None
        if friendly_name_fn is None:
            def friendly_name_fn(v: str) -> str:
                return str(v or '')

        tiles = build_sword_tiles(
            swords=swords,
            swords_rect=swords_rect,
            cols=cols,
            tile_w=tile_w,
            tile_h=tile_h,
            gap=gap,
            cur_scroll=cur_scroll,
            friendly_name_fn=friendly_name_fn,
            rect_factory=pygame.Rect,
        )

        return {
            'panel': panel,
            'dropdown_rect': dropdown_rect,
            'swords_rect': swords_rect,
            'tiles': tiles,
            'max_scroll': max_scroll,
            'gap': gap,
        }

    def bot_battle_sword_tile_at(self, client: Any, pos) -> tuple[str, str] | None:
        """Return ('a'|'b', sword_value) if a Bot Battle sword tile was clicked."""
        try:
            lay_a = self.bot_battle_sword_layout(client, 'left')
        except Exception:
            lay_a = {}
        try:
            lay_b = self.bot_battle_sword_layout(client, 'right')
        except Exception:
            lay_b = {}
        return sword_tile_at_from_layouts(pos=pos, lay_a=lay_a, lay_b=lay_b)

    def begin_menu_transition(self, client: Any, to_view: str, duration_ms: int | None = None) -> None:
        try:
            client._menu_transition_active = True
            client._menu_transition_from = str(getattr(client, '_menu_view', 'main') or 'main')
            client._menu_transition_to = str(to_view or 'main')
            client._menu_transition_start_ms = int(pygame.time.get_ticks())
            if duration_ms is not None:
                client._menu_transition_duration_ms = max(120, int(duration_ms))
        except Exception:
            client._menu_transition_active = False

    def on_menu_button(self, client: Any, bid: str) -> None:
        bid = (bid or '').strip().lower()
        view = str(getattr(client, '_menu_view', 'main') or 'main').strip().lower()

        # Story-specific menus (bypass the standard button builder).
        if view == 'story_quarters':
            if bid == 'story_sleep':
                self.set_menu_status(client, '')
                try:
                    client._story_has_slept = True
                except Exception:
                    pass
                # Enter inside-cabin scene in the pre-sleep state.
                try:
                    client._story_inside_cabin_slept = False
                except Exception:
                    pass
                # Sleep -> wake up inside the cabin.
                self.begin_menu_transition(client, 'story_inside_cabin', duration_ms=650)
                return

        if view == 'story_inside_cabin':
            if bid == 'story_practice_exams':
                self.set_menu_status(client, '')
                self.begin_menu_transition(client, 'story_practice_exams', duration_ms=650)
                return
            if bid == 'story_cabin_sleep':
                # Fade into the same scene to simulate sleeping/waking up.
                self.set_menu_status(client, '')
                try:
                    client._story_inside_cabin_slept = True
                except Exception:
                    pass
                self.begin_menu_transition(client, 'story_inside_cabin', duration_ms=650)
                return
            if bid == 'story_proceed_examinations':
                self.set_menu_status(client, '')
                self.begin_menu_transition(client, 'story_examinations', duration_ms=650)
                return

        if view == 'story_examinations':
            if bid == 'back':
                self.set_menu_status(client, '')
                self.begin_menu_transition(client, 'story_inside_cabin', duration_ms=650)
                return

        if view == 'story_practice_exams':
            if bid == 'back':
                self.set_menu_status(client, '')
                self.begin_menu_transition(client, 'story_inside_cabin', duration_ms=650)
                return
            if bid == 'practice_speed_test':
                self.set_menu_status(client, '')
                client._start_practice_event('speed_test')
                return
            if bid == 'practice_1v1':
                self.set_menu_status(client, '')
                client._start_practice_event('boss_1v1')
                return
        if view == 'options':
            if bid == 'back':
                client._menu_view = 'main'
                self.set_menu_status(client, '')
                try:
                    client._menu_selected = 0
                except Exception:
                    pass
                return
            if bid == 'controls':
                client._menu_view = 'controls'
                client._rebind_action = None
                try:
                    client._menu_selected = 0
                except Exception:
                    pass
                self.set_menu_status(client, 'Click/Enter an action, then press a key (Esc cancels)')
                return
            if bid == 'toggle_sfx':
                client._toggle_sfx()
                self.set_menu_status(client, 'SFX ' + ('enabled' if bool(getattr(client, '_sfx_enabled', True)) else 'disabled'))
                return
            if bid == 'toggle_fullscreen':
                try:
                    client._set_fullscreen_enabled(not bool(getattr(client, '_fullscreen_enabled', False)), persist=True)
                    self.set_menu_status(client, 'Fullscreen ' + ('enabled' if bool(getattr(client, '_fullscreen_enabled', False)) else 'disabled') + ' (saved)')
                    # Force button relayout (window size likely changed)
                    try:
                        client._menu_buttons = []
                        client._menu_last_size = None
                    except Exception:
                        pass
                except Exception:
                    self.set_menu_status(client, 'Failed to toggle fullscreen')
                return
            if bid == 'vol_down':
                client._set_sfx_volume(float(getattr(client, '_sfx_volume', 0.65) or 0.65) - 0.05)
                try:
                    client._persist_volume_preference()
                except Exception:
                    pass
                self.set_menu_status(client, f"Volume: {int(round(float(client._sfx_volume) * 100.0))}% (saved)")
                return
            if bid == 'vol_up':
                client._set_sfx_volume(float(getattr(client, '_sfx_volume', 0.65) or 0.65) + 0.05)
                try:
                    client._persist_volume_preference()
                except Exception:
                    pass
                self.set_menu_status(client, f"Volume: {int(round(float(client._sfx_volume) * 100.0))}% (saved)")
                return
            if bid == 'hmove_faster':
                client._set_horizontal_move_repeat_ms(int(getattr(client, '_horizontal_move_repeat_ms', 70) or 70) - 10)
                try:
                    client._persist_volume_preference()
                except Exception:
                    pass
                self.set_menu_status(client, f"Horizontal move repeat: {int(getattr(client, '_horizontal_move_repeat_ms', 70) or 70)} ms (saved)")
                return
            if bid == 'hmove_slower':
                client._set_horizontal_move_repeat_ms(int(getattr(client, '_horizontal_move_repeat_ms', 70) or 70) + 10)
                try:
                    client._persist_volume_preference()
                except Exception:
                    pass
                self.set_menu_status(client, f"Horizontal move repeat: {int(getattr(client, '_horizontal_move_repeat_ms', 70) or 70)} ms (saved)")
                return
            if bid == 'save_settings':
                try:
                    client._persist_volume_preference()
                    self.set_menu_status(client, 'Settings saved')
                except Exception:
                    self.set_menu_status(client, 'Failed to save settings')
                return
            return

        if view == 'controls':
            if bid == 'back':
                client._menu_view = 'options'
                client._rebind_action = None
                try:
                    client._menu_selected = 0
                except Exception:
                    pass
                self.set_menu_status(client, '')
                return
            if bid == 'reset_controls':
                try:
                    client._keybinds = client._normalize_keybinds({}, client._default_keybinds)
                    client._persist_controls_preference()
                    self.set_menu_status(client, 'Controls reset (saved)')
                except Exception:
                    self.set_menu_status(client, 'Failed to reset controls')
                return
            if bid.startswith('bind:'):
                act = str(bid.split(':', 1)[1] if ':' in bid else '').strip()
                if act:
                    client._rebind_action = act
                    self.set_menu_status(client, f"Press a key for: {act} (Esc cancels)")
                return
            return

        if view == 'enemy_select':
            if bid == 'back':
                client._menu_view = 'main'
                self.set_menu_status(client, '')
                try:
                    client._menu_selected = 0
                except Exception:
                    pass
                return
            if bid == 'enemy_pattern':
                client._menu_view = 'enemy_pattern'
                self.set_menu_status(client, 'Pick the enemy sword pattern (this controls what you receive)')
                try:
                    client._menu_selected = 0
                except Exception:
                    pass
                return
            if bid == 'rubix3':
                client._start_match('rubix3', None)
                return
            if bid == 'rubix4':
                client._start_match('rubix4', None)
                return
            if bid == 'rubix5':
                client._start_match('rubix5', None)
                return
            if bid == 'rubix6':
                client._start_match('rubix6', None)
                return
            if bid == 'boss':
                client._start_match('boss', None)
                return
            if bid == 'mirror':
                client._start_match('mirror', None)
                return
            if bid == 'passive':
                client._start_match('passive', None)
                return
            if bid == 'solo':
                client._start_match('solo', None)
                return
            return

        if view == 'enemy_pattern':
            if bid == 'back':
                client._menu_view = 'enemy_select'
                self.set_menu_status(client, '')
                try:
                    client._menu_selected = 0
                except Exception:
                    pass
                return
            if bid.startswith('enemy_sword:'):
                raw = str(bid.split(':', 1)[1] if ':' in bid else '').strip().lower()
                if raw:
                    try:
                        client._enemy_sword_value = str(raw)
                        client._persist_enemy_sword_preference()
                        client._apply_enemy_sword_to_session()
                        try:
                            st = client._resolve_sword_type(raw)
                            patt = SWORD_PATTERNS.get(st)
                            nm = str(getattr(patt, 'name', raw) or raw)
                        except Exception:
                            nm = raw
                        self.set_menu_status(client, f"Enemy pattern: {nm} (saved)")
                    except Exception:
                        self.set_menu_status(client, 'Failed to set enemy pattern')
                return
            return

        if view == 'inventory':
            if bid == 'back':
                client._menu_view = 'main'
                self.set_menu_status(client, '')
                try:
                    client._menu_selected = 0
                except Exception:
                    pass
                return

            if bid.startswith('sword:'):
                raw = str(bid.split(':', 1)[1] if ':' in bid else '').strip().lower()
                if raw:
                    try:
                        client._equipped_sword_value = str(raw)
                        client._persist_equipped_sword_preference()
                        client._apply_equipped_sword_to_session()
                        try:
                            st = client._resolve_sword_type(raw)
                            patt = SWORD_PATTERNS.get(st)
                            nm = str(getattr(patt, 'name', raw) or raw)
                        except Exception:
                            nm = raw
                        self.set_menu_status(client, f"Equipped: {nm} (saved)")
                    except Exception:
                        self.set_menu_status(client, 'Failed to equip sword')
                return
            return

        if view == 'bot_battle':
            if bid == 'back':
                client._menu_view = 'main'
                self.set_menu_status(client, '')
                try:
                    client._menu_selected = 0
                except Exception:
                    pass
                return
            if bid == 'start_bot_battle':
                self.set_menu_status(client, '')
                client._start_bot_battle()
                return
            return

        # Main menu
        if bid == 'quickplay':
            client._start_quickplay()
        elif bid == 'strike_test':
            client._enter_strike_test()
        elif bid == 'bot_battle':
            client._menu_view = 'bot_battle'
            self.set_menu_status(client, '')
            try:
                client._menu_selected = 0
            except Exception:
                pass
        elif bid == 'inventory':
            client._menu_view = 'inventory'
            self.set_menu_status(client, 'Select a sword to equip it')
            try:
                client._menu_selected = 0
            except Exception:
                pass
        elif bid == 'options':
            client._menu_view = 'options'
            self.set_menu_status(client, f"Volume: {int(round(float(getattr(client, '_sfx_volume', 0.65) or 0.65) * 100.0))}%")
            try:
                client._menu_selected = 0
            except Exception:
                pass
        elif bid == 'exit':
            client.running = False
        elif bid == 'story':
            client._menu_view = 'story_char_select'
            client._menu_pause_active = False
            client._menu_pause_buttons = []
            client._story_char_buttons = []
            client._story_selected_character = None
            # For now, always restart Story Mode from the beginning so content/layout
            # adjustments can be made without old progress skipping steps.
            client._story_swift_tutorial_complete = False
            client._story_player_name = ''
            client._story_name_confirmed = False
            client._story_dialogue_step = 0
            client._story_post_tutorial_step = 0
            try:
                client._story_has_slept = False
            except Exception:
                pass
            self.set_menu_status(client, '')
        elif bid == 'multiplayer':
            self.set_menu_status(client, 'Multiplayer: coming soon')
        elif bid == 'story_proceed_academy':
            # Post-tutorial: player attempts to enter the Academy.
            try:
                client._story_post_tutorial_step = 2
            except Exception:
                client._story_post_tutorial_step = 2
            self.set_menu_status(client, '')
        elif bid == 'story_proceed_quarters':
            # Post-tutorial: move to quarters placeholder screen.
            try:
                client._story_post_tutorial_step = 3
            except Exception:
                client._story_post_tutorial_step = 3
            self.set_menu_status(client, '')
            self.begin_menu_transition(client, 'story_quarters', duration_ms=650)

    def handle_menu_event(self, client: Any, event: Any) -> bool:
        """Handle a single pygame event while the client is in menu state.

        Returns True if the event was consumed.
        """
        try:
            et = int(getattr(event, 'type', -1) or -1)
        except Exception:
            et = -1

        # --- Keyboard -------------------------------------------------
        if et == int(getattr(pygame, 'KEYDOWN', -9999)):
            view = str(getattr(client, '_menu_view', 'main') or 'main')

            # Controls menu: capture a new binding.
            if view == 'controls' and str(getattr(client, '_rebind_action', '') or '').strip():
                if client._event_is_action(getattr(event, 'key', None), 'ui_back'):
                    client._rebind_action = None
                    self.set_menu_status(client, 'Rebind canceled')
                    return True
                try:
                    act = str(getattr(client, '_rebind_action', '') or '').strip()
                    if act:
                        client._set_single_binding(act, int(getattr(event, 'key', 0) or 0))
                        client._persist_controls_preference()
                        self.set_menu_status(client, f"Bound {act} to {client._format_action_keys(act)} (saved)")
                except Exception:
                    self.set_menu_status(client, 'Failed to bind key')
                client._rebind_action = None
                return True

            # Story menus have their own flow.
            if view in ('story_char_select', 'story_intro', 'story_academy', 'story_quarters', 'story_inside_cabin', 'story_practice_exams', 'story_examinations'):
                if client._event_is_action(getattr(event, 'key', None), 'pause'):
                    self.enter_menu_pause(client)
                    return True
                if view == 'story_intro':
                    if client._event_is_action(getattr(event, 'key', None), 'ui_confirm'):
                        client._advance_story_intro()
                        return True
                    if not bool(getattr(client, '_story_swift_tutorial_complete', False)):
                        client._handle_story_name_input(event)
                        return True

                # For story views that draw clickable buttons into client._menu_buttons,
                # allow keyboard navigation + Enter to activate.
                if view in ('story_academy', 'story_quarters', 'story_inside_cabin', 'story_practice_exams', 'story_examinations'):
                    btns = list(getattr(client, '_menu_buttons', None) or [])

                    if client._event_is_action(getattr(event, 'key', None), 'ui_up') or int(getattr(event, 'key', 0) or 0) == int(getattr(pygame, 'K_LEFT', 0) or 0):
                        try:
                            cur = int(getattr(client, '_menu_selected', 0) or 0)
                        except Exception:
                            cur = 0
                        client._menu_selected = max(0, cur - 1) if btns else 0
                        return True

                    if client._event_is_action(getattr(event, 'key', None), 'ui_down') or int(getattr(event, 'key', 0) or 0) == int(getattr(pygame, 'K_RIGHT', 0) or 0):
                        try:
                            cur = int(getattr(client, '_menu_selected', 0) or 0)
                        except Exception:
                            cur = 0
                        client._menu_selected = min(max(0, len(btns) - 1), cur + 1) if btns else 0
                        return True

                    if client._event_is_action(getattr(event, 'key', None), 'ui_confirm'):
                        try:
                            idx = int(getattr(client, '_menu_selected', 0) or 0)
                        except Exception:
                            idx = 0
                        if 0 <= idx < len(btns):
                            try:
                                client._ui_flash_button('menu', str(btns[idx].get('id')))
                            except Exception:
                                pass
                            self.on_menu_button(client, str(btns[idx].get('id')))
                        return True
                return True

            # Standard menu navigation.
            if client._event_is_action(getattr(event, 'key', None), 'ui_back'):
                if view == 'options':
                    client._menu_view = 'main'
                    self.set_menu_status(client, '')
                    client._menu_selected = 0
                elif view == 'controls':
                    client._menu_view = 'options'
                    self.set_menu_status(client, '')
                    client._menu_selected = 0
                    client._rebind_action = None
                elif view == 'enemy_select':
                    client._menu_view = 'main'
                    self.set_menu_status(client, '')
                    client._menu_selected = 0
                elif view == 'bot_battle':
                    client._menu_view = 'main'
                    self.set_menu_status(client, '')
                    client._menu_selected = 0
                else:
                    # Don't allow Esc to exit from the main menu.
                    pass
                return True

            if client._event_is_action(getattr(event, 'key', None), 'ui_up') or int(getattr(event, 'key', 0) or 0) == int(getattr(pygame, 'K_LEFT', 0) or 0):
                try:
                    btns = self.build_menu_buttons(client, str(view))
                    client._menu_selected = max(0, int(getattr(client, '_menu_selected', 0) or 0) - 1)
                    client._menu_selected = min(client._menu_selected, max(0, len(btns) - 1))
                except Exception:
                    client._menu_selected = 0
                return True

            if client._event_is_action(getattr(event, 'key', None), 'ui_down') or int(getattr(event, 'key', 0) or 0) == int(getattr(pygame, 'K_RIGHT', 0) or 0):
                try:
                    btns = self.build_menu_buttons(client, str(view))
                    client._menu_selected = min(max(0, len(btns) - 1), int(getattr(client, '_menu_selected', 0) or 0) + 1)
                except Exception:
                    client._menu_selected = 0
                return True

            if client._event_is_action(getattr(event, 'key', None), 'ui_confirm'):
                try:
                    btns = self.build_menu_buttons(client, str(view))
                    idx = int(getattr(client, '_menu_selected', 0) or 0)
                except Exception:
                    btns = []
                    idx = 0

                if view == 'enemy_select':
                    # Default: rubix3
                    client._start_match('rubix3', None)
                    return True

                if 0 <= idx < len(btns):
                    try:
                        client._ui_flash_button('menu', str(btns[idx].get('id')))
                    except Exception:
                        pass
                    self.on_menu_button(client, str(btns[idx].get('id')))
                    return True

                if view == 'main':
                    client._start_quickplay()
                    return True

            return False

        # --- Mouse click ---------------------------------------------
        if et == int(getattr(pygame, 'MOUSEBUTTONDOWN', -9999)) and int(getattr(event, 'button', 0) or 0) == 1:
            view = str(getattr(client, '_menu_view', 'main') or 'main')
            if view == 'story_char_select':
                cid = self.story_char_button_at(client, getattr(event, 'pos', (0, 0)))
                if cid:
                    client._start_story_intro_from_character(str(cid))
                return True

            if view == 'bot_battle':
                # Dropdown interactions take priority over sword selection.
                opt = self.bot_battle_dropdown_option_at(client, getattr(event, 'pos', (0, 0)))
                if opt is not None:
                    side, style = opt
                    style = str(style or '').strip().lower()
                    if str(side) == 'a':
                        try:
                            client._bot_battle_a_style = str(style)
                        except Exception:
                            pass
                        try:
                            lbl = client._fmt_bot_battle_style(style)
                        except Exception:
                            lbl = str(style)
                        self.set_menu_status(client, f"Bot A: {lbl}")
                    else:
                        try:
                            client._bot_battle_b_style = str(style)
                        except Exception:
                            pass
                        try:
                            lbl = client._fmt_bot_battle_style(style)
                        except Exception:
                            lbl = str(style)
                        self.set_menu_status(client, f"Bot B: {lbl}")
                    try:
                        client._bot_battle_dropdown_open = None
                    except Exception:
                        pass
                    return True

                hdr = self.bot_battle_dropdown_header_at(client, getattr(event, 'pos', (0, 0)))
                if hdr is not None:
                    try:
                        cur = str(getattr(client, '_bot_battle_dropdown_open', None) or '').strip().lower()
                    except Exception:
                        cur = ''
                    try:
                        client._bot_battle_dropdown_open = None if cur == str(hdr) else str(hdr)
                    except Exception:
                        pass
                    return True

                # Click outside while open closes dropdown. Only consume the click if it was
                # inside a sword grid (avoid accidental equips), but allow Start/Back clicks.
                try:
                    if str(getattr(client, '_bot_battle_dropdown_open', None) or '').strip().lower() in ('a', 'b'):
                        client._bot_battle_dropdown_open = None
                        try:
                            _p, _dd, sr_a = self.get_bot_battle_panel_inner_rects(client, 'left')
                            _p, _dd, sr_b = self.get_bot_battle_panel_inner_rects(client, 'right')
                            pos = getattr(event, 'pos', (0, 0))
                            if (sr_a is not None and sr_a.collidepoint(pos)) or (sr_b is not None and sr_b.collidepoint(pos)):
                                return True
                        except Exception:
                            return True
                except Exception:
                    pass

                hit = self.bot_battle_sword_tile_at(client, getattr(event, 'pos', (0, 0)))
                if hit is not None:
                    side, sword_value = hit
                    sword_value = str(sword_value or '').strip().lower()
                    if sword_value:
                        nm = client._friendly_sword_name(sword_value)
                        if str(side) == 'a':
                            try:
                                client._equipped_sword_value = str(sword_value)
                                client._persist_equipped_sword_preference()
                                client._apply_equipped_sword_to_session()
                            except Exception:
                                pass
                            self.set_menu_status(client, f"Bot A sword: {nm} (saved)")
                        else:
                            try:
                                client._enemy_sword_value = str(sword_value)
                                client._persist_enemy_sword_preference()
                                client._apply_enemy_sword_to_session()
                            except Exception:
                                pass
                            self.set_menu_status(client, f"Bot B sword: {nm} (saved)")
                    return True

            if view == 'enemy_select':
                hit = self.quickplay_sword_tile_at(client, getattr(event, 'pos', (0, 0)))
                if hit is not None:
                    side, sword_value = hit
                    sword_value = str(sword_value or '').strip().lower()
                    if sword_value:
                        nm = client._friendly_sword_name(sword_value)
                        if str(side) == 'a':
                            try:
                                client._equipped_sword_value = str(sword_value)
                                client._persist_equipped_sword_preference()
                                client._apply_equipped_sword_to_session()
                            except Exception:
                                pass
                            self.set_menu_status(client, f"{nm} (saved)")
                        else:
                            try:
                                client._enemy_sword_value = str(sword_value)
                                client._persist_enemy_sword_preference()
                                client._apply_enemy_sword_to_session()
                            except Exception:
                                pass
                            self.set_menu_status(client, f"{nm} (saved)")
                    return True

            bid = self.menu_button_at(client, getattr(event, 'pos', (0, 0)))
            if bid:
                try:
                    btns = self.build_menu_buttons(client, str(view))
                    for i, bb in enumerate(btns):
                        if str(bb.get('id')) == str(bid):
                            client._menu_selected = int(i)
                            break
                except Exception:
                    pass
                try:
                    client._ui_flash_button('menu', str(bid))
                except Exception:
                    pass
                self.on_menu_button(client, str(bid))
                return True

            return False

        # --- Mouse wheel ---------------------------------------------
        try:
            mw = getattr(pygame, 'MOUSEWHEEL', None)
        except Exception:
            mw = None

        if mw is not None and et == int(mw):
            view = str(getattr(client, '_menu_view', 'main') or 'main')

            if view == 'bot_battle':
                try:
                    mx, my = pygame.mouse.get_pos()
                    mpos = (int(mx), int(my))
                except Exception:
                    mpos = (0, 0)

                try:
                    ui_scale = float(getattr(client, 'ui_scale', 1.0) or 1.0)
                except Exception:
                    ui_scale = 1.0
                step = int(max(24, round(56 * ui_scale)))

                try:
                    lay_left = self.bot_battle_sword_layout(client, 'left')
                except Exception:
                    lay_left = None
                try:
                    lay_right = self.bot_battle_sword_layout(client, 'right')
                except Exception:
                    lay_right = None

                scroll_key = None
                max_scroll = 0
                try:
                    rr = (lay_left or {}).get('swords_rect')
                    if rr is not None and rr.collidepoint(mpos):
                        scroll_key = 'a'
                        max_scroll = int((lay_left or {}).get('max_scroll', 0) or 0)
                except Exception:
                    pass
                if scroll_key is None:
                    try:
                        rr = (lay_right or {}).get('swords_rect')
                        if rr is not None and rr.collidepoint(mpos):
                            scroll_key = 'b'
                            max_scroll = int((lay_right or {}).get('max_scroll', 0) or 0)
                    except Exception:
                        pass

                if scroll_key is not None:
                    try:
                        cur = int((getattr(client, '_bot_battle_sword_scroll_y', None) or {}).get(scroll_key, 0) or 0)
                    except Exception:
                        cur = 0
                    try:
                        wheel_y = int(getattr(event, 'y', 0) or 0)
                    except Exception:
                        wheel_y = 0

                    # pygame: wheel up => y=+1. We want that to scroll toward the top.
                    cur = int(cur - wheel_y * step)
                    cur = int(max(0, min(int(max_scroll), int(cur))))
                    try:
                        client._bot_battle_sword_scroll_y[str(scroll_key)] = int(cur)
                    except Exception:
                        pass

            if view == 'enemy_select':
                try:
                    mx, my = pygame.mouse.get_pos()
                    mpos = (int(mx), int(my))
                except Exception:
                    mpos = (0, 0)

                try:
                    ui_scale = float(getattr(client, 'ui_scale', 1.0) or 1.0)
                except Exception:
                    ui_scale = 1.0
                step = int(max(24, round(56 * ui_scale)))

                try:
                    lay_left = self.quickplay_sword_layout(client, 'left')
                except Exception:
                    lay_left = None
                try:
                    lay_right = self.quickplay_sword_layout(client, 'right')
                except Exception:
                    lay_right = None

                scroll_key = None
                max_scroll = 0
                try:
                    rr = (lay_left or {}).get('swords_rect')
                    if rr is not None and rr.collidepoint(mpos):
                        scroll_key = 'a'
                        max_scroll = int((lay_left or {}).get('max_scroll', 0) or 0)
                except Exception:
                    pass
                if scroll_key is None:
                    try:
                        rr = (lay_right or {}).get('swords_rect')
                        if rr is not None and rr.collidepoint(mpos):
                            scroll_key = 'b'
                            max_scroll = int((lay_right or {}).get('max_scroll', 0) or 0)
                    except Exception:
                        pass

                if scroll_key is not None:
                    try:
                        cur = int((getattr(client, '_quickplay_sword_scroll_y', None) or {}).get(scroll_key, 0) or 0)
                    except Exception:
                        cur = 0
                    try:
                        wheel_y = int(getattr(event, 'y', 0) or 0)
                    except Exception:
                        wheel_y = 0

                    cur = int(cur - wheel_y * step)
                    cur = int(max(0, min(int(max_scroll), int(cur))))
                    try:
                        client._quickplay_sword_scroll_y[str(scroll_key)] = int(cur)
                    except Exception:
                        pass

            return True

        return False

    def build_menu_buttons(self, client: Any, view: str) -> list[dict]:
        w = int(client.screen.get_width())

        btn = getattr(client, '_menu_button_scaled', None)
        if btn is not None:
            bw, bh = int(btn.get_width()), int(btn.get_height())
        else:
            bw, bh = int(min(w * 0.34, 520)), 84
            bw = max(220, int(bw))
            bh = max(60, int(bh))

        gap = max(12, int(round(bh * 0.24)))

        try:
            view_norm = str(view or 'main').strip().lower()
        except Exception:
            view_norm = 'main'

        safe_top, safe_bottom_y = self.get_menu_safe_bounds(client, str(view_norm))

        bot_battle_mid = None
        enemy_select_mid = None
        if view_norm == 'bot_battle':
            try:
                _lp, _rp, bot_battle_mid = self.get_bot_battle_sword_panel_rects(client)
            except Exception:
                bot_battle_mid = None
        if view_norm == 'enemy_select':
            try:
                _lp, _rp, enemy_select_mid = self.get_quickplay_sword_panel_rects(client)
            except Exception:
                enemy_select_mid = None

        if view_norm == 'options':
            items = [
                {'id': 'controls', 'label': 'Controls'},
                {'id': 'toggle_sfx', 'label': 'SFX: ' + ('On' if bool(getattr(client, '_sfx_enabled', True)) else 'Off')},
                {'id': 'toggle_fullscreen', 'label': 'Fullscreen: ' + ('On' if bool(getattr(client, '_fullscreen_enabled', False)) else 'Off')},
                {'id': 'vol_down', 'label': 'Volume -'},
                {'id': 'vol_up', 'label': 'Volume +'},
                {'id': 'hmove_slower', 'label': f"Move Repeat: {int(getattr(client, '_horizontal_move_repeat_ms', 70) or 70)} ms (Slower)"},
                {'id': 'hmove_faster', 'label': f"Move Repeat: {int(getattr(client, '_horizontal_move_repeat_ms', 70) or 70)} ms (Faster)"},
                {'id': 'save_settings', 'label': 'Save Settings'},
                {'id': 'back', 'label': 'Back'},
            ]
        elif view_norm == 'controls':
            pairs = [
                ('move_left', 'Move Left'),
                ('move_right', 'Move Right'),
                ('rotate_ccw', 'Rotate CCW'),
                ('rotate_cw', 'Rotate CW'),
                ('fast_fall', 'Fast Fall'),
                ('pause', 'Pause / Resume'),
                ('ui_up', 'Menu Up'),
                ('ui_down', 'Menu Down'),
                ('ui_confirm', 'Menu Confirm'),
                ('ui_back', 'Menu Back'),
            ]
            items = []
            for act, label in pairs:
                items.append({'id': f"bind:{act}", 'label': f"{label}: {client._format_action_keys(act)}"})
            items.extend([
                {'id': 'reset_controls', 'label': 'Reset Controls to Defaults'},
                {'id': 'back', 'label': 'Back'},
            ])
        elif view_norm == 'enemy_select':
            items = [
                {'id': 'rubix3', 'label': 'Rubix 3 (Boards)'},
                {'id': 'rubix4', 'label': 'Rubix 4 (Boards)'},
                {'id': 'rubix5', 'label': 'Rubix 5 (Boards)'},
                {'id': 'rubix6', 'label': 'Rubix 6 (Boards)'},
                {'id': 'boss', 'label': 'Boss Cube (HP + Attacks)'},
                {'id': 'mirror', 'label': 'Mirror Cube (Invincible)'},
                {'id': 'back', 'label': 'Back'},
            ]
        elif view_norm == 'enemy_pattern':
            items = []
            try:
                selected = str(getattr(client, '_enemy_sword_value', 'rusty_sword') or 'rusty_sword').strip().lower()
            except Exception:
                selected = 'rusty_sword'
            try:
                for st in get_available_swords():
                    nm = client._friendly_sword_name(str(getattr(st, 'value', st) or st))
                    tag = ' (Selected)' if str(getattr(st, 'value', '') or '').strip().lower() == selected else ''
                    items.append({'id': f"enemy_sword:{st.value}", 'label': f"{nm}{tag}"})
            except Exception:
                pass
            items.append({'id': 'back', 'label': 'Back'})
        elif view_norm == 'inventory':
            items = []
            try:
                equipped = str(getattr(client, '_equipped_sword_value', 'rusty_sword') or 'rusty_sword').strip().lower()
            except Exception:
                equipped = 'rusty_sword'
            try:
                for st in get_available_swords():
                    nm = client._friendly_sword_name(str(getattr(st, 'value', st) or st))
                    tag = ' (Equipped)' if str(getattr(st, 'value', '') or '').strip().lower() == equipped else ''
                    items.append({'id': f"sword:{st.value}", 'label': f"{nm}{tag}"})
            except Exception:
                pass
            items.append({'id': 'back', 'label': 'Back'})
        elif view_norm == 'bot_battle':
            # Bot selections are handled via the per-panel dropdowns above the swords.
            items = [
                {'id': 'start_bot_battle', 'label': 'Start Battle'},
                {'id': 'back', 'label': 'Back'},
            ]
        else:
            items = [
                {'id': 'quickplay', 'label': 'Quick Play'},
                {'id': 'story', 'label': 'Story Mode'},
                {'id': 'strike_test', 'label': 'Strike Test'},
                {'id': 'bot_battle', 'label': 'Battle of the Bots'},
                {'id': 'inventory', 'label': 'Inventory (Swords)'},
                {'id': 'multiplayer', 'label': 'Multiplayer'},
                {'id': 'options', 'label': 'Options'},
                {'id': 'exit', 'label': 'Exit Game'},
            ]

        total_h = len(items) * bh + max(0, len(items) - 1) * gap
        available_h = int(max(0, safe_bottom_y - safe_top))
        if total_h > available_h and available_h > 0:
            scale = float(available_h) / float(max(1, total_h))
            # Keep buttons usable/clickable even in small windows.
            bh = max(44, int(round(float(bh) * scale)))
            bw = max(200, int(round(float(bw) * scale)))
            gap = max(6, int(round(float(gap) * scale)))
            total_h = len(items) * bh + max(0, len(items) - 1) * gap

        start_y = int(safe_top + max(0, (available_h - total_h) / 2))
        if start_y < safe_top:
            start_y = int(safe_top)

        bx = int((w - bw) / 2)
        if view_norm == 'bot_battle' and bot_battle_mid is not None:
            try:
                bx = int(bot_battle_mid.x + (int(bot_battle_mid.w) - int(bw)) / 2)
            except Exception:
                bx = int((w - bw) / 2)
        if view_norm == 'enemy_select' and enemy_select_mid is not None:
            try:
                bx = int(enemy_select_mid.x + (int(enemy_select_mid.w) - int(bw)) / 2)
            except Exception:
                bx = int((w - bw) / 2)

        out: list[dict] = []
        for i, it in enumerate(items):
            by = int(start_y + i * (bh + gap))
            out.append({'id': str(it['id']), 'label': str(it['label']), 'rect': pygame.Rect(bx, by, bw, bh)})
        return out



    def enter_pause(self, client: Any) -> None:
        # Freeze the current frame so the pause overlay sits on top.
        client.state = 'pause'
        client._pause_view = 'main'
        client._pause_status_text = ''
        try:
            client._pause_selected = int(getattr(client, '_pause_selected', 0) or 0)
        except Exception:
            client._pause_selected = 0
        client._pause_buttons = []
        try:
            if getattr(client, '_last_snapshot', None) is None:
                client._last_snapshot = client.session.snapshot()
        except Exception:
            pass

    def pause_action(self, client: Any, action_id: str) -> None:
        aid = (action_id or '').strip().lower()
        if aid == 'options':
            client._pause_view = 'options'
            client._pause_selected = 0
            client._pause_buttons = []
            return
        if aid == 'back':
            client._pause_view = 'main'
            client._pause_selected = 0
            client._pause_buttons = []
        if aid == 'toggle_fullscreen':
            try:
                client._set_fullscreen_enabled(not bool(getattr(client, '_fullscreen_enabled', False)), persist=True)
                client._pause_status_text = 'Fullscreen ' + ('enabled' if bool(getattr(client, '_fullscreen_enabled', False)) else 'disabled') + ' (saved)'
            except Exception:
                client._pause_status_text = 'Failed to toggle fullscreen'
            client._pause_buttons = []
            return
        if aid == 'vol_down':
            client._set_sfx_volume(float(getattr(client, '_sfx_volume', 0.65) or 0.65) - 0.05)
            try:
                client._persist_volume_preference()
            except Exception:
                pass
            client._pause_status_text = f"Volume: {int(round(float(client._sfx_volume) * 100.0))}% (saved)"
            client._pause_buttons = []
            return
        if aid == 'vol_up':
            client._pause_buttons = []
            return
        if aid == 'hmove_faster':
            client._set_horizontal_move_repeat_ms(int(getattr(client, '_horizontal_move_repeat_ms', 70) or 70) - 10)
            try:
                client._persist_volume_preference()
            except Exception:
                pass
            client._pause_status_text = f"Horizontal move repeat: {int(getattr(client, '_horizontal_move_repeat_ms', 70) or 70)} ms (saved)"
            client._pause_buttons = []
            return
        if aid == 'hmove_slower':
            client._set_horizontal_move_repeat_ms(int(getattr(client, '_horizontal_move_repeat_ms', 70) or 70) + 10)
            try:
                client._persist_volume_preference()
            except Exception:
                pass
            client._pause_status_text = f"Horizontal move repeat: {int(getattr(client, '_horizontal_move_repeat_ms', 70) or 70)} ms (saved)"
            client._pause_buttons = []
            return
        if aid == 'save_settings':
            try:
                client._persist_volume_preference()
                client._pause_status_text = 'Settings saved'
            except Exception:
                client._pause_status_text = 'Failed to save settings'
            client._pause_buttons = []
            return

        if aid == 'resume':
            client.state = 'game'
            try:
                client._pause_buttons = []
            except Exception:
                pass
            return
        if aid == 'menu':
            client.state = 'menu'
            client._menu_view = 'main'
            self.set_menu_status(client, '')
            client._last_snapshot = None
            try:
                client._pause_buttons = []
            except Exception:
                pass
            return
        if aid == 'exit':
            client.running = False
            return

    def postgame_action(self, client: Any, action_id: str) -> None:
        aid = (action_id or '').strip().lower()
        if aid == 'replay':
            client._reset_session()
            client.state = 'game'
            return
        if aid == 'enemy_select':
            client.state = 'menu'
            client._menu_view = 'enemy_select'
            self.set_menu_status(client, '')
            client._last_snapshot = None
            return
        if aid == 'menu':
            client.state = 'menu'
            client._menu_view = 'main'
            self.set_menu_status(client, '')
            client._last_snapshot = None
            return

    def build_postgame_buttons(self, client: Any) -> list[dict]:
        w = int(client.screen.get_width())
        h = int(client.screen.get_height())

        # Desired button size (may be clamped to fit the available side area).
        btn = getattr(client, '_menu_button_scaled', None)
        if btn is not None:
            bw, bh = int(btn.get_width()), int(btn.get_height())
        else:
            bw, bh = int(min(w * 0.34, 520)), 84
            bw = max(220, int(bw))
            bh = max(60, int(bh))

        gap = max(12, int(round(bh * 0.28)))
        total_h = 3 * bh + 2 * gap

        # Postgame UI is drawn in a right-side panel so the boards remain visible.
        try:
            ui_scale = float(getattr(client, 'ui_scale', 1.0) or 1.0)
        except Exception:
            ui_scale = 1.0
        side_margin = int(max(12, round(18 * ui_scale)))
        pad = int(max(10, round(14 * ui_scale)))

        # Start the postgame panel at the right edge of the rightmost board so it never covers the boards.
        try:
            board_right = int(getattr(client, 'player_offset_x', 0) + getattr(client, 'board_px_w', 0))
        except Exception:
            board_right = int(w * 0.60)
        try:
            enemy_has_board = bool(getattr(getattr(client, 'session', None), 'enemy_has_board', True))
        except Exception:
            enemy_has_board = True
        try:
            if bool(getattr(getattr(client, 'session', None), 'ai', None) is not None):
                if enemy_has_board:
                    board_right = max(int(board_right), int(getattr(client, 'enemy_offset_x', 0) + getattr(client, 'board_px_w', 0)))
                else:
                    board_right = max(int(board_right), int(getattr(client, 'enemy_offset_x', 0) + getattr(client, 'enemy_panel_px_w', 0)))
        except Exception:
            pass

        panel_x = int(max(0, min(int(w - side_margin - 1), int(board_right))))
        panel_w = int(max(160, int(w - side_margin - panel_x)))

        # Clamp button width to fit within the side panel; images will be scaled at draw time.
        bw = int(min(int(bw), int(max(140, panel_w - 2 * pad))))
        bx = int(panel_x + (panel_w - bw) / 2)
        start_y = int(h * 0.62 - total_h / 2)

        return [
            {'id': 'replay', 'label': 'Replay', 'rect': pygame.Rect(bx, int(start_y), bw, bh)},
            {'id': 'enemy_select', 'label': 'Enemy Select', 'rect': pygame.Rect(bx, int(start_y + bh + gap), bw, bh)},
            {'id': 'menu', 'label': 'Main Menu', 'rect': pygame.Rect(bx, int(start_y + 2 * (bh + gap)), bw, bh)},
        ]

    def build_pause_buttons(self, client: Any) -> list[dict]:
        w = int(client.screen.get_width())
        h = int(client.screen.get_height())

        btn = getattr(client, '_menu_button_scaled', None)
        if btn is not None:
            bw, bh = int(btn.get_width()), int(btn.get_height())
        else:
            bw, bh = int(min(w * 0.34, 520)), 84
            bw = max(220, int(bw))
            bh = max(60, int(bh))

        gap = max(12, int(round(bh * 0.24)))
        bx = int((w - bw) / 2)

        view = str(getattr(client, '_pause_view', 'main') or 'main')
        if view == 'options':
            items = [
                {'id': 'toggle_sfx', 'label': 'SFX: ' + ('On' if bool(getattr(client, '_sfx_enabled', True)) else 'Off')},
                {'id': 'toggle_fullscreen', 'label': 'Fullscreen: ' + ('On' if bool(getattr(client, '_fullscreen_enabled', False)) else 'Off')},
                {'id': 'vol_down', 'label': 'Volume -'},
                {'id': 'vol_up', 'label': 'Volume +'},
                {'id': 'hmove_slower', 'label': f"Move Repeat: {int(getattr(client, '_horizontal_move_repeat_ms', 70) or 70)} ms (Slower)"},
                {'id': 'hmove_faster', 'label': f"Move Repeat: {int(getattr(client, '_horizontal_move_repeat_ms', 70) or 70)} ms (Faster)"},
                {'id': 'save_settings', 'label': 'Save Settings'},
                {'id': 'back', 'label': 'Back'},
            ]
        else:
            items = [
                {'id': 'resume', 'label': 'Resume'},
                {'id': 'options', 'label': 'Options'},
                {'id': 'menu', 'label': 'Main Menu'},
                {'id': 'exit', 'label': 'Exit Game'},
            ]

        total_h = len(items) * bh + max(0, len(items) - 1) * gap
        start_y = int(h * 0.58 - total_h / 2)

        out: list[dict] = []
        for i, it in enumerate(items):
            by = int(start_y + i * (bh + gap))
            out.append({'id': str(it['id']), 'label': str(it['label']), 'rect': pygame.Rect(bx, by, bw, bh)})
        return out

    def postgame_button_at(self, client: Any, pos) -> int | None:
        try:
            x, y = int(pos[0]), int(pos[1])
        except Exception:
            return None
        for i, b in enumerate(getattr(client, '_postgame_buttons', []) or []):
            rect = b.get('rect', None)
            if rect is not None and rect.collidepoint((x, y)):
                return int(i)
        return None

    def pause_button_at(self, client: Any, pos) -> int | None:
        try:
            x, y = int(pos[0]), int(pos[1])
        except Exception:
            return None
        for i, b in enumerate(getattr(client, '_pause_buttons', []) or []):
            rect = b.get('rect', None)
            if rect is not None and rect.collidepoint((x, y)):
                return int(i)
        return None

    def draw_postgame_prompt(self, client: Any) -> None:
        # Right-side postgame panel (do not cover the boards).
        try:
            w, h = int(client.screen.get_width()), int(client.screen.get_height())
        except Exception:
            return

        try:
            ui_scale = float(getattr(client, 'ui_scale', 1.0) or 1.0)
        except Exception:
            ui_scale = 1.0
        side_margin = int(max(12, round(18 * ui_scale)))
        pad = int(max(10, round(14 * ui_scale)))

        # Approx button height reserve (score/labels should not overlap buttons).
        # The exact button rects are built later; this is a safe estimate.
        try:
            bh = int(max(60, round(84 * ui_scale)))
        except Exception:
            bh = 84

        # Determine the right edge of the rightmost board, so the panel doesn't cover it.
        try:
            board_right = int(getattr(client, 'player_offset_x', 0) + getattr(client, 'board_px_w', 0))
        except Exception:
            board_right = int(w * 0.60)
        try:
            enemy_has_board = bool(getattr(getattr(client, 'session', None), 'enemy_has_board', True))
        except Exception:
            enemy_has_board = True
        try:
            if bool(getattr(getattr(client, 'session', None), 'ai', None) is not None):
                if enemy_has_board:
                    board_right = max(int(board_right), int(getattr(client, 'enemy_offset_x', 0) + getattr(client, 'board_px_w', 0)))
                else:
                    board_right = max(int(board_right), int(getattr(client, 'enemy_offset_x', 0) + getattr(client, 'enemy_panel_px_w', 0)))
        except Exception:
            pass

        panel_x = int(max(0, min(int(w - side_margin - 1), int(board_right))))
        panel_w = int(max(160, int(w - side_margin - panel_x)))
        panel_y = int(h * 0.10)
        panel_h = int(h * 0.82)

        # Preserve the outer panel geometry for later layout calculations.
        outer_x, outer_y, outer_w, outer_h = int(panel_x), int(panel_y), int(panel_w), int(panel_h)

        try:
            overlay = pygame.Surface((int(panel_w), int(panel_h)), flags=pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 165))
            client.screen.blit(overlay, (panel_x, panel_y))
            pygame.draw.rect(client.screen, (255, 255, 255), pygame.Rect(panel_x, panel_y, panel_w, panel_h), width=2, border_radius=12)
        except Exception:
            pass

        # Title
        try:
            res = str(getattr(client, '_postgame_result', 'win') or 'win').strip().lower()
        except Exception:
            res = 'win'
        title_txt = 'Victory!' if res == 'win' else 'Defeat'
        try:
            font = pygame.font.SysFont(None, max(26, int(round(64 * float(getattr(client, 'ui_scale', 1.0) or 1.0)))))
            title = font.render(title_txt, True, (255, 255, 255))
            tx = int(panel_x + panel_w / 2 - title.get_width() / 2)
            ty = int(panel_y + max(10, round(14 * ui_scale)))
            client.screen.blit(title, (tx, ty))
        except Exception:
            pass

        # Score breakdown + gold payout
        try:
            bd = getattr(client, '_postgame_breakdown', None) or {}
        except Exception:
            bd = {}

        if not bd:
            try:
                snap = getattr(client, '_last_snapshot', None) or client.session.snapshot()
                p_score = ((snap.get('scoring', {}) or {}).get('player', {}) or {})
                pts = int(p_score.get('points_total', 0) or 0)
                clears = int(p_score.get('clears_total', 0) or 0)
                mx = int(p_score.get('max_chain', 0) or 0)
                bd = {'points': pts, 'gold_earned': max(0, pts), 'clears_total': clears, 'max_chain': mx}
            except Exception:
                bd = {}

        try:
            pad = int(max(10, round(14 * float(getattr(client, 'ui_scale', 1.0) or 1.0))))
            gap = int(max(2, round(6 * float(getattr(client, 'ui_scale', 1.0) or 1.0))))

            lines = [
                f"Score: {int(bd.get('points', 0) or 0)}",
                f"Blocks Cleared: {int(bd.get('clears_total', 0) or 0)}",
                f"Max Combo: {int(bd.get('max_chain', 0) or 0)}x",
                f"Gold Earned: +{int(bd.get('gold_earned', 0) or 0)}",
            ]
            rendered = [client.ui_font.render(t, True, (245, 245, 245)) for t in lines]
            score_w = max(r.get_width() for r in rendered) + 2 * pad
            score_h = sum(r.get_height() for r in rendered) + (len(rendered) - 1) * gap + 2 * pad

            # Clamp within the outer panel, and center.
            max_score_w = max(120, int(outer_w - 2 * pad))
            score_w = min(int(score_w), int(max_score_w))
            score_x = int(outer_x + (outer_w - score_w) / 2)
            score_y = int(outer_y + max(80, int(round(110 * ui_scale))))
            # Prevent the score box from overlapping the bottom buttons.
            score_y = min(int(score_y), int(outer_y + outer_h - score_h - int(round(3.5 * bh))))

            score_panel = pygame.Surface((int(score_w), int(score_h)), flags=pygame.SRCALPHA)
            score_panel.fill((0, 0, 0, 165))
            client.screen.blit(score_panel, (score_x, score_y))
            pygame.draw.rect(client.screen, (255, 255, 255), pygame.Rect(score_x, score_y, score_w, score_h), width=2, border_radius=12)

            yy = int(score_y + pad)
            for r in rendered:
                client.screen.blit(r, (int(score_x + pad), yy))
                yy += int(r.get_height() + gap)
        except Exception:
            pass

        # Buttons
        if not getattr(client, '_postgame_buttons', None):
            client._postgame_buttons = self.build_postgame_buttons(client)

        btn_img_normal = getattr(client, '_menu_button_scaled', None)
        btn_img_hover = getattr(client, '_menu_button_hover_scaled', None) or btn_img_normal
        btn_img_pressed = getattr(client, '_menu_button_pressed_scaled', None) or btn_img_hover or btn_img_normal
        icon_replay = getattr(client, '_menu_icon_gamepad_scaled', None)
        icon_menu = getattr(client, '_menu_icon_gear_scaled', None)

        try:
            _label_font = pygame.font.SysFont(None, max(18, int(round(44 * float(getattr(client, 'ui_scale', 1.0) or 1.0)))))
        except Exception:
            _label_font = client.ui_font

        sel = int(getattr(client, '_postgame_selected', 0) or 0)

        try:
            mouse_pos = pygame.mouse.get_pos()
        except Exception:
            mouse_pos = (0, 0)
        try:
            mouse_down = bool(pygame.mouse.get_pressed()[0])
        except Exception:
            mouse_down = False

        for i, b in enumerate(client._postgame_buttons):
            rect = b.get('rect')
            if rect is None:
                continue

            hovered = False
            try:
                hovered = bool(rect.collidepoint(mouse_pos))
            except Exception:
                hovered = False
            pressed = bool(mouse_down and hovered)
            try:
                if client._ui_is_button_flashed('postgame', str(b.get('id'))):
                    pressed = True
            except Exception:
                pass

            # Draw the button (must be inside the loop; otherwise only the last one renders).
            # Scale menu button images to the rect size (postgame panel can be narrow).
            src_normal = btn_img_normal
            src_hover = btn_img_hover
            src_pressed = btn_img_pressed
            try:
                if btn_img_normal is not None:
                    tw, th = int(rect.width), int(rect.height)
                    cache = getattr(client, '_postgame_button_img_cache', None)
                    if cache is None:
                        cache = {}
                        client._postgame_button_img_cache = cache
                    key = (tw, th)
                    if key not in cache:
                        cache[key] = {
                            'normal': pygame.transform.smoothscale(btn_img_normal, (tw, th)),
                            'hover': pygame.transform.smoothscale(btn_img_hover, (tw, th)) if btn_img_hover is not None else None,
                            'pressed': pygame.transform.smoothscale(btn_img_pressed, (tw, th)) if btn_img_pressed is not None else None,
                        }
                    entry = cache.get(key) or {}
                    src_normal = entry.get('normal', btn_img_normal)
                    src_hover = entry.get('hover', btn_img_hover) or src_normal
                    src_pressed = entry.get('pressed', btn_img_pressed) or src_hover
            except Exception:
                src_normal = btn_img_normal
                src_hover = btn_img_hover
                src_pressed = btn_img_pressed

            if src_normal is None:
                pygame.draw.rect(client.screen, (40, 40, 60), rect, border_radius=12)
                pygame.draw.rect(
                    client.screen,
                    (220, 220, 240) if i == sel else (160, 160, 190),
                    rect,
                    width=3 if i == sel else 2,
                    border_radius=12,
                )
            else:
                src = src_pressed if pressed else (src_hover if (hovered or i == sel) else src_normal)
                client.screen.blit(src, (int(rect.x), int(rect.y)))
                if i == sel:
                    pygame.draw.rect(client.screen, (255, 255, 255), rect, width=3, border_radius=12)

            # Icon + label
            icon = icon_replay if str(b.get('id')) == 'replay' else icon_menu
            btn_pad = max(10, int(round(rect.height * 0.16)))
            ix = rect.x + btn_pad
            if icon is not None:
                try:
                    iy = int(rect.centery - icon.get_height() / 2)
                    client.screen.blit(icon, (int(ix), int(iy)))
                    text_x = int(ix + icon.get_width() + btn_pad)
                except Exception:
                    text_x = None
            else:
                text_x = None

            try:
                if text_x is None:
                    client._blit_fitted_text(
                        str(b.get('label', '')),
                        rect,
                        color=(255, 255, 255),
                        pad=btn_pad,
                        base_px=max(18, int(round(44 * ui_scale))),
                        max_lines=2,
                    )
                else:
                    client._blit_fitted_text(
                        str(b.get('label', '')),
                        rect,
                        color=(255, 255, 255),
                        pad=btn_pad,
                        x=int(text_x),
                        align='left',
                        base_px=max(18, int(round(44 * ui_scale))),
                        max_lines=2,
                    )
            except Exception:
                pass

        # Defeat reason debug (helps diagnose "unfair defeat" reports).
        try:
            snap = getattr(client, '_last_snapshot', None) or client.session.snapshot()
        except Exception:
            snap = {}

        def _fmt_reason(side_label: str, reason: str | None, ctx: dict | None) -> str | None:
            r = str(reason or '').strip().lower()
            if not r:
                return None
            c = dict(ctx or {})

            # Keep this compact; avoid dumping huge payloads.
            extra = ''
            try:
                if r == 'game_over_column_full':
                    col = c.get('col_1b', None)
                    if col is not None:
                        extra = f" (col {int(col)})"
                elif r == 'spawn_overlap':
                    cells = c.get('cells', None)
                    if isinstance(cells, list) and cells:
                        shown = cells[:3]
                        extra = f" (cells {shown}{'…' if len(cells) > 3 else ''})"
                elif r == 'inbound_overflow':
                    parts: list[str] = []
                    ph = c.get('phase', None)
                    if ph:
                        parts.append(str(ph))
                    try:
                        k = c.get('kind', None)
                        if k:
                            parts.append(str(k))
                    except Exception:
                        pass
                    try:
                        cid = c.get('cluster_id', None)
                        if cid is not None:
                            parts.append(f"cid={int(cid)}")
                    except Exception:
                        pass
                    try:
                        w = c.get('width', None)
                        h = c.get('height', None)
                        if w is not None and h is not None:
                            parts.append(f"{int(w)}x{int(h)}")
                    except Exception:
                        pass
                    try:
                        cols = c.get('cols', None)
                        if isinstance(cols, list) and cols:
                            shown = cols[:4]
                            parts.append(f"cols {shown}{'…' if len(cols) > 4 else ''}")
                    except Exception:
                        pass
                    try:
                        my = c.get('min_y', None)
                        if my is not None:
                            parts.append(f"min_y={int(my)}")
                    except Exception:
                        pass
                    if parts:
                        extra = f" ({' '.join(parts)})"
                elif r == 'top_row_full':
                    extra = " (row 0)"
            except Exception:
                extra = ''

            return f"{side_label}: {r}{extra}"

        try:
            p = (snap.get('player', {}) or {})
        except Exception:
            p = {}
        try:
            a = (snap.get('ai', {}) or {})
        except Exception:
            a = {}

        lines: list[str] = []
        try:
            try:
                dm = str(os.getenv('BF_DEFEAT_MODE', '') or '').strip().lower()
            except Exception:
                dm = ''
            if dm:
                lines.append(f"mode={dm}")
            pr = _fmt_reason('You', p.get('defeat_reason', None), p.get('defeat_context', None))
            ar = _fmt_reason('Enemy', a.get('defeat_reason', None), a.get('defeat_context', None))
            if pr:
                lines.append(pr)
            if ar:
                lines.append(ar)
        except Exception:
            lines = []

        if lines:
            try:
                header = client.ui_font.render('Defeat reason', True, (235, 235, 235))
                rendered = [client.ui_font.render(t, True, (220, 220, 220)) for t in lines]
                gap2 = int(max(2, round(5 * ui_scale)))

                hint_h = 0
                try:
                    hint_h = int(client.ui_font.get_height())
                except Exception:
                    hint_h = 18

                total_h = int(header.get_height() + gap2 + sum(r.get_height() for r in rendered) + max(0, len(rendered) - 1) * gap2)
                x0 = int(outer_x + pad)
                y0 = int(outer_y + outer_h - pad - hint_h - gap2 - total_h)
                y0 = max(int(outer_y + pad), int(y0))

                client.screen.blit(header, (x0, y0))
                yy = int(y0 + header.get_height() + gap2)
                for r in rendered:
                    client.screen.blit(r, (x0, yy))
                    yy += int(r.get_height() + gap2)
            except Exception:
                pass

        # Hint
        try:
            hint = client.ui_font.render('Enter=Select   Esc=Main Menu', True, (230, 230, 230))
            hx = int(outer_x + pad)
            hy = int(outer_y + outer_h - hint.get_height() - pad)
            client.screen.blit(hint, (hx, hy))
        except Exception:
            pass

    def draw_pause_prompt(self, client: Any) -> None:
        # Dim overlay
        try:
            w, h = int(client.screen.get_width()), int(client.screen.get_height())
            overlay = pygame.Surface((w, h), flags=pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 165))
            client.screen.blit(overlay, (0, 0))
        except Exception:
            pass

        w = int(client.screen.get_width())
        h = int(client.screen.get_height())

        view = str(getattr(client, '_pause_view', 'main') or 'main')

        # Title
        try:
            title_txt = 'Options' if view == 'options' else 'Paused'
            title = client._menu_title_font.render(title_txt, True, (245, 245, 245))
            client.screen.blit(title, (int((w - title.get_width()) / 2), int(h * 0.20)))
        except Exception:
            pass

        if not getattr(client, '_pause_buttons', None):
            client._pause_buttons = self.build_pause_buttons(client)

        btn_img_normal = getattr(client, '_menu_button_scaled', None)
        btn_img_hover = getattr(client, '_menu_button_hover_scaled', None) or btn_img_normal
        btn_img_pressed = getattr(client, '_menu_button_pressed_scaled', None) or btn_img_hover or btn_img_normal

        sel = int(getattr(client, '_pause_selected', 0) or 0)

        try:
            mouse_pos = pygame.mouse.get_pos()
        except Exception:
            mouse_pos = (0, 0)
        try:
            mouse_down = bool(pygame.mouse.get_pressed()[0])
        except Exception:
            mouse_down = False

        for i, b in enumerate(client._pause_buttons):
            rect = b.get('rect')
            if rect is None:
                continue

            hovered = False
            try:
                hovered = bool(rect.collidepoint(mouse_pos))
            except Exception:
                hovered = False
            pressed = bool(mouse_down and hovered)
            try:
                if client._ui_is_button_flashed('pause', str(b.get('id'))):
                    pressed = True
            except Exception:
                pass

            if btn_img_normal is None:
                pygame.draw.rect(client.screen, (40, 40, 60), rect, border_radius=12)
                pygame.draw.rect(client.screen, (180, 180, 200), rect, width=2, border_radius=12)
            else:
                src = btn_img_pressed if pressed else (btn_img_hover if (hovered or i == sel) else btn_img_normal)
                client.screen.blit(src, (int(rect.x), int(rect.y)))

            # Selection outline
            if i == sel:
                try:
                    pygame.draw.rect(
                        client.screen,
                        (255, 220, 120),
                        rect,
                        width=max(2, int(round(3 * float(getattr(client, 'ui_scale', 1.0) or 1.0)))),
                        border_radius=12,
                    )
                except Exception:
                    pass

            try:
                client._blit_fitted_text(
                    str(b.get('label', '')),
                    rect,
                    color=(255, 255, 255),
                    base_px=int(getattr(client, '_menu_button_font_px', 40) or 40),
                    max_lines=2,
                )
            except Exception:
                pass

        # Hint
        try:
            hint_txt = 'P/Esc = Back   Enter/Click = Select' if view == 'options' else 'P/Esc = Resume   Enter/Click = Select'
            hint = client.ui_font.render(hint_txt, True, (230, 230, 230))
            client.screen.blit(hint, (int(w * 0.06), int(h * 0.14)))
        except Exception:
            pass

        # Status
        try:
            st = str(getattr(client, '_pause_status_text', '') or '').strip()
            if st:
                status = client.ui_font.render(st, True, (240, 240, 200))
                client.screen.blit(status, (int(w * 0.06), int(h * 0.90)))
        except Exception:
            pass
