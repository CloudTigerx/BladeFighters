import pytest

from swordfighting_new.session import MatchSession
from swordfighting_new.attacks.types import Attack, AttackKind


def test_hp_mode_boss_default_hp_is_halved(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("BF_BOSS_HP", raising=False)

    s = MatchSession(enemy_style="boss")
    assert s.ai is not None
    assert bool(getattr(s, "enemy_has_board", True)) is False

    assert int(getattr(s, "enemy_hp_max", 0) or 0) == 100
    assert int(getattr(s, "enemy_hp", 0) or 0) == 100


def test_hp_mode_combo_multiplies_damage(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("BF_BOSS_HP", raising=False)

    s = MatchSession(enemy_style="boss")
    assert s.ai is not None

    # Keep the update loop focused on HP damage conversion.
    s.player.update = lambda intents: None  # type: ignore[assignment]
    s.ai.update = lambda: None  # type: ignore[assignment]

    s.player.collect_ready_attacks = lambda: [
        Attack(kind=AttackKind.SPRINKLE, amount=10, delay=0, meta={"chain": 3})
    ]  # type: ignore[assignment]

    s.update({})

    assert int(getattr(s, "enemy_hp", 0) or 0) == 70


def test_hp_mode_enemy_defeat_persists_after_zero_hp(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("BF_BOSS_HP", raising=False)

    s = MatchSession(enemy_style="boss")
    assert s.ai is not None

    # Keep the update loop focused on HP damage conversion.
    s.player.update = lambda intents: None  # type: ignore[assignment]
    s.ai.update = lambda: None  # type: ignore[assignment]

    # Deal exactly lethal damage.
    s.player.collect_ready_attacks = lambda: [
        Attack(kind=AttackKind.SPRINKLE, amount=100, delay=0, meta={"chain": 1})
    ]  # type: ignore[assignment]

    s.update({})
    assert int(getattr(s, "enemy_hp", 0) or 0) == 0
    assert bool(getattr(s.ai, "defeated", False)) is True

    # Next frame, defeat should not be cleared by HP-mode enemy updater.
    s.player.collect_ready_attacks = lambda: []  # type: ignore[assignment]
    s.update({})
    assert bool(getattr(s.ai, "defeated", False)) is True
