"""session.py - MatchSession orchestrates two fighters and attack exchange.

Responsibilities:
 - Own player + enemy fighters
 - Apply player intents each frame
 - Tick both fighters
 - Exchange outbound/inbound attacks
 - Expose snapshot incl. scoring
"""
from __future__ import annotations
from typing import Dict, Any
from typing import Tuple
import os
import random
import re
import time

from swordfighting_new.mechanics.timing import DEFAULT_TIMING
from swordfighting_new.fighters.player import PlayerFighter
from swordfighting_new.fighters.base_fighter import BaseFighter
from swordfighting_new.mechanics.movement import PieceMover
from swordfighting_new.mechanics.gravity import GravityManager
from swordfighting_new.pieces.piece import Piece
from swordfighting_new.pieces.shared_piece_queue import create_shared_piece_queue, SharedPieceQueue
from swordfighting_new.mechanics.scoring import ScoringManager
from swordfighting_new.util.stats_recorder import get_recorder
from swordfighting_new.attacks.garbage_pattern import SwordType
from swordfighting_new.attacks import Attack, AttackKind
from swordfighting_new.util.debug import dprint, env_flag


class PassiveOpponent(BaseFighter):
    """Non-AI opponent that simply lets gravity advance pieces (no decision logic)."""
    def __init__(self, timing, **kwargs):
        super().__init__(timing, fighter_name="Enemy", **kwargs)

    def update(self):
        super().update({'move': 0, 'rotate_cw': False, 'rotate_ccw': False, 'fast': False})


class MirrorOpponent(PassiveOpponent):
    """Mirror opponent.

    Whenever the player sends attacks out, mirror sends those same attacks back
    to the player. This directly ties difficulty to the attack system's real
    outputs (no "free" pressure) and avoids complex placement AI.
    """

    def on_player_attacks(self, attacks: list[Attack], player: PlayerFighter | None = None) -> None:
        if player is None:
            return
        if getattr(self, 'defeated', False):
            return
        if not attacks:
            return

        mirrored: list[Attack] = []
        for atk in attacks:
            try:
                meta = dict(atk.meta or {})
                meta['mirror'] = True
                mirrored.append(Attack(atk.kind, int(atk.amount), delay=0, meta=meta))
            except Exception:
                pass

        if mirrored:
            player.receive_attacks(mirrored)

    def update(self):
        """Mirror Cube is intended as an invincible training dummy.

        In HP-mode, the enemy shouldn't top-out on its own board (which would
        stop mirroring and end the match). So we intentionally do *not* run the
        normal puzzle simulation here.
        """
        try:
            self.frame += 1
        except Exception:
            pass

        # Never allow the mirror dummy to enter a defeated state.
        self.defeated = False
        try:
            self.movement.defeated = False
        except Exception:
            pass

        # Keep its board empty so it cannot naturally top-out.
        try:
            self.board.clear()
        except Exception:
            pass

        # Still tick attack delays (defensive; mirror doesn't normally generate attacks).
        try:
            self.attacks.tick_all()
        except Exception:
            pass


