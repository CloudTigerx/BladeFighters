from __future__ import annotations


class TextRenderController:
    def __init__(self, *, pygame):
        self._pygame = pygame

    def wrap_text(self, text: str, font, max_width: int) -> list[str]:
        s = str(text or '')
        if max_width <= 1:
            return [s]

        out: list[str] = []
        for para in s.split('\n'):
            words = [w for w in para.split(' ') if w != '']
            if not words:
                out.append('')
                continue
            line = words[0]
            for w in words[1:]:
                test = f"{line} {w}" if line else w
                try:
                    if int(font.size(test)[0]) <= int(max_width):
                        line = test
                    else:
                        out.append(line)
                        line = w
                except Exception:
                    out.append(line)
                    line = w
            out.append(line)
        return out

    def ellipsize_text(self, text: str, font, max_width: int) -> str:
        s = str(text or '')
        if max_width <= 1:
            return ''
        try:
            if int(font.size(s)[0]) <= int(max_width):
                return s
        except Exception:
            return s

        ell = '...'
        try:
            if int(font.size(ell)[0]) > int(max_width):
                return ell
        except Exception:
            return ell

        lo, hi = 0, len(s)
        while lo < hi:
            mid = (lo + hi) // 2
            candidate = (s[:mid] + ell).rstrip()
            try:
                if int(font.size(candidate)[0]) <= int(max_width):
                    lo = mid + 1
                else:
                    hi = mid
            except Exception:
                break
        cut = max(0, lo - 1)
        return (s[:cut] + ell).rstrip()

    def _get_font_cached(self, client, px: int):
        pygame = self._pygame
        px = max(1, int(px))
        cache = getattr(client, '_font_cache', None)
        if cache is None:
            try:
                client._font_cache = {}
            except Exception:
                client._font_cache = {}
            cache = client._font_cache

        try:
            cached = cache.get(px)
        except Exception:
            cached = None
        if cached is not None:
            return cached

        try:
            font_obj = pygame.font.Font(None, px)
        except Exception:
            font_obj = getattr(client, '_menu_button_font', None)
            if font_obj is None:
                return None
        try:
            cache[px] = font_obj
        except Exception:
            pass
        return font_obj

    def render_fitted_text(
        self,
        client,
        text: str,
        *,
        max_width: int,
        max_height: int,
        color=(255, 255, 255),
        base_px: int | None = None,
        min_px: int | None = None,
        max_lines: int = 2,
    ):
        pygame = self._pygame

        s = str(text or '')
        if max_width <= 1 or max_height <= 1:
            return None

        try:
            ui_scale = float(getattr(client, 'ui_scale', 1.0) or 1.0)
        except Exception:
            ui_scale = 1.0

        if base_px is None:
            try:
                base_px = int(getattr(client, '_menu_button_font_px', 40) or 40)
            except Exception:
                base_px = 40

        if min_px is None:
            min_px = max(12, int(round(18 * ui_scale)))

        base_px = max(8, int(base_px))
        min_px = max(8, int(min_px))

        # Fast path: cached fitted text.
        try:
            ft_cache = getattr(client, '_fitted_text_cache', None)
        except Exception:
            ft_cache = None
        if ft_cache is None:
            try:
                client._fitted_text_cache = {}
            except Exception:
                client._fitted_text_cache = {}
            ft_cache = client._fitted_text_cache

        try:
            color_key = tuple(int(c) for c in (color or (255, 255, 255)))
        except Exception:
            color_key = (255, 255, 255)

        cache_key = (s, int(max_width), int(max_height), color_key, int(base_px), int(min_px), int(max_lines))
        try:
            cached = ft_cache.get(cache_key)
        except Exception:
            cached = None
        if cached is not None:
            return cached

        for px in range(base_px, min_px - 1, -1):
            try:
                font = self._get_font_cached(client, int(px))
            except Exception:
                font = getattr(client, '_menu_button_font', None)
            if font is None:
                return None

            # Single-line fit.
            try:
                surf = font.render(s, True, color)
                if int(surf.get_width()) <= int(max_width) and int(surf.get_height()) <= int(max_height):
                    try:
                        if len(ft_cache) > 256:
                            ft_cache.clear()
                        ft_cache[cache_key] = surf
                    except Exception:
                        pass
                    return surf
            except Exception:
                pass

            # Two-line wrap fit (when allowed by height).
            if int(max_lines) >= 2:
                try:
                    lines = self.wrap_text(s, font, int(max_width))
                except Exception:
                    lines = [s]
                if len(lines) >= 2:
                    use_lines = lines[: int(max_lines)]
                    try:
                        line_gap = max(1, int(round(px * 0.18)))
                    except Exception:
                        line_gap = 2
                    line_surfs: list[object] = []
                    for line in use_lines:
                        try:
                            line_surfs.append(font.render(str(line), True, color))
                        except Exception:
                            line_surfs = []
                            break
                    if line_surfs:
                        try:
                            block_w = max(int(ls.get_width()) for ls in line_surfs)
                            block_h = sum(int(ls.get_height()) for ls in line_surfs) + line_gap * (len(line_surfs) - 1)
                        except Exception:
                            block_w, block_h = (0, 0)
                        if block_w > 0 and block_h > 0 and block_w <= int(max_width) and block_h <= int(max_height):
                            try:
                                block = pygame.Surface((int(block_w), int(block_h)), flags=pygame.SRCALPHA)
                                y = 0
                                for ls in line_surfs:
                                    x = int((block_w - int(ls.get_width())) / 2)
                                    block.blit(ls, (x, y))
                                    y += int(ls.get_height()) + line_gap
                                try:
                                    if len(ft_cache) > 256:
                                        ft_cache.clear()
                                    ft_cache[cache_key] = block
                                except Exception:
                                    pass
                                return block
                            except Exception:
                                pass

        # Final fallback: ellipsis at min size.
        try:
            font = self._get_font_cached(client, int(min_px))
        except Exception:
            font = getattr(client, '_menu_button_font', None)
        if font is None:
            return None
        try:
            s2 = self.ellipsize_text(s, font, int(max_width))
            surf = font.render(s2, True, color)
            try:
                if len(ft_cache) > 256:
                    ft_cache.clear()
                ft_cache[cache_key] = surf
            except Exception:
                pass
            return surf
        except Exception:
            return None

    def blit_fitted_text(
        self,
        client,
        text: str,
        rect,
        *,
        color=(255, 255, 255),
        pad: int | None = None,
        x: int | None = None,
        align: str = 'center',
        base_px: int | None = None,
        max_lines: int = 2,
    ) -> None:
        try:
            ui_scale = float(getattr(client, 'ui_scale', 1.0) or 1.0)
        except Exception:
            ui_scale = 1.0

        if pad is None:
            pad = int(max(10, round(18 * ui_scale)))
        pad = max(2, int(pad))

        if x is None:
            x = int(rect.x + pad)
        try:
            max_w = int(rect.right - pad - x)
        except Exception:
            max_w = int(rect.w - 2 * pad)
        max_h = int(rect.h - 2 * pad)
        if max_w <= 1 or max_h <= 1:
            return

        surf = self.render_fitted_text(
            client,
            str(text or ''),
            max_width=max_w,
            max_height=max_h,
            color=color,
            base_px=base_px,
            max_lines=max_lines,
        )
        if surf is None:
            return

        if str(align).lower() == 'left':
            bx = int(x)
        else:
            bx = int(rect.centerx - int(surf.get_width()) / 2)
        by = int(rect.centery - int(surf.get_height()) / 2)
        try:
            client.screen.blit(surf, (bx, by))
        except Exception:
            pass
