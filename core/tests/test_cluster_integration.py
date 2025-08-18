"""
Integration test suite for ClusterDetector class - Task 3B Integration Testing.

This module provides comprehensive integration tests for the cluster detection functionality,
ensuring that the migrated methods work correctly with other game systems like the renderer,
gravity system, and attack delivery system.

Author: Senior Dev 2 - Task 3B (Integration Testing)
"""

import sys
import os
from typing import List, Set, Tuple, Optional
from unittest.mock import Mock, MagicMock

# Add the core directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cluster_detection import ClusterDetector


class IntegrationTestRunner:
    """Integration test runner for ClusterDetector class."""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.total = 0
    
    def assert_equal(self, actual, expected, test_name):
        """Assert that actual equals expected."""
        self.total += 1
        if actual == expected:
            self.passed += 1
            print(f"✅ PASS: {test_name}")
        else:
            self.failed += 1
            print(f"❌ FAIL: {test_name}")
            print(f"   Expected: {expected}")
            print(f"   Actual:   {actual}")
    
    def assert_true(self, condition, test_name):
        """Assert that condition is True."""
        self.total += 1
        if condition:
            self.passed += 1
            print(f"✅ PASS: {test_name}")
        else:
            self.failed += 1
            print(f"❌ FAIL: {test_name}")
    
    def assert_false(self, condition, test_name):
        """Assert that condition is False."""
        self.total += 1
        if not condition:
            self.passed += 1
            print(f"✅ PASS: {test_name}")
        else:
            self.failed += 1
            print(f"❌ FAIL: {test_name}")
    
    def print_summary(self):
        """Print test summary."""
        print(f"\n📊 INTEGRATION TEST SUMMARY:")
        print(f"   Total: {self.total}")
        print(f"   Passed: {self.passed}")
        print(f"   Failed: {self.failed}")
        print(f"   Success Rate: {(self.passed/self.total*100):.1f}%" if self.total > 0 else "   Success Rate: N/A")


def create_empty_grid(width=10, height=25):
    """Create an empty grid for testing."""
    return [[None for _ in range(width)] for _ in range(height)]


def create_renderer_test_grid():
    """Create a grid with clusters for renderer integration testing."""
    grid = create_empty_grid()
    
    # 2x2 red cluster at (1, 1) - should be highlighted
    grid[1][1] = "red"
    grid[1][2] = "red"
    grid[2][1] = "red"
    grid[2][2] = "red"
    
    # 3x2 blue cluster at (5, 1) - should be highlighted
    grid[1][5] = "blue"
    grid[1][6] = "blue"
    grid[1][7] = "blue"
    grid[2][5] = "blue"
    grid[2][6] = "blue"
    grid[2][7] = "blue"
    
    # Single blocks - should not be highlighted
    grid[5][1] = "green"
    grid[5][5] = "yellow"
    
    return grid


def create_attack_delivery_test_grid():
    """Create a grid with clusters for attack delivery integration testing."""
    grid = create_empty_grid()
    
    # 2x2 red cluster at (1, 1) - should be protected from piercing
    grid[1][1] = "red"
    grid[1][2] = "red"
    grid[2][1] = "red"
    grid[2][2] = "red"
    
    # 2x2 blue cluster at (5, 1) - should be protected from piercing
    grid[1][5] = "blue"
    grid[1][6] = "blue"
    grid[2][5] = "blue"
    grid[2][6] = "blue"
    
    # Non-cluster blocks - can be pierced
    grid[5][1] = "green"
    grid[5][5] = "yellow"
    grid[6][1] = "green"
    grid[6][5] = "yellow"
    
    return grid


