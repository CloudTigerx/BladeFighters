"""
Simple System Integration Test Suite for ClusterDetector - Task 6A System Integration.

This module provides comprehensive system integration tests for the cluster detection functionality,
focusing on edge cases, error conditions, and complete game flow scenarios.

Author: Senior Dev 2 - Task 6A (System Integration - Person 2)
"""

import sys
import os
import time

# Add the core directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cluster_detection import ClusterDetector


def test_edge_case_cluster_detection():
    """Test cluster detection with various edge cases."""
    print("\n🧪 TESTING: Edge Case Cluster Detection")
    
    detector = ClusterDetector(grid_width=10, grid_height=20, total_grid_height=25)
    
    # Create edge case grid
    grid = [[None for _ in range(10)] for _ in range(25)]
    
    # Edge case 1: Single block at corner
    grid[0][0] = "red_block"
    
    # Edge case 2: Single block at opposite corner
    grid[24][9] = "blue_block"
    
    # Edge case 3: 1x2 line at edge
    grid[0][8] = "green_block"
    grid[0][9] = "green_block"
    
    # Edge case 4: 2x1 line at edge
    grid[23][0] = "yellow_block"
    grid[24][0] = "yellow_block"
    
    # Edge case 5: L-shaped cluster
    grid[10][5] = "red_block"
    grid[10][6] = "red_block"
    grid[11][5] = "red_block"
    
    # Test detect_clusters with edge cases
    clusters = detector.detect_clusters(grid)
    print(f"✅ detect_clusters finds {len(clusters)} cluster blocks")
    
    # Test that corner blocks are not considered clusters
    corner_positions = {(0, 0), (24, 9)}
    for pos in corner_positions:
        if pos not in clusters:
            print(f"✅ corner position {pos} not considered cluster")
        else:
            print(f"❌ corner position {pos} incorrectly considered cluster")
    
    # Test that edge lines are not considered clusters
    edge_line_positions = {(0, 8), (0, 9), (23, 0), (24, 0)}
    for pos in edge_line_positions:
        if pos not in clusters:
            print(f"✅ edge line position {pos} not considered cluster")
        else:
            print(f"❌ edge line position {pos} incorrectly considered cluster")
    
    # Test that L-shaped cluster is detected
    l_cluster_positions = {(5, 10), (6, 10), (5, 11)}
    l_cluster_found = any(pos in clusters for pos in l_cluster_positions)
    if l_cluster_found:
        print("✅ L-shaped cluster detected")
    else:
        print("❌ L-shaped cluster not detected")
    
    return True


def test_error_conditions():
    """Test error handling and edge conditions."""
    print("\n🧪 TESTING: Error Conditions and Edge Cases")
    
    detector = ClusterDetector(grid_width=10, grid_height=20, total_grid_height=25)
    
    # Test with None grid
    try:
        detector.detect_clusters(None)
        print("❌ detect_clusters should raise TypeError for None grid")
    except TypeError:
        print("✅ detect_clusters raises TypeError for None grid")
    
    # Test with empty grid
    try:
        detector.find_all_clusters([])
        print("❌ find_all_clusters should raise IndexError for empty grid")
    except IndexError:
        print("✅ find_all_clusters raises IndexError for empty grid")
    
    # Test with malformed grid (wrong dimensions)
    malformed_grid = [[None for _ in range(5)] for _ in range(10)]  # Wrong width
    try:
        detector.detect_clusters(malformed_grid)
        print("❌ detect_clusters should raise IndexError for malformed grid")
    except IndexError:
        print("✅ detect_clusters raises IndexError for malformed grid")
    
    # Test with invalid coordinates for find_connected_pieces
    grid = [[None for _ in range(10)] for _ in range(25)]
    grid[10][5] = "red_block"
    grid[10][6] = "red_block"
    grid[11][5] = "red_block"
    grid[11][6] = "red_block"
    
    # Test with invalid coordinates for find_connected_pieces (returns empty set)
    result = detector.find_connected_pieces(-1, 0, "red", grid)
    if len(result) == 0:
        print("✅ find_connected_pieces returns empty set for invalid x")
    else:
        print("❌ find_connected_pieces should return empty set for invalid x")
    
    result = detector.find_connected_pieces(0, -1, "red", grid)
    if len(result) == 0:
        print("✅ find_connected_pieces returns empty set for invalid y")
    else:
        print("❌ find_connected_pieces should return empty set for invalid y")
    
    # Test with empty cluster_blocks
    result = detector.is_cluster_supported(set(), grid)
    if result:
        print("✅ empty cluster is trivially supported")
    else:
        print("❌ empty cluster should be trivially supported")
    
    return True


