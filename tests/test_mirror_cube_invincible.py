import pytest

from swordfighting_new.attacks import Attack, AttackKind
from swordfighting_new.session import MatchSession


def test_mirror_cube_never_loses_hp_or_defeated() -> None:
    s = MatchSession(enemy_style="mirror")
    assert s.ai is not None

    # Keep the update loop focused on HP-mode conversion.
    s.player.update = lambda intents: None  # type: ignore[assignment]
    s.ai.update = lambda: None  # type: ignore[assignment]

    start_enemy_hp = int(getattr(s, "enemy_hp", 0) or 0)
    start_enemy_hp_max = int(getattr(s, "enemy_hp_max", 0) or 0)

    # Big damage should be reflected to the player, not applied to the mirror.
    s.player.collect_ready_attacks = lambda: [
        Attack(kind=AttackKind.SPRINKLE, amount=200, delay=0, meta={"chain": 5})
    ]  # type: ignore[assignment]

    s.update({})

    assert int(getattr(s, "enemy_hp", 0) or 0) == start_enemy_hp
    assert int(getattr(s, "enemy_hp_max", 0) or 0) == start_enemy_hp_max
    assert bool(getattr(s.ai, "defeated", False)) is False


def test_mirror_cube_defensive_reset_clears_defeat_flags() -> None:
    s = MatchSession(enemy_style="mirror")
    assert s.ai is not None

    # Force a bad/buggy state that might happen via offscreen board logic.
    s.enemy_hp = 0
    s.ai.defeated = True
    try:
        s.ai.movement.defeated = True
    except Exception:
        pass

    # Run a frame; mirror invincibility should be enforced.
    s.player.update = lambda intents: None  # type: ignore[assignment]
    s.ai.update = lambda: None  # type: ignore[assignment]
    s.player.collect_ready_attacks = lambda: []  # type: ignore[assignment]

    s.update({})

    assert bool(getattr(s.ai, "defeated", False)) is False
    assert int(getattr(s, "enemy_hp", 0) or 0) == int(getattr(s, "enemy_hp_max", 1) or 1)