def create_gravity_test_grid():
    """Create a grid with floating clusters for gravity integration testing."""
    grid = create_empty_grid()
    
    # Floating 2x2 red cluster at (1, 5) - should fall
    grid[5][1] = "red"
    grid[5][2] = "red"
    grid[6][1] = "red"
    grid[6][2] = "red"
    
    # Supported 2x2 blue cluster at (5, 18) - should not fall
    grid[18][5] = "blue"
    grid[18][6] = "blue"
    grid[19][5] = "blue"
    grid[19][6] = "blue"
    
    # Support blocks
    grid[20][5] = "green"
    grid[20][6] = "green"
    
    return grid


def test_renderer_integration():
    """Test ClusterDetector integration with renderer system."""
    print("\n🧪 TESTING: Renderer Integration")
    runner = IntegrationTestRunner()
    detector = ClusterDetector(grid_width=10, grid_height=20, total_grid_height=25)
    
    # Test grid with clusters
    grid = create_renderer_test_grid()
    
    # Test find_rectangular_clusters_for_render (primary renderer method)
    rectangles = detector.find_rectangular_clusters_for_render(grid)
    runner.assert_equal(len(rectangles), 2, "renderer finds correct number of rectangular clusters")
    
    # Test that rectangles are non-overlapping (renderer requirement)
    all_cells = set()
    for rect in rectangles:
        intersection = rect & all_cells
        runner.assert_equal(len(intersection), 0, "renderer rectangles are non-overlapping")
        all_cells.update(rect)
    
    # Test that each rectangle contains the expected cluster
    red_cluster = {(1, 1), (1, 2), (2, 1), (2, 2)}
    blue_cluster = {(5, 1), (6, 1), (7, 1), (5, 2), (6, 2), (7, 2)}
    
    found_red = any(red_cluster.issubset(rect) for rect in rectangles)
    found_blue = any(blue_cluster.issubset(rect) for rect in rectangles)
    
    runner.assert_true(found_red, "renderer contains red cluster")
    runner.assert_true(found_blue, "renderer contains blue cluster")
    
    # Test fallback to find_all_clusters (renderer fallback behavior)
    all_clusters = detector.find_all_clusters(grid)
    runner.assert_equal(len(all_clusters), 2, "renderer fallback finds correct number of clusters")
    
    # Test that single blocks are not included (renderer should not highlight singles)
    single_blocks = {(1, 5), (5, 5)}
    for cluster in all_clusters:
        for block in single_blocks:
            runner.assert_false(block in cluster, f"renderer does not include single block {block}")
    
    return runner


def test_attack_delivery_integration():
    """Test ClusterDetector integration with attack delivery system."""
    print("\n🧪 TESTING: Attack Delivery Integration")
    runner = IntegrationTestRunner()
    detector = ClusterDetector(grid_width=10, grid_height=20, total_grid_height=25)
    
    # Test grid with clusters
    grid = create_attack_delivery_test_grid()
    
    # Test find_all_clusters (primary attack delivery method)
    clusters = detector.find_all_clusters(grid)
    runner.assert_equal(len(clusters), 2, "attack delivery finds correct number of clusters")
    
    # Collect all cluster cells (attack delivery logic)
    cluster_cells = set()
    for cluster in clusters:
        cluster_cells.update(cluster)
    
    # Test that cluster cells are protected from piercing
    red_cluster_cells = {(1, 1), (1, 2), (2, 1), (2, 2)}
    blue_cluster_cells = {(5, 1), (6, 1), (5, 2), (6, 2)}
    
    for cell in red_cluster_cells:
        runner.assert_true(cell in cluster_cells, f"attack delivery protects red cluster cell {cell}")
    
    for cell in blue_cluster_cells:
        runner.assert_true(cell in cluster_cells, f"attack delivery protects blue cluster cell {cell}")
    
    # Test that non-cluster cells are not protected
    non_cluster_cells = {(1, 5), (5, 5), (6, 1), (6, 5)}
    for cell in non_cluster_cells:
        if cell not in red_cluster_cells and cell not in blue_cluster_cells:
            runner.assert_false(cell in cluster_cells, f"attack delivery allows piercing of non-cluster cell {cell}")
    
    # Test fallback to find_rectangular_clusters_for_render (attack delivery fallback)
    rectangles = detector.find_rectangular_clusters_for_render(grid)
    fallback_cluster_cells = set()
    for rect in rectangles:
        fallback_cluster_cells.update(rect)
    
    # Verify fallback provides similar protection
    for cell in red_cluster_cells:
        runner.assert_true(cell in fallback_cluster_cells, f"attack delivery fallback protects red cluster cell {cell}")
    
    for cell in blue_cluster_cells:
        runner.assert_true(cell in fallback_cluster_cells, f"attack delivery fallback protects blue cluster cell {cell}")
    
    return runner


