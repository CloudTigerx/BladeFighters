#!/usr/bin/env python3
"""Debug the failing tests to understand expected vs actual behavior."""

from swordfighting_new.core.board import Board
from swordfighting_new.mechanics.breaker import BreakerManager
from swordfighting_new.pieces.piece import Block

def _place(board: Board, placements):
    for x, y, block in placements:
        board.set_piece(x, y, block)

def print_board(board, title="Board"):
    """Print board state with colors."""
    print(f"\n{title}:")
    for y in range(min(15, board.HEIGHT)):
        row = ""
        for x in range(board.WIDTH):
            cell = board.get_piece(x, y)
            if cell == board.EMPTY:
                row += "."
            elif hasattr(cell, 'marked_for_clearing') and cell.marked_for_clearing:
                row += "X"
            elif hasattr(cell, 'is_breaker') and cell.is_breaker:
                row += cell.color[0].upper()
            else:
                row += cell.color[0]
        print(f"{y:2d}: {row}")

def debug_test_single_breaker_no_neighbor():
    """Debug the failing test - breaker with no neighbor should not trigger."""
    print("=== test_single_breaker_no_neighbor ===")
    b = Board()
    _place(b, [(5, 10, Block("red", is_breaker=True))])
    print_board(b, "Setup: Isolated breaker")

    bm = BreakerManager(b, debug=True)
    result = bm.apply_breakers()
    print(f"apply_breakers() returned: {result}")
    print_board(b, "After apply_breakers")
    print(f"Expected: 0, Got: {result}")

def debug_test_single_breaker_with_neighbor():
    """Debug the failing test - breaker with neighbor should clear both."""
    print("\n=== test_single_breaker_with_neighbor ===")
    b = Board()
    _place(b, [
        (5, 10, Block("red", is_breaker=True)),
        (5, 9, Block("red")),
    ])
    print_board(b, "Setup: Breaker with neighbor")

    bm = BreakerManager(b, debug=True)
    result = bm.apply_breakers()
    print(f"apply_breakers() returned: {result}")
    print_board(b, "After apply_breakers")
    print(f"Expected: 2, Got: {result}")

    # Test full chain
    print("\nTesting full chain:")
    b2 = Board()
    _place(b2, [
        (5, 10, Block("red", is_breaker=True)),
        (5, 9, Block("red")),
    ])
    bm2 = BreakerManager(b2, debug=True)
    chains, total, per_pass = bm2.apply_breaker_chain()
    print(f"apply_breaker_chain() returned: chains={chains}, total={total}, per_pass={per_pass}")

def debug_test_cross_color_breakers():
    """Debug cross-color breakers that shouldn't trigger each other."""
    print("\n=== test_adjacent_cross_color_breakers_do_not_trigger ===")
    b = Board()
    _place(b, [
        (6, 12, Block("red", is_breaker=True)),
        (7, 12, Block("blue", is_breaker=True)),
    ])
    print_board(b, "Setup: Adjacent different color breakers")

    bm = BreakerManager(b, debug=True)
    result = bm.apply_breakers()
    print(f"apply_breakers() returned: {result}")
    print_board(b, "After apply_breakers")
    print(f"Expected: 0, Got: {result}")

if __name__ == "__main__":
    debug_test_single_breaker_no_neighbor()
    debug_test_single_breaker_with_neighbor()
    debug_test_cross_color_breakers()
