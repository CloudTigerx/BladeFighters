from swordfighting_new.core.board import Board
from swordfighting_new.fighters.movement_controller import MovementController
from swordfighting_new.mechanics.gravity import GravityManager
from swordfighting_new.mechanics.movement import PieceMover
from swordfighting_new.mechanics.timing import TimingConfig
from swordfighting_new.pieces.piece import Piece


def test_top_row_fall_is_3x_slower(monkeypatch):
    # Keep the multiplier explicit for the test.
    monkeypatch.setenv('BF_TOP_ROW_FALL_SLOW_MULT', '3')

    board = Board()
    mover = PieceMover(board)
    timing = TimingConfig(gravity_interval_frames=2, gravity_fast_interval_frames=1)
    gravity = GravityManager(board, mover=mover, timing=timing)

    mc = MovementController(board, mover, gravity, timing, spawn_x=3)

    # Force a single-block controllable piece in the top row.
    mc.current_piece = Piece.single_block('red')
    mc.current_piece.x = 3
    mc.current_piece.y = 0

    # Base interval is 2 frames; with 3x top-row slow it becomes 6.
    should_lock, gravity_applied = mc.update(intents={}, frame=2)
    assert should_lock is False
    assert gravity_applied is False
    assert mc.current_piece.y == 0

    should_lock, gravity_applied = mc.update(intents={}, frame=6)
    assert should_lock is False
    assert gravity_applied is True
    assert mc.current_piece.y == 1
