from swordfighting_new.core.board import Board
from swordfighting_new.mechanics.timing import DEFAULT_TIMING
from swordfighting_new.pieces.piece import Block
from swordfighting_new.session import RubixOpponent


def test_rubix_simulated_resolve_counts_breaker_clear() -> None:
    b = Board()

    # Build a connected red region with a breaker at the bottom.
    breaker_xy = (2, 11)
    region = [
        (2, 10),
        (2, 9),
        (2, 8),
        (1, 10),
        (3, 10),
        (1, 9),
        (3, 9),
    ]

    b.set_piece(*breaker_xy, Block("red", is_breaker=True))
    for x, y in region:
        b.set_piece(x, y, Block("red", is_breaker=False))

    ai = RubixOpponent(DEFAULT_TIMING)
    resolved, cleared = ai._simulate_combo_resolve_with_stats(b, max_steps=1)

    # The breaker is triggered (adjacent same-color neighbor), so it should clear
    # itself and the whole connected component.
    expected = 1 + len(region)
    assert cleared >= expected
    assert resolved.get_piece(*breaker_xy) == resolved.EMPTY
    for x, y in region:
        assert resolved.get_piece(x, y) == resolved.EMPTY
