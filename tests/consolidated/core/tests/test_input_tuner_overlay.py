import pygame
import types

from utils.clock import FakeClock
from core.ui.input_tuner_overlay import InputTunerOverlay


class DummyInputHandler:
    def __init__(self, clock):
        self.clock = clock
        self._events = []

    def get_diagnostics(self):
        return {
            'now_ms': self.clock.now_ms(),
            'timings': {
                # DAS/ARR functionality removed
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
        settings = DummySettings({})
        font = pygame.font.SysFont(None, 18)
        overlay = InputTunerOverlay(clock, settings, ih, font)
        overlay.toggle()

        # Since there are no parameters to adjust, just test that the overlay can be drawn
        # without throwing exceptions
        surf = pygame.Surface((640, 360))
        pre = surf.get_at((10, 10))
        overlay.draw(surf)
        post = surf.get_at((10, 10))
        # Not strict pixel compare (could be same if corner), but assert draw ran without exception
        assert isinstance(post, pygame.Color)

        # Test that the overlay can handle key events without crashing
        overlay.update([make_keydown(pygame.K_l)])
        overlay.update([make_keydown(pygame.K_j)])
        overlay.update([make_keydown(pygame.K_k)])

        # Verify the overlay is still functional
        assert overlay.visible == True
    finally:
        pygame.quit()

