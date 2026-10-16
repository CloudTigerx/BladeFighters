from __future__ import annotations

import pytest

from swordfighting_new.pieces.piece import Block


class _TimingStub:
    target_fps = 60
    autonomous_fall_interval_frames = 6


class _GravityStub:
    def __init__(self, board):
        self.board = board

    def lock_piece(self, piece):
        self.board.place_piece(piece)


class _HorizStub:
    def spawn_horizontal_sword(self, *args, **kwargs):
        raise AssertionError("horizontal sword spawn not expected in this test")


def _find_inbound_attack_handler():
    from swordfighting_new.fighters.inbound_attack_handler import InboundAttackHandler

    return InboundAttackHandler


def _find_board_class():
    from swordfighting_new.core.board import Board

    return Board


@pytest.mark.unit
def test_vertical_strike_cluster_preselects_lane_avoiding_surface_cluster_when_possible():
    """Wide vertical strikes should choose a landing lane up-front, not shift mid-fall.

    If the planned lane's surface is a 2x2 cluster, prefer another lane when available.
    """

    Board = _find_board_class()
    InboundAttackHandler = _find_inbound_attack_handler()

    board = Board()

    # Make a 2x2 cluster whose topmost occupied blocks are in columns 4-5.
    for xx in (4, 5):
        for yy in (10, 11):
            board.set_piece(xx, yy, Block("blue"))

    handler = InboundAttackHandler(board=board, timing=_TimingStub(), piece_mover=None, gravity_manager=_GravityStub(board))

    handler._pending_in_strike_clusters = [("vsword", (2, 6))]

    handler._spawn_multiple_strike_clusters(_HorizStub())

    fallers = [g for g in handler.garbage_fallers if getattr(g, "strike_cluster_id", None) is not None]
    assert fallers, "expected a spawned strike cluster"

    left = min(int(getattr(g, "x", 0)) for g in fallers)

    # The lane at left=4 would be directly above a surface cluster; it should avoid it.
    assert left != 4


@pytest.mark.unit
def test_vertical_strike_cluster_does_not_shift_columns_mid_fall():
    """Regression: strikes should not change columns while falling (pathfinding is preselected)."""

    Board = _find_board_class()
    InboundAttackHandler = _find_inbound_attack_handler()

    board = Board()

    # Cluster directly below the sword columns at y=6.
    for xx in (4, 5):
        for yy in (6, 7):
            board.set_piece(xx, yy, Block("blue"))

    handler = InboundAttackHandler(board=board, timing=_TimingStub(), piece_mover=None, gravity_manager=_GravityStub(board))

    # Force-spawn a 2-wide strike cluster at left=4.
    handler._spawn_strike_cluster_at(left=4, width=2, height=1)

    # Place the fallers directly above the cluster so a downward move is blocked
    # and (previously) the sidestep logic would try to change columns.
    for g in handler.garbage_fallers:
        setattr(g, "y", 5)
        setattr(g, "sword_width", 2)
        g.autonomous_fall_interval = 1
        g.autonomous_fall_timer = 1

    handler.update_inbound_garbage()

    # The sword should lock directly above the cluster in its original columns.
    assert board.get_piece(4, 5) != board.EMPTY
    assert board.get_piece(5, 5) != board.EMPTY
