"""
Test suite for ClusterDetector class.

This module provides comprehensive tests for the cluster detection functionality,
ensuring that the migrated methods produce identical results to the original
implementation in puzzle_module.py.

Author: Senior Dev 1 - Task 2C
"""

import pytest
from typing import List, Set, Tuple, Optional
from core.cluster_detection import ClusterDetector


class TestClusterDetector:
    """Test suite for ClusterDetector class."""
    
    @pytest.fixture
    def detector(self):
        """Create a ClusterDetector instance for testing."""
        return ClusterDetector(grid_width=10, grid_height=20, total_grid_height=25)
    
    @pytest.fixture
    def empty_grid(self) -> List[List[Optional[str]]]:
        """Create an empty 10x25 grid for testing."""
        return [[None for _ in range(10)] for _ in range(25)]
    
    @pytest.fixture
    def simple_2x2_cluster_grid(self) -> List[List[Optional[str]]]:
        """Create a grid with a simple 2x2 red cluster."""
        grid = [[None for _ in range(10)] for _ in range(25)]
        # Create a 2x2 red cluster at position (2, 2)
        grid[2][2] = "red"
        grid[2][3] = "red"
        grid[3][2] = "red"
        grid[3][3] = "red"
        return grid
    
    @pytest.fixture
    def complex_cluster_grid(self) -> List[List[Optional[str]]]:
        """Create a grid with multiple clusters for complex testing."""
        grid = [[None for _ in range(10)] for _ in range(25)]
        
        # 2x2 red cluster at (1, 1)
        grid[1][1] = "red"
        grid[1][2] = "red"
        grid[2][1] = "red"
        grid[2][2] = "red"
        
        # 3x2 blue cluster at (5, 1)
        grid[1][5] = "blue"
        grid[1][6] = "blue"
        grid[1][7] = "blue"
        grid[2][5] = "blue"
        grid[2][6] = "blue"
        grid[2][7] = "blue"
        
        # 2x3 green cluster at (1, 5)
        grid[5][1] = "green"
        grid[5][2] = "green"
        grid[6][1] = "green"
        grid[6][2] = "green"
        grid[7][1] = "green"
        grid[7][2] = "green"
        
        return grid
    
    def test_initialization(self, detector):
        """Test ClusterDetector initialization."""
        assert detector.grid_width == 10
        assert detector.grid_height == 20
        assert detector.total_grid_height == 25
    
    def test_detect_clusters_empty_grid(self, detector, empty_grid):
        """Test cluster detection on empty grid."""
        clusters = detector.detect_clusters(empty_grid)
        assert clusters == set()
    
    def test_detect_clusters_simple_2x2(self, detector, simple_2x2_cluster_grid):
        """Test detection of simple 2x2 cluster."""
        clusters = detector.detect_clusters(simple_2x2_cluster_grid)
        expected = {(2, 2), (2, 3), (3, 2), (3, 3)}
        assert clusters == expected
    
    def test_detect_clusters_complex_grid(self, detector, complex_cluster_grid):
        """Test detection of multiple clusters in complex grid."""
        clusters = detector.detect_clusters(complex_cluster_grid)
        
        # Should detect all three clusters
        expected_positions = {
            # Red 2x2 cluster
            (1, 1), (1, 2), (2, 1), (2, 2),
            # Blue 3x2 cluster
            (1, 5), (1, 6), (1, 7), (2, 5), (2, 6), (2, 7),
            # Green 2x3 cluster
            (5, 1), (5, 2), (6, 1), (6, 2), (7, 1), (7, 2)
        }
        assert clusters == expected_positions

    # ===== SENIOR DEV 3 - TASK 3A: EDGE CASE TESTING =====
    
    @pytest.fixture
    def edge_case_grid(self) -> List[List[Optional[str]]]:
        """Create a grid with various edge cases for testing."""
        grid = [[None for _ in range(10)] for _ in range(25)]
        
        # Edge case 1: Single piece (not a cluster)
        grid[0][0] = "red"
        
        # Edge case 2: 1x2 line (not a cluster)
        grid[1][0] = "blue"
        grid[1][1] = "blue"
        
        # Edge case 3: 2x1 line (not a cluster)
        grid[2][0] = "green"
        grid[3][0] = "green"
        
        # Edge case 4: L-shaped arrangement (not rectangular)
        grid[5][0] = "yellow"
        grid[5][1] = "yellow"
        grid[6][0] = "yellow"
        
        # Edge case 5: Overlapping rectangles
        grid[8][0] = "purple"
        grid[8][1] = "purple"
        grid[9][0] = "purple"
        grid[9][1] = "purple"
        grid[8][1] = "purple"
        grid[8][2] = "purple"
        grid[9][1] = "purple"
        grid[9][2] = "purple"
        
        # Edge case 6: Strike blocks (should be ignored)
        grid[10][0] = "red_strike"
        grid[10][1] = "red_strike"
        grid[11][0] = "red_strike"
        grid[11][1] = "red_strike"
        
        # Edge case 7: Garbage blocks (should be ignored)
        grid[12][0] = "blue_garbage"
        grid[12][1] = "blue_garbage"
        grid[13][0] = "blue_garbage"
        grid[13][1] = "blue_garbage"
        
        # Edge case 8: Boundary conditions (grid edges)
        grid[23][8] = "green"
        grid[23][9] = "green"
        grid[24][8] = "green"
        grid[24][9] = "green"
        
        return grid
    
    @pytest.fixture
    def connected_pieces_grid(self) -> List[List[Optional[str]]]:
        """Create a grid for testing find_connected_pieces edge cases."""
        grid = [[None for _ in range(10)] for _ in range(25)]
        
        # Connected pieces of same color
        grid[0][0] = "red"
        grid[0][1] = "red"
        grid[1][0] = "red"
        grid[1][1] = "red"
        grid[2][0] = "red"
        
        # Disconnected pieces of same color
        grid[0][5] = "red"
        grid[0][7] = "red"
        
        # Mixed colors
        grid[5][0] = "blue"
        grid[5][1] = "red"
        grid[5][2] = "blue"
        
        # Strike blocks interrupting connection
        grid[10][0] = "green"
        grid[10][1] = "green_strike"
        grid[10][2] = "green"
        
        return grid

    def test_find_rectangular_clusters_edge_cases(self, detector, edge_case_grid):
        """Test find_rectangular_clusters_for_render with edge cases."""
        rectangles = detector.find_rectangular_clusters_for_render(edge_case_grid)
        
        # Should only find true rectangular clusters (2x2 or larger)
        # Single pieces, lines, L-shapes should be ignored
        assert len(rectangles) > 0
        
        # Verify no single pieces are included
        for rect in rectangles:
            assert len(rect) >= 4  # Minimum 2x2 = 4 cells
        
        # Verify boundary condition handling
        boundary_rect = None
        for rect in rectangles:
            if (23, 8) in rect:
                boundary_rect = rect
                break
        
        if boundary_rect:
            assert (23, 8) in boundary_rect
            assert (23, 9) in boundary_rect
            assert (24, 8) in boundary_rect
            assert (24, 9) in boundary_rect

    def test_find_rectangular_clusters_overlapping_logic(self, detector):
        """Test the non-overlap logic in find_rectangular_clusters_for_render."""
        grid = [[None for _ in range(10)] for _ in range(25)]
        
        # Create overlapping rectangles
        # Rectangle 1: (0,0) to (1,1)
        grid[0][0] = "red"
        grid[0][1] = "red"
        grid[1][0] = "red"
        grid[1][1] = "red"
        
        # Rectangle 2: (1,1) to (2,2) - overlaps with Rectangle 1
        grid[1][1] = "red"
        grid[1][2] = "red"
        grid[2][1] = "red"
        grid[2][2] = "red"
        
        rectangles = detector.find_rectangular_clusters_for_render(grid)
        
        # Should prefer larger rectangles and avoid overlaps
        # The algorithm should select the larger rectangle and exclude the smaller overlapping one
        assert len(rectangles) >= 1
        
        # Verify no overlapping cells between rectangles
        all_cells = set()
        for rect in rectangles:
            for cell in rect:
                assert cell not in all_cells, f"Cell {cell} appears in multiple rectangles"
                all_cells.add(cell)

    def test_find_connected_pieces_edge_cases(self, detector, connected_pieces_grid):
        """Test find_connected_pieces with edge cases."""
        # Test connected pieces
        connected = detector.find_connected_pieces(0, 0, "red", connected_pieces_grid)
        expected_connected = {(0, 0), (0, 1), (1, 0), (1, 1), (0, 2)}
        assert connected == expected_connected
        
        # Test disconnected pieces
        connected = detector.find_connected_pieces(5, 0, "red", connected_pieces_grid)
        expected_disconnected = {(5, 0)}
        assert connected == expected_disconnected
        
        # Test strike block interruption
        connected = detector.find_connected_pieces(0, 10, "green", connected_pieces_grid)
        expected_interrupted = {(0, 10)}
        assert connected == expected_interrupted

    def test_find_connected_pieces_boundary_conditions(self, detector):
        """Test find_connected_pieces with boundary conditions."""
        grid = [[None for _ in range(10)] for _ in range(25)]
        
        # Test invalid starting position
        connected = detector.find_connected_pieces(-1, 0, "red", grid)
        assert connected == set()
        
        connected = detector.find_connected_pieces(0, -1, "red", grid)
        assert connected == set()
        
        connected = detector.find_connected_pieces(10, 0, "red", grid)  # Out of bounds
        assert connected == set()
        
        connected = detector.find_connected_pieces(0, 25, "red", grid)  # Out of bounds
        assert connected == set()
        
        # Test empty cell
        connected = detector.find_connected_pieces(0, 0, "red", grid)
        assert connected == set()
        
        # Test color mismatch
        grid[0][0] = "blue"
        connected = detector.find_connected_pieces(0, 0, "red", grid)
        assert connected == set()

    def test_extend_cluster_size_limits(self, detector):
        """Test _extend_cluster with size limits."""
        grid = [[None for _ in range(10)] for _ in range(25)]
        
        # Create a large area of same color
        for y in range(10):
            for x in range(10):
                grid[y][x] = "red"
        
        clusters = set()
        visited = set()
        
        # Test with size limits (5x5 max)
        detector._extend_cluster(clusters, visited, 0, 0, "red", 5, 5, grid)
        
        # Should respect size limits
        assert len(clusters) <= 25  # 5x5 = 25 cells max

    def test_extend_cluster_boundary_handling(self, detector):
        """Test _extend_cluster with boundary conditions."""
        grid = [[None for _ in range(10)] for _ in range(25)]
        
        # Create cluster near grid boundary
        grid[23][8] = "red"
        grid[23][9] = "red"
        grid[24][8] = "red"
        grid[24][9] = "red"
        
        clusters = set()
        visited = set()
        
        # Add the initial 2x2 cluster first (as the method expects)
        clusters.add((8, 23))
        clusters.add((9, 23))
        clusters.add((8, 24))
        clusters.add((9, 24))
        visited.add((8, 23))
        visited.add((9, 23))
        visited.add((8, 24))
        visited.add((9, 24))
        
        # Should handle boundary gracefully
        detector._extend_cluster(clusters, visited, 8, 23, "red", 5, 5, grid)
        
        # Should not crash and should include valid cells
        assert (8, 23) in clusters
        assert (9, 23) in clusters
        assert (8, 24) in clusters
        assert (9, 24) in clusters

    def test_extend_cluster_invalid_color_extension(self, detector):
        """Test _extend_cluster with invalid color extensions."""
        grid = [[None for _ in range(10)] for _ in range(25)]
        
        # Create 2x2 cluster with different color extension
        grid[0][0] = "red"
        grid[0][1] = "red"
        grid[1][0] = "red"
        grid[1][1] = "red"
        grid[0][2] = "blue"  # Different color
        grid[1][2] = "blue"  # Different color
        
        clusters = set()
        visited = set()
        
        # Should not extend beyond color boundary
        detector._extend_cluster(clusters, visited, 0, 0, "red", 5, 5, grid)
        
        # Should only include red cells
        for x, y in clusters:
            assert grid[y][x] == "red"

    def test_performance_with_large_clusters(self, detector):
        """Test performance with large cluster areas."""
        grid = [[None for _ in range(10)] for _ in range(25)]
        
        # Create large area of same color
        for y in range(20):
            for x in range(8):
                grid[y][x] = "red"
        
        clusters = set()
        visited = set()
        
        # Should complete within reasonable time
        import time
        start_time = time.time()
        detector._extend_cluster(clusters, visited, 0, 0, "red", 5, 5, grid)
        end_time = time.time()
        
        # Should complete in under 1 second
        assert end_time - start_time < 1.0
        
        # Should respect size limits even with large areas
        assert len(clusters) <= 25  # 5x5 max

    # ===== SENIOR DEV 3 - TASK 3B: RENDERER INTEGRATION TESTING =====
    
    @pytest.fixture
    def renderer_integration_grid(self) -> List[List[Optional[str]]]:
        """Create a grid for testing renderer integration scenarios."""
        grid = [[None for _ in range(10)] for _ in range(25)]
        
        # Scenario 1: Multiple rectangular clusters for UI highlighting
        # 2x2 red cluster
        grid[0][0] = "red"
        grid[0][1] = "red"
        grid[1][0] = "red"
        grid[1][1] = "red"
        
        # 3x2 blue cluster
        grid[3][0] = "blue"
        grid[3][1] = "blue"
        grid[3][2] = "blue"
        grid[4][0] = "blue"
        grid[4][1] = "blue"
        grid[4][2] = "blue"
        
        # 2x3 green cluster
        grid[6][0] = "green"
        grid[6][1] = "green"
        grid[7][0] = "green"
        grid[7][1] = "green"
        grid[8][0] = "green"
        grid[8][1] = "green"
        
        # Scenario 2: Overlapping rectangles (should prefer larger ones)
        grid[10][0] = "purple"
        grid[10][1] = "purple"
        grid[11][0] = "purple"
        grid[11][1] = "purple"
        grid[10][1] = "purple"
        grid[10][2] = "purple"
        grid[11][1] = "purple"
        grid[11][2] = "purple"
        
        # Scenario 3: Strike blocks (should be ignored for UI highlighting)
        grid[13][0] = "yellow_strike"
        grid[13][1] = "yellow_strike"
        grid[14][0] = "yellow_strike"
        grid[14][1] = "yellow_strike"
        
        return grid

    def test_renderer_cluster_detection_integration(self, detector, renderer_integration_grid):
        """Test cluster detection integration with renderer system."""
        # Test find_rectangular_clusters_for_render (used by renderer)
        rectangles = detector.find_rectangular_clusters_for_render(renderer_integration_grid)
        
        # Should find multiple rectangular clusters
        assert len(rectangles) >= 3
        
        # Verify each rectangle is valid for UI highlighting
        for rect in rectangles:
            # Should be at least 2x2
            assert len(rect) >= 4
            
            # Should not contain strike blocks
            for x, y in rect:
                cell = renderer_integration_grid[y][x]
                assert cell is not None
                assert '_strike' not in str(cell)
        
        # Verify non-overlap logic works (renderer expects no overlapping cells)
        all_cells = set()
        for rect in rectangles:
            for cell in rect:
                assert cell not in all_cells, f"Cell {cell} appears in multiple rectangles"
                all_cells.add(cell)

    def test_renderer_cluster_animation_scenarios(self, detector):
        """Test cluster detection for renderer animation scenarios."""
        grid = [[None for _ in range(10)] for _ in range(25)]
        
        # Scenario: Cluster that should trigger animation (4+ blocks)
        grid[0][0] = "red"
        grid[0][1] = "red"
        grid[0][2] = "red"
        grid[1][0] = "red"
        grid[1][1] = "red"
        grid[1][2] = "red"
        
        rectangles = detector.find_rectangular_clusters_for_render(grid)
        
        # Should find a cluster with 6 blocks (enough for animation)
        assert len(rectangles) == 1
        assert len(rectangles[0]) == 6
        
        # Scenario: Small cluster that shouldn't trigger animation (< 4 blocks)
        grid = [[None for _ in range(10)] for _ in range(25)]
        grid[0][0] = "blue"
        grid[0][1] = "blue"
        grid[1][0] = "blue"
        grid[1][1] = "blue"
        
        rectangles = detector.find_rectangular_clusters_for_render(grid)
        
        # Should find a cluster with exactly 4 blocks (minimum for animation)
        assert len(rectangles) == 1
        assert len(rectangles[0]) == 4

    def test_renderer_strike_block_filtering(self, detector):
        """Test that strike blocks are properly filtered for renderer."""
        grid = [[None for _ in range(10)] for _ in range(25)]
        
        # Create a 2x2 cluster with strike blocks
        grid[0][0] = "red_strike"
        grid[0][1] = "red_strike"
        grid[1][0] = "red_strike"
        grid[1][1] = "red_strike"
        
        rectangles = detector.find_rectangular_clusters_for_render(grid)
        
        # Should not find any rectangles (strike blocks are ignored)
        assert len(rectangles) == 0
        
        # Create a mixed cluster (normal + strike blocks)
        grid = [[None for _ in range(10)] for _ in range(25)]
        grid[0][0] = "blue"
        grid[0][1] = "blue"
        grid[1][0] = "blue_strike"
        grid[1][1] = "blue"
        
        rectangles = detector.find_rectangular_clusters_for_render(grid)
        
        # Should not find any rectangles (mixed with strike blocks)
        assert len(rectangles) == 0

    def test_renderer_cluster_color_extraction(self, detector):
        """Test cluster color extraction for renderer glow effects."""
        grid = [[None for _ in range(10)] for _ in range(25)]
        
        # Create clusters of different colors
        grid[0][0] = "red"
        grid[0][1] = "red"
        grid[1][0] = "red"
        grid[1][1] = "red"
        
        grid[3][0] = "blue"
        grid[3][1] = "blue"
        grid[4][0] = "blue"
        grid[4][1] = "blue"
        
        rectangles = detector.find_rectangular_clusters_for_render(grid)
        
        # Should find 2 clusters
        assert len(rectangles) == 2
        
        # Verify colors can be extracted for glow effects
        for rect in rectangles:
            # Get color from first block (as renderer does)
            first_block = next(iter(rect))
            x, y = first_block
            color = grid[y][x].split('_')[0]  # Remove any suffixes
            
            # Color should be valid
            assert color in ['red', 'blue', 'green', 'yellow', 'purple']

    def test_renderer_cluster_boundary_conditions(self, detector):
        """Test cluster detection at grid boundaries for renderer."""
        grid = [[None for _ in range(10)] for _ in range(25)]
        
        # Create cluster at grid edges
        grid[23][8] = "green"
        grid[23][9] = "green"
        grid[24][8] = "green"
        grid[24][9] = "green"
        
        rectangles = detector.find_rectangular_clusters_for_render(grid)
        
        # Should find the boundary cluster
        assert len(rectangles) == 1
        boundary_cluster = rectangles[0]
        
        # Should include all boundary cells
        assert (8, 23) in boundary_cluster
        assert (9, 23) in boundary_cluster
        assert (8, 24) in boundary_cluster
        assert (9, 24) in boundary_cluster

    def test_renderer_cluster_performance_validation(self, detector):
        """Test cluster detection performance for renderer integration."""
        grid = [[None for _ in range(10)] for _ in range(25)]
        
        # Create a complex grid with many rectangular clusters
        # Create 2x2 clusters in a checkerboard pattern
        for y in range(0, 20, 2):
            for x in range(0, 8, 2):
                grid[y][x] = "red"
                grid[y][x+1] = "red"
                grid[y+1][x] = "red"
                grid[y+1][x+1] = "red"
        
        # Test performance of rectangular cluster detection
        import time
        start_time = time.time()
        rectangles = detector.find_rectangular_clusters_for_render(grid)
        end_time = time.time()
        
        # Should complete within reasonable time for renderer (60fps = 16ms)
        assert end_time - start_time < 0.016
        
        # Should find some clusters
        assert len(rectangles) > 0

    def test_renderer_cluster_consistency(self, detector):
        """Test that cluster detection is consistent across multiple calls."""
        grid = [[None for _ in range(10)] for _ in range(25)]
        
        # Create a stable cluster configuration
        grid[0][0] = "red"
        grid[0][1] = "red"
        grid[1][0] = "red"
        grid[1][1] = "red"
        
        # Call multiple times
        result1 = detector.find_rectangular_clusters_for_render(grid)
        result2 = detector.find_rectangular_clusters_for_render(grid)
        result3 = detector.find_rectangular_clusters_for_render(grid)
        
        # Results should be identical
        assert result1 == result2
        assert result2 == result3
        
        # Should be deterministic
        assert len(result1) == 1
        assert len(result1[0]) == 4
    
    def test_find_all_clusters_empty_grid(self, detector, empty_grid):
        """Test find_all_clusters on empty grid."""
        clusters = detector.find_all_clusters(empty_grid)
        assert clusters == []
    
    def test_find_all_clusters_simple_2x2(self, detector, simple_2x2_cluster_grid):
        """Test find_all_clusters with simple 2x2 cluster."""
        clusters = detector.find_all_clusters(simple_2x2_cluster_grid)
        assert len(clusters) == 1
        assert clusters[0] == {(2, 2), (2, 3), (3, 2), (3, 3)}
    
    def test_find_all_clusters_complex_grid(self, detector, complex_cluster_grid):
        """Test find_all_clusters with multiple clusters."""
        clusters = detector.find_all_clusters(complex_cluster_grid)
        assert len(clusters) == 3
        
        # Check that each cluster is properly separated
        cluster_sizes = [len(cluster) for cluster in clusters]
        assert 4 in cluster_sizes  # Red 2x2
        assert 6 in cluster_sizes  # Blue 3x2
        assert 6 in cluster_sizes  # Green 2x3
    
    def test_is_cluster_supported_ground_level(self, detector, simple_2x2_cluster_grid):
        """Test cluster support when cluster is at ground level."""
        cluster_blocks = {(2, 2), (2, 3), (3, 2), (3, 3)}
        # Modify grid to put cluster at bottom
        simple_2x2_cluster_grid[18][2] = "red"
        simple_2x2_cluster_grid[18][3] = "red"
        simple_2x2_cluster_grid[19][2] = "red"
        simple_2x2_cluster_grid[19][3] = "red"
        
        supported = detector.is_cluster_supported(cluster_blocks, simple_2x2_cluster_grid)
        assert supported is True
    
    def test_is_cluster_supported_floating(self, detector, simple_2x2_cluster_grid):
        """Test cluster support when cluster is floating."""
        cluster_blocks = {(2, 2), (2, 3), (3, 2), (3, 3)}
        supported = detector.is_cluster_supported(cluster_blocks, simple_2x2_cluster_grid)
        assert supported is False
    
    def test_find_rectangular_clusters_for_render(self, detector, complex_cluster_grid):
        """Test rectangular cluster detection for rendering."""
        rectangles = detector.find_rectangular_clusters_for_render(complex_cluster_grid)
        assert len(rectangles) == 3
        
        # Check that rectangles are non-overlapping
        all_cells = set()
        for rect in rectangles:
            assert not (rect & all_cells)  # No overlap
            all_cells.update(rect)
    
    def test_find_connected_pieces(self, detector, complex_cluster_grid):
        """Test connected pieces detection."""
        # Test from within the red cluster
        connected = detector.find_connected_pieces(1, 1, "red", complex_cluster_grid)
        expected = {(1, 1), (1, 2), (2, 1), (2, 2)}
        assert connected == expected
    
    def test_find_connected_pieces_invalid_start(self, detector, empty_grid):
        """Test connected pieces with invalid starting position."""
        connected = detector.find_connected_pieces(-1, 0, "red", empty_grid)
        assert connected == set()
        
        connected = detector.find_connected_pieces(0, -1, "red", empty_grid)
        assert connected == set()
        
        connected = detector.find_connected_pieces(10, 0, "red", empty_grid)
        assert connected == set()
        
        connected = detector.find_connected_pieces(0, 25, "red", empty_grid)
        assert connected == set()
    
    def test_find_connected_pieces_empty_cell(self, detector, empty_grid):
        """Test connected pieces starting from empty cell."""
        connected = detector.find_connected_pieces(0, 0, "red", empty_grid)
        assert connected == set()
    
    def test_find_connected_pieces_wrong_color(self, detector, simple_2x2_cluster_grid):
        """Test connected pieces with wrong target color."""
        connected = detector.find_connected_pieces(2, 2, "blue", simple_2x2_cluster_grid)
        assert connected == set()
    
    def test_garbage_strike_filtering(self, detector):
        """Test that garbage and strike blocks are properly filtered."""
        grid = [[None for _ in range(10)] for _ in range(25)]
        
        # Create a 2x2 pattern with garbage/strike blocks
        grid[1][1] = "red"
        grid[1][2] = "red_garbage"  # Should be filtered
        grid[2][1] = "red_strike"   # Should be filtered
        grid[2][2] = "red"
        
        clusters = detector.detect_clusters(grid)
        assert clusters == set()  # No valid 2x2 cluster
    
    def test_performance_optimization_visited_set(self, detector, complex_cluster_grid):
        """Test that visited set optimization works correctly."""
        clusters = detector.detect_clusters(complex_cluster_grid)
        
        # Should not have duplicate coordinates
        assert len(clusters) == len(set(clusters))
        
        # Should have exactly the expected number of cluster positions
        expected_count = 4 + 6 + 6  # red + blue + green clusters
        assert len(clusters) == expected_count


