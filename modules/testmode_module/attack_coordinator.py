"""
Attack Coordinator - Handles attack delivery and flow management
Extracted from TestMode to manage attack system coordination.
"""

import pygame
from typing import Dict, List, Optional, Any
from modules.attack_module import AttackManager
from modules.attack_module.attacks_service import AttacksService
from modules.attack_module.column_rotator import ColumnRotator
from .attack_flow_tracker import AttackFlowTracker
from .attack_flow_manager import AttackFlowManager, AttackFlowConfig

class AttackCoordinator:
    """
    Manages attack delivery, spawning, and flow coordination.
    Handles attack system integration between boards.
    """
    
    def __init__(self, clock=None, settings_system=None, item_system=None):
        """Initialize the attack coordinator."""
        self.clock = clock
        self.settings_system = settings_system
        
        # Initialize attack manager (centralized system) and facade service
        self.attack_manager = AttackManager()
        self.attacks_service = AttacksService(
            clock=self.clock
        )
        
        # Database indicator for UI (AttackManager uses internal calculator; keep flag for UI)
        self.database_enabled = False
        
        # Initialize persistent column rotators for each player
        self.player_column_rotator = ColumnRotator(grid_width=6)
        self.enemy_column_rotator = ColumnRotator(grid_width=6)
        
        # Initialize attack flow tracker for clean debug output
        self.attack_tracker = AttackFlowTracker(clock=self.clock)
        
        # Attack flow manager
        self.attack_flow_manager = None
        
        # Pause window to receive attacks cleanly at end of turn (ms)
        self.attack_receive_pause_ms = 400
        
        # Initialize attack flow manager
        self._initialize_attack_flow_manager()
        
    def _initialize_attack_flow_manager(self):
        """Initialize the attack flow manager."""
        config = AttackFlowConfig(
            chain_window_duration=302,
            attack_receive_pause_ms=400,
            max_chain_length=10
        )
        self.attack_flow_manager = AttackFlowManager(config, self.attacks_service)
        
    def set_blocks_broken_handlers(self, player_engine, enemy_engine):
        """Set up blocks broken handlers for both engines."""
        # Connect attack system handlers for BOTH players via facade
        player_engine.blocks_broken_handler = lambda broken_blocks, is_cluster, combo_multiplier: self.attacks_service.on_combo(broken_blocks, is_cluster, combo_multiplier, player_id=1)
        enemy_engine.blocks_broken_handler = lambda broken_blocks, is_cluster, combo_multiplier: self.attacks_service.on_combo(broken_blocks, is_cluster, combo_multiplier, player_id=2)
        
        # Mark engines for side mapping
        setattr(player_engine, 'is_player_board', True)
        setattr(enemy_engine, 'is_player_board', False)
        
    def set_test_mode_reference(self, test_mode, player_engine, enemy_engine):
        """Set test mode reference on engines for attack spawning."""
        setattr(player_engine, 'test_mode', test_mode)
        setattr(enemy_engine, 'test_mode', test_mode)
        
    def deliver_attacks(self, player_engine, enemy_engine, player_renderer, enemy_renderer):
        """Deliver any ready attacks via facade."""
        res_player = self.attacks_service.deliver(board=player_engine, renderer=player_renderer)
        res_enemy = self.attacks_service.deliver(board=enemy_engine, renderer=enemy_renderer)
        return res_player, res_enemy
        
    def update_attack_spawning(self):
        """Update attack spawning system and deliver attacks."""
        current_time = self._now_ms()
        
        # Advance time and process attack queue to make attacks ready
        now_sec = current_time / 1000.0
        update_result = self.attack_manager.update(now_sec)
        ready_attacks = update_result.get('ready_attacks', {})
        
        # Deliver attacks from attack_manager to boards
        if hasattr(self, 'player_engine') and hasattr(self, 'enemy_engine'):
            self.attacks_service.deliver_with_ready_attacks(board=self.player_engine, renderer=getattr(self, 'player_renderer', None), ready_attacks=ready_attacks)
            self.attacks_service.deliver_with_ready_attacks(board=self.enemy_engine, renderer=getattr(self, 'enemy_renderer', None), ready_attacks=ready_attacks)
            
    def reset_attack_queues(self):
        """Reset attack queues."""
        if hasattr(self, 'attack_manager'):
            self.attack_manager.clear_attack_queues()
            
    def print_attack_summary(self):
        """Print attack flow summary if needed."""
        if self.attack_tracker.should_print_summary():
            self.attack_tracker.print_summary()
            
    def get_attack_manager(self) -> AttackManager:
        """Get the attack manager."""
        return self.attack_manager
        
    def get_attacks_service(self) -> AttacksService:
        """Get the attacks service."""
        return self.attacks_service
        
    def get_attack_flow_manager(self) -> AttackFlowManager:
        """Get the attack flow manager."""
        return self.attack_flow_manager
        
    def _now_ms(self) -> int:
        """Get current time in milliseconds."""
        if self.clock:
            return self.clock.now_ms()
        return pygame.time.get_ticks() 