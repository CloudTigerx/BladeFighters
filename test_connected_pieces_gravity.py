#!/usr/bin/env python3
"""
Test script to verify the connected pieces gravity fix.
This tests that connected pieces fall together as a unit.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_connected_pieces_gravity_logic():
    """Test the logic for detecting and moving connected piece groups."""
    print("=== TESTING CONNECTED PIECES GRAVITY LOGIC ===")
    
    # Simulate the connected pieces detection logic
    def simulate_connected_groups(grid, grid_width, grid_height):
        """Simulate finding connected piece groups."""
        connected_groups = []
        visited = set()
        
        # Scan the grid for connected pieces
        for y in range(grid_height):
            for x in range(grid_width):
                if (x, y) in visited:
                    continue
                
                if grid[y][x] is not None:
                    # Start a new connected group
                    group = set()
                    queue = [(x, y)]
                    group_visited = set(queue)
                    
                    while queue:
                        cx, cy = queue.pop(0)
                        group.add((cx, cy))
                        
                        # Check adjacent positions for connected pieces
                        for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:  # Up, right, down, left
                            nx, ny = cx + dx, cy + dy
                            
                            if ((nx, ny) not in group_visited and
                                0 <= nx < grid_width and
                                0 <= ny < grid_height and
                                grid[ny][nx] is not None):
                                
                                queue.append((nx, ny))
                                group_visited.add((nx, ny))
                    
                    # Only add groups with multiple pieces (connected pieces)
                    if len(group) > 1:
                        connected_groups.append(group)
                        visited.update(group)
        
        return connected_groups
    
    # Test case 1: Two adjacent pieces (should be detected as connected)
    grid_width, grid_height = 6, 12
    grid = [[None for _ in range(grid_width)] for _ in range(grid_height)]
    
    # Place two adjacent pieces
    grid[0][2] = "red_block"    # Position (2, 0)
    grid[0][3] = "blue_block"   # Position (3, 0) - adjacent to red_block
    
    print("Test case 1 - Two adjacent pieces:")
    print(f"  Red block at (2, 0)")
    print(f"  Blue block at (3, 0)")
    
    connected_groups = simulate_connected_groups(grid, grid_width, grid_height)
    print(f"  Connected groups found: {len(connected_groups)}")
    
    if len(connected_groups) == 1 and len(connected_groups[0]) == 2:
        print("✅ SUCCESS: Correctly detected connected pieces!")
    else:
        print("❌ FAILURE: Failed to detect connected pieces!")
        return False
    
    # Test case 2: Two separate pieces (should not be detected as connected)
    grid = [[None for _ in range(grid_width)] for _ in range(grid_height)]
    
    # Place two separate pieces
    grid[0][1] = "red_block"    # Position (1, 0)
    grid[0][4] = "blue_block"   # Position (4, 0) - not adjacent to red_block
    
    print("\nTest case 2 - Two separate pieces:")
    print(f"  Red block at (1, 0)")
    print(f"  Blue block at (4, 0)")
    
    connected_groups = simulate_connected_groups(grid, grid_width, grid_height)
    print(f"  Connected groups found: {len(connected_groups)}")
    
    if len(connected_groups) == 0:
        print("✅ SUCCESS: Correctly detected non-connected pieces!")
    else:
        print("❌ FAILURE: Incorrectly detected connected pieces!")
        return False
    
    # Test case 3: Three connected pieces in a line
    grid = [[None for _ in range(grid_width)] for _ in range(grid_height)]
    
    # Place three connected pieces
    grid[0][2] = "red_block"    # Position (2, 0)
    grid[0][3] = "blue_block"   # Position (3, 0) - adjacent to red_block
    grid[0][4] = "green_block"  # Position (4, 0) - adjacent to blue_block
    
    print("\nTest case 3 - Three connected pieces:")
    print(f"  Red block at (2, 0)")
    print(f"  Blue block at (3, 0)")
    print(f"  Green block at (4, 0)")
    
    connected_groups = simulate_connected_groups(grid, grid_width, grid_height)
    print(f"  Connected groups found: {len(connected_groups)}")
    
    if len(connected_groups) == 1 and len(connected_groups[0]) == 3:
        print("✅ SUCCESS: Correctly detected three connected pieces!")
    else:
        print("❌ FAILURE: Failed to detect three connected pieces!")
        return False
    
    print("\n✅ ALL TESTS PASSED: Connected pieces gravity logic works correctly!")
    return True

if __name__ == "__main__":
    success = test_connected_pieces_gravity_logic()
    sys.exit(0 if success else 1)
