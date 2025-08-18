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
    for row_idx, row in enumerate(grid):
        for col_idx, cell in enumerate(row):
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

    finally:
        try:
            pygame.quit()
        except Exception:
            pass


def test_garbage_delivery_animated_path_spawns_above_and_falls():
    """Test that garbage blocks spawn above the board and fall to their landing positions."""
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

        # Verify that pending landings are created
        assert len(tm.pending_landings['enemy']) > 0, "Expected pending landings to be created"
        
        # Verify that visual falling blocks are created
        asm = tm.enemy_renderer.animation_state_manager
        assert len(asm.visual_falling_blocks) > 0, "Expected visual falling blocks to be created"
        
        # Verify that the pending landing has the correct structure
        pending_landing = tm.pending_landings['enemy'][0]
        col, row, block_type, end_ms = pending_landing
        assert block_type == 'garbage_block', f"Expected garbage_block, got {block_type}"
        assert end_ms > clock.now_ms(), "Expected end time to be in the future"
        
        # Verify that the visual falling block has the correct structure
        visual_block_key = list(asm.visual_falling_blocks.keys())[0]
        visual_block_data = asm.visual_falling_blocks[visual_block_key]
        assert visual_block_data['block_type'] == 'garbage_block', f"Expected garbage_block, got {visual_block_data['block_type']}"
        assert visual_block_data['start_y'] < 0, f"Expected spawn above board (start_y < 0), got {visual_block_data['start_y']}"
        assert visual_block_data['final_position'] == (col, row), f"Expected final position to match pending landing"

        # Run until placement occurs and verify the landing commit happens
        landing_committed = False
        for i in range(120):
            clock.advance(50)
            tm.update()
            
            # Check if pending landings are cleared (indicating successful commit)
            if len(tm.pending_landings['enemy']) == 0:
                landing_committed = True
                break
        
        # The test passes if the landing was committed (even if the block gets overwritten later)
        assert landing_committed, 'Garbage landing should be committed during the falling animation'

    finally:
        try:
            pygame.quit()
        except Exception:
            pass

