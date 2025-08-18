#!/usr/bin/env python3
"""
Test script to verify cluster detection integration in gravity system.
This tests Task 4B - Method Replacement (Person 2) for Senior Dev 3.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
from core.puzzle_module import PuzzleEngine

def test_cluster_gravity_integration():
    """Test that cluster detection is properly integrated in gravity system."""
    print("🧪 Testing Cluster Detection Integration in Gravity System...")
    
    # Initialize pygame and create engine
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    font = pygame.font.Font(None, 36)
    engine = PuzzleEngine(screen, font)
    
    # Test 1: Verify ClusterDetector is properly initialized
    print("  ✅ Test 1: ClusterDetector initialization...")
    assert hasattr(engine, 'cluster_detector'), "ClusterDetector not initialized"
    assert engine.cluster_detector is not None, "ClusterDetector is None"
    print("    ✓ ClusterDetector properly initialized")
    
    # Test 2: Create a test grid with clusters
    print("  ✅ Test 2: Creating test grid with clusters...")
    test_grid = [[None for _ in range(6)] for _ in range(13)]
    
    # Create a 2x2 red cluster (floating above bottom)
    test_grid[8][0] = "red_block"
    test_grid[8][1] = "red_block"
    test_grid[9][0] = "red_block"
    test_grid[9][1] = "red_block"
    
    # Create a 3x2 blue cluster (floating above bottom)
    test_grid[6][3] = "blue_block"
    test_grid[6][4] = "blue_block"
    test_grid[6][5] = "blue_block"
    test_grid[7][3] = "blue_block"
    test_grid[7][4] = "blue_block"
    test_grid[7][5] = "blue_block"
    
    # Set the test grid
    engine.puzzle_grid = test_grid
    
    # Test 3: Verify cluster detection works
    print("  ✅ Test 3: Testing cluster detection...")
    clusters = engine.cluster_detector.find_all_clusters(engine.puzzle_grid)
    assert len(clusters) == 2, f"Expected 2 clusters, got {len(clusters)}"
    print(f"    ✓ Found {len(clusters)} clusters")
    
    # Test 4: Verify cluster support detection works
    print("  ✅ Test 4: Testing cluster support detection...")
    for cluster in clusters:
        is_supported = engine.cluster_detector.is_cluster_supported(cluster, engine.puzzle_grid)
        print(f"    ✓ Cluster support check: {is_supported}")
    
    # Test 5: Test gravity application with clusters
    print("  ✅ Test 5: Testing gravity with clusters...")
    
    # Create a scenario where clusters should fall (unsupported)
    # Remove the support blocks to make clusters float
    test_grid[12][0] = None  # Remove support for red cluster
    test_grid[12][3] = None  # Remove support for blue cluster
    
    # Apply gravity
    gravity_applied = engine.apply_gravity()
    print(f"    ✓ Gravity applied: {gravity_applied}")
    
    # Test 6: Verify clusters moved as units
    print("  ✅ Test 6: Verifying cluster integrity...")
    
    # Check that the red cluster is still intact and moved down
    red_cluster_intact = (
        engine.puzzle_grid[10][0] == "red_block" and
        engine.puzzle_grid[10][1] == "red_block" and
        engine.puzzle_grid[11][0] == "red_block" and
        engine.puzzle_grid[11][1] == "red_block"
    )
    
    # Check that the blue cluster is still intact and moved down
    blue_cluster_intact = (
        engine.puzzle_grid[10][3] == "blue_block" and
        engine.puzzle_grid[10][4] == "blue_block" and
        engine.puzzle_grid[10][5] == "blue_block" and
        engine.puzzle_grid[11][3] == "blue_block" and
        engine.puzzle_grid[11][4] == "blue_block" and
        engine.puzzle_grid[11][5] == "blue_block"
    )
    
    assert red_cluster_intact, "Red cluster integrity lost"
    assert blue_cluster_intact, "Blue cluster integrity lost"
    print("    ✓ Cluster integrity maintained")
    
    print("🎉 All cluster gravity integration tests passed!")
    return True

def test_individual_block_gravity():
    """Test that individual blocks (not in clusters) fall correctly."""
    print("🧪 Testing Individual Block Gravity...")
    
    # Initialize pygame and create engine
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    font = pygame.font.Font(None, 36)
    engine = PuzzleEngine(screen, font)
    
    # Create a test grid with individual blocks that should fall
    test_grid = [[None for _ in range(6)] for _ in range(13)]
    
    # Place individual blocks in the middle
    test_grid[5][2] = "red_block"
    test_grid[5][3] = "blue_block"
    
    # Place support blocks at the bottom
    test_grid[12][2] = "green_block"
    test_grid[12][3] = "green_block"
    
    engine.puzzle_grid = test_grid
    
    # Apply gravity
    gravity_applied = engine.apply_gravity()
    print(f"  ✓ Gravity applied: {gravity_applied}")
    
    # Verify blocks fell to the bottom
    assert engine.puzzle_grid[11][2] == "red_block", "Red block didn't fall correctly"
    assert engine.puzzle_grid[11][3] == "blue_block", "Blue block didn't fall correctly"
    print("  ✓ Individual blocks fell correctly")
    
    print("🎉 Individual block gravity test passed!")
    return True

def test_mixed_scenario():
    """Test a mixed scenario with both clusters and individual blocks."""
    print("🧪 Testing Mixed Scenario...")
    
    # Initialize pygame and create engine
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    font = pygame.font.Font(None, 36)
    engine = PuzzleEngine(screen, font)
    
    # Create a complex test grid
    test_grid = [[None for _ in range(6)] for _ in range(13)]
    
    # Create a 2x2 cluster
    test_grid[8][0] = "red_block"
    test_grid[8][1] = "red_block"
    test_grid[9][0] = "red_block"
    test_grid[9][1] = "red_block"
    
    # Create individual blocks
    test_grid[6][3] = "blue_block"
    test_grid[7][4] = "green_block"
    
    # Create support structure
    test_grid[12][0] = "yellow_block"
    test_grid[12][1] = "yellow_block"
    test_grid[12][3] = "yellow_block"
    test_grid[12][4] = "yellow_block"
    
    engine.puzzle_grid = test_grid
    
    # Apply gravity
    gravity_applied = engine.apply_gravity()
    print(f"  ✓ Gravity applied: {gravity_applied}")
    
    # Verify cluster moved as unit
    cluster_moved = (
        engine.puzzle_grid[10][0] == "red_block" and
        engine.puzzle_grid[10][1] == "red_block" and
        engine.puzzle_grid[11][0] == "red_block" and
        engine.puzzle_grid[11][1] == "red_block"
    )
    
    # Verify individual blocks fell
    individual_fell = (
        engine.puzzle_grid[11][3] == "blue_block" and
        engine.puzzle_grid[11][4] == "green_block"
    )
    
    assert cluster_moved, "Cluster didn't move as unit"
    assert individual_fell, "Individual blocks didn't fall correctly"
    print("  ✓ Mixed scenario handled correctly")
    
    print("🎉 Mixed scenario test passed!")
    return True

if __name__ == "__main__":
    try:
        print("🚀 Starting Cluster Gravity Integration Tests...")
        print("=" * 50)
        
        test_cluster_gravity_integration()
        test_individual_block_gravity()
        test_mixed_scenario()
        
        print("=" * 50)
        print("🎉 ALL TESTS PASSED! Task 4B integration successful!")
        print("✅ Cluster detection properly integrated in gravity system")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
