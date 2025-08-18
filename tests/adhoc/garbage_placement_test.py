#!/usr/bin/env python3
"""
GARBAGE PLACEMENT TEST
======================

This test validates that garbage blocks are properly rotating through columns
and spreading evenly instead of stacking 5+ on top of each other.
"""

import sys
import os
from typing import List, Tuple, Dict, Any

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.testmode_module.test_mode import TestModeRefactored
import pygame

def test_garbage_column_rotation():
    """Test that garbage blocks rotate through columns properly"""
    print("🗑️ TESTING GARBAGE COLUMN ROTATION...")
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
    
    # Clear the grid first
    for row in range(engine.grid_height):
        for col in range(engine.grid_width):
            engine.puzzle_grid[row][col] = None
    
    # Test with 12 garbage blocks (should use all 6 columns twice)
    print("Testing with 12 garbage blocks...")
    
    # Create a test attack
    test_attack = {
        'type': 'garbage',
        'blocks_remaining': 12,
        'sprinkle_side': 'R',
        'handedness': 'R'
    }
    
    # Place garbage blocks
    blocks_placed = test_mode._place_garbage_attack_direct(engine, test_attack, 'enemy')
    
    print(f"Placed {blocks_placed} garbage blocks")
    
    # Check column distribution
    column_counts = [0] * engine.grid_width
    for row in range(engine.grid_height):
        for col in range(engine.grid_width):
            if engine.puzzle_grid[row][col] == 'garbage_block':
                column_counts[col] += 1
    
    print("Column distribution:")
    for i, count in enumerate(column_counts):
        print(f"  Column {i}: {count} blocks")
    
    # Expected: Each column should have 2 blocks (12 blocks / 6 columns = 2 each)
    expected_per_column = 12 // 6
    max_per_column = max(column_counts)
    min_per_column = min(column_counts)
    
    print(f"\nExpected blocks per column: {expected_per_column}")
    print(f"Actual max per column: {max_per_column}")
    print(f"Actual min per column: {min_per_column}")
    
    # Check if distribution is even
    distribution_even = max_per_column <= expected_per_column + 1 and min_per_column >= expected_per_column - 1
    
    if distribution_even:
        print("✅ Garbage distribution is even across columns!")
    else:
        print("❌ Garbage distribution is uneven - blocks are stacking!")
    
    # Check for stacking (more than 3 blocks in any column)
    stacking_detected = max_per_column > 3
    
    if not stacking_detected:
        print("✅ No excessive stacking detected!")
    else:
        print(f"❌ Excessive stacking detected: {max_per_column} blocks in one column!")
    
    return distribution_even and not stacking_detected

def test_garbage_rotation_pattern():
    """Test that garbage follows the correct rotation pattern"""
    print("\n🔄 TESTING GARBAGE ROTATION PATTERN...")
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
    
    # Clear the grid first
    for row in range(engine.grid_height):
        for col in range(engine.grid_width):
            engine.puzzle_grid[row][col] = None
    
    # Expected rotation pattern: 0,5,1,4,2,3 (0-based)
    expected_pattern = [0, 5, 1, 4, 2, 3]
    
    print("Expected rotation pattern:", expected_pattern)
    
    # Test with 6 garbage blocks to see the first rotation
    test_attack = {
        'type': 'garbage',
        'blocks_remaining': 6,
        'sprinkle_side': 'R',
        'handedness': 'R'
    }
    
    # Place garbage blocks
    blocks_placed = test_mode._place_garbage_attack_direct(engine, test_attack, 'enemy')
    
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
        print("✅ Garbage follows correct rotation pattern!")
    else:
        print("❌ Garbage does not follow correct rotation pattern!")
        print(f"Expected: {expected_pattern}")
        print(f"Actual: {actual_pattern}")
    
    return pattern_correct

def test_garbage_fill_vacant_areas():
    """Test that garbage fills vacant areas when columns are full"""
    print("\n📍 TESTING GARBAGE FILLS VACANT AREAS...")
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
    
    # Clear the grid first
    for row in range(engine.grid_height):
        for col in range(engine.grid_width):
            engine.puzzle_grid[row][col] = None
    
    # Fill columns 0 and 1 completely (simulate full columns)
    for row in range(engine.grid_height):
        engine.puzzle_grid[row][0] = 'filled'
        engine.puzzle_grid[row][1] = 'filled'
    
    print("Filled columns 0 and 1 completely")
    
    # Test with 8 garbage blocks
    test_attack = {
        'type': 'garbage',
        'blocks_remaining': 8,
        'sprinkle_side': 'R',
        'handedness': 'R'
    }
    
    # Place garbage blocks
    blocks_placed = test_mode._place_garbage_attack_direct(engine, test_attack, 'enemy')
    
    print(f"Placed {blocks_placed} garbage blocks")
    
    # Check that no garbage was placed in full columns
    garbage_in_full_columns = 0
    for row in range(engine.grid_height):
        if engine.puzzle_grid[row][0] == 'garbage_block':
            garbage_in_full_columns += 1
        if engine.puzzle_grid[row][1] == 'garbage_block':
            garbage_in_full_columns += 1
    
    # Check that garbage was placed in other columns
    garbage_in_other_columns = 0
    for row in range(engine.grid_height):
        for col in range(2, engine.grid_width):
            if engine.puzzle_grid[row][col] == 'garbage_block':
                garbage_in_other_columns += 1
    
    print(f"Garbage in full columns (should be 0): {garbage_in_full_columns}")
    print(f"Garbage in other columns: {garbage_in_other_columns}")
    
    fills_vacant_areas = garbage_in_full_columns == 0 and garbage_in_other_columns > 0
    
    if fills_vacant_areas:
        print("✅ Garbage properly fills vacant areas when columns are full!")
    else:
        print("❌ Garbage does not properly fill vacant areas!")
    
    return fills_vacant_areas

def main():
    """Run all garbage placement tests"""
    print("🗑️ GARBAGE PLACEMENT VALIDATION")
    print("=" * 60)
    print()
    
    # Run all tests
    rotation_ok = test_garbage_column_rotation()
    pattern_ok = test_garbage_rotation_pattern()
    fill_ok = test_garbage_fill_vacant_areas()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 GARBAGE PLACEMENT TEST SUMMARY")
    print("=" * 60)
    
    all_passed = all([rotation_ok, pattern_ok, fill_ok])
    
    if all_passed:
        print("✅ ALL GARBAGE PLACEMENT TESTS PASSED!")
        print("Garbage blocks now:")
        print("  • Rotate through columns properly (1→6→2→5→3→4)")
        print("  • Spread evenly instead of stacking")
        print("  • Fill vacant areas when columns are full")
    else:
        print("❌ SOME GARBAGE PLACEMENT TESTS FAILED!")
        if not rotation_ok:
            print("  • Column rotation distribution issues")
        if not pattern_ok:
            print("  • Rotation pattern incorrect")
        if not fill_ok:
            print("  • Vacant area filling issues")
    
    print("\n🔧 RECOMMENDATIONS:")
    if all_passed:
        print("• Garbage placement is working correctly")
        print("• No more 5+ blocks stacking in one column")
        print("• Test in-game to verify behavior")
    else:
        print("• Review garbage placement logic")
        print("• Check column rotation implementation")
        print("• Verify vacant area handling")

if __name__ == "__main__":
    main()
