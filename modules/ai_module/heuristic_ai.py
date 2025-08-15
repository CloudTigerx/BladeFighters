from __future__ import annotations

import random
import time
import copy

from .base import EnemyAIConfig
from ..logging_module.error_handler import (
    safe_operation,
    log_and_continue
)
from ..logging_module.logger import get_logger

logger = get_logger(__name__)


class HeuristicAI:
    """Heuristic-driven AI that prefers flatter stacks, avoids holes,
    and optionally tries to build 2x2 clusters.

    Behavior and speed are controlled via EnemyAIConfig.
    """

    def __init__(self, config: EnemyAIConfig | None = None):
        self.config = config or EnemyAIConfig()
        self._last_action_ms: int = 0

    # -------------------------- Public API --------------------------
    def update(self, engine, now_ms: int) -> None:
        # Throttle actions with adaptive urgency when the stack is high or attacks are incoming
        effective_interval = self.config.action_interval_ms
        
        # Check stack height for urgency adjustment
        effective_interval = self._adjust_interval_for_stack_height(engine, effective_interval)
        
        # Incoming pressure speeds decisions
        effective_interval = self._adjust_interval_for_incoming_attacks(engine, effective_interval)

        if now_ms - self._last_action_ms < effective_interval:
            return

        self._last_action_ms = now_ms

        # If we intentionally make a mistake, do a random small action or nothing
        if random.random() < self.config.mistake_rate:
            self._perform_imperfect_action(engine)
            return

        # Main AI decision making
        self._make_ai_decision(engine)

    @safe_operation("adjust interval for stack height", 50, "WARNING")
    def _adjust_interval_for_stack_height(self, engine, base_interval: int) -> int:
        """Adjust action interval based on stack height."""
        try:
            highest_column = max(
                self._compute_column_height(engine.puzzle_grid, x, engine.total_grid_height)
                for x in range(engine.grid_width)
            )
            if highest_column >= max(0, engine.total_grid_height - 3):
                return max(50, int(base_interval * 0.6))
        except Exception as e:
            logger.warning(f"Failed to compute stack height: {str(e)}")
        return base_interval

    @safe_operation("adjust interval for incoming attacks", 45, "WARNING")
    def _adjust_interval_for_incoming_attacks(self, engine, base_interval: int) -> int:
        """Adjust action interval based on incoming attacks."""
        try:
            incoming = 0
            tm = getattr(engine, 'test_mode', None)
            if tm and hasattr(tm, 'pending_attacks'):
                incoming = len(tm.pending_attacks.get('enemy', []))
            if incoming > 0:
                return max(45, int(base_interval * 0.85))
        except Exception as e:
            logger.warning(f"Failed to check incoming attacks: {str(e)}")
        return base_interval

    @log_and_continue("AI decision making failed", None, "ERROR")
    def _make_ai_decision(self, engine) -> None:
        """Make the main AI decision with error handling."""
        # If we want to build 2x2 clusters, orient horizontally more often
        if self.config.build_2x2_clusters:
            self._ensure_horizontal_orientation(engine)

        # Choose target (with simple 1-ply placement search at higher difficulties)
        if self.config.lookahead_depth >= 1:
            target_column, target_pos = self._choose_target_with_1ply(engine)
            # Steer orientation first if needed
            self._rotate_towards_orientation(engine, target_pos)
        else:
            target_column = self._choose_target_column(engine)

        self._move_towards_column(engine, target_column)

        # Soft drop occasionally or when aligned
        main_x = engine.piece_position[0]
        if self.config.soft_drop and (main_x == target_column or random.random() < 0.25):
            engine.move_piece(0, 1)

    # -------------------------- Heuristics --------------------------
    def _choose_target_column(self, engine) -> int:
        grid = engine.puzzle_grid
        width = engine.grid_width
        height = engine.total_grid_height

        # Extract current piece colors for simple matching preferences
        piece_colors: list[str] = []
        self._extract_piece_colors(engine, piece_colors)

        # Incoming pressure factor
        pressure = self._calculate_pressure_factor(engine)

        best_score = float('inf')
        best_x = engine.piece_position[0]

        # Precompute neighbor heights for well detection
        column_heights = [self._compute_column_height(grid, x, height) for x in range(width)]

        for x in range(width):
            column_height = column_heights[x]
            hole_count = self._count_column_holes(grid, x, height)

            # Prefer matching top color if available
            color_match_bonus = 0.0
            top_color = self._top_color(grid, x, height)
            if top_color and piece_colors:
                if top_color in piece_colors:
                    color_match_bonus = -0.5  # reduce score a bit

            # Extra bonus if we can potentially complete a 2x2 with a neighbor of same color
            two_by_two_bonus = 0.0
            if self.config.build_2x2_clusters and piece_colors and top_color:
                for nx in (x - 1, x + 1):
                    if 0 <= nx < width:
                        neighbor_color = self._top_color(grid, nx, height)
                        if neighbor_color and neighbor_color == top_color and neighbor_color in piece_colors:
                            neighbor_height = column_heights[nx]
                            if abs(neighbor_height - column_height) <= 1:
                                two_by_two_bonus += -0.6

            # Avoid dropping on top of garbage or strikes if possible
            garbage_top_penalty = 0.0
            top_raw = self._top_raw(grid, x, height)
            if top_raw and ('_garbage' in top_raw or '_strike' in top_raw):
                garbage_top_penalty = 0.6

            # Distance from current x; reduce weight at higher difficulty (lower mistake_rate)
            current_x = engine.piece_position[0]
            lateral_weight = 0.18 * (0.5 + 0.5 * (self.config.mistake_rate))
            lateral_distance = abs(x - current_x) * lateral_weight

            # Stronger penalty for building under the game-over column (index 3)
            center_safety_penalty = self._calculate_center_safety_penalty(x, column_height, height, pressure)

            # Tall tower penalty grows sharply when near the top
            tall_penalty = (max(0, column_height - (height - 6)) ** 1.25) * 0.7 * pressure

            # Well-filling incentive: encourage filling deep wells relative to neighbors
            left_h = column_heights[x - 1] if x - 1 >= 0 else column_height
            right_h = column_heights[x + 1] if x + 1 < width else column_height
            neighbor_min = min(left_h, right_h)
            well_bonus = -0.6 if column_height + 2 <= neighbor_min else 0.0

            # Base score: height + holes*weight + distance - bonuses + penalties
            score = (
                column_height
                + hole_count * (0.8 if self.config.avoid_holes else 0.3)
                + lateral_distance
                + center_safety_penalty
                + garbage_top_penalty
                + tall_penalty
                + well_bonus
                + two_by_two_bonus
                + color_match_bonus
            )

            # Simple lookahead: penalize very tall neighboring towers if enabled
            if self.config.lookahead_depth >= 1:
                left_h = self._compute_column_height(grid, max(0, x - 1), height)
                right_h = self._compute_column_height(grid, min(width - 1, x + 1), height)
                variance_penalty = abs(left_h - column_height) * 0.12 + abs(right_h - column_height) * 0.12
                score += variance_penalty

            if score < best_score:
                best_score = score
                best_x = x

        return best_x

    def _choose_target_with_1ply(self, engine) -> tuple[int, int]:
        """Choose (target_column, target_attached_pos) using a lightweight 1-ply evaluation,
        including a short simulation of immediate clears and gravity chains. If lookahead_depth>=2,
        include a best-second-move bonus based on the next piece preview when available.
        attached_position: 0=Top, 1=Right, 2=Bottom, 3=Left
        """
        grid = engine.puzzle_grid
        width = engine.grid_width
        height = engine.total_grid_height
        current_x = engine.piece_position[0]

        # Colors of current piece
        main_color, att_color = self._extract_current_piece_colors(engine)

        # Next piece colors (for 2-ply)
        next_main, next_att = self._extract_next_piece_colors(engine)

        # Incoming pressure factor
        pressure = self._calculate_pressure_factor(engine)

        best = (engine.piece_position[0], getattr(engine, 'attached_position', 0))
        best_score = float('inf')

        for x in range(width):
            for pos in (0, 1, 2, 3):
                # Determine columns occupied by main and attached
                main_col = x
                att_col = x
                if pos == 1:
                    att_col = x + 1
                elif pos == 3:
                    att_col = x - 1
                # Skip invalid columns
                if att_col < 0 or att_col >= width or main_col < 0 or main_col >= width:
                    continue

                # Predict landing rows (topmost empty cell indices)
                base_main_y = self._predict_landing_y(grid, main_col, height)
                base_att_y = self._predict_landing_y(grid, att_col, height)
                if base_main_y is None or base_att_y is None:
                    continue  # column is full

                # Base board features
                h_main = self._compute_column_height(grid, main_col, height)
                h_att = self._compute_column_height(grid, att_col, height)
                holes_penalty = (
                    self._count_column_holes(grid, main_col, height)
                    + self._count_column_holes(grid, att_col, height)
                ) * (0.8 if self.config.avoid_holes else 0.3)

                # Lateral movement cost relative to current position
                lateral_weight = 0.18 * (0.5 + 0.5 * (self.config.mistake_rate))
                lateral_cost = abs(x - current_x) * lateral_weight

                # Center safety penalty for stacking in game-over column (index 3)
                center_pen = 0.0
                if main_col == 3 or att_col == 3:
                    center_pen = max(0, max(h_main, h_att) - (height - 6)) * 1.0 * pressure

                # Garbage/strike top penalties
                garbage_pen = 0.0
                top_main_raw = self._top_raw(grid, main_col, height)
                top_att_raw = self._top_raw(grid, att_col, height)
                if top_main_raw and ('_garbage' in top_main_raw or '_strike' in top_main_raw):
                    garbage_pen += 0.6
                if top_att_raw and ('_garbage' in top_att_raw or '_strike' in top_att_raw):
                    garbage_pen += 0.6

                # Local color adjacency bonus near landing
                cluster_prep_bonus = 0.0
                if main_color:
                    cluster_prep_bonus += self._local_color_bonus(grid, main_col, base_main_y, height, main_color)
                if att_color:
                    cluster_prep_bonus += self._local_color_bonus(grid, att_col, base_att_y, height, att_color)

                # Neighbor variance smoothing
                left_h = self._compute_column_height(grid, max(0, x - 1), height)
                right_h = self._compute_column_height(grid, min(width - 1, x + 1), height)
                variance_penalty = abs(left_h - max(h_main, h_att)) * 0.12 + abs(right_h - max(h_main, h_att)) * 0.12

                # Simulate immediate placement and up to 2 gravity/clear waves; get grid after placement
                sim_bonus, grid_after = self._simulate_place_and_chain(
                    grid, width, height, x, pos, main_color, att_color
                )

                # Optional 2-ply: evaluate best follow-up using preview piece
                second_ply_bonus = 0.0
                if self.config.lookahead_depth >= 2 and (next_main or next_att) and grid_after is not None:
                    second_ply_bonus = self._best_second_ply_bonus(
                        grid_after, width, height, next_main, next_att
                    )

                score = (
                    max(h_main, h_att)
                    + holes_penalty
                    + lateral_cost
                    + center_pen
                    + garbage_pen
                    + variance_penalty
                    - cluster_prep_bonus
                    - sim_bonus
                    - second_ply_bonus
                )

                if score < best_score:
                    best_score = score
                    best = (x, pos)

        return best

    def _ensure_horizontal_orientation(self, engine) -> None:
        # attached_position: 0=Top, 1=Right, 2=Bottom, 3=Left
        pos = getattr(engine, 'attached_position', 0)
        if pos in (1, 3):
            return  # already horizontal

        # Try rotating clockwise. If fails, try counter-clockwise
        if not self._safe_rotate(engine, +1):
            self._safe_rotate(engine, -1)

    def _move_towards_column(self, engine, target_x: int) -> None:
        current_x = engine.piece_position[0]
        dx = 0
        if current_x < target_x:
            dx = +1
        elif current_x > target_x:
            dx = -1

        if dx != 0:
            engine.move_piece(dx, 0)

    def _rotate_towards_orientation(self, engine, target_pos: int) -> None:
        try:
            current_pos = getattr(engine, 'attached_position', 0)
            if current_pos == target_pos:
                return
            diff = (target_pos - current_pos) % 4
            if diff == 1:
                self._safe_rotate(engine, +1)
            elif diff == 3:
                self._safe_rotate(engine, -1)
            elif diff == 2:
                # Two steps; pick a direction and rotate once now
                self._safe_rotate(engine, +1 if random.random() < 0.5 else -1)
        except Exception:
            pass

    # -------------------------- Imperfect action --------------------------
    def _perform_imperfect_action(self, engine) -> None:
        choice = random.random()
        try:
            if choice < 0.33:
                engine.move_piece(random.choice([-1, 1]), 0)
            elif choice < 0.66:
                self._safe_rotate(engine, random.choice([-1, +1]))
            else:
                if self.config.soft_drop:
                    engine.move_piece(0, 1)
        except Exception:
            pass

    # -------------------------- Utilities --------------------------
    @staticmethod
    def _safe_rotate(engine, direction: int) -> bool:
        try:
            return bool(engine.rotate_attached_piece(direction))
        except Exception:
            return False

    @staticmethod
    def _compute_column_height(grid, x: int, total_h: int) -> int:
        # Height is number of filled cells in column
        filled = 0
        for y in range(total_h):
            if grid[y][x] is not None:
                filled = total_h - y
                break
        return filled

    @staticmethod
    def _count_column_holes(grid, x: int, total_h: int) -> int:
        # Count empty cells that have at least one filled cell somewhere below
        seen_filled_below = False
        holes = 0
        for y in range(total_h - 1, -1, -1):
            if grid[y][x] is not None:
                seen_filled_below = True
            else:
                if seen_filled_below:
                    holes += 1
        return holes

    @staticmethod
    def _top_color(grid, x: int, total_h: int) -> str | None:
        for y in range(total_h):
            if grid[y][x] is not None:
                try:
                    return str(grid[y][x]).split('_')[0]
                except Exception:
                    return None
        return None

    @staticmethod
    def _top_raw(grid, x: int, total_h: int) -> str | None:
        """Return the raw string of the first non-empty top cell in the column, if any."""
        for y in range(total_h):
            if grid[y][x] is not None:
                try:
                    return str(grid[y][x])
                except Exception:
                    return None
        return None

    @staticmethod
    def _predict_landing_y(grid, x: int, total_h: int) -> int | None:
        """Return the y index where a new block would land in column x (top-most empty), or None if full."""
        for y in range(total_h):
            if grid[y][x] is not None:
                return max(0, y - 1)
        # Column entirely empty
        return total_h - 1

    @staticmethod
    def _local_color_bonus(grid, x: int, y: int, total_h: int, color: str) -> float:
        """Simple local bonus for placing a block with matching neighbors near (x, y)."""
        if y is None:
            return 0.0
        bonus = 0.0
        # Check up/down/left/right if within bounds
        neighbors = [
            (x - 1, y),
            (x + 1, y),
            (x, y - 1),
            (x, y + 1),
        ]
        for nx, ny in neighbors:
            if 0 <= nx < len(grid[0]) and 0 <= ny < total_h:
                cell = grid[ny][nx]
                if cell is not None:
                    try:
                        if str(cell).split('_')[0] == color:
                            bonus += 0.25
                    except Exception:
                        continue
        return bonus

    # -------------------------- Simulation helpers --------------------------
    def _simulate_place_and_chain(self, grid, width: int, height: int, x: int, pos: int, main_color: str | None, att_color: str | None) -> tuple[float, list[list] | None]:
        """Simulate placing the current piece at (x,pos) and return (bonus, resulting_grid)
        based on immediate clears and up to 2 gravity/clear waves. Includes setup bonus for near-2x2s created.
        Emphasizes quick triples by weighting chain count higher and adding a bonus for 3+ chains."""
        try:
            g = [row[:] for row in grid]

            # Determine columns
            main_col = x
            att_col = x
            if pos == 1:
                att_col = x + 1
            elif pos == 3:
                att_col = x - 1
            if att_col < 0 or att_col >= width or main_col < 0 or main_col >= width:
                return 0.0, None

            placed_positions: list[tuple[int, int, str]] = []

            # Compute landing positions and place blocks
            if pos in (0, 2):
                base_y = self._predict_landing_y(g, main_col, height)
                if base_y is None or base_y - 1 < 0:
                    return 0.0, None
                bottom_color = att_color if pos == 2 else main_color
                top_color = main_color if pos == 2 else att_color
                if bottom_color:
                    g[base_y][main_col] = f"{bottom_color}_sim"
                    placed_positions.append((main_col, base_y, bottom_color))
                if top_color:
                    g[base_y - 1][main_col] = f"{top_color}_sim"
                    placed_positions.append((main_col, base_y - 1, top_color))
            else:
                y_main = self._predict_landing_y(g, main_col, height)
                y_att = self._predict_landing_y(g, att_col, height)
                if y_main is None or y_att is None:
                    return 0.0, None
                if main_color:
                    g[y_main][main_col] = f"{main_color}_sim"
                    placed_positions.append((main_col, y_main, main_color))
                if att_color:
                    g[y_att][att_col] = f"{att_color}_sim"
                    placed_positions.append((att_col, y_att, att_color))

            # Setup bonuses: near-2x2 and 2x3/3x2 rectangles around new placements
            setup_bonus = self._near_2x2_setup_bonus(g, width, height, placed_positions)
            setup_bonus += self._near_rect_setup_bonus(g, width, height, placed_positions)

            # Run up to 2 clear/gravity waves
            total_cleared = 0
            chains = 0
            for _ in range(2):
                cluster = self._detect_2x2_clusters_on_grid(g, width, height)
                if not cluster:
                    break
                chains += 1
                total_cleared += len(cluster)
                # Clear cluster
                for (cx, cy) in cluster:
                    g[cy][cx] = None
                # Apply gravity
                self._apply_gravity_on_grid(g, width, height)

            # Convert clears/chains into a scalar bonus; emphasize quick triples
            chain_weight = 2.6
            triple_spike = 3.0 if chains >= 3 else 0.0
            total_bonus = total_cleared * 0.85 + chains * chain_weight + triple_spike + setup_bonus
            return total_bonus, g
        except Exception:
            return 0.0, None

    @staticmethod
    def _detect_2x2_clusters_on_grid(grid, width: int, height: int) -> set[tuple[int, int]]:
        cluster = set()
        for y in range(height - 1):
            for x in range(width - 1):
                a = grid[y][x]
                b = grid[y][x + 1]
                c = grid[y + 1][x]
                d = grid[y + 1][x + 1]
                if not a or not b or not c or not d:
                    continue
                sa = str(a)
                sb = str(b)
                sc = str(c)
                sd = str(d)
                if ('_garbage' in sa) or ('_garbage' in sb) or ('_garbage' in sc) or ('_garbage' in sd):
                    continue
                if ('_strike' in sa) or ('_strike' in sb) or ('_strike' in sc) or ('_strike' in sd):
                    continue
                ca = sa.split('_')[0]
                cb = sb.split('_')[0]
                cc = sc.split('_')[0]
                cd = sd.split('_')[0]
                if ca == cb == cc == cd:
                    cluster.update({(x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)})
        return cluster

    @staticmethod
    def _apply_gravity_on_grid(grid, width: int, height: int) -> None:
        for x in range(width):
            write_y = height - 1
            for y in range(height - 1, -1, -1):
                if grid[y][x] is not None:
                    if write_y != y:
                        grid[write_y][x] = grid[y][x]
                        grid[y][x] = None
                    write_y -= 1
            # Clear cells above write_y
            for y in range(write_y, -1, -1):
                grid[y][x] = None

    @staticmethod
    def _near_2x2_setup_bonus(grid, width: int, height: int, placed_positions: list[tuple[int, int, str]]) -> float:
        """Score near-2x2 formations (3 of 4 same-color) that include the newly placed cells.
        Rewards future-clear potential even when nothing clears immediately."""
        bonus = 0.0
        seen_windows: set[tuple[int, int, str]] = set()
        for px, py, color in placed_positions:
            for ox in (-1, 0):
                for oy in (-1, 0):
                    wx = px + ox
                    wy = py + oy
                    if wx < 0 or wy < 0 or wx + 1 >= width or wy + 1 >= height:
                        continue
                    key = (wx, wy, color)
                    if key in seen_windows:
                        continue
                    seen_windows.add(key)

                    cells = [
                        grid[wy][wx], grid[wy][wx + 1],
                        grid[wy + 1][wx], grid[wy + 1][wx + 1]
                    ]
                    skip = False
                    for c in cells:
                        if c is None:
                            continue
                        sc = str(c)
                        if ('_garbage' in sc) or ('_strike' in sc):
                            skip = True
                            break
                    if skip:
                        continue

                    matches = 0
                    empties = 0
                    for c in cells:
                        if c is None:
                            empties += 1
                        else:
                            try:
                                if str(c).split('_')[0] == color:
                                    matches += 1
                            except Exception:
                                pass
                    if matches >= 3 and empties >= 1:
                        bonus += 0.9
                    elif matches == 2 and empties >= 1:
                        bonus += 0.35
        return bonus

    @staticmethod
    def _near_rect_setup_bonus(grid, width: int, height: int, placed_positions: list[tuple[int, int, str]]) -> float:
        """Score near-2x3 and 3x2 rectangles to encourage building larger patterns that can triple quickly."""
        bonus = 0.0
        for px, py, color in placed_positions:
            # 2x3 windows around placement
            for ox in (-1, 0):
                for oy in (-2, -1, 0):
                    wx = px + ox
                    wy = py + oy
                    if wx < 0 or wy < 0 or wx + 1 >= width or wy + 2 >= height:
                        continue
                    cells = [
                        grid[wy][wx], grid[wy][wx + 1],
                        grid[wy + 1][wx], grid[wy + 1][wx + 1],
                        grid[wy + 2][wx], grid[wy + 2][wx + 1],
                    ]
                    if any((c is not None and (('_garbage' in str(c)) or ('_strike' in str(c)))) for c in cells):
                        continue
                    matches = 0
                    empties = 0
                    for c in cells:
                        if c is None:
                            empties += 1
                        else:
                            try:
                                if str(c).split('_')[0] == color:
                                    matches += 1
                            except Exception:
                                pass
                    if matches >= 5 and empties >= 1:
                        bonus += 0.8
                    elif matches == 4 and empties >= 1:
                        bonus += 0.4
            # 3x2 windows around placement
            for ox in (-2, -1, 0):
                for oy in (-1, 0):
                    wx = px + ox
                    wy = py + oy
                    if wx < 0 or wy < 0 or wx + 2 >= width or wy + 1 >= height:
                        continue
                    cells = [
                        grid[wy][wx], grid[wy][wx + 1], grid[wy][wx + 2],
                        grid[wy + 1][wx], grid[wy + 1][wx + 1], grid[wy + 1][wx + 2],
                    ]
                    if any((c is not None and (('_garbage' in str(c)) or ('_strike' in str(c)))) for c in cells):
                        continue
                    matches = 0
                    empties = 0
                    for c in cells:
                        if c is None:
                            empties += 1
                        else:
                            try:
                                if str(c).split('_')[0] == color:
                                    matches += 1
                            except Exception:
                                pass
                    if matches >= 5 and empties >= 1:
                        bonus += 0.8
                    elif matches == 4 and empties >= 1:
                        bonus += 0.4
        return bonus

    def _best_second_ply_bonus(self, grid_after, width: int, height: int, next_main: str | None, next_att: str | None) -> float:
        """Evaluate the best immediate clear/setup bonus for the preview piece on the provided grid."""
        if not (next_main or next_att):
            return 0.0
        best = 0.0
        for x in range(width):
            for pos in (0, 1, 2, 3):
                bonus, _ = self._simulate_place_and_chain(grid_after, width, height, x, pos, next_main, next_att)
                if bonus > best:
                    best = bonus
        # Slightly discount second ply to balance runtime and aggressiveness
        return best * 0.8

    @safe_operation("extract piece colors", None, "WARNING")
    def _extract_piece_colors(self, engine, piece_colors: list[str]) -> None:
        """Extract colors from current pieces."""
        try:
            if getattr(engine, 'main_piece', None):
                piece_colors.append(str(engine.main_piece).split('_')[0])
            if getattr(engine, 'attached_piece', None):
                piece_colors.append(str(engine.attached_piece).split('_')[0])
        except Exception as e:
            logger.warning(f"Failed to extract piece colors: {str(e)}")

    @safe_operation("calculate pressure factor", 1.0, "WARNING")
    def _calculate_pressure_factor(self, engine) -> float:
        """Calculate pressure factor based on incoming attacks."""
        try:
            tm = getattr(engine, 'test_mode', None)
            if tm and hasattr(tm, 'pending_attacks'):
                incoming = len(tm.pending_attacks.get('enemy', []))
                return 1.0 + min(incoming, 3) * 0.25
        except Exception as e:
            logger.warning(f"Failed to calculate pressure factor: {str(e)}")
        return 1.0

    @safe_operation("calculate center safety penalty", 0.0, "WARNING")
    def _calculate_center_safety_penalty(self, x: int, column_height: int, height: int, pressure: float) -> float:
        """Calculate safety penalty for building under the game-over column."""
        try:
            if x == 3:  # Column 4 is special game-over column
                return max(0, column_height - (height - 6)) * 0.9 * pressure
        except Exception as e:
            logger.warning(f"Failed to calculate center safety penalty: {str(e)}")
        return 0.0

    @safe_operation("extract current piece colors", (None, None), "WARNING")
    def _extract_current_piece_colors(self, engine) -> tuple[str | None, str | None]:
        """Extract colors from current pieces."""
        try:
            main_color = str(engine.main_piece).split('_')[0] if getattr(engine, 'main_piece', None) else None
            att_color = str(engine.attached_piece).split('_')[0] if getattr(engine, 'attached_piece', None) else None
            return main_color, att_color
        except Exception as e:
            logger.warning(f"Failed to extract current piece colors: {str(e)}")
            return None, None

    @safe_operation("extract next piece colors", (None, None), "WARNING")
    def _extract_next_piece_colors(self, engine) -> tuple[str | None, str | None]:
        """Extract colors from next pieces."""
        try:
            next_main = str(engine.next_main_piece).split('_')[0] if getattr(engine, 'next_main_piece', None) else None
            next_att = str(engine.next_attached_piece).split('_')[0] if getattr(engine, 'next_attached_piece', None) else None
            return next_main, next_att
        except Exception as e:
            logger.warning(f"Failed to extract next piece colors: {str(e)}")
            return None, None

