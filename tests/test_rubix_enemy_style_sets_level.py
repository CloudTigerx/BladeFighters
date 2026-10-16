from swordfighting_new.session import MatchSession


def test_rubix3_enemy_style_sets_rubix_level() -> None:
    s = MatchSession(enemy_style="rubix3")
    assert s.ai is not None
    assert int(getattr(s.ai, "_rubix_level", 0) or 0) == 3


def test_rubix4_enemy_style_sets_rubix_level() -> None:
    s = MatchSession(enemy_style="rubix4")
    assert s.ai is not None
    assert int(getattr(s.ai, "_rubix_level", 0) or 0) == 4


def test_rubix6_enemy_style_sets_rubix_level() -> None:
    s = MatchSession(enemy_style="rubix6")
    assert s.ai is not None
    assert int(getattr(s.ai, "_rubix_level", 0) or 0) == 6


def test_rubix5_enemy_style_sets_rubix_level() -> None:
    s = MatchSession(enemy_style="rubix5")
    assert s.ai is not None
    assert int(getattr(s.ai, "_rubix_level", 0) or 0) == 5


def test_rubix5_computes_opponent_sprinkle_profile(monkeypatch) -> None:
    # Ensure opponent pattern is deterministic.
    monkeypatch.setenv('BF_PLAYER_SWORD', 'cutlass')
    s = MatchSession(enemy_style="rubix5")
    assert s.ai is not None

    ai = s.ai
    p = getattr(getattr(ai, 'movement', None), 'current_piece', None)
    assert p is not None

    # Force one plan so ctx + debug fields are updated.
    ai._plan_for_piece(p)

    counts = getattr(ai, '_debug_last_opp_sprinkle_counts', None)
    assert isinstance(counts, dict)
    assert set(counts.keys()) >= {'red', 'blue', 'green', 'yellow'}
    assert sum(int(v or 0) for v in counts.values()) > 0


def test_rubix4_enables_beam_by_default(monkeypatch) -> None:
    # rubix4 should not silently cap down to rubix2 due to missing env flags.
    monkeypatch.setenv('BF_RUBIX_BEAM_ENABLED', '0')
    monkeypatch.delenv('BF_RUBIX_FORCE_GREEDY', raising=False)
    monkeypatch.delenv('BF_RUBIX_FORCE_LEVEL', raising=False)

    s = MatchSession(enemy_style="rubix4")
    assert s.ai is not None

    ai = s.ai
    p = getattr(getattr(ai, 'movement', None), 'current_piece', None)
    assert p is not None

    # Force one plan so debug fields are updated.
    ai._plan_for_piece(p)
    assert bool(getattr(ai, '_debug_last_beam_enabled', False)) is True
    assert int(getattr(ai, '_debug_last_effective_lv', 0) or 0) == 4


def test_rubix4_does_not_idle_on_vertical_flip_target() -> None:
    # When asked to go from orientation 0 -> 2 on an empty board,
    # rubix4 should rotate immediately (0->1 or 0->3), not wait.
    s = MatchSession(enemy_style="rubix4")
    assert s.ai is not None
    ai = s.ai
    p = getattr(getattr(ai, 'movement', None), 'current_piece', None)
    assert p is not None

    # Ensure a deterministic, rotatable setup.
    p.controllable = True
    p.orientation = 0
    p.y = 4
    ai._plan_piece_id = id(p)
    ai._plan_target_x = int(getattr(p, 'x', 0) or 0)
    ai._plan_target_o = 2

    ai.update()
    assert int(getattr(p, 'orientation', 0) or 0) % 4 != 0


def test_boss_level_overrides_rubix_style_level() -> None:
    s = MatchSession(enemy_style="rubix3", boss_level=5)
    assert s.ai is not None
    assert int(getattr(s.ai, "_rubix_level", 0) or 0) == 5


def test_rubix_top_caps_by_color_counts_column_tops() -> None:
    s = MatchSession(enemy_style="rubix5")
    assert s.ai is not None
    ai = s.ai

    class _Blk:
        def __init__(self, color: str, *, is_garbage: bool = False, attack_state=None):
            self.color = color
            self.is_garbage = is_garbage
            self.attack_state = attack_state

    b = ai.board
    b.clear()

    # Column 0: single red at bottom => cap is red.
    b.set_piece(0, b.HEIGHT - 1, _Blk('red'))
    # Column 1: two blues stacked => cap is blue at y=HEIGHT-2.
    b.set_piece(1, b.HEIGHT - 1, _Blk('blue'))
    b.set_piece(1, b.HEIGHT - 2, _Blk('blue'))
    # Column 2: top is garbage => should not count.
    b.set_piece(2, b.HEIGHT - 1, _Blk('green'))
    b.set_piece(2, b.HEIGHT - 2, _Blk('yellow', is_garbage=True))
    # Column 3: top is attack_state => should not count.
    b.set_piece(3, b.HEIGHT - 1, _Blk('green'))
    b.set_piece(3, b.HEIGHT - 2, _Blk('green', attack_state='sprinkle'))

    caps = ai._count_top_caps_by_color(b)
    assert isinstance(caps, dict)
    assert int(caps.get('red', 0) or 0) == 1
    assert int(caps.get('blue', 0) or 0) == 1
    assert int(caps.get('green', 0) or 0) == 0
    assert int(caps.get('yellow', 0) or 0) == 0


def test_rubix_surface_exposure_by_color_counts_open_air_above() -> None:
    s = MatchSession(enemy_style="rubix5")
    assert s.ai is not None
    ai = s.ai

    class _Blk:
        def __init__(self, color: str, *, is_garbage: bool = False, attack_state=None):
            self.color = color
            self.is_garbage = is_garbage
            self.attack_state = attack_state

    b = ai.board
    b.clear()

    # Stack in column 0:
    # y=HEIGHT-1 red (has air above?) yes if HEIGHT-2 empty
    # y=HEIGHT-2 red (above is empty at HEIGHT-3) yes
    # y=HEIGHT-3 blue (above is empty at HEIGHT-4) yes
    b.set_piece(0, b.HEIGHT - 1, _Blk('red'))
    b.set_piece(0, b.HEIGHT - 2, _Blk('red'))
    b.set_piece(0, b.HEIGHT - 3, _Blk('blue'))

    # Cover the topmost blue with a green above it => blue loses exposure.
    b.set_piece(0, b.HEIGHT - 4, _Blk('green'))

    # Garbage on top should not count.
    b.set_piece(1, b.HEIGHT - 1, _Blk('yellow'))
    b.set_piece(1, b.HEIGHT - 2, _Blk('yellow', is_garbage=True))

    exp = ai._count_surface_exposure_by_color(b)
    assert isinstance(exp, dict)
    # Column 0: red at HEIGHT-1 is covered by red above => not exposed.
    # red at HEIGHT-2 has blue above => not exposed.
    # blue at HEIGHT-3 has green above => not exposed.
    # green at HEIGHT-4 has empty above => exposed.
    assert int(exp.get('green', 0) or 0) == 1
    assert int(exp.get('red', 0) or 0) == 0
    assert int(exp.get('blue', 0) or 0) == 0
