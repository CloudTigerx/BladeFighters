"""Animation feature tests (skipped if progressive cascade API absent).

Currently the progressive wave API may be disabled; these tests auto-skip.
"""
import pytest
from swordfighting_new.core.board import Board
from swordfighting_new.pieces.piece import Block
from swordfighting_new.mechanics.breaker import BreakerManager


progressive = hasattr(BreakerManager, 'begin_breaker_cascade')


@pytest.mark.skipif(not progressive, reason="Progressive cascade API not present")
def test_wave0_breakers_only():
    b = Board()
    b.set_piece(5, 10, Block("red", is_breaker=True))
    b.set_piece(5, 9, Block("red"))
    state = BreakerManager(b).begin_breaker_cascade()
    assert state is not None
    wave0 = state.waves[0]
    assert wave0, "Wave0 empty"
    for (x, y) in wave0:
        cell = b.get_piece(x, y)
        assert getattr(cell, 'is_breaker', False)
