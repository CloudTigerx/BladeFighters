"""
Refactored TestMode - Streamlined implementation using extracted components
Replaces the monolithic TestMode with a clean, component-based architecture.
"""

import time
import pygame
import sys
import logging
import traceback
from typing import List, Optional

# Try to import the interface contract
try:
    from contracts.testmode_interface_contract import TestModeInterface, validate_testmode_interface
    interface_available = True
except ImportError:
    class TestModeInterface:
        pass
    
    def validate_testmode_interface(cls):
        return cls
    
    interface_available = False

# Import our refactored components
from .board_manager import BoardManager
from .ai_manager import AIManager
from .game_state_manager import GameStateManager
from .input_handler import InputHandler
from .attack_coordinator import AttackCoordinator
from .attack_delivery_committer import AttackDeliveryCommitter
from .render_coordinator import RenderCoordinator
from .board_runtime import BoardRuntime

# Set up logging
logger = logging.getLogger(__name__)

# QA Instrumentation - Attack Delivery Monitoring
DEBUG_ATTACK_DELIVERY = True  # Flag for easy on/off switch

class AttackDeliveryMonitor:
    """Lightweight monitor for payload-related grid writes during animation windows."""
    
    def __init__(self):
        self.pending_landings = {'player': [], 'enemy': []}
        self.grid_write_log = []
        self.frame_counters = {'player': 0, 'enemy': 0}
        
    def log_grid_write(self, board, x, y, block_type, callsite, now_ms):
        """Log any payload-related grid writes before the end of their animation window."""
        if not DEBUG_ATTACK_DELIVERY:
            return
            
        # Check if this write is to a pending landing position
        player_key = 'player' if board == 'player' else 'enemy'
        pending = self.pending_landings.get(player_key, [])
        
        for pending_col, pending_row, _, end_ms in pending:
            if pending_col == x and pending_row == y and now_ms < end_ms:
                logger.error(f"PRE-COMMIT GRID WRITE VIOLATION:")
                logger.error(f"  Board: {board}, Position: ({x}, {y}), Block: {block_type}")
                logger.error(f"  Callsite: {callsite}")
                logger.error(f"  Current time: {now_ms}, Landing end: {end_ms}")
                logger.error(f"  Time remaining: {end_ms - now_ms}ms")
                
                # Log stack trace for debugging
                stack = traceback.extract_stack()
                logger.error("Stack trace:")
                for frame in stack[-5:]:  # Last 5 frames
                    logger.error(f"    {frame.filename}:{frame.lineno} in {frame.name}")
                
                # Store for reporting
                self.grid_write_log.append({
                    'timestamp': now_ms,
                    'board': board,
                    'position': (x, y),
                    'block_type': block_type,
                    'callsite': callsite,
                    'pending_end_ms': end_ms,
                    'time_remaining': end_ms - now_ms
                })
                break
    
    def update_pending_landings(self, player_key, pending_list):
        """Update the monitor's pending landings tracking."""
        self.pending_landings[player_key] = pending_list.copy() if pending_list else []
    
    def get_frame_counters(self, player_key):
        """Get current frame counters for overlay display."""
        return self.frame_counters.get(player_key, 0)
    
    def update_frame_counters(self, player_key, visual_falling_count, pending_landings_count):
        """Update frame counters for overlay display."""
        self.frame_counters[player_key] = {
            'visual_falling': visual_falling_count,
            'pending_landings': pending_landings_count
        }
    
    def get_violations_report(self):
        """Get a summary of all violations detected."""
        if not self.grid_write_log:
            return "No pre-commit grid write violations detected."
        
        report = f"Found {len(self.grid_write_log)} pre-commit grid write violations:\n"
        for violation in self.grid_write_log:
            report += f"  {violation['board']} ({violation['position'][0]},{violation['position'][1]}) "
            report += f"{violation['block_type']} at {violation['timestamp']}ms "
            report += f"(landing ends at {violation['pending_end_ms']}ms)\n"
        return report

# Global monitor instance
attack_delivery_monitor = AttackDeliveryMonitor()

# Attack delivery guardrails and enforcements
def _guard_against_pending_landing_writes(grid, col, row, player_key, pending_landings):
    """Guard against writes to positions that have pending landings."""
    if not hasattr(pending_landings, 'get'):
        return True  # No pending landings, allow write
    
    pending = pending_landings.get(player_key, [])
    current_time = int(time.time() * 1000)
    
    for pending_col, pending_row, _, end_ms in pending:
        if pending_col == col and pending_row == row and current_time < end_ms:
            logger.error(f"BLOCKED: Attempted write to pending landing position ({col}, {row}) for {player_key}")
            logger.error(f"Pending landing ends at {end_ms}, current time {current_time}")
            return False
    
    return True

def _assert_no_grid_zero_writes_from_attack_delivery():
    """Dev assertion: raise if any write to grid[0][col] originates from attack delivery."""
    import traceback
    stack = traceback.extract_stack()
    
    # Check if any frame in the stack contains attack delivery code
    attack_delivery_keywords = ['attack', 'deliver', 'spawn', 'garbage', 'strike']
    for frame in stack:
        if any(keyword in frame.filename.lower() or keyword in frame.line.lower() 
               for keyword in attack_delivery_keywords):
            logger.error("VIOLATION: Write to grid[0][col] from attack delivery detected!")
            logger.error("Stack trace:")
            for frame in stack:
                logger.error(f"  {frame.filename}:{frame.lineno} in {frame.name}")
            raise AssertionError("Write to grid[0][col] from attack delivery is forbidden")

