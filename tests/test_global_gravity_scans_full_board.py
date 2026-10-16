from swordfighting_new.core.board import Board
from swordfighting_new.mechanics.gravity import GravityManager
from swordfighting_new.pieces.piece import Block


class _TimingStub:
    target_fps = 60
    autonomous_fall_interval_frames = 6
    split_fall_interval_frames = 6


def test_apply_global_gravity_scans_full_board():
    board = Board()

    x = 0
    y = 3  # not the bottom row
    b = Block("red")
    board.set_piece(x, y, b)

    g = GravityManager(board=board, mover=None, timing=_TimingStub())
    fallers = g.apply_global_gravity()

    # Snap-settle: the block should compress to the lowest available row immediately.
    assert fallers == []
    assert board.get_piece(x, y) == board.EMPTY
    assert board.get_piece(x, board.HEIGHT - 1) is b
