from __future__ import annotations

import os


class StrikeArtController:
    def __init__(self, *, pygame, assets_dir_fn):
        self._pygame = pygame
        self._assets_dir_fn = assets_dir_fn

    def init_state(self, client) -> None:
        try:
            client._strike_solid_src = None
        except Exception:
            pass
        try:
            client._strike_solid_scaled_cache = {}
        except Exception:
            pass

    def get_strike_solid_block(self, client):
        cached = getattr(client, '_strike_solid_src', None)
        if cached is not None:
            return cached
        try:
            base = os.path.join(os.fspath(self._assets_dir_fn()), 'sprinkle')
            p = os.path.join(base, 'solid.png')
            if not os.path.isfile(p):
                client._strike_solid_src = None
                return None
            img = self._pygame.image.load(p).convert_alpha()
            client._strike_solid_src = img
            return img
        except Exception:
            client._strike_solid_src = None
            return None

    def get_strike_solid_scaled(self, client, size: tuple[int, int]):
        try:
            w, h = int(size[0]), int(size[1])
        except Exception:
            return None
        if w <= 1 or h <= 1:
            return None
        try:
            key = (w, h)
            cached = client._strike_solid_scaled_cache.get(key)
            if cached is not None:
                return cached
        except Exception:
            cached = None

        src = self.get_strike_solid_block(client)
        if src is None:
            return None
        try:
            img = self._pygame.transform.smoothscale(src, (w, h))
        except Exception:
            try:
                img = self._pygame.transform.scale(src, (w, h))
            except Exception:
                return None
        try:
            if len(client._strike_solid_scaled_cache) > 128:
                client._strike_solid_scaled_cache.clear()
            client._strike_solid_scaled_cache[key] = img
        except Exception:
            pass
        return img
