"""
Attack Delivery Committer
Handles committing attack payloads to the grid with piercing and transformation logic.
Extracted from TestMode to separate commit logic from planning and animation.
"""

import time
import traceback
from typing import Dict, Any, List, Set, Tuple
from dataclasses import dataclass

# Import the monitor from test_mode
try:
    from .test_mode import attack_delivery_monitor
except ImportError:
    # Fallback if import fails
    attack_delivery_monitor = None


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
        now_ms = int(time.time() * 1000)
        
        for block in plan.garbage_blocks:
            if (0 <= block.row < engine.grid_height and 
                0 <= block.column < engine.grid_width and
                engine.puzzle_grid[block.row][block.column] in ['empty', None]):
                
                # QA Monitoring: Log the write
                if attack_delivery_monitor:
                    callsite = f"{traceback.extract_stack()[-2].filename}:{traceback.extract_stack()[-2].lineno}"
                    attack_delivery_monitor.log_grid_write(player_key, block.column, block.row, f"{block.color}_garbage", callsite, now_ms)
                
                # Apply colored garbage directly - NO NEUTRAL GREY STATE
                engine.puzzle_grid[block.row][block.column] = f"{block.color}_garbage"
                
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
        now_ms = int(time.time() * 1000)
        
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
                    
                    # QA Monitoring: Log the write
                    if attack_delivery_monitor:
                        callsite = f"{traceback.extract_stack()[-2].filename}:{traceback.extract_stack()[-2].lineno}"
                        attack_delivery_monitor.log_grid_write(player_key, col, row, block_type, callsite, now_ms)
                    
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
        """
        DEPRECATED: This method contains duplicate transformation logic.
        
        The transformation logic has been moved to TestModeRefactored._on_piece_landed()
        to avoid race conditions and ensure single source of truth.
        
        This method is kept for backward compatibility but should not be used.
        """
        # DEPRECATED: Transformation logic moved to TestModeRefactored
        # This method is kept for backward compatibility but does nothing
        pass 