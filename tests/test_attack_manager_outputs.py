import pytest

from swordfighting_new.attacks.manager import AttackManager
from swordfighting_new.attacks.types import AttackKind


@pytest.mark.unit
@pytest.mark.parametrize(
    "sprinkles,pass_index,expected",
    [
        (0, 1, 0),
        (1, 1, 0),
        (2, 1, 1),
        (4, 1, 2),
        (6, 1, 3),
        (12, 1, 6),
        (2, 2, 2),
        (4, 2, 4),
        (6, 2, 6),
        (12, 2, 12),
    ],
)
def test_attack_manager_sprinkles_only_formula(sprinkles, pass_index, expected):
    mgr = AttackManager()
    mgr.generate_from_pass(pass_index, {"sprinkles": sprinkles, "rectangles": []})

    out = list(mgr.generated_last_chain)
    if expected <= 0:
        assert out == []
        return

    assert len(out) == 1
    assert out[0].kind == AttackKind.SPRINKLE
    assert int(out[0].amount) == int(expected)


@pytest.mark.unit
@pytest.mark.parametrize(
    "rect,pass_index,expected_amount,expected_meta_key,expected_shape",
    [
        ({"width": 2, "height": 2}, 1, 4, "sword_shape", (2, 2)),
        ({"width": 2, "height": 3}, 1, 6, "sword_shape", (2, 3)),
        # Vertical length is capped by board height (12).
        ({"width": 2, "height": 12}, 1, 24, "sword_shape", (2, 12)),
        ({"width": 3, "height": 12}, 1, 36, "sword_shape", (3, 12)),
        ({"width": 1, "height": 12}, 1, 12, "sword_shape", (1, 12)),
    ],
)
def test_attack_manager_vertical_strike_shapes(rect, pass_index, expected_amount, expected_meta_key, expected_shape):
    mgr = AttackManager()
    mgr.generate_from_pass(pass_index, {"sprinkles": 0, "rectangles": [rect]})

    out = list(mgr.generated_last_chain)
    assert len(out) == 1
    atk = out[0]

    assert atk.kind == AttackKind.STRIKE
    assert int(atk.amount) == int(expected_amount)
    assert expected_meta_key in (atk.meta or {})
    assert tuple(atk.meta[expected_meta_key]) == tuple(expected_shape)


@pytest.mark.unit
@pytest.mark.parametrize(
    "rect,pass_index,expected_amount,expected_shape",
    [
        # Wider-than-tall => horizontal sword, length enters up to board width (6).
        ({"width": 4, "height": 2}, 1, 8, (2, 4)),
        ({"width": 6, "height": 2}, 1, 12, (2, 6)),
        ({"width": 8, "height": 2}, 1, 12, (2, 6)),
    ],
)
def test_attack_manager_horizontal_strike_shapes(rect, pass_index, expected_amount, expected_shape):
    mgr = AttackManager()
    mgr.generate_from_pass(pass_index, {"sprinkles": 0, "rectangles": [rect]})

    out = list(mgr.generated_last_chain)
    assert len(out) == 1
    atk = out[0]

    assert atk.kind == AttackKind.STRIKE
    assert int(atk.amount) == int(expected_amount)
    assert "horizontal_sword_shape" in (atk.meta or {})
    assert tuple(atk.meta["horizontal_sword_shape"]) == tuple(expected_shape)


@pytest.mark.unit
def test_attack_manager_horizontal_converts_to_vertical_when_too_long_for_entry():
    mgr = AttackManager()

    # width=6, chain=2 => raw_length = 12, conversion threshold = 12 => convert
    mgr.generate_from_pass(2, {"sprinkles": 0, "rectangles": [{"width": 6, "height": 2}]})

    out = list(mgr.generated_last_chain)
    assert len(out) == 1
    atk = out[0]

    assert atk.kind == AttackKind.STRIKE
    assert int(atk.amount) == 24
    assert atk.meta.get("orientation") == "vertical"


