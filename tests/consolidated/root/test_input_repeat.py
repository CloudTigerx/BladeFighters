import pygame
import types

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


def test_move_repeat_tap_vs_hold():
    clock = FakeClock(0)
    engine = DummyEngine(clock)
    settings = DummySettings({
        'repeat_initial_delay_ms': 120,
        'repeat_move_interval_ms': 80,
        'repeat_rotate_interval_ms': 200,
    })
    ih = InputHandler(engine, settings)

    # Initial press should move immediately
    ih.process_events([make_event(pygame.K_RIGHT, pygame.KEYDOWN)])
    assert engine.move_calls and engine.move_calls[-1][1:] == (1, 0)

    # Hold without enough time: no additional move
    pre_count = len(engine.move_calls)
    clock.advance(100)
    ih.process_events([])
    assert len(engine.move_calls) == pre_count

    # After initial delay + first repeat interval, should repeat
    clock.advance(40)  # total 140ms > 120 initial delay but < 200; still wait until interval
    ih.process_events([])
    pre_count = len(engine.move_calls)
    clock.advance(80)  # now exceed repeat interval
    ih.process_events([])
    assert len(engine.move_calls) > pre_count


def test_rotate_vs_move_have_distinct_rates():
    clock = FakeClock(0)
    engine = DummyEngine(clock)
    settings = DummySettings({
        'repeat_move_interval_ms': 50,
        'repeat_rotate_interval_ms': 300,
    })
    ih = InputHandler(engine, settings)

    # Press both keys
    ih.process_events([make_event(pygame.K_RIGHT, pygame.KEYDOWN), make_event(pygame.K_UP, pygame.KEYDOWN)])

    # Advance shorter than rotate interval but longer than move interval
    clock.advance(200)
    ih.process_events([])

    # Expect move repeated but rotate did not
    move_repeats = len([c for c in engine.move_calls if c[1] == 1])
    rotate_repeats = len(engine.rotate_calls)
    assert move_repeats >= 2
    assert rotate_repeats <= 1


def test_no_double_fire_on_frame_spikes():
    clock = FakeClock(0)
    engine = DummyEngine(clock)
    settings = DummySettings({
        'repeat_initial_delay_ms': 120,
        'repeat_move_interval_ms': 80,
    })
    ih = InputHandler(engine, settings)

    ih.process_events([make_event(pygame.K_LEFT, pygame.KEYDOWN)])
    start_count = len(engine.move_calls)

    # Large spike (e.g., 1000ms) should align to interval math and not double count in one call
    clock.advance(1000)
    ih.process_events([])
    after = len(engine.move_calls)
    # At least one repeat occurred, but a single processing step should not emit many at once
    assert after - start_count <= 2

