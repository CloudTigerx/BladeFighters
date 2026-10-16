from swordfighting_new.core.board import Board
from swordfighting_new.fighters.movement_controller import MovementController
from swordfighting_new.mechanics.gravity import GravityManager
from swordfighting_new.mechanics.movement import PieceMover
from swordfighting_new.mechanics.timing import TimingConfig
from swordfighting_new.pieces.piece import Block

def test_top_row_full_triggers_defeat_after_settle() -> None:
    board = Board()
    mover = PieceMover(board)
    timing = TimingConfig(gravity_interval_frames=2, gravity_fast_interval_frames=1)
    gravity = GravityManager(board=board, mover=mover, timing=timing)
    mc = MovementController(board=board, piece_mover=mover, gravity_manager=gravity, timing=timing, spawn_x=3)

    # Fill the entire board so snap-settle cannot change occupancy.
    w = int(getattr(board, 'WIDTH', 6) or 6)
    h = int(getattr(board, 'HEIGHT', 12) or 12)
    for x in range(w):
        for y in range(h):
            board.set_piece(int(x), int(y), Block('red'))

    assert bool(mc.check_top_row_full_defeat(transient_piece=None)) is True
    assert bool(mc.is_defeated()) is True


def test_top_row_full_does_not_false_defeat_if_blocks_can_fall() -> None:
    board = Board()
    mover = PieceMover(board)
    timing = TimingConfig(gravity_interval_frames=2, gravity_fast_interval_frames=1)
    gravity = GravityManager(board=board, mover=mover, timing=timing)
    mc = MovementController(board=board, piece_mover=mover, gravity_manager=gravity, timing=timing, spawn_x=3)

    # Put blocks in the top row but leave space beneath them so snap-settle can drop them.
    w = int(getattr(board, 'WIDTH', 6) or 6)
    for x in range(w):
        board.set_piece(int(x), 0, Block('blue'))
        board.set_piece(int(x), 1, board.EMPTY)

    assert bool(mc.check_top_row_full_defeat(transient_piece=None)) is False

    # After settle, the top row should not remain full, so no defeat.
    assert bool(mc.is_defeated()) is False

    for x in range(w):
        assert board.get_piece(int(x), 0) == board.EMPTY
