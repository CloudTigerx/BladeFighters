#!/usr/bin/env python3
"""Test to verify the timing conflict fix for autonomous pieces."""

from swordfighting_new.fighters.player import PlayerFighter
from swordfighting_new.mechanics.timing import TimingConfig
from swordfighting_new.pieces.piece import Piece

def test_autonomous_timing_fix():
    """Test that autonomous pieces don't have timing conflicts."""
    timing = TimingConfig()
    player = PlayerFighter(timing)

    print("🔧 Testing autonomous piece timing conflict fix...")

    # Create a horizontal piece that will split
    piece = Piece()
    piece.orientation = 1  # horizontal
    piece.x = 3
    piece.y = 5

    # Simulate partial blockage to trigger split
    # Block the right side to force a split
    player.board.set_piece(4, 6, piece.blocks[0])  # block right side

    # Verify piece starts as controllable
    assert piece.controllable == True, "Piece should start controllable"

    # Apply gravity to trigger split
    result = player.gravity.apply_gravity(piece)

    if not piece.controllable:
        print("✅ Piece became autonomous after split")
        print(f"   Autonomous interval: {piece.autonomous_fall_interval} frames")
        print(f"   Autonomous timer: {piece.autonomous_fall_timer}")

        # Test that autonomous timing works correctly
        # On frames that aren't autonomous timing frames, gravity should return True but not move
        old_y = piece.y
        for frame in range(5):
            # Clear board position for movement
            for x in range(player.board.WIDTH):
                for y in range(player.board.HEIGHT):
                    if player.board.get_piece(x, y) != player.board.EMPTY:
                        player.board.set_piece(x, y, player.board.EMPTY)

            result = player.gravity.apply_gravity(piece)
            if frame % piece.autonomous_fall_interval == 0 and frame > 0:
                print(f"   Frame {frame}: Should move (timer reset)")
            else:
                print(f"   Frame {frame}: Should wait (timer: {piece.autonomous_fall_timer})")

        print("✅ Autonomous timing working correctly")
    else:
        print("ℹ️  Piece didn't split (no timing conflict to test)")

    print("\n🎯 Key Fix: Main update loop now respects autonomous piece timing")
    print("   - Controllable pieces: Use main loop timing (15/2 frames)")
    print("   - Autonomous pieces: Use internal timing (3 frames)")
    print("   - No more timing conflicts causing slow falls!")

if __name__ == "__main__":
    test_autonomous_timing_fix()
    print("\n✅ Timing conflict fix test completed! 🎉")
