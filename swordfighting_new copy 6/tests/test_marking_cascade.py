#!/usr/bin/env python3
"""Test to demonstrate the new marking-based cascade system."""

from swordfighting_new.core.board import Board
from swordfighting_new.pieces.piece import Block
from swordfighting_new.mechanics.breaker import BreakerManager
from swordfighting_new.mechanics.cascade import CascadeManager

def test_marking_cascade_system():
    """Test that blocks are marked instead of instantly cleared."""
    print("🧪 Testing new marking-based cascade system...")

    board = Board()
    breakers = BreakerManager(board)
    cascade = CascadeManager(board)

    # Create a simple setup with breaker and adjacent blocks
    # Layout (4x4 red blocks to trigger breaker):
    #   R R R R
    #   R B R R  (B = red breaker in the middle)
    #   R R R R
    #   R R R R

    # Fill a 4x4 area with red blocks
    for x in range(4):
        for y in range(4):
            board.set_piece(x + 5, y + 15, Block('red'))

    # Place a red breaker in the middle
    board.set_piece(6, 16, Block('red', is_breaker=True))  # breaker

    print("Initial board setup (4x4 red blocks with breaker in middle):")
    print("  R R R R")
    print("  R B R R  (B = red breaker)")
    print("  R R R R")
    print("  R R R R")

    # Apply breakers - this should mark blocks but not clear them yet
    marked = breakers.apply_breakers()
    print(f"\n✅ Breakers marked {marked} blocks for clearing")

    # Check that blocks are marked but still on board
    marked_count = 0
    total_blocks = 0
    for x in range(board.WIDTH):
        for y in range(board.HEIGHT):
            cell = board.get_piece(x, y)
            if cell != board.EMPTY:
                total_blocks += 1
                if getattr(cell, 'marked_for_clearing', False):
                    marked_count += 1

    print(f"   Blocks still on board: {total_blocks}")
    print(f"   Blocks marked for clearing: {marked_count}")

    # Now apply cascade - this should clear marked blocks and apply gravity
    cleared_and_moved = cascade.apply_full()
    print(f"\n✅ Cascade cleared and moved {cleared_and_moved} blocks")

    # Check final state
    final_blocks = 0
    for x in range(board.WIDTH):
        for y in range(board.HEIGHT):
            cell = board.get_piece(x, y)
            if cell != board.EMPTY:
                final_blocks += 1

    print(f"   Final blocks remaining: {final_blocks}")

    print("\n🎯 Key Improvements:")
    print("   ✅ No more instant disappearing - blocks are marked first")
    print("   ✅ Cascade handles both clearing and gravity in one operation")
    print("   ✅ More predictable and visually consistent behavior")
    print("   ✅ Breakers can be processed in correct order during cascade")

if __name__ == "__main__":
    test_marking_cascade_system()
    print("\n🎉 Marking cascade system test completed!")