def test_gravity_integration():
    """Test ClusterDetector integration with gravity system."""
    print("\n🧪 TESTING: Gravity Integration")
    runner = IntegrationTestRunner()
    detector = ClusterDetector(grid_width=10, grid_height=20, total_grid_height=25)
    
    # Test grid with floating and supported clusters
    grid = create_gravity_test_grid()
    
    # Test find_all_clusters (gravity system uses this)
    clusters = detector.find_all_clusters(grid)
    runner.assert_equal(len(clusters), 2, "gravity finds correct number of clusters")
    
    # Test is_cluster_supported for each cluster
    for cluster in clusters:
        supported = detector.is_cluster_supported(cluster, grid)
        
        # Check if this is the floating cluster (should not be supported)
        if (1, 5) in cluster:  # Floating red cluster
            runner.assert_false(supported, "gravity correctly identifies floating cluster as unsupported")
        elif (5, 18) in cluster:  # Supported blue cluster
            runner.assert_true(supported, "gravity correctly identifies supported cluster as supported")
    
    # Test detect_clusters (gravity system also uses this)
    all_cluster_blocks = detector.detect_clusters(grid)
    runner.assert_true(len(all_cluster_blocks) > 0, "gravity detects cluster blocks")
    
    # Verify that floating cluster blocks are included
    floating_blocks = {(1, 5), (1, 6), (2, 5), (2, 6)}
    for block in floating_blocks:
        runner.assert_true(block in all_cluster_blocks, f"gravity includes floating cluster block {block}")
    
    return runner


def test_strike_block_filtering():
    """Test that strike blocks are properly filtered in integration scenarios."""
    print("\n🧪 TESTING: Strike Block Filtering")
    runner = IntegrationTestRunner()
    detector = ClusterDetector(grid_width=10, grid_height=20, total_grid_height=25)
    
    # Create grid with strike blocks
    grid = create_empty_grid()
    
    # 2x2 cluster with one strike block - should not be a valid cluster
    grid[1][1] = "red"
    grid[1][2] = "red_strike"  # Strike block
    grid[2][1] = "red"
    grid[2][2] = "red"
    
    # Test detect_clusters (should not detect cluster with strike)
    clusters = detector.detect_clusters(grid)
    runner.assert_equal(clusters, set(), "strike blocks prevent cluster detection")
    
    # Test find_all_clusters (should not find clusters with strikes)
    all_clusters = detector.find_all_clusters(grid)
    runner.assert_equal(all_clusters, [], "strike blocks prevent cluster grouping")
    
    # Test find_rectangular_clusters_for_render (should not render clusters with strikes)
    rectangles = detector.find_rectangular_clusters_for_render(grid)
    runner.assert_equal(rectangles, [], "strike blocks prevent rectangular cluster rendering")
    
    return runner


