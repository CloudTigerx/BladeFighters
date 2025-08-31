#!/usr/bin/env python3
"""Debug the test behavior."""

import sys
sys.path.insert(0, '.')

from swordfighting_new.core.board import Board
from swordfighting_new.pieces.piece import Block
from swordfighting_new.mechanics.breaker import BreakerManager

def _place(board, placements):
    """Helper to place blocks on board."""
    for x, y, block in placements:
        board.set_piece(x, y, block)

def debug_test_behavior():
    """Debug what the test is doing."""
    print("=== Debugging Test Behavior ===")

    b = Board()
    _place(b, [
        (5, 10, Block("red", is_breaker=True)),
        (5, 9, Block("red")),
    ])

    print("Initial board:")
    for y in range(8, 12):
        row = []
        for x in range(4, 7):
            cell = b.get_piece(x, y)
            if cell == b.EMPTY:
                row.append(".")
            else:
                color = getattr(cell, 'color', '?')[0].upper()
                breaker = "!" if getattr(cell, 'is_breaker', False) else ""
                row.append(f"{color}{breaker}")
        print(f"y{y}: {' '.join(row)}")

    # First call - like in the test
    print(f"\nCalling first BreakerManager(b).apply_breakers()...")
    result1 = BreakerManager(b).apply_breakers()
    print(f"Result: {result1}")

    print("Board after first call:")
    for y in range(8, 12):
        row = []
        for x in range(4, 7):
            cell = b.get_piece(x, y)
            if cell == b.EMPTY:
                row.append(".")
            else:
                color = getattr(cell, 'color', '?')[0].upper()
                breaker = "!" if getattr(cell, 'is_breaker', False) else ""
                row.append(f"{color}{breaker}")
        print(f"y{y}: {' '.join(row)}")

    # Second call - like in the test
    print(f"\nCalling second BreakerManager(b).apply_breaker_chain()...")
    bm = BreakerManager(b)
    chains, total, per_pass = bm.apply_breaker_chain()
    print(f"Results: chains={chains}, total={total}, per_pass={per_pass}")

    print("Board after second call:")
    for y in range(8, 12):
        row = []
        for x in range(4, 7):
            cell = b.get_piece(x, y)
            if cell == b.EMPTY:
                row.append(".")
            else:
                color = getattr(cell, 'color', '?')[0].upper()
                breaker = "!" if getattr(cell, 'is_breaker', False) else ""
                row.append(f"{color}{breaker}")
        print(f"y{y}: {' '.join(row)}")

if __name__ == "__main__":
    debug_test_behavior()