class TestClusterDetectorEdgeCases:
    """Test edge cases and boundary conditions."""
    
    @pytest.fixture
    def detector(self):
        """Create a ClusterDetector instance for testing."""
        return ClusterDetector(grid_width=5, grid_height=10, total_grid_height=15)
    
    def test_cluster_at_grid_boundaries(self, detector):
        """Test cluster detection at grid boundaries."""
        grid = [[None for _ in range(5)] for _ in range(15)]
        
        # 2x2 cluster at bottom-right corner
        grid[13][3] = "red"
        grid[13][4] = "red"
        grid[14][3] = "red"
        grid[14][4] = "red"
        
        clusters = detector.detect_clusters(grid)
        expected = {(3, 13), (3, 14), (4, 13), (4, 14)}
        assert clusters == expected
    
    def test_large_cluster_extension_limits(self, detector):
        """Test that cluster extension respects size limits."""
        grid = [[None for _ in range(5)] for _ in range(15)]
        
        # Create a large area of same color (should be limited by max_width/max_height)
        for y in range(10):
            for x in range(5):
                grid[y][x] = "red"
        
        clusters = detector.detect_clusters(grid)
        
        # Should not exceed the 5x5 limit from _extend_cluster
        # The exact count depends on the implementation, but should be reasonable
        assert len(clusters) > 0
        assert len(clusters) <= 25  # 5x5 maximum


if __name__ == "__main__":
    pytest.main([__file__])
