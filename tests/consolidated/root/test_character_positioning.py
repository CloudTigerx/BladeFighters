#!/usr/bin/env python3
"""
Test Character Positioning - Verify character alignment and positioning
"""

import pygame
import sys
import os

# Initialize pygame
pygame.init()

# Create a test screen
screen = pygame.display.set_mode((1200, 800))
pygame.display.set_caption("Character Positioning Test")

# Test character positioning
try:
    from modules.character_module.character_sprite_manager import CharacterSpriteManager
    
    # Initialize sprite manager
    sprite_manager = CharacterSpriteManager("puzzleassets", 1200, 800)
    
    print("✅ Sprite manager initialized")
    
    # Test positioning calculation
    test_board_pos = {"x": 100, "y": 100}
    test_board_dims = (30, 30, 180, 450)  # cell_w, cell_h, board_w, board_h
    
    char_x, char_y = sprite_manager.calculate_character_position(
        test_board_pos, test_board_dims, 'yuki'
    )
    print(f"✅ Character position calculated: ({char_x}, {char_y})")
    
    # Test rendering with animation
    from modules.character_module.character_animation_manager import CharacterAnimationManager
    
    animation_manager = CharacterAnimationManager()
    yuki_config = sprite_manager.get_character_config('yuki')
    if yuki_config:
        animation_manager.initialize_character('yuki', yuki_config)
        print("✅ Animation manager initialized")
    
    # Test rendering loop
    clock = pygame.time.Clock()
    running = True
    frame_count = 0
    
    while running and frame_count < 300:  # Run for 5 seconds at 60fps
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
        current_frame = animation_manager.update_character_animation('yuki')
        
        # Draw character
        sprite = sprite_manager.get_character_sprite('yuki', 'idle', current_frame)
        if sprite:
            screen.blit(sprite, (char_x, char_y))
            
            # Draw a reference line at the character's baseline
            baseline_y = char_y + sprite.get_height()
            pygame.draw.line(screen, (255, 255, 0), (char_x, baseline_y), (char_x + sprite.get_width(), baseline_y), 2)
        
        # Draw info text
        font = pygame.font.Font(None, 24)
        info_text = f"Frame: {current_frame}/8 | Position: ({char_x}, {char_y}) | Press ESC to exit"
        text_surface = font.render(info_text, True, (255, 255, 255))
        screen.blit(text_surface, (10, 10))
        
        pygame.display.flip()
        clock.tick(60)
        frame_count += 1
    
    print("✅ Character positioning test completed successfully")
    
except Exception as e:
    print(f"❌ Character positioning test failed: {e}")
    import traceback
    traceback.print_exc()

pygame.quit()
