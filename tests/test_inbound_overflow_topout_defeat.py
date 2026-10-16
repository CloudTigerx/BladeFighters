from swordfighting_new.fighters.base_fighter import BaseFighter
from swordfighting_new.mechanics.timing import TimingConfig
from swordfighting_new.pieces.piece import Block, Piece


def test_inbound_overflow_locks_above_board_triggers_defeat() -> None:
    timing = TimingConfig(gravity_interval_frames=2, gravity_fast_interval_frames=1)
    f = BaseFighter(timing=timing, spawn_x=3)

    # Ensure no controllable piece interferes with inbound ticking.
    f.movement.current_piece = None

    # Create a 3-tall inbound piece whose anchor block is at y=0.
    # Two blocks are above the board (y=-1, y=-2). If it locks now, that is a top-out.
    p = Piece.from_cells(
        [
            (0, 0, Block("red")),
            (0, -1, Block("red")),
            (0, -2, Block("red")),
        ]
    )
    p.x = 2
    p.y = 0
    p.controllable = False
    p.autonomous_fall_interval = 1
    p.autonomous_fall_timer = 1

    # Block downward movement so the piece locks at y=0.
    f.board.set_piece(2, 1, Block("blue"))

    f.inbound_handler.garbage_fallers = [p]

    f.update({})

    assert bool(getattr(f.inbound_handler, "inbound_overflowed", False)) is True
    assert bool(f.defeated) is True
    assert bool(f.movement.is_defeated()) is True
    assert str(getattr(f, 'last_defeat_reason', None) or '') == 'inbound_overflow'
    assert str(getattr(getattr(f, 'movement', None), 'last_defeat_reason', None) or '') == 'inbound_overflow'
