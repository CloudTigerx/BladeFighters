#!/usr/bin/env python3
"""
Test Character System - Verify character sprite integration
Tests the character sprite system in isolation.
"""

import pygame
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_character_system():
    """Test the character sprite system."""
    print("🧪 Testing Character Sprite System...")
    
    # Initialize pygame
    pygame.init()
    
    # Create a test screen
    screen = pygame.display.set_mode((1200, 800))
    pygame.display.set_caption("Character System Test")
    
    # Test character sprite manager
    try:
        from modules.character_module.character_sprite_manager import CharacterSpriteManager
        from modules.character_module.character_animation_manager import CharacterAnimationManager
        
        # Initialize managers
        sprite_manager = CharacterSpriteManager("puzzleassets", 1200, 800)
        animation_manager = CharacterAnimationManager()
        
        print("✅ Character managers initialized")
        
        # Test sprite loading
        yuki_sprite = sprite_manager.get_character_sprite('yuki', 'idle')
        if yuki_sprite:
            print(f"✅ Yuki sprite loaded: {yuki_sprite.get_width()}x{yuki_sprite.get_height()}")
        else:
            print("❌ Failed to load Yuki sprite")
            return False
        
        # Test animation initialization
        yuki_config = sprite_manager.get_character_config('yuki')
        if yuki_config:
            animation_manager.initialize_character('yuki', yuki_config)
            print("✅ Yuki animation initialized")
        else:
            print("❌ Failed to get Yuki config")
            return False
        
        # Test positioning
        test_board_pos = {"x": 100, "y": 100}
        test_board_dims = (30, 30, 180, 450)  # cell_w, cell_h, board_w, board_h
        char_x, char_y = sprite_manager.calculate_character_position(
            test_board_pos, test_board_dims, 'yuki'
        )
        print(f"✅ Character position calculated: ({char_x}, {char_y})")
        
        # Test rendering
        clock = pygame.time.Clock()
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            
            # Clear screen
            screen.fill((20, 20, 40))
            
            # Draw test board background
            pygame.draw.rect(screen, (50, 50, 80), (100, 100, 180, 450))
            
            # Update animation
            animation_manager.update_character_animation('yuki')
            
            # Draw character
            sprite = sprite_manager.get_character_sprite('yuki', 'idle')
            if sprite:
                screen.blit(sprite, (char_x, char_y))
            
            # Draw info text
            font = pygame.font.Font(None, 24)
            info_text = f"Yuki Character Test - Press ESC to exit"
            text_surface = font.render(info_text, True, (255, 255, 255))
            screen.blit(text_surface, (10, 10))
            
            pygame.display.flip()
            clock.tick(60)
        
        print("✅ Character system test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Character system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        pygame.quit()

if __name__ == "__main__":
    success = test_character_system()
    sys.exit(0 if success else 1)
