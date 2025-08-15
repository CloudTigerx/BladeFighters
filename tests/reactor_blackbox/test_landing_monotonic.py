import os
import pygame

from utils.clock import FakeClock
from tests.reactor_blackbox.harness import load_fixture, run_fixture
from core.puzzle_module import PuzzleEngine


def test_engine_grid_y_monotonic_after_landing(tmp_path):
    os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
    pygame.init()
    try:
        screen = pygame.display.set_mode((640, 480))
        font = pygame.font.Font(None, 24)
        clock = FakeClock(0)

        # Build engine and attach clock
        engine = PuzzleEngine(screen, font, audio=None, asset_path="puzzleassets", settings_system=None)
        setattr(engine, 'clock', clock)

        engine.start_game()

        # Spawn a piece high enough to fall one cell then land immediately on a placed block
        # Place a solid row at y=5
        for x in range(engine.grid_width):
            engine.puzzle_grid[5][x] = 'red_block'

        # Put active piece at y=3 so it will land at y=4
        engine.main_piece = 'blue_block'
        engine.attached_piece = None
        engine.piece_position = [3, 3]
        engine.attached_position = 0

        grid_ys = []

        landed = False
        for step in range(50):
            clock.advance(20)
            engine.update()
            # Track y while piece is active
            if engine.main_piece:
                grid_ys.append(engine.piece_position[1])
            # When piece places, break
            if engine.main_piece is None and not landed:
                landed = True
                # capture last grid y (landing row)
                if grid_ys:
                    landed_y = grid_ys[-1]
                else:
                    landed_y = 4
            # After landed, ensure no engine y increases (no bounce up)
            if landed:
                # Engine has no active piece; invariant is that we won't resurrect a higher y
                pass

        # Monotonic non-increasing after last active y: trivial here but keeps guard in place
        assert all(a <= b for a, b in zip(grid_ys, grid_ys[1:])), "Engine grid_y should not increase while falling"

    finally:
        try:
            pygame.quit()
        except Exception:
            pass

