"""display_controller.py - Display/DPI/window mode helpers for Blade Fighters.

This module is part of the staged modularization of `pygame_client.py`.
It keeps `PygameClient` as the orchestrator while extracting display-mode
and DPI setup helpers.
"""

from __future__ import annotations

from typing import Any

import os


def set_windows_dpi_awareness() -> None:
    """Best-effort DPI awareness so 4K sizing isn't distorted by Windows scaling."""
    if os.name != 'nt':
        return
    try:
        import ctypes
    except Exception:
        return

    # Prefer Per-Monitor v2 awareness when available.
    try:
        user32 = ctypes.windll.user32
        set_ctx = getattr(user32, 'SetProcessDpiAwarenessContext', None)
        if set_ctx is not None:
            # DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2 = -4
            try:
                set_ctx(ctypes.c_void_p(-4))
                return
            except Exception:
                pass
    except Exception:
        pass


def get_desktop_size(pygame) -> tuple[int, int]:
    """Best-effort desktop size (used to avoid 0x0 SCALED fullscreen modes)."""
    # Newer pygame provides get_desktop_sizes.
    try:
        sizes = pygame.display.get_desktop_sizes()
        if sizes:
            w, h = sizes[0]
            w, h = int(w), int(h)
            if w > 0 and h > 0:
                return (w, h)
    except Exception:
        pass

    try:
        info = pygame.display.Info()
        w, h = int(getattr(info, 'current_w', 0) or 0), int(getattr(info, 'current_h', 0) or 0)
        if w > 0 and h > 0:
            return (w, h)
    except Exception:
        pass

    # Final fallback: prefer user env, else 4K.
    try:
        w = int(os.getenv('BF_SCREEN_W', '3840') or '3840')
    except Exception:
        w = 3840
    try:
        h = int(os.getenv('BF_SCREEN_H', '2160') or '2160')
    except Exception:
        h = 2160
    return (max(1, w), max(1, h))


class DisplayController:
    def __init__(self, *, pygame) -> None:
        self._pygame = pygame

    def apply_display_mode(self, client: Any, fullscreen_enabled: bool) -> None:
        """Apply exclusive fullscreen/windowed mode and refresh layout."""
        pygame = self._pygame
        want_fullscreen = bool(fullscreen_enabled)

        flags = 0
        if want_fullscreen:
            try:
                flags |= pygame.FULLSCREEN
            except Exception:
                pass
        else:
            try:
                flags |= pygame.RESIZABLE
            except Exception:
                pass

        # SCALED defaults: on in fullscreen, off in windowed unless explicitly requested.
        try:
            default_scaled = '1' if want_fullscreen else '0'
        except Exception:
            default_scaled = '0'
        want_scaled = False
        try:
            want_scaled = str(os.getenv('BF_SCALED', default_scaled) or default_scaled).strip().lower() not in (
                '0', 'false', 'no', 'off'
            )
        except Exception:
            want_scaled = (default_scaled == '1')
        if want_scaled:
            try:
                flags |= pygame.SCALED
            except Exception:
                pass

        if want_fullscreen:
            req_w, req_h = get_desktop_size(pygame)
        else:
            try:
                req_w = int(os.getenv('BF_WINDOW_W', '1920') or '1920')
            except Exception:
                req_w = 1920
            try:
                req_h = int(os.getenv('BF_WINDOW_H', '1080') or '1080')
            except Exception:
                req_h = 1080

        size = (int(req_w), int(req_h))
        try:
            client.screen = pygame.display.set_mode(size, flags)
        except Exception:
            try:
                client.screen = pygame.display.set_mode(size, (flags & ~getattr(pygame, 'SCALED', 0)))
            except Exception:
                fallback_flags = pygame.FULLSCREEN if want_fullscreen else 0
                client.screen = pygame.display.set_mode(size, fallback_flags)

        try:
            pygame.display.set_caption("Blade Fighters Modular")
        except Exception:
            pass

        try:
            client._recompute_ui_scale_and_assets()
        except Exception:
            pass
