"""
fighters/base_fighter.py - Base fighter class with shared functionality.

This contains all the common board mechanics that both players and AI use.
The only difference between fighters should be their input source.
"""
from __future__ import annotations
from typing import List, Dict, Any, Optional, Iterable
import os
import random

from swordfighting_new.core.board import Board
from swordfighting_new.pieces.piece import Piece
from swordfighting_new.pieces.shared_piece_queue import SharedPieceQueue
from swordfighting_new.mechanics.movement import PieceMover
from swordfighting_new.mechanics.gravity import GravityManager
from swordfighting_new.mechanics.combo import ComboManager
from swordfighting_new.mechanics.breaker import BreakerManager
from swordfighting_new.mechanics.chain_runner import BreakerChainRunner
from swordfighting_new.mechanics.timing import TimingConfig
from swordfighting_new.attacks import AttackManager, Attack, AttackKind, HorizontalSwordManager
from swordfighting_new.fighters.inbound_attack_handler import InboundAttackHandler
from swordfighting_new.attacks.garbage_pattern import PatternManager, SwordType
from swordfighting_new.fighters.movement_controller import MovementController
from swordfighting_new.util.stats_recorder import get_recorder


class BaseFighter:
    """Base fighter class containing all shared board mechanics.
    
    Both player-controlled and AI-controlled fighters inherit from this.
    The only difference should be how they generate their intents.
    """
    
    def __init__(self, timing: TimingConfig, spawn_x: int = 3,
                 attack_delay_frames: int = 24,
                 bulk_delivery: bool = True,
                 garbage_spawn_interval: int = 3,
                 enable_puzzle_speeds: bool = False,
                 puzzle_normal_us: int = 640000,
                 puzzle_fast_us: int = 2400,
                 lifecycle_debug: bool = False,
                 debug_attack_lifecycle: bool = False,
                 fighter_name: str = "Fighter",
                 piece_queue: SharedPieceQueue | None = None,
                 board: Board | None = None):
        
        self.fighter_name = fighter_name
        self.board = board if board is not None else Board()
        self.mover = PieceMover(self.board)
        self.gravity = GravityManager(self.board, self.mover, timing)
        self.combo = ComboManager(self.board)

        # Initialize movement controller
        self.movement = MovementController(self.board, self.mover, self.gravity, timing, spawn_x, piece_queue=piece_queue)

        # Breaker / chain resolution (simplified cascade system)
        self.breaker = BreakerManager(self.board)
        env_mode = os.getenv('BF_CASCADE_MODE', '').strip().lower()
        cascade_mode = env_mode if env_mode in ('step', 'fast') else 'step'
        self.chain_runner = BreakerChainRunner(
            self.board,
            self.breaker,
            frame_delay=max(0, timing.chain_frame_delay),
            cascade_mode=cascade_mode
        )

        self.attacks = AttackManager()
        self.horizontal_swords = HorizontalSwordManager(self.board, timing)
        self.spawn_x = spawn_x
        self.timing = timing
        self.attack_delay_frames = attack_delay_frames
        self.bulk_delivery = bulk_delivery
        self.garbage_spawn_interval = garbage_spawn_interval
        self.frame = 0

        # Pattern manager selection per fighter (can be customized later via inventory)
        self._pattern_manager = PatternManager()  # separate instance per fighter for flexibility

        # Weapon selection / session seed
        self._equipped_sword_type: SwordType = SwordType.CUTLASS
        self._match_seed: int | None = None

        # Fists weapon: one solid color per game.
        self._fists_color_key: str | None = None

        self.inbound_handler = InboundAttackHandler(
            board=self.board,
            timing=timing,
            piece_mover=self.mover,
            gravity_manager=self.gravity,
            attack_delay_frames=attack_delay_frames,
            bulk_delivery=bulk_delivery,
            garbage_spawn_interval=garbage_spawn_interval,
            lifecycle_debug=lifecycle_debug,
            debug_attack_lifecycle=debug_attack_lifecycle,
            color_provider=self._weapon_color_for_block
        )

        self.debug_attack_lifecycle = debug_attack_lifecycle

        if enable_puzzle_speeds:
            timing.use_puzzle_speeds = True
            timing.puzzle_normal_us = puzzle_normal_us
            timing.puzzle_fast_us = puzzle_fast_us

        # Runtime status
        self.defeated = False
        self._piece_spawn_frame = None  # track spawn frame for stats
        self.opponent = None  # will be set by session for opponent summary stats

        # Defeat instrumentation (used to diagnose "unfair defeat" reports).
        # Prefer fighter-level fields so session/UI can read a single place.
        self.last_defeat_reason: str | None = None
        self.last_defeat_context: dict[str, Any] = {}

        # Post-lock flow: we may wait for inbound garbage to settle before spawning
        self._waiting_to_spawn_post_chain = False
        # Between-pieces turn boundary: apply inbound lifecycle transforms once
        # before evaluating defeat/spawn guardrails.
        self._post_chain_lifecycle_applied = False

    def _record_defeat_reason(self, reason: str, context: dict[str, Any] | None = None) -> None:
        """Best-effort: record the first defeat reason/context for this fighter."""
        try:
            if getattr(self, 'last_defeat_reason', None) is not None:
                return
        except Exception:
            return
        try:
            self.last_defeat_reason = str(reason or '').strip().lower() or None
            self.last_defeat_context = dict(context or {})
        except Exception:
            pass

    def _sync_defeat_reason_from_movement(self) -> None:
        """If movement has a reason and fighter doesn't, copy it."""
        try:
            if getattr(self, 'last_defeat_reason', None) is not None:
                return
        except Exception:
            return
        mv = getattr(self, 'movement', None)
        if mv is None:
            return
        try:
            r = getattr(mv, 'last_defeat_reason', None)
            c = getattr(mv, 'last_defeat_context', None)
        except Exception:
            r, c = None, None
        if r:
            self._record_defeat_reason(str(r), dict(c or {}))

    def set_match_seed(self, seed: int | None) -> None:
        """Provide a session seed for any per-game fighter randomness.

        This must be stable within a match for deterministic behavior.
        """
        try:
            self._match_seed = int(seed) if seed is not None else None
        except Exception:
            self._match_seed = None

    def _ensure_fists_color_key(self) -> str:
        if self._fists_color_key is not None:
            return str(self._fists_color_key)

        palette = ('red', 'blue', 'green', 'yellow')
        try:
            s = int(self._match_seed) if self._match_seed is not None else None
        except Exception:
            s = None

        if s is None:
            self._fists_color_key = str(random.choice(list(palette)))
            return str(self._fists_color_key)

        rng = random.Random(int(s) ^ 0xF157_2026)
        self._fists_color_key = str(rng.choice(list(palette)))
        return str(self._fists_color_key)

    def _weapon_color_for_block(self, blk):
        """Return the correct inbound attack color for a block.

        Implements PATTERN_MASTER mapping rules using block metadata provided
        by inbound systems (sprinkle turn/layer, strike offsets, hsword info).
        """
        try:
            if getattr(self, '_equipped_sword_type', None) == SwordType.FISTS:
                return self._ensure_fists_color_key()
        except Exception:
            pass

        try:
            is_player = getattr(self, 'fighter_name', '').strip().lower() != 'enemy'
            pattern = self._pattern_manager.get_pattern_for_fighter(is_player)
        except Exception:
            return 'red'

        kind = str(getattr(blk, 'inbound_kind', '') or '').strip().lower()
        try:
            x = int(getattr(blk, 'x'))
            y = int(getattr(blk, 'y'))
        except Exception:
            x, y = 0, 0

        # Robust strike detection: some blocks may not carry inbound_kind (older paths).
        is_strike_like = (
            kind == 'strike'
            or bool(getattr(blk, 'is_strike', False))
            or str(getattr(blk, 'attack_state', '') or '').strip().lower() == 'strike'
            or hasattr(blk, 'vstrike_left_x')
            or hasattr(blk, 'strike_cluster_id')
            or hasattr(blk, 'hsword_length')
        )

        if kind == 'sprinkle':
            try:
                layer = int(getattr(blk, 'inbound_layer', 1) or 1)
            except Exception:
                layer = 1
            return pattern.get_sprinkle_color(int(x), int(y), layer=int(layer))

        if is_strike_like:
            # Horizontal sword metadata
            if bool(getattr(blk, 'hsword_hold', False)) or hasattr(blk, 'hsword_length'):
                try:
                    rows = int(getattr(blk, 'hsword_rows', 1) or 1)
                    length = int(getattr(blk, 'hsword_length', 1) or 1)
                    from_right = bool(getattr(blk, 'hsword_from_right', False))
                    col_off = int(getattr(blk, 'hsword_col_offset', 0) or 0)
                    y_off = int(getattr(blk, 'hsword_y_offset', 0) or 0)
                except Exception:
                    rows, length, from_right, col_off, y_off = 1, 1, False, 0, 0
                return pattern.get_strike_color(
                    x=0,
                    y=int(y),
                    strike_width=int(length),
                    strike_height=int(rows),
                    block_x_offset=int(col_off),
                    block_y_offset=int(y_off),
                    is_horizontal=True,
                    from_right=bool(from_right),
                )

            # Vertical strike cluster metadata
            try:
                left_x = int(getattr(blk, 'vstrike_left_x', int(x)) or int(x))
                width = int(getattr(blk, 'vstrike_width', 1) or 1)
                height = int(getattr(blk, 'vstrike_height', 1) or 1)
                x_off = int(getattr(blk, 'vstrike_x_offset', 0) or 0)
                y_off = int(getattr(blk, 'vstrike_y_offset', 0) or 0)
            except Exception:
                left_x, width, height, x_off, y_off = int(x), 1, 1, 0, 0

            # If metadata wasn't present, try to derive from strike_cluster_id on the board.
            if (width <= 1 and height <= 1 and x_off == 0 and y_off == 0):
                try:
                    cid = getattr(blk, 'strike_cluster_id', None)
                except Exception:
                    cid = None
                if cid is not None:
                    try:
                        w = int(getattr(self.board, 'WIDTH', 6) or 6)
                        h = int(getattr(self.board, 'HEIGHT', 12) or 12)
                        xs: list[int] = []
                        ys: list[int] = []
                        for xx in range(w):
                            for yy in range(h):
                                cell = self.board.get_piece(xx, yy)
                                if cell == self.board.EMPTY or cell is None:
                                    continue
                                if getattr(cell, 'strike_cluster_id', None) != cid:
                                    continue
                                xs.append(int(xx))
                                ys.append(int(yy))
                        if xs and ys:
                            left_x = int(min(xs))
                            right_x = int(max(xs))
                            top_y = int(min(ys))
                            bottom_y = int(max(ys))
                            width = int(right_x - left_x + 1)
                            height = int(bottom_y - top_y + 1)
                            x_off = int(x) - int(left_x)
                            y_off = int(bottom_y) - int(y)
                    except Exception:
                        pass

            return pattern.get_strike_color(
                x=int(left_x),
                y=int(y),
                strike_width=int(width),
                strike_height=int(height),
                block_x_offset=int(x_off),
                block_y_offset=int(y_off),
                is_horizontal=False,
                from_right=False,
            )

        # Fallback: behave like single-layer sprinkles.
        return pattern.get_sprinkle_color(int(x), int(y), layer=1)

    def update(self, intents: Dict[str, Any]):
        """Update fighter with the given intents.
        
        Intents format:
        {
            'move': -1|0|1,      # horizontal move (-1=left, 1=right, 0=none)
            'rotate_cw': bool,   # rotate clockwise
            'rotate_ccw': bool,  # rotate counter-clockwise  
            'fast': bool         # fast-fall (soft drop)
        }
        """
        self.frame += 1
        # Tag spawn_frame for current piece if not already tagged (dataset)
        curp = self.movement.current_piece
        if curp is not None and getattr(curp, 'spawn_frame', None) is None:
            setattr(curp, 'spawn_frame', self.frame)
        
        # Handle chain resolution first
        if self.chain_runner.active:
            self.chain_runner.update()
            if self.chain_runner.finished:
                # Chain finished - generate attacks and transition to post-chain phase
                self._handle_chain_completion()
                # Note: chain_runner resets itself when start() is called next time
            return

        # If we are in post-chain phase, deliver inbound (if any) and wait for it to settle
        if self._waiting_to_spawn_post_chain:
            # Turn-boundary rule: apply any pending inbound lifecycle transforms first.
            # This ensures blocks that are ready to transform on the next turn do so
            # before breaker clears and defeat guardrails are evaluated.
            if not bool(getattr(self, '_post_chain_lifecycle_applied', False)):
                try:
                    self.inbound_handler.process_lifecycle_update()
                except Exception:
                    pass
                self._post_chain_lifecycle_applied = True

            # If transforms created any breaker triggers, resolve them before
            # processing further inbound/gravity/defeat.
            try:
                bm = getattr(self, 'breaker', None)
                if bm is not None and (bool(getattr(bm, 'cascade_in_progress', False)) or bool(bm.has_pending_breakers())):
                    self.chain_runner.start()
                    return
            except Exception:
                pass

            self.inbound_handler.set_frame(self.frame)
            # Ensure any pending inbound is eligible to land now (we are between pieces)
            if (self.inbound_handler.pending_in_sprinkle + self.inbound_handler.pending_in_strike) > 0:
                self.inbound_handler.inbound_delay = 0
                self.inbound_handler.process_inbound(self.horizontal_swords)

            # IMPORTANT ordering (fairness): let the *board* settle first before inbound
            # fallers decide whether they must lock. Otherwise an inbound strike can
            # lock above-board against blocks that would have fallen this same frame.
            occupied = self._collect_transient_occupied_cells()
            self.gravity.apply_global_gravity(occupied_cells=occupied)

            # Tick inbound fallers and allow the board to settle under them
            self.inbound_handler.update_inbound_garbage()

            # Inbound top-out: if inbound locks above y=0, end immediately.
            try:
                if bool(getattr(self.inbound_handler, 'inbound_overflowed', False)):
                    try:
                        defeat_mode = str(os.getenv('BF_DEFEAT_MODE', '') or '').strip().lower()
                    except Exception:
                        defeat_mode = ''

                    if defeat_mode in ('b', 'mode_b', 'spawn_column_full'):
                        # Mode B: do not treat inbound overflow as an immediate defeat.
                        # Above-board strike cells are not written to the board; we simply
                        # continue and let the configured defeat rule decide.
                        try:
                            self.inbound_handler.inbound_overflowed = False
                        except Exception:
                            pass
                        try:
                            self.inbound_handler.last_inbound_overflow_context = {}
                        except Exception:
                            pass
                    else:
                        try:
                            overflow_ctx = dict(getattr(self.inbound_handler, 'last_inbound_overflow_context', {}) or {})
                        except Exception:
                            overflow_ctx = {}
                        overflow_ctx.update(
                            {
                                'phase': 'post_chain',
                                'frame': int(getattr(self, 'frame', 0) or 0),
                            }
                        )
                        self._record_defeat_reason('inbound_overflow', overflow_ctx)
                        try:
                            if getattr(self.movement, 'last_defeat_reason', None) is None and hasattr(self.movement, '_mark_defeat'):
                                self.movement._mark_defeat('inbound_overflow', dict(overflow_ctx))
                        except Exception:
                            pass
                        self.movement.defeated = True
                        self.defeated = True
                        self._waiting_to_spawn_post_chain = False
                        self._post_chain_lifecycle_applied = False
                        return
            except Exception:
                pass

            # One more settle pass after inbound moved/locked.
            occupied = self._collect_transient_occupied_cells()
            self.gravity.apply_global_gravity(occupied_cells=occupied)

            # If inbound landing/gravity created breaker triggers, resolve them
            # before defeat checks/spawn.
            try:
                bm = getattr(self, 'breaker', None)
                if bm is not None and (bool(getattr(bm, 'cascade_in_progress', False)) or bool(bm.has_pending_breakers())):
                    self.chain_runner.start()
                    return
            except Exception:
                pass

            # Movement updates do not run in this phase; explicitly check defeat rule.
            try:
                if bool(self.movement.check_game_over_column_full_defeat(transient_piece=None)):
                    self.defeated = True
                    self._sync_defeat_reason_from_movement()
                    self._waiting_to_spawn_post_chain = False
                    self._post_chain_lifecycle_applied = False
                    return
            except Exception:
                pass

            # Also allow true top-out from inbound: if the settled board fills the
            # entire top row, defeat immediately.
            try:
                try:
                    defeat_mode = str(os.getenv('BF_DEFEAT_MODE', '') or '').strip().lower()
                except Exception:
                    defeat_mode = ''
                if defeat_mode not in ('b', 'mode_b', 'spawn_column_full'):
                    if bool(getattr(self.movement, 'check_top_row_full_defeat', None)):
                        if bool(self.movement.check_top_row_full_defeat(transient_piece=None)):
                            self.defeated = True
                            self._sync_defeat_reason_from_movement()
                            self._waiting_to_spawn_post_chain = False
                            self._post_chain_lifecycle_applied = False
                            return
            except Exception:
                pass

            inbound_pending = (
                (self.inbound_handler.pending_in_sprinkle + self.inbound_handler.pending_in_strike) > 0
                or getattr(self.inbound_handler, 'spawn_queue', 0) > 0
                or len(getattr(self.inbound_handler, 'garbage_fallers', [])) > 0
                or len(getattr(self.inbound_handler, '_delayed_clusters', [])) > 0
            )

            if not inbound_pending:
                # Safe to spawn the next controllable piece now.
                spawned = self.movement.spawn_new_piece_post_chain()
                if not spawned:
                    self.defeated = True
                    self._sync_defeat_reason_from_movement()
                else:
                    npiece = self.movement.current_piece
                    if npiece is not None:
                        setattr(npiece, 'spawn_frame', self.frame)
                self._waiting_to_spawn_post_chain = False
                self._post_chain_lifecycle_applied = False
            return
        
        # Update movement (piece control)
        should_lock, gravity_applied = self.movement.update(intents, self.frame)

        if should_lock:
            self._lock_piece_and_start_chain()
            # IMPORTANT: Once a controllable piece locks, do not run any other
            # board-mutating systems in the same frame (global gravity, inbound
            # fallers, horizontal swords, etc.). The breaker chain resolution is
            # responsible for post-lock clears + cascades, and must see the
            # board state immediately after the lock.
            self.defeated = self.movement.is_defeated()
            if self.defeated:
                self._sync_defeat_reason_from_movement()
            return
        
        # Update defeated status from movement controller
        self.defeated = self.movement.is_defeated()
        if self.defeated:
            self._sync_defeat_reason_from_movement()
        
        # Tick inbound fallers every frame (autonomous blocks), but do NOT land new inbound here
        self.inbound_handler.set_frame(self.frame)
        self.inbound_handler.update_inbound_garbage()

        # Inbound top-out: if inbound locks above y=0, end immediately.
        try:
            if bool(getattr(self.inbound_handler, 'inbound_overflowed', False)):
                try:
                    defeat_mode = str(os.getenv('BF_DEFEAT_MODE', '') or '').strip().lower()
                except Exception:
                    defeat_mode = ''

                if defeat_mode in ('b', 'mode_b', 'spawn_column_full'):
                    # Mode B: do not treat inbound overflow as an immediate defeat.
                    try:
                        self.inbound_handler.inbound_overflowed = False
                    except Exception:
                        pass
                    try:
                        self.inbound_handler.last_inbound_overflow_context = {}
                    except Exception:
                        pass
                else:
                    try:
                        overflow_ctx = dict(getattr(self.inbound_handler, 'last_inbound_overflow_context', {}) or {})
                    except Exception:
                        overflow_ctx = {}
                    overflow_ctx.update(
                        {
                            'phase': 'active',
                            'frame': int(getattr(self, 'frame', 0) or 0),
                        }
                    )
                    self._record_defeat_reason('inbound_overflow', overflow_ctx)
                    try:
                        if getattr(self.movement, 'last_defeat_reason', None) is None and hasattr(self.movement, '_mark_defeat'):
                            self.movement._mark_defeat('inbound_overflow', dict(overflow_ctx))
                    except Exception:
                        pass
                    self.movement.defeated = True
                    self.defeated = True
                    return
        except Exception:
            pass

        # Apply global gravity to make floating blocks fall (CRITICAL for horizontal swords!)
        occupied = self._collect_transient_occupied_cells()
        self.gravity.apply_global_gravity(occupied_cells=occupied)
        
        # Update attack systems
        self.attacks.tick_all()
        
        # Process horizontal swords (this handles movement and returns newly locked pieces)
        new_falling_pieces, new_locked_blocks = self.horizontal_swords.update(self.frame)
        self.inbound_handler.add_garbage_fallers(new_falling_pieces)
        
        # Register newly locked horizontal sword blocks with lifecycle
        if new_locked_blocks:
            for piece in new_locked_blocks:
                for x, y, block in piece.get_block_positions():
                    if getattr(block, 'attack_state', None):
                        # Attach coordinates so lifecycle can color by weapon pattern
                        try:
                            setattr(block, 'x', x)
                            setattr(block, 'y', y)
                        except Exception:
                            pass
                        self.inbound_handler.register_new_attack_block(block)

    def postgame_settle_tick(self) -> None:
        """Advance only the "visual settling" systems for postgame.

        This avoids continuing normal turn gameplay (spawning/locking controllable
        pieces, generating new outgoing attacks) after the match is already decided.

        We intentionally still tick:
        - breaker chain resolution
        - inbound fallers + pending inbound spawns
        - horizontal swords already in-flight
        - global gravity to settle the board under transient fallers
        """
        try:
            self.frame = int(getattr(self, 'frame', 0) or 0) + 1
        except Exception:
            self.frame = 0

        # Continue any active breaker chain.
        try:
            if bool(getattr(self.chain_runner, 'active', False)):
                self.chain_runner.update()
                return
        except Exception:
            # If chain runner is misbehaving, don't deadlock settle.
            return

        # Allow already-queued inbound to spawn/land so defeat-causing attacks resolve visually.
        try:
            self.inbound_handler.set_frame(self.frame)
        except Exception:
            pass
        try:
            if (int(getattr(self.inbound_handler, 'pending_in_sprinkle', 0) or 0) + int(getattr(self.inbound_handler, 'pending_in_strike', 0) or 0)) > 0:
                try:
                    self.inbound_handler.inbound_delay = 0
                except Exception:
                    pass
                self.inbound_handler.process_inbound(self.horizontal_swords)
        except Exception:
            pass

        # Fairness ordering: settle board first, then tick inbound fallers.
        try:
            occupied = self._collect_transient_occupied_cells()
            self.gravity.apply_global_gravity(occupied_cells=occupied)
        except Exception:
            pass

        try:
            self.inbound_handler.update_inbound_garbage()
        except Exception:
            pass

        # Horizontal swords already in flight should keep moving/locking.
        try:
            new_falling_pieces, new_locked_blocks = self.horizontal_swords.update(self.frame)
            try:
                self.inbound_handler.add_garbage_fallers(new_falling_pieces)
            except Exception:
                pass
            if new_locked_blocks:
                for piece in new_locked_blocks:
                    for x, y, block in piece.get_block_positions():
                        if getattr(block, 'attack_state', None):
                            try:
                                setattr(block, 'x', int(x))
                                setattr(block, 'y', int(y))
                            except Exception:
                                pass
                            try:
                                self.inbound_handler.register_new_attack_block(block)
                            except Exception:
                                pass
        except Exception:
            pass

        # Settle again after inbound/swords moved.
        try:
            occupied = self._collect_transient_occupied_cells()
            self.gravity.apply_global_gravity(occupied_cells=occupied)
        except Exception:
            pass

        # If settling created breaker triggers, kick off a chain runner pass.
        try:
            bm = getattr(self, 'breaker', None)
            if bm is not None and (bool(getattr(bm, 'cascade_in_progress', False)) or bool(bm.has_pending_breakers())):
                self.chain_runner.start()
                return
        except Exception:
            pass

    def _collect_transient_occupied_cells(self) -> set[tuple[int, int]]:
        """Cells occupied by non-board pieces (current piece + garbage fallers)."""
        occupied: set[tuple[int, int]] = set()

        try:
            p = getattr(self.movement, 'current_piece', None)
            if p is not None:
                for x, y, _b in p.get_block_positions():
                    if self.board.is_in_bounds(x, y):
                        xi = int(x)
                        yi = int(y)
                        try:
                            if self.board.get_piece(xi, yi) == self.board.EMPTY:
                                occupied.add((xi, yi))
                        except Exception:
                            continue
        except Exception:
            pass

        try:
            for g in (getattr(self.inbound_handler, 'garbage_fallers', None) or []):
                try:
                    for x, y, _b in g.get_block_positions():
                        if self.board.is_in_bounds(x, y):
                            xi = int(x)
                            yi = int(y)
                            try:
                                if self.board.get_piece(xi, yi) == self.board.EMPTY:
                                    occupied.add((xi, yi))
                            except Exception:
                                continue
                except Exception:
                    continue
        except Exception:
            pass

        return occupied

    def receive_attacks(self, attacks: List[Attack]):
        """Receive attacks from opponent."""
        self.inbound_handler.receive_attacks(attacks)

    def collect_ready_attacks(self) -> List[Attack]:
        """Collect ready outbound attacks to send to opponent."""
        return self.attacks.collect_ready()

    def add_garbage_fallers(self, fallers: List[Piece]):
        """Add garbage fallers (e.g., from horizontal swords)."""
        self.inbound_handler.add_garbage_fallers(fallers)

    # Board state accessors (for rendering)
    def get_board(self):
        """Get board state for rendering."""
        return self.board

    def get_piece(self):
        """Get current falling piece."""
        return self.movement.current_piece

    def get_next_piece(self):
        """Get next piece preview."""
        return self.movement.next_piece

    def get_garbage_fallers(self):
        """Get falling garbage pieces."""
        return self.inbound_handler.garbage_fallers

    # --- Weapon pattern configuration ---------------------------------------
    def set_weapon_sword(self, sword_type: SwordType):
        """Set this fighter's weapon sword pattern.

        For the human player, this sets the player sword; for the enemy, the AI sword.
        """
        try:
            self._equipped_sword_type = sword_type
            is_player = getattr(self, 'fighter_name', '').lower() != 'enemy'
            if is_player:
                self._pattern_manager.set_player_sword(sword_type)
            else:
                self._pattern_manager.set_ai_sword(sword_type)
        except Exception:
            pass

    # Internal helper methods
    def _lock_piece_and_start_chain(self):
        """Lock current piece and start chain resolution."""
        # Lock the piece via movement controller
        cur = self.movement.current_piece
        locked_ok = self.movement.lock_current_piece()
        if not locked_ok:
            # Only treat as defeat if movement controller marked defeat.
            # (We may refuse to lock above-board pieces to prevent exploits.)
            if self.movement.is_defeated():
                self.defeated = True
                try:
                    self.movement.current_piece = None
                except Exception:
                    pass
            return
        # After locking, clear the active controllable piece until post-chain spawn.
        # This prevents a "frozen" next piece while inbound garbage is still landing.
        self.movement.current_piece = None

        # Horizontal swords: if a piece is placed adjacent/on-top, release held swords to gravity.
        try:
            hs = getattr(self, 'horizontal_swords', None)
            if hs is not None and cur is not None and hasattr(hs, 'notify_piece_locked'):
                hs.notify_piece_locked(cur)
        except Exception:
            pass
        
        # Stats: record piece outcome using cur
        rec = get_recorder()
        if rec.enabled and cur is not None:
            positions = [(x,y) for x,y,_ in cur.get_block_positions()]
            sf = getattr(cur, 'spawn_frame', None)
            # Outcome tagging: compare heights / holes vs decision snapshot
            heights_before = getattr(self, '_last_decision_heights', None)
            holes_before = getattr(self, '_last_decision_holes', None)
            heights_after = self.board.get_column_heights()
            # Convert heights_after (counts from bottom) to absolute heights from bottom (already that) ensure length
            if heights_before and len(heights_before) == len(heights_after):
                heights_delta = [ha - hb for hb, ha in zip(heights_before, heights_after)]
            else:
                heights_delta = None
            # Derive holes after
            holes_after = None
            try:
                from swordfighting_new.policies.heuristic_policy import HeuristicPolicy  # type: ignore
                # exploit _count_holes static-like method via temp policy? Instead implement quick count here
            except Exception:
                pass
            holes_after = self._count_holes_simple()
            rec.record_piece(self.frame, self.fighter_name, getattr(self,'seed',None), {
                'spawn_frame': sf,
                'lock_frame': self.frame,
                'age': None if sf is None else self.frame - sf,
                'pos': positions,
                'orientation': getattr(cur, 'orientation', None),
                'dec_id': getattr(self, '_last_decision_id', None),
                'dec_orient': getattr(cur, 'dec_orient', None),
                'dec_col': getattr(cur, 'dec_col', None),
                'dec_source': getattr(cur, 'dec_source', None),
                'board_w': self.board.WIDTH,
                'board_h': self.board.HEIGHT,
                'heights_before': heights_before,
                'heights_after': heights_after,
                'heights_delta': heights_delta,
                'holes_before': holes_before,
                'holes_after': holes_after
            })
            # For human/AI data: log a final decision snapshot at lock (one per piece)
            try:
                from swordfighting_new.util.board_hash import compute_board_hash
                from swordfighting_new.util.feature_indices import build_fvec_from_dict
                # Reconstruct a final decision approximating the locked placement
                final_rotation = 0 if getattr(cur, 'orientation', 0) in (0,2) else 1
                # Estimate landing x as average of block xs at lock (clamped)
                xs = [x for x,_ in [(p[0],p[1]) for p in positions]] if positions else []
                x_est = int(sum(xs)/len(xs)) if xs else getattr(cur, 'x', 0)
                x_est = max(0, min(self.board.WIDTH - 1, x_est))
                mask = [0] * (self.board.WIDTH * 2)
                hb = heights_after
                for c in range(self.board.WIDTH):
                    if hb[c] + 2 <= self.board.HEIGHT:
                        mask[0 * self.board.WIDTH + c] = 1
                for c in range(self.board.WIDTH - 1):
                    if max(hb[c], hb[c + 1]) + 1 <= self.board.HEIGHT:
                        mask[1 * self.board.WIDTH + c] = 1
                # Color/breaker-aware local features at lock
                clusters = 0
                breaker_adj = 0
                potential_rect2 = 0
                immediate_triggers = 0
                # Gather block colors from the locked piece
                try:
                    block_positions = list(cur.get_block_positions())
                except Exception:
                    block_positions = []
                for bx, by, block in block_positions:
                    col = getattr(block, 'color', None)
                    for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                        nx, ny = bx + dx, by + dy
                        if 0 <= nx < self.board.WIDTH and 0 <= ny < self.board.HEIGHT:
                            nb = self.board.get_piece(nx, ny)
                            if nb != self.board.EMPTY and nb is not None and getattr(nb, 'attack_state', None) is None and not getattr(nb, 'is_garbage', False):
                                if getattr(nb, 'color', None) == col:
                                    clusters += 1
                                    if getattr(nb, 'is_breaker', False):
                                        immediate_triggers += 1
                                if getattr(nb, 'is_breaker', False):
                                    breaker_adj += 1
                    # Check 2x2 same-color square including (bx,by)
                    for ox, oy in [(0,0),(1,0),(0,1),(1,1)]:
                        cx0, cy0 = bx + (ox-0), by + (oy-0)
                        # normalize to top-left of 2x2 window
                    # Evaluate four anchored windows
                    for ax, ay in [(-1,-1), (0,-1), (-1,0), (0,0)]:
                        coords = [(bx+ax,by+ay),(bx+ax+1,by+ay),(bx+ax,by+ay+1),(bx+ax+1,by+ay+1)]
                        ok = True
                        cols = []
                        for cx, cy in coords:
                            if not (0 <= cx < self.board.WIDTH and 0 <= cy < self.board.HEIGHT):
                                ok = False; break
                            cb = self.board.get_piece(cx, cy)
                            if cb == self.board.EMPTY or cb is None:
                                ok = False; break
                            cols.append(getattr(cb, 'color', None))
                        if ok and len(cols) == 4 and None not in cols and len(set(cols)) == 1:
                            potential_rect2 += 1
                # Next-piece lookahead (_look): quick potential score on resulting surface
                _look_val = 0.0
                try:
                    npiece = getattr(self.movement, 'next_piece', None)
                    if npiece is not None:
                        # Evaluate simple adjacency-based potential for next piece on heights_after
                        def adj_same(x:int,y:int,color):
                            if color is None: return 0.0
                            tot=0.0
                            for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
                                nx,ny=x+dx,y+dy
                                cell = self.board.get_piece(nx, ny)
                                if cell != self.board.EMPTY and cell is not None and getattr(cell,'color',None)==color:
                                    tot += 1.0
                            return tot
                        # Vertical placements
                        for c in range(self.board.WIDTH):
                            if hb[c] + 2 <= self.board.HEIGHT:
                                by = self.board.HEIGHT - 1 - hb[c]
                                ty = by - 1
                                c0 = getattr(npiece.blocks[0],'color',None)
                                c1 = getattr(npiece.blocks[1],'color',None)
                                s = adj_same(c,by,c0)+adj_same(c,ty,c1)
                                _look_val = max(_look_val, s)
                        # Horizontal placements
                        for c in range(self.board.WIDTH-1):
                            if max(hb[c], hb[c+1]) + 1 <= self.board.HEIGHT:
                                y = self.board.HEIGHT - 1 - max(hb[c], hb[c+1])
                                cL = getattr(npiece.blocks[0],'color',None)
                                cR = getattr(npiece.blocks[1],'color',None)
                                s = adj_same(c,y,cL)+adj_same(c+1,y,cR)
                                _look_val = max(_look_val, s)
                except Exception:
                    _look_val = 0.0

                chosen = {
                    'rotation': int(final_rotation),
                    'x': int(x_est),
                    'legal_mask': mask,
                    'features': {
                        'clusters': float(clusters),
                        'breaker_adjacency': float(breaker_adj),
                        'potential_rect2': float(potential_rect2),
                        'immediate_breaker_triggers': float(immediate_triggers),
                        'holes': float(holes_after),
                        'surface_bumpiness': float(sum(abs(hb[i]-hb[i+1]) for i in range(len(hb)-1))) if hb else 0.0,
                        'height_max': float(max(hb) if hb else 0),
                        '_base': 0.0,
                        '_look': float(_look_val),
                    },
                    'board_hash': int(compute_board_hash(self.board)),
                }
                # Opponent summary (minimal)
                opp = getattr(self, 'opponent', None)
                opp_summary = None
                try:
                    if opp is not None:
                        ob = opp.get_board()
                        oh = [0]*ob.WIDTH
                        for cx in range(ob.WIDTH):
                            for cy in range(ob.HEIGHT-1, -1, -1):
                                if ob.get_piece(cx, cy) != ob.EMPTY:
                                    oh[cx] = cy+1; break
                        opp_summary = {
                            'height_max': float(max(oh) if oh else 0),
                            'holes': float(self._count_holes_simple()),
                            'pending_sprinkle': float(getattr(self.inbound_handler, 'pending_in_sprinkle', 0)),
                            'pending_strike': float(getattr(self.inbound_handler, 'pending_in_strike', 0)),
                            'inbound_delay': float(getattr(self.inbound_handler, 'inbound_delay', 0)),
                        }
                except Exception:
                    opp_summary = None
                # Embed fvec for direct dataset use
                try:
                    fvec = build_fvec_from_dict(chosen['features'], opp_summary or {}, chosen['board_hash'])
                    chosen['fvec'] = fvec
                except Exception:
                    pass
                # Tag role consistently: 'player' for PlayerFighter, 'ai' otherwise
                role = 'player' if getattr(self, 'fighter_name', '').lower() == 'player' else 'ai'
                self._last_decision_id = (getattr(self, '_last_decision_id', 0) or 0) + 1
                rec.record_decision(self.frame, role, getattr(self, 'seed', None), self._last_decision_id, {'why':'final_lock'}, None, chosen)
            except Exception:
                pass
        
        # Start chain resolution
        self.chain_runner.start()
    
    def _handle_chain_completion(self):
        """Handle chain completion - generate attacks and spawn new piece."""
        # Generate attacks from chain results
        results = self.chain_runner.get_legacy_results()
        if results:
            chains, total, per_pass = results
            try:
                import os
                if os.getenv('BF_DEBUG_FIGHTER', '0') == '1':
                    print(f"[{self.fighter_name.upper()}] Chain finished: {chains} passes, {total} total cleared")
            except Exception:
                pass

            # Expose chain results on the breaker manager for scoring/UI.
            # In this codebase, the chain is resolved by BreakerChainRunner, so we
            # forward its results into BreakerManager's legacy fields.
            try:
                bm = getattr(self, 'breaker', None)
                if bm is not None:
                    bm.last_chain_results = (int(chains), int(total), list(per_pass))
                    try:
                        hist = self.chain_runner.get_pass_stats() or []
                        bm.last_pass_stats = (hist[-1] if hist else None)
                    except Exception:
                        bm.last_pass_stats = None
            except Exception:
                pass
            
            # Generate attacks from chain history
            history = self.chain_runner.get_pass_stats()
            self.attacks.generate_from_chain(history, self.board.WIDTH, self.board.HEIGHT)
            
            # Set delay on generated attacks
            for atk in self.attacks.generated_last_chain:
                atk.delay = self.attack_delay_frames
        
        # Process combos
        combo_count, total = self.combo.process_clears()
        if combo_count:
            try:
                import os
                if os.getenv('BF_DEBUG_FIGHTER', '0') == '1':
                    print(f"[{self.fighter_name.upper()}] Combo {combo_count} cleared {total}")
            except Exception:
                pass
        
        # Transition into a post-chain phase: deliver inbound (if any), wait for it to settle, then spawn.
        was_waiting = bool(getattr(self, '_waiting_to_spawn_post_chain', False))
        self._waiting_to_spawn_post_chain = True
        # Only reset turn-boundary lifecycle application when we are newly entering
        # the between-pieces phase; if a chain is triggered while already between
        # pieces (e.g., from lifecycle transforms), do not advance twice.
        if not was_waiting:
            self._post_chain_lifecycle_applied = False
    # --- Simple hole counter (duplicate of heuristic feature) -----------------
    def _count_holes_simple(self):
        holes = 0
        # A hole: empty cell with any filled cell above in same column
        for x in range(self.board.WIDTH):
            filled_seen = False
            for y in range(self.board.HEIGHT):
                cell = self.board.get_piece(x, y)
                if cell != self.board.EMPTY:
                    filled_seen = True
                else:
                    if filled_seen:
                        holes += 1
        return holes
