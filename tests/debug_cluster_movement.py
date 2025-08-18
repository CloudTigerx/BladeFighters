#!/usr/bin/env python3
"""
Debug script to understand cluster movement in gravity system.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
from core.puzzle_module import PuzzleEngine

def debug_cluster_movement():
    """Debug cluster movement in gravity system."""
    print("🔍 Debugging Cluster Movement...")
    
    # Initialize pygame and create engine
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    font = pygame.font.Font(None, 36)
    engine = PuzzleEngine(screen, font)
    
    # Create a simple test grid with a 2x2 cluster that should fall
    test_grid = [[None for _ in range(6)] for _ in range(13)]
    
    # Create a 2x2 red cluster at position (0, 8) and (0, 9) - FLOATING ABOVE BOTTOM
    test_grid[8][0] = "red_block"
    test_grid[8][1] = "red_block"
    test_grid[9][0] = "red_block"
    test_grid[9][1] = "red_block"
    
    # NO support at the bottom - cluster should fall
    # test_grid[12][0] = "green_block"  # Commented out to make cluster float
    # test_grid[12][1] = "green_block"  # Commented out to make cluster float
    
    engine.puzzle_grid = test_grid
    
    print("Initial grid state:")
    for y in range(8, 13):
        row = []
        for x in range(6):
            cell = test_grid[y][x]
            row.append(cell if cell else ".")
        print(f"Row {y}: {row}")
    
    # Test cluster detection
    print("\nTesting cluster detection...")
    clusters = engine.cluster_detector.find_all_clusters(engine.puzzle_grid)
    print(f"Found {len(clusters)} clusters")
    for i, cluster in enumerate(clusters):
        print(f"Cluster {i}: {cluster}")
        is_supported = engine.cluster_detector.is_cluster_supported(cluster, engine.puzzle_grid)
        print(f"  Supported: {is_supported}")
    
    # Apply gravity
    print("\nApplying gravity...")
    gravity_applied = engine.apply_gravity()
    print(f"Gravity applied: {gravity_applied}")
    
    print("\nFinal grid state:")
    for y in range(8, 13):
        row = []
        for x in range(6):
            cell = engine.puzzle_grid[y][x]
            row.append(cell if cell else ".")
        print(f"Row {y}: {row}")
    
    # Check what happened to the red cluster
    print("\nChecking red cluster positions:")
    red_positions = []
    for y in range(13):
        for x in range(6):
            if engine.puzzle_grid[y][x] == "red_block":
                red_positions.append((x, y))
    print(f"Red blocks found at: {red_positions}")
    
    # Check if cluster moved down as expected
    expected_positions = [(0, 10), (1, 10), (0, 11), (1, 11)]
    if set(red_positions) == set(expected_positions):
        print("✅ Cluster moved down correctly as a unit!")
    else:
        print("❌ Cluster did not move as expected")
        print(f"Expected: {expected_positions}")
        print(f"Actual: {red_positions}")

if __name__ == "__main__":
    debug_cluster_movement()
