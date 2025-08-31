"""ai.py - Simple randomized AI controller for an enemy board.

Responsibilities:
 - Maintain its own board state (piece spawn, gravity, breaker chains)
 - Perform occasional lateral moves, rotations, and fast-fall bursts
 - Mirror player gravity/chain logic without user input

Design goals (first pass):
 - Keep AI intentionally imperfect / low skill
 - Fast-fall (space analog) should be used sparingly, not held forever
 - Deterministic-ish pacing using a fixed decision interval
"""

from __future__ import annotations

import random
from typing import Optional, List

from swordfighting_new.core.board import Board
from swordfighting_new.pieces.piece import Piece
from swordfighting_new.mechanics.movement import PieceMover
from swordfighting_new.mechanics.gravity import GravityManager
from swordfighting_new.mechanics.breaker import BreakerManager
from swordfighting_new.mechanics.chain_runner import BreakerChainRunner
from swordfighting_new.mechanics.combo import ComboManager
from swordfighting_new.mechanics.timing import TimingConfig
from swordfighting_new.attacks import AttackManager, AttackKind


class AIFighter:
    """Lightweight AI controlling an opponent board with simple random actions."""

    DECISION_INTERVAL = 10
    H_MOVE_PROB = 0.55
    ROTATE_PROB = 0.25
    FAST_TRIGGER_PROB = 0.18
    FAST_BURST_MIN = 18
    FAST_BURST_MAX = 40

    def __init__(self, timing: TimingConfig, spawn_x: int = 6, seed: Optional[int] = None):
        if seed is not None:
            random.seed(seed)
        # Core state components
        self.board = Board()
        self.mover = PieceMover(self.board)
        self.gravity = GravityManager(self.board, self.mover, timing)
        self.breakers = BreakerManager(self.board)
        self.chain_runner = BreakerChainRunner(
            self.board,
            self.breakers,
            frame_delay=max(15, timing.chain_frame_delay),  # Increased minimum for visual feedback
            cascade_mode='step'
        )
        # Modular attacks manager (AI outbound)
        self.attacks = AttackManager()
        self.combo = ComboManager(self.board)
        self.timing = timing
        self.spawn_x = spawn_x
        self.current_piece = Piece.spawn_random(self.spawn_x)
        # Runtime flags / counters
        self.frame = 0
        self.fast = False
        self._fast_remaining = 0
        self._pending_garbage = 0  # singles queued for gradual spawn
        self._garbage_fallers = []
        self.defeated = False
        self._pending_outbound_sprinkle = 0  # legacy aggregation (kept for now)
        self._pending_outbound_strike = 0
        # Inbound attack lifecycle tracking (mirrors player side logic)
        self._inbound_attack_blocks = []      # blocks currently on board with attack_state
        self._new_attack_blocks = []          # blocks locked this frame (promoted next piece lock)

    # ------------------------------------------------------------------
    def _spawn_new_piece(self):
        self.current_piece = Piece.spawn_random(self.spawn_x)
        self.fast = False
        self._fast_remaining = 0
        # Game over if overlapping visible cells (y>=0)
        for x, y, _ in self.current_piece.get_block_positions():
            if y >= 0 and self.board.get_piece(x, y) != self.board.EMPTY:
                self.defeated = True
                break

    # --- Decision logic -------------------------------------------------
    def _maybe_decide_actions(self):
        if self.frame % self.DECISION_INTERVAL != 0:
            return
        p = self.current_piece
        if not p.controllable:
            return
        # Horizontal move
        if random.random() < self.H_MOVE_PROB:
            dx = random.choice([-1, 1])
            self.mover.move(p, dx, 0)
        # Rotation
        if random.random() < self.ROTATE_PROB:
            self.mover.rotate(p, clockwise=random.random() < 0.5)
        # Fast-fall burst trigger (only if not already fast)
        if self._fast_remaining <= 0 and random.random() < self.FAST_TRIGGER_PROB:
            self._fast_remaining = random.randint(self.FAST_BURST_MIN, self.FAST_BURST_MAX)

    # --- Update loop ----------------------------------------------------
    def update(self):
        if self.defeated:
            return
        # Chain resolution first
        if self.chain_runner.active:
            self.chain_runner.update()
            if self.chain_runner.finished:
                # Process combos after full chain (if any)
                combo_count, total = self.combo.process_clears()
                if combo_count:
                    # Minimal debug print; caller may suppress
                    print(f"[AI] Combo {combo_count} cleared {total}")
                # Generate attacks from chain history and queue outbound amount
                history = self.chain_runner.get_pass_stats()
                if history:
                    self.attacks.generate_from_chain(history, self.board.WIDTH, self.board.HEIGHT)
                    # Normalize delays to global pacing
                    for atk in self.attacks.generated_last_chain:
                        atk.delay = max(atk.delay, 0)  # will be advanced by tick
                    print(f"[AI] Generated attacks {[ (a.kind, a.amount) for a in self.attacks.generated_last_chain ]}")
                self._spawn_new_piece()
            return
        self.frame += 1
        # Decrement fast burst timer
        if self._fast_remaining > 0:
            self._fast_remaining -= 1
            self.fast = True
        else:
            self.fast = False
        # Random decision making
        self._maybe_decide_actions()
        # Gravity interval per timing config
        # But skip timing control if piece has become autonomous (non-controllable)
        if self.current_piece.controllable:
            interval = self.timing.interval_for_level(level=1, fast=self.fast)
            if self.frame % max(1, interval) == 0:
                if not self.gravity.apply_gravity(self.current_piece):
                    # Mirror player: advance existing inbound attack blocks once per piece lock
                    self._advance_inbound_attack_blocks()
                    # Lock current piece
                    self.gravity.lock_piece(self.current_piece)
                    # Promote any newly locked attack blocks from garbage fall earlier this frame
                    if self._new_attack_blocks:
                        self._inbound_attack_blocks.extend(self._new_attack_blocks)
                        self._new_attack_blocks = []
                    self.chain_runner.start()
        else:
            # Autonomous piece - apply gravity every frame, let the piece handle its own timing
            if not self.gravity.apply_gravity(self.current_piece):
                # Mirror player: advance existing inbound attack blocks once per piece lock
                self._advance_inbound_attack_blocks()
                # Lock current piece
                self.gravity.lock_piece(self.current_piece)
                # Promote any newly locked attack blocks from garbage fall earlier this frame
                if self._new_attack_blocks:
                    self._inbound_attack_blocks.extend(self._new_attack_blocks)
                    self._new_attack_blocks = []
                self.chain_runner.start()
        # Spawn inbound garbage singles gradually (limit concurrent fallers)
        self._spawn_garbage_if_needed()
        # Update garbage fallers
        self._update_garbage_fallers()

    # --- Rendering helpers ----------------------------------------------
    def get_board(self) -> Board:
        return self.board

    def get_piece(self) -> Piece:
        return self.current_piece

    # --- Garbage / attacks interface ----------------------------------
    def add_garbage(self, amount: int):
        if amount <= 0:
            return
        # Bulk delivery path: spawn immediately in even stacks
        try:
            from swordfighting_new.pygame_client import BULK_GARBAGE_DELIVERY  # local import to avoid cycle at module load
        except Exception:
            BULK_GARBAGE_DELIVERY = False
        if BULK_GARBAGE_DELIVERY:
            self._spawn_bulk_garbage(amount)
        else:
            self._pending_garbage += amount

    def collect_outbound_attack_amount(self) -> int:
        total = self._pending_outbound_sprinkle + self._pending_outbound_strike
        self._pending_outbound_sprinkle = 0
        self._pending_outbound_strike = 0
        return total

    def collect_outbound_attack_breakdown(self):
        spr, stk = self._pending_outbound_sprinkle, self._pending_outbound_strike
        self._pending_outbound_sprinkle = 0
        self._pending_outbound_strike = 0
        return spr, stk

    def add_strikes(self, amount: int):
        if amount <= 0:
            return
        for _ in range(amount):
            col = random.randrange(self.board.WIDTH)
            s = Piece.single_block(color='white', is_strike=True, attack_state='strike')
            s.x = col
            s.y = -1
            s.controllable = False
            self._garbage_fallers.append(s)

    def add_strike_cluster(self, width: int, height: int, color: str = 'yellow'):
        if width <= 0 or height <= 0:
            return
        if width >= self.board.WIDTH:
            left = 0
        else:
            left = random.randrange(self.board.WIDTH - width + 1)
        for dx in range(width):
            for dy in range(height):
                p = Piece.single_block(color='white', is_strike=True, attack_state='strike')
                p.x = left + dx
                p.y = -1 - dy
                p.controllable = False
                self._garbage_fallers.append(p)

    def add_horizontal_sword(self, rows: int, length: int, color: str = 'white'):
        """Add a horizontal sword that enters from the side of the board."""
        if rows <= 0 or length <= 0:
            return

        # Create a horizontal sword piece
        p = Piece.single_block(color=color, is_strike=True, attack_state='strike')
        p.controllable = False
        p.horizontal_sword = True
        p.sword_rows = rows
        p.sword_length = length

        # Determine entry side - alternate for now (could be based on game state)
        sword_count = self.frame // 10
        p.sword_from_right = (sword_count % 2) == 0

        # Calculate vertical position (2 rows below highest block)
        highest_block = 0
        for x in range(self.board.WIDTH):
            for y in range(self.board.HEIGHT):
                if self.board.get_piece(x, y) != self.board.EMPTY:
                    highest_block = max(highest_block, self.board.HEIGHT - y)
                    break

        # Position 2 rows below highest block, or middle if board is empty
        top_row = max(2, self.board.HEIGHT - highest_block - 2) if highest_block > 0 else self.board.HEIGHT // 2

        # Ensure sword fits within board height
        if top_row + rows > self.board.HEIGHT:
            top_row = self.board.HEIGHT - rows
        if top_row < 0:
            top_row = 0

        # Start outside the board
        if p.sword_from_right:
            p.x = self.board.WIDTH  # Start to the right
        else:
            p.x = -1  # Start to the left

        p.y = top_row
        print(f"[AI DEBUG] Adding horizontal sword: rows={rows}, length={length}, from_right={p.sword_from_right}, start_x={p.x}, y={p.y}")
        self._garbage_fallers.append(p)

    def _get_horizontal_sword_blocks(self, sword_piece):
        """Get all block positions for a horizontal sword."""
        blocks = []
        if not hasattr(sword_piece, 'sword_rows') or not hasattr(sword_piece, 'sword_length'):
            return [(sword_piece.x, sword_piece.y)]

        for row_offset in range(sword_piece.sword_rows):
            for col_offset in range(sword_piece.sword_length):
                if sword_piece.sword_from_right:
                    block_x = sword_piece.x - col_offset
                else:
                    block_x = sword_piece.x + col_offset
                block_y = sword_piece.y + row_offset
                blocks.append((block_x, block_y))
        return blocks

    # New: tick and consume ready outbound Attack objects (returns list)
    def tick_attack_delivery(self, delivery_delay_frames: int):
        # Use a uniform external pacing: if an attack still has default delay, set to delivery_delay_frames once
        for atk in self.attacks.queue:
            if atk.delay == 0:  # already scheduled immediate
                continue
        self.attacks.tick_all()
        return self.attacks.consume_ready()

    def _spawn_garbage_if_needed(self):
        if self._pending_garbage <= 0:
            return
        max_concurrent = 6
        capacity = max(0, max_concurrent - len(self._garbage_fallers))
        if capacity <= 0:
            return
        spawn_now = min(capacity, self._pending_garbage)
        for _ in range(spawn_now):
            col = random.randrange(self.board.WIDTH)
            g = Piece.single_block(color='red', is_garbage=False, attack_state='sprinkle')
            g.x = col
            g.y = -1
            g.controllable = False
            self._garbage_fallers.append(g)
            self._pending_garbage -= 1

    def _update_garbage_fallers(self):
        still = []
        do_fall = (self.frame % max(1, self.timing.garbage_fall_interval_frames) == 0)
        for g in self._garbage_fallers:
            # Handle horizontal swords movement
            if hasattr(g, 'horizontal_sword') and g.horizontal_sword:
                # Move horizontal sword at a controlled pace
                move_horizontal = (self.frame % max(1, self.timing.garbage_fall_interval_frames // 2) == 0)
                if move_horizontal:
                    old_x = g.x
                    if hasattr(g, 'sword_from_right') and g.sword_from_right:
                        # Moving from right to left
                        g.x -= 1
                        if g.x + g.sword_length < 0:  # Sword has completely exited
                            continue  # Remove from garbage_fallers
                    else:
                        # Moving from left to right
                        g.x += 1
                        if g.x >= self.board.WIDTH:  # Sword has exited
                            continue  # Remove from garbage_fallers

                    # Check if sword should lock (hit something or reached penetration limit)
                    sword_blocks = self._get_horizontal_sword_blocks(g)
                    should_lock = False

                    # Count how many blocks have penetrated the board
                    blocks_in_board = 0
                    for block_x, block_y in sword_blocks:
                        if 0 <= block_x < self.board.WIDTH and 0 <= block_y < self.board.HEIGHT:
                            blocks_in_board += 1
                            existing = self.board.get_piece(block_x, block_y)
                            if existing != self.board.EMPTY:
                                should_lock = True
                                print(f"[AI DEBUG] Horizontal sword hit obstacle at ({block_x},{block_y})")
                                break

                    # Also lock if the sword has fully penetrated (all its length is in the board)
                    if blocks_in_board >= g.sword_length:
                        should_lock = True
                        print(f"[AI DEBUG] Horizontal sword fully penetrated (length={g.sword_length})")

                    # Or if leading edge has reached a certain penetration depth
                    if g.sword_from_right:
                        # Moving left: lock when front edge reaches middle of board or hits something
                        front_x = g.x - g.sword_length + 1
                        if front_x <= self.board.WIDTH // 2:
                            should_lock = True
                            print(f"[AI DEBUG] Horizontal sword reached penetration limit (front_x={front_x})")
                    else:
                        # Moving right: lock when front edge reaches middle of board or hits something
                        front_x = g.x + g.sword_length - 1
                        if front_x >= self.board.WIDTH // 2:
                            should_lock = True
                            print(f"[AI DEBUG] Horizontal sword reached penetration limit (front_x={front_x})")

                    if should_lock:
                        # Lock all sword blocks that are within the board
                        for block_x, block_y in sword_blocks:
                            if 0 <= block_x < self.board.WIDTH and 0 <= block_y < self.board.HEIGHT:
                                if self.board.get_piece(block_x, block_y) == self.board.EMPTY:
                                    from swordfighting_new.pieces.piece import Block
                                    template_block = g.blocks[0]
                                    new_block = Block(
                                        color=template_block.color,
                                        is_breaker=template_block.is_breaker,
                                        is_garbage=template_block.is_garbage,
                                        is_strike=template_block.is_strike,
                                        attack_state=template_block.attack_state
                                    )
                                    self.board.set_piece(block_x, block_y, new_block)
                                    if getattr(new_block, 'attack_state', None):
                                        self._new_attack_blocks.append(new_block)
                        continue  # Remove from garbage_fallers

                still.append(g)
                continue

            # Regular falling garbage logic
            if do_fall:
                if not self.gravity.apply_gravity(g):
                    # Lock and drop
                    self.gravity.lock_piece(g)
                    for x, y, block in g.get_block_positions():
                        if getattr(block, 'attack_state', None):
                            self._new_attack_blocks.append(block)
                else:
                    still.append(g)
            else:
                still.append(g)
        self._garbage_fallers = still

    def get_garbage_fallers(self):
        return list(self._garbage_fallers)

    # Bulk spawn helper mirrors player bulk logic
    def _spawn_bulk_garbage(self, amount: int):
        if amount <= 0:
            return
        w = self.board.WIDTH
        per_col = amount // w
        remainder = amount % w
        start_offset = (self.frame // 5) % w
        for i in range(w):
            col = (start_offset + i) % w
            stack_height = per_col + (1 if i < remainder else 0)
            for s in range(stack_height):
                g = Piece.single_block(color='red', is_garbage=False, attack_state='sprinkle')
                g.x = col
                g.y = -1 - s
                g.controllable = False
                self._garbage_fallers.append(g)

    # --- Inbound attack lifecycle (mirrors player) ----------------------
    def _advance_inbound_attack_blocks(self):
        if not self._inbound_attack_blocks:
            return
        remaining = []
        for blk in self._inbound_attack_blocks:
            st = getattr(blk, 'attack_state', None)
            if st == 'strike':
                blk.attack_state = 'sprinkle'
                blk.is_strike = False
            elif st == 'sprinkle':
                blk.attack_state = 'cgarbage'
                blk.is_garbage = True
            elif st == 'cgarbage':
                blk.attack_state = None
                blk.is_garbage = False
                blk.is_strike = False
                blk.color = random.choice(Piece.COLORS)
            if getattr(blk, 'attack_state', None):
                remaining.append(blk)
        self._inbound_attack_blocks = remaining

# End ai.py
