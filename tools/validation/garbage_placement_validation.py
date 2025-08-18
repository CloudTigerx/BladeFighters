#!/usr/bin/env python3
"""
GARBAGE PLACEMENT VALIDATION
============================

This script validates that garbage blocks:
1. Rotate through columns properly (1→6→2→5→3→4)
2. Spread evenly instead of stacking 5+ in one column
3. Fill vacant areas when columns are full
4. Follow the correct placement patterns

Run this to ensure garbage placement is working correctly!
"""

import sys
import os
import time
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
    
    # FIXED: Track placement order by checking rotation state progression
    # Since we can't easily track the exact order when placing multiple blocks,
    # let's verify the rotation state is correct and test the pattern step by step
    
    # Check rotation state after placement
    rotation_state = getattr(test_mode, '_garbage_rotation_index', 0)
    print(f"Rotation state after placement: {rotation_state}")
    
    # The rotation state should be 0 after placing 6 blocks (6 % 6 = 0)
    rotation_correct = rotation_state == 0
    
    if rotation_correct:
        print("✅ Rotation state is correct after 6 blocks!")
    else:
        print(f"❌ Rotation state is incorrect: expected 0, got {rotation_state}")
    
    # Now test step by step to verify the pattern
    print("\nVerifying pattern step by step...")
    
    # Reset rotation state
    test_mode._garbage_rotation_index = 0
    
    # Test each block individually
    step_by_step_pattern = []
    for i in range(6):
        # Clear the grid
        for row in range(engine.grid_height):
            for col in range(engine.grid_width):
                engine.puzzle_grid[row][col] = None
        
        # Place 1 block
        single_attack = {
            'type': 'garbage',
            'blocks_remaining': 1,
            'sprinkle_side': 'R',
            'handedness': 'R'
        }
        
        test_mode._place_garbage_attack_direct(engine, single_attack, 'enemy')
        
        # Find which column got the block
        placed_column = None
        for row in range(engine.grid_height):
            for col in range(engine.grid_width):
                if engine.puzzle_grid[row][col] == 'garbage_block':
                    placed_column = col
                    break
            if placed_column is not None:
                break
        
        step_by_step_pattern.append(placed_column)
        print(f"  Block {i+1}: Column {placed_column}")
    
    print(f"Step-by-step pattern: {step_by_step_pattern}")
    
    # Check if step-by-step pattern matches expected
    step_pattern_correct = step_by_step_pattern == expected_pattern
    
    if step_pattern_correct:
        print("✅ Step-by-step pattern matches expected!")
    else:
        print("❌ Step-by-step pattern is incorrect!")
        print(f"Expected: {expected_pattern}")
        print(f"Actual: {step_by_step_pattern}")
    
    # Overall test passes if both rotation state and step-by-step pattern are correct
    pattern_correct = rotation_correct and step_pattern_correct
    
    if pattern_correct:
        print("✅ Garbage follows correct rotation pattern!")
    else:
        print("❌ Garbage rotation pattern is incorrect!")
    
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
    
    # Fill columns 0 and 1 completely to test vacant area filling
    print("Filling columns 0 and 1 completely...")
    for row in range(engine.grid_height):
        engine.puzzle_grid[row][0] = 'filled_block'
        engine.puzzle_grid[row][1] = 'filled_block'
    
    # Test with 8 garbage blocks (should skip full columns and use others)
    test_attack = {
        'type': 'garbage',
        'blocks_remaining': 8,
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
    
    # Check that full columns (0 and 1) have no garbage
    full_columns_empty = column_counts[0] == 0 and column_counts[1] == 0
    
    if full_columns_empty:
        print("✅ Full columns correctly skipped!")
    else:
        print("❌ Garbage placed in full columns!")
    
    # Check that other columns got garbage
    other_columns_filled = sum(column_counts[2:]) > 0
    
    if other_columns_filled:
        print("✅ Vacant areas correctly filled!")
    else:
        print("❌ Vacant areas not filled!")
    
    return full_columns_empty and other_columns_filled

def test_garbage_large_payload():
    """Test that large garbage payloads don't stack excessively"""
    print("\n📦 TESTING LARGE GARBAGE PAYLOAD...")
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
    
    # Test with 30 garbage blocks (should distribute evenly)
    print("Testing with 30 garbage blocks...")
    
    test_attack = {
        'type': 'garbage',
        'blocks_remaining': 30,
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
    
    # Expected: Each column should have 5 blocks (30 blocks / 6 columns = 5 each)
    expected_per_column = 30 // 6
    max_per_column = max(column_counts)
    min_per_column = min(column_counts)
    
    print(f"\nExpected blocks per column: {expected_per_column}")
    print(f"Actual max per column: {max_per_column}")
    print(f"Actual min per column: {min_per_column}")
    
    # Check for excessive stacking (more than 6 blocks in any column)
    excessive_stacking = max_per_column > 6
    
    if not excessive_stacking:
        print("✅ No excessive stacking in large payload!")
    else:
        print(f"❌ Excessive stacking in large payload: {max_per_column} blocks in one column!")
    
    # Check distribution is reasonable (within 2 blocks of expected)
    distribution_reasonable = max_per_column <= expected_per_column + 2 and min_per_column >= expected_per_column - 2
    
    if distribution_reasonable:
        print("✅ Large payload distributed reasonably!")
    else:
        print("❌ Large payload distribution is poor!")
    
    return not excessive_stacking and distribution_reasonable

def test_garbage_multiple_payloads():
    """Test that multiple garbage payloads don't stack together"""
    print("\n🔄 TESTING MULTIPLE GARBAGE PAYLOADS...")
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
    
    # Test multiple payloads
    print("Testing multiple garbage payloads...")
    
    payloads = [
        {'blocks_remaining': 6, 'sprinkle_side': 'R'},
        {'blocks_remaining': 4, 'sprinkle_side': 'L'},
        {'blocks_remaining': 8, 'sprinkle_side': 'R'},
    ]
    
    total_placed = 0
    for i, payload in enumerate(payloads):
        print(f"Placing payload {i+1}: {payload['blocks_remaining']} blocks")
        
        test_attack = {
            'type': 'garbage',
            'blocks_remaining': payload['blocks_remaining'],
            'sprinkle_side': payload['sprinkle_side'],
            'handedness': 'R'
        }
        
        blocks_placed = test_mode._place_garbage_attack_direct(engine, test_attack, 'enemy')
        total_placed += blocks_placed
        print(f"  Placed {blocks_placed} blocks")
    
    print(f"Total placed: {total_placed} blocks")
    
    # Check column distribution
    column_counts = [0] * engine.grid_width
    for row in range(engine.grid_height):
        for col in range(engine.grid_width):
            if engine.puzzle_grid[row][col] == 'garbage_block':
                column_counts[col] += 1
    
    print("Final column distribution:")
    for i, count in enumerate(column_counts):
        print(f"  Column {i}: {count} blocks")
    
    # Check for excessive stacking (more than 4 blocks in any column)
    excessive_stacking = max(column_counts) > 4
    
    if not excessive_stacking:
        print("✅ Multiple payloads don't stack excessively!")
    else:
        print(f"❌ Multiple payloads stack excessively: {max(column_counts)} blocks in one column!")
    
    return not excessive_stacking

def main():
    """Run all garbage placement tests"""
    print("🗑️ GARBAGE PLACEMENT VALIDATION")
    print("=" * 60)
    print()
    
    # Run all tests
    rotation_ok = test_garbage_column_rotation()
    pattern_ok = test_garbage_rotation_pattern()
    fill_ok = test_garbage_fill_vacant_areas()
    large_ok = test_garbage_large_payload()
    multiple_ok = test_garbage_multiple_payloads()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 GARBAGE PLACEMENT TEST SUMMARY")
    print("=" * 60)
    
    all_passed = all([rotation_ok, pattern_ok, fill_ok, large_ok, multiple_ok])
    
    if all_passed:
        print("✅ ALL GARBAGE PLACEMENT TESTS PASSED!")
        print("Garbage blocks now:")
        print("  • Rotate through columns properly (1→6→2→5→3→4)")
        print("  • Spread evenly instead of stacking")
        print("  • Fill vacant areas when columns are full")
        print("  • Handle large payloads without excessive stacking")
        print("  • Multiple payloads don't stack together")
    else:
        print("❌ SOME GARBAGE PLACEMENT TESTS FAILED!")
        if not rotation_ok:
            print("  • Column rotation distribution issues")
        if not pattern_ok:
            print("  • Rotation pattern incorrect")
        if not fill_ok:
            print("  • Vacant area filling issues")
        if not large_ok:
            print("  • Large payload stacking issues")
        if not multiple_ok:
            print("  • Multiple payload stacking issues")
    
    print("\n🔧 RECOMMENDATIONS:")
    if all_passed:
        print("• Garbage placement is working correctly")
        print("• No more 5+ blocks stacking in one column")
        print("• Test in-game to verify behavior")
    else:
        print("• Review garbage placement logic")
        print("• Check column rotation implementation")
        print("• Verify vacant area handling")
        print("• Test with different payload sizes")

if __name__ == "__main__":
    main()
