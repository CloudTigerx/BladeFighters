#!/usr/bin/env python3
"""
DETAILED GARBAGE ROTATION DEBUG
===============================

Test garbage rotation with the same TestMode instance to verify persistent state.
"""

import sys
import os
from typing import List, Tuple, Dict, Any

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.testmode_module.test_mode import TestModeRefactored
import pygame

def test_garbage_rotation_with_same_instance():
    """Test garbage rotation using the same TestMode instance"""
    print("🔄 TESTING GARBAGE ROTATION WITH SAME INSTANCE...")
    print("=" * 60)
    
    # Initialize pygame and test mode (same instance for all tests)
    pygame.init()
    screen = pygame.display.set_mode((1200, 800))
    font = pygame.font.Font(None, 24)
    
    test_mode = TestModeRefactored(
        screen=screen,
        font=font,
        audio=None,
        asset_path="puzzleassets",
        settings_system=None,
        clock=None
    )
    test_mode.initialize_test()
    
    # Get the enemy engine for testing
    engine = test_mode.enemy_engine
    
    # Expected rotation pattern: 0,5,1,4,2,3 (0-based)
    expected_pattern = [0, 5, 1, 4, 2, 3]
    print("Expected rotation pattern:", expected_pattern)
    
    # Test with 6 garbage blocks to see the first rotation
    print("\nPlacing 6 garbage blocks...")
    
    # Clear the grid first
    for row in range(engine.grid_height):
        for col in range(engine.grid_width):
            engine.puzzle_grid[row][col] = None
    
    test_attack = {
        'type': 'garbage',
        'blocks_remaining': 6,
        'sprinkle_side': 'R',
        'handedness': 'R'
    }
    
    # Place garbage blocks
    blocks_placed = test_mode._place_garbage_attack_direct(engine, test_attack, 'enemy')
    print(f"Placed {blocks_placed} blocks")
    
    # Find which columns got blocks (in order)
    actual_pattern = []
    for row in range(engine.grid_height):
        for col in range(engine.grid_width):
            if engine.puzzle_grid[row][col] == 'garbage_block':
                if col not in actual_pattern:
                    actual_pattern.append(col)
    
    print("Actual placement pattern:", actual_pattern)
    
    # Check if pattern matches
    pattern_correct = actual_pattern == expected_pattern
    
    if pattern_correct:
        print("✅ First 6 blocks follow correct rotation pattern!")
    else:
        print("❌ First 6 blocks rotation pattern is incorrect!")
        print(f"Expected: {expected_pattern}")
        print(f"Actual: {actual_pattern}")
    
    # Now test the next 6 blocks to see if rotation continues
    print("\nPlacing next 6 garbage blocks...")
    
    # Clear the grid again
    for row in range(engine.grid_height):
        for col in range(engine.grid_width):
            engine.puzzle_grid[row][col] = None
    
    # Place next 6 blocks
    blocks_placed = test_mode._place_garbage_attack_direct(engine, test_attack, 'enemy')
    print(f"Placed {blocks_placed} blocks")
    
    # Find which columns got blocks (in order)
    second_pattern = []
    for row in range(engine.grid_height):
        for col in range(engine.grid_width):
            if engine.puzzle_grid[row][col] == 'garbage_block':
                if col not in second_pattern:
                    second_pattern.append(col)
    
    print("Second placement pattern:", second_pattern)
    
    # Expected: Should continue from where it left off: [0, 5, 1, 4, 2, 3]
    # Since we placed 6 blocks, we should start the cycle again
    expected_second = [0, 5, 1, 4, 2, 3]
    second_correct = second_pattern == expected_second
    
    if second_correct:
        print("✅ Second 6 blocks follow correct rotation pattern!")
    else:
        print("❌ Second 6 blocks rotation pattern is incorrect!")
        print(f"Expected: {expected_second}")
        print(f"Actual: {second_pattern}")
    
    # Check if rotation state is persistent
    print(f"\nRotation state after second placement: {getattr(test_mode, '_garbage_rotation_index', 'Not set')}")
    
    return pattern_correct and second_correct

def test_garbage_rotation_step_by_step():
    """Test garbage rotation step by step to see exactly what's happening"""
    print("\n🔍 TESTING GARBAGE ROTATION STEP BY STEP...")
    print("=" * 60)
    
    # Initialize pygame and test mode
    pygame.init()
    screen = pygame.display.set_mode((1200, 800))
    font = pygame.font.Font(None, 24)
    
    test_mode = TestModeRefactored(
        screen=screen,
        font=font,
        audio=None,
        asset_path="puzzleassets",
        settings_system=None,
        clock=None
    )
    test_mode.initialize_test()
    
    # Get the enemy engine for testing
    engine = test_mode.enemy_engine
    
    # Test placing blocks one by one
    print("Placing garbage blocks one by one...")
    
    for i in range(6):
        # Clear the grid
        for row in range(engine.grid_height):
            for col in range(engine.grid_width):
                engine.puzzle_grid[row][col] = None
        
        # Place 1 block
        test_attack = {
            'type': 'garbage',
            'blocks_remaining': 1,
            'sprinkle_side': 'R',
            'handedness': 'R'
        }
        
        blocks_placed = test_mode._place_garbage_attack_direct(engine, test_attack, 'enemy')
        
        # Find which column got the block
        placed_column = None
        for row in range(engine.grid_height):
            for col in range(engine.grid_width):
                if engine.puzzle_grid[row][col] == 'garbage_block':
                    placed_column = col
                    break
            if placed_column is not None:
                break
        
        print(f"  Block {i+1}: Column {placed_column}")
        
        # Check rotation state
        rotation_state = getattr(test_mode, '_garbage_rotation_index', 'Not set')
        print(f"    Rotation state: {rotation_state}")
    
    return True

def main():
    """Run all detailed rotation tests"""
    print("🔄 DETAILED GARBAGE ROTATION DEBUG")
    print("=" * 60)
    print()
    
    # Run tests
    same_instance_ok = test_garbage_rotation_with_same_instance()
    step_by_step_ok = test_garbage_rotation_step_by_step()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 DETAILED ROTATION DEBUG SUMMARY")
    print("=" * 60)
    
    all_passed = all([same_instance_ok, step_by_step_ok])
    
    if all_passed:
        print("✅ ALL DETAILED ROTATION TESTS PASSED!")
        print("The rotation logic is working correctly with persistent state.")
    else:
        print("❌ SOME DETAILED ROTATION TESTS FAILED!")
        if not same_instance_ok:
            print("  • Same instance rotation has issues")
        if not step_by_step_ok:
            print("  • Step by step rotation has issues")
    
    print("\n🔧 NEXT STEPS:")
    if all_passed:
        print("• The rotation logic is working correctly")
        print("• The issue might be in the test setup")
        print("• Check if the test is creating multiple instances")
    else:
        print("• Investigate the rotation state management")
        print("• Check if the rotation index is being reset")

if __name__ == "__main__":
    main()
