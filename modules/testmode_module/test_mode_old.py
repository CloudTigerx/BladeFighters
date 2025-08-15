"""
Simplified TestMode Implementation
Core puzzle battle functionality: 2 grids, piece previews, backgrounds.
Stripped of attack system complexity to focus on essential gameplay.
"""

import pygame
import os
import random
import time
from typing import List, Dict, Optional, Any, Tuple

# Try to import the interface contract
try:
    from contracts.testmode_interface_contract import TestModeInterface, validate_testmode_interface
    interface_available = True
except ImportError:
    # Create a dummy interface if not available
    class TestModeInterface:
        pass
    
    def validate_testmode_interface(cls):
        return cls
    
    interface_available = False

# Import required game components
from core.puzzle_module import PuzzleEngine
from core.puzzle_renderer import PuzzleRenderer

# Import the attack system
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from modules.attack_module import AttackManager
from modules.attack_module import AttackCalculator
from modules.attack_module.attacks_service import AttacksService
from modules.ai_module import EnemyAIConfig, RandomAI, HeuristicAI, config_for_difficulty
from modules.attack_module.column_rotator import ColumnRotator
from .board_runtime import BoardRuntime
from .attack_flow_tracker import AttackFlowTracker
from modules.items_module import ItemSystem
from modules.items_module.item_system import create_weapon_by_name
from modules.items_module.persistence import load_items_config, save_items_config

# Import new attack delivery services
from .attack_delivery_planner import AttackDeliveryPlanner, DeliveryConfig
from .attack_delivery_animator import AttackDeliveryAnimator
from .attack_delivery_committer import AttackDeliveryCommitter

# Import attack flow manager
from .attack_flow_manager import AttackFlowManager, AttackFlowConfig

