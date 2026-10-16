from __future__ import annotations

import pytest

from swordfighting_new.pieces.piece import Piece


class _TimingStub:
    target_fps = 60
    autonomous_fall_interval_frames = 6


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
def test_inbound_bulk_uses_existing_spawn_count_for_capacity():
    """Regression: capacity checks must include already spawned above-board fallers.

    Otherwise bulk inbound can over-stack a column (even when others have room),
    leading to avoidable y<0 locks and surprise defeats.
    """

    Board = _find_board_class()
    InboundAttackHandler = _find_inbound_attack_handler()

    board = Board()
    handler = InboundAttackHandler(board=board, timing=_TimingStub(), piece_mover=None, gravity_manager=_GravityStub(board))

    # Make a deterministic column order.
    handler._sprinkle_column_order = lambda avoid, prefer: [0, 1, 2, 3, 4, 5]

    # Create an existing above-board inbound faller in col 0.
    existing = Piece.single_block(color="red", is_garbage=False, is_strike=False, attack_state="sprinkle")
    existing.x = 0
    existing.y = -1
    existing.controllable = False
    handler.garbage_fallers.append(existing)

    # Fill column 0 so it has capacity=1 (only y=0 is empty).
    # With existing_spawn_count=1, it should not place any more into col 0.
    for y in range(1, int(board.HEIGHT)):
        board.set_piece(0, y, object())

    before = len(handler.garbage_fallers)
    handler._spawn_bulk(amount=1, is_strike=False)
    after = len(handler.garbage_fallers)

    assert after == before + 1
    new_piece = handler.garbage_fallers[-1]
    assert int(getattr(new_piece, "x", -1)) != 0
