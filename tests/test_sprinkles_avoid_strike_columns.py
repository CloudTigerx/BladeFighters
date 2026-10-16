import types

from swordfighting_new.core.board import Board
from swordfighting_new.fighters.inbound_attack_handler import InboundAttackHandler


class _DummyGravity:
    def lock_piece(self, piece):
        # Not needed for this test.
        return


def test_deferred_sprinkles_avoid_last_strike_columns_when_room():
    board = Board()
    timing = types.SimpleNamespace(
        target_fps=60,
        autonomous_fall_interval_frames=6,
        garbage_fall_interval_frames=6,
    )

    handler = InboundAttackHandler(
        board=board,
        timing=timing,
        piece_mover=None,
        gravity_manager=_DummyGravity(),
        attack_delay_frames=0,
        bulk_delivery=True,
    )

    # Simulate: strikes were just placed in center columns, and we have deferred sprinkles.
    handler.inbound_delay = 0
    handler.pending_in_sprinkle = 2
    handler._last_strike_place_frame = 0
    handler._sprinkle_deferral_frames = 0
    handler._last_strike_cols = {2, 3}
    handler.frame = 10

    handler.update_inbound_garbage()

    # Sprinkles should spawn as fallers above-board.
    assert len(handler.garbage_fallers) == 2

    cols = {int(getattr(p, 'x')) for p in handler.garbage_fallers}
    assert cols.isdisjoint({2, 3})
