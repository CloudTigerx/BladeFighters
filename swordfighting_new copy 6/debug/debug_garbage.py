#!/usr/bin/env python3
"""Debug the garbage block test."""

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
            elif hasattr(cell, 'is_garbage') and cell.is_garbage:
                row += "#"  # Garbage
            else:
                row += cell.color[0]
        print(f"{y:2d}: {row}")

def debug_garbage_test():
    """Debug the garbage blocks test."""
    print("=== test_garbage_blocks_block_flood ===")
    b = Board()
    _place(b, [
        (5, 10, Block("yellow", is_breaker=True)),
        (5, 9, Block("yellow")),
        (5, 8, Block("yellow", is_garbage=True)),
        (5, 7, Block("yellow")),
    ])
    print_board(b, "Setup: Breaker with garbage blocking propagation")

    # Test single pass
    bm = BreakerManager(b, debug=True)
    result = bm.apply_breakers()
    print(f"apply_breakers() returned: {result}")
    print_board(b, "After single apply_breakers()")

    # Test full chain
    print("\nTesting full chain:")
    b2 = Board()
    _place(b2, [
        (5, 10, Block("yellow", is_breaker=True)),
        (5, 9, Block("yellow")),
        (5, 8, Block("yellow", is_garbage=True)),
        (5, 7, Block("yellow")),
    ])
    bm2 = BreakerManager(b2, debug=True)
    chains, total, per_pass = bm2.apply_breaker_chain()
    print(f"apply_breaker_chain() returned: chains={chains}, total={total}, per_pass={per_pass}")
    print_board(b2, "Final state after full chain")

if __name__ == "__main__":
    debug_garbage_test()
