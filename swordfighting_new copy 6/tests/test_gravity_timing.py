#!/usr/bin/env python3
"""Test script to verify gravity timing consistency."""

from swordfighting_new.fighters.player import PlayerFighter
from swordfighting_new.mechanics.timing import TimingConfig
from swordfighting_new.pieces.piece import Piece

def test_gravity_timing_consistency():
    """Test that gravity timing is consistent for normal and split pieces."""
    timing = TimingConfig()
    player = PlayerFighter(timing)

    # Test normal piece gravity timing
    normal_interval = timing.interval_for_level(level=1, fast=False)
    fast_interval = timing.interval_for_level(level=1, fast=True)

    print(f"Normal interval: {normal_interval} frames")
    print(f"Fast interval: {fast_interval} frames")
    print(f"Gravity interval setting: {timing.gravity_interval_frames} frames")
    print(f"Gravity fast interval setting: {timing.gravity_fast_interval_frames} frames")

    # Verify that the intervals match the configured values
    assert normal_interval == timing.gravity_interval_frames, f"Normal interval {normal_interval} != configured {timing.gravity_interval_frames}"
    assert fast_interval == timing.gravity_fast_interval_frames, f"Fast interval {fast_interval} != configured {timing.gravity_fast_interval_frames}"

    print("✓ Gravity timing is consistent!")

def test_autonomous_piece_timing():
    """Test that autonomous pieces (from splits) have their own timing."""
    timing = TimingConfig()
    player = PlayerFighter(timing)

    # Create a horizontal piece
    piece = Piece()
    piece.orientation = 1  # horizontal
    piece.x = 3
    piece.y = 5

    # Simulate a split by making one side unable to fall
    # Place a block underneath the right side
    player.board.set_piece(4, 6, player.board.EMPTY)  # left side can fall
    player.board.set_piece(5, 6, piece.blocks[0])      # right side blocked

    # Test that autonomous pieces have timing attributes
    test_piece = Piece.single_block('red')
    test_piece.controllable = False

    assert hasattr(test_piece, 'autonomous_fall_timer'), "Autonomous piece should have fall timer"
    assert hasattr(test_piece, 'autonomous_fall_interval'), "Autonomous piece should have fall interval"

    print("✓ Autonomous piece timing attributes are present!")

if __name__ == "__main__":
    test_gravity_timing_consistency()
    test_autonomous_piece_timing()
    print("\nAll gravity timing tests passed! 🎉")
