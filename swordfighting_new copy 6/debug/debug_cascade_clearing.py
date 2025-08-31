#!/usr/bin/env python3
"""Debug the cascade clearing issue."""

import sys
sys.path.insert(0, '.')

from swordfighting_new.core.board import Board
from swordfighting_new.pieces.piece import Block
from swordfighting_new.mechanics.breaker import BreakerManager

def _place(board, placements):
    """Helper to place blocks on board."""
    for x, y, block in placements:
        board.set_piece(x, y, block)

def print_board(board, title="Board"):
    """Print board state for debugging."""
    print(f"\n{title}:")
    print("  ", end="")
    for x in range(board.WIDTH):
        print(f"{x:2}", end="")
    print()

    for y in range(min(15, board.HEIGHT)):  # Only show top 15 rows
        print(f"{y:2}", end="")
        for x in range(board.WIDTH):
            cell = board.get_piece(x, y)
            if cell == board.EMPTY:
                print(" .", end="")
            elif hasattr(cell, 'color'):
                color_short = cell.color[0].upper() if cell.color else '?'
                if hasattr(cell, 'is_breaker') and cell.is_breaker:
                    print(f" {color_short}!", end="")
                else:
                    print(f" {color_short}", end="")
            else:
                print(" ?", end="")
        print()

def debug_cascade_clearing():
    """Debug what's happening with cascade clearing."""
    print("=== Debugging Cascade Clearing ===")

    b = Board()

    # Simple setup: one breaker with connected blocks
    placements = [
        (5, 10, Block("red", is_breaker=True)),
        (5, 9, Block("red")),
        (5, 8, Block("red")),
    ]

    _place(b, placements)
    print_board(b, "Initial Setup")

    bm = BreakerManager(b, debug=True)

    print(f"\nCascade in progress: {bm.cascade_in_progress}")
    print(f"Recently cleared spaces: {bm.recently_cleared_spaces}")
    print(f"Cascade colors: {bm.cascade_colors}")

    # Step 1: Apply breakers
    print(f"\n=== Step 1: Apply breakers ===")
    cleared = bm.apply_breakers()
    print(f"Cleared: {cleared}")
    print(f"Cascade in progress: {bm.cascade_in_progress}")
    print(f"Recently cleared spaces: {bm.recently_cleared_spaces}")
    print(f"Cascade colors: {bm.cascade_colors}")
    print_board(b, "After Step 1")

    # Step 2: Apply again (should continue cascade)
    print(f"\n=== Step 2: Apply breakers again ===")
    cleared = bm.apply_breakers()
    print(f"Cleared: {cleared}")
    print(f"Cascade in progress: {bm.cascade_in_progress}")
    print(f"Recently cleared spaces: {bm.recently_cleared_spaces}")
    print(f"Cascade colors: {bm.cascade_colors}")
    print_board(b, "After Step 2")

    # Step 3: Apply again
    print(f"\n=== Step 3: Apply breakers again ===")
    cleared = bm.apply_breakers()
    print(f"Cleared: {cleared}")
    print(f"Cascade in progress: {bm.cascade_in_progress}")
    print(f"Recently cleared spaces: {bm.recently_cleared_spaces}")
    print(f"Cascade colors: {bm.cascade_colors}")
    print_board(b, "After Step 3")

    # Step 4: Apply again
    print(f"\n=== Step 4: Apply breakers again ===")
    cleared = bm.apply_breakers()
    print(f"Cleared: {cleared}")
    print(f"Cascade in progress: {bm.cascade_in_progress}")
    print(f"Recently cleared spaces: {bm.recently_cleared_spaces}")
    print(f"Cascade colors: {bm.cascade_colors}")
    print_board(b, "After Step 4")

if __name__ == "__main__":
    debug_cascade_clearing()
