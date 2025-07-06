#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Bladefighters - Main entry point for the game
A puzzle game with a clean architecture separating game logic from visuals
"""

import pygame
import sys
from game_model import GameModel
from game_view import GameView
from game_controller import GameController

class GameApp:
    """Main application class that initializes and runs the game."""
    
    def __init__(self):
        """Initialize the game application."""
        # Initialize pygame
        pygame.init()
        
        # Set up the window
        self.width = 800
        self.height = 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Bladefighters")
        
        # Initialize clock for controlling frame rate
        self.clock = pygame.time.Clock()
        self.target_fps = 60
        
        # Initialize the MVC components
        self.model = GameModel()
        self.view = GameView(self.model, self.screen)
        self.controller = GameController(self.model, self.view)
        
        # Track time for delta time calculations
        self.last_update_time = pygame.time.get_ticks()
    
    def run(self):
        """Main game loop."""
        running = True
        
        while running:
            # Calculate delta time in seconds
            current_time = pygame.time.get_ticks()
            delta_time = (current_time - self.last_update_time) / 1000.0
            self.last_update_time = current_time
            
            # Process events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                # Let the controller handle input events
                self.controller.handle_event(event)
            
            # Update game state
            self.model.update(delta_time)
            
            # Update visual state (interpolation happens here)
            self.view.update(delta_time)
            
            # Render the game
            self.view.render()
            
            # Update the display
            pygame.display.flip()
            
            # Control frame rate
            self.clock.tick(self.target_fps)
        
        # Clean up
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    # Create and run the game
    game = GameApp()
    game.run() 