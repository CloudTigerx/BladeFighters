#!/usr/bin/env python3
"""Debug cascade behavior to see what's happening with instant clearing."""

from swordfighting_new.core.board import Board
from swordfighting_new.mechanics.breaker import BreakerManager
from swordfighting_new.mechanics.chain_runner import BreakerChainRunner
from swordfighting_new.pieces.piece import Block

def print_board(board, title="Board"):
    """Print board state with colors."""
    print(f"\n{title}:")
    for y in range(board.HEIGHT):
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

def test_simple_cascade():
    """Test a simple cascade scenario."""
    b = Board()

    # Place pieces that should cascade properly
    placements = [
        (5, 12, Block("red", is_breaker=True)),  # Bottom breaker
        (5, 11, Block("red")),                   # Connected red block
        (5, 8, Block("blue")),                   # Blue block that should fall
        (5, 6, Block("green")),                  # Green block that should fall
    ]

    for x, y, block in placements:
        b.set_piece(x, y, block)

    print_board(b, "Initial State")

    # Create breaker manager and chain runner
    bm = BreakerManager(b, debug=True)
    runner = BreakerChainRunner(b, bm, frame_delay=0, cascade_mode='step')

    print("\n=== Starting Chain ===")
    runner.start()

    step = 0
    while runner.active:
        step += 1
        print(f"\n--- Step {step}: {runner.state} ---")
        runner.update()
        print_board(b, f"After Step {step}")

        if step > 20:  # Safety break
            print("Breaking out of infinite loop!")
            break

    print(f"\nFinal results: {runner.results}")

def test_breaker_only():
    """Test just the breaker marking behavior."""
    b = Board()

    # Simple breaker setup
    placements = [
        (5, 12, Block("red", is_breaker=True)),
        (5, 11, Block("red")),
    ]

    for x, y, block in placements:
        b.set_piece(x, y, block)

    print_board(b, "Before breaker apply")

    bm = BreakerManager(b, debug=True)
    marked = bm.apply_breakers()

    print(f"Marked {marked} blocks")
    print_board(b, "After breaker apply (should show X for marked)")

    # Now apply cascade step
    moved = bm.cascade_step('step')
    print(f"Moved {moved} blocks in cascade step")
    print_board(b, "After cascade step (marked should be cleared)")

if __name__ == "__main__":
    print("=== Testing Breaker Only ===")
    test_breaker_only()

    print("\n" + "="*50)
    print("=== Testing Simple Cascade ===")
    test_simple_cascade()
