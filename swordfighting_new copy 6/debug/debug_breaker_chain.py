#!/usr/bin/env python3
"""Debug the apply_breaker_chain issue."""

import sys
sys.path.insert(0, '.')

from swordfighting_new.core.board import Board
from swordfighting_new.pieces.piece import Block
from swordfighting_new.mechanics.breaker import BreakerManager

def _place(board, placements):
    """Helper to place blocks on board."""
    for x, y, block in placements:
        board.set_piece(x, y, block)

def debug_breaker_chain():
    """Debug the apply_breaker_chain method."""
    print("=== Debugging apply_breaker_chain ===")

    b = Board()
    _place(b, [
        (5, 10, Block("red", is_breaker=True)),
        (5, 9, Block("red")),
    ])

    print("Initial board:")
    for y in range(5, 15):
        row = []
        for x in range(3, 8):
            cell = b.get_piece(x, y)
            if cell == b.EMPTY:
                row.append(".")
            else:
                color = getattr(cell, 'color', '?')[0].upper()
                breaker = "!" if getattr(cell, 'is_breaker', False) else ""
                row.append(f"{color}{breaker}")
        print(f"y{y}: {' '.join(row)}")

    bm = BreakerManager(b, debug=True)

    print(f"\nInitial state:")
    print(f"  cascade_in_progress: {bm.cascade_in_progress}")
    print(f"  recently_cleared_spaces: {bm.recently_cleared_spaces}")

    # Check what breakers are found
    triggered = bm._find_triggered_breakers()
    print(f"  triggered breakers: {triggered}")

    print(f"\nCalling apply_breaker_chain()...")
    chains, total, per_pass = bm.apply_breaker_chain()

    print(f"Results:")
    print(f"  chains: {chains}")
    print(f"  total: {total}")
    print(f"  per_pass: {per_pass}")

    print(f"\nFinal board:")
    for y in range(5, 15):
        row = []
        for x in range(3, 8):
            cell = b.get_piece(x, y)
            if cell == b.EMPTY:
                row.append(".")
            else:
                color = getattr(cell, 'color', '?')[0].upper()
                breaker = "!" if getattr(cell, 'is_breaker', False) else ""
                row.append(f"{color}{breaker}")
        print(f"y{y}: {' '.join(row)}")

if __name__ == "__main__":
    debug_breaker_chain()
