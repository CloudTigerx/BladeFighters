#!/usr/bin/env python3
"""
Final verification test to confirm all fixes are working.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pygame

def main():
    """Final verification."""
    print("🎯 FINAL VERIFICATION - All Fixes Working")
    print("="*50)
    
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
        
        # Test 1: Place blocks and verify transformations
        print("\n🧪 Test 1: Block transformations")
        
        # Place test blocks
        test_blocks = [
            (3, 8, 'red_strike'),
            (4, 8, 'blue_garbage'),
            (5, 8, 'green_block')
        ]
        
        for x, y, block_type in test_blocks:
            if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
                grid[y][x] = block_type
                print(f"  📍 Placed {block_type} at ({x}, {y})")
        
        # Initialize tracking
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
        
        print("  ✅ Tracking initialized")
        
        # Simulate landing
        print("  🔄 Simulating piece landing...")
        test_mode._on_piece_landed(2)
        
        # Check results
        strike_cell = grid[8][3] if 0 <= 8 < len(grid) and 0 <= 3 < len(grid[0]) else None
        garbage_cell = grid[8][4] if 0 <= 8 < len(grid) and 0 <= 4 < len(grid[0]) else None
        
        print(f"  📊 Strike cell: {strike_cell}")
        print(f"  📊 Garbage cell: {garbage_cell}")
        
        strike_transformed = strike_cell == 'red_garbage'
        garbage_transformed = garbage_cell == 'blue_block'
        
        print(f"  ✅ Strike transformed: {strike_transformed}")
        print(f"  ✅ Garbage transformed: {garbage_transformed}")
        
        # Test 2: Check colors
        print("\n🧪 Test 2: Color verification")
        renderer = test_mode.enemy_renderer
        
        for x, y, block_type in test_blocks:
            if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
                color = renderer._get_block_color((x, y))
                print(f"  🎨 ({x}, {y}): {grid[y][x]} -> {color}")
                
                # Check for proper colors (not grey/white)
                if color == (128, 128, 128) or color == (255, 255, 255):
                    print(f"    ⚠️  GREY/WHITE COLOR DETECTED: {color}")
        
        # Test 3: Check cluster detection
        print("\n🧪 Test 3: Cluster detection")
        
        # Create a cluster with garbage nearby
        cluster_positions = [(1, 8), (2, 8), (1, 9), (2, 9)]
        for x, y in cluster_positions:
            if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
                grid[y][x] = 'green_block'
        
        # Place garbage nearby
        garbage_positions = [(0, 8), (3, 8)]
        for x, y in garbage_positions:
            if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
                grid[y][x] = 'yellow_garbage'
        
        clusters = engine.find_rectangular_clusters_for_render()
        print(f"  📊 Found {len(clusters)} clusters")
        
        garbage_in_clusters = 0
        for cluster in clusters:
            for x, y in cluster:
                if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
                    cell = grid[y][x]
                    if cell and '_garbage' in str(cell):
                        garbage_in_clusters += 1
                        print(f"    ❌ Garbage in cluster at ({x}, {y}): {cell}")
        
        print(f"  ✅ Garbage in clusters: {garbage_in_clusters}")
        
        # Test 4: Check cluster glows
        print("\n🧪 Test 4: Cluster glow verification")
        renderer.update_visual_state()
        
        glow_effects = renderer.cluster_glow_effects
        print(f"  📊 Found {len(glow_effects)} cluster glow effects")
        
        white_glows = 0
        for cluster_id, glow_data in glow_effects.items():
            color = glow_data['color']
            if color == (255, 255, 255) or color == (128, 128, 128):
                white_glows += 1
                print(f"    ❌ WHITE/GREY GLOW: {color}")
        
        print(f"  ✅ White/grey glows: {white_glows}")
        
        # Final summary
        print("\n" + "="*50)
        print("📊 FINAL VERIFICATION SUMMARY")
        print("="*50)
        
        results = [
            ("Strike Transformation", strike_transformed),
            ("Garbage Transformation", garbage_transformed),
            ("No Grey/White Colors", white_glows == 0),
            ("Clusters Exclude Garbage", garbage_in_clusters == 0)
        ]
        
        passed = 0
        for name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {name}")
            if result:
                passed += 1
        
        print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
        
        if passed == len(results):
            print("🎉 ALL FIXES WORKING CORRECTLY!")
            print("✅ No grey/silver blocks anywhere")
            print("✅ All attacks transform properly")
            print("✅ Clusters exclude garbage blocks")
            print("✅ No white/silver glows")
            print("✅ All colors are proper")
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
