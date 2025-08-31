#!/usr/bin/env python3
"""Step-by-step debug of cascade clearing."""

import sys
sys.path.insert(0, '.')

from swordfighting_new.core.board import Board
from swordfighting_new.pieces.piece import Block
from swordfighting_new.mechanics.breaker import BreakerManager

def _place(board, placements):
    """Helper to place blocks on board."""
    for x, y, block in placements:
        board.set_piece(x, y, block)

def debug_step_by_step():
    """Debug cascade clearing step by step."""
    print("=== Step-by-Step Cascade Debug ===")

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

    step = 0
    while True:
        step += 1
        print(f"\n--- Step {step} ---")
        print(f"Cascade in progress: {bm.cascade_in_progress}")
        print(f"Recently cleared: {bm.recently_cleared_spaces}")
        print(f"Cascade colors: {bm.cascade_colors}")

        # Check triggered breakers
        triggered = bm._find_triggered_breakers()
        print(f"Triggered breakers: {triggered}")

        cleared = bm.apply_breakers()
        print(f"Cleared: {cleared}")

        print_board(f"After step {step}")

        if cleared == 0:
            break
        if step > 10:  # Safety
            break

    print(f"\nFinal state after {step} steps")

if __name__ == "__main__":
    debug_step_by_step()
