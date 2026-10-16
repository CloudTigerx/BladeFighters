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
def test_vertical_strike_uses_spawn_spanning_lane_if_only_lane_that_fits():
    """If the only lane that can fit the strike height spans the spawn column,
    prefer that lane over a non-fitting avoid-spawn lane.

    Regression: previously the planner could pick a non-fitting avoid-spawn lane
    (e.g. cols 4-5) even though a fitting spawn-spanning lane existed.
    """

    Board = _find_board_class()
    InboundAttackHandler = _find_inbound_attack_handler()

    board = Board()

    # We will spawn a 2-wide, 3-tall strike. It requires lane capacity >= 3.
    # Make every lane fail except left=2 (cols 2-3), which spans the default spawn column (3).
    # To make a column's capacity 2, ensure its topmost occupied cell is at y=2.
    for xx in (0, 1, 4, 5):
        board.set_piece(xx, 2, Block("blue"))

    handler = InboundAttackHandler(board=board, timing=_TimingStub(), piece_mover=None, gravity_manager=_GravityStub(board))

    handler._pending_in_strike_clusters = [("vsword", (2, 3))]
    handler.frame = 0
    handler._strike_rot_seed = 0

    handler._spawn_multiple_strike_clusters(_HorizStub())

    fallers = [g for g in handler.garbage_fallers if getattr(g, "strike_cluster_id", None) is not None]
    assert fallers, "expected a spawned strike cluster"

    left = min(int(getattr(g, "x", 0)) for g in fallers)
    assert left == 2
