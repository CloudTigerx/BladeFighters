import pytest


def test_bot_battle_session_constructs_and_ticks():
    from swordfighting_new.session import BotBattleSession

    s = BotBattleSession(bot_a_style='rubix3', bot_b_style='rubix4', seed=123)
    assert getattr(s, 'enemy_has_board', True) is True
    assert getattr(s, 'accepts_player_input', True) is False

    snap0 = s.snapshot()
    assert snap0['player']['board'] is not None
    assert snap0['ai']['board'] is not None

    # Tick a few frames to ensure both bots advance without errors.
    for _ in range(30):
        s.update({})

    snap = s.snapshot()
    assert 'scoring' in snap
    assert snap['frame'] >= 30
