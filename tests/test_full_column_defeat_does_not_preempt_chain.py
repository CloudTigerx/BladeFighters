from __future__ import annotations

from swordfighting_new.core.board import Board
from swordfighting_new.fighters.base_fighter import BaseFighter
from swordfighting_new.mechanics.timing import TimingConfig


def test_full_column_defeat_check_does_not_preempt_active_chain(monkeypatch) -> None:
    # Enable the optional full-column defeat rule (defaults to disabled).
    # Use the default spawn column (spawn_x=3 -> 1-based col 4).
    monkeypatch.setenv("BF_GAME_OVER_COLUMN", "4")

    # Minimal fighter + board.
    timing = TimingConfig()
    f = BaseFighter(timing=timing, fighter_name="player", board=Board())

    # Force chain runner to be active (simulate a just-locked piece starting a chain).
    f.chain_runner.start()

    # Fill the monitored game-over column to a losing state.
    gox = int(getattr(f.movement, "game_over_x", 0) or 0)
    for y in range(f.board.HEIGHT):
        f.board.set_piece(gox, y, 1)

    assert bool(getattr(f, "defeated", False)) is False

    # Update should prioritize chain resolution and not instantly defeat.
    f.update(intents={})

    assert bool(getattr(f, "defeated", False)) is False
    # With no triggered breakers, a started chain finishes immediately.
    assert bool(getattr(f.chain_runner, "finished", False)) is True