def test_garbage_block_filtering():
    """Test that garbage blocks are properly filtered in integration scenarios."""
    print("\n🧪 TESTING: Garbage Block Filtering")
    runner = IntegrationTestRunner()
    detector = ClusterDetector(grid_width=10, grid_height=20, total_grid_height=25)
    
    # Create grid with garbage blocks
    grid = create_empty_grid()
    
    # 2x2 cluster with one garbage block - should not be a valid cluster
    grid[1][1] = "red"
    grid[1][2] = "red_garbage"  # Garbage block
    grid[2][1] = "red"
    grid[2][2] = "red"
    
    # Test detect_clusters (should not detect cluster with garbage)
    clusters = detector.detect_clusters(grid)
    runner.assert_equal(clusters, set(), "garbage blocks prevent cluster detection")
    
    # Test find_all_clusters (should not find clusters with garbage)
    all_clusters = detector.find_all_clusters(grid)
    runner.assert_equal(all_clusters, [], "garbage blocks prevent cluster grouping")
    
    # Test find_rectangular_clusters_for_render (should not render clusters with garbage)
    rectangles = detector.find_rectangular_clusters_for_render(grid)
    runner.assert_equal(rectangles, [], "garbage blocks prevent rectangular cluster rendering")
    
    return runner


def test_renderer_cluster_animation_integration():
    """Test ClusterDetector integration with renderer cluster animation system."""
    print("\n🧪 TESTING: Renderer Cluster Animation Integration")
    runner = IntegrationTestRunner()
    detector = ClusterDetector(grid_width=10, grid_height=20, total_grid_height=25)
    
    # Create grid with clusters for animation testing
    grid = create_empty_grid()
    
    # 2x2 red cluster - should be animated
    grid[1][1] = "red"
    grid[1][2] = "red"
    grid[2][1] = "red"
    grid[2][2] = "red"
    
    # 3x2 blue cluster - should be animated
    grid[1][5] = "blue"
    grid[1][6] = "blue"
    grid[1][7] = "blue"
    grid[2][5] = "blue"
    grid[2][6] = "blue"
    grid[2][7] = "blue"
    
    # Test find_rectangular_clusters_for_render (used for animation)
    rectangles = detector.find_rectangular_clusters_for_render(grid)
    runner.assert_equal(len(rectangles), 2, "animation system finds correct number of clusters")
    
    # Test that clusters are large enough for animation (4+ blocks)
    for rect in rectangles:
        runner.assert_true(len(rect) >= 4, f"animation cluster has sufficient size: {len(rect)} blocks")
    
    # Test that clusters don't contain strike blocks (animation requirement)
    for rect in rectangles:
        has_strike = False
        for x, y in rect:
            if grid[y][x] and ('strike' in str(grid[y][x])):
                has_strike = True
                break
        runner.assert_false(has_strike, "animation clusters contain no strike blocks")
    
    return runner


def test_performance_integration():
    """Test ClusterDetector performance in integration scenarios."""
    print("\n🧪 TESTING: Performance Integration")
    runner = IntegrationTestRunner()
    detector = ClusterDetector(grid_width=10, grid_height=20, total_grid_height=25)
    
    # Create a large grid with many clusters
    grid = create_empty_grid()
    
    # Add multiple clusters across the grid
    cluster_positions = [
        # Row 1 clusters
        (1, 1, 2, 2), (5, 1, 2, 2), (1, 5, 2, 2), (5, 5, 2, 2),
        # Row 10 clusters
        (1, 10, 2, 2), (5, 10, 2, 2), (1, 15, 2, 2), (5, 15, 2, 2)
    ]
    
    for start_x, start_y, width, height in cluster_positions:
        color = "red" if (start_x + start_y) % 2 == 0 else "blue"
        for x in range(start_x, start_x + width):
            for y in range(start_y, start_y + height):
                grid[y][x] = color
    
    # Test performance of detect_clusters
    import time
    start_time = time.time()
    clusters = detector.detect_clusters(grid)
    detect_time = time.time() - start_time
    
    runner.assert_true(detect_time < 0.1, f"detect_clusters completes in reasonable time: {detect_time:.3f}s")
    
    # Test performance of find_all_clusters
    start_time = time.time()
    all_clusters = detector.find_all_clusters(grid)
    find_all_time = time.time() - start_time
    
    runner.assert_true(find_all_time < 0.1, f"find_all_clusters completes in reasonable time: {find_all_time:.3f}s")
    
    # Test performance of find_rectangular_clusters_for_render
    start_time = time.time()
    rectangles = detector.find_rectangular_clusters_for_render(grid)
    rect_time = time.time() - start_time
    
    runner.assert_true(rect_time < 0.1, f"find_rectangular_clusters_for_render completes in reasonable time: {rect_time:.3f}s")
    
    # Verify results are correct
    runner.assert_equal(len(clusters), 32, "performance test detects correct number of cluster blocks")
    runner.assert_equal(len(all_clusters), 8, "performance test groups clusters correctly")
    runner.assert_equal(len(rectangles), 8, "performance test finds correct number of rectangles")
    
    return runner


