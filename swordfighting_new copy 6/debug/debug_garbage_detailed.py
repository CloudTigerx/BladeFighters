#!/usr/bin/env python3
"""More detailed debug of the garbage block cascade behavior."""

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

def debug_step_by_step():
    """Debug step by step cascade behavior."""
    print("=== Step by Step Garbage Test ===")
    b = Board()
    _place(b, [
        (5, 10, Block("yellow", is_breaker=True)),
        (5, 9, Block("yellow")),
        (5, 8, Block("yellow", is_garbage=True)),
        (5, 7, Block("yellow")),
    ])
    print_board(b, "Initial Setup")

    bm = BreakerManager(b, debug=True)

    # Step 1: Apply breakers (should only clear the breaker)
    print("\n--- Step 1: Apply Breakers ---")
    marked = bm.apply_breakers()
    print(f"Marked {marked} blocks")
    print_board(b, "After apply_breakers (breaker marked)")

    # Step 2: Apply cascade (should clear marked and apply gravity)
    print("\n--- Step 2: Apply Cascade ---")
    moved = bm.cascade_step('step')
    print(f"Cascade moved {moved} blocks")
    print_board(b, "After first cascade step")

    # Step 3: Apply breakers again (should try cascade clearing)
    print("\n--- Step 3: Apply Breakers Again ---")
    marked2 = bm.apply_breakers()
    print(f"Marked {marked2} blocks")
    print_board(b, "After second apply_breakers")

    # Continue cascade until stable
    print("\n--- Continue Cascade Until Stable ---")
    cascade_step = 1
    while True:
        moved = bm.cascade_step('step')
        print(f"Cascade step {cascade_step}: moved {moved} blocks")
        if moved == 0:
            break
        print_board(b, f"After cascade step {cascade_step}")
        cascade_step += 1
        if cascade_step > 10:
            print("Too many cascade steps, breaking")
            break

    print_board(b, "Final State")

if __name__ == "__main__":
    debug_step_by_step()
