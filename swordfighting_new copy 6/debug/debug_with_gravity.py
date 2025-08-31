#!/usr/bin/env python3
"""Debug with gravity application."""

import sys
sys.path.insert(0, '.')

from swordfighting_new.core.board import Board
from swordfighting_new.pieces.piece import Block
from swordfighting_new.mechanics.breaker import BreakerManager

def _place(board, placements):
    """Helper to place blocks on board."""
    for x, y, block in placements:
        board.set_piece(x, y, block)

def debug_with_gravity():
    """Debug cascade clearing with gravity."""
    print("=== Debug with Gravity ===")

    b = Board()
    _place(b, [
        (5, 10, Block("red", is_breaker=True)),
        (5, 9, Block("red")),
        (5, 4, Block("red", is_breaker=True)),
        (5, 2, Block("red")),
    ])

    def print_board(title):
        print(f"\n{title}:")
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

    print_board("Initial board")

    bm = BreakerManager(b, debug=True)

    # Manually run one breaker pass
    print(f"\n=== Breaker Pass 1 ===")
    step = 0
    while True:
        step += 1
        cleared = bm.apply_breakers()
        print(f"Step {step}: cleared {cleared} (cascade: {bm.cascade_in_progress})")
        print_board(f"After step {step}")
        if cleared == 0:
            break

    print(f"\n=== Applying Gravity ===")
    moved = bm.cascade_manager.apply_full()
    print(f"Gravity moved {moved} blocks")
    print_board("After gravity")

    print(f"\n=== Checking for next breaker pass ===")
    triggered = bm._find_triggered_breakers()
    print(f"Newly triggered breakers: {triggered}")

    if triggered:
        print(f"\n=== Breaker Pass 2 ===")
        step = 0
        while True:
            step += 1
            cleared = bm.apply_breakers()
            print(f"Step {step}: cleared {cleared} (cascade: {bm.cascade_in_progress})")
            print_board(f"After step {step}")
            if cleared == 0:
                break

if __name__ == "__main__":
    debug_with_gravity()
