import os
import pygame

from utils.clock import FakeClock
from core.puzzle_module import PuzzleEngine
from core.puzzle_renderer import PuzzleRenderer


def test_per_board_animation_state_isolated():
    os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
    pygame.init()
    try:
        screen = pygame.display.set_mode((800, 600))
        font = pygame.font.Font(None, 24)
        clock = FakeClock(0)

        p_engine = PuzzleEngine(screen, font, audio=None, asset_path="puzzleassets", settings_system=None)
        e_engine = PuzzleEngine(screen, font, audio=None, asset_path="puzzleassets", settings_system=None)

        setattr(p_engine, 'clock', clock)
        setattr(e_engine, 'clock', clock)

        p_engine.start_game()
        e_engine.start_game()

        p_renderer = PuzzleRenderer(p_engine, clock=clock)
        e_renderer = PuzzleRenderer(e_engine, clock=clock)

        # Different state manager objects
        assert p_renderer.animation_state_manager is not e_renderer.animation_state_manager
        # And renderers do not share dict objects
        assert p_renderer.animation_state_manager.visual_falling_blocks is not e_renderer.animation_state_manager.visual_falling_blocks

        # Mutate one and ensure the other is unaffected
        p_renderer.animation_state_manager.visual_falling_blocks[(0, 1)] = {
            'start_time': 0.0,
            'duration': 0.5,
            'start_y': 0,
            'block_type': 'red_block',
        }
        assert (0, 1) not in e_renderer.animation_state_manager.visual_falling_blocks

    finally:
        try:
            pygame.quit()
        except Exception:
            pass

