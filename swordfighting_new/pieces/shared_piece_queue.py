"""shared_piece_queue.py

Deterministic piece generation so every fighter sees the *same sequence* of
pieces (colors + breaker flags) independent of render timing or future
visual re‑themes.

Design:
 - Single SharedPieceQueue owned by the session, seeded once.
 - Fighters do NOT consume from a mutable pop() queue (which would desync
   if one fighter locks faster). Instead each fighter keeps its own index
   into a lazily generated infinite sequence. Asking for index *i* always
   returns the same PieceSpec; the queue extends itself on demand.
 - This mirrors “bag” style fairness but currently uses pure IID sampling
   (can be swapped later for 8/14 bag logic without changing fighter code).

Future extensions:
 - Replace _generate_spec with 2/4/6/8 piece bag.
 - Add serialization of RNG / generated length for network sync.
"""
from __future__ import annotations

from dataclasses import dataclass
import random
import secrets
from typing import List, Sequence, Tuple


@dataclass(frozen=True)
class PieceSpec:
    """Specification for a falling two-block piece.

    color1 / color2: logical color names (stable identifiers, not RGB)
    breaker1 / breaker2: whether each block is a breaker.
    """
    color1: str
    breaker1: bool
    color2: str
    breaker2: bool

    def as_tuple(self) -> Tuple[str, bool, str, bool]:  # convenient for hashing/logging
        return (self.color1, self.breaker1, self.color2, self.breaker2)


class SharedPieceQueue:
    """Lazily generates an infinite deterministic sequence of PieceSpec objects.

    Fighters hold an integer cursor (piece_index). To obtain current & next pieces
    they call queue.get(index) and queue.get(index+1). Advancing the index is totally
    local; therefore one fighter temporarily racing ahead does not alter the future
    specs the trailing fighter will see—fair and reproducible.
    """

    def __init__(self,
                 seed: int,
                 colors: Sequence[str] = ("red", "blue", "yellow", "green"),
                 breaker_prob: float = 0.25):
        self.seed = int(seed)
        self._rng = random.Random(self.seed)
        self.colors: List[str] = list(colors)
        self.breaker_prob = breaker_prob
        self._generated: List[PieceSpec] = []

    # --- Public API --------------------------------------------------
    def get(self, index: int) -> PieceSpec:
        """Return the PieceSpec at sequence position `index` (0-based)."""
        if index < 0:
            raise ValueError("index must be >= 0")
        self._ensure(index)
        return self._generated[index]

    def preview_window(self, start: int, length: int) -> List[PieceSpec]:
        """Return a slice [start, start+length) without advancing anything."""
        end = start + length
        self._ensure(end - 1)
        return self._generated[start:end]

    def state_hash(self, look_ahead: int = 8) -> int:
        """Cheap reproducibility hash of upcoming sequence portion."""
        self._ensure(look_ahead - 1)
        frac = tuple(ps.as_tuple() for ps in self._generated[:look_ahead])
        return hash(frac + (self.seed,))

    # --- Internal ----------------------------------------------------
    def _ensure(self, index: int):
        while len(self._generated) <= index:
            self._generated.append(self._generate_spec())

    def _generate_spec(self) -> PieceSpec:
        c1 = self._rng.choice(self.colors)
        b1 = self._rng.random() < self.breaker_prob
        c2 = self._rng.choice(self.colors)
        b2 = self._rng.random() < self.breaker_prob
        return PieceSpec(c1, b1, c2, b2)


# Convenience factory (could add bag logic later)
def create_shared_piece_queue(seed: int | None) -> SharedPieceQueue:
    if seed is None:
        # Derive a seed from cryptographic randomness to avoid contamination
        # from any global random.seed() calls elsewhere.
        seed = secrets.randbits(31)
    return SharedPieceQueue(seed=seed)
