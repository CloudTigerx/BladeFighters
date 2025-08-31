#!/usr/bin/env python3
"""Debug cascade behavior with many pieces to see the actual problem."""

from swordfighting_new.core.board import Board
from swordfighting_new.mechanics.breaker import BreakerManager
from swordfighting_new.mechanics.chain_runner import BreakerChainRunner
from swordfighting_new.pieces.piece import Block

def print_board(board, title="Board"):
    """Print board state with colors."""
    print(f"\n{title}:")
    for y in range(min(15, board.HEIGHT)):  # Only show top 15 rows
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

def test_complex_cascade():
    """Test cascading with many pieces like a real game scenario."""
    b = Board()

    # Create a complex board state with multiple colors and breakers
    placements = [
        # Bottom layer - stable base
        (1, 23, Block("gray")), (2, 23, Block("gray")), (3, 23, Block("gray")),
        (4, 23, Block("gray")), (5, 23, Block("gray")), (6, 23, Block("gray")),
        (7, 23, Block("gray")), (8, 23, Block("gray")), (9, 23, Block("gray")),
        (10, 23, Block("gray")),

        # Several layers of mixed colors
        (1, 22, Block("blue")), (2, 22, Block("red")), (3, 22, Block("green")),
        (4, 22, Block("blue")), (5, 22, Block("red")), (6, 22, Block("green")),
        (7, 22, Block("blue")), (8, 22, Block("red")), (9, 22, Block("green")),
        (10, 22, Block("blue")),

        (1, 21, Block("red")), (2, 21, Block("green")), (3, 21, Block("blue")),
        (4, 21, Block("red")), (5, 21, Block("green")), (6, 21, Block("blue")),
        (7, 21, Block("red")), (8, 21, Block("green")), (9, 21, Block("blue")),
        (10, 21, Block("red")),

        # More layers with some gaps
        (2, 20, Block("yellow")), (3, 20, Block("yellow")), (4, 20, Block("purple")),
        (6, 20, Block("purple")), (7, 20, Block("yellow")), (8, 20, Block("yellow")),

        (1, 19, Block("orange")), (3, 19, Block("orange")), (5, 19, Block("cyan")),
        (7, 19, Block("cyan")), (9, 19, Block("orange")),

        # Upper layers with breakers
        (2, 18, Block("red")), (3, 18, Block("red")), (4, 18, Block("red", is_breaker=True)),
        (5, 18, Block("red")), (6, 18, Block("red")),

        (3, 17, Block("blue")), (4, 17, Block("blue")), (5, 17, Block("blue")),

        (1, 16, Block("green")), (2, 16, Block("green", is_breaker=True)),
        (3, 16, Block("green")), (7, 16, Block("green")), (8, 16, Block("green")),

        # Some isolated pieces that should fall
        (4, 14, Block("purple")), (6, 14, Block("purple")),
        (5, 12, Block("orange")), (7, 12, Block("orange")),
        (3, 10, Block("cyan")), (8, 10, Block("cyan")),

        # Top layer breakers that should trigger chains
        (2, 8, Block("blue", is_breaker=True)), (3, 8, Block("blue")),
        (6, 6, Block("yellow", is_breaker=True)), (7, 6, Block("yellow")),
    ]

    for x, y, block in placements:
        b.set_piece(x, y, block)

    print_board(b, "Initial Complex Board State")

    # Create breaker manager and chain runner
    bm = BreakerManager(b, debug=True)
    runner = BreakerChainRunner(b, bm, frame_delay=0, cascade_mode='step')

    print("\n=== Starting Complex Chain ===")
    runner.start()

    step = 0
    while runner.active:
        step += 1
        print(f"\n--- Step {step}: {runner.state} ---")
        old_state = runner.state
        runner.update()

        if runner.state != old_state or step % 5 == 0:  # Only print on state changes or every 5 steps
            print_board(b, f"After Step {step}")

        if step > 100:  # Safety break
            print("Breaking out of potential infinite loop!")
            break

    print(f"\nFinal results: {runner.results}")
    print_board(b, "Final Board State")

def test_immediate_clearing_bug():
    """Test for the specific bug where pieces clear instantly instead of cascading."""
    b = Board()

    # Create a scenario where we should see step-by-step cascading
    placements = [
        # A column with a breaker that should clear step by step
        (5, 23, Block("red", is_breaker=True)),
        (5, 22, Block("red")),
        (5, 21, Block("red")),
        (5, 20, Block("red")),
        (5, 19, Block("red")),

        # Pieces above that should fall down one by one
        (5, 16, Block("blue")),
        (5, 13, Block("green")),
        (5, 10, Block("yellow")),
        (5, 7, Block("purple")),
        (5, 4, Block("orange")),

        # Other columns to show the problem
        (3, 23, Block("blue", is_breaker=True)),
        (3, 22, Block("blue")),
        (3, 21, Block("blue")),
        (3, 18, Block("cyan")),
        (3, 15, Block("magenta")),
        (3, 12, Block("pink")),

        (7, 23, Block("green", is_breaker=True)),
        (7, 22, Block("green")),
        (7, 19, Block("white")),
        (7, 16, Block("black")),
    ]

    for x, y, block in placements:
        b.set_piece(x, y, block)

    print_board(b, "Test Setup for Instant Clearing Bug")

    # Test just the breaker application first
    bm = BreakerManager(b, debug=True)
    print("\n=== Step 1: Apply Breakers (should mark, not clear) ===")
    marked = bm.apply_breakers()
    print(f"Marked {marked} blocks for clearing")
    print_board(b, "After Breaker Application (X = marked for clearing)")

    print("\n=== Step 2: First Cascade Step (should clear marked + gravity) ===")
    moved = bm.cascade_step('step')
    print(f"Moved/cleared {moved} blocks in cascade step")
    print_board(b, "After First Cascade Step")

    print("\n=== Step 3: Continue Cascade Steps ===")
    step = 2
    while True:
        step += 1
        moved = bm.cascade_step('step')
        print(f"Step {step}: Moved {moved} blocks")
        if moved == 0:
            print("Cascade stabilized")
            break
        if step % 3 == 0:  # Show every 3rd step
            print_board(b, f"After Cascade Step {step}")
        if step > 50:
            print("Too many steps, breaking")
            break

    print_board(b, "Final State After All Cascading")

if __name__ == "__main__":
    print("=== Testing Immediate Clearing Bug ===")
    test_immediate_clearing_bug()

    print("\n" + "="*80)
    print("=== Testing Complex Cascade Scenario ===")
    test_complex_cascade()