@validate_testmode_interface
class TestMode(TestModeInterface):
    """Simplified TestMode focusing on core puzzle battle functionality."""
    
    def __init__(self, screen, font, audio, asset_path: str, settings_system=None, clock=None):
        """Initialize the test mode with core puzzle battle setup."""
        self.screen = screen
        self.font = font
        self.audio = audio
        self.asset_path = asset_path
        self.settings_system = settings_system
        # Unified time source (ms)
        from utils.clock import PygameClock, Clock  # local import to avoid circulars
        self.clock = clock or PygameClock()
        
        # Get screen dimensions
        self.width = screen.get_width()
        self.height = screen.get_height()
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GRAY = (100, 100, 100)
        self.LIGHT_BLUE = (100, 150, 255)
        
        # Create player puzzle engine
        self.player_engine = PuzzleEngine(screen, font, audio, asset_path, settings_system)
        # Create enemy puzzle engine (no audio to avoid conflicts)
        self.enemy_engine = PuzzleEngine(screen, font, None, asset_path, settings_system)
        
        # Set test_mode attribute so puzzle module knows to use landing-based transformation
        self.player_engine.test_mode = self
        self.enemy_engine.test_mode = self
        
        # Set player-specific on_piece_landed callbacks
        self.player_engine.on_piece_landed = lambda: self.on_piece_landed(1)
        self.enemy_engine.on_piece_landed = lambda: self.on_piece_landed(2)
        # Ensure both engines can call back to TestMode
        
        # Create renderers for both engines
        self.player_renderer = PuzzleRenderer(self.player_engine, clock=self.clock)
        self.enemy_renderer = PuzzleRenderer(self.enemy_engine, clock=self.clock)
        
        # Configure preview sides for both renderers
        self.player_renderer.preview_side = 'left'  # Player on the left
        self.enemy_renderer.preview_side = 'right'  # Enemy on the right
        
        # Initialize Enemy AI (decoupled controller) with default difficulty
        self.ai_difficulty: int = 10
        self.enemy_ai = HeuristicAI(config_for_difficulty(self.ai_difficulty))
        
        # Initialize attack manager (centralized system) and facade service
        self.attack_manager = AttackManager()
        self.attacks_service = AttacksService(clock=self.clock, attack_manager=self.attack_manager, item_system=None, settings=self.settings_system)
        # Database indicator for UI (AttackManager uses internal calculator; keep flag for UI)
        self.database_enabled = False
        
        # Chain tracking
        self.player_chain_position = 0
        self.enemy_chain_position = 0
        self.player_chain_active = False
        self.enemy_chain_active = False
        self.chain_window_duration = 302  # 2 seconds to continue chain
        self.last_player_combo_time = 0
        self.last_enemy_combo_time = 0

        # Per-board runtimes for input/chain locks
        self.player_runtime = BoardRuntime(board_id=1)
        self.enemy_runtime = BoardRuntime(board_id=2)
        
        # Connect attack system handlers for BOTH players via facade
        self.player_engine.blocks_broken_handler = lambda broken_blocks, is_cluster, combo_multiplier: self.attacks_service.on_combo(broken_blocks, is_cluster, combo_multiplier, player_id=1)
        self.enemy_engine.blocks_broken_handler = lambda broken_blocks, is_cluster, combo_multiplier: self.attacks_service.on_combo(broken_blocks, is_cluster, combo_multiplier, player_id=2)
        # Mark engines for side mapping
        setattr(self.player_engine, 'is_player_board', True)
        setattr(self.enemy_engine, 'is_player_board', False)
        
        # Load background images
        try:
            self.puzzle_background = pygame.image.load(os.path.join(asset_path, "puzzlebackground.jpg"))
        except pygame.error:
            self.puzzle_background = None
        
        # Set up board positions and dimensions
        self.setup_board_positions()
        
        # Initialize garbage block tracking
        self.garbage_block_brightness = {}
        
        # Initialize persistent column rotators for each player
        self.player_column_rotator = ColumnRotator(grid_width=6)
        self.enemy_column_rotator = ColumnRotator(grid_width=6)
        
        # Initialize attack flow tracker for clean debug output
        self.attack_tracker = AttackFlowTracker(clock=self.clock)

        # Initialize per-player item systems and equip from persisted config
        self.player_items = ItemSystem()
        self.enemy_items = ItemSystem()
        try:
            cfg_path = os.path.join(self.asset_path if hasattr(self, 'asset_path') else '.', 'items_config.json')
            items_cfg = load_items_config(cfg_path)
            p_name = items_cfg.get('player_weapon', 'Rusted Sword')
            e_name = items_cfg.get('enemy_weapon', 'Rusted Sword')
            p_w = create_weapon_by_name(p_name) or create_weapon_by_name('Rusted Sword')
            e_w = create_weapon_by_name(e_name) or create_weapon_by_name('Rusted Sword')
            if p_w:
                self.player_items.equip_weapon(p_w)
            if e_w:
                self.enemy_items.equip_weapon(e_w)
            # load ownership
            # Seed placeholder items if file has only the Rusted Sword
            p_owned = items_cfg.get('player_weapons', ['Rusted Sword'])
            e_owned = items_cfg.get('enemy_weapons', ['Rusted Sword'])
            # If minimal inventory, seed curated set for demo visibility
            if len(p_owned) <= 1 or len(e_owned) <= 1:
                try:
                    from modules.items_module.catalog import CURATED_WEAPONS
                    curated_names = [w['name'] for w in CURATED_WEAPONS]
                    if len(p_owned) <= 1:
                        p_owned = curated_names[:60]
                    if len(e_owned) <= 1:
                        e_owned = curated_names[:12]
                except Exception:
                    pass
            self.player_items.set_owned_weapons(p_owned)
            self.enemy_items.set_owned_weapons(e_owned)
        except Exception as e:
            pass

        # Pause window to receive attacks cleanly at end of turn (ms)
        self.attack_receive_pause_ms = 400

        # Provide clock to engines so subsystems can consume it
        try:
            setattr(self.player_engine, 'clock', self.clock)
            setattr(self.enemy_engine, 'clock', self.clock)
        except Exception:
            pass

        # Feature flags for safe rollout of falling attacks
        self.flags = {
            'attacks_fall_enabled': True,     # master switch for falling attacks
            'fall_garbage_enabled': True,     # enable falling for garbage (sprinkles)
            'fall_strikes_enabled': True,     # enable falling for strikes (phase 2)
            'enemy_only_fall': False,         # enable falling for both boards
            'fall_speed_scale': 0.75,         # >1.0 = slower falls; <1.0 = faster
            # Garbage lightning (Phase 1: instant)
            'lightning_breaks_enabled': True,
            'lightning_staggered': True,
        }
        
        # Initialize attack delivery services
        delivery_config = DeliveryConfig(
            attacks_fall_enabled=self.flags['attacks_fall_enabled'],
            fall_garbage_enabled=self.flags['fall_garbage_enabled'],
            fall_strikes_enabled=self.flags['fall_strikes_enabled'],
            enemy_only_fall=self.flags['enemy_only_fall'],
            fall_speed_scale=self.flags['fall_speed_scale'],
            lightning_breaks_enabled=self.flags['lightning_breaks_enabled'],
            lightning_staggered=self.flags['lightning_staggered'],
            lightning_hop_ms=self.flags.get('lightning_hop_ms', 75),
            lightning_affects_strikes=self.flags.get('lightning_affects_strikes', False)
        )
        self.delivery_planner = AttackDeliveryPlanner(delivery_config)
        self.delivery_animator = AttackDeliveryAnimator(delivery_config)
        self.delivery_committer = AttackDeliveryCommitter(delivery_config)
        
        # Initialize attack flow manager
        flow_config = AttackFlowConfig(
            chain_window_duration=self.chain_window_duration,
            attack_receive_pause_ms=self.attack_receive_pause_ms
        )
        self.attack_flow_manager = AttackFlowManager(flow_config, self.attacks_service)
        
        # UNIFIED ATTACK SPAWNING SYSTEM
        # Note: pending_attacks is now managed by attack_flow_manager
        # Keeping this for backward compatibility with existing code
        self.pending_attacks = self.attack_flow_manager.pending_attacks

        # Honor spawn mode setting (animated | instant)
        try:
            cfg = getattr(self.settings_system, 'config', self.settings_system)
            mode = str(cfg.get('attacks.spawn_mode', 'animated')).strip().lower() if cfg and hasattr(cfg, 'get') else 'animated'
            if mode == 'instant':
                # Disable falling so update_attack_spawning uses direct placement branches
                self.flags['attacks_fall_enabled'] = False
                self.flags['fall_garbage_enabled'] = False
                self.flags['fall_strikes_enabled'] = False
            else:
                self.flags['attacks_fall_enabled'] = True
                self.flags['fall_garbage_enabled'] = True
                self.flags['fall_strikes_enabled'] = True
        except Exception:
            pass

        # Propagate lightning flags to engines
        for eng in (self.player_engine, self.enemy_engine):
            eng.lightning_breaks_enabled = self.flags.get('lightning_breaks_enabled', False)
            eng.lightning_staggered = self.flags.get('lightning_staggered', False)
            eng.lightning_hop_ms = int(self.flags.get('lightning_hop_ms', 100))
            eng.lightning_affects_strikes = self.flags.get('lightning_affects_strikes', False)

        # Initialize flags watcher signature and print initial state
        try:
            self._flags_last_sig = tuple(sorted(self.flags.items()))
            print(f"[FLAGS init] {self.flags}")
        except Exception:
            pass

    def _now_ms(self) -> int:
        return int(self.clock.now_ms())

    def _now_s(self) -> float:
        return self._now_ms() / 1000.0

        # Aggregate attacks across chain and release when chain closes
        self.aggregated_attacks = {
            'player': [],  # attacks targeting player
            'enemy': []    # attacks targeting enemy
        }

        # Spawn pause (stop piece updates) during strike delivery
        self.player_spawn_pause_until = 0
        self.enemy_spawn_pause_until = 0

        # Initialize the puzzle battle
        self.initialize_test()

        
    
    def save_equipment(self):
        """Persist current equipped items for both player and enemy."""
        try:
            cfg_path = os.path.join(self.asset_path if hasattr(self, 'asset_path') else '.', 'items_config.json')
            p_name = self.player_items.get_equipped_weapon().name if self.player_items and self.player_items.get_equipped_weapon() else 'Rusted Sword'
            e_name = self.enemy_items.get_equipped_weapon().name if self.enemy_items and self.enemy_items.get_equipped_weapon() else 'Rusted Sword'
            save_items_config(cfg_path, {
                'player_weapon': p_name,
                'enemy_weapon': e_name,
                'player_weapons': self.player_items.get_owned_weapons(),
                'enemy_weapons': self.enemy_items.get_owned_weapons(),
            })
        except Exception:
            pass
        
    def setup_board_positions(self):
        """Set up the positions for the player and enemy puzzle boards."""
        # Use actual engine grid specs so containers/backgrounds match rendered grids
        grid_width = getattr(self.player_engine, 'grid_width', 6)
        # If engines differ, take the max height to avoid clipping
        p_h = getattr(self.player_engine, 'grid_height', 15)
        e_h = getattr(self.enemy_engine, 'grid_height', p_h)
        grid_height = max(p_h, e_h)
        
        # Use the actual block sizes from the engines instead of hardcoded values
        cell_width = self.player_engine.block_size
        cell_height = self.player_engine.block_size
        border_size = 10  # Space between container edge and the actual grid
        
        # Calculate board dimensions
        board_width = grid_width * cell_width
        board_height = grid_height * cell_height
        
        # Calculate proper centered positions
        screen_width = self.width
        board_spacing = 40  # Space between boards
        
        # Center calculation - include borders in the total width
        total_width_needed = (board_width * 2) + board_spacing + (border_size * 4)
        start_x = (screen_width - total_width_needed) // 2
        
        # Player board position (left side)
        player_x = start_x + border_size
        player_y = 80
        
        # Enemy board position (right side) 
        enemy_x = start_x + board_width + board_spacing + (border_size * 3)
        enemy_y = 80
        
        # Store positions
        self.player_grid_position = {"x": player_x, "y": player_y}
        self.enemy_grid_position = {"x": enemy_x, "y": enemy_y}
        
        # Update engine grid offsets for proper rendering
        self.player_engine.grid_x_offset = player_x
        self.player_engine.grid_y_offset = player_y
        self.enemy_engine.grid_x_offset = enemy_x
        self.enemy_engine.grid_y_offset = enemy_y
        
        # Update renderer coordinate offsets to match the new positions
        self.player_renderer.update_coordinate_offsets()
        self.enemy_renderer.update_coordinate_offsets()
        
        # Store cell dimensions for use in drawing
        self.cell_width = cell_width
        self.cell_height = cell_height
        self.board_width = board_width
        self.board_height = board_height
    
    def initialize_test(self):
        """Initialize or reset the test mode game state."""
        print("🔄 COMPREHENSIVE GAME RESET INITIATED...")
        
        # Reset chain states
        self.player_chain_position = 0
        self.enemy_chain_position = 0
        self.player_chain_active = False
        self.enemy_chain_active = False
        self.last_player_combo_time = 0
        self.last_enemy_combo_time = 0
        
        # Reset attack queues
        if hasattr(self, 'attack_manager'):
            self.attack_manager.clear_attack_queues()
        
        # Reset piece movement state for both engines
        self.player_engine.current_fall_speed = self.player_engine.normal_fall_speed
        self.player_engine.last_fall_time = self._now_ms()
        self.player_engine.micro_fall_time = self.player_engine._calculate_micro_fall_time(self.player_engine.current_fall_speed)
        self.enemy_engine.current_fall_speed = self.enemy_engine.normal_fall_speed
        self.enemy_engine.last_fall_time = self._now_ms()
        self.enemy_engine.micro_fall_time = self.enemy_engine._calculate_micro_fall_time(self.enemy_engine.current_fall_speed)
        
        # Reset engine state completely
        self.reset_engine_state(self.player_engine)
        self.reset_engine_state(self.enemy_engine)
        
        # Start both games
        self.player_engine.start_game()
        self.enemy_engine.start_game()
        
        # Reset renderer animation states
        self.reset_renderer_state(self.player_renderer)
        self.reset_renderer_state(self.enemy_renderer)
        
        # Update renderers
        self.player_renderer.update_visual_state()
        self.player_renderer.update_animations()
        self.enemy_renderer.update_visual_state()
        self.enemy_renderer.update_animations()
        
        # Reset garbage block state
        self.reset_garbage_block_state()
        
        # Reset unified attack spawning system
        self.attack_flow_manager.clear_pending_attacks('player')
        self.attack_flow_manager.clear_pending_attacks('enemy')
        # Reset aggregated attacks across chains to avoid stale carry-over
        if hasattr(self, 'aggregated_attacks'):
            self.aggregated_attacks = {'player': [], 'enemy': []}
        # Reset any spawn pauses
        if hasattr(self, 'player_spawn_pause_until'):
            self.player_spawn_pause_until = 0
        if hasattr(self, 'enemy_spawn_pause_until'):
            self.enemy_spawn_pause_until = 0
        
        # Clear any stuck alternators
        for player_key in ['player', 'enemy']:
            if hasattr(self, f'{player_key}_side_column_alternator'):
                delattr(self, f'{player_key}_side_column_alternator')
            if hasattr(self, f'{player_key}_side_layer_alternator'):
                delattr(self, f'{player_key}_side_layer_alternator')
        
        # Reset column rotators to ensure proper distribution
        self.player_column_rotator.reset_rotation()
        self.enemy_column_rotator.reset_rotation()
        
        print("✅ COMPREHENSIVE GAME RESET COMPLETED")
    
    def reset_engine_state(self, engine):
        """Reset all engine state including breakers, clusters, and animations."""
        # Reset core game state
        engine.chain_reaction_in_progress = False
        engine.breaking_blocks = []
        engine.clusters = set()
        engine.chain_state = "idle"
        engine.chain_count = 0
        engine.last_state_change = 0
        
        # Reset breaker detection state
        if hasattr(engine, 'last_cluster_check_time'):
            engine.last_cluster_check_time = 0
        
        # Reset animation state if renderer exists
        if hasattr(engine, 'renderer') and engine.renderer:
            if hasattr(engine.renderer, 'animation_manager'):
                engine.renderer.animation_manager.reset_animation_state()
        
        # Clear any pending animations
        if hasattr(engine, 'renderer') and engine.renderer:
            engine.renderer.clear_all_animations()
    
    def reset_renderer_state(self, renderer):
        """Reset renderer animation and visual state."""
        if hasattr(renderer, 'animation_manager'):
            renderer.animation_manager.reset_animation_state()
        
        # Clear any cluster highlights or visual effects
        if hasattr(renderer, 'cluster_highlights'):
            renderer.cluster_highlights.clear()
        
        # Reset visual state
        renderer.update_visual_state()
        renderer.update_animations()

    def reset_garbage_block_state(self):
        """Reset all garbage block transformation state."""
        self.garbage_block_brightness.clear()

    # UNIFIED ATTACK SPAWNING SYSTEM METHODS
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
            created_ms = int(payload.get('created_ms', self._now_ms()))
            start_y = int(payload.get('start_y', -1))
        else:
            target_player = target_player_or_payload
            created_ms = self._now_ms()
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
            'handedness': self.attack_manager.get_next_handedness() if hasattr(self, 'attack_manager') else 'R',
            # For sprinkles (garbage), store sweep side (R/L)
            'sprinkle_side': self.attack_manager.get_next_handedness() if hasattr(self, 'attack_manager') else 'R'
        }

        # Use attack flow manager to queue the attack
        self.attack_flow_manager.queue_attack(target_player, attack_data)
        
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
    
    def update_attack_spawning(self):
        """Apply pending attacks directly to the board when eligible (no above-board falling)."""
        # Watch for runtime changes to flags
        try:
            current_sig = tuple(sorted(self.flags.items()))
            if getattr(self, '_flags_last_sig', None) != current_sig:
                print(f"[FLAGS update] {self.flags}")
                self._flags_last_sig = current_sig
        except Exception:
            pass
        current_time = self._now_ms()
        
        # Advance time and process attack queue to make attacks ready
        now_sec = current_time / 1000.0
        update_result = self.attack_manager.update(now_sec)
        ready_attacks = update_result.get('ready_attacks', {})
        
        # Deliver attacks from attack_manager to pending_attacks for both players
        self.attacks_service.deliver_with_ready_attacks(board=self.player_engine, renderer=self.player_renderer, ready_attacks=ready_attacks)
        self.attacks_service.deliver_with_ready_attacks(board=self.enemy_engine, renderer=self.enemy_renderer, ready_attacks=ready_attacks)
        
        # Update renderer animations to clean up expired animations
        self.player_renderer.update_animations()
        self.enemy_renderer.update_animations()
        

        
        # Process attacks for both players
        for player_key in ['player', 'enemy']:
            engine = self.player_engine if player_key == 'player' else self.enemy_engine
            column_rotator = self.player_column_rotator if player_key == 'player' else self.enemy_column_rotator
            
            # Do not gate spawning animations; allow visuals to begin immediately.
            # We will still respect safe commit semantics inside placement routines.
            
            # Process each pending attack
            attacks_to_remove = []
            for attack in self.pending_attacks[player_key]:
                # Safety check: if attack is too old, remove it to prevent infinite loops
                if current_time - attack['spawn_time'] > 10000:  # 10 seconds
                    attacks_to_remove.append(attack)
                    continue
                
                complete_this_attack = False
                blocks_placed = 0

                if attack['type'] == 'strike':
                    # Strikes: use falling group path when enabled
                    use_falling_strikes = (
                        self.flags.get('attacks_fall_enabled', False)
                        and self.flags.get('fall_strikes_enabled', False)
                        and (player_key == 'enemy' or not self.flags.get('enemy_only_fall', False))
                    )
                    if use_falling_strikes:
                        # Use delivery services directly
                        now_sec = self._now_s()
                        if 'plan' not in attack:
                            item_system = self.enemy_items if player_key == 'player' else self.player_items
                            column_rotator = self.player_column_rotator if player_key == 'player' else self.enemy_column_rotator
                            plan = self.delivery_planner.plan_strike_delivery(engine, attack, player_key, item_system, column_rotator)
                            attack['plan'] = plan
                            attack['anim_state'] = None
                            attack['anim_started'] = False
                        
                        if not attack.get('anim_started'):
                            anim_state = self.delivery_animator.start_strike_animation(engine, attack['plan'], now_sec)
                            attack['anim_state'] = anim_state
                            attack['anim_started'] = True
                            continue
                        
                        if not self.delivery_animator.is_animation_complete(engine, attack['anim_state'], now_sec):
                            continue
                        
                        result = self.delivery_committer.commit_strikes(engine, attack['plan'], player_key)
                        self.delivery_animator.cleanup_animation(engine, attack['anim_state'])
                        blocks_placed = result.blocks_placed
                        complete_this_attack = True
                    else:
                        blocks_placed = self.place_strike_with_falling(engine, attack, player_key, column_rotator)
                        complete_this_attack = True
                else:
                    # Garbage: optionally use falling path per flags
                    use_falling = (
                        self.flags.get('attacks_fall_enabled', False)
                        and self.flags.get('fall_garbage_enabled', False)
                        and (player_key == 'enemy' or not self.flags.get('enemy_only_fall', False))
                    )
                    if use_falling:
                        # Use delivery services directly
                        now_sec = self._now_s()
                        if 'plan' not in attack:
                            item_system = self.enemy_items if player_key == 'player' else self.player_items
                            plan = self.delivery_planner.plan_garbage_delivery(engine, attack, player_key, item_system)
                            attack['plan'] = plan
                            attack['anim_state'] = None
                            attack['anim_started'] = False
                        
                        if not attack.get('anim_started'):
                            anim_state = self.delivery_animator.start_garbage_animation(engine, attack['plan'], now_sec)
                            attack['anim_state'] = anim_state
                            attack['anim_started'] = True
                            continue
                        
                        if not self.delivery_animator.is_animation_complete(engine, attack['anim_state'], now_sec):
                            continue
                        
                        result = self.delivery_committer.commit_garbage(engine, attack['plan'], player_key)
                        self.delivery_animator.cleanup_animation(engine, attack['anim_state'])
                        blocks_placed = result.blocks_placed
                        complete_this_attack = True
                    else:
                        # Immediate placement path (teleport-style)
                        blocks_placed = self.place_garbage_payload(engine, attack, player_key, column_rotator)
                        complete_this_attack = True

                if blocks_placed:
                    # Track placed blocks (for strikes it's total cells; for garbage it's total sprinkles)
                    attack_type = 'strikes' if attack['type'] == 'strike' else 'garbage'
                    self.attack_tracker.track_placed(player_key, attack_type, blocks_placed)

                    # Update log placed count with the total placed for this payload
                    try:
                        for entry in reversed(self.recent_attack_log):
                            if not entry.get('closed') and entry['target'] == player_key and entry['type'] == attack['type']:
                                entry['placed'] += int(blocks_placed)
                                break
                    except Exception:
                        pass

                    # While receiving, pause next piece spawn briefly to avoid overlap
                    pause_field = 'player_spawn_pause_until' if player_key == 'player' else 'enemy_spawn_pause_until'
                    setattr(self, pause_field, max(getattr(self, pause_field, 0), current_time + self.attack_receive_pause_ms))

                if complete_this_attack:
                    attack['blocks_remaining'] = 0
                    attacks_to_remove.append(attack)
            
            # Remove completed attacks
            for attack in attacks_to_remove:
                self.pending_attacks[player_key].remove(attack)
                try:
                    for entry in reversed(self.recent_attack_log):
                        if not entry.get('closed') and entry['target'] == player_key and entry['type'] == attack['type']:
                            entry['closed'] = True
                            break
                except Exception:
                    pass
    
    
    

    
    def place_garbage_payload(self, engine, attack, player_key, column_rotator):
        """Place all garbage (sprinkles) for this queued attack.
        - Alternates side per attack group using stored sprinkle_side (R/L)
        - Sweeps across columns in that direction
        - Avoids maximizing; respects filled columns as wasted
        - Column 4: if target row would exceed row 10 in column 4, treat as wasted
        """
        grid = engine.puzzle_grid
        player = 1 if player_key == 'player' else 2
        blocks_to_place = attack['blocks_remaining']

        # Colors determined per column by item system

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
                # Respect instakill cap in column 4 (index 3): if already >= 10 rows tall, waste
                if column == 3:
                    # Count filled cells in column 4 from bottom
                    filled = sum(1 for y in range(engine.grid_height-1, -1, -1) if grid[y][column] not in ['empty', None])
                    if filled >= 10:
                        # Wasted, do not place elsewhere
                        blocks_to_place -= 1
                        continue

                # Find next landing spot in this column
                landing_row = None
                for row in range(engine.grid_height - 1, -1, -1):
                    if grid[row][column] in ['empty', None]:
                        landing_row = row
                        break
                if landing_row is None:
                    # Entire column full => waste and continue (do not reroute)
                    blocks_to_place -= 1
                    continue

                # Place sprinkle
                item_sys = self.enemy_items if player_key == 'player' else self.player_items
                col_color = item_sys.get_garbage_color_for_column(column)
                # Stage 0 visual: neutral garbage immediately on receipt
                grid[landing_row][column] = 'garbage_block'

                tracking_key = (column, landing_row, player)
                self.garbage_block_brightness[tracking_key] = {
                    'landings': 0,
                    'color': col_color,
                    'is_strike': False
                }

                blocks_placed += 1
                blocks_to_place -= 1

            # Continue sweeping until all placed or wasted

        

        attack['blocks_remaining'] = 0
        return blocks_placed
    

    



    
    def place_strike_with_falling(self, engine, attack, player_key, column_rotator):
        """Place a strike attack with proper dimensions and falling animation from above the board.
        Supports multiple strike patterns in one payload.
        """
        grid = engine.puzzle_grid
        player = 1 if player_key == 'player' else 2
        strike_details = attack.get('strike_details', [])
        if not strike_details:
            strike_details = [f"1x{min(8, max(1, attack['count']))}"]

        total_blocks_placed = 0
        # Determine strike color per column from item system when placing

        # Compute cluster cells to respect non-piercing rule
        cluster_cells = self._compute_cluster_cells(engine)

        pierce_budgets = attack.get('pierce_budgets', [1] * len(strike_details))
        # Track reserved columns for this batch to enforce multi-sword forcing rules
        reserved_spans: set[int] = set()
        for idx, dimensions in enumerate(strike_details):
            try:
                if 'x' in dimensions:
                    width, height = map(int, dimensions.split('x'))
                else:
                    width, height = 1, int(dimensions)
            except Exception:
                continue

            # Find a suitable starting column
            start_column = self.find_strike_starting_column(engine, width, column_rotator, strike_height=height, reserved_spans=reserved_spans)
            if start_column is None:
                
                continue

            # Determine landing position across width
            max_placement_row = engine.grid_height - 1
            for col in range(start_column, start_column + width):
                placement_row = engine.grid_height - 1
                while placement_row >= 0 and grid[placement_row][col] not in ['empty', None]:
                    placement_row -= 1
                max_placement_row = min(max_placement_row, placement_row)

            # Truncate height if needed
            if max_placement_row - height + 1 < 0:
                original_height = height
                height = max_placement_row + 1
                

            blocks_placed = 0
            budget = pierce_budgets[idx] if idx < len(pierce_budgets) else 1
            for col in range(start_column, start_column + width):
                for row in range(max_placement_row - height + 1, max_placement_row + 1):
                    # Respect non-piercing rule for cluster cells unless we have budget to pierce normal blocks only
                    if (col, row) in cluster_cells:
                        continue
                    # If there's a normal (non-empty, non-cluster) block, consume budget to pierce it
                    if grid[row][col] not in ['empty', None] and (col, row) not in cluster_cells:
                        if budget <= 0:
                            continue
                        budget -= 1
                    # Place strike
                    item_sys = self.enemy_items if player_key == 'player' else self.player_items
                    # Convert grid row to board position color using full 12-row pattern
                    col_color = item_sys.get_strike_color_for_cell(col, row, engine.grid_height)
                    # Bounds safety: ensure we do not write outside grid
                    if 0 <= row < engine.grid_height and 0 <= col < engine.grid_width:
                        block_type = f"{col_color}_strike"
            # No animation registration; rely on existing visuals
                        grid[row][col] = block_type
                    else:
                        continue
                    tracking_key = (col, row, player)
                    self.garbage_block_brightness[tracking_key] = {
                        'landings': 0,
                        'color': col_color,
                        'is_strike': True
                    }
                    blocks_placed += 1
                    total_blocks_placed += 1

            # Reserve the span for this batch so subsequent swords avoid stacking directly
            for c in range(start_column, min(start_column + width, engine.grid_width)):
                reserved_spans.add(c)

            side = "left" if start_column < 3 else "right"
            

        # Return the exact count so the caller can decrement blocks_remaining correctly
        return total_blocks_placed




    def _compute_cluster_cells(self, engine):
        """Compute positions that are part of any 2x2+ same-color rectangle cluster on the target grid."""
        grid = engine.puzzle_grid
        width = engine.grid_width
        height = engine.grid_height
        cluster = set()

        # Simple 2x2 detection; mark all four cells; this also marks larger rectangles via overlapping 2x2s
        for y in range(height - 1):
            for x in range(width - 1):
                a = grid[y][x]
                b = grid[y][x + 1]
                c = grid[y + 1][x]
                d = grid[y + 1][x + 1]
                if not a or not b or not c or not d:
                    continue
                # Exclude strike/garbage from forming protective clusters
                if ('_strike' in str(a)) or ('_strike' in str(b)) or ('_strike' in str(c)) or ('_strike' in str(d)):
                    continue
                if ('_garbage' in str(a)) or ('_garbage' in str(b)) or ('_garbage' in str(c)) or ('_garbage' in str(d)):
                    continue
                ca = a.split('_')[0]
                cb = b.split('_')[0]
                cc = c.split('_')[0]
                cd = d.split('_')[0]
                if ca == cb == cc == cd:
                    cluster.update({(x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)})

        return cluster

    def find_strike_starting_column(self, engine, strike_width, column_rotator, strike_height=None, reserved_spans: set[int] | None = None):
        """Find a starting column using shared column sequence and handedness rules.
        - Start at the next column in 2,3,4,5,6,1 (0-based: 1,2,3,4,5,0)
        - Avoid column 4 unless forced
        - Handedness determines scan direction for obstacle avoidance
        - If no full fit exists, pick column that allows largest portion (wastage elsewhere)
        """
        grid = engine.puzzle_grid
        grid_w = engine.grid_width
        grid_h = engine.grid_height

        # Shared rotation (preferred order) fetched from manager sequence (1-based → 0-based)
        try:
            mgr_seq = getattr(self.attack_manager, 'column_sequence', [2, 3, 4, 5, 6, 1])
            rotation = [(max(1, min(6, v)) - 1) for v in mgr_seq]
        except Exception:
            rotation = [1, 2, 3, 4, 5, 0]  # 0-based for 2,3,4,5,6,1

        # Determine handedness from manager (R or L)
        try:
            hand = self.attack_manager.get_next_handedness()
        except Exception:
            hand = 'R'

        # Helper: check maximum vertical length that can enter for this start column span
        def capacity_for_span(start_col: int, width: int) -> int:
            if start_col < 0 or start_col + width > grid_w:
                return -1
            # Avoid spans reserved by earlier swords in this batch
            if reserved_spans:
                for cc in range(start_col, start_col + width):
                    if cc in reserved_spans:
                        return -1
            max_rows = grid_h
            # Find highest filled cell in each column and derive contiguous empty space from top
            # Here we compute how many rows from top can be filled before hitting non-empty
            # For placement we actually drop from top, so usable length is count of empty cells from top per column
            col_caps = []
            for c in range(start_col, start_col + width):
                empty_from_top = 0
                for r in range(0, grid_h):
                    if grid[r][c] in ['empty', None]:
                        empty_from_top += 1
                    else:
                        break
                col_caps.append(empty_from_top)
            return min(col_caps) if col_caps else -1

        # Deterministic base column from sword-width specific patterns, else fallback to rotation
        base_candidates = []
        try:
            # Determine sword width in columns for vertical placement
            sword_width = max(1, min(3, int(strike_width)))
            patterns = getattr(self.attack_manager, 'vertical_patterns', None)
            indices = getattr(self.attack_manager, 'vertical_pattern_indices', None)
            if patterns and indices and sword_width in patterns:
                pat = patterns[sword_width]
                idx = indices[sword_width] % len(pat)
                base = pat[idx]
                # Advance index for next time (horizontals also advance elsewhere)
                self.attack_manager.vertical_pattern_indices[sword_width] = (idx + 1) % len(pat)
                # Convert to 0-based; for tuples, prefer left-most column to seed scan
                if isinstance(base, tuple):
                    base_candidates = [b - 1 for b in base]
                else:
                    base_candidates = [int(base) - 1]
        except Exception:
            base_candidates = []

        # If no deterministic base from patterns, fallback to shared rotation order
        if not base_candidates:
            base_idx = (self.attack_manager.column_rotation_state) % len(rotation) if hasattr(self.attack_manager, 'column_rotation_state') else 0
            ordered = rotation[base_idx:] + rotation[:base_idx]
        else:
            # Seed ordered list with pattern-derived base(s), then fill with rotation as secondary
            base_idx = (self.attack_manager.column_rotation_state) % len(rotation) if hasattr(self.attack_manager, 'column_rotation_state') else 0
            rotation_order = rotation[base_idx:] + rotation[:base_idx]
            ordered = base_candidates + [c for c in rotation_order if c not in base_candidates]

        # Apply handedness scanning: start at base, then step right/left accordingly
        def scan_order(cols: list[int], hand_side: str) -> list[int]:
            if hand_side == 'R':
                # Prefer moving toward higher indices first
                return cols
            # Left-handed: reverse preference
            return cols[::-1]

        ordered = scan_order(ordered, hand)

        # Primary: find a span that fully fits (capacity >= 1) and does not land directly atop strikes
        best_partial = (-1, -1)  # (best_capacity, start_col)
        for start in ordered:
            # Avoid starting such that span includes column index 3 (col 4) unless no other place
            span_cols = list(range(start, min(start + strike_width, grid_w)))
            if 3 in span_cols:
                # Defer this unless forced
                pass
            cap = capacity_for_span(start, strike_width)
            if cap <= 0:
                continue
            # If a height is given, ensure we won't land directly atop an existing strike
            if strike_height is not None:
                # Compute landing rows per column (bottom-most empty)
                placement_rows = []
                for c in span_cols:
                    pr = None
                    for row in range(grid_h - 1, -1, -1):
                        if grid[row][c] in ['empty', None]:
                            pr = row
                            break
                    if pr is None:
                        placement_rows = []
                        break
                    placement_rows.append(pr)
                if placement_rows:
                    max_placement_row = min(placement_rows)
                    # Check base cell below landing for each col
                    strike_on_base = False
                    for idx_c, c in enumerate(span_cols):
                        base_below = max_placement_row + 1
                        if base_below < grid_h and grid[base_below][c] and ('_strike' in str(grid[base_below][c])):
                            strike_on_base = True
                            break
                    if strike_on_base:
                        continue  # skip starts that land atop strikes
            if cap == grid_h:
                # Full empty board fit: ideal
                return start
            if cap > 0:
                # Track best partial capacity to maximize sword entry
                if cap > best_partial[0] and (3 not in span_cols):
                    best_partial = (cap, start)

        # If no non-column-4 full/partial fit found, allow column 4
        if best_partial[0] > 0:
            return best_partial[1]

        # As last resort, allow spans crossing column 4 and pick best capacity
        best_with_center = (-1, -1)
        for start in ordered:
            cap = capacity_for_span(start, strike_width)
            if cap > best_with_center[0]:
                best_with_center = (cap, start)
        if best_with_center[0] > 0:
            return best_with_center[1]

        # Fallback to rotator
        base = column_rotator.get_next_column()
        if base + strike_width <= grid_w:
            return base
        return None

    def update(self) -> Optional[str]:
        """Update the test mode state."""
        current_time = self._now_ms()

        # Maintain lock windows
        try:
            self.player_runtime.clear_expired(current_time)
            # Chain lock if player's chain is active (best-effort hook)
            if getattr(self.player_engine, 'chain_reaction_in_progress', False):
                freeze_ms = self._get_attack_freeze_ms()
                self.player_runtime.lock_chain(freeze_ms, current_time)
        except Exception:
            pass

        # Apply input locks to player's input handler before engine updates
        try:
            self.player_engine.input_handler.apply_external_lock(self.player_runtime.is_input_locked(current_time))
        except Exception:
            pass
        
        # Update player engine (respect spawn pause)
        if current_time >= getattr(self, 'player_spawn_pause_until', 0):
            self.player_engine.update()
        
        # Update enemy engine and AI (respect spawn pause)
        if current_time >= getattr(self, 'enemy_spawn_pause_until', 0):
            self.enemy_engine.update()
            # Decoupled AI tick (can be disabled by setting self.enemy_ai = None)
            if getattr(self, 'enemy_ai', None) and self.enemy_engine.game_active:
                self.enemy_ai.update(self.enemy_engine, current_time)
        
        # Deliver any ready attacks via facade, then update spawning system
        res_player = self.attacks_service.deliver(board=self.player_engine, renderer=self.player_renderer)
        res_enemy = self.attacks_service.deliver(board=self.enemy_engine, renderer=self.enemy_renderer)

        # If payloads were applied to the player, lock player input briefly
        try:
            if isinstance(res_player, dict) and int(res_player.get("payload_count", 0)) > 0 and int(res_player.get("applied_to_board_id", 0)) == 1:
                self.player_runtime.lock_input(self._get_attack_freeze_ms(), current_time)
        except Exception:
            pass
        self.update_attack_spawning()

        # Safety: reconcile tracked strike/garbage with actual grid state to avoid visual desyncs
        self._reconcile_garbage_tracking_with_grid()
        
        # Print attack flow summary periodically
        if self.attack_tracker.should_print_summary():
            self.attack_tracker.print_summary()
        
        # Inline random movement removed in favor of decoupled AI
        # Ensure both renderers are updated using the same clock snapshot in draw()
        
        # Chain aggregation is disabled for attack delivery; keep these only for UI if needed.
        
        # Check for game over conditions (auto-reset disabled during tests to preserve spawn flow)
        # Keep game running; external client may reset explicitly.
        
        return None

    def _get_attack_freeze_ms(self) -> int:
        # Resolve from settings service if available; otherwise default
        try:
            cfg = getattr(self.settings_system, 'config', self.settings_system)
            if cfg and hasattr(cfg, 'get'):
                return int(cfg.get('attack_freeze_ms_on_receive', 150))
        except Exception:
            pass
        return 150
    
    def process_events(self, events: List) -> Optional[str]:
        """Process input events for the test mode."""
        # Let the player engine handle its own events first
        self.player_engine.process_events(events)
        
        # Handle test mode specific events
        for event in events:
            if event.type == pygame.KEYDOWN:
                # Escape key to return to menu
                if event.key == pygame.K_ESCAPE:
                    return "back_to_menu"
                
                # Quick AI difficulty set: number keys 1..0 (0 maps to 10)
                if pygame.K_1 <= event.key <= pygame.K_9 or event.key == pygame.K_0:
                    if event.key == pygame.K_0:
                        new_level = 10
                    else:
                        new_level = (event.key - pygame.K_1) + 1
                    self.ai_difficulty = max(1, min(10, new_level))
                    self.enemy_ai.config = config_for_difficulty(self.ai_difficulty)
                    
                
                # Fine adjust: '-' decreases, '='/'+' increases
                if event.key in (pygame.K_MINUS, pygame.K_EQUALS, pygame.K_PLUS):
                    delta = -1 if event.key == pygame.K_MINUS else 1
                    self.ai_difficulty = max(1, min(10, self.ai_difficulty + delta))
                    self.enemy_ai.config = config_for_difficulty(self.ai_difficulty)
                    

                # Toggle AI type: R = Random, H = Heuristic
                if event.key == pygame.K_r:
                    self.enemy_ai = RandomAI(config_for_difficulty(self.ai_difficulty))
                    
                if event.key == pygame.K_h:
                    self.enemy_ai = HeuristicAI(config_for_difficulty(self.ai_difficulty))
                    
        
        return None
    
    def handle_player_blocks_broken(self, broken_blocks, is_cluster, combo_multiplier):
        """Handle blocks broken by player - generate attacks"""
        current_time = self._now_ms()
        # Defensive: dedupe identical break events within a short window to avoid repeated attack generation
        try:
            sig = (1, tuple(sorted((int(x), int(y)) for x, y, _ in broken_blocks)), int(combo_multiplier))
            if not hasattr(self, '_recent_break_sigs'):
                self._recent_break_sigs = {}
            last_ts = self._recent_break_sigs.get(sig)
            if last_ts is not None and current_time - last_ts < 300:
                return
            self._recent_break_sigs[sig] = current_time
            # prune old
            for k, ts in list(self._recent_break_sigs.items()):
                if current_time - ts > 1000:
                    self._recent_break_sigs.pop(k, None)
        except Exception:
            pass
        
        # Use centralized manager: process combo directly with the engine-provided combo_multiplier.
        # Do NOT time-aggregate chains here; each engine combo event is independent.
        is_cluster_flag = is_cluster or (len(broken_blocks) >= 4)
        # Process the combo and generate attacks (player 1) using incoming combo_multiplier
        self.attack_manager.process_combo(
            broken_blocks=broken_blocks,
            is_cluster=is_cluster_flag,
            combo_multiplier=max(1, int(combo_multiplier)),
            player_id=1,
        )
        # Immediately dispatch attacks for this event to enemy (no time-window aggregation)
        attacks = self.attack_manager.pop_attacks_for_player(target_player=2)
        if attacks:
            self.send_player_attacks_to_enemy(attacks)
    
    def handle_enemy_blocks_broken(self, broken_blocks, is_cluster, combo_multiplier):
        """Handle blocks broken by enemy - generate attacks"""
        current_time = self._now_ms()
        # Defensive: dedupe identical break events within a short window
        try:
            sig = (2, tuple(sorted((int(x), int(y)) for x, y, _ in broken_blocks)), int(combo_multiplier))
            if not hasattr(self, '_recent_break_sigs'):
                self._recent_break_sigs = {}
            last_ts = self._recent_break_sigs.get(sig)
            if last_ts is not None and current_time - last_ts < 300:
                return
            self._recent_break_sigs[sig] = current_time
            for k, ts in list(self._recent_break_sigs.items()):
                if current_time - ts > 1000:
                    self._recent_break_sigs.pop(k, None)
        except Exception:
            pass
        
        # Use centralized manager directly with engine-provided combo_multiplier.
        is_cluster_flag = is_cluster or (len(broken_blocks) >= 4)
        # Process the combo and generate attacks (player 2)
        self.attack_manager.process_combo(
            broken_blocks=broken_blocks,
            is_cluster=is_cluster_flag,
            combo_multiplier=max(1, int(combo_multiplier)),
            player_id=2,
        )
        # Immediately dispatch attacks for this event to player (no time-window aggregation)
        attacks = self.attack_manager.pop_attacks_for_player(target_player=1)
        if attacks:
            self.send_enemy_attacks_to_player(attacks)
    
    def end_player_chain(self):
        """End the player's chain and send final attacks."""
        if self.player_chain_active:
            
            # Send aggregated attacks to enemy
            attacks = self.aggregated_attacks['enemy']
            if attacks:
                self.send_player_attacks_to_enemy(attacks)
                self.aggregated_attacks['enemy'] = []
            self.player_chain_active = False
            self.player_chain_position = 0
    
    def end_enemy_chain(self):
        """End the enemy's chain and send final attacks."""
        if self.enemy_chain_active:
            
            # Send aggregated attacks to player
            attacks = self.aggregated_attacks['player']
            if attacks:
                self.send_enemy_attacks_to_player(attacks)
                self.aggregated_attacks['player'] = []
            self.enemy_chain_active = False
            self.enemy_chain_position = 0
    
    def send_player_attacks_to_enemy(self, attacks=None):
        """Send player's pending attacks to enemy using unified spawning system.
        If a list of attacks is provided, use it directly; otherwise pop from the manager.
        Aggregate multiple attacks into single payloads per type.
        """
        if attacks is None:
            attacks = self.attack_manager.pop_attacks_for_player(target_player=2)
        if not attacks:
            return

        total_garbage = 0
        strike_details = []
        pierce_budgets = []  # per-strike pattern budget based on combo level
        total_strike_blocks = 0

        for attack in attacks:
            a_type = getattr(attack, 'attack_type', None).value if getattr(attack, 'attack_type', None) else None
            if a_type == 'garbage_blocks':
                total_garbage += getattr(attack, 'block_count', 0)
            elif a_type == 'cluster_strike':
                w = getattr(attack, 'strike_width', 1)
                h = getattr(attack, 'strike_height', 1)
                patt = getattr(attack, 'strike_pattern', '') or ''
                is_horizontal = patt.endswith('_horizontal')
                combo = 1
                if hasattr(attack, 'source_cluster') and attack.source_cluster:
                    combo = max(1, getattr(attack.source_cluster, 'combo_level', 1))
                # Build strike entries as WxH strings to match placement parser
                strike_details.append(f"{int(w)}x{int(h)}")
                pierce_budgets.append(combo)
                try:
                    total_strike_blocks += int(w) * int(h)
                except Exception:
                    pass

        if total_garbage > 0:
            self.queue_attack_spawn('enemy', 'garbage', total_garbage)
            self.attack_tracker.track_queued('enemy', 'garbage', total_garbage)

        if strike_details:
            self.queue_attack_spawn('enemy', 'strike', total_strike_blocks, strike_details)
            # Attach pierce budgets to the last queued attack
            if self.pending_attacks['enemy']:
                self.pending_attacks['enemy'][-1]['pierce_budgets'] = pierce_budgets
            self.attack_tracker.track_queued('enemy', 'strikes', len(strike_details))
            # Pause enemy spawn during strike placement
        self.enemy_spawn_pause_until = self._now_ms() + 1000
    
    def send_enemy_attacks_to_player(self, attacks=None):
        """Send enemy's pending attacks to player using unified spawning system.
        Aggregate multiple attacks into single payloads per type.
        If a list of attacks is provided, use it directly; otherwise pop from the manager.
        """
        if attacks is None:
            attacks = self.attack_manager.pop_attacks_for_player(target_player=1)
        if not attacks:
            return
        
        total_garbage = 0
        strike_details = []
        pierce_budgets = []

        for attack in attacks:
            a_type = getattr(attack, 'attack_type', None).value if getattr(attack, 'attack_type', None) else None
            if a_type == 'garbage_blocks':
                total_garbage += getattr(attack, 'block_count', 0)
            elif a_type == 'cluster_strike':
                w = getattr(attack, 'strike_width', 1)
                h = getattr(attack, 'strike_height', 1)
                combo = 1
                if hasattr(attack, 'source_cluster') and attack.source_cluster:
                    combo = max(1, getattr(attack.source_cluster, 'combo_level', 1))
                remaining = max(1, int(w))
                while remaining > 0:
                    seg_w = min(3, remaining)
                    strike_details.append(f"{seg_w}x{h}")
                    pierce_budgets.append(combo)
                    remaining -= seg_w

        if total_garbage > 0:
            self.queue_attack_spawn('player', 'garbage', total_garbage)
            self.attack_tracker.track_queued('player', 'garbage', total_garbage)

        if strike_details:
            total_strike_blocks = 0
            for d in strike_details:
                try:
                    w, h = map(int, d.split('x'))
                    total_strike_blocks += w * h
                except Exception:
                    pass
            self.queue_attack_spawn('player', 'strike', total_strike_blocks, strike_details)
            if self.pending_attacks['player']:
                self.pending_attacks['player'][-1]['pierce_budgets'] = pierce_budgets
            self.attack_tracker.track_queued('player', 'strikes', len(strike_details))
            # Pause player spawn during strike placement
        self.player_spawn_pause_until = self._now_ms() + 1000

    # OLD DIRECT PLACEMENT METHODS REMOVED - Now using unified spawning system

    def on_piece_landed(self, player):
        """Called when a piece lands - increment landing counters for nearby garbage blocks."""
        # First, drop any stale tracking that no longer matches the grid
        try:
            self._reconcile_garbage_tracking_with_grid()
        except Exception:
            pass
        # Only pause spawn if there are incoming attacks that are ready to apply now
        try:
            now = self._now_ms()
            pending_key = 'player' if player == 1 else 'enemy'
            pending_list = self.pending_attacks.get(pending_key, [])
            has_ready = bool(pending_list)
            # Only pause if end-of-turn conditions are already satisfied to apply immediately
            engine = self.player_engine if player == 1 else self.enemy_engine
            eligible_to_apply = (
                getattr(engine, 'main_piece', None) is None and
                not getattr(engine, 'chain_reaction_in_progress', False) and
                (not hasattr(engine, 'renderer') or not engine.renderer.animations_in_progress())
            )
            if has_ready and eligible_to_apply:
                pause_field = 'player_spawn_pause_until' if player == 1 else 'enemy_spawn_pause_until'
                setattr(self, pause_field, max(getattr(self, pause_field, 0), now + self.attack_receive_pause_ms))
        except Exception:
            pass

        # Get the engine for this player
        engine = self.player_engine if player == 1 else self.enemy_engine
        grid = engine.puzzle_grid
        
        # Reconcile any attack block movements under gravity to keep tracking keys in sync
        moved = getattr(engine, 'attack_block_movements', None)
        if moved:
            updated_brightness = {}
            for pos_key, data in list(self.garbage_block_brightness.items()):
                x, y, block_player = pos_key
                if block_player != player:
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
            if block_player == player:
                # Check if this tracked block is still in the grid
                if 0 <= y < len(grid) and 0 <= x < len(grid[0]) and grid[y][x] and (('_garbage' in grid[y][x]) or (grid[y][x] == 'garbage_block') or ('_strike' in grid[y][x])):
                    blocks_to_increment.append(pos_key)
        
        
        
        # Increment landing counters (only when actual piece landed, not mid-animation)
        for pos_key in blocks_to_increment:
            self.garbage_block_brightness[pos_key]['landings'] += 1
            
        
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
            if block_player != player:
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
                    old_block_type = grid[y][x]
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
                        # Clear any lingering falling overlay that might still draw neutral art
                        try:
                            if hasattr(self.player_renderer, 'animation_state_manager'):
                                self.player_renderer.animation_state_manager.visual_falling_blocks.pop((x, y), None)
                            if hasattr(self.enemy_renderer, 'animation_state_manager'):
                                self.enemy_renderer.animation_state_manager.visual_falling_blocks.pop((x, y), None)
                        except Exception:
                            pass

        # Apply colored garbage → normal
        if to_finalize_garbage:
            
            self.transform_garbage_blocks(to_finalize_garbage)
        
        # Use committer service to handle block transformations (alternative approach)
        player_key = 'player' if player == 1 else 'enemy'
        self.delivery_committer.update_received_blocks(engine, player_key)
        
        # Debug: Show all tracked blocks
        
    
    # place_cluster_strike method removed - cluster strike system disabled

    def transform_garbage_blocks(self, to_transform):
        """Transform garbage blocks to normal colored blocks."""
        for pos_key, new_block_type in to_transform:
            x, y, player = pos_key
            engine = self.player_engine if player == 1 else self.enemy_engine
            grid = engine.puzzle_grid
            
            # Transform the block
            if y < len(grid) and x < len(grid[0]):
                old_block_type = grid[y][x]
                grid[y][x] = new_block_type
                
                
                # Remove from tracking
                if pos_key in self.garbage_block_brightness:
                    del self.garbage_block_brightness[pos_key]

        # Ensure renderer sees the updated state and clear any falling visuals for those positions
        self.player_renderer.update_visual_state()
        self.enemy_renderer.update_visual_state()
        if hasattr(self.player_renderer, 'animation_state_manager'):
            for pos_key, _ in to_transform:
                x, y, player = pos_key
                if player == 1:
                    self.player_renderer.animation_state_manager.visual_falling_blocks.pop((x, y), None)
                else:
                    self.enemy_renderer.animation_state_manager.visual_falling_blocks.pop((x, y), None)

    def _reconcile_garbage_tracking_with_grid(self):
        """Remove tracking entries that no longer match grid (e.g., cleaned, overwritten, or moved)."""
        for player, engine in ((1, self.player_engine), (2, self.enemy_engine)):
            grid = engine.puzzle_grid
            invalid_keys = []
            for pos_key, data in self.garbage_block_brightness.items():
                x, y, block_player = pos_key
                if block_player != player:
                    continue
                # Out of bounds or cell changed to non-attack-type means drop tracking
                if not (0 <= y < len(grid) and 0 <= x < len(grid[0])):
                    invalid_keys.append(pos_key)
                    continue
                cell = grid[y][x]
                is_attack = isinstance(cell, str) and (('_garbage' in cell) or (cell == 'garbage_block') or ('_strike' in cell))
                if not is_attack:
                    invalid_keys.append(pos_key)
            for k in invalid_keys:
                self.garbage_block_brightness.pop(k, None)

    def _create_player_engine(self):
        """Creates a puzzle engine instance for the player."""
        engine = PuzzleEngine(self.screen, self.font, self.audio, self.asset_path)
        engine.renderer = PuzzleRenderer(engine)
        engine.renderer.preview_side = 'left'  # Player on the left
        return engine

    def _create_enemy_engine(self):
        """Creates a puzzle engine instance for the enemy."""
        engine = PuzzleEngine(self.screen, self.font, self.audio, self.asset_path)
        engine.renderer = PuzzleRenderer(engine)
        engine.renderer.preview_side = 'right'  # Enemy on the right
        return engine

    def draw(self):
        """Draws the test mode screen, including both puzzle grids."""
        # Draw background
        self.screen.fill((10, 10, 30))  # Dark blue background
        
        # Use stored dimensions from setup_board_positions
        cell_width = self.cell_width
        cell_height = self.cell_height
        border_size = 10
        board_width = self.board_width
        board_height = self.board_height
        
        # Draw player board container
        player_container = pygame.Rect(
            self.player_grid_position["x"] - border_size,
            self.player_grid_position["y"] - 35,
            board_width + (border_size * 2),
            board_height + 35 + border_size
        )
        pygame.draw.rect(self.screen, (30, 30, 60), player_container, border_radius=5)
        
        # Draw enemy board container
        enemy_container = pygame.Rect(
            self.enemy_grid_position["x"] - border_size,
            self.enemy_grid_position["y"] - 35,
            board_width + (border_size * 2),
            board_height + 35 + border_size
        )
        pygame.draw.rect(self.screen, (30, 30, 60), enemy_container, border_radius=5)
        
        # Draw puzzle backgrounds if available
        if self.puzzle_background:
            scaled_bg = pygame.transform.scale(self.puzzle_background, (board_width, board_height))
            
            # Player board background
            self.screen.blit(scaled_bg, (self.player_grid_position["x"], self.player_grid_position["y"]))
            
            # Enemy board background
            self.screen.blit(scaled_bg, (self.enemy_grid_position["x"], self.enemy_grid_position["y"]))
        
        # Update animations before drawing
        self.player_renderer.update_visual_state()
        self.player_renderer.update_animations()
        self.enemy_renderer.update_visual_state()
        self.enemy_renderer.update_animations()
        
        # Draw player grid and pieces using the new coordinated method
        self.player_renderer.draw_game_content()

        # Draw Player 2's (Enemy) grid using the new coordinated method
        self.enemy_renderer.draw_game_content()

        # Minimal test mode: no labels, controls text, database status, or attack HUD overlay



    def draw_pending_attack_indicators(self):
        """Draw visual indicators for pending attacks above the boards."""
        current_time = self._now_ms()
        
        # Draw indicators for player board (enemy attacks)
        if self.pending_attacks['player']:
            self.draw_attack_indicator(self.player_grid_position, self.pending_attacks['player'], current_time)
        
        # Draw indicators for enemy board (player attacks)
        if self.pending_attacks['enemy']:
            self.draw_attack_indicator(self.enemy_grid_position, self.pending_attacks['enemy'], current_time)
    
    def draw_attack_indicator(self, board_position, attacks, current_time):
        """Draw attack indicators above a specific board."""
        indicator_y = board_position["y"] - 20  # Above the board
        
        for i, attack in enumerate(attacks):
            # Calculate time until spawn
            time_until_spawn = max(0, self.attack_spawn_delay - (current_time - attack['spawn_time']))
            
            if time_until_spawn > 0:
                # Show countdown
                countdown_text = f"Attack in {time_until_spawn // 1000}s"
                color = (255, 255, 0) if time_until_spawn < 1000 else (255, 100, 100)  # Yellow then red
            else:
                # Show falling indicator
                countdown_text = f"Falling: {attack['blocks_remaining']} blocks"
                color = (100, 255, 100)  # Green
            
            # Draw the indicator
            indicator_font = pygame.font.SysFont(None, 16)
            indicator_surface = indicator_font.render(countdown_text, True, color)
            indicator_rect = indicator_surface.get_rect(
                center=(board_position["x"] + self.board_width // 2, indicator_y + i * 15)
            )
            self.screen.blit(indicator_surface, indicator_rect) 