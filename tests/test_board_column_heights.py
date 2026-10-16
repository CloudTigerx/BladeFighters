import pytest

from swordfighting_new.core.board import Board
from swordfighting_new.pieces.piece import Block


@pytest.mark.unit
def test_get_column_heights_reports_true_stack_height() -> None:
    b = Board()

    # Empty => all 0.
    assert b.get_column_heights() == [0] * b.WIDTH

    # Bottom-only fill => height 1.
    b.set_piece(0, b.HEIGHT - 1, Block("red"))
    hs = b.get_column_heights()
    assert hs[0] == 1

    # Add a block 3 rows above bottom => height 4.
    b.set_piece(0, b.HEIGHT - 4, Block("blue"))
    hs = b.get_column_heights()
    assert hs[0] == 4

    # Top cell occupied => column full.
    b.set_piece(1, 0, Block("green"))
    hs = b.get_column_heights()
    assert hs[1] == b.HEIGHT
