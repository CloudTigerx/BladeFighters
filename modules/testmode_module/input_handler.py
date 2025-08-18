"""
Unified Input Handler for TestMode
==================================

Uses the new unified input management system for TestMode input handling.
"""

import pygame
from typing import List, Optional
from modules.ai_module import config_for_difficulty
from ..logging_module.error_handler import (
    safe_operation,
    InputError
)
from ..logging_module.logger import get_logger
from ..input_module import UnifiedInputManager, InputAction, InputEvent

logger = get_logger(__name__)


class InputHandler:
    """
    Manages input event processing and controls for TestMode using the unified input system.
    Handles keyboard events, AI difficulty controls, and input locks.
    """
    
    def __init__(self, ai_manager, game_state_manager, config_manager=None, clock=None):
        """Initialize the input handler."""
        self.ai_manager = ai_manager
        self.game_state_manager = game_state_manager
        
        # Create unified input manager
        self.unified_input = UnifiedInputManager(config_manager, clock)
        
        # Register test mode specific action handlers
        self._register_test_mode_handlers()
        
        logger.info("TestMode InputHandler initialized with unified input system")
    
    def _register_test_mode_handlers(self):
        """Register action handlers for test mode specific functionality."""
        # AI difficulty controls
        self.unified_input.register_action_handler(InputAction.AI_DIFFICULTY_1, lambda e: self._set_ai_difficulty(1))
        self.unified_input.register_action_handler(InputAction.AI_DIFFICULTY_2, lambda e: self._set_ai_difficulty(2))
        self.unified_input.register_action_handler(InputAction.AI_DIFFICULTY_3, lambda e: self._set_ai_difficulty(3))
        self.unified_input.register_action_handler(InputAction.AI_DIFFICULTY_4, lambda e: self._set_ai_difficulty(4))
        self.unified_input.register_action_handler(InputAction.AI_DIFFICULTY_5, lambda e: self._set_ai_difficulty(5))
        self.unified_input.register_action_handler(InputAction.AI_DIFFICULTY_6, lambda e: self._set_ai_difficulty(6))
        self.unified_input.register_action_handler(InputAction.AI_DIFFICULTY_7, lambda e: self._set_ai_difficulty(7))
        self.unified_input.register_action_handler(InputAction.AI_DIFFICULTY_8, lambda e: self._set_ai_difficulty(8))
        self.unified_input.register_action_handler(InputAction.AI_DIFFICULTY_9, lambda e: self._set_ai_difficulty(9))
        self.unified_input.register_action_handler(InputAction.AI_DIFFICULTY_10, lambda e: self._set_ai_difficulty(10))
        self.unified_input.register_action_handler(InputAction.AI_DIFFICULTY_INC, lambda e: self._adjust_ai_difficulty(1))
        self.unified_input.register_action_handler(InputAction.AI_DIFFICULTY_DEC, lambda e: self._adjust_ai_difficulty(-1))
    
    def _set_ai_difficulty(self, level: int):
        """Set AI difficulty to a specific level."""
        try:
            self.ai_manager.set_difficulty(level)
            logger.info(f"AI difficulty set to: {level}")
        except Exception as e:
            logger.error(f"Failed to set AI difficulty: {e}")
    
    def _adjust_ai_difficulty(self, delta: int):
        """Adjust AI difficulty by a delta."""
        try:
            self.ai_manager.adjust_difficulty(delta)
            logger.info(f"AI difficulty adjusted to: {self.ai_manager.get_difficulty()}")
        except Exception as e:
            logger.error(f"Failed to adjust AI difficulty: {e}")
        
    def process_events(self, events: List, player_engine, current_time: int) -> Optional[str]:
        """Process input events for the test mode."""
        # Let the player engine handle its own events first
        player_engine.process_events(events)
        
        # Apply input locks to player's input handler before engine updates
        self._apply_input_locks(player_engine, current_time)
        
        # Process events through unified input manager
        processed_events = self.unified_input.process_events(events)
        
        # Check for menu actions
        for event in processed_events:
            if event.action == InputAction.MENU_CANCEL and event.is_pressed:
                return "back_to_menu"
                    
        return None
        
    @safe_operation("apply input locks", None, "WARNING")
    def _apply_input_locks(self, player_engine, current_time: int):
        """Apply input locks to player's input handler."""
        is_locked = self.game_state_manager.is_player_input_locked(current_time)
        player_engine.input_handler.apply_external_lock(is_locked)
        
    @safe_operation("handle chain lock", None, "WARNING")
    def handle_chain_lock(self, player_engine, current_time: int):
        """Handle chain reaction input locking."""
        # Chain lock if player's chain is active (best-effort hook)
        if getattr(player_engine, 'chain_reaction_in_progress', False):
            freeze_ms = self._get_attack_freeze_ms()
            # Use lock_player_input instead of lock_player_chain (which doesn't exist)
            self.game_state_manager.lock_player_input(freeze_ms, current_time)
            
    @safe_operation("handle attack lock", None, "WARNING")
    def handle_attack_lock(self, attack_result, current_time: int):
        """Handle input locking due to received attacks."""
        # If payloads were applied to the player, lock player input briefly
        if (isinstance(attack_result, dict) and 
            int(attack_result.get("payload_count", 0)) > 0 and 
            int(attack_result.get("applied_to_board_id", 0)) == 1):
            freeze_ms = self._get_attack_freeze_ms()
            self.game_state_manager.lock_player_input(freeze_ms, current_time)
            
    @safe_operation("get attack freeze duration", 150, "WARNING")
    def _get_attack_freeze_ms(self) -> int:
        """Get the attack freeze duration in milliseconds."""
        # Resolve from settings service if available; otherwise default
        # This would need to be passed in from the main TestMode
        # For now, return default value
        return 150 