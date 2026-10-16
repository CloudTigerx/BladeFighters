from __future__ import annotations

from swordfighting_new.core.board import Board
from swordfighting_new.attacks.horizontal_sword import HorizontalSwordManager


class _TimingStub:
    garbage_fall_interval_frames = 6


def test_horizontal_sword_never_spawns_on_top_row():
    board = Board()
    mgr = HorizontalSwordManager(board=board, timing=_TimingStub())

    # Even with an excessive requested height, the sword should be clamped
    # to leave y=0 and y=1 free and never spawn at the top of the board.
    mgr.spawn_horizontal_sword(rows=board.HEIGHT, length=3, frame=0)

    assert mgr.active_swords, "Expected a sword to spawn"
    piece, state = mgr.active_swords[0]

    assert int(piece.y) >= 2
    assert int(state.target_row) >= 2
    assert int(state.rows) <= board.HEIGHT - 2
