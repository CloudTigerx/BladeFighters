#!/usr/bin/env python3

import sys
sys.path.insert(0, '/Users/justinearp/Desktop/swordfighting_new copy 5')

from swordfighting_new.core.board import Board
from swordfighting_new.pieces.piece import Block
from swordfighting_new.mechanics.breaker import BreakerManager

def _place(board, pieces):
    for x, y, piece in pieces:
        board.set_piece(x, y, piece)

def debug_test():
    print("=== Debug Progressive Clearing ===")

    # Set up test case
    b = Board()
    _place(b, [
        (5, 10, Block("red", is_breaker=True)),
        (5, 9, Block("red")),
    ])

    print("Initial board:")
    for y in range(15, 5, -1):  # Print top to bottom
        row = []
        for x in range(4, 8):  # Just around our pieces
            piece = b.get_piece(x, y)
            if piece == b.EMPTY:
                row.append(".")
            elif hasattr(piece, 'is_breaker') and piece.is_breaker:
                row.append(f"B{piece.color[0]}")
            else:
                row.append(piece.color[0])
        print(f"y={y}: {' '.join(row)}")

    # Test step by step what apply_breaker_chain does
    bm = BreakerManager(b, debug=True)

    print("\n=== Step 1: apply_breakers() ===")
    cleared1 = bm.apply_breakers()
    print(f"Cleared: {cleared1}")
    print(f"Recently cleared spaces: {bm.recently_cleared_spaces}")

    print("Board after step 1:")
    for y in range(15, 5, -1):
        row = []
        for x in range(4, 8):
            piece = b.get_piece(x, y)
            if piece == b.EMPTY:
                row.append(".")
            elif hasattr(piece, 'is_breaker') and piece.is_breaker:
                row.append(f"B{piece.color[0]}")
            else:
                row.append(piece.color[0])
        print(f"y={y}: {' '.join(row)}")

    print("\n=== Step 2: apply_full() (gravity) ===")
    bm.cascade_manager.apply_full()

    print("Board after gravity:")
    for y in range(15, 5, -1):
        row = []
        for x in range(4, 8):
            piece = b.get_piece(x, y)
            if piece == b.EMPTY:
                row.append(".")
            elif hasattr(piece, 'is_breaker') and piece.is_breaker:
                row.append(f"B{piece.color[0]}")
            else:
                row.append(piece.color[0])
        print(f"y={y}: {' '.join(row)}")

    print("\n=== Step 3: apply_breakers() again ===")
    cleared2 = bm.apply_breakers()
    print(f"Cleared: {cleared2}")
    print(f"Recently cleared spaces: {bm.recently_cleared_spaces}")

if __name__ == "__main__":
    debug_test()
