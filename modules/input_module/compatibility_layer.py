"""
Input System Compatibility Layer
===============================

Provides backward compatibility for existing code that uses the old InputHandler
interface while using the new UnifiedInputManager underneath.

This allows for a gradual migration to the new input system without breaking
existing code.
"""

import pygame
import time
from typing import List, Optional, Dict, Any
from collections import deque

from .unified_input_manager import UnifiedInputManager, InputAction, InputEvent
from ..logging_module.logger import get_logger
from ..settings_module.unified_config import UnifiedConfigManager

logger = get_logger(__name__)


class InputHandlerCompat:
    """
    Compatibility wrapper for the old InputHandler interface.
    
    This class provides the same interface as the original InputHandler
    but uses the new UnifiedInputManager underneath.
    """
    
    def __init__(self, puzzle_engine, settings_ui=None, state_manager=None, clock=None):
        """
        Initialize the compatibility input handler.
        
        Args:
            puzzle_engine: Reference to the puzzle engine for calling game methods
            settings_ui: Reference to settings UI for custom controls
            state_manager: Optional state manager for state integration
            clock: Optional clock instance for time management
        """
        self.engine = puzzle_engine
        self.settings_ui = settings_ui
        self.state_manager = state_manager
        
        # Get clock from parameter, engine, or create default
        self.clock = clock or getattr(self.engine, 'clock', None)
        
        # Create unified input manager with state manager
        config_manager = UnifiedConfigManager()
        self.unified_input = UnifiedInputManager(config_manager, self.clock, state_manager)
        
        # Legacy attributes for compatibility
        self.keys_pressed = {}  # Legacy key tracking
        self.last_key_action_time = {}
        self.key_press_time = {}
        self._external_lock = False
        
        # Movement gate
        self.is_falling = True
        
        # Debug flag
        self.debug_spacebar = False
        
        # Diagnostics
        self._diag_events = deque(maxlen=64)
        self._last_diag_ts = None
        self._intents = []
        
        # Rotation state management to prevent race conditions
        self._last_rotation_time = 0
        self._rotation_cooldown_ms = 50  # Minimum time between rotations
        
        # Register movement gate callback
        self.unified_input.register_movement_gate_callback(self._on_movement_gate_change)
        
        # Register action handlers for engine integration
        self._register_engine_handlers()
        
        logger.info("InputHandlerCompat initialized with unified input manager")
    
    def _load_config(self):
        """Load configuration from settings UI or unified config."""
        try:
            # Try to load from settings UI first (legacy path)
            if self.settings_ui and hasattr(self.settings_ui, 'config'):
                cfg = self.settings_ui.config
                # self.key_repeat_delay = int(cfg.get('repeat_initial_delay_ms', self.key_repeat_delay)) # Removed DAS/ARR fields
                # self.key_repeat_interval = int(cfg.get('repeat_interval_ms', self.key_repeat_interval))
                # self.arrow_repeat_interval = int(cfg.get('repeat_move_interval_ms', self.arrow_repeat_interval))
                # self.rotate_repeat_interval = int(cfg.get('repeat_rotate_interval_ms', self.rotate_repeat_interval))
                
                # Map to new fields
                # self.movement_das_ms = self.key_repeat_delay # Removed DAS/ARR fields
                # self.movement_arr_ms = self.arrow_repeat_interval # Removed DAS/ARR fields
                # self.movement_rotate_repeat_ms = self.rotate_repeat_interval # Removed DAS/ARR fields
                # self.movement_tap_grace_ms = int(cfg.get('tap_grace_ms', self.movement_tap_grace_ms)) # Removed DAS/ARR fields
            
            # Update unified input manager with these values
            # self.unified_input.config_manager.set("repeat_initial_delay_ms", self.movement_das_ms) # Removed DAS/ARR fields
            # self.unified_input.config_manager.set("repeat_interval_ms", self.movement_arr_ms) # Removed DAS/ARR fields
            # self.unified_input.config_manager.set("repeat_rotate_interval_ms", self.movement_rotate_repeat_ms) # Removed DAS/ARR fields
            # self.unified_input.config_manager.set("tap_grace_ms", self.movement_tap_grace_ms) # Removed DAS/ARR fields
            
            logger.debug("Configuration loaded successfully")
        except Exception as e:
            logger.warning(f"Failed to load configuration: {e}")
    
    def _register_engine_handlers(self):
        """Register action handlers that call engine methods."""
        # Movement actions
        self.unified_input.register_action_handler(InputAction.MOVE_LEFT, self._handle_move_left)
        self.unified_input.register_action_handler(InputAction.MOVE_RIGHT, self._handle_move_right)
        self.unified_input.register_action_handler(InputAction.MOVE_UP, self._handle_move_up)
        self.unified_input.register_action_handler(InputAction.MOVE_DOWN, self._handle_move_down)
        self.unified_input.register_action_handler(InputAction.ROTATE_CW, self._handle_rotate_cw)
        self.unified_input.register_action_handler(InputAction.ROTATE_CCW, self._handle_rotate_ccw)
        self.unified_input.register_action_handler(InputAction.FLIP, self._handle_flip)
        self.unified_input.register_action_handler(InputAction.DROP, self._handle_drop)
        self.unified_input.register_action_handler(InputAction.ACTION, self._handle_action)
    
    def _handle_move_left(self, event: InputEvent):
        """Handle left movement."""
        if event.is_pressed and self.is_falling:
            self.engine.move_piece(-1, 0)
            self._log_diag('move', pygame.K_LEFT, event.timestamp)
    
    def _handle_move_right(self, event: InputEvent):
        """Handle right movement."""
        if event.is_pressed and self.is_falling:
            self.engine.move_piece(1, 0)
            self._log_diag('move', pygame.K_RIGHT, event.timestamp)
    
    def _handle_move_up(self, event: InputEvent):
        """Handle up arrow - rotate pieces counter-clockwise."""
        if event.is_pressed and self.is_falling:
            current_time = self._now_ms()
            if current_time - self._last_rotation_time >= self._rotation_cooldown_ms:
                self.engine.rotate_attached_piece(-1)  # Counter-clockwise
                self._last_rotation_time = current_time
                self._log_diag('rotate', pygame.K_UP, event.timestamp)
    
    def _handle_move_down(self, event: InputEvent):
        """Handle down arrow - rotate pieces clockwise."""
        if event.is_pressed and self.is_falling:
            current_time = self._now_ms()
            if current_time - self._last_rotation_time >= self._rotation_cooldown_ms:
                self.engine.rotate_attached_piece(1)  # Clockwise
                self._last_rotation_time = current_time
                self._log_diag('rotate', pygame.K_DOWN, event.timestamp)
    
    def _handle_rotate_cw(self, event: InputEvent):
        """Handle clockwise rotation."""
        if event.is_pressed and self.is_falling:
            self.engine.rotate_attached_piece(1)
            self._log_diag('rotate', pygame.K_z, event.timestamp)
    
    def _handle_rotate_ccw(self, event: InputEvent):
        """Handle counter-clockwise rotation."""
        if event.is_pressed and self.is_falling:
            self.engine.rotate_attached_piece(-1)
            self._log_diag('rotate', pygame.K_x, event.timestamp)
    
    def _handle_flip(self, event: InputEvent):
        """Handle piece flip."""
        if event.is_pressed and self.is_falling:
            self.engine.flip_pieces_vertically()
            self._log_diag('flip', pygame.K_f, event.timestamp)
    
    def _handle_drop(self, event: InputEvent):
        """Handle piece drop."""
        if event.is_pressed and self.is_falling:
            self.engine.place_piece_on_grid()
            self._log_diag('drop', pygame.K_SPACE, event.timestamp)
    
    def _handle_action(self, event: InputEvent):
        """Handle action key (spacebar)."""
        # Space bar should only accelerate, not place pieces
        if event.is_pressed and self.is_falling:
            # Only accelerate fall speed, don't place piece
            self.engine.current_fall_speed = self.engine.accelerated_fall_speed
            self.engine.micro_fall_time = self.engine._calculate_micro_fall_time(self.engine.current_fall_speed)
            self._log_diag('accelerate', pygame.K_SPACE, event.timestamp)
    
    def _on_movement_gate_change(self, enabled: bool):
        """Handle movement gate changes."""
        self.is_falling = enabled
    
    def get_control(self, action: str) -> int:
        """Get the key code for a specific action from settings or fall back to defaults."""
        # Try unified input manager first
        try:
            action_enum = InputAction(action)
            key_bindings = self.unified_input._get_key_bindings()
            return key_bindings.get(action, self._get_default_control(action))
        except ValueError:
            return self._get_default_control(action)
    
    def _get_default_control(self, action: str) -> int:
        """Get default key code for an action."""
        default_controls = {
            'move_up': pygame.K_UP,
            'move_down': pygame.K_DOWN,
            'move_left': pygame.K_LEFT,
            'move_right': pygame.K_RIGHT,
            'action': pygame.K_SPACE,
            'menu_cancel': pygame.K_ESCAPE,
            'music_pause': pygame.K_p,
            'music_next': pygame.K_RIGHTBRACKET,
            'music_prev': pygame.K_LEFTBRACKET,
            'music_vol_up': pygame.K_EQUALS,
            'music_vol_down': pygame.K_MINUS,
        }
        return default_controls.get(action, pygame.K_UNKNOWN)
    
    def is_key_pressed(self, action: str) -> bool:
        """Check if a key for a specific action is currently pressed."""
        key_code = self.get_control(action)
        return self.unified_input.is_key_pressed(key_code)
    
    def process_events(self, events):
        """
        Process pygame events for the puzzle game.
        Returns the action to perform (e.g., 'back_to_menu') or None.
        """
        # Process events through unified input manager
        processed_events = self.unified_input.process_events(events)
        
        # Update legacy key tracking for compatibility
        self._update_legacy_key_tracking(processed_events)
        
        # Check for menu actions
        for event in processed_events:
            if event.action == InputAction.MENU_CANCEL and event.is_pressed:
                return "back_to_menu"
        
        return None
    
    def _update_legacy_key_tracking(self, processed_events: List[InputEvent]):
        """Update legacy key tracking for compatibility."""
        current_time = int(self.clock.now_ms()) if self.clock else int(time.time() * 1000)
        
        for event in processed_events:
            if event.is_pressed:
                self.keys_pressed[event.key_code] = current_time
                self.key_press_time[event.key_code] = current_time
                
                # Handle space bar press
                if event.key_code == self.get_control('action'):
                    self._handle_spacebar_press()
            else:
                if event.key_code in self.keys_pressed:
                    del self.keys_pressed[event.key_code]
                if event.key_code in self.key_press_time:
                    del self.key_press_time[event.key_code]
                
                # Handle space bar release
                if event.key_code == self.get_control('action'):
                    self._handle_spacebar_release()
    
    def _handle_continuous_keys(self):
        """Handle continuous key presses for held keys (legacy method)."""
        # DAS/ARR functionality removed - no automatic key repeat
        pass
    
    def clear_spacebar_from_keys(self):
        """Clear action key from tracked keys (used when generating new pieces)."""
        action_key = self.get_control('action')
        self.unified_input.clear_key(action_key)
        if action_key in self.keys_pressed:
            del self.keys_pressed[action_key]
        if action_key in self.last_key_action_time:
            del self.last_key_action_time[action_key]
    
    def _handle_spacebar_press(self):
        """Handle spacebar press for acceleration."""
        # Increase fall speed for micro-movements
        self.engine.current_fall_speed = self.engine.accelerated_fall_speed
        self.engine.micro_fall_time = self.engine._calculate_micro_fall_time(self.engine.current_fall_speed)
    
    def _handle_spacebar_release(self):
        """Handle spacebar release to reset fall speed."""
        self.engine.current_fall_speed = self.engine.normal_fall_speed
        self.engine.micro_fall_time = self.engine._calculate_micro_fall_time(self.engine.current_fall_speed)
    
    def set_debug_spacebar(self, debug):
        """Enable or disable spacebar debug output."""
        self.debug_spacebar = debug
    
    def _now_ms(self) -> int:
        """Get current time in milliseconds."""
        return int(self.clock.now_ms()) if self.clock else int(time.time() * 1000)
    
    def _on_piece_landed(self):
        """Callback when a piece lands."""
        try:
            self.is_falling = False
            self.unified_input.set_movement_gate(False)
        except Exception:
            pass
    
    def _log_diag(self, kind: str, key_code: int, ts_ms: int) -> None:
        """Log diagnostic information."""
        # Store in diagnostic events
        self._diag_events.append({
            'kind': kind,
            'key_code': key_code,
            'timestamp': ts_ms
        })
        self._last_diag_ts = ts_ms
    
    def apply_external_lock(self, locked: bool):
        """Apply external input lock."""
        self._external_lock = locked
        if locked:
            self.unified_input.lock_input(1000, "external_lock")  # Lock for 1 second
        else:
            self.unified_input.unlock_input()
    
    def get_pressed_keys(self) -> Dict[int, int]:
        """Get currently pressed keys with their press timestamps."""
        return self.unified_input.get_pressed_keys()
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the input handler."""
        status = self.unified_input.get_status()
        status.update({
            'legacy_keys_pressed': len(self.keys_pressed),
            'legacy_external_lock': self._external_lock,
            'is_falling': self.is_falling,
            'debug_spacebar': self.debug_spacebar
        })
        return status


# Legacy alias for backward compatibility
InputHandler = InputHandlerCompat 