import types
import pygame

from utils.clock import FakeClock
from core.input_handler import InputHandler


class DummyEngine:
    def __init__(self, clock):
        self.clock = clock
        self.game_active = True
        self.normal_fall_speed = 1.0
        self.accelerated_fall_speed = 3.0
        self.current_fall_speed = self.normal_fall_speed
        self.micro_fall_time = 0
        self.move_calls = []
        self.rotate_calls = []
        self.main_piece = True

    def _calculate_micro_fall_time(self, speed):
        return max(1, int(1000 / max(0.001, speed)))

    def move_piece(self, dx, dy):
        self.move_calls.append((self.clock.now_ms(), dx, dy))

    def rotate_attached_piece(self, direction):
        self.rotate_calls.append((self.clock.now_ms(), direction))
        return True


class DummySettings:
    def __init__(self, cfg=None):
        self.config = types.SimpleNamespace(get=lambda k, d=None: (cfg or {}).get(k, d))


def make_event(key, etype):
    e = types.SimpleNamespace()
    e.type = etype
    e.key = key
    return e


def test_gate_blocks_after_land_until_spawn():
    clock = FakeClock(0)
    engine = DummyEngine(clock)
    ih = InputHandler(engine, DummySettings())
    # Active piece -> movement works
    ih.process_events([make_event(pygame.K_LEFT, pygame.KEYDOWN)])
    assert engine.move_calls
    # Land callback
    ih._on_piece_landed()
    # Simulate hold but no movement should occur now
    pre = len(engine.move_calls)
    clock.advance(500)
    ih.process_events([])
    assert len(engine.move_calls) == pre
    # Next spawn reenables
    engine.main_piece = True
    ih.is_falling = True
    clock.advance(200)
    ih.process_events([make_event(pygame.K_RIGHT, pygame.KEYDOWN)])
    assert len(engine.move_calls) > pre

