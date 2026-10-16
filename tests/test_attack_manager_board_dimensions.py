import pytest

from swordfighting_new.attacks.manager import AttackManager
from swordfighting_new.attacks.types import AttackKind


@pytest.mark.unit
def test_attack_manager_vertical_strike_caps_to_board_height_from_generate_from_chain():
    """Strike generation should cap vertical sword length to the provided board height.

    This guards against hard-coded 6x12 assumptions in attack generation.
    """
    mgr = AttackManager()

    # Height is larger than board_height; length should cap to 16.
    mgr.generate_from_chain(
        [{"sprinkles": 0, "rectangles": [{"width": 3, "height": 20}]}],
        board_width=6,
        board_height=16,
    )

    out = list(mgr.generated_last_chain)
    assert len(out) == 1
    atk = out[0]

    assert atk.kind == AttackKind.STRIKE
    assert tuple(atk.meta.get("sword_shape")) == (3, 16)
    assert int(atk.amount) == 48


@pytest.mark.unit
def test_attack_manager_horizontal_entry_caps_to_board_width_from_generate_from_chain():
    """Horizontal sword entry should cap to the provided board width."""
    mgr = AttackManager()

    # Wider-than-tall => horizontal candidate. raw_length=10*1=10, enters up to board_width=8.
    mgr.generate_from_chain(
        [{"sprinkles": 0, "rectangles": [{"width": 10, "height": 2}]}],
        board_width=8,
        board_height=12,
    )

    out = list(mgr.generated_last_chain)
    assert len(out) == 1
    atk = out[0]

    assert atk.kind == AttackKind.STRIKE
    assert tuple(atk.meta.get("horizontal_sword_shape")) == (2, 8)
    assert int(atk.amount) == 16
