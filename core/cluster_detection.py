"""
Cluster Detection Module

This module provides dedicated cluster detection functionality for the puzzle game.
It encapsulates all cluster detection logic, providing a clean interface for
finding, analyzing, and managing clusters in the puzzle grid.

Author: Senior Dev 1 - Task 2A
"""

from typing import Set, List, Tuple, Optional


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
        
    def detect_clusters(self, puzzle_grid: List[List[Optional[str]]]) -> Set[Tuple[int, int]]:
        """
        Detect clusters of blocks that are 2+ blocks wide and 2+ blocks high.
        
        Args:
            puzzle_grid: 2D grid representation of the puzzle board
            
        Returns:
            Set of (x, y) coordinates of blocks in clusters
        """
        # Performance optimization - use a more efficient algorithm
        clusters = set()
        visited = set()
        
        # Go through each cell in the grid
        for y in range(self.total_grid_height):
            for x in range(self.grid_width):
                # Skip if already visited or if empty
                if (x, y) in visited or puzzle_grid[y][x] is None:
                    continue
                
                # Skip strike/garbage cells for cluster purposes
                if ('_garbage' in str(puzzle_grid[y][x])) or ('_strike' in str(puzzle_grid[y][x])):
                    continue
                # Get the color of the current block
                current_color = puzzle_grid[y][x].split('_')[0]
                
                # Check for minimum 2x2 cluster at this position
                if (x + 1 < self.grid_width and 
                    y + 1 < self.total_grid_height and
                    puzzle_grid[y][x+1] is not None and
                    puzzle_grid[y+1][x] is not None and
                    puzzle_grid[y+1][x+1] is not None):
                    
                    # Skip if any are strike/garbage
                    if ('_garbage' in str(puzzle_grid[y][x+1])) or ('_strike' in str(puzzle_grid[y][x+1])):
                        continue
                    if ('_garbage' in str(puzzle_grid[y+1][x])) or ('_strike' in str(puzzle_grid[y+1][x])):
                        continue
                    if ('_garbage' in str(puzzle_grid[y+1][x+1])) or ('_strike' in str(puzzle_grid[y+1][x+1])):
                        continue
                    # Check if all are the same color
                    if (puzzle_grid[y][x+1].split('_')[0] == current_color and
                        puzzle_grid[y+1][x].split('_')[0] == current_color and
                        puzzle_grid[y+1][x+1].split('_')[0] == current_color):
                        
                        # We've found a 2x2 cluster of the same color
                        clusters.add((x, y))
                        clusters.add((x+1, y))
                        clusters.add((x, y+1))
                        clusters.add((x+1, y+1))
                        
                        # Mark all as visited
                        visited.add((x, y))
                        visited.add((x+1, y))
                        visited.add((x, y+1))
                        visited.add((x+1, y+1))
                        
                        # Try to extend the cluster if possible (but limit to avoid excessive computation)
                        self._extend_cluster(clusters, visited, x, y, current_color, 5, 5, puzzle_grid)
        
        return clusters
        
    def find_all_clusters(self, puzzle_grid: List[List[Optional[str]]]) -> List[Set[Tuple[int, int]]]:
        """
        Find all clusters in the grid and return them as separate groups.
        
        Args:
            puzzle_grid: 2D grid representation of the puzzle board
            
        Returns:
            List of sets, where each set contains the (x, y) coordinates of a cluster
        """
        # Get all cluster blocks
        all_cluster_blocks = self.detect_clusters(puzzle_grid)
        
        # If no clusters, return empty list
        if not all_cluster_blocks:
            return []
        
        # Group clusters by connectivity
        clusters = []
        visited = set()
        
        for x, y in all_cluster_blocks:
            if (x, y) in visited:
                continue
                
            # Start a new cluster
            if puzzle_grid[y][x] is None:
                continue
                
            cell_val = puzzle_grid[y][x]
            # Skip non-normal blocks (garbage/strike/neutral)
            if (cell_val is None) or ('_garbage' in str(cell_val)) or ('_strike' in str(cell_val)) or (cell_val == 'garbage_block'):
                continue
            color = cell_val.split('_')[0]
            current_cluster = set()
            
            # Use a flood-fill approach to find all connected blocks of the same color
            queue = [(x, y)]
            cluster_visited = set(queue)
            
            while queue:
                cx, cy = queue.pop(0)
                if (cx, cy) in all_cluster_blocks:  # Only include blocks that are in clusters
                    current_cluster.add((cx, cy))
                    
                    # Check adjacent positions
                    for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:  # Up, right, down, left
                        nx, ny = cx + dx, cy + dy
                        
                        if ((nx, ny) not in cluster_visited and
                            (nx, ny) in all_cluster_blocks and
                            0 <= nx < self.grid_width and
                            0 <= ny < self.grid_height and
                            puzzle_grid[ny][nx] is not None and
                            puzzle_grid[ny][nx].split('_')[0] == color):
                            
                            queue.append((nx, ny))
                            cluster_visited.add((nx, ny))
            
            # Add the current cluster if it's non-empty
            if current_cluster:
                clusters.append(current_cluster)
                visited.update(current_cluster)
        
        return clusters
        
    def is_cluster_supported(self, cluster_blocks: Set[Tuple[int, int]], 
                           puzzle_grid: List[List[Optional[str]]]) -> bool:
        """
        Check if a cluster has any support beneath it.
        A cluster should remain standing if ANY of its bottom cells has direct support below.
        It should only fall when the entire underside is unsupported.
        
        Args:
            cluster_blocks: Set of (x, y) coordinates that form the cluster
            puzzle_grid: 2D grid representation of the puzzle board
            
        Returns:
            True if the cluster is supported, False otherwise
        """
        # First identify the bottom row of blocks in the cluster
        if not cluster_blocks:
            return True  # Empty clusters are trivially supported
            
        # Group blocks by x-coordinate
        columns = {}
        for x, y in cluster_blocks:
            if x not in columns:
                columns[x] = []
            columns[x].append(y)
        
        # If ANY bottom cell has support, the cluster is supported.
        for x, y_values in columns.items():
            bottom_y = max(y_values)
            # Bottom row of grid counts as supported
            if bottom_y >= self.grid_height - 1:
                return True
            below_pos = (x, bottom_y + 1)
            cell_below = puzzle_grid[bottom_y + 1][x]
            if below_pos not in cluster_blocks and cell_below is not None:
                return True
        
        # No support found under any bottom cell → entire underside is clear → should fall
        return False
        
    def find_rectangular_clusters_for_render(self, puzzle_grid: List[List[Optional[str]]]) -> List[Set[Tuple[int, int]]]:
        """
        Find only true rectangular clusters (2x2 or larger) for UI highlighting.
        Returns a list of sets, each set containing the (x, y) cells of one rectangle.
        This avoids unioning overlapping rectangles, so partial shapes won't all glow at once.
        
        Args:
            puzzle_grid: 2D grid representation of the puzzle board
            
        Returns:
            List of sets, each set containing the (x, y) cells of one rectangle
        """
        rectangles = []

        def is_valid_cell(cx: int, cy: int, color: str) -> bool:
            if cx < 0 or cy < 0 or cx >= self.grid_width or cy >= self.total_grid_height:
                return False
            cell = puzzle_grid[cy][cx]
            if cell is None:
                return False
            if ('_garbage' in str(cell)) or ('_strike' in str(cell)):
                return False
            return cell.split('_')[0] == color

        y = 0
        while y < self.total_grid_height:
            x = 0
            while x < self.grid_width:
                cell = puzzle_grid[y][x]
                if cell is None or ('_garbage' in str(cell)) or ('_strike' in str(cell)) or (cell == 'garbage_block'):
                    x += 1
                    continue
                color = cell.split('_')[0]

                # Check for minimum 2x2 starting at (x, y)
                if not (is_valid_cell(x + 1, y, color) and is_valid_cell(x, y + 1, color) and is_valid_cell(x + 1, y + 1, color)):
                    x += 1
                    continue

                # Extend width
                width = 2
                while True:
                    next_col = x + width
                    all_match = True
                    if next_col >= self.grid_width:
                        break
                    for ry in range(y, y + 2):
                        if not is_valid_cell(next_col, ry, color):
                            all_match = False
                            break
                    if not all_match:
                        break
                    width += 1

                # Extend height across current width
                height = 2
                while True:
                    next_row = y + height
                    all_match = True
                    if next_row >= self.total_grid_height:
                        break
                    for rx in range(x, x + width):
                        if not is_valid_cell(rx, next_row, color):
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

                x += 1
            y += 1

        # Prefer larger rectangles: sort by area desc, then width desc, then height desc
        def rect_dims(rc):
            xs = [p[0] for p in rc]; ys = [p[1] for p in rc]
            w = (max(xs) - min(xs) + 1) if xs else 0
            h = (max(ys) - min(ys) + 1) if ys else 0
            return w, h

        ranked = sorted(rectangles, key=lambda rc: (-len(rc), -rect_dims(rc)[0], -rect_dims(rc)[1]))
        selected: List[Set[Tuple[int, int]]] = []
        for rc in ranked:
            keep = True
            for sc in selected:
                # Strict non-overlap for UI clarity: never reuse cells across rectangles
                if rc & sc:
                    keep = False
                    break
            if keep:
                selected.append(rc)

        return selected
    
    def find_connected_pieces(self, start_x: int, start_y: int, target_color: str,
                            puzzle_grid: List[List[Optional[str]]]) -> Set[Tuple[int, int]]:
        """
        Use flood fill to find all connected pieces of the same color.
        Returns a set of (x, y) coordinates.
        
        Args:
            start_x: Starting x coordinate
            start_y: Starting y coordinate
            target_color: Color to search for
            puzzle_grid: 2D grid representation of the puzzle board
            
        Returns:
            Set of (x, y) coordinates of connected pieces
        """
        if not (0 <= start_x < self.grid_width and 0 <= start_y < self.grid_height):
            return set()
            
        if puzzle_grid[start_y][start_x] is None:
            return set()
            
        # Get color of the starting piece without any suffix
        start_cell = puzzle_grid[start_y][start_x]
        # Treat strike/garbage as non-traversable and non-connectable until transformed
        if ('_garbage' in str(start_cell)) or ('_strike' in str(start_cell)):
            return set()
        piece_color = start_cell.split('_')[0]
        if piece_color != target_color:
            return set()
        
        # Initialize the search
        connected = set()
        queue = [(start_x, start_y)]
        visited = set(queue)
        
        # Breadth-first search to find all connected pieces
        while queue:
            x, y = queue.pop(0)
            connected.add((x, y))
            
            # Check all four adjacent positions
            for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:  # Up, right, down, left
                nx, ny = x + dx, y + dy
                
                # Check if the new position is valid and has the same color
                if ((nx, ny) not in visited and 
                    0 <= nx < self.grid_width and 
                    0 <= ny < self.grid_height and 
                    puzzle_grid[ny][nx] is not None):
                    
                    cell = puzzle_grid[ny][nx]
                    # Do not traverse through or include strike/garbage while untransformed
                    if ('_garbage' in str(cell)) or ('_strike' in str(cell)):
                        visited.add((nx, ny))
                        continue
                    # Check if the color matches (ignoring suffixes like "_breaker")
                    next_color = cell.split('_')[0]
                    if next_color == target_color:
                        queue.append((nx, ny))
                        visited.add((nx, ny))
        
        return connected
        
    def _extend_cluster(self, clusters: Set[Tuple[int, int]], visited: Set[Tuple[int, int]],
                       start_x: int, start_y: int, color: str, max_width: int, max_height: int,
                       puzzle_grid: List[List[Optional[str]]]) -> None:
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
        # Find how far right and down we can extend
        width = 2  # Already verified 2x2
        height = 2
        
        # Try to extend right
        for x in range(start_x + 2, min(start_x + max_width, self.grid_width)):
            # Check if entire column has same color
            valid_column = True
            for y in range(start_y, min(start_y + height, self.total_grid_height)):
                if (y >= self.total_grid_height or 
                    puzzle_grid[y][x] is None or
                    '_garbage' in str(puzzle_grid[y][x]) or '_strike' in str(puzzle_grid[y][x]) or
                    puzzle_grid[y][x].split('_')[0] != color):
                    valid_column = False
                    break
            
            if valid_column:
                # Add all blocks in this column to the cluster
                for y in range(start_y, start_y + height):
                    clusters.add((x, y))
                    visited.add((x, y))
                width += 1
            else:
                break
                
        # Try to extend down
        for y in range(start_y + 2, min(start_y + max_height, self.total_grid_height)):
            # Check if entire row has same color
            valid_row = True
            for x in range(start_x, start_x + width):
                if (x >= self.grid_width or 
                    puzzle_grid[y][x] is None or
                    '_garbage' in str(puzzle_grid[y][x]) or '_strike' in str(puzzle_grid[y][x]) or
                    puzzle_grid[y][x].split('_')[0] != color):
                    valid_row = False
                    break
            
            if valid_row:
                # Add all blocks in this row to the cluster
                for x in range(start_x, start_x + width):
                    clusters.add((x, y))
                    visited.add((x, y))
                height += 1
            else:
                break
