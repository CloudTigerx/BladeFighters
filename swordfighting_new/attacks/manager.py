"""Attack generation & queue management.

This module centralizes how breaker pass statistics are translated into
scheduled outbound attacks. Design goals:

 - Modularity: stats-to-attack formulas live here (isolated from rendering,
   AI, breaker resolution) making tuning simpler.
 - Extensibility: future attack kinds (e.g. "combo", "special") can register
   new generator functions without touching callers.
 - Testability: pure functions / small methods for formula logic.

Attack Kinds:
 - Sprinkle: Derived from *non-rectangle* single clears ("sprinkles"). Formula
     (restored original): floor(group_size / 2) * combo_index.
 - Strike: Each cleared rectangle (cluster) yields a strike. Uses original
     Blade Fighters formulas from design docs (vertical vs horizontal swords).

Pass Stats Contract (input dict per chain pass):
    {
        'sprinkles': int,               # count of singles not part of any rectangle
        'rectangles': [                 # list of rectangle dicts
            {'width': int, 'height': int, 'size': int, ...},
            ...
        ]
    }
Other keys are ignored.
"""
from __future__ import annotations
from typing import Iterable, List, Dict, Callable, Any
import inspect

from swordfighting_new.util.debug import dprint, env_flag

from .types import Attack, AttackKind, DEFAULT_ATTACK_DELAY

SprinkleFormula = Callable[[int, int], int]  # (sprinkles, chain_index) -> amount
StrikeFormula = Callable[..., Dict]   # (rectangle_stats, chain_index[, board_w, board_h]) -> info dict


def default_sprinkle_formula(sprinkles: int, chain_index: int) -> int:
    """Calculate sprinkle attack strength using original Blade Fighters formula.

    This is called once per combo step, where:
    - sprinkles = number of individual blocks cleared in this step
    - chain_index = 1-based combo multiplier (1st combo, 2nd combo, etc.)

    Original formula from docs: floor(group_size / 2) * combo_index
    """
    if sprinkles <= 0:
        return 0

    # Original formula: floor(sprinkles / 2) * chain_index
    base = sprinkles // 2  # floor division
    return max(base * chain_index, 0)  # ensure non-negative


def default_strike_formula(rect: Dict, chain_index: int, board_width: int = 6, board_height: int = 12) -> Dict:
    """Generate strike (sword) from rectangle using original Blade Fighters formulas.

    Based on docs2/README2.MD and docs2/DESIGN.md:
    - If H >= W (taller/square): vertical sword
    - If W > H (wider): horizontal sword (may convert to vertical)
    - Width cap: 3, Length cap: 12 (for 6x12 board)
    """
    width = rect.get('width', 0)
    height = rect.get('height', 0)

    # Board dimensions. Defaults keep legacy 6x12 behavior.
    BOARD_WIDTH = max(1, int(board_width))
    BOARD_HEIGHT = max(1, int(board_height))
    # Design rule: sword width is capped to 3; sword length is capped to board height.
    MAX_SWORD_WIDTH = 3

    def min3(x):
        return min(int(x), int(MAX_SWORD_WIDTH))

    def cap(x, lo, hi):
        return max(lo, min(x, hi))

    # Decide orientation: taller-or-square vs wider
    if height >= width:
        # Vertical sword (taller or square)
        sword_width = min3(width)
        # Combo multiplier scales vertical length.
        sword_length = cap(int(height) * int(chain_index), 1, BOARD_HEIGHT)

        return {
            'amount': sword_width * sword_length,
            'orientation': 'vertical',
            'sword_shape': (sword_width, sword_length),
            'rect': (width, height),
            'chain': chain_index
        }
    else:
        # Horizontal sword candidate (wider)
        sword_rows = min3(height)
        raw_length = width * chain_index

        # Auto-convert to vertical if at least half cannot enter
        conversion_threshold = 2 * BOARD_WIDTH  # kept for legacy behavior

        if raw_length >= conversion_threshold:
            # Convert to vertical
            sword_width = sword_rows
            sword_length = cap(int(raw_length), 1, BOARD_HEIGHT)

            return {
                'amount': sword_width * sword_length,
                'orientation': 'vertical',
                'sword_shape': (sword_width, sword_length),
                'rect': (width, height),
                'chain': chain_index,
                'converted_from_horizontal': True
            }
        else:
            # Special-case: once a horizontal sword is saturated (it would fully occupy
            # the 6-wide entry), additional combo scaling can otherwise appear to “do
            # nothing” because the visible/entered length is capped to BOARD_WIDTH.
            #
            # For combo step 3+ when raw_length exceeds BOARD_WIDTH (but is still below
            # the legacy auto-convert threshold), convert to a vertical sword using the
            # entered length. This matches expected behavior for 3x2 @ x3: 2x6 vertical.
            try:
                saturated_overflow = (int(chain_index) >= 3) and (int(raw_length) > int(BOARD_WIDTH)) and (int(raw_length) < int(conversion_threshold))
            except Exception:
                saturated_overflow = False

            if saturated_overflow:
                sword_width = sword_rows
                sword_length = cap(int(BOARD_WIDTH), 1, BOARD_HEIGHT)
                return {
                    'amount': sword_width * sword_length,
                    'orientation': 'vertical',
                    'sword_shape': (sword_width, sword_length),
                    'rect': (width, height),
                    'chain': chain_index,
                    'converted_from_horizontal_saturation': True,
                    'raw_length': int(raw_length),
                    'entered_length': int(BOARD_WIDTH),
                }

            # Keep horizontal
            # Horizontal can only physically enter up to board width.
            entered_length = min(int(raw_length), int(BOARD_WIDTH))

            return {
                'amount': entered_length * sword_rows,
                'orientation': 'horizontal',
                'horizontal_sword_shape': (sword_rows, entered_length),
                'rect': (width, height),
                'chain': chain_index,
                'raw_length': raw_length
            }


