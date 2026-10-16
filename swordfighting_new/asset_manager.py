from __future__ import annotations

import os
from typing import TYPE_CHECKING

import pygame

from swordfighting_new.attacks.garbage_pattern import SwordType, get_sword_asset_filename
from swordfighting_new.util.resources import assets_dir

if TYPE_CHECKING:
    from swordfighting_new.pygame_client import PygameClient


class AssetManager:
    def get_coin_icon_scaled(self, client: "PygameClient", *, target_h: int) -> pygame.Surface | None:
        """Return a scaled coin icon surface (or None if unavailable)."""
        try:
            th = int(target_h)
        except Exception:
            th = 0
        th = max(6, min(256, th))

        raw = getattr(client, '_coin_icon_raw', None)
        if raw is None:
            try:
                base_dir = os.fspath(assets_dir())
                p = os.path.join(base_dir, 'currency', 'coins.png')
                if os.path.isfile(p):
                    raw = pygame.image.load(p).convert_alpha()
                    client._coin_icon_raw = raw
            except Exception:
                raw = None

        if raw is None:
            return None

        # Many icon PNGs contain a lot of transparent padding; trim so "target_h"
        # corresponds to the visible coin rather than the empty border.
        src = getattr(client, '_coin_icon_raw_trimmed', None)
        if src is None:
            try:
                src = self.trim_alpha_surface(raw)
                client._coin_icon_raw_trimmed = src
            except Exception:
                src = raw
        if src is None:
            return None

        try:
            sw, sh = int(src.get_width()), int(src.get_height())
        except Exception:
            return None
        if sh <= 0 or sw <= 0:
            return None

        try:
            cache = getattr(client, '_coin_icon_scaled_cache', None)
            if cache is None or (not isinstance(cache, dict)):
                cache = {}
                client._coin_icon_scaled_cache = cache
        except Exception:
            cache = None

        cache_key = (int(th), int(sw), int(sh))
        if isinstance(cache, dict):
            hit = cache.get(cache_key)
            if hit is not None:
                return hit

        try:
            scale = float(th) / float(sh)
            tw = max(1, int(round(float(sw) * scale)))
            surf = pygame.transform.smoothscale(src, (int(tw), int(th)))
        except Exception:
            return None

        try:
            if isinstance(cache, dict):
                cache[cache_key] = surf
        except Exception:
            pass
        return surf

    def load_menu_assets(self, client: "PygameClient") -> None:
        client._menu_bg = None
        client._menu_button_img = None
        client._menu_button_hover_img = None
        client._menu_button_pressed_img = None
        client._menu_icon_gamepad = None
        client._menu_icon_gear = None
        client._menu_title_wordmark = None
        client._story_menu1_img = None
        client._story_menu2_img = None
        client._story_menu3_img = None
        client._story_menu4_img = None
        client._story_menu5_img = None
        client._menu_bg_scaled = None
        client._menu_button_scaled = None
        client._menu_button_hover_scaled = None
        client._menu_button_pressed_scaled = None
        client._menu_icon_gamepad_scaled = None
        client._menu_icon_gear_scaled = None
        client._menu_title_wordmark_scaled = None
        client._story_menu1_scaled = None
        client._story_menu2_scaled = None
        client._story_menu3_scaled = None
        client._story_menu4_scaled = None
        client._story_menu5_scaled = None
        try:
            base_dir = os.fspath(assets_dir())
            menus_dir = os.path.join(base_dir, 'menus')
            bg_path = os.path.join(menus_dir, 'Official_mainmenu_background.png')
            btn_path = os.path.join(menus_dir, 'button_normal.png')
            btn_hover_path = os.path.join(menus_dir, 'button_hover.png')
            btn_pressed_path = os.path.join(menus_dir, 'button_pressed.png')
            btn_pressed_path_alt = os.path.join(menus_dir, 'button_ pressed.png')
            icon_gamepad_path = os.path.join(menus_dir, 'icon_gamepad.png')
            icon_gear_path = os.path.join(menus_dir, 'icon_gear.png')
            title_path = os.path.join(menus_dir, 'title_wordmark.png')
            story_menu1_path = os.path.join(menus_dir, 'menu1.png')
            story_menu2_path = os.path.join(menus_dir, 'menu2.png')
            story_menu3_path = os.path.join(menus_dir, 'menu3.png')
            # Story menu4/menu5: swap file mapping (art order is menu5 then menu4).
            story_menu4_path = os.path.join(menus_dir, 'menu5.png')
            story_menu5_path = os.path.join(menus_dir, 'menu4.png')

            if os.path.isfile(bg_path):
                client._menu_bg = pygame.image.load(bg_path).convert()
            if os.path.isfile(btn_path):
                client._menu_button_img = pygame.image.load(btn_path).convert_alpha()
            if os.path.isfile(btn_hover_path):
                client._menu_button_hover_img = pygame.image.load(btn_hover_path).convert_alpha()
            if os.path.isfile(btn_pressed_path):
                client._menu_button_pressed_img = pygame.image.load(btn_pressed_path).convert_alpha()
            elif os.path.isfile(btn_pressed_path_alt):
                client._menu_button_pressed_img = pygame.image.load(btn_pressed_path_alt).convert_alpha()
            if os.path.isfile(icon_gamepad_path):
                client._menu_icon_gamepad = pygame.image.load(icon_gamepad_path).convert_alpha()
            if os.path.isfile(icon_gear_path):
                client._menu_icon_gear = pygame.image.load(icon_gear_path).convert_alpha()
            if os.path.isfile(title_path):
                client._menu_title_wordmark = pygame.image.load(title_path).convert_alpha()
            if os.path.isfile(story_menu1_path):
                # Story/academy intro background.
                client._story_menu1_img = pygame.image.load(story_menu1_path).convert()
            if os.path.isfile(story_menu2_path):
                # Story/academy detail background.
                client._story_menu2_img = pygame.image.load(story_menu2_path).convert()
            if os.path.isfile(story_menu3_path):
                # Story/quarters background.
                client._story_menu3_img = pygame.image.load(story_menu3_path).convert()
            if os.path.isfile(story_menu4_path):
                # Story/outside-cabin background.
                client._story_menu4_img = pygame.image.load(story_menu4_path).convert()
            if os.path.isfile(story_menu5_path):
                # Story/inside-cabin (wake up) background.
                client._story_menu5_img = pygame.image.load(story_menu5_path).convert()
        except Exception:
            client._menu_bg = None
            client._menu_button_img = None
            client._menu_button_hover_img = None
            client._menu_button_pressed_img = None
            client._menu_icon_gamepad = None
            client._menu_icon_gear = None
            client._menu_title_wordmark = None
            client._story_menu1_img = None
            client._story_menu2_img = None
            client._story_menu3_img = None
            client._story_menu4_img = None
            client._story_menu5_img = None

        self.rebuild_menu_scaled_assets(client)

    def rebuild_menu_scaled_assets(self, client: "PygameClient") -> None:
        # Build scaled copies sized for the current window.
        try:
            w, h = int(client.screen.get_width()), int(client.screen.get_height())
        except Exception:
            return

        try:
            client._menu_button_state_scaled_cache.clear()
        except Exception:
            pass

        try:
            client._menu_last_size = (int(w), int(h))
        except Exception:
            client._menu_last_size = None

        try:
            if client._menu_bg is not None:
                client._menu_bg_scaled = pygame.transform.smoothscale(client._menu_bg, (w, h))
            else:
                client._menu_bg_scaled = None
        except Exception:
            client._menu_bg_scaled = None

        # Story menu1 background: keep native sizing, centered; only scale DOWN if too large.
        try:
            img = getattr(client, '_story_menu1_img', None)
            if img is None:
                client._story_menu1_scaled = None
            else:
                iw, ih = int(img.get_width()), int(img.get_height())
                if iw <= 0 or ih <= 0:
                    client._story_menu1_scaled = None
                else:
                    scale = min(1.0, float(w) / float(iw), float(h) / float(ih))
                    if scale < 0.999:
                        tw, th = max(1, int(round(iw * scale))), max(1, int(round(ih * scale)))
                        client._story_menu1_scaled = pygame.transform.smoothscale(img, (tw, th))
                    else:
                        client._story_menu1_scaled = img
        except Exception:
            client._story_menu1_scaled = None

        # Story menu2 background: keep native sizing, centered; only scale DOWN if too large.
        try:
            img = getattr(client, '_story_menu2_img', None)
            if img is None:
                client._story_menu2_scaled = None
            else:
                iw, ih = int(img.get_width()), int(img.get_height())
                if iw <= 0 or ih <= 0:
                    client._story_menu2_scaled = None
                else:
                    scale = min(1.0, float(w) / float(iw), float(h) / float(ih))
                    if scale < 0.999:
                        tw, th = max(1, int(round(iw * scale))), max(1, int(round(ih * scale)))
                        client._story_menu2_scaled = pygame.transform.smoothscale(img, (tw, th))
                    else:
                        client._story_menu2_scaled = img
        except Exception:
            client._story_menu2_scaled = None

        # Story menu3 background: keep native sizing, centered; only scale DOWN if too large.
        try:
            img = getattr(client, '_story_menu3_img', None)
            if img is None:
                client._story_menu3_scaled = None
            else:
                iw, ih = int(img.get_width()), int(img.get_height())
                if iw <= 0 or ih <= 0:
                    client._story_menu3_scaled = None
                else:
                    scale = min(1.0, float(w) / float(iw), float(h) / float(ih))
                    if scale < 0.999:
                        tw, th = max(1, int(round(iw * scale))), max(1, int(round(ih * scale)))
                        client._story_menu3_scaled = pygame.transform.smoothscale(img, (tw, th))
                    else:
                        client._story_menu3_scaled = img
        except Exception:
            client._story_menu3_scaled = None

        # Story menu4 background: keep native sizing, centered; only scale DOWN if too large.
        try:
            img = getattr(client, '_story_menu4_img', None)
            if img is None:
                client._story_menu4_scaled = None
            else:
                iw, ih = int(img.get_width()), int(img.get_height())
                if iw <= 0 or ih <= 0:
                    client._story_menu4_scaled = None
                else:
                    scale = min(1.0, float(w) / float(iw), float(h) / float(ih))
                    if scale < 0.999:
                        tw, th = max(1, int(round(iw * scale))), max(1, int(round(ih * scale)))
                        client._story_menu4_scaled = pygame.transform.smoothscale(img, (tw, th))
                    else:
                        client._story_menu4_scaled = img
        except Exception:
            client._story_menu4_scaled = None

        # Story menu5 background: keep native sizing, centered; only scale DOWN if too large.
        try:
            img = getattr(client, '_story_menu5_img', None)
            if img is None:
                client._story_menu5_scaled = None
            else:
                iw, ih = int(img.get_width()), int(img.get_height())
                if iw <= 0 or ih <= 0:
                    client._story_menu5_scaled = None
                else:
                    scale = min(1.0, float(w) / float(iw), float(h) / float(ih))
                    if scale < 0.999:
                        tw, th = max(1, int(round(iw * scale))), max(1, int(round(ih * scale)))
                        client._story_menu5_scaled = pygame.transform.smoothscale(img, (tw, th))
                    else:
                        client._story_menu5_scaled = img
        except Exception:
            client._story_menu5_scaled = None

        try:
            base_btn = getattr(client, '_menu_button_img', None) or getattr(client, '_menu_button_hover_img', None) or getattr(client, '_menu_button_pressed_img', None)
            if base_btn is None:
                client._menu_button_scaled = None
                client._menu_button_hover_scaled = None
                client._menu_button_pressed_scaled = None
            else:
                # Scale button to a reasonable size (based on board width)
                target_w = int(min(w * 0.38, 520))
                if target_w < 220:
                    target_w = 220
                aspect = float(base_btn.get_height()) / float(max(1, base_btn.get_width()))
                target_h = int(max(60, target_w * aspect))

                normal_src = getattr(client, '_menu_button_img', None) or base_btn
                hover_src = getattr(client, '_menu_button_hover_img', None) or normal_src
                pressed_src = getattr(client, '_menu_button_pressed_img', None) or hover_src

                client._menu_button_scaled = pygame.transform.smoothscale(normal_src, (target_w, target_h))
                client._menu_button_hover_scaled = pygame.transform.smoothscale(hover_src, (target_w, target_h))
                client._menu_button_pressed_scaled = pygame.transform.smoothscale(pressed_src, (target_w, target_h))
        except Exception:
            client._menu_button_scaled = None
            client._menu_button_hover_scaled = None
            client._menu_button_pressed_scaled = None

        # Prompt/menu icons (scale relative to button height)
        try:
            btn_h = int(client._menu_button_scaled.get_height()) if client._menu_button_scaled is not None else int(max(60, h * 0.08))
        except Exception:
            btn_h = int(max(60, h * 0.08))
        icon_h = max(16, int(round(btn_h * 0.55)))

        def _scale_icon(img):
            if img is None:
                return None
            try:
                iw, ih = int(img.get_width()), int(img.get_height())
                if iw <= 0 or ih <= 0:
                    return None
                icon_w = max(1, int(round(iw * (float(icon_h) / float(ih)))))
                return pygame.transform.smoothscale(img, (icon_w, icon_h))
            except Exception:
                return None

        client._menu_icon_gamepad_scaled = _scale_icon(getattr(client, '_menu_icon_gamepad', None))
        client._menu_icon_gear_scaled = _scale_icon(getattr(client, '_menu_icon_gear', None))

        # Title wordmark (scale to fit near the top)
        client._menu_title_wordmark_scaled = None
        try:
            img = getattr(client, '_menu_title_wordmark', None)
            if img is not None:
                iw, ih = int(img.get_width()), int(img.get_height())
                if iw > 0 and ih > 0:
                    # Intentionally large: user wants a prominent title.
                    max_w = int(round(w * 0.88))
                    # In smaller windows, avoid consuming too much vertical space.
                    max_h_frac = 0.24 if int(h) < 820 else 0.32
                    max_h = int(round(h * float(max_h_frac)))
                    max_w = max(240, max_w)
                    max_h = max(60, max_h)
                    scale = min(float(max_w) / float(iw), float(max_h) / float(ih))
                    # Allow upscale (up to ~2x) for punchy title.
                    scale = max(0.05, min(2.0, float(scale)))
                    tw, th = max(1, int(round(iw * scale))), max(1, int(round(ih * scale)))
                    client._menu_title_wordmark_scaled = pygame.transform.smoothscale(img, (tw, th))
        except Exception:
            client._menu_title_wordmark_scaled = None

        # Button rects depend on scaled sizes; rebuild lazily during draw.
        client._menu_buttons = []
        client._story_char_buttons = []
        client._menu_pause_buttons = []

    def get_scaled_menu_button_surface(
        self,
        client: "PygameClient",
        state: str,
        src: pygame.Surface | None,
        size: tuple[int, int],
    ) -> pygame.Surface | None:
        if src is None:
            return None
        try:
            w, h = int(size[0]), int(size[1])
        except Exception:
            return src
        w = max(1, int(w))
        h = max(1, int(h))

        try:
            sw, sh = int(src.get_width()), int(src.get_height())
        except Exception:
            return src
        if sw == w and sh == h:
            return src

        key = (str(state or 'normal'), int(w), int(h))
        try:
            cached = client._menu_button_state_scaled_cache.get(key)
            if cached is not None:
                return cached
        except Exception:
            cached = None

        try:
            scaled = pygame.transform.smoothscale(src, (w, h))
        except Exception:
            try:
                scaled = pygame.transform.scale(src, (w, h))
            except Exception:
                return src

        try:
            if len(client._menu_button_state_scaled_cache) > 48:
                client._menu_button_state_scaled_cache.clear()
            client._menu_button_state_scaled_cache[key] = scaled
        except Exception:
            pass
        return scaled

    def load_images(self, client: "PygameClient", *, cell_w: int, cell_h: int) -> None:
        # Load and scale PNGs for colored blocks and breakers
        client.block_images = {}
        client.breaker_images = {}
        client.garbage_images = {}
        try:
            cell_w = int(cell_w)
            cell_h = int(cell_h)
        except Exception:
            cell_w, cell_h = (40, 40)

        try:
            base_dir = os.fspath(assets_dir())
            colors = ('red', 'blue', 'yellow', 'green')

            def load_scaled(path: str):
                try:
                    img = pygame.image.load(path).convert_alpha()
                    # Slight inset to respect cell border
                    return pygame.transform.smoothscale(img, (max(1, cell_w - 2), max(1, cell_h - 2)))
                except Exception:
                    return None

            for c in colors:
                # Block tile art (do not use assets/sprites/*_sprite.png here; those are explosion strips).
                client.block_images[c] = load_scaled(os.path.join(base_dir, 'blocks', f'{c}block.png'))
                client.breaker_images[c] = load_scaled(os.path.join(base_dir, 'breakers', f'{c}breaker.png'))
                # Colorized garbage variants (optional)
                gpath = os.path.join(base_dir, 'sprinkle', f'{c}_garbage.png')
                surf = load_scaled(gpath)
                if surf is not None:
                    client.garbage_images[c] = surf
            # Generic garbage block fallback
            gen = load_scaled(os.path.join(base_dir, 'sprinkle', 'garbage_block.png'))
            if gen is not None:
                client.garbage_images['generic'] = gen
        except Exception:
            # Leave dicts empty; renderer will fall back to rects
            pass

    def load_explosion_sprites(self, client: "PygameClient", *, cell_w: int, cell_h: int) -> None:
        if not getattr(client, '_explode_enabled', True):
            return

        try:
            base_dir = os.fspath(assets_dir())
            sprites_dir = os.path.join(base_dir, 'sprites')
        except Exception:
            return

        try:
            cell_w = int(cell_w)
            cell_h = int(cell_h)
        except Exception:
            cell_w, cell_h = (40, 40)

        target_w = max(1, cell_w - 2)
        target_h = max(1, cell_h - 2)
        colors = ('red', 'blue', 'yellow', 'green')

        def _scale(img):
            try:
                return pygame.transform.smoothscale(img, (target_w, target_h))
            except Exception:
                try:
                    return pygame.transform.scale(img, (target_w, target_h))
                except Exception:
                    return None

        def _slice_sheet_3x3(img) -> list[pygame.Surface]:
            try:
                w, h = int(img.get_width()), int(img.get_height())
            except Exception:
                return []
            fw = max(1, w // 3)
            fh = max(1, h // 3)
            frames = []
            for i in range(9):
                cx = (i % 3) * fw
                cy = (i // 3) * fh
                try:
                    sub = pygame.Surface((fw, fh), flags=pygame.SRCALPHA)
                    sub.fill((0, 0, 0, 0))
                    sub.blit(img, (0, 0), pygame.Rect(cx, cy, fw, fh))
                    frames.append(sub)
                except Exception:
                    continue
            return frames

        def _slice_strip(img, n: int) -> list[pygame.Surface]:
            try:
                w, h = int(img.get_width()), int(img.get_height())
            except Exception:
                return []
            n = max(1, int(n))
            if n == 1:
                return [img]
            frames = []
            for i in range(n):
                try:
                    x0 = int(round((i * w) / float(n)))
                    x1 = int(round(((i + 1) * w) / float(n)))
                    if x1 <= x0:
                        continue
                    sw = max(1, x1 - x0)
                    sub = pygame.Surface((sw, h), flags=pygame.SRCALPHA)
                    sub.fill((0, 0, 0, 0))
                    sub.blit(img, (0, 0), pygame.Rect(x0, 0, sw, h))
                    frames.append(sub)
                except Exception:
                    continue
            return frames

        for color in colors:
            # Explosion animation assets.
            # IMPORTANT: any filename containing "sheet" must never be used.
            # Only allow the canonical per-color strip sprites.
            candidates: list[str] = [os.path.join(sprites_dir, f'{color}_sprite.png')]

            img = None
            chosen = None
            for p in candidates:
                try:
                    base = os.path.basename(str(p or '')).strip().lower()
                    if 'sheet' in base:
                        continue
                    if os.path.exists(p):
                        img = pygame.image.load(p).convert_alpha()
                        chosen = p
                        break
                except Exception:
                    img = None
                    chosen = None

            if img is None:
                continue

            base_name = ''
            try:
                base_name = os.path.basename(str(chosen or '')).strip().lower()
            except Exception:
                base_name = ''
            # Heuristics:
            # - Very wide images are horizontal strips.
            # - Square-ish images are treated as sheets and will be rejected unless slice succeeds.
            try:
                iw, ih = int(img.get_width()), int(img.get_height())
            except Exception:
                iw, ih = 0, 0
            try:
                ratio = float(iw) / float(max(1, ih))
            except Exception:
                ratio = 0.0

            is_sheet = bool(
                (iw > 0 and ih > 0 and 0.85 <= ratio <= 1.15)
            )
            is_strip = bool((not is_sheet) and (base_name.endswith('_sprite.png') or ratio >= 2.4))

            frames = []
            if is_sheet:
                frames = _slice_sheet_3x3(img)
            elif is_strip:
                frames = _slice_strip(img, int(getattr(client, '_explode_strip_frames', 9) or 9))
            # Never fall back to drawing a whole sheet/strip image scaled into a cell;
            # that looks like a tiny noisy tile (often mistaken for "particle" glitches).
            if not frames:
                if is_sheet or is_strip:
                    continue
                frames = [img]

            scaled = []
            for fr in frames:
                sc = _scale(fr)
                if sc is not None:
                    scaled.append(sc)
            if scaled:
                try:
                    if getattr(client, '_explode_frames_by_color', None) is None:
                        client._explode_frames_by_color = {}
                except Exception:
                    client._explode_frames_by_color = {}
                client._explode_frames_by_color[str(color)] = scaled

    def load_board_background(self, client: "PygameClient", *, margin: int) -> None:
        client.board_bg = None
        try:
            margin = int(margin)
        except Exception:
            margin = 8

        try:
            base_dir = os.path.join(os.fspath(assets_dir()), 'puzzle_boards')
            # Prefer explicit default file
            preferred = os.path.join(base_dir, 'defaultboard.png')
            fallback = os.path.join(base_dir, 'puzzlebackground.png')
            path = preferred if os.path.exists(preferred) else fallback
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                # Scale to inner grid size (no margins)
                client.board_bg = pygame.transform.smoothscale(
                    img,
                    (int(client.board_px_w) - int(margin) * 2, int(client.board_px_h) - int(margin) * 2),
                )
        except Exception:
            client.board_bg = None

    def weapon_asset_path(self, client: "PygameClient", sword_type: SwordType) -> str | None:
        try:
            base_dir = os.fspath(assets_dir())
            weapons_dir = os.path.join(base_dir, 'Weapons')
            fn = get_sword_asset_filename(sword_type)
            if not fn:
                fn = f"{str(sword_type.value)}.png"
            p = os.path.join(weapons_dir, str(fn))
            return p if os.path.isfile(p) else None
        except Exception:
            return None

    def weapon_inventory_target_h_px(self, client: "PygameClient") -> int:
        """Target pixel height for weapon art in the inventory panel.

        Gameplay previews reuse this so the sword art matches the inventory size.
        """
        try:
            target_h = int(round(float(client.screen.get_height()) * 0.28))
        except Exception:
            target_h = 180
        return max(120, min(320, int(target_h)))

    def trim_alpha_surface(self, surf: pygame.Surface) -> pygame.Surface:
        """Return a copy of `surf` cropped to its non-transparent bounds.

        Many weapon PNGs contain a lot of transparent padding (especially when angled),
        which makes them look tiny when scaled-to-fit in small UI boxes.
        """
        if surf is None:
            return surf
        try:
            # pygame 2 supports min_alpha.
            rect = surf.get_bounding_rect(min_alpha=1)
        except TypeError:
            try:
                rect = surf.get_bounding_rect()
            except Exception:
                return surf
        except Exception:
            return surf

        try:
            if int(rect.width) <= 0 or int(rect.height) <= 0:
                return surf
        except Exception:
            return surf

        # Give a little breathing room so we don't crop glows too tightly.
        try:
            pad = 2
            rect = rect.inflate(int(pad * 2), int(pad * 2))
            rect = rect.clamp(surf.get_rect())
        except Exception:
            pass

        try:
            if rect.size == surf.get_rect().size:
                return surf
        except Exception:
            pass

        try:
            return surf.subsurface(rect).copy()
        except Exception:
            return surf

    def invalidate_weapon_scaled_caches_for_key(self, client: "PygameClient", key: str) -> None:
        try:
            k = str(key or '').strip().lower()
        except Exception:
            return
        if not k:
            return
        try:
            client._weapon_img_scaled = {ck: cv for ck, cv in (getattr(client, '_weapon_img_scaled', {}) or {}).items() if str(ck[0]).strip().lower() != k}
        except Exception:
            pass
        try:
            client._weapon_img_preview_scaled = {ck: cv for ck, cv in (getattr(client, '_weapon_img_preview_scaled', {}) or {}).items() if str(ck[0]).strip().lower() != k}
        except Exception:
            pass
        try:
            client._weapon_img_preview_scaled_tuned = {ck: cv for ck, cv in (getattr(client, '_weapon_img_preview_scaled_tuned', {}) or {}).items() if str(ck[0]).strip().lower() != k}
        except Exception:
            pass

    def ensure_weapon_raw_trimmed(self, client: "PygameClient", key: str, raw: pygame.Surface) -> pygame.Surface:
        try:
            k = str(key or '').strip().lower()
        except Exception:
            return raw
        if not k or raw is None:
            return raw
        try:
            if k in (getattr(client, '_weapon_img_raw_trimmed', set()) or set()):
                return raw
        except Exception:
            pass

        trimmed = self.trim_alpha_surface(raw)
        try:
            client._weapon_img_raw[k] = trimmed
        except Exception:
            pass
        try:
            client._weapon_img_raw_trimmed.add(k)
        except Exception:
            pass
        # Trim changes pixel dimensions; drop any scaled caches for this weapon.
        try:
            self.invalidate_weapon_scaled_caches_for_key(client, k)
        except Exception:
            pass
        return trimmed

    def get_weapon_art_scaled(self, client: "PygameClient", sword_type: SwordType) -> pygame.Surface | None:
        key = str(getattr(sword_type, 'value', sword_type) or '').strip().lower()
        if not key:
            return None

        target_h = int(self.weapon_inventory_target_h_px(client))

        cache_key = (key, int(target_h))
        try:
            if cache_key in (getattr(client, '_weapon_img_scaled', {}) or {}):
                return client._weapon_img_scaled[cache_key]
        except Exception:
            pass

        # Load raw if needed
        raw = None
        try:
            if key in (getattr(client, '_weapon_img_raw', {}) or {}):
                raw = client._weapon_img_raw[key]
        except Exception:
            raw = None

        if raw is None:
            p = self.weapon_asset_path(client, sword_type)
            if not p:
                return None
            try:
                raw = pygame.image.load(p).convert_alpha()
                client._weapon_img_raw[key] = raw
            except Exception:
                return None

        try:
            raw = self.ensure_weapon_raw_trimmed(client, key, raw)
        except Exception:
            pass

        try:
            iw, ih = int(raw.get_width()), int(raw.get_height())
            if iw <= 0 or ih <= 0:
                return None
            scale = float(target_h) / float(ih)
            tw = max(1, int(round(iw * scale)))
            th = max(1, int(round(ih * scale)))

            # Scaling strategy:
            # - Downscale: smoothscale for better filtering
            # - Upscale: scale (nearest) to avoid blur on pixel art
            if tw <= iw and th <= ih:
                scaled = pygame.transform.smoothscale(raw, (tw, th))
            else:
                scaled = pygame.transform.scale(raw, (tw, th))

            client._weapon_img_scaled[cache_key] = scaled
            return scaled
        except Exception:
            return None

    def get_weapon_art_scaled_preview(self, client: "PygameClient", sword_type: SwordType, *, max_w: int, max_h: int) -> pygame.Surface | None:
        """Return a sword image scaled to fit within (max_w, max_h) for side previews."""
        key = str(getattr(sword_type, 'value', sword_type) or '').strip().lower()
        if not key:
            return None

        try:
            max_w = max(1, int(max_w))
            max_h = max(1, int(max_h))
        except Exception:
            max_w, max_h = (80, 80)

        cache_key = (key, int(max_w), int(max_h))
        try:
            cached = (getattr(client, '_weapon_img_preview_scaled', {}) or {}).get(cache_key)
            if cached is not None:
                return cached
        except Exception:
            pass

        # Load raw if needed
        raw = None
        try:
            raw = (getattr(client, '_weapon_img_raw', {}) or {}).get(key)
        except Exception:
            raw = None

        if raw is None:
            p = self.weapon_asset_path(client, sword_type)
            if not p:
                return None
            try:
                raw = pygame.image.load(p).convert_alpha()
                client._weapon_img_raw[key] = raw
            except Exception:
                return None

        try:
            raw = self.ensure_weapon_raw_trimmed(client, key, raw)
        except Exception:
            pass

        try:
            iw, ih = int(raw.get_width()), int(raw.get_height())
            if iw <= 0 or ih <= 0:
                return None

            # Fit by height first, then clamp by width.
            scale = float(max_h) / float(ih)
            tw = max(1, int(round(iw * scale)))
            th = max(1, int(round(ih * scale)))
            if tw > max_w:
                scale2 = float(max_w) / float(tw)
                tw = max(1, int(round(tw * scale2)))
                th = max(1, int(round(th * scale2)))

            # Downscale: smoothscale; Upscale: scale (nearest) for crispness.
            if int(tw) <= int(iw) and int(th) <= int(ih):
                scaled = pygame.transform.smoothscale(raw, (int(tw), int(th)))
            else:
                scaled = pygame.transform.scale(raw, (int(tw), int(th)))
            try:
                client._weapon_img_preview_scaled[cache_key] = scaled
            except Exception:
                pass
            return scaled
        except Exception:
            return None

    def get_weapon_art_raw_trimmed(self, client: "PygameClient", sword_type: SwordType) -> pygame.Surface | None:
        """Return the trimmed raw weapon art surface for a sword type (loaded on-demand)."""
        key = str(getattr(sword_type, 'value', sword_type) or '').strip().lower()
        if not key:
            return None

        raw = None
        try:
            raw = (getattr(client, '_weapon_img_raw', {}) or {}).get(key)
        except Exception:
            raw = None

        if raw is None:
            p = self.weapon_asset_path(client, sword_type)
            if not p:
                return None
            try:
                raw = pygame.image.load(p).convert_alpha()
                client._weapon_img_raw[key] = raw
            except Exception:
                return None

        try:
            raw = self.ensure_weapon_raw_trimmed(client, key, raw)
        except Exception:
            pass
        return raw

    def get_weapon_art_scaled_preview_exact(self, client: "PygameClient", sword_type: SwordType, *, target_w: int, target_h: int) -> pygame.Surface | None:
        """Return weapon art scaled to an exact pixel size (target_w, target_h), scaled from raw (cached)."""
        key = str(getattr(sword_type, 'value', sword_type) or '').strip().lower()
        if not key:
            return None

        try:
            target_w = max(1, int(target_w))
            target_h = max(1, int(target_h))
        except Exception:
            target_w, target_h = (80, 80)

        cache_key = (key, int(target_w), int(target_h), 0)
        try:
            cached = (getattr(client, '_weapon_img_preview_scaled_tuned', {}) or {}).get(cache_key)
            if cached is not None:
                return cached
        except Exception:
            pass

        raw = self.get_weapon_art_raw_trimmed(client, sword_type)
        if raw is None:
            return None

        try:
            iw, ih = int(raw.get_width()), int(raw.get_height())
        except Exception:
            iw, ih = (0, 0)

        try:
            if int(target_w) <= int(iw) and int(target_h) <= int(ih):
                scaled = pygame.transform.smoothscale(raw, (int(target_w), int(target_h)))
            else:
                scaled = pygame.transform.scale(raw, (int(target_w), int(target_h)))
        except Exception:
            return None

        try:
            if len(getattr(client, '_weapon_img_preview_scaled_tuned', {}) or {}) > 384:
                client._weapon_img_preview_scaled_tuned = {}
            client._weapon_img_preview_scaled_tuned[cache_key] = scaled
        except Exception:
            pass
        return scaled
