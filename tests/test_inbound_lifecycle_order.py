from swordfighting_new.core.board import Board
from swordfighting_new.fighters.inbound_attack_handler import InboundAttackHandler


class _TimingStub:
    target_fps = 60
    autonomous_fall_interval_frames = 6


def test_process_lifecycle_update_registers_before_advance():
    board = Board()
    handler = InboundAttackHandler(
        board=board,
        timing=_TimingStub(),
        piece_mover=None,
        gravity_manager=None,
    )

    calls: list[str] = []

    class _LifecycleSpy:
        def register_new_locked(self, blocks):
            calls.append("register")

        def advance(self):
            calls.append("advance")

    handler.lifecycle = _LifecycleSpy()
    handler._new_attack_blocks = [object()]

    handler.process_lifecycle_update()

    assert calls == ["register", "advance"]
