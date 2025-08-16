import pygame
import os
from typing import Dict, Optional, Tuple


class SettingsUI:
    """
    Lightweight settings overlay with a few sliders and toggles.
    """

    def __init__(self, screen: pygame.Surface, config_service, on_apply_callbacks: Dict[str, callable], on_get_recommendation: callable = None, on_apply_recommendation: callable = None, asset_path: Optional[str] = None):
        self.screen = screen
        self.config = config_service
        self.on_apply = on_apply_callbacks or {}
        self.on_get_recommendation = on_get_recommendation
        self.on_apply_recommendation = on_apply_recommendation

        # layout
        self.width = screen.get_width()
        self.height = screen.get_height()
        self.font_title = pygame.font.SysFont(None, 48)
        self.font = pygame.font.SysFont(None, 28)
        self.small = pygame.font.SysFont(None, 22)

        # widget rects
        self.widgets: Dict[str, pygame.Rect] = {}
        self.visible = False
        self._dragging_key: Optional[str] = None
        self.active_tab = 'Graphics'  # Graphics | Audio | Controls
        self.rebinding_action: Optional[str] = None
        # No scrolling by default; keep everything within panel content
        self.scroll_y = 0
        # Slider ranges per setting key
        self.slider_ranges = {
            'master_volume': (0.0, 1.0),
            'music_volume': (0.0, 1.0),
            'brightness': (0.3, 1.0),
            'ui_scale': (0.8, 1.5),
        }

        # Theming assets (optional)
        self.ui_assets: Dict[str, Optional[pygame.Surface]] = {}
        # Base asset path (e.g., puzzleassets)
        self.asset_path = asset_path or 'puzzleassets'
        self._load_ui_assets()

    def update_screen(self, screen: pygame.Surface):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()

    def open(self):
        self.visible = True

    def close(self):
        self.visible = False

    def is_open(self) -> bool:
        return self.visible

    def handle_events(self, events) -> Optional[str]:
        if not self.visible:
            return None
        for e in events:
            # Handle tab clicks
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                for t in ("Graphics", "Audio", "Controls"):
                    r = self.widgets.get(f"tab_{t}")
                    if r and r.collidepoint(e.pos):
                        self.active_tab = t
                        self._dragging_key = None
                        self.rebinding_action = None
                        return None
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                self.close()
                return "close"
            # Scroll disabled; keep content fitted within panel
            if e.type == pygame.MOUSEWHEEL or (e.type == pygame.MOUSEBUTTONDOWN and e.button in (4, 5)):
                continue
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                mx, my = e.pos
                # sliders (based on active tab) — check both bar and knob
                slider_keys = []
                if self.active_tab == 'Graphics':
                    slider_keys = ["brightness"]
                elif self.active_tab == 'Audio':
                    slider_keys = ["master_volume", "music_volume", "ui_scale"] if False else ["master_volume", "music_volume"]
                # Also allow ui_scale on Graphics
                if self.active_tab == 'Graphics':
                    slider_keys.append("ui_scale")
                for key in slider_keys:
                    bar = self.widgets.get(f"bar_{key}")
                    knob = self.widgets.get(f"knob_{key}")
                    if (bar and bar.collidepoint(mx, my)) or (knob and knob.collidepoint(mx, my)):
                        self._dragging_key = key
                        self._set_slider_from_mouse(key, bar, mx)
                        self._apply_immediate(key)
                # toggles (based on active tab)
                toggle_keys = []
                if self.active_tab == 'Graphics':
                    toggle_keys = ["fullscreen", "native_fullscreen", "borderless", "vsync", "particle_effects", "show_fps"]
                for key in toggle_keys:
                    box = self.widgets.get(f"toggle_{key}")
                    if box and box.collidepoint(mx, my):
                        self._toggle_bool(key)
                        self._apply_immediate(key)
                # Recommendation apply
                rec_btn = self.widgets.get('rec_apply')
                if rec_btn:
                    btn_rect, action_key = rec_btn
                    if btn_rect.collidepoint(mx, my) and callable(self.on_apply_recommendation):
                        try:
                            self.on_apply_recommendation(action_key)
                        except Exception:
                            pass
                # back button
                back = self.widgets.get("btn_back")
                if back and back.collidepoint(mx, my):
                    self.close()
                    return "close"
                # controls rebinding
                if self.active_tab == 'Controls':
                    for k, r in self.widgets.items():
                        if k.startswith('bind_') and r.collidepoint(mx, my):
                            self.rebinding_action = k.replace('bind_', '')
                            return None
            if e.type == pygame.KEYDOWN and self.rebinding_action:
                # Save binding via config (settings service) so it persists
                self.config.update({f"bind_{self.rebinding_action}": int(e.key)})
                self.rebinding_action = None
            if e.type == pygame.MOUSEMOTION and self._dragging_key:
                key = self._dragging_key
                bar = self.widgets.get(f"bar_{key}")
                if bar:
                    self._set_slider_from_mouse(key, bar, e.pos[0])
                    self._apply_immediate(key)
            if e.type == pygame.MOUSEBUTTONUP and e.button == 1 and self._dragging_key:
                self._dragging_key = None
        return None

    def _set_slider_from_mouse(self, key: str, bar_rect: pygame.Rect, mx: int):
        t = (mx - bar_rect.x) / max(1, bar_rect.width)
        t = max(0.0, min(1.0, t))
        min_v, max_v = self.slider_ranges.get(key, (0.0, 1.0))
        val = min_v + t * (max_v - min_v)
        # Round sensibly
        prec = 2 if key in ('ui_scale', 'brightness', 'master_volume', 'music_volume') else 2
        self.config.update({key: round(val, prec)})

    def _toggle_bool(self, key: str):
        cur = bool(self.config.get(key, False))
        self.config.update({key: not cur})

    def _apply_immediate(self, key: str):
        cb = self.on_apply.get(key)
        if callable(cb):
            try:
                cb(self.config.get(key))
            except Exception:
                pass

    def draw(self):
        if not self.visible:
            return
        # dim background
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        # Larger, proportional settings panel (reduce outer margin further for a bigger panel)
        panel_margin = max(8, int(min(self.width, self.height) * 0.01))
        panel_w = max(720, self.width - 2 * panel_margin)
        panel_h = max(540, self.height - 2 * panel_margin)
        panel_x = (self.width - panel_w) // 2
        panel_y = (self.height - panel_h) // 2
        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        # Use a slightly larger border value to match the visible nine-slice edge thickness
        border_px = 36
        if self.ui_assets.get('panel_9slice'):
            self._draw_nine_slice(panel_rect, self.ui_assets['panel_9slice'], border=border_px)
        else:
            pygame.draw.rect(self.screen, (35, 35, 45), panel_rect, border_radius=12)
            pygame.draw.rect(self.screen, (120, 120, 160), panel_rect, 2, border_radius=12)

        # Content rect constrained to inner area of nine-slice
        content_rect = pygame.Rect(
            panel_x + border_px,
            panel_y + border_px,
            panel_w - 2 * border_px,
            panel_h - 2 * border_px,
        )
        # An extra safe inset so UI never kisses the rounded corners
        content_inner = content_rect.inflate(-16, -16)

        # Horizontal offset to shift content inside the panel without moving the panel itself
        content_offset_x = 250
        title = self.font_title.render("Settings", True, (255, 255, 255))
        self.screen.blit(title, (content_inner.x + 12 + content_offset_x, content_inner.y + 20))

        # Tabs
        tabs = ["Graphics", "Audio", "Controls"]
        tab_x = content_inner.x + 12 + content_offset_x
        tab_y = content_inner.y + 68
        for t in tabs:
            is_active = (t == self.active_tab)
            tw = 120
            th = 28
            rect = pygame.Rect(tab_x, tab_y, tw, th)
            img = self.ui_assets['tab_active'] if is_active else self.ui_assets['tab_inactive']
            if img:
                scaled = pygame.transform.smoothscale(img, (tw, th))
                self.screen.blit(scaled, (rect.x, rect.y))
            else:
                pygame.draw.rect(self.screen, (70, 80, 110) if is_active else (55, 60, 85), rect, border_radius=6)
                pygame.draw.rect(self.screen, (160, 170, 210), rect, 2, border_radius=6)
            label = self.small.render(t, True, (255, 255, 255))
            self.screen.blit(label, label.get_rect(center=rect.center))
            self.widgets[f"tab_{t}"] = rect
            tab_x += tw + 10

        # Content area constrained to inner panel with margins
        viewport_y = tab_y + 56
        content_margin = 96
        x = content_inner.x + content_margin + content_offset_x
        col_w = max(120, content_inner.width - 2 * content_margin - content_offset_x)
        y = viewport_y
        # Clip all content drawing to inner content area to guarantee no overflow
        prev_clip = self.screen.get_clip()
        self.screen.set_clip(content_inner)

        if self.active_tab == 'Graphics':
            # Sliders
            y = self._draw_slider("Interface Scale", "ui_scale", x, y, col_w)
            y = self._draw_slider("Brightness", "brightness", x, y, col_w)
            # Toggles
            y += 16
            y = self._draw_toggle("Fullscreen", "fullscreen", x, y)
            y = self._draw_toggle("Native Fullscreen", "native_fullscreen", x, y)
            y = self._draw_toggle("Borderless Windowed", "borderless", x, y)
            y = self._draw_toggle("V-Sync", "vsync", x, y)
            y = self._draw_toggle("Particles", "particle_effects", x, y)
            y = self._draw_toggle("Show FPS", "show_fps", x, y)
            # Recommendation block
            y += 12
            y = self._draw_recommendation(x, y, col_w)
        elif self.active_tab == 'Audio':
            y = self._draw_slider("Master Volume", "master_volume", x, y, col_w)
            y = self._draw_slider("Music Volume", "music_volume", x, y, col_w)
        elif self.active_tab == 'Controls':
            y = self._draw_controls(x, y, col_w)

        # (Info line removed to avoid clipping controls)

        # Footer/back
        # Back button (skinned if available)
        btn_w, btn_h = 150, 40
        btn_x = content_inner.right - btn_w - 12
        btn_y = content_inner.bottom - btn_h - 12
        btn_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
        self._draw_button(btn_rect, "Back")
        self.widgets["btn_back"] = btn_rect

        # Restore previous clip
        self.screen.set_clip(prev_clip)

    def _draw_slider(self, label: str, key: str, x: int, y: int, width: int) -> int:
        self.screen.blit(self.font.render(label, True, (230, 230, 240)), (x, y))
        y += 24
        bar_h = 10
        # Keep slider within the provided column width (do not extend beyond panel content)
        width = max(120, width)
        # Add internal padding so knob stays well inside rounded panel edges
        bar_x = x + 20
        usable_w = max(100, width - 40)
        bar_rect = pygame.Rect(bar_x, y, usable_w, bar_h)
        if self.ui_assets.get('slider_track'):
            track_img = pygame.transform.smoothscale(self.ui_assets['slider_track'], (usable_w, bar_h))
            self.screen.blit(track_img, (bar_x, y))
        else:
            pygame.draw.rect(self.screen, (60, 60, 80), bar_rect, border_radius=4)

        min_v, max_v = self.slider_ranges.get(key, (0.0, 1.0))
        val = float(self.config.get(key, max_v))
        # Normalize to [0,1]
        if max_v > min_v:
            t = (val - min_v) / (max_v - min_v)
        else:
            t = 1.0
        t = max(0.0, min(1.0, t))
        knob_x = int(bar_x + t * usable_w)
        knob = pygame.Rect(knob_x - 8, y - 8, 16, 28)
        if self.ui_assets.get('slider_knob'):
            knob_img = pygame.transform.smoothscale(self.ui_assets['slider_knob'], (knob.width, knob.height))
            self.screen.blit(knob_img, (knob.x, knob.y))
        else:
            pygame.draw.rect(self.screen, (180, 200, 255), knob, border_radius=6)
        # value text (clamped to the right edge)
        vtxt = self.small.render(f"{val:.2f}", True, (200, 200, 220))
        vpos_x = min(bar_x + usable_w - vtxt.get_width(), bar_x + usable_w - 36)
        self.screen.blit(vtxt, (vpos_x, y - 10))

        self.widgets[f"bar_{key}"] = bar_rect
        self.widgets[f"knob_{key}"] = knob
        return y + 36

    def _draw_toggle(self, label: str, key: str, x: int, y: int) -> int:
        flag = bool(self.config.get(key, False))
        # If toggle skin exists (2 frames horizontally), draw it scaled to a compact height
        toggle_img = self.ui_assets.get('toggle_strip')
        if toggle_img:
            fw = toggle_img.get_width() // 2
            fh = toggle_img.get_height()
            src = pygame.Rect(fw if flag else 0, 0, fw, fh)
            target_h = 32
            target_w = max(56, int(fw * (target_h / max(1, fh))))
            dest = pygame.Rect(x, y, target_w, target_h)
            scaled = pygame.transform.smoothscale(toggle_img.subsurface(src), (dest.width, dest.height))
            self.screen.blit(scaled, (dest.x, dest.y))
            text_x = dest.right + 12
            text_y = dest.y + (dest.height - 20) // 2
            self.screen.blit(self.font.render(label, True, (230, 230, 240)), (text_x, text_y))
            self.widgets[f"toggle_{key}"] = dest
            return dest.bottom + 12
        else:
            box = pygame.Rect(x, y, 28, 18)
            pygame.draw.rect(self.screen, (60, 60, 80), box, border_radius=9)
            knob_x = box.x + (box.width - 16 - 2 if flag else 2)
            knob = pygame.Rect(knob_x, box.y + 2, 16, 14)
            pygame.draw.rect(self.screen, (120, 220, 140) if flag else (180, 180, 200), knob, border_radius=7)
            self.screen.blit(self.font.render(label, True, (230, 230, 240)), (x + 40, y - 2))
            self.widgets[f"toggle_{key}"] = box
            return y + 32

    def _draw_controls(self, x: int, y: int, width: int) -> int:
        self.screen.blit(self.font.render("Click a binding to rebind, press any key", True, (230, 230, 240)), (x, y))
        y += 32
        actions = [
            ("Rotate Left", "move_up"),
            ("Rotate Right", "move_down"),
            ("Move Left", "move_left"),
            ("Move Right", "move_right"),
            ("Soft Drop", "action"),
            ("Music: Play/Pause", "music_pause"),
            ("Music: Next", "music_next"),
            ("Music: Prev", "music_prev"),
            ("Music: Volume Up", "music_vol_up"),
            ("Music: Volume Down", "music_vol_down"),
        ]
        # Constrain rows within the content column with a bit of inner padding
        row_inset_x = x + 16
        # Reduce horizontal size by an additional 200 px as requested
        row_width = max(160, width - 32 - 200)
        for label, action in actions:
            row = pygame.Rect(row_inset_x, y, row_width, 32)
            pygame.draw.rect(self.screen, (50, 55, 75), row, border_radius=6)
            pygame.draw.rect(self.screen, (110, 120, 160), row, 1, border_radius=6)
            self.screen.blit(self.small.render(label, True, (230, 230, 240)), (row_inset_x + 10, y + 7))
            # value box
            keybox = pygame.Rect(row_inset_x + row_width - 200, y + 4, 180, 24)
            pygame.draw.rect(self.screen, (65, 70, 95), keybox, border_radius=6)
            pygame.draw.rect(self.screen, (140, 150, 190), keybox, 1, border_radius=6)
            cur = self.config.get(f"bind_{action}")
            if not isinstance(cur, (int, float)):
                # Friendly default display values; not persisted unless changed
                default_map = {
                    'music_pause': pygame.K_p,
                    'music_next': pygame.K_RIGHTBRACKET,
                    'music_prev': pygame.K_LEFTBRACKET,
                    'music_vol_up': pygame.K_EQUALS,
                    'music_vol_down': pygame.K_MINUS,
                }
                cur = default_map.get(action, 0)
            keyname = pygame.key.name(int(cur)) if int(cur) > 0 else "(unset)"
            text = ("Press a key..." if self.rebinding_action == action else keyname)
            self.screen.blit(self.small.render(text, True, (255, 255, 255)), self.small.render(text, True, (255,255,255)).get_rect(center=keybox.center))
            self.widgets[f"bind_{action}"] = keybox
            y += 40
        return y

    def _draw_recommendation(self, x: int, y: int, width: int) -> int:
        # Ask game for a recommendation based on current screen and display
        text, action_key = None, None
        if callable(self.on_get_recommendation):
            try:
                rec = self.on_get_recommendation()
                if rec and isinstance(rec, dict):
                    text = rec.get('text')
                    action_key = rec.get('action_key')
            except Exception:
                pass
        if not text:
            return y
        row = pygame.Rect(x, y, width, 52)
        pygame.draw.rect(self.screen, (50, 70, 55), row, border_radius=8)
        pygame.draw.rect(self.screen, (120, 180, 130), row, 2, border_radius=8)
        self.screen.blit(self.small.render(text, True, (230, 255, 230)), (x + 12, y + 8))
        btn = pygame.Rect(x + width - 140, y + 10, 120, 30)
        pygame.draw.rect(self.screen, (70, 100, 75), btn, border_radius=6)
        pygame.draw.rect(self.screen, (150, 210, 160), btn, 2, border_radius=6)
        self.screen.blit(self.small.render("Apply", True, (255, 255, 255)), self.small.render("Apply", True, (255,255,255)).get_rect(center=btn.center))
        self.widgets['rec_apply'] = (btn, action_key)
        return y + 60

    def _load_ui_assets(self) -> None:
        """Load optional UI theming assets from puzzleassets/menus."""
        try:
            # Use provided asset path (game's ASSET_PATH) and menus subfolder
            menus = os.path.join(self.asset_path, 'menus')
            def _opt(name: str) -> Optional[pygame.Surface]:
                path = os.path.join(menus, name)
                return pygame.image.load(path) if os.path.exists(path) else None
            self.ui_assets['panel_9slice'] = _opt('panel_9slice.png')
            self.ui_assets['tab_active'] = _opt('tab_active.png')
            self.ui_assets['tab_inactive'] = _opt('tab_inactive.png')
            self.ui_assets['toggle_strip'] = _opt('toggle_strip.png')
            self.ui_assets['slider_track'] = _opt('slider_track.png')
            self.ui_assets['slider_knob'] = _opt('slider_knob.png')
            self.ui_assets['button_normal'] = _opt('button_normal.png')
            self.ui_assets['button_hover'] = _opt('button_hover.png')
            self.ui_assets['button_pressed'] = _opt('button_pressed.png')
            # Optional icons
            self.ui_assets['icon_gear'] = _opt('icon_gear.png')
            self.ui_assets['icon_music'] = _opt('icon_music.png')
            self.ui_assets['icon_gamepad'] = _opt('icon_gamepad.png')
        except Exception:
            pass

    def _draw_nine_slice(self, dest_rect: pygame.Rect, img: pygame.Surface, border: int = 24) -> None:
        """Draw a 9-slice scaled panel to fit dest_rect."""
        try:
            iw, ih = img.get_width(), img.get_height()
            b = min(border, iw // 3, ih // 3)
            # Source rects
            s = {
                'tl': pygame.Rect(0, 0, b, b),
                'tr': pygame.Rect(iw - b, 0, b, b),
                'bl': pygame.Rect(0, ih - b, b, b),
                'br': pygame.Rect(iw - b, ih - b, b, b),
                't': pygame.Rect(b, 0, iw - 2*b, b),
                'b': pygame.Rect(b, ih - b, iw - 2*b, b),
                'l': pygame.Rect(0, b, b, ih - 2*b),
                'r': pygame.Rect(iw - b, b, b, ih - 2*b),
                'c': pygame.Rect(b, b, iw - 2*b, ih - 2*b),
            }
            # Dest rects
            d = {
                'tl': pygame.Rect(dest_rect.left, dest_rect.top, b, b),
                'tr': pygame.Rect(dest_rect.right - b, dest_rect.top, b, b),
                'bl': pygame.Rect(dest_rect.left, dest_rect.bottom - b, b, b),
                'br': pygame.Rect(dest_rect.right - b, dest_rect.bottom - b, b, b),
                't': pygame.Rect(dest_rect.left + b, dest_rect.top, dest_rect.width - 2*b, b),
                'b': pygame.Rect(dest_rect.left + b, dest_rect.bottom - b, dest_rect.width - 2*b, b),
                'l': pygame.Rect(dest_rect.left, dest_rect.top + b, b, dest_rect.height - 2*b),
                'r': pygame.Rect(dest_rect.right - b, dest_rect.top + b, b, dest_rect.height - 2*b),
                'c': pygame.Rect(dest_rect.left + b, dest_rect.top + b, dest_rect.width - 2*b, dest_rect.height - 2*b),
            }
            # Blit corners
            self.screen.blit(img.subsurface(s['tl']), d['tl'])
            self.screen.blit(img.subsurface(s['tr']), d['tr'])
            self.screen.blit(img.subsurface(s['bl']), d['bl'])
            self.screen.blit(img.subsurface(s['br']), d['br'])
            # Edges
            t_scaled = pygame.transform.smoothscale(img.subsurface(s['t']), (d['t'].width, d['t'].height))
            b_scaled = pygame.transform.smoothscale(img.subsurface(s['b']), (d['b'].width, d['b'].height))
            l_scaled = pygame.transform.smoothscale(img.subsurface(s['l']), (d['l'].width, d['l'].height))
            r_scaled = pygame.transform.smoothscale(img.subsurface(s['r']), (d['r'].width, d['r'].height))
            self.screen.blit(t_scaled, d['t'])
            self.screen.blit(b_scaled, d['b'])
            self.screen.blit(l_scaled, d['l'])
            self.screen.blit(r_scaled, d['r'])
            # Center
            c_scaled = pygame.transform.smoothscale(img.subsurface(s['c']), (d['c'].width, d['c'].height))
            self.screen.blit(c_scaled, d['c'])
        except Exception:
            # Fallback to simple rect if anything goes wrong
            pygame.draw.rect(self.screen, (35, 35, 45), dest_rect, border_radius=12)
            pygame.draw.rect(self.screen, (120, 120, 160), dest_rect, 2, border_radius=12)

    def _draw_button(self, rect: pygame.Rect, label: str) -> None:
        """Draw a skinned button if assets exist, otherwise simple rounded button."""
        try:
            mouse_pos = pygame.mouse.get_pos()
            hover = rect.collidepoint(mouse_pos)
            pressed = hover and pygame.mouse.get_pressed()[0]
            img = None
            if pressed and self.ui_assets.get('button_pressed'):
                img = self.ui_assets['button_pressed']
            elif hover and self.ui_assets.get('button_hover'):
                img = self.ui_assets['button_hover']
            elif self.ui_assets.get('button_normal'):
                img = self.ui_assets['button_normal']
            if img:
                scaled = pygame.transform.smoothscale(img, (rect.width, rect.height))
                self.screen.blit(scaled, (rect.x, rect.y))
            else:
                pygame.draw.rect(self.screen, (70, 80, 110), rect, border_radius=8)
                pygame.draw.rect(self.screen, (150, 160, 200), rect, 2, border_radius=8)
            txt = self.font.render(label, True, (255, 255, 255))
            self.screen.blit(txt, txt.get_rect(center=rect.center))
        except Exception:
            pygame.draw.rect(self.screen, (70, 80, 110), rect, border_radius=8)
            pygame.draw.rect(self.screen, (150, 160, 200), rect, 2, border_radius=8)
            txt = self.font.render(label, True, (255, 255, 255))
            self.screen.blit(txt, txt.get_rect(center=rect.center))

