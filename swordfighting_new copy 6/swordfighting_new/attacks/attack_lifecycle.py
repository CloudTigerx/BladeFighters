"""attack_lifecycle.py - Shared inbound attack block lifecycle advancement.
(Moved from mechanics.attack_lifecycle to attacks.attack_lifecycle for better modular grouping.)
"""
from __future__ import annotations
from typing import Iterable, List, Optional, Dict, Protocol, runtime_checkable, Any
import random

@runtime_checkable
class AttackBlock(Protocol):  # minimal structural typing for lifecycle
    attack_state: Optional[str]
    is_strike: bool
    is_garbage: bool
    color: Any
    ...

AttackState = str  # alias for readability

class InboundAttackLifecycle:
    STATE_ORDER = ["strike", "sprinkle", "cgarbage"]  # final -> normal

    def __init__(self, debug: bool = False, dwell_map: Optional[Dict[AttackState, int]] = None):
        self._tracked = []  # type: List[AttackBlock]
        self.debug = debug
        self.dwell_map = dwell_map or {}  # type: Dict[AttackState, int]
        self._state_counters = {}  # type: Dict[int, int]

    def register_new_locked(self, blocks: Iterable[AttackBlock]):
        for blk in blocks:
            if getattr(blk, 'attack_state', None):
                self._tracked.append(blk)
                blk_id = id(blk)
                st = getattr(blk, 'attack_state', None)
                if st and st in self.dwell_map:
                    self._state_counters[blk_id] = self.dwell_map[st]
                if self.debug:
                    print(f"[Lifecycle] track id={blk_id} state={getattr(blk,'attack_state',None)}")

    def advance(self):
        if not self._tracked:
            return
        remaining = []
        for blk in self._tracked:
            blk_id = id(blk)
            st = getattr(blk, 'attack_state', None)
            if not st:
                continue
            if blk_id in self._state_counters:
                self._state_counters[blk_id] -= 1
                if self._state_counters[blk_id] > 0:
                    remaining.append(blk)
                    continue
                else:
                    self._state_counters.pop(blk_id, None)
            if st == 'strike':
                blk.attack_state = 'sprinkle'
                blk.is_strike = False
                if self.debug:
                    print(f"[Lifecycle] id={blk_id} strike->sprinkle")
            elif st == 'sprinkle':
                blk.attack_state = 'cgarbage'
                blk.is_garbage = True
                if self.debug:
                    print(f"[Lifecycle] id={blk_id} sprinkle->cgarbage")
            elif st == 'cgarbage':
                self._finalise(blk)
                if self.debug:
                    print(f"[Lifecycle] id={blk_id} cgarbage->normal color={blk.color}")
            if getattr(blk, 'attack_state', None):
                remaining.append(blk)
        self._tracked = remaining

    def _finalise(self, blk: AttackBlock):
        blk.attack_state = None
        blk.is_garbage = False
        blk.is_strike = False
        if not getattr(blk, 'color', None):
            try:
                from swordfighting_new.pieces.piece import Piece
                blk.color = random.choice(Piece.COLORS)
            except Exception:
                blk.color = 'white'
        else:
            try:
                from swordfighting_new.pieces.piece import Piece
                blk.color = random.choice(Piece.COLORS)
            except Exception:
                pass

    def tracked_count(self) -> int:
        return len(self._tracked)

    def debug_snapshot(self):  # pragma: no cover
        return [(id(b), getattr(b, 'attack_state', None)) for b in self._tracked]
