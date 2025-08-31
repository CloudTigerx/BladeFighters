#!/usr/bin/env python3
"""Test to reproduce the issue with instant clearing and wrong order."""

from swordfighting_new.core.board import Board
from swordfighting_new.mechanics.breaker import BreakerManager
from swordfighting_new.mechanics.combo import ComboManager
from swordfighting_new.pieces.piece import Block

def test_combo_vs_breaker_priority():
    """Test if combos are being cleared before breakers get a chance."""
    b = Board()

    # Create a scenario with both a 2x2 combo AND a breaker pattern
    placements = [
        # 2x2 red cluster (should NOT clear in current design)
        (4, 22, Block("red")),
        (5, 22, Block("red")),
        (4, 23, Block("red")),
        (5, 23, Block("red")),

        # Red breaker with connected piece (should clear)
        (6, 22, Block("red", is_breaker=True)),
        (6, 21, Block("red")),

        # Some other blocks
        (7, 23, Block("blue")),
        (3, 20, Block("green")),
    ]

    for x, y, block in placements:
        b.set_piece(x, y, block)

    print_board(b, "Initial setup")

    # Test combo system
    combo = ComboManager(b)
    clusters = combo.find_clusters()
    print(f"Found {len(clusters)} clusters")
    for i, cluster in enumerate(clusters):
        print(f"  Cluster {i}: {cluster}")

    # Test if combo.process_clears() does anything (it shouldn't in current design)
    combo_count, cleared = combo.process_clears()
    print(f"Combo process_clears returned: count={combo_count}, cleared={cleared}")

    print_board(b, "After combo process_clears")

    # Now test breaker system
    bm = BreakerManager(b, debug=True)
    marked = bm.apply_breakers()
    print(f"Breakers marked {marked} blocks")

    print_board(b, "After breaker apply (should see X for marked)")

    # Apply cascade
    moved = bm.cascade_step('step')
    print(f"Cascade cleared {moved} blocks")

    print_board(b, "After cascade step")

def print_board(board, title="Board"):
    """Print board state with colors."""
    print(f"\n{title}:")
    for y in range(min(15, board.HEIGHT)):  # Only show relevant rows
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

def test_instant_clearing_issue():
    """Test if blocks are being cleared instantly instead of through proper cascade."""
    b = Board()

    # Set up a complex scenario with multiple colors and breakers
    placements = [
        # Bottom breaker cluster
        (5, 23, Block("red", is_breaker=True)),
        (5, 22, Block("red")),
        (4, 23, Block("red")),
        (6, 23, Block("red")),

        # Blocks that should fall after clearing
        (5, 18, Block("blue")),
        (5, 15, Block("green")),
        (5, 12, Block("yellow")),

        # Another breaker higher up that should trigger in second pass
        (5, 10, Block("blue", is_breaker=True)),
        (5, 9, Block("blue")),
    ]

    for x, y, block in placements:
        b.set_piece(x, y, block)

    print_board(b, "Complex scenario setup")

    # Test full chain
    bm = BreakerManager(b, debug=True)
    chains, total, per_pass = bm.apply_breaker_chain()

    print(f"Chain completed: {chains} passes, {total} total cleared, per_pass={per_pass}")
    print_board(b, "After full chain")

if __name__ == "__main__":
    print("=== Testing Combo vs Breaker Priority ===")
    test_combo_vs_breaker_priority()

    print("\n" + "="*60)
    print("=== Testing Instant Clearing Issue ===")
    test_instant_clearing_issue()
