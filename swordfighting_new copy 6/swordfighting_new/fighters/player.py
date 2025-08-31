"""player.py - Player-controlled fighter logic (decoupled from pygame UI).

Handles:
 - Piece movement & rotation via passed-in intents
 - Gravity / piece locking / breaker chain progression
 - Combo processing after chains
 - Outbound attack generation via AttackManager
 - Inbound attack accumulation, delay, spawning (bulk or gradual)
 - Inbound attack block lifecycle advancement (strike->sprinkle->cgarbage->normal)

Intents contract (dict keys used by update()):
    {
      'move': -1|0|1,          # horizontal move this frame
      'rotate_cw': bool,
      'rotate_ccw': bool,
      'fast': bool             # fast-fall (soft drop)
    }

Outbound attack exchange is performed externally by a session orchestrator:
  - Call collect_ready_attacks() each frame AFTER update() to get attacks to
    deliver to opponent.
  - Feed opponent attacks into receive_attacks(list[Attack], base_delay_frames)
"""
from __future__ import annotations
from typing import List, Iterable
import random

from swordfighting_new.core.board import Board
from swordfighting_new.pieces.piece import Piece
from swordfighting_new.mechanics.movement import PieceMover
from swordfighting_new.mechanics.gravity import GravityManager
from swordfighting_new.mechanics.combo import ComboManager
from swordfighting_new.mechanics.breaker import BreakerManager
from swordfighting_new.mechanics.chain_runner import BreakerChainRunner
from swordfighting_new.mechanics.timing import TimingConfig
from swordfighting_new.attacks import AttackManager, Attack, AttackKind
from swordfighting_new.util.debug import log
import os
from swordfighting_new.attacks.attack_lifecycle import InboundAttackLifecycle

class DelayedCluster:
    """Helper class to track delayed cluster spawning."""
    def __init__(self, width: int, height: int, delay_frames: int):
        self.width = width
        self.height = height
        self.delay_frames = delay_frames
        self.y_offset = 0  # Additional Y offset to prevent stacking

