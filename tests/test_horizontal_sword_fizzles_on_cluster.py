from __future__ import annotations

from swordfighting_new.attacks.horizontal_sword import HorizontalSwordManager
from swordfighting_new.core.board import Board
from swordfighting_new.pieces.piece import Block


class _TimingStub:
    garbage_fall_interval_frames = 6


def test_horizontal_sword_fizzles_on_cluster_hit_and_places_nothing():
    board = Board()
    mgr = HorizontalSwordManager(board=board, timing=_TimingStub())

    # Spawn a 2-row sword so it can collide with a 2x2 cluster.
    mgr.spawn_horizontal_sword(rows=2, length=3, frame=0)
    assert mgr.active_swords

    sword_piece, state = mgr.active_swords[0]

    # Predict the very first movement step and the leading-edge x that will newly enter.
    old_x = int(sword_piece.x)
    x_next = old_x - 1 if state.from_right else old_x + 1
    lead_x = (x_next - (int(state.length) - 1)) if state.from_right else (x_next + (int(state.length) - 1))

    y0 = int(state.target_row)
    assert 0 <= y0 < board.HEIGHT
    assert 0 <= (y0 + 1) < board.HEIGHT

    # Build a 2x2 same-color normal-block cluster right where the sword will first contact.
    for dx in (0, 1):
        for dy in (0, 1):
            board.set_piece(int(lead_x) + dx, int(y0) + dy, Block("blue"))

    # One update tick should move the sword into the board, detect the cluster cell,
    # emit sparks, and then fizzle (no placement).
    falling, newly_locked = mgr.update(frame=0)

    assert newly_locked == []
    assert falling == []
    assert mgr.active_swords == []

    # The original cluster must remain intact.
    for dx in (0, 1):
        for dy in (0, 1):
            cell = board.get_piece(int(lead_x) + dx, int(y0) + dy)
            assert cell != board.EMPTY
            assert getattr(cell, "color", None) == "blue"
            assert not getattr(cell, "is_strike", False)

    # And no strike blocks should have been placed anywhere.
    for x in range(board.WIDTH):
        for y in range(board.HEIGHT):
            cell = board.get_piece(x, y)
            if cell == board.EMPTY:
                continue
            assert not getattr(cell, "is_strike", False)
