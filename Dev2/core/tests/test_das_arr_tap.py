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


def test_tap_vs_hold_arr_das():
    clock = FakeClock(0)
    engine = DummyEngine(clock)
    settings = DummySettings({
        'repeat_initial_delay_ms': 100,  # DAS
        'repeat_move_interval_ms': 50,   # ARR
        'tap_grace_ms': 90,
        'repeat_rotate_interval_ms': 200,
    })
    ih = InputHandler(engine, settings)

    # Tap left: press then release before tap_grace -> only one step total
    ih.process_events([make_event(pygame.K_LEFT, pygame.KEYDOWN)])
    pre = len(engine.move_calls)
    clock.advance(80)  # within grace
    ih.process_events([make_event(pygame.K_LEFT, pygame.KEYUP)])
    ih.process_events([])
    assert len(engine.move_calls) == pre  # Only initial press triggered exactly once overall

    # Hold right: after DAS then repeat on ARR cadence
    ih.process_events([make_event(pygame.K_RIGHT, pygame.KEYDOWN)])
    start = len(engine.move_calls)
    # Before DAS: no repeat
    clock.advance(90)
    ih.process_events([])
    assert len(engine.move_calls) == start  # only initial press counted earlier
    # Cross DAS and ARR intervals -> repeats
    clock.advance(20)  # reach DAS
    ih.process_events([])
    clock.advance(50)
    ih.process_events([])
    clock.advance(50)
    ih.process_events([])
    assert len(engine.move_calls) >= start + 2

    # Rotate hold repeats independently
    ih.process_events([make_event(pygame.K_UP, pygame.KEYDOWN)])
    r0 = len(engine.rotate_calls)
    clock.advance(190)
    ih.process_events([])
    assert len(engine.rotate_calls) == r0  # not yet
    clock.advance(10)
    ih.process_events([])
    assert len(engine.rotate_calls) == r0 + 1

