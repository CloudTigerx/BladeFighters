#!/usr/bin/env python3
"""
Procedural Katana Interface Demo
Showcasing pure code magic with procedurally generated textures!
"""

import pygame
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.menu_module.procedural_katana_system import ProceduralKatanaSystem

def main():
    pygame.init()
    
    # Create a window (you can change this to test different resolutions)
    screen = pygame.display.set_mode((1200, 800))
    pygame.display.set_caption("🗡️ Procedural Katana Interface - Pure Code Magic")
    
    # Create a font
    font = pygame.font.SysFont(None, 48)
    
    # Create procedural katana menu system
    procedural_menu = ProceduralKatanaSystem(screen, font, None, "puzzleassets")
    
    clock = pygame.time.Clock()
    running = True
    
    print("🗡️ Procedural Katana Interface Demo!")
    print("Features:")
    print("  - Pure code-generated katana textures")
    print("  - Golden ratio positioning (1.618)")
    print("  - Visual weight psychology")
    print("  - Lightning effects with procedural generation")
    print("  - Particle systems with procedural textures")
    print("  - Breathing animations with perfect math")
    print("  - Color psychology optimization")
    print("\nWatch the pure code magic unfold...")
    
    while running:
        dt = clock.tick(60) / 1000.0  # Delta time in seconds
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            
            # Handle menu events
            action = procedural_menu.handle_event(event)
            if action:
                print(f"🎯 Action triggered: {action}")
                if action == "quit":
                    running = False
        
        # Update procedural menu
        procedural_menu.update(dt)
        
        # Draw everything
        procedural_menu.draw()
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()


