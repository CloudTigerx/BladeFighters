"""
Attack Service - Coordinates attack generation and delivery
Provides a high-level interface for processing combos and delivering attacks.
"""

import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from .attack_manager import AttackManager
from .data_structures import ComboData
from ..logging_module.error_handler import (
    safe_operation,
    log_and_continue
)
from ..logging_module.logger import get_logger

logger = get_logger(__name__)


@dataclass
class Payload:
    """Lightweight payload descriptor for external consumption."""
    kind: str  # 'garbage' or 'strike'
    count: int
    pattern: Optional[str]  # For strikes: "1x4", "2x2", etc.
    color: Optional[str]  # For garbage: color name
    target_board: int


class AttacksService:
    """
    High-level service for coordinating attack generation and delivery.
    Handles combo processing, attack queuing, and delivery to game boards.
    """

    def __init__(self, clock=None, attack_manager=None, item_system=None, settings=None):
        self.clock = clock
        self.attack_manager = attack_manager or AttackManager()
        self.item_system = item_system
        self.settings = settings
        self._recent_break_sigs: Dict[str, int] = {}

    def process_combo(
        self,
        broken_blocks: List[str],
        is_cluster: bool = False,
        chain_multiplier: int = 1,
        player_id: int = 1,
    ) -> None:
        """Process a combo and generate attacks."""
        # Deduplicate rapid-fire combos (anti-spam)
        try:
            now_ms = int(self.clock.now_ms()) if self.clock else int(time.time() * 1000)
            sig = f"{player_id}_{len(broken_blocks)}_{is_cluster}_{chain_multiplier}"
            last = self._recent_break_sigs.get(sig)
            if last is not None and (now_ms - last) < 300:
                return
            self._recent_break_sigs[sig] = now_ms
            # prune old
            for k, ts in list(self._recent_break_sigs.items()):
                if now_ms - ts > 1000:
                    self._recent_break_sigs.pop(k, None)
        except Exception as e:
            logger.warning(f"Failed to process combo deduplication: {str(e)}")

        # Normalize and forward to AttackManager; manager handles detection details
        self.attack_manager.process_combo(
            broken_blocks=broken_blocks,
            is_cluster=bool(is_cluster),
            combo_multiplier=int(max(1, chain_multiplier)),
            player_id=int(player_id),
        )

    def on_combo(
        self,
        broken_blocks: List[str],
        is_cluster: bool = False,
        combo_multiplier: int = 1,
        player_id: int = 1,
    ) -> None:
        """Backward compatibility method for on_combo calls."""
        self.process_combo(
            broken_blocks=broken_blocks,
            is_cluster=is_cluster,
            chain_multiplier=combo_multiplier,
            player_id=player_id,
        )

    # For modes that need raw queued payload descriptors
    def queue_payloads(self, board_id: int) -> List[Payload]:
        """Convert internal payloads to lightweight DTOs."""
        # Convert internal payloads to lightweight DTOs; this keeps tests decoupled
        target_player = int(board_id)
        internal = self.attack_manager.get_pending_attacks(target_player=target_player)
        result: List[Payload] = []
        
        for atk in internal:
            payload = self._convert_attack_to_payload(atk, target_player)
            if payload:
                result.append(payload)
                
        return result

    @safe_operation("convert attack to payload", None, "WARNING")
    def _convert_attack_to_payload(self, atk, target_player: int) -> Optional[Payload]:
        """Convert an internal attack to a payload DTO."""
        try:
            a_type = getattr(atk, 'attack_type', None)
            a_val = a_type.value if a_type is not None else None
            
            if a_val == 'garbage_blocks':
                return Payload(
                    kind='garbage', 
                    count=int(getattr(atk, 'block_count', 0)), 
                    pattern=None, 
                    color=None, 
                    target_board=target_player
                )
            elif a_val == 'cluster_strike':
                patt = getattr(atk, 'strike_pattern', None)
                w = int(getattr(atk, 'strike_width', 1) or 1)
                h = int(getattr(atk, 'strike_height', 1) or 1)
                # Use WxH naming for placement compatibility if detailed pattern is missing
                norm = patt or f"{w}x{h}"
                cnt = int(getattr(atk, 'strike_count', 1) or 1) * max(1, w * h)
                return Payload(
                    kind='strike', 
                    count=cnt, 
                    pattern=norm, 
                    color=None, 
                    target_board=target_player
                )
        except Exception as e:
            logger.warning(f"Failed to convert attack to payload: {str(e)}")
        return None

    # Deliver to a specific board via the mode's renderer/placement rules
    def deliver(self, *, board, renderer) -> Dict[str, Any]:
        """Deliver attacks to a specific board."""
        # Determine which side this board is (expects attributes set by TestMode)
        # Fall back to player if unsure
        is_player = self._determine_board_side(board)

        # AttackManager queues are for target players 1 and 2; map to 'player'/'enemy'
        side_key = 'player' if is_player else 'enemy'

        # Get ready attacks from the current state
        target_player = 1 if is_player else 2
        
        # Get ready attacks from the current state (legacy path)
        # Check if attacks are already in ready_attacks from a previous update
        ready = getattr(self.attack_manager, '_last_ready_attacks', {})
        attacks = ready.get('player1' if target_player == 1 else 'player2', [])
        
        # If no ready attacks, try to process the queue
        if not attacks:
            now_ms = int(self.clock.now_ms())
            update_result = self.attack_manager.update(current_time=now_ms / 1000.0)
            ready = update_result.get('ready_attacks', {})
            attacks = ready.get('player1' if target_player == 1 else 'player2', [])
        if not attacks:
            return {"applied_to_board_id": None, "payload_count": 0}

        # Aggregate for legacy placement behavior
        total_garbage = 0
        strike_details = []
        pierce_budgets = []
        total_strike_blocks = 0

        # Process attacks with error handling
        attack_summary = self._process_attacks(attacks)
        total_garbage = attack_summary['total_garbage']
        strike_details = attack_summary['strike_details']
        pierce_budgets = attack_summary['pierce_budgets']
        total_strike_blocks = attack_summary['total_strike_blocks']

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

        target_key = side_key
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

    def deliver_with_ready_attacks(self, *, board, renderer, ready_attacks: Dict[str, List]) -> Dict[str, Any]:
        """Deliver attacks using pre-computed ready attacks."""
        # Determine which side this board is (expects attributes set by TestMode)
        # Fall back to player if unsure
        try:
            is_player = getattr(board, 'is_player_board', True)
        except Exception:
            is_player = True

        # AttackManager queues are for target players 1 and 2; map to 'player'/'enemy'
        side_key = 'player' if is_player else 'enemy'

        # Get ready attacks for this target
        target_player = 1 if is_player else 2
        attacks = ready_attacks.get('player1' if target_player == 1 else 'player2', [])
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
                strike_details.append({'width': w, 'height': h})
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

        target_key = side_key
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

    @safe_operation("determine board side", True, "WARNING")
    def _determine_board_side(self, board) -> bool:
        """Determine if the board is a player board."""
        try:
            return getattr(board, 'is_player_board', True)
        except Exception as e:
            logger.warning(f"Failed to determine board side: {str(e)}")
            return True

    @safe_operation("process attacks", {
        'total_garbage': 0,
        'strike_details': [],
        'pierce_budgets': [],
        'total_strike_blocks': 0
    }, "WARNING")
    def _process_attacks(self, attacks) -> Dict[str, Any]:
        """Process attacks and return summary statistics."""
        total_garbage = 0
        strike_details = []
        pierce_budgets = []
        total_strike_blocks = 0

        try:
            for atk in attacks:
                a_type = getattr(atk, 'attack_type', None)
                a_val = a_type.value if a_type is not None else None
                if a_val == 'garbage_blocks':
                    block_count = int(getattr(atk, 'block_count', 0))
                    total_garbage += block_count
                elif a_val == 'cluster_strike':
                    w = int(getattr(atk, 'strike_width', 1) or 1)
                    h = int(getattr(atk, 'strike_height', 1) or 1)
                    strike_details.append(f"{w}x{h}")
                    combo = self._extract_combo_level(atk)
                    pierce_budgets.append(combo)
                    total_strike_blocks += w * h
        except Exception as e:
            logger.warning(f"Failed to process attacks: {str(e)}")

        return {
            'total_garbage': total_garbage,
            'strike_details': strike_details,
            'pierce_budgets': pierce_budgets,
            'total_strike_blocks': total_strike_blocks
        }

    @safe_operation("extract combo level", 1, "WARNING")
    def _extract_combo_level(self, atk) -> int:
        """Extract combo level from attack."""
        try:
            if getattr(atk, 'source_cluster', None):
                return max(1, int(getattr(atk.source_cluster, 'combo_level', 1)))
        except Exception as e:
            logger.warning(f"Failed to extract combo level: {str(e)}")
        return 1

