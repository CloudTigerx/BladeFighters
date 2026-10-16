from swordfighting_new.core.board import Board
from swordfighting_new.mechanics.cascade import CascadeManager
from swordfighting_new.mechanics.gravity import GravityManager
from swordfighting_new.pieces.piece import Block


class _TimingStub:
    target_fps = 60
    autonomous_fall_interval_frames = 6
    split_fall_interval_frames = 6


def test_supported_overhang_does_not_drip_or_fall():
    """Overhang blocks should fall even if their cluster is partially supported.

    Layout (y increases downward):
      R R
      R .

    The top-right R has empty below and should fall ("drip") down.
    """
    # Global gravity: snap-settle should drop the unsupported overhang cell immediately.
    b1 = Board()
    red1 = Block("red")
    red2 = Block("red")
    support = Block("blue")
    b1.set_piece(0, 10, red1)
    b1.set_piece(1, 10, red2)
    b1.set_piece(0, 11, support)  # grounded (bottom row)

    g = GravityManager(board=b1, mover=None, timing=_TimingStub())
    fallers = g.apply_global_gravity()
    assert fallers == []
    assert b1.get_piece(1, 10) == b1.EMPTY
    assert b1.get_piece(1, 11) != b1.EMPTY

    # Cascade: should "drip" the overhang down by one.
    b2 = Board()
    red1b = Block("red")
    red2b = Block("red")
    supportb = Block("blue")
    b2.set_piece(0, 10, red1b)
    b2.set_piece(1, 10, red2b)
    b2.set_piece(0, 11, supportb)

    c = CascadeManager(b2)
    moved = c.apply_step()
    assert moved == 1
    assert b2.get_piece(0, 10) != b2.EMPTY
    assert b2.get_piece(1, 10) == b2.EMPTY
    assert b2.get_piece(0, 11) != b2.EMPTY
    assert b2.get_piece(1, 11) != b2.EMPTY
