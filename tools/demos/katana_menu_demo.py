#!/usr/bin/env python3
"""
Katana Blade Interface Demo
Showcasing mathematical perfection and visual weight magic!
"""

import pygame
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.menu_module.katana_menu_system import KatanaMenuSystem

def main():
    pygame.init()
    
    # Create a window (you can change this to test different resolutions)
    screen = pygame.display.set_mode((1200, 800))
    pygame.display.set_caption("🗡️ Katana Blade Interface - Mathematical Perfection")
    
    # Create a font
    font = pygame.font.SysFont(None, 48)
    
    # Create katana menu system
    katana_menu = KatanaMenuSystem(screen, font, None, "puzzleassets")
    
    clock = pygame.time.Clock()
    running = True
    
    print("🗡️ Katana Blade Interface Demo!")
    print("Features:")
    print("  - Golden ratio positioning (1.618)")
    print("  - Katana-styled buttons with breathing animations")
    print("  - Lightning effects in the background")
    print("  - Particle systems for atmosphere")
    print("  - Mathematical perfection in every pixel!")
    print("\nWatch the magic unfold...")
    
    while running:
        dt = clock.tick(60) / 1000.0  # Delta time in seconds
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            
            # Handle menu events
            action = katana_menu.handle_event(event)
            if action:
                print(f"🎯 Action triggered: {action}")
                if action == "quit":
                    running = False
        
        # Update katana menu
        katana_menu.update(dt)
        
        # Draw everything
        katana_menu.draw()
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
