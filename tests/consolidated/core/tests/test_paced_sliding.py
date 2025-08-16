import os
import pygame
import time

from utils.clock import FakeClock
from core.puzzle_module import PuzzleEngine
from core.puzzle_renderer import PuzzleRenderer


def _tick(renderer, clock, ms):
    # Advance fake clock and update animations
    clock._now_ms += ms
    renderer.update_animations()
    # Drive render pass to advance and cleanup time.time()-based animations
    renderer.draw_grid_blocks()


def test_sliding_paced_to_breaking_animation_duration():
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

        # Set up a simple scene that will cause lateral gap next to a falling block after break
        # Place a block at (3, 10) and empty at (4, 10); remove support under (3, 10) so it wants to fall
        for y in range(engine.grid_height):
            for x in range(engine.grid_width):
                engine.puzzle_grid[y][x] = None

        # Create a small cluster that will break at (2, 11) and (2, 10)
        engine.puzzle_grid[11][2] = 'red_block'
        engine.puzzle_grid[10][2] = 'red_block'
        # Neighbor block that should slide right into (4, 10)
        engine.puzzle_grid[10][3] = 'blue_block'
        # Place supports to encourage lateral slide rather than immediate vertical fall
        engine.puzzle_grid[11][3] = 'red_block'   # support below source
        engine.puzzle_grid[11][4] = 'red_block'   # support below target

        # Mark a breaking animation at (2, 10) to simulate active break pacing
        asm = renderer.animation_state_manager
        now_s = time.time()
        asm.breaking_blocks_animations[(2, 10)] = {
            'start_time': now_s,
            'total_duration': asm.breaking_animation_duration,
            'progress': 0.0,
        }

        # Directly invoke sliding handler to queue slide animations (no teleport)
        engine._handle_piece_sliding({})

        # Expect a sliding animation exists targeting the right neighbor cell of (3,10) if empty
        # The candidate loop adds slide for (3,10) -> (4,10)
        assert (4, 10) in getattr(asm, 'visual_sliding_blocks', {}), "Expected sliding animation to be queued"

        slide = asm.visual_sliding_blocks[(4, 10)]
        # Duration should match breaking animation duration (seconds)
        assert abs(float(slide['duration']) - float(asm.breaking_animation_duration)) < 1e-6

    finally:
        try:
            pygame.quit()
        except Exception:
            pass


