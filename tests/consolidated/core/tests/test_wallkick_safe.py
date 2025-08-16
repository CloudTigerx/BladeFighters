from core.basic_physics import BasicPhysics


class DummyEngine:
    def __init__(self, grid_width=6, grid_height=12):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.total_grid_height = grid_height
        self.block_size = 24
        self.puzzle_grid = [[None for _ in range(grid_width)] for _ in range(grid_height)]


def test_wallkick_at_walls():
    eng = DummyEngine()
    phys = BasicPhysics(eng)
    # Near left wall, attached on left (position 3). Try clockwise to top (0) with +1 kick
    piece_pos = [0, 5]
    attached_pos = 3
    ok, dx = phys.would_fit_after_rotate(piece_pos, attached_pos, +1)
    # dx can be +1 to move right and fit
    assert (ok and dx in (0, 1))


def test_wallkick_blocked_when_obstructed():
    eng = DummyEngine()
    # Place a block where the in-place attached would go and where the kick would go
    eng.puzzle_grid[4][0] = 'red_block'  # blocks in-place rotation (attached at top)
    eng.puzzle_grid[5][1] = 'red_block'
    phys = BasicPhysics(eng)
    piece_pos = [0, 5]
    attached_pos = 3
    ok, dx = phys.would_fit_after_rotate(piece_pos, attached_pos, +1)
    assert not ok

