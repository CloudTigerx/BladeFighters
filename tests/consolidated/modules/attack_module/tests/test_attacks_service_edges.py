import types

from utils.clock import FakeClock
from modules.attack_module.attacks_service import AttacksService


class DummyAttackManager:
    def __init__(self):
        self.combos = []
        self.pending = {1: [], 2: []}
        self.time_args = []

    def process_combo(self, broken_blocks, is_cluster, combo_multiplier, player_id):
        # Capture exactly what service forwards
        self.combos.append((tuple(broken_blocks), is_cluster, combo_multiplier, player_id))
        # Minimal emulation of outputs to drive service behavior
        target = 2 if player_id == 1 else 1
        if is_cluster:
            atk = types.SimpleNamespace(
                attack_type=types.SimpleNamespace(value='cluster_strike'),
                strike_pattern='2x4_vertical',
                strike_width=2,
                strike_height=4,
                strike_count=1,
                source_cluster=types.SimpleNamespace(combo_level=combo_multiplier),
            )
            self.pending[target].append(atk)
        else:
            count = max(1, len(broken_blocks) // 2) * combo_multiplier
            atk = types.SimpleNamespace(
                attack_type=types.SimpleNamespace(value='garbage_blocks'),
                block_count=count,
            )
            self.pending[target].append(atk)

    def get_pending_attacks(self, target_player: int):
        return list(self.pending.get(target_player, []))

    def pop_attacks_for_player(self, target_player: int):
        lst = list(self.pending.get(target_player, []))
        self.pending[target_player] = []
        return lst

    def update(self, current_time: float):
        self.time_args.append(current_time)
        return {'ready_attacks': {}}


def test_no_duplicate_events_within_window():
    # Two identical combos inside dedupe window → only one payload
    clock = FakeClock(0)
    mgr = DummyAttackManager()
    svc = AttacksService(clock=clock, attack_manager=mgr)

    broken = [(0, 0, 'r'), (1, 0, 'b')]
    svc.on_combo(broken, is_cluster=False, chain_multiplier=1, player_id=1)
    clock.advance(100)  # < 300ms dedupe window
    svc.on_combo(broken, is_cluster=False, chain_multiplier=1, player_id=1)

    payloads = svc.queue_payloads(board_id=2)
    assert len(payloads) == 1
    assert payloads[0].kind == 'garbage'


def test_legit_rapid_combos_not_deduped():
    # Different broken sets within window → both preserved
    clock = FakeClock(0)
    mgr = DummyAttackManager()
    svc = AttacksService(clock=clock, attack_manager=mgr)

    broken_a = [(0, 0, 'r'), (1, 0, 'b')]
    broken_b = [(2, 0, 'g'), (3, 0, 'y')]  # different coordinates
    svc.on_combo(broken_a, is_cluster=False, chain_multiplier=1, player_id=1)
    clock.advance(50)
    svc.on_combo(broken_b, is_cluster=False, chain_multiplier=1, player_id=1)

    payloads = svc.queue_payloads(board_id=2)
    assert len(payloads) == 2
    # Also verify difference via counts (same size → same count); order should be FIFO
    assert payloads[0].count == payloads[1].count


def test_legit_rapid_combos_different_chain_preserved():
    # Same broken set but different chain_multiplier within window → both preserved
    clock = FakeClock(0)
    mgr = DummyAttackManager()
    svc = AttacksService(clock=clock, attack_manager=mgr)

    broken = [(0, 0, 'r'), (1, 0, 'b')]
    svc.on_combo(broken, is_cluster=False, chain_multiplier=1, player_id=1)
    clock.advance(20)
    svc.on_combo(broken, is_cluster=False, chain_multiplier=2, player_id=1)

    payloads = svc.queue_payloads(board_id=2)
    assert len(payloads) == 2
    # Increasing chain → increasing count
    assert [p.count for p in payloads] == [1, 2]


def test_fifo_ordering_with_increasing_chain():
    # Three combos with increasing multipliers; ensure FIFO queue order
    clock = FakeClock(0)
    mgr = DummyAttackManager()
    svc = AttacksService(clock=clock, attack_manager=mgr)

    broken = [(0, 0, 'r'), (1, 0, 'b')]  # floor(2/2)=1 base
    svc.on_combo(broken, is_cluster=False, chain_multiplier=1, player_id=1)
    clock.advance(1)
    svc.on_combo(broken, is_cluster=False, chain_multiplier=2, player_id=1)
    clock.advance(1)
    svc.on_combo(broken, is_cluster=False, chain_multiplier=3, player_id=1)

    payloads = svc.queue_payloads(board_id=2)
    assert [p.count for p in payloads] == [1, 2, 3]


def test_irregular_timestamps_preserve_call_order():
    # Irregular advances: 0 → 37 → 38 → 120ms; ensure call order dictates queue order
    clock = FakeClock(0)
    mgr = DummyAttackManager()
    svc = AttacksService(clock=clock, attack_manager=mgr)

    broken = [(0, 0, 'r'), (1, 0, 'b')]
    svc.on_combo(broken, is_cluster=False, chain_multiplier=1, player_id=1)  # t=0
    clock.advance(37)
    svc.on_combo(broken, is_cluster=False, chain_multiplier=2, player_id=1)  # t=37
    clock.advance(1)
    svc.on_combo(broken, is_cluster=False, chain_multiplier=3, player_id=1)  # t=38
    clock.advance(82)
    svc.on_combo(broken, is_cluster=False, chain_multiplier=4, player_id=1)  # t=120

    payloads = svc.queue_payloads(board_id=2)
    assert [p.count for p in payloads] == [1, 2, 3, 4]


def test_service_transparency_to_manager_inputs():
    # The service should forward args without mutating the inputs
    clock = FakeClock(0)
    mgr = DummyAttackManager()
    svc = AttacksService(clock=clock, attack_manager=mgr)

    broken = [(2, 1, 'g'), (0, 0, 'r'), (1, 0, 'b')]  # deliberately unsorted
    svc.on_combo(broken, is_cluster=True, chain_multiplier=2, player_id=2)

    # Verify manager received exactly what was passed (no reordering/mutation)
    assert mgr.combos, 'Manager should have received a combo call'
    forwarded = mgr.combos[-1]
    assert forwarded == (tuple(broken), True, 2, 2)

    # Also ensure the produced strike DTO reflects the manager output, not mutated
    payloads = svc.queue_payloads(board_id=1)  # player 2 targets board 1
    assert any(p.kind == 'strike' for p in payloads)

