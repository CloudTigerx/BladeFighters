#!/usr/bin/env python3
"""
Debug script to test grey block fixes with simpler approach.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pygame

def test_garbage_creation_direct():
    """Test garbage block creation directly without TestMode."""
    print("🧪 Testing garbage block creation directly...")
    
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    font = pygame.font.Font(None, 36)
    
    try:
        from modules.testmode_module.attack_delivery_planner import AttackDeliveryPlanner
        from modules.testmode_module.attack_delivery_committer import AttackDeliveryCommitter
        from modules.items_module.item_system import ItemSystem, create_rusted_sword
        from core.puzzle_module import PuzzleEngine
        
        # Create puzzle engine
        engine = PuzzleEngine(screen, font, None, "puzzleassets")
        grid = engine.puzzle_grid
        
        # Create item system and equip weapon properly
        item_system = ItemSystem()
        weapon = create_rusted_sword()
        item_system.equip_weapon(weapon)
        
        # Create planner and committer
        planner = AttackDeliveryPlanner()
        committer = AttackDeliveryCommitter({})
        
        # Test attack data
        test_attack_data = {
            'attack_type': 'garbage_blocks',
            'block_count': 2,
            'handedness': 'R'
        }
        
        # Plan garbage delivery
        plan = planner.plan_garbage_delivery(engine, test_attack_data, 'enemy', item_system)
        
        print(f"✅ Plan created with {len(plan.garbage_blocks)} garbage blocks")
        
        # Check plan colors
        for i, block in enumerate(plan.garbage_blocks):
            print(f"  Block {i}: color={block.color}, pos=({block.column}, {block.row})")
        
        # Commit garbage blocks
        result = committer.commit_garbage(engine, plan, 'enemy')
        
        print(f"✅ Committed {result.blocks_placed} garbage blocks")
        
        # Check grid for grey vs colored blocks
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
        
        success = grey_blocks == 0 and colored_blocks > 0
        print(f"{'✅ SUCCESS' if success else '❌ FAILURE'}: Grey block elimination")
        
        return success
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        pygame.quit()

def test_transformation_logic():
    """Test the transformation logic directly."""
    print("\n🧪 Testing transformation logic...")
    
    try:
        from modules.testmode_module.test_mode import TestModeRefactored
        
        # Initialize pygame
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        font = pygame.font.Font(None, 36)
        
        # Create test mode
        test_mode = TestModeRefactored(screen, font, None, "puzzleassets")
        
        # Get enemy engine
        engine = test_mode.enemy_engine
        grid = engine.puzzle_grid
        
        # Manually place colored garbage
        test_pos = (3, 10)
        grid[test_pos[1]][test_pos[0]] = 'red_garbage'
        
        # Initialize tracking
        pos_key = (test_pos[0], test_pos[1], 2)
        test_mode.garbage_block_brightness[pos_key] = {
            'landings': 0,
            'color': 'red',
            'is_strike': False
        }
        
        print(f"✅ Placed red_garbage at {test_pos}")
        print(f"✅ Tracking initialized: {test_mode.garbage_block_brightness[pos_key]}")
        
        # Place a normal block above to simulate landing area
        grid[test_pos[1]-1][test_pos[0]] = 'blue_block'
        print(f"✅ Placed blue_block at ({test_pos[0]}, {test_pos[1]-1}) to create landing area")
        
        # Simulate landing
        print("🔄 Simulating landing...")
        test_mode._on_piece_landed(2)
        
        # Check tracking after landing
        if pos_key in test_mode.garbage_block_brightness:
            tracking = test_mode.garbage_block_brightness[pos_key]
            print(f"📊 Tracking after landing: {tracking}")
            
            if tracking['landings'] > 0:
                print("✅ Landing count incremented")
            else:
                print("❌ Landing count not incremented")
        else:
            print("❌ Tracking entry removed")
        
        # Check if transformation occurred
        current_cell = grid[test_pos[1]][test_pos[0]]
        print(f"📊 Current cell: {current_cell}")
        
        if current_cell == 'red_block':
            print("✅ SUCCESS: Garbage transformed to normal block")
            return True
        else:
            print(f"❌ FAILURE: Expected red_block, got {current_cell}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        pygame.quit()

def main():
    """Run debug tests."""
    print("🔍 Starting debug tests...\n")
    
    test1 = test_garbage_creation_direct()
    test2 = test_transformation_logic()
    
    print(f"\n📊 Debug Results:")
    print(f"  Garbage Creation: {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"  Transformation: {'✅ PASS' if test2 else '❌ FAIL'}")
    
    return test1 and test2

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
