from __future__ import annotations

from swordfighting_new.core.board import Board
from swordfighting_new.fighters.movement_controller import MovementController
from swordfighting_new.mechanics.gravity import GravityManager
from swordfighting_new.mechanics.movement import PieceMover
from swordfighting_new.pieces.piece import Piece, Block


class _TimingStub:
    # MovementController expects these
    lock_delay_frames = 0

    # GravityManager expects these
    autonomous_fall_interval_frames = 6
    split_fall_interval_frames = 6

    def interval_for_level(self, level: int, fast: bool) -> int:
        return 60


def test_spawn_overlap_rechecked_after_global_gravity(monkeypatch):
    # Force visible spawn so the overlap check can trigger.
    monkeypatch.setenv("BF_SPAWN_Y", "0")

    board = Board()
    mover = PieceMover(board)
    gravity = GravityManager(board=board, mover=mover, timing=_TimingStub())

    mc = MovementController(board=board, piece_mover=mover, gravity_manager=gravity, timing=_TimingStub(), spawn_x=3)

    # Put a floating block in the spawn cell; global gravity should drop it.
    spawn_x = mc.spawn_x
    board.set_piece(spawn_x, 0, 123)

    # Ensure we spawn a deterministic piece.
    mc.next_piece = Piece([Block("red"), Block("blue")])

    ok = mc.spawn_new_piece_post_chain()
    assert ok is True
    assert mc.defeated is False

    # The floating block should have snap-settled to the bottom.
    assert board.get_piece(spawn_x, 0) == board.EMPTY
    assert board.get_piece(spawn_x, board.HEIGHT - 1) != board.EMPTY


def test_above_board_top_blocked_rechecked_after_global_gravity():
    # Make the top row appear blocked, but with empty space below so it can settle.
    board = Board()
    mover = PieceMover(board)
    gravity = GravityManager(board=board, mover=mover, timing=_TimingStub())

    mc = MovementController(board=board, piece_mover=mover, gravity_manager=gravity, timing=_TimingStub(), spawn_x=3)

    spawn_x = mc.spawn_x
    board.set_piece(spawn_x, 0, 77)

    # Place current piece above-board and grounded (it can't move down into y=0).
    mc.current_piece = Piece([Block("red"), Block("blue")])
    mc.current_piece.x = spawn_x
    mc.current_piece.y = -1
    mc.current_piece.orientation = 0
    mc.current_piece.controllable = True

    _should_lock, _grav = mc.update(intents={}, frame=1)

    # Snap-settle should drop the floating top-row blocker, and we should NOT
    # immediately top-out since descent becomes possible after settling.
    assert mc.defeated is False
    assert board.get_piece(spawn_x, 0) == board.EMPTY
    assert board.get_piece(spawn_x, board.HEIGHT - 1) != board.EMPTY