def test_error_handling_integration():
    """Test ClusterDetector error handling in integration scenarios."""
    print("\n🧪 TESTING: Error Handling Integration")
    runner = IntegrationTestRunner()
    detector = ClusterDetector(grid_width=10, grid_height=20, total_grid_height=25)
    
    # Test with None grid
    try:
        clusters = detector.detect_clusters(None)
        runner.assert_true(False, "detect_clusters should handle None grid gracefully")
    except Exception:
        runner.assert_true(True, "detect_clusters handles None grid with exception")
    
    # Test with empty grid
    empty_grid = []
    try:
        clusters = detector.detect_clusters(empty_grid)
        runner.assert_true(False, "detect_clusters should handle empty grid gracefully")
    except Exception:
        runner.assert_true(True, "detect_clusters handles empty grid with exception")
    
    # Test with malformed grid
    malformed_grid = [[None, None], [None]]  # Inconsistent row lengths
    try:
        clusters = detector.detect_clusters(malformed_grid)
        runner.assert_true(False, "detect_clusters should handle malformed grid gracefully")
    except Exception:
        runner.assert_true(True, "detect_clusters handles malformed grid with exception")
    
    # Test with invalid cluster blocks for is_cluster_supported
    grid = create_empty_grid()
    invalid_cluster = {(100, 100), (-1, -1)}  # Out of bounds
    try:
        supported = detector.is_cluster_supported(invalid_cluster, grid)
        runner.assert_true(True, "is_cluster_supported handles invalid cluster blocks gracefully")
    except Exception:
        runner.assert_true(False, "is_cluster_supported should handle invalid cluster blocks")
    
    return runner


def main():
    """Run all integration tests."""
    print("🚀 SENIOR DEV 2 - TASK 3B: INTEGRATION TESTING")
    print("=" * 60)
    
    # Run all integration test suites
    test_suites = [
        test_renderer_integration,
        test_attack_delivery_integration,
        test_gravity_integration,
        test_strike_block_filtering,
        test_garbage_block_filtering,
        test_renderer_cluster_animation_integration,
        test_performance_integration,
        test_error_handling_integration
    ]
    
    total_passed = 0
    total_failed = 0
    total_tests = 0
    
    for test_suite in test_suites:
        runner = test_suite()
        total_passed += runner.passed
        total_failed += runner.failed
        total_tests += runner.total
    
    # Print final summary
    print("\n" + "=" * 60)
    print("📊 FINAL INTEGRATION TEST SUMMARY:")
    print(f"   Total Tests: {total_tests}")
    print(f"   Passed: {total_passed}")
    print(f"   Failed: {total_failed}")
    if total_tests > 0:
        success_rate = (total_passed / total_tests) * 100
        print(f"   Success Rate: {success_rate:.1f}%")
        
        if success_rate == 100:
            print("🎉 ALL INTEGRATION TESTS PASSED! Task 3B Integration Testing Complete!")
        else:
            print("⚠️  Some integration tests failed. Review and fix issues.")
    else:
        print("   Success Rate: N/A")
    
    return total_failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
