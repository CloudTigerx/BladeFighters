#!/usr/bin/env python3
"""
Debug script to reproduce and analyze the placement issue.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def debug_placement_logic():
    """Debug the placement logic to understand why pieces are separating."""
    print("=== DEBUGGING PLACEMENT LOGIC ===")
    
    # Simulate the exact scenario from the game
    main_x, main_y = 3, -1  # Main piece at row -1
    attached_x, attached_y = 3, -2  # Attached piece at row -2
    
    print(f"Original positions:")
    print(f"  Main piece: ({main_x}, {main_y})")
    print(f"  Attached piece: ({attached_x}, {attached_y})")
    
    # Simulate the placement logic
    pieces_to_place = []
    
    # Handle main piece placement
    if main_y < 0 and 0 <= main_x < 6:  # grid_width = 6
        pieces_to_place.append((main_x, 0, "red_block"))
        print(f"  Added main piece at ({main_x}, 0)")
    
    # Handle attached piece placement
    if attached_y < 0 and 0 <= attached_x < 6:  # grid_width = 6
        pieces_to_place.append((attached_x, 0, "blue_block"))
        print(f"  Added attached piece at ({attached_x}, 0)")
    
    print(f"Pieces to place: {pieces_to_place}")
    
    # Check if both pieces are trying to land at the same row
    both_at_same_row = (len(pieces_to_place) == 2 and 
                       pieces_to_place[0][1] == pieces_to_place[1][1])
    
    # Also check if pieces are at the same x-coordinate (vertical stack)
    both_at_same_x = (len(pieces_to_place) == 2 and 
                     pieces_to_place[0][0] == pieces_to_place[1][0])
    
    print(f"Both at same row: {both_at_same_row}")
    print(f"Both at same x: {both_at_same_x}")
    
    # Handle connected pieces (same row) or vertical stack (same x)
    should_use_connected_logic = both_at_same_row or both_at_same_x
    
    if should_use_connected_logic:
        print("✅ Connected pieces logic should be triggered!")
        
        # Simulate the connected placement logic
        main_x, main_y, main_piece = pieces_to_place[0]
        attached_x, attached_y, attached_piece = pieces_to_place[1]
        
        print(f"Connected placement:")
        print(f"  Main piece: {main_piece} at ({main_x}, {main_y})")
        print(f"  Attached piece: {attached_piece} at ({attached_x}, {attached_y})")
        
        # Check if they would be adjacent
        are_adjacent = abs(main_x - attached_x) == 1 and main_y == attached_y
        print(f"  Would be adjacent: {are_adjacent}")
        
        if not are_adjacent:
            print("❌ ISSUE: Pieces are at same row but not adjacent!")
            print("  This means they're at the same position and will collide.")
            
        # Check if this is a vertical stack case
        if both_at_same_x and not both_at_same_row:
            print("✅ This is a vertical stack case - pieces should be placed adjacent horizontally!")
        elif both_at_same_row:
            print("✅ This is a same-row case - pieces should be placed adjacent horizontally!")
    else:
        print("❌ Connected pieces logic NOT triggered!")
    
    return both_at_same_row

if __name__ == "__main__":
    debug_placement_logic()
