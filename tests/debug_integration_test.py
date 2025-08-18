#!/usr/bin/env python3
"""
Debug script to understand the integration test issue.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
from core.puzzle_module import PuzzleEngine

def debug_integration_test():
    """Debug the integration test scenario."""
    print("🔍 Debugging Integration Test...")
    
    # Initialize pygame and create engine
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    font = pygame.font.Font(None, 36)
    engine = PuzzleEngine(screen, font)
    
    # Create the exact same test grid as in the integration test
    test_grid = [[None for _ in range(6)] for _ in range(13)]
    
    # Create a 2x2 red cluster
    test_grid[10][0] = "red_block"
    test_grid[10][1] = "red_block"
    test_grid[11][0] = "red_block"
    test_grid[11][1] = "red_block"
    
    # Create a 3x2 blue cluster
    test_grid[8][3] = "blue_block"
    test_grid[8][4] = "blue_block"
    test_grid[8][5] = "blue_block"
    test_grid[9][3] = "blue_block"
    test_grid[9][4] = "blue_block"
    test_grid[9][5] = "blue_block"
    
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
    
    # Remove support blocks to make clusters float
    test_grid[12][0] = None  # Remove support for red cluster
    test_grid[12][3] = None  # Remove support for blue cluster
    
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
    
    # Check what happened to the blue cluster
    print("\nChecking blue cluster positions:")
    blue_positions = []
    for y in range(13):
        for x in range(6):
            if engine.puzzle_grid[y][x] == "blue_block":
                blue_positions.append((x, y))
    print(f"Blue blocks found at: {blue_positions}")

if __name__ == "__main__":
    debug_integration_test()
