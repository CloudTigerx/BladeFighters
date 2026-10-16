from __future__ import annotations

from typing import Any

from swordfighting_new.attacks.garbage_pattern import SwordType, SWORD_PATTERNS


class MenuRenderController:
    def __init__(self, *, pygame: Any):
        self._pygame = pygame

    def draw_menu_view(self, client: Any, view, *, color_map: dict) -> None:
        # Background
        try:
            # Rebuild scaled assets if needed or if the screen size changed.
            w0 = int(client.screen.get_width())
            h0 = int(client.screen.get_height())
            last = getattr(client, '_menu_last_size', None)
            if last is None or tuple(last) != (w0, h0):
                client._rebuild_menu_scaled_assets()

            bg = getattr(client, '_menu_bg_scaled', None)
            try:
                # If something accidentally stuffed a non-Surface here, discard it.
                if bg is not None and (not isinstance(bg, self._pygame.Surface)):
                    bg = None
                    client._menu_bg_scaled = None
            except Exception:
                bg = getattr(client, '_menu_bg_scaled', None)

            if bg is None:
                client._rebuild_menu_scaled_assets()
                bg = getattr(client, '_menu_bg_scaled', None)

            if bg is not None:
                try:
                    client.screen.blit(bg, (0, 0))
                except Exception:
                    try:
                        client.screen.fill((10, 10, 18))
                    except Exception:
                        return
            else:
                try:
                    client.screen.fill((10, 10, 18))
                except Exception:
                    return
        except Exception:
            try:
                client.screen.fill((10, 10, 18))
            except Exception:
                return

        w = int(client.screen.get_width())
        h = int(client.screen.get_height())

        view = view if view is not None else getattr(client, '_menu_view', 'main')

        # Story placeholder character select screen (black background)
        if str(view) == 'story_char_select':
            try:
                client.screen.fill((0, 0, 0))
            except Exception:
                pass

            try:
                title = client._menu_title_font.render('Choose Character', True, (245, 245, 245))
                client.screen.blit(title, (int((w - title.get_width()) / 2), int(h * 0.10)))
            except Exception:
                pass

            if not getattr(client, '_story_char_buttons', None):
                client._story_char_buttons = client._build_story_character_buttons()

            try:
                for b in client._story_char_buttons:
                    rect = b.get('rect')
                    rgba = b.get('rgba')
                    if rect is None or rgba is None:
                        continue
                    tile = self._pygame.Surface((int(rect.w), int(rect.h)), flags=self._pygame.SRCALPHA)
                    tile.fill(tuple(rgba))
                    client.screen.blit(tile, (int(rect.x), int(rect.y)))
                    self._pygame.draw.rect(client.screen, (255, 255, 255), rect, width=2, border_radius=8)
            except Exception:
                pass

            try:
                hint = client.ui_font.render('Click a square (placeholder). Esc/P = Pause menu', True, (230, 230, 230))
                client.screen.blit(hint, (int(w * 0.06), int(h * 0.18)))
            except Exception:
                pass

            try:
                st = str(getattr(client, '_menu_status_text', '') or '').strip()
                if st:
                    status = client.ui_font.render(st, True, (240, 240, 200))
                    client.screen.blit(status, (int(w * 0.06), int(h * 0.90)))
            except Exception:
                pass

            if bool(getattr(client, '_menu_pause_active', False)):
                client._draw_menu_pause_overlay()
            return

        # Story academy intro screen (menu1.png + dialogue)
        if str(view) == 'story_intro':
            client._draw_story_intro()
            return

        # Story academy detail screen (menu2.png + buttons)
        if str(view) == 'story_academy':
            client._draw_story_academy()
            return

        # Story quarters placeholder (until next image is provided)
        if str(view) == 'story_quarters':
            client._draw_story_quarters()
            return

        if str(view) == 'story_inside_cabin':
            client._draw_story_inside_cabin()
            return

        if str(view) == 'story_practice_exams':
            client._draw_story_practice_exams()
            return

        if str(view) == 'story_examinations':
            client._draw_story_examinations()
            return

        # Title
        try:
            if str(view) == 'enemy_select':
                pass
            elif str(view) == 'controls':
                title_txt = 'Controls'
                title = client._menu_title_font.render(title_txt, True, (245, 245, 245))
                client.screen.blit(title, (int(w * 0.06), int(h * 0.06)))
            elif str(view) == 'inventory':
                title_txt = 'Inventory'
                title = client._menu_title_font.render(title_txt, True, (245, 245, 245))
                client.screen.blit(title, (int(w * 0.06), int(h * 0.06)))
            elif str(view) == 'enemy_pattern':
                title_txt = 'Enemy Pattern'
                title = client._menu_title_font.render(title_txt, True, (245, 245, 245))
                client.screen.blit(title, (int(w * 0.06), int(h * 0.06)))
            elif view != 'options' and getattr(client, '_menu_title_wordmark_scaled', None) is not None:
                img = client._menu_title_wordmark_scaled
                x = int((w - int(img.get_width())) / 2)
                y = int(h * 0.035)
                client.screen.blit(img, (x, y))
            else:
                title_txt = 'Options' if str(view) == 'options' else 'Blade Fighters'
                title = client._menu_title_font.render(title_txt, True, (245, 245, 245))
                client.screen.blit(title, (int(w * 0.06), int(h * 0.06)))
        except Exception:
            pass

        # Buttons
        btn_img_normal = getattr(client, '_menu_button_scaled', None)
        btn_img_hover = getattr(client, '_menu_button_hover_scaled', None) or btn_img_normal
        btn_img_pressed = getattr(client, '_menu_button_pressed_scaled', None) or btn_img_hover or btn_img_normal

        client._menu_buttons = client._build_menu_buttons(str(view))

        try:
            mouse_pos = self._pygame.mouse.get_pos()
        except Exception:
            mouse_pos = (0, 0)
        try:
            mouse_down = bool(self._pygame.mouse.get_pressed()[0])
        except Exception:
            mouse_down = False

        try:
            sel = int(getattr(client, '_menu_selected', 0) or 0)
        except Exception:
            sel = 0

        # Bot Battle sword picker panels (left/right)
        if str(view) == 'bot_battle':
            try:
                client._draw_bot_battle_sword_panels(mouse_pos=tuple(mouse_pos))
            except Exception:
                pass

        # Quickplay (enemy_select) sword picker panels (left/right)
        if str(view) == 'enemy_select':
            try:
                client._draw_quickplay_sword_panels(mouse_pos=tuple(mouse_pos))
            except Exception:
                pass

        for i, b in enumerate(client._menu_buttons):
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
                if client._ui_is_button_flashed('menu', str(b.get('id'))):
                    pressed = True
            except Exception:
                pass

            if btn_img_normal is None:
                self._pygame.draw.rect(client.screen, (40, 40, 60), rect, border_radius=12)
                self._pygame.draw.rect(client.screen, (180, 180, 200), rect, width=2, border_radius=12)
            else:
                state = 'pressed' if pressed else ('hover' if (hovered or i == sel) else 'normal')
                src0 = btn_img_pressed if pressed else (btn_img_hover if (hovered or i == sel) else btn_img_normal)
                src = client._get_scaled_menu_button_surface(state, src0, (int(rect.w), int(rect.h))) or src0
                client.screen.blit(src, (int(rect.x), int(rect.y)))

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

        # Inventory preview panel (weapon art + pattern)
        if str(view) in ('inventory', 'enemy_pattern'):
            try:
                # Resolve selected sword from menu selection (fallback to equipped)
                sel = int(getattr(client, '_menu_selected', 0) or 0)
            except Exception:
                sel = 0
            chosen_value = None
            try:
                if 0 <= sel < len(client._menu_buttons):
                    bid = str(client._menu_buttons[sel].get('id', '') or '')
                    if bid.startswith('sword:'):
                        chosen_value = str(bid.split(':', 1)[1] if ':' in bid else '').strip().lower() or None
                    elif bid.startswith('enemy_sword:'):
                        chosen_value = str(bid.split(':', 1)[1] if ':' in bid else '').strip().lower() or None
            except Exception:
                chosen_value = None
            if not chosen_value:
                try:
                    if str(view) == 'enemy_pattern':
                        chosen_value = str(getattr(client, '_enemy_sword_value', 'rusty_sword') or 'rusty_sword').strip().lower()
                    else:
                        chosen_value = str(getattr(client, '_equipped_sword_value', 'rusty_sword') or 'rusty_sword').strip().lower()
                except Exception:
                    chosen_value = 'rusty_sword'

            try:
                sword_type = client._resolve_sword_type(chosen_value)
            except Exception:
                sword_type = SwordType.RUSTY_SWORD

            patt = None
            try:
                patt = SWORD_PATTERNS.get(sword_type)
            except Exception:
                patt = None

            # Panel area (left side)
            px = int(w * 0.06)
            py = int(h * 0.20)
            pw = int(max(280, w * 0.34))
            ph = int(max(240, h * 0.62))
            panel_rect = self._pygame.Rect(px, py, pw, ph)

            try:
                panel = self._pygame.Surface((int(panel_rect.w), int(panel_rect.h)), flags=self._pygame.SRCALPHA)
                panel.fill((0, 0, 0, 150))
                client.screen.blit(panel, (int(panel_rect.x), int(panel_rect.y)))
                self._pygame.draw.rect(client.screen, (255, 255, 255), panel_rect, width=2, border_radius=12)
            except Exception:
                pass

            # Weapon name
            title_h = 0
            try:
                nm = str(getattr(patt, 'name', chosen_value) or chosen_value)
                title2 = client.ui_font.render(nm, True, (245, 245, 245))
                client.screen.blit(title2, (int(panel_rect.x + 12), int(panel_rect.y + 10)))
                title_h = int(title2.get_height())
            except Exception:
                pass

            # Fists note (solid color randomizes per game)
            note_h = 0
            try:
                if sword_type == SwordType.FISTS:
                    note = client.ui_font.render('randomizes per game', True, (210, 210, 210))
                    client.screen.blit(note, (int(panel_rect.x + 12), int(panel_rect.y + 10 + title_h + 2)))
                    note_h = int(note.get_height()) + 4
            except Exception:
                note_h = 0

            # Weapon art
            art = None
            try:
                art = client._get_weapon_art_scaled(sword_type)
            except Exception:
                art = None
            cur_y = int(panel_rect.y + 34 + note_h)
            if art is not None:
                try:
                    ax = int(panel_rect.centerx - art.get_width() / 2)
                    client.screen.blit(art, (ax, cur_y))
                    cur_y = int(cur_y + art.get_height() + 10)
                except Exception:
                    pass

            # Pattern grid (6 wide)
            try:
                if patt is not None and isinstance(getattr(patt, 'pattern', None), list):
                    # Show a consistent 12-row preview (matches the visible board height).
                    # Many patterns are stored at shorter heights, but strikes use fold/repeat
                    # rules when the requested row exceeds the stored height.
                    preview_rows = 12

                    # Legend first so we can size the grid to fit.
                    legend = client.ui_font.render('Drop Pattern (12 rows)', True, (220, 220, 220))

                    # Compute cell size constrained by both width and available panel height.
                    # Leave some breathing room for borders and the legend.
                    max_cell_w = float(panel_rect.w - 24) / 6.0
                    available_h = float(panel_rect.bottom - 10 - cur_y - legend.get_height() - 8)
                    max_cell_h = available_h / float(max(1, preview_rows))
                    cell = int(max(8, min(28, max_cell_w, max_cell_h)))

                    gx = int(panel_rect.x + (panel_rect.w - cell * 6) / 2)
                    gy = int(min(panel_rect.bottom - 10 - cell * preview_rows, cur_y + legend.get_height() + 8))
                    gy = max(int(cur_y + legend.get_height() + 8), int(gy))

                    # Build an "effective" 12-row color grid using the same fold rules
                    # as vertical strikes (pattern columns align with board columns).
                    # Rows are 1-based from the bottom.
                    effective = []
                    for row1 in range(1, preview_rows + 1):
                        row_colors = []
                        for c in range(6):
                            ck = 'yellow'
                            try:
                                ck = str(
                                    patt.get_strike_color(
                                        x=0,
                                        y=0,
                                        strike_width=6,
                                        strike_height=preview_rows,
                                        block_x_offset=int(c),
                                        block_y_offset=int(row1 - 1),
                                        is_horizontal=False,
                                        from_right=False,
                                    )
                                ).strip().lower()
                            except Exception:
                                # Fallback: use raw stored pattern (may be shorter than 12)
                                try:
                                    raw = getattr(patt, 'pattern', None) or []
                                    if raw and 0 <= (row1 - 1) < len(raw) and 0 <= c < len(raw[row1 - 1]):
                                        ck = str(raw[row1 - 1][c]).strip().lower()
                                except Exception:
                                    ck = 'yellow'
                            row_colors.append(ck)
                        effective.append(row_colors)

                    # Draw from top to bottom so it reads like the doc
                    for r in range(preview_rows - 1, -1, -1):
                        row = effective[r]
                        for c in range(6):
                            try:
                                ck = str(row[c]).strip().lower()
                            except Exception:
                                ck = 'yellow'
                            rgb = color_map.get(ck, (200, 200, 200))
                            rr = self._pygame.Rect(
                                int(gx + c * cell),
                                int(gy + (preview_rows - 1 - r) * cell),
                                int(cell),
                                int(cell),
                            )
                            self._pygame.draw.rect(client.screen, rgb, rr)
                            self._pygame.draw.rect(client.screen, (15, 15, 20), rr, width=1)

                    # Legend (above grid)
                    client.screen.blit(legend, (int(panel_rect.centerx - legend.get_width() / 2), int(gy - legend.get_height() - 4)))
            except Exception:
                pass

        # Hover pattern preview (same effect as Bot Battle) for Quickplay/Inventory sword lists.
        # - inventory: hover a sword -> show its pattern to the right
        # - enemy_pattern: hover an enemy sword -> show its pattern to the right
        # - enemy_select: hover the "Enemy Pattern" row -> show the currently selected incoming pattern
        try:
            view_s = str(view or '').strip().lower()
        except Exception:
            view_s = ''

        if view_s in ('inventory', 'enemy_pattern', 'enemy_select'):
            hover_rect = None
            hover_id = None
            try:
                for bb in (getattr(client, '_menu_buttons', []) or []):
                    rr = bb.get('rect')
                    if rr is not None and rr.collidepoint(mouse_pos):
                        hover_rect = rr
                        hover_id = str(bb.get('id', '') or '')
                        break
            except Exception:
                hover_rect = None
                hover_id = None

            hover_value = None
            try:
                if hover_id and view_s == 'inventory' and hover_id.startswith('sword:'):
                    hover_value = str(hover_id.split(':', 1)[1] if ':' in hover_id else '').strip().lower() or None
                elif hover_id and view_s == 'enemy_pattern' and hover_id.startswith('enemy_sword:'):
                    hover_value = str(hover_id.split(':', 1)[1] if ':' in hover_id else '').strip().lower() or None
                elif hover_id and view_s == 'enemy_select' and hover_id == 'enemy_pattern':
                    hover_value = str(getattr(client, '_enemy_sword_value', 'rusty_sword') or 'rusty_sword').strip().lower() or None
            except Exception:
                hover_value = None

            if hover_rect is not None and hover_value:
                try:
                    st = client._resolve_sword_type(str(hover_value))
                except Exception:
                    st = None
                if st is not None:
                    try:
                        client._draw_bot_battle_hover_pattern(sword_type=st, anchor_rect=hover_rect)
                    except Exception:
                        pass

        # Player gold (top-right) on standard menus.
        try:
            view_s2 = str(view or '').strip().lower()
        except Exception:
            view_s2 = ''
        if view_s2 and (not view_s2.startswith('story_')):
            try:
                gold = int(getattr(client, '_player_gold', 0) or 0)
            except Exception:
                gold = 0
            try:
                coin = None
                try:
                    fh = int(client.ui_font.get_height())
                except Exception:
                    fh = int(round(20 * float(getattr(client, 'ui_scale', 1.0) or 1.0)))
                try:
                    assets = getattr(client, '_assets', None)
                    if assets is not None:
                        coin = assets.get_coin_icon_scaled(client, target_h=max(84, int(round(fh * 12.0))))
                except Exception:
                    coin = None

                txt = client.ui_font.render(f"{gold}", True, (245, 245, 245))
                pad = int(max(8, round(12 * float(getattr(client, 'ui_scale', 1.0) or 1.0))))

                try:
                    pad_mult = float(getattr(client, '_coin_panel_pad_mult', 1.0) or 1.0)
                except Exception:
                    pad_mult = 1.0
                pad_mult = max(0.50, min(2.00, float(pad_mult)))
                pad = int(max(4, int(round(float(pad) * float(pad_mult)))))

                try:
                    icon_cap_mult = float(getattr(client, '_coin_panel_icon_layout_cap_mult', 1.25) or 1.25)
                except Exception:
                    icon_cap_mult = 1.25
                icon_cap_mult = max(1.00, min(3.50, float(icon_cap_mult)))
                icon_gap = int(max(4, round(6 * float(getattr(client, 'ui_scale', 1.0) or 1.0))))
                try:
                    if coin is not None:
                        eff_h = min(int(coin.get_height()), int(round(float(fh) * 3.0)))
                        icon_gap = int(max(int(icon_gap), int(round(float(eff_h) * 0.22))))
                except Exception:
                    pass
                content_w = int(txt.get_width())
                content_h = int(txt.get_height())
                if coin is not None:
                    content_w = int(content_w + int(coin.get_width()) + int(icon_gap))
                    # Keep the panel compact even if coin is oversized.
                    try:
                        coin_layout_h = min(int(coin.get_height()), int(round(float(content_h) * float(icon_cap_mult))))
                    except Exception:
                        coin_layout_h = int(content_h)
                    content_h = int(max(content_h, int(coin_layout_h)))
                panel_w = int(content_w) + 2 * pad
                panel_h = int(content_h) + 2 * pad

                # Manual resize override (drag corner).
                try:
                    ov_f = (getattr(client, '_coin_panel_size_override_frac', {}) or {}).get('menu', None)
                except Exception:
                    ov_f = None
                if isinstance(ov_f, (list, tuple)) and len(ov_f) >= 2:
                    try:
                        ow = int(round(float(ov_f[0]) * float(w)))
                        oh = int(round(float(ov_f[1]) * float(h)))
                        panel_w = int(max(40, min(int(w - 6), int(ow))))
                        panel_h = int(max(24, min(int(h - 6), int(oh))))
                    except Exception:
                        pass
                else:
                    try:
                        ov = (getattr(client, '_coin_panel_size_override', {}) or {}).get('menu', None)
                    except Exception:
                        ov = None
                    if isinstance(ov, (list, tuple)) and len(ov) >= 2:
                        try:
                            ow = int(ov[0])
                            oh = int(ov[1])
                            panel_w = int(max(40, min(int(w - 6), int(ow))))
                            panel_h = int(max(24, min(int(h - 6), int(oh))))
                        except Exception:
                            pass

                px = int(w - panel_w - int(w * 0.03))
                py = int(h * 0.02)

                try:
                    client._last_coin_panel_rects['menu'] = self._pygame.Rect(int(px), int(py), int(panel_w), int(panel_h))
                except Exception:
                    pass
                panel = self._pygame.Surface((int(panel_w), int(panel_h)), flags=self._pygame.SRCALPHA)
                panel.fill((0, 0, 0, 140))
                client.screen.blit(panel, (px, py))
                self._pygame.draw.rect(client.screen, (255, 255, 255), self._pygame.Rect(px, py, panel_w, panel_h), width=2, border_radius=10)
                x = int(px + pad)
                y0 = int(py + pad)
                if coin is not None:
                    # Center relative to text height; coin may extend beyond panel.
                    try:
                        iy = int(y0 + (int(txt.get_height()) - int(coin.get_height())) // 2)
                    except Exception:
                        iy = int(y0)
                    iy = max(0, int(iy))
                    client.screen.blit(coin, (int(x), int(iy)))
                    x = int(x + int(coin.get_width()) + int(icon_gap))
                ty = int(y0 + (content_h - int(txt.get_height())) // 2)
                client.screen.blit(txt, (int(x), int(ty)))
            except Exception:
                pass

    def draw_main_menu(self, client: Any) -> None:
        if bool(getattr(client, '_menu_transition_active', False)):
            try:
                start = int(getattr(client, '_menu_transition_start_ms', 0) or 0)
                dur = int(getattr(client, '_menu_transition_duration_ms', 650) or 650)
                now = int(self._pygame.time.get_ticks())
                t = 1.0 if dur <= 0 else max(0.0, min(1.0, float(now - start) / float(dur)))
            except Exception:
                t = 1.0

            from_view = str(getattr(client, '_menu_transition_from', 'main') or 'main')
            to_view = str(getattr(client, '_menu_transition_to', 'main') or 'main')
            if t < 0.5:
                client._draw_menu_view(from_view)
                alpha = int(round(255.0 * (t / 0.5)))
            else:
                # Switch underlying view halfway so input state is consistent after the fade.
                try:
                    client._menu_view = to_view
                except Exception:
                    pass
                client._draw_menu_view(to_view)
                alpha = int(round(255.0 * (1.0 - (t - 0.5) / 0.5)))

            try:
                w, h = int(client.screen.get_width()), int(client.screen.get_height())
                overlay = self._pygame.Surface((w, h), flags=self._pygame.SRCALPHA)
                overlay.fill((0, 0, 0, max(0, min(255, alpha))))
                client.screen.blit(overlay, (0, 0))
            except Exception:
                pass

            if t >= 1.0:
                client._menu_transition_active = False
            return

        client._draw_menu_view(getattr(client, '_menu_view', 'main'))

        try:
            view = str(getattr(client, '_menu_view', 'main') or 'main')
        except Exception:
            view = 'main'
        try:
            w, h = int(client.screen.get_width()), int(client.screen.get_height())
        except Exception:
            w, h = 0, 0

        # Status
        try:
            st = str(getattr(client, '_menu_status_text', '') or '').strip()
            if st:
                status = client.ui_font.render(st, True, (240, 240, 200))
                client.screen.blit(status, (int(w * 0.06), int(h * 0.90)))
        except Exception:
            pass
