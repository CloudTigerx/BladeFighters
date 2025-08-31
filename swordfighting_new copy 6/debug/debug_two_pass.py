#!/usr/bin/env python3
"""Debug the two-pass chain test."""

import sys
sys.path.insert(0, '.')

from swordfighting_new.core.board import Board
from swordfighting_new.pieces.piece import Block
from swordfighting_new.mechanics.breaker import BreakerManager

def _place(board, placements):
    """Helper to place blocks on board."""
    for x, y, block in placements:
        board.set_piece(x, y, block)

def debug_two_pass_chain():
    """Debug the two-pass chain scenario."""
    print("=== Debugging Two-Pass Chain ===")

    b = Board()
    _place(b, [
        (5, 10, Block("red", is_breaker=True)),
        (5, 9, Block("red")),
        (5, 4, Block("red", is_breaker=True)),
        (5, 2, Block("red")),
    ])

    print("Initial board:")
    for y in range(0, 12):
        row = []
        for x in range(4, 7):
            cell = b.get_piece(x, y)
            if cell == b.EMPTY:
                row.append(".")
            else:
                color = getattr(cell, 'color', '?')[0].upper()
                breaker = "!" if getattr(cell, 'is_breaker', False) else ""
                row.append(f"{color}{breaker}")
        print(f"y{y:2}: {' '.join(row)}")

    bm = BreakerManager(b, debug=True)

    # Check initially triggered breakers
    triggered = bm._find_triggered_breakers()
    print(f"\nInitially triggered breakers: {triggered}")

    # Run chain
    chains, total, per_pass = bm.apply_breaker_chain()
    print(f"\nResults:")
    print(f"  Chains: {chains}")
    print(f"  Total: {total}")
    print(f"  Per pass: {per_pass}")

    print("\nFinal board:")
    for y in range(0, 12):
        row = []
        for x in range(4, 7):
            cell = b.get_piece(x, y)
            if cell == b.EMPTY:
                row.append(".")
            else:
                color = getattr(cell, 'color', '?')[0].upper()
                breaker = "!" if getattr(cell, 'is_breaker', False) else ""
                row.append(f"{color}{breaker}")
        print(f"y{y:2}: {' '.join(row)}")

if __name__ == "__main__":
    debug_two_pass_chain()
