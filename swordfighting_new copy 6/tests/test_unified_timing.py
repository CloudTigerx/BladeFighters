#!/usr/bin/env python3
"""Test script to verify unified timing for autonomous and garbage pieces."""

from swordfighting_new.fighters.player import PlayerFighter
from swordfighting_new.mechanics.timing import TimingConfig

def test_unified_timing():
    """Test that autonomous pieces and garbage pieces use the same timing."""
    timing = TimingConfig()
    player = PlayerFighter(timing)

    print(f"Autonomous fall interval: {timing.autonomous_fall_interval_frames} frames")
    print(f"Garbage fall interval: {timing.garbage_fall_interval_frames} frames")
    print(f"Normal gravity interval: {timing.gravity_interval_frames} frames")
    print(f"Fast gravity interval: {timing.gravity_fast_interval_frames} frames")

    # Verify that autonomous and garbage use the same timing
    assert timing.autonomous_fall_interval_frames == timing.garbage_fall_interval_frames, \
        f"Autonomous ({timing.autonomous_fall_interval_frames}) != Garbage ({timing.garbage_fall_interval_frames})"

    # Verify that the GravityManager uses the correct timing
    assert player.gravity.autonomous_fall_interval == timing.autonomous_fall_interval_frames, \
        f"GravityManager interval ({player.gravity.autonomous_fall_interval}) != Config ({timing.autonomous_fall_interval_frames})"

    print("✓ Autonomous and garbage pieces now use unified timing!")
    print(f"✓ Both fall every {timing.autonomous_fall_interval_frames} frames")

if __name__ == "__main__":
    test_unified_timing()
    print("\nTiming unification test passed! 🎉")