def _enforce_animated_spawn_mode_only(settings_system):
    """Enforce that only animated spawn mode is allowed in production."""
    if not settings_system:
        return True
    
    try:
        cfg = getattr(settings_system, 'config', settings_system)
        if cfg and hasattr(cfg, 'get'):
            spawn_mode = cfg.get('attacks.spawn_mode', 'animated')
            if str(spawn_mode).strip().lower() != 'animated':
                logger.warning(f"Non-animated spawn mode detected: {spawn_mode}, forcing to 'animated'")
                return False
    except Exception:
        pass
    
    return True

def _safe_grid_write(grid, row, col, value, context="unknown", board="unknown"):
    """Safe grid write with attack delivery guards and monitoring."""
    import traceback
    now_ms = int(time.time() * 1000)
    
    # QA Monitoring: Log the write
    callsite = f"{traceback.extract_stack()[-2].filename}:{traceback.extract_stack()[-2].lineno}"
    attack_delivery_monitor.log_grid_write(board, col, row, value, callsite, now_ms)
    
    # Guard against grid[0][col] writes from attack delivery
    # But allow landing commits to write to their intended landing positions
    if row == 0 and "attack_landing" not in context:
        import traceback
        stack = traceback.extract_stack()
        
        # Check if any frame in the stack contains attack delivery code
        attack_delivery_keywords = ['attack', 'deliver', 'spawn', 'garbage', 'strike']
        for frame in stack:
            if any(keyword in frame.filename.lower() or keyword in frame.line.lower() 
                   for keyword in attack_delivery_keywords):
                logger.error("VIOLATION: Write to grid[0][col] from attack delivery detected!")
                logger.error(f"Context: {context}")
                logger.error("Stack trace:")
                for frame in stack:
                    logger.error(f"  {frame.filename}:{frame.lineno} in {frame.name}")
                raise AssertionError("Write to grid[0][col] from attack delivery is forbidden")
    
    # Perform the write
    grid[row][col] = value

