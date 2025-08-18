#!/usr/bin/env python3
"""
Quick test to verify the transformation and color fixes.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pygame

def main():
    """Test the fixes."""
    print("🔧 Testing transformation and color fixes...")
    
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    font = pygame.font.Font(None, 36)
    
    try:
        from modules.testmode_module.test_mode import TestModeRefactored
        
        # Create test mode
        test_mode = TestModeRefactored(screen, font, None, "puzzleassets")
        
        # Get enemy engine
        engine = test_mode.enemy_engine
        grid = engine.puzzle_grid
        
        print("✅ TestMode initialized")
        
        # Test 1: Place strike and garbage blocks
        print("\n🧪 Test 1: Placing strike and garbage blocks")
        grid[10][3] = 'red_strike'
        grid[10][4] = 'blue_garbage'
        
        # Initialize tracking
        strike_key = (3, 10, 2)
        garbage_key = (4, 10, 2)
        
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
        
        print(f"✅ Placed red_strike at (3, 10)")
        print(f"✅ Placed blue_garbage at (4, 10)")
        print(f"✅ Tracking initialized")
        
        # Test 2: Simulate piece landing
        print("\n🧪 Test 2: Simulating piece landing")
        test_mode._on_piece_landed(2)
        
        # Check tracking
        strike_tracking = test_mode.garbage_block_brightness.get(strike_key)
        garbage_tracking = test_mode.garbage_block_brightness.get(garbage_key)
        
        print(f"📊 Strike tracking: {strike_tracking}")
        print(f"📊 Garbage tracking: {garbage_tracking}")
        
        # Test 3: Check transformations
        print("\n🧪 Test 3: Checking transformations")
        strike_cell = grid[10][3]
        garbage_cell = grid[10][4]
        
        print(f"📊 Strike cell: {strike_cell}")
        print(f"📊 Garbage cell: {garbage_cell}")
        
        strike_transformed = strike_cell == 'red_garbage'
        garbage_transformed = garbage_cell == 'blue_block'
        
        print(f"✅ Strike transformed: {strike_transformed}")
        print(f"✅ Garbage transformed: {garbage_transformed}")
        
        # Test 4: Check colors
        print("\n🧪 Test 4: Checking colors")
        from core.puzzle_renderer import PuzzleRenderer
        
        renderer = test_mode.enemy_renderer
        strike_color = renderer._get_block_color((3, 10))
        garbage_color = renderer._get_block_color((4, 10))
        
        print(f"📊 Strike color: {strike_color}")
        print(f"📊 Garbage color: {garbage_color}")
        
        # Check that colors are correct for the block types
        strike_color_correct = strike_color == (255, 100, 100)  # red_garbage should be red
        garbage_color_correct = garbage_color == (0, 0, 255)    # blue_block should be blue
        
        print(f"✅ Strike color correct: {strike_color_correct}")
        print(f"✅ Garbage color correct: {garbage_color_correct}")
        
        # Final results
        print("\n" + "="*40)
        print("📊 RESULTS")
        print("="*40)
        
        results = [
            ("Strike Transformation", strike_transformed),
            ("Garbage Transformation", garbage_transformed),
            ("Strike Color Correct", strike_color_correct),
            ("Garbage Color Correct", garbage_color_correct)
        ]
        
        passed = 0
        for name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {name}")
            if result:
                passed += 1
        
        print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
        
        if passed == len(results):
            print("🎉 ALL FIXES WORKING!")
        else:
            print("⚠️  Some issues remain")
        
        return passed == len(results)
        
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
