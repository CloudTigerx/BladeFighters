from swordfighting_new.mechanics.timing import DEFAULT_TIMING
from swordfighting_new.session import RubixOpponent, create_shared_piece_queue
from swordfighting_new.pieces.piece import Block
from swordfighting_new.pieces.shared_piece_queue import SharedPieceQueue


def _fill_column(board, x: int, height: int, *, color: str = "red") -> None:
    """Fill bottom `height` cells in column x."""
    height = max(0, min(int(getattr(board, "HEIGHT", 12) or 12), int(height)))
    h = int(getattr(board, "HEIGHT", 12) or 12)
    for i in range(height):
        y = h - 1 - i
        board.set_piece(int(x), int(y), Block(color))


def test_rubix6_switches_to_survival_and_back(monkeypatch) -> None:
    # Disable breaker-grace so this test exercises only the raw thresholds.
    monkeypatch.setenv('BF_RUBIX6_BREAKER_GRACE', '0')

    pq = create_shared_piece_queue(123)
    ai = RubixOpponent(
        DEFAULT_TIMING,
        spawn_x=3,
        attack_delay_frames=24,
        bulk_delivery=True,
        enable_puzzle_speeds=False,
        piece_queue=pq,
    )
    ai.set_boss_level(6)

    # Start empty => aggressive.
    ai._update_rubix6_mode()
    assert getattr(ai, "_rubix6_mode", None) == "aggressive"

    # Raise stack to row 7 (HEIGHT=12 default) => survival.
    for x in range(int(getattr(ai.board, "WIDTH", 6) or 6)):
        _fill_column(ai.board, x, 7)
    ai._update_rubix6_mode()
    assert getattr(ai, "_rubix6_mode", None) == "survival"

    # Score should report effective lv=5 while in survival.
    _ = ai._score_board_state(ai.board)
    assert getattr(ai, "_debug_last_effective_level", None) == 5
    assert getattr(ai, "_debug_last_rubix6_mode", "") == "survival"

    # Clear down to/below row 5 => aggressive.
    ai.board.clear()
    for x in range(int(getattr(ai.board, "WIDTH", 6) or 6)):
        _fill_column(ai.board, x, 5)
    ai._update_rubix6_mode()
    assert getattr(ai, "_rubix6_mode", None) == "aggressive"

    _ = ai._score_board_state(ai.board)
    assert getattr(ai, "_debug_last_effective_level", None) == 6


def test_rubix6_breaker_grace_delays_survival_switch(monkeypatch) -> None:
    # Make the breaker-lookahead deterministic: always red, always breaker.
    pq = SharedPieceQueue(seed=1, colors=("red",), breaker_prob=1.0)
    ai = RubixOpponent(
        DEFAULT_TIMING,
        spawn_x=3,
        attack_delay_frames=24,
        bulk_delivery=True,
        enable_puzzle_speeds=False,
        piece_queue=pq,
    )
    ai.set_boss_level(6)

    monkeypatch.delenv('BF_RUBIX6_BREAKER_GRACE', raising=False)
    monkeypatch.setenv('BF_RUBIX6_BREAKER_LOOKAHEAD', '4')
    monkeypatch.setenv('BF_RUBIX6_BREAKER_MAX_DIST', '2')
    monkeypatch.setenv('BF_RUBIX6_BREAKER_GROUP_MIN', '8')
    monkeypatch.setenv('BF_RUBIX6_BREAKER_EXPOSURE_MIN', '2')

    # Build a big exposed red clump, but no breaker on-board yet.
    ai.board.clear()
    for x in range(int(getattr(ai.board, "WIDTH", 6) or 6)):
        _fill_column(ai.board, x, 7, color="red")

    # We are at/above survival threshold (7), but a breaker payoff is imminent
    # (next_piece is a red breaker), so mode should stay aggressive.
    ai._rubix6_mode = "aggressive"
    ai._update_rubix6_mode()
    assert getattr(ai, "_rubix6_mode", None) == "aggressive"
