# ClusterDetector API Documentation

## Overview

The `ClusterDetector` class provides dedicated cluster detection functionality for the Blade Fighters puzzle game. It encapsulates all cluster detection logic, providing a clean interface for finding, analyzing, and managing clusters in the puzzle grid.

**Author**: Senior Dev 1 - Task 2A  
**Integration**: Senior Dev 3 - Task 4B  
**Documentation**: Senior Dev 3 - Task 5C  

## Class Definition

```python
class ClusterDetector:
    """
    Dedicated cluster detection engine for puzzle game mechanics.
    
    This class encapsulates all cluster detection logic, providing a clean
    interface for finding, analyzing, and managing clusters in the puzzle grid.
    """
```

## Constructor

### `__init__(grid_width: int, grid_height: int, total_grid_height: int)`

Initialize the cluster detector with grid dimensions.

**Parameters:**
- `grid_width` (int): Width of the puzzle grid
- `grid_height` (int): Height of the visible grid
- `total_grid_height` (int): Total height including hidden areas

**Example:**
```python
# Initialize for a 6x12 grid with 13 total rows (including hidden)
detector = ClusterDetector(grid_width=6, grid_height=12, total_grid_height=13)
```

## Core Methods

### `detect_clusters(puzzle_grid: List[List[Optional[str]]]) -> Set[Tuple[int, int]]`

Detect clusters of blocks that are 2+ blocks wide and 2+ blocks high.

**Parameters:**
- `puzzle_grid` (List[List[Optional[str]]]): 2D grid representation of the puzzle board

**Returns:**
- `Set[Tuple[int, int]]`: Set of (x, y) coordinates of blocks in clusters

**Algorithm:**
1. Scans the grid for 2x2 blocks of the same color
2. Extends clusters up to 5x5 maximum size
3. Excludes strike/garbage blocks from cluster detection
4. Uses performance optimization with visited tracking

**Example:**
```python
# Create a test grid with a 2x2 red cluster
grid = [[None for _ in range(6)] for _ in range(13)]
grid[8][0] = "red_block"
grid[8][1] = "red_block"
grid[9][0] = "red_block"
grid[9][1] = "red_block"

# Detect clusters
clusters = detector.detect_clusters(grid)
# Returns: {(0, 8), (1, 8), (0, 9), (1, 9)}
```

### `find_all_clusters(puzzle_grid: List[List[Optional[str]]]) -> List[Set[Tuple[int, int]]]`

Find all clusters in the grid and return them as separate groups.

**Parameters:**
- `puzzle_grid` (List[List[Optional[str]]]): 2D grid representation of the puzzle board

**Returns:**
- `List[Set[Tuple[int, int]]]`: List of sets, where each set contains the (x, y) coordinates of a cluster

**Algorithm:**
1. Uses `detect_clusters()` to find all cluster blocks
2. Groups connected blocks into separate clusters using flood-fill
3. Returns each cluster as a separate set

**Example:**
```python
# Find all separate clusters
all_clusters = detector.find_all_clusters(grid)
# Returns: [{(0, 8), (1, 8), (0, 9), (1, 9)}, {(3, 6), (4, 6), (5, 6), (3, 7), (4, 7), (5, 7)}]
```

### `is_cluster_supported(cluster_blocks: Set[Tuple[int, int]], puzzle_grid: List[List[Optional[str]]]) -> bool`

Check if a cluster has any support beneath it.

**Parameters:**
- `cluster_blocks` (Set[Tuple[int, int]]): Set of (x, y) coordinates that form the cluster
- `puzzle_grid` (List[List[Optional[str]]]): 2D grid representation of the puzzle board

**Returns:**
- `bool`: True if the cluster is supported, False otherwise

**Logic:**
- A cluster is supported if ANY of its bottom cells has direct support below
- Clusters at the bottom of the grid are considered supported
- Empty clusters are trivially supported

**Example:**
```python
# Check if a cluster is supported
cluster = {(0, 8), (1, 8), (0, 9), (1, 9)}
is_supported = detector.is_cluster_supported(cluster, grid)
# Returns: False (cluster is floating)
```

### `find_rectangular_clusters_for_render(puzzle_grid: List[List[Optional[str]]]) -> List[Set[Tuple[int, int]]]`

Find only true rectangular clusters (2x2 or larger) for UI highlighting.

**Parameters:**
- `puzzle_grid` (List[List[Optional[str]]]): 2D grid representation of the puzzle board

**Returns:**
- `List[Set[Tuple[int, int]]]`: List of sets, each set containing the (x, y) cells of one rectangle

**Features:**
- Avoids unioning overlapping rectangles
- Prefers larger rectangles (sorted by area, width, height)
- Strict non-overlap for UI clarity
- Excludes strike/garbage blocks

**Example:**
```python
# Find rectangular clusters for UI highlighting
rectangles = detector.find_rectangular_clusters_for_render(grid)
# Returns: [{(0, 8), (1, 8), (0, 9), (1, 9)}] for a 2x2 cluster
```

