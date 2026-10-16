"""attack_lifecycle.py - Shared inbound attack block lifecycle advancement.
(Moved from mechanics.attack_lifecycle to attacks.attack_lifecycle for better modular grouping.)
"""
from __future__ import annotations
from typing import Iterable, List, Optional, Dict, Protocol, runtime_checkable, Any, Callable
import os
import zlib

from swordfighting_new.util.debug import dprint

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

    def __init__(self, debug: bool = False, dwell_map: Optional[Dict[AttackState, int]] = None,
                 color_provider: Optional[Callable[..., Any]] = None,
                 board: Any | None = None,
                 seed: int | None = None):
        self._tracked = []  # type: List[AttackBlock]
        self.debug = debug
        self.dwell_map = dwell_map or {}  # type: Dict[AttackState, int]
        self._state_counters = {}  # type: Dict[int, int]
        # Optional provider that maps board (x,y) -> color string for this fighter's weapon pattern
        self.color_provider = color_provider
        # Optional board reference for computing per-turn sprinkle layers.
        self.board = board
        self._seed = self._resolve_seed(seed)

    @staticmethod
    def _resolve_seed(seed: int | None) -> int:
        if seed is not None:
            try:
                return int(seed)
            except Exception:
                return 0
        raw = os.getenv('BF_SEED')
        if raw is None or str(raw).strip() == '':
            return 0
        try:
            return int(str(raw).strip())
        except Exception:
            return 0

    def _deterministic_fallback_color(self, blk: AttackBlock) -> Any:
        """Deterministic fallback color when pattern/provider lookups aren't usable.

        This must NOT depend on Python's global RNG state. It derives a stable choice from
        inbound metadata (turn id/kind/layer/cluster id) and the optional BF_SEED.
        """
        try:
            from swordfighting_new.pieces.piece import Piece
            colors = list(getattr(Piece, 'COLORS', []) or [])
        except Exception:
            colors = []
        if not colors:
            return 'yellow'

        parts: list[str] = []
        try:
            kind = getattr(blk, 'inbound_kind', None)
            if kind is not None:
                parts.append(f"kind={str(kind)}")
        except Exception:
            pass

        for attr in ('inbound_turn_id', 'inbound_layer', 'strike_cluster_id', 'x', 'y'):
            try:
                v = getattr(blk, attr, None)
            except Exception:
                v = None
            if v is None:
                continue
            try:
                parts.append(f"{attr}={int(v)}")
            except Exception:
                parts.append(f"{attr}={str(v)}")

        # If we have no meaningful metadata, return a safe deterministic color.
        if not parts:
            return 'yellow'

        parts.append(f"seed={int(getattr(self, '_seed', 0) or 0)}")
        data = ('|'.join(parts)).encode('utf-8', errors='ignore')
        idx = int(zlib.crc32(data) & 0xFFFFFFFF) % int(len(colors))
        try:
            return colors[idx]
        except Exception:
            return 'yellow'

    def _call_color_provider(self, blk: AttackBlock) -> Any | None:
        """Call the injected provider with best available context.

        Supports providers with either:
        - provider(block)
        - provider(x, y)
        """
        if self.color_provider is None:
            return None
        try:
            return self.color_provider(blk)
        except TypeError:
            pass
        except Exception:
            return None
        try:
            x = int(getattr(blk, 'x'))
            y = int(getattr(blk, 'y'))
        except Exception:
            return None
        try:
            return self.color_provider(x, y)
        except Exception:
            return None

    def _compute_sprinkle_layer(self, blk: AttackBlock) -> int:
        """Compute 1-based sprinkle layer within the same inbound turn and column.

        PATTERN_MASTER: within one turn, layers alternate pattern rows 1/2 per column.
        """
        try:
            turn_id = getattr(blk, 'inbound_turn_id', None)
            kind = str(getattr(blk, 'inbound_kind', '') or '').strip().lower()
            x = int(getattr(blk, 'x'))
            y = int(getattr(blk, 'y'))
        except Exception:
            return 1

        if not turn_id or kind != 'sprinkle' or self.board is None:
            return 1

        ys: list[int] = []
        try:
            h = int(getattr(self.board, 'HEIGHT', 0) or 0)
        except Exception:
            h = 0
        if h <= 0:
            return 1

        for yy in range(h):
            cell = self.board.get_piece(int(x), int(yy))
            if cell in (None, getattr(self.board, 'EMPTY', None)):
                continue
            try:
                if getattr(cell, 'inbound_turn_id', None) != turn_id:
                    continue
                if str(getattr(cell, 'inbound_kind', '') or '').strip().lower() != 'sprinkle':
                    continue
                ys.append(int(getattr(cell, 'y', yy)))
            except Exception:
                continue

        if not ys:
            return 1

        # Bottom-most has the largest y.
        ys_sorted = sorted(set(ys), reverse=True)
        try:
            return int(ys_sorted.index(int(y)) + 1)
        except ValueError:
            return 1

    def register_new_locked(self, blocks: Iterable[AttackBlock]):
        for blk in blocks:
            if getattr(blk, 'attack_state', None):
                self._tracked.append(blk)
                blk_id = id(blk)
                st = getattr(blk, 'attack_state', None)
                if st and st in self.dwell_map:
                    self._state_counters[blk_id] = self.dwell_map[st]
                dprint(self.debug, f"[Lifecycle] track id={blk_id} state={getattr(blk,'attack_state',None)}")

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
                dprint(self.debug, f"[Lifecycle] id={blk_id} strike->sprinkle")
            elif st == 'sprinkle':
                blk.attack_state = 'cgarbage'
                blk.is_garbage = True
                # Pre-color cgarbage with its eventual pattern color so art matches
                try:
                    # Provide per-turn sprinkle layer context.
                    try:
                        if str(getattr(blk, 'inbound_kind', '') or '').strip().lower() == 'sprinkle':
                            setattr(blk, 'inbound_layer', int(self._compute_sprinkle_layer(blk)))
                    except Exception:
                        pass

                    # Prefer injected provider; fall back to global pattern.
                    c = self._call_color_provider(blk)
                    if c is not None:
                        blk.color = c
                    else:
                        if hasattr(blk, 'x') and hasattr(blk, 'y'):
                            from swordfighting_new.attacks.garbage_pattern import get_pattern_color
                            blk.color = get_pattern_color(int(getattr(blk, 'x')), int(getattr(blk, 'y')))
                except Exception:
                    # Leave existing color if pattern lookup fails
                    pass
                try:
                    dprint(self.debug, f"[Lifecycle] id={blk_id} sprinkle->cgarbage color={getattr(blk,'color',None)}")
                except Exception:
                    dprint(self.debug, f"[Lifecycle] id={blk_id} sprinkle->cgarbage")
            elif st == 'cgarbage':
                self._finalise(blk)
                dprint(self.debug, f"[Lifecycle] id={blk_id} cgarbage->normal color={blk.color}")
            if getattr(blk, 'attack_state', None):
                remaining.append(blk)
        self._tracked = remaining

    def _finalise(self, blk: AttackBlock):
        blk.attack_state = None
        blk.is_garbage = False
        blk.is_strike = False
        
        # Use pattern-based color assignment instead of random
        try:
            # Provide per-turn sprinkle layer context.
            if str(getattr(blk, 'inbound_kind', '') or '').strip().lower() == 'sprinkle':
                setattr(blk, 'inbound_layer', int(self._compute_sprinkle_layer(blk)))
        except Exception:
            pass

        try:
            c = self._call_color_provider(blk)
            if c is not None:
                blk.color = c
                return
        except Exception:
            pass

        if hasattr(blk, 'x') and hasattr(blk, 'y'):
            try:
                from swordfighting_new.attacks.garbage_pattern import get_pattern_color
                c = get_pattern_color(int(getattr(blk, 'x')), int(getattr(blk, 'y')))
                if c is not None and str(c) != '':
                    blk.color = c
                    return
            except Exception:
                pass

        # Fallback
        blk.color = self._deterministic_fallback_color(blk)

    def tracked_count(self) -> int:
        return len(self._tracked)

    def debug_snapshot(self):  # pragma: no cover
        return [(id(b), getattr(b, 'attack_state', None)) for b in self._tracked]
