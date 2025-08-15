"""
Game State Manager - Handles game initialization and reset logic
Extracted from TestMode to manage game state lifecycle.
"""

import json
import os
import pygame
from typing import Dict, Any, Optional
from ..items_module.item_system import ItemSystem
from ..logging_module.error_handler import (
    safe_file_operation,
    safe_operation,
    GameStateError
)
from ..logging_module.logger import get_logger

logger = get_logger(__name__)


class GameStateManager:
    def __init__(self, clock=None):
        self.clock = clock
        self.player_items = ItemSystem()
        self.enemy_items = ItemSystem()
        self.player_runtime = None
        self.enemy_runtime = None
        
        # Chain state tracking
        self.player_chain_position = 0
        self.enemy_chain_position = 0
        self.player_chain_active = False
        self.enemy_chain_active = False
        self.last_player_combo_time = 0
        self.last_enemy_combo_time = 0
        
        # Feature flags
        self.flags = {
            "enable_chain_reactions": True,
            "enable_attack_animations": True,
            "enable_particle_effects": True,
            "enable_sound_effects": True,
            "enable_debug_overlay": False,
        }
        
        # Load item configuration
        self._load_item_config()

    @safe_file_operation("load item configuration", "items_config.json", {})
    def _load_item_config_file(self) -> Dict[str, Any]:
        """Load item configuration from file with proper error handling."""
        config_path = "puzzleassets/items_config.json"
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _load_item_config(self):
        """Load item configuration with error handling."""
        try:
            items_cfg = self._load_item_config_file()
            
            if not items_cfg:
                logger.warning("No item configuration found, using defaults")
                return
            
            # Load weapons
            from modules.items_module.catalog import create_weapon_by_name
            
            p_name = items_cfg.get('player_weapon', 'Rusted Sword')
            e_name = items_cfg.get('enemy_weapon', 'Rusted Sword')
            p_w = create_weapon_by_name(p_name) or create_weapon_by_name('Rusted Sword')
            e_w = create_weapon_by_name(e_name) or create_weapon_by_name('Rusted Sword')
            
            if p_w:
                self.player_items.equip_weapon(p_w)
            if e_w:
                self.enemy_items.equip_weapon(e_w)
                
            # Load ownership
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
                except Exception as e:
                    logger.warning(f"Failed to load curated weapons: {str(e)}")
                    
            self.player_items.set_owned_weapons(p_owned)
            self.enemy_items.set_owned_weapons(e_owned)
            
            logger.info("Item configuration loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading item config: {str(e)}")
            
    def reset_chain_states(self):
        """Reset all chain-related states."""
        self.player_chain_position = 0
        self.enemy_chain_position = 0
        self.player_chain_active = False
        self.enemy_chain_active = False
        self.last_player_combo_time = 0
        self.last_enemy_combo_time = 0
        
    @safe_operation("reset runtime locks", None, "WARNING")
    def reset_runtime_locks(self, current_time: int):
        """Reset runtime locks for both boards."""
        if self.player_runtime:
            self.player_runtime.clear_expired(current_time)
        if self.enemy_runtime:
            self.enemy_runtime.clear_expired(current_time)
            
    @safe_operation("lock player chain", None, "WARNING")
    def lock_player_chain(self, freeze_ms: int, current_time: int):
        """Lock player input due to chain reaction."""
        if self.player_runtime:
            self.player_runtime.lock_chain(freeze_ms, current_time)
            
    @safe_operation("lock player input", None, "WARNING")
    def lock_player_input(self, freeze_ms: int, current_time: int):
        """Lock player input due to attack received."""
        if self.player_runtime:
            self.player_runtime.lock_input(freeze_ms, current_time)
            
    @safe_operation("check player input lock", False, "WARNING")
    def is_player_input_locked(self, current_time: int) -> bool:
        """Check if player input is currently locked."""
        if self.player_runtime:
            return self.player_runtime.is_input_locked(current_time)
        return False
        
    def get_flags(self) -> Dict[str, Any]:
        """Get the feature flags."""
        return self.flags.copy()
        
    def set_flag(self, flag_name: str, value: Any):
        """Set a feature flag."""
        if flag_name in self.flags:
            self.flags[flag_name] = value
            logger.debug(f"Set flag {flag_name} = {value}")
        else:
            logger.warning(f"Unknown flag: {flag_name}")
            
    def get_player_items(self) -> ItemSystem:
        """Get the player item system."""
        return self.player_items
        
    def get_enemy_items(self) -> ItemSystem:
        """Get the enemy item system."""
        return self.enemy_items
        
    def get_player_runtime(self):
        """Get the player board runtime."""
        return self.player_runtime
        
    def get_enemy_runtime(self):
        """Get the enemy board runtime."""
        return self.enemy_runtime
        
    def _now_ms(self) -> int:
        """Get current time in milliseconds."""
        if self.clock:
            return self.clock.now_ms()
        import pygame
        return pygame.time.get_ticks() 