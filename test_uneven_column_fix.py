#!/usr/bin/env python3
"""
Test script to verify the uneven column teleportation fix.
This test creates a scenario where pieces fall on uneven columns and verifies
that they separate properly instead of teleporting.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pygame
from core.puzzle_module import PuzzleEngine

def test_uneven_column_separation():
    """Test that pieces separate properly when falling on uneven columns."""
    
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    font = pygame.font.Font(None, 36)
    
    # Create puzzle engine
    engine = PuzzleEngine(screen, font)
    
    # Set up an uneven column scenario
    # Create a tower in column 2 (height 3) and column 4 (height 1)
    engine.puzzle_grid[9][2] = 'red_block'    # Column 2, row 9
    engine.puzzle_grid[10][2] = 'blue_block'  # Column 2, row 10
    engine.puzzle_grid[11][2] = 'green_block' # Column 2, row 11
    
    engine.puzzle_grid[11][4] = 'yellow_block' # Column 4, row 11 (lower height)
    
    print("Test setup:")
    print("Column 2: Height 3 (rows 9, 10, 11)")
    print("Column 4: Height 1 (row 11)")
    print("Other columns: Empty")
    
    # Spawn a piece pair that will fall on the uneven columns
    engine.main_piece = 'red_block'
    engine.attached_piece = 'blue_block'
    engine.piece_position = [3, -1]  # Middle column, just above grid
    engine.attached_position = 1  # Right orientation (attached piece to the right)
    
    print(f"\nSpawned piece pair:")
    print(f"Main piece: {engine.main_piece} at position {engine.piece_position}")
    print(f"Attached piece: {engine.attached_piece} at orientation {engine.attached_position}")
    
    # Test the separation logic
    should_separate, separation_type = engine.physics.should_pieces_separate(
        engine.piece_position, engine.attached_position
    )
    
    print(f"\nSeparation check result:")
    print(f"Should separate: {should_separate}")
    print(f"Separation type: {separation_type}")
    
    # Simulate the piece falling to the collision point
    # Move the piece down to where it would collide
    engine.piece_position[1] = 10  # Move to row 10
    
    # Check separation again at collision point
    should_separate_collision, separation_type_collision = engine.physics.should_pieces_separate(
        engine.piece_position, engine.attached_position
    )
    
    print(f"\nSeparation check at collision point (row 10):")
    print(f"Should separate: {should_separate_collision}")
    print(f"Separation type: {separation_type_collision}")
    
    # Test individual fall status
    main_can_fall, attached_can_fall = engine.physics.get_individual_fall_status(
        engine.piece_position, engine.attached_position
    )
    
    print(f"\nIndividual fall status at collision point:")
    print(f"Main piece can fall: {main_can_fall}")
    print(f"Attached piece can fall: {attached_can_fall}")
    
    # Verify the fix works as expected
    expected_separation = True
    expected_type = 'attached'  # Attached piece should land, main should continue falling
    
    if should_separate_collision == expected_separation and separation_type_collision == expected_type:
        print(f"\n✅ TEST PASSED: Pieces separate correctly on uneven columns")
        print(f"Expected: separate={expected_separation}, type='{expected_type}'")
        print(f"Actual: separate={should_separate_collision}, type='{separation_type_collision}'")
    else:
        print(f"\n❌ TEST FAILED: Pieces don't separate correctly")
        print(f"Expected: separate={expected_separation}, type='{expected_type}'")
        print(f"Actual: separate={should_separate_collision}, type='{separation_type_collision}'")
    
    pygame.quit()
    return should_separate_collision == expected_separation and separation_type_collision == expected_type

if __name__ == "__main__":
    success = test_uneven_column_separation()
    sys.exit(0 if success else 1)
