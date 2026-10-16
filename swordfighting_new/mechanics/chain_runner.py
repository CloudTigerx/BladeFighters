"""chain_runner.py - Frame-step breaker chain resolution.

Separates breaker clearing and gravity cascade across update cycles so the
player can (later) see intermediate board states instead of instant full-chain.

States:
  idle -> (start) -> breaker_pass -> cascade -> breaker_pass ... -> done

Usage:
    runner = BreakerChainRunner(board, breakers)
    runner.start()
    # each frame in update loop:
    if runner.active:
        runner.update()
        if runner.finished:
            chains, total, per_pass = runner.results
            # spawn next piece
"""
from __future__ import annotations

class BreakerChainRunner:
    def __init__(self, board, breaker_manager, frame_delay: int = 0, cascade_mode: str = 'step'):
        self.board = board
        self.breakers = breaker_manager
        self.frame_delay = max(0, frame_delay)
        # cascade_mode: 'step' (incremental for animation), 'fast' (instant settle)
        self.cascade_mode = cascade_mode
        self.state = 'idle'
        self.pending_delay = 0
        self.chain_count = 0
        self.total_cleared = 0
        # Separate totals so callers can ignore breaker blocks if desired.
        self.total_normal_cleared = 0
        self.total_breaker_cleared = 0
        self.per_pass = []  # cleared count per pass (breaker-only, no cascade)
        self.per_pass_cascade = []  # cascade clearing per pass
        self.pass_stats_history = []  # list of stats dicts captured each breaker pass
        self.finished = False
        # Phase 3: Enhanced statistics tracking
        self.current_pass_breaker_clear = 0
        self.current_pass_cascade_clear = 0
        # Visual ordering: during an in-progress cascade clearing, alternate
        # gravity/clear so unsupported pieces can visibly fall between clears.
        self._cascade_next_action: str = 'gravity'  # 'gravity' | 'clear'
        # Accumulate per-pass statistics across cascade clear waves. The breaker
        # manager overwrites last_pass_stats on each apply_breakers() call; we
        # merge subsequent cascade-wave stats into the current pass's stats.
        self._current_pass_stats = None

    def _merge_pass_stats(self, base: dict | None, incoming: dict | None) -> dict | None:
        if base is None:
            if incoming is None:
                return None
            return dict(incoming)
        if not incoming:
            return base

        # Sum known numeric counters.
        for k in ('sprinkles', 'normal_cleared', 'breaker_cleared', 'garbage_removed'):
            try:
                base[k] = int(base.get(k, 0) or 0) + int(incoming.get(k, 0) or 0)
            except Exception:
                pass

        # Append rectangle entries.
        try:
            base_rects = list(base.get('rectangles', []) or [])
            inc_rects = list(incoming.get('rectangles', []) or [])
            if inc_rects:
                base['rectangles'] = base_rects + inc_rects
        except Exception:
            pass

        return base

    # Properties -----------------------------------------------------
    @property
    def active(self):
        return self.state != 'idle' and not self.finished

    @property
    def results(self):
        """Phase 3: Enhanced results with separate breaker and cascade statistics."""
        if not self.finished:
            return None
        # Return enhanced results tuple
        return {
            'chains': self.chain_count,
            'total_cleared': self.total_cleared,
            'per_pass_breaker': list(self.per_pass),
            'per_pass_cascade': list(self.per_pass_cascade),
            'per_pass_combined': [b + c for b, c in zip(self.per_pass, self.per_pass_cascade)],
            'pass_stats': self.get_pass_stats()
        }

    # Control --------------------------------------------------------
    def start(self):
        """Initialize a new breaker chain run.

        Resets counters, transitions to first breaker pass, and applies the
        configured frame delay (if any) so that logic does not execute in the
        same frame the runner was started (useful for future animations).
        """
        if self.active:
            return
        # Reset tracking for new chain
        self.breakers.reset_chain_tracking()

        # Phase 3: Enhanced initialization
        self.chain_count = 0
        self.total_cleared = 0
        self.total_normal_cleared = 0
        self.total_breaker_cleared = 0
        self.per_pass.clear()
        self.per_pass_cascade.clear()
        self.pass_stats_history.clear()
        self.current_pass_breaker_clear = 0
        self.current_pass_cascade_clear = 0
        self._cascade_next_action = 'gravity'
        self._current_pass_stats = None
        self.finished = False
        self.state = 'breaker_pass'
        # Ensure breakers clear immediately on the next update for correct visuals
        self.pending_delay = 0

    def get_pass_stats(self):
        """Return a copy of stats gathered per breaker pass."""
        return list(self.pass_stats_history)

    # Phase 3: Legacy compatibility method
    def get_legacy_results(self):
        """Return results in the old (chains, total, per_pass) format for compatibility."""
        if not self.finished:
            return None
        # Use combined totals for backward compatibility
        combined_per_pass = [b + c for b, c in zip(self.per_pass, self.per_pass_cascade)]
        return (self.chain_count, self.total_cleared, combined_per_pass)

    # Phase 2: Enhanced gravity settlement detection
    def _is_board_stable(self) -> bool:
        """Check if board is truly stable with no floating blocks.

        This provides better settlement detection than just checking
        if gravity moves returned 0, by also validating board state.

        Returns:
            bool: True if board is stable and ready for next breaker pass
        """
        # Prefer cascade manager's stability check.
        # NOTE: Stability is defined by cascade's current gravity rules.
        if hasattr(self.breakers, 'cascade_manager'):
            try:
                return bool(self.breakers.cascade_manager.is_stable())
            except Exception:
                return True

        # Fallback: if we can't reason about stability, don't deadlock the chain.
        return True

    def _manual_stability_check(self) -> bool:
        """Manual check for board stability as fallback."""
        return True

    # Phase 2: Gravity settlement coordination
    def wait_for_settlement(self) -> bool:
        """Wait for gravity to fully settle before proceeding.

        This method can be called to ensure proper timing between
        breaker passes and gravity settlement.

        Returns:
            bool: True if settlement is complete, False if still settling
        """
        if not self._is_board_stable():
            return False

        # Additional validation: ensure no cascade is in progress
        if hasattr(self.breakers, 'cascade_in_progress') and self.breakers.cascade_in_progress:
            return False

        return True

    # Update loop ----------------------------------------------------
    def update(self):
        if not self.active:
            return
        if self.pending_delay > 0:
            self.pending_delay -= 1
            return
        if self.state == 'breaker_pass':
            # Phase 3: Start new pass tracking
            self.current_pass_breaker_clear = 0
            self.current_pass_cascade_clear = 0

            marked = self.breakers.apply_breakers()  # Now marks blocks instead of clearing them
            if marked <= 0:
                self.state = 'done'
                self.finished = True
                return

            # Phase 3: Track breaker clearing separately
            self.current_pass_breaker_clear = marked
            self.chain_count += 1
            self.total_cleared += marked
            self.per_pass.append(marked)

            stats = getattr(self.breakers, 'last_pass_stats', None)
            if stats:
                # Store a mutable stats dict we can merge cascade-wave clears into.
                stats_copy = dict(stats)
                self.pass_stats_history.append(stats_copy)
                self._current_pass_stats = stats_copy
                try:
                    self.total_normal_cleared += int(stats.get('normal_cleared', 0) or 0)
                except Exception:
                    pass
                try:
                    self.total_breaker_cleared += int(stats.get('breaker_cleared', 0) or 0)
                except Exception:
                    pass
                # debug logging removed
            else:
                # Ensure later cascade stats (if any) have somewhere to merge.
                self._current_pass_stats = None
            self.state = 'cascade'
            # After breaker pop, show gravity first so unsupported blocks fall
            # before subsequent cascade clear waves.
            self._cascade_next_action = 'gravity'
            self.pending_delay = self.frame_delay
        elif self.state == 'cascade':
            if self.cascade_mode == 'fast':
                # Phase 3: Enhanced cascade tracking
                initial_cascade_state = self.breakers.cascade_in_progress
                moved = self.breakers.cascade_full_stepwise(mode='fast')

                # Continue cascade clearing if in progress
                if self.breakers.cascade_in_progress:
                    # In fast mode, alternate a gravity settle with a clear wave.
                    if getattr(self, '_cascade_next_action', 'gravity') == 'gravity':
                        _ = self.breakers.cascade_step(mode='fast')
                        self._cascade_next_action = 'clear'
                    else:
                        cascade_cleared = self.breakers.apply_breakers()
                        if cascade_cleared > 0:
                            # Phase 3: Track cascade clearing separately
                            self.current_pass_cascade_clear += cascade_cleared
                            self.total_cleared += cascade_cleared
                            stats = getattr(self.breakers, 'last_pass_stats', None)
                            if stats:
                                # Merge cascade-wave clear stats into this pass for attack generation.
                                if self._current_pass_stats is None:
                                    stats_copy = dict(stats)
                                    self.pass_stats_history.append(stats_copy)
                                    self._current_pass_stats = stats_copy
                                else:
                                    self._merge_pass_stats(self._current_pass_stats, stats)
                                try:
                                    self.total_normal_cleared += int(stats.get('normal_cleared', 0) or 0)
                                except Exception:
                                    pass
                                try:
                                    self.total_breaker_cleared += int(stats.get('breaker_cleared', 0) or 0)
                                except Exception:
                                    pass
                        self._cascade_next_action = 'gravity'

                # Phase 3: Enhanced settlement detection and coordination
                if moved == 0 and not self.breakers.cascade_in_progress:
                    # Finalize current pass statistics
                    self.per_pass_cascade.append(self.current_pass_cascade_clear)

                    # Ensure board is truly stable before proceeding
                    if self._is_board_stable():
                        # removed external assertions/loggers
                        self.state = 'breaker_pass'
                        self.pending_delay = self.frame_delay
                    else:
                        # Force additional gravity step if instability detected
                        moved = self.breakers.cascade_step(mode='fast')
                else:
                    # Throttle fast-cascade visual updates
                    self.pending_delay = self.frame_delay
            else:  # step mode
                # Step mode: alternate gravity and clear waves during an active cascade.
                if self.breakers.cascade_in_progress:
                    if getattr(self, '_cascade_next_action', 'gravity') == 'gravity':
                        _ = self.breakers.cascade_step(mode='step')
                        self._cascade_next_action = 'clear'
                        self.pending_delay = self.frame_delay
                    else:
                        cascade_cleared = self.breakers.apply_breakers()
                        if cascade_cleared > 0:
                            self.current_pass_cascade_clear += cascade_cleared
                            self.total_cleared += cascade_cleared
                            stats = getattr(self.breakers, 'last_pass_stats', None)
                            if stats:
                                # Merge cascade-wave clear stats into this pass for attack generation.
                                if self._current_pass_stats is None:
                                    stats_copy = dict(stats)
                                    self.pass_stats_history.append(stats_copy)
                                    self._current_pass_stats = stats_copy
                                else:
                                    self._merge_pass_stats(self._current_pass_stats, stats)
                                try:
                                    self.total_normal_cleared += int(stats.get('normal_cleared', 0) or 0)
                                except Exception:
                                    pass
                                try:
                                    self.total_breaker_cleared += int(stats.get('breaker_cleared', 0) or 0)
                                except Exception:
                                    pass
                        self._cascade_next_action = 'gravity'
                        self.pending_delay = self.frame_delay
                    # Stay in cascade state until cascade_in_progress becomes False.
                else:
                    # Apply gravity step with enhanced settlement detection
                    moved = self.breakers.cascade_step(mode='step')
                    if moved:
                        pass  # removed debug log

                    # Phase 3: Better settlement validation and pass completion
                    if moved == 0 and self._is_board_stable():
                        # Finalize current pass statistics
                        self.per_pass_cascade.append(self.current_pass_cascade_clear)

                        # removed external assertions/loggers
                        self.state = 'breaker_pass'
                        self.pending_delay = self.frame_delay
                    else:
                        # Throttle gravity step updates for visibility
                        self.pending_delay = self.frame_delay
        elif self.state == 'done':
            # Phase 3: Ensure final pass statistics are recorded
            if len(self.per_pass_cascade) < len(self.per_pass):
                # Add final cascade clear count if missing
                self.per_pass_cascade.append(self.current_pass_cascade_clear)
            self.finished = True
        else:
            # Phase 3: Handle unexpected states gracefully
            if len(self.per_pass_cascade) < len(self.per_pass):
                self.per_pass_cascade.append(self.current_pass_cascade_clear)
            self.finished = True
            self.state = 'done'