from __future__ import annotations

from swordfighting_new.core.board import Board
from swordfighting_new.fighters.movement_controller import MovementController
from swordfighting_new.mechanics.gravity import GravityManager
from swordfighting_new.mechanics.movement import PieceMover


class _TimingStub:
    # MovementController expects these
    lock_delay_frames = 0

    # GravityManager expects these
    autonomous_fall_interval_frames = 6
    split_fall_interval_frames = 6

    def interval_for_level(self, level: int, fast: bool) -> int:
        return 60


def test_defeated_when_game_over_column_is_full_even_if_spawn_clear(monkeypatch):
    # Pick a game-over column that is NOT the spawn column.
    # Env var is 1-based column index.
    monkeypatch.setenv("BF_GAME_OVER_COLUMN", "1")

    board = Board()
    mover = PieceMover(board)
    gravity = GravityManager(board=board, mover=mover, timing=_TimingStub())

    mc = MovementController(board=board, piece_mover=mover, gravity_manager=gravity, timing=_TimingStub(), spawn_x=3)

    gox = int(mc.game_over_x)
    assert gox == 0

    # Fill the entire monitored column.
    for y in range(board.HEIGHT):
        board.set_piece(gox, y, 99)

    assert mc.defeated is False

    _should_lock, _grav = mc.update(intents={}, frame=1)

    assert mc.defeated is True
