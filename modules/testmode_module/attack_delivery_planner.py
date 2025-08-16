"""
Attack Delivery Planner
Handles planning where to place garbage blocks and strike patterns on the grid.
Extracted from TestMode to reduce complexity and improve testability.
"""

from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass


@dataclass
class DeliveryConfig:
    """Configuration for attack delivery behavior."""
    attacks_fall_enabled: bool = True
    fall_garbage_enabled: bool = True
    fall_strikes_enabled: bool = True
    enemy_only_fall: bool = False
    fall_speed_scale: float = 0.75
    lightning_breaks_enabled: bool = False
    lightning_staggered: bool = False
    lightning_hop_ms: int = 75
    lightning_affects_strikes: bool = False


@dataclass
class GarbagePlan:
    """Planned garbage block placement."""
    column: int
    row: int
    color: str


@dataclass
class StrikePlan:
    """Planned strike pattern placement."""
    columns: List[int]
    top_row: int
    height: int
    color_map: Dict[Tuple[int, int], str]
    pierce_budget: int


@dataclass
class DeliveryPlan:
    """Complete plan for delivering an attack."""
    attack_type: str  # 'garbage' or 'strike'
    target_player: str  # 'player' or 'enemy'
    blocks_remaining: int
    garbage_blocks: List[GarbagePlan]
    strike_patterns: List[StrikePlan]
    pierce_budgets: List[int]
    handedness: str
    sprinkle_side: str


class AttackDeliveryPlanner:
    """Plans where to place attack payloads on the grid."""
    
    def __init__(self, config: DeliveryConfig):
        self.config = config
    
    def plan_garbage_delivery(self, engine, attack_data: Dict[str, Any], 
                            player_key: str, item_system) -> DeliveryPlan:
        """Plan garbage block placement for a queued attack."""
        blocks_to_place = attack_data.get('blocks_remaining', 0)
        planned_blocks = []
        
        # Build simulated occupancy to avoid conflicts
        planned_occupancy = [[(grid_cell not in ['empty', None]) 
                            for grid_cell in row] for row in engine.puzzle_grid]
        
        # Set sweep order by side
        side = attack_data.get('sprinkle_side', 'R')
        cols_order = list(range(engine.grid_width))
        if side == 'R':
            cols_order = list(reversed(cols_order))
        
        blocks_placed = 0
        while blocks_placed < blocks_to_place:
            for column in cols_order:
                if blocks_placed >= blocks_to_place:
                    break
                    
                # Respect instakill cap in column 4 (index 3)
                if column == 3:
                    filled = sum(1 for y in range(engine.grid_height-1, -1, -1) 
                               if engine.puzzle_grid[y][column] not in ['empty', None])
                    if filled >= 10:
                        blocks_placed += 1  # waste
                        continue
                
                # Find next landing spot in this column
                landing_row = None
                for row in range(engine.grid_height - 1, -1, -1):
                    if not planned_occupancy[row][column]:
                        landing_row = row
                        break
                        
                if landing_row is None:
                    blocks_placed += 1  # full column -> waste
                    continue
                
                # Determine color per column
                col_color = item_system.get_garbage_color_for_column(column)
                planned_blocks.append(GarbagePlan(
                    column=column,
                    row=landing_row,
                    color=col_color
                ))
                planned_occupancy[landing_row][column] = True
                blocks_placed += 1
        
        return DeliveryPlan(
            attack_type='garbage',
            target_player=player_key,
            blocks_remaining=len(planned_blocks),
            garbage_blocks=planned_blocks,
            strike_patterns=[],
            pierce_budgets=[],
            handedness=attack_data.get('handedness', 'R'),
            sprinkle_side=side
        )
    
    def plan_strike_delivery(self, engine, attack_data: Dict[str, Any], 
                           player_key: str, item_system, column_rotator) -> DeliveryPlan:
        """Plan strike pattern placement for a queued attack."""
        strike_details = attack_data.get('strike_details', [])
        pierce_budgets = attack_data.get('pierce_budgets', [1] * len(strike_details))
        planned_patterns = []
        
        # Track reserved columns to avoid stacking
        reserved_spans = set()
        
        for idx, dimensions in enumerate(strike_details):
            try:
                if 'x' in dimensions:
                    width, height = map(int, dimensions.split('x'))
                else:
                    width, height = 1, int(dimensions)
            except Exception:
                continue
            
            # Find starting column
            start_column = self._find_strike_starting_column(
                engine, width, column_rotator, height, reserved_spans)
            if start_column is None:
                continue
            
            # Determine landing position across width
            max_placement_row = engine.grid_height - 1
            for col in range(start_column, start_column + width):
                placement_row = engine.grid_height - 1
                while placement_row >= 0 and engine.puzzle_grid[placement_row][col] not in ['empty', None]:
                    placement_row -= 1
                max_placement_row = min(max_placement_row, placement_row)
            
            # Truncate height if needed
            if max_placement_row - height + 1 < 0:
                height = max_placement_row + 1
            
            if height <= 0:
                continue
            
            # Build color map
            color_map = {}
            for col in range(start_column, start_column + width):
                for row in range(max_placement_row - height + 1, max_placement_row + 1):
                    col_color = item_system.get_strike_color_for_cell(col, row, engine.grid_height)
                    color_map[(col, row)] = col_color
            
            planned_patterns.append(StrikePlan(
                columns=list(range(start_column, start_column + width)),
                top_row=max_placement_row - height + 1,
                height=height,
                color_map=color_map,
                pierce_budget=int(pierce_budgets[idx] if idx < len(pierce_budgets) else 1)
            ))
            
            # Reserve the span
            for c in range(start_column, min(start_column + width, engine.grid_width)):
                reserved_spans.add(c)
        
        return DeliveryPlan(
            attack_type='strike',
            target_player=player_key,
            blocks_remaining=sum(len(p.columns) * p.height for p in planned_patterns),
            garbage_blocks=[],
            strike_patterns=planned_patterns,
            pierce_budgets=pierce_budgets,
            handedness=attack_data.get('handedness', 'R'),
            sprinkle_side=attack_data.get('sprinkle_side', 'R')
        )
    
    def _find_strike_starting_column(self, engine, width: int, column_rotator, 
                                   strike_height: int, reserved_spans: set) -> Optional[int]:
        """Find a suitable starting column for a strike pattern."""
        # Use column rotator logic (simplified from TestMode)
        for col in range(engine.grid_width - width + 1):
            # Check if any column in span is reserved
            span_available = True
            for c in range(col, col + width):
                if c in reserved_spans:
                    span_available = False
                    break
            
            if not span_available:
                continue
            
            # Check if pattern fits
            fits = True
            for c in range(col, col + width):
                if c >= engine.grid_width:
                    fits = False
                    break
                # Check if there's space for the height
                placement_row = engine.grid_height - 1
                while placement_row >= 0 and engine.puzzle_grid[placement_row][c] not in ['empty', None]:
                    placement_row -= 1
                if placement_row - strike_height + 1 < 0:
                    fits = False
                    break
            
            if fits:
                return col
        
        return None 