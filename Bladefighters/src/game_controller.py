#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Game Controller - Handles user input and communicates with the model
This acts as the mediator between user events and game logic
"""

import pygame

class GameController:
    """Handles user input and communicates with the model."""
    
    def __init__(self, model, view):
        """Initialize with game model and view."""
        self.model = model
        self.view = view
        
        # Input state
        self.keys_pressed = {}
        self.key_repeat_delay = 180  # ms before the first repeat
        self.key_repeat_interval = 80  # ms between repeats
        self.last_key_action_time = {}
        
        # Cooldowns to prevent rapid firing
        self.action_cooldowns = {
            "rotate": 150,  # ms
            "hard_drop": 300,  # ms
            "restart": 500,  # ms
        }
        self.last_action_time = {
            "rotate": 0,
            "hard_drop": 0,
            "restart": 0,
        }
    
    def handle_event(self, event):
        """Process pygame events and update the model accordingly."""
        current_time = pygame.time.get_ticks()
        
        if event.type == pygame.KEYDOWN:
            # Store the key press time
            self.keys_pressed[event.key] = current_time
            self.last_key_action_time[event.key] = current_time
            
            # Process immediate actions
            if event.key == pygame.K_UP:
                self._try_action("rotate", lambda: self.model.rotate_piece(1))
            
            elif event.key == pygame.K_SPACE:
                # If game is over, restart
                if not self.model.game_active:
                    self._try_action("restart", lambda: self.model.start_game())
                else:
                    # Hard drop the current piece
                    self._try_action("hard_drop", lambda: self.model.hard_drop())
        
        elif event.type == pygame.KEYUP:
            # Remove the key from pressed keys
            if event.key in self.keys_pressed:
                del self.keys_pressed[event.key]
            
            # Also remove from last action time to reset repeat
            if event.key in self.last_key_action_time:
                del self.last_key_action_time[event.key]
    
    def update(self, delta_time):
        """Update controller state and handle continuous input."""
        current_time = pygame.time.get_ticks()
        
        # Process continuous/repeated key actions
        for key in list(self.keys_pressed.keys()):
            # Get the initial press time
            initial_press_time = self.keys_pressed[key]
            
            # Calculate time since the last action for this key
            time_since_last_action = current_time - self.last_key_action_time.get(key, 0)
            
            # Check if we've passed the initial delay
            if current_time - initial_press_time < self.key_repeat_delay:
                continue  # Still within initial delay
            
            # For subsequent repeats, check if enough time has passed
            if time_since_last_action < self.key_repeat_interval:
                continue  # Not ready for the next repeat
            
            # Update the last action time for this key
            self.last_key_action_time[key] = current_time
            
            # Process movement keys
            if key == pygame.K_LEFT:
                self.model.move_piece(-1, 0)
            elif key == pygame.K_RIGHT:
                self.model.move_piece(1, 0)
            elif key == pygame.K_DOWN:
                # Increase fall speed when down is held
                if self.model.current_piece:
                    self.model.current_fall_speed = self.model.FAST_FALL_SPEED
            
            # Don't repeat rotation and space bar actions - they're handled on key down
    
    def _try_action(self, action_name, action_func):
        """Try to perform an action if its cooldown has expired."""
        current_time = pygame.time.get_ticks()
        cooldown = self.action_cooldowns.get(action_name, 0)
        last_time = self.last_action_time.get(action_name, 0)
        
        if current_time - last_time >= cooldown:
            result = action_func()
            if result:  # Only update cooldown if action was successful
                self.last_action_time[action_name] = current_time
            return result
        
        return False 