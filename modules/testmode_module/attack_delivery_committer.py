"""
Attack Delivery Committer
Handles committing attack payloads to the grid with piercing and transformation logic.
Extracted from TestMode to separate commit logic from planning and animation.
"""

from typing import Dict, Any, List, Set, Tuple
from dataclasses import dataclass


@dataclass
class CommitResult:
    """Result of committing an attack to the grid."""
    blocks_placed: int
    blocks_pierced: int
    written_positions: Set[Tuple[int, int]]


class AttackDeliveryCommitter:
    """Handles committing attack payloads to the grid."""
    
    def __init__(self, config):
        self.config = config
    
    def commit_garbage(self, engine, plan, player_key: str) -> CommitResult:
        """Commit garbage blocks to the grid."""
        blocks_placed = 0
        written_positions = set()
        
        for block in plan.garbage_blocks:
            if (0 <= block.row < engine.grid_height and 
                0 <= block.column < engine.grid_width and
                engine.puzzle_grid[block.row][block.column] in ['empty', None]):
                
                # Apply neutral garbage first
                engine.puzzle_grid[block.row][block.column] = 'garbage_block'
                
                # Track for brightness/transformation
                player_id = 1 if player_key == 'player' else 2
                if hasattr(engine, 'test_mode') and hasattr(engine.test_mode, 'garbage_block_brightness'):
                    engine.test_mode.garbage_block_brightness[(block.column, block.row, player_id)] = {
                        'landings': 0,
                        'color': block.color,
                        'is_strike': False
                    }
                
                written_positions.add((block.column, block.row))
                blocks_placed += 1
        
        return CommitResult(
            blocks_placed=blocks_placed,
            blocks_pierced=0,
            written_positions=written_positions
        )
    
    def commit_strikes(self, engine, plan, player_key: str) -> CommitResult:
        """Commit strike patterns to the grid with piercing logic."""
        blocks_placed = 0
        blocks_pierced = 0
        written_positions = set()
        
        # Compute cluster cells to respect non-piercing rule
        cluster_cells = self._compute_cluster_cells(engine)
        
        for pattern in plan.strike_patterns:
            budget = pattern.pierce_budget
            
            for col in pattern.columns:
                for row in range(pattern.top_row, pattern.top_row + pattern.height):
                    if (col, row) in cluster_cells:
                        continue  # Don't pierce cluster cells
                    
                    # Avoid double write in same payload
                    if (col, row) in written_positions:
                        continue
                    
                    # Check if we need to pierce
                    cell = engine.puzzle_grid[row][col]
                    if cell not in ['empty', None]:
                        if budget <= 0:
                            continue  # No budget left to pierce
                        budget -= 1
                        blocks_pierced += 1
                        engine.puzzle_grid[row][col] = None
                    
                    # Place strike block
                    color = pattern.color_map.get((col, row), 'yellow')
                    block_type = f"{color}_strike"
                    engine.puzzle_grid[row][col] = block_type
                    
                    # Track for brightness/transformation
                    player_id = 1 if player_key == 'player' else 2
                    if hasattr(engine, 'test_mode') and hasattr(engine.test_mode, 'garbage_block_brightness'):
                        engine.test_mode.garbage_block_brightness[(col, row, player_id)] = {
                            'landings': 0,
                            'color': color,
                            'is_strike': True
                        }
                    
                    written_positions.add((col, row))
                    blocks_placed += 1
        
        return CommitResult(
            blocks_placed=blocks_placed,
            blocks_pierced=blocks_pierced,
            written_positions=written_positions
        )
    
    def _compute_cluster_cells(self, engine) -> Set[Tuple[int, int]]:
        """Compute which cells are part of clusters (for piercing rules)."""
        cluster_cells = set()
        
        try:
            # Use engine's cluster detection if available
            if hasattr(engine, 'find_all_clusters'):
                clusters = engine.find_all_clusters()
                for cluster in clusters:
                    cluster_cells.update(cluster)
            elif hasattr(engine, 'find_rectangular_clusters_for_render'):
                clusters = engine.find_rectangular_clusters_for_render()
                for cluster in clusters:
                    cluster_cells.update(cluster)
        except Exception:
            pass
        
        return cluster_cells
    
    def update_received_blocks(self, engine, player_key: str):
        """Update received blocks (strikes -> garbage -> normal) based on landings."""
        if not hasattr(engine, 'test_mode') or not hasattr(engine.test_mode, 'garbage_block_brightness'):
            return
        
        grid = engine.puzzle_grid
        player = 1 if player_key == 'player' else 2
        brightness_data = engine.test_mode.garbage_block_brightness
        
        # Find all strike/garbage blocks for this player and increment landing counters
        blocks_to_increment = []
        for pos_key, data in brightness_data.items():
            x, y, block_player = pos_key
            if block_player == player:
                # Check if this tracked block is still in the grid
                if (0 <= y < len(grid) and 0 <= x < len(grid[0]) and 
                    grid[y][x] and (('_garbage' in grid[y][x]) or 
                                   (grid[y][x] == 'garbage_block') or 
                                   ('_strike' in grid[y][x]))):
                    blocks_to_increment.append(pos_key)
        
        # Increment landing counters
        for pos_key in blocks_to_increment:
            brightness_data[pos_key]['landings'] += 1
        
        # Apply transformation rules
        to_demote_strikes = []  # (pos_key, new_block_type)
        to_finalize_garbage = []
        to_colorize_garbage = []
        
        for pos_key, data in list(brightness_data.items()):
            x, y, block_player = pos_key
            if block_player != player:
                continue
                
            is_strike = data.get('is_strike', False)
            color = data['color']
            current_block = None
            
            # Guard against out-of-bounds or grid changes
            if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
                current_block = grid[y][x]
            
            # Stage 1: strike demotion after 1 landing
            if is_strike and data['landings'] >= 1:
                to_demote_strikes.append((pos_key, 'garbage_block'))
            
            # Stage 2: neutral garbage -> colored garbage after 1 landing
            if (not is_strike) and data['landings'] >= 1:
                if current_block == 'garbage_block':
                    to_colorize_garbage.append((pos_key, f"{color}_garbage"))
            
            # Stage 3: colored garbage -> normal block after 2 landings
            if (not is_strike) and data['landings'] >= 2:
                if isinstance(current_block, str) and current_block.startswith(f"{color}_garbage"):
                    to_finalize_garbage.append((pos_key, f"{color}_block"))
        
        # Apply transformations
        for pos_key, new_block_type in to_demote_strikes:
            x, y, _ = pos_key
            if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
                grid[y][x] = new_block_type
                # Update tracking: now behaves like newly received garbage
                brightness_data[pos_key]['is_strike'] = False
                brightness_data[pos_key]['landings'] = 0
        
        for pos_key, new_block_type in to_colorize_garbage:
            x, y, _ = pos_key
            if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
                grid[y][x] = new_block_type
        
        for pos_key, new_block_type in to_finalize_garbage:
            x, y, _ = pos_key
            if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
                grid[y][x] = new_block_type
                # Remove from tracking once fully transformed
                brightness_data.pop(pos_key, None) 