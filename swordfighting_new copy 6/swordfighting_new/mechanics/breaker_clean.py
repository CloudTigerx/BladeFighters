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
ENABLE_DEBUG = False


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

    def apply_breakers(self):
        """Scan board, activate breakers, clear matching color regions progressively.

        Progressive clearing behavior:
        1. First pass: Clear only triggered breakers
        2. Subsequent passes: Clear blocks adjacent to recently cleared spaces

        This creates the proper cascading effect where blocks are cleared
        layer by layer rather than all at once.

        Returns number of blocks cleared. If zero, no state change.
        """
        # First, check if there are any triggered breakers
        triggered_breakers = self._find_triggered_breakers()

        if triggered_breakers:
            return self._clear_breakers(triggered_breakers)
        else:
            # No breakers triggered, try cascade clearing ONLY if we have recently cleared spaces
            if self.recently_cleared_spaces:
                return self._apply_cascade_clearing()
            else:
                return 0  # No clearing to cascade from

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

        per_pass = []
        total = 0
        passes = 0
        while True:
            if max_passes is not None and passes >= max_passes:
                break
            cleared = self.apply_breakers()
            if cleared <= 0:
                break
            per_pass.append(cleared)
            total += cleared
            passes += 1
            # Perform full (instant) cascade compression between passes for logical chain detection.
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

    def _clear_breakers(self, triggered_breakers):
        """Clear only the triggered breakers (progressive clearing first pass)."""
        cleared = 0
        for x, y, color in triggered_breakers:
            cell = self.board.get_piece(x, y)
            if cell != self.board.EMPTY:
                self.board.set_piece(x, y, self.board.EMPTY)
                self.recently_cleared_spaces.add((x, y))
                cleared += 1

        if self.debug:
            log('BREAK', f"cleared {cleared} breakers")
        return cleared

    def _apply_cascade_clearing(self):
        """Clear blocks adjacent to recently cleared spaces (progressive clearing subsequent passes)."""
        to_clear = set()

        # Find blocks adjacent to recently cleared spaces
        for cx, cy in self.recently_cleared_spaces:
            neighbors = [(cx-1,cy),(cx+1,cy),(cx,cy-1),(cx,cy+1)]
            for nx, ny in neighbors:
                if not self.board.is_in_bounds(nx, ny):
                    continue
                if (nx, ny) in self.recently_cleared_spaces:
                    continue  # Already cleared

                ncell = self.board.get_piece(nx, ny)
                if ncell == self.board.EMPTY:
                    continue
                if hasattr(ncell, 'is_garbage') and getattr(ncell, 'is_garbage'):
                    continue  # Don't clear garbage

                to_clear.add((nx, ny))

        # Clear the adjacent blocks
        cleared = 0
        new_cleared_spaces = set()
        for x, y in to_clear:
            cell = self.board.get_piece(x, y)
            if cell != self.board.EMPTY:
                self.board.set_piece(x, y, self.board.EMPTY)
                new_cleared_spaces.add((x, y))
                cleared += 1

        # Update recently cleared spaces for next pass
        self.recently_cleared_spaces = new_cleared_spaces

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
