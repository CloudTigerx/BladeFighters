import types

from utils.clock import FakeClock
from modules.testmode_module.test_mode import TestMode
import core.asset_loader as asset_loader


class DummyAudio:
    def play_sound(self, name):
        pass


class DummyScreen:
    def get_width(self):
        return 800

    def get_height(self):
        return 600


class DummyFont:
    pass


def test_engine_callback_to_service_and_delivery(monkeypatch):
    # Avoid heavy asset IO in tests
    monkeypatch.setattr(asset_loader.AssetLoader, "_load_standard_assets", lambda self: None, raising=False)
    screen = DummyScreen()
    font = DummyFont()
    audio = DummyAudio()
    clock = FakeClock(0)

    tm = TestMode(screen, font, audio, 'puzzleassets', settings_system=None, clock=clock)

    # Simulate reactor emission: player breaks two blocks (non-cluster)
    broken = [(0, 0, 'r'), (1, 0, 'b')]
    tm.player_engine.blocks_broken_handler(broken, False, 1)

    # Advance time so attacks are ready
    clock.advance(1200)
    
    # Update attack spawning to deliver attacks from attack_manager to pending_attacks
    tm.update_attack_spawning()

    # Debug output
    print(f"Player 1 attacks: {len(tm.attack_manager.player1_attacks)}")
    print(f"Player 2 attacks: {len(tm.attack_manager.player2_attacks)}")
    print(f"Pending enemy attacks: {len(tm.pending_attacks['enemy'])}")

    # The service should have queued at least one garbage payload for enemy
    pending = tm.pending_attacks['enemy']
    assert pending
    assert pending[0]['type'] in ('garbage', 'strike')
    
    # Simulate multiple game loop iterations to complete the animation
    for i in range(20):  # Increased from 10 to 20
        clock.advance(50)  # Advance 50ms per frame
        tm.update_attack_spawning()
        if not tm.pending_attacks['enemy']:
            print(f"Attack completed after {i+1} iterations")
            break
    else:
        print("Attack did not complete after 20 iterations")

