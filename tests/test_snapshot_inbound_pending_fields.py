from __future__ import annotations

from swordfighting_new.session import MatchSession


def test_snapshot_includes_inbound_pending_fields() -> None:
    s = MatchSession(enemy_style="passive")
    snap = s.snapshot()

    assert "player" in snap
    assert "ai" in snap

    for side_key in ("player", "ai"):
        side = snap[side_key]
        assert isinstance(side, dict)
        for k in ("pending_sprinkle", "pending_strike", "inbound_delay", "spawn_queue", "strike_land_seq"):
            assert k in side
            assert isinstance(side[k], int)
            assert side[k] >= 0
