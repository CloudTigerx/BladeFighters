"""
Unified Input Management System
==============================

Provides a single, robust input management system that consolidates
all game input handling into a unified interface with proper event routing,
key repeat management, and configuration integration.

Features:
- Single input manager for all game input
- Event routing with priority system
- Unified key repeat management (DAS/ARR)
- Input locking and gating
- Configuration integration
- Comprehensive event logging
- Hot-reload capability for input settings
"""

import pygame
import time
from collections import deque, defaultdict
from typing import Dict, List, Optional, Callable, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

from ..logging_module.error_handler import (
    safe_operation,
    safe_value_conversion,
    InputError
)
from ..logging_module.logger import get_logger
from ..settings_module.unified_config import UnifiedConfigManager, ConfigCategory

logger = get_logger(__name__)


class InputPriority(Enum):
    """Input event processing priorities."""
    CRITICAL = 0      # System events (quit, resize)
    HIGH = 1          # UI overlays (settings, tuner)
    NORMAL = 2        # Game input (movement, actions)
    LOW = 3           # Background systems (audio, etc.)


class InputAction(Enum):
    """Standard input actions."""
    # Movement actions
    MOVE_LEFT = "move_left"
    MOVE_RIGHT = "move_right"
    MOVE_UP = "move_up"
    MOVE_DOWN = "move_down"
    ROTATE_CW = "rotate_cw"
    ROTATE_CCW = "rotate_ccw"
    FLIP = "flip"
    DROP = "drop"
    SOFT_DROP = "soft_drop"
    
    # Game actions
    ACTION = "action"
    PAUSE = "pause"
    MENU_CONFIRM = "menu_confirm"
    MENU_CANCEL = "menu_cancel"
    MENU_TAB = "menu_tab"
    
    # Audio controls
    MUSIC_PAUSE = "music_pause"
    MUSIC_NEXT = "music_next"
    MUSIC_PREV = "music_prev"
    MUSIC_VOL_UP = "music_vol_up"
    MUSIC_VOL_DOWN = "music_vol_down"
    
    # System controls
    FULLSCREEN_TOGGLE = "fullscreen_toggle"
    SETTINGS_TOGGLE = "settings_toggle"
    INPUT_TUNER_TOGGLE = "input_tuner_toggle"
    
    # Test mode controls
    AI_DIFFICULTY_1 = "ai_difficulty_1"
    AI_DIFFICULTY_2 = "ai_difficulty_2"
    AI_DIFFICULTY_3 = "ai_difficulty_3"
    AI_DIFFICULTY_4 = "ai_difficulty_4"
    AI_DIFFICULTY_5 = "ai_difficulty_5"
    AI_DIFFICULTY_6 = "ai_difficulty_6"
    AI_DIFFICULTY_7 = "ai_difficulty_7"
    AI_DIFFICULTY_8 = "ai_difficulty_8"
    AI_DIFFICULTY_9 = "ai_difficulty_9"
    AI_DIFFICULTY_10 = "ai_difficulty_10"
    AI_DIFFICULTY_INC = "ai_difficulty_inc"
    AI_DIFFICULTY_DEC = "ai_difficulty_dec"


@dataclass
class InputEvent:
    """Represents a processed input event."""
    action: InputAction
    timestamp: int
    key_code: int
    is_pressed: bool
    is_repeat: bool = False
    data: Dict[str, Any] = field(default_factory=dict)


