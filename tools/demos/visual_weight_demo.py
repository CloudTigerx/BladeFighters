#!/usr/bin/env python3
"""
Visual Weight Magic Demonstration
Press V to cycle through different visual weight styles and see the magic!
"""

import pygame
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.menu_module.menu_system import MenuSystem

def main():
    pygame.init()
    
    # Create a window
    screen = pygame.display.set_mode((1200, 800))
    pygame.display.set_caption("Visual Weight Magic Demo - Press V to cycle styles!")
    
    # Create a simple font
    font = pygame.font.SysFont(None, 48)
    
    # Create menu system
    menu_system = MenuSystem(screen, font, None, "puzzleassets")
    
    # Set initial style
    menu_system.set_visual_weight_style("heavy")
    
    clock = pygame.time.Clock()
    running = True
    
    print("🎨 Visual Weight Magic Demo!")
    print("Press V to cycle through visual weight styles:")
    print("  - HEAVY: 20px glow, 3px outline, orange text")
    print("  - LIGHT: 5px glow, 1px outline, white text") 
    print("  - MODERN: No glow, 1px border, light gray text")
    print("  - MINIMAL: No effects, gray text")
    print("\nWatch how the buttons feel completely different!")
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_v:
                    menu_system.cycle_visual_weight_style()
                elif event.key == pygame.K_ESCAPE:
                    running = False
        
        # Clear screen
        screen.fill((20, 20, 50))
        
        # Draw title
        title = font.render("Visual Weight Magic Demo", True, (255, 255, 255))
        screen.blit(title, (50, 20))
        
        # Draw instructions
        instructions = [
            "Press V to cycle visual weight styles",
            "Watch how buttons feel completely different!",
            "",
            "HEAVY: Feels 'important' and 'floating'",
            "LIGHT: Feels 'clean' and 'accessible'", 
            "MODERN: Feels 'sleek' and 'professional'",
            "MINIMAL: Feels 'subtle' and 'quiet'"
        ]
        
        instruction_font = pygame.font.SysFont(None, 24)
        for i, instruction in enumerate(instructions):
            text = instruction_font.render(instruction, True, (200, 200, 200))
            screen.blit(text, (50, 80 + i * 25))
        
        # Draw some demo buttons
        button_configs = [
            ("Demo Button 1", None),
            ("Demo Button 2", None),
            ("Demo Button 3", None),
            ("Demo Button 4", None)
        ]
        
        button_width = 300
        button_height = 60
        button_margin = 20
        start_y = 300
        
        for i, (text, action) in enumerate(button_configs):
            button_y = start_y + i * (button_height + button_margin)
            button_x = (screen.get_width() - button_width) // 2
            
            # Create and draw button using menu system
            button = menu_system.create_button(
                button_x, button_y,
                button_width, button_height,
                text, action
            )
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
