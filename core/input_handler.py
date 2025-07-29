import pygame
import time

class InputHandler:
    """
    Handles all input processing for the puzzle game.
    Manages keyboard and mouse events, key repeat timing, and game controls.
    """
    
    def __init__(self, puzzle_engine, settings_system=None):
        """
        Initialize the input handler.
        
        Args:
            puzzle_engine: Reference to the puzzle engine for calling game methods
            settings_system: Reference to settings system for custom controls
        """
        self.engine = puzzle_engine
        self.settings_system = settings_system
        
        # Key tracking system
        self.keys_pressed = {}
        self.last_key_action_time = {}
        
        # Key repeat timing settings
        self.key_repeat_delay = 120  # ms before the first repeat
        self.key_repeat_interval = 80  # ms between repeats after the first one
        
        # Different repeat intervals for different key types
        self.arrow_repeat_interval = 500  # Much slower repeat rate for movement (500ms between repeats)
        self.rotate_repeat_interval = 600  # Slower repeat rate for rotations (600ms between repeats)
        
        # Debug flag for spacebar acceleration
        self.debug_spacebar = False
    
    def get_control(self, action: str) -> int:
        """Get the key code for a specific action from settings."""
        if self.settings_system:
            return self.settings_system.get_control(action)
        # Fallback to default keys
        default_controls = {
            'move_up': pygame.K_UP,
            'move_down': pygame.K_DOWN,
            'move_left': pygame.K_LEFT,
            'move_right': pygame.K_RIGHT,
            'action': pygame.K_SPACE,
            'menu_cancel': pygame.K_ESCAPE
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
        self.last_key_action_time[event.key] = pygame.time.get_ticks()
        
        # Handle one-time key presses
        if self.engine.game_active:
            # Handle rotation with move_up key (counter-clockwise)
            if event.key == self.get_control('move_up'):
                # First try to rotate, if that fails, try to flip
                if not self.engine.rotate_attached_piece(-1):
                    self.engine.flip_pieces_vertically()
            
            # Handle rotation with move_down key (clockwise)
            elif event.key == self.get_control('move_down'):
                # First try to rotate, if that fails, try to flip
                if not self.engine.rotate_attached_piece(1):
                    self.engine.flip_pieces_vertically()
            
            # Handle immediate left/right movement on initial press
            elif event.key == self.get_control('move_left'):
                self.engine.move_piece(-1, 0)  # Move left
            elif event.key == self.get_control('move_right'):
                self.engine.move_piece(1, 0)  # Move right
            
            # Handle immediate acceleration when action key is first pressed
            elif event.key == self.get_control('action'):
                self._handle_spacebar_press()
        
        # Menu cancel key - go back to menu
        if event.key == self.get_control('menu_cancel'):
            return "back_to_menu"
        
        return None
    
    def _handle_key_release(self, event):
        """Handle keyboard key release events."""
        if event.key in self.keys_pressed:
            del self.keys_pressed[event.key]
        
        if event.key in self.last_key_action_time:
            del self.last_key_action_time[event.key]
        
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
        current_time = pygame.time.get_ticks()
        
        for key in self.keys_pressed:
            # Check if it's time for a repeat action
            time_since_last_action = current_time - self.last_key_action_time.get(key, 0)
            
            # Movement keys have no delay for first press, but slow repeats for held keys
            if key in [self.get_control('move_left'), self.get_control('move_right')]:
                # Immediate response for first press or if enough time has passed
                if time_since_last_action >= self.arrow_repeat_interval:
                    if key == self.get_control('move_left'):
                        self.engine.move_piece(-1, 0)  # Move left
                    elif key == self.get_control('move_right'):
                        self.engine.move_piece(1, 0)  # Move right
                    # Update last action time to control repeat rate
                    self.last_key_action_time[key] = current_time
            
            # Handle move_up and move_down for rotations with slow repeats
            elif key in [self.get_control('move_up'), self.get_control('move_down')]:
                if time_since_last_action >= self.rotate_repeat_interval:
                    if key == self.get_control('move_up'):
                        self.engine.rotate_attached_piece(-1)  # Counter-clockwise
                    elif key == self.get_control('move_down'):
                        self.engine.rotate_attached_piece(1)   # Clockwise
                    # Update last action time
                    self.last_key_action_time[key] = current_time
            
            # Handle action key for immediate acceleration with no delay
            elif key == self.get_control('action'):
                # DEBUG: Print values during continuous action key press every second
                if self.debug_spacebar and current_time % 1000 < 20:  # Only print once per second approximately
                    print(f"ACTION KEY HELD: current_speed={self.engine.current_fall_speed}, micro_time={self.engine.micro_fall_time}")
                
                # Always apply acceleration immediately with no delay
                self.engine.current_fall_speed = self.engine.accelerated_fall_speed
                self.engine.micro_fall_time = self.engine._calculate_micro_fall_time(self.engine.current_fall_speed)
            
            # Other keys use the general timing system
            else:
                # Initial delay for first repeat
                initial_delay_passed = time_since_last_action >= self.key_repeat_delay
                
                # For subsequent repeats, check if interval time has passed
                repeat_ready = (initial_delay_passed and 
                              (time_since_last_action - self.key_repeat_delay) % self.key_repeat_interval <= 16)
                
                if repeat_ready:
                    # Update the last action time for this key
                    self.last_key_action_time[key] = current_time - (
                        self.key_repeat_delay + 
                        ((time_since_last_action - self.key_repeat_delay) // self.key_repeat_interval) 
                        * self.key_repeat_interval
                    )
    
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