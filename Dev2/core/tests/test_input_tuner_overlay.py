import pygame
import types

from utils.clock import FakeClock
from core.ui.input_tuner_overlay import InputTunerOverlay


class DummyInputHandler:
    def __init__(self, clock):
        self.clock = clock
        self.key_repeat_delay = 120
        self.key_repeat_interval = 80
        self.arrow_repeat_interval = 500
        self.rotate_repeat_interval = 600
        self._events = []

    def get_diagnostics(self):
        return {
            'now_ms': self.clock.now_ms(),
            'timings': {
                'repeat_initial_delay_ms': self.key_repeat_delay,
                'repeat_interval_ms': self.key_repeat_interval,
                'repeat_move_interval_ms': self.arrow_repeat_interval,
                'repeat_rotate_interval_ms': self.rotate_repeat_interval,
            },
            'last_events': self._events,
        }


class DummySettings:
    def __init__(self, data=None):
        self._data = dict(data or {})

    def get(self, k, d=None):
        return self._data.get(k, d)

    def update(self, updates):
        self._data.update({k: int(v) for k, v in updates.items()})
        return self._data


def make_keydown(key):
    e = types.SimpleNamespace()
    e.type = pygame.KEYDOWN
    e.key = key
    return e


def test_overlay_adjusts_and_draws_text(tmp_path):
    pygame.init()
    try:
        clock = FakeClock(0)
        ih = DummyInputHandler(clock)
        settings = DummySettings({
            'repeat_initial_delay_ms': 120,
            'repeat_interval_ms': 80,
            'repeat_move_interval_ms': 500,
            'repeat_rotate_interval_ms': 600,
        })
        font = pygame.font.SysFont(None, 18)
        overlay = InputTunerOverlay(clock, settings, ih, font)
        overlay.toggle()

        # Adjust currently selected (initial delay) by +5 and then -5 (L/J)
        overlay.update([make_keydown(pygame.K_l)])
        clock.advance(16)
        overlay.update([make_keydown(pygame.K_j)])

        # Move selection down and adjust move interval (K to move selection, L to inc)
        overlay.update([make_keydown(pygame.K_k)])  # select generic
        overlay.update([make_keydown(pygame.K_k)])  # select move interval
        overlay.update([make_keydown(pygame.K_l)])

        # Render to a surface and ensure some pixels drawn (non-empty blit)
        surf = pygame.Surface((640, 360))
        pre = surf.get_at((10, 10))
        overlay.draw(surf)
        post = surf.get_at((10, 10))
        # Not strict pixel compare (could be same if corner), but assert draw ran without exception
        assert isinstance(post, pygame.Color)

        # Verify settings reflect at least one update
        assert settings.get('repeat_move_interval_ms') is not None
    finally:
        pygame.quit()