class AttackManager:
    """Owns the pending outbound attack queue and formulas.

    Typical usage:
        mgr = AttackManager()
        for pass_index, stats in enumerate(history, start=1):
            mgr.generate_from_pass(pass_index, stats)
        mgr.tick_all()  # advance delays each frame
        ready = mgr.consume_ready()
    """

    def __init__(self,
                 sprinkle_formula: SprinkleFormula | None = None,
                 strike_formula: StrikeFormula | None = None,
                 default_delay: int = DEFAULT_ATTACK_DELAY):
        self.queue: List[Attack] = []
        self.generated_last_chain: List[Attack] = []
        self._sprinkle_formula = sprinkle_formula or default_sprinkle_formula
        self._strike_formula = strike_formula or default_strike_formula
        self._default_delay = default_delay
        self._debug = env_flag('BF_DEBUG_ATTACK_GEN', default=False)
        # Optional board dimensions for dimension-aware strike formulas.
        # If unset, default_strike_formula will behave as legacy 6x12.
        self._board_width: int | None = None
        self._board_height: int | None = None

    def _call_strike_formula(self, rect: Dict, pass_index: int) -> Dict:
        """Call strike formula with best-available board dimension context.

        Backward-compatible with older formulas that accept only (rect, pass_index).
        """
        bw = int(self._board_width) if self._board_width else 6
        bh = int(self._board_height) if self._board_height else 12
        fn = self._strike_formula

        # Prefer to detect arity rather than catching TypeError from inside the formula.
        try:
            sig = inspect.signature(fn)
            params = list(sig.parameters.values())
            has_varargs = any(p.kind == inspect.Parameter.VAR_POSITIONAL for p in params)
            positional = [p for p in params if p.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)]
            if has_varargs or len(positional) >= 4:
                return fn(rect, pass_index, bw, bh)
        except Exception:
            # If we can't inspect it, fall back to runtime call attempts.
            pass

        try:
            return fn(rect, pass_index)
        except TypeError:
            # Last resort: try the 4-arg form.
            return fn(rect, pass_index, bw, bh)

    # --- Queue helpers -------------------------------------------------
    def reset_chain(self):
        self.generated_last_chain = []

    def tick_all(self):
        for atk in self.queue:
            atk.tick()

    def consume_ready(self) -> List[Attack]:
        ready = [a for a in self.queue if a.ready]
        if ready:
            self.queue = [a for a in self.queue if not a.ready]
        return ready

    def collect_ready(self) -> List[Attack]:
        """Backward-compatible alias for older callers."""
        return self.consume_ready()

    # --- Generation ----------------------------------------------------
    def generate_from_pass(self, pass_index: int, stats: Dict):
        """Translate one chain pass stats block into attacks and enqueue them."""
        dprint(self._debug, f"[ATTACK GEN] Pass {pass_index}, stats: {stats}")
        sprinkles = stats.get('sprinkles', 0)
        sprinkle_amt = self._sprinkle_formula(sprinkles, pass_index)
        dprint(self._debug, f"[ATTACK GEN] Sprinkles {sprinkles} -> amount {sprinkle_amt}")
        if sprinkle_amt > 0:
            self._enqueue(Attack(AttackKind.SPRINKLE, sprinkle_amt, self._default_delay,
                                 meta={'pass': pass_index, 'sprinkles': sprinkles, 'chain': pass_index}))

        for rect in stats.get('rectangles', []) or []:
            info = self._call_strike_formula(rect, pass_index)
            if not info or info.get('amount', 0) <= 0:
                continue
            meta = {'pass': pass_index, **{k: v for k, v in info.items() if k != 'amount'}}
            # Debug: log horizontal sword detection
            if 'horizontal_sword_shape' in info:
                dprint(self._debug, f"[ATTACK GEN] Horizontal sword detected: {info['horizontal_sword_shape']} from rect {rect}")
            elif 'orientation' in info and info['orientation'] == 'horizontal':
                dprint(self._debug, f"[ATTACK GEN] Horizontal orientation detected: {info}")
            self._enqueue(Attack(AttackKind.STRIKE, info['amount'], self._default_delay, meta=meta))

    def generate_from_chain(self, pass_history: Iterable[Dict], board_width: int, board_height: int):
        """Batch-generate attacks over an entire chain history.

        Currently a thin loop; placeholder for future board-dimension scaling.
        """
        # Record board dims so strike formulas can cap by the actual mode/board.
        try:
            self._board_width = max(1, int(board_width))
        except Exception:
            self._board_width = None
        try:
            self._board_height = max(1, int(board_height))
        except Exception:
            self._board_height = None

        dprint(self._debug, "[ATTACK GEN] generate_from_chain called, resetting chain")
        self.reset_chain()
        for idx, stats in enumerate(pass_history, start=1):
            self.generate_from_pass(idx, stats)
        dprint(self._debug, f"[ATTACK GEN] generate_from_chain complete, generated_last_chain has {len(self.generated_last_chain)} attacks")

    # --- Internal ------------------------------------------------------
    def _enqueue(self, attack: Attack):
        dprint(self._debug, f"[ATTACK GEN] Enqueueing {attack.kind.value}:{attack.amount}d{attack.delay}")
        self.queue.append(attack)
        self.generated_last_chain.append(attack)
        dprint(self._debug, f"[ATTACK GEN] generated_last_chain now has {len(self.generated_last_chain)} attacks")
