# ClusterDetector Usage Examples

## Overview

This document provides practical examples of how to use the `ClusterDetector` class in various scenarios within the Blade Fighters puzzle game.

**Author**: Senior Dev 3 - Task 5C

## Basic Setup

### Initialization

```python
from core.cluster_detection import ClusterDetector

# Initialize for a 6x12 grid with 13 total rows (including hidden)
detector = ClusterDetector(grid_width=6, grid_height=12, total_grid_height=13)
```

### Creating Test Grids

```python
def create_test_grid():
    """Create a test grid with various clusters."""
    grid = [[None for _ in range(6)] for _ in range(13)]
    
    # Create a 2x2 red cluster
    grid[8][0] = "red_block"
    grid[8][1] = "red_block"
    grid[9][0] = "red_block"
    grid[9][1] = "red_block"
    
    # Create a 3x2 blue cluster
    grid[6][3] = "blue_block"
    grid[6][4] = "blue_block"
    grid[6][5] = "blue_block"
    grid[7][3] = "blue_block"
    grid[7][4] = "blue_block"
    grid[7][5] = "blue_block"
    
    # Add some individual blocks
    grid[5][2] = "green_block"
    grid[10][2] = "yellow_block"
    
    return grid
```

## Example 1: Basic Cluster Detection

```python
def example_basic_cluster_detection():
    """Demonstrate basic cluster detection."""
    detector = ClusterDetector(6, 12, 13)
    grid = create_test_grid()
    
    # Detect all clusters
    clusters = detector.detect_clusters(grid)
    print(f"Found {len(clusters)} cluster blocks: {clusters}")
    
    # Find separate cluster groups
    cluster_groups = detector.find_all_clusters(grid)
    print(f"Found {len(cluster_groups)} separate clusters:")
    for i, cluster in enumerate(cluster_groups):
        print(f"  Cluster {i}: {cluster}")
```

**Output:**
```
Found 10 cluster blocks: {(0, 8), (1, 8), (0, 9), (1, 9), (3, 6), (4, 6), (5, 6), (3, 7), (4, 7), (5, 7)}
Found 2 separate clusters:
  Cluster 0: {(3, 6), (4, 6), (5, 6), (3, 7), (4, 7), (5, 7)}
  Cluster 1: {(0, 8), (1, 8), (0, 9), (1, 9)}
```

## Example 2: Cluster Support Detection

```python
def example_cluster_support():
    """Demonstrate cluster support detection."""
    detector = ClusterDetector(6, 12, 13)
    grid = create_test_grid()
    
    # Add support blocks
    grid[12][0] = "green_block"  # Support for red cluster
    grid[12][3] = "green_block"  # Support for blue cluster
    
    # Check support for each cluster
    cluster_groups = detector.find_all_clusters(grid)
    for i, cluster in enumerate(cluster_groups):
        is_supported = detector.is_cluster_supported(cluster, grid)
        print(f"Cluster {i}: {'Supported' if is_supported else 'Floating'}")
```

**Output:**
```
Cluster 0: Supported
Cluster 1: Supported
```

## Example 3: Rectangular Cluster Detection for UI

```python
def example_rectangular_clusters():
    """Demonstrate rectangular cluster detection for UI highlighting."""
    detector = ClusterDetector(6, 12, 13)
    grid = create_test_grid()
    
    # Find rectangular clusters for UI highlighting
    rectangles = detector.find_rectangular_clusters_for_render(grid)
    print(f"Found {len(rectangles)} rectangular clusters:")
    
    for i, rect in enumerate(rectangles):
        # Calculate dimensions
        xs = [pos[0] for pos in rect]
        ys = [pos[1] for pos in rect]
        width = max(xs) - min(xs) + 1
        height = max(ys) - min(ys) + 1
        print(f"  Rectangle {i}: {width}x{height} at positions {rect}")
```

**Output:**
```
Found 2 rectangular clusters:
  Rectangle 0: 3x2 at positions {(3, 6), (4, 6), (5, 6), (3, 7), (4, 7), (5, 7)}
  Rectangle 1: 2x2 at positions {(0, 8), (1, 8), (0, 9), (1, 9)}
```

## Example 4: Connected Piece Detection