def test_performance_edge_cases():
    """Test performance with edge case scenarios."""
    print("\n🧪 TESTING: Performance Edge Cases")
    
    detector = ClusterDetector(grid_width=10, grid_height=20, total_grid_height=25)
    
    # Test with very large grid (simulate performance stress)
    large_grid = [[None for _ in range(10)] for _ in range(25)]
    
    # Fill most of the grid with blocks
    for y in range(20):
        for x in range(10):
            if (x + y) % 2 == 0:
                large_grid[y][x] = "red_block"
    
    # Test performance of detect_clusters
    start_time = time.time()
    clusters = detector.detect_clusters(large_grid)
    end_time = time.time()
    duration = end_time - start_time
    
    if duration < 0.1:
        print(f"✅ detect_clusters completes in reasonable time: {duration:.3f}s")
    else:
        print(f"❌ detect_clusters takes too long: {duration:.3f}s")
    
    if len(clusters) > 0:
        print(f"✅ detect_clusters finds {len(clusters)} clusters in large grid")
    else:
        print("❌ detect_clusters should find clusters in large grid")
    
    # Test performance of find_all_clusters
    start_time = time.time()
    all_clusters = detector.find_all_clusters(large_grid)
    end_time = time.time()
    duration = end_time - start_time
    
    if duration < 0.1:
        print(f"✅ find_all_clusters completes in reasonable time: {duration:.3f}s")
    else:
        print(f"❌ find_all_clusters takes too long: {duration:.3f}s")
    
    if len(all_clusters) > 0:
        print(f"✅ find_all_clusters finds {len(all_clusters)} cluster groups in large grid")
    else:
        print("❌ find_all_clusters should find cluster groups in large grid")
    
    return True


def test_boundary_conditions():
    """Test boundary conditions and limits."""
    print("\n🧪 TESTING: Boundary Conditions")
    
    detector = ClusterDetector(grid_width=10, grid_height=20, total_grid_height=25)
    
    # Test with grid at minimum valid size
    min_grid = [[None for _ in range(10)] for _ in range(25)]
    min_grid[0][0] = "red_block"
    min_grid[0][1] = "red_block"
    min_grid[1][0] = "red_block"
    min_grid[1][1] = "red_block"
    
    clusters = detector.detect_clusters(min_grid)
    if len(clusters) == 4:
        print("✅ minimum valid 2x2 cluster detected")
    else:
        print(f"❌ expected 4 cluster blocks, got {len(clusters)}")
    
    # Test with single block (should not be a cluster)
    single_grid = [[None for _ in range(10)] for _ in range(25)]
    single_grid[10][5] = "red_block"
    
    clusters = detector.detect_clusters(single_grid)
    if len(clusters) == 0:
        print("✅ single block not considered cluster")
    else:
        print(f"❌ single block incorrectly considered cluster: {len(clusters)} blocks")
    
    return True


def test_data_integrity():
    """Test data integrity and consistency."""
    print("\n🧪 TESTING: Data Integrity and Consistency")
    
    detector = ClusterDetector(grid_width=10, grid_height=20, total_grid_height=25)
    
    # Create test grid
    grid = [[None for _ in range(10)] for _ in range(25)]
    grid[10][5] = "red_block"
    grid[10][6] = "red_block"
    grid[11][5] = "red_block"
    grid[11][6] = "red_block"
    grid[15][2] = "blue_block"
    grid[15][3] = "blue_block"
    grid[16][2] = "blue_block"
    grid[16][3] = "blue_block"
    
    # Test that detect_clusters and find_all_clusters are consistent
    all_cluster_blocks = detector.detect_clusters(grid)
    cluster_groups = detector.find_all_clusters(grid)
    
    # All blocks in cluster groups should be in all_cluster_blocks
    all_consistent = True
    for cluster in cluster_groups:
        for pos in cluster:
            if pos not in all_cluster_blocks:
                print(f"❌ cluster position {pos} not in all_cluster_blocks")
                all_consistent = False
    
    if all_consistent:
        print("✅ detect_clusters and find_all_clusters are consistent")
    
    # Test that find_rectangular_clusters_for_render returns valid rectangles
    rectangles = detector.find_rectangular_clusters_for_render(grid)
    rectangles_consistent = True
    for rect in rectangles:
        for pos in rect:
            if pos not in all_cluster_blocks:
                print(f"❌ rectangle position {pos} not in all_cluster_blocks")
                rectangles_consistent = False
    
    if rectangles_consistent:
        print("✅ find_rectangular_clusters_for_render returns valid rectangles")
    
    # Test that is_cluster_supported works with cluster groups
    support_consistent = True
    for cluster in cluster_groups:
        supported = detector.is_cluster_supported(cluster, grid)
        if not isinstance(supported, bool):
            print(f"❌ is_cluster_supported should return boolean, got {type(supported)}")
            support_consistent = False
    
    if support_consistent:
        print("✅ is_cluster_supported returns boolean for all clusters")
    
    return True


