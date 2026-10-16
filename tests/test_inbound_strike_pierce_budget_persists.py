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
def test_single_strike_pierce_budget_persists_across_calls():
    """Regression: strike pierce budget reset every tick.

    A small sword (<=4 rows) should only pierce 2 normal blocks total, not 2 per tick.
    """

    Board = _find_board_class()
    InboundAttackHandler = _find_inbound_attack_handler()

    board = Board()

    # Place 4 normal blocks below the strike piece.
    # Strike starts at y=5, so targets are y=6..9.
    for yy in (6, 7, 8, 9):
        board.set_piece(2, yy, Block('blue'))

    handler = InboundAttackHandler(board=board, timing=_TimingStub(), piece_mover=None, gravity_manager=None)

    class _P:
        def __init__(self):
            self.x = 2
            self.y = 5
            self.sword_rows = 2

    g = _P()

    cluster_cells = set()

    pierced1 = handler._resolve_strike_pierce_before_lock(g, cluster_cells)
    assert pierced1 is True

    # Budget for sword_rows=2 is 2; so y=6 and y=7 should be cleared, y=8 remains.
    assert board.get_piece(2, 6) == board.EMPTY
    assert board.get_piece(2, 7) == board.EMPTY
    assert board.get_piece(2, 8) != board.EMPTY

    # Second call in a later tick should NOT pierce any more blocks.
    pierced2 = handler._resolve_strike_pierce_before_lock(g, cluster_cells)
    assert pierced2 is False

    assert board.get_piece(2, 8) != board.EMPTY
    assert board.get_piece(2, 9) != board.EMPTY


@pytest.mark.unit
def test_single_strike_breaker_destruction_counts_as_pierce():
    """Regression: breaker-only destruction returned False and caused premature lock."""

    Board = _find_board_class()
    InboundAttackHandler = _find_inbound_attack_handler()

    board = Board()

    # Breaker directly below.
    board.set_piece(1, 6, Block('red', is_breaker=True))

    handler = InboundAttackHandler(board=board, timing=_TimingStub(), piece_mover=None, gravity_manager=None)

    class _P:
        def __init__(self):
            self.x = 1
            self.y = 5
            self.sword_rows = 2

    g = _P()

    pierced = handler._resolve_strike_pierce_before_lock(g, set())
    assert pierced is True
    assert board.get_piece(1, 6) == board.EMPTY
