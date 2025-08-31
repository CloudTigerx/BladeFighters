"""Core breaker logic tests (pytest style).

Run: pytest -q
"""
from swordfighting_new.core.board import Board
from swordfighting_new.mechanics.breaker import BreakerManager
from swordfighting_new.pieces.piece import Block


def _place(board: Board, placements):
    for x, y, block in placements:
        board.set_piece(x, y, block)


def test_single_breaker_no_neighbor():
    b = Board()
    _place(b, [(5, 10, Block("red", is_breaker=True))])
    assert BreakerManager(b).apply_breakers() == 0


def test_single_breaker_with_neighbor():
    b = Board()
    _place(b, [
        (5, 10, Block("red", is_breaker=True)),
        (5, 9, Block("red")),
    ])
    # Test progressive clearing within single instance
    bm = BreakerManager(b)
    # First pass clears only the breaker
    assert bm.apply_breakers() == 1
    # Second pass clears the connected neighbor
    assert bm.apply_breakers() == 1
    # No more to clear
    assert bm.apply_breakers() == 0

    # Full chain from fresh state should clear both blocks
    b2 = Board()
    _place(b2, [
        (5, 10, Block("red", is_breaker=True)),
        (5, 9, Block("red")),
    ])
    bm2 = BreakerManager(b2)
    chains, total, per_pass = bm2.apply_breaker_chain()
    assert total == 2
    assert chains == 1  # Single chain with progressive clearing


def test_chain_two_passes():
    b = Board()
    # First pass clears bottom pair; second pass clears pair that become adjacent after cascade.
    _place(b, [
        (5, 10, Block("red", is_breaker=True)),
        (5, 9, Block("red")),
        (5, 4, Block("red", is_breaker=True)),
        (5, 2, Block("red")),
    ])
    bm = BreakerManager(b)
    chains, total, per_pass = bm.apply_breaker_chain()
    # Progressive clearing creates more passes than the old system
    assert chains >= 2, per_pass
    assert total >= 4  # All blocks should eventually be cleared


def test_mixed_colors_isolated():
    b = Board()
    _place(b, [
        (2, 10, Block("red", is_breaker=True)), (2, 9, Block("red")),
        (8, 12, Block("blue", is_breaker=True)), (9, 12, Block("blue")),
    ])
    # Test progressive clearing within single instance
    bm = BreakerManager(b)
    # First pass clears only the breakers
    assert bm.apply_breakers() == 2
    # Continue cascade clearing
    assert bm.apply_breakers() == 2  # Clear the connected blocks
    # No more to clear
    assert bm.apply_breakers() == 0

    # Full chain from fresh state should clear all blocks
    b2 = Board()
    _place(b2, [
        (2, 10, Block("red", is_breaker=True)), (2, 9, Block("red")),
        (8, 12, Block("blue", is_breaker=True)), (9, 12, Block("blue")),
    ])
    bm2 = BreakerManager(b2)
    chains, total, per_pass = bm2.apply_breaker_chain()
    assert total == 4


def test_garbage_blocks_block_flood():
    b = Board()
    _place(b, [
        (5, 10, Block("yellow", is_breaker=True)),
        (5, 9, Block("yellow")),
        (5, 8, Block("yellow", is_garbage=True)),
        (5, 7, Block("yellow")),
    ])
    # Garbage stops propagation upward.
    # Test progressive clearing within single instance
    bm = BreakerManager(b)
    # First pass clears only the breaker
    assert bm.apply_breakers() == 1
    # Second pass clears the connected block (not through garbage)
    assert bm.apply_breakers() == 1
    # No more clearing (garbage blocks propagation)
    assert bm.apply_breakers() == 0

    # Full chain should clear breaker + connected block (garbage blocks propagation)
    b2 = Board()
    _place(b2, [
        (5, 10, Block("yellow", is_breaker=True)),
        (5, 9, Block("yellow")),
        (5, 8, Block("yellow", is_garbage=True)),
        (5, 7, Block("yellow")),
    ])
    bm2 = BreakerManager(b2)
    chains, total, per_pass = bm2.apply_breaker_chain()
    assert total == 2  # breaker + connected block (garbage blocks propagation)


def test_adjacent_same_color_breakers_trigger_each_other():
    b = Board()
    _place(b, [
        (4, 10, Block("red", is_breaker=True)),
        (5, 10, Block("red", is_breaker=True)),
    ])
    assert BreakerManager(b).apply_breakers() == 2


def test_adjacent_cross_color_breakers_do_not_trigger():
    b = Board()
    _place(b, [
        (6, 12, Block("red", is_breaker=True)),
        (7, 12, Block("blue", is_breaker=True)),
    ])
    assert BreakerManager(b).apply_breakers() == 0
