#!/usr/bin/env python3
"""
Final comprehensive test for grey block elimination and garbage transformation.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pygame

def test_grey_block_elimination():
    """Test that no grey blocks are created in the actual game flow."""
    print("🧪 Testing grey block elimination in game flow...")
    
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
        
        # Create weapon and equip it
        weapon = create_rusted_sword()
        test_mode.enemy_items.equip_weapon(weapon)
        
        # Simulate an attack that creates garbage blocks
        # We'll use the test mode's built-in attack system
        test_mode.queue_attack_spawn('enemy', 'garbage_blocks', 3)
        
        # Update the game to process the attack
        for _ in range(10):  # Update a few frames
            test_mode.update()
        
        # Check for grey vs colored blocks
        grey_blocks = 0
        colored_blocks = 0
        
        for y in range(len(grid)):
            for x in range(len(grid[0])):
                cell = grid[y][x]
                if cell:
                    if cell == 'garbage_block':
                        grey_blocks += 1
                        print(f"❌ Grey block at ({x}, {y})")
                    elif '_garbage' in str(cell):
                        colored_blocks += 1
                        print(f"✅ Colored garbage at ({x}, {y}): {cell}")
        
        print(f"📊 Results: {grey_blocks} grey blocks, {colored_blocks} colored blocks")
        
        success = grey_blocks == 0
        print(f"{'✅ SUCCESS' if success else '❌ FAILURE'}: No grey blocks created")
        
        return success
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        pygame.quit()

def test_garbage_transformation():
    """Test that garbage blocks transform properly when pieces land."""
    print("\n🧪 Testing garbage transformation...")
    
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
        
        # Manually place colored garbage blocks
        test_positions = [(2, 10), (3, 10), (4, 10)]
        colors = ['red', 'blue', 'green']
        
        for i, (x, y) in enumerate(test_positions):
            color = colors[i]
            grid[y][x] = f"{color}_garbage"
            
            # Initialize tracking
            pos_key = (x, y, 2)  # player_id = 2 for enemy
            test_mode.garbage_block_brightness[pos_key] = {
                'landings': 0,
                'color': color,
                'is_strike': False
            }
        
        print(f"✅ Placed {len(test_positions)} colored garbage blocks")
        
        # Place normal blocks above to create landing areas
        for x, y in test_positions:
            grid[y-1][x] = 'yellow_block'
        
        print("✅ Created landing areas above garbage blocks")
        
        # Simulate piece landing
        print("🔄 Simulating piece landing...")
        test_mode._on_piece_landed(2)  # enemy player
        
        # Check transformations
        transformations = 0
        
        for i, (x, y) in enumerate(test_positions):
            current_cell = grid[y][x]
            expected_color = colors[i]
            expected_normal = f"{expected_color}_block"
            
            if current_cell == expected_normal:
                transformations += 1
                print(f"✅ Garbage transformed at ({x}, {y}): {current_cell}")
            else:
                print(f"❌ Garbage not transformed at ({x}, {y}): {current_cell} (expected {expected_normal})")
        
        success = transformations == len(test_positions)
        print(f"{'✅ SUCCESS' if success else '❌ FAILURE'}: {transformations}/{len(test_positions)} garbage blocks transformed")
        
        return success
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        pygame.quit()

def test_cluster_exclusion():
    """Test that clusters don't include garbage blocks."""
    print("\n🧪 Testing cluster exclusion...")
    
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
        
        # Create a 2x2 cluster of normal blocks
        cluster_positions = [(1, 10), (2, 10), (1, 11), (2, 11)]
        for x, y in cluster_positions:
            grid[y][x] = 'red_block'
        
        # Place garbage blocks nearby (should not affect cluster)
        garbage_positions = [(0, 10), (3, 10), (1, 9), (2, 9)]
        for x, y in garbage_positions:
            grid[y][x] = 'blue_garbage'
        
        print("✅ Created test grid with normal blocks and garbage")
        
        # Test cluster detection
        clusters = engine.find_rectangular_clusters_for_render()
        
        print(f"✅ Found {len(clusters)} clusters")
        
        # Check that clusters only contain normal blocks
        garbage_in_clusters = 0
        
        for cluster in clusters:
            for x, y in cluster:
                if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
                    cell = grid[y][x]
                    if cell and '_garbage' in str(cell):
                        garbage_in_clusters += 1
                        print(f"❌ Found garbage in cluster at ({x}, {y}): {cell}")
        
        success = garbage_in_clusters == 0
        print(f"{'✅ SUCCESS' if success else '❌ FAILURE'}: No garbage blocks in clusters")
        
        return success
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        pygame.quit()

def test_cluster_glow_exclusion():
    """Test that cluster glows don't appear for garbage blocks."""
    print("\n🧪 Testing cluster glow exclusion...")
    
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    font = pygame.font.Font(None, 36)
    
    try:
        from modules.testmode_module.test_mode import TestModeRefactored
        
        # Create test mode
        test_mode = TestModeRefactored(screen, font, None, "puzzleassets")
        
        # Get enemy engine and renderer
        engine = test_mode.enemy_engine
        renderer = test_mode.enemy_renderer
        grid = engine.puzzle_grid
        
        # Create a cluster of garbage blocks (should not get glow)
        garbage_cluster = [(1, 10), (2, 10), (1, 11), (2, 11)]
        for x, y in garbage_cluster:
            grid[y][x] = 'red_garbage'
        
        # Create a cluster of normal blocks (should get glow)
        normal_cluster = [(4, 10), (5, 10), (4, 11), (5, 11)]
        for x, y in normal_cluster:
            grid[y][x] = 'blue_block'
        
        print("✅ Created test grid with garbage and normal clusters")
        
        # Update visual state to trigger cluster detection
        renderer.update_visual_state()
        
        # Check cluster glow effects
        glow_effects = renderer.cluster_glow_effects
        
        print(f"✅ Found {len(glow_effects)} cluster glow effects")
        
        # Check that no glow effects contain garbage blocks
        garbage_in_glows = 0
        
        for cluster_id, glow_data in glow_effects.items():
            for x, y in glow_data['blocks']:
                if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
                    cell = grid[y][x]
                    if cell and '_garbage' in str(cell):
                        garbage_in_glows += 1
                        print(f"❌ Found garbage in glow effect at ({x}, {y}): {cell}")
        
        success = garbage_in_glows == 0
        print(f"{'✅ SUCCESS' if success else '❌ FAILURE'}: No garbage blocks in cluster glows")
        
        return success
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        pygame.quit()

def main():
    """Run all tests."""
    print("🚀 Starting final comprehensive testing of grey block fixes...\n")
    
    tests = [
        ("Grey Block Elimination", test_grey_block_elimination),
        ("Garbage Transformation", test_garbage_transformation),
        ("Cluster Exclusion", test_cluster_exclusion),
        ("Cluster Glow Exclusion", test_cluster_glow_exclusion)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ ERROR in {test_name}: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 FINAL TEST RESULTS SUMMARY")
    print("="*60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Grey block fixes are working correctly.")
        print("✅ No grey/silver blocks anywhere in the game")
        print("✅ Garbage blocks transform properly after piece landings")
        print("✅ Clusters exclude garbage blocks correctly")
        print("✅ Cluster glows exclude garbage blocks correctly")
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
