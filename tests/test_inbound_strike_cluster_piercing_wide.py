import pytest

from swordfighting_new.pieces.piece import Block


class _TimingStub:
    target_fps = 60
    autonomous_fall_interval_frames = 6


def _find_inbound_attack_handler():
    # Avoid tight coupling to module layout changes.
    from swordfighting_new.fighters.inbound_attack_handler import InboundAttackHandler

    return InboundAttackHandler


def _find_board_class():
    from swordfighting_new.core.board import Board

    return Board


def _make_piece(x, y):
    # Lightweight piece-like object: the handler only needs .x, .y, and .sword_rows.
    class _P:
        def __init__(self, x, y):
            self.x = x
            self.y = y
            self.sword_rows = 2

    return _P(x, y)


@pytest.mark.unit
def test_strike_cluster_pierces_all_columns_in_step():
    """A wide (2-column) inbound strike cluster should pierce in both columns.

    Regression: piercing budget was shared across columns and consumed on the first
    column processed, causing only one column to be pierced.
    """

    Board = _find_board_class()
    InboundAttackHandler = _find_inbound_attack_handler()

    board = Board()

    # Place two normal blocks directly below the bottom edge of a 2-wide sword.
    # Pieces are located at y=5 in columns 2 and 3; the pierced targets are at y=6.
    board.set_piece(2, 6, Block('blue'))
    board.set_piece(3, 6, Block('green'))

    handler = InboundAttackHandler(
        board=board,
        timing=_TimingStub(),
        piece_mover=None,
        gravity_manager=None,
    )

    pieces = [_make_piece(2, 5), _make_piece(3, 5)]
    cluster_cells = set()

    handler._resolve_strike_cluster_pierce_before_lock(pieces, cluster_cells)

    assert board.get_piece(2, 6) == board.EMPTY
    assert board.get_piece(3, 6) == board.EMPTY

    # After piercing, the cluster should be able to step down (possibly multiple rows).
    ys_by_x = {p.x: p.y for p in pieces}
    assert ys_by_x[2] >= 6
    assert ys_by_x[3] >= 6
    assert ys_by_x[2] == ys_by_x[3]
