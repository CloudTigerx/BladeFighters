from swordfighting_new.core.board import Board
from swordfighting_new.mechanics.gravity import GravityManager
from swordfighting_new.pieces.piece import Block


class _TimingStub:
    target_fps = 60
    autonomous_fall_interval_frames = 6
    split_fall_interval_frames = 6


def test_global_gravity_moves_strike_phase_overhang_block() -> None:
    """Strike-phase blocks should still settle under global snap gravity.

    If strike garbage is treated as immovable while in attack_state='strike',
    it can create persistent overhangs/air pockets that reduce top-out pressure.

    Layout (y increases downward):
      S S
      X .

    The top-right strike block has empty below and should fall.
    """
    board = Board()
    strike_left = Block("white", is_strike=True, attack_state="strike")
    strike_right = Block("white", is_strike=True, attack_state="strike")
    support = Block("blue")

    board.set_piece(0, 10, strike_left)
    board.set_piece(1, 10, strike_right)
    board.set_piece(0, 11, support)

    g = GravityManager(board=board, mover=None, timing=_TimingStub())
    fallers = g.apply_global_gravity()

    assert fallers == []
    assert board.get_piece(1, 10) == board.EMPTY
    assert board.get_piece(1, 11) is strike_right
    assert board.get_piece(0, 11) is support
