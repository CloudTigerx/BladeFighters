#!/usr/bin/env python3

import sys
sys.path.insert(0, '/Users/justinearp/Desktop/swordfighting_new copy 5')

from swordfighting_new.core.board import Board
from swordfighting_new.pieces.piece import Block
from swordfighting_new.mechanics.breaker import BreakerManager

def _place(board, pieces):
    for x, y, piece in pieces:
        board.set_piece(x, y, piece)

def test_single_instance():
    """Test with single instance like test_chain_two_passes does"""
    print("=== Test with single instance ===")

    b = Board()
    _place(b, [
        (5, 10, Block("red", is_breaker=True)),
        (5, 9, Block("red")),
    ])

    bm = BreakerManager(b, debug=True)
    chains, total, per_pass = bm.apply_breaker_chain()
    print(f"Chains: {chains}, Total: {total}, Per-pass: {per_pass}")

    # This should work if progressive clearing is designed for chain calls
    assert total == 2, f"Expected 2, got {total}"
    assert chains == 2, f"Expected 2 chains, got {chains}"
    print("✓ Single instance test passed!")

if __name__ == "__main__":
    test_single_instance()
