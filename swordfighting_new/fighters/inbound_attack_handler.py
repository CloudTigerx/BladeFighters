"""inbound_attack_handler.py - Handles incoming attacks and garbage spawning.

Responsibilities:
- Processing incoming attacks (sprinkle/strike)
- Managing delayed cluster spawning
- Spawning and updating garbage fallers
- Attack lifecycle management
- Cluster flood-fill algorithms
"""
from __future__ import annotations
from typing import List, Iterable
import os
import random

from swordfighting_new.attacks import Attack, AttackKind
from swordfighting_new.pieces.piece import Piece
from swordfighting_new.attacks.attack_lifecycle import InboundAttackLifecycle
from swordfighting_new.attacks.garbage_pattern import get_pattern_color
from swordfighting_new.util.fx_bus import emit_sparks
from swordfighting_new.util.debug import dprint, env_flag


class DelayedCluster:
    """Helper class to track delayed cluster spawning."""
    def __init__(self, width: int, height: int, delay_frames: int):
        self.width = width
        self.height = height
        self.delay_frames = delay_frames
        self.y_offset = 0  # Additional Y offset to prevent stacking


class InboundAttackHandler:
    """Manages all incoming attack processing and garbage spawning."""
    
    def __init__(self, board, timing, piece_mover, gravity_manager, attack_delay_frames: int = 24,
                 bulk_delivery: bool = True, garbage_spawn_interval: int = 3,
                 lifecycle_debug: bool = False, debug_attack_lifecycle: bool = False,
                 color_provider=None):
        self.board = board
        self.piece_mover = piece_mover
        self.gravity_manager = gravity_manager
        self.timing = timing
        self.attack_delay_frames = attack_delay_frames
        self.bulk_delivery = bulk_delivery
        self.garbage_spawn_interval = garbage_spawn_interval
        self.debug_attack_lifecycle = debug_attack_lifecycle
        self._debug_inbound = bool(debug_attack_lifecycle) or env_flag('BF_DEBUG_INBOUND', default=False)
        
        # Inbound accumulation
        self.pending_in_sprinkle = 0
        self.pending_in_strike = 0
        self._pending_in_strike_clusters = []  # list[(kind,(w,h))]
        self.inbound_delay = 0
        self.spawn_queue = 0  # gradual singles remaining
        self.garbage_spawn_cooldown = 0
        self.garbage_fallers: List[Piece] = []  # inbound falling singles/cluster blocks
        self._new_attack_blocks = []  # staged new blocks locked this frame (for lifecycle)
        self._delayed_clusters = []  # clusters waiting to spawn with delay

        # Inbound overflow (top-out) detection.
        # If any inbound faller locks while part of it remains above the visible board (y < 0),
        # it must count as defeat for the owning fighter. GravityManager.lock_piece() intentionally
        # ignores out-of-bounds blocks, so we track this here and let the fighter/session decide.
        self.inbound_overflowed: bool = False
        # Best-effort metadata describing the first overflow event observed.
        # Used for on-screen diagnostics ("why did I lose?").
        self.last_inbound_overflow_context: dict = {}

        # Inject a color provider for this fighter's weapon pattern; fallback to global get_pattern_color
        def _default_provider(*args):
            # Supports provider(block) and provider(x,y).
            if len(args) == 1:
                blk = args[0]
                try:
                    return get_pattern_color(int(getattr(blk, 'x', 0)), int(getattr(blk, 'y', 0)))
                except Exception:
                    return get_pattern_color(0, 0)
            if len(args) >= 2:
                try:
                    return get_pattern_color(int(args[0]), int(args[1]))
                except Exception:
                    return get_pattern_color(0, 0)
            return get_pattern_color(0, 0)

        provider = color_provider if callable(color_provider) else _default_provider
        self.lifecycle = InboundAttackLifecycle(debug=lifecycle_debug, color_provider=provider, board=self.board)
        self.frame = 0  # Track frame for spawning calculations
        # Rotation seeds/state
        self._strike_rot_seed = 0
        # Unique ID generator for vertical strike clusters.
        # Important for fairness/accuracy: multiple clusters spawned in the same frame must
        # not share an id, otherwise they get treated as a single rigid sword.
        self._strike_cluster_seq = 0

        # Strike SFX bookkeeping (consumed by AudioManager via session.snapshot).
        # Incremented once when a strike first contacts a block and begins piercing.
        self.strike_land_seq: int = 0
        self._strike_land_noted_clusters: set[int] = set()
        # Short sprinkle deferral window after strikes (approx 10 ms)
        fps = getattr(self.timing, 'target_fps', 60)
        self._sprinkle_deferral_frames = max(1, int(round(0.010 * float(fps))))
        try:
            override = os.getenv('BF_SPRINKLE_AFTER_STRIKE_FRAMES')
            if override is not None and str(override).strip() != '':
                self._sprinkle_deferral_frames = max(0, int(str(override).strip()))
        except Exception:
            pass
        self._last_strike_place_frame = None
        self._last_strike_cols: set[int] = set()

        # Sprinkle turn sequencing: used to compute per-turn layer coloring per PATTERN_MASTER.
        self._sprinkle_turn_seq = 0

        # Spawn column and sprinkle distribution policy.
        # The spawn column is kept last in normal conditions and can be hard-avoided
        # when the board gets tall, to prevent "forced top-out" by sprinkles.
        try:
            sc = os.getenv('BF_SPAWN_COLUMN', '3')
            self._spawn_col = int(str(sc).strip())
        except Exception:
            self._spawn_col = 3
        try:
            self._spawn_col = max(0, min(int(self.board.WIDTH) - 1, int(self._spawn_col)))
        except Exception:
            self._spawn_col = 3

        # Env override example: "0,6,2,5,3,4" (treats 6 as last col for width=6).
        self._sprinkle_col_order_env = None
        try:
            raw = os.getenv('BF_SPRINKLE_COLUMN_ORDER')
            if raw is not None and str(raw).strip() != '':
                self._sprinkle_col_order_env = str(raw)
        except Exception:
            self._sprinkle_col_order_env = None

        # When the board is tall, avoid placing inbound sprinkles into the spawn column.
        # Default: once any column reaches HEIGHT-3 (top 3 rows), protect spawn column.
        self._sprinkle_spawn_protect_rows = 3
        try:
            self._sprinkle_spawn_protect_rows = max(0, int(os.getenv('BF_SPRINKLE_SPAWN_PROTECT_ROWS', '3') or '3'))
        except Exception:
            self._sprinkle_spawn_protect_rows = 3
        self._sprinkle_spawn_lock_at_height = None
        try:
            raw_h = os.getenv('BF_SPRINKLE_SPAWN_LOCK_AT_HEIGHT', '').strip()
            if raw_h:
                self._sprinkle_spawn_lock_at_height = max(0, int(raw_h))
        except Exception:
            self._sprinkle_spawn_lock_at_height = None

        # Strike piercing needs to be consistent across frames.
        # Vertical strike clusters share a pierce budget that must persist while falling,
        # otherwise budgets reset every tick and small swords can over-pierce.
        self._strike_cluster_pierce_state: dict[int, tuple[int, bool]] = {}

        # Cluster-avoidance (pathfinding) state for vertical strike clusters.
        # Prevents left/right oscillation when a strike is blocked by an unpierceable cluster.
        # Keyed by strike_cluster_id.
        self._strike_cluster_avoid_state: dict[int, dict[str, object]] = {}

    def _mark_inbound_overflow(self, context: dict | None = None) -> None:
        """Mark inbound overflow and store first-seen context for debugging."""
        try:
            self.inbound_overflowed = True
        except Exception:
            pass
        try:
            if not isinstance(getattr(self, 'last_inbound_overflow_context', None), dict):
                self.last_inbound_overflow_context = {}
            if self.last_inbound_overflow_context:
                return
            self.last_inbound_overflow_context = dict(context or {})
        except Exception:
            pass

    def _new_strike_cluster_id(self) -> int:
        """Return a unique, monotonically increasing strike cluster id."""
        try:
            self._strike_cluster_seq = int(getattr(self, '_strike_cluster_seq', 0) or 0) + 1
        except Exception:
            self._strike_cluster_seq = 1
        return int(self._strike_cluster_seq)

    def _next_sprinkle_turn_id(self) -> int:
        try:
            self._sprinkle_turn_seq = int(getattr(self, '_sprinkle_turn_seq', 0) or 0) + 1
        except Exception:
            self._sprinkle_turn_seq = 1
        return int(self._sprinkle_turn_seq)

    def _should_lockout_spawn_col_for_sprinkles(self) -> bool:
        """Return True when we should avoid placing sprinkles into the spawn column."""
        try:
            heights = list(self.board.get_column_heights())
            max_h = max(heights) if heights else 0
        except Exception:
            max_h = 0

        try:
            lock_at = getattr(self, '_sprinkle_spawn_lock_at_height', None)
            if lock_at is not None:
                return int(max_h) >= int(lock_at)
        except Exception:
            pass

        try:
            protect_rows = int(getattr(self, '_sprinkle_spawn_protect_rows', 3) or 0)
        except Exception:
            protect_rows = 3
        protect_rows = max(0, protect_rows)

        try:
            h = int(getattr(self.board, 'HEIGHT', 12) or 12)
        except Exception:
            h = 12
        threshold = max(0, int(h) - int(protect_rows))
        return int(max_h) >= int(threshold)

    def _default_sprinkle_column_order(self) -> list[int]:
        """Default even-dispersal order: outer-to-inner, with spawn column last."""
        w = int(self.board.WIDTH)
        base: list[int] = []
        lo, hi = 0, w - 1
        while lo <= hi:
            if lo == hi:
                base.append(lo)
            else:
                base.append(lo)
                base.append(hi)
            lo += 1
            hi -= 1
        # Move spawn column to end if present.
        sc = int(getattr(self, '_spawn_col', 3))
        base = [c for c in base if c != sc] + ([sc] if 0 <= sc < w else [])
        return base

    def _parse_sprinkle_column_order(self) -> list[int]:
        w = int(self.board.WIDTH)
        raw = getattr(self, '_sprinkle_col_order_env', None)
        if not raw:
            return self._default_sprinkle_column_order()

        out: list[int] = []
        for part in str(raw).replace(' ', '').split(','):
            if not part:
                continue
            try:
                v = int(part)
            except Exception:
                continue
            # Convenience: if user writes "6" on a 6-wide board, treat it as last col (5).
            if v == w:
                v = w - 1
            if 0 <= v < w and v not in out:
                out.append(v)

        sc = int(getattr(self, '_spawn_col', 3))
        # Append any missing columns (keep spawn last).
        for c in range(w):
            if c != sc and c not in out:
                out.append(c)
        out = [c for c in out if c != sc] + ([sc] if 0 <= sc < w else [])

        if not out:
            return self._default_sprinkle_column_order()
        return out

    def _sprinkle_column_order(self, avoid_cols: set[int] | None, prefer_cols: set[int] | None) -> list[int]:
        """Column priority with prefer-first and avoid-last behavior."""
        avoid_cols = avoid_cols or set()
        prefer_cols = prefer_cols or set()
        base = self._parse_sprinkle_column_order()

        prefer = [c for c in base if c in prefer_cols]
        rest = [c for c in base if c not in prefer_cols]

        prefer_non = [c for c in prefer if c not in avoid_cols]
        prefer_avoided = [c for c in prefer if c in avoid_cols]
        rest_non = [c for c in rest if c not in avoid_cols]
        rest_avoided = [c for c in rest if c in avoid_cols]

        return prefer_non + prefer_avoided + rest_non + rest_avoided

    def _sprinkle_capacity_by_col(self) -> list[int]:
        """How many more blocks each column can accept before row 0 is filled."""
        try:
            heights = list(self.board.get_column_heights())
        except Exception:
            heights = [0 for _ in range(int(self.board.WIDTH))]
        caps: list[int] = []
        for h in heights:
            try:
                cap = int(self.board.HEIGHT) - int(h)
            except Exception:
                cap = int(self.board.HEIGHT)
            caps.append(max(0, cap))
        return caps

    def _existing_inbound_spawn_count(self) -> list[int]:
        """Count inbound fallers already spawned above-board per column."""
        w = int(self.board.WIDTH)
        counts = [0] * w
        for g in getattr(self, 'garbage_fallers', []) or []:
            try:
                x = int(getattr(g, 'x', -1))
                y = int(getattr(g, 'y', 0))
            except Exception:
                continue
            if 0 <= x < w and y < 0:
                counts[x] += 1
        return counts

    def set_frame(self, frame: int):
        """Update the current frame number."""
        self.frame = frame

    def receive_attacks(self, attacks: Iterable[Attack]):
        """Process incoming attacks and aggregate them into pending counts."""
        attack_list = list(attacks)
        if attack_list:
            dprint(self._debug_inbound, f"[INBOUND] Processing {len(attack_list)} attacks: {[f'{a.kind.value}:{a.amount}' for a in attack_list]}")
        
        new_any = False
        for atk in attack_list:
            if atk.kind == AttackKind.SPRINKLE:
                self.pending_in_sprinkle += atk.amount
                new_any = True
            elif atk.kind == AttackKind.STRIKE:
                meta = atk.meta or {}
                # Safety: strikes are capped by design rules (width<=3) and board dimensions.
                try:
                    board_w = int(getattr(self.board, 'WIDTH', 6) or 6)
                except Exception:
                    board_w = 6
                try:
                    board_h = int(getattr(self.board, 'HEIGHT', 12) or 12)
                except Exception:
                    board_h = 12

                def _clamp_w(v: int) -> int:
                    try:
                        return max(1, min(3, int(v)))
                    except Exception:
                        return 1

                def _clamp_h(v: int) -> int:
                    try:
                        return max(1, min(int(board_h), int(v)))
                    except Exception:
                        return 1

                def _clamp_len(v: int) -> int:
                    try:
                        return max(1, min(int(board_w), int(v)))
                    except Exception:
                        return 1
                if meta.get('sword_shape'):
                    w, h = meta['sword_shape']
                    w = _clamp_w(w)
                    h = _clamp_h(h)
                    self._pending_in_strike_clusters.append(('sword', (w, h)))
                    self.pending_in_strike += w * h
                elif meta.get('horizontal_sword_shape'):
                    rows, length = meta['horizontal_sword_shape']
                    rows = _clamp_w(rows)
                    length = _clamp_len(length)
                    # treat as cluster for now
                    self._pending_in_strike_clusters.append(('hsword', (rows, length)))
                    self.pending_in_strike += rows * length
                elif meta.get('rect'):
                    # Rectangle-based strike - use original rectangle dimensions
                    w, h = meta['rect']
                    # Interpret as a vertical cluster-like shape (legacy fallback).
                    w = _clamp_w(w)
                    h = _clamp_h(h)
                    self._pending_in_strike_clusters.append(('cluster', (w, h)))
                    self.pending_in_strike += w * h
                else:
                    # If we don't have a shape, cap magnitude to the maximum vertical sword area (3 x board_h).
                    try:
                        self.pending_in_strike += max(0, min(int(3 * board_h), int(atk.amount)))
                    except Exception:
                        self.pending_in_strike += 0
                new_any = True
        if new_any and self.inbound_delay < self.attack_delay_frames:
            old_delay = self.inbound_delay
            self.inbound_delay = self.attack_delay_frames
            dprint(self._debug_inbound, f"[INBOUND] Set inbound delay from {old_delay} to {self.inbound_delay} frames")
        
        # Log current pending amounts
        if self.pending_in_sprinkle + self.pending_in_strike > 0:
            dprint(self._debug_inbound, f"[INBOUND] Pending attacks: sprinkle={self.pending_in_sprinkle}, strike={self.pending_in_strike}, delay={self.inbound_delay}")

    def process_inbound(self, horizontal_swords_manager):
        """Process all inbound attack logic."""
        # Handle pending attacks
        inbound_total = self.pending_in_sprinkle + self.pending_in_strike
        if inbound_total:
            dprint(self._debug_inbound, f"[INBOUND] Processing inbound total={inbound_total}, delay={self.inbound_delay}")
            if self.inbound_delay > 0:
                self.inbound_delay -= 1
            if self.inbound_delay == 0:
                dprint(self._debug_inbound, f"[INBOUND] Delay reached 0; spawning attacks: sprinkle={self.pending_in_sprinkle}, strike={self.pending_in_strike}, bulk_delivery={self.bulk_delivery}")
                if self.bulk_delivery:
                    strikes_processed = False
                    # IMPORTANT: Resolve strikes before sprinkles to avoid interleaving
                    if self.pending_in_strike:
                        # Place all strike clusters this tick (non-overlapping). Any that don't fit are delayed.
                        reserved_cols = self._spawn_multiple_strike_clusters(horizontal_swords_manager)
                        strikes_processed = True
                        # Clear cluster list; delayed ones live in _delayed_clusters
                        self._pending_in_strike_clusters.clear()
                        self.pending_in_strike = 0
                        # Persist last strike placement info for sprinkle preference
                        try:
                            self._last_strike_place_frame = self.frame
                            self._last_strike_cols = set(reserved_cols or set())
                        except Exception:
                            self._last_strike_cols = set()
                    # Sprinkles must NOT spawn while any strike fallers are still in-flight,
                    # otherwise they can land into the middle of the strike cluster.
                    # Defer sprinkles until (a) strike fallers are gone, and (b) any delayed
                    # strike clusters have spawned and settled.
                    if self.pending_in_sprinkle and strikes_processed:
                        dprint(self._debug_inbound, f"[INBOUND] Deferring sprinkles until strikes settle: sprinkle={self.pending_in_sprinkle}")
                else:
                    self.spawn_queue += self.pending_in_sprinkle
                # Important: do not zero pending_in_sprinkle here; keep any deferred amount
                # pending_in_strike already cleared when processed
        
        # Gradual spawning (only when no controllable piece exists)
        if (not self.bulk_delivery) and self.spawn_queue > 0 and not self._has_active_controllable_piece():
            if self.garbage_spawn_cooldown > 0:
                self.garbage_spawn_cooldown -= 1
            if self.garbage_spawn_cooldown == 0:
                self._spawn_single(is_strike=False)
                self.spawn_queue -= 1
                self.garbage_spawn_cooldown = self.garbage_spawn_interval

        # Process delayed clusters
        self._process_delayed_clusters()

    def update_inbound_garbage(self):
        """Update falling garbage pieces and handle lifecycle processing."""
        # Precompute normal-block cluster cells once per tick (small board).
        cluster_cells = None
        still = []

        fall_debug = (os.getenv('BF_FALL_DEBUG', '0') == '1')

        # Snapshot occupied cells by *other fallers* so inbound pieces don't
        # incorrectly lock mid-air when they are only blocked by another faller.
        # (Faller pieces are not written into the board, so PieceMover ignores them.)
        all_faller_cells: set[tuple[int, int]] = set()
        try:
            for fp in (self.garbage_fallers or []):
                if getattr(fp, 'controllable', False):
                    continue
                for x, y, _b in fp.get_block_positions():
                    all_faller_cells.add((int(x), int(y)))
        except Exception:
            all_faller_cells = set()

        def _can_move_with_fallers(piece: Piece, dx: int, dy: int, occupied: set[tuple[int, int]]) -> bool:
            try:
                cur = {(int(x), int(y)) for x, y, _b in piece.get_block_positions()}
            except Exception:
                cur = set()
            for x, y, _b in piece.get_block_positions():
                nx, ny = int(x) + int(dx), int(y) + int(dy)
                if not (0 <= nx < self.board.WIDTH):
                    return False
                if ny >= self.board.HEIGHT:
                    return False
                if (nx, ny) in cur:
                    continue
                if ny >= 0:
                    try:
                        if self.board.get_piece(nx, ny) != self.board.EMPTY:
                            return False
                    except Exception:
                        return False
                    if (nx, ny) in occupied:
                        return False
            return True

        def _blocked_only_by_faller(piece: Piece, dx: int, dy: int, occupied: set[tuple[int, int]]) -> bool:
            """True if the move is blocked, and every blocking cell is a faller (board is empty)."""
            blocked_by_faller = False
            blocked_by_board = False
            try:
                cur = {(int(x), int(y)) for x, y, _b in piece.get_block_positions()}
            except Exception:
                cur = set()
            for x, y, _b in piece.get_block_positions():
                nx, ny = int(x) + int(dx), int(y) + int(dy)
                if (nx, ny) in cur:
                    continue
                # OOB counts as board blockage (settle/lock)
                if (not (0 <= nx < self.board.WIDTH)) or (ny >= self.board.HEIGHT):
                    blocked_by_board = True
                    continue
                if ny >= 0:
                    try:
                        if self.board.get_piece(nx, ny) != self.board.EMPTY:
                            blocked_by_board = True
                    except Exception:
                        blocked_by_board = True
                    if (nx, ny) in occupied:
                        blocked_by_faller = True
            return (blocked_by_faller and (not blocked_by_board))

        def _blocked_by_board_or_bottom(piece: Piece, dx: int, dy: int) -> bool:
            """True if the move is blocked by board occupancy or bounds (ignores other fallers)."""
            try:
                cur = {(int(x), int(y)) for x, y, _b in piece.get_block_positions()}
            except Exception:
                cur = set()
            for x, y, _b in piece.get_block_positions():
                nx, ny = int(x) + int(dx), int(y) + int(dy)
                if (nx, ny) in cur:
                    continue
                if (not (0 <= nx < self.board.WIDTH)) or (ny >= self.board.HEIGHT):
                    return True
                if ny >= 0:
                    try:
                        if self.board.get_piece(nx, ny) != self.board.EMPTY:
                            return True
                    except Exception:
                        return True
            return False

        def _describe_cell(x: int, y: int) -> str:
            """Best-effort description of what's in the board at (x,y)."""
            try:
                if not (0 <= int(x) < int(self.board.WIDTH) and 0 <= int(y) < int(self.board.HEIGHT)):
                    return 'OOB'
            except Exception:
                return 'OOB'

            try:
                obj = self.board.get_piece(int(x), int(y))
            except Exception:
                obj = None

            if obj in (None, self.board.EMPTY):
                return 'EMPTY'

            # Avoid noisy repr; keep the properties we care about.
            try:
                t = type(obj).__name__
            except Exception:
                t = 'Block'
            try:
                c = getattr(obj, 'color', None)
            except Exception:
                c = None
            try:
                st = getattr(obj, 'attack_state', None)
            except Exception:
                st = None
            try:
                gar = bool(getattr(obj, 'is_garbage', False))
            except Exception:
                gar = False
            try:
                br = bool(getattr(obj, 'is_breaker', False))
            except Exception:
                br = False
            return f"{t}(color={c}, attack_state={st}, garbage={gar}, breaker={br})"

        def _debug_blockers_for_piece(piece: Piece, dx: int, dy: int, occupied: set[tuple[int, int]]) -> list[str]:
            """Return human-readable reasons a move is blocked (board/faller/bounds)."""
            blockers: list[str] = []
            try:
                cur = {(int(x), int(y)) for x, y, _b in piece.get_block_positions()}
            except Exception:
                cur = set()

            for x, y, _b in piece.get_block_positions():
                nx, ny = int(x) + int(dx), int(y) + int(dy)
                if (nx, ny) in cur:
                    continue
                if not (0 <= nx < int(self.board.WIDTH)):
                    blockers.append(f"below ({nx},{ny}) => OOB-X")
                    continue
                if ny >= int(self.board.HEIGHT):
                    blockers.append(f"below ({nx},{ny}) => FLOOR")
                    continue
                if ny >= 0:
                    desc = _describe_cell(nx, ny)
                    if desc != 'EMPTY':
                        blockers.append(f"below ({nx},{ny}) => BOARD {desc}")
                    if (nx, ny) in occupied:
                        blockers.append(f"below ({nx},{ny}) => FALLER")
            # De-dupe while keeping order.
            out: list[str] = []
            seen = set()
            for b in blockers:
                if b in seen:
                    continue
                seen.add(b)
                out.append(b)
            return out

        # Group vertical strike cluster fallers so they move/pierce/lock as one sword.
        strike_groups: dict[int, list[Piece]] = {}
        strike_group_ids: set[int] = set()
        try:
            for g in self.garbage_fallers:
                if getattr(g, 'controllable', False):
                    continue
                cid = getattr(g, 'strike_cluster_id', None)
                if cid is None:
                    continue
                if not self._is_strike_piece(g):
                    continue
                cid_i = int(cid)
                strike_groups.setdefault(cid_i, []).append(g)
                strike_group_ids.add(cid_i)
        except Exception:
            strike_groups = {}
            strike_group_ids = set()

        # Process strike groups first (so they don't split across columns).
        for cid, pieces in (strike_groups or {}).items():
            if not pieces:
                continue

            # Other fallers act as temporary blockers (do not lock just because of them).
            try:
                group_cells = {(int(x), int(y)) for p in pieces for x, y, _b in p.get_block_positions()}
            except Exception:
                group_cells = set()
            occupied_other = set(all_faller_cells)
            try:
                occupied_other.difference_update(group_cells)
            except Exception:
                pass

            # All pieces in the group share timing; use the first as the representative.
            rep = pieces[0]
            try:
                if rep.autonomous_fall_timer >= rep.autonomous_fall_interval:
                    for p in pieces:
                        p.autonomous_fall_timer = 0

                    # Attempt to move the whole sword down by 1.
                    can_all_move = True
                    for p in pieces:
                        if not _can_move_with_fallers(p, 0, 1, occupied_other):
                            can_all_move = False
                            break

                    if can_all_move:
                        for p in pieces:
                            p.y += 1
                        # Any downward progress resets cluster-avoidance state.
                        try:
                            self._strike_cluster_avoid_state.pop(int(cid), None)
                        except Exception:
                            pass
                        still.extend(pieces)
                    else:
                        # If blocked only by another faller (not the board), just wait.
                        any_faller_block = False
                        any_board_block = False
                        try:
                            any_faller_block = any(_blocked_only_by_faller(p, 0, 1, occupied_other) for p in pieces)
                        except Exception:
                            any_faller_block = False
                        try:
                            any_board_block = any(_blocked_by_board_or_bottom(p, 0, 1) for p in pieces)
                        except Exception:
                            any_board_block = False

                        # Only wait when the group is blocked *solely* by other fallers.
                        # If any part of the cluster is blocked by the board/bottom, we must
                        # proceed to pierce/lock instead of waiting (otherwise strikes can stall).
                        if any_faller_block and (not any_board_block):
                            dprint(fall_debug, f"[FALL] Strike cluster cid={cid} blocked by another faller; waiting")
                            still.extend(pieces)
                            continue

                        # Debug: explain what blocked the sword.
                        try:
                            blockers = []
                            for p in pieces:
                                blockers.extend(_debug_blockers_for_piece(p, 0, 1, occupied_other))
                            # Keep log readable.
                            blockers = blockers[:8]
                            dprint(fall_debug, f"[FALL] Strike cluster cid={cid} blocked by board/bottom: {blockers}")
                        except Exception:
                            pass

                        # Strike/sword fallers can pierce through blocks/breakers before settling.
                        if cluster_cells is None:
                            cluster_cells = self._compute_normal_cluster_cells()

                        # IMPORTANT: no mid-fall column shifting. Vertical strike lanes are
                        # chosen up-front at spawn time; if blocked by an unpierceable cluster,
                        # the sword locks instead of drifting sideways.
                        try:
                            self._strike_cluster_avoid_state.pop(int(cid), None)
                        except Exception:
                            pass
                        
                        # Pierce blocks in the path, but don't lock yet.
                        pierced_any = False
                        try:
                            pierced_any = self._resolve_strike_cluster_pierce_before_lock(pieces, cluster_cells)
                        except Exception:
                            # Fall back to per-piece pierce if needed.
                            for p in pieces:
                                try:
                                    if self._resolve_strike_pierce_before_lock(p, cluster_cells):
                                        pierced_any = True
                                except Exception:
                                    pass
                        
                        # If we pierced blocks, keep the sword falling so it can continue
                        # down through the newly cleared space. Otherwise lock it.
                        if pierced_any:
                            try:
                                cid_i = int(cid)
                            except Exception:
                                cid_i = 0
                            if cid_i:
                                try:
                                    noted = getattr(self, '_strike_land_noted_clusters', set())
                                    if cid_i not in noted:
                                        noted.add(cid_i)
                                        self._strike_land_noted_clusters = noted
                                        try:
                                            self.strike_land_seq = int(getattr(self, 'strike_land_seq', 0) or 0) + 1
                                        except Exception:
                                            self.strike_land_seq = 1
                                except Exception:
                                    pass
                            dprint(fall_debug, f"[FALL] Strike cluster cid={cid} pierced blocks; continuing to fall")
                            still.extend(pieces)
                        else:
                            # No pierce happened; lock the whole sword as a unit.
                            # Attach stable strike metadata for weapon-pattern coloring.
                            # This prevents pattern mapping from shifting later if some blocks
                            # in the cluster are cleared (board-scan derivation would shrink).
                            try:
                                all_cells = [(int(x), int(y), b) for pp in pieces for x, y, b in pp.get_block_positions()]
                            except Exception:
                                all_cells = []
                            try:
                                left_x = min(xx for xx, _yy, _b in all_cells) if all_cells else 0
                            except Exception:
                                left_x = 0
                            try:
                                bottom_y = max(yy for _xx, yy, _b in all_cells) if all_cells else 0
                            except Exception:
                                bottom_y = 0
                            # Use the declared sword shape if available (prefer deterministic).
                            try:
                                sword_w = int(getattr(rep, 'sword_width', 0) or 0)
                            except Exception:
                                sword_w = 0
                            try:
                                sword_h = int(getattr(rep, 'sword_rows', 0) or 0)
                            except Exception:
                                sword_h = 0
                            # Fallback to measured extents.
                            if sword_w <= 0:
                                try:
                                    sword_w = int((max(xx for xx, _yy, _b in all_cells) - left_x) + 1) if all_cells else 1
                                except Exception:
                                    sword_w = 1
                            if sword_h <= 0:
                                try:
                                    top_y = min(yy for _xx, yy, _b in all_cells) if all_cells else bottom_y
                                    sword_h = int((bottom_y - top_y) + 1)
                                except Exception:
                                    sword_h = 1

                            # Inbound top-out: if any part of this sword is still above the visible
                            # board at the moment it locks, the owning fighter must be defeated.
                            try:
                                if any(int(yy) < 0 for _xx, yy, _b in all_cells):
                                    try:
                                        min_y = min(int(yy) for _xx, yy, _b in all_cells) if all_cells else -1
                                    except Exception:
                                        min_y = -1
                                    try:
                                        cols = sorted({int(_xx) for _xx, _yy, _b in all_cells}) if all_cells else []
                                    except Exception:
                                        cols = []
                                    self._mark_inbound_overflow(
                                        {
                                            'kind': 'strike_cluster',
                                            'cluster_id': int(cid),
                                            'min_y': int(min_y),
                                            'cols': cols,
                                            'width': int(sword_w),
                                            'height': int(sword_h),
                                        }
                                    )
                            except Exception:
                                pass

                            for p in pieces:
                                self.gravity_manager.lock_piece(p)
                                for x, y, block in p.get_block_positions():
                                    if getattr(block, 'attack_state', None):
                                        try:
                                            xi = int(x)
                                            yi = int(y)
                                            if not bool(self.board.is_in_bounds(xi, yi)):
                                                # Above-board blocks are not written to the board.
                                                # If this happens, the strike has overflowed.
                                                if yi < 0:
                                                    self._mark_inbound_overflow(
                                                        {
                                                            'kind': 'strike_block',
                                                            'cluster_id': int(cid),
                                                            'x': int(xi),
                                                            'y': int(yi),
                                                            'width': int(sword_w),
                                                            'height': int(sword_h),
                                                        }
                                                    )
                                                continue
                                            setattr(block, 'x', xi)
                                            setattr(block, 'y', yi)
                                            setattr(block, 'inbound_kind', 'strike')
                                            # Vertical strike cluster mapping info.
                                            setattr(block, 'vstrike_left_x', int(left_x))
                                            setattr(block, 'vstrike_width', int(sword_w))
                                            setattr(block, 'vstrike_height', int(sword_h))
                                            setattr(block, 'vstrike_x_offset', int(xi) - int(left_x))
                                            setattr(block, 'vstrike_y_offset', int(bottom_y) - int(yi))
                                        except Exception:
                                            pass
                                        self._new_attack_blocks.append(block)
                            # Do not add locked sword pieces back to still.
                            try:
                                self._strike_cluster_pierce_state.pop(int(cid), None)
                            except Exception:
                                pass
                            try:
                                self._strike_cluster_avoid_state.pop(int(cid), None)
                            except Exception:
                                pass
                            try:
                                getattr(self, '_strike_land_noted_clusters', set()).discard(int(cid))
                            except Exception:
                                pass
                else:
                    for p in pieces:
                        p.autonomous_fall_timer += 1
                    still.extend(pieces)
            except Exception:
                # Conservative: keep pieces falling if anything goes wrong.
                try:
                    for p in pieces:
                        p.autonomous_fall_timer += 1
                except Exception:
                    pass
                still.extend(pieces)

        for g in self.garbage_fallers:
            if g.controllable:
                still.append(g)
            else:
                # Skip strike-cluster pieces here; handled above.
                try:
                    if getattr(g, 'strike_cluster_id', None) is not None and int(getattr(g, 'strike_cluster_id')) in strike_group_ids:
                        continue
                except Exception:
                    pass
                if g.autonomous_fall_timer >= g.autonomous_fall_interval:
                    g.autonomous_fall_timer = 0
                    # Try to move down
                    old_y = g.y
                    occupied_other = set(all_faller_cells)
                    try:
                        # Don't treat the piece's own cells as blockers.
                        for x, y, _b in g.get_block_positions():
                            occupied_other.discard((int(x), int(y)))
                    except Exception:
                        pass

                    if _can_move_with_fallers(g, 0, 1, occupied_other):
                        g.y += 1
                        # Downward progress clears any cluster-avoidance memory.
                        try:
                            for attr in ('_cluster_avoid_y', '_cluster_avoid_dx', '_cluster_avoid_seen_x'):
                                if hasattr(g, attr):
                                    delattr(g, attr)
                        except Exception:
                            pass
                        dprint(fall_debug, f"[FALL] Block moved from y={old_y} to y={g.y}")
                        still.append(g)  # Important: add back to still list
                    else:
                        # If blocked only by another faller, don't lock mid-air.
                        if _blocked_only_by_faller(g, 0, 1, occupied_other):
                            dprint(fall_debug, f"[FALL] Block at ({g.x},{g.y}) blocked by faller; waiting")
                            still.append(g)
                            continue

                        # Lock in place (blocked by board/bottom)
                        try:
                            blockers = _debug_blockers_for_piece(g, 0, 1, occupied_other)
                            dprint(fall_debug, f"[FALL] Piece locked (blocked by board/bottom): {blockers[:6]}")
                        except Exception:
                            pass
                        
                        # Strike/sword fallers can pierce through blocks/breakers before settling.
                        pierced_any = False
                        if self._is_strike_piece(g):
                            if cluster_cells is None:
                                cluster_cells = self._compute_normal_cluster_cells()

                            # IMPORTANT: no mid-fall column shifting. If blocked by a cluster,
                            # resolve pierce/lock in the current column.
                            try:
                                for attr in ('_cluster_avoid_y', '_cluster_avoid_dx', '_cluster_avoid_seen_x'):
                                    if hasattr(g, attr):
                                        delattr(g, attr)
                            except Exception:
                                pass
                            pierced_any = self._resolve_strike_pierce_before_lock(g, cluster_cells)
                        
                        # If we pierced blocks, keep the piece falling so it can continue
                        # down through the newly cleared space. Otherwise lock it.
                        if pierced_any:
                            try:
                                if not bool(getattr(g, '_strike_land_noted', False)):
                                    setattr(g, '_strike_land_noted', True)
                                    try:
                                        self.strike_land_seq = int(getattr(self, 'strike_land_seq', 0) or 0) + 1
                                    except Exception:
                                        self.strike_land_seq = 1
                            except Exception:
                                pass
                            dprint(fall_debug, f"[FALL] Single faller at ({g.x},{g.y}) pierced blocks; continuing to fall")
                            still.append(g)
                        else:
                            # Ensure we write the block into the board when it settles
                            # Inbound top-out: if the piece contains any block above the board at
                            # lock time, it has overflowed.
                            try:
                                if any(int(y) < 0 for _x, y, _b in g.get_block_positions()):
                                    try:
                                        xs = [int(_x) for _x, _y, _b in g.get_block_positions()]
                                    except Exception:
                                        xs = []
                                    try:
                                        min_y = min(int(_y) for _x, _y, _b in g.get_block_positions())
                                    except Exception:
                                        min_y = -1
                                    self._mark_inbound_overflow(
                                        {
                                            'kind': 'single_faller',
                                            'attack_state': str(getattr(g, 'attack_state', '') or '').strip().lower(),
                                            'min_y': int(min_y),
                                            'cols': sorted(set(xs)) if xs else [],
                                        }
                                    )
                            except Exception:
                                pass
                            self.gravity_manager.lock_piece(g)
                            # Register new attack blocks with lifecycle if they have attack_state
                            # Attach board-space coordinates so lifecycle can pattern-color cgarbage correctly
                            for piece in [g]:  # g is already a single piece
                                for x, y, block in piece.get_block_positions():
                                    if getattr(block, 'attack_state', None):
                                        try:
                                            # Provide positional context to the lifecycle
                                            xi = int(x)
                                            yi = int(y)
                                            if not bool(self.board.is_in_bounds(xi, yi)):
                                                if yi < 0:
                                                    self._mark_inbound_overflow(
                                                        {
                                                            'kind': 'single_block',
                                                            'attack_state': str(getattr(block, 'attack_state', '') or '').strip().lower(),
                                                            'x': int(xi),
                                                            'y': int(yi),
                                                        }
                                                    )
                                                continue
                                            setattr(block, 'x', xi)
                                            setattr(block, 'y', yi)
                                            if getattr(block, 'attack_state', None) == 'strike':
                                                setattr(block, 'inbound_kind', 'strike')
                                                setattr(block, 'vstrike_left_x', int(xi))
                                                setattr(block, 'vstrike_width', 1)
                                                setattr(block, 'vstrike_height', int(getattr(g, 'sword_rows', 1) or 1))
                                                setattr(block, 'vstrike_x_offset', 0)
                                                setattr(block, 'vstrike_y_offset', 0)
                                            else:
                                                setattr(block, 'inbound_kind', 'sprinkle')
                                        except Exception:
                                            pass
                                        self._new_attack_blocks.append(block)
                            # Note: locked pieces are NOT added to still list - they're removed
                else:
                    g.autonomous_fall_timer += 1
                    still.append(g)
        # Debug spam removed - only log when pieces actually change
        if len(still) != len(self.garbage_fallers):
            dprint(fall_debug, f"[FALL DEBUG] Garbage pieces changed: {len(self.garbage_fallers)} -> {len(still)}")
        self.garbage_fallers = still

        # Short-deferred sprinkle drop (frame-based), so they don't wait for next lock
        if self.pending_in_sprinkle > 0 and self.inbound_delay == 0:
            # Do not spawn sprinkles while any strike fallers are active or while
            # delayed strike clusters are waiting to spawn.
            if self._has_active_strike_fallers() or (len(getattr(self, '_delayed_clusters', []) or []) > 0):
                return

            # Enforce a minimal deferral window after the last strike placement.
            last = getattr(self, '_last_strike_place_frame', None)
            if last is None:
                ok = True
            else:
                ok = (self.frame - last) >= int(getattr(self, '_sprinkle_deferral_frames', 0) or 0)

            if ok:
                # After strikes, keep sprinkles out of the strike columns when possible.
                # (They can still overflow into these columns if the board is nearly full.)
                avoid = getattr(self, '_last_strike_cols', set()) or set()
                placed = self._spawn_sprinkles_avoiding(self.pending_in_sprinkle, avoid, prefer_cols=set())
                self.pending_in_sprinkle = max(0, self.pending_in_sprinkle - placed)

    def _resolve_strike_cluster_pierce_before_lock(self, pieces: list[Piece], cluster_cells: set[tuple[int, int]]) -> bool:
        """Apply strike piercing rules for a whole vertical strike cluster (rigid sword).

        This prevents the sword from splitting when one column hits first.

        Shared rules (mirrors horizontal sword behavior):
        - One shared pierce budget for the whole sword.
        - Breakers can be destroyed only before piercing any normal blocks.
        - Cluster cells stop the sword.
        
        Returns:
            True if any blocks were pierced/destroyed, False otherwise.
        """
        if not pieces:
            return False

        # Shared pierce state must persist across ticks for the same falling cluster.
        try:
            cid = int(getattr(pieces[0], 'strike_cluster_id', 0) or 0)
        except Exception:
            cid = 0

        # Determine sword size for pierce budget.
        try:
            sword_rows = int(getattr(pieces[0], 'sword_rows', 1) or 1)
        except Exception:
            sword_rows = 1
        if cid:
            prior = getattr(self, '_strike_cluster_pierce_state', {}).get(int(cid))
        else:
            prior = None
        if prior is None:
            budget_left = int(self._strike_pierce_budget(sword_rows) or 0)
            pierced_any_normal = False
        else:
            try:
                budget_left = int(prior[0])
            except Exception:
                budget_left = int(self._strike_pierce_budget(sword_rows) or 0)
            pierced_any_normal = bool(prior[1])

        any_destroyed_total = False

        # Treat the cluster as rigid: advance as far as possible by clearing the bottom edge.
        while True:
            # Map x -> bottom-most y among pieces in that column.
            bottoms: dict[int, int] = {}
            for p in pieces:
                try:
                    px = int(getattr(p, 'x', 0))
                    py = int(getattr(p, 'y', 0))
                except Exception:
                    continue
                if px not in bottoms or py > bottoms[px]:
                    bottoms[px] = py

            if not bottoms:
                break

            # Inspect cells directly below the bottom edge.
            stop = False
            spark_cells: list[tuple[int, int]] = []

            # Breaker rule is evaluated relative to whether we've pierced normals in prior steps.
            pre_pierced_any_normal = bool(pierced_any_normal)

            # Decide and apply effects across ALL columns before stopping,
            # so wide swords don't only damage one column.
            any_pierced_this_step = False
            for px, py in bottoms.items():
                ny = py + 1
                if ny >= int(self.board.HEIGHT):
                    stop = True
                    continue
                cell = self.board.get_piece(px, ny)
                if cell == self.board.EMPTY or cell is None:
                    continue

                # Always stop on other attack blocks / garbage.
                # NOTE: sprinkles (attack_state='sprinkle') are treated like normal blocks and may be pierced.
                if bool(getattr(cell, 'hsword_hold', False)) or getattr(cell, 'is_strike', False) or getattr(cell, 'attack_state', None) == 'strike' or getattr(cell, 'is_garbage', False):
                    stop = True
                    continue

                # Breakers: destroy only if we haven't pierced any normal blocks yet.
                if getattr(cell, 'is_breaker', False):
                    if not pre_pierced_any_normal:
                        self.board.set_piece(px, ny, self.board.EMPTY)
                        any_destroyed_total = True
                        continue
                    stop = True
                    continue

                # Normal block.
                if (px, ny) in (cluster_cells or set()):
                    spark_cells.append((px, ny))
                    stop = True
                    continue

                # Normal block: pierce if the sword has remaining budget.
                if int(budget_left) <= 0:
                    stop = True
                    continue

                self.board.set_piece(px, ny, self.board.EMPTY)
                budget_left = int(budget_left) - 1
                any_pierced_this_step = True
                any_destroyed_total = True

            if any_pierced_this_step:
                pierced_any_normal = True

            if spark_cells:
                try:
                    side = 'player' if str(getattr(self.fighter, 'fighter_name', '')).strip().lower() == 'player' else 'ai'
                    spark_colors: list[str | None] = []
                    for sx, sy in (spark_cells or []):
                        try:
                            cell_obj = self.board.get_piece(int(sx), int(sy))
                            c = str(getattr(cell_obj, 'color', '') or '').strip().lower()
                            spark_colors.append(c if c else None)
                        except Exception:
                            spark_colors.append(None)
                    emit_sparks(spark_cells, side=side, colors=spark_colors)
                except Exception:
                    pass

            if stop:
                break

            # If we cleared blocks and/or there are empty spaces beneath, we can move the whole cluster down.
            # Only move if all bottom-edge below cells are empty now.
            can_step = True
            for px, py in bottoms.items():
                ny = py + 1
                if ny >= int(self.board.HEIGHT):
                    can_step = False
                    break
                cell = self.board.get_piece(px, ny)
                if not (cell == self.board.EMPTY or cell is None):
                    can_step = False
                    break

            if not can_step:
                break

            for p in pieces:
                try:
                    p.y = int(getattr(p, 'y', 0)) + 1
                except Exception:
                    pass

            # Continue loop: the sword may be able to pierce/fall further this tick.
        
        # Return True if we destroyed any blocks.
        if cid:
            try:
                self._strike_cluster_pierce_state[int(cid)] = (int(budget_left), bool(pierced_any_normal))
            except Exception:
                pass
        return bool(any_destroyed_total)

    def _has_active_controllable_piece(self) -> bool:
        try:
            # Access fighter movement if reachable via gravity_manager/mover
            # Fallback heuristic: check for any Piece with controllable=True in fallers
            for g in self.garbage_fallers:
                if getattr(g, 'controllable', False):
                    return True
        except Exception:
            pass
        return False

    def get_cluster_size_at(self, x, y, color):
        """Get the size of the color cluster containing the block at (x, y)."""
        visited = set()
        cluster = self._flood_fill_cluster(x, y, color, visited)
        return len(cluster)

    def _flood_fill_cluster(self, x, y, target_color, visited):
        """Flood fill to find all connected blocks of the same color."""
        if (x, y) in visited:
            return set()
        if not self.board.is_in_bounds(x, y):
            return set()

        block = self.board.get_piece(x, y)
        if block == self.board.EMPTY or not hasattr(block, 'color') or block.color != target_color:
            return set()

        # Skip garbage blocks in cluster detection
        if getattr(block, 'is_garbage', False):
            return set()

        visited.add((x, y))
        cluster = {(x, y)}

        # Check all 4 directions
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            cluster.update(self._flood_fill_cluster(x + dx, y + dy, target_color, visited))

        return cluster

    def get_garbage_fallers(self):
        """Get a copy of the current garbage fallers list."""
        return list(self.garbage_fallers)

    def add_garbage_fallers(self, pieces):
        """Add pieces to the garbage fallers list."""
        self.garbage_fallers.extend(pieces)

    def register_new_attack_block(self, block):
        """Register a new attack block for lifecycle processing."""
        self._new_attack_blocks.append(block)

    def has_ready_inbound(self) -> bool:
        """Return True if inbound attacks are ready to land this frame (delay expired)."""
        return (self.pending_in_sprinkle + self.pending_in_strike) > 0 and self.inbound_delay == 0

    def process_lifecycle_update(self):
        """Process attack lifecycle updates and return newly locked blocks."""
        # This is called at a piece-lock boundary.
        # Register blocks that locked since the previous boundary *before* advancing so
        # the first placement after an inbound strike correctly transitions strike->sprinkle.
        if self._new_attack_blocks:
            self.lifecycle.register_new_locked(self._new_attack_blocks)
            if self.debug_attack_lifecycle:
                dprint(self.debug_attack_lifecycle, f"[LIFECYCLE] Registered {len(self._new_attack_blocks)} new attack blocks")
            self._new_attack_blocks.clear()

        # Now advance lifecycle state for all tracked inbound blocks.
        self.lifecycle.advance()
        return []  # The advance method handles updates internally

    def _process_delayed_clusters(self):
        """Process delayed clusters, spawning them when their delay expires."""
        remaining = []
        for cluster in self._delayed_clusters:
            cluster.delay_frames -= 1
            if cluster.delay_frames <= 0:
                # Spawn the cluster now with Y offset
                self._spawn_strike_cluster(cluster.width, cluster.height, y_offset=cluster.y_offset)
            else:
                remaining.append(cluster)
        self._delayed_clusters = remaining

    def _spawn_multiple_strike_clusters(self, horizontal_swords_manager):
        """Process and spawn all pending strike clusters in the same tick (non-overlapping).

        Returns a set of column indices reserved by vertical strikes placed this tick.
        """
        clusters = list(self._pending_in_strike_clusters)
        if not clusters:
            return set()

        # Sort clusters by width ascending (fit more), then height descending
        clusters.sort(key=lambda x: (x[1][0], -x[1][1]) if x[0] != 'hsword' else (x[1][0], -x[1][1]))
        
        # Precompute cluster cells once for preselecting strike lanes.
        try:
            _cluster_cells_now = self._compute_normal_cluster_cells()
        except Exception:
            _cluster_cells_now = set()
        
        def _lane_surface_hits_cluster(left: int, w: int) -> bool:
            """True if any column in the lane has its topmost occupied block as a cluster cell."""
            try:
                board_h = int(self.board.HEIGHT)
            except Exception:
                board_h = 12
            for dx in range(int(w)):
                x = int(left) + int(dx)
                # Find first occupied cell from the top.
                first_y = None
                for y in range(board_h):
                    cell = self.board.get_piece(x, y)
                    if cell != self.board.EMPTY and cell is not None:
                        first_y = int(y)
                        break
                if first_y is None:
                    continue
                if (int(x), int(first_y)) in (_cluster_cells_now or set()):
                    return True
            return False

        # Capacity model for vertical strikes:
        # A rigid vertical strike cluster of height h will lock when any column under it is blocked.
        # It top-outs if it would need to occupy y < 0 in that blocking column.
        # For a given column, first_y is the topmost occupied y (or board_h if empty).
        # The cluster fits if min(first_y across lane) >= h.
        try:
            _board_h_cap = int(self.board.HEIGHT)
        except Exception:
            _board_h_cap = 12
        try:
            _board_w_cap = int(self.board.WIDTH)
        except Exception:
            _board_w_cap = 6
        _top_y_by_col: list[int] = []
        for _x in range(int(_board_w_cap)):
            _first_y = None
            for _y in range(int(_board_h_cap)):
                _cell = self.board.get_piece(int(_x), int(_y))
                if _cell != self.board.EMPTY and _cell is not None:
                    _first_y = int(_y)
                    break
            if _first_y is None:
                _first_y = int(_board_h_cap)
            _top_y_by_col.append(int(_first_y))

        def _lane_capacity(left: int, w: int) -> int:
            try:
                seg = _top_y_by_col[int(left): int(left) + int(w)]
                return int(min(seg)) if seg else 0
            except Exception:
                return 0

        # Plan placements for vertical clusters in one pass to maximize count
        reserved = [False] * self.board.WIDTH
        planned: List[tuple[int, int, int]] = []  # (left, w, h)
        delayed_vertical: List[tuple[int, int]] = []  # (w,h)

        # Build helper lists of positions per width
        def plan_place(w: int, h: int) -> int | None:
            total_positions = self.board.WIDTH - w + 1
            if total_positions <= 0:
                return None
            spawn_col = int(getattr(self, '_spawn_col', 3))

            # If *any* currently-available lane can fit this strike height, we must not
            # select a lane that cannot fit (even if it avoids the spawn column).
            # Otherwise we can create avoidable top-outs where the only safe lane spans
            # the spawn column.
            try:
                hh = int(h)
            except Exception:
                hh = 0
            fit_anywhere = False
            if hh > 0:
                try:
                    for p in range(int(total_positions)):
                        if not all(not reserved[int(p) + int(dx)] for dx in range(int(w))):
                            continue
                        if int(_lane_capacity(int(p), int(w))) >= int(hh):
                            fit_anywhere = True
                            break
                except Exception:
                    fit_anywhere = False

            # For 2-wide vertical swords, strongly prefer non-overlapping column-pairs.
            # This prevents scenarios where 3 simultaneous 2-wide swords on a 6-wide board
            # get forced into a delay due to a (1,4,...) placement choice.
            if int(w) == 2:
                ordered_all = [p for p in range(total_positions) if (p % 2) == 0] + [
                    p for p in range(total_positions) if (p % 2) == 1
                ]
            else:
                ordered_all = list(range(total_positions))

            # Prefer not spanning the spawn column, but ensure deterministic packing for 2-wide swords.
            pos_no_spawn = [p for p in ordered_all if not any((p + dx) == spawn_col for dx in range(w))]
            pos_with_spawn = [p for p in ordered_all if any((p + dx) == spawn_col for dx in range(w))]

            def pick_from(cands: list[int]) -> int | None:
                if not cands:
                    return None

                # Prefer candidate lanes that can fit this strike height without top-out.
                try:
                    fit = [p for p in cands if int(_lane_capacity(int(p), int(w))) >= int(h)]
                except Exception:
                    fit = []
                if fit:
                    cands = fit
                elif fit_anywhere:
                    # Do not pick a non-fitting lane if a fitting lane exists elsewhere;
                    # allow the caller to try other candidate groups (including spawn-spanning).
                    return None

                def _try(require_non_cluster_surface: bool) -> int | None:
                    # Rotate starting point to distribute placements over time.
                    rot = (self.frame // 3 + int(getattr(self, '_strike_rot_seed', 0)) + int(w)) % len(cands)
                    for i in range(len(cands)):
                        p = cands[(rot + i) % len(cands)]
                        if require_non_cluster_surface and _lane_surface_hits_cluster(int(p), int(w)):
                            continue
                        if all(not reserved[p + dx] for dx in range(w)):
                            try:
                                self._strike_rot_seed = (int(getattr(self, '_strike_rot_seed', 0)) + 1) % max(1, len(cands))
                            except Exception:
                                pass
                            return p
                    return None

                # Prefer lanes where the sword surface is not immediately a cluster.
                pick = _try(require_non_cluster_surface=True)
                if pick is not None:
                    return pick
                return _try(require_non_cluster_surface=False)

            # For 2-wide swords: fill even-pair positions before allowing odd positions.
            if int(w) == 2:
                pos_no_spawn_even = [p for p in pos_no_spawn if (p % 2) == 0]
                pos_no_spawn_odd = [p for p in pos_no_spawn if (p % 2) == 1]
                pos_with_spawn_even = [p for p in pos_with_spawn if (p % 2) == 0]
                pos_with_spawn_odd = [p for p in pos_with_spawn if (p % 2) == 1]

                pick = pick_from(pos_no_spawn_even)
                if pick is not None:
                    return pick
                pick = pick_from(pos_no_spawn_odd)
                if pick is not None:
                    return pick
                pick = pick_from(pos_with_spawn_even)
                if pick is not None:
                    return pick
                return pick_from(pos_with_spawn_odd)

            # Try avoid-spawn first.
            pick = pick_from(pos_no_spawn)
            if pick is not None:
                return pick
            # Allow spawn-including if needed.
            return pick_from(pos_with_spawn)

        # First handle horizontals immediately (as before), collect verticals for planning
        verticals: List[tuple[int, int]] = []
        horizontals: List[tuple[int, int]] = []
        for kind, dims in clusters:
            if kind == 'hsword':
                horizontals.append(dims)
            else:
                verticals.append(dims)

        # Place horizontals first (immediate lock)
        for rows, length in horizontals:
            dprint(self._debug_inbound, f"[INBOUND] Spawning horizontal sword (animated entry): rows={rows}, length={length}")
            try:
                horizontal_swords_manager.spawn_horizontal_sword(rows, length, frame=self.frame)
            except Exception:
                pass

        # Plan verticals to maximize simultaneous count
        for w, h in verticals:
            left = plan_place(w, h)
            if left is None:
                delayed_vertical.append((w, h))
            else:
                planned.append((left, w, h))
                for dx in range(w):
                    reserved[left + dx] = True

        # Spawn planned verticals now
        for left, w, h in planned:
            self._spawn_strike_cluster_at(left, w, h)

        # Delay any that couldn't fit
        for i, (w, h) in enumerate(delayed_vertical):
            delayed_cluster = DelayedCluster(w, h, delay_frames=4 + i)
            self._delayed_clusters.append(delayed_cluster)

        # Return the set of reserved columns used by verticals this tick
        reserved_cols_set = {i for i, used in enumerate(reserved) if used}
        return reserved_cols_set

    def _spawn_single(self, is_strike: bool):
        """Spawn a single garbage block."""
        base_index = len(self.garbage_fallers) + self.spawn_queue + self.pending_in_sprinkle + self.pending_in_strike
        col = self._get_safe_column(base_index)
        attack_state = 'strike' if is_strike else 'sprinkle'
        g = Piece.single_block(color='white' if is_strike else 'red', is_garbage=False, is_strike=is_strike, attack_state=attack_state)
        # Tag sword size for strike piercing logic (singles count as 1-row swords).
        if is_strike:
            try:
                g.sword_rows = 1
                g.sword_width = 1
            except Exception:
                pass
        g.x = col
        g.y = -1
        g.controllable = False
        # Inbound attacks should land promptly: make them fall faster than generic autonomous pieces.
        try:
            g.autonomous_fall_timer = 0
            g.autonomous_fall_interval = max(1, int(getattr(self.timing, 'autonomous_fall_interval_frames', 6)) // 2)
        except Exception:
            pass
        self.garbage_fallers.append(g)
        if self.debug_attack_lifecycle:
            dprint(self.debug_attack_lifecycle, f"[DEBUG] Spawn {'STRIKE' if is_strike else 'SPRINKLE'} single id={id(g.blocks[0])} col={col} state={attack_state}")

    def _spawn_bulk(self, amount: int, is_strike: bool):
        """Spawn multiple garbage blocks in bulk."""
        if amount <= 0:

            return
        dprint(self._debug_inbound, f"[INBOUND] _spawn_bulk called: amount={amount}, is_strike={is_strike}")
        w = int(self.board.WIDTH)
        order = self._sprinkle_column_order(set(), set())
        if not order:
            order = list(range(w))

        caps = self._sprinkle_capacity_by_col()
        existing = self._existing_inbound_spawn_count()
        used = [0] * w

        placed = 0
        idx = 0
        max_iters = max(1, amount) * max(1, w)
        iters = 0
        while placed < amount and iters < max_iters:
            iters += 1
            col = int(order[idx % len(order)])
            idx += 1
            if not (0 <= col < w):
                continue
            # Capacity must account for already-spawned above-board inbound in this column.
            if (int(caps[col]) - int(existing[col]) - int(used[col])) <= 0:
                # Overflow: try next columns with remaining capacity.
                continue

            attack_state = 'strike' if is_strike else 'sprinkle'
            g = Piece.single_block(
                color='white' if is_strike else 'red',
                is_garbage=False,
                is_strike=is_strike,
                attack_state=attack_state,
            )
            # Tag sword size for strike piercing logic.
            if is_strike:
                try:
                    g.sword_rows = 1
                    g.sword_width = 1
                except Exception:
                    pass
            g.x = col
            g.y = -1 - int(existing[col] + used[col])
            g.controllable = False
            g.autonomous_fall_timer = 0
            # Faster fall for inbound attacks.
            g.autonomous_fall_interval = max(1, int(getattr(self.timing, 'autonomous_fall_interval_frames', 6)) // 2)
            self.garbage_fallers.append(g)
            used[col] += 1
            placed += 1

        if placed < amount:
            dprint(self._debug_inbound, f"[INBOUND] Bulk overflow: placed={placed}/{amount} (no capacity)")

    def _spawn_sprinkles_avoiding(self, amount: int, avoid_cols: set[int], prefer_cols: set[int] | None = None) -> int:
        """Spawn sprinkles while preferring to avoid columns reserved by strikes this tick.

        Returns number of sprinkles spawned this call.
        """
        if amount <= 0:
            return 0
        turn_id = self._next_sprinkle_turn_id()
        w = int(self.board.WIDTH)
        avoid_cols = avoid_cols or set()
        prefer_cols = prefer_cols or set()

        # Height-based spawn-column protection.
        try:
            if self._should_lockout_spawn_col_for_sprinkles():
                avoid_cols = set(avoid_cols)
                avoid_cols.add(int(getattr(self, '_spawn_col', 3)))
        except Exception:
            pass

        column_order = self._sprinkle_column_order(avoid_cols, prefer_cols)
        if not column_order:
            column_order = list(range(w))

        # Overflow-aware even dispersal:
        # - round-robin across the priority order
        # - each column can only accept (HEIGHT - current_height) more blocks
        caps = self._sprinkle_capacity_by_col()
        existing = self._existing_inbound_spawn_count()
        used = [0] * w

        placed = 0
        idx = 0
        max_iters = max(1, amount) * max(1, len(column_order))
        iters = 0
        while placed < amount and iters < max_iters:
            iters += 1
            col = int(column_order[idx % len(column_order)])
            idx += 1
            if not (0 <= col < w):
                continue
            if (int(caps[col]) - int(existing[col]) - int(used[col])) <= 0:
                # Overflow to the next columns in priority order.
                continue

            g = Piece.single_block(color='red', is_garbage=False, is_strike=False, attack_state='sprinkle')
            try:
                for b in getattr(g, 'blocks', []) or []:
                    setattr(b, 'inbound_kind', 'sprinkle')
                    setattr(b, 'inbound_turn_id', int(turn_id))
            except Exception:
                pass
            g.x = col
            g.y = -1 - int(existing[col] + used[col])
            g.controllable = False
            g.autonomous_fall_timer = 0
            # Faster fall for inbound attacks.
            g.autonomous_fall_interval = max(1, int(getattr(self.timing, 'autonomous_fall_interval_frames', 6)) // 2)
            self.garbage_fallers.append(g)
            used[col] += 1
            placed += 1

        # Second pass: if we still have sprinkles to place but we skipped capacity due
        # to ordering/avoidance preferences, fill any remaining capacity anywhere.
        if placed < amount:
            # Preserve spawn-column protection if possible.
            sc = int(getattr(self, '_spawn_col', 3))
            lockout = False
            try:
                lockout = bool(self._should_lockout_spawn_col_for_sprinkles())
            except Exception:
                lockout = False
            all_cols = [c for c in range(w) if (not lockout) or (c != sc)]
            if not all_cols:
                all_cols = list(range(w))
            idx2 = 0
            max_iters2 = max(1, amount - placed) * max(1, w)
            iters2 = 0
            while placed < amount and iters2 < max_iters2:
                iters2 += 1
                col = int(all_cols[idx2 % len(all_cols)])
                idx2 += 1
                if not (0 <= col < w):
                    continue
                if (int(caps[col]) - int(existing[col]) - int(used[col])) <= 0:
                    continue
                g = Piece.single_block(color='red', is_garbage=False, is_strike=False, attack_state='sprinkle')
                try:
                    for b in getattr(g, 'blocks', []) or []:
                        setattr(b, 'inbound_kind', 'sprinkle')
                        setattr(b, 'inbound_turn_id', int(turn_id))
                except Exception:
                    pass
                g.x = col
                g.y = -1 - int(existing[col] + used[col])
                g.controllable = False
                g.autonomous_fall_timer = 0
                g.autonomous_fall_interval = max(1, int(getattr(self.timing, 'autonomous_fall_interval_frames', 6)) // 2)
                self.garbage_fallers.append(g)
                used[col] += 1
                placed += 1

            # Last resort: if we still couldn't place everything (all other cols full),
            # allow using the spawn column to avoid "dropping" attacks on the floor.
            if placed < amount and lockout and (0 <= sc < w) and ((int(caps[sc]) - int(existing[sc]) - int(used[sc])) > 0):
                idx3 = 0
                max_iters3 = max(1, amount - placed)
                iters3 = 0
                while placed < amount and iters3 < max_iters3 and ((int(caps[sc]) - int(existing[sc]) - int(used[sc])) > 0):
                    iters3 += 1
                    g = Piece.single_block(color='red', is_garbage=False, is_strike=False, attack_state='sprinkle')
                    try:
                        for b in getattr(g, 'blocks', []) or []:
                            setattr(b, 'inbound_kind', 'sprinkle')
                            setattr(b, 'inbound_turn_id', int(turn_id))
                    except Exception:
                        pass
                    g.x = sc
                    g.y = -1 - int(existing[sc] + used[sc])
                    g.controllable = False
                    g.autonomous_fall_timer = 0
                    g.autonomous_fall_interval = max(1, int(getattr(self.timing, 'autonomous_fall_interval_frames', 6)) // 2)
                    self.garbage_fallers.append(g)
                    used[sc] += 1
                    placed += 1

        return placed

    def _spawn_strike_cluster(self, width: int, height: int, color: str = 'white', y_offset: int = 0):
        """Spawn a vertical strike cluster as falling blocks (smooth), avoiding interleaving.

        We place the rectangle above the board so each block falls naturally to its column top.
        """
        if width <= 0 or height <= 0:
            return
        # Choose a left position that avoids spawn column and current strikes
        left = self._get_safe_cluster_position(width, height)

        # Spawn the cluster above the board so it falls down
        cluster_id = self._new_strike_cluster_id()
        handed = 1 if (int(cluster_id) % 2 == 0) else -1
        for dx in range(width):
            for dy in range(height):
                p = Piece.single_block(color=color, is_strike=True, attack_state='strike')
                p.x = left + dx
                p.y = -1 - dy - y_offset
                p.controllable = False
                # Stable handedness for cluster pathfinding around 2x2+ clusters.
                try:
                    p.strike_handedness = int(handed)
                except Exception:
                    pass
                # Tag sword size for strike piercing logic.
                try:
                    p.sword_rows = int(height)
                    p.sword_width = int(width)
                except Exception:
                    pass
                # Faster autonomous fall for strikes so they land promptly
                p.autonomous_fall_timer = 0
                p.autonomous_fall_interval = max(1, self.timing.autonomous_fall_interval_frames // 2)
                # Tag cluster
                p.strike_cluster_id = cluster_id
                try:
                    if getattr(p, 'blocks', None):
                        setattr(p.blocks[0], 'strike_cluster_id', cluster_id)
                except Exception:
                    pass
                self.garbage_fallers.append(p)
            dprint(self._debug_inbound, f"[INBOUND] Spawned vertical strike fallers {width}x{height} at left={left}")

    def _spawn_strike_cluster_at(self, left: int, width: int, height: int, color: str = 'white', y_offset: int = 0):
        """Spawn a vertical strike cluster at a specific left position as falling blocks."""
        if width <= 0 or height <= 0:
            return
        cluster_id = self._new_strike_cluster_id()
        handed = 1 if (int(cluster_id) % 2 == 0) else -1
        for dx in range(width):
            for dy in range(height):
                p = Piece.single_block(color=color, is_strike=True, attack_state='strike')
                p.x = left + dx
                p.y = -1 - dy - y_offset
                p.controllable = False
                try:
                    p.strike_handedness = int(handed)
                except Exception:
                    pass
                # Tag sword size for strike piercing logic.
                try:
                    p.sword_rows = int(height)
                    p.sword_width = int(width)
                except Exception:
                    pass
                p.autonomous_fall_timer = 0
                p.autonomous_fall_interval = max(1, self.timing.autonomous_fall_interval_frames // 2)
                p.strike_cluster_id = cluster_id
                try:
                    if getattr(p, 'blocks', None):
                        setattr(p.blocks[0], 'strike_cluster_id', cluster_id)
                except Exception:
                    pass
                self.garbage_fallers.append(p)
            dprint(self._debug_inbound, f"[INBOUND] Spawned vertical strike fallers {width}x{height} at left={left}")

    def _is_strike_piece(self, piece: Piece) -> bool:
        try:
            if getattr(piece, 'attack_state', None) == 'strike':
                return True
        except Exception:
            pass
        try:
            for b in getattr(piece, 'blocks', []) or []:
                if getattr(b, 'attack_state', None) == 'strike' or getattr(b, 'is_strike', False):
                    return True
        except Exception:
            pass
        return False

    def _strike_pierce_budget(self, sword_rows: int) -> int:
        """Pierce power based on sword length in rows."""
        try:
            r = int(sword_rows)
        except Exception:
            r = 1
        # Design rule: small swords (height <= 4) can pierce 2 blocks, then stop.
        if r <= 4:
            return 2
        if r <= 8:
            return 3
        return 4

    def _compute_normal_cluster_cells(self) -> set[tuple[int, int]]:
        """Return all cells that are part of a 2x2 (or larger) same-color *square* cluster.

        IMPORTANT: We intentionally mark only the cells that participate in at least
        one 2x2 square, not the entire connected component.

        Rationale: a single block "on top" of a 2x2 cluster should be pierceable
        (it is not itself part of a 2x2), even though it is connected by adjacency.

        Cluster checks exclude breakers, garbage, and strike/attack lifecycle blocks.
        """
        w = int(self.board.WIDTH)
        h = int(self.board.HEIGHT)

        def color_key(cell):
            if cell is None or cell == self.board.EMPTY:
                return None
            if getattr(cell, 'is_breaker', False):
                return None
            if getattr(cell, 'is_garbage', False):
                return None
            # Any inbound lifecycle block (strike/sprinkle/cgarbage) is not a normal colored block
            # for cluster purposes until it fully transforms (attack_state becomes None).
            if getattr(cell, 'attack_state', None):
                return None
            c = getattr(cell, 'color', None)
            return c

        cluster_cells: set[tuple[int, int]] = set()

        # Scan all possible 2x2 squares and mark their member cells.
        # Any larger rectangle will contain one or more 2x2 squares, so this
        # captures ">=2x2" naturally.
        for x in range(max(0, w - 1)):
            for y in range(max(0, h - 1)):
                c00 = color_key(self.board.get_piece(x, y))
                if c00 is None:
                    continue
                c10 = color_key(self.board.get_piece(x + 1, y))
                if c10 != c00:
                    continue
                c01 = color_key(self.board.get_piece(x, y + 1))
                if c01 != c00:
                    continue
                c11 = color_key(self.board.get_piece(x + 1, y + 1))
                if c11 != c00:
                    continue
                cluster_cells.add((x, y))
                cluster_cells.add((x + 1, y))
                cluster_cells.add((x, y + 1))
                cluster_cells.add((x + 1, y + 1))

        return cluster_cells

    def _resolve_strike_pierce_before_lock(self, g: Piece, cluster_cells: set[tuple[int, int]]) -> bool:
        """Mutate board + piece position to apply sword piercing rules before lock.

        - Destroys breakers on contact if no normal blocks have been pierced yet (can clear a stacked breaker column).
        - Pierces (destroys) up to N normal blocks that are NOT part of a cluster.
        - Stops when hitting a cluster cell, strike/garbage blocks, or a breaker after normal blocks were pierced.
        
        Returns:
            True if any blocks were pierced/destroyed, False otherwise.
        """
        try:
            x = int(getattr(g, 'x', 0))
            y = int(getattr(g, 'y', 0))
        except Exception:
            return False

        # Determine sword size for pierce budget.
        try:
            sword_rows = int(getattr(g, 'sword_rows', 1) or 1)
        except Exception:
            sword_rows = 1
        try:
            budget = int(getattr(g, 'pierce_budget_left'))
        except Exception:
            budget = int(self._strike_pierce_budget(sword_rows) or 0)
        pierced_any_normal = bool(getattr(g, 'pierced_any_normal', False))
        any_destroyed = False

        # Walk downward as far as we are allowed to pierce.
        while True:
            ny = y + 1
            if ny >= int(self.board.HEIGHT):
                break
            cell = self.board.get_piece(x, ny)
            if cell == self.board.EMPTY or cell is None:
                # If there's an empty gap (possible with partial locks/global gravity), just fall into it.
                y = ny
                continue

            # Always stop on other attack blocks / garbage.
            # NOTE: sprinkles (attack_state='sprinkle') are treated like normal blocks and may be pierced.
            if bool(getattr(cell, 'hsword_hold', False)) or getattr(cell, 'is_strike', False) or getattr(cell, 'attack_state', None) == 'strike' or getattr(cell, 'is_garbage', False):
                break

            # Breakers: destroy only if we haven't pierced any normal blocks yet.
            if getattr(cell, 'is_breaker', False):
                if not pierced_any_normal:
                    self.board.set_piece(x, ny, self.board.EMPTY)
                    any_destroyed = True
                    # Continue downward through stacked breakers.
                    continue
                # After piercing normal blocks, breakers underneath are safe.
                break

            # Normal block.
            if (x, ny) in (cluster_cells or set()):
                # Cluster contact stops the sword (sparks).
                try:
                    side = 'player' if str(getattr(self.fighter, 'fighter_name', '')).strip().lower() == 'player' else 'ai'
                    spark_color = None
                    try:
                        cell_obj = self.board.get_piece(int(x), int(ny))
                        c = str(getattr(cell_obj, 'color', '') or '').strip().lower()
                        spark_color = c if c else None
                    except Exception:
                        spark_color = None
                    emit_sparks([(x, ny)], side=side, colors=[spark_color])
                except Exception:
                    pass
                break
            if budget <= 0:
                break

            # Pierce (destroy) this normal block and advance.
            self.board.set_piece(x, ny, self.board.EMPTY)
            budget -= 1
            pierced_any_normal = True
            any_destroyed = True
            y = ny

        try:
            g.y = int(y)
        except Exception:
            pass

        # Persist state so repeated calls across frames don't reset the budget.
        try:
            setattr(g, 'pierce_budget_left', int(budget))
            setattr(g, 'pierced_any_normal', bool(pierced_any_normal))
        except Exception:
            pass
        
        # Return True if we destroyed any blocks (breakers or normals).
        return bool(any_destroyed)

    def _get_safe_column(self, base_index: int) -> int:
        """Get a column that avoids the configured spawn column for strike/garbage placement.

        Prefer columns that have remaining capacity once we account for already-spawned
        above-board inbound fallers in that column.
        """
        spawn_col = int(getattr(self, '_spawn_col', 3))
        try:
            w = int(self.board.WIDTH)
        except Exception:
            w = 6

        # Deterministic initial candidate (legacy behavior).
        candidate = ((base_index) * 3 + self.frame) % max(1, int(w))
        if int(candidate) == int(spawn_col):
            candidate = (int(candidate) + 1) % max(1, int(w))

        # Capacity-aware selection.
        try:
            caps = self._sprinkle_capacity_by_col()
            existing = self._existing_inbound_spawn_count()
        except Exception:
            caps = []
            existing = []

        def has_room(col: int) -> bool:
            try:
                return int(caps[int(col)]) - int(existing[int(col)]) > 0
            except Exception:
                return True

        if 0 <= int(candidate) < int(w) and has_room(int(candidate)):
            return int(candidate)

        cols = list(range(int(w)))
        try:
            rot = int(self.frame) % max(1, int(w))
        except Exception:
            rot = 0
        cols = cols[rot:] + cols[:rot]

        for col in cols:
            if int(col) == int(spawn_col):
                continue
            if has_room(int(col)):
                return int(col)
        for col in cols:
            if has_room(int(col)):
                return int(col)

        return int(candidate)

    def _get_safe_cluster_position(self, width: int, height: int | None = None) -> int:
        """Get a safe left position for a cluster that avoids the spawn column and doesn't overlap with existing strikes.

        If height is provided, prefer lanes with enough vertical capacity to avoid an avoidable top-out.
        """
        if width >= self.board.WIDTH:
            return 0

        spawn_col = int(getattr(self, '_spawn_col', 3))

        total_positions = self.board.WIDTH - width + 1
        # Build candidate left positions that avoid spawn column if possible
        candidates = [pos for pos in range(total_positions) if not any(pos + dx == spawn_col for dx in range(width))]
        fallback_all = (len(candidates) == 0)
        if fallback_all:
            candidates = list(range(total_positions))

        # Capacity filter (optional): keep candidates that can fit the requested height.
        if height is not None:
            try:
                h = int(height)
            except Exception:
                h = 0
            if h > 0 and candidates:
                try:
                    board_h = int(self.board.HEIGHT)
                except Exception:
                    board_h = 12
                top_y_by_col: list[int] = []
                for x in range(int(self.board.WIDTH)):
                    first_y = None
                    for y in range(int(board_h)):
                        cell = self.board.get_piece(int(x), int(y))
                        if cell != self.board.EMPTY and cell is not None:
                            first_y = int(y)
                            break
                    if first_y is None:
                        first_y = int(board_h)
                    top_y_by_col.append(int(first_y))

                fit = []
                for pos in candidates:
                    seg = top_y_by_col[int(pos): int(pos) + int(width)]
                    cap = int(min(seg)) if seg else 0
                    if cap >= int(h):
                        fit.append(int(pos))
                if fit:
                    candidates = fit
                else:
                    # If no avoid-spawn candidate fits, but a spawn-spanning lane does fit,
                    # prefer the fitting lane over any non-fitting avoid-spawn lane.
                    try:
                        total_positions = int(self.board.WIDTH) - int(width) + 1
                    except Exception:
                        total_positions = 0
                    if total_positions > 0:
                        fit_all: list[int] = []
                        for pos in range(int(total_positions)):
                            seg = top_y_by_col[int(pos): int(pos) + int(width)]
                            cap = int(min(seg)) if seg else 0
                            if cap >= int(h):
                                fit_all.append(int(pos))
                        if fit_all:
                            candidates = fit_all

        # Rotate candidates to spread usage over time and alternate bias
        if candidates:
            rot = (self.frame // 3 + self._strike_rot_seed) % len(candidates)
            # Scan starting at rotated index for a non-overlapping spot w.r.t current strike fallers
            for i in range(len(candidates)):
                base_pos = candidates[(rot + i) % len(candidates)]
                overlaps = False
                for g in self.garbage_fallers:
                    if hasattr(g, 'blocks') and any(getattr(b, 'is_strike', False) for b in g.blocks):
                        # Avoid spawning a new cluster into any active strike faller columns.
                        # (Not just those still at y == -1.)
                        try:
                            gx = int(getattr(g, 'x', -9999))
                        except Exception:
                            gx = -9999
                        if base_pos <= gx < (base_pos + int(width)):
                            overlaps = True
                            break
                    if overlaps:
                        break
                if not overlaps:
                    # Advance seed for next call to avoid repeated left bias
                    self._strike_rot_seed = (self._strike_rot_seed + 1) % max(1, len(candidates))
                    return base_pos

        # Fallback 1: find any position that avoids spawn column and fits
        for pos in range(self.board.WIDTH - width + 1):
            if not any(pos + dx == spawn_col for dx in range(width)):
                return pos

        # Fallback 2: as last resort, allow spanning spawn column if necessary; choose first fit
        for pos in range(self.board.WIDTH - width + 1):
            return pos

        # Should not happen, but default to 0
        return 0

    def _has_active_strike_fallers(self) -> bool:
        try:
            for g in self.garbage_fallers:
                if hasattr(g, 'blocks'):
                    for b in g.blocks:
                        if getattr(b, 'attack_state', None) == 'strike' or getattr(b, 'is_strike', False):
                            return True
        except Exception:
            pass
        return False
