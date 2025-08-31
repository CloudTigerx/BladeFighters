#!/usr/bin/env python3
"""Test the corrected progressive clearing behavior."""

import sys
sys.path.insert(0, '.')

from swordfighting_new.core.board import Board
from swordfighting_new.pieces.piece import Block
from swordfighting_new.mechanics.breaker import BreakerManager

def _place(board, placements):
    """Helper to place blocks on board."""
    for x, y, block in placements:
        board.set_piece(x, y, block)

def test_progressive_clearing():
    """Test progressive clearing within single BreakerManager instance."""
    print("=== Testing Progressive Clearing ===")

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

    bm = BreakerManager(b, debug=True)

    # First call should clear the breaker
    print(f"\nStep 1: Apply breakers (should clear breaker only)")
    cleared1 = bm.apply_breakers()
    print(f"Cleared: {cleared1}")
    print(f"Cascade in progress: {bm.cascade_in_progress}")

    print("Board after step 1:")
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

    # Second call should continue cascade clearing
    print(f"\nStep 2: Apply breakers again (should continue cascade)")
    cleared2 = bm.apply_breakers()
    print(f"Cleared: {cleared2}")
    print(f"Cascade in progress: {bm.cascade_in_progress}")

    print("Board after step 2:")
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

    print(f"\nTotal cleared: {cleared1 + cleared2}")

def test_apply_breaker_chain():
    """Test apply_breaker_chain with fresh board."""
    print("\n=== Testing apply_breaker_chain ===")

    b = Board()
    _place(b, [
        (5, 10, Block("red", is_breaker=True)),
        (5, 9, Block("red")),
    ])

    bm = BreakerManager(b, debug=True)
    chains, total, per_pass = bm.apply_breaker_chain()

    print(f"Chains: {chains}")
    print(f"Total cleared: {total}")
    print(f"Per pass: {per_pass}")

    return total

if __name__ == "__main__":
    test_progressive_clearing()
    total = test_apply_breaker_chain()
    print(f"\nExpected total from apply_breaker_chain: {total}")

    if total == 2:
        print("✓ apply_breaker_chain works correctly")
    else:
        print("✗ apply_breaker_chain has issues")
