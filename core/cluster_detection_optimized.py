"""
Optimized Cluster Detection Module

This module provides an optimized version of the ClusterDetector class with
performance improvements including caching, optimized algorithms, and better
memory management.

Author: Senior Dev 1 - Task 5B Performance Optimization
"""

from typing import Set, List, Tuple, Optional, Dict
from functools import lru_cache
import time


class OptimizedClusterDetector:
    """
    Optimized cluster detection engine with performance improvements.
    
    Performance optimizations:
    - LRU caching for expensive operations
    - Optimized grid access patterns
    - Reduced string operations
    - Memory-efficient data structures
    - Early termination conditions
    """

    def __init__(self, grid_width: int, grid_height: int, total_grid_height: int):
        """
        Initialize the optimized cluster detector.

        Args:
            grid_width: Width of the puzzle grid
            grid_height: Height of the visible grid
            total_grid_height: Total height including hidden areas
        """
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.total_grid_height = total_grid_height
        
        # Performance monitoring
        self.performance_stats = {
            'detect_clusters_calls': 0,
            'find_all_clusters_calls': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'total_time': 0.0
        }
        
        # Cache for expensive operations
        self._grid_hash_cache = {}
        self._cluster_cache = {}
        self._support_cache = {}

    def _get_grid_hash(self, puzzle_grid: List[List[Optional[str]]]) -> int:
        """Generate a hash for the grid state for caching."""
        # Simple hash based on grid content
        hash_val = 0
        for y in range(min(10, self.total_grid_height)):  # Only hash first 10 rows for performance
            for x in range(min(10, self.grid_width)):     # Only hash first 10 columns
                cell = puzzle_grid[y][x]
                if cell is not None:
                    hash_val = (hash_val * 31 + hash(cell)) & 0xFFFFFFFF
        return hash_val

    def _is_valid_cell(self, cell: Optional[str]) -> bool:
        """Optimized cell validation."""
        if cell is None:
            return False
        # Use 'in' instead of string operations for better performance
        return not ('_garbage' in cell or '_strike' in cell)

    def _get_cell_color(self, cell: Optional[str]) -> Optional[str]:
        """Optimized color extraction."""
        if cell is None:
            return None
        # Use split only once and cache the result
        return cell.split('_')[0] if '_' in cell else cell

    def detect_clusters(self, puzzle_grid: List[List[Optional[str]]]) -> Set[Tuple[int, int]]:
        """
        Optimized cluster detection with caching and early termination.
        """
        start_time = time.time()
        self.performance_stats['detect_clusters_calls'] += 1
        
        # Check cache first
        grid_hash = self._get_grid_hash(puzzle_grid)
        if grid_hash in self._cluster_cache:
            self.performance_stats['cache_hits'] += 1
            return self._cluster_cache[grid_hash]
        
        self.performance_stats['cache_misses'] += 1
        
        clusters = set()
        visited = set()
        
        # Pre-compute valid cells for better performance
        valid_cells = set()
        for y in range(self.total_grid_height):
            for x in range(self.grid_width):
                if self._is_valid_cell(puzzle_grid[y][x]):
                    valid_cells.add((x, y))
        
        # Early termination if no valid cells
        if len(valid_cells) < 4:
            self._cluster_cache[grid_hash] = clusters
            self.performance_stats['total_time'] += time.time() - start_time
            return clusters
        
        # Optimized cluster detection
        for x, y in valid_cells:
            if (x, y) in visited:
                continue
            
            current_color = self._get_cell_color(puzzle_grid[y][x])
            if current_color is None:
                continue
            
            # Check for minimum 2x2 cluster with early termination
            if (x + 1 >= self.grid_width or y + 1 >= self.total_grid_height):
                continue
                
            # Check all four corners efficiently
            corners = [
                (x, y), (x+1, y), (x, y+1), (x+1, y+1)
            ]
            
            # Early termination if any corner is invalid
            if not all(corner in valid_cells for corner in corners):
                continue
                
            # Check if all corners have the same color
            if all(self._get_cell_color(puzzle_grid[cy][cx]) == current_color 
                   for cx, cy in corners):
                
                # Add all corners to cluster
                clusters.update(corners)
                visited.update(corners)
                
                # Extend cluster with size limits for performance
                self._extend_cluster_optimized(clusters, visited, x, y, current_color, 
                                             puzzle_grid, max_width=8, max_height=8)
        
        # Cache result
        self._cluster_cache[grid_hash] = clusters
        
        # Limit cache size for memory management
        if len(self._cluster_cache) > 100:
            # Remove oldest entries
            oldest_key = next(iter(self._cluster_cache))
            del self._cluster_cache[oldest_key]
        
        self.performance_stats['total_time'] += time.time() - start_time
        return clusters

    def _extend_cluster_optimized(self, clusters: Set[Tuple[int, int]], 
                                visited: Set[Tuple[int, int]], start_x: int, start_y: int, 
                                color: str, puzzle_grid: List[List[Optional[str]]], 
                                max_width: int, max_height: int) -> None:
        """
        Optimized cluster extension with better performance.
        """
        width = 2
        height = 2
        
        # Extend right with early termination
        for x in range(start_x + 2, min(start_x + max_width, self.grid_width)):
            # Check entire column efficiently
            valid_column = True
            for y in range(start_y, min(start_y + height, self.total_grid_height)):
                if (y >= self.total_grid_height or 
                    not self._is_valid_cell(puzzle_grid[y][x]) or
                    self._get_cell_color(puzzle_grid[y][x]) != color):
                    valid_column = False
                    break
            
            if not valid_column:
                break
                
            # Add column to cluster
            for y in range(start_y, start_y + height):
                clusters.add((x, y))
                visited.add((x, y))
            width += 1
        
        # Extend down with early termination
        for y in range(start_y + 2, min(start_y + max_height, self.total_grid_height)):
            # Check entire row efficiently
            valid_row = True
            for x in range(start_x, start_x + width):
                if (x >= self.grid_width or 
                    not self._is_valid_cell(puzzle_grid[y][x]) or
                    self._get_cell_color(puzzle_grid[y][x]) != color):
                    valid_row = False
                    break
            
            if not valid_row:
                break
                
            # Add row to cluster
            for x in range(start_x, start_x + width):
                clusters.add((x, y))
                visited.add((x, y))
            height += 1

    def find_all_clusters(self, puzzle_grid: List[List[Optional[str]]]) -> List[Set[Tuple[int, int]]]:
        """
        Optimized find_all_clusters with improved flood-fill algorithm.
        """
        self.performance_stats['find_all_clusters_calls'] += 1
        
        # Get all cluster blocks
        all_cluster_blocks = self.detect_clusters(puzzle_grid)
        
        if not all_cluster_blocks:
            return []
        
        # Optimized flood-fill for cluster grouping
        clusters = []
        visited = set()
        
        # Use a more efficient flood-fill with early termination
        for x, y in all_cluster_blocks:
            if (x, y) in visited:
                continue
            
            if not self._is_valid_cell(puzzle_grid[y][x]):
                continue
                
            color = self._get_cell_color(puzzle_grid[y][x])
            if color is None:
                continue
                
            # Optimized flood-fill
            current_cluster = set()
            queue = [(x, y)]
            cluster_visited = {x, y}
            
            while queue:
                cx, cy = queue.pop(0)
                if (cx, cy) in all_cluster_blocks:
                    current_cluster.add((cx, cy))
                    
                    # Check adjacent positions with early termination
                    for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
                        nx, ny = cx + dx, cy + dy
                        
                        if ((nx, ny) not in cluster_visited and
                            (nx, ny) in all_cluster_blocks and
                            0 <= nx < self.grid_width and
                            0 <= ny < self.grid_height and
                            self._is_valid_cell(puzzle_grid[ny][nx]) and
                            self._get_cell_color(puzzle_grid[ny][nx]) == color):
                            
                            queue.append((nx, ny))
                            cluster_visited.add((nx, ny))
            
            if current_cluster:
                clusters.append(current_cluster)
                visited.update(current_cluster)
        
        return clusters

    def is_cluster_supported(self, cluster_blocks: Set[Tuple[int, int]],
                           puzzle_grid: List[List[Optional[str]]]) -> bool:
        """
        Optimized cluster support detection with caching.
        """
        if not cluster_blocks:
            return True
        
        # Check cache
        cluster_key = frozenset(cluster_blocks)
        if cluster_key in self._support_cache:
            return self._support_cache[cluster_key]
        
        # Optimized support detection
        columns = {}
        for x, y in cluster_blocks:
            if x not in columns:
                columns[x] = []
            columns[x].append(y)
        
        # Check if ANY bottom cell has support
        for x, y_values in columns.items():
            bottom_y = max(y_values)
            
            # Bottom row of grid counts as supported
            if bottom_y >= self.grid_height - 1:
                self._support_cache[cluster_key] = True
                return True
                
            # Check cell below
            below_pos = (x, bottom_y + 1)
            if below_pos not in cluster_blocks and puzzle_grid[bottom_y + 1][x] is not None:
                self._support_cache[cluster_key] = True
                return True
        
        # No support found
        self._support_cache[cluster_key] = False
        
        # Limit cache size
        if len(self._support_cache) > 200:
            oldest_key = next(iter(self._support_cache))
            del self._support_cache[oldest_key]
        
        return False

    def find_rectangular_clusters_for_render(self, puzzle_grid: List[List[Optional[str]]]) -> List[Set[Tuple[int, int]]]:
        """
        Optimized rectangular cluster detection for rendering with improved performance.
        """
        rectangles = []
        
        # Pre-compute valid cells for better performance
        valid_cells = {}
        for y in range(self.total_grid_height):
            for x in range(self.grid_width):
                cell = puzzle_grid[y][x]
                if self._is_valid_cell(cell):
                    color = self._get_cell_color(cell)
                    if color not in valid_cells:
                        valid_cells[color] = set()
                    valid_cells[color].add((x, y))
        
        # Process each color separately for better performance
        for color, cells in valid_cells.items():
            if len(cells) < 4:  # Need at least 4 cells for a 2x2 rectangle
                continue
                
            # Find rectangular clusters for this color
            color_rectangles = self._find_rectangles_for_color(cells, color, puzzle_grid)
            rectangles.extend(color_rectangles)
        
        # Optimized rectangle selection
        def rect_dims(rc):
            xs = [p[0] for p in rc]; ys = [p[1] for p in rc]
            w = (max(xs) - min(xs) + 1) if xs else 0
            h = (max(ys) - min(ys) + 1) if ys else 0
            return w, h
        
        # Sort by area, width, height (descending)
        ranked = sorted(rectangles, key=lambda rc: (-len(rc), -rect_dims(rc)[0], -rect_dims(rc)[1]))
        
        # Select non-overlapping rectangles efficiently
        selected = []
        for rc in ranked:
            keep = True
            for sc in selected:
                if rc & sc:  # Check for overlap
                    keep = False
                    break
            if keep:
                selected.append(rc)
        
        return selected

    def _find_rectangles_for_color(self, cells: Set[Tuple[int, int]], color: str, 
                                 puzzle_grid: List[List[Optional[str]]]) -> List[Set[Tuple[int, int]]]:
        """Find rectangular clusters for a specific color efficiently."""
        rectangles = []
        
        # Group cells by position for faster lookup
        cell_set = cells
        
        # Find potential rectangle starting points
        for x, y in cells:
            # Check for minimum 2x2 starting at (x, y)
            corners = [(x, y), (x+1, y), (x, y+1), (x+1, y+1)]
            if not all(corner in cell_set for corner in corners):
                continue
            
            # Extend width efficiently
            width = 2
            while True:
                next_col = x + width
                if next_col >= self.grid_width:
                    break
                # Check if entire column has the color
                all_match = True
                for ry in range(y, y + 2):
                    if (next_col, ry) not in cell_set:
                        all_match = False
                        break
                if not all_match:
                    break
                width += 1
            
            # Extend height efficiently
            height = 2
            while True:
                next_row = y + height
                if next_row >= self.total_grid_height:
                    break
                # Check if entire row has the color
                all_match = True
                for rx in range(x, x + width):
                    if (rx, next_row) not in cell_set:
                        all_match = False
                        break
                if not all_match:
                    break
                height += 1
            
            # Build rectangle set
            if width >= 2 and height >= 2:
                rect_cells = set()
                for rx in range(x, x + width):
                    for ry in range(y, y + height):
                        rect_cells.add((rx, ry))
                rectangles.append(rect_cells)
        
        return rectangles

    def find_connected_pieces(self, start_x: int, start_y: int, target_color: str,
                            puzzle_grid: List[List[Optional[str]]]) -> Set[Tuple[int, int]]:
        """
        Optimized connected pieces detection with early termination.
        """
        if not (0 <= start_x < self.grid_width and 0 <= start_y < self.grid_height):
            return set()
        
        if not self._is_valid_cell(puzzle_grid[start_y][start_x]):
            return set()
        
        start_color = self._get_cell_color(puzzle_grid[start_y][start_x])
        if start_color != target_color:
            return set()
        
        # Optimized flood-fill
        connected = set()
        queue = [(start_x, start_y)]
        visited = {(start_x, start_y)}
        
        while queue:
            x, y = queue.pop(0)
            connected.add((x, y))
            
            # Check adjacent positions with early termination
            for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
                nx, ny = x + dx, y + dy
                
                if ((nx, ny) not in visited and
                    0 <= nx < self.grid_width and
                    0 <= ny < self.grid_height and
                    self._is_valid_cell(puzzle_grid[ny][nx]) and
                    self._get_cell_color(puzzle_grid[ny][nx]) == target_color):
                    
                    queue.append((nx, ny))
                    visited.add((nx, ny))
        
        return connected

    def get_performance_stats(self) -> Dict:
        """Get performance statistics."""
        return self.performance_stats.copy()

    def clear_caches(self) -> None:
        """Clear all caches for memory management."""
        self._grid_hash_cache.clear()
        self._cluster_cache.clear()
        self._support_cache.clear()
        self.performance_stats = {
            'detect_clusters_calls': 0,
            'find_all_clusters_calls': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'total_time': 0.0
        }
