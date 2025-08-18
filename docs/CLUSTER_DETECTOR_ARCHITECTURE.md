# ClusterDetector Architecture Design
**Senior Dev 1 - Task 1C**

## Overview
This document outlines the architecture design for migrating cluster detection functionality from `puzzle_module.py` to a dedicated `core/cluster_detection.py` module.

## Current State Analysis

### Existing Cluster Methods (puzzle_module.py)
1. **`detect_clusters()`** (lines 1029-1086)
   - Main cluster detection algorithm
   - Returns: `set[tuple[int, int]]` - coordinates of blocks in clusters
   - Performance optimized with size limits (5x5 max)

2. **`_extend_cluster()`** (lines 1087-1134)
   - Helper method for extending clusters
   - Parameters: clusters, visited, start_x, start_y, color, max_width, max_height
   - Internal method (should be private in new module)

3. **`is_cluster_supported()`** (lines 1135-1171)
   - Check if cluster has support beneath it
   - Parameters: `cluster_blocks: set[tuple[int, int]]`
   - Returns: `bool`

4. **`find_all_clusters()`** (lines 1172-1234)
   - Find all separate cluster groups
   - Returns: `list[set[tuple[int, int]]]` - list of cluster sets

5. **`find_rectangular_clusters_for_render()`** (lines 1235-1332)
   - UI-specific rectangular clusters for rendering
   - Returns: `list[set[tuple[int, int]]]` - non-overlapping rectangles
   - Complex logic for UI clarity

6. **`find_connected_pieces()`** (lines 1333-1400)
   - Flood fill for connected pieces of same color
   - Parameters: `start_x, start_y, target_color`
   - Returns: `set[tuple[int, int]]`

### Current Dependencies
- **puzzle_renderer.py**: Uses `find_rectangular_clusters_for_render()` and `find_all_clusters()`
- **attack_delivery_committer.py**: Uses `find_all_clusters()` and `find_rectangular_clusters_for_render()`
- **puzzle_module.py internal**: Uses all methods for gravity and breaker systems

## Proposed Architecture

### 1. Module Structure
```
core/
├── cluster_detection.py          # Main module
├── __init__.py                   # Updated to export ClusterDetector
└── tests/
    └── test_cluster_detection.py # Unit tests
```

### 2. ClusterDetector Class Design

```python
class ClusterDetector:
    """
    Dedicated cluster detection engine for puzzle game mechanics.
    
    This class encapsulates all cluster detection logic, providing a clean
    interface for finding, analyzing, and managing clusters in the puzzle grid.
    """
    
    def __init__(self, grid_width: int, grid_height: int, total_grid_height: int):
        """
        Initialize the cluster detector.
        
        Args:
            grid_width: Width of the puzzle grid
            grid_height: Height of the visible grid
            total_grid_height: Total height including hidden areas
        """
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.total_grid_height = total_grid_height
        
    def detect_clusters(self, puzzle_grid: list[list[str | None]]) -> set[tuple[int, int]]:
        """
        Detect clusters of blocks that are 2+ blocks wide and 2+ blocks high.
        
        Args:
            puzzle_grid: 2D grid representation of the puzzle board
            
        Returns:
            Set of (x, y) coordinates of blocks in clusters
        """
        pass
        
    def find_all_clusters(self, puzzle_grid: list[list[str | None]]) -> list[set[tuple[int, int]]]:
        """
        Find all clusters in the grid and return them as separate groups.
        
        Args:
            puzzle_grid: 2D grid representation of the puzzle board
            
        Returns:
            List of sets, where each set contains the (x, y) coordinates of a cluster
        """
        pass
        
    def is_cluster_supported(self, cluster_blocks: set[tuple[int, int]], 
                           puzzle_grid: list[list[str | None]]) -> bool:
        """
        Check if a cluster has any support beneath it.
        
        Args:
            cluster_blocks: Set of (x, y) coordinates that form the cluster
            puzzle_grid: 2D grid representation of the puzzle board
            
        Returns:
            True if the cluster is supported, False otherwise
        """
        pass
        
    def find_rectangular_clusters_for_render(self, puzzle_grid: list[list[str | None]]) -> list[set[tuple[int, int]]]:
        """
        Find only true rectangular clusters for UI highlighting.
        
        Args:
            puzzle_grid: 2D grid representation of the puzzle board
            
        Returns:
            List of sets, each set containing the (x, y) cells of one rectangle
        """
        pass
        
    def find_connected_pieces(self, start_x: int, start_y: int, target_color: str,
                            puzzle_grid: list[list[str | None]]) -> set[tuple[int, int]]:
        """
        Use flood fill to find all connected pieces of the same color.
        
        Args:
            start_x: Starting x coordinate
            start_y: Starting y coordinate
            target_color: Color to search for
            puzzle_grid: 2D grid representation of the puzzle board
            
        Returns:
            Set of (x, y) coordinates of connected pieces
        """
        pass
        
    def _extend_cluster(self, clusters: set[tuple[int, int]], visited: set[tuple[int, int]],
                       start_x: int, start_y: int, color: str, max_width: int, max_height: int,
                       puzzle_grid: list[list[str | None]]) -> None:
        """
        Helper method to extend clusters efficiently with size limits.
        
        Args:
            clusters: Set to add cluster coordinates to
            visited: Set of already visited coordinates
            start_x: Starting x coordinate
            start_y: Starting y coordinate
            color: Color of the cluster
            max_width: Maximum width to extend
            max_height: Maximum height to extend
            puzzle_grid: 2D grid representation of the puzzle board
        """
        pass
```