class RubixOpponent(BaseFighter):
    """Simple placement AI opponent.

    Plans a target (orientation, x) for each spawned piece by simulating drops
    into a copied board and scoring the result with a lightweight heuristic.
    """

    def __init__(self, timing, **kwargs):
        super().__init__(timing, fighter_name="Enemy", **kwargs)
        self._plan_piece_id: int | None = None
        self._plan_target_x: int | None = None
        self._plan_target_o: int | None = None
        self._rubix_level: int = 1

        # rubix2: cache mobility/reachability results per spawned piece (perf)
        self._reach_cache_piece_id: int | None = None
        self._reach_cache_scores: Dict[Tuple[int, int], float] | None = None

        # If a plan requires the special vertical flip (0 <-> 2), avoid fast-drop
        # until the flip is achieved (helps reliability in tight columns).
        self._flip_goal_active: bool = False

        # Lightweight tactical context (updated per planned piece).
        # Used to make rubix4+ react to inbound pressure and opponent state.
        self._rubix_ctx: dict = {}

        # rubix6: dynamic weight switching.
        # - aggressive: combo-oriented (doubles->triples)
        # - survival: use rubix5-style survival weights when stack is high
        self._rubix6_mode: str = 'aggressive'

    def _update_rubix6_mode(self) -> None:
        """Update rubix6 mode based on current board height.

        Switch to survival once the stack reaches half the board height.
        Switch back to aggressive once the stack falls below a lower threshold
        (hysteresis) to avoid flip-flopping every piece.
        """
        try:
            lv = int(getattr(self, '_rubix_level', 1) or 1)
        except Exception:
            lv = 1
        if int(lv) != 6:
            return

        b = getattr(self, 'board', None)
        if b is None:
            return
        try:
            heights = list(b.get_column_heights())
            max_h = max(heights) if heights else 0
        except Exception:
            max_h = 0
        try:
            h = int(getattr(b, 'HEIGHT', 12) or 12)
        except Exception:
            h = 12

        # Thresholds are in "occupied rows" units (0..HEIGHT).
        # Default tuning (for HEIGHT=12):
        # - switch to survival at row 7
        # - return to aggression at row 5
        # These are env-overridable for tuning.
        try:
            hi_ref = int(os.getenv('BF_RUBIX6_SURVIVAL_HI', '7') or '7')
        except Exception:
            hi_ref = 7
        try:
            lo_ref = int(os.getenv('BF_RUBIX6_SURVIVAL_LO', '5') or '5')
        except Exception:
            lo_ref = 5

        # Scale thresholds if board height isn't the default 12.
        if int(h) == 12:
            hi = int(hi_ref)
            lo = int(lo_ref)
        else:
            try:
                hi = int(round(float(h) * (float(hi_ref) / 12.0)))
            except Exception:
                hi = int(hi_ref)
            try:
                lo = int(round(float(h) * (float(lo_ref) / 12.0)))
            except Exception:
                lo = int(lo_ref)

        hi = max(1, min(int(h), int(hi)))
        lo = max(0, min(int(h), int(lo)))
        if lo >= hi:
            lo = max(0, int(hi) - 1)

        cur = str(getattr(self, '_rubix6_mode', 'aggressive') or 'aggressive')

        # Optional "ESP": if a breaker payoff is imminent, allow rubix6 to keep
        # chasing the combo even slightly above the survival threshold. This
        # avoids bailing out mid-combo when a big breaker is 1-2 pieces away.
        try:
            grace_enabled = str(os.getenv('BF_RUBIX6_BREAKER_GRACE', '1') or '1').strip().lower() not in ('0', 'false', 'no', 'off')
        except Exception:
            grace_enabled = True

        # Safety cap: never keep chasing when we're very tall.
        hi_hard = min(int(h), int(hi) + 3)

        if cur == 'aggressive' and int(max_h) >= int(hi):
            delay = False
            if grace_enabled and int(max_h) < int(hi_hard):
                try:
                    delay = bool(self._rubix6_breaker_payoff_soon())
                except Exception:
                    delay = False
            if not delay:
                self._rubix6_mode = 'survival'
        elif cur == 'survival' and int(max_h) <= int(lo):
            self._rubix6_mode = 'aggressive'

    def _rubix6_breaker_payoff_soon(self) -> bool:
        """Heuristic: is a large breaker clear likely within the next few pieces?

        We use this only for rubix6 mode switching (aggressive->survival).
        If the board has a large exposed cluster of some color, and a breaker
        of that color is coming very soon, it's often correct to keep playing
        aggressive even if the stack is a bit high.
        """
        try:
            lv = int(getattr(self, '_rubix_level', 1) or 1)
        except Exception:
            lv = 1
        if int(lv) != 6:
            return False

        b = getattr(self, 'board', None)
        if b is None:
            return False

        try:
            look_n = int(os.getenv('BF_RUBIX6_BREAKER_LOOKAHEAD', '4') or '4')
        except Exception:
            look_n = 4
        look_n = max(0, min(int(look_n), 8))
        if look_n <= 0:
            return False

        try:
            # Default to "next piece" only for safety; you can widen this (e.g. 2)
            # if you want more aggressive breaker-chasing.
            max_dist = int(os.getenv('BF_RUBIX6_BREAKER_MAX_DIST', '1') or '1')
        except Exception:
            max_dist = 1
        max_dist = max(1, min(int(max_dist), int(look_n)))

        # Board signals: big cluster + surface exposure of that color.
        try:
            groups = self._largest_connected_groups_by_color(b)
        except Exception:
            groups = {}
        try:
            exposure = self._count_surface_exposure_by_color(b)
        except Exception:
            exposure = {}

        try:
            group_min = int(os.getenv('BF_RUBIX6_BREAKER_GROUP_MIN', '8') or '8')
        except Exception:
            group_min = 8
        try:
            exposure_min = int(os.getenv('BF_RUBIX6_BREAKER_EXPOSURE_MIN', '2') or '2')
        except Exception:
            exposure_min = 2
        group_min = max(2, int(group_min))
        exposure_min = max(1, int(exposure_min))

        # Upcoming breaker colors and how soon they arrive.
        soonest: dict[str, int] = {}

        def _record(color: str, dist: int) -> None:
            c = str(color or '').strip().lower()
            if c not in ('red', 'blue', 'green', 'yellow'):
                return
            d = int(dist)
            prev = soonest.get(c)
            if prev is None or d < int(prev):
                soonest[c] = d

        # next_piece is distance=1 from current.
        try:
            np = getattr(self.movement, 'next_piece', None)
        except Exception:
            np = None
        if np is not None:
            try:
                for blk in list(getattr(np, 'blocks', []) or []):
                    if bool(getattr(blk, 'is_breaker', False)):
                        _record(str(getattr(blk, 'color', '') or ''), 1)
            except Exception:
                pass

        # Then peek the shared piece queue for pieces after next_piece.
        try:
            pq = getattr(self.movement, 'piece_queue', None)
            idx = int(getattr(self.movement, 'piece_index', 0) or 0)
        except Exception:
            pq = None
            idx = 0

        if pq is not None and look_n > 1:
            try:
                specs = list(pq.preview_window(int(idx), int(look_n - 1)))
            except Exception:
                specs = []
            for i, spec in enumerate(specs):
                dist = 2 + int(i)
                try:
                    if bool(getattr(spec, 'breaker1', False)):
                        _record(str(getattr(spec, 'color1', '') or ''), dist)
                except Exception:
                    pass
                try:
                    if bool(getattr(spec, 'breaker2', False)):
                        _record(str(getattr(spec, 'color2', '') or ''), dist)
                except Exception:
                    pass

        # Decide: do we have a viable color with a big cluster AND a breaker coming soon?
        for c, dist in (soonest or {}).items():
            if int(dist) > int(max_dist):
                continue
            try:
                g = int(groups.get(c, 0) or 0)
            except Exception:
                g = 0
            try:
                ex = int(exposure.get(c, 0) or 0)
            except Exception:
                ex = 0
            if int(g) >= int(group_min) and int(ex) >= int(exposure_min):
                return True

        return False

    def set_boss_level(self, level: int | None) -> None:
        """Reuse the session's boss_level hook for Rubix difficulty tiers."""
        try:
            lv = int(level) if level is not None else 1
        except Exception:
            lv = 1
        self._rubix_level = max(1, lv)

    def update(self):
        intents = {'move': 0, 'rotate_cw': False, 'rotate_ccw': False, 'fast': False}

        try:
            p = getattr(self.movement, 'current_piece', None)
        except Exception:
            p = None

        lv = max(1, int(getattr(self, '_rubix_level', 1) or 1))

        # rubix6: update weight mode once per frame.
        if int(lv) == 6:
            try:
                self._update_rubix6_mode()
            except Exception:
                pass

        # Only steer while a piece is controllable.
        if p is not None and bool(getattr(p, 'controllable', False)):
            try:
                pid = id(p)
            except Exception:
                pid = None

            if pid is not None and pid != self._plan_piece_id:
                self._plan_piece_id = pid
                # Clear per-piece caches
                self._reach_cache_piece_id = None
                self._reach_cache_scores = None
                self._flip_goal_active = False
                tx, to = self._plan_for_piece(p)
                self._plan_target_x = tx
                self._plan_target_o = to

            tx = self._plan_target_x
            to = self._plan_target_o

            if tx is not None and to is not None:
                cur_o = int(getattr(p, 'orientation', 0) or 0) % 4
                cur_x = int(getattr(p, 'x', 0) or 0)

                try:
                    mover = getattr(self.movement, 'mover', None)
                except Exception:
                    mover = None

                # Special case (rubix2+): execute vertical flip (0 <-> 2) safely.
                # In this ruleset, PieceMover.rotate() will attempt a vertical flip only
                # when a normal rotation is blocked and the piece is vertical.
                need_vertical_flip = (cur_o in (0, 2)) and (int(to) % 4 in (0, 2)) and (cur_o != (int(to) % 4))
                if lv >= 2 and need_vertical_flip:
                    self._flip_goal_active = True
                if self._flip_goal_active and (cur_o == (int(to) % 4)):
                    # Flip achieved.
                    self._flip_goal_active = False

                # Prefer finishing rotation first (less likely to miss due to lock).
                if need_vertical_flip and lv >= 2:
                    # Move into the target column first.
                    if cur_x != int(tx):
                        intents['move'] = -1 if cur_x > int(tx) else 1
                    else:
                        try:
                            mover = getattr(self.movement, 'mover', None)
                            can_cw = bool(mover.can_rotate(p, clockwise=True, dx=0)) if mover is not None else False
                            can_ccw = bool(mover.can_rotate(p, clockwise=False, dx=0)) if mover is not None else False
                        except Exception:
                            can_cw = False
                            can_ccw = False

                        if lv >= 4:
                            # rubix4+: do not wait for a special blocked-rotation flip.
                            # Just rotate toward the target; for 0<->2 this takes two rotations
                            # (0->1->2 or 2->3->0) and avoids long "idle" soft-fall stalls.
                            cw_steps = (int(to) - cur_o) % 4
                            ccw_steps = (cur_o - int(to)) % 4
                            if cw_steps <= ccw_steps:
                                intents['rotate_cw'] = True
                            else:
                                intents['rotate_ccw'] = True
                        else:
                            # rubix2/3: trigger the vertical flip as soon as the *attempted*
                            # rotation is blocked in either direction (rotate() will then try
                            # the 0<->2 flip). Requiring both directions blocked caused stalls.
                            if not can_cw:
                                intents['rotate_cw'] = True
                            elif not can_ccw:
                                intents['rotate_ccw'] = True
                            else:
                                # Don't rotate yet (would turn horizontal). Keep descending normally.
                                intents['fast'] = False
                elif cur_o != int(to) % 4:
                    cw = (int(to) - cur_o) % 4
                    ccw = (cur_o - int(to)) % 4
                    rotate_cw = (cw <= ccw)

                    # rubix4+: if rotation is currently impossible (often due to a full adjacent column
                    # while still in hidden rows), don't spam-rotate in place while falling.
                    # Instead, move toward the target column to create space, then rotate.
                    if lv >= 4 and mover is not None:
                        try:
                            can_rot = bool(mover.can_rotate(p, clockwise=rotate_cw, dx=0))
                        except Exception:
                            can_rot = True
                        if not can_rot:
                            if cur_x != int(tx):
                                intents['move'] = -1 if cur_x > int(tx) else 1
                            else:
                                # Nudge off the blocked column to allow a later rotation.
                                try:
                                    spawn_x = int(getattr(self.movement, 'spawn_x', 3) or 3)
                                except Exception:
                                    spawn_x = 3
                                intents['move'] = -1 if cur_x >= int(spawn_x) else 1
                        else:
                            if rotate_cw:
                                intents['rotate_cw'] = True
                            else:
                                intents['rotate_ccw'] = True
                    else:
                        if rotate_cw:
                            intents['rotate_cw'] = True
                        else:
                            intents['rotate_ccw'] = True
                elif cur_x != int(tx):
                    intents['move'] = -1 if cur_x > int(tx) else 1
                else:
                    # Aligned: accelerate descent.
                    intents['fast'] = True

                # If we're committed to a flip goal, do not fast-drop until it succeeds.
                if lv >= 2 and bool(getattr(self, '_flip_goal_active', False)) and int(lv) < 4:
                    intents['fast'] = False

                # --- Entry safety (hidden rows) ---------------------------------
                # If the piece is entirely above the visible board *and blocked from
                # descending*, do not fast-drop.
                #
                # Rationale: Fast drop reduces the gravity interval to ~3 frames by
                # default. When a spawn column is near-full, a piece can become
                # grounded while still fully above-board; fast-drop then burns the
                # remaining lock/settle frames too quickly for the bot to slide/rotate
                # into a valid entry column, causing an "accidental" above-board topout.
                #
                # Note: When the piece can freely descend through the headroom, we
                # keep fast-drop enabled so Rubix bots don't look sluggish.
                try:
                    pos0 = list(p.get_block_positions())
                except Exception:
                    pos0 = []
                try:
                    all_above = bool(pos0) and all(int(y) < 0 for _x, y, _b in pos0)
                except Exception:
                    all_above = False
                if all_above:
                    grounded_above = False
                    if mover is not None:
                        try:
                            grounded_above = not bool(mover.can_move(p, 0, 1))
                        except Exception:
                            grounded_above = False

                    if grounded_above:
                        intents['fast'] = False

                    # If we're grounded while still fully above-board, we're at risk
                    # of an imminent topout. Override steering to try to find *any*
                    # move/rotation that enables downward motion.
                    if grounded_above and mover is not None:
                        def _clone_piece(src: Piece) -> Piece:
                            q = Piece(list(getattr(src, 'blocks', []) or []))
                            q.block_offsets = getattr(src, 'block_offsets', None)
                            q.orientation = int(getattr(src, 'orientation', 0) or 0) % 4
                            q.x = int(getattr(src, 'x', 0) or 0)
                            q.y = int(getattr(src, 'y', -1) or -1)
                            q.controllable = True
                            return q

                        # Prefer lateral move that makes a downward move possible.
                        best_dx = None
                        for dx in (-1, 1):
                            try:
                                tmp = _clone_piece(p)
                                if mover.move(tmp, int(dx), 0) and bool(mover.can_move(tmp, 0, 1)):
                                    best_dx = int(dx)
                                    break
                            except Exception:
                                continue

                        if best_dx is not None:
                            intents['move'] = int(best_dx)
                            intents['rotate_cw'] = False
                            intents['rotate_ccw'] = False
                        else:
                            # If no lateral shift immediately opens descent, try a rotation.
                            try:
                                tmp = _clone_piece(p)
                                if mover.rotate(tmp, clockwise=True) and bool(mover.can_move(tmp, 0, 1)):
                                    intents['rotate_cw'] = True
                                    intents['rotate_ccw'] = False
                                    intents['move'] = 0
                                else:
                                    tmp2 = _clone_piece(p)
                                    if mover.rotate(tmp2, clockwise=False) and bool(mover.can_move(tmp2, 0, 1)):
                                        intents['rotate_ccw'] = True
                                        intents['rotate_cw'] = False
                                        intents['move'] = 0
                            except Exception:
                                pass

        super().update(intents)

    def _plan_for_piece(self, piece: Piece) -> tuple[int, int]:
        """Return (target_x, target_orientation)."""
        board = self.board
        best = None
        best_tx = int(getattr(piece, 'x', 0) or 0)
        best_to = int(getattr(piece, 'orientation', 0) or 0) % 4

        try:
            next_piece = getattr(self.movement, 'next_piece', None)
        except Exception:
            next_piece = None

        lv = max(1, int(getattr(self, '_rubix_level', 1) or 1))

        # Capture opponent + inbound context once per plan so scoring can react.
        # - Spawn column is relatively "safe" (inbound avoids it), so preserving
        #   useful structures there is often correct.
        # - When inbound is ready to land soon, switch to aggressive defense.
        try:
            spawn_col = int(os.getenv('BF_SPAWN_COLUMN', str(getattr(self.movement, 'spawn_x', 3) or 3)))
        except Exception:
            try:
                spawn_col = int(getattr(self.movement, 'spawn_x', 3) or 3)
            except Exception:
                spawn_col = 3

        incoming_total = 0
        incoming_ready = False
        incoming_sprinkle = 0
        incoming_strike = 0
        try:
            ih = getattr(self, 'inbound_handler', None)
            if ih is not None:
                incoming_sprinkle = int(getattr(ih, 'pending_in_sprinkle', 0) or 0)
                incoming_strike = int(getattr(ih, 'pending_in_strike', 0) or 0)
                incoming_total = int(incoming_sprinkle) + int(incoming_strike)
                incoming_ready = bool(getattr(ih, 'has_ready_inbound', lambda: False)())
        except Exception:
            incoming_total = 0
            incoming_ready = False
            incoming_sprinkle = 0
            incoming_strike = 0

        opp_max_h = 0
        opp_top = 0
        try:
            opp = getattr(self, 'opponent', None)
            ob = getattr(opp, 'board', None) if opp is not None else None
            if ob is not None:
                oh = list(ob.get_column_heights())
                opp_max_h = max(oh) if oh else 0
                try:
                    ow = int(getattr(ob, 'WIDTH', 6) or 6)
                except Exception:
                    ow = 6
                for xx in range(max(0, int(ow))):
                    try:
                        if ob.get_piece(xx, 0) != ob.EMPTY:
                            opp_top += 1
                    except Exception:
                        continue
        except Exception:
            opp_max_h = 0
            opp_top = 0

        self._rubix_ctx = {
            'spawn_col': int(spawn_col),
            'incoming_total': int(incoming_total),
            'incoming_sprinkle': int(incoming_sprinkle),
            'incoming_strike': int(incoming_strike),
            'incoming_ready': bool(incoming_ready),
            'opp_max_h': int(opp_max_h),
            'opp_top': int(opp_top),
        }

        # rubix5+: sprinkle-awareness. Compute the opponent's likely sprinkle colors
        # (bottom 2 rows of their sword pattern) so we can build foundations that
        # convert incoming sprinkles into fuel/combos.
        if int(lv) >= 5:
            try:
                w = int(getattr(board, 'WIDTH', 6) or 6)
            except Exception:
                w = 6

            opp_counts: dict[str, int] | None = None
            try:
                opp = getattr(self, 'opponent', None)
                provider = getattr(opp, '_weapon_color_for_block', None) if opp is not None else None
                if callable(provider):
                    class _DummySprinkle:
                        inbound_kind = 'sprinkle'
                        inbound_layer = 1
                        x = 0
                        y = 0

                    opp_counts = {'red': 0, 'blue': 0, 'green': 0, 'yellow': 0}
                    dummy = _DummySprinkle()
                    for xx in range(max(1, int(w))):
                        for layer in (1, 2):
                            try:
                                dummy.x = int(xx)
                                dummy.y = 0
                                dummy.inbound_layer = int(layer)
                                c = provider(dummy)
                            except Exception:
                                c = None
                            try:
                                key = str(c or '').strip().lower()
                            except Exception:
                                key = ''
                            if key not in opp_counts:
                                continue
                            opp_counts[key] = int(opp_counts.get(key, 0) or 0) + 1
            except Exception:
                opp_counts = None

            try:
                self._rubix_ctx['opp_sprinkle_counts'] = dict(opp_counts) if isinstance(opp_counts, dict) else None
            except Exception:
                pass

        # Planning can be expensive at higher rubix levels (especially beam search).
        # Keep gameplay smooth by enforcing a soft time budget per piece.
        # You can tune this in milliseconds via BF_RUBIX_PLAN_BUDGET_MS.
        try:
            raw_budget = os.getenv('BF_RUBIX_PLAN_BUDGET_MS', None)
            if raw_budget is None:
                # Slightly larger default budget for rubix4+ so beam lookahead has
                # a chance to actually explore.
                plan_budget_ms = 10.0 if int(lv) >= 4 else 6.0
            else:
                plan_budget_ms = float(raw_budget)
        except Exception:
            plan_budget_ms = 6.0
        plan_budget_ms = max(0.0, float(plan_budget_ms))
        t0 = time.perf_counter()

        # Beam search is intentionally opt-in because it can be very CPU-heavy.
        # Enable via BF_RUBIX_BEAM_ENABLED=1.
        beam_enabled = (os.getenv('BF_RUBIX_BEAM_ENABLED', '0') == '1')

        # Allow forcing planner mode for debugging/perf isolation.
        # - BF_RUBIX_FORCE_GREEDY=1 forces rubix1 (fastest)
        # - BF_RUBIX_FORCE_LEVEL=N forces an explicit level (1..)
        # - If beam is disabled, lv>=3 will be capped to lv=2.
        effective_lv = lv
        if os.getenv('BF_RUBIX_FORCE_GREEDY', '0') == '1':
            effective_lv = 1
        else:
            try:
                force_level = os.getenv('BF_RUBIX_FORCE_LEVEL', '').strip()
            except Exception:
                force_level = ''
            if force_level:
                try:
                    effective_lv = max(1, int(force_level))
                except Exception:
                    effective_lv = effective_lv

        # rubix4+ should be "a clone + improvements" and must not silently
        # downgrade into the rubix2 planner due to missing env flags.
        if effective_lv >= 4:
            beam_enabled = True

        if effective_lv >= 3 and (not beam_enabled):
            effective_lv = 2

        # Expose computed mode for debugging + tests.
        try:
            self._debug_last_effective_lv = int(effective_lv)
            self._debug_last_beam_enabled = bool(beam_enabled)
        except Exception:
            pass

        # Optional debug profiling.
        profile = (os.getenv('BF_RUBIX_PROFILE', '0') == '1')
        iters = 0
        broke_budget = False

        # Only 2-block pieces have meaningful rotations in current rules.
        orientations = [0, 1, 2, 3] if len(getattr(piece, 'blocks', []) or []) == 2 else [0]

        reachable_scores: Dict[Tuple[int, int], float] | None = None
        if effective_lv == 2:
            try:
                reachable_scores = self._reachable_scores_for_piece(piece)
            except Exception:
                reachable_scores = None
            if not reachable_scores:
                # If reachability fails for any reason, fall back to greedy.
                effective_lv = 1
                reachable_scores = None

        # NOTE: we intentionally do not apply reachability pruning for rubix4+.
        # In practice it can exclude valid placements under the real-time movement
        # rules and hurts long-run stability.

        # Unified deadline for any deeper lookahead work.
        deadline_t: float | None = None
        if plan_budget_ms > 0.0:
            try:
                deadline_t = float(t0) + float(plan_budget_ms) / 1000.0
            except Exception:
                deadline_t = None

        # For rubix3+: do a fast pass to rank candidates, then run beam search only
        # on the best few. This avoids doing a full beam search for every (x,o).
        beam_candidates: list[tuple[float, int, int]] | None = None
        if effective_lv >= 3:
            try:
                raw_k = os.getenv('BF_RUBIX_BEAM_CANDIDATES', '').strip()
                if not raw_k:
                    # rubix5+ benefits from a slightly wider candidate set because
                    # the best survival move can look "worse" before clears resolve.
                    if int(effective_lv) >= 5:
                        k = 14
                    elif int(effective_lv) >= 4:
                        k = 10
                    else:
                        k = 8
                else:
                    k = int(raw_k)
            except Exception:
                k = 8
            k = max(1, min(int(k), 24))
            beam_candidates = []

        w = int(getattr(board, 'WIDTH', 6) or 6)

        for o in orientations:
            for x in range(w):
                iters += 1
                # Check budget occasionally to avoid perf_counter() overhead in the hot loop.
                if deadline_t is not None and (iters % 12) == 0:
                    if time.perf_counter() >= float(deadline_t):
                        broke_budget = True
                        break

                if effective_lv == 2:
                    # rubix2: mobility-aware (reachability search)
                    try:
                        score = reachable_scores.get((int(x), int(o) % 4)) if reachable_scores else None
                    except Exception:
                        score = None
                    if score is None:
                        continue
                    if best is None or score < best:
                        best = score
                        best_tx = int(x)
                        best_to = int(o)
                    continue

                # rubix1 (and rubix3+ fast-pass): score the drop.
                # For beam tiers, rank candidates based on a *post-clear* snapshot
                # so we don't filter out lifesaving immediate clears.
                if effective_lv >= 4:
                    score = self._score_after_drop_candidate(piece, x=int(x), o=int(o), resolve_steps=2)
                elif effective_lv >= 3:
                    score = self._score_after_drop_candidate(piece, x=int(x), o=int(o), resolve_steps=1)
                else:
                    score = self._score_after_drop(piece, x=int(x), o=int(o))
                if score is None:
                    continue

                if effective_lv >= 3 and beam_candidates is not None:
                    beam_candidates.append((float(score), int(x), int(o)))
                else:
                    if best is None or score < best:
                        best = score
                        best_tx = int(x)
                        best_to = int(o)

            if broke_budget:
                break

        # rubix3+: now apply bounded beam search to the best greedy candidates.
        if effective_lv >= 3 and beam_candidates:
            beam_candidates.sort(key=lambda t: t[0])
            try:
                raw_k = os.getenv('BF_RUBIX_BEAM_CANDIDATES', '').strip()
                if not raw_k:
                    if int(effective_lv) >= 5:
                        k = 14
                    elif int(effective_lv) >= 4:
                        k = 10
                    else:
                        k = 8
                else:
                    k = int(raw_k)
            except Exception:
                k = 8
            k = max(1, min(int(k), 24))
            beam_candidates = beam_candidates[:k]

            # Keep the best greedy as a fallback even if we run out of budget.
            try:
                best = float(beam_candidates[0][0])
                best_tx = int(beam_candidates[0][1])
                best_to = int(beam_candidates[0][2])
            except Exception:
                pass

            for _base_s, x, o in beam_candidates:
                if deadline_t is not None and time.perf_counter() >= float(deadline_t):
                    broke_budget = True
                    break
                score = self._score_after_drop_beam(piece, x=int(x), o=int(o), deadline_t=deadline_t)
                if score is None:
                    continue
                if best is None or score < best:
                    best = float(score)
                    best_tx = int(x)
                    best_to = int(o)

        if profile and (os.getenv('BF_RUBIX_PROFILE', '0') == '1'):
            try:
                dt_ms = (time.perf_counter() - t0) * 1000.0
                print(
                    f"[RUBIX] plan lv={lv} eff={effective_lv} beam={'1' if beam_enabled else '0'} "
                    f"iters={iters} dt_ms={dt_ms:.2f} budget_ms={plan_budget_ms:.2f}"
                )
            except Exception:
                pass

        return best_tx, best_to

    def _score_after_drop_beam(self, piece: Piece, *, x: int, o: int, deadline_t: float | None = None) -> float | None:
        """rubix3+: bounded lookahead planner (beam search).

        Uses the shared piece queue preview so the game remains random, but the
        bot can "see" the next few pieces and plan.

        We keep this deliberately lightweight:
        - Beam width is small (env-tunable)
        - Depth is small (rubix3: ~3 pieces total, rubix4+: ~5)
        - Uses survival-first heuristic score
        """
        b0 = self._simulate_place_on_copy(self.board, piece, x=int(x), o=int(o))
        if b0 is None:
            return None

        lv = max(1, int(getattr(self, '_rubix_level', 1) or 1))

        # Resolve a few combo steps so the search reasons about the post-clear board.
        b0r, cleared0 = self._simulate_combo_resolve_with_stats(b0, max_steps=4)

        # Reward clear yield explicitly. Post-clear snapshots often have no remaining
        # 2x2 clusters, so without this, the bot can undervalue lifesaving clears.
        try:
            ctx = dict(getattr(self, '_rubix_ctx', {}) or {})
        except Exception:
            ctx = {}
        try:
            incoming_total = int(ctx.get('incoming_total', 0) or 0)
        except Exception:
            incoming_total = 0
        try:
            incoming_ready = bool(ctx.get('incoming_ready', False))
        except Exception:
            incoming_ready = False
        no_inbound = (int(incoming_total) == 0) and (not bool(incoming_ready))

        clear_cell_w = 1.25
        if int(lv) >= 5 and no_inbound:
            clear_cell_w = 4.00

        # Gather upcoming pieces (excluding the current one).
        lv = max(1, int(lv))
        # rubix5+: a tiny bit more lookahead helps it stay stable during long
        # no-pressure stretches (the best "maintenance" move can be 1-2 pieces away).
        look_n = 3 if lv == 3 else (6 if lv >= 5 else (5 if lv >= 4 else 1))
        future_pieces = self._get_future_pieces(look_n)
        if not future_pieces:
            return float(self._score_board_state(b0r))

        # Critical safety: if the *next* piece would immediately top-out due to
        # spawn-overlap, this move is effectively losing right now even if there
        # are "open moves" lower on the board.
        try:
            if self._rubix_would_defeat_on_spawn(b0r, future_pieces[0]):
                return 1.0e12
        except Exception:
            pass

        try:
            raw_w = os.getenv('BF_RUBIX_BEAM_WIDTH', '').strip()
            if not raw_w:
                if int(lv) >= 5:
                    beam_w = 18
                else:
                    beam_w = 14 if int(lv) >= 4 else 10
            else:
                beam_w = int(raw_w)
        except Exception:
            beam_w = 10
        beam_w = max(1, min(int(beam_w), 40))

        # Each beam item: (score_so_far, board_state)
        # Use discounted cumulative score so nearer-term survival matters more.
        base = float(self._score_board_state(b0r)) - float(int(cleared0) * float(clear_cell_w))
        beam: list[tuple[float, object]] = [(base, b0r)]
        discount = 0.70

        # Explore future pieces
        for depth, fp in enumerate(future_pieces[:look_n], start=1):
            new_beam: list[tuple[float, object]] = []
            expansions = 0
            for score_so_far, bstate in beam:
                if deadline_t is not None and (expansions % 40) == 0:
                    try:
                        if time.perf_counter() >= float(deadline_t):
                            # Out of time: return best we've seen so far.
                            return float(min(s for s, _b in beam))
                    except Exception:
                        pass
                # Enumerate candidate placements for fp on this bstate.
                # If fp cannot spawn on this state (spawn overlap), this branch is losing.
                try:
                    if self._rubix_would_defeat_on_spawn(bstate, fp):
                        continue
                except Exception:
                    pass
                try:
                    w = int(getattr(bstate, 'WIDTH', 6) or 6)
                except Exception:
                    w = 6
                orientations = [0, 1, 2, 3] if len(getattr(fp, 'blocks', []) or []) == 2 else [0]
                for oo in orientations:
                    for xx in range(w):
                        expansions += 1
                        if deadline_t is not None and (expansions % 80) == 0:
                            try:
                                if time.perf_counter() >= float(deadline_t):
                                    return float(min(s for s, _b in beam))
                            except Exception:
                                pass
                        b2 = self._simulate_place_on_copy(bstate, fp, x=int(xx), o=int(oo))
                        if b2 is None:
                            continue

                        b2r, cleared2 = self._simulate_combo_resolve_with_stats(b2, max_steps=4)
                        s2 = float(self._score_board_state(b2r)) - float(int(cleared2) * float(clear_cell_w))
                        cum = float(score_so_far) + (discount ** float(depth)) * s2
                        new_beam.append((cum, b2r))

            if not new_beam:
                break

            # Keep best beam_w states.
            new_beam.sort(key=lambda t: t[0])
            beam = new_beam[:beam_w]

        # Best cumulative score across explored futures.
        try:
            return float(min(s for s, _b in beam))
        except Exception:
            return float(self._score_board_state(b0r))

    def _rubix_get_spawn_y(self, board) -> int:
        try:
            spawn_y = getattr(board, 'spawn_y', None)
            if spawn_y is None:
                raise ValueError('no board.spawn_y')
            return int(spawn_y)
        except Exception:
            try:
                return int(os.getenv('BF_SPAWN_Y', '-2'))
            except Exception:
                return -2

    def _rubix_spawn_piece(self, piece: Piece, board) -> Piece | None:
        """Build a spawn-positioned copy of `piece` (x/y/orientation) for `board`."""
        try:
            p = Piece(list(getattr(piece, 'blocks', []) or []))
            p.block_offsets = getattr(piece, 'block_offsets', None)
            p.orientation = int(getattr(piece, 'orientation', 0) or 0) % 4
            p.x = int(getattr(self.movement, 'spawn_x', 3) or 3)
            p.y = int(self._rubix_get_spawn_y(board))
            p.controllable = True
            return p
        except Exception:
            return None

    def _rubix_spawn_overlap_cells(self, board, spawn_piece: Piece) -> list[tuple[int, int]]:
        """Return in-bounds overlap cells for a newly spawned piece (yi >= 0)."""
        overlaps: list[tuple[int, int]] = []
        try:
            pos = list(spawn_piece.get_block_positions())
        except Exception:
            pos = []

        for x, y, _b in pos:
            try:
                xi = int(x)
                yi = int(y)
            except Exception:
                continue
            if yi < 0:
                continue
            try:
                if getattr(board, 'get_piece')(xi, yi) != getattr(board, 'EMPTY'):
                    overlaps.append((xi, yi))
            except Exception:
                continue
        return overlaps

    def _rubix_has_any_reachable_landing(self, board, piece: Piece) -> bool:
        """True if `piece` (from spawn state) can reach any in-bounds landing.

        This mirrors the real top-out condition in MovementController.update:
        if a piece becomes grounded while still above the visible board and has
        no in-bounds blocks, the player is defeated.

        We use a small BFS over (x, y, orientation) and stop at the first
        in-bounds grounded state.
        """
        try:
            w = int(getattr(board, 'WIDTH', 6) or 6)
        except Exception:
            w = 6
        try:
            h = int(getattr(board, 'HEIGHT', 12) or 12)
        except Exception:
            h = 12
        mover = PieceMover(board)

        def mk_piece(xi: int, yi: int, oi: int) -> Piece:
            p = Piece(list(getattr(piece, 'blocks', []) or []))
            p.block_offsets = getattr(piece, 'block_offsets', None)
            p.controllable = True
            p.x = int(xi)
            p.y = int(yi)
            p.orientation = int(oi) % 4
            return p

        try:
            sx = int(getattr(piece, 'x', int(getattr(self.movement, 'spawn_x', 3) or 3)) or 0)
        except Exception:
            sx = int(getattr(self.movement, 'spawn_x', 3) or 3)
        try:
            sy = int(getattr(piece, 'y', self._rubix_get_spawn_y(board)) or self._rubix_get_spawn_y(board))
        except Exception:
            sy = int(self._rubix_get_spawn_y(board))
        try:
            so = int(getattr(piece, 'orientation', 0) or 0) % 4
        except Exception:
            so = 0

        start = (sx, sy, so)
        min_y = -4
        max_y = h - 1

        from collections import deque
        q = deque([start])
        seen: set[tuple[int, int, int]] = set([start])

        while q:
            x0, y0, o0 = q.popleft()
            try:
                p0 = mk_piece(x0, y0, o0)
            except Exception:
                continue

            # If grounded and any block is in-bounds, we found a valid landing.
            try:
                if not mover.can_move(p0, 0, 1):
                    any_in_bounds = False
                    try:
                        any_in_bounds = any(getattr(board, 'is_in_bounds')(int(px), int(py)) for px, py, _b in p0.get_block_positions())
                    except Exception:
                        any_in_bounds = False
                    if any_in_bounds:
                        return True
            except Exception:
                pass

            # Lateral/rotation transitions.
            for act in ('left', 'right', 'rot_cw', 'rot_ccw'):
                try:
                    p1 = mk_piece(x0, y0, o0)
                except Exception:
                    continue
                ok = False
                try:
                    if act == 'left':
                        ok = mover.move(p1, -1, 0)
                    elif act == 'right':
                        ok = mover.move(p1, 1, 0)
                    elif act == 'rot_cw':
                        ok = mover.rotate(p1, clockwise=True)
                    elif act == 'rot_ccw':
                        ok = mover.rotate(p1, clockwise=False)
                except Exception:
                    ok = False
                if ok:
                    s2 = (int(p1.x), int(p1.y), int(p1.orientation) % 4)
                    if (min_y <= s2[1] <= max_y) and (0 <= s2[0] < w) and (s2 not in seen):
                        seen.add(s2)
                        q.append(s2)

            # Gravity transition.
            try:
                if mover.can_move(p0, 0, 1):
                    p_down = mk_piece(x0, y0, o0)
                    if mover.move(p_down, 0, 1):
                        s3 = (int(p_down.x), int(p_down.y), int(p_down.orientation) % 4)
                        if (min_y <= s3[1] <= max_y) and (0 <= s3[0] < w) and (s3 not in seen):
                            seen.add(s3)
                            q.append(s3)
            except Exception:
                pass

        return False

    def _rubix_would_defeat_on_spawn(self, board, next_piece: Piece) -> bool:
        """Mirror MovementController.spawn_new_piece_post_chain defeat rule.

        We also emulate its single "pre-defeat settle" (global snap-settle) before
        deciding that spawn-overlap is fatal.
        """
        sp = self._rubix_spawn_piece(next_piece, board)
        if sp is None:
            return False

        # Fast-path: if it can descend immediately from spawn, we are not in the
        # instant "grounded above-board" topout case.
        try:
            if PieceMover(board).can_move(sp, 0, 1):
                return False
        except Exception:
            pass

        # Most common real failure mode: the piece cannot even enter the visible
        # grid (it becomes grounded while y < 0 and has no in-bounds blocks).
        try:
            if not self._rubix_has_any_reachable_landing(board, sp):
                return True
        except Exception:
            pass

        overlaps = self._rubix_spawn_overlap_cells(board, sp)
        if not overlaps:
            return False

        # Emulate the one-time snap-settle grace, treating empty transient cells
        # of the spawned piece as solid blockers.
        try:
            b2 = board.copy()
        except Exception:
            b2 = None
        if b2 is None:
            return True

        occupied: set[tuple[int, int]] = set()
        try:
            for x, y, _b in sp.get_block_positions():
                xi = int(x)
                yi = int(y)
                if yi < 0:
                    continue
                try:
                    if getattr(b2, 'is_in_bounds')(xi, yi) and getattr(b2, 'get_piece')(xi, yi) == getattr(b2, 'EMPTY'):
                        occupied.add((xi, yi))
                except Exception:
                    continue
        except Exception:
            occupied = set()

        try:
            GravityManager(b2).apply_global_gravity(occupied_cells=occupied)
        except Exception:
            pass

        return bool(self._rubix_spawn_overlap_cells(b2, sp))

    def _get_future_pieces(self, n: int) -> list[Piece]:
        """Return up to `n` upcoming pieces from the shared queue (not mutating indices)."""
        out: list[Piece] = []
        if n <= 0:
            return out

        # First: movement.next_piece is already constructed.
        try:
            np = getattr(self.movement, 'next_piece', None)
        except Exception:
            np = None
        if np is not None:
            try:
                p0 = Piece(list(getattr(np, 'blocks', []) or []))
                p0.block_offsets = getattr(np, 'block_offsets', None)
                p0.orientation = int(getattr(np, 'orientation', 0) or 0) % 4
                p0.x = int(getattr(self.movement, 'spawn_x', 3) or 3)
                p0.y = int(getattr(np, 'y', -1) or -1)
                p0.controllable = True
                out.append(p0)
            except Exception:
                pass

        if len(out) >= n:
            return out[:n]

        # Then: peek additional specs from piece_queue without consuming.
        try:
            pq = getattr(self.movement, 'piece_queue', None)
            idx = int(getattr(self.movement, 'piece_index', 0) or 0)
        except Exception:
            pq = None
            idx = 0

        if pq is None:
            return out[:n]

        need = max(0, int(n - len(out)))
        try:
            specs = list(pq.preview_window(idx, need))
        except Exception:
            specs = []

        for spec in specs:
            try:
                out.append(Piece.from_spec(spec, int(getattr(self.movement, 'spawn_x', 3) or 3)))
            except Exception:
                continue
            if len(out) >= n:
                break

        return out[:n]

    def _simulate_combo_resolve(self, board, *, max_steps: int = 4):
        """Apply a few clear+settle steps until stable or max_steps reached."""
        try:
            b = board
            for _ in range(max(0, int(max_steps))):
                nb = b

                # Breaker clears can be very large and are important to see
                # during planning.
                try:
                    nb, _ = self._simulate_breaker_chain_resolve(nb, max_steps=2)
                except Exception:
                    pass

                nb2 = self._simulate_one_combo_step(nb)
                if nb2 is None:
                    break
                nb = nb2
                # If no further clears happened, _simulate_one_combo_step returns an identical board.
                # Detect stability by comparing string renders (cheap) to avoid deep equality.
                try:
                    if str(nb) == str(b):
                        b = nb
                        break
                except Exception:
                    pass
                b = nb
            return b
        except Exception:
            return board

    def _count_filled_cells(self, board) -> int:
        """Fast filled-cell count used for scoring clear yield during simulation."""
        try:
            w = int(getattr(board, 'WIDTH', 6) or 6)
        except Exception:
            w = 6
        try:
            h = int(getattr(board, 'HEIGHT', 12) or 12)
        except Exception:
            h = 12

        filled = 0
        try:
            for xx in range(int(w)):
                for yy in range(int(h)):
                    v = board.get_piece(int(xx), int(yy))
                    if v is None or v == board.EMPTY:
                        continue
                    filled += 1
        except Exception:
            return int(filled)
        return int(filled)

    def _simulate_combo_resolve_with_stats(self, board, *, max_steps: int = 4):
        """Like _simulate_combo_resolve, but also returns total cells cleared."""
        try:
            b = board
            cleared_total = 0
            for _ in range(max(0, int(max_steps))):
                filled_before = self._count_filled_cells(b)
                nb = b

                try:
                    nb, _ = self._simulate_breaker_chain_resolve(nb, max_steps=2)
                except Exception:
                    pass

                nb2 = self._simulate_one_combo_step(nb)
                if nb2 is None:
                    break
                nb = nb2
                filled_after = self._count_filled_cells(nb)
                try:
                    cleared_total += max(0, int(filled_before) - int(filled_after))
                except Exception:
                    pass
                try:
                    if str(nb) == str(b):
                        b = nb
                        break
                except Exception:
                    pass
                b = nb
            return b, int(cleared_total)
        except Exception:
            return board, 0

    def _score_after_drop_candidate(self, piece: Piece, *, x: int, o: int, resolve_steps: int = 1) -> float | None:
        """Fast candidate score for beam tiers.

        The beam planner only explores the best few candidates. If we rank those
        candidates on the pre-clear board, we can accidentally filter out moves
        that create immediate clears (which is exactly how a bot survives long
        idle stretches).
        """
        b0 = self._simulate_place_on_copy(self.board, piece, x=int(x), o=int(o))
        if b0 is None:
            return None

        try:
            steps = max(0, int(resolve_steps))
        except Exception:
            steps = 0
        cleared = 0
        if steps > 0:
            b0, cleared = self._simulate_combo_resolve_with_stats(b0, max_steps=steps)

        # Reward taking clears even when scoring post-clear board states.
        try:
            lv = max(1, int(getattr(self, '_rubix_level', 1) or 1))
        except Exception:
            lv = 1
        try:
            ctx = dict(getattr(self, '_rubix_ctx', {}) or {})
        except Exception:
            ctx = {}
        try:
            incoming_total = int(ctx.get('incoming_total', 0) or 0)
        except Exception:
            incoming_total = 0
        try:
            incoming_ready = bool(ctx.get('incoming_ready', False))
        except Exception:
            incoming_ready = False
        no_inbound = (int(incoming_total) == 0) and (not bool(incoming_ready))

        clear_cell_w = 1.25
        if int(lv) >= 5 and no_inbound:
            clear_cell_w = 4.00

        try:
            return float(self._score_board_state(b0)) - float(int(cleared) * float(clear_cell_w))
        except Exception:
            return None

    def _score_after_drop_reachable(self, piece: Piece, *, x: int, o: int) -> float | None:
        """Mobility-aware scoring: is (x,o) reachable from the current spawn state?

        Uses a small BFS over (x,y,orientation) with explicit "down" steps.
        If the target landing is reachable, returns its board score; otherwise None.
        """
        try:
            target_x = int(x)
            target_o = int(o) % 4
        except Exception:
            return None

        scores = self._reachable_scores_for_piece(piece)
        if not scores:
            return None
        return scores.get((target_x, target_o))

    def _reachable_scores_for_piece(self, piece: Piece) -> Dict[Tuple[int, int], float]:
        """Return best score per (x,o) among reachable landings for this piece."""
        try:
            pid = id(piece)
        except Exception:
            pid = None

        if pid is not None and pid == getattr(self, '_reach_cache_piece_id', None) and isinstance(getattr(self, '_reach_cache_scores', None), dict):
            return self._reach_cache_scores  # type: ignore

        landings = self._enumerate_reachable_landings(piece)
        scores: Dict[Tuple[int, int], float] = {}
        for st in landings or []:
            try:
                key = (int(st.get('x')), int(st.get('o')) % 4)
                val = float(st.get('score'))
            except Exception:
                continue
            prev = scores.get(key)
            if prev is None or val < prev:
                scores[key] = val

        self._reach_cache_piece_id = pid
        self._reach_cache_scores = scores
        return scores

    def _enumerate_reachable_landings(self, piece: Piece) -> list[dict]:
        """Enumerate reachable landing states and their scores.

        Returns list of dicts: {'x': int, 'y': int, 'o': int, 'score': float}
        """
        board = self.board
        mover = PieceMover(board)
        w = int(getattr(board, 'WIDTH', 6) or 6)
        h = int(getattr(board, 'HEIGHT', 12) or 12)

        def mk_piece(xi: int, yi: int, oi: int) -> Piece:
            p = Piece(list(getattr(piece, 'blocks', []) or []))
            p.block_offsets = getattr(piece, 'block_offsets', None)
            p.controllable = True
            p.x = int(xi)
            p.y = int(yi)
            p.orientation = int(oi) % 4
            return p

        try:
            sx = int(getattr(piece, 'x', 0) or 0)
            sy = int(getattr(piece, 'y', -1) or -1)
            so = int(getattr(piece, 'orientation', 0) or 0) % 4
        except Exception:
            sx, sy, so = 0, -1, 0

        start = (sx, sy, so)
        # Constrain y range we explore (hidden row down to bottom).
        min_y = -4
        max_y = h - 1

        from collections import deque

        q = deque([start])
        seen: set[tuple[int, int, int]] = set([start])
        landings: list[dict] = []

        while q:
            x0, y0, o0 = q.popleft()

            # Build a piece at this state. If it's invalid (overlapping), skip.
            try:
                p0 = mk_piece(x0, y0, o0)
            except Exception:
                continue

            # Generate lateral/rotation transitions at same y.
            for act in ('noop', 'left', 'right', 'rot_cw', 'rot_ccw'):
                try:
                    p1 = mk_piece(x0, y0, o0)
                except Exception:
                    continue
                ok = True
                if act == 'left':
                    ok = mover.move(p1, -1, 0)
                elif act == 'right':
                    ok = mover.move(p1, 1, 0)
                elif act == 'rot_cw':
                    ok = mover.rotate(p1, clockwise=True)
                elif act == 'rot_ccw':
                    ok = mover.rotate(p1, clockwise=False)
                else:
                    ok = True
                if ok:
                    s2 = (int(p1.x), int(p1.y), int(p1.orientation) % 4)
                    if (min_y <= s2[1] <= max_y) and (0 <= s2[0] < w) and (s2 not in seen):
                        seen.add(s2)
                        q.append(s2)

            # Gravity step: allow moving down by 1.
            try:
                if mover.can_move(p0, 0, 1):
                    p_down = mk_piece(x0, y0, o0)
                    if mover.move(p_down, 0, 1):
                        s3 = (int(p_down.x), int(p_down.y), int(p_down.orientation) % 4)
                        if (min_y <= s3[1] <= max_y) and (0 <= s3[0] < w) and (s3 not in seen):
                            seen.add(s3)
                            q.append(s3)
                else:
                    # Can't go down: this is a grounded/landing state. Score it.
                    b2 = None
                    try:
                        b2 = board.copy()
                    except Exception:
                        b2 = None
                    if b2 is not None:
                        try:
                            any_in_bounds = any(b2.is_in_bounds(px, py) for px, py, _blk in p0.get_block_positions())
                        except Exception:
                            any_in_bounds = False
                        if any_in_bounds:
                            try:
                                b2.place_piece(p0)
                                s = self._score_board_state(b2)
                                landings.append({'x': int(x0), 'y': int(y0), 'o': int(o0) % 4, 'score': float(s)})
                            except Exception:
                                pass
            except Exception:
                continue

        return landings



    def _score_after_drop_lookahead(self, piece: Piece, next_piece: Piece | None, *, x: int, o: int, depth: int = 1) -> float | None:
        """Evaluate a placement with a small lookahead.

        For rubix2+: try to approximate a "double combo" by:
        1) placing current piece
        2) simulating one clear+settle step (2x2 cluster removal + column compression)
        3) scoring the best placement of the next piece on that resulting board

        This avoids needing to run the full breaker/chain logic inside the bot.
        """
        b0 = self._simulate_place_on_copy(self.board, piece, x=int(x), o=int(o))
        if b0 is None:
            return None

        base_score = self._score_board_state(b0)
        if next_piece is None or depth <= 0:
            return float(base_score)

        # Simulate one "combo step": clear any 2x2 clusters and settle.
        b1 = self._simulate_one_combo_step(b0)
        if b1 is None:
            b1 = b0

        # Find best next placement.
        best_next = None
        orientations = [0, 1, 2, 3] if len(getattr(next_piece, 'blocks', []) or []) == 2 else [0]
        w = int(getattr(b1, 'WIDTH', 6) or 6)
        for o2 in orientations:
            for x2 in range(w):
                b2 = self._simulate_place_on_copy(b1, next_piece, x=int(x2), o=int(o2))
                if b2 is None:
                    continue
                s2 = self._score_board_state(b2)
                if best_next is None or s2 < best_next:
                    best_next = float(s2)

        if best_next is None:
            return float(base_score)

        # Weighting: prioritize not dying now, but bias toward setups that also look good next.
        # Higher levels care more about the lookahead term.
        lv = max(1, int(getattr(self, '_rubix_level', 1) or 1))
        look_w = min(0.25 + 0.10 * float(lv - 2), 0.55)  # rubix2=0.25, rubix4=0.45
        return float(base_score) * (1.0 - look_w) + float(best_next) * look_w

    def _simulate_place_on_copy(self, board, piece: Piece, *, x: int, o: int):
        """Return a new Board with `piece` hard-dropped and placed; None if invalid."""
        try:
            b = board.copy()
        except Exception:
            return None

        try:
            p = Piece(list(getattr(piece, 'blocks', []) or []))
            p.block_offsets = getattr(piece, 'block_offsets', None)
            p.orientation = int(o) % 4
            p.x = int(x)
            p.y = int(getattr(piece, 'y', -1) or -1)
            p.controllable = True
        except Exception:
            return None

        mover = PieceMover(b)
        if not self._can_place_piece(b, p):
            return None

        try:
            mover.hard_drop(p)
        except Exception:
            return None

        try:
            any_in_bounds = any(b.is_in_bounds(px, py) for px, py, _blk in p.get_block_positions())
        except Exception:
            any_in_bounds = False
        if not any_in_bounds:
            return None

        try:
            b.place_piece(p)
        except Exception:
            return None

        return b

    def _simulate_breaker_clear_pass(self, board):
        """Simulate a single breaker-trigger clear pass + gravity settle.

        This is a lightweight approximation of the real breaker system used
        in gameplay. It exists primarily so the planner can value breaker
        pieces and breaker-adjacent placements (which can clear large connected
        regions) rather than treating them like inert blocks.

        Returns (new_board, cleared_cells).
        """
        try:
            b = board.copy()
        except Exception:
            return None, 0

        try:
            w = int(getattr(b, 'WIDTH', 6) or 6)
        except Exception:
            w = 6
        try:
            h = int(getattr(b, 'HEIGHT', 12) or 12)
        except Exception:
            h = 12

        def _eligible_color(xx, yy):
            v = b.get_piece(int(xx), int(yy))
            if v is None or v == b.EMPTY:
                return None
            if bool(getattr(v, 'is_garbage', False)):
                return None
            if getattr(v, 'attack_state', None) is not None:
                return None
            try:
                col = str(getattr(v, 'color', '') or '').strip().lower()
            except Exception:
                col = ''
            return col or None

        def _is_breaker(xx, yy):
            v = b.get_piece(int(xx), int(yy))
            if v is None or v == b.EMPTY:
                return False
            if getattr(v, 'attack_state', None) is not None:
                return False
            return bool(getattr(v, 'is_breaker', False))

        clear_cells = set()
        visited = set()

        from collections import deque

        # Find triggered breakers (breaker with any orthogonal same-color eligible neighbor).
        for xx in range(int(w)):
            for yy in range(int(h)):
                if not _is_breaker(xx, yy):
                    continue
                c0 = _eligible_color(xx, yy)
                if not c0:
                    continue

                neighbors = []
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = int(xx + dx), int(yy + dy)
                    if nx < 0 or nx >= int(w) or ny < 0 or ny >= int(h):
                        continue
                    if _eligible_color(nx, ny) == c0:
                        neighbors.append((nx, ny))

                if not neighbors:
                    continue

                # Triggered: clear breaker itself.
                clear_cells.add((int(xx), int(yy)))

                # Clear the full connected component (same color, eligible) reachable from neighbors.
                q = deque(neighbors)
                while q:
                    x1, y1 = q.popleft()
                    key = (int(x1), int(y1))
                    if key in visited:
                        continue
                    visited.add(key)
                    if _eligible_color(x1, y1) != c0:
                        continue
                    clear_cells.add(key)
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, ny = int(x1 + dx), int(y1 + dy)
                        if nx < 0 or nx >= int(w) or ny < 0 or ny >= int(h):
                            continue
                        if (nx, ny) in visited:
                            continue
                        # Only enqueue if color matches; avoids scanning empty cells.
                        if _eligible_color(nx, ny) == c0:
                            q.append((nx, ny))

        if not clear_cells:
            return b, 0

        # Clear.
        for cx, cy in clear_cells:
            try:
                b.set_piece(int(cx), int(cy), b.EMPTY)
            except Exception:
                pass

        # Settle: compress each column downward.
        try:
            for xx in range(int(w)):
                col = []
                for yy in range(int(h) - 1, -1, -1):
                    v = b.get_piece(int(xx), int(yy))
                    if v != b.EMPTY and v is not None:
                        col.append(v)
                ydst = int(h) - 1
                for v in col:
                    b.set_piece(int(xx), int(ydst), v)
                    ydst -= 1
                for yy in range(int(ydst), -1, -1):
                    b.set_piece(int(xx), int(yy), b.EMPTY)
        except Exception:
            pass

        return b, int(len(clear_cells))

    def _simulate_breaker_chain_resolve(self, board, *, max_steps: int = 4):
        """Apply repeated breaker clear passes until stable or max_steps reached.

        Returns (resolved_board, total_cleared_cells).
        """
        try:
            b = board
            cleared_total = 0
            for _ in range(max(0, int(max_steps))):
                nb, cleared = self._simulate_breaker_clear_pass(b)
                if nb is None:
                    break
                if int(cleared) <= 0:
                    b = nb
                    break
                cleared_total += int(cleared)
                b = nb
            return b, int(cleared_total)
        except Exception:
            return board, 0

    def _simulate_one_combo_step(self, board):
        """Approximate one combo resolution step: clear 2x2 clusters, then settle columns."""
        try:
            b = board.copy()
        except Exception:
            return None

        # Collect all cells that are part of any 2x2 same-color square.
        try:
            clear_cells: set[tuple[int, int]] = set()
            w = int(getattr(b, 'WIDTH', 6) or 6)
            h = int(getattr(b, 'HEIGHT', 12) or 12)

            def cell_color(xx: int, yy: int) -> str | None:
                c = b.get_piece(xx, yy)
                if c is None or c == b.EMPTY:
                    return None
                if bool(getattr(c, 'is_garbage', False)):
                    return None
                if getattr(c, 'attack_state', None) is not None:
                    return None
                col = str(getattr(c, 'color', '') or '').strip().lower()
                return col or None

            for x in range(w - 1):
                for y in range(h - 1):
                    c0 = cell_color(x, y)
                    if not c0:
                        continue
                    if c0 == cell_color(x + 1, y) == cell_color(x, y + 1) == cell_color(x + 1, y + 1):
                        clear_cells.update({(x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)})

            if not clear_cells:
                return b

            # Clear
            for (cx, cy) in clear_cells:
                try:
                    b.set_piece(int(cx), int(cy), b.EMPTY)
                except Exception:
                    pass

            # Settle: compress each column downward.
            for x in range(w):
                col = []
                for y in range(h - 1, -1, -1):
                    v = b.get_piece(x, y)
                    if v != b.EMPTY and v is not None:
                        col.append(v)
                # Refill from bottom
                yy = h - 1
                for v in col:
                    b.set_piece(x, yy, v)
                    yy -= 1
                for y in range(yy, -1, -1):
                    b.set_piece(x, y, b.EMPTY)

        except Exception:
            return None

        return b

    def _score_board_state(self, b) -> float:
        """Score a board snapshot directly (shared by greedy + lookahead)."""
        # Current tier affects all heuristics.
        lv_raw = max(1, int(getattr(self, '_rubix_level', 1) or 1))
        lv = int(lv_raw)

        # rubix6: when stack is high, switch to rubix5-style survival weights.
        rubix6_mode = ''
        try:
            rubix6_mode = str(getattr(self, '_rubix6_mode', '') or '')
        except Exception:
            rubix6_mode = ''
        if int(lv_raw) == 6 and str(rubix6_mode) == 'survival':
            lv = 5
        heights = b.get_column_heights()
        max_h = max(heights) if heights else 0
        try:
            sum_h = int(sum(int(hh) for hh in (heights or [])))
        except Exception:
            sum_h = int(max_h) * int(max(1, len(heights or [])))
        bump = 0
        try:
            for i in range(len(heights) - 1):
                bump += abs(int(heights[i]) - int(heights[i + 1]))
        except Exception:
            bump = 0

        # Penalize "spire" stacks (a couple columns much taller than the rest)
        # and mild edge-heaviness so rubix doesn't always tower in columns 1-2.
        spire = 0.0
        edge_mass = 0.0
        try:
            w_h = max(1, len(heights))
            mean_h = float(sum(float(hh) for hh in heights)) / float(w_h)
        except Exception:
            mean_h = float(max_h)
        try:
            for i, hh in enumerate(heights or []):
                # Anything > mean+~2 is increasingly risky.
                over = max(0.0, float(hh) - (float(mean_h) + 2.0))
                spire += over * over
        except Exception:
            spire = 0.0

        holes = self._count_holes(b)

        try:
            h = int(getattr(b, 'HEIGHT', 12) or 12)
        except Exception:
            h = 12

        top_row_filled = 0
        try:
            w = int(getattr(b, 'WIDTH', 6) or 6)
            for xx in range(w):
                if b.get_piece(xx, 0) != b.EMPTY:
                    top_row_filled += 1
        except Exception:
            top_row_filled = 0

        spawn_blocked = False
        try:
            gox = int(getattr(self.movement, 'game_over_x', 0) or 0)
            spawn_blocked = (b.get_piece(gox, 0) != b.EMPTY)
        except Exception:
            spawn_blocked = False

        # Context: spawn column is special (inbound avoids it), and we also allow
        # rubix4+ to react to imminent inbound pressure and opponent state.
        try:
            ctx = dict(getattr(self, '_rubix_ctx', {}) or {})
        except Exception:
            ctx = {}
        try:
            spawn_col = int(ctx.get('spawn_col', int(getattr(self.movement, 'spawn_x', 3) or 3)))
        except Exception:
            spawn_col = int(getattr(self.movement, 'spawn_x', 3) or 3)
        try:
            spawn_col = max(0, min(int(getattr(b, 'WIDTH', 6) or 6) - 1, int(spawn_col)))
        except Exception:
            spawn_col = int(spawn_col)

        try:
            incoming_total = int(ctx.get('incoming_total', 0) or 0)
        except Exception:
            incoming_total = 0
        try:
            incoming_ready = bool(ctx.get('incoming_ready', False))
        except Exception:
            incoming_ready = False

        # Maintenance mode: when there is no inbound pressure, prioritize keeping the
        # board low and light to prevent long-run self-topouts.
        no_inbound = False
        if lv >= 5:
            try:
                no_inbound = (int(incoming_total) == 0) and (not bool(incoming_ready))
            except Exception:
                no_inbound = False

        maintenance = 0.0
        if lv >= 5 and no_inbound:
            try:
                # Stronger when we're already a bit tall.
                maintenance = 0.35 + 0.65 * min(1.0, float(max_h) / 7.0)
            except Exception:
                maintenance = 0.80

        # Style selection: rubix4+ defaults to aggressive "combo fishing".
        try:
            style = str(os.getenv('BF_RUBIX_STYLE', '') or '').strip().lower()
        except Exception:
            style = ''
        if not style:
            style = 'combo' if lv >= 4 else 'balanced'
        if style not in ('combo', 'balanced'):
            style = 'balanced'

        # rubix6: force balanced style while in survival mode.
        if int(lv_raw) == 6 and str(rubix6_mode) == 'survival':
            style = 'balanced'

        # In maintenance mode (no inbound), avoid overly-greedy combo fishing.
        # Favor stable, frequent clears instead of tunneling into one color.
        if lv >= 5 and float(maintenance) > 0.0:
            style = 'balanced'

        # Evaluate per-color combo potential.
        try:
            groups_after = self._largest_connected_groups_by_color(b)
        except Exception:
            groups_after = {}
        try:
            clusters_after = self._count_2x2_clusters_by_color(b)
        except Exception:
            clusters_after = {}
        try:
            almost_after = self._count_almost_2x2_by_color(b)
        except Exception:
            almost_after = {}

        # rubix5+: cap potential (top of column colors). Helps convert sprinkles into fuel.
        try:
            caps_after = self._count_top_caps_by_color(b)
        except Exception:
            caps_after = {}

        # rubix5+: surface exposure. Helps avoid burying large clumps under junk.
        try:
            exposure_after = self._count_surface_exposure_by_color(b)
        except Exception:
            exposure_after = {}

        # Additional low-cost "combo fishing" features (rubix6+):
        # - adjacency edges: encourages building stable doubles/triples
        # - 2-of-4 2x2 setups: encourages laying foundations for future 3-of-4 threats
        try:
            edges_after = self._count_adjacent_edges_by_color(b)
        except Exception:
            edges_after = {}
        try:
            two_after = self._count_two_of_4_2x2_by_color(b)
        except Exception:
            two_after = {}

        # Pick a target color that maximizes near-term combo potential.
        # (This is the "super power": consistently convert doubles into triples/2x2s.)
        # rubix5+: optionally bias target-color toward what the opponent is likely
        # to sprinkle onto us (so incoming garbage becomes fuel).
        opp_sprinkle_counts: dict[str, int] | None = None
        sprinkle_pressure = 0.0
        opp_sprinkle_total = 0
        if lv >= 5:
            try:
                opp_sprinkle_counts = ctx.get('opp_sprinkle_counts', None)
                if not isinstance(opp_sprinkle_counts, dict):
                    opp_sprinkle_counts = None
            except Exception:
                opp_sprinkle_counts = None

            try:
                opp_sprinkle_total = int(sum(int(v or 0) for v in (opp_sprinkle_counts or {}).values()))
            except Exception:
                opp_sprinkle_total = 0

            try:
                inc_s = int(ctx.get('incoming_sprinkle', 0) or 0)
            except Exception:
                inc_s = 0
            # Normalize by board width: ~1.5 rows of pending singles ~= "heavy".
            try:
                sprinkle_pressure = min(1.0, float(inc_s) / max(1.0, float(w) * 1.5))
            except Exception:
                sprinkle_pressure = 0.0

        sprinkle_bias = 0.0
        if lv >= 5 and opp_sprinkle_counts:
            try:
                # Base bias is small (we don't want to suicide chasing fuel).
                # Increase bias when pending sprinkles are high.
                sprinkle_bias = (0.40 + 0.12 * float(max(0, int(lv) - 5))) * (0.60 + 0.70 * float(sprinkle_pressure))
            except Exception:
                sprinkle_bias = 0.0

        cap_bias = 0.0
        if lv >= 5:
            try:
                # Prefer having many columns capped with the likely sprinkle colors.
                cap_bias = (0.32 + 0.10 * float(max(0, int(lv) - 5))) * (0.35 + 0.90 * float(sprinkle_pressure))
            except Exception:
                cap_bias = 0.0

        target_color = None
        best_pot = None
        for c in ('red', 'blue', 'green', 'yellow'):
            g = int(groups_after.get(c, 0) or 0)
            cl = int(clusters_after.get(c, 0) or 0)
            al = int(almost_after.get(c, 0) or 0)
            ed = int(edges_after.get(c, 0) or 0)
            tw = int(two_after.get(c, 0) or 0)
            cap_cnt = int(caps_after.get(c, 0) or 0)

            sprinkle_bonus = 0.0
            if sprinkle_bias > 0.0 and opp_sprinkle_counts is not None:
                try:
                    sprinkle_bonus = float(opp_sprinkle_counts.get(c, 0) or 0) * float(sprinkle_bias)
                except Exception:
                    sprinkle_bonus = 0.0

            cap_bonus = 0.0
            if cap_bias > 0.0:
                try:
                    if opp_sprinkle_counts is not None and int(opp_sprinkle_total) > 0:
                        p = float(int(opp_sprinkle_counts.get(c, 0) or 0)) / float(max(1, int(opp_sprinkle_total)))
                        # Sprinkle-likely colors get more value from being capped.
                        p_scale = 0.45 + 1.25 * float(p)
                    else:
                        p_scale = 0.35
                    cap_bonus = float(cap_cnt) * float(cap_bias) * float(p_scale)
                except Exception:
                    cap_bonus = 0.0

            if style == 'combo':
                # rubix6+: prefer colors that already have "building blocks" for combos.
                # Keep weights modest so survival still matters.
                if lv >= 6:
                    pot = 1.0 * g + 6.0 * cl + 2.2 * al + 0.55 * ed + 0.65 * tw + float(sprinkle_bonus) + float(cap_bonus)
                else:
                    pot = 1.0 * g + 6.0 * cl + 2.2 * al + float(sprinkle_bonus) + float(cap_bonus)
            else:
                if lv >= 6:
                    pot = 1.0 * g + 3.0 * cl + 1.2 * al + 0.35 * ed + 0.40 * tw + float(sprinkle_bonus) + float(cap_bonus)
                else:
                    pot = 1.0 * g + 3.0 * cl + 1.2 * al + float(sprinkle_bonus) + float(cap_bonus)
            if best_pot is None or float(pot) > float(best_pot):
                best_pot = float(pot)
                target_color = str(c)

        # Expose debug values for tests/tuning.
        try:
            self._debug_last_target_color = str(target_color or '')
            self._debug_last_sprinkle_bias = float(sprinkle_bias)
            self._debug_last_opp_sprinkle_counts = dict(opp_sprinkle_counts) if isinstance(opp_sprinkle_counts, dict) else None
            self._debug_last_effective_level = int(lv)
            self._debug_last_rubix6_mode = str(rubix6_mode or '')
        except Exception:
            pass

        if not target_color:
            target_color = 'red'

        target_group_after = int(groups_after.get(target_color, 0) or 0)
        target_clusters_after = int(clusters_after.get(target_color, 0) or 0)
        target_almost_after = int(almost_after.get(target_color, 0) or 0)
        target_edges_after = int(edges_after.get(target_color, 0) or 0)
        target_two_after = int(two_after.get(target_color, 0) or 0)
        target_caps_after = int(caps_after.get(target_color, 0) or 0)

        # "Danger" score: when the stack rises, prioritize survival over combo fishing.
        # This prevents rubix4 from suiciding into tall/unsafe builds if the player stalls.
        try:
            w = int(getattr(b, 'WIDTH', 6) or 6)
        except Exception:
            w = 6
        w = max(1, int(w))
        safe_margin = 5  # keep at least this many rows "headroom" when possible
        # rubix5+: if we are not under inbound pressure, start playing "tidy" earlier.
        # This significantly reduces random self-topouts during long no-attack stretches.
        if lv >= 5:
            try:
                if int(incoming_total) == 0 and (not bool(incoming_ready)):
                    safe_margin = 9
            except Exception:
                pass
        try:
            danger_h = max(0.0, float(max_h) - float(max(0, h - safe_margin)))
            danger_h = min(1.0, danger_h / max(1.0, float(safe_margin)))
        except Exception:
            danger_h = 0.0
        try:
            danger_top = min(1.0, float(top_row_filled) / float(w))
        except Exception:
            danger_top = 0.0
        danger = max(0.0, min(1.0, 0.70 * float(danger_h) + 0.30 * float(danger_top)))

        # Incoming attacks are a major reason good humans switch to defense.
        # Treat "ready to land" as high danger; treat queued as moderate danger.
        if lv >= 4:
            try:
                incoming_norm = min(1.0, float(incoming_total) / max(1.0, float(w) * 2.0))
            except Exception:
                incoming_norm = 0.0
            inc = 0.0
            try:
                inc = 0.55 * float(incoming_norm) + (0.55 if incoming_ready else 0.0)
            except Exception:
                inc = 0.0
            danger = max(0.0, min(1.0, max(float(danger), float(inc))))

        # Opponent-aware tempo: if opponent is in more danger than we are, we can
        # be a bit more aggressive; otherwise prioritize survival.
        tempo = 0.0
        if lv >= 4:
            try:
                opp_h = int(ctx.get('opp_max_h', 0) or 0)
            except Exception:
                opp_h = 0
            try:
                opp_top = int(ctx.get('opp_top', 0) or 0)
            except Exception:
                opp_top = 0
            try:
                opp_dh = max(0.0, float(opp_h) - float(max(0, h - safe_margin)))
                opp_dh = min(1.0, opp_dh / max(1.0, float(safe_margin)))
            except Exception:
                opp_dh = 0.0
            try:
                opp_dt = min(1.0, float(opp_top) / float(max(1, w)))
            except Exception:
                opp_dt = 0.0
            opp_danger = max(0.0, min(1.0, 0.70 * float(opp_dh) + 0.30 * float(opp_dt)))
            try:
                tempo = max(-1.0, min(1.0, float(opp_danger) - float(danger)))
            except Exception:
                tempo = 0.0

        holes_w = 6.0
        maxh_w = 1.5
        bump_w = 0.7
        top_w = 45.0
        spawn_block_pen = 1_000_000.0

        # Nonlinear height risk: a small additional penalty helps prevent slow
        # upward drift during long idle stretches.
        quad_h_w = 0.0
        if lv >= 5:
            try:
                quad_h_w = (0.10 + 0.08 * float(max(0, int(lv) - 5))) * (0.35 + 1.15 * float(danger) + 0.85 * float(maintenance))
            except Exception:
                quad_h_w = 0.18

        # rubix5 tuning: bias toward a low, sustainable board.
        # Keep this mostly in rubix5 so rubix6 can remain the "stronger" greedy tier.
        if lv == 5:
            holes_w *= 1.20
            maxh_w *= 2.55
            bump_w *= 1.18
            top_w *= 2.00

        # Reward shaping.
        # - Balanced: still prefers survival/flatness, mild combo incentives.
        # - Combo: heavier incentives for (near) 2x2 setups and connected groups.
        group_reward = 2.0 + 0.6 * float(lv - 1)
        cluster_reward = 10.0 + 3.0 * float(lv - 1)
        almost_reward = 4.0 + 1.2 * float(lv - 1)
        # Keep raw versions for "immediate clear" incentives (not target-color gated).
        cluster_reward_raw = float(cluster_reward)
        almost_reward_raw = float(almost_reward)
        edge_reward = 0.0
        two_reward = 0.0
        if lv >= 6:
            edge_reward = 0.9 + 0.15 * float(lv - 6)
            two_reward = 1.4 + 0.25 * float(lv - 6)

        cap_reward = 0.0
        cap_scale = 0.0
        if lv >= 5:
            try:
                # Encourage columns capped with target_color so incoming sprinkles
                # can immediately attach.
                cap_reward = 0.95 + 0.18 * float(max(0, int(lv) - 5))
                # Only matters when sprinkles are actually coming in.
                cap_scale = 0.15 + 0.85 * float(sprinkle_pressure)
                if opp_sprinkle_counts is None:
                    cap_scale *= 0.35
            except Exception:
                cap_reward = 0.0
                cap_scale = 0.0
        if style == 'combo':
            group_reward *= 1.15
            cluster_reward *= 1.65
            almost_reward *= 2.25
            cluster_reward_raw *= 1.65
            almost_reward_raw *= 2.25
            if lv >= 6:
                edge_reward *= 1.35
                two_reward *= 1.55
            if lv >= 5:
                cap_reward *= 1.10
            # Let the bot accept a bit more surface roughness if it is building threats.
            bump_w *= 0.85

        # rubix5: soften combo incentives so it doesn't tower/bury itself chasing setups.
        if lv == 5:
            group_reward *= 0.82
            cluster_reward *= 0.84
            almost_reward *= 0.84
            cluster_reward_raw *= 0.86
            almost_reward_raw *= 0.86

        # Under no inbound pressure, further reduce long-term "clump building" so the
        # bot keeps converting pieces into clears instead of accumulating mass.
        if lv >= 5 and float(maintenance) > 0.0:
            try:
                group_reward *= (1.0 - 0.45 * float(maintenance))
                almost_reward *= (1.0 - 0.22 * float(maintenance))
                # Height/top risk matters even when danger is currently low.
                maxh_w *= (1.0 + 0.50 * float(maintenance))
                top_w *= (1.0 + 0.65 * float(maintenance))
            except Exception:
                pass

        # Spawn column is "safe" from inbound targeting; allow slightly more
        # structure there (less bump penalty around spawn) when not in danger.
        if lv >= 4:
            try:
                # Scale: safe => relax bump, danger => enforce flatten.
                bump_w *= (0.78 + 1.10 * float(danger))
            except Exception:
                pass

        # If we're in danger, de-emphasize combo rewards so we stabilize instead of greed.
        # Keep a floor so combos can still be taken if they also reduce danger.
        if lv >= 4:
            combo_scale = 1.0
            try:
                # If opponent is in trouble (tempo>0), stay more combo-oriented.
                # If we're the one in trouble, clamp hard into defense.
                base = 1.0 - 0.85 * float(danger)
                base = base + 0.25 * float(tempo)
                combo_scale = max(0.12, min(1.15, float(base)))
            except Exception:
                combo_scale = 1.0
            group_reward *= combo_scale
            cluster_reward *= combo_scale
            almost_reward *= combo_scale
            edge_reward *= combo_scale
            two_reward *= combo_scale

            # When danger rises, height and top pressure matter more.
            maxh_w *= (1.0 + 0.85 * float(danger))
            top_w *= (1.0 + 1.10 * float(danger))

        # Spire penalty should be "strategic": allow towers when safe, punish when dangerous.
        try:
            spire_scale = 0.18 * (0.25 + 1.15 * float(danger))
        except Exception:
            spire_scale = 0.18

        # Make off-spawn stacking less attractive. Anchor distance to spawn column
        # (inbound tends to avoid it), not geometric center.
        try:
            center = float(spawn_col)
            for i, hh in enumerate(heights or []):
                edge_mass += float(hh) * abs(float(i) - float(center))
            # Normalize so weights are stable across widths.
            edge_mass = float(edge_mass) / max(1.0, float(w))
        except Exception:
            edge_mass = 0.0

        # Also reward any-color cluster potential a bit so we don't tunnel on one color.
        try:
            total_clusters = sum(int(v or 0) for v in (clusters_after or {}).values())
        except Exception:
            total_clusters = 0
        try:
            total_almost = sum(int(v or 0) for v in (almost_after or {}).values())
        except Exception:
            total_almost = 0

        score = 0.0
        score += float(holes) * holes_w
        score += float(max_h) * maxh_w
        if float(quad_h_w) > 0.0:
            score += float(max_h) * float(max_h) * float(quad_h_w)

        # rubix5+: if we are in maintenance mode (no inbound), be extremely
        # averse to entering the top few rows. This targets the "dies without
        # receiving attacks" failure mode.
        if lv >= 5 and float(maintenance) > 0.0:
            try:
                near_top = max(0.0, float(max_h) - float(max(0, int(h) - 4)))
                if float(near_top) > 0.0:
                    score += (float(near_top) ** 3.0) * (85.0 * float(maintenance))
            except Exception:
                pass
        score += float(bump) * bump_w
        # Spire/edge penalties are small but persistent and help avoid suicidal towers.
        score += float(spire) * float(spire_scale)
        score += float(edge_mass) * 0.10
        score += float(top_row_filled) * top_w
        if spawn_blocked:
            score += spawn_block_pen
        score -= float(target_group_after) * group_reward
        score -= float(target_clusters_after) * cluster_reward
        score -= float(target_almost_after) * almost_reward
        if lv >= 5 and float(cap_scale) > 0.0:
            score -= float(target_caps_after) * float(cap_reward) * float(cap_scale)
        if lv >= 6:
            score -= float(target_edges_after) * float(edge_reward)
            score -= float(target_two_after) * float(two_reward)

        # Any-color incentives so we take obvious survival clears even if not target_color.
        # Scale up when in danger: stalling player shouldn't cause bot to ignore "save" breaks.
        any_cluster_scale = (0.35 if style == 'combo' else 0.18)
        any_almost_scale = (0.18 if style == 'combo' else 0.10)
        if lv >= 4:
            try:
                any_cluster_scale *= (1.0 + 1.25 * float(danger))
                any_almost_scale *= (1.0 + 0.90 * float(danger))
            except Exception:
                pass
        if lv >= 5 and float(maintenance) > 0.0:
            try:
                any_cluster_scale *= (1.0 + 2.20 * float(maintenance))
                any_almost_scale *= (1.0 + 1.60 * float(maintenance))
            except Exception:
                pass
        if int(total_clusters) > 0:
            # Immediate clear potential is very valuable (especially when danger is high).
            try:
                immediate = 0.30 + 0.55 * float(danger)
            except Exception:
                immediate = 0.30
            if lv >= 5 and float(maintenance) > 0.0:
                try:
                    # Under no-inbound maintenance, bias harder toward taking clears
                    # to reduce early-death seeds (p10 survivability).
                    immediate *= (1.0 + 1.85 * float(maintenance))
                except Exception:
                    pass
            score -= float(total_clusters) * float(cluster_reward_raw) * float(immediate)
            score -= float(total_clusters) * float(cluster_reward) * float(any_cluster_scale)
        if int(total_almost) > 0:
            score -= float(total_almost) * float(almost_reward) * float(any_almost_scale)

        # Mass/ceiling penalties (maintenance mode): prefer frequent clears.
        if lv >= 5 and float(maintenance) > 0.0:
            try:
                approx_mass = max(0.0, float(sum_h) - float(holes))
            except Exception:
                approx_mass = 0.0

            ceiling_cells = 0
            try:
                rows = min(int(h), 3)
                for yy in range(rows):
                    for xx in range(int(w)):
                        if b.get_piece(int(xx), int(yy)) != b.EMPTY:
                            ceiling_cells += 1
            except Exception:
                ceiling_cells = 0

            try:
                mass_w = (0.95 + 0.15 * float(max(0, int(lv) - 5))) * float(maintenance)
                mass_w *= 1.55
                ceiling_w = 8.5 * float(maintenance)
                score += float(approx_mass) * float(mass_w)
                score += float(ceiling_cells) * float(ceiling_w)
            except Exception:
                pass

        # Anti-bury heuristic (rubix5+): penalize large clumps that have low exposure.
        # This discourages building a long bar of a color and then covering it.
        if lv >= 5 and isinstance(exposure_after, dict) and isinstance(groups_after, dict):
            try:
                bury_pen = 0.0
                for c in ('red', 'blue', 'green', 'yellow'):
                    gsz = int(groups_after.get(c, 0) or 0)
                    if gsz < 8:
                        continue
                    exp = int(exposure_after.get(c, 0) or 0)
                    ratio = float(exp) / float(max(1, gsz))
                    # If < ~35% of blocks have open air above, we consider it "entombed".
                    deficit = max(0.0, 0.35 - float(ratio))

                    # If a color already has combo potential, burying it is extra bad.
                    # This matches human play: don't cover an active 2x2 engine unless
                    # the move is immediately converting into clears/combos.
                    try:
                        cl = int(clusters_after.get(c, 0) or 0)
                    except Exception:
                        cl = 0
                    try:
                        al = int(almost_after.get(c, 0) or 0)
                    except Exception:
                        al = 0
                    try:
                        combo_mult = 1.0 + 0.90 * float(min(3, max(0, cl))) + 0.35 * float(min(6, max(0, al)))
                    except Exception:
                        combo_mult = 1.0

                    bury_pen += float(gsz - 7) * float(deficit) * float(deficit) * float(combo_mult)

                # Scale with sprinkle pressure a bit (sprinkle-heavy games punish burying more),
                # but don't let it dominate survival.
                try:
                    inc_s = int(ctx.get('incoming_sprinkle', 0) or 0)
                except Exception:
                    inc_s = 0
                try:
                    sp = min(1.0, float(inc_s) / max(1.0, float(w) * 1.5))
                except Exception:
                    sp = 0.0
                bury_w = 10.0 * (0.75 + 0.50 * float(sp))
                # When danger is high, survival matters more; soften the penalty.
                try:
                    bury_w *= (0.75 + 0.65 * (1.0 - float(danger)))
                except Exception:
                    pass
                score += float(bury_pen) * float(bury_w)
            except Exception:
                pass
        return float(score)

    def _count_adjacent_edges_by_color(self, board) -> Dict[str, int]:
        """Count same-color adjacent pairs (edges) per color.

        This is a cheap signal for "I have doubles/triples forming" even before
        a full 3-of-4 2x2 threat exists.
        Excludes garbage and blocks with non-None attack_state.
        """
        w = int(getattr(board, 'WIDTH', 6) or 6)
        h = int(getattr(board, 'HEIGHT', 12) or 12)
        out: Dict[str, int] = {'red': 0, 'blue': 0, 'green': 0, 'yellow': 0}

        def cell_color(x: int, y: int) -> str | None:
            c = board.get_piece(x, y)
            if c is None or c == board.EMPTY:
                return None
            if bool(getattr(c, 'is_garbage', False)):
                return None
            if getattr(c, 'attack_state', None) is not None:
                return None
            col = str(getattr(c, 'color', '') or '').strip().lower()
            return col or None

        for y in range(h):
            for x in range(w):
                c0 = cell_color(x, y)
                if not c0:
                    continue
                if x + 1 < w:
                    c1 = cell_color(x + 1, y)
                    if c1 and c1 == c0:
                        out[c0] = int(out.get(c0, 0) or 0) + 1
                if y + 1 < h:
                    c2 = cell_color(x, y + 1)
                    if c2 and c2 == c0:
                        out[c0] = int(out.get(c0, 0) or 0) + 1

        return out

    def _count_two_of_4_2x2_by_color(self, board) -> Dict[str, int]:
        """Count 2x2 windows with exactly 2 of a color + 2 empties.

        This encourages laying foundations for future 3-of-4 threats.
        Excludes garbage and blocks with non-None attack_state.
        """
        w = int(getattr(board, 'WIDTH', 6) or 6)
        h = int(getattr(board, 'HEIGHT', 12) or 12)
        out: Dict[str, int] = {'red': 0, 'blue': 0, 'green': 0, 'yellow': 0}

        for x in range(w - 1):
            for y in range(h - 1):
                empties = 0
                cols: list[str] = []
                invalid = False
                for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
                    c = board.get_piece(x + dx, y + dy)
                    if c is None or c == board.EMPTY:
                        empties += 1
                        continue
                    if bool(getattr(c, 'is_garbage', False)) or getattr(c, 'attack_state', None) is not None:
                        invalid = True
                        break
                    col = str(getattr(c, 'color', '') or '').strip().lower()
                    if not col:
                        invalid = True
                        break
                    cols.append(col)
                if invalid:
                    continue
                if empties != 2 or len(cols) != 2:
                    continue
                if len(set(cols)) == 1:
                    c0 = cols[0]
                    out[c0] = int(out.get(c0, 0) or 0) + 1

        return out

    def _count_almost_2x2_by_color(self, board) -> Dict[str, int]:
        """Count 2x2 squares that are 3-of-4 of the same color + 1 empty.

        This is a good proxy for "double -> triple soon" combo fishing.
        Excludes garbage and blocks with non-None attack_state.
        """
        w = int(getattr(board, 'WIDTH', 6) or 6)
        h = int(getattr(board, 'HEIGHT', 12) or 12)
        out: Dict[str, int] = {'red': 0, 'blue': 0, 'green': 0, 'yellow': 0}

        def cell_color(x: int, y: int) -> str | None:
            c = board.get_piece(x, y)
            if c is None or c == board.EMPTY:
                return None
            if bool(getattr(c, 'is_garbage', False)):
                return None
            if getattr(c, 'attack_state', None) is not None:
                return None
            col = str(getattr(c, 'color', '') or '').strip().lower()
            return col or None

        for x in range(w - 1):
            for y in range(h - 1):
                cols: list[str] = []
                empties = 0
                invalid = False
                for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
                    c = board.get_piece(x + dx, y + dy)
                    if c is None or c == board.EMPTY:
                        empties += 1
                        continue
                    if bool(getattr(c, 'is_garbage', False)) or getattr(c, 'attack_state', None) is not None:
                        invalid = True
                        break
                    col = str(getattr(c, 'color', '') or '').strip().lower()
                    if not col:
                        invalid = True
                        break
                    cols.append(col)
                if invalid:
                    continue
                if empties == 1 and len(cols) == 3 and len(set(cols)) == 1:
                    c0 = cols[0]
                    out[c0] = int(out.get(c0, 0) or 0) + 1

        return out

    def _score_after_drop(self, piece: Piece, *, x: int, o: int) -> float | None:
        try:
            b = self.board.copy()
        except Exception:
            return None

        try:
            p = Piece(list(getattr(piece, 'blocks', []) or []))
            p.block_offsets = getattr(piece, 'block_offsets', None)
            p.orientation = int(o) % 4
            p.x = int(x)
            p.y = int(getattr(piece, 'y', -1) or -1)
            p.controllable = True
        except Exception:
            return None

        mover = PieceMover(b)
        if not self._can_place_piece(b, p):
            return None

        try:
            mover.hard_drop(p)
        except Exception:
            return None

        # Must land at least one in-bounds block.
        try:
            any_in_bounds = any(b.is_in_bounds(px, py) for px, py, _blk in p.get_block_positions())
        except Exception:
            any_in_bounds = False
        if not any_in_bounds:
            return None

        try:
            b.place_piece(p)
        except Exception:
            return None

        return float(self._score_board_state(b))

    def _can_place_piece(self, board, piece: Piece) -> bool:
        """Placement validity check for a piece at its current (x,y,o)."""
        try:
            for x, y, _blk in piece.get_block_positions():
                if not (0 <= int(x) < int(board.WIDTH)):
                    return False
                if int(y) >= int(board.HEIGHT):
                    return False
                if int(y) < 0:
                    # Disallow hidden-row occupancy above a completely full column.
                    has_space = False
                    for yy in range(int(board.HEIGHT)):
                        if board.get_piece(int(x), int(yy)) == board.EMPTY:
                            has_space = True
                            break
                    if not has_space:
                        return False
                    continue
                if board.get_piece(int(x), int(y)) != board.EMPTY:
                    return False
        except Exception:
            return False
        return True

    def _count_holes(self, board) -> int:
        holes = 0
        w = int(getattr(board, 'WIDTH', 6) or 6)
        h = int(getattr(board, 'HEIGHT', 12) or 12)
        for x in range(w):
            seen_block = False
            for y in range(h):
                filled = (board.get_piece(x, y) != board.EMPTY)
                if filled:
                    seen_block = True
                elif seen_block:
                    holes += 1
        return int(holes)

    def _largest_connected_groups_by_color(self, board) -> Dict[str, int]:
        """Return max connected component size per color.

        Excludes garbage and blocks with non-None attack_state.
        Connectivity is 4-neighbor.
        """
        w = int(getattr(board, 'WIDTH', 6) or 6)
        h = int(getattr(board, 'HEIGHT', 12) or 12)
        visited: set[tuple[int, int]] = set()
        best: Dict[str, int] = {}

        def ok_cell(cell) -> bool:
            if cell is None or cell == board.EMPTY:
                return False
            if bool(getattr(cell, 'is_garbage', False)):
                return False
            if getattr(cell, 'attack_state', None) is not None:
                return False
            c = getattr(cell, 'color', None)
            return bool(c)

        for x in range(w):
            for y in range(h):
                if (x, y) in visited:
                    continue
                cell = board.get_piece(x, y)
                if not ok_cell(cell):
                    continue
                color = str(getattr(cell, 'color', '') or '').strip().lower()
                if not color:
                    continue
                # BFS
                q = [(x, y)]
                visited.add((x, y))
                size = 0
                while q:
                    cx, cy = q.pop()
                    ccell = board.get_piece(cx, cy)
                    if not ok_cell(ccell):
                        continue
                    ccolor = str(getattr(ccell, 'color', '') or '').strip().lower()
                    if ccolor != color:
                        continue
                    size += 1
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, ny = cx + dx, cy + dy
                        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in visited:
                            ncell = board.get_piece(nx, ny)
                            if ok_cell(ncell) and str(getattr(ncell, 'color', '') or '').strip().lower() == color:
                                visited.add((nx, ny))
                                q.append((nx, ny))

                if size:
                    prev = int(best.get(color, 0) or 0)
                    if size > prev:
                        best[color] = int(size)

        return best

    def _count_top_caps_by_color(self, board) -> Dict[str, int]:
        """Count the top-most (highest) normal block color in each column.

        This approximates how often an incoming sprinkle block will immediately
        connect when it lands on a column.

        Excludes garbage and blocks with non-None attack_state.
        """
        w = int(getattr(board, 'WIDTH', 6) or 6)
        h = int(getattr(board, 'HEIGHT', 12) or 12)
        out: Dict[str, int] = {'red': 0, 'blue': 0, 'green': 0, 'yellow': 0}

        for x in range(w):
            top = None
            for y in range(h):
                c = board.get_piece(x, y)
                if c is None or c == board.EMPTY:
                    continue
                top = c
                break
            if top is None:
                continue
            if bool(getattr(top, 'is_garbage', False)):
                continue
            if getattr(top, 'attack_state', None) is not None:
                continue
            col = str(getattr(top, 'color', '') or '').strip().lower()
            if col in out:
                out[col] = int(out.get(col, 0) or 0) + 1

        return out

    def _count_surface_exposure_by_color(self, board) -> Dict[str, int]:
        """Count blocks that have empty space directly above them, per color.

        This approximates how "accessible" a color clump is for future growth.
        If you cover a large clump with other colors, its exposure drops.

        Excludes garbage and blocks with non-None attack_state.
        """
        w = int(getattr(board, 'WIDTH', 6) or 6)
        h = int(getattr(board, 'HEIGHT', 12) or 12)
        out: Dict[str, int] = {'red': 0, 'blue': 0, 'green': 0, 'yellow': 0}

        def ok_cell(c) -> bool:
            if c is None or c == board.EMPTY:
                return False
            if bool(getattr(c, 'is_garbage', False)):
                return False
            if getattr(c, 'attack_state', None) is not None:
                return False
            return bool(str(getattr(c, 'color', '') or '').strip())

        for x in range(w):
            for y in range(1, h):
                c = board.get_piece(x, y)
                if not ok_cell(c):
                    continue
                above = board.get_piece(x, y - 1)
                if above is None or above == board.EMPTY:
                    col = str(getattr(c, 'color', '') or '').strip().lower()
                    if col in out:
                        out[col] = int(out.get(col, 0) or 0) + 1

        return out

    def _count_2x2_clusters_by_color(self, board) -> Dict[str, int]:
        """Count 2x2 same-color squares per color (proxy for immediate break potential)."""
        w = int(getattr(board, 'WIDTH', 6) or 6)
        h = int(getattr(board, 'HEIGHT', 12) or 12)
        out: Dict[str, int] = {'red': 0, 'blue': 0, 'green': 0, 'yellow': 0}

        def cell_color(x: int, y: int) -> str | None:
            c = board.get_piece(x, y)
            if c is None or c == board.EMPTY:
                return None
            if bool(getattr(c, 'is_garbage', False)):
                return None
            if getattr(c, 'attack_state', None) is not None:
                return None
            col = str(getattr(c, 'color', '') or '').strip().lower()
            return col or None

        for x in range(w - 1):
            for y in range(h - 1):
                c0 = cell_color(x, y)
                if not c0:
                    continue
                if c0 == cell_color(x + 1, y) == cell_color(x, y + 1) == cell_color(x + 1, y + 1):
                    out[c0] = int(out.get(c0, 0) or 0) + 1
        return out


