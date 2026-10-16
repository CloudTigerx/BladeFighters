from __future__ import annotations

import pytest

from swordfighting_new.attacks.manager import AttackManager
from swordfighting_new.attacks.types import AttackKind
from swordfighting_new.core.board import Board
from swordfighting_new.mechanics.breaker import BreakerManager
from swordfighting_new.mechanics.chain_runner import BreakerChainRunner
from swordfighting_new.pieces.piece import Block


def _run_chain_and_collect_attacks(board: Board) -> tuple[list[dict], list]:
    bm = BreakerManager(board=board, debug=False)
    runner = BreakerChainRunner(board=board, breaker_manager=bm, frame_delay=0, cascade_mode="fast")

    runner.start()
    safety = 0
    while runner.active and safety < 5000:
        safety += 1
        runner.update()

    assert runner.finished is True

    pass_stats = runner.get_pass_stats()
    mgr = AttackManager()
    mgr.generate_from_chain(pass_stats, board_width=board.WIDTH, board_height=board.HEIGHT)
    return pass_stats, list(mgr.generated_last_chain)


@pytest.mark.integration
def test_pipeline_detects_full_height_rectangle_2x12(monkeypatch):
    # Keep tests readable: disable extremely chatty debug prints in breaker.
    import swordfighting_new.mechanics.breaker as breaker_mod

    monkeypatch.setattr(breaker_mod, "ENABLE_DEBUG", False, raising=False)

    board = Board()

    # Build a 2x12 rectangle of normal blocks (red) plus an adjacent red breaker.
    for x in (0, 1):
        for y in range(board.HEIGHT):
            board.set_piece(x, y, Block("red"))

    # Breaker adjacent to the rectangle triggers and clears it.
    board.set_piece(2, 0, Block("red", is_breaker=True))

    pass_stats, attacks = _run_chain_and_collect_attacks(board)

    assert len(pass_stats) == 1
    s0 = pass_stats[0]

    # Stats extraction should recognize the full-height rectangle.
    rects = list(s0.get("rectangles", []) or [])
    assert rects and rects[0]["width"] == 2 and rects[0]["height"] == 12
    assert int(s0.get("sprinkles", 0)) == 0

    # Attack generation should preserve the source rect metadata and cap by board dimensions.
    assert len(attacks) == 1
    atk = attacks[0]
    assert atk.kind == AttackKind.STRIKE
    assert int(atk.amount) == 24  # 2x12 at board-height cap
    assert tuple(atk.meta.get("rect")) == (2, 12)
    assert tuple(atk.meta.get("sword_shape")) == (2, 12)


@pytest.mark.integration
def test_pipeline_chain_multiplier_applies_on_second_pass(monkeypatch):
    import swordfighting_new.mechanics.breaker as breaker_mod

    monkeypatch.setattr(breaker_mod, "ENABLE_DEBUG", False, raising=False)

    board = Board()

    # Pass 1: a blue breaker clears itself + one adjacent blue normal.
    # This removes 2 cells in column 5, creating space for green blocks above to fall.
    board.set_piece(5, 11, Block("blue", is_breaker=True))
    board.set_piece(5, 10, Block("blue"))

    # Pass 2 setup: a green breaker sits at (4,11) and will only trigger
    # after cascade makes (5,11) become green.
    board.set_piece(4, 11, Block("green", is_breaker=True))

    # Four green blocks above the blue pair. After pass 1 clears, these fall down 2,
    # placing a green at (5,11) adjacent to the green breaker.
    for y in (6, 7, 8, 9):
        board.set_piece(5, y, Block("green"))

    pass_stats, attacks = _run_chain_and_collect_attacks(board)

    # We expect two passes of stats.
    assert len(pass_stats) == 2

    # Second pass should be 4 sprinkles (1x4 vertical line => no rectangles).
    s1 = pass_stats[1]
    assert int(s1.get("sprinkles", 0)) == 4
    assert list(s1.get("rectangles", []) or []) == []

    # AttackManager: pass_index=2 => floor(4/2)*2 = 4 sprinkles.
    sprinkle_attacks = [a for a in attacks if a.kind == AttackKind.SPRINKLE]
    assert len(sprinkle_attacks) == 1
    assert int(sprinkle_attacks[0].amount) == 4
