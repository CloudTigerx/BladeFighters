import pytest

from swordfighting_new.core.board import Board
from swordfighting_new.fighters.inbound_attack_handler import InboundAttackHandler
from swordfighting_new.pieces.piece import Block


class _TimingStub:
    target_fps = 60
    autonomous_fall_interval_frames = 6


@pytest.mark.unit
def test_spawn_sprinkles_second_pass_fills_capacity_even_if_first_pass_order_is_bad(monkeypatch):
    board = Board()

    # Make column 0 report zero remaining capacity.
    # NOTE: Board.get_column_heights() considers a column "full" when row y=0 is occupied.
    board.set_piece(0, 0, Block("blue"))

    handler = InboundAttackHandler(
        board=board,
        timing=_TimingStub(),
        piece_mover=None,
        gravity_manager=None,
    )

    # Simulate a pathological ordering bug: the first pass only considers a single full column.
    def _bad_order(_avoid_cols, _prefer_cols):
        return [0]

    monkeypatch.setattr(handler, "_sprinkle_column_order", _bad_order)

    placed = handler._spawn_sprinkles_avoiding(amount=3, avoid_cols=set(), prefer_cols=set())

    assert placed == 3
    assert len(handler.garbage_fallers) == 3

    for g in handler.garbage_fallers:
        assert getattr(g.blocks[0], "attack_state", None) == "sprinkle"
        assert int(getattr(g, "x", -1)) != 0
        assert int(getattr(g, "y", 0)) < 0
