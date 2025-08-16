#!/usr/bin/env python3
"""
Cross-resolution coordinate/scaling invariants.

Verifies that:
- Board layout derives from centralized asset scaler
- Coordinate transforms are consistent across supported resolutions
- Dual-grid spacing scales with UI scale
"""

import os
import sys
import pygame


def test_cross_resolution_coordinate_invariants():
    # Ensure project root is importable when running this test standalone
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
    pygame.init()
    try:
        # Import singletons
        from core.scaling import resolution_manager, asset_scaler, coordinate_system

        available = resolution_manager.get_available_resolutions()
        assert isinstance(available, list) and len(available) >= 1

        # Use up to 3 resolutions to keep runtime short
        sample_res = available[:3]

        prev_block = None
        for res in sample_res:
            # Switch resolution and update scalers
            assert resolution_manager.set_resolution(res) is True
            # Refresh asset scaler cache/scale factor
            asset_scaler.update_scale()

            block_size = asset_scaler.get_block_size()
            assert isinstance(block_size, int) and block_size > 0

            # Coordinate system should use the current block size
            coordinate_system.set_block_size(block_size)

            # Calculate grid position using scaler (source of truth)
            grid_offset = asset_scaler.calculate_grid_position((res.width, res.height))
            assert isinstance(grid_offset, tuple) and len(grid_offset) == 2
            coordinate_system.set_grid_offset(grid_offset)

            # Round-trip a few grid points
            from core.scaling.coordinate_system import GridPosition
            for gx, gy in [(0, 0), (1, 1), (5, 11)]:
                gp = GridPosition(gx, gy)
                sp = coordinate_system.grid_to_screen(gp)
                # Must be aligned to offset + multiples of block size
                assert sp.x == grid_offset[0] + gx * block_size
                assert sp.y == grid_offset[1] + gy * block_size
                # And invertible
                gp2 = coordinate_system.screen_to_grid((sp.x + block_size // 2, sp.y + block_size // 2))
                assert gp2 is not None and gp2.x == gx and gp2.y == gy

            # Dual-grid layout spacing invariant
            layout = asset_scaler.calculate_dual_grid_layout((res.width, res.height))
            px, py = layout['player']
            ex, ey = layout['enemy']
            grid_w, grid_h = layout['grid_size']
            spacing = layout['spacing']

            # Enemy X should start immediately after player grid and spacing
            assert ex == px + grid_w + spacing
            assert isinstance(spacing, int) and spacing >= 0

            # Block size should be non-decreasing as resolution density increases in our ordered list
            if prev_block is not None:
                assert block_size >= prev_block
            prev_block = block_size
    finally:
        pygame.quit()


