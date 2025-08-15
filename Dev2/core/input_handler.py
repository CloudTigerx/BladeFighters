import pygame
import time
from collections import deque
from utils.clock import Clock, PygameClock

class InputHandler:
    """
    Handles all input processing for the puzzle game.
    Manages keyboard and mouse events, key repeat timing, and game controls.
    """
    
    def __init__(self, puzzle_engine, settings_ui=None):
        """
        Initialize the input handler.
        
        Args:
            puzzle_engine: Reference to the puzzle engine for calling game methods
            settings_ui: Reference to settings UI for custom controls
        """
        self.engine = puzzle_engine
        self.settings_ui = settings_ui
        # Unified time source
        self.clock: Clock = getattr(self.engine, 'clock', None) or PygameClock()
        
        # Key tracking system
        self.keys_pressed = {}
        self.last_key_action_time = {}
        self.key_press_time = {}
        # External input lock (e.g., per-board freeze during payload receipt or chains)
        self._external_lock = False
        
        # Movement gate: true when a piece is actively falling and may accept movement inputs
        self.is_falling = True
        # Bind land callback if engine supports it
        try:
            setattr(self.engine, 'on_piece_landed', self._on_piece_landed)
        except Exception:
            pass
        
        # Debug flag for spacebar acceleration
        self.debug_spacebar = False
        
        # Diagnostics: recent key events (press/release/repeat) with timestamps
        self._diag_events = deque(maxlen=64)
        self._last_diag_ts = None
        # Frame intents buffer for recorder/replay
        self._intents = []
    
    def get_control(self, action: str) -> int:
        """Get the key code for a specific action from settings or fall back to defaults."""
        # Prefer bindings from the enhanced settings system if available
        if hasattr(self, 'settings_ui') and self.settings_ui and hasattr(self.settings_ui, 'get_control'):
            key_code = self.settings_ui.get_control(action)
            if key_code is not None:
                return key_code

        # Pull from config-enhanced settings if present
        try:
            if hasattr(self.settings_ui, 'config') and self.settings_ui.config:
                cfg_key = f"bind_{action}"
                val = self.settings_ui.config.get(cfg_key)
                if isinstance(val, (int, float)):
                    return int(val)
        except Exception:
            pass
        # Fallback defaults
        default_controls = {
            'move_up': pygame.K_UP,
            'move_down': pygame.K_DOWN,
            'move_left': pygame.K_LEFT,
            'move_right': pygame.K_RIGHT,
            'action': pygame.K_SPACE,
            'menu_cancel': pygame.K_ESCAPE,
            # MP3 controls defaults
            'music_pause': pygame.K_p,
            'music_next': pygame.K_RIGHTBRACKET,
            'music_prev': pygame.K_LEFTBRACKET,
            'music_vol_up': pygame.K_EQUALS,
            'music_vol_down': pygame.K_MINUS,
        }
        return default_controls.get(action, pygame.K_UNKNOWN)
    
    def is_key_pressed(self, action: str) -> bool:
        """Check if a control action key is currently pressed."""
        key_code = self.get_control(action)
        return key_code in self.keys_pressed
    
    def process_events(self, events):
        """
        Process pygame events for the puzzle game.
        Returns the action to perform (e.g., 'back_to_menu') or None.
        """
        action = None
        
        for event in events:
            # Mouse events
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
                action = self._handle_mouse_click(event)
            
            # Keyboard events
            elif event.type == pygame.KEYDOWN:
                action = self._handle_key_press(event)
            
            # Track key releases
            elif event.type == pygame.KEYUP:
                self._handle_key_release(event)
        
        # Handle continuous key presses
        if self.engine.game_active:
            self._handle_continuous_keys()
        
        return action
    
    def _handle_mouse_click(self, event):
        """Handle mouse click events."""
        # Check for button clicks
        mouse_pos = pygame.mouse.get_pos()
        for button in self.engine.game_buttons:
            if button["rect"].collidepoint(mouse_pos):
                return button["action"]
        return None
    
    def _handle_key_press(self, event):
        """Handle keyboard key press events."""
        # Track key press
        self.keys_pressed[event.key] = True
        now = self._now_ms()
        self.last_key_action_time[event.key] = now
        self.key_press_time[event.key] = now
        self._log_diag('press', event.key, self.last_key_action_time[event.key])
        
        # Handle one-time key presses
        if self.engine.game_active:
            # Handle rotation with move_up key (counter-clockwise)
            if event.key == self.get_control('move_up'):
                if not self._external_lock:
                    # First try to rotate, if that fails, try to flip
                    if not self.engine.rotate_attached_piece(-1):
                        self.engine.flip_pieces_vertically()
            
            # Handle rotation with move_down key (clockwise)
            elif event.key == self.get_control('move_down'):
                if not self._external_lock:
                    # First try to rotate, if that fails, try to flip
                    if not self.engine.rotate_attached_piece(1):
                        self.engine.flip_pieces_vertically()
            
            # Handle immediate left/right movement on initial press
            elif event.key == self.get_control('move_left'):
                if not self._external_lock:
                    self.engine.move_piece(-1, 0)  # Move left
                    self._emit_intent('move_l', {})
            elif event.key == self.get_control('move_right'):
                if not self._external_lock:
                    self.engine.move_piece(1, 0)  # Move right
                    self._emit_intent('move_r', {})
            
            # Handle immediate acceleration when action key is first pressed
            elif event.key == self.get_control('action'):
                if not self._external_lock:
                    self._handle_spacebar_press()
                    self._emit_intent('drop', {'state': 'press'})
        
        # Menu cancel key - go back to menu
        if event.key == self.get_control('menu_cancel'):
            self._emit_intent('pause', {})
            return "back_to_menu"
        
        return None
    
    def _handle_key_release(self, event):
        """Handle keyboard key release events."""
        if event.key in self.keys_pressed:
            del self.keys_pressed[event.key]
        
        if event.key in self.last_key_action_time:
            del self.last_key_action_time[event.key]
        if event.key in self.key_press_time:
            del self.key_press_time[event.key]
        self._log_diag('release', event.key, self._now_ms())
        
        # Reset speed when action key is released
        if event.key == self.get_control('action'):
            self._handle_spacebar_release()
    
    def _handle_spacebar_press(self):
        """Handle spacebar press for acceleration."""
        if self.debug_spacebar:
            print(f"SPACE PRESSED: normal_speed={self.engine.normal_fall_speed}, accel_speed={self.engine.accelerated_fall_speed}")
        
        # Increase fall speed for micro-movements
        self.engine.current_fall_speed = self.engine.accelerated_fall_speed
        self.engine.micro_fall_time = self.engine._calculate_micro_fall_time(self.engine.current_fall_speed)
        
        if self.debug_spacebar:
            print(f"AFTER SPACE: current_speed={self.engine.current_fall_speed}, micro_time={self.engine.micro_fall_time}")
    
    def _handle_spacebar_release(self):
        """Handle spacebar release to reset fall speed."""
        if self.debug_spacebar:
            print(f"SPACE RELEASED: Setting speed back to normal={self.engine.normal_fall_speed}")
        
        self.engine.current_fall_speed = self.engine.normal_fall_speed
        self.engine.micro_fall_time = self.engine._calculate_micro_fall_time(self.engine.current_fall_speed)
        
        if self.debug_spacebar:
            print(f"AFTER RELEASE: current_speed={self.engine.current_fall_speed}, micro_time={self.engine.micro_fall_time}")
    
    def _handle_continuous_keys(self):
        """Handle continuous key presses for held keys."""
        current_time = self._now_ms()
        # Movement gate is controlled via callbacks; do not infer here
        
        for key in self.keys_pressed:
            # Check if it's time for a repeat action
            time_since_last_action = current_time - self.last_key_action_time.get(key, 0)
            time_since_press = current_time - self.key_press_time.get(key, self.last_key_action_time.get(key, current_time))
            
            # Movement keys honor initial delay, then use move interval for repeats
            if key in [self.get_control('move_left'), self.get_control('move_right')]:
                if not self.is_falling:
                    continue
                initial_delay_passed = time_since_last_action >= 120 # Legacy alias for initial delay
                # Tap grace prevents repeats when released quickly
                tap_block = time_since_press < 120 # Legacy alias for tap grace
                # DAS/ARR
                das = 120
                arr = 80
                das_ready = time_since_press >= das
                arr_ready = das_ready and (time_since_last_action >= arr)
                if not tap_block and arr_ready:
                    if key == self.get_control('move_left'):
                        self.engine.move_piece(-1, 0)  # Move left
                        self._emit_intent('move_l', {})
                    elif key == self.get_control('move_right'):
                        self.engine.move_piece(1, 0)  # Move right
                        self._emit_intent('move_r', {})
                    # Reset last action for ARR cadence
                    self.last_key_action_time[key] = current_time
                    self._log_diag('repeat', key, current_time)
            
            # Handle move_up and move_down for rotations with slow repeats
            elif key in [self.get_control('move_up'), self.get_control('move_down')]:
                if not self.is_falling:
                    continue
                if time_since_last_action >= 600: # Legacy alias for rotate repeat interval
                    if key == self.get_control('move_up'):
                        self.engine.rotate_attached_piece(-1)  # Counter-clockwise
                        self._emit_intent('rotate', {'dir': -1})
                    elif key == self.get_control('move_down'):
                        self.engine.rotate_attached_piece(1)   # Clockwise
                        self._emit_intent('rotate', {'dir': 1})
                    # Update last action time
                    self.last_key_action_time[key] = current_time
                    self._log_diag('repeat', key, current_time)
            
            # Handle action key for immediate acceleration with no delay
            elif key == self.get_control('action'):
                # DEBUG: Print values during continuous action key press every second
                if self.debug_spacebar and current_time % 1000 < 20:  # Only print once per second approximately
                    print(f"ACTION KEY HELD: current_speed={self.engine.current_fall_speed}, micro_time={self.engine.micro_fall_time}")
                
                # Always apply acceleration immediately with no delay
                if self.is_falling:
                    self.engine.current_fall_speed = self.engine.accelerated_fall_speed
                    self.engine.micro_fall_time = self.engine._calculate_micro_fall_time(self.engine.current_fall_speed)
                    self._emit_intent('drop', {'state': 'hold'})
                else:
                    continue
            
            # Other keys use the general timing system
            else:
                # Initial delay for first repeat
                initial_delay_passed = time_since_last_action >= 120 # Legacy alias for initial delay
                
                # For subsequent repeats, check if interval time has passed
                repeat_ready = (initial_delay_passed and 
                              (time_since_last_action - 120) % 80 <= 16) # Legacy aliases for interval
                
                if repeat_ready:
                    # Update the last action time for this key
                    self.last_key_action_time[key] = current_time - (
                        120 + 
                        ((time_since_last_action - 120) // 80) 
                        * 80
                    )
                    self._log_diag('repeat', key, current_time)
    
    def clear_spacebar_from_keys(self):
        """Clear action key from tracked keys (used when generating new pieces)."""
        action_key = self.get_control('action')
        if action_key in self.keys_pressed:
            del self.keys_pressed[action_key]
        if action_key in self.last_key_action_time:
            del self.last_key_action_time[action_key]
    
    def set_debug_spacebar(self, debug):
        """Enable or disable spacebar debug output."""
        self.debug_spacebar = debug 

    def _now_ms(self) -> int:
        return int(self.clock.now_ms())

    # Movement gate callbacks
    def _on_piece_landed(self):
        try:
            self.is_falling = False
        except Exception:
            pass

    # ------------------------
    # Diagnostics API
    # ------------------------
    def _log_diag(self, kind: str, key_code: int, ts_ms: int) -> None:
        try:
            prev = self._last_diag_ts
            delta = 0 if prev is None else max(0, int(ts_ms) - int(prev))
            self._diag_events.append({
                't': int(ts_ms),
                'delta': int(delta),
                'type': str(kind),
                'key': int(key_code),
            })
            self._last_diag_ts = int(ts_ms)
        except Exception:
            # Never let diagnostics affect gameplay
            pass

    def _emit_intent(self, intent: str, data: dict) -> None:
        try:
            self._intents.append({
                't_ms': int(self._now_ms()),
                'intent': str(intent),
                'data': dict(data or {}),
            })
        except Exception:
            pass

    def pop_intents(self) -> list:
        intents = self._intents
        self._intents = []
        # When externally locked, suppress gameplay movement/rotation/drop intents
        if self._external_lock:
            try:
                blocked = {"move_l", "move_r", "rotate", "drop"}
                return [i for i in intents if str(i.get("intent")) not in blocked]
            except Exception:
                return []
        return intents

    def apply_external_lock(self, is_locked: bool) -> None:
        """Enable/disable external input lock gate.

        When enabled, `pop_intents()` will suppress gameplay intents except UI/system ones.
        """
        try:
            self._external_lock = bool(is_locked)
        except Exception:
            self._external_lock = False

    def get_diagnostics(self) -> dict:
        """
        Return a read-only snapshot of input diagnostics for UI overlays.
        Includes recent events and current repeat timing configuration.
        """
        try:
            return {
                'now_ms': self._now_ms(),
                'timings': {
                    'repeat_initial_delay_ms': 120, # Legacy alias
                    'repeat_interval_ms': 80, # Legacy alias
                    'repeat_move_interval_ms': 80, # Legacy alias
                    'repeat_rotate_interval_ms': 600, # Legacy alias
                    'tap_grace_ms': 120, # Legacy alias
                },
                'last_events': list(self._diag_events),
                'keys_pressed_count': len(self.keys_pressed),
            }
        except Exception:
            return {
                'now_ms': 0,
                'timings': {},
                'last_events': [],
                'keys_pressed_count': 0,
            }