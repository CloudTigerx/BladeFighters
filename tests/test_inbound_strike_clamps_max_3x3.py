import pytest

from swordfighting_new.attacks.types import Attack, AttackKind


class _TimingStub:
    target_fps = 60
    autonomous_fall_interval_frames = 6


@pytest.mark.unit
def test_inbound_strike_clamps_to_board_and_width_caps_for_shapes_and_rects():
    from swordfighting_new.core.board import Board
    from swordfighting_new.fighters.inbound_attack_handler import InboundAttackHandler

    board = Board()
    handler = InboundAttackHandler(
        board=board,
        timing=_TimingStub(),
        piece_mover=None,
        gravity_manager=None,
    )

    handler.receive_attacks(
        [
            Attack(AttackKind.STRIKE, 999, meta={"sword_shape": (3, 12)}),
            Attack(AttackKind.STRIKE, 999, meta={"horizontal_sword_shape": (3, 6)}),
            Attack(AttackKind.STRIKE, 999, meta={"rect": (6, 6)}),
            Attack(AttackKind.STRIKE, 999, meta={}),
        ]
    )

    # Shapes are clamped by design rules (width<=3) and board bounds.
    # (Board is 6x12) so max vertical sword area is 3*12=36.
    assert handler.pending_in_strike <= 36 * 4

    # And the stored cluster dims must respect width<=3 and board dims.
    for kind, dims in (getattr(handler, "_pending_in_strike_clusters", []) or []):
        w, h = dims
        assert int(w) <= 3
        if kind == 'hsword':
            assert int(h) <= 6
        else:
            assert int(h) <= 12
