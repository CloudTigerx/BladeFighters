#!/usr/bin/env python3
"""
Test script to verify grey block elimination and garbage transformation fixes.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pygame
from modules.testmode_module.test_mode import TestModeRefactored
from modules.testmode_module.attack_delivery_planner import AttackDeliveryPlanner
from modules.testmode_module.attack_delivery_committer import AttackDeliveryCommitter
from core.puzzle_module import PuzzleEngine
from core.puzzle_renderer import PuzzleRenderer
from modules.items_module.item_system import ItemSystem

def test_grey_block_elimination():
    """Test that no grey blocks are created."""
    print("🧪 Testing grey block elimination...")
    
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    font = pygame.font.Font(None, 36)
    
    try:
        # Create test mode with proper initialization
        test_mode = TestModeRefactored(screen, font, None, "puzzleassets")
        
        # Test garbage block creation
        engine = test_mode.enemy_engine
        grid = engine.puzzle_grid
        
        # Simulate placing garbage blocks
        test_attack_data = {
            'attack_type': 'garbage_blocks',
            'block_count': 3,
            'handedness': 'R'
        }
        
        # Create item system for color assignment
        item_system = ItemSystem()
        item_system.equip_weapon("rusted_sword")
        
        # Create planner and committer
        planner = AttackDeliveryPlanner()
        committer = AttackDeliveryCommitter({})
        
        # Plan garbage delivery
        plan = planner.plan_garbage_delivery(engine, test_attack_data, 'enemy', item_system)
        
        # Commit garbage blocks
        result = committer.commit_garbage(engine, plan, 'enemy')
        
        print(f"✅ Placed {result.blocks_placed} garbage blocks")
        
        # Check that no grey blocks exist
        grey_blocks_found = 0
        colored_garbage_found = 0
        
        for y in range(len(grid)):
            for x in range(len(grid[0])):
                cell = grid[y][x]
                if cell:
                    if cell == 'garbage_block':
                        grey_blocks_found += 1
                        print(f"❌ Found grey block at ({x}, {y}): {cell}")
                    elif '_garbage' in str(cell):
                        colored_garbage_found += 1
                        print(f"✅ Found colored garbage at ({x}, {y}): {cell}")
        
        if grey_blocks_found == 0:
            print("✅ SUCCESS: No grey blocks found!")
        else:
            print(f"❌ FAILURE: Found {grey_blocks_found} grey blocks")
            
        if colored_garbage_found > 0:
            print(f"✅ SUCCESS: Found {colored_garbage_found} colored garbage blocks")
        else:
            print("❌ FAILURE: No colored garbage blocks found")
            
        return grey_blocks_found == 0 and colored_garbage_found > 0
        
    except Exception as e:
        print(f"❌ ERROR during grey block test: {e}")
        return False
    finally:
        pygame.quit()

def test_garbage_transformation():
    """Test that garbage blocks transform properly."""
    print("\n🧪 Testing garbage transformation...")
    
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    font = pygame.font.Font(None, 36)
    
    try:
        # Create test mode with proper initialization
        test_mode = TestModeRefactored(screen, font, None, "puzzleassets")
        
        # Get enemy engine and place some colored garbage
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
        
        # Simulate piece landing near garbage blocks
        print("🔄 Simulating piece landing...")
        
        # Call the piece landed handler
        test_mode._on_piece_landed(2)  # enemy player
        
        # Check if transformations occurred
        transformations_found = 0
        
        for x, y in test_positions:
            current_cell = grid[y][x]
            expected_color = colors[test_positions.index((x, y))]
            expected_normal = f"{expected_color}_block"
            
            if current_cell == expected_normal:
                transformations_found += 1
                print(f"✅ Garbage transformed at ({x}, {y}): {current_cell}")
            else:
                print(f"❌ Garbage not transformed at ({x}, {y}): {current_cell} (expected {expected_normal})")
        
        if transformations_found == len(test_positions):
            print("✅ SUCCESS: All garbage blocks transformed!")
        else:
            print(f"❌ FAILURE: Only {transformations_found}/{len(test_positions)} garbage blocks transformed")
            
        return transformations_found == len(test_positions)
        
    except Exception as e:
        print(f"❌ ERROR during transformation test: {e}")
        return False
    finally:
        pygame.quit()

def test_cluster_detection():
    """Test that clusters don't include garbage blocks."""
    print("\n🧪 Testing cluster detection...")
    
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    font = pygame.font.Font(None, 36)
    
    try:
        # Create test mode with proper initialization
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
        
        if garbage_in_clusters == 0:
            print("✅ SUCCESS: No garbage blocks in clusters!")
        else:
            print(f"❌ FAILURE: Found {garbage_in_clusters} garbage blocks in clusters")
            
        return garbage_in_clusters == 0
        
    except Exception as e:
        print(f"❌ ERROR during cluster test: {e}")
        return False
    finally:
        pygame.quit()

def main():
    """Run all tests."""
    print("🚀 Starting comprehensive testing of grey block fixes...\n")
    
    tests = [
        ("Grey Block Elimination", test_grey_block_elimination),
        ("Garbage Transformation", test_garbage_transformation),
        ("Cluster Detection", test_cluster_detection)
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
    print("\n" + "="*50)
    print("📊 TEST RESULTS SUMMARY")
    print("="*50)
    
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
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
