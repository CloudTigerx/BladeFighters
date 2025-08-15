from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass
class EnemyAIConfig:
    # Behavior toggles
    random_moves: bool = True
    use_column_height_heuristic: bool = False
    avoid_holes: bool = False
    build_2x2_clusters: bool = False
    soft_drop: bool = True
    use_wall_kicks: bool = True

    # Difficulty knobs
    lookahead_depth: int = 0  # 0..2
    mistake_rate: float = 0.0  # 0..1
    action_interval_ms: int = 90


class PuzzleAI(Protocol):
    def update(self, engine, now_ms: int) -> None:
        ...


def config_for_difficulty(level: int) -> EnemyAIConfig:
    """Create an EnemyAIConfig for a given difficulty level (1-10).

    Difficulty scaling rules:
    - Faster actions at higher difficulty (shorter action interval)
    - Fewer mistakes at higher difficulty
    - Enable heuristics as difficulty increases
    - Increase lookahead at higher difficulty
    """
    # Clamp to 1..10
    level = max(1, min(10, int(level)))

    # Action interval: 220ms (L1) → 70ms (L10)
    max_interval = 220
    min_interval = 70
    # Linear interpolation across 9 steps
    interval = int(max_interval - (max_interval - min_interval) * ((level - 1) / 9))

    # Mistake rate: 0.50 (L1) → 0.05 (L10)
    max_mistake = 0.50
    min_mistake = 0.05
    mistake = max_mistake - (max_mistake - min_mistake) * ((level - 1) / 9)

    # Lookahead depth tiers: 0 (1-3), 1 (4-7), 2 (8-10)
    if level <= 3:
        lookahead = 0
    elif level <= 7:
        lookahead = 1
    else:
        lookahead = 2

    # Heuristic toggles by difficulty
    use_height_heuristic = level >= 4
    avoid_holes = level >= 6
    build_2x2 = level >= 8

    return EnemyAIConfig(
        random_moves=True,
        use_column_height_heuristic=use_height_heuristic,
        avoid_holes=avoid_holes,
        build_2x2_clusters=build_2x2,
        soft_drop=True,
        use_wall_kicks=True,
        lookahead_depth=lookahead,
        mistake_rate=mistake,
        action_interval_ms=interval,
    )