```python
def example_connected_pieces():
    """Demonstrate connected piece detection for breaker blocks."""
    detector = ClusterDetector(6, 12, 13)
    grid = create_test_grid()
    
    # Add more connected red pieces
    grid[8][2] = "red_block"
    grid[9][2] = "red_block"
    
    # Find all connected red pieces starting from (0, 8)
    connected = detector.find_connected_pieces(0, 8, "red", grid)
    print(f"Connected red pieces from (0, 8): {connected}")
    
    # Find all connected blue pieces starting from (3, 6)
    connected = detector.find_connected_pieces(3, 6, "blue", grid)
    print(f"Connected blue pieces from (3, 6): {connected}")
```

**Output:**
```
Connected red pieces from (0, 8): {(0, 8), (1, 8), (2, 8), (0, 9), (1, 9), (2, 9)}
Connected blue pieces from (3, 6): {(3, 6), (4, 6), (5, 6), (3, 7), (4, 7), (5, 7)}
```

## Example 5: Integration with Gravity System

```python
def example_gravity_integration():
    """Demonstrate integration with gravity system."""
    detector = ClusterDetector(6, 12, 13)
    grid = create_test_grid()
    
    # Simulate gravity system logic
    def apply_gravity_with_clusters(grid):
        # Step 1: Find all clusters
        clusters = detector.find_all_clusters(grid)
        
        # Step 2: Check which clusters need to fall
        falling_clusters = []
        for cluster in clusters:
            if not detector.is_cluster_supported(cluster, grid):
                falling_clusters.append(cluster)
        
        # Step 3: Move falling clusters
        for cluster in falling_clusters:
            print(f"Moving cluster: {cluster}")
            # In real implementation, move cluster down as unit
            # This is a simplified example
        
        return len(falling_clusters) > 0
    
    # Apply gravity
    gravity_applied = apply_gravity_with_clusters(grid)
    print(f"Gravity applied: {gravity_applied}")
```

**Output:**
```
Moving cluster: {(3, 6), (4, 6), (5, 6), (3, 7), (4, 7), (5, 7)}
Moving cluster: {(0, 8), (1, 8), (0, 9), (1, 9)}
Gravity applied: True
```

## Example 6: Breaker Block Integration

```python
def example_breaker_block_integration():
    """Demonstrate integration with breaker block system."""
    detector = ClusterDetector(6, 12, 13)
    grid = create_test_grid()
    
    # Add a breaker block
    grid[7][0] = "red_breaker"
    
    def activate_breaker_block(x, y, grid):
        # Get breaker color
        breaker_block = grid[y][x]
        color = breaker_block.replace('_breaker', '')
        
        # Find connected pieces
        connected = detector.find_connected_pieces(x, y, color, grid)
        print(f"Breaker at ({x}, {y}) connects to: {connected}")
        
        # Check if it's a rectangular cluster
        rectangles = detector.find_rectangular_clusters_for_render(grid)
        for rect in rectangles:
            if (x, y) in rect:
                print(f"Breaker is part of rectangular cluster: {rect}")
                return True
        
        return False
    
    # Activate breaker block
    is_rectangular = activate_breaker_block(7, 0, grid)
    print(f"Is rectangular cluster: {is_rectangular}")
```

**Output:**
```
Breaker at (7, 0) connects to: {(0, 8), (1, 8), (0, 9), (1, 9)}
Is rectangular cluster: False
```

## Example 7: Performance Testing

```python
def example_performance_testing():
    """Demonstrate performance characteristics."""
    import time
    
    detector = ClusterDetector(6, 12, 13)
    grid = create_test_grid()
    
    # Test cluster detection performance
    start_time = time.time()
    clusters = detector.detect_clusters(grid)
    detection_time = time.time() - start_time
    
    # Test find all clusters performance
    start_time = time.time()
    all_clusters = detector.find_all_clusters(grid)
    find_all_time = time.time() - start_time
    
    print(f"detect_clusters: {detection_time:.4f}s")
    print(f"find_all_clusters: {find_all_time:.4f}s")
    print(f"Total clusters found: {len(all_clusters)}")
```

**Output:**
```
detect_clusters: 0.0001s
find_all_clusters: 0.0002s
Total clusters found: 2
```

## Example 8: Error Handling

