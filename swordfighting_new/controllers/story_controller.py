from __future__ import annotations

from typing import Any


class StoryController:
    def __init__(self, *, pygame: Any):
        self._pygame = pygame

    def get_story_dialogue_text(self, client: Any) -> str:
        # Post-tutorial story: menu1->menu2 cutscene (handled by separate views)
        if bool(getattr(client, '_story_swift_tutorial_complete', False)):
            name = str(getattr(client, '_story_player_name', 'Fighter') or 'Fighter').strip() or 'Fighter'
            return f"Behold the Academy, {name}."  # menu1 line before fading

        if not bool(getattr(client, '_story_name_confirmed', False)):
            return "Welcome to the Academy. What's your name?"

        name = str(getattr(client, '_story_player_name', 'Fighter') or 'Fighter').strip() or 'Fighter'
        step = int(getattr(client, '_story_dialogue_step', 0) or 0)
        if step <= 0:
            return f"Nice to meet you, {name}. I'm your Academy instructor."
        if step == 1:
            return "Here you'll learn how swords, breakers, and gravity interact. We'll start with movement and rotations."
        return 'Press Enter to begin training.'

    def draw_story_intro(self, client: Any) -> None:
        # Background: centered image at native size (or scaled down to fit).
        try:
            client.screen.fill((0, 0, 0))
        except Exception:
            pass

        bg = getattr(client, '_story_menu1_scaled', None)
        if bg is not None:
            try:
                w = int(client.screen.get_width())
                h = int(client.screen.get_height())
                bx = int((w - int(bg.get_width())) / 2)
                by = int((h - int(bg.get_height())) / 2)
                client.screen.blit(bg, (bx, by))
            except Exception:
                pass

        w = int(client.screen.get_width())
        h = int(client.screen.get_height())

        # Player info (top-right): name, gold, and future currencies.
        try:
            pad = int(max(10, round(14 * float(getattr(client, 'ui_scale', 1.0) or 1.0))))
            line_gap = int(max(2, round(6 * float(getattr(client, 'ui_scale', 1.0) or 1.0))))

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

            # Show live name while typing.
            nm = str(getattr(client, '_story_player_name', '') or '').strip()
            show_name = nm if nm else '---'
            gold = int(getattr(client, '_player_gold', 0) or 0)

            coin = None
            try:
                assets = getattr(client, '_assets', None)
                if assets is not None:
                    try:
                        fh = int(client.ui_font.get_height())
                    except Exception:
                        fh = int(round(20 * float(getattr(client, 'ui_scale', 1.0) or 1.0)))
                    coin = assets.get_coin_icon_scaled(client, target_h=max(84, int(round(fh * 12.0))))
            except Exception:
                coin = None

            lines = [
                f'Name: {show_name}',
                f'Gold: {gold}',
                'Gems: 0',
            ]

            rendered = [client.ui_font.render(t, True, (245, 245, 245)) for t in lines]

            icon_gap = int(max(4, round(6 * float(getattr(client, 'ui_scale', 1.0) or 1.0))))
            try:
                if coin is not None:
                    try:
                        fh = int(client.ui_font.get_height())
                    except Exception:
                        fh = int(round(20 * float(getattr(client, 'ui_scale', 1.0) or 1.0)))
                    eff_h = min(int(coin.get_height()), int(round(float(fh) * 3.0)))
                    icon_gap = int(max(int(icon_gap), int(round(float(eff_h) * 0.22))))
            except Exception:
                pass
            row_ws: list[int] = []
            row_hs: list[int] = []
            for i, r in enumerate(rendered):
                row_w = int(r.get_width())
                row_h = int(r.get_height())
                if i == 1 and coin is not None:
                    row_w = int(row_w + int(coin.get_width()) + int(icon_gap))
                    try:
                        coin_layout_h = min(int(coin.get_height()), int(round(float(row_h) * float(icon_cap_mult))))
                    except Exception:
                        coin_layout_h = int(row_h)
                    row_h = int(max(row_h, int(coin_layout_h)))
                row_ws.append(int(row_w))
                row_hs.append(int(row_h))

            panel_w = int(max(row_ws) if row_ws else 1) + 2 * pad
            panel_h = int(sum(row_hs)) + (len(row_hs) - 1) * line_gap + 2 * pad

            # Manual resize override (drag corner).
            try:
                ov_f = (getattr(client, '_coin_panel_size_override_frac', {}) or {}).get('story', None)
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
                    ov = (getattr(client, '_coin_panel_size_override', {}) or {}).get('story', None)
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
            panel_x = int(w - panel_w - int(w * 0.04))
            panel_y = int(h * 0.06)

            try:
                client._last_coin_panel_rects['story'] = self._pygame.Rect(int(panel_x), int(panel_y), int(panel_w), int(panel_h))
            except Exception:
                pass

            panel = self._pygame.Surface((int(panel_w), int(panel_h)), flags=self._pygame.SRCALPHA)
            panel.fill((0, 0, 0, 150))
            client.screen.blit(panel, (panel_x, panel_y))
            self._pygame.draw.rect(client.screen, (255, 255, 255), self._pygame.Rect(panel_x, panel_y, panel_w, panel_h), width=2, border_radius=10)

            yy = int(panel_y + pad)
            for i, r in enumerate(rendered):
                # Add a coin icon to the Gold line.
                if i == 1 and coin is not None:
                    try:
                        try:
                            coin_layout_h = min(int(coin.get_height()), int(round(float(r.get_height()) * float(icon_cap_mult))))
                        except Exception:
                            coin_layout_h = int(r.get_height())
                        row_h = int(max(int(r.get_height()), int(coin_layout_h)))
                        # Keep the panel compact; center the coin relative to text height.
                        iy = int(yy + (int(r.get_height()) - int(coin.get_height())) // 2)
                        iy = max(0, int(iy))
                        client.screen.blit(coin, (int(panel_x + pad), int(iy)))
                        client.screen.blit(r, (int(panel_x + pad + int(coin.get_width()) + int(icon_gap)), int(yy + (row_h - int(r.get_height())) // 2)))
                        yy += int(row_h + line_gap)
                        continue
                    except Exception:
                        pass
                client.screen.blit(r, (int(panel_x + pad), yy))
                yy += int(r.get_height() + line_gap)
        except Exception:
            pass

        # Simple instructor placeholder (left side)
        try:
            cx = int(w * 0.16)
            cy = int(h * 0.52)
            r = int(max(26, min(w, h) * 0.045))
            self._pygame.draw.circle(client.screen, (240, 240, 240), (cx, cy), r)
            self._pygame.draw.circle(client.screen, (20, 20, 20), (cx, cy), r, width=2)
            label = client.ui_font.render('Instructor', True, (245, 245, 245))
            client.screen.blit(label, (int(cx - label.get_width() / 2), int(cy + r + 10)))
        except Exception:
            pass

        # Chat box
        try:
            box_h = int(max(140, h * 0.26))
            box_w = int(max(420, w * 0.88))
            box_x = int((w - box_w) / 2)
            box_y = int(h - box_h - h * 0.06)
            rect = self._pygame.Rect(box_x, box_y, box_w, box_h)

            panel = self._pygame.Surface((int(rect.w), int(rect.h)), flags=self._pygame.SRCALPHA)
            panel.fill((0, 0, 0, 170))
            client.screen.blit(panel, (int(rect.x), int(rect.y)))
            self._pygame.draw.rect(client.screen, (255, 255, 255), rect, width=2, border_radius=12)

            pad = int(max(12, round(18 * float(getattr(client, 'ui_scale', 1.0) or 1.0))))
            text_x = int(rect.x + pad)
            text_y = int(rect.y + pad)
            max_text_w = int(rect.w - 2 * pad)

            msg = self.get_story_dialogue_text(client)
            lines = client._wrap_text(msg, client.ui_font, max_text_w)

            # Render message
            y = text_y
            for line in lines[:6]:
                surf = client.ui_font.render(line, True, (245, 245, 245))
                client.screen.blit(surf, (text_x, y))
                y += int(surf.get_height() + max(3, round(6 * float(getattr(client, 'ui_scale', 1.0) or 1.0))))

            # Name input line
            if (not bool(getattr(client, '_story_swift_tutorial_complete', False))) and (not bool(getattr(client, '_story_name_confirmed', False))):
                name = str(getattr(client, '_story_player_name', '') or '')
                cursor_on = (int(self._pygame.time.get_ticks() / 450) % 2) == 0
                cursor = '_' if cursor_on else ' '
                prompt = f'Name: {name}{cursor}'
                surf = client.ui_font.render(prompt, True, (240, 220, 140))
                client.screen.blit(surf, (text_x, int(rect.bottom - pad - surf.get_height())))
            else:
                hint_txt = 'Enter = Next   Esc/P = Pause menu'
                if bool(getattr(client, '_story_swift_tutorial_complete', False)):
                    hint_txt = 'Enter = Continue   Esc/P = Pause menu'
                hint = client.ui_font.render(hint_txt, True, (220, 220, 220))
                client.screen.blit(hint, (text_x, int(rect.bottom - pad - hint.get_height())))
        except Exception:
            pass

        # Status text (optional)
        try:
            st = str(getattr(client, '_menu_status_text', '') or '').strip()
            if st:
                status = client.ui_font.render(st, True, (240, 240, 200))
                client.screen.blit(status, (int(w * 0.06), int(h * 0.90)))
        except Exception:
            pass

        if bool(getattr(client, '_menu_pause_active', False)):
            client._draw_menu_pause_overlay()

    def story_message_for_academy(self, client: Any) -> str:
        name = str(getattr(client, '_story_player_name', 'Fighter') or 'Fighter').strip() or 'Fighter'
        step = int(getattr(client, '_story_post_tutorial_step', 0) or 0)
        if step <= 1:
            return (
                'Behold the Academy.\n\n'
                "This is where legends hone their skills — where blades learn discipline, breakers learn purpose, "
                'and gravity always tells the truth.\n\n'
                "When you're ready, step inside."
            )
        # step >= 2
        return (
            'Ha! Not so fast.\n\n'
            'Before you can enter the Academy, you must pass your exams!\n\n'
            'For now, you sleep behind the school in the Comfort building. '
            "(A proud name… for a place that's virtually inhospitable.)\n\n"
            f'Proceed to your quarters, {name}.'
        )

    def draw_story_academy(self, client: Any) -> None:
        # Background: menu2.png (centered, downscaled if needed).
        try:
            client.screen.fill((0, 0, 0))
        except Exception:
            pass

        bg = getattr(client, '_story_menu2_scaled', None)
        if bg is not None:
            try:
                w = int(client.screen.get_width())
                h = int(client.screen.get_height())
                bx = int((w - int(bg.get_width())) / 2)
                by = int((h - int(bg.get_height())) / 2)
                client.screen.blit(bg, (bx, by))
            except Exception:
                pass

        # Reuse the intro draw for HUD + chat box styling by temporarily rendering the same elements.
        # We keep the background above and then render the HUD/chat box similarly.
        w = int(client.screen.get_width())
        h = int(client.screen.get_height())

        # Player HUD (top-right)
        try:
            pad = int(max(10, round(14 * float(getattr(client, 'ui_scale', 1.0) or 1.0))))
            line_gap = int(max(2, round(6 * float(getattr(client, 'ui_scale', 1.0) or 1.0))))
            nm = str(getattr(client, '_story_player_name', '') or '').strip()
            show_name = nm if nm else '---'
            gold = int(getattr(client, '_player_gold', 0) or 0)
            lines = [f'Name: {show_name}', f'Gold: {gold}', 'Gems: 0']
            rendered = [client.ui_font.render(t, True, (245, 245, 245)) for t in lines]
            panel_w = max(r.get_width() for r in rendered) + 2 * pad
            panel_h = sum(r.get_height() for r in rendered) + (len(rendered) - 1) * line_gap + 2 * pad
            panel_x = int(w - panel_w - int(w * 0.04))
            panel_y = int(h * 0.06)
            panel = self._pygame.Surface((int(panel_w), int(panel_h)), flags=self._pygame.SRCALPHA)
            panel.fill((0, 0, 0, 150))
            client.screen.blit(panel, (panel_x, panel_y))
            self._pygame.draw.rect(client.screen, (255, 255, 255), self._pygame.Rect(panel_x, panel_y, panel_w, panel_h), width=2, border_radius=10)
            yy = int(panel_y + pad)
            for r in rendered:
                client.screen.blit(r, (int(panel_x + pad), yy))
                yy += int(r.get_height() + line_gap)
        except Exception:
            pass

        # Instructor placeholder
        try:
            cx = int(w * 0.16)
            cy = int(h * 0.52)
            rr = int(max(26, min(w, h) * 0.045))
            self._pygame.draw.circle(client.screen, (240, 240, 240), (cx, cy), rr)
            self._pygame.draw.circle(client.screen, (20, 20, 20), (cx, cy), rr, width=2)
            label = client.ui_font.render('Instructor', True, (245, 245, 245))
            client.screen.blit(label, (int(cx - label.get_width() / 2), int(cy + rr + 10)))
        except Exception:
            pass

        # Chat box + button(s)
        client._menu_buttons = []
        try:
            box_h = int(max(140, h * 0.30))
            box_w = int(max(420, w * 0.88))
            box_x = int((w - box_w) / 2)
            box_y = int(h - box_h - h * 0.06)
            rect = self._pygame.Rect(box_x, box_y, box_w, box_h)

            panel = self._pygame.Surface((int(rect.w), int(rect.h)), flags=self._pygame.SRCALPHA)
            panel.fill((0, 0, 0, 170))
            client.screen.blit(panel, (int(rect.x), int(rect.y)))
            self._pygame.draw.rect(client.screen, (255, 255, 255), rect, width=2, border_radius=12)

            pad = int(max(12, round(18 * float(getattr(client, 'ui_scale', 1.0) or 1.0))))
            text_x = int(rect.x + pad)
            text_y = int(rect.y + pad)
            max_text_w = int(rect.w - 2 * pad)

            msg = self.story_message_for_academy(client)
            lines = client._wrap_text(msg, client.ui_font, max_text_w)
            y = text_y
            for line in lines[:7]:
                surf = client.ui_font.render(line, True, (245, 245, 245))
                client.screen.blit(surf, (text_x, y))
                y += int(surf.get_height() + max(3, round(6 * float(getattr(client, 'ui_scale', 1.0) or 1.0))))

            step = int(getattr(client, '_story_post_tutorial_step', 0) or 0)
            btn_img_normal = getattr(client, '_menu_button_scaled', None)
            btn_img_hover = getattr(client, '_menu_button_hover_scaled', None) or btn_img_normal
            btn_img_pressed = getattr(client, '_menu_button_pressed_scaled', None) or btn_img_hover or btn_img_normal

            bw = int(btn_img_normal.get_width()) if btn_img_normal is not None else int(min(w * 0.34, 520))
            bh = int(btn_img_normal.get_height()) if btn_img_normal is not None else 84
            bw = max(220, bw)
            bh = max(60, bh)
            bx = int(rect.right - pad - bw)
            by = int(rect.bottom - pad - bh)

            if step <= 1:
                client._menu_buttons = [
                    {'id': 'story_proceed_academy', 'label': 'Proceed to Academy', 'rect': self._pygame.Rect(bx, by, bw, bh)},
                ]
            else:
                client._menu_buttons = [
                    {'id': 'story_proceed_quarters', 'label': 'Proceed to your quarters', 'rect': self._pygame.Rect(bx, by, bw, bh)},
                ]

            try:
                mouse_pos = self._pygame.mouse.get_pos()
            except Exception:
                mouse_pos = (0, 0)
            try:
                mouse_down = bool(self._pygame.mouse.get_pressed()[0])
            except Exception:
                mouse_down = False

            sel = 0
            try:
                sel = int(getattr(client, '_menu_selected', 0) or 0)
            except Exception:
                sel = 0

            for i, b in enumerate(client._menu_buttons):
                brect = b.get('rect')
                if brect is None:
                    continue

                hovered = False
                try:
                    hovered = bool(brect.collidepoint(mouse_pos))
                except Exception:
                    hovered = False
                pressed = bool(mouse_down and hovered)
                try:
                    if client._ui_is_button_flashed('menu', str(b.get('id'))):
                        pressed = True
                except Exception:
                    pass

                if btn_img_normal is None:
                    self._pygame.draw.rect(client.screen, (40, 40, 60), brect, border_radius=12)
                    self._pygame.draw.rect(client.screen, (180, 180, 200), brect, width=2, border_radius=12)
                else:
                    src = btn_img_pressed if pressed else (btn_img_hover if (hovered or i == sel) else btn_img_normal)
                    client.screen.blit(src, (int(brect.x), int(brect.y)))
                try:
                    client._blit_fitted_text(
                        str(b.get('label', '')),
                        brect,
                        color=(255, 255, 255),
                        base_px=int(getattr(client, '_menu_button_font_px', 40) or 40),
                        max_lines=2,
                    )
                except Exception:
                    pass

            hint = client.ui_font.render('Click the button (Enter also works). Esc/P = Pause menu', True, (220, 220, 220))
            client.screen.blit(hint, (text_x, int(rect.bottom - pad - hint.get_height())))
        except Exception:
            client._menu_buttons = []

        if bool(getattr(client, '_menu_pause_active', False)):
            client._draw_menu_pause_overlay()

    def draw_story_quarters(self, client: Any) -> None:
        # Outside the cabin (story progression hub).
        try:
            client.screen.fill((0, 0, 0))
        except Exception:
            pass

        w = int(client.screen.get_width())
        h = int(client.screen.get_height())

        # Quarters backdrop (menu3.png). Keep menu4 reserved for later scenes.
        bg = getattr(client, '_story_menu3_scaled', None)
        if bg is None:
            bg = getattr(client, '_story_menu4_scaled', None)
        if bg is None:
            bg = getattr(client, '_story_menu2_scaled', None)
        if bg is not None:
            try:
                bx = int((w - int(bg.get_width())) / 2)
                by = int((h - int(bg.get_height())) / 2)
                client.screen.blit(bg, (bx, by))
            except Exception:
                pass

        client._menu_buttons = []
        try:
            box_h = int(max(140, h * 0.26))
            box_w = int(max(420, w * 0.88))
            box_x = int((w - box_w) / 2)
            box_y = int(h - box_h - h * 0.06)
            rect = self._pygame.Rect(box_x, box_y, box_w, box_h)

            panel = self._pygame.Surface((int(rect.w), int(rect.h)), flags=self._pygame.SRCALPHA)
            panel.fill((0, 0, 0, 170))
            client.screen.blit(panel, (int(rect.x), int(rect.y)))
            self._pygame.draw.rect(client.screen, (255, 255, 255), rect, width=2, border_radius=12)

            pad = int(max(12, round(18 * float(getattr(client, 'ui_scale', 1.0) or 1.0))))
            text_x = int(rect.x + pad)
            text_y = int(rect.y + pad)
            name = str(getattr(client, '_story_player_name', 'Fighter') or 'Fighter').strip() or 'Fighter'
            msg = (
                f'Outside the cabin, {name}.\n\n'
                'You feel exhausted. Maybe you should sleep.'
            )
            max_text_w = int(rect.w - 2 * pad)
            lines = client._wrap_text(msg, client.ui_font, max_text_w)
            y = text_y
            for line in lines[:6]:
                surf = client.ui_font.render(line, True, (245, 245, 245))
                client.screen.blit(surf, (text_x, y))
                y += int(surf.get_height() + max(3, round(6 * float(getattr(client, 'ui_scale', 1.0) or 1.0))))

            # Buttons: stacked on the right side of the chat box.
            btn_img_normal = getattr(client, '_menu_button_scaled', None)
            btn_img_hover = getattr(client, '_menu_button_hover_scaled', None) or btn_img_normal
            btn_img_pressed = getattr(client, '_menu_button_pressed_scaled', None) or btn_img_hover or btn_img_normal

            bw = int(btn_img_normal.get_width()) if btn_img_normal is not None else int(min(w * 0.34, 520))
            bh = int(btn_img_normal.get_height()) if btn_img_normal is not None else 84
            bw = max(220, bw)
            bh = max(60, bh)
            _gap = int(max(8, round(bh * 0.18)))

            stack_h = 1 * bh
            bx = int(rect.right - pad - bw)
            by0 = int(rect.bottom - pad - stack_h)

            client._menu_buttons = [
                {'id': 'story_sleep', 'label': 'proceed inside', 'rect': self._pygame.Rect(bx, by0, bw, bh)},
            ]

            try:
                mouse_pos = self._pygame.mouse.get_pos()
            except Exception:
                mouse_pos = (0, 0)
            try:
                mouse_down = bool(self._pygame.mouse.get_pressed()[0])
            except Exception:
                mouse_down = False

            sel = 0
            try:
                sel = int(getattr(client, '_menu_selected', 0) or 0)
            except Exception:
                sel = 0
            sel = max(0, min(sel, max(0, len(client._menu_buttons) - 1)))
            try:
                client._menu_selected = int(sel)
            except Exception:
                pass

            for i, b in enumerate(client._menu_buttons):
                brect = b.get('rect')
                if brect is None:
                    continue
                try:
                    hovered = bool(brect.collidepoint(mouse_pos))
                except Exception:
                    hovered = False
                pressed = bool(mouse_down and hovered)
                try:
                    if client._ui_is_button_flashed('menu', str(b.get('id'))):
                        pressed = True
                except Exception:
                    pass

                if btn_img_normal is None:
                    self._pygame.draw.rect(client.screen, (40, 40, 60), brect, border_radius=12)
                    self._pygame.draw.rect(client.screen, (180, 180, 200), brect, width=2, border_radius=12)
                else:
                    src = btn_img_pressed if pressed else (btn_img_hover if (hovered or i == sel) else btn_img_normal)
                    client.screen.blit(src, (int(brect.x), int(brect.y)))
                try:
                    client._blit_fitted_text(
                        str(b.get('label', '')),
                        brect,
                        color=(255, 255, 255),
                        base_px=int(getattr(client, '_menu_button_font_px', 40) or 40),
                        max_lines=2,
                    )
                except Exception:
                    pass

            try:
                st = str(getattr(client, '_menu_status_text', '') or '').strip()
                if st:
                    status = client.ui_font.render(st, True, (240, 240, 200))
                    client.screen.blit(status, (int(w * 0.06), int(h * 0.90)))
            except Exception:
                pass
        except Exception:
            pass

        if bool(getattr(client, '_menu_pause_active', False)):
            client._draw_menu_pause_overlay()

    def draw_story_inside_cabin(self, client: Any) -> None:
        # Wake-up scene inside the cabin.
        try:
            client.screen.fill((0, 0, 0))
        except Exception:
            pass

        w = int(client.screen.get_width())
        h = int(client.screen.get_height())

        bg = (
            getattr(client, '_story_menu5_scaled', None)
            or getattr(client, '_story_menu4_scaled', None)
            or getattr(client, '_story_menu3_scaled', None)
            or getattr(client, '_story_menu2_scaled', None)
        )
        if bg is not None:
            try:
                bx = int((w - int(bg.get_width())) / 2)
                by = int((h - int(bg.get_height())) / 2)
                client.screen.blit(bg, (bx, by))
            except Exception:
                pass

        client._menu_buttons = []
        try:
            box_h = int(max(140, h * 0.26))
            box_w = int(max(420, w * 0.88))
            box_x = int((w - box_w) / 2)
            box_y = int(h - box_h - h * 0.06)
            rect = self._pygame.Rect(box_x, box_y, box_w, box_h)

            panel = self._pygame.Surface((int(rect.w), int(rect.h)), flags=self._pygame.SRCALPHA)
            panel.fill((0, 0, 0, 170))
            client.screen.blit(panel, (int(rect.x), int(rect.y)))
            self._pygame.draw.rect(client.screen, (255, 255, 255), rect, width=2, border_radius=12)

            pad = int(max(12, round(18 * float(getattr(client, 'ui_scale', 1.0) or 1.0))))
            text_x = int(rect.x + pad)
            text_y = int(rect.y + pad)
            msg = 'You wake up in the cabin.\n\nWhat do you want to do today?'
            lines = client._wrap_text(msg, client.ui_font, int(rect.w - 2 * pad))
            y = text_y
            for line in lines[:6]:
                surf = client.ui_font.render(line, True, (245, 245, 245))
                client.screen.blit(surf, (text_x, y))
                y += int(surf.get_height() + max(3, round(6 * float(getattr(client, 'ui_scale', 1.0) or 1.0))))

            btn_img_normal = getattr(client, '_menu_button_scaled', None)
            btn_img_hover = getattr(client, '_menu_button_hover_scaled', None) or btn_img_normal
            btn_img_pressed = getattr(client, '_menu_button_pressed_scaled', None) or btn_img_hover or btn_img_normal

            bw = int(btn_img_normal.get_width()) if btn_img_normal is not None else int(min(w * 0.34, 520))
            bh = int(btn_img_normal.get_height()) if btn_img_normal is not None else 84
            bw = max(220, bw)
            bh = max(60, bh)
            gap = int(max(8, round(bh * 0.18)))
            stack_h = 2 * bh + gap
            bx = int(rect.right - pad - bw)
            by0 = int(rect.bottom - pad - stack_h)

            slept = bool(getattr(client, '_story_inside_cabin_slept', False))
            client._menu_buttons = [
                {'id': 'story_practice_exams', 'label': 'Practice for Exams', 'rect': self._pygame.Rect(bx, by0 + 0 * (bh + gap), bw, bh)},
                (
                    {'id': 'story_proceed_examinations', 'label': 'Proceed to Exams', 'rect': self._pygame.Rect(bx, by0 + 1 * (bh + gap), bw, bh)}
                    if slept
                    else {'id': 'story_cabin_sleep', 'label': 'Sleep', 'rect': self._pygame.Rect(bx, by0 + 1 * (bh + gap), bw, bh)}
                ),
            ]

            try:
                mouse_pos = self._pygame.mouse.get_pos()
            except Exception:
                mouse_pos = (0, 0)
            try:
                mouse_down = bool(self._pygame.mouse.get_pressed()[0])
            except Exception:
                mouse_down = False

            sel = 0
            try:
                sel = int(getattr(client, '_menu_selected', 0) or 0)
            except Exception:
                sel = 0
            sel = max(0, min(sel, max(0, len(client._menu_buttons) - 1)))
            try:
                client._menu_selected = int(sel)
            except Exception:
                pass

            for i, b in enumerate(client._menu_buttons):
                brect = b.get('rect')
                if brect is None:
                    continue
                try:
                    hovered = bool(brect.collidepoint(mouse_pos))
                except Exception:
                    hovered = False
                pressed = bool(mouse_down and hovered)
                try:
                    if client._ui_is_button_flashed('menu', str(b.get('id'))):
                        pressed = True
                except Exception:
                    pass

                if btn_img_normal is None:
                    self._pygame.draw.rect(client.screen, (40, 40, 60), brect, border_radius=12)
                    self._pygame.draw.rect(client.screen, (180, 180, 200), brect, width=2, border_radius=12)
                else:
                    src = btn_img_pressed if pressed else (btn_img_hover if (hovered or i == sel) else btn_img_normal)
                    client.screen.blit(src, (int(brect.x), int(brect.y)))
                try:
                    client._blit_fitted_text(
                        str(b.get('label', '')),
                        brect,
                        color=(255, 255, 255),
                        base_px=int(getattr(client, '_menu_button_font_px', 40) or 40),
                        max_lines=2,
                    )
                except Exception:
                    pass
        except Exception:
            pass

        if bool(getattr(client, '_menu_pause_active', False)):
            client._draw_menu_pause_overlay()

    def draw_story_practice_exams(self, client: Any) -> None:
        try:
            client.screen.fill((0, 0, 0))
        except Exception:
            pass

        w = int(client.screen.get_width())
        h = int(client.screen.get_height())

        bg = getattr(client, '_story_menu4_scaled', None) or getattr(client, '_story_menu3_scaled', None) or getattr(client, '_story_menu2_scaled', None)
        if bg is not None:
            try:
                bx = int((w - int(bg.get_width())) / 2)
                by = int((h - int(bg.get_height())) / 2)
                client.screen.blit(bg, (bx, by))
            except Exception:
                pass

        client._menu_buttons = []
        try:
            box_h = int(max(140, h * 0.30))
            box_w = int(max(420, w * 0.88))
            box_x = int((w - box_w) / 2)
            box_y = int(h - box_h - h * 0.06)
            rect = self._pygame.Rect(box_x, box_y, box_w, box_h)

            panel = self._pygame.Surface((int(rect.w), int(rect.h)), flags=self._pygame.SRCALPHA)
            panel.fill((0, 0, 0, 170))
            client.screen.blit(panel, (int(rect.x), int(rect.y)))
            self._pygame.draw.rect(client.screen, (255, 255, 255), rect, width=2, border_radius=12)

            pad = int(max(12, round(18 * float(getattr(client, 'ui_scale', 1.0) or 1.0))))
            text_x = int(rect.x + pad)
            text_y = int(rect.y + pad)
            msg = 'Practice for Exams\n\nChoose a challenge:'
            lines = client._wrap_text(msg, client.ui_font, int(rect.w - 2 * pad))
            y = text_y
            for line in lines[:5]:
                surf = client.ui_font.render(line, True, (245, 245, 245))
                client.screen.blit(surf, (text_x, y))
                y += int(surf.get_height() + max(3, round(6 * float(getattr(client, 'ui_scale', 1.0) or 1.0))))

            btn_img_normal = getattr(client, '_menu_button_scaled', None)
            btn_img_hover = getattr(client, '_menu_button_hover_scaled', None) or btn_img_normal
            btn_img_pressed = getattr(client, '_menu_button_pressed_scaled', None) or btn_img_hover or btn_img_normal

            bw = int(btn_img_normal.get_width()) if btn_img_normal is not None else int(min(w * 0.34, 520))
            bh = int(btn_img_normal.get_height()) if btn_img_normal is not None else 84
            bw = max(220, bw)
            bh = max(60, bh)
            gap = int(max(8, round(bh * 0.18)))

            ids = [
                ('practice_speed_test', 'Speed test'),
                ('practice_1v1', '1v1'),
                ('back', 'Back'),
            ]
            stack_h = len(ids) * bh + (len(ids) - 1) * gap
            bx = int(rect.right - pad - bw)
            by0 = int(rect.bottom - pad - stack_h)

            client._menu_buttons = []
            for i, (bid, label) in enumerate(ids):
                client._menu_buttons.append({'id': bid, 'label': label, 'rect': self._pygame.Rect(bx, by0 + i * (bh + gap), bw, bh)})

            try:
                mouse_pos = self._pygame.mouse.get_pos()
            except Exception:
                mouse_pos = (0, 0)
            try:
                mouse_down = bool(self._pygame.mouse.get_pressed()[0])
            except Exception:
                mouse_down = False

            sel = 0
            try:
                sel = int(getattr(client, '_menu_selected', 0) or 0)
            except Exception:
                sel = 0
            sel = max(0, min(sel, max(0, len(client._menu_buttons) - 1)))
            try:
                client._menu_selected = int(sel)
            except Exception:
                pass

            for i, b in enumerate(client._menu_buttons):
                brect = b.get('rect')
                if brect is None:
                    continue
                try:
                    hovered = bool(brect.collidepoint(mouse_pos))
                except Exception:
                    hovered = False
                pressed = bool(mouse_down and hovered)
                try:
                    if client._ui_is_button_flashed('menu', str(b.get('id'))):
                        pressed = True
                except Exception:
                    pass

                if btn_img_normal is None:
                    self._pygame.draw.rect(client.screen, (40, 40, 60), brect, border_radius=12)
                    self._pygame.draw.rect(client.screen, (180, 180, 200), brect, width=2, border_radius=12)
                else:
                    src = btn_img_pressed if pressed else (btn_img_hover if (hovered or i == sel) else btn_img_normal)
                    client.screen.blit(src, (int(brect.x), int(brect.y)))
                try:
                    client._blit_fitted_text(
                        str(b.get('label', '')),
                        brect,
                        color=(255, 255, 255),
                        base_px=int(getattr(client, '_menu_button_font_px', 40) or 40),
                        max_lines=2,
                    )
                except Exception:
                    pass

            try:
                st = str(getattr(client, '_menu_status_text', '') or '').strip()
                if st:
                    status = client.ui_font.render(st, True, (240, 240, 200))
                    client.screen.blit(status, (int(w * 0.06), int(h * 0.90)))
            except Exception:
                pass
        except Exception:
            pass

        if bool(getattr(client, '_menu_pause_active', False)):
            client._draw_menu_pause_overlay()

    def draw_story_examinations(self, client: Any) -> None:
        # Placeholder until the examinations scene/image is provided.
        try:
            client.screen.fill((0, 0, 0))
        except Exception:
            pass

        w = int(client.screen.get_width())
        h = int(client.screen.get_height())

        bg = getattr(client, '_story_menu4_scaled', None) or getattr(client, '_story_menu3_scaled', None) or getattr(client, '_story_menu2_scaled', None)
        if bg is not None:
            try:
                bx = int((w - int(bg.get_width())) / 2)
                by = int((h - int(bg.get_height())) / 2)
                client.screen.blit(bg, (bx, by))
            except Exception:
                pass

        client._menu_buttons = []
        try:
            box_h = int(max(140, h * 0.30))
            box_w = int(max(420, w * 0.88))
            box_x = int((w - box_w) / 2)
            box_y = int(h - box_h - h * 0.06)
            rect = self._pygame.Rect(box_x, box_y, box_w, box_h)

            panel = self._pygame.Surface((int(rect.w), int(rect.h)), flags=self._pygame.SRCALPHA)
            panel.fill((0, 0, 0, 170))
            client.screen.blit(panel, (int(rect.x), int(rect.y)))
            self._pygame.draw.rect(client.screen, (255, 255, 255), rect, width=2, border_radius=12)

            pad = int(max(12, round(18 * float(getattr(client, 'ui_scale', 1.0) or 1.0))))
            text_x = int(rect.x + pad)
            text_y = int(rect.y + pad)
            msg = "Examinations\n\n(Coming soon — you said you'll work on the next picture.)"
            lines = client._wrap_text(msg, client.ui_font, int(rect.w - 2 * pad))
            y = text_y
            for line in lines[:6]:
                surf = client.ui_font.render(line, True, (245, 245, 245))
                client.screen.blit(surf, (text_x, y))
                y += int(surf.get_height() + max(3, round(6 * float(getattr(client, 'ui_scale', 1.0) or 1.0))))

            btn_img_normal = getattr(client, '_menu_button_scaled', None)
            btn_img_hover = getattr(client, '_menu_button_hover_scaled', None) or btn_img_normal
            btn_img_pressed = getattr(client, '_menu_button_pressed_scaled', None) or btn_img_hover or btn_img_normal

            bw = int(btn_img_normal.get_width()) if btn_img_normal is not None else int(min(w * 0.34, 520))
            bh = int(btn_img_normal.get_height()) if btn_img_normal is not None else 84
            bw = max(220, bw)
            bh = max(60, bh)
            bx = int(rect.right - pad - bw)
            by = int(rect.bottom - pad - bh)

            client._menu_buttons = [
                {'id': 'back', 'label': 'Back', 'rect': self._pygame.Rect(bx, by, bw, bh)},
            ]

            try:
                mouse_pos = self._pygame.mouse.get_pos()
            except Exception:
                mouse_pos = (0, 0)
            try:
                mouse_down = bool(self._pygame.mouse.get_pressed()[0])
            except Exception:
                mouse_down = False

            hovered = False
            try:
                hovered = bool(client._menu_buttons[0]['rect'].collidepoint(mouse_pos))
            except Exception:
                hovered = False
            pressed = bool(mouse_down and hovered)
            try:
                if client._ui_is_button_flashed('menu', str(client._menu_buttons[0].get('id'))):
                    pressed = True
            except Exception:
                pass

            brect = client._menu_buttons[0]['rect']
            if btn_img_normal is None:
                self._pygame.draw.rect(client.screen, (40, 40, 60), brect, border_radius=12)
                self._pygame.draw.rect(client.screen, (180, 180, 200), brect, width=2, border_radius=12)
            else:
                src = btn_img_pressed if pressed else (btn_img_hover if hovered else btn_img_normal)
                client.screen.blit(src, (int(brect.x), int(brect.y)))
            try:
                client._blit_fitted_text('Back', brect, color=(255, 255, 255), base_px=int(getattr(client, '_menu_button_font_px', 40) or 40), max_lines=1)
            except Exception:
                pass
        except Exception:
            pass

        if bool(getattr(client, '_menu_pause_active', False)):
            client._draw_menu_pause_overlay()
