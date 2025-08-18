#!/usr/bin/env python3
"""
Debug script to identify real transformation and color issues.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pygame

def main():
    """Debug the real issues."""
    print("🔍 DEBUGGING REAL ISSUES")
    print("="*50)
    
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    font = pygame.font.Font(None, 36)
    
    try:
        from modules.testmode_module.test_mode import TestModeRefactored
        from modules.items_module.item_system import create_rusted_sword
        
        # Create test mode
        test_mode = TestModeRefactored(screen, font, None, "puzzleassets")
        
        # Get enemy engine
        engine = test_mode.enemy_engine
        grid = engine.puzzle_grid
        
        print("✅ TestMode initialized")
        
        # Check if test_mode is properly set on engines
        print(f"📊 Player engine test_mode: {hasattr(engine, 'test_mode')}")
        print(f"📊 Enemy engine test_mode: {hasattr(test_mode.enemy_engine, 'test_mode')}")
        
        if hasattr(engine, 'test_mode'):
            print(f"📊 Engine test_mode type: {type(engine.test_mode)}")
            print(f"📊 Engine test_mode has garbage_block_brightness: {hasattr(engine.test_mode, 'garbage_block_brightness')}")
        
        # Test 1: Check what blocks exist and their exact types
        print("\n🧪 Test 1: Block inventory")
        
        # Place various block types to see what happens
        test_blocks = [
            (3, 8, 'red_strike'),
            (4, 8, 'blue_garbage'),
            (5, 8, 'green_block'),
            (3, 9, 'red_garbage'),
            (4, 9, 'blue_block'),
            (5, 9, 'yellow_block')
        ]
        
        for x, y, block_type in test_blocks:
            if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
                grid[y][x] = block_type
                print(f"  📍 Placed {block_type} at ({x}, {y})")
        
        # Check what's actually in the grid
        print("\n📊 Grid contents:")
        for y in range(len(grid)):
            for x in range(len(grid[0])):
                cell = grid[y][x]
                if cell:
                    print(f"  📍 ({x}, {y}): {cell}")
        
        # Test 2: Check colors for each block
        print("\n🧪 Test 2: Color analysis")
        renderer = test_mode.enemy_renderer
        
        for y in range(len(grid)):
            for x in range(len(grid[0])):
                cell = grid[y][x]
                if cell:
                    color = renderer._get_block_color((x, y))
                    print(f"  🎨 ({x}, {y}): {cell} -> {color}")
                    
                    # Check for dark blue blocks
                    if color == (0, 0, 255):
                        print(f"    ⚠️  DARK BLUE DETECTED: {cell}")
        
        # Test 3: Check transformation tracking
        print("\n🧪 Test 3: Transformation tracking")
        
        # Initialize tracking for strike and garbage
        strike_key = (3, 8, 2)
        garbage_key = (4, 8, 2)
        
        test_mode.garbage_block_brightness[strike_key] = {
            'landings': 0,
            'color': 'red',
            'is_strike': True
        }
        
        test_mode.garbage_block_brightness[garbage_key] = {
            'landings': 0,
            'color': 'blue',
            'is_strike': False
        }
        
        print(f"  📊 Strike tracking: {test_mode.garbage_block_brightness[strike_key]}")
        print(f"  📊 Garbage tracking: {test_mode.garbage_block_brightness[garbage_key]}")
        
        # Test 4: Simulate landing and check what happens
        print("\n🧪 Test 4: Landing simulation")
        test_mode._on_piece_landed(2)
        
        print(f"  📊 Strike tracking after landing: {test_mode.garbage_block_brightness.get(strike_key)}")
        print(f"  📊 Garbage tracking after landing: {test_mode.garbage_block_brightness.get(garbage_key)}")
        
        # Check actual grid state
        strike_cell = grid[8][3] if 0 <= 8 < len(grid) and 0 <= 3 < len(grid[0]) else None
        garbage_cell = grid[8][4] if 0 <= 8 < len(grid) and 0 <= 4 < len(grid[0]) else None
        print(f"  📊 Strike cell after landing: {strike_cell}")
        print(f"  📊 Garbage cell after landing: {garbage_cell}")
        
        # Test 5: Check if there are any blocks that look like old grey blocks
        print("\n🧪 Test 5: Grey block detection")
        
        grey_like_blocks = []
        for y in range(len(grid)):
            for x in range(len(grid[0])):
                cell = grid[y][x]
                if cell:
                    # Check for any blocks that might be old grey blocks
                    if cell == 'garbage_block' or cell == 'strike_block':
                        grey_like_blocks.append((x, y, cell, "NEUTRAL_BLOCK"))
                    elif '_garbage' in str(cell) or '_strike' in str(cell):
                        # Check if this block is tracked
                        pos_key = (x, y, 2)
                        if pos_key not in test_mode.garbage_block_brightness:
                            grey_like_blocks.append((x, y, cell, "UNTRACKED"))
                        else:
                            tracking = test_mode.garbage_block_brightness[pos_key]
                            if tracking['landings'] == 0:
                                grey_like_blocks.append((x, y, cell, f"NO_LANDINGS_{tracking}"))
        
        print(f"  📊 Found {len(grey_like_blocks)} grey-like blocks:")
        for x, y, cell, reason in grey_like_blocks:
            print(f"    📍 ({x}, {y}): {cell} - {reason}")
        
        # Test 6: Check if the transformation logic is being called
        print("\n🧪 Test 6: Transformation logic check")
        
        # Check if _process_garbage_transformations is working
        print("  🔄 Calling _process_garbage_transformations directly...")
        test_mode._process_garbage_transformations(2, grid)
        
        # Check grid state after direct transformation call
        print("  📊 Grid state after direct transformation:")
        for y in range(len(grid)):
            for x in range(len(grid[0])):
                cell = grid[y][x]
                if cell and ('_garbage' in str(cell) or '_strike' in str(cell)):
                    print(f"    📍 ({x}, {y}): {cell}")
        
        # Summary
        print("\n" + "="*50)
        print("📊 DEBUG SUMMARY")
        print("="*50)
        
        issues = []
        
        # Check for dark blue blocks
        dark_blue_count = 0
        for y in range(len(grid)):
            for x in range(len(grid[0])):
                cell = grid[y][x]
                if cell:
                    color = renderer._get_block_color((x, y))
                    if color == (0, 0, 255):
                        dark_blue_count += 1
        
        if dark_blue_count > 0:
            issues.append(f"❌ Found {dark_blue_count} dark blue blocks")
        else:
            print("✅ No dark blue blocks found")
        
        # Check transformation issues
        if strike_cell != 'red_garbage':
            issues.append(f"❌ Strike not transformed: {strike_cell}")
        else:
            print("✅ Strike transformation working")
            
        if garbage_cell != 'blue_block':
            issues.append(f"❌ Garbage not transformed: {garbage_cell}")
        else:
            print("✅ Garbage transformation working")
        
        # Check tracking issues
        if grey_like_blocks:
            issues.append(f"❌ Found {len(grey_like_blocks)} grey-like blocks")
        else:
            print("✅ No grey-like blocks found")
        
        if issues:
            print("\n⚠️  ISSUES FOUND:")
            for issue in issues:
                print(f"  {issue}")
        else:
            print("\n🎉 NO ISSUES FOUND!")
        
        return len(issues) == 0
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        pygame.quit()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
