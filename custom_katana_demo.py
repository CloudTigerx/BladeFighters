#!/usr/bin/env python3
"""
Custom Katana Menu Demo
Tests the new katana menu system with custom assets
"""

import pygame
import sys
import os

# Add the modules directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

# Import directly from the file
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules', 'menu_module'))
from custom_katana_system import CustomKatanaSystem

def main():
    """Main demo function"""
    pygame.init()
    
    # Set up display
    width, height = 1920, 1080  # Standard HD for testing
    screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
    pygame.display.set_caption("Custom Katana Menu Demo")
    
    # Initialize the custom katana system
    print("🗡️ Initializing Custom Katana System...")
    katana_system = CustomKatanaSystem(width, height)
    
    # Game loop variables
    clock = pygame.time.Clock()
    running = True
    
    print("🎮 Custom Katana Demo started!")
    print("📱 Mouse over buttons to see effects")
    print("🖱️ Click buttons to see animations")
    print("🔧 Press ESC to exit")
    
    while running:
        dt = clock.tick(60) / 1000.0  # Delta time in seconds
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.VIDEORESIZE:
                # Handle window resize
                width, height = event.size
                screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
                katana_system = CustomKatanaSystem(width, height)
            
            # Handle menu events
            action = katana_system.handle_event(event)
            if action:
                print(f"🎯 Button clicked: {action}")
                if action == "exit":
                    running = False
        
        # Update the katana system
        katana_system.update(dt)
        
        # Clear screen
        screen.fill((0, 0, 0))
        
        # Draw the katana menu
        katana_system.draw(screen)
        
        # Update display
        pygame.display.flip()
    
    pygame.quit()
    print("👋 Custom Katana Demo ended!")

if __name__ == "__main__":
    main()
