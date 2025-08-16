#!/usr/bin/env python3
"""
Test Sprite Sheet Loading - Verify sprite sheet frame extraction
"""

import pygame
import sys
import os

# Initialize pygame
pygame.init()

# Create a test screen
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Sprite Sheet Test")

# Test sprite sheet loading
try:
    from modules.character_module.character_sprite_manager import CharacterSpriteManager
    
    # Initialize sprite manager
    sprite_manager = CharacterSpriteManager("puzzleassets", 800, 600)
    
    print("✅ Sprite manager initialized")
    print(f"Available sprites: {list(sprite_manager.sprite_cache.keys())}")
    
    # Check for Yuki frames
    yuki_frames = [k for k in sprite_manager.sprite_cache.keys() if k.startswith("yuki_idle_")]
    print(f"Yuki frames found: {len(yuki_frames)}")
    print(f"Frame keys: {yuki_frames}")
    
    # Test getting different frames
    for i in range(9):
        sprite = sprite_manager.get_character_sprite('yuki', 'idle', i)
        if sprite:
            print(f"Frame {i}: {sprite.get_width()}x{sprite.get_height()}")
        else:
            print(f"Frame {i}: Not found")
    
    print("✅ Sprite sheet test completed successfully")
    
except Exception as e:
    print(f"❌ Sprite sheet test failed: {e}")
    import traceback
    traceback.print_exc()

pygame.quit()
