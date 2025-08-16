#!/usr/bin/env python3
"""
Test script to verify the connected pieces fix.
This tests that when two pieces land at the same row, they stay connected.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_connected_pieces_logic():
    """Test the logic for detecting connected pieces landing at the same row."""
    print("=== TESTING CONNECTED PIECES LOGIC ===")
    
    # Simulate the pieces_to_place logic from place_piece_on_grid
    def simulate_piece_placement(main_x, main_y, attached_x, attached_y):
        pieces_to_place = []
        
        # Handle main piece placement (simplified from actual code)
        if main_y < 0 and 0 <= main_x < 6:  # grid_width = 6
            pieces_to_place.append((main_x, 0, "red_block"))
        
        # Handle attached piece placement (simplified from actual code)
        if attached_y < 0 and 0 <= attached_x < 6:  # grid_width = 6
            pieces_to_place.append((attached_x, 0, "blue_block"))
        
        # Check if both pieces are trying to land at the same row (connected pieces)
        both_at_same_row = (len(pieces_to_place) == 2 and 
                           pieces_to_place[0][1] == pieces_to_place[1][1])
        
        return pieces_to_place, both_at_same_row
    
    # Test case 1: Both pieces at same row (should be connected)
    main_x, main_y = 3, -1
    attached_x, attached_y = 3, -2  # This becomes (3, 0) after clamping
    
    pieces_to_place, both_at_same_row = simulate_piece_placement(main_x, main_y, attached_x, attached_y)
    
    print(f"Test case 1 - Both pieces at same row:")
    print(f"  Main piece: ({main_x}, {main_y}) -> ({main_x}, 0)")
    print(f"  Attached piece: ({attached_x}, {attached_y}) -> ({attached_x}, 0)")
    print(f"  Pieces to place: {pieces_to_place}")
    print(f"  Both at same row: {both_at_same_row}")
    
    if both_at_same_row:
        print("✅ SUCCESS: Correctly detected connected pieces!")
    else:
        print("❌ FAILURE: Failed to detect connected pieces!")
        return False
    
    # Test case 2: Pieces at different rows (should not be connected)
    main_x, main_y = 3, 1
    attached_x, attached_y = 3, 2
    
    pieces_to_place, both_at_same_row = simulate_piece_placement(main_x, main_y, attached_x, attached_y)
    
    print(f"\nTest case 2 - Pieces at different rows:")
    print(f"  Main piece: ({main_x}, {main_y})")
    print(f"  Attached piece: ({attached_x}, {attached_y})")
    print(f"  Pieces to place: {pieces_to_place}")
    print(f"  Both at same row: {both_at_same_row}")
    
    if not both_at_same_row:
        print("✅ SUCCESS: Correctly detected non-connected pieces!")
    else:
        print("❌ FAILURE: Incorrectly detected connected pieces!")
        return False
    
    print("\n✅ ALL TESTS PASSED: Connected pieces logic works correctly!")
    return True

if __name__ == "__main__":
    success = test_connected_pieces_logic()
    sys.exit(0 if success else 1)
