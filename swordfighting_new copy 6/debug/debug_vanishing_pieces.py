#!/usr/bin/env python3
"""Test pieces vanishing when they land - the real issue."""

from swordfighting_new.core.board import Board
from swordfighting_new.mechanics.breaker import BreakerManager
from swordfighting_new.mechanics.chain_runner import BreakerChainRunner
from swordfighting_new.pieces.piece import Block

def print_board(board, title="Board"):
    """Print board state with colors."""
    print(f"\n{title}:")
    for y in range(min(25, board.HEIGHT)):
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

def test_pieces_vanishing_on_landing():
    """Test the issue where pieces vanish when they land."""
    b = Board()

    # Simulate a realistic game scenario where pieces have been falling
    # and some clearing has happened, leaving empty spaces
    placements = [
        # Bottom layer - some stable pieces
        (3, 23, Block("gray")), (4, 23, Block("gray")), (5, 23, Block("gray")),
        (6, 23, Block("gray")), (7, 23, Block("gray")), (8, 23, Block("gray")),

        # Some pieces that landed after clearing
        (3, 22, Block("red")), (4, 22, Block("blue")), (5, 22, Block("green")),

        # A breaker that triggered and cleared some stuff
        (6, 22, Block("red", is_breaker=True)),
        (7, 22, Block("red")),  # This should connect to breaker

        # Some pieces that just landed and shouldn't disappear
        (8, 22, Block("yellow")),
        (9, 22, Block("purple")),

        # Higher up pieces that fell down
        (4, 21, Block("orange")),
        (5, 21, Block("cyan")),
    ]

    for x, y, block in placements:
        b.set_piece(x, y, block)

    print_board(b, "Initial state - pieces have landed")

    # Now simulate what happens when the breaker system runs
    bm = BreakerManager(b, debug=True)

    print("\n=== First breaker pass ===")
    marked1 = bm.apply_breakers()
    print(f"Marked {marked1} blocks")
    print_board(b, "After first breaker pass")

    # Apply cascade step (this is where pieces might vanish)
    print("\n=== First cascade step ===")
    moved1 = bm.cascade_step('step')
    print(f"Moved/cleared {moved1} blocks")
    print_board(b, "After first cascade step")

    # Continue with more breaker passes to see the issue
    print("\n=== Second breaker pass ===")
    marked2 = bm.apply_breakers()
    print(f"Marked {marked2} blocks")
    print_board(b, "After second breaker pass")

    if marked2 > 0:
        print("\n=== Second cascade step ===")
        moved2 = bm.cascade_step('step')
        print(f"Moved/cleared {moved2} blocks")
        print_board(b, "After second cascade step")

    # Check what pieces are left
    remaining = 0
    for x in range(b.WIDTH):
        for y in range(b.HEIGHT):
            if b.get_piece(x, y) != b.EMPTY:
                remaining += 1

    print(f"\nRemaining pieces: {remaining}")

def test_fresh_pieces_landing():
    """Test what happens when fresh pieces land on a board with empty spaces."""
    b = Board()

    # Create a board that has some empty spaces from previous clearing
    placements = [
        # Bottom stable layer
        (2, 23, Block("gray")), (3, 23, Block("gray")), (4, 23, Block("gray")),
        (7, 23, Block("gray")), (8, 23, Block("gray")), (9, 23, Block("gray")),

        # Empty spaces at (5,23) and (6,23) from previous clearing

        # Some pieces that are still on the board
        (2, 22, Block("blue")), (3, 22, Block("green")),
        (8, 22, Block("purple")), (9, 22, Block("orange")),

        # Fresh pieces that just landed in/near the empty spaces
        (5, 22, Block("red")),    # This shouldn't disappear!
        (6, 22, Block("yellow")), # This shouldn't disappear!
        (4, 21, Block("cyan")),   # This shouldn't disappear!
    ]

    for x, y, block in placements:
        b.set_piece(x, y, block)

    print_board(b, "Fresh pieces have just landed")

    # Run breaker system - the fresh pieces should NOT be cleared
    bm = BreakerManager(b, debug=True)

    print("\n=== Running breaker check on fresh pieces ===")
    marked = bm.apply_breakers()
    print(f"Marked {marked} blocks (should be 0 - no breakers)")
    print_board(b, "After breaker check - fresh pieces should still be there")

    if marked > 0:
        print("\n⚠️ ERROR: Fresh pieces are being marked for clearing!")

    # Count pieces before and after
    before_count = sum(1 for x in range(b.WIDTH) for y in range(b.HEIGHT)
                      if b.get_piece(x, y) != b.EMPTY)

    print(f"Pieces on board: {before_count}")

if __name__ == "__main__":
    print("=== Testing Pieces Vanishing on Landing ===")
    test_pieces_vanishing_on_landing()

    print("\n" + "="*80)
    print("=== Testing Fresh Pieces Landing ===")
    test_fresh_pieces_landing()