class PlayerFighter:
    def __init__(self, timing: TimingConfig, spawn_x: int = 6,
                 attack_delay_frames: int = 24,
                 bulk_delivery: bool = True,
                 garbage_spawn_interval: int = 3,
                 enable_puzzle_speeds: bool = False,
                 puzzle_normal_us: int = 640000,
                 puzzle_fast_us: int = 2400,
                 lifecycle_debug: bool = False,
                 debug_attack_lifecycle: bool = False):
        self.board = Board()
        self.mover = PieceMover(self.board)
        self.gravity = GravityManager(self.board, self.mover, timing)
        self.combo = ComboManager(self.board)
        # Breaker / chain resolution (simplified cascade system)
        self.breakers = BreakerManager(self.board)
        # Allow environment override for cascade pacing.
        # Modes: step (per-row animation), fast (full compress per pass)
        env_mode = os.getenv('BF_CASCADE_MODE', '').strip().lower()
        # Default to 'step' mode to show individual cascade steps instead of instant resolution
        cascade_mode = env_mode if env_mode in ('step','fast') else 'step'
        self.chain_runner = BreakerChainRunner(
            self.board,
            self.breakers,
            frame_delay=max(15, timing.chain_frame_delay),  # Increased from 8 to 15 for better visual feedback
            cascade_mode=cascade_mode
        )
        self.attacks = AttackManager()
        self.spawn_x = spawn_x
        self.timing = timing
        self.attack_delay_frames = attack_delay_frames
        self.bulk_delivery = bulk_delivery
        self.garbage_spawn_interval = garbage_spawn_interval
        self.current_piece = Piece.spawn_random(self.spawn_x)
        self.next_piece = Piece.spawn_random(self.spawn_x)  # Preview piece
        self.fast = False
        self.frame = 0
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
        self.lifecycle = InboundAttackLifecycle(debug=lifecycle_debug)
        self.debug_attack_lifecycle = debug_attack_lifecycle
        # Apply optional puzzle speeds
        if enable_puzzle_speeds:
            timing.use_puzzle_speeds = True
            timing.puzzle_normal_us = puzzle_normal_us
            timing.puzzle_fast_us = puzzle_fast_us
        self.defeated = False

    # ------------------------------------------------------------------
    def update(self, intents: dict):
        if self.defeated:
            return
        # Chain resolution first
        if self.chain_runner.active:
            self.chain_runner.update()
            if self.chain_runner.finished:
                res = self.chain_runner.get_legacy_results()
                if res:
                    chains, total, per_pass = res
                    log('PLAYER', f'chain_finished passes={chains} total_cleared={total} per_pass={per_pass}')
                    history = self.chain_runner.get_pass_stats()
                    self.attacks.generate_from_chain(history, self.board.WIDTH, self.board.HEIGHT)
                    for atk in self.attacks.generated_last_chain:
                        atk.delay = self.attack_delay_frames
                    if self.attacks.generated_last_chain:
                        summary = [f"{a.kind.value}:{a.amount}d{a.delay}" for a in self.attacks.generated_last_chain]
                        log('ATTACK', 'generated ' + ', '.join(summary))
                self._spawn_new_piece_post_chain()
            # still allow inbound garbage fallers to update
            self._update_inbound_garbage()
            return
        self.frame += 1

        # Check if piece should lock BEFORE processing input to prevent visual jerking
        p = self.current_piece
        should_apply_gravity = False
        should_lock = False

        if p.controllable:
            interval = self.timing.interval_for_level(level=1, fast=bool(intents.get('fast')))
            should_apply_gravity = (self.frame % max(1, interval) == 0)
            if should_apply_gravity:
                # Pre-check if piece can fall to prevent input processing on pieces about to lock
                can_fall = self.gravity.can_fall(p)
                if not can_fall:
                    # Mark piece as non-controllable immediately to prevent visual jerking
                    p.controllable = False
                    should_lock = True
        elif not p.controllable:
            # Autonomous piece - will be handled in gravity application
            pass

        # Handle intents (movement / rotation) only if piece is still controllable
        if p.controllable:
            move = intents.get('move', 0)
            if move != 0:
                self.mover.move(p, move, 0)
            if intents.get('rotate_cw'):
                self.mover.rotate(p, clockwise=True)
            if intents.get('rotate_ccw'):
                self.mover.rotate(p, clockwise=False)

        self.fast = bool(intents.get('fast'))

        # Apply gravity or lock piece
        if should_lock:
            self._lock_and_start_chain()
        elif should_apply_gravity:
            # Apply gravity normally (piece can fall)
            if not self.gravity.apply_gravity(self.current_piece):
                self._lock_and_start_chain()
        elif not p.controllable:
            # Autonomous piece - apply gravity every frame, let the piece handle its own timing
            if not self.gravity.apply_gravity(self.current_piece):
                self._lock_and_start_chain()

        # Tick inbound timers & spawn
        self._process_inbound()
        self._update_inbound_garbage()
        # Process delayed clusters
        self._process_delayed_clusters()

    # ------------------------------------------------------------------
    def collect_ready_attacks(self) -> List[Attack]:
        self.attacks.tick_all()
        return self.attacks.consume_ready()

    # ------------------------------------------------------------------
    def receive_attacks(self, attacks: Iterable[Attack]):
        # Aggregate into pending sprinkle / strike counts with delay reset when new attacks arrive
        new_any = False
        for atk in attacks:
            if atk.kind == AttackKind.SPRINKLE:
                self.pending_in_sprinkle += atk.amount
                new_any = True
            elif atk.kind == AttackKind.STRIKE:
                meta = atk.meta or {}
                if meta.get('sword_shape'):
                    w, h = meta['sword_shape']
                    self._pending_in_strike_clusters.append(('sword', (w, h)))
                    self.pending_in_strike += w * h
                elif meta.get('horizontal_sword_shape'):
                    rows, length = meta['horizontal_sword_shape']
                    # treat as cluster for now
                    self._pending_in_strike_clusters.append(('hsword', (rows, length)))
                    self.pending_in_strike += rows * length
                elif meta.get('rect'):
                    # Rectangle-based strike - use original rectangle dimensions
                    w, h = meta['rect']
                    self._pending_in_strike_clusters.append(('cluster', (w, h)))
                    self.pending_in_strike += w * h
                else:
                    self.pending_in_strike += atk.amount
                new_any = True
        if new_any and self.inbound_delay < self.attack_delay_frames:
            self.inbound_delay = self.attack_delay_frames

    # ------------------------------------------------------------------
    def _lock_and_start_chain(self):
        # Advance lifecycle for previously tracked inbound attack blocks
        self.lifecycle.advance()
        # Lock current piece
        self.gravity.lock_piece(self.current_piece)
        # Promote newly locked inbound attack blocks (from previously falling garbage this frame)
        if self._new_attack_blocks:
            self.lifecycle.register_new_locked(self._new_attack_blocks)
            self._new_attack_blocks = []
        self.fast = False
        self.chain_runner.start()

    def _spawn_new_piece_post_chain(self):
        combo_count, total = self.combo.process_clears()
        if combo_count:
            print(f"Combo {combo_count} cleared {total}")
        # Use the next piece as current, generate new next piece
        self.current_piece = self.next_piece
        self.current_piece.x = self.spawn_x  # Reset position
        self.current_piece.y = -1
        self.next_piece = Piece.spawn_random(self.spawn_x)  # Generate new preview piece
        for x, y, _ in self.current_piece.get_block_positions():
            if y >= 0 and self.board.get_piece(x, y) != self.board.EMPTY:
                self.defeated = True
                break
        # Late ready outbound already handled by collect_ready_attacks() in session

    # ------------------------------------------------------------------ inbound processing
    def _process_inbound(self):
        inbound_total = self.pending_in_sprinkle + self.pending_in_strike
        if inbound_total:
            if self.inbound_delay > 0:
                self.inbound_delay -= 1
            if self.inbound_delay == 0:
                if self.bulk_delivery:
                    if self.pending_in_sprinkle:
                        self._spawn_bulk(self.pending_in_sprinkle, is_strike=False)
                    if self.pending_in_strike:
                        # Process strike clusters individually to avoid stacking
                        total_cluster_blocks = 0
                        for kind, dims in self._pending_in_strike_clusters:
                            if kind == 'hsword':
                                rows, length = dims
                                total_cluster_blocks += rows * length
                            else:
                                w, h = dims
                                total_cluster_blocks += w * h

                        self._spawn_multiple_strike_clusters()
                        leftover = self.pending_in_strike - total_cluster_blocks
                        if leftover > 0:
                            self._spawn_bulk(leftover, is_strike=True)
                        self._pending_in_strike_clusters.clear()
                else:
                    self.spawn_queue += self.pending_in_sprinkle
                self.pending_in_sprinkle = 0
                self.pending_in_strike = 0
        # Gradual spawning
        if (not self.bulk_delivery) and self.spawn_queue > 0:
            if self.garbage_spawn_cooldown > 0:
                self.garbage_spawn_cooldown -= 1
            if self.garbage_spawn_cooldown == 0:
                self._spawn_single(is_strike=False)
                self.spawn_queue -= 1
                self.garbage_spawn_cooldown = self.garbage_spawn_interval

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

        # Process delayed horizontal sword blocks
        self._process_delayed_horizontal_swords()

    def _process_delayed_horizontal_swords(self):
        """Process horizontal sword blocks that are waiting for delivery delay to expire."""
        # Scan board for horizontal sword blocks with delayed gravity
        for y in range(self.board.HEIGHT):
            for x in range(self.board.WIDTH):
                block = self.board.get_piece(x, y)
                if (block != self.board.EMPTY and
                    hasattr(block, 'horizontal_sword_delayed') and
                    block.horizontal_sword_delayed):

                    # Countdown the delivery delay
                    current_delay = getattr(block, 'delivery_delay_frames', 0)
                    current_delay -= 1
                    setattr(block, 'delivery_delay_frames', current_delay)

                    # If delay expired, convert to falling piece
                    if current_delay <= 0:
                        print(f"[DEBUG] Horizontal sword block at ({x},{y}) delay expired, converting to falling piece")

                        # Remove block from board
                        self.board.set_piece(x, y, self.board.EMPTY)

                        # Create a falling piece
                        from swordfighting_new.pieces.piece import Piece
                        falling_piece = Piece.single_block(
                            color=block.color,
                            is_breaker=getattr(block, 'is_breaker', False),
                            is_garbage=getattr(block, 'is_garbage', False),
                            is_strike=getattr(block, 'is_strike', False),
                            attack_state=getattr(block, 'attack_state', None)
                        )
                        falling_piece.x = x
                        falling_piece.y = y
                        falling_piece.controllable = False
                        falling_piece.autonomous_fall_timer = 0
                        falling_piece.autonomous_fall_interval = self.timing.autonomous_fall_interval_frames

                        # Add to garbage fallers so it falls with gravity
                        self.garbage_fallers.append(falling_piece)

    def _get_safe_column(self, base_index: int) -> int:
        """Get a column that avoids column 6 (spawn column) for strike/garbage placement."""
        # Generate candidate column, avoiding column 6
        candidate = ((base_index) * 3 + self.frame) % self.board.WIDTH
        # Skip column 6 (0-indexed spawn column)
        if candidate == 6:
            candidate = (candidate + 1) % self.board.WIDTH
        return candidate

    def _get_safe_cluster_position(self, width: int) -> int:
        """Get a safe left position for a cluster that avoids column 6 (spawn column) and doesn't overlap with existing strikes."""
        if width >= self.board.WIDTH:
            return 0

        # Track cluster count to spread out multiple strikes from same payload
        cluster_count = len([g for g in self.garbage_fallers if hasattr(g, 'blocks') and
                           any(getattr(b, 'is_strike', False) for b in g.blocks)])

        # Try multiple positions to find one that doesn't overlap and fits properly
        for attempt in range(self.board.WIDTH):
            # Generate position based on frame, cluster count, and attempt to avoid stacking
            base_pos = (self.frame * 3 + cluster_count * width + attempt * 2) % (self.board.WIDTH - width + 1)

            # Ensure cluster fits within board bounds
            if base_pos + width > self.board.WIDTH:
                base_pos = self.board.WIDTH - width

            # Check if this position would place any blocks in column 6 (spawn column)
            cluster_spans_spawn = any(base_pos + dx == 6 for dx in range(width))
            if cluster_spans_spawn:
                continue  # Try next position

            # Check for overlaps with existing garbage fallers at the same Y level
            overlaps = False
            for g in self.garbage_fallers:
                if hasattr(g, 'blocks') and any(getattr(b, 'is_strike', False) for b in g.blocks):
                    # Check if this existing strike would overlap with our proposed cluster
                    if g.y == -1:  # Same spawn level
                        for dx in range(width):
                            if g.x == base_pos + dx:
                                overlaps = True
                                break
                if overlaps:
                    break

            if not overlaps:
                return base_pos

        # Fallback: find any position that avoids spawn column and fits
        for pos in range(self.board.WIDTH - width + 1):
            if not any(pos + dx == 6 for dx in range(width)):
                return pos

        # Last resort: position 0 if cluster doesn't span column 6
        return 0 if width <= 6 else 7

    def _spawn_multiple_strike_clusters(self):
        """Spawn multiple strike clusters with spacing to prevent stacking."""
        clusters = list(self._pending_in_strike_clusters)

        # Sort clusters by size to ensure larger ones get priority placement
        clusters.sort(key=lambda x: (
            x[1][0] * x[1][1] if x[0] != 'hsword' else x[1][0] * x[1][1]
        ), reverse=True)

        for i, (kind, dims) in enumerate(clusters):
            if kind == 'hsword':
                # Horizontal sword: (rows, length) - enters from side
                rows, length = dims
                print(f"[DEBUG] About to spawn horizontal sword: kind={kind}, dims={dims}, rows={rows}, length={length}")
                self._spawn_horizontal_sword(rows, length)
            else:
                # Regular vertical sword/cluster: (width, height) - enters from top
                w, h = dims
                # Space out multiple clusters both in time and vertically to prevent stacking
                if i > 0:
                    # Stagger spawn timing and Y position for subsequent clusters
                    delayed_cluster = DelayedCluster(w, h, delay_frames=i * 8)  # Increased delay
                    delayed_cluster.y_offset = i * 2  # Spawn at different Y levels
                    self._delayed_clusters.append(delayed_cluster)
                else:
                    # Spawn first cluster immediately
                    self._spawn_strike_cluster(w, h)

    def _spawn_single(self, is_strike: bool):
        base_index = len(self.garbage_fallers) + self.spawn_queue + self.pending_in_sprinkle + self.pending_in_strike
        col = self._get_safe_column(base_index)
        attack_state = 'strike' if is_strike else 'sprinkle'
        g = Piece.single_block(color='white' if is_strike else 'red', is_garbage=False, is_strike=is_strike, attack_state=attack_state)
        g.x = col
        g.y = -1
        g.controllable = False
        self.garbage_fallers.append(g)
        if self.debug_attack_lifecycle:
            print(f"[DEBUG] Spawn {'STRIKE' if is_strike else 'SPRINKLE'} single id={id(g.blocks[0])} col={col} state={attack_state}")

    def _spawn_bulk(self, amount: int, is_strike: bool):
        if amount <= 0:
            return
        w = self.board.WIDTH
        per_col = amount // w
        remainder = amount % w
        start_offset = (self.frame // 5) % w
        for i in range(w):
            col = (start_offset + i) % w
            # Skip column 6 (spawn column) for strike/garbage placement
            if col == 6:
                continue
            stack_height = per_col + (1 if i < remainder else 0)
            for s in range(stack_height):
                attack_state = 'strike' if is_strike else 'sprinkle'
                g = Piece.single_block(color='white' if is_strike else 'red', is_garbage=False, is_strike=is_strike, attack_state=attack_state)
                g.x = col
                g.y = -1 - s
                g.controllable = False
                self.garbage_fallers.append(g)
                if self.debug_attack_lifecycle:
                    print(f"[DEBUG] Spawn BULK {'STRIKE' if is_strike else 'SPRINKLE'} id={id(g.blocks[0])} col={col} y={g.y} state={attack_state}")

    def _spawn_strike_cluster(self, width: int, height: int, color: str = 'white', y_offset: int = 0):
        if width <= 0 or height <= 0:
            return
        # Calculate safe position that avoids column 6 and doesn't stack with other strikes
        left = self._get_safe_cluster_position(width)

        # Spawn vertical sword blocks starting high enough that they won't disappear partially
        # The top block should start well above the board to give time for the entire sword to be visible
        start_y = -max(height, 5) - y_offset  # Start at least 5 rows above, or sword height, whichever is more

        for dx in range(width):
            for dy in range(height):
                p = Piece.single_block(color=color, is_strike=True, attack_state='strike')
                p.x = left + dx
                p.y = start_y + dy  # Staggered positions for the sword blocks
                p.controllable = False
                self.garbage_fallers.append(p)

    def _spawn_horizontal_sword(self, rows: int, length: int, color: str = 'white'):
        """Spawn a horizontal sword that enters from the side of the board.

        Args:
            rows: Height of the sword (how many rows it spans)
            length: How far it penetrates into the board
            color: Color of the sword blocks
        """
        if rows <= 0 or length <= 0:
            return

        # Determine entry side based on sword handedness pattern
        # For now, alternate: even sword count = right side, odd = left side
        sword_count = self.frame // 10  # Simple way to alternate sides over time
        from_right = (sword_count % 2) == 0

        # Calculate vertical position based on board state
        # According to docs: enter 2 rows below highest block (if no gems)
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

        # Limit length to board width (up to 12 columns max penetration)
        actual_length = min(length, self.board.WIDTH)

        # Create a single horizontal sword piece that will slide in
        p = Piece.single_block(color=color, is_strike=True, attack_state='strike')
        p.controllable = False
        p.horizontal_sword = True
        p.sword_rows = rows
        p.sword_length = actual_length
        p.sword_from_right = from_right
        p.sword_target_row = top_row

        # Start outside the board
        if from_right:
            p.x = self.board.WIDTH  # Start one column to the right of board
        else:
            p.x = -1  # Start one column to the left of board

        p.y = top_row  # At the target row
        p.entry_delay = 0  # No delay, start moving immediately

        print(f"[DEBUG] Spawning horizontal sword: rows={rows}, length={actual_length}, from_right={from_right}, start_x={p.x}, y={p.y}")
        self.garbage_fallers.append(p)

    def _update_inbound_garbage(self):
        if not self.garbage_fallers:
            return
        still = []
        do_fall = (self.frame % max(1, self.timing.garbage_fall_interval_frames) == 0)
        for g in self.garbage_fallers:
            # Handle horizontal sword entry delay
            if hasattr(g, 'entry_delay') and g.entry_delay > 0:
                g.entry_delay -= 1
                still.append(g)
                continue

            # Handle horizontal swords movement
            if hasattr(g, 'horizontal_sword') and g.horizontal_sword:
                # Move horizontal sword at a controlled pace (not every frame)
                move_horizontal = (self.frame % max(1, self.timing.garbage_fall_interval_frames // 2) == 0)
                if move_horizontal:
                    old_x = g.x
                    if hasattr(g, 'sword_from_right') and g.sword_from_right:
                        # Moving from right to left
                        g.x -= 1
                        if g.x + g.sword_length < 0:  # Sword has completely exited the board
                            print(f"[DEBUG] Horizontal sword exited left side")
                            continue  # Remove from garbage_fallers
                    else:
                        # Moving from left to right
                        g.x += 1
                        if g.x >= self.board.WIDTH:  # Sword has exited the board
                            print(f"[DEBUG] Horizontal sword exited right side")
                            continue  # Remove from garbage_fallers

                    print(f"[DEBUG] Moving horizontal sword from x={old_x} to x={g.x}, from_right={getattr(g, 'sword_from_right', 'unknown')}")

                    # Check if sword should lock (hit something or reached final position)
                    sword_blocks = self._get_horizontal_sword_blocks(g)
                    should_lock = False
                    pierced_blocks = []  # Track blocks to be destroyed by piercing

                    # Count how many blocks have penetrated the board
                    blocks_in_board = 0
                    for block_x, block_y in sword_blocks:
                        if 0 <= block_x < self.board.WIDTH and 0 <= block_y < self.board.HEIGHT:
                            blocks_in_board += 1
                            existing = self.board.get_piece(block_x, block_y)
                            if existing != self.board.EMPTY:
                                # Check if this block should be pierced or should stop the sword
                                if self._should_pierce_block(block_x, block_y, existing):
                                    # Pierce through this block - mark it for destruction
                                    pierced_blocks.append((block_x, block_y))
                                    print(f"[DEBUG] Horizontal sword piercing through block at ({block_x},{block_y})")
                                else:
                                    # This block stops the sword
                                    should_lock = True
                                    print(f"[DEBUG] Horizontal sword blocked by rectangle/cluster at ({block_x},{block_y})")
                                    break

                    # Also lock if the sword has fully penetrated (all its length is in the board)
                    if not should_lock and blocks_in_board >= g.sword_length:
                        should_lock = True
                        print(f"[DEBUG] Horizontal sword fully penetrated (length={g.sword_length})")

                    # Lock when the sword has moved its own length into the board (complete penetration)
                    if not should_lock:
                        # Track how far the sword has penetrated by counting movement from its initial position
                        if not hasattr(g, 'initial_x'):
                            g.initial_x = g.x  # Record initial position
                            setattr(g, 'penetration_distance', 0)

                        # Calculate penetration distance
                        if g.sword_from_right:
                            # Moving left: penetration = initial_x - current_x
                            g.penetration_distance = g.initial_x - g.x
                        else:
                            # Moving right: penetration = current_x - initial_x
                            g.penetration_distance = g.x - g.initial_x

                        # Lock when penetration equals sword length
                        if g.penetration_distance >= g.sword_length:
                            should_lock = True
                            print(f"[DEBUG] Horizontal sword completed penetration (distance={g.penetration_distance}, length={g.sword_length})")

                    if should_lock:
                        # First, destroy any pierced blocks
                        for pierce_x, pierce_y in pierced_blocks:
                            print(f"[DEBUG] Destroying pierced block at ({pierce_x},{pierce_y})")
                            self.board.set_piece(pierce_x, pierce_y, self.board.EMPTY)

                        # Lock all sword blocks that are within the board
                        locked_blocks = []
                        for block_x, block_y in sword_blocks:
                            if 0 <= block_x < self.board.WIDTH and 0 <= block_y < self.board.HEIGHT:
                                if self.board.get_piece(block_x, block_y) == self.board.EMPTY:
                                    # Create individual blocks for the sword (each position gets its own block)
                                    from swordfighting_new.pieces.piece import Block
                                    template_block = g.blocks[0]  # Use the original block as template
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
                                        if self.debug_attack_lifecycle:
                                            print(f"[DEBUG] Lock horizontal sword block id={id(new_block)} at ({block_x},{block_y}) state={new_block.attack_state}")
                                    locked_blocks.append((block_x, block_y, new_block))

                        # Mark locked blocks for delayed gravity - they should remain static until attack delivery delay is complete
                        # This implements the behavior where horizontal swords don't fall until after enemy piece has landed
                        for block_x, block_y, block in locked_blocks:
                            # Add metadata to track that this block should fall after delivery delay
                            setattr(block, 'horizontal_sword_delayed', True)
                            setattr(block, 'delivery_delay_frames', getattr(self, 'attack_delay_frames', 24) * 4)  # D=4 lock delay
                            print(f"[DEBUG] Horizontal sword block at ({block_x},{block_y}) locked but will fall after delivery delay")

                        continue  # Remove the original sword from garbage_fallers
                    else:
                        # Sword continues moving - destroy any pierced blocks
                        for pierce_x, pierce_y in pierced_blocks:
                            print(f"[DEBUG] Destroying pierced block at ({pierce_x},{pierce_y}) while sword continues")
                            self.board.set_piece(pierce_x, pierce_y, self.board.EMPTY)

                still.append(g)
                continue

            # Regular falling garbage
            if do_fall:
                # Check if this is a strike piece that should pierce
                if self._is_strike_piece(g):
                    # Apply piercing gravity for strikes
                    if not self._apply_piercing_gravity(g):
                        # Strike hit the bottom or a blocking object, lock it
                        print(f"[DEBUG] Locking strike piece at position x={g.x}, y={g.y}")
                        print(f"[DEBUG] Strike piece block positions before locking: {list(g.get_block_positions())}")
                        self.gravity.lock_piece(g)
                        for x, y, block in g.get_block_positions():
                            if self.board.is_in_bounds(x, y):
                                print(f"[DEBUG] Locked strike block at ({x},{y}) within bounds")
                            else:
                                print(f"[DEBUG] WARNING: Strike block at ({x},{y}) is OUT OF BOUNDS!")
                            if getattr(block, 'attack_state', None):
                                self._new_attack_blocks.append(block)
                                if self.debug_attack_lifecycle:
                                    print(f"[DEBUG] Lock inbound strike block id={id(block)} at ({x},{y}) state={block.attack_state}")
                    else:
                        still.append(g)
                else:
                    # Regular gravity for non-strike pieces
                    if not self.gravity.apply_gravity(g):
                        self.gravity.lock_piece(g)
                        for x, y, block in g.get_block_positions():
                            if getattr(block, 'attack_state', None):
                                self._new_attack_blocks.append(block)
                                if self.debug_attack_lifecycle:
                                    print(f"[DEBUG] Lock inbound block id={id(block)} at ({x},{y}) state={block.attack_state}")
                    else:
                        still.append(g)
            else:
                still.append(g)
        self.garbage_fallers = still

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

    def _should_pierce_block(self, x, y, block):
        """
        Determine if a horizontal sword should pierce through a block or be stopped by it.

        Pierce through:
        - Individual blocks (sprinkle/garbage state)
        - Single blocks not part of a rectangle cluster

        Stop at:
        - Rectangle clusters (2x2+ same color formations)
        - Normal player pieces that are part of clusters
        """
        # Always pierce through attack blocks (sprinkle, cgarbage, etc.)
        attack_state = getattr(block, 'attack_state', None)
        if attack_state in ('sprinkle', 'cgarbage'):
            return True

        # Always pierce through garbage blocks
        if getattr(block, 'is_garbage', False):
            return True

        # For normal blocks, check if they're part of a rectangle cluster
        if hasattr(block, 'color'):
            cluster_size = self._get_cluster_size_at(x, y, block.color)
            # Pierce through single blocks or small clusters, stop at rectangles (4+ blocks)
            return cluster_size < 4

        # Default: stop at unknown block types
        return False

    def _get_cluster_size_at(self, x, y, color):
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

    def _is_strike_piece(self, piece):
        """Check if a piece is a strike piece that should pierce when falling."""
        if hasattr(piece, 'blocks'):
            for block in piece.blocks:
                if getattr(block, 'is_strike', False) or getattr(block, 'attack_state', None) == 'strike':
                    return True
        return False

    def _apply_piercing_gravity(self, piece):
        """Apply gravity with piercing behavior for strike pieces.

        Returns True if the piece moved or pierced through something,
        False if it should lock (hit bottom or non-pierceable obstacle).
        """
        # Handle autonomous piece timing
        if not piece.controllable:
            piece.autonomous_fall_timer += 1
            if piece.autonomous_fall_timer < piece.autonomous_fall_interval:
                return True  # Still falling, just not this frame
            piece.autonomous_fall_timer = 0  # Reset timer for next fall

        # First, check if any part of the piece would go out of bounds
        for x, y, block in piece.get_block_positions():
            if y + 1 >= self.board.HEIGHT:
                print(f"[DEBUG] Strike piece hit bottom boundary at y={y}, board height={self.board.HEIGHT}")
                print(f"[DEBUG] Strike piece position: x={piece.x}, y={piece.y}")
                print(f"[DEBUG] All block positions: {list(piece.get_block_positions())}")
                return False  # Hit bottom, should lock

        # Check if this is a vertical strike and if it has exceeded its piercing limit
        is_horizontal = hasattr(piece, 'horizontal_sword') and piece.horizontal_sword
        if not is_horizontal:
            # For vertical strikes, limit piercing to only a few rows
            if not hasattr(piece, 'pierce_start_y'):
                # Record the starting position for piercing distance calculation
                piece.pierce_start_y = piece.y
                piece.pierced_rows = 0

            # Vertical strikes should only pierce through 3 rows maximum
            max_pierce_rows = 3
            if piece.pierced_rows >= max_pierce_rows:
                print(f"[DEBUG] Vertical strike reached piercing limit ({max_pierce_rows} rows)")
                return False  # Stop piercing after limit

        # Check if piece can fall to the next row
        can_fall_normally = self.mover.can_move(piece, 0, 1)

        if can_fall_normally:
            # Normal fall - no obstacles
            piece.y += 1
            return True
        else:
            # Something is blocking us - check if we can pierce through
            pierced_any = False
            for x, y, block in piece.get_block_positions():
                next_y = y + 1
                # Double-check bounds (should never happen since we checked above)
                if next_y >= self.board.HEIGHT:
                    print(f"[DEBUG] Strike piece would move out of bounds at y={next_y}")
                    return False

                blocking_cell = self.board.get_piece(x, next_y)
                if blocking_cell != self.board.EMPTY:
                    # Check if we should pierce this block
                    if self._should_pierce_block(x, next_y, blocking_cell):
                        print(f"[DEBUG] Strike piece piercing through block at ({x},{next_y})")
                        self.board.set_piece(x, next_y, self.board.EMPTY)
                        pierced_any = True
                    else:
                        print(f"[DEBUG] Strike piece blocked by non-pierceable block at ({x},{next_y})")
                        return False  # Blocked by non-pierceable object

            if pierced_any:
                # We pierced through something, move down and track piercing
                piece.y += 1
                if not is_horizontal and hasattr(piece, 'pierced_rows'):
                    piece.pierced_rows += 1
                    print(f"[DEBUG] Vertical strike pierced row, total: {piece.pierced_rows}")
                return True
            else:
                # Nothing to pierce but couldn't move, should lock
                return False

    # Accessors ------------------------------------------------------
    def get_board(self):
        return self.board
    def get_piece(self):
        return self.current_piece
    def get_next_piece(self):
        return self.next_piece
    def get_garbage_fallers(self):
        return list(self.garbage_fallers)