### `find_connected_pieces(start_x: int, start_y: int, target_color: str, puzzle_grid: List[List[Optional[str]]]) -> Set[Tuple[int, int]]`

Use flood fill to find all connected pieces of the same color.

**Parameters:**
- `start_x` (int): Starting x coordinate
- `start_y` (int): Starting y coordinate
- `target_color` (str): Target color to search for
- `puzzle_grid` (List[List[Optional[str]]]): 2D grid representation of the puzzle board

**Returns:**
- `Set[Tuple[int, int]]`: Set of (x, y) coordinates of connected pieces

**Algorithm:**
- Uses breadth-first search (flood fill)
- Checks all four adjacent positions (up, right, down, left)
- Excludes strike/garbage blocks from traversal
- Ignores color suffixes (e.g., "_breaker", "_block")

**Example:**
```python
# Find all connected red pieces starting from (0, 8)
connected = detector.find_connected_pieces(0, 8, "red", grid)
# Returns: {(0, 8), (1, 8), (0, 9), (1, 9), (2, 8)} for connected red pieces
```

## Helper Methods

### `_extend_cluster(clusters: Set[Tuple[int, int]], visited: Set[Tuple[int, int]], start_x: int, start_y: int, color: str, max_width: int, max_height: int, puzzle_grid: List[List[Optional[str]]])`

Helper method to extend clusters efficiently with size limits.

**Parameters:**
- `clusters` (Set[Tuple[int, int]]): Set to add cluster positions to
- `visited` (Set[Tuple[int, int]]): Set of already visited positions
- `start_x` (int): Starting x coordinate of the cluster
- `start_y` (int): Starting y coordinate of the cluster
- `color` (str): Color of the cluster
- `max_width` (int): Maximum width to extend (default: 5)
- `max_height` (int): Maximum height to extend (default: 5)
- `puzzle_grid` (List[List[Optional[str]]]): 2D grid representation of the puzzle board

**Algorithm:**
1. Starts with a verified 2x2 cluster
2. Extends right by checking entire columns
3. Extends down by checking entire rows
4. Respects maximum size limits
5. Excludes strike/garbage blocks

## Integration Examples

### Basic Usage in PuzzleEngine

```python
# Initialize ClusterDetector in PuzzleEngine constructor
self.cluster_detector = ClusterDetector(
    grid_width=self.grid_width,
    grid_height=self.grid_height,
    total_grid_height=self.total_grid_height
)

# Use in gravity system
current_clusters = self.cluster_detector.find_all_clusters(self.puzzle_grid)
for cluster_blocks in current_clusters:
    if not self.cluster_detector.is_cluster_supported(cluster_blocks, self.puzzle_grid):
        # Move entire cluster as a unit
        # ... gravity logic ...
```

### Renderer Integration

```python
# Get rectangular clusters for UI highlighting
rectangular_clusters = self.cluster_detector.find_rectangular_clusters_for_render(self.puzzle_grid)
for cluster in rectangular_clusters:
    # Highlight each rectangular cluster
    # ... rendering logic ...
```

### Breaker Block Integration

```python
# Find connected pieces for breaker block activation
connected_blocks = self.cluster_detector.find_connected_pieces(
    x, y, breaker_color, self.puzzle_grid
)
# Process connected blocks for breaking
```

## Performance Characteristics

- **Time Complexity**: O(n²) where n is grid size
- **Space Complexity**: O(n²) for visited tracking
- **Optimizations**:
  - Visited set prevents redundant processing
  - Size limits (5x5 max) prevent excessive computation
  - Early termination for invalid cells
  - Efficient flood-fill algorithms

## Error Handling

- **Invalid coordinates**: Methods return empty sets/lists for out-of-bounds coordinates
- **Empty grids**: Gracefully handle empty or None grids
- **Invalid block types**: Skip strike/garbage blocks automatically
- **Missing parameters**: Type hints help prevent parameter errors

## Migration Guide

### From Old Methods

**Before (in puzzle_module.py):**
```python
clusters = self.detect_clusters()
is_supported = self.is_cluster_supported(cluster_blocks)
```

**After (with ClusterDetector):**
```python
clusters = self.cluster_detector.find_all_clusters(self.puzzle_grid)
is_supported = self.cluster_detector.is_cluster_supported(cluster_blocks, self.puzzle_grid)
```

### Backward Compatibility

The ClusterDetector maintains backward compatibility by:
- Using the same method signatures where possible
- Providing the same return types
- Handling the same edge cases
- Supporting the same grid formats

## Testing

Comprehensive test suite available in `core/tests/test_cluster_detection.py`:

- Unit tests for each method
- Edge case testing
- Performance validation
- Integration testing with gravity system

Run tests with:
```bash
python -m pytest core/tests/test_cluster_detection.py -v
```

## Future Enhancements

- **Caching**: Cache cluster detection results for performance
- **Parallel processing**: Multi-threaded cluster detection for large grids
- **Advanced algorithms**: More sophisticated cluster detection algorithms
- **Visualization tools**: Debug visualization for cluster detection
- **Configuration**: Configurable cluster detection parameters