@validate_testmode_interface
class TestModeRefactored(TestModeInterface):
    """Streamlined TestMode using extracted components."""
    
    def __init__(self, screen, font, audio, asset_path: str, settings_system=None, clock=None):
        """Initialize the refactored test mode."""
        self.screen = screen
        self.font = font
        self.audio = audio
        self.asset_path = asset_path
        self.settings_system = settings_system
        
        # Unified time source (ms)
        from utils.clock import PygameClock
        self.clock = clock or PygameClock()
        
        # Get screen dimensions
        self.width = screen.get_width()
        self.height = screen.get_height()
        
        self._initialize_components()
        self._connect_components()
        
        # Enforce animated spawn mode only
        if not _enforce_animated_spawn_mode_only(self.settings_system):
            logger.warning("Non-animated spawn mode detected, enforcing animated mode")
        
        # Validate interface contract if available
        try:
            from contracts.testmode_interface_contract import validate_testmode_interface
            validate_testmode_interface(self)
        except ImportError:
            logger.warning("TestMode interface contract not found, running without validation")

        logger.info("TestModeRefactored initialized with component-based architecture")
        
    def _initialize_components(self):
        """Initialize all refactored components."""
        self.board_manager = BoardManager(
            self.screen, self.font, self.audio, self.asset_path, 
            self.settings_system, self.clock
        )
        
        # Easy enemy bot for testing - difficulty 1: slow actions (220ms), high mistake rate (50%), no heuristics
        self.ai_manager = AIManager(initial_difficulty=1)
        
        self.game_state_manager = GameStateManager()
        # Initialize per-board runtime locks for input/chain locking
        try:
            from .board_runtime import BoardRuntime
            self.game_state_manager.player_runtime = BoardRuntime(board_id=1)
            self.game_state_manager.enemy_runtime = BoardRuntime(board_id=2)
        except Exception:
            pass
        
        self.input_handler = InputHandler(self.ai_manager, self.game_state_manager)
        
        self.attack_coordinator = AttackCoordinator(
            clock=self.clock,
            settings_system=self.settings_system,
            item_system=self.game_state_manager.get_player_items()
        )
        
        self.render_coordinator = RenderCoordinator(self.screen, self.board_manager)
        
        # Delivery committer for post-landing transformations (strike→garbage→colored→normal)
        self.delivery_committer = AttackDeliveryCommitter(config=None)
        
        # Back-compat: expose commonly used attributes for tests/legacy
        try:
            from .board_runtime import BoardRuntime
            # Use the same runtime objects as game_state_manager
            self.player_runtime = self.game_state_manager.player_runtime
            self.enemy_runtime = self.game_state_manager.enemy_runtime
            if hasattr(self.attack_coordinator, 'get_attacks_service'):
                self.attacks_service = self.attack_coordinator.get_attacks_service()
            elif hasattr(self.attack_coordinator, 'attacks_service'):
                self.attacks_service = self.attack_coordinator.attacks_service
        except Exception:
            pass
        
    def _connect_components(self):
        """Connect all components together."""
        player_engine, enemy_engine = self.board_manager.get_engines()
        player_renderer, enemy_renderer = self.board_manager.get_renderers()
        
        self.board_manager.set_piece_landed_callbacks(
            lambda: self._on_piece_landed(1),
            lambda: self._on_piece_landed(2)
        )
        
        self.attack_coordinator.set_blocks_broken_handlers(player_engine, enemy_engine)
        
        self.attack_coordinator.set_test_mode_reference(self, player_engine, enemy_engine)
        
        self.attack_coordinator.player_engine = player_engine
        self.attack_coordinator.enemy_engine = enemy_engine
        self.attack_coordinator.player_renderer = player_renderer
        self.attack_coordinator.enemy_renderer = enemy_renderer
        
        # Store references for easy access
        self.player_engine = player_engine
        self.enemy_engine = enemy_engine
        self.player_renderer = player_renderer
        self.enemy_renderer = enemy_renderer
        
        # Expose board positioning for interface validation
        self.player_grid_position = self.board_manager.player_grid_position
        self.enemy_grid_position = self.board_manager.enemy_grid_position
        
        # Initialize pending attacks for attack spawning
        # Use attack flow manager's pending_attacks for consistency
        self.pending_attacks = self.attack_coordinator.attack_flow_manager.pending_attacks
        
        # Initialize garbage block transformation tracking
        self.garbage_block_brightness = {}  # (x, y, player) -> {'landings': int, 'color': str, 'is_strike': bool}
        
    def queue_attack_spawn(self, target_player_or_payload, attack_type: str = None, count: int = None, strike_details=None):
        """Queue an attack to spawn above the target player's board.
        Backward compatible signature, also accepts a DTO-like payload:
          queue_attack_spawn({ 'target': 'player'|'enemy', 'type': 'garbage'|'strike', 'count': n, 'pattern': ..., 'created_ms': ..., 'start_y': -1 })
        """
        # Normalize arguments
        if isinstance(target_player_or_payload, dict) and 'type' in target_player_or_payload:
            payload = target_player_or_payload
            target_player = payload.get('target') or ('player' if payload.get('target_board_id') == 1 else 'enemy')
            attack_type = payload.get('type') or payload.get('kind')
            count = int(payload.get('count', 0))
            strike_details = payload.get('strike_details') or payload.get('pattern')
            created_ms = int(payload.get('created_ms', self.clock.now_ms()))
            start_y = int(payload.get('start_y', -1))
        else:
            target_player = target_player_or_payload
            created_ms = self.clock.now_ms()
            start_y = -1

        attack_data = {
            'type': attack_type,
            'count': count,
            'expected_count': count,
            'strike_details': strike_details,
            'spawn_time': created_ms,
            'start_y': start_y,
            'blocks_remaining': count,
            # For sprinkle/horizontal side alternation we track the group side once per queued attack
            'handedness': self.attack_coordinator.attack_manager.get_next_handedness() if hasattr(self.attack_coordinator, 'attack_manager') else 'R',
            # For sprinkles (garbage), store sweep side (R/L)
            'sprinkle_side': self.attack_coordinator.attack_manager.get_next_handedness() if hasattr(self.attack_coordinator, 'attack_manager') else 'R'
        }

        # Use attack flow manager to queue the attack
        self.attack_coordinator.attack_flow_manager.queue_attack(target_player, attack_data)
        
        # Also add to pending attacks for backward compatibility
        if target_player in self.pending_attacks:
            self.pending_attacks[target_player].append(attack_data)
            print(f"Queued attack for {target_player}: {attack_data}")
        
        # Record in recent attack log for HUD
        try:
            if not hasattr(self, 'recent_attack_log'):
                self.recent_attack_log = []
            self.recent_attack_log.append({
                'target': target_player,
                'type': attack_type,
                'expected': int(count),
                'details': strike_details,
                'placed': 0,
                'time': created_ms,
                'closed': False
            })
        except Exception:
            pass
        
    def _on_piece_landed(self, player_id: int):
        """Handle piece landed events and trigger garbage transformation."""
        # Get the appropriate engine and renderer
        engine = self.player_engine if player_id == 1 else self.enemy_engine
        renderer = self.player_renderer if player_id == 1 else self.enemy_renderer
        grid = engine.puzzle_grid
        
        # Ensure all strike blocks are properly tracked
        self._ensure_strike_tracking(player_id, grid)
        
        # Track landings for garbage block transformation
        self._track_garbage_landings(player_id, grid)
        
        # Process garbage transformations
        self._process_garbage_transformations(player_id, grid)
        
    def _track_garbage_landings(self, player_id: int, grid):
        """Track landings for garbage block transformation."""
        for y in range(len(grid)):
            for x in range(len(grid[0])):
                cell = grid[y][x]
                if cell and ('garbage_block' in str(cell) or '_garbage' in str(cell) or '_strike' in str(cell) or cell == 'strike_block'):
                    pos_key = (x, y, player_id)
                    if pos_key not in self.garbage_block_brightness:
                        # Initialize tracking for new garbage/strike blocks
                        is_strike = '_strike' in cell
                        color = self._get_block_color(cell)
                        self.garbage_block_brightness[pos_key] = {
                            'landings': 0,
                            'color': color,
                            'is_strike': is_strike
                        }
                    # Increment landing count
                    self.garbage_block_brightness[pos_key]['landings'] += 1
                    
    def _get_block_color(self, block_type: str) -> str:
        """Extract color from block type."""
        if '_garbage' in block_type:
            # Extract color from colored garbage (e.g., "blue_garbage" -> "blue")
            parts = block_type.split('_garbage')
            return parts[0] if parts[0] else 'blue'
        elif '_strike' in block_type:
            # Extract color from strike blocks (e.g., "blue_strike" -> "blue")
            parts = block_type.split('_strike')
            return parts[0] if parts[0] else 'blue'
        else:
            # Default color for neutral garbage
            return 'blue'
            
    def _process_garbage_transformations(self, player_id: int, grid):
        """Process garbage block transformations based on landing count."""
        to_demote_strikes = []  # (pos_key, new_block_type)
        to_finalize_garbage = []
        to_colorize_garbage = []
        
        for pos_key, data in list(self.garbage_block_brightness.items()):
            x, y, block_player = pos_key
            if block_player != player_id:
                continue
                
            is_strike = data.get('is_strike', False)
            color = data['color']
            current_block = None
            
            # Guard against out-of-bounds or grid changes
            if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
                current_block = grid[y][x]
                
            # Stage 1: strike demotion after 1 landing
            if is_strike and data['landings'] >= 1:
                to_demote_strikes.append((pos_key, 'garbage_block'))
                
            # Stage 2: neutral garbage -> colored garbage after 1 landing
            if (not is_strike) and data['landings'] >= 1:
                if current_block == 'garbage_block':
                    to_colorize_garbage.append((pos_key, f"{color}_garbage"))
                    
            # Stage 3: colored garbage -> normal block after 2 landings
            if (not is_strike) and data['landings'] >= 2:
                if isinstance(current_block, str) and current_block.startswith(f"{color}_garbage"):
                    to_finalize_garbage.append((pos_key, f"{color}_block"))
        
        # Apply transformations
        self._apply_strike_demotions(to_demote_strikes, grid)
        self._apply_garbage_colorization(to_colorize_garbage, grid)
        self._apply_garbage_finalization(to_finalize_garbage, grid)
        
    def _apply_strike_demotions(self, to_demote_strikes, grid):
        """Apply strike to neutral garbage transformations."""
        for pos_key, new_block_type in to_demote_strikes:
            x, y, _ = pos_key
            if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
                grid[y][x] = new_block_type
                # Update tracking: now behaves like newly received garbage
                self.garbage_block_brightness[pos_key]['is_strike'] = False
                self.garbage_block_brightness[pos_key]['landings'] = 0
                
    def _apply_garbage_colorization(self, to_colorize_garbage, grid):
        """Apply neutral garbage to colored garbage transformations."""
        for pos_key, new_block_type in to_colorize_garbage:
            x, y, _ = pos_key
            if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
                if grid[y][x] == 'garbage_block':
                    grid[y][x] = new_block_type
                    
    def _apply_garbage_finalization(self, to_finalize_garbage, grid):
        """Apply colored garbage to normal block transformations."""
        for pos_key, new_block_type in to_finalize_garbage:
            x, y, player = pos_key
            engine = self.player_engine if player == 1 else self.enemy_engine
            engine_grid = engine.puzzle_grid
            
            # Transform the block
            if 0 <= y < len(engine_grid) and 0 <= x < len(engine_grid[0]):
                engine_grid[y][x] = new_block_type
                # Remove from tracking
                if pos_key in self.garbage_block_brightness:
                    del self.garbage_block_brightness[pos_key]
                            
    def _update_attack_block_positions(self, attack_movements):
        """Update attack block positions when they move due to sliding/falling."""
        for old_pos, new_pos in attack_movements.items():
            old_x, old_y = old_pos
            new_x, new_y = new_pos
            
            # Find and update tracking entries for this block
            for pos_key in list(self.garbage_block_brightness.keys()):
                x, y, player = pos_key
                if x == old_x and y == old_y:
                    # Remove old tracking entry
                    tracking_data = self.garbage_block_brightness.pop(pos_key)
                    # Add new tracking entry
                    new_pos_key = (new_x, new_y, player)
                    self.garbage_block_brightness[new_pos_key] = tracking_data
                    break
        
        # Update renderers
        self.player_renderer.update_visual_state()
        self.enemy_renderer.update_visual_state()
        
    def _ensure_strike_tracking(self, player_id: int, grid):
        """Ensure all strike blocks are properly tracked for transformation."""
        for y in range(len(grid)):
            for x in range(len(grid[0])):
                cell = grid[y][x]
                if cell == 'strike_block':
                    pos_key = (x, y, player_id)
                    if pos_key not in self.garbage_block_brightness:
                        # Initialize tracking for strike block
                        self.garbage_block_brightness[pos_key] = {
                            'landings': 0,
                            'color': 'blue',  # Default color
                            'is_strike': True
                        }
        
    def setup_board_positions(self):
        """Set up the positions for the player and enemy puzzle boards."""
        # This is handled by the BoardManager component
        # The positions are already set up during initialization
        pass
        
    def initialize_test(self):
        """Initialize or reset the test mode game state."""
        logger.info("COMPREHENSIVE GAME RESET INITIATED...")
        
        # Reset attack queues
        self.attack_coordinator.reset_attack_queues()
        
        # Reset game state
        self.game_state_manager.reset_chain_states()
        
        # Reset board states
        self.board_manager.reset_engine_states()
        self.board_manager.reset_renderer_states()
        
        # Start games
        self.board_manager.start_games()
        
        # Reset render state
        self.render_coordinator.reset_garbage_block_state()
        
        # Update renderers
        self.board_manager.update_renderers()
        
        logger.info("COMPREHENSIVE GAME RESET COMPLETED")
        
    def update(self) -> Optional[str]:
        """Update the test mode state."""
        current_time = self.clock.now_ms()
        
        # Reset runtime locks
        self.game_state_manager.reset_runtime_locks(current_time)
        
        # Handle chain locking
        self.input_handler.handle_chain_lock(self.player_engine, current_time)
        
        # Update engines
        self.board_manager.update_engines(
            current_time,
            getattr(self, 'player_spawn_pause_until', 0),
            getattr(self, 'enemy_spawn_pause_until', 0)
        )
        
        # Update AI
        self.ai_manager.update_ai(self.enemy_engine, current_time)
        
        # Deliver attacks
        res_player, res_enemy = self.attack_coordinator.deliver_attacks(
            self.player_engine, self.enemy_engine,
            self.player_renderer, self.enemy_renderer
        )
        
        # Handle attack locking
        self.input_handler.handle_attack_lock(res_player, current_time)
        
        # Update attack spawning
        self.attack_coordinator.update_attack_spawning()
        
        # Update attack spawning for visual feedback
        self._update_attack_spawning()
        
        # Safety: reconcile garbage tracking
        self.render_coordinator.reconcile_garbage_tracking_with_grid(
            self.player_engine, self.enemy_engine
        )
        
        # Print attack flow summary
        self.attack_coordinator.print_attack_summary()
        
        return None
        
    def _update_attack_spawning(self):
        """Update attack spawning for visual feedback and animation updates."""
        current_time = self.clock.now_ms()

        # Update renderer animations to clean up expired animations
        self.player_renderer.update_animations()
        self.enemy_renderer.update_animations()

        # QA Monitoring: Update frame counters for overlay display
        for player_key in ['player', 'enemy']:
            renderer = self.player_renderer if player_key == 'player' else self.enemy_renderer
            asm = getattr(renderer, 'animation_state_manager', None)
            visual_falling_count = len(getattr(asm, 'visual_falling_blocks', {})) if asm else 0
            pending_landings_count = len(getattr(self, 'pending_landings', {}).get(player_key, []))
            attack_delivery_monitor.update_frame_counters(player_key, visual_falling_count, pending_landings_count)

        # Process pending attacks for actual placement
        for player_key in ['player', 'enemy']:
            engine = self.player_engine if player_key == 'player' else self.enemy_engine

            # Debug: log pending attacks
            if self.pending_attacks[player_key]:
                logger.debug(f"Processing {len(self.pending_attacks[player_key])} pending attacks for {player_key}")

            # Process each pending attack for placement
            attacks_to_remove = []
            for attack in self.pending_attacks[player_key]:
                # Safety check: if attack is too old, remove it to prevent infinite loops
                if current_time - attack['spawn_time'] > 10000:  # 10 seconds
                    attacks_to_remove.append(attack)
                    continue

                # Place attacks on the board
                if attack['type'] == 'strike':
                    # Place strikes
                    blocks_placed = self._place_strike_attack(engine, attack, player_key)
                    if blocks_placed > 0:
                        attack['blocks_remaining'] = max(0, attack['blocks_remaining'] - blocks_placed)
                        if attack['blocks_remaining'] <= 0:
                            attacks_to_remove.append(attack)
                else:
                    # Place garbage
                    blocks_placed = self._place_garbage_attack(engine, attack, player_key)
                    if blocks_placed > 0:
                        attack['blocks_remaining'] = max(0, attack['blocks_remaining'] - blocks_placed)
                        if attack['blocks_remaining'] <= 0:
                            attacks_to_remove.append(attack)

            # Remove completed attacks
            for attack in attacks_to_remove:
                if attack in self.pending_attacks[player_key]:
                    self.pending_attacks[player_key].remove(attack)
                    try:
                        for entry in reversed(self.recent_attack_log):
                            if not entry.get('closed') and entry['target'] == player_key and entry['type'] == attack['type']:
                                entry['closed'] = True
                                break
                    except Exception:
                        pass

        # Commit landings after animations complete (no on-grid spawn before this)
        for player_key in ['player', 'enemy']:
            engine = self.player_engine if player_key == 'player' else self.enemy_engine
            pending = list(self.pending_landings.get(player_key, [])) if hasattr(self, 'pending_landings') else []
            if pending:
                print(f"Processing {len(pending)} pending landings for {player_key}")
            if not pending:
                continue

            # QA Monitoring: Update monitor's pending landings tracking
            attack_delivery_monitor.update_pending_landings(player_key, pending)

            new_pending = []
            for (col, row, block_type, end_ms) in pending:
                print(f"Landing check: current_time={current_time}, end_ms={end_ms}, diff={end_ms - current_time}")
                if current_time >= end_ms:
                    print(f"Committing landing: ({col}, {row}) = {block_type}")
                    # Guard against writes to pending landing positions
                    if not _guard_against_pending_landing_writes(engine.puzzle_grid, col, row, player_key, self.pending_landings):
                        logger.warning(f"Skipping commit to protected position ({col}, {row}) for {player_key}")
                        continue
                    
                    # Place only if still empty; otherwise the block is wasted
                    if engine.puzzle_grid[row][col] in (None, 'empty'):
                        _safe_grid_write(engine.puzzle_grid, row, col, block_type, f"attack_landing_{player_key}", board=player_key)
                        print(f"Placed {block_type} at ({col}, {row})")
                    else:
                        print(f"Position ({col}, {row}) not empty, skipping")
                else:
                    new_pending.append((col, row, block_type, end_ms))

            self.pending_landings[player_key] = new_pending

            # Clear spawn pause if nothing left pending
            if not new_pending:
                if player_key == 'player':
                    self.player_spawn_pause_until = max(getattr(self, 'player_spawn_pause_until', 0), current_time)
                else:
                    self.enemy_spawn_pause_until = max(getattr(self, 'enemy_spawn_pause_until', 0), current_time)

        # After any commits, update received blocks to advance transformations
        try:
            self.delivery_committer.update_received_blocks(self.player_engine, 'player')
            self.delivery_committer.update_received_blocks(self.enemy_engine, 'enemy')
        except Exception:
            pass
                        
    def _place_garbage_attack(self, engine, attack, player_key):
        """Place garbage blocks on the board by spawning them high above and letting them fall."""
        grid = engine.puzzle_grid
        blocks_to_place = attack.get('blocks_remaining', 0)
        blocks_placed = 0

        # Set sweep order by side
        side = attack.get('sprinkle_side', 'R')
        cols_order = list(range(engine.grid_width))
        if side == 'R':
            cols_order = list(reversed(cols_order))

        # Get renderer and animation state manager
        renderer = self.player_renderer if player_key == 'player' else self.enemy_renderer
        if not hasattr(renderer, 'animation_state_manager'):
            # Fallback to direct placement if no animation system available
            return self._place_garbage_attack_direct(engine, attack, player_key)

        asm = renderer.animation_state_manager
        # Use unified ms clock for logic timing; visuals still use seconds
        now_ms = int(self.clock.now_ms()) if hasattr(self, 'clock') and self.clock else int(time.time() * 1000)
        current_time = time.time()

        # Ensure landing queue exists
        if not hasattr(self, 'pending_landings'):
            self.pending_landings = {'player': [], 'enemy': []}

        # Calculate spawn height above the board (negative row positions)
        spawn_height = -3  # Spawn 3 rows above the visible board

        max_end_ms = 0

        while blocks_to_place > 0:
            for column in cols_order:
                if blocks_to_place <= 0:
                    break

                # Find next landing spot in this column
                landing_row = None
                for row in range(engine.grid_height - 1, -1, -1):
                    if grid[row][column] in ['empty', None]:
                        landing_row = row
                        break

                if landing_row is None:
                    # Column full, waste this block
                    blocks_to_place -= 1
                    continue

                # Calculate fall distance and duration
                fall_distance = landing_row - spawn_height
                fall_duration = asm.fall_animation_duration * fall_distance
                fall_duration_ms = int(asm.fall_animation_duration * 1000 * fall_distance)

                # Set up falling animation
                animation_key = (column, landing_row)
                asm.visual_falling_blocks[animation_key] = {
                    'start_time': current_time,
                    'duration': fall_duration,
                    'start_y': spawn_height,
                    'block_type': 'garbage_block',
                    'payload': True,
                    'phase': 'spawning',
                    'final_position': (column, landing_row)  # Track final position
                }

                # Queue landing commit instead of mutating grid immediately
                end_ms = now_ms + fall_duration_ms
                self.pending_landings[player_key].append((column, landing_row, 'garbage_block', end_ms))
                if end_ms > max_end_ms:
                    max_end_ms = end_ms

                # REMOVE this (was causing "on-grid" spawn):
                # grid[0][column] = 'garbage_block'

                # Track the garbage block for transformation
                player_id = 1 if player_key == 'player' else 2
                pos_key = (column, landing_row, player_id)
                self.garbage_block_brightness[pos_key] = {
                    'landings': 0,
                    'color': 'blue',  # Default color, will be determined by item system
                    'is_strike': False
                }

                blocks_placed += 1
                blocks_to_place -= 1

        # Freeze updates for this side until payload finishes landing
        if max_end_ms > 0:
            if player_key == 'player':
                self.player_spawn_pause_until = max(getattr(self, 'player_spawn_pause_until', 0), max_end_ms)
            else:
                self.enemy_spawn_pause_until = max(getattr(self, 'enemy_spawn_pause_until', 0), max_end_ms)

        # Also lock player input for the duration of the animation window
        try:
            if max_end_ms > 0 and player_key == 'player' and hasattr(self, 'game_state_manager'):
                freeze_ms = max(0, int(max_end_ms) - int(now_ms))
                if freeze_ms > 0:
                    self.game_state_manager.lock_player_input(freeze_ms, now_ms)
        except Exception:
            pass

        return blocks_placed
    
    def _place_garbage_attack_direct(self, engine, attack, player_key):
        """Fallback method for direct garbage block placement (original behavior)."""
        grid = engine.puzzle_grid
        blocks_to_place = attack.get('blocks_remaining', 0)
        blocks_placed = 0
        
        # Set sweep order by side
        side = attack.get('sprinkle_side', 'R')
        cols_order = list(range(engine.grid_width))
        if side == 'R':
            cols_order = list(reversed(cols_order))
        
        while blocks_to_place > 0:
            for column in cols_order:
                if blocks_to_place <= 0:
                    break
                    
                # Find next landing spot in this column
                landing_row = None
                for row in range(engine.grid_height - 1, -1, -1):
                    if grid[row][column] in ['empty', None]:
                        landing_row = row
                        break
                        
                if landing_row is None:
                    # Column full, waste this block
                    blocks_to_place -= 1
                    continue
                
                # Place garbage block
                grid[landing_row][column] = 'garbage_block'
                
                # Track the garbage block for transformation
                player_id = 1 if player_key == 'player' else 2
                pos_key = (column, landing_row, player_id)
                self.garbage_block_brightness[pos_key] = {
                    'landings': 0,
                    'color': 'blue',  # Default color, will be determined by item system
                    'is_strike': False
                }
                
                blocks_placed += 1
                blocks_to_place -= 1
        
        return blocks_placed
        
    def _place_strike_attack(self, engine, attack, player_key):
        """Place strike attacks on the board by spawning them high above and letting them fall."""
        grid = engine.puzzle_grid
        strike_details = attack.get('strike_details', [])
        blocks_placed = 0

        # Get renderer and animation state manager
        renderer = self.player_renderer if player_key == 'player' else self.enemy_renderer
        if not hasattr(renderer, 'animation_state_manager'):
            # Fallback to direct placement if no animation system available
            return self._place_strike_attack_direct(engine, attack, player_key)

        asm = renderer.animation_state_manager
        # Use unified ms clock for logic timing; visuals still use seconds
        now_ms = int(self.clock.now_ms()) if hasattr(self, 'clock') and self.clock else int(time.time() * 1000)
        current_time = time.time()

        # Ensure landing queue exists
        if not hasattr(self, 'pending_landings'):
            self.pending_landings = {'player': [], 'enemy': []}

        # Calculate spawn height above the board (negative row positions)
        spawn_height = -3  # Spawn 3 rows above the visible board

        max_end_ms = 0

        for strike in strike_details:
            # Handle both dictionary and string formats for backward compatibility
            if isinstance(strike, dict):
                width = strike.get('width', 2)
                height = strike.get('height', 4)
            elif isinstance(strike, str) and 'x' in strike:
                # Handle old string format like "2x4"
                try:
                    width, height = map(int, strike.split('x'))
                except (ValueError, AttributeError):
                    width, height = 2, 4
            else:
                # Fallback to default values
                width, height = 2, 4

            # Find placement position (start from top)
            placed = False
            for start_row in range(engine.grid_height - height + 1):
                for start_col in range(engine.grid_width - width + 1):
                    # Check if area is clear
                    can_place = True
                    for row in range(start_row, start_row + height):
                        for col in range(start_col, start_col + width):
                            if grid[row][col] not in ['empty', None]:
                                can_place = False
                                break
                        if not can_place:
                            break

                    if can_place:
                        # Calculate fall distance and duration for the strike pattern
                        fall_distance = start_row - spawn_height
                        fall_duration = asm.fall_animation_duration * fall_distance
                        fall_duration_ms = int(asm.fall_animation_duration * 1000 * fall_distance)
                        end_ms = now_ms + fall_duration_ms
                        if end_ms > max_end_ms:
                            max_end_ms = end_ms

                        # Set up falling animations for each block in the strike pattern
                        for row in range(start_row, start_row + height):
                            for col in range(start_col, start_col + width):
                                animation_key = (col, row)
                                asm.visual_falling_blocks[animation_key] = {
                                    'start_time': current_time,
                                    'duration': fall_duration,
                                    'start_y': spawn_height + (row - start_row),  # Stagger the spawn heights
                                    'block_type': 'orange_strike',
                                    'payload': True,
                                    'phase': 'spawning',
                                    'final_position': (col, row)  # Track final position
                                }

                                # Queue landing commit instead of mutating grid immediately
                                self.pending_landings[player_key].append((col, row, 'orange_strike', end_ms))

                                # REMOVE this (was causing "on-grid" spawn):
                                # grid[0][col] = 'strike_block'

                                # Track the strike block for transformation
                                player_id = 1 if player_key == 'player' else 2
                                pos_key = (col, row, player_id)
                                self.garbage_block_brightness[pos_key] = {
                                    'landings': 0,
                                    'color': 'blue',  # Default color, will be determined by item system
                                    'is_strike': True
                                }

                                blocks_placed += 1
                        placed = True
                        break
                if placed:
                    break

        # Freeze updates for this side until payload finishes landing
        if max_end_ms > 0:
            if player_key == 'player':
                self.player_spawn_pause_until = max(getattr(self, 'player_spawn_pause_until', 0), max_end_ms)
            else:
                self.enemy_spawn_pause_until = max(getattr(self, 'enemy_spawn_pause_until', 0), max_end_ms)

        # Also lock player input for the duration of the strike animation window
        try:
            if max_end_ms > 0 and player_key == 'player' and hasattr(self, 'game_state_manager'):
                freeze_ms = max(0, int(max_end_ms) - int(now_ms))
                if freeze_ms > 0:
                    self.game_state_manager.lock_player_input(freeze_ms, now_ms)
        except Exception:
            pass

        return blocks_placed
    
    def _place_strike_attack_direct(self, engine, attack, player_key):
        """Fallback method for direct strike block placement (original behavior)."""
        grid = engine.puzzle_grid
        strike_details = attack.get('strike_details', [])
        blocks_placed = 0
        
        for strike in strike_details:
            # Handle both dictionary and string formats for backward compatibility
            if isinstance(strike, dict):
                width = strike.get('width', 2)
                height = strike.get('height', 4)
            elif isinstance(strike, str) and 'x' in strike:
                # Handle old string format like "2x4"
                try:
                    width, height = map(int, strike.split('x'))
                except (ValueError, AttributeError):
                    width, height = 2, 4
            else:
                # Fallback to default values
                width, height = 2, 4
            
            # Find placement position (start from top)
            placed = False
            for start_row in range(engine.grid_height - height + 1):
                for start_col in range(engine.grid_width - width + 1):
                    # Check if area is clear
                    can_place = True
                    for row in range(start_row, start_row + height):
                        for col in range(start_col, start_col + width):
                            if grid[row][col] not in ['empty', None]:
                                can_place = False
                                break
                        if not can_place:
                            break
                    
                    if can_place:
                        # Place strike blocks
                        for row in range(start_row, start_row + height):
                            for col in range(start_col, start_col + width):
                                grid[row][col] = 'orange_strike'
                                
                                # Track the strike block for transformation
                                player_id = 1 if player_key == 'player' else 2
                                pos_key = (col, row, player_id)
                                self.garbage_block_brightness[pos_key] = {
                                    'landings': 0,
                                    'color': 'blue',  # Default color, will be determined by item system
                                    'is_strike': True
                                }
                                
                                blocks_placed += 1
                        placed = True
                        break
                if placed:
                    break
        
        return blocks_placed
        
    def _finalize_attack_block_placement(self, engine, player_key):
        """Finalize the placement of attack blocks after their animations complete."""
        # This method will be called after animations complete to ensure blocks are in their final positions
        # For now, gravity will handle moving blocks from the top row to their final positions
        pass
        
    def process_events(self, events: List) -> Optional[str]:
        """Process input events for the test mode."""
        current_time = self.clock.now_ms()
        return self.input_handler.process_events(events, self.player_engine, current_time)
        
    def draw(self):
        """Draw the test mode screen."""
        # Draw boards
        self.render_coordinator.draw_boards()
        
        # Draw attack indicators
        self.render_coordinator.draw_attack_indicators()
        
        # Draw characters
        self.render_coordinator.draw_characters()
        
        # QA Monitoring: Draw frame counter overlay
        if DEBUG_ATTACK_DELIVERY:
            self._draw_frame_counter_overlay()
        
    def _draw_frame_counter_overlay(self):
        """Draw frame counter overlay showing visual_falling_blocks and pending_landings counts."""
        if not hasattr(self, 'font') or not self.font:
            return
            
        # Get current frame counters
        player_counters = attack_delivery_monitor.get_frame_counters('player')
        enemy_counters = attack_delivery_monitor.get_frame_counters('enemy')
        
        # Draw player board counters
        if isinstance(player_counters, dict):
            player_text = f"P: VF={player_counters.get('visual_falling', 0)} PL={player_counters.get('pending_landings', 0)}"
            player_surface = self.font.render(player_text, True, (255, 255, 255))
            self.screen.blit(player_surface, (10, 10))
        
        # Draw enemy board counters
        if isinstance(enemy_counters, dict):
            enemy_text = f"E: VF={enemy_counters.get('visual_falling', 0)} PL={enemy_counters.get('pending_landings', 0)}"
            enemy_surface = self.font.render(enemy_text, True, (255, 255, 255))
            self.screen.blit(enemy_surface, (10, 40))
        
        # Draw violations count if any
        violations = len(attack_delivery_monitor.grid_write_log)
        if violations > 0:
            violation_text = f"VIOLATIONS: {violations}"
            violation_surface = self.font.render(violation_text, True, (255, 0, 0))
            self.screen.blit(violation_surface, (10, 70))
        
    def get_ai_difficulty(self) -> int:
        """Get the current AI difficulty."""
        return self.ai_manager.get_difficulty()
        
    def set_ai_difficulty(self, difficulty: int):
        """Set the AI difficulty."""
        self.ai_manager.set_difficulty(difficulty)
        
    def get_flags(self):
        """Get feature flags."""
        return self.game_state_manager.get_flags()
        
    def get_player_items(self):
        """Get player item system."""
        return self.game_state_manager.get_player_items()
        
    def get_enemy_items(self):
        """Get enemy item system."""
        return self.game_state_manager.get_enemy_items() 

# Back-compat alias for legacy imports expecting `TestMode` in this module
TestMode = TestModeRefactored