@pytest.mark.unit
def test_attack_manager_3x2_chain_3_converts_to_vertical_2x6() -> None:
    mgr = AttackManager()

    # 3x2 at chain 1 => 2x3 horizontal (partial entry)
    # 3x2 at chain 2 => 2x6 horizontal (full entry)
    # 3x2 at chain 3 previously repeated 2x6 horizontal due to entry cap;
    # expected behavior is a 2x6 vertical sword.
    mgr.generate_from_pass(3, {"sprinkles": 0, "rectangles": [{"width": 3, "height": 2}]})

    out = list(mgr.generated_last_chain)
    assert len(out) == 1
    atk = out[0]

    assert atk.kind == AttackKind.STRIKE
    assert int(atk.amount) == 12
    assert atk.meta.get("orientation") == "vertical"
    assert tuple(atk.meta.get("sword_shape")) == (2, 6)
    assert bool(atk.meta.get("converted_from_horizontal_saturation")) is True


@pytest.mark.unit
def test_attack_manager_mix_sprinkles_and_rectangles_same_pass():
    mgr = AttackManager()
    mgr.generate_from_pass(
        1,
        {
            "sprinkles": 6,  # => floor(6/2)*1 = 3
            "rectangles": [
                {"width": 2, "height": 2},
                {"width": 3, "height": 3},
            ],
        },
    )

    out = list(mgr.generated_last_chain)
    assert [a.kind for a in out] == [AttackKind.SPRINKLE, AttackKind.STRIKE, AttackKind.STRIKE]
    assert int(out[0].amount) == 3
    assert int(out[1].amount) == 4
    assert int(out[2].amount) == 9


@pytest.mark.unit
def test_attack_manager_chain_multiplier_applies_per_pass_index():
    mgr = AttackManager()
    mgr.generate_from_chain(
        [
            {"sprinkles": 4, "rectangles": []},  # pass 1 => 2
            {"sprinkles": 4, "rectangles": []},  # pass 2 => 4
        ],
        board_width=6,
        board_height=12,
    )

    out = list(mgr.generated_last_chain)
    assert len(out) == 2
    assert out[0].kind == AttackKind.SPRINKLE and int(out[0].amount) == 2
    assert out[1].kind == AttackKind.SPRINKLE and int(out[1].amount) == 4


@pytest.mark.unit
@pytest.mark.parametrize(
    "rect,pass_index",
    [
        ({"width": 999, "height": 999}, 1),
        ({"width": 999, "height": 1}, 1),
        ({"width": 999, "height": 2}, 5),
        ({"width": 6, "height": 2}, 10),  # would be huge raw_length, must still cap by board dims
    ],
)
def test_attack_manager_strike_is_capped_by_board_and_width_rules(rect, pass_index):
    mgr = AttackManager()
    mgr.generate_from_pass(pass_index, {"sprinkles": 0, "rectangles": [rect]})

    out = list(mgr.generated_last_chain)
    assert len(out) == 1
    atk = out[0]

    assert atk.kind == AttackKind.STRIKE
    assert int(atk.amount) <= 3 * 12

    meta = atk.meta or {}
    if "sword_shape" in meta:
        w, h = meta["sword_shape"]
        assert int(w) <= 3
        assert int(h) <= 12
    if "horizontal_sword_shape" in meta:
        rows, length = meta["horizontal_sword_shape"]
        assert int(rows) <= 3
        assert int(length) <= 6


@pytest.mark.unit
def test_attack_manager_sprinkles_below_two_do_not_emit_even_with_rectangles_present():
    mgr = AttackManager()
    mgr.generate_from_pass(
        1,
        {
            "sprinkles": 1,
            "rectangles": [{"width": 2, "height": 2}],
        },
    )

    out = list(mgr.generated_last_chain)
    assert len(out) == 1
    assert out[0].kind == AttackKind.STRIKE
    assert int(out[0].amount) == 4
