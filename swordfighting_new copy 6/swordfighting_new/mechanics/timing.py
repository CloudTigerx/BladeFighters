"""timing.py - Centralized gameplay timing & speed configuration.

This abstracts frame and millisecond timing so we can later port legacy
behaviors (micro-fall interpolation, animation pacing, gravity level curves)
from the decompiled Java sources without scattering magic numbers.

Design goals:
 - Single authoritative place for default speeds
 - Easy runtime override (env vars or external dict)
 - Future: per-level gravity progression & difficulty scaling
"""

from __future__ import annotations

from dataclasses import dataclass, field
import os
from typing import Callable


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, default))
    except Exception:
        return default


@dataclass
class TimingConfig:
    # Frame timing
    target_fps: int = _env_int("BF_FPS", 60)

    # Gravity (frames between natural soft drops)
    gravity_interval_frames: int = _env_int("BF_GRAVITY_INTERVAL", 15)  # Increased from 30 to 15 for faster fall
    gravity_fast_interval_frames: int = _env_int("BF_GRAVITY_FAST_INTERVAL", 2)  # Increased from 4 to 2 for faster soft drop
    # Garbage block fall interval - now matches autonomous piece speed for consistency
    garbage_fall_interval_frames: int = _env_int("BF_GARBAGE_FALL_INTERVAL", 3)  # Unified with autonomous piece timing
    # Autonomous piece fall interval (split pieces from uneven columns)
    autonomous_fall_interval_frames: int = _env_int("BF_AUTONOMOUS_FALL_INTERVAL", 3)  # Slightly faster than before

    # Chain / breaker pacing (frames to pause between breaker pass & cascade visual step)
    chain_frame_delay: int = _env_int("BF_CHAIN_FRAME_DELAY", 20)  # Increased from 0 to 20 for visual feedback

    # Optional: hard drop lock delay (frames) (unused yet)
    lock_delay_frames: int = _env_int("BF_LOCK_DELAY", 0)

    # Future micro-fall (ms per sub-step) - placeholder for smooth fall interpolation
    micro_fall_ms: int = _env_int("BF_MICRO_FALL_MS", 0)  # 0 = disabled

    # --- Puzzle-module legacy speed bridge (microsecond-style values) ---
    # These mirror the old puzzle_module numbers (e.g. 640000 normal, 2400 fast).
    # Enable via env BF_USE_PUZZLE_SPEEDS=1 to derive per-cell frame intervals from them.
    puzzle_normal_us: int = _env_int("BF_PUZZLE_NORMAL_US", 640000)
    puzzle_fast_us: int = _env_int("BF_PUZZLE_FAST_US", 2400)
    use_puzzle_speeds: bool = bool(_env_int("BF_USE_PUZZLE_SPEEDS", 0))

    # Level scaling hook (returns interval frames for given level)
    gravity_curve: Callable[[int], int] = field(default=lambda lvl: max(4, 30 - (lvl // 3) * 2))

    def interval_for_level(self, level: int, fast: bool) -> int:
        # Optional legacy puzzle speed mapping
        if self.use_puzzle_speeds:
            # Convert microsecond fall duration to frame count at current target FPS.
            us = self.puzzle_fast_us if fast else self.puzzle_normal_us
            # Guard against zero / negative
            us = max(1, us)
            ms = us / 1000.0
            frame_time_ms = 1000.0 / max(1, self.target_fps)
            frames = int(round(ms / frame_time_ms))
            # Ensure at least 1 frame between drops (fast can legitimately be 1)
            return max(1, frames)
        # Default frame-based system
        if fast:
            return self.gravity_fast_interval_frames
        else:
            return self.gravity_interval_frames


DEFAULT_TIMING = TimingConfig()


def load_timing(overrides: dict | None = None) -> TimingConfig:
    """Return a TimingConfig applying optional overrides (dict of field->value)."""
    if not overrides:
        return DEFAULT_TIMING
    cfg = TimingConfig(**{**DEFAULT_TIMING.__dict__, **overrides})
    return cfg
