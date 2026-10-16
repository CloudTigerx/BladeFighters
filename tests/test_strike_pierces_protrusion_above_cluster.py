from __future__ import annotations

import pytest

from swordfighting_new.pieces.piece import Block


class _TimingStub:
    target_fps = 60
    autonomous_fall_interval_frames = 6


def _find_inbound_attack_handler():
    from swordfighting_new.fighters.inbound_attack_handler import InboundAttackHandler

    return InboundAttackHandler


def _find_board_class():
    from swordfighting_new.core.board import Board

    return Board


@pytest.mark.unit
def test_strike_pierces_single_block_protrusion_before_stopping_on_cluster():
    """A block sitting on top of a 2x2 cluster should be pierceable.

    The strike should destroy the protruding single block, then stop (or pathfind)
    when it reaches the actual 2x2 cluster cells.
    """

    Board = _find_board_class()
    InboundAttackHandler = _find_inbound_attack_handler()

    board = Board()

    # Base 2x2 cluster at y=7..8, x=2..3.
    for xx in (2, 3):
        for yy in (7, 8):
            board.set_piece(xx, yy, Block("blue"))

    # Protruding single block above the cluster.
    board.set_piece(2, 6, Block("blue"))

    handler = InboundAttackHandler(board=board, timing=_TimingStub(), piece_mover=None, gravity_manager=None)

    # Strike piece positioned so its first contact is the protrusion at (2,6).
    class _P:
        def __init__(self):
            self.x = 2
            self.y = 5
            self.sword_rows = 6

    g = _P()

    cluster_cells = handler._compute_normal_cluster_cells()

    pierced = handler._resolve_strike_pierce_before_lock(g, cluster_cells)
    assert pierced is True

    # Protrusion should be destroyed.
    assert board.get_piece(2, 6) == board.EMPTY

    # The actual 2x2 cluster must remain intact.
    for xx in (2, 3):
        for yy in (7, 8):
            assert board.get_piece(xx, yy) != board.EMPTY
