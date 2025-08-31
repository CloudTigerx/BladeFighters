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
from typing import Iterable, List, Dict, Callable

from .types import Attack, AttackKind, DEFAULT_ATTACK_DELAY

SprinkleFormula = Callable[[int, int], int]  # (sprinkles, chain_index) -> amount
StrikeFormula = Callable[[Dict, int], Dict]   # (rectangle_stats, chain_index) -> info dict


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


def default_strike_formula(rect: Dict, chain_index: int) -> Dict:
    """Generate strike (sword) from rectangle using original Blade Fighters formulas.

    Based on docs2/README2.MD and docs2/DESIGN.md:
    - If H >= W (taller/square): vertical sword
    - If W > H (wider): horizontal sword (may convert to vertical)
    - Width cap: 3, Length cap: 24 (for 12x24 board)
    """
    width = rect.get('width', 0)
    height = rect.get('height', 0)

    # Board constants - these should match your current board (12x24)
    BOARD_WIDTH = 12  # from swordfighting_new.core.board.Board.WIDTH
    BOARD_HEIGHT = 24  # from swordfighting_new.core.board.Board.HEIGHT
    MAX_SWORD_WIDTH = 3  # from original design docs

    def min3(x):
        return min(x, MAX_SWORD_WIDTH)

    def cap(x, lo, hi):
        return max(lo, min(x, hi))

    # Decide orientation: taller-or-square vs wider
    if height >= width:
        # Vertical sword (taller or square)
        sword_width = min3(width)
        sword_length = cap(height * chain_index, 1, BOARD_HEIGHT)

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
        conversion_threshold = 2 * BOARD_WIDTH  # 24 for 12-wide board

        if raw_length >= conversion_threshold:
            # Convert to vertical
            sword_width = sword_rows
            sword_length = cap(raw_length, 1, BOARD_HEIGHT)

            return {
                'amount': sword_width * sword_length,
                'orientation': 'vertical',
                'sword_shape': (sword_width, sword_length),
                'rect': (width, height),
                'chain': chain_index,
                'converted_from_horizontal': True
            }
        else:
            # Keep horizontal
            entered_length = min(raw_length, BOARD_WIDTH)

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

    # --- Generation ----------------------------------------------------
    def generate_from_pass(self, pass_index: int, stats: Dict):
        """Translate one chain pass stats block into attacks and enqueue them."""
        sprinkles = stats.get('sprinkles', 0)
        sprinkle_amt = self._sprinkle_formula(sprinkles, pass_index)
        if sprinkle_amt > 0:
            self._enqueue(Attack(AttackKind.SPRINKLE, sprinkle_amt, self._default_delay,
                                 meta={'pass': pass_index, 'sprinkles': sprinkles, 'chain': pass_index}))

        for rect in stats.get('rectangles', []) or []:
            info = self._strike_formula(rect, pass_index)
            if not info or info.get('amount', 0) <= 0:
                continue
            meta = {'pass': pass_index, **{k: v for k, v in info.items() if k != 'amount'}}
            # Debug: log horizontal sword detection
            if 'horizontal_sword_shape' in info:
                print(f"[DEBUG] Horizontal sword detected: {info['horizontal_sword_shape']} from rect {rect}")
            elif 'orientation' in info and info['orientation'] == 'horizontal':
                print(f"[DEBUG] Horizontal orientation detected: {info}")
            self._enqueue(Attack(AttackKind.STRIKE, info['amount'], self._default_delay, meta=meta))

    def generate_from_chain(self, pass_history: Iterable[Dict], board_width: int, board_height: int):
        """Batch-generate attacks over an entire chain history.

        Currently a thin loop; placeholder for future board-dimension scaling.
        """
        self.reset_chain()
        for idx, stats in enumerate(pass_history, start=1):
            self.generate_from_pass(idx, stats)

    # --- Internal ------------------------------------------------------
    def _enqueue(self, attack: Attack):
        self.queue.append(attack)
        self.generated_last_chain.append(attack)
