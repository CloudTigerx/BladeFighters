from typing import Dict, Tuple

from .item_system import WeaponPattern, VALID_COLORS


def color_counts_for_pattern(pattern: WeaponPattern, grid_height: int = 12) -> Dict[str, int]:
    """Count total cells per color across a 6 x grid_height preview of the pattern."""
    counts: Dict[str, int] = {c: 0 for c in VALID_COLORS}
    for col in range(6):
        for r in range(grid_height):
            # Convert preview row (top=0) to engine index
            engine_row_idx = (grid_height - 1 - r)
            color = pattern.color_for_cell(col, engine_row_idx, grid_height)
            if color in counts:
                counts[color] += 1
    return counts


def validate_max_color_ratio(pattern: WeaponPattern, grid_height: int = 12, max_ratio: float = 0.70) -> Tuple[bool, str]:
    """
    Returns (allowed, reason). Disallow if any single color occupies >= max_ratio of the grid.
    Increased limit to 70% to accommodate weapon patterns with strong color dominance.
    """
    total_cells = 6 * grid_height
    counts = color_counts_for_pattern(pattern, grid_height)
    # Check dominance
    for color, count in counts.items():
        ratio = count / total_cells
        if ratio >= max_ratio:
            return False, f"{color} dominates {ratio:.0%} (limit {int(max_ratio*100)}%)"
    return True, "ok"


def is_pattern_allowed(pattern: WeaponPattern, grid_height: int = 12) -> Tuple[bool, str]:
    """Composite policy for pattern acceptance. Extend with more rules here."""
    return validate_max_color_ratio(pattern, grid_height)

