import os
import types
import pygame

from utils.clock import FakeClock
from modules.testmode_module.test_mode import TestMode


class DummySettings:
    def __init__(self, cfg=None):
        cfg = cfg or {}
        self.config = types.SimpleNamespace(get=lambda k, d=None: cfg.get(k, d))


def _count_cells(grid, predicate):
    c = 0
    for row in grid:
        for cell in row:
            if predicate(cell):
                c += 1
    return c


def test_garbage_delivery_animated_path_spawns_above_and_falls():
    os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
    pygame.init()
    try:
        screen = pygame.display.set_mode((800, 600))
        font = pygame.font.Font(None, 24)
        clock = FakeClock(0)
        settings = DummySettings({
            'attacks.spawn_mode': 'animated',
            'renderer.snap_on_land': True,
        })

        tm = TestMode(screen, font, audio=None, asset_path='puzzleassets', settings_system=settings, clock=clock)

        # Seed a simple combo on player to generate garbage to enemy
        broken = [(0, 0, 'red'), (1, 0, 'blue')]
        tm.attacks_service.on_combo(broken, is_cluster=False, chain_multiplier=1, player_id=1)

        # First update performs delivery (enqueue only)
        tm.update()

        # No grid mutation on frame 0
        garbage_before = _count_cells(tm.enemy_engine.puzzle_grid, lambda v: v == 'garbage_block')
        assert garbage_before == 0

        # Advance a few frames; ensure visual falling entries appear above top and progress
        asm = tm.enemy_renderer.animation_state_manager
        seen_above = 0
        for _ in range(3):
            clock.advance(50)
            tm.update()
            # Keys are (col, row) target cells; entries carry start_y
            for _, data in list(asm.visual_falling_blocks.items()):
                if int(data.get('start_y', 0)) < 0 or int(data.get('start_y', 0)) == 0:
                    seen_above += 1
        assert seen_above >= 1, 'Expected at least one falling entity spawned above the board'

        # Run until placement occurs
        placed = False
        for _ in range(120):
            clock.advance(50)
            tm.update()
            garbage_now = _count_cells(tm.enemy_engine.puzzle_grid, lambda v: v == 'garbage_block')
            if garbage_now > 0:
                placed = True
                break
        assert placed, 'Garbage should eventually be placed after falling animation completes'
    finally:
        try:
            pygame.quit()
        except Exception:
            pass


def test_strike_delivery_animated_path_spawns_above_and_falls():
    os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
    pygame.init()
    try:
        screen = pygame.display.set_mode((800, 600))
        font = pygame.font.Font(None, 24)
        clock = FakeClock(0)
        settings = DummySettings({
            'attacks.spawn_mode': 'animated',
            'renderer.snap_on_land': True,
        })

        tm = TestMode(screen, font, audio=None, asset_path='puzzleassets', settings_system=settings, clock=clock)

        # Seed a cluster-y combo to generate a strike to enemy
        broken = [(0, 0, 'r'), (1, 0, 'r'), (0, 1, 'r'), (1, 1, 'r')]
        tm.attacks_service.on_combo(broken, is_cluster=True, chain_multiplier=2, player_id=1)

        # First update enqueues spawn
        tm.update()

        # No immediate strike cells on grid
        strike_before = _count_cells(tm.enemy_engine.puzzle_grid, lambda v: isinstance(v, str) and v.endswith('_strike'))
        assert strike_before == 0

        # Observe falling visuals from above
        asm = tm.enemy_renderer.animation_state_manager
        seen_any = False
        for _ in range(5):
            clock.advance(50)
            tm.update()
            if asm.visual_falling_blocks:
                seen_any = True
                break
        assert seen_any, 'Expected strike falling visuals before placement'

        # Eventually placed
        placed = False
        for _ in range(180):
            clock.advance(50)
            tm.update()
            strike_now = _count_cells(tm.enemy_engine.puzzle_grid, lambda v: isinstance(v, str) and v.endswith('_strike'))
            if strike_now > 0:
                placed = True
                break
        assert placed, 'Strike should eventually be placed after falling animation completes'
    finally:
        try:
            pygame.quit()
        except Exception:
            pass

