"""Horizontal sword attack system.

Handles horizontal sword creation, movement, collision detection, and locking.
Keeps all horizontal sword logic separate from the main player fighter.
"""
from __future__ import annotations
from typing import List, Tuple, Optional, TYPE_CHECKING
from dataclasses import dataclass

import os

from swordfighting_new.util.fx_bus import emit_sparks
from swordfighting_new.util.debug import dprint

if TYPE_CHECKING:
    from swordfighting_new.core.board import Board
    from swordfighting_new.pieces.piece import Piece, Block
    from swordfighting_new.mechanics.timing import TimingConfig

@dataclass
class HorizontalSwordState:
    """Tracks the state of a horizontal sword during its lifecycle."""
    rows: int
    length: int
    from_right: bool
    target_row: int
    initial_x: int
    penetration_distance: int = 0
    delivery_delay_frames: int = 0
    locked: bool = False
    pierce_budget_left: int = 0
    pierced_any_normal: bool = False

class HorizontalSwordManager:
    """Manages horizontal sword attacks from creation to completion."""
    
    def __init__(self, board: Board, timing: TimingConfig):
        self.board = board
        self.timing = timing
        self.active_swords: List[Tuple[Piece, HorizontalSwordState]] = []
        self._debug = os.getenv('BF_HSWORD_DEBUG', '0') == '1'

        # How long sword blocks remain "held" (immune to snap-settle gravity) before
        # automatically releasing. This prevents rare cases where held blocks appear
        # to float forever if the player never locks adjacent.
        try:
            self._hold_release_frames = max(0, int(os.getenv('BF_HSWORD_HOLD_FRAMES', '120')))
        except Exception:
            self._hold_release_frames = 120

    def _auto_release_expired_holds(self, frame: int) -> None:
        if self._hold_release_frames <= 0:
            return

        try:
            w = int(self.board.WIDTH)
            h = int(self.board.HEIGHT)
        except Exception:
            return

        released = 0
        for x in range(w):
            for y in range(h):
                cell = self.board.get_piece(x, y)
                if cell == self.board.EMPTY or cell is None:
                    continue
                if not bool(getattr(cell, 'hsword_hold', False)):
                    continue
                until = getattr(cell, 'hsword_hold_until_frame', None)
                try:
                    if until is not None and int(until) <= int(frame):
                        setattr(cell, 'hsword_hold', False)
                        released += 1
                except Exception:
                    continue
        if released and self._debug:
            dprint(self._debug, f"[HSWORD] Auto-released {released} expired held blocks")
        
    def spawn_horizontal_sword(self, rows: int, length: int, color: str = 'white', frame: int = 0) -> None:
        """Spawn a new horizontal sword that enters from the side of the board."""
        if rows <= 0 or length <= 0:
            return

        # Horizontal swords may be up to the board width; do not apply the old 3x3 cap.
        try:
            length = max(1, min(int(length), int(self.board.WIDTH)))
        except Exception:
            length = 1

        # Never allow horizontal swords to occupy the very top of the board.
        # Keep y=0 and y=1 free (when possible) to avoid immediate defeat and
        # "top row" spawn artifacts.
        try:
            max_rows = max(0, int(self.board.HEIGHT) - 2)
        except Exception:
            max_rows = 0
        if max_rows <= 0:
            return
        rows = min(int(rows), int(max_rows))
            
        # Determine entry side based on frame (alternating pattern)
        sword_count = frame // 10
        from_right = (sword_count % 2) == 0
        
        # Calculate vertical position (2 rows below highest block)
        target_row = self._calculate_entry_row(rows)
        
        # Create the sword piece
        from swordfighting_new.pieces.piece import Piece
        sword_piece = Piece.single_block(color=color, is_strike=True, attack_state='strike')
        sword_piece.controllable = False
        sword_piece.horizontal_sword = True
        sword_piece.sword_rows = rows
        sword_piece.sword_length = int(length)
        sword_piece.sword_from_right = from_right
        
        # Position outside the board
        if from_right:
            sword_piece.x = self.board.WIDTH  # Start to the right
            initial_x = self.board.WIDTH
        else:
            sword_piece.x = -1  # Start to the left
            initial_x = -1
            
        sword_piece.y = target_row
        
        # Create state tracker
        state = HorizontalSwordState(
            rows=rows,
            length=int(length),
            from_right=from_right,
            target_row=target_row,
            initial_x=initial_x,
            pierce_budget_left=self._strike_pierce_budget(rows),
            pierced_any_normal=False,
        )
        
        self.active_swords.append((sword_piece, state))
        dprint(self._debug, f"[HSWORD] Spawned {rows}x{state.length} sword, from_right={from_right}, y={target_row}")

    def spawn_and_lock_immediately(self, rows: int, length: int, color: str = 'white', frame: int = 0):
        """Spawn a horizontal sword and resolve its lock in the same tick (atomic).

        This avoids interleaving with sprinkles by placing the sword blocks on the
        board immediately instead of animating across frames.
        Returns (falling_pieces, newly_locked_pieces) just like update().
        """
        if rows <= 0 or length <= 0:
            return [], []

        # Horizontal swords may be up to the board width; do not apply the old 3x3 cap.
        try:
            length = max(1, min(int(length), int(self.board.WIDTH)))
        except Exception:
            length = 1

        # Never allow horizontal swords to occupy the very top of the board.
        try:
            max_rows = max(0, int(self.board.HEIGHT) - 2)
        except Exception:
            max_rows = 0
        if max_rows <= 0:
            return [], []
        rows = min(int(rows), int(max_rows))

        # Determine entry side and target row consistently with normal spawn
        sword_count = frame // 10
        from_right = (sword_count % 2) == 0
        target_row = self._calculate_entry_row(rows)

        # Construct a temporary sword piece positioned fully on-board
        from swordfighting_new.pieces.piece import Piece
        sword_piece = Piece.single_block(color=color, is_strike=True, attack_state='strike')
        sword_piece.controllable = False
        sword_piece.horizontal_sword = True
        sword_piece.sword_rows = rows
        sword_piece.sword_length = int(length)
        sword_piece.sword_from_right = from_right
        sword_piece.y = target_row

        # Place fully inside the board to force immediate lock
        if from_right:
            sword_piece.x = self.board.WIDTH - 1
            initial_x = self.board.WIDTH
        else:
            sword_piece.x = 0
            initial_x = -1

        state = HorizontalSwordState(
            rows=rows,
            length=int(length),
            from_right=from_right,
            target_row=target_row,
            initial_x=initial_x,
            penetration_distance=length,
            pierce_budget_left=self._strike_pierce_budget(rows),
            pierced_any_normal=False,
        )

        # Lock immediately
        falling_pieces, newly_locked = self._lock_sword(sword_piece, state, frame=frame)
        state.locked = True
        dprint(self._debug, f"[HSWORD] Immediately locked {rows}x{state.length} sword at y={target_row}")
        return falling_pieces, newly_locked
        
    def update(self, frame: int):
        """Update all active horizontal swords.

        Returns:
            (falling_pieces, newly_locked_pieces)
        """
        # Safety: release any held blocks whose hold window expired.
        self._auto_release_expired_holds(frame)

        # Process delayed blocks every frame
        delayed_pieces = self._process_delayed_blocks()
        if not self.active_swords:
            return delayed_pieces, []  # Return tuple: (falling_pieces, newly_locked_pieces)
            
        still_active = []
        falling_pieces = list(delayed_pieces)  # Start with delayed pieces
        newly_locked_pieces = []  # CHANGE: pieces instead of blocks
        move_interval = max(1, self.timing.garbage_fall_interval_frames // 2)
        should_move = (frame % move_interval == 0)
        
        # Precompute normal-block cluster cells once per update (small board).
        cluster_cells = self._compute_normal_cluster_cells()

        for sword_piece, state in self.active_swords:
            if state.locked:
                # Locked swords have already been placed onto the board. We no longer
                # keep them around (delayed-block system was removed).
                continue
                
            if should_move:
                # Attempt one movement step, applying piercing on the leading edge.
                old_x = int(sword_piece.x)
                x_next = old_x - 1 if state.from_right else old_x + 1

                # Exit check (sword missed the board entirely)
                if state.from_right and x_next < -state.length:
                    dprint(self._debug, "[HSWORD] Sword exited left side")
                    continue
                if (not state.from_right) and x_next >= self.board.WIDTH:
                    dprint(self._debug, "[HSWORD] Sword exited right side")
                    continue

                # Check / pierce blocks at the leading edge that would newly enter the board.
                lock_now = False
                stop_due_to_cluster = False
                spark_cells: List[Tuple[int, int]] = []
                lead_cells = self._leading_edge_cells(x_next, state)
                for lx, ly in lead_cells:
                    if not (0 <= lx < self.board.WIDTH and 0 <= ly < self.board.HEIGHT):
                        continue
                    existing = self.board.get_piece(lx, ly)
                    if existing == self.board.EMPTY or existing is None:
                        continue

                    # Always stop on other attack blocks / garbage.
                    if bool(getattr(existing, 'is_strike', False)) or bool(getattr(existing, 'is_garbage', False)) or getattr(existing, 'attack_state', None) == 'strike':
                        lock_now = True
                        break

                    # Breakers: destroy only if no normal blocks have been pierced yet.
                    if bool(getattr(existing, 'is_breaker', False)):
                        if not bool(getattr(state, 'pierced_any_normal', False)):
                            self.board.set_piece(lx, ly, self.board.EMPTY)
                            continue
                        lock_now = True
                        break

                    # Normal blocks.
                    if (lx, ly) in (cluster_cells or set()):
                        lock_now = True
                        stop_due_to_cluster = True
                        spark_cells.append((lx, ly))
                        break
                    if int(getattr(state, 'pierce_budget_left', 0) or 0) <= 0:
                        lock_now = True
                        break

                    # Pierce this normal block and continue the step.
                    self.board.set_piece(lx, ly, self.board.EMPTY)
                    state.pierce_budget_left = int(getattr(state, 'pierce_budget_left', 0) or 0) - 1
                    state.pierced_any_normal = True

                if lock_now:
                    # Spark when we stopped due to a cluster hit.
                    try:
                        if spark_cells:
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

                    # Design rule: if a horizontal sword hits a normal-block cluster,
                    # the attack should be nullified (no placement), but show sparks.
                    if stop_due_to_cluster:
                        state.locked = True
                        dprint(self._debug, f"[HSWORD] Fizzled on cluster at y={state.target_row}")
                        continue

                    locked_pieces, new_pieces = self._lock_sword(sword_piece, state, frame=frame)
                    falling_pieces.extend(locked_pieces)
                    newly_locked_pieces.extend(new_pieces)
                    state.locked = True
                    dprint(self._debug, f"[HSWORD] Locked sword (blocked) at penetration {state.penetration_distance}")
                    continue

                # Apply movement.
                sword_piece.x = x_next
                state.penetration_distance = self._calculate_penetration(sword_piece, state)
                dprint(self._debug, f"[HSWORD] Moved from {old_x} to {sword_piece.x}, penetration: {state.penetration_distance}/{state.length}")

                # Lock once the entire sword is on-board.
                if self._all_blocks_on_board(sword_piece, state):
                    locked_pieces, new_pieces = self._lock_sword(sword_piece, state, frame=frame)
                    falling_pieces.extend(locked_pieces)
                    newly_locked_pieces.extend(new_pieces)
                    state.locked = True
                    dprint(self._debug, f"[HSWORD] Locked sword (fully entered) at penetration {state.penetration_distance}")
                else:
                    still_active.append((sword_piece, state))
            else:
                still_active.append((sword_piece, state))
                
        self.active_swords = still_active
        return falling_pieces, newly_locked_pieces  # CHANGE VARIABLE NAME
        
    def get_active_sword_pieces(self) -> List[Piece]:
        """Get all active (unlocked) sword pieces for rendering."""
        return [piece for piece, state in self.active_swords if not state.locked]
        
    def _calculate_entry_row(self, rows: int) -> int:
        """Calculate the row where the sword should enter."""
        # Find highest block
        highest_block = 0
        for x in range(self.board.WIDTH):
            for y in range(self.board.HEIGHT):
                if self.board.get_piece(x, y) != self.board.EMPTY:
                    highest_block = max(highest_block, self.board.HEIGHT - y)
                    break
                    
        # Position 2 rows below highest block, or middle if board is empty
        if highest_block > 0:
            target_row = max(2, self.board.HEIGHT - highest_block - 2)
        else:
            target_row = self.board.HEIGHT // 2
            
        # Ensure sword fits within board bounds with safety margin
        max_allowed_top_row = self.board.HEIGHT - rows
        if target_row > max_allowed_top_row:
            target_row = max_allowed_top_row
            
        # Prevent positioning too close to bottom
        min_top_row = max(0, min(2, self.board.HEIGHT - rows - 2))
        if target_row < min_top_row:
            target_row = min_top_row
            
        # y=0 is the top row on this board implementation; never spawn at y=0 or y=1.
        try:
            min_spawn_row = 2 if int(self.board.HEIGHT) > 2 else (1 if int(self.board.HEIGHT) > 1 else 0)
        except Exception:
            min_spawn_row = 0
        return max(int(min_spawn_row), min(int(target_row), int(self.board.HEIGHT - rows)))
        
    def _calculate_penetration(self, sword_piece: Piece, state: HorizontalSwordState) -> int:
        """Calculate how far the sword has penetrated into the board."""
        # Calculate based on how far we've moved from initial position
        if state.from_right:
            # Moving left: penetration = how far left we've moved from initial position
            return max(0, state.initial_x - sword_piece.x)
        else:
            # Moving right: penetration = how far right we've moved from initial position  
            return max(0, sword_piece.x - state.initial_x)
            
    def _check_should_lock(self, sword_piece: Piece, state: HorizontalSwordState) -> bool:
        """Check if the sword should lock (hit obstacle or completed penetration)."""
        # Check for collision with existing blocks
        sword_blocks = self._get_sword_block_positions(sword_piece, state)
        for block_x, block_y in sword_blocks:
            if 0 <= block_x < self.board.WIDTH and 0 <= block_y < self.board.HEIGHT:
                existing = self.board.get_piece(block_x, block_y)
                if existing != self.board.EMPTY:
                    dprint(self._debug, f"[HSWORD] Hit obstacle at ({block_x},{block_y})")
                    return True
                    
        # FIXED: Check if the sword has fully entered the board (all its blocks are on-board)
        blocks_on_board = 0
        for block_x, block_y in sword_blocks:
            if 0 <= block_x < self.board.WIDTH and 0 <= block_y < self.board.HEIGHT:
                blocks_on_board += 1
                
        total_blocks = state.rows * state.length
        if blocks_on_board >= total_blocks:
            dprint(self._debug, f"[HSWORD] All blocks on board ({blocks_on_board}/{total_blocks})")
            return True
            
        return False

    def _strike_pierce_budget(self, sword_rows: int) -> int:
        """Return pierce power budget for the entering sword."""
        # Smaller swords pierce less.
        if sword_rows <= 4:
            return 2
        if sword_rows <= 8:
            return 3
        return 4

    def _compute_normal_cluster_cells(self) -> set[tuple[int, int]]:
        """Return all cells that are part of a 2x2-or-larger same-color normal-block cluster.

        Excludes breakers, garbage, and strike/attack blocks.
        """
        w = int(self.board.WIDTH)
        h = int(self.board.HEIGHT)

        def color_key(cell):
            if cell is None or cell == self.board.EMPTY:
                return None
            if getattr(cell, 'is_breaker', False) or getattr(cell, 'is_garbage', False):
                return None
            if getattr(cell, 'is_strike', False) or getattr(cell, 'attack_state', None) == 'strike':
                return None
            return getattr(cell, 'color', None)

        visited: set[tuple[int, int]] = set()
        cluster_cells: set[tuple[int, int]] = set()
        for x in range(w):
            for y in range(h):
                if (x, y) in visited:
                    continue
                cell = self.board.get_piece(x, y)
                ck = color_key(cell)
                if ck is None:
                    continue
                stack = [(x, y)]
                comp: set[tuple[int, int]] = set()
                while stack:
                    cx, cy = stack.pop()
                    if (cx, cy) in visited:
                        continue
                    visited.add((cx, cy))
                    if not (0 <= cx < w and 0 <= cy < h):
                        continue
                    ccell = self.board.get_piece(cx, cy)
                    if color_key(ccell) != ck:
                        continue
                    comp.add((cx, cy))
                    stack.append((cx - 1, cy))
                    stack.append((cx + 1, cy))
                    stack.append((cx, cy - 1))
                    stack.append((cx, cy + 1))
                if len(comp) < 4:
                    continue
                xs = [px for px, _ in comp]
                ys = [py for _, py in comp]
                width = max(xs) - min(xs) + 1
                height = max(ys) - min(ys) + 1
                if width >= 2 and height >= 2:
                    cluster_cells.update(comp)
        return cluster_cells

    def _leading_edge_cells(self, x_next: int, state: HorizontalSwordState) -> List[Tuple[int, int]]:
        """Cells at the leading edge that newly enter the board on this step."""
        lead_x = (x_next - (state.length - 1)) if state.from_right else (x_next + (state.length - 1))
        out: List[Tuple[int, int]] = []
        for row_offset in range(int(state.rows)):
            out.append((int(lead_x), int(state.target_row) + int(row_offset)))
        return out

    def _all_blocks_on_board(self, sword_piece: Piece, state: HorizontalSwordState) -> bool:
        sword_blocks = self._get_sword_block_positions(sword_piece, state)
        blocks_on_board = 0
        for block_x, block_y in sword_blocks:
            if 0 <= block_x < self.board.WIDTH and 0 <= block_y < self.board.HEIGHT:
                blocks_on_board += 1
        total_blocks = int(state.rows) * int(state.length)
        return blocks_on_board >= total_blocks
        
    def _get_sword_block_positions(self, sword_piece: Piece, state: HorizontalSwordState) -> List[Tuple[int, int]]:
        """Get all block positions for a horizontal sword."""
        positions = []
        for row_offset in range(state.rows):
            for col_offset in range(state.length):
                if state.from_right:
                    block_x = sword_piece.x - col_offset
                else:
                    block_x = sword_piece.x + col_offset
                block_y = sword_piece.y + row_offset
                positions.append((block_x, block_y))
        return positions
        
    def _lock_sword(self, sword_piece: Piece, state: HorizontalSwordState, frame: int | None = None) -> List[Piece]:
        """Lock the sword blocks to the board and return any delayed falling pieces."""
        if frame is None:
            frame = 0
        falling_pieces = []
        newly_locked_pieces = []  # CHANGE: pieces instead of blocks

        for row_offset in range(int(state.rows)):
            for col_offset in range(int(state.length)):
                if state.from_right:
                    block_x = int(sword_piece.x) - int(col_offset)
                else:
                    block_x = int(sword_piece.x) + int(col_offset)
                block_y = int(sword_piece.y) + int(row_offset)

                if not (0 <= block_x < self.board.WIDTH and 0 <= block_y < self.board.HEIGHT):
                    continue
                existing_block = self.board.get_piece(block_x, block_y)
                
                if existing_block == self.board.EMPTY:
                    # SIMPLIFIED: Just place the block normally - global gravity will handle falling
                    from swordfighting_new.pieces.piece import Block, Piece
                    template_block = sword_piece.blocks[0]
                    new_block = Block(
                        color=template_block.color,
                        is_breaker=template_block.is_breaker,
                        is_garbage=template_block.is_garbage,
                        is_strike=template_block.is_strike,
                        attack_state=template_block.attack_state
                    )

                    # Hold horizontal sword blocks in place until released by piece placement.
                    try:
                        setattr(new_block, 'x', int(block_x))
                        setattr(new_block, 'y', int(block_y))
                        setattr(new_block, 'inbound_kind', 'strike')
                        setattr(new_block, 'hsword_hold', True)
                        setattr(new_block, 'hsword_hold_until_frame', int(frame) + int(self._hold_release_frames))
                        setattr(new_block, 'hsword_rows', int(state.rows))
                        setattr(new_block, 'hsword_length', int(state.length))
                        setattr(new_block, 'hsword_from_right', bool(state.from_right))
                        # Offsets used for strike pattern mapping.
                        # col_offset: 0 is the entry-side edge (rightmost when from_right).
                        setattr(new_block, 'hsword_col_offset', int(col_offset))
                        # Map vertical thickness to pattern rows bottom-up.
                        setattr(new_block, 'hsword_y_offset', int((int(state.rows) - 1) - int(row_offset)))
                    except Exception:
                        pass
                    
                    # Simply place the block - no special delay flags needed
                    self.board.set_piece(block_x, block_y, new_block)
                    
                    # Create a Piece wrapper using the SAME block instance that's on the board
                    piece_wrapper = Piece([new_block])  # Use the actual block that was placed
                    piece_wrapper.x = block_x
                    piece_wrapper.y = block_y
                    piece_wrapper.controllable = False
                    newly_locked_pieces.append(piece_wrapper)

                    dprint(self._debug, f"[HSWORD] Locked block at ({block_x},{block_y}) - will fall via global gravity")
                    
                elif not getattr(existing_block, 'is_strike', False) and not getattr(existing_block, 'is_garbage', False):
                    # Replace non-critical blocks
                    dprint(self._debug, f"[HSWORD] Destroying block at ({block_x},{block_y})")
                    from swordfighting_new.pieces.piece import Block, Piece
                    template_block = sword_piece.blocks[0]
                    new_block = Block(
                        color=template_block.color,
                        is_breaker=template_block.is_breaker,
                        is_garbage=template_block.is_garbage,
                        is_strike=template_block.is_strike,
                        attack_state=template_block.attack_state
                    )

                    # Hold horizontal sword blocks in place until released by piece placement.
                    try:
                        setattr(new_block, 'x', int(block_x))
                        setattr(new_block, 'y', int(block_y))
                        setattr(new_block, 'inbound_kind', 'strike')
                        setattr(new_block, 'hsword_hold', True)
                        setattr(new_block, 'hsword_hold_until_frame', int(frame) + int(self._hold_release_frames))
                        setattr(new_block, 'hsword_rows', int(state.rows))
                        setattr(new_block, 'hsword_length', int(state.length))
                        setattr(new_block, 'hsword_from_right', bool(state.from_right))
                        setattr(new_block, 'hsword_col_offset', int(col_offset))
                        setattr(new_block, 'hsword_y_offset', int((int(state.rows) - 1) - int(row_offset)))
                    except Exception:
                        pass
                    
                    # Simply place the block - no special delay flags needed
                    self.board.set_piece(block_x, block_y, new_block)
                    
                    # Create a Piece wrapper using the SAME block instance that's on the board
                    piece_wrapper = Piece([new_block])  # Use the actual block that was placed
                    piece_wrapper.x = block_x
                    piece_wrapper.y = block_y
                    piece_wrapper.controllable = False
                    newly_locked_pieces.append(piece_wrapper)
                    
                else:
                    dprint(self._debug, f"[HSWORD] Blocked by critical block at ({block_x},{block_y})")
                    
        return falling_pieces, newly_locked_pieces  # RETURN PIECES

    def notify_piece_locked(self, locked_piece: Piece) -> None:
        """Release any held horizontal sword blocks when a piece is placed adjacent.

        Rule: once the player places a piece that can stack against the sword
        (touching it from above or side), the sword is released to gravity.
        """
        if locked_piece is None:
            return

        # Quick scan for adjacency between the locked piece and held hsword blocks.
        try:
            locked_cells = [(int(x), int(y)) for x, y, _ in locked_piece.get_block_positions()]
        except Exception:
            locked_cells = []
        if not locked_cells:
            return

        w = int(self.board.WIDTH)
        h = int(self.board.HEIGHT)
        touched = False
        for x, y in locked_cells:
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                nx, ny = x + dx, y + dy
                if not (0 <= nx < w and 0 <= ny < h):
                    continue
                cell = self.board.get_piece(nx, ny)
                if cell == self.board.EMPTY or cell is None:
                    continue
                if bool(getattr(cell, 'hsword_hold', False)):
                    touched = True
                    break
            if touched:
                break

        if not touched:
            return

        # Release all held hsword blocks so global gravity will make them fall.
        released = 0
        for x in range(w):
            for y in range(h):
                cell = self.board.get_piece(x, y)
                if cell == self.board.EMPTY or cell is None:
                    continue
                if bool(getattr(cell, 'hsword_hold', False)):
                    try:
                        setattr(cell, 'hsword_hold', False)
                    except Exception:
                        pass
                    released += 1
        if released:
            dprint(self._debug, f"[HSWORD] Released {released} held sword blocks")
        
    def trigger_immediate_fall(self) -> List[Piece]:
        """Legacy method - now simplified since global gravity handles everything.
        
        With global gravity implemented, horizontal sword blocks will naturally fall
        when floating, so we don't need complex triggering logic anymore.
        """
        # Global gravity will handle any floating blocks automatically
        # This method can now be much simpler or potentially removed entirely
        dprint(self._debug, "[HSWORD] Trigger called - global gravity will handle floating blocks")
        return []
    
    def _process_delayed_blocks(self) -> List[Piece]:
        """Legacy method - no longer needed with global gravity."""
        # Global gravity will handle any floating blocks automatically
        return []
