from __future__ import annotations

import pytest

from swordfighting_new.pieces.piece import Block, Piece


class _TimingStub:
    target_fps = 60
    autonomous_fall_interval_frames = 2


class _GravityStub:
    def __init__(self, board):
        self.board = board

    def lock_piece(self, piece):
        self.board.place_piece(piece)


def _find_inbound_attack_handler():
    from swordfighting_new.fighters.inbound_attack_handler import InboundAttackHandler

    return InboundAttackHandler


def _find_board_class():
    from swordfighting_new.core.board import Board

    return Board


@pytest.mark.unit
def test_vertical_strike_cluster_shifts_sideways_when_blocked_by_2x2_cluster():
    """Strikes do NOT pierce 2x2+ clusters.

    They also must NOT shift columns mid-fall; instead they lock above the cluster.
    """

    Board = _find_board_class()
    InboundAttackHandler = _find_inbound_attack_handler()

    board = Board()

    # Create a 2x2 same-color cluster at x=2..3, y=6..7.
    for xx in (2, 3):
        for yy in (6, 7):
            board.set_piece(xx, yy, Block("blue"))

    handler = InboundAttackHandler(board=board, timing=_TimingStub(), piece_mover=None, gravity_manager=_GravityStub(board))

    # Represent a 2x6 incoming vertical strike cluster with just the bottom row pieces.
    # (Pathfinding is driven by the bottom edge.)
    strike_a = Piece.single_block(color="white", is_strike=True, attack_state="strike")
    strike_a.x = 2
    strike_a.y = 5
    strike_a.controllable = False
    strike_a.autonomous_fall_interval = 1
    strike_a.autonomous_fall_timer = 1
    strike_a.sword_rows = 6
    strike_a.sword_width = 2
    strike_a.strike_cluster_id = 101  # odd => left-first

    strike_b = Piece.single_block(color="white", is_strike=True, attack_state="strike")
    strike_b.x = 3
    strike_b.y = 5
    strike_b.controllable = False
    strike_b.autonomous_fall_interval = 1
    strike_b.autonomous_fall_timer = 1
    strike_b.sword_rows = 6
    strike_b.sword_width = 2
    strike_b.strike_cluster_id = 101

    handler.garbage_fallers = [strike_a, strike_b]

    handler.update_inbound_garbage()

    # Locks directly above the cluster without drifting.
    assert board.get_piece(2, 5) != board.EMPTY
    assert board.get_piece(3, 5) != board.EMPTY
    assert handler.garbage_fallers == []

    # Cluster must remain intact (strikes do not pierce clusters).
    for xx in (2, 3):
        for yy in (6, 7):
            cell = board.get_piece(xx, yy)
            assert cell != board.EMPTY
            assert getattr(cell, "color", None) == "blue"
