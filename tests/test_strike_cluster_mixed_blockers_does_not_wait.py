import pytest

from swordfighting_new.pieces.piece import Block, Piece


class _TimingStub:
    target_fps = 60
    autonomous_fall_interval_frames = 2


class _GravityStub:
    def lock_piece(self, _piece):
        # This test exercises the pre-lock piercing path.
        return


def _find_inbound_attack_handler():
    from swordfighting_new.fighters.inbound_attack_handler import InboundAttackHandler

    return InboundAttackHandler


def _find_board_class():
    from swordfighting_new.core.board import Board

    return Board


@pytest.mark.unit
def test_strike_cluster_does_not_wait_when_board_blocked_and_faller_blocked():
    """If a strike cluster is board-blocked, it must not 'wait' just because another faller
    also blocks part of the cluster.

    Regression: the strike-group logic used `any(_blocked_only_by_faller(...))` and would wait
    even when another part of the cluster was blocked by the board, preventing piercing/locking.
    """

    Board = _find_board_class()
    InboundAttackHandler = _find_inbound_attack_handler()

    board = Board()

    # Board blocker directly under the strike piece at x=2.
    board.set_piece(2, 6, Block('blue'))

    handler = InboundAttackHandler(
        board=board,
        timing=_TimingStub(),
        piece_mover=None,
        gravity_manager=_GravityStub(),
    )

    # Two strike pieces in the same cluster, both attempting to fall from y=5 -> y=6.
    strike_a = Piece.single_block(color='white', is_strike=True, attack_state='strike')
    strike_a.x = 2
    strike_a.y = 5
    strike_a.controllable = False
    strike_a.autonomous_fall_interval = 1
    strike_a.autonomous_fall_timer = 1
    strike_a.sword_rows = 2
    strike_a.sword_width = 2
    strike_a.strike_cluster_id = 123

    strike_b = Piece.single_block(color='white', is_strike=True, attack_state='strike')
    strike_b.x = 3
    strike_b.y = 5
    strike_b.controllable = False
    strike_b.autonomous_fall_interval = 1
    strike_b.autonomous_fall_timer = 1
    strike_b.sword_rows = 2
    strike_b.sword_width = 2
    strike_b.strike_cluster_id = 123

    # Another non-strike faller sits under strike_b at (3,6), which should not cause the
    # whole cluster to wait when strike_a is board-blocked.
    other = Piece.single_block(color='red')
    other.x = 3
    other.y = 6
    other.controllable = False
    other.autonomous_fall_interval = 999
    other.autonomous_fall_timer = 0

    handler.garbage_fallers = [strike_a, strike_b, other]

    handler.update_inbound_garbage()

    # The board blocker should have been pierced/cleared.
    assert board.get_piece(2, 6) == board.EMPTY

    # The strike pieces should have advanced at least one row.
    assert strike_a.y >= 6
    assert strike_b.y >= 6
