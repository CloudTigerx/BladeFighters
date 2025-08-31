"""breaker.py - Breaker activation & chain logic for Blade Fighters.

Behavior summary (single activation pass):
 1. A breaker block (block.is_breaker) *only triggers* if it has at least one
     orthogonal neighbor (up/down/left/right) that shares its color.
 2. When triggered it clears: the breaker itself PLUS every 4-directionally
     connected normal (non-garbage, non-breaker-of-different-color) block of the
     same color reachable from ANY of its matching neighbors (the flood starts
     from each qualifying neighbor, but the breaker cell is also removed).
 3. Multiple breakers of the same color incident to the same color region merge
     implicitly because we collect cleared coordinates in a set.
 4. Garbage (is_garbage) never propagates the flood and is never cleared by a
     breaker color flood. (Future: other special block types could hook here.)
 5. A breaker with *no* same-color orthogonal neighbor remains on the board.

Chain reactions:
 After one pass, gravity may cause blocks to settle, potentially creating new
 adjacencies that wake further breakers. The helper method
 ``apply_breaker_chain`` repeatedly calls the single-pass ``apply_breakers``
 until a pass clears zero blocks. Each non-zero pass increments the chain
 counter. This mirrors classic falling-block chain mechanics and provides a
 deterministic (no timers) resolution step that callers can run immediately
 after locking a piece.

Public API additions:
 - BreakerManager.apply_breakers(): one pass, returns count cleared (existing behavior).
 - BreakerManager.apply_breaker_chain(max_passes=None): multi-pass, returns
      (chain_count, total_cleared, per_pass_clears[list]). Stops early if
      max_passes is provided.

Design notes:
 - Gravity is handled internally per pass via _cascade_columns(). If external
    visuals need per-pass timing they can call single-pass in a loop with delays.
 - Logic remains board-implementation agnostic so long as board provides:
         WIDTH, HEIGHT, EMPTY sentinel, get_piece(x,y), set_piece(x,y, value),
         is_in_bounds(x,y)
 - This file purposefully does *not* import other game systems to stay lean.

Updated behavior (progressive clearing):
 - Breakers are cleared first, then connected blocks are cleared in subsequent passes
 - This creates proper cascading where blocks disappear layer by layer
 - Prevents all connected blocks from disappearing instantly
"""

from collections import deque
from swordfighting_new.util.debug import log
from swordfighting_new.mechanics.cascade import CascadeManager

# Toggle for debugging - kept simple
ENABLE_DEBUG = True


