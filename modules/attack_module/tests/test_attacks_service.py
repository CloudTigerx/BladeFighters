import types

from utils.clock import FakeClock
from modules.attack_module.attacks_service import AttacksService


class DummyAttackManager:
    def __init__(self):
        self.combos = []
        self.pending = {1: [], 2: []}
        self.time_args = []

    def process_combo(self, broken_blocks, is_cluster, combo_multiplier, player_id):
        self.combos.append((tuple(broken_blocks), bool(is_cluster), int(combo_multiplier), int(player_id)))
        # Very small emulation of outputs to drive service behavior
        target = 2 if player_id == 1 else 1
        # If any block has a color tuple implying cluster-ish, add a strike; else garbage
        if is_cluster:
            atk = types.SimpleNamespace(attack_type=types.SimpleNamespace(value='cluster_strike'), strike_pattern='2x4_vertical', strike_width=2, strike_height=4, strike_count=1, source_cluster=types.SimpleNamespace(combo_level=combo_multiplier))
            self.pending[target].append(atk)
        else:
            count = max(1, len(broken_blocks) // 2) * combo_multiplier
            atk = types.SimpleNamespace(attack_type=types.SimpleNamespace(value='garbage_blocks'), block_count=count)
            self.pending[target].append(atk)

    def get_pending_attacks(self, target_player: int):
        return list(self.pending.get(target_player, []))

    def pop_attacks_for_player(self, target_player: int):
        lst = list(self.pending.get(target_player, []))
        self.pending[target_player] = []
        return lst

    def update(self, current_time: float):
        # No delay logic for test; just echo structure
        self.time_args.append(current_time)
        return {'ready_attacks': {}}


def test_single_combo_garbage_payload_queueing():
    clock = FakeClock(0)
    mgr = DummyAttackManager()
    svc = AttacksService(clock=clock, attack_manager=mgr)

    broken = [(0, 0, 'red'), (1, 0, 'blue')]  # 2 cells -> floor(2/2)=1
    svc.on_combo(broken, is_cluster=False, chain_multiplier=1, player_id=1)

    payloads = svc.queue_payloads(board_id=2)
    assert payloads, 'Expected payloads for enemy board'
    assert payloads[0].kind == 'garbage'
    assert payloads[0].count >= 1


def test_chain_combo_multiple_payloads_order():
    clock = FakeClock(0)
    mgr = DummyAttackManager()
    svc = AttacksService(clock=clock, attack_manager=mgr)

    # Two consecutive combos with increasing multiplier
    svc.on_combo([(0, 0, 'r'), (1, 0, 'b')], is_cluster=False, chain_multiplier=1, player_id=1)
    svc.on_combo([(2, 0, 'g'), (3, 0, 'y')], is_cluster=False, chain_multiplier=2, player_id=1)

    payloads = svc.queue_payloads(board_id=2)
    assert len(payloads) >= 2
    # Order preserved: first smaller, then larger garbage
    assert payloads[0].count <= payloads[1].count


def test_cluster_strike_pattern_passthrough():
    clock = FakeClock(0)
    mgr = DummyAttackManager()
    svc = AttacksService(clock=clock, attack_manager=mgr)

    broken = [(0, 0, 'r'), (1, 0, 'r'), (0, 1, 'r'), (1, 1, 'r')]  # looks like 2x2
    svc.on_combo(broken, is_cluster=True, chain_multiplier=3, player_id=1)

    payloads = svc.queue_payloads(board_id=2)
    strike = next(p for p in payloads if p.kind == 'strike')
    assert strike.pattern in ('2x4_vertical', '2x4_vertical')
    assert strike.count >= 1

