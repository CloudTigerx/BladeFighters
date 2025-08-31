from swordfighting_new.core.board import Board
from swordfighting_new.mechanics.breaker import BreakerManager
from swordfighting_new.pieces.piece import Block


def _place(board: Board, placements):
    for x,y,b in placements:
        board.set_piece(x,y,b)


def _column_cells(board, x):
    return [board.get_piece(x,y) for y in range(board.HEIGHT)]


def test_no_floating_blocks_after_fast_cascade():
    b = Board()
    # Create a gapped column then compress using new fast cascade.
    _place(b, [
        (2, 20, Block('red')),
        (2, 17, Block('red')),
        (2, 10, Block('red')),
    ])
    bm = BreakerManager(b)
    moved = bm.cascade_step(mode='fast')
    assert moved == 3
    # Verify contiguous bottom stack
    col = _column_cells(b, 2)
    empties_seen = False
    for y in range(b.HEIGHT-1, -1, -1):  # bottom->top
        cell = col[y]
        if cell == b.EMPTY:
            if not empties_seen:
                empties_seen = True
            continue
        # solid
        assert not empties_seen, f"Floating block detected at (2,{y})"


def test_no_floating_after_multiple_passes_chain():
    b = Board()
    # Layout two breakers whose first clear creates gaps in other columns.
    # We'll simulate clears by removing cells then cascading.
    for x in range(4):
        for y in range(10, 15):
            b.set_piece(x, y, Block('blue'))
    # Create holes in middle column to mimic clear
    b.set_piece(1, 11, b.EMPTY)
    b.set_piece(1, 13, b.EMPTY)
    bm = BreakerManager(b)
    # Run full compression
    bm.cascade_full_stepwise(mode='fast')
    # Invariant: each column contiguous at bottom
    for x in range(b.WIDTH):
        empties = False
        for y in range(b.HEIGHT-1, -1, -1):
            cell = b.get_piece(x, y)
            if cell == b.EMPTY:
                if not empties:
                    empties = True
                continue
            assert not empties, f"Floating at {(x,y)}"
