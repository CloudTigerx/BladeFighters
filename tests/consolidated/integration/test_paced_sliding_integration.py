import os
import pygame
import time

from utils.clock import FakeClock
from core.puzzle_module import PuzzleEngine
from core.puzzle_renderer import PuzzleRenderer


def test_paced_slide_respects_breaking_duration_and_no_teleport():
    os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
    pygame.init()
    try:
        screen = pygame.display.set_mode((800, 600))
        font = pygame.font.Font(None, 24)
        clock = FakeClock(0)

        engine = PuzzleEngine(screen, font, audio=None, asset_path="puzzleassets", settings_system=None)
        setattr(engine, 'clock', clock)
        engine.start_game()
        renderer = PuzzleRenderer(engine, clock=clock)

        # Clear grid and set up a lateral slide scenario
        for y in range(engine.grid_height):
            for x in range(engine.grid_width):
                engine.puzzle_grid[y][x] = None

        # Place a single block with an empty neighbor and SUPPORT below to simulate horizontal slide
        engine.puzzle_grid[8][3] = 'green_block'
        engine.puzzle_grid[9][3] = 'red_block'   # support below source
        engine.puzzle_grid[9][4] = 'red_block'   # support below target

        # Simulate breaking window active to pace slide
        asm = renderer.animation_state_manager
        now_s = time.time()
        asm.breaking_blocks_animations[(0, 0)] = {
            'start_time': now_s,
            'total_duration': asm.breaking_animation_duration,
            'progress': 0.0,
        }

        # Directly queue sliding based on current board state
        engine._handle_piece_sliding({})

        # There should be a slide queued to either (2,8) or (4,8)
        slides = getattr(asm, 'visual_sliding_blocks', {})
        assert (4, 8) in slides or (2, 8) in slides, "Expected horizontal slide animation queued"
        slide = slides.get((4, 8)) or slides.get((2, 8))
        assert abs(float(slide['duration']) - float(asm.breaking_animation_duration)) < 1e-6

    finally:
        try:
            pygame.quit()
        except Exception:
            pass


