from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, Any


def compute_chain_points(per_pass: Any) -> tuple[int, list[int]]:
    """Compute points for a chain.

    Scoring rule (tunable later, but centralized here):
    - Each pass i (1-based) has multiplier (i + 1).
    - Points for that pass = cleared_in_pass * multiplier.

    This matches the example: 4 blocks at 4x combo => 4 * (4 + 1) = 20.
    """
    per_pass_list: list[int] = []
    try:
        if isinstance(per_pass, list):
            per_pass_list = [int(x or 0) for x in per_pass]
        elif per_pass is None:
            per_pass_list = []
        else:
            # Best-effort conversion for other sequences.
            per_pass_list = [int(x or 0) for x in list(per_pass)]
    except Exception:
        per_pass_list = []

    points_per_pass: list[int] = []
    total_points = 0
    for i0, cleared in enumerate(per_pass_list):
        mult = int(i0 + 2)  # pass 1 => x2, pass 4 => x5
        pts = int(max(0, int(cleared)) * mult)
        points_per_pass.append(pts)
        total_points += pts
    return int(total_points), points_per_pass


@dataclass
class _ScoreSlot:
    clears_total: int = 0
    chains: int = 0
    max_chain: int = 0
    sprinkles_sent: int = 0
    strikes_sent: int = 0
    sprinkles_received: int = 0
    strikes_received: int = 0
    piece_locks: int = 0
    points_total: int = 0
    last_chain: Dict[str, int] | None = None
    last_chain_points: int = 0
    last_chain_points_per_pass: list[int] | None = None

    def record_chain(self, passes: int, total_cleared: int, per_pass: Any, garbage_removed: int = 0) -> None:
        self.chains += 1
        self.max_chain = max(self.max_chain, passes)
        self.clears_total += int(total_cleared)

        chain_points, points_per_pass = compute_chain_points(per_pass)
        self.points_total += int(chain_points)
        self.last_chain_points = int(chain_points)
        self.last_chain_points_per_pass = list(points_per_pass)
        self.last_chain = {
            'passes': int(passes),
            'total_cleared': int(total_cleared),
            'garbage_removed': int(garbage_removed),
        }

    def to_snapshot(self) -> Dict[str, Any]:
        data = asdict(self)
        return data


class ScoringManager:
    def __init__(self) -> None:
        self.player = _ScoreSlot()
        self.ai = _ScoreSlot()

    def to_snapshot(self) -> Dict[str, Any]:
        return {
            'player': self.player.to_snapshot(),
            'ai': self.ai.to_snapshot(),
        }


