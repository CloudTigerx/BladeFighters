import pygame
import time

class InputHandler:
    """
    Handles all input processing for the puzzle game.
    Manages keyboard and mouse events, key repeat timing, and game controls.
    """
    
    def __init__(self, puzzle_engine):
        """
        Initialize the input handler.
        
        Args:
            puzzle_engine: Reference to the puzzle engine for calling game methods
        """
        self.engine = puzzle_engine
        
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
            # Handle rotation with UP key (counter-clockwise)
            if event.key == pygame.K_UP:
                # First try to rotate, if that fails, try to flip
                if not self.engine.rotate_attached_piece(-1):
                    self.engine.flip_pieces_vertically()
            
            # Handle rotation with DOWN key (clockwise)
            elif event.key == pygame.K_DOWN:
                # First try to rotate, if that fails, try to flip
                if not self.engine.rotate_attached_piece(1):
                    self.engine.flip_pieces_vertically()
            
            # Handle immediate left/right movement on initial press
            elif event.key == pygame.K_LEFT:
                self.engine.move_piece(-1, 0)  # Move left
            elif event.key == pygame.K_RIGHT:
                self.engine.move_piece(1, 0)  # Move right
            
            # Handle immediate acceleration when space is first pressed
            elif event.key == pygame.K_SPACE:
                self._handle_spacebar_press()
        
        # Escape key - go back to menu
        if event.key == pygame.K_ESCAPE:
            return "back_to_menu"
        
        return None
    
    def _handle_key_release(self, event):
        """Handle keyboard key release events."""
        if event.key in self.keys_pressed:
            del self.keys_pressed[event.key]
        
        if event.key in self.last_key_action_time:
            del self.last_key_action_time[event.key]
        
        # Reset speed when spacebar is released
        if event.key == pygame.K_SPACE:
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
            
            # Arrow keys have no delay for first press, but slow repeats for held keys
            if key in [pygame.K_LEFT, pygame.K_RIGHT]:
                # Immediate response for first press or if enough time has passed
                if time_since_last_action >= self.arrow_repeat_interval:
                    if key == pygame.K_LEFT:
                        self.engine.move_piece(-1, 0)  # Move left
                    elif key == pygame.K_RIGHT:
                        self.engine.move_piece(1, 0)  # Move right
                    # Update last action time to control repeat rate
                    self.last_key_action_time[key] = current_time
            
            # Handle UP and DOWN for rotations with slow repeats
            elif key in [pygame.K_UP, pygame.K_DOWN]:
                if time_since_last_action >= self.rotate_repeat_interval:
                    if key == pygame.K_UP:
                        self.engine.rotate_attached_piece(-1)  # Counter-clockwise
                    elif key == pygame.K_DOWN:
                        self.engine.rotate_attached_piece(1)   # Clockwise
                    # Update last action time
                    self.last_key_action_time[key] = current_time
            
            # Handle spacebar for immediate acceleration with no delay
            elif key == pygame.K_SPACE:
                # DEBUG: Print values during continuous space press every second
                if self.debug_spacebar and current_time % 1000 < 20:  # Only print once per second approximately
                    print(f"SPACE HELD: current_speed={self.engine.current_fall_speed}, micro_time={self.engine.micro_fall_time}")
                
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
        """Clear spacebar from tracked keys (used when generating new pieces)."""
        if pygame.K_SPACE in self.keys_pressed:
            del self.keys_pressed[pygame.K_SPACE]
        if pygame.K_SPACE in self.last_key_action_time:
            del self.last_key_action_time[pygame.K_SPACE]
    
    def set_debug_spacebar(self, debug):
        """Enable or disable spacebar debug output."""
        self.debug_spacebar = debug 