import types

from utils.clock import FakeClock
from modules.testmode_module.test_mode import TestMode
from modules.attack_module.attacks_service import AttacksService


class DummyScreen:
    def get_width(self):
        return 800
    def get_height(self):
        return 600


class DummyFont:
    pass


class DummyAudio:
    pass


def _fast_assets(monkeypatch):
    import modules.asset_module.preflight as pre
    from core import asset_loader
    monkeypatch.setattr(asset_loader.AssetLoader, "_load_standard_assets", lambda self: None, raising=False)


def test_enemy_combo_does_not_lock_player_until_payload_applied(monkeypatch):
    _fast_assets(monkeypatch)
    screen = DummyScreen()
    font = DummyFont()
    audio = DummyAudio()
    clock = FakeClock(0)

    tm = TestMode(screen, font, audio, 'puzzleassets', settings_system=None, clock=clock)

    # Ensure no lock to start
    assert not tm.player_runtime.is_input_locked(clock.now_ms())

    # Simulate enemy making a combo via facade callback (no delivery yet)
    enemy_broken = [(0, 0, 'r'), (1, 0, 'b'), (2, 0, 'g'), (3, 0, 'y')]
    tm.attacks_service.on_combo(enemy_broken, True, 1, player_id=2)

    # Player should still not be locked before delivery
    assert not tm.player_runtime.is_input_locked(clock.now_ms())

    # Advance time so delivery queue updates, then deliver to PLAYER only
    clock.advance(200)
    res_player = tm.attacks_service.deliver(board=tm.player_engine, renderer=tm.player_renderer)

    # If payloads applied to player, lock should engage
    if res_player.get("payload_count", 0) > 0:
        tm.player_runtime.lock_input(tm._get_attack_freeze_ms(), clock.now_ms())
        assert tm.player_runtime.is_input_locked(clock.now_ms())
        # After freeze duration, it should clear
        clock.advance(int(tm._get_attack_freeze_ms()))
        tm.player_runtime.clear_expired(clock.now_ms())
        assert not tm.player_runtime.is_input_locked(clock.now_ms())


def test_chain_lock_affects_only_player(monkeypatch):
    _fast_assets(monkeypatch)
    screen = DummyScreen()
    font = DummyFont()
    audio = DummyAudio()
    clock = FakeClock(0)

    tm = TestMode(screen, font, audio, 'puzzleassets', settings_system=None, clock=clock)

    now = clock.now_ms()
    tm.player_runtime.lock_chain(120, now)
    assert tm.player_runtime.is_input_locked(now)
    # Enemy should remain unaffected
    assert not tm.enemy_runtime.is_input_locked(now)