class BossOpponent(PassiveOpponent):
    """Boss opponent tuned for *fairness*.

    Key idea: instead of injecting "free" huge attacks on a timer (which can
    feel unwinnable regardless of piece constraints), the boss mostly responds
    to what the player *actually generated* via clears/rectangles.

    This directly relates "what combos/rectangles are possible" to boss output.
    """

    def __init__(self, timing, **kwargs):
        super().__init__(timing, **kwargs)
        # Difficulty tier for the boss. 1 = first boss (low chance of large attacks).
        self._boss_level = 1

        # RNG for timed pulses; seeded by MatchSession.
        self._boss_rng = random.Random()

        # Timed boss pressure (independent of clears):
        # - wait ~15 seconds, then
        # - every ~10 seconds send out some attacks.
        fps = int(getattr(self.timing, 'target_fps', 60) or 60)
        fps = max(1, fps)
        self._pulse_warmup_frames = 15 * fps
        self._pulse_interval_frames = 10 * fps
        self._next_pulse_frame = 0

        # How much of the player's outbound pressure the boss mirrors back.
        # 0.0 -> no echo, 1.0 -> equal mirror. Default is intentionally mild.
        try:
            self._echo_scale = float(os.getenv('BF_BOSS_ECHO_SCALE', '0.40'))
        except Exception:
            self._echo_scale = 0.40
        self._echo_scale = max(0.0, min(2.0, self._echo_scale))

        # Cap how much can be echoed per player batch (prevents sudden spikes).
        try:
            self._echo_cap_total = int(os.getenv('BF_BOSS_ECHO_CAP_TOTAL', '12'))
        except Exception:
            self._echo_cap_total = 12
        self._echo_cap_total = max(0, self._echo_cap_total)

        # Optional small baseline pressure so the boss isn't trivial if the
        # player never sends attacks.
        try:
            self._base_sprinkle = int(os.getenv('BF_BOSS_BASE_SPRINKLE', '0'))
        except Exception:
            self._base_sprinkle = 0
        self._base_sprinkle = max(0, self._base_sprinkle)

        try:
            self._base_interval = int(os.getenv('BF_BOSS_BASE_INTERVAL_FRAMES', '240'))
        except Exception:
            self._base_interval = 240
        self._base_interval = max(60, self._base_interval)

        try:
            self._echo_delay = int(os.getenv('BF_BOSS_ECHO_DELAY_FRAMES', '36'))
        except Exception:
            self._echo_delay = 36
        self._echo_delay = max(0, self._echo_delay)

        self._next_base_frame = 0

    def update(self):
        super().update()
        self._boss_baseline_tick()
        self._boss_pulse_tick()

    def set_boss_seed(self, seed: int | None) -> None:
        try:
            s = int(seed) if seed is not None else 0
        except Exception:
            s = 0
        # Mix the seed so different systems don't line up too predictably.
        self._boss_rng.seed(s ^ 0xB055_2026)

    def set_boss_level(self, level: int | None) -> None:
        try:
            lv = int(level) if level is not None else 1
        except Exception:
            lv = 1
        self._boss_level = max(1, lv)

    def _boss_pulse_tick(self) -> None:
        if getattr(self, 'defeated', False):
            return

        frame = int(getattr(self, 'frame', 0) or 0)

        # Initialize schedule after warmup.
        if self._next_pulse_frame <= 0:
            self._next_pulse_frame = frame + int(self._pulse_warmup_frames)
            return

        if frame < self._next_pulse_frame:
            return

        # First boss: low chance of large attacks.
        # Higher boss_level => higher large chance.
        # Keep it bounded so it never becomes 100% large.
        large_chance = min(0.05 + 0.03 * float(self._boss_level - 1), 0.35)
        medium_chance = min(0.25 + 0.05 * float(self._boss_level - 1), 0.55)
        # Ensure probabilities are sane.
        medium_chance = max(0.0, min(medium_chance, 1.0))
        large_chance = max(0.0, min(large_chance, 1.0 - medium_chance))
        small_chance = max(0.0, 1.0 - medium_chance - large_chance)

        def pick_tier() -> str:
            r = self._boss_rng.random()
            if r < small_chance:
                return 'small'
            if r < (small_chance + medium_chance):
                return 'medium'
            return 'large'

        tier = pick_tier()

        # Choose what kind of pressure this pulse is.
        # Bias toward sprinkles for early boss; strikes become more common later.
        strike_bias = min(0.20 + 0.05 * float(self._boss_level - 1), 0.55)
        do_strike = self._boss_rng.random() < strike_bias

        delay = 6
        try:
            if do_strike:
                shapes_small = [(2, 2), (3, 2), (2, 3)]
                shapes_medium = [(3, 3), (3, 4)]
                shapes_large = [(3, 5), (3, 6)]
                if tier == 'small':
                    w, h = self._boss_rng.choice(shapes_small)
                elif tier == 'medium':
                    w, h = self._boss_rng.choice(shapes_medium)
                else:
                    w, h = self._boss_rng.choice(shapes_large)
                amt = int(w * h)
                self.attacks.queue.append(
                    Attack(
                        AttackKind.STRIKE,
                        amt,
                        delay=delay,
                        meta={'boss': True, 'mode': 'pulse', 'tier': tier, 'sword_shape': (int(w), int(h))},
                    )
                )
            else:
                if tier == 'small':
                    amt = int(self._boss_rng.choice([3, 4, 5, 6]))
                elif tier == 'medium':
                    amt = int(self._boss_rng.choice([6, 7, 8, 9]))
                else:
                    amt = int(self._boss_rng.choice([10, 12, 14]))
                self.attacks.queue.append(
                    Attack(
                        AttackKind.SPRINKLE,
                        int(amt),
                        delay=delay,
                        meta={'boss': True, 'mode': 'pulse', 'tier': tier},
                    )
                )
        except Exception:
            pass

        # Schedule next pulse.
        self._next_pulse_frame = frame + int(self._pulse_interval_frames)

    def _boss_baseline_tick(self) -> None:
        if getattr(self, 'defeated', False):
            return
        if self._base_sprinkle <= 0:
            return

        frame = int(getattr(self, 'frame', 0) or 0)
        if self._next_base_frame <= 0:
            self._next_base_frame = frame + self._base_interval
            return

        if frame >= self._next_base_frame:
            try:
                self.attacks.queue.append(
                    Attack(
                        AttackKind.SPRINKLE,
                        int(self._base_sprinkle),
                        delay=int(self._echo_delay),
                        meta={'boss': True, 'mode': 'baseline'},
                    )
                )
            except Exception:
                pass
            self._next_base_frame = frame + self._base_interval

    def on_player_attacks(self, attacks: list[Attack]) -> None:
        """Echo back a scaled subset of player attacks.

        The boss stays within the same "attack vocabulary" (sprinkle/strike)
        and is bounded by an explicit per-batch cap.
        """
        if getattr(self, 'defeated', False):
            return
        if not attacks:
            return
        if self._echo_scale <= 0.0:
            return

        remaining = int(self._echo_cap_total)
        if remaining <= 0:
            return

        def _shape_for_amount_at_most(amount: int) -> tuple[int, int]:
            """Pick a sword_shape (w,h) with area <= amount.

            We must not exceed `amount`, because inbound strike clusters use
            `w*h` as the actual block count when sword_shape is provided.
            """
            target = max(1, int(amount))
            best_w, best_h, best_area = 1, 1, 1
            for w in (3, 2, 1):
                for h in range(12, 0, -1):
                    area = int(w * h)
                    if area <= target and area > best_area:
                        best_w, best_h, best_area = int(w), int(h), area
                        if best_area == target:
                            return best_w, best_h
            return best_w, best_h

        for atk in attacks:
            if remaining <= 0:
                break

            try:
                scaled = int(atk.amount * float(self._echo_scale))
            except Exception:
                continue

            if scaled <= 0:
                continue

            try:
                if atk.kind == AttackKind.SPRINKLE:
                    send_amt = min(scaled, remaining)
                    remaining -= send_amt
                    self.attacks.queue.append(
                        Attack(
                            AttackKind.SPRINKLE,
                            int(send_amt),
                            delay=int(self._echo_delay),
                            meta={'boss': True, 'mode': 'echo'},
                        )
                    )
                elif atk.kind == AttackKind.STRIKE:
                    target = min(scaled, remaining)
                    w, h = _shape_for_amount_at_most(int(target))
                    area = int(w * h)
                    remaining -= area
                    self.attacks.queue.append(
                        Attack(
                            AttackKind.STRIKE,
                            int(area),
                            delay=int(self._echo_delay),
                            meta={'boss': True, 'mode': 'echo', 'sword_shape': (int(w), int(h))},
                        )
                    )
            except Exception:
                pass


