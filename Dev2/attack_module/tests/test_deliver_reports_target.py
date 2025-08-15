import types

from utils.clock import FakeClock
from modules.attack_module.attack_manager import AttackManager
from modules.attack_module.attacks_service import AttacksService


class DummyBoard:
    def __init__(self, is_player_board):
        self.is_player_board = is_player_board
        self.test_mode = types.SimpleNamespace(pending_attacks={'player': [], 'enemy': []})


class DummyRenderer:
    pass


def test_deliver_returns_target_board_and_count(monkeypatch):
    # Create service with fake clock
    clock = FakeClock(0)
    mgr = AttackManager()
    svc = AttacksService(clock=clock, attack_manager=mgr)

    # Enqueue a simple attack by simulating a combo from player 1 -> target enemy(2)
    mgr.process_combo(broken_blocks=[(0,0,'r'),(1,0,'g'),(2,0,'b'),(3,0,'y')], is_cluster=True, combo_multiplier=1, player_id=1)

    # Advance time so it's ready
    clock.advance(1200)
    enemy_board = DummyBoard(is_player_board=False)
    res_enemy = svc.deliver(board=enemy_board, renderer=DummyRenderer())

    assert isinstance(res_enemy, dict)
    assert res_enemy["applied_to_board_id"] == 2
    assert res_enemy["payload_count"] >= 1
