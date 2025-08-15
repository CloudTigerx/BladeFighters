from utils.clock import FakeClock


class SimpleAnim:
    def __init__(self, frame_ms: int, frames: int, clock):
        self.frame_ms = frame_ms
        self.frames = frames
        self.clock = clock
        self.current_frame = 0
        self.last_advance = self.clock.now_ms()

    def update(self):
        now = self.clock.now_ms()
        elapsed = now - self.last_advance
        while elapsed >= self.frame_ms and self.current_frame < self.frames - 1:
            self.current_frame += 1
            self.last_advance += self.frame_ms
            elapsed -= self.frame_ms


def test_anim_advances_deterministically():
    clock = FakeClock(0)
    anim = SimpleAnim(frame_ms=100, frames=5, clock=clock)

    # No progress at t=0
    anim.update()
    assert anim.current_frame == 0

    # Advance 100ms -> frame 1
    clock.advance(100)
    anim.update()
    assert anim.current_frame == 1

    # Advance 250ms -> frames 2 and 3 (200ms), remainder 50ms stays
    clock.advance(250)
    anim.update()
    assert anim.current_frame == 3

    # Advance to finish
    clock.advance(1000)
    anim.update()
    assert anim.current_frame == 4