class MatchSession:
    def __init__(self, timing=DEFAULT_TIMING, attack_delay_frames: int = 24,
                 bulk_delivery: bool = True, seed: int | None = None,
                 enemy_style: str = 'passive', boss_level: int | None = None):
        self._debug_session = env_flag('BF_DEBUG_SESSION', default=False)
        self.timing = timing
        self.piece_queue: SharedPieceQueue = create_shared_piece_queue(seed)
        self.seed = self.piece_queue.seed
        if os.getenv('BF_LOG_FIRST_PIECES'):
            try:
                preview = [ps.as_tuple() for ps in self.piece_queue.preview_window(0, 10)]
                dprint(self._debug_session, f"[SESSION] Piece seed={self.seed} preview10={preview}")
            except Exception as e:
                dprint(self._debug_session, f"[SESSION] Failed to print preview pieces: {e}")

        enemy_style_norm = str(enemy_style or 'passive').strip().lower()

        # Endless Combo Mode was removed; keep backwards compatibility for old env/config.
        if enemy_style_norm == 'endless_combo':
            enemy_style_norm = 'passive'
        self.enemy_style = str(enemy_style_norm)

        # Player (human-controlled)
        player_board = None
        self.player = PlayerFighter(
            timing,
            spawn_x=3,
            attack_delay_frames=attack_delay_frames,
            bulk_delivery=bulk_delivery,
            enable_puzzle_speeds=False,
            piece_queue=self.piece_queue,
            board=player_board,
        )

        # Provide a stable per-match seed for any per-game fighter randomness (e.g., fists color).
        try:
            if hasattr(self.player, 'set_match_seed'):
                self.player.set_match_seed(self.seed)
        except Exception:
            pass

        # Enemy board can be disabled (player-only puzzle). This is used for
        # non-Rubix enemies where puzzle attacks translate to HP damage instead
        # of a full PvP puzzle exchange.
        # Only Rubix currently plays full board-vs-board.
        self.enemy_has_board: bool = bool(enemy_style_norm.startswith('rubix') or enemy_style_norm in ('rubixcube', 'rubiks', 'rubik'))

        # HP-mode defaults (used when enemy_has_board is False and ai exists).
        self.player_hp_max: int = 100
        self.player_hp: int = 100
        self.enemy_hp_max: int = 100
        self.enemy_hp: int = 100

        # Allow enemy style selectors like "rubix3" to imply a difficulty tier.
        # BF_BOSS_LEVEL (boss_level arg) remains the explicit override.
        rubix_level_from_style: int | None = None
        try:
            m = re.match(r'^rubix(?P<lv>\d+)$', enemy_style_norm)
            if m is not None:
                rubix_level_from_style = int(m.group('lv'))
        except Exception:
            rubix_level_from_style = None

        self.ai = None
        if enemy_style_norm not in ('none', 'player_only', 'solo', 'practice', 'off', 'disabled'):
            # Enemy (default: passive; optional boss/mirror/rubix)
            if enemy_style_norm == 'boss':
                enemy_cls = BossOpponent
            elif enemy_style_norm == 'mirror':
                enemy_cls = MirrorOpponent
            elif enemy_style_norm.startswith('rubix') or enemy_style_norm in ('rubixcube', 'rubiks', 'rubik'):
                enemy_cls = RubixOpponent
            else:
                enemy_cls = PassiveOpponent
            self.ai = enemy_cls(
                timing,
                spawn_x=3,
                attack_delay_frames=attack_delay_frames,
                bulk_delivery=bulk_delivery,
                enable_puzzle_speeds=False,
                piece_queue=self.piece_queue
            )

            try:
                if hasattr(self.ai, 'set_match_seed'):
                    self.ai.set_match_seed(self.seed)
            except Exception:
                pass

        # Initialize HP if we're in HP-mode (non-rubix enemies).
        if (self.ai is not None) and (not bool(self.enemy_has_board)):
            # Player HP
            try:
                self.player_hp_max = max(1, int(os.getenv('BF_PLAYER_HP', '100') or '100'))
            except Exception:
                self.player_hp_max = 100
            self.player_hp = int(self.player_hp_max)

            # Enemy HP (style-specific, overridable)
            default_enemy_hp = 100
            if enemy_style_norm == 'boss':
                default_enemy_hp = 100
                try:
                    default_enemy_hp = int(os.getenv('BF_BOSS_HP', str(default_enemy_hp)) or str(default_enemy_hp))
                except Exception:
                    default_enemy_hp = 100
            elif enemy_style_norm == 'mirror':
                try:
                    default_enemy_hp = int(os.getenv('BF_MIRROR_HP', str(default_enemy_hp)) or str(default_enemy_hp))
                except Exception:
                    default_enemy_hp = 100
            else:
                try:
                    default_enemy_hp = int(os.getenv('BF_ENEMY_HP', str(default_enemy_hp)) or str(default_enemy_hp))
                except Exception:
                    default_enemy_hp = 100

            self.enemy_hp_max = max(1, int(default_enemy_hp))
            self.enemy_hp = int(self.enemy_hp_max)

        # Seed boss RNG (if supported) for reproducible difficulty per seed.
        try:
            if self.ai is not None and hasattr(self.ai, 'set_boss_seed'):
                self.ai.set_boss_seed(self.seed)
        except Exception:
            pass

        # Configure boss tier / rubix tier (if supported).
        try:
            if self.ai is not None and hasattr(self.ai, 'set_boss_level'):
                effective_level = boss_level
                if effective_level is None and rubix_level_from_style is not None:
                    effective_level = rubix_level_from_style
                self.ai.set_boss_level(effective_level)
        except Exception:
            pass

        # Link opponents (for opponent-aware logging / features)
        try:
            if self.ai is not None:
                self.player.opponent = self.ai
                self.ai.opponent = self.player
            else:
                self.player.opponent = None
        except AttributeError:
            pass

        self.attack_delay_frames = attack_delay_frames
        self.bulk_delivery = bulk_delivery
        self.frame = 0
        self.scoring = ScoringManager()

        try:
            if self.ai is None:
                dprint(self._debug_session, f"[SESSION] Match started (seed={self.seed}): Player (solo)")
            else:
                dprint(self._debug_session, f"[SESSION] Match started (seed={self.seed}): Player vs Enemy")
        except Exception:
            pass

        # Optional: configure weapon patterns via environment variables
        try:
            p_sword = os.getenv('BF_PLAYER_SWORD', '').strip().lower()
            e_sword = os.getenv('BF_ENEMY_SWORD', '').strip().lower()
            if p_sword:
                for st in SwordType:
                    if st.value == p_sword:
                        self.player.set_weapon_sword(st)
                        dprint(self._debug_session, f"[SESSION] Player sword set to {st.value}")
                        break
            if e_sword:
                if self.ai is not None:
                    for st in SwordType:
                        if st.value == e_sword:
                            self.ai.set_weapon_sword(st)
                            dprint(self._debug_session, f"[SESSION] Enemy sword set to {st.value}")
                            break
        except Exception:
            pass

    def update(self, intents: Dict[str, Any]):
        self.frame += 1
        rec = get_recorder()
        player_was_active = self.player.chain_runner.active
        ai_was_active = (self.ai.chain_runner.active if self.ai is not None else False)

        self.player.update(intents)
        if self.ai is not None:
            # HP-mode enemies do not use their own puzzle board as a defeat condition.
            # If we simulate their board, it can top-out offscreen and incorrectly
            # mark the boss as defeated while HP is still full.
            if not bool(getattr(self, 'enemy_has_board', True)):
                self._update_hp_mode_enemy()
            else:
                self.ai.update()

        player_piece_locked = (not player_was_active) and self.player.chain_runner.active
        ai_piece_locked = (not ai_was_active) and (self.ai.chain_runner.active if self.ai is not None else False)
        if player_piece_locked:
            self.scoring.player.piece_locks += 1
        if ai_piece_locked and self.ai is not None:
            self.scoring.ai.piece_locks += 1

        if player_piece_locked:
            if self.ai is not None:
                ai_swords = self.ai.horizontal_swords.trigger_immediate_fall()
                if ai_swords:
                    dprint(self._debug_session, f"[SESSION] Player lock triggered {len(ai_swords)} enemy horizontal sword blocks")
                    self.ai.add_garbage_fallers(ai_swords)
        if ai_piece_locked and self.ai is not None:
            pl_swords = self.player.horizontal_swords.trigger_immediate_fall()
            if pl_swords:
                dprint(self._debug_session, f"[SESSION] Enemy lock triggered {len(pl_swords)} player horizontal sword blocks")
                self.player.add_garbage_fallers(pl_swords)

        p_out = self.player.collect_ready_attacks()
        if p_out:
            dprint(self._debug_session, f"[SESSION ATTACK] Player -> Enemy {[(a.kind.value,a.amount) for a in p_out]}")
            if self.ai is not None:
                if bool(getattr(self, 'enemy_has_board', True)):
                    # Color inbound using the SENDER's weapon pattern (so received garbage matches attacker).
                    try:
                        provider = getattr(self.player, '_weapon_color_for_block', None)
                        ih = getattr(self.ai, 'inbound_handler', None)
                        lc = getattr(ih, 'lifecycle', None) if ih is not None else None
                        if callable(provider) and lc is not None:
                            setattr(lc, 'color_provider', provider)
                    except Exception:
                        pass
                    self.ai.receive_attacks(p_out)

                # Allow special enemies (boss/mirror) to respond based on what the player
                # actually generated via the attack system.
                try:
                    if hasattr(self.ai, 'on_player_attacks'):
                        try:
                            self.ai.on_player_attacks(list(p_out), self.player)
                        except TypeError:
                            self.ai.on_player_attacks(list(p_out))
                except Exception:
                    pass

                # HP-mode: player attacks deal damage instead of spawning an enemy board.
                if not bool(getattr(self, 'enemy_has_board', True)):
                    dmg = 0
                    for a in p_out:
                        try:
                            base = max(0, int(a.amount))
                            chain_idx = 1
                            try:
                                meta = getattr(a, 'meta', None)
                                if isinstance(meta, dict):
                                    chain_idx = int(meta.get('chain', 1) or 1)
                            except Exception:
                                chain_idx = 1
                            chain_idx = max(1, chain_idx)
                            dmg += base * chain_idx
                        except Exception:
                            pass

                    if dmg > 0:
                        # Mirror: invincible, reflects damage back.
                        if str(getattr(self, 'enemy_style', '') or '').strip().lower() == 'mirror':
                            try:
                                self.player_hp = max(0, int(getattr(self, 'player_hp', 0) or 0) - int(dmg))
                            except Exception:
                                pass
                        else:
                            try:
                                self.enemy_hp = max(0, int(getattr(self, 'enemy_hp', 0) or 0) - int(dmg))
                            except Exception:
                                pass

                    # Defeat conditions in HP-mode.
                    try:
                        if int(getattr(self, 'player_hp', 0) or 0) <= 0:
                            self.player.defeated = True
                    except Exception:
                        pass
                    try:
                        if str(getattr(self, 'enemy_style', '') or '').strip().lower() != 'mirror':
                            if int(getattr(self, 'enemy_hp', 0) or 0) <= 0:
                                self.ai.defeated = True
                    except Exception:
                        pass
            if rec.enabled:
                rec.record_attack(self.frame, 'player', self.seed, 'out', [{'k':a.kind.value,'amt':a.amount,'delay':a.delay} for a in p_out])
            for a in p_out:
                if a.kind.value == 'sprinkle':
                    self.scoring.player.sprinkles_sent += a.amount
                elif a.kind.value == 'strike':
                    self.scoring.player.strikes_sent += a.amount
        ai_out = (self.ai.collect_ready_attacks() if self.ai is not None else [])
        if ai_out:
            dprint(self._debug_session, f"[SESSION ATTACK] Enemy -> Player {[(a.kind.value,a.amount) for a in ai_out]}")
            # Color inbound using the SENDER's weapon pattern (so received garbage matches attacker).
            try:
                provider = getattr(self.ai, '_weapon_color_for_block', None) if self.ai is not None else None
                ih = getattr(self.player, 'inbound_handler', None)
                lc = getattr(ih, 'lifecycle', None) if ih is not None else None
                if callable(provider) and lc is not None:
                    setattr(lc, 'color_provider', provider)
            except Exception:
                pass
            self.player.receive_attacks(ai_out)
            if rec.enabled:
                rec.record_attack(self.frame, 'enemy', self.seed, 'out', [{'k':a.kind.value,'amt':a.amount,'delay':a.delay} for a in ai_out])
            for a in ai_out:
                if a.kind.value == 'sprinkle':
                    self.scoring.ai.sprinkles_sent += a.amount
                elif a.kind.value == 'strike':
                    self.scoring.ai.strikes_sent += a.amount

        # Aggregate per-frame received counts (for UI/stats).
        self.scoring.player.sprinkles_received = self.scoring.ai.sprinkles_sent
        self.scoring.player.strikes_received = self.scoring.ai.strikes_sent
        self.scoring.ai.sprinkles_received = self.scoring.player.sprinkles_sent
        self.scoring.ai.strikes_received = self.scoring.player.strikes_sent

        fighters = [(self.player, self.scoring.player)]
        if self.ai is not None:
            fighters.append((self.ai, self.scoring.ai))
        for fighter, slot in fighters:
            bm = getattr(fighter, 'breaker', None)
            if bm is None:
                bm = getattr(fighter, 'breaker_manager', None)
            if bm and getattr(bm, 'last_chain_results', None):
                passes, total, per_pass = bm.last_chain_results
                garbage_removed = 0
                stats = getattr(bm, 'last_pass_stats', None)
                if stats and 'garbage_removed' in stats:
                    garbage_removed = stats['garbage_removed']
                slot.record_chain(passes, total, per_pass, garbage_removed)
                if rec.enabled:
                    rec.record_chain(self.frame, getattr(fighter, 'fighter_name', '?'), self.seed, {
                        'passes': passes,
                        'total': total,
                        'per_pass': per_pass,
                        'garbage_removed': garbage_removed,
                        'dec_id': getattr(fighter, '_last_decision_id', None)
                    })
                bm.last_chain_results = None

        # Mirror Cube is intended to be an invincible training dummy.
        # Be defensive here: even if some upstream logic flips defeat/HP state
        # (e.g., offscreen board interactions), never allow mirror to end the match.
        try:
            if str(getattr(self, 'enemy_style', '') or '').strip().lower() == 'mirror':
                if self.ai is not None:
                    try:
                        self.ai.defeated = False
                    except Exception:
                        pass
                    try:
                        self.ai.movement.defeated = False
                    except Exception:
                        pass
                try:
                    self.enemy_hp = int(getattr(self, 'enemy_hp_max', self.enemy_hp) or self.enemy_hp)
                except Exception:
                    pass
        except Exception:
            pass

    def settle_update(self) -> None:
        """Advance only the minimal simulation needed to visually settle.

        Used by pygame_client's postgame settle window so the match doesn't
        continue for additional turns after a win/loss is already decided.
        """
        try:
            self.frame = int(getattr(self, 'frame', 0) or 0) + 1
        except Exception:
            self.frame = 0

        try:
            if hasattr(self.player, 'postgame_settle_tick'):
                self.player.postgame_settle_tick()
        except Exception:
            pass

        if self.ai is not None and bool(getattr(self, 'enemy_has_board', True)):
            try:
                if hasattr(self.ai, 'postgame_settle_tick'):
                    self.ai.postgame_settle_tick()
            except Exception:
                pass

    def _update_hp_mode_enemy(self) -> None:
        """Advance the enemy in HP-mode without running its board simulation.

        HP-mode uses player attacks to reduce `enemy_hp`. The enemy's own board
        is not visible/meaningful, so it must not be allowed to top-out and
        trigger an early win/loss state.
        """
        ai = getattr(self, 'ai', None)
        if ai is None:
            return

        # If HP has already hit 0 for a non-mirror enemy, preserve defeat.
        try:
            style = str(getattr(self, 'enemy_style', '') or '').strip().lower()
        except Exception:
            style = ''
        if style != 'mirror':
            try:
                if int(getattr(self, 'enemy_hp', 0) or 0) <= 0:
                    try:
                        ai.defeated = True
                    except Exception:
                        pass
                    try:
                        ai.movement.defeated = True
                    except Exception:
                        pass
                    return
            except Exception:
                pass

        # Advance a simple frame counter so boss pulse scheduling remains stable.
        try:
            ai.frame += 1
        except Exception:
            try:
                ai.frame = int(getattr(ai, 'frame', 0) or 0) + 1
            except Exception:
                pass

        # Keep enemy from entering a defeated state due to hidden board.
        try:
            ai.defeated = False
        except Exception:
            pass
        try:
            ai.movement.defeated = False
        except Exception:
            pass

        # Keep its board empty so it cannot naturally top-out.
        try:
            ai.board.clear()
        except Exception:
            pass

        # Still tick attack delays so boss/mirror/passive can emit pressure.
        try:
            ai.attacks.tick_all()
        except Exception:
            pass

        # Boss: maintain its timed baseline + pulse pressure in HP-mode.
        try:
            if str(getattr(self, 'enemy_style', '') or '').strip().lower() == 'boss':
                if hasattr(ai, '_boss_baseline_tick'):
                    ai._boss_baseline_tick()
                if hasattr(ai, '_boss_pulse_tick'):
                    ai._boss_pulse_tick()
        except Exception:
            pass

    def snapshot(self):
        # Expose chain/cascade state so non-Pygame renderers can match pygame_client visuals.
        # Transient particle FX are intentionally disabled in this project.
        fx_events = []
        ai_snap = {
            'board': None,
            'piece': None,
            'next_piece': None,
            'garbage_fallers': [],
            'defeated': False,
            'defeat_reason': None,
            'defeat_context': {},
            'fighter_name': 'Enemy',
            'fast_falling': False,
            'chain_active': False,
            'cascade_mode': 'step',
            'pending_sprinkle': 0,
            'pending_strike': 0,
            'inbound_delay': 0,
            'spawn_queue': 0,
            'strike_land_seq': 0,
        }
        if self.ai is not None:
            ih = getattr(self.ai, 'inbound_handler', None)
            ai_snap = {
                'board': self.ai.get_board(),
                'piece': self.ai.get_piece(),
                'next_piece': self.ai.get_next_piece(),
                'garbage_fallers': self.ai.get_garbage_fallers(),
                'defeated': self.ai.defeated,
                'defeat_reason': getattr(self.ai, 'last_defeat_reason', None) or getattr(getattr(self.ai, 'movement', None), 'last_defeat_reason', None),
                'defeat_context': getattr(self.ai, 'last_defeat_context', None) or getattr(getattr(self.ai, 'movement', None), 'last_defeat_context', None) or {},
                'fighter_name': self.ai.fighter_name,
                'fast_falling': self.ai.movement.is_fast_falling(),
                'chain_active': bool(getattr(self.ai.chain_runner, 'active', False)),
                'cascade_mode': getattr(self.ai.chain_runner, 'cascade_mode', 'step'),
                'pending_sprinkle': int(getattr(ih, 'pending_in_sprinkle', 0) or 0),
                'pending_strike': int(getattr(ih, 'pending_in_strike', 0) or 0),
                'inbound_delay': int(getattr(ih, 'inbound_delay', 0) or 0),
                'spawn_queue': int(getattr(ih, 'spawn_queue', 0) or 0),
                'strike_land_seq': int(getattr(ih, 'strike_land_seq', 0) or 0),
            }

        hp_snap = None
        try:
            if (self.ai is not None) and (not bool(getattr(self, 'enemy_has_board', True))):
                hp_snap = {
                    'player': int(getattr(self, 'player_hp', 0) or 0),
                    'player_max': int(getattr(self, 'player_hp_max', 0) or 0),
                    'enemy': int(getattr(self, 'enemy_hp', 0) or 0),
                    'enemy_max': int(getattr(self, 'enemy_hp_max', 0) or 0),
                }
        except Exception:
            hp_snap = None

        return {
            'player': {
                'board': self.player.get_board(),
                'piece': self.player.get_piece(),
                'next_piece': self.player.get_next_piece(),
                'garbage_fallers': self.player.get_garbage_fallers(),
                'defeated': self.player.defeated,
                'defeat_reason': getattr(self.player, 'last_defeat_reason', None) or getattr(getattr(self.player, 'movement', None), 'last_defeat_reason', None),
                'defeat_context': getattr(self.player, 'last_defeat_context', None) or getattr(getattr(self.player, 'movement', None), 'last_defeat_context', None) or {},
                'fighter_name': self.player.fighter_name,
                'fast_falling': self.player.movement.is_fast_falling(),
                'chain_active': bool(getattr(self.player.chain_runner, 'active', False)),
                'cascade_mode': getattr(self.player.chain_runner, 'cascade_mode', 'step'),
                'pending_sprinkle': int(getattr(getattr(self.player, 'inbound_handler', None), 'pending_in_sprinkle', 0) or 0),
                'pending_strike': int(getattr(getattr(self.player, 'inbound_handler', None), 'pending_in_strike', 0) or 0),
                'inbound_delay': int(getattr(getattr(self.player, 'inbound_handler', None), 'inbound_delay', 0) or 0),
                'spawn_queue': int(getattr(getattr(self.player, 'inbound_handler', None), 'spawn_queue', 0) or 0),
                'strike_land_seq': int(getattr(getattr(self.player, 'inbound_handler', None), 'strike_land_seq', 0) or 0),
            },
            'ai': ai_snap,  # keep key name for UI compatibility
            'fx_events': fx_events,
            'frame': self.frame,
            'seed': self.seed,
            'enemy_style': self.enemy_style,
            'enemy_has_board': bool(getattr(self, 'enemy_has_board', True)),
            'hp': hp_snap,
            'scoring': self.scoring.to_snapshot(),
            'timing': self.timing,
        }


