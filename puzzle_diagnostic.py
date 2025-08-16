#!/usr/bin/env python3
"""
Puzzle Piece Rendering Diagnostic
Tests the puzzle piece rendering system to identify why only 1 block is showing instead of 2.
"""

import pygame
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.puzzle_module import PuzzleEngine
from core.puzzle_renderer import PuzzleRenderer
from core.scaling import true_resolution_scaler
from utils.clock import PygameClock

def test_puzzle_rendering():
    """Test puzzle piece rendering to identify the issue."""
    
    # Initialize pygame
    pygame.init()
    
    # Create a test screen
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Puzzle Rendering Diagnostic")
    
    # Create a test font
    font = pygame.font.Font(None, 24)
    
    # Create puzzle engine
    engine = PuzzleEngine(screen, font, None, "puzzleassets")
    
    # Create puzzle renderer
    renderer = PuzzleRenderer(engine, clock=PygameClock())
    
    print(f"🔍 Diagnostic Results:")
    print(f"   Engine block dimensions: {engine.block_width}x{engine.block_height}")
    print(f"   Renderer block dimensions: {renderer.block_width}x{renderer.block_height}")
    print(f"   Grid dimensions: {engine.grid_width}x{engine.grid_height}")
    
    # Test puzzle pieces dictionary
    print(f"\n📦 Puzzle Pieces Available:")
    for key, value in engine.puzzle_pieces.items():
        if value is not None:
            print(f"   ✅ {key}: {value.get_size() if hasattr(value, 'get_size') else 'Surface'}")
        else:
            print(f"   ❌ {key}: None")
    
    # Test block images through asset loader
    print(f"\n🎨 Block Images Available:")
    for key, value in engine.asset_loader.block_images.items():
        if value is not None:
            print(f"   ✅ {key}: {value.get_size() if hasattr(value, 'get_size') else 'Surface'}")
        else:
            print(f"   ❌ {key}: None")
    
    # Test asset loader
    print(f"\n📁 Asset Loader Test:")
    print(f"   Asset path: {engine.asset_loader.asset_path}")
    print(f"   Block width: {engine.asset_loader.block_width}")
    print(f"   Block height: {engine.asset_loader.block_height}")
    
    # Test resolution scaler
    print(f"\n🖥️ Resolution Scaler Test:")
    try:
        current_res = true_resolution_scaler.resolution_manager.get_current_resolution()
        print(f"   Current resolution: {current_res.width}x{current_res.height}")
        
        # Test loading a block
        test_block = true_resolution_scaler.load_puzzle_piece("redblock")
        if test_block:
            print(f"   ✅ Resolution scaler loaded redblock: {test_block.get_size()}")
        else:
            print(f"   ❌ Resolution scaler failed to load redblock")
    except Exception as e:
        print(f"   ❌ Resolution scaler error: {e}")
    
    # Test piece generation
    print(f"\n🎲 Piece Generation Test:")
    engine.generate_new_piece()
    print(f"   Main piece: {engine.main_piece}")
    print(f"   Attached piece: {engine.attached_piece}")
    print(f"   Piece position: {engine.piece_position}")
    print(f"   Attached position: {engine.attached_position}")
    
    # Test visual position calculation
    print(f"\n📍 Visual Position Test:")
    main_vis = engine.get_visual_position()
    attached_vis = engine.get_attached_visual_position()
    print(f"   Main visual position: {main_vis}")
    print(f"   Attached visual position: {attached_vis}")
    
    # Test rendering
    print(f"\n🎨 Rendering Test:")
    try:
        # Clear screen
        screen.fill((0, 0, 0))
        
        # Draw grid background
        renderer.draw_grid_background()
        
        # Draw falling piece
        renderer.draw_falling_piece()
        
        # Update display
        pygame.display.flip()
        
        print(f"   ✅ Rendering completed successfully")
        
        # Wait a moment to see the result
        pygame.time.wait(2000)
        
    except Exception as e:
        print(f"   ❌ Rendering error: {e}")
        import traceback
        traceback.print_exc()
    
    pygame.quit()

if __name__ == "__main__":
    test_puzzle_rendering()
