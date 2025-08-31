#!/usr/bin/env python3
"""Test the fixed progressive cascade behavior."""

from swordfighting_new.core.board import Board
from swordfighting_new.mechanics.breaker import BreakerManager
from swordfighting_new.mechanics.chain_runner import BreakerChainRunner
from swordfighting_new.pieces.piece import Block

def print_board(board, title="Board"):
    """Print board state with colors."""
    print(f"\n{title}:")
    for y in range(min(20, board.HEIGHT)):  # Only show top 20 rows
        row = ""
        for x in range(board.WIDTH):
            cell = board.get_piece(x, y)
            if cell == board.EMPTY:
                row += "."
            elif hasattr(cell, 'marked_for_clearing') and cell.marked_for_clearing:
                row += "X"  # marked for clearing
            elif hasattr(cell, 'is_breaker') and cell.is_breaker:
                row += cell.color[0].upper()  # Breaker in uppercase
            else:
                row += cell.color[0]  # normal block in lowercase
        print(f"{y:2d}: {row}")

def test_progressive_cascade():
    """Test that shows proper progressive cascading."""
    b = Board()

    # Create a simple scenario that should cascade step by step
    placements = [
        # A vertical chain of red blocks with a breaker at the bottom
        (5, 20, Block("red", is_breaker=True)),
        (5, 19, Block("red")),
        (5, 18, Block("red")),
        (5, 17, Block("red")),
        (5, 16, Block("red")),

        # Some other blocks that should fall
        (5, 14, Block("blue")),
        (5, 12, Block("green")),
        (5, 10, Block("yellow")),
    ]

    for x, y, block in placements:
        b.set_piece(x, y, block)

    print_board(b, "Initial Setup - Vertical Chain Test")

    # Test the progressive clearing manually step by step
    bm = BreakerManager(b, debug=True)

    print("\n=== Manual Step-by-Step Clearing ===")

    step = 0
    while True:
        step += 1
        print(f"\n--- Breaker Pass {step} ---")

        # Apply breakers
        marked = bm.apply_breakers()
        print(f"Marked {marked} blocks for clearing")

        if marked == 0:
            print("No more blocks to clear - chain complete!")
            break

        print_board(b, f"After Breaker Pass {step} (X = marked)")

        # Apply cascade until stable
        cascade_step = 0
        while True:
            cascade_step += 1
            moved = bm.cascade_step('step')
            print(f"Cascade step {cascade_step}: moved {moved} blocks")

            if moved == 0:
                print("Cascade stabilized")
                break

            if cascade_step <= 3:  # Only show first few cascade steps
                print_board(b, f"After Cascade Step {cascade_step}")

            if cascade_step > 50:  # Safety
                print("Cascade taking too long, breaking")
                break

        print_board(b, f"After Full Cascade {step}")

        if step > 10:  # Safety
            print("Too many breaker passes, breaking")
            break

    print_board(b, "Final Result")

def test_horizontal_chain():
    """Test horizontal chain clearing."""
    b = Board()

    # Create a horizontal chain
    placements = [
        # Horizontal red chain
        (2, 20, Block("red", is_breaker=True)),
        (3, 20, Block("red")),
        (4, 20, Block("red")),
        (5, 20, Block("red")),
        (6, 20, Block("red")),

        # Some blocks above that should fall
        (3, 18, Block("blue")),
        (4, 16, Block("green")),
        (5, 14, Block("yellow")),
    ]

    for x, y, block in placements:
        b.set_piece(x, y, block)

    print_board(b, "Initial Setup - Horizontal Chain Test")

    # Use the chain runner to see the full behavior
    bm = BreakerManager(b, debug=True)
    runner = BreakerChainRunner(b, bm, frame_delay=0, cascade_mode='step')

    print("\n=== Chain Runner Test ===")
    runner.start()

    step = 0
    while runner.active:
        step += 1
        print(f"\n--- Step {step}: {runner.state} ---")
        runner.update()

        if step % 5 == 0 or runner.state == 'breaker_pass':  # Show key steps
            print_board(b, f"After Step {step}")

        if step > 50:  # Safety
            print("Chain taking too long, breaking")
            break

    print(f"\nChain Results: {runner.results}")
    print_board(b, "Final Chain Result")

if __name__ == "__main__":
    print("=== Testing Progressive Cascade ===")
    test_progressive_cascade()

    print("\n" + "="*80)
    print("=== Testing Horizontal Chain ===")
    test_horizontal_chain()
