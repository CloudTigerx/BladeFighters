"""
Refactored TestMode - Streamlined implementation using extracted components
Replaces the monolithic TestMode with a clean, component-based architecture.
"""

import time
import pygame
import sys
import logging
import traceback
import json
import os
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
from modules.game_state_module.game_state_manager import GameStateManager
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
        try:
            self.board_manager = BoardManager(
                self.screen, self.font, self.audio, self.asset_path, 
                self.settings_system, self.clock
            )
            
            # Easy enemy bot for testing - difficulty 1: slow actions (220ms), high mistake rate (50%), no heuristics
            self.ai_manager = AIManager(initial_difficulty=1)
            
            self.game_state_manager = GameStateManager()
            
            # CRITICAL: Set as global instance for transformation system
            from modules.game_state_module.game_state_manager import set_global_game_state_manager
            set_global_game_state_manager(self.game_state_manager)
            
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
            
            # CRITICAL FIX: Expose player_items and enemy_items for backward compatibility
            # This allows the inventory interface to access them directly
            self.player_items = self.game_state_manager.get_player_items()
            self.enemy_items = self.game_state_manager.get_enemy_items()
            
        except Exception as e:
            # CRITICAL FIX: Catch any initialization errors, especially color-related ones
            logger.error(f"Error during TestMode component initialization: {e}")
            import traceback
            traceback.print_exc()
            
            # Try to provide a minimal working state
            if hasattr(self, 'game_state_manager'):
                self.player_items = self.game_state_manager.get_player_items()
                self.enemy_items = self.game_state_manager.get_enemy_items()
            else:
                # Create minimal fallback
                from modules.items_module.item_system import ItemSystem
                self.player_items = ItemSystem()
                self.enemy_items = ItemSystem()
        
    def _connect_components(self):
        """Connect all components together."""
        player_engine, enemy_engine = self.board_manager.get_engines()
        player_renderer, enemy_renderer = self.board_manager.get_renderers()
        
        self.board_manager.set_piece_landed_callbacks(
            None,  # No additional callback needed - BoardManager handles transformations
            None
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
        # Garbage block tracking removed - ready for new replacement system
        
        # CRITICAL FIX: Set test_mode attribute on engines so attack delivery can access tracking
        self.player_engine.test_mode = self
        self.enemy_engine.test_mode = self
        
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
        
    # Piece landing is now handled by BoardManager transformation system
        
    # _track_garbage_landings method removed - ready for new replacement system
    
    # _get_landing_piece_positions method removed - ready for new replacement system
    
    # All transformation methods removed - ready for new replacement system
                            
    # _update_attack_block_positions and _ensure_strike_tracking methods removed - ready for new replacement system
        
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
        
        # Garbage block tracking removed - ready for new replacement system
        
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
            if not pending:
                continue

            new_pending = []
            for (col, row, block_type, end_ms) in pending:
                # Defer until animation end
                if current_time < end_ms:
                    new_pending.append((col, row, block_type, end_ms))
                    continue

                # Recompute final landing row at commit time to avoid post-commit gravity fall
                final_row = None
                for r in range(engine.grid_height - 1, -1, -1):
                    cell = engine.puzzle_grid[r][col]
                    if cell in (None, 'empty'):
                        final_row = r
                        break

                if final_row is None:
                    # Column is full; drop this pending landing
                    logger.debug(f"Column {col} full, dropping {block_type} landing for {player_key}")
                    continue

                # Write block at true final landing row (no on-grid-then-fall effect)
                if engine.puzzle_grid[final_row][col] in (None, 'empty'):
                    engine.puzzle_grid[final_row][col] = block_type
                    logger.debug(f"Bulletproof landing: {block_type} at ({col}, {final_row}) for {player_key}")
                else:
                    logger.debug(f"Position ({col}, {final_row}) occupied, dropping {block_type} for {player_key}")

            self.pending_landings[player_key] = new_pending

            # Clear spawn pause if nothing left pending for this side
            if not new_pending:
                if player_key == 'player':
                    self.player_spawn_pause_until = max(getattr(self, 'player_spawn_pause_until', 0), current_time)
                else:
                    self.enemy_spawn_pause_until = max(getattr(self, 'enemy_spawn_pause_until', 0), current_time)

        # DISABLED: Duplicate transformation system - using TestMode's _on_piece_landed() instead
        # The delivery_committer.update_received_blocks() was causing race conditions
        # with the main transformation logic in _on_piece_landed()
        pass

        # Fallback: commit from visual animations if pending entries were lost
        try:
            now_ms = int(self.clock.now_ms()) if hasattr(self, 'clock') and self.clock else int(time.time() * 1000)
            now_s = float(now_ms) / 1000.0
            for player_key in ['player', 'enemy']:
                engine = self.player_engine if player_key == 'player' else self.enemy_engine
                asm = (self.player_renderer.animation_state_manager if player_key == 'player'
                       else self.enemy_renderer.animation_state_manager)
                to_remove = []
                for key, data in list(asm.visual_falling_blocks.items()):
                    if not data.get('payload'):
                        continue
                    start_time = float(data.get('start_time', 0.0))
                    duration = float(data.get('duration', 0.0))
                    if now_s - start_time < duration:
                        continue
                    # Determine target cell
                    tgt = data.get('final_position')
                    if isinstance(tgt, (tuple, list)) and len(tgt) == 2:
                        tgt_col, tgt_row = int(tgt[0]), int(tgt[1])
                    else:
                        # Fallback to key if needed
                        tgt_col, tgt_row = int(key[0]), int(key[1])

                    # Recompute final landing row
                    final_row = None
                    for r in range(engine.grid_height - 1, -1, -1):
                        if engine.puzzle_grid[r][tgt_col] in (None, 'empty'):
                            final_row = r
                            break
                    if final_row is not None and engine.puzzle_grid[final_row][tgt_col] in (None, 'empty'):
                        engine.puzzle_grid[final_row][tgt_col] = data.get('block_type', 'garbage_block')
                        logger.debug(f"Fallback landing: {data.get('block_type', 'garbage_block')} at ({tgt_col}, {final_row}) for {player_key}")
                        to_remove.append(key)
                    else:
                        logger.debug(f"Fallback landing failed: no space in column {tgt_col} for {player_key}")
                for key in to_remove:
                    asm.visual_falling_blocks.pop(key, None)
        except Exception:
            pass
                        
    def _place_garbage_attack(self, engine, attack, player_key):
        """Place garbage blocks on the board by spawning them high above and letting them fall."""
        grid = engine.puzzle_grid
        blocks_to_place = attack.get('blocks_remaining', 0)
        blocks_placed = 0

        # FIXED: Use proper column rotation pattern instead of simple sweep
        # Column rotation sequence per spec (1-indexed): 1,6,2,5,3,4
        # Convert to 0-based: 0,5,1,4,2,3
        column_rotation = [0, 5, 1, 4, 2, 3]  # 0-based columns
        
        # FIXED: Use persistent rotation state across multiple calls
        if not hasattr(self, '_garbage_rotation_index'):
            self._garbage_rotation_index = 0
        
        current_rotation_index = self._garbage_rotation_index

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
        reserved = set()  # prevent choosing the same (col,row) multiple times this pass

        while blocks_to_place > 0:
            # Use column rotation pattern for even distribution
            column = column_rotation[current_rotation_index]
            current_rotation_index = (current_rotation_index + 1) % len(column_rotation)

            # Find next landing spot in this column
            landing_row = None
            for row in range(engine.grid_height - 1, -1, -1):
                if grid[row][column] in ['empty', None] and (column, row) not in reserved:
                    landing_row = row
                    break

            if landing_row is None:
                # Column full, try next column in rotation
                continue

            # Calculate fall distance and duration
            fall_distance = landing_row - spawn_height
            fall_duration = asm.fall_animation_duration * fall_distance
            fall_duration_ms = int(asm.fall_animation_duration * 1000 * fall_distance)

            # Visual falling
            animation_key = (column, landing_row)
            asm.visual_falling_blocks[animation_key] = {
                'start_time': current_time,
                'duration': fall_duration,
                'start_y': spawn_height,
                'block_type': 'garbage_block',
                'payload': True,
                'phase': 'spawning',
                'final_position': (column, landing_row)
            }

            # Queue landing
            end_ms = now_ms + fall_duration_ms
            self.pending_landings[player_key].append((column, landing_row, 'garbage_block', end_ms))
            logger.debug(f"Queued landing: ({column}, {landing_row}) = garbage_block, end_ms={end_ms} for {player_key}")
            reserved.add((column, landing_row))
            if end_ms > max_end_ms:
                max_end_ms = end_ms

            # Transformation system removed - ready for new replacement system

            blocks_placed += 1
            blocks_to_place -= 1

        # Freeze updates for this side until payload finishes landing
        if max_end_ms > 0:
            if player_key == 'player':
                self.player_spawn_pause_until = max(getattr(self, 'player_spawn_pause_until', 0), max_end_ms)
            else:
                self.enemy_spawn_pause_until = max(getattr(self, 'enemy_spawn_pause_until', 0), max_end_ms)

        # FIXED: Save the rotation state for next call
        self._garbage_rotation_index = current_rotation_index
        
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
        
        # FIXED: Use proper column rotation pattern instead of simple sweep
        # Column rotation sequence per spec (1-indexed): 1,6,2,5,3,4
        # Convert to 0-based: 0,5,1,4,2,3
        column_rotation = [0, 5, 1, 4, 2, 3]  # 0-based columns
        
        # FIXED: Use persistent rotation state across multiple calls
        if not hasattr(self, '_garbage_rotation_index'):
            self._garbage_rotation_index = 0
        
        current_rotation_index = self._garbage_rotation_index
        
        while blocks_to_place > 0:
            # Use column rotation pattern for even distribution
            column = column_rotation[current_rotation_index]
            current_rotation_index = (current_rotation_index + 1) % len(column_rotation)
            
            # Find next landing spot in this column
            landing_row = None
            for row in range(engine.grid_height - 1, -1, -1):
                if grid[row][column] in ['empty', None]:
                    landing_row = row
                    break
                    
            if landing_row is None:
                # Column full, try next column in rotation
                continue
            
            # Place garbage block
            grid[landing_row][column] = 'garbage_block'
            
            # Transformation system removed - ready for new replacement system
            
            blocks_placed += 1
            blocks_to_place -= 1
        
        # FIXED: Save the rotation state for next call
        self._garbage_rotation_index = current_rotation_index
        
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
        reserved = set()  # prevent duplicate cells within a single strike placement pass

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
                        fall_distance = start_row - spawn_height
                        fall_duration = asm.fall_animation_duration * fall_distance
                        fall_duration_ms = int(asm.fall_animation_duration * 1000 * fall_distance)
                        end_ms = now_ms + fall_duration_ms
                        if end_ms > max_end_ms:
                            max_end_ms = end_ms

                        for row in range(start_row, start_row + height):
                            for col in range(start_col, start_col + width):
                                if (col, row) in reserved:
                                    continue
                                animation_key = (col, row)
                                asm.visual_falling_blocks[animation_key] = {
                                    'start_time': current_time,
                                    'duration': fall_duration,
                                    'start_y': spawn_height + (row - start_row),
                                    'block_type': 'orange_strike',
                                    'payload': True,
                                    'phase': 'spawning',
                                    'final_position': (col, row)
                                }
                                self.pending_landings[player_key].append((col, row, 'orange_strike', end_ms))
                                reserved.add((col, row))

                                # Transformation system removed - ready for new replacement system

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
                                
                                # Transformation system removed - ready for new replacement system
                                
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
        
    def save_equipment(self):
        """Save equipment configuration for backward compatibility."""
        try:
            # Save to items_config.json
            config = {
                'player_weapon': self.player_items.get_equipped_weapon().name if self.player_items.get_equipped_weapon() else 'Rusted Sword',
                'enemy_weapon': self.enemy_items.get_equipped_weapon().name if self.enemy_items.get_equipped_weapon() else 'Rusted Sword',
                'player_weapons': self.player_items.get_owned_weapons(),
                'enemy_weapons': self.enemy_items.get_owned_weapons()
            }
            
            config_path = "puzzleassets/items_config.json"
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
                
            logger.info("Equipment configuration saved successfully")
        except Exception as e:
            logger.warning(f"Failed to save equipment configuration: {str(e)}")
        
    def get_attack_delivery_violations_report(self):
        """Get a summary of all attack delivery violations detected."""
        return attack_delivery_monitor.get_violations_report()
        
    def clear_attack_delivery_violations(self):
        """Clear the attack delivery violations log."""
        attack_delivery_monitor.grid_write_log.clear()
    
    # TRANSFORMATION SYSTEM METHODS
    def _process_garbage_transformations(self, player_id: int, grid):
        """Process garbage block transformations for the specified player."""
        # Get the engine for this player
        engine = self.player_engine if player_id == 1 else self.enemy_engine
        
        # Initialize tracking if not present
        if not hasattr(self, 'garbage_block_brightness'):
            self.garbage_block_brightness = {}
        
        # Reconcile any attack block movements under gravity to keep tracking keys in sync
        moved = getattr(engine, 'attack_block_movements', None)
        if moved:
            updated_brightness = {}
            for pos_key, data in list(self.garbage_block_brightness.items()):
                x, y, block_player = pos_key
                if block_player != player_id:
                    # Not this player's block; keep as-is
                    updated_brightness[pos_key] = data
                    continue
                # If this tracked block moved, update its key to the new position
                new_pos = moved.get((x, y))
                if new_pos is not None:
                    nx, ny = new_pos
                    new_key = (nx, ny, block_player)
                    updated_brightness[new_key] = data
                else:
                    updated_brightness[pos_key] = data
            self.garbage_block_brightness = updated_brightness
        
        # Find all strike/garbage blocks for this player and increment their landing counters
        blocks_to_increment = []
        for pos_key, data in self.garbage_block_brightness.items():
            x, y, block_player = pos_key
            if block_player == player_id:
                # Check if this tracked block is still in the grid
                if (0 <= y < len(grid) and 0 <= x < len(grid[0]) and 
                    grid[y][x] and (('_garbage' in grid[y][x]) or 
                                   (grid[y][x] == 'garbage_block') or 
                                   ('_strike' in grid[y][x]))):
                    blocks_to_increment.append(pos_key)
        
        # Increment landing counters (only when actual piece landed, not mid-animation)
        for pos_key in blocks_to_increment:
            self.garbage_block_brightness[pos_key]['landings'] += 1
        
        # Apply transformations
        self._apply_garbage_finalization(player_id, grid)
    
    def _apply_garbage_finalization(self, player_id: int, grid):
        """Apply garbage block transformations."""
        # Transformation rules:
        # For received garbage (not strike):
        # 1) Neutral Garbage → Colored Garbage after 1 landing
        # 2) Colored Garbage → Normal after 2 landings
        # For strikes: one extra step at the start → becomes Neutral first, then follow the above
        
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

        # Apply strike → neutral garbage
        if to_demote_strikes:
            for pos_key, new_block_type in to_demote_strikes:
                x, y, _ = pos_key
                if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
                    grid[y][x] = new_block_type
                    # Update tracking: now behaves like newly received garbage
                    self.garbage_block_brightness[pos_key]['is_strike'] = False
                    self.garbage_block_brightness[pos_key]['landings'] = 0

        # Apply neutral garbage → colored garbage
        if to_colorize_garbage:
            for pos_key, new_block_type in to_colorize_garbage:
                x, y, _ = pos_key
                if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
                    if grid[y][x] == 'garbage_block':
                        grid[y][x] = new_block_type
                        # Clear any lingering falling overlay
                        try:
                            if hasattr(self.player_renderer, 'animation_state_manager'):
                                self.player_renderer.animation_state_manager.visual_falling_blocks.pop((x, y), None)
                            if hasattr(self.enemy_renderer, 'animation_state_manager'):
                                self.enemy_renderer.animation_state_manager.visual_falling_blocks.pop((x, y), None)
                        except Exception:
                            pass

        # Apply colored garbage → normal block
        if to_finalize_garbage:
            for pos_key, new_block_type in to_finalize_garbage:
                x, y, _ = pos_key
                if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
                    if isinstance(grid[y][x], str) and grid[y][x].startswith(f"{data['color']}_garbage"):
                        grid[y][x] = new_block_type
                        # Remove from tracking since it's now a normal block
                        self.garbage_block_brightness.pop(pos_key, None)
    
    def _track_garbage_landings(self, player_id: int, grid):
        """Track landings for garbage block transformation."""
        # Initialize tracking if not present
        if not hasattr(self, 'garbage_block_brightness'):
            self.garbage_block_brightness = {}
        
        # First, ensure all garbage/strike blocks are tracked
        for y in range(len(grid)):
            for x in range(len(grid[0])):
                cell = grid[y][x]
                if cell and ('_garbage' in str(cell) or '_strike' in str(cell) or cell == 'strike_block'):
                    pos_key = (x, y, player_id)
                    if pos_key not in self.garbage_block_brightness:
                        # Initialize tracking for new garbage/strike blocks
                        is_strike = '_strike' in cell or cell == 'strike_block'
                        color = self._get_block_color(cell)
                        self.garbage_block_brightness[pos_key] = {
                            'landings': 0,
                            'color': color,
                            'is_strike': is_strike
                        }
        
        # Apply affect radius logic (Manhattan distance of 3)
        affect_radius = 3
        for pos_key, data in list(self.garbage_block_brightness.items()):
            x, y, block_player = pos_key
            if block_player != player_id:
                continue
            
            # Calculate Manhattan distance to landing position
            # For now, assume landing at current piece position
            landing_x, landing_y = 0, 0  # Default landing position
            if hasattr(self, 'player_engine') and hasattr(self.player_engine, 'piece_position'):
                landing_x, landing_y = self.player_engine.piece_position
            
            distance = abs(x - landing_x) + abs(y - landing_y)
            
            # Only increment if within affect radius
            if distance <= affect_radius:
                data['landings'] += 1
    
    def _get_block_color(self, block_type: str) -> str:
        """Get the color for a block type."""
        if 'red' in block_type:
            return 'red'
        elif 'blue' in block_type:
            return 'blue'
        elif 'green' in block_type:
            return 'green'
        elif 'yellow' in block_type:
            return 'yellow'
        else:
            return 'blue'  # Default color

# Back-compat alias for legacy imports expecting `TestMode` in this module
TestMode = TestModeRefactored