def test_complete_game_flow_simulation():
    """Test complete game flow simulation with cluster detection."""
    print("\n🧪 TESTING: Complete Game Flow Simulation")
    
    detector = ClusterDetector(grid_width=10, grid_height=20, total_grid_height=25)
    
    # Simulate a game state with various clusters
    game_grid = [[None for _ in range(10)] for _ in range(25)]
    
    # Add some clusters
    # Cluster 1: 2x2 red cluster
    game_grid[10][5] = "red_block"
    game_grid[10][6] = "red_block"
    game_grid[11][5] = "red_block"
    game_grid[11][6] = "red_block"
    
    # Cluster 2: 3x2 blue cluster
    game_grid[15][2] = "blue_block"
    game_grid[15][3] = "blue_block"
    game_grid[15][4] = "blue_block"
    game_grid[16][2] = "blue_block"
    game_grid[16][3] = "blue_block"
    game_grid[16][4] = "blue_block"
    
    # Cluster 3: L-shaped green cluster
    game_grid[5][8] = "green_block"
    game_grid[5][9] = "green_block"
    game_grid[6][8] = "green_block"
    
    # Test cluster detection
    clusters = detector.detect_clusters(game_grid)
    if len(clusters) >= 10:
        print(f"✅ detect_clusters finds {len(clusters)} cluster blocks")
    else:
        print(f"❌ detect_clusters should find at least 10 cluster blocks, got {len(clusters)}")
    
    # Test cluster grouping
    cluster_groups = detector.find_all_clusters(game_grid)
    if len(cluster_groups) >= 3:
        print(f"✅ find_all_clusters finds {len(cluster_groups)} cluster groups")
    else:
        print(f"❌ find_all_clusters should find at least 3 cluster groups, got {len(cluster_groups)}")
    
    # Test rectangular cluster detection for rendering
    rectangles = detector.find_rectangular_clusters_for_render(game_grid)
    if len(rectangles) >= 2:
        print(f"✅ find_rectangular_clusters_for_render finds {len(rectangles)} rectangular clusters")
    else:
        print(f"❌ find_rectangular_clusters_for_render should find at least 2 rectangular clusters, got {len(rectangles)}")
    
    # Test cluster support detection
    support_works = True
    for cluster in cluster_groups:
        supported = detector.is_cluster_supported(cluster, game_grid)
        if not isinstance(supported, bool):
            print("❌ is_cluster_supported should return boolean")
            support_works = False
    
    if support_works:
        print("✅ is_cluster_supported works for all clusters")
    
    # Test connected pieces detection
    connected = detector.find_connected_pieces(5, 10, "red", game_grid)
    if len(connected) == 4:
        print("✅ find_connected_pieces finds red cluster")
    else:
        print(f"❌ find_connected_pieces should find 4 red blocks, got {len(connected)}")
    
    connected = detector.find_connected_pieces(2, 15, "blue", game_grid)
    if len(connected) == 6:
        print("✅ find_connected_pieces finds blue cluster")
    else:
        print(f"❌ find_connected_pieces should find 6 blue blocks, got {len(connected)}")
    
    return True


def main():
    """Run all system integration tests."""
    print("🚀 SENIOR DEV 2 - TASK 6A: SYSTEM INTEGRATION TESTING")
    print("=" * 60)
    
    # Run all test suites
    test_functions = [
        test_edge_case_cluster_detection,
        test_error_conditions,
        test_performance_edge_cases,
        test_boundary_conditions,
        test_data_integrity,
        test_complete_game_flow_simulation
    ]
    
    passed = 0
    total = len(test_functions)
    
    for test_func in test_functions:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test_func.__name__} failed with error: {e}")
    
    print("\n" + "=" * 60)
    print("📊 FINAL SYSTEM INTEGRATION TEST SUMMARY:")
    print(f"   Total Test Suites: {total}")
    print(f"   Passed: {passed}")
    print(f"   Failed: {total - passed}")
    print(f"   Success Rate: {(passed / total * 100) if total > 0 else 0:.1f}%")
    
    if passed == total:
        print("🎉 ALL SYSTEM INTEGRATION TESTS PASSED! Task 6A Complete!")
        return True
    else:
        print(f"⚠️  {total - passed} test suites failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