### 3. Integration Strategy

#### Backward Compatibility Layer
```python
# In puzzle_module.py (temporary during migration)
from core.cluster_detection import ClusterDetector

class PuzzleEngine:
    def __init__(self, ...):
        # ... existing initialization ...
        self.cluster_detector = ClusterDetector(self.grid_width, self.grid_height, self.total_grid_height)
    
    # Temporary wrapper methods for backward compatibility
    def detect_clusters(self):
        return self.cluster_detector.detect_clusters(self.puzzle_grid)
        
    def find_all_clusters(self):
        return self.cluster_detector.find_all_clusters(self.puzzle_grid)
        
    def is_cluster_supported(self, cluster_blocks):
        return self.cluster_detector.is_cluster_supported(cluster_blocks, self.puzzle_grid)
        
    def find_rectangular_clusters_for_render(self):
        return self.cluster_detector.find_rectangular_clusters_for_render(self.puzzle_grid)
        
    def find_connected_pieces(self, start_x, start_y, target_color):
        return self.cluster_detector.find_connected_pieces(start_x, start_y, target_color, self.puzzle_grid)
```

#### Direct Integration Points
```python
# For systems that can be updated immediately
from core.cluster_detection import ClusterDetector

# Initialize with grid dimensions
detector = ClusterDetector(grid_width, grid_height, total_grid_height)

# Use directly
clusters = detector.detect_clusters(puzzle_grid)
rectangular_clusters = detector.find_rectangular_clusters_for_render(puzzle_grid)
```

### 4. Design Principles

1. **Separation of Concerns**: Cluster logic completely separated from puzzle logic
2. **Dependency Injection**: Grid passed as parameter, not stored as instance variable
3. **Immutability**: Methods don't modify the input grid
4. **Performance**: Maintain existing performance optimizations
5. **Backward Compatibility**: Wrapper methods during migration phase
6. **Testability**: Easy to unit test with mock grids
7. **Extensibility**: Clean interface for future enhancements

### 5. Migration Benefits

1. **Cleaner Code**: Puzzle module focused on game logic, not cluster detection
2. **Reusability**: Cluster detection can be used by other systems
3. **Testability**: Isolated cluster logic easier to test
4. **Maintainability**: Changes to cluster logic don't affect puzzle logic
5. **Performance**: Potential for optimization without affecting other systems

### 6. Risk Mitigation

1. **Gradual Migration**: Keep old methods during transition
2. **Comprehensive Testing**: Test both old and new implementations
3. **Performance Monitoring**: Ensure no performance regressions
4. **Rollback Plan**: Easy to revert if issues arise

## Next Steps

1. **Senior Dev 1**: Create `core/cluster_detection.py` with ClusterDetector class
2. **Senior Dev 2**: Complete code audit and dependency mapping
3. **Senior Dev 3**: Prepare for method migration tasks
4. **Team**: Review architecture design and provide feedback

## Success Criteria

- [ ] ClusterDetector class created with all 6 methods
- [ ] Backward compatibility layer implemented
- [ ] All existing functionality preserved
- [ ] Performance maintained or improved
- [ ] Comprehensive test coverage
- [ ] Clean separation of concerns achieved
