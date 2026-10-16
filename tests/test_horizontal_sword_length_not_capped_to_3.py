from __future__ import annotations

from swordfighting_new.attacks.horizontal_sword import HorizontalSwordManager
from swordfighting_new.core.board import Board


class _TimingStub:
    garbage_fall_interval_frames = 6


def test_horizontal_sword_length_clamps_to_board_width_not_three():
    board = Board()
    mgr = HorizontalSwordManager(board=board, timing=_TimingStub())

    # Request a full-width sword. Historically this was incorrectly capped to 3.
    mgr.spawn_horizontal_sword(rows=2, length=board.WIDTH, frame=0)

    assert mgr.active_swords
    piece, state = mgr.active_swords[0]

    assert int(state.length) == board.WIDTH
    assert int(getattr(piece, "sword_length", 0)) == board.WIDTH