class BotBattleSession:
    """AI-vs-AI match session.

    This is used by the "Battle of the Bots" menu mode so two bots can play
    against each other on full boards and exchange real attacks.

    Interface is intentionally compatible with MatchSession for pygame_client:
    - exposes .player and .ai
    - .update(intents) is accepted (intents ignored)
    - .snapshot() returns the same keys
    """

    def __init__(
        self,
        timing=DEFAULT_TIMING,
        attack_delay_frames: int = 24,
        bulk_delivery: bool = True,
        seed: int | None = None,
        bot_a_style: str = 'rubix3',
        bot_b_style: str = 'rubix4',
    ):
        self._debug_session = env_flag('BF_DEBUG_SESSION', default=False)
        self.timing = timing
        self.piece_queue: SharedPieceQueue = create_shared_piece_queue(seed)
        self.seed = self.piece_queue.seed

        self.bot_a_style = str(bot_a_style or 'rubix3').strip().lower()
        self.bot_b_style = str(bot_b_style or 'rubix4').strip().lower()

        self.enemy_style = 'bot_battle'
        self.enemy_has_board = True
        self.accepts_player_input = False

        def _mk_bot(style: str, fighter_name: str) -> BaseFighter:
            style_norm = str(style or 'rubix3').strip().lower()

            # For bot-vs-bot we only support board-playing styles.
            # (Mirror/Boss are HP-mode / invincible dummy semantics.)
            if style_norm.startswith('rubix') or style_norm in ('rubixcube', 'rubiks', 'rubik'):
                cls = RubixOpponent
            else:
                # Default fallback: passive board (no decision logic).
                cls = PassiveOpponent

            bot = cls(
                timing,
                spawn_x=3,
                attack_delay_frames=attack_delay_frames,
                bulk_delivery=bulk_delivery,
                enable_puzzle_speeds=False,
                piece_queue=self.piece_queue,
            )
            try:
                bot.fighter_name = str(fighter_name)
            except Exception:
                pass

            # Parse rubixN to imply tier.
            try:
                m = re.match(r'^rubix(?P<lv>\d+)$', style_norm)
                if m is not None and hasattr(bot, 'set_boss_level'):
                    bot.set_boss_level(int(m.group('lv')))
            except Exception:
                pass

            return bot

        self.player = _mk_bot(self.bot_a_style, 'Bot A')
        self.ai = _mk_bot(self.bot_b_style, 'Bot B')

        # Provide a stable per-match seed for any per-game fighter randomness (e.g., fists color).
        try:
            if hasattr(self.player, 'set_match_seed'):
                self.player.set_match_seed(self.seed)
        except Exception:
            pass
        try:
            if hasattr(self.ai, 'set_match_seed'):
                self.ai.set_match_seed(self.seed)
        except Exception:
            pass

        self.attack_delay_frames = attack_delay_frames
        self.bulk_delivery = bulk_delivery
        self.frame = 0
        self.scoring = ScoringManager()

        try:
            dprint(
                self._debug_session,
                f"[SESSION] Bot battle started (seed={self.seed}): {self.bot_a_style} vs {self.bot_b_style}",
            )
        except Exception:
            pass

    def settle_update(self) -> None:
        """Bot-battle variant of settle tick (both sides are board fighters)."""
        try:
            self.frame = int(getattr(self, 'frame', 0) or 0) + 1
        except Exception:
            self.frame = 0

        try:
            if hasattr(self.player, 'postgame_settle_tick'):
                self.player.postgame_settle_tick()
        except Exception:
            pass
        try:
            if self.ai is not None and hasattr(self.ai, 'postgame_settle_tick'):
                self.ai.postgame_settle_tick()
        except Exception:
            pass

        # Link opponents.
        try:
            self.player.opponent = self.ai
            self.ai.opponent = self.player
        except Exception:
            pass

    def update(self, intents: Dict[str, Any]):
        # Intents are ignored (bots are AI-driven).
        self.frame += 1
        rec = get_recorder()

        a_was_active = bool(getattr(self.player.chain_runner, 'active', False))
        b_was_active = bool(getattr(self.ai.chain_runner, 'active', False))

        self.player.update()
        self.ai.update()

        a_piece_locked = (not a_was_active) and bool(getattr(self.player.chain_runner, 'active', False))
        b_piece_locked = (not b_was_active) and bool(getattr(self.ai.chain_runner, 'active', False))
        if a_piece_locked:
            self.scoring.player.piece_locks += 1
        if b_piece_locked:
            self.scoring.ai.piece_locks += 1

        # Lock triggers: force opponent horizontal swords to fall immediately.
        if a_piece_locked:
            try:
                b_swords = self.ai.horizontal_swords.trigger_immediate_fall()
                if b_swords:
                    dprint(self._debug_session, f"[SESSION] Bot A lock triggered {len(b_swords)} Bot B horizontal sword blocks")
                    self.ai.add_garbage_fallers(b_swords)
            except Exception:
                pass
        if b_piece_locked:
            try:
                a_swords = self.player.horizontal_swords.trigger_immediate_fall()
                if a_swords:
                    dprint(self._debug_session, f"[SESSION] Bot B lock triggered {len(a_swords)} Bot A horizontal sword blocks")
                    self.player.add_garbage_fallers(a_swords)
            except Exception:
                pass

        a_out = self.player.collect_ready_attacks()
        if a_out:
            dprint(self._debug_session, f"[SESSION ATTACK] Bot A -> Bot B {[(a.kind.value,a.amount) for a in a_out]}")
            # Color inbound using the SENDER's weapon pattern.
            try:
                provider = getattr(self.player, '_weapon_color_for_block', None)
                ih = getattr(self.ai, 'inbound_handler', None)
                lc = getattr(ih, 'lifecycle', None) if ih is not None else None
                if callable(provider) and lc is not None:
                    setattr(lc, 'color_provider', provider)
            except Exception:
                pass
            self.ai.receive_attacks(a_out)
            if rec.enabled:
                rec.record_attack(self.frame, 'bot_a', self.seed, 'out', [{'k':x.kind.value,'amt':x.amount,'delay':x.delay} for x in a_out])
            for x in a_out:
                if x.kind.value == 'sprinkle':
                    self.scoring.player.sprinkles_sent += x.amount
                elif x.kind.value == 'strike':
                    self.scoring.player.strikes_sent += x.amount

        b_out = self.ai.collect_ready_attacks()
        if b_out:
            dprint(self._debug_session, f"[SESSION ATTACK] Bot B -> Bot A {[(a.kind.value,a.amount) for a in b_out]}")
            # Color inbound using the SENDER's weapon pattern.
            try:
                provider = getattr(self.ai, '_weapon_color_for_block', None)
                ih = getattr(self.player, 'inbound_handler', None)
                lc = getattr(ih, 'lifecycle', None) if ih is not None else None
                if callable(provider) and lc is not None:
                    setattr(lc, 'color_provider', provider)
            except Exception:
                pass
            self.player.receive_attacks(b_out)
            if rec.enabled:
                rec.record_attack(self.frame, 'bot_b', self.seed, 'out', [{'k':x.kind.value,'amt':x.amount,'delay':x.delay} for x in b_out])
            for x in b_out:
                if x.kind.value == 'sprinkle':
                    self.scoring.ai.sprinkles_sent += x.amount
                elif x.kind.value == 'strike':
                    self.scoring.ai.strikes_sent += x.amount

        # Aggregate per-frame received counts (for UI/stats).
        self.scoring.player.sprinkles_received = self.scoring.ai.sprinkles_sent
        self.scoring.player.strikes_received = self.scoring.ai.strikes_sent
        self.scoring.ai.sprinkles_received = self.scoring.player.sprinkles_sent
        self.scoring.ai.strikes_received = self.scoring.player.strikes_sent

        fighters = [(self.player, self.scoring.player), (self.ai, self.scoring.ai)]
        for fighter, slot in fighters:
            bm = getattr(fighter, 'breaker', None)
            if bm is None:
                bm = getattr(fighter, 'breaker_manager', None)
            if bm and getattr(bm, 'last_chain_results', None):
                passes, total, per_pass = bm.last_chain_results
                garbage_removed = 0
                stats = getattr(bm, 'last_pass_stats', None)
                if stats and 'garbage_removed' in stats:
                    garbage_removed = stats['garbage_removed']
                slot.record_chain(passes, total, per_pass, garbage_removed)
                if rec.enabled:
                    rec.record_chain(self.frame, getattr(fighter, 'fighter_name', '?'), self.seed, {
                        'passes': passes,
                        'total': total,
                        'per_pass': per_pass,
                        'garbage_removed': garbage_removed,
                        'dec_id': getattr(fighter, '_last_decision_id', None)
                    })
                bm.last_chain_results = None

    def snapshot(self):
        fx_events = []
        return {
            'player': {
                'board': self.player.get_board(),
                'piece': self.player.get_piece(),
                'next_piece': self.player.get_next_piece(),
                'garbage_fallers': self.player.get_garbage_fallers(),
                'defeated': self.player.defeated,
                'defeat_reason': getattr(self.player, 'last_defeat_reason', None) or getattr(getattr(self.player, 'movement', None), 'last_defeat_reason', None),
                'defeat_context': getattr(self.player, 'last_defeat_context', None) or getattr(getattr(self.player, 'movement', None), 'last_defeat_context', None) or {},
                'fighter_name': self.player.fighter_name,
                'fast_falling': self.player.movement.is_fast_falling(),
                'chain_active': bool(getattr(self.player.chain_runner, 'active', False)),
                'cascade_mode': getattr(self.player.chain_runner, 'cascade_mode', 'step'),
                'pending_sprinkle': int(getattr(getattr(self.player, 'inbound_handler', None), 'pending_in_sprinkle', 0) or 0),
                'pending_strike': int(getattr(getattr(self.player, 'inbound_handler', None), 'pending_in_strike', 0) or 0),
                'inbound_delay': int(getattr(getattr(self.player, 'inbound_handler', None), 'inbound_delay', 0) or 0),
                'spawn_queue': int(getattr(getattr(self.player, 'inbound_handler', None), 'spawn_queue', 0) or 0),
                'strike_land_seq': int(getattr(getattr(self.player, 'inbound_handler', None), 'strike_land_seq', 0) or 0),
            },
            'ai': {
                'board': self.ai.get_board(),
                'piece': self.ai.get_piece(),
                'next_piece': self.ai.get_next_piece(),
                'garbage_fallers': self.ai.get_garbage_fallers(),
                'defeated': self.ai.defeated,
                'defeat_reason': getattr(self.ai, 'last_defeat_reason', None) or getattr(getattr(self.ai, 'movement', None), 'last_defeat_reason', None),
                'defeat_context': getattr(self.ai, 'last_defeat_context', None) or getattr(getattr(self.ai, 'movement', None), 'last_defeat_context', None) or {},
                'fighter_name': self.ai.fighter_name,
                'fast_falling': self.ai.movement.is_fast_falling(),
                'chain_active': bool(getattr(self.ai.chain_runner, 'active', False)),
                'cascade_mode': getattr(self.ai.chain_runner, 'cascade_mode', 'step'),
                'pending_sprinkle': int(getattr(getattr(self.ai, 'inbound_handler', None), 'pending_in_sprinkle', 0) or 0),
                'pending_strike': int(getattr(getattr(self.ai, 'inbound_handler', None), 'pending_in_strike', 0) or 0),
                'inbound_delay': int(getattr(getattr(self.ai, 'inbound_handler', None), 'inbound_delay', 0) or 0),
                'spawn_queue': int(getattr(getattr(self.ai, 'inbound_handler', None), 'spawn_queue', 0) or 0),
                'strike_land_seq': int(getattr(getattr(self.ai, 'inbound_handler', None), 'strike_land_seq', 0) or 0),
            },
            'fx_events': fx_events,
            'frame': self.frame,
            'seed': self.seed,
            'enemy_style': self.enemy_style,
            'enemy_has_board': True,
            'hp': None,
            'scoring': self.scoring.to_snapshot(),
            'timing': self.timing,
            'bot_battle': {
                'bot_a_style': self.bot_a_style,
                'bot_b_style': self.bot_b_style,
            },
        }
