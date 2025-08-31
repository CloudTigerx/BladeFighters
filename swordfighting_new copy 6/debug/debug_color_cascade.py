#!/usr/bin/env python3

import sys
sys.path.insert(0, '.')

from swordfighting_new.core.board import Board
from swordfighting_new.pieces.piece import Block
from swordfighting_new.mechanics.breaker import BreakerManager

def _place(board, placements):
    for x, y, block in placements:
        board.set_piece(x, y, block)

def test_simple_cascade():
    print("=== Testing Simple Color Cascade ===")
    b = Board()
    print(f"Board dimensions: {b.WIDTH} x {b.HEIGHT}")

    _place(b, [
        (5, 10, Block("red", is_breaker=True)),
        (5, 9, Block("red")),
    ])

    print("Initial board state:")
    print_board(b)

    bm = BreakerManager(b, debug=True)

    print("\n--- Step 1: Find triggered breakers ---")
    triggered = bm._find_triggered_breakers()
    print(f"Triggered breakers: {triggered}")

    print("\n--- Step 2: Clear breakers manually ---")
    cleared = bm._clear_breakers(triggered)
    print(f"Cleared: {cleared}")
    print("Recently cleared spaces:", bm.recently_cleared_spaces)
    print("Cascade colors:", bm.cascade_colors)

    print("\nBoard after clearing breakers (BEFORE gravity):")
    print_board(b)

    # Check the red block at (5, 9)
    red_block = b.get_piece(5, 9)
    print(f"\nRed block at (5, 9): {red_block}")
    print(f"Color: {getattr(red_block, 'color', 'None')}")
    print(f"marked_for_clearing: {getattr(red_block, 'marked_for_clearing', 'None')}")
    print(f"is_breaker: {getattr(red_block, 'is_breaker', 'None')}")
    print(f"is_garbage: {getattr(red_block, 'is_garbage', 'None')}")

    print("\n--- Step 2b: Apply gravity manually ---")
    print("Checking board position (5,11) before gravity:")
    print(f"(5,11): {b.get_piece(5, 11)}")
    gravity_moves = bm.cascade_manager.apply_full()
    print(f"Gravity moved {gravity_moves} blocks")
    print("Checking board position (5,11) after gravity:")
    print(f"(5,11): {b.get_piece(5, 11)}")
    print("Checking all positions in column 5:")
    for y in range(24):
        cell = b.get_piece(5, y)
        if cell != b.EMPTY:
            print(f"  (5,{y}): {cell} (color: {getattr(cell, 'color', 'None')})")

    print("\nBoard after gravity:")
    print_board(b)

    print("\n--- Step 3: Apply cascade clearing ---")
    cascade_cleared = bm._apply_cascade_clearing()
    print(f"Cascade cleared: {cascade_cleared}")
    print("Recently cleared spaces:", bm.recently_cleared_spaces)
    print("Cascade colors:", bm.cascade_colors)

    print("\nBoard after cascade clearing:")
    print_board(b)

def print_board(b):
    for y in range(6, 18):  # Even wider range
        row = ""
        for x in range(3, 8):
            cell = b.get_piece(x, y)
            if cell == b.EMPTY:
                row += ". "
            else:
                color = getattr(cell, 'color', '?')
                is_breaker = hasattr(cell, 'is_breaker') and getattr(cell, 'is_breaker', False)
                marker = f"{color[0].upper()}B" if is_breaker else color[0].upper()
                row += f"{marker} "
        print(f"Y{y}: {row}")

if __name__ == "__main__":
    test_simple_cascade()
