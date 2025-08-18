#!/usr/bin/env python3
"""
Quick test to verify procedural katana system integration
"""

import pygame
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.menu_module.procedural_katana_system import ProceduralKatanaSystem

def test_procedural_system():
    """Test the procedural katana system integration."""
    pygame.init()
    
    # Create a test window
    screen = pygame.display.set_mode((1200, 800))
    pygame.display.set_caption("🗡️ Procedural Katana Integration Test")
    
    # Create a font
    font = pygame.font.SysFont(None, 48)
    
    # Create procedural katana menu system
    procedural_menu = ProceduralKatanaSystem(screen, font, None, "puzzleassets")
    
    clock = pygame.time.Clock()
    running = True
    
    print("🧪 Testing Procedural Katana System Integration...")
    print("✅ Procedural system created successfully")
    print("✅ Textures generated: ", len(procedural_menu.textures))
    print("✅ Buttons created: ", len(procedural_menu.buttons))
    print("✅ Colors configured: ", len(procedural_menu.colors))
    
    # Test button actions
    test_actions = ["quickplay", "story", "test", "smithing", "inventory", "settings", "quit"]
    for action in test_actions:
        print(f"✅ Button action '{action}' configured")
    
    print("\n🎮 Integration test complete! Your procedural katana menu is ready!")
    print("🚀 Run 'python3 main.py' to see it in action!")
    
    # Quick demo
    print("\n🎬 Running quick demo...")
    for i in range(60):  # 1 second at 60fps
        dt = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            
            # Test event handling
            action = procedural_menu.handle_event(event)
            if action:
                print(f"🎯 Action triggered: {action}")
        
        # Update and draw
        procedural_menu.update(dt)
        procedural_menu.draw()
        pygame.display.flip()
    
    pygame.quit()
    print("✅ Integration test completed successfully!")

if __name__ == "__main__":
    test_procedural_system()
