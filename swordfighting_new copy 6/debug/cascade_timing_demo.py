#!/usr/bin/env python3
"""Demo of the new cascade timing for visual feedback."""

from swordfighting_new.mechanics.timing import TimingConfig

def show_cascade_timing():
    """Show the new cascade timing settings."""
    timing = TimingConfig()

    print("🎬 New Cascade Timing for Visual Feedback")
    print("=" * 45)

    fps = timing.target_fps
    chain_delay_ms = (timing.chain_frame_delay / fps) * 1000
    minimum_delay_ms = (15 / fps) * 1000  # minimum enforced delay

    print(f"🎮 Target FPS: {fps}")
    print(f"⏱️  Chain Frame Delay: {timing.chain_frame_delay} frames ({chain_delay_ms:.0f}ms)")
    print(f"⏱️  Minimum Delay: 15 frames ({minimum_delay_ms:.0f}ms)")
    print(f"📐 Cascade Mode: 'step' (one row at a time)")

    print(f"\n🎭 Visual Flow:")
    print(f"   1. Breaker Pass (marks blocks)")
    print(f"   2. Wait {max(15, timing.chain_frame_delay)} frames ({max(minimum_delay_ms, chain_delay_ms):.0f}ms)")
    print(f"   3. Cascade Step (clear marked + move blocks down 1 row)")
    print(f"   4. Wait {max(15, timing.chain_frame_delay)} frames ({max(minimum_delay_ms, chain_delay_ms):.0f}ms)")
    print(f"   5. Repeat cascade steps until stable")
    print(f"   6. Next breaker pass (if any new patterns)")

    print(f"\n⚡ Timing Comparison:")
    print(f"   Old timing: 0-8 frames (~0-133ms) - too fast to see")
    print(f"   New timing: {max(15, timing.chain_frame_delay)} frames (~{max(minimum_delay_ms, chain_delay_ms):.0f}ms) - visible steps")

    print(f"\n🔧 Environment Variables for Tuning:")
    print(f"   BF_CHAIN_FRAME_DELAY={timing.chain_frame_delay}  # Base delay between steps")
    print(f"   BF_CASCADE_MODE=step                               # 'step' or 'fast'")

    print(f"\n🎯 Result: You should now see blocks:")
    print(f"   ✅ Get marked for clearing")
    print(f"   ✅ Clear during cascade step")
    print(f"   ✅ Fall one row at a time with pauses")
    print(f"   ✅ Stabilize before next breaker pass")

if __name__ == "__main__":
    show_cascade_timing()
