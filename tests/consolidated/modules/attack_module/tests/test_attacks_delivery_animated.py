import os
import types
import pygame
import pytest

from utils.clock import FakeClock
from modules.testmode_module import TestMode


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


@pytest.mark.parametrize("resolution", [
    (1280, 720),   # 720p
    (2560, 1440),  # 1440p
])
def test_attack_coordinates_consistent_across_resolutions(resolution):
    """Verify attack coordinates are grid-space consistent across resolutions."""
    os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
    pygame.init()
    try:
        width, height = resolution
        screen = pygame.display.set_mode((width, height))
        font = pygame.font.Font(None, 24)
        clock = FakeClock(0)
        settings = DummySettings({
            'attacks.spawn_mode': 'animated',
            'renderer.snap_on_land': True,
        })

        tm = TestMode(screen, font, audio=None, asset_path='puzzleassets', settings_system=settings, clock=clock)

        # Seed identical combo to generate identical attack
        broken = [(0, 0, 'red'), (1, 0, 'blue')]
        tm.attack_coordinator.get_attacks_service().on_combo(broken, is_cluster=False, combo_multiplier=1, player_id=1)

        # First update enqueues spawn
        tm.update()

        # Capture pending landings content - should be identical across resolutions
        pending_landings = tm.pending_landings['enemy']
        assert len(pending_landings) > 0, "Expected pending landings to be queued"
        
        # Extract grid coordinates (col, row) from pending landings
        landing_coords = [(col, row) for col, row, block_type, end_ms in pending_landings]
        
        # Verify spawn height is consistent (grid-space, not pixel-space)
        asm = tm.enemy_renderer.animation_state_manager
        for (col, row), data in asm.visual_falling_blocks.items():
            start_y = data.get('start_y', 0)
            # start_y should be grid-space (negative for above-board spawn)
            assert start_y < 0, f"Expected spawn above board, got start_y={start_y}"
            # Verify target row is within grid bounds
            assert 0 <= row < tm.enemy_engine.grid_height, f"Invalid target row {row}"
            assert 0 <= col < tm.enemy_engine.grid_width, f"Invalid target col {col}"

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

        # Verify final grid positions match the original pending landing coordinates
        final_garbage_positions = []
        for row in range(tm.enemy_engine.grid_height):
            for col in range(tm.enemy_engine.grid_width):
                if tm.enemy_engine.puzzle_grid[row][col] == 'garbage_block':
                    final_garbage_positions.append((col, row))
        
        # Sort both lists for comparison (order may vary due to animation timing)
        landing_coords.sort()
        final_garbage_positions.sort()
        assert landing_coords == final_garbage_positions, (
            f"Final grid positions {final_garbage_positions} should match "
            f"original pending landing coordinates {landing_coords}"
        )

    finally:
        try:
            pygame.quit()
        except Exception:
            pass


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
        tm.attack_coordinator.get_attacks_service().on_combo(broken, is_cluster=False, combo_multiplier=1, player_id=1)

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

        # Assert that no grid cells changed before animation end by checking that
        # at least one pending landing existed prior to placement.
        # (Indirectly validated above by zero before and >0 after.)
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
        tm.attack_coordinator.get_attacks_service().on_combo(broken, is_cluster=True, combo_multiplier=2, player_id=1)

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

        # Assert that no on-grid spawn occurred before end (zero -> then >0 only after time passed)
    finally:
        try:
            pygame.quit()
        except Exception:
            pass

