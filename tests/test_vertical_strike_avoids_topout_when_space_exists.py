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
def test_vertical_strike_prefers_lane_that_fits_height_when_possible():
    """If a vertical strike would top-out in one lane but another lane fits, prefer the safe lane.

    This prevents avoidable instant defeats when there is still ample empty space elsewhere.
    """

    Board = _find_board_class()
    InboundAttackHandler = _find_inbound_attack_handler()

    board = Board()

    # Make columns 0-1 too tall to accept a 2x6 strike without locking above y=0.
    # First occupied y becomes 5, so height 6 would require y=-1.
    for xx in (0, 1):
        for yy in range(5, 12):
            board.set_piece(xx, yy, Block("blue"))

    handler = InboundAttackHandler(board=board, timing=_TimingStub(), piece_mover=None, gravity_manager=_GravityStub(board))

    # A 2-wide, 6-tall strike. With default preselect ordering for 2-wide,
    # left=0 is normally considered first; we expect it to avoid that lane.
    handler._pending_in_strike_clusters = [("vsword", (2, 6))]
    handler.frame = 0
    handler._strike_rot_seed = 0

    handler._spawn_multiple_strike_clusters(_HorizStub())

    fallers = [g for g in handler.garbage_fallers if getattr(g, "strike_cluster_id", None) is not None]
    assert fallers, "expected a spawned strike cluster"

    left = min(int(getattr(g, "x", 0)) for g in fallers)

    # left=0 would top-out; left=4 fits (cols 4-5 are empty).
    assert left != 0
