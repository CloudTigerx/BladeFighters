import os

from swordfighting_new.fighters.base_fighter import BaseFighter
from swordfighting_new.mechanics.timing import TimingConfig
from swordfighting_new.pieces.piece import Block, Piece


def test_spawn_overlap_records_defeat_reason() -> None:
    prev = os.environ.get('BF_SPAWN_Y')
    prev_go = os.environ.get('BF_GAME_OVER_COLUMN')
    os.environ['BF_SPAWN_Y'] = '0'
    os.environ.pop('BF_GAME_OVER_COLUMN', None)
    try:
        timing = TimingConfig(gravity_interval_frames=2, gravity_fast_interval_frames=1)
        f = BaseFighter(timing=timing, spawn_x=3)

        # Force a 1-block piece so overlap is deterministic.
        f.movement.next_piece = Piece.from_cells([(0, 0, Block('red'))])

        # Occupy the spawn cell so spawning overlaps in-bounds.
        # Fill the whole column so the pre-defeat snap-settle cannot "save" the spawn
        # by dropping the blocker down.
        for yy in range(int(getattr(f.board, 'HEIGHT', 12) or 12)):
            f.board.set_piece(3, yy, Block('blue'))

        ok = f.movement.spawn_new_piece_post_chain()
        assert ok is False
        assert bool(f.movement.defeated) is True
        assert str(getattr(f.movement, 'last_defeat_reason', None) or '') == 'spawn_overlap'
    finally:
        if prev is None:
            os.environ.pop('BF_SPAWN_Y', None)
        else:
            os.environ['BF_SPAWN_Y'] = prev

        if prev_go is None:
            os.environ.pop('BF_GAME_OVER_COLUMN', None)
        else:
            os.environ['BF_GAME_OVER_COLUMN'] = prev_go
