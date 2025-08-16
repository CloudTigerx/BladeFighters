import os
import pygame

from utils.clock import FakeClock
from core.puzzle_module import PuzzleEngine
from core.puzzle_renderer import PuzzleRenderer


def test_renderer_snaps_on_land_no_overshoot():
    os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
    pygame.init()
    try:
        screen = pygame.display.set_mode((640, 480))
        font = pygame.font.Font(None, 24)
        clock = FakeClock(0)

        engine = PuzzleEngine(screen, font, audio=None, asset_path="puzzleassets", settings_system=None)
        setattr(engine, 'clock', clock)
        engine.start_game()

        # Prepare a landing surface at row 5
        for x in range(engine.grid_width):
            engine.puzzle_grid[5][x] = 'red_block'

        # Active piece just above landing row
        engine.main_piece = 'blue_block'
        engine.attached_piece = None
        engine.piece_position = [3, 3]
        engine.attached_position = 0

        renderer = PuzzleRenderer(engine, clock=clock)

        # Advance until we are about to land
        overshot = False
        for i in range(30):
            clock.advance(16)
            engine.update()
            renderer.update_visual_state()
            renderer.update_animations()

            if engine.main_piece:
                # Compute current visual y in pixels for the main piece
                vis = renderer.animation_state_manager.visual_piece_position
                if vis:
                    y = vis[1]
                    # Target cell just before landing is y=4
                    # Ensure we never draw below that boundary while falling
                    if y > 4.9999:
                        overshot = True
                        break
            else:
                # Landed this frame; the piece should be placed and not drawn as falling
                break

        assert not overshot, "Renderer must not overshoot below the landing cell while falling"
    finally:
        try:
            pygame.quit()
        except Exception:
            pass