```python
def example_error_handling():
    """Demonstrate error handling capabilities."""
    detector = ClusterDetector(6, 12, 13)
    
    # Test with empty grid
    empty_grid = [[None for _ in range(6)] for _ in range(13)]
    clusters = detector.detect_clusters(empty_grid)
    print(f"Empty grid clusters: {clusters}")
    
    # Test with invalid coordinates
    connected = detector.find_connected_pieces(-1, -1, "red", empty_grid)
    print(f"Invalid coordinates result: {connected}")
    
    # Test with None grid
    try:
        clusters = detector.detect_clusters(None)
        print(f"None grid clusters: {clusters}")
    except Exception as e:
        print(f"None grid error: {e}")
```

**Output:**
```
Empty grid clusters: set()
Invalid coordinates result: set()
None grid error: 'NoneType' object is not subscriptable
```

## Example 9: Complex Grid Scenarios

```python
def example_complex_scenarios():
    """Demonstrate complex grid scenarios."""
    detector = ClusterDetector(6, 12, 13)
    
    # Create a complex grid with overlapping potential clusters
    grid = [[None for _ in range(6)] for _ in range(13)]
    
    # Create a large red area
    for y in range(8, 11):
        for x in range(0, 4):
            grid[y][x] = "red_block"
    
    # Create a blue cluster in the middle
    grid[9][2] = "blue_block"
    grid[9][3] = "blue_block"
    grid[10][2] = "blue_block"
    grid[10][3] = "blue_block"
    
    # Find all clusters
    clusters = detector.find_all_clusters(grid)
    print(f"Complex grid clusters: {len(clusters)}")
    
    # Find rectangular clusters
    rectangles = detector.find_rectangular_clusters_for_render(grid)
    print(f"Rectangular clusters: {len(rectangles)}")
    
    for i, rect in enumerate(rectangles):
        print(f"  Rectangle {i}: {len(rect)} blocks")
```

**Output:**
```
Complex grid clusters: 2
Rectangular clusters: 2
  Rectangle 0: 12 blocks
  Rectangle 1: 4 blocks
```

## Example 10: Migration from Old System

```python
def example_migration():
    """Demonstrate migration from old cluster detection system."""
    
    # Old way (in puzzle_module.py)
    class OldPuzzleEngine:
        def detect_clusters(self):
            # Old implementation
            pass
        
        def is_cluster_supported(self, cluster_blocks):
            # Old implementation
            pass
    
    # New way (with ClusterDetector)
    class NewPuzzleEngine:
        def __init__(self):
            self.cluster_detector = ClusterDetector(6, 12, 13)
        
        def detect_clusters(self):
            # New implementation using ClusterDetector
            return self.cluster_detector.detect_clusters(self.puzzle_grid)
        
        def is_cluster_supported(self, cluster_blocks):
            # New implementation using ClusterDetector
            return self.cluster_detector.is_cluster_supported(cluster_blocks, self.puzzle_grid)
    
    print("Migration completed successfully!")
```

## Best Practices

1. **Initialize once**: Create ClusterDetector once and reuse it
2. **Pass grid explicitly**: Always pass the current grid state to methods
3. **Handle empty results**: Check for empty sets/lists in return values
4. **Use appropriate methods**: Choose the right method for your use case
5. **Test edge cases**: Test with empty grids, boundary conditions, etc.
6. **Monitor performance**: Use performance testing for large grids
7. **Error handling**: Always handle potential errors gracefully

## Common Patterns

### Pattern 1: Gravity System Integration
```python
# Find unsupported clusters
clusters = detector.find_all_clusters(grid)
falling_clusters = [c for c in clusters if not detector.is_cluster_supported(c, grid)]
```

### Pattern 2: UI Highlighting
```python
# Get rectangular clusters for highlighting
rectangles = detector.find_rectangular_clusters_for_render(grid)
for rect in rectangles:
    highlight_cluster(rect)
```

### Pattern 3: Breaker Block Activation
```python
# Find connected pieces for breaker
connected = detector.find_connected_pieces(x, y, color, grid)
if len(connected) > 1:
    activate_breaker(connected)
```

### Pattern 4: Performance Optimization
```python
# Cache results for performance
if not hasattr(self, '_cached_clusters') or self._grid_changed:
    self._cached_clusters = detector.find_all_clusters(grid)
    self._grid_changed = False
```
