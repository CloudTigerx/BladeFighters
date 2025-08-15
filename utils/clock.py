import time
from typing import Optional


class Clock:
    """
    Abstract time source providing a monotonic current time in milliseconds.
    All non-reactor modules should depend on this interface for time.
    """

    def now_ms(self) -> int:
        raise NotImplementedError


class SystemClock(Clock):
    """Clock based on time.perf_counter(), converted to integer milliseconds."""

    def __init__(self):
        self._start = time.perf_counter()

    def now_ms(self) -> int:
        return int((time.perf_counter() - self._start) * 1000.0)


class PygameClock(Clock):
    """Clock that wraps pygame.time.get_ticks() when pygame is available."""

    def now_ms(self) -> int:
        try:
            import pygame  # Local import to avoid hard dependency for tests
            return int(pygame.time.get_ticks())
        except Exception:
            # Fallback to SystemClock semantics if pygame isn't initialized
            return int(time.perf_counter() * 1000.0)


class FakeClock(Clock):
    """
    Deterministic test clock. Advance time manually via advance(ms).
    """

    def __init__(self, start_ms: int = 0):
        self._now_ms = int(start_ms)

    def now_ms(self) -> int:
        return int(self._now_ms)

    def advance(self, ms: int) -> None:
        self._now_ms += int(ms)

