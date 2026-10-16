from __future__ import annotations

import pytest

from swordfighting_new.pieces.piece import Block, Piece


class _TimingStub:
    target_fps = 60
    autonomous_fall_interval_frames = 6


class _GravityStub:
    def __init__(self, board):
        self.board = board

    def lock_piece(self, piece):
        # Minimal behavior: write cells to the board.
        self.board.place_piece(piece)


def _find_inbound_attack_handler():
    from swordfighting_new.fighters.inbound_attack_handler import InboundAttackHandler

    return InboundAttackHandler


def _find_board_class():
    from swordfighting_new.core.board import Board

    return Board


def _make_strike_single(x: int, y: int, handedness: int = 1) -> Piece:
    p = Piece.single_block("red", is_strike=True, attack_state="strike")
    p.controllable = False
    p.x = x
    p.y = y
    p.attack_state = "strike"
    p.sword_rows = 6
    p.sword_width = 2
    p.strike_handedness = int(handedness)
    # Force processing each tick by setting the timer to the interval.
    p.autonomous_fall_interval = 1
    p.autonomous_fall_timer = 1
    return p


@pytest.mark.unit
def test_single_strike_does_not_oscillate_when_sidestep_hits_wall():
    """Regression: strikes must not change columns mid-fall.

    When a strike is blocked by an unpierceable 2x2+ cluster, it locks in place
    (lane chosen at spawn), rather than shifting sideways.
    """

    Board = _find_board_class()
    InboundAttackHandler = _find_inbound_attack_handler()

    board = Board()

    # Build a 2x2 blue cluster at columns 4-5, rows 6-7.
    for xx in (4, 5):
        for yy in (6, 7):
            board.set_piece(xx, yy, Block("blue"))

    handler = InboundAttackHandler(board=board, timing=_TimingStub(), piece_mover=None, gravity_manager=_GravityStub(board))

    g = _make_strike_single(x=5, y=5, handedness=1)
    handler.garbage_fallers = [g]

    handler.update_inbound_garbage()

    # Locked directly above the cluster without drifting.
    assert board.get_piece(5, 5) != board.EMPTY
    assert handler.garbage_fallers == []


@pytest.mark.unit
def test_strike_cluster_group_does_not_oscillate_when_sidestep_hits_wall():
    """Same as above, but through the strike-cluster grouping path."""

    Board = _find_board_class()
    InboundAttackHandler = _find_inbound_attack_handler()

    board = Board()

    for xx in (4, 5):
        for yy in (6, 7):
            board.set_piece(xx, yy, Block("blue"))

    handler = InboundAttackHandler(board=board, timing=_TimingStub(), piece_mover=None, gravity_manager=_GravityStub(board))

    # One piece, but marked as part of a strike cluster so it uses the strike-group logic.
    g = _make_strike_single(x=5, y=5, handedness=1)
    g.strike_cluster_id = 2  # even -> prefer right, which hits wall

    handler.garbage_fallers = [g]

    handler.update_inbound_garbage()

    assert board.get_piece(5, 5) != board.EMPTY
    assert handler.garbage_fallers == []


@pytest.mark.unit
def test_single_width_strike_does_not_sidestep_around_cluster():
    """Strikes should not change columns when they touch a cluster."""

    Board = _find_board_class()
    InboundAttackHandler = _find_inbound_attack_handler()

    board = Board()

    # 2x2 cluster below the strike.
    for xx in (2, 3):
        for yy in (6, 7):
            board.set_piece(xx, yy, Block("blue"))

    handler = InboundAttackHandler(board=board, timing=_TimingStub(), piece_mover=None, gravity_manager=_GravityStub(board))

    g = _make_strike_single(x=2, y=5, handedness=1)
    g.sword_width = 1
    handler.garbage_fallers = [g]

    handler.update_inbound_garbage()

    assert board.get_piece(2, 5) != board.EMPTY
    assert handler.garbage_fallers == []
