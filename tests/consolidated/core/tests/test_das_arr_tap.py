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


def test_no_automatic_key_repeat():
    """Test that DAS/ARR functionality has been removed and no automatic key repeat occurs."""
    clock = FakeClock(0)
    engine = DummyEngine(clock)
    settings = DummySettings({})
    ih = InputHandler(engine, settings)

    # Test that pressing and holding left arrow only triggers one move
    ih.process_events([make_event(pygame.K_LEFT, pygame.KEYDOWN)])
    initial_moves = len(engine.move_calls)
    
    # Advance time significantly and process events multiple times
    clock.advance(1000)  # 1 second
    ih.process_events([])
    ih._handle_continuous_keys()
    
    clock.advance(1000)  # Another second
    ih.process_events([])
    ih._handle_continuous_keys()
    
    # Should still only have the initial move, no automatic repeats
    assert len(engine.move_calls) == initial_moves, "No automatic key repeat should occur"

    # Test that pressing and holding right arrow only triggers one move
    ih.process_events([make_event(pygame.K_RIGHT, pygame.KEYDOWN)])
    initial_moves = len(engine.move_calls)
    
    # Advance time and process events
    clock.advance(1000)
    ih.process_events([])
    ih._handle_continuous_keys()
    
    # Should still only have the initial move
    assert len(engine.move_calls) == initial_moves, "No automatic key repeat should occur"

    # Test that pressing and holding up arrow only triggers one rotation
    ih.process_events([make_event(pygame.K_UP, pygame.KEYDOWN)])
    initial_rotations = len(engine.rotate_calls)
    
    # Advance time and process events
    clock.advance(1000)
    ih.process_events([])
    ih._handle_continuous_keys()
    
    # Should still only have the initial rotation
    assert len(engine.rotate_calls) == initial_rotations, "No automatic rotation repeat should occur"

    print("✓ DAS/ARR functionality successfully removed - no automatic key repeat occurs")