class UnifiedInputManager:
    """
    Unified input management system.
    
    Consolidates all game input handling into a single service with:
    - Event routing with priority system
    - Input locking and gating
    - Configuration integration
    - Comprehensive event logging
    """
    
    def __init__(self, config_manager: Optional[UnifiedConfigManager] = None, clock=None, state_manager=None):
        self.config_manager = config_manager or UnifiedConfigManager()
        self.clock = clock
        self.state_manager = state_manager
        
        # Event routing system
        self._event_handlers: Dict[InputPriority, List[Callable]] = defaultdict(list)
        self._action_handlers: Dict[InputAction, List[Callable]] = defaultdict(list)
        
        # Key tracking system
        self._keys_pressed: Dict[int, int] = {}  # key_code -> press_timestamp
        self._last_action_time: Dict[int, int] = {}  # key_code -> last_action_timestamp
        
        # Input locking system
        self._external_lock = False
        self._lock_until_ms = 0
        self._lock_reason = ""
        
        # Movement gating
        self._movement_gate_enabled = True
        self._movement_gate_callbacks: List[Callable] = []
        
        # Event logging
        self._event_log: deque = deque(maxlen=128)
        self._log_events = True
        
        # State update callbacks
        self._state_update_callbacks: List[Callable] = []
        
        # Register default event handlers
        self._register_default_handlers()
        
        # Initialize state manager if provided
        if self.state_manager:
            self._initialize_state_manager()
        
        logger.info("UnifiedInputManager initialized")
    
    def _initialize_state_manager(self):
        """Initialize state manager integration."""
        if not self.state_manager:
            return
        
        # Register state change callbacks for specific input fields
        self.state_manager.add_change_callback("input.input_locked", self._on_state_change, "Input lock state change callback")
        
        # Initialize input state
        self._update_state_manager()
        
        logger.info("State manager integration initialized")
    
    def register_state_update_callback(self, callback: Callable[[dict], None]):
        """Register a callback for state updates."""
        self._state_update_callbacks.append(callback)
        logger.debug(f"Registered state update callback: {callback.__name__}")
    
    def _update_state_manager(self):
        """Update state manager with current input state."""
        if not self.state_manager:
            return
        
        try:
            # Update keys pressed
            self.state_manager.set("input.keys_pressed", set(self._keys_pressed.keys()), 
                                 source="input_manager", description="Update pressed keys")
            
            # Update input timing
            current_time = int(self.clock.now_ms()) if self.clock else int(time.time() * 1000)
            self.state_manager.set("input.last_input_time", current_time / 1000.0, 
                                 source="input_manager", description="Update last input time")
            
            # Update input locking
            self.state_manager.set("input.input_locked", self._external_lock, 
                                 source="input_manager", description="Update input lock state")
            self.state_manager.set("input.input_lock_reason", self._lock_reason, 
                                 source="input_manager", description="Update input lock reason")
            
        except Exception as e:
            logger.error(f"Error updating state manager: {e}")
    
    def _on_state_change(self, field_path: str, old_value: any, new_value: any):
        """Handle state changes from state manager."""
        try:
            if field_path == "input.input_locked":
                if new_value and not self._external_lock:
                    # Lock input through state manager
                    self.lock_input(1000, "state_manager_lock")
                elif not new_value and self._external_lock:
                    # Unlock input through state manager
                    self.unlock_input()
                
        except Exception as e:
            logger.error(f"Error handling state change {field_path}: {e}")
    
    def _register_default_handlers(self):
        """Register default event handlers for system events."""
        # Register system event handlers
        self.register_event_handler(InputPriority.CRITICAL, self._handle_system_events)
        self.register_event_handler(InputPriority.NORMAL, self._handle_game_events)
    
    def register_event_handler(self, priority: InputPriority, handler: Callable):
        """Register an event handler with a specific priority."""
        self._event_handlers[priority].append(handler)
        logger.debug(f"Registered event handler with priority {priority.name}")
    
    def register_action_handler(self, action: InputAction, handler: Callable):
        """Register a handler for a specific input action."""
        self._action_handlers[action].append(handler)
        logger.debug(f"Registered action handler for {action.value}")
    
    def unregister_event_handler(self, priority: InputPriority, handler: Callable):
        """Unregister an event handler."""
        if handler in self._event_handlers[priority]:
            self._event_handlers[priority].remove(handler)
            logger.debug(f"Unregistered event handler with priority {priority.name}")
    
    def unregister_action_handler(self, action: InputAction, handler: Callable):
        """Unregister an action handler."""
        if handler in self._action_handlers[action]:
            self._action_handlers[action].remove(handler)
            logger.debug(f"Unregistered action handler for {action.value}")
    
    def process_events(self, events: List[pygame.event.Event]) -> List[InputEvent]:
        """
        Process pygame events and return processed input events.
        
        Args:
            events: List of pygame events to process
            
        Returns:
            List of processed InputEvent objects
        """
        processed_events = []
        current_time = int(self.clock.now_ms()) if self.clock else int(time.time() * 1000)
        
        # Check if input is locked
        if self._is_input_locked(current_time):
            return processed_events
        
        # Process events by priority
        for priority in sorted(InputPriority, key=lambda p: p.value):
            for handler in self._event_handlers[priority]:
                try:
                    result = handler(events, current_time)
                    if result:
                        if isinstance(result, InputEvent):
                            processed_events.append(result)
                        elif isinstance(result, list):
                            processed_events.extend(result)
                except Exception as e:
                    logger.error(f"Error in event handler {handler.__name__}: {e}")
        
        # Log events if enabled
        if self._log_events:
            self._log_input_events(processed_events)
        
        return processed_events
    
    def _handle_system_events(self, events: List[pygame.event.Event], current_time: int) -> List[InputEvent]:
        """Handle critical system events."""
        system_events = []
        
        for event in events:
            if event.type == pygame.QUIT:
                # System quit event
                system_events.append(InputEvent(
                    action=InputAction.MENU_CANCEL,  # Use cancel as quit action
                    timestamp=current_time,
                    key_code=pygame.K_ESCAPE,
                    is_pressed=True,
                    data={"system_quit": True}
                ))
            elif event.type == pygame.VIDEORESIZE:
                # Window resize event
                system_events.append(InputEvent(
                    action=InputAction.MENU_CONFIRM,  # Use confirm as resize action
                    timestamp=current_time,
                    key_code=0,
                    is_pressed=True,
                    data={"resize": (event.w, event.h)}
                ))
        
        return system_events
    
    def _handle_game_events(self, events: List[pygame.event.Event], current_time: int) -> List[InputEvent]:
        """Handle game input events."""
        game_events = []
        
        for event in events:
            if event.type == pygame.KEYDOWN:
                input_event = self._process_keydown(event, current_time)
                if input_event:
                    game_events.append(input_event)
            elif event.type == pygame.KEYUP:
                input_event = self._process_keyup(event, current_time)
                if input_event:
                    game_events.append(input_event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                input_event = self._process_mouse_click(event, current_time)
                if input_event:
                    game_events.append(input_event)
        
        return game_events
    
    def _process_keydown(self, event: pygame.event.Event, current_time: int) -> Optional[InputEvent]:
        """Process a keydown event."""
        key_code = event.key
        
        # Track key press
        self._keys_pressed[key_code] = current_time
        
        # Update state manager
        self._update_state_manager()
        
        # Map key to action
        action = self._map_key_to_action(key_code)
        if not action:
            return None
        
        # Create input event
        input_event = InputEvent(
            action=action,
            timestamp=current_time,
            key_code=key_code,
            is_pressed=True,
            is_repeat=False
        )
        
        # Call action handlers
        self._call_action_handlers(input_event)
        
        return input_event
    
    def _process_keyup(self, event: pygame.event.Event, current_time: int) -> Optional[InputEvent]:
        """Process a keyup event."""
        key_code = event.key
        
        # Remove from pressed keys
        if key_code in self._keys_pressed:
            del self._keys_pressed[key_code]
        
        if key_code in self._last_action_time:
            del self._last_action_time[key_code]
        
        # Update state manager
        self._update_state_manager()
        
        # Map key to action
        action = self._map_key_to_action(key_code)
        if not action:
            return None
        
        # Create input event
        input_event = InputEvent(
            action=action,
            timestamp=current_time,
            key_code=key_code,
            is_pressed=False,
            is_repeat=False
        )
        
        # Call action handlers
        self._call_action_handlers(input_event)
        
        return input_event
    
    def _process_mouse_click(self, event: pygame.event.Event, current_time: int) -> Optional[InputEvent]:
        """Process a mouse click event."""
        if event.button != 1:  # Only handle left clicks
            return None
        
        # Create input event for mouse click
        input_event = InputEvent(
            action=InputAction.ACTION,  # Use action for mouse clicks
            timestamp=current_time,
            key_code=0,
            is_pressed=True,
            is_repeat=False,
            data={"mouse_pos": event.pos, "mouse_button": event.button}
        )
        
        # Call action handlers
        self._call_action_handlers(input_event)
        
        return input_event
    
    def _map_key_to_action(self, key_code: int) -> Optional[InputAction]:
        """Map a key code to an input action."""
        # Get key bindings from configuration
        key_bindings = self._get_key_bindings()
        
        # Reverse lookup: key_code -> action
        for action_name, bound_key in key_bindings.items():
            if bound_key == key_code:
                try:
                    return InputAction(action_name)
                except ValueError:
                    continue
        
        # Fallback to hardcoded mappings
        fallback_mappings = {
            pygame.K_LEFT: InputAction.MOVE_LEFT,
            pygame.K_RIGHT: InputAction.MOVE_RIGHT,
            pygame.K_UP: InputAction.MOVE_UP,      # Rotates counter-clockwise
            pygame.K_DOWN: InputAction.MOVE_DOWN,  # Rotates clockwise
            pygame.K_SPACE: InputAction.ACTION,
            pygame.K_ESCAPE: InputAction.MENU_CANCEL,
            pygame.K_RETURN: InputAction.MENU_CONFIRM,
            pygame.K_TAB: InputAction.MENU_TAB,
            pygame.K_p: InputAction.MUSIC_PAUSE,
            pygame.K_RIGHTBRACKET: InputAction.MUSIC_NEXT,
            pygame.K_LEFTBRACKET: InputAction.MUSIC_PREV,
            pygame.K_EQUALS: InputAction.MUSIC_VOL_UP,
            pygame.K_MINUS: InputAction.MUSIC_VOL_DOWN,
            pygame.K_F11: InputAction.FULLSCREEN_TOGGLE,
            pygame.K_F1: InputAction.SETTINGS_TOGGLE,
            # pygame.K_F9: InputAction.INPUT_TUNER_TOGGLE,  # Disabled for now
        }
        
        return fallback_mappings.get(key_code)
    
    def _get_key_bindings(self) -> Dict[str, int]:
        """Get key bindings from configuration."""
        try:
            # Get all input-related settings
            input_config = self.config_manager.get_category(ConfigCategory.INPUT)
            
            # Extract key bindings
            key_bindings = {}
            for key, value in input_config.items():
                if key in ["move_up", "move_down", "move_left", "move_right", "action", 
                          "menu_cancel", "menu_confirm", "menu_tab", "music_pause", 
                          "music_next", "music_prev", "fullscreen_toggle"]:
                    key_bindings[key] = value
            
            return key_bindings
        except Exception as e:
            logger.warning(f"Failed to get key bindings: {e}")
            return {}
    
    def _handle_continuous_keys(self, current_time: int):
        """Handle continuous key presses for key repeat."""
        # DAS/ARR functionality removed - no automatic key repeat
        pass
    
    def _get_repeat_interval(self, action: InputAction) -> int:
        """Get the repeat interval for a specific action."""
        # DAS/ARR functionality removed - no automatic key repeat
        return 0
    
    def _get_key_code_for_action(self, action: InputAction) -> Optional[int]:
        """Get the key code for a specific action."""
        key_bindings = self._get_key_bindings()
        return key_bindings.get(action.value)
    
    def _call_action_handlers(self, input_event: InputEvent):
        """Call all registered handlers for an input action."""
        for handler in self._action_handlers[input_event.action]:
            try:
                handler(input_event)
            except Exception as e:
                logger.error(f"Error in action handler {handler.__name__}: {e}")
    
    def _is_input_locked(self, current_time: int) -> bool:
        """Check if input is currently locked."""
        if self._external_lock and current_time < self._lock_until_ms:
            return True
        return False
    
    def lock_input(self, duration_ms: int, reason: str = ""):
        """Lock input for a specified duration."""
        current_time = int(self.clock.now_ms()) if self.clock else int(time.time() * 1000)
        self._external_lock = True
        self._lock_until_ms = current_time + duration_ms
        self._lock_reason = reason
        
        # Update state manager
        self._update_state_manager()
        
        logger.debug(f"Input locked for {duration_ms}ms: {reason}")
    
    def unlock_input(self):
        """Unlock input immediately."""
        self._external_lock = False
        self._lock_until_ms = 0
        self._lock_reason = ""
        
        # Update state manager
        self._update_state_manager()
        
        logger.debug("Input unlocked")
    
    def set_movement_gate(self, enabled: bool):
        """Enable or disable the movement gate."""
        old_state = self._movement_gate_enabled
        self._movement_gate_enabled = enabled
        
        if old_state != enabled:
            logger.debug(f"Movement gate {'enabled' if enabled else 'disabled'}")
            
            # Call movement gate callbacks
            for callback in self._movement_gate_callbacks:
                try:
                    callback(enabled)
                except Exception as e:
                    logger.error(f"Error in movement gate callback: {e}")
    
    def register_movement_gate_callback(self, callback: Callable[[bool], None]):
        """Register a callback for movement gate changes."""
        self._movement_gate_callbacks.append(callback)
    
    def get_pressed_keys(self) -> Dict[int, int]:
        """Get currently pressed keys with their press timestamps."""
        return self._keys_pressed.copy()
    
    def is_key_pressed(self, key_code: int) -> bool:
        """Check if a specific key is currently pressed."""
        return key_code in self._keys_pressed
    
    def clear_key(self, key_code: int):
        """Clear a specific key from the pressed keys."""
        if key_code in self._keys_pressed:
            del self._keys_pressed[key_code]
        if key_code in self._last_action_time:
            del self._last_action_time[key_code]
    
    def clear_all_keys(self):
        """Clear all pressed keys."""
        self._keys_pressed.clear()
        self._last_action_time.clear()
    
    def reload_config(self):
        """Reload input configuration from the config manager."""
        logger.info("Input configuration reloaded")
    
    def _log_input_events(self, events: List[InputEvent]):
        """Log input events for debugging."""
        for event in events:
            self._event_log.append({
                "action": event.action.value,
                "timestamp": event.timestamp,
                "key_code": event.key_code,
                "is_pressed": event.is_pressed,
                "is_repeat": event.is_repeat,
                "data": event.data
            })
    
    def get_event_log(self, limit: int = 10) -> List[Dict]:
        """Get recent input events for debugging."""
        return list(self._event_log)[-limit:]
    
    def clear_event_log(self):
        """Clear the input event log."""
        self._event_log.clear()
    
    def set_event_logging(self, enabled: bool):
        """Enable or disable event logging."""
        self._log_events = enabled
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the input manager."""
        current_time = int(self.clock.now_ms()) if self.clock else int(time.time() * 1000)
        
        return {
            "pressed_keys_count": len(self._keys_pressed),
            "external_lock": self._external_lock,
            "lock_until_ms": self._lock_until_ms,
            "lock_reason": self._lock_reason,
            "movement_gate_enabled": self._movement_gate_enabled,
            "event_logging_enabled": self._log_events,
            "event_log_size": len(self._event_log),
            "repeat_config": {
                "das_ms": 0, # No DAS/ARR, so no config
                "arr_ms": 0, # No DAS/ARR, so no config
                "rotate_repeat_ms": 0, # No DAS/ARR, so no config
                "tap_grace_ms": 0 # No DAS/ARR, so no config
            },
            "is_input_locked": self._is_input_locked(current_time)
        } 