"""Simplified inbound attack lifecycle helper.

Central place to advance block.attack_state sequence:
    strike -> sprinkle -> cgarbage -> (normal piece)

Call advance() once per piece-lock event. Register newly locked inbound
attack blocks (those with a non-None attack_state) via register_new_locked.
"""
from typing import Iterable
import random

class InboundAttackLifecycle:
    def __init__(self, debug: bool = False):
        self._tracked = []  # list[Block]
        self.debug = debug

    def register_new_locked(self, blocks: Iterable[object]):
        for b in blocks:
            if getattr(b, 'attack_state', None):
                self._tracked.append(b)
                if self.debug:
                    print(f"[Lifecycle] track id={id(b)} state={getattr(b,'attack_state',None)}")

    def advance(self):
        if not self._tracked:
            return
        remaining = []
        for b in self._tracked:
            st = getattr(b, 'attack_state', None)
            if st == 'strike':
                b.attack_state = 'sprinkle'
                b.is_strike = False
                if self.debug: print(f"[Lifecycle] id={id(b)} strike->sprinkle")
            elif st == 'sprinkle':
                b.attack_state = 'cgarbage'
                b.is_garbage = True
                if self.debug: print(f"[Lifecycle] id={id(b)} sprinkle->cgarbage")
            elif st == 'cgarbage':
                b.attack_state = None
                b.is_garbage = False
                b.is_strike = False
                # assign normal color
                try:
                    from swordfighting_new.pieces.piece import Piece
                    b.color = random.choice(Piece.COLORS)
                except Exception:
                    b.color = 'red'
                if self.debug: print(f"[Lifecycle] id={id(b)} cgarbage->normal {b.color}")
            if getattr(b, 'attack_state', None):
                remaining.append(b)
        self._tracked = remaining

    def tracked_count(self):
        return len(self._tracked)