class BreakerManager:
    def __init__(self, board, debug: bool = False):
        self.board = board
        self.debug = debug  # enables extra validation/logging
        # Stats (reset each chain invocation)
        self.last_chain_results = None  # (chains, total, per_pass) or None
        self.last_pass_stats = None  # stats dict for most recent pass
        # Use dedicated cascade manager
        self.cascade_manager = CascadeManager(board)
        # Track spaces cleared during current chain for proper cascade logic
        self.recently_cleared_spaces = set()  # (x, y) positions cleared in this chain
        # Track which colors are cascading from each position
        self.cascade_colors = {}  # (x, y) -> color mapping
        # Track cascade state to prevent premature breaker activation
        self.cascade_in_progress = False  # True when cascade is still settling

    def reset_chain_tracking(self):
        """Reset the tracking of recently cleared spaces for a new chain."""
        self.recently_cleared_spaces.clear()
        self.cascade_colors.clear()
        self.last_chain_results = None
        self.last_pass_stats = None
        self.cascade_in_progress = False

    def apply_breakers(self):
        """Scan board, activate breakers, clear matching color regions progressively.

        NEW BEHAVIOR (Phase 1): Only clears ONE breaker group per call.
        This enables proper multi-chain combos where each group clears separately.

        Progressive clearing behavior:
        1. First pass: Clear only triggered breakers
        2. Subsequent passes: Clear blocks adjacent to recently cleared spaces

        This creates the proper cascading effect where blocks are cleared
        layer by layer rather than all at once.

        Returns number of blocks cleared. If zero, no state change.
        """
        # Continue cascade clearing if in progress
        if self.cascade_in_progress:
            # Only continue cascade clearing if we have recently cleared spaces
            if self.recently_cleared_spaces:
                return self._apply_cascade_clearing()
            else:
                # No more cascade clearing to do, cascade is complete
                self.cascade_in_progress = False
                # Don't return here - check for new breakers below

        # PHASE 1 CHANGE: Get only the FIRST breaker group, not all of them
        triggered_breakers = self._find_first_triggered_breaker_group()

        if triggered_breakers:
            # Store the full region that would be cleared for stats calculation BEFORE clearing
            all_cleared_positions = self._get_full_clear_region(triggered_breakers)

            if ENABLE_DEBUG:
                print(f"[DEBUG] About to calculate stats for positions: {all_cleared_positions}")

            # Calculate stats before clearing (this provides attack generation data)
            self._calculate_pass_stats(all_cleared_positions, triggered_breakers)

            if ENABLE_DEBUG:
                print(f"[DEBUG] Calculated stats: {self.last_pass_stats}")

            # For the first breaker trigger, return the total that will be cleared for stats
            # This maintains compatibility with existing tests and attack generation
            total_would_clear = len(all_cleared_positions)

            # Actually perform progressive clearing (just clear breakers this pass)
            actual_cleared = self._clear_breakers(triggered_breakers)
            if actual_cleared > 0:
                self.cascade_in_progress = True  # Start cascade sequence

            # Return total for stats/test compatibility, but only clear breakers this pass
            return total_would_clear
        else:
            # No breakers triggered
            return 0

    # ------------------------------------------------------------------
    # Chain driver
    # ------------------------------------------------------------------
    def apply_breaker_chain(self, max_passes: int | None = None):
        """Run repeated breaker passes until none clear or max_passes reached.

        Args:
            max_passes: Optional cap on number of passes (useful for tests or
                        debugging infinite loops).

        Returns:
            (chain_count, total_cleared, per_pass_clears)

        chain_count: number of *successful* passes (each >0 clears)
        total_cleared: cumulative blocks removed
        per_pass_clears: list of counts per successful pass
        """
        # Reset recently cleared spaces at start of chain
        self.recently_cleared_spaces = set()
        self.cascade_in_progress = False

        per_pass = []
        total = 0
        passes = 0

        while True:
            if max_passes is not None and passes >= max_passes:
                break

            # PHASE 1 CHANGE: Check if any breakers are triggered for a new pass
            # Use the new has_pending_breakers() method for proper termination
            if not self.has_pending_breakers() and not self.cascade_in_progress:
                break  # No more breakers to trigger and no cascade in progress

            cleared = self.apply_breakers()
            if cleared <= 0:
                break

            # If this is a new breaker pass (not continuation of cascade), start new pass
            if not self.cascade_in_progress or len(per_pass) == 0:
                per_pass.append(cleared)
                passes += 1
            else:
                # Add to current pass if we're continuing cascade clearing
                per_pass[-1] += cleared

            total += cleared

            # If we started a cascade, complete it before allowing new breaker passes
            if self.cascade_in_progress:
                while self.cascade_in_progress:
                    cascade_cleared = self.apply_breakers()
                    if cascade_cleared > 0:
                        per_pass[-1] += cascade_cleared
                        total += cascade_cleared
                    else:
                        break  # cascade clearing is done

            # Apply gravity between breaker passes
            self.cascade_manager.apply_full()

        # Store for external consumers (UI, scoring)
        self.last_chain_results = (passes, total, per_pass)
        return passes, total, per_pass

    # ------------------------------------------------------------------
    # Public cascade methods (delegate to CascadeManager)
    # ------------------------------------------------------------------
    def cascade(self):
        """Apply full gravity/cascade after a clear."""
        return self.cascade_manager.apply_full()

    def cascade_step(self, mode: str = "step") -> int:
        """Perform a single incremental gravity step.

        Args:
            mode: "step" moves blocks down one space if possible
                  "fast" performs full column compression

        Returns:
            int: number of individual block movements performed this step.
        """
        if mode == "fast":
            return self.cascade_manager.apply_full()
        else:
            return self.cascade_manager.apply_step()

    def cascade_full_stepwise(self, mode: str = "step", max_iters: int | None = None) -> int:
        """Run repeated cascade_step calls until stable or cap reached.

        Args:
            max_iters: optional safety cap on iterations.
            mode: "step" or "fast" forwarded to cascade_step.
        Returns:
            total moved block count across iterations.
        """
        if mode == "fast":
            return self.cascade_manager.apply_full()
        else:
            return self.cascade_manager.apply_until_stable(max_iters or 100)

    # --- helpers ----------------------------------------------------
    def _get_full_clear_region(self, triggered_breakers):
        """Get all positions that would be cleared by the triggered breakers (for stats calculation)."""
        all_positions = set()

        for x, y, color in triggered_breakers:
            # Add the breaker position
            all_positions.add((x, y))

            # Find all connected blocks of the same color using flood fill
            flood_region = set()
            self._flood_color_for_stats(x, y, color, flood_region)
            all_positions.update(flood_region)

        return all_positions

    def _flood_color_for_stats(self, start_x, start_y, color, acc):
        """Flood fill to find all blocks that would be cleared (for stats calculation only)."""
        stack = [(start_x, start_y)]

        while stack:
            x, y = stack.pop()
            if (x, y) in acc:
                continue
            if not self.board.is_in_bounds(x, y):
                continue

            cell = self.board.get_piece(x, y)
            # Check if this cell would be cleared
            if self._color_key(cell) != color:
                continue

            acc.add((x, y))
            # Add adjacent cells to check
            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                stack.append((x + dx, y + dy))

    def _calculate_pass_stats(self, cleared_positions, triggered_breakers):
        """Calculate pass statistics for attack generation.

        This must calculate stats for the FULL region that will be cleared,
        regardless of progressive clearing steps.
        """
        if not cleared_positions:
            self.last_pass_stats = {}
            return

        # Count sprinkles (individual blocks not part of rectangles)
        rectangles = self._find_rectangles_in_region(cleared_positions)
        rectangle_positions = set()
        for rect in rectangles:
            for x in range(rect['minx'], rect['minx'] + rect['width']):
                for y in range(rect['miny'], rect['miny'] + rect['height']):
                    rectangle_positions.add((x, y))

        # Sprinkles = blocks cleared that are NOT part of any rectangle
        sprinkle_positions = cleared_positions - rectangle_positions
        sprinkles = len(sprinkle_positions)

        # Count breakers vs normal blocks
        breaker_count = len(triggered_breakers)
        normal_count = len(cleared_positions) - breaker_count

        # Store stats in format expected by original attack system
        self.last_pass_stats = {
            'sprinkles': sprinkles,
            'rectangles': rectangles,
            'breaker_cleared': breaker_count,
            'normal_cleared': normal_count,
            'total_cleared': len(cleared_positions)
        }

        if ENABLE_DEBUG:
            print(f"[BreakerManager] Calculated stats: rectangles={len(rectangles)}, sprinkles={sprinkles}")
            print(f"[BreakerManager] Full stats: {self.last_pass_stats}")

    def _find_rectangles_in_region(self, positions):
        """Find rectangular clusters within the cleared positions using optimal algorithm."""
        if not positions:
            return []

        if ENABLE_DEBUG:
            print(f"[DEBUG] Finding rectangles in positions: {positions}")

        # Convert to sorted list for deterministic processing (bottom-left to top-right)
        sorted_positions = sorted(positions, key=lambda p: (p[1], p[0]))  # sort by y, then x

        # Find all possible rectangles and choose the optimal partitioning
        all_possible_rects = self._find_all_possible_rectangles(positions)

        if ENABLE_DEBUG:
            print(f"[DEBUG] Found {len(all_possible_rects)} possible rectangles")
            for rect in all_possible_rects:
                print(f"[DEBUG]   Possible: {rect['width']}x{rect['height']} at ({rect['minx']}, {rect['miny']})")

        # Find optimal non-overlapping set of rectangles
        optimal_rectangles = self._find_optimal_rectangle_partition(positions, all_possible_rects)

        if ENABLE_DEBUG:
            print(f"[DEBUG] Final rectangles: {optimal_rectangles}")

        return optimal_rectangles

    def _find_largest_rectangle_from(self, start_x, start_y, available_positions):
        """Find the largest rectangle starting from the given position."""
        best_rect = None
        best_area = 0

        if ENABLE_DEBUG:
            print(f"[DEBUG] Looking for rectangle from ({start_x}, {start_y}) in {available_positions}")

        # Try different rectangle sizes
        for width in range(1, 5):  # reduced limit for testing
            for height in range(1, 5):
                # Check if this rectangle fits
                valid = True
                positions_to_check = []
                # Build rectangle by going across X first, then up Y (towards higher Y values)
                for y in range(start_y, start_y + height):
                    for x in range(start_x, start_x + width):
                        positions_to_check.append((x, y))
                        if (x, y) not in available_positions:
                            valid = False
                            break
                    if not valid:
                        break

                if ENABLE_DEBUG and width == 2 and height == 2:
                    print(f"[DEBUG] Checking 2x2 from ({start_x}, {start_y}): positions {positions_to_check}, valid: {valid}")

                if valid:
                    area = width * height
                    if ENABLE_DEBUG and width >= 2 and height >= 2:
                        print(f"[DEBUG] Found valid {width}x{height} rectangle (area {area}) at ({start_x}, {start_y})")
                    if area > best_area and width >= 2 and height >= 2:
                        best_area = area
                        best_rect = {
                            'width': width,
                            'height': height,
                            'size': area,
                            'minx': start_x,
                            'miny': start_y  # Bottom-left corner of rectangle
                        }
                        if ENABLE_DEBUG:
                            print(f"[DEBUG] New best rectangle: {best_rect}")

        if ENABLE_DEBUG:
            print(f"[DEBUG] Final best rectangle from ({start_x}, {start_y}): {best_rect}")
        return best_rect

    def _find_all_possible_rectangles(self, positions):
        """Find all possible rectangles that can be formed from the given positions."""
        positions_set = set(positions)
        possible_rectangles = []

        # Try every position as a potential bottom-left corner
        for start_x, start_y in positions:
            # Try all possible rectangle sizes from this corner
            max_width = 0
            max_height = 0

            # Find maximum possible dimensions
            for test_x in range(start_x, start_x + 10):  # reasonable limit
                if (test_x, start_y) not in positions_set:
                    break
                max_width = test_x - start_x + 1

            for test_y in range(start_y, start_y + 10):  # reasonable limit
                if (start_x, test_y) not in positions_set:
                    break
                max_height = test_y - start_y + 1

            # Try all combinations up to max dimensions
            for width in range(2, max_width + 1):
                for height in range(2, max_height + 1):
                    # Check if this rectangle is completely filled
                    valid = True
                    rect_positions = []
                    for x in range(start_x, start_x + width):
                        for y in range(start_y, start_y + height):
                            if (x, y) not in positions_set:
                                valid = False
                                break
                            rect_positions.append((x, y))
                        if not valid:
                            break

                    if valid:
                        possible_rectangles.append({
                            'width': width,
                            'height': height,
                            'size': width * height,
                            'minx': start_x,
                            'miny': start_y,
                            'positions': set(rect_positions)
                        })

        return possible_rectangles

    def _find_optimal_rectangle_partition(self, all_positions, possible_rectangles):
        """Find the optimal non-overlapping set of rectangles that maximizes coverage."""
        all_positions_set = set(all_positions)

        # Sort rectangles by area (largest first) for greedy optimization
        sorted_rects = sorted(possible_rectangles, key=lambda r: r['size'], reverse=True)

        # Greedy algorithm: pick largest non-overlapping rectangles
        selected_rectangles = []
        covered_positions = set()

        for rect in sorted_rects:
            # Check if this rectangle overlaps with already selected ones
            if not rect['positions'].intersection(covered_positions):
                selected_rectangles.append({
                    'width': rect['width'],
                    'height': rect['height'],
                    'size': rect['size'],
                    'minx': rect['minx'],
                    'miny': rect['miny']
                })
                covered_positions.update(rect['positions'])

        return selected_rectangles

    def _is_breaker(self, cell):
        return hasattr(cell, 'is_breaker') and getattr(cell, 'is_breaker')

    def _color_key(self, cell):
        """Return color key for matching: only non-garbage blocks have a color."""
        if cell is None or cell == self.board.EMPTY:
            return None
        if hasattr(cell, 'is_garbage') and getattr(cell, 'is_garbage'):
            return None
        if not hasattr(cell, 'color'):
            return None
        return cell.color

    def _find_triggered_breakers(self):
        """Find all breakers that have at least one same-color orthogonal neighbor."""
        triggered = []
        h = self.board.HEIGHT
        w = self.board.WIDTH

        for x in range(w):
            for y in range(h):
                cell = self.board.get_piece(x, y)
                if not self._is_breaker(cell):
                    continue
                color = getattr(cell, 'color', None)
                if color is None:
                    continue

                # Check for same-color orthogonal neighbors
                neighbors = [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]
                has_matching_neighbor = False
                for nx, ny in neighbors:
                    if not self.board.is_in_bounds(nx, ny):
                        continue
                    ncell = self.board.get_piece(nx, ny)
                    if self._color_key(ncell) == color:
                        has_matching_neighbor = True
                        break

                if has_matching_neighbor:
                    triggered.append((x, y, color))

        return triggered

    def _find_first_triggered_breaker_group(self):
        """PHASE 1: Find only the FIRST triggered breaker group to enable proper multi-chain.

        Returns a list of breakers that are connected and should be cleared together.
        This prevents flood-fill clearing of all breakers simultaneously.
        """
        h = self.board.HEIGHT
        w = self.board.WIDTH

        # Find first triggered breaker
        for x in range(w):
            for y in range(h):
                cell = self.board.get_piece(x, y)
                if not self._is_breaker(cell):
                    continue
                color = getattr(cell, 'color', None)
                if color is None:
                    continue

                # Check for same-color orthogonal neighbors
                neighbors = [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]
                has_matching_neighbor = False
                for nx, ny in neighbors:
                    if not self.board.is_in_bounds(nx, ny):
                        continue
                    ncell = self.board.get_piece(nx, ny)
                    if self._color_key(ncell) == color:
                        has_matching_neighbor = True
                        break

                if has_matching_neighbor:
                    # Found first triggered breaker, now find all connected breakers of same color
                    return self._find_connected_breaker_group(x, y, color)

        return []  # No triggered breakers found

    def _find_connected_breaker_group(self, start_x, start_y, color):
        """Find all breakers connected to the starting breaker of the same color."""
        group = []
        visited = set()
        stack = [(start_x, start_y)]

        while stack:
            x, y = stack.pop()
            if (x, y) in visited:
                continue
            if not self.board.is_in_bounds(x, y):
                continue

            cell = self.board.get_piece(x, y)
            if not self._is_breaker(cell):
                continue
            if getattr(cell, 'color', None) != color:
                continue

            visited.add((x, y))
            group.append((x, y, color))

            # Check orthogonal neighbors for more breakers of same color
            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                nx, ny = x + dx, y + dy
                if (nx, ny) not in visited:
                    stack.append((nx, ny))

        return group

    def has_pending_breakers(self):
        """PHASE 1: Check if there are any more breakers that could be triggered.

        This is used by ChainRunner to determine if chain resolution should continue.
        """
        return len(self._find_triggered_breakers()) > 0

    # Phase 2: Enhanced gravity coordination
    def ensure_gravity_settled(self) -> bool:
        """Ensure gravity is fully settled before allowing next breaker pass.

        Returns:
            bool: True if gravity is settled, False if still settling
        """
        if self.cascade_in_progress:
            return False

        # Check if cascade manager reports stability
        if hasattr(self.cascade_manager, 'is_stable'):
            return self.cascade_manager.is_stable()

        return True  # Assume stable if no cascade manager available

    def wait_for_settlement(self) -> bool:
        """Phase 2: Wait for proper gravity settlement.

        This method coordinates with gravity to ensure proper
        settlement before proceeding to next breaker detection.

        Returns:
            bool: True when settlement is complete
        """
        # Apply any remaining gravity steps until stable
        attempts = 0
        max_attempts = 10  # Safety limit

        while not self.ensure_gravity_settled() and attempts < max_attempts:
            moved = self.cascade_step(mode='fast')
            if moved == 0:
                break
            attempts += 1

        return self.ensure_gravity_settled()

    def _clear_breakers(self, triggered_breakers):
        """Clear only the triggered breakers (progressive clearing first pass)."""
        cleared = 0
        for x, y, color in triggered_breakers:
            cell = self.board.get_piece(x, y)
            if cell != self.board.EMPTY:
                self.board.set_piece(x, y, self.board.EMPTY)
                self.recently_cleared_spaces.add((x, y))
                # Track the color that was cleared from this position
                self.cascade_colors[(x, y)] = color
                cleared += 1

        # Apply gravity after clearing breakers
        # if cleared > 0:
        #     self.cascade_manager.apply_full()

        if self.debug:
            log('BREAK', f"cleared {cleared} breakers")
        return cleared

    def _apply_cascade_clearing(self):
        """Clear blocks adjacent to recently cleared spaces (progressive clearing subsequent passes).

        Only clears blocks that match the color of the original breaker that started the cascade.
        """
        new_clears = set()
        new_cascade_colors = {}

        # For each recently cleared space, check adjacent blocks
        for cx, cy in self.recently_cleared_spaces:
            # Get the color that was cascading from this position
            cascading_color = self.cascade_colors.get((cx, cy))
            if cascading_color is None:
                continue  # No color info, skip this position

            neighbors = [(cx-1,cy),(cx+1,cy),(cx,cy-1),(cx,cy+1)]
            for nx, ny in neighbors:
                if not self.board.is_in_bounds(nx, ny):
                    continue
                if (nx, ny) in self.recently_cleared_spaces:
                    continue  # Already cleared
                if (nx, ny) in new_clears:
                    continue  # Already marked for clearing

                ncell = self.board.get_piece(nx, ny)
                if ncell == self.board.EMPTY:
                    continue
                if hasattr(ncell, 'is_garbage') and getattr(ncell, 'is_garbage'):
                    continue  # Don't clear garbage
                if hasattr(ncell, 'is_breaker') and getattr(ncell, 'is_breaker'):
                    continue  # Don't cascade-clear breakers (they trigger separately)

                # Get the neighbor's color
                neighbor_color = self._color_key(ncell)

                # Only clear if the neighbor matches the cascading color
                if neighbor_color == cascading_color:
                    new_clears.add((nx, ny))
                    new_cascade_colors[(nx, ny)] = cascading_color

        # Clear the new blocks
        cleared = len(new_clears)
        for x, y in new_clears:
            self.board.set_piece(x, y, self.board.EMPTY)

        # Update recently cleared spaces and colors for next pass
        self.recently_cleared_spaces = new_clears
        self.cascade_colors = new_cascade_colors

        # If no more blocks to cascade clear, mark cascade as complete
        if cleared == 0:
            self.cascade_in_progress = False

        if self.debug:
            log('BREAK', f"cascade cleared {cleared} blocks")
        return cleared

    def _flood_color(self, x, y, color, acc):
        """Flood fill algorithm for color matching (used in old implementation)."""
        if (x, y) in acc:
            return
        q = deque([(x, y)])
        while q:
            cx, cy = q.popleft()
            if (cx, cy) in acc:
                continue
            if not self.board.is_in_bounds(cx, cy):
                continue
            cell = self.board.get_piece(cx, cy)
            # Only match exact color; breakers of other colors ignored.
            if self._color_key(cell) != color:
                continue
            acc.add((cx, cy))
            q.extend([(cx-1,cy),(cx+1,cy),(cx,cy-1),(cx,cy+1)])

# End of breaker.py
