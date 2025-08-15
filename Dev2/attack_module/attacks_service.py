"""
AttacksService Facade

Centralizes attack flow and timing outside the reactor. This service:
- Receives combo callbacks from the reactor
- Delegates to AttackManager for calculations/queueing
- Applies placement policies and triggers visuals/SFX via TestMode's existing
  board/renderer integration paths

This module must not import reactor modules. It depends on:
- modules.attack_module.attack_manager.AttackManager
- modules.items_module.* (for item effects)
- utils.clock.Clock
- settings/config modules
"""

from typing import List, Optional, Dict, Any

from .attack_manager import AttackManager
from .data_structures import Payload


class AttacksService:
    def __init__(self, *, clock, attack_manager: Optional[AttackManager] = None, item_system=None, settings=None):
        self.clock = clock
        self.attack_manager = attack_manager or AttackManager()
        self.item_system = item_system
        self.settings = settings
        # Optional external placement/demotion policies
        self._policies = None
        # Dedupe recent combo events to preserve legacy behavior
        self._recent_break_sigs: Dict[Any, int] = {}

    # Reactor callback boundary
    def on_combo(self, broken_blocks, is_cluster: bool, chain_multiplier: int, player_id: int = 1) -> None:
        # Defensive dedupe: avoid duplicate callbacks within a short window
        now_ms = int(self.clock.now_ms())
        try:
            sig = (int(player_id), tuple(sorted((int(x), int(y)) for x, y, _ in broken_blocks)), int(chain_multiplier))
            last = self._recent_break_sigs.get(sig)
            if last is not None and (now_ms - last) < 300:
                return
            self._recent_break_sigs[sig] = now_ms
            # prune old
            for k, ts in list(self._recent_break_sigs.items()):
                if now_ms - ts > 1000:
                    self._recent_break_sigs.pop(k, None)
        except Exception:
            pass

        # Normalize and forward to AttackManager; manager handles detection details
        self.attack_manager.process_combo(
            broken_blocks=broken_blocks,
            is_cluster=bool(is_cluster),
            combo_multiplier=int(max(1, chain_multiplier)),
            player_id=int(player_id),
        )

    # For modes that need raw queued payload descriptors
    def queue_payloads(self, board_id: int) -> List[Payload]:
        # Convert internal payloads to lightweight DTOs; this keeps tests decoupled
        target_player = int(board_id)
        internal = self.attack_manager.get_pending_attacks(target_player=target_player)
        result: List[Payload] = []
        for atk in internal:
            a_type = getattr(atk, 'attack_type', None)
            a_val = a_type.value if a_type is not None else None
            if a_val == 'garbage_blocks':
                result.append(Payload(kind='garbage', count=int(getattr(atk, 'block_count', 0)), pattern=None, color=None, target_board=target_player))
            elif a_val == 'cluster_strike':
                patt = getattr(atk, 'strike_pattern', None)
                w = int(getattr(atk, 'strike_width', 1) or 1)
                h = int(getattr(atk, 'strike_height', 1) or 1)
                # Use WxH naming for placement compatibility if detailed pattern is missing
                norm = patt or f"{w}x{h}"
                cnt = int(getattr(atk, 'strike_count', 1) or 1) * max(1, w * h)
                result.append(Payload(kind='strike', count=cnt, pattern=norm, color=None, target_board=target_player))
        return result

    # Deliver to a specific board via the mode's renderer/placement rules
    def deliver(self, *, board, renderer) -> Dict[str, Any]:
        now_ms = int(self.clock.now_ms())
        ready = self.attack_manager.update(current_time=now_ms / 1000.0).get('ready_attacks', {})

        # Determine which side this board is (expects attributes set by TestMode)
        # Fall back to player if unsure
        try:
            is_player = getattr(board, 'is_player_board', True)
        except Exception:
            is_player = True

        # AttackManager queues are for target players 1 and 2; map to 'player'/'enemy'
        side_key = 'player' if is_player else 'enemy'

        # Pull the exact attacks for this side and translate to TestMode's spawning API
        attacks = self.attack_manager.pop_attacks_for_player(target_player=1 if is_player else 2)
        if not attacks:
            return {"applied_to_board_id": None, "payload_count": 0}

        # Aggregate for legacy placement behavior
        total_garbage = 0
        strike_details = []
        pierce_budgets = []
        total_strike_blocks = 0

        for atk in attacks:
            a_type = getattr(atk, 'attack_type', None)
            a_val = a_type.value if a_type is not None else None
            if a_val == 'garbage_blocks':
                total_garbage += int(getattr(atk, 'block_count', 0))
            elif a_val == 'cluster_strike':
                w = int(getattr(atk, 'strike_width', 1) or 1)
                h = int(getattr(atk, 'strike_height', 1) or 1)
                strike_details.append(f"{w}x{h}")
                combo = 1
                try:
                    if getattr(atk, 'source_cluster', None):
                        combo = max(1, int(getattr(atk.source_cluster, 'combo_level', 1)))
                except Exception:
                    pass
                pierce_budgets.append(combo)
                total_strike_blocks += w * h

        # Use TestMode's existing queue/spawn methods if present
        mode = getattr(board, 'test_mode', None)
        if mode is None:
            # If board is a raw engine without mode backref, we cannot place
            return {"applied_to_board_id": (1 if is_player else 2), "payload_count": len(attacks)}

        # Spawn mode switch (default: animated)
        spawn_mode = None
        try:
            cfg = getattr(self.settings, 'config', self.settings)
            if cfg and hasattr(cfg, 'get'):
                spawn_mode = cfg.get('attacks.spawn_mode', 'animated')
        except Exception:
            spawn_mode = 'animated'
        spawn_mode = (str(spawn_mode).strip().lower() if spawn_mode else 'animated')

        target_key = ('enemy' if side_key == 'enemy' else 'player')
        if hasattr(mode, 'queue_attack_spawn') and spawn_mode == 'animated':
            # Animated path: enqueue DTO-like spawn events; no grid mutation here
            if total_garbage > 0:
                try:
                    mode.queue_attack_spawn(target_key, 'garbage', total_garbage)
                    if hasattr(mode, 'attack_tracker'):
                        mode.attack_tracker.track_queued(side_key, 'garbage', total_garbage)
                except Exception:
                    pass
            if strike_details:
                try:
                    mode.queue_attack_spawn(target_key, 'strike', total_strike_blocks, strike_details)
                    # Attach pierce budgets if supported by pending queue
                    try:
                        pending = mode.pending_attacks[target_key]
                        if pending:
                            pending[-1]['pierce_budgets'] = pierce_budgets
                    except Exception:
                        pass
                    if hasattr(mode, 'attack_tracker'):
                        mode.attack_tracker.track_queued(side_key, 'strike', total_strike_blocks)
                except Exception:
                    pass
        else:
            # Instant path: legacy direct placement via mode's existing immediate placement logic
            # For tests/tools only. Defer to mode.update_attack_spawning immediate branch.
            if total_garbage > 0 and hasattr(mode, 'queue_attack_spawn'):
                mode.queue_attack_spawn(target_key, 'garbage', total_garbage)
                if hasattr(mode, 'attack_tracker'):
                    mode.attack_tracker.track_queued(side_key, 'garbage', total_garbage)
            if strike_details and hasattr(mode, 'queue_attack_spawn'):
                mode.queue_attack_spawn(target_key, 'strike', total_strike_blocks, strike_details)
                try:
                    pending = mode.pending_attacks[target_key]
                    if pending:
                        pending[-1]['pierce_budgets'] = pierce_budgets
                except Exception:
                    pass

        # Do not set any global pauses here; caller decides per-board locks

        return {"applied_to_board_id": (1 if is_player else 2), "payload_count": len(attacks)}

    def set_policies(self, policies) -> None:
        self._policies = policies

