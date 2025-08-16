import os
import pygame

from utils.clock import FakeClock
from modules.testmode_module.test_mode import TestModeRefactored as TestMode


def test_fixture_payload_falls_for_multiple_frames():
    os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
    pygame.init()
    try:
        screen = pygame.display.set_mode((800, 600))
        font = pygame.font.Font(None, 24)
        clock = FakeClock(0)
        # Default config uses animated spawn mode
        tm = TestMode(screen, font, audio=None, asset_path='puzzleassets', settings_system=None, clock=clock)

        # Manually enqueue a small garbage payload to enemy
        tm.queue_attack_spawn({
            'target': 'enemy',
            'type': 'garbage',
            'count': 1,
            'created_ms': int(clock.now_ms()),
            'start_y': -1,
        })

        # Frame 0: nothing on grid yet
        assert all(cell != 'garbage_block' for row in tm.enemy_engine.puzzle_grid for cell in row)

        # Ensure at least 2 frames show the entity above the board before landing
        above_frames = 0
        landed = False
        for _ in range(120):
            clock.advance(16)
            tm.update()
            asm = tm.enemy_renderer.animation_state_manager
            if asm.visual_falling_blocks:
                above_frames += 1
            # check landing
            if any(cell == 'garbage_block' for row in tm.enemy_engine.puzzle_grid for cell in row):
                landed = True
                break
        assert above_frames >= 2, 'Expected at least 2 frames with visual entity above the board'
        assert landed, 'Expected eventual landing and grid placement'
    finally:
        try:
            pygame.quit()
        except Exception:
            pass

