# combo.py
"""
Combo and clearing logic for Blade Fighters.
Handles:
- Cluster detection (2x2 or larger, same color)
- Clearing clusters and single sprinkles
- Cascade logic (gravity after clears)
- Combo counting

Extension points:
- Visual effects for glowing clusters
- Attack/strike generation after clears
"""

class ComboManager:
    def __init__(self, board):
        self.board = board  # Board instance

    def find_clusters(self):
        """
        Finds all clusters (2x2 or larger, same color) on the board.
        Returns a list of clusters, each as a set of (x, y) tuples.
        """
        visited = set()
        clusters = []
        for x in range(self.board.WIDTH):
            for y in range(self.board.HEIGHT):
                cell = self.board.get_piece(x, y)
                if cell is None or cell == self.board.EMPTY or (x, y) in visited:
                    continue
                color_key = self._color_key(cell)
                cluster = self._flood_fill(x, y, color_key, visited)
                if self._is_valid_cluster(cluster):
                    clusters.append(cluster)
        return clusters

    def _flood_fill(self, x, y, color_key, visited):
        """
        Flood fill to find all connected blocks of the same color.
        """
        stack = [(x, y)]
        cluster = set()
        while stack:
            cx, cy = stack.pop()
            if (cx, cy) in visited:
                continue
            if not self.board.is_in_bounds(cx, cy):
                continue
            cell = self.board.get_piece(cx, cy)
            if self._color_key(cell) != color_key:
                continue
            visited.add((cx, cy))
            cluster.add((cx, cy))
            # Check 4 directions (no diagonals)
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                stack.append((cx+dx, cy+dy))
        return cluster

    def _is_valid_cluster(self, cluster):
        """
        Returns True if the cluster is at least 2x2 in size (not just a line).
        """
        if len(cluster) < 4:
            return False
        xs = [x for x, y in cluster]
        ys = [y for x, y in cluster]
        width = max(xs) - min(xs) + 1
        height = max(ys) - min(ys) + 1
        return width >= 2 and height >= 2

    def _color_key(self, cell):
        """Normalize a board cell to a comparable color key."""
        if hasattr(cell, 'is_garbage') and getattr(cell, 'is_garbage'):
            return None  # garbage does not form color clusters directly
        if hasattr(cell, 'color'):
            return cell.color
        return cell

    def clear_clusters(self, clusters):
        """
        Clears all clusters from the board and returns the number of blocks cleared.
        """
        cleared = 0
        for cluster in clusters:
            for x, y in cluster:
                self.board.set_piece(x, y, self.board.EMPTY)
                cleared += 1
        return cleared

    def process_clears(self):
        """No-op: 2x2 cluster clearing disabled per new design (only breakers clear)."""
        return 0, 0

# Usage:
# combo = ComboManager(board)
# combo_count, total_cleared = combo.process_clears()
