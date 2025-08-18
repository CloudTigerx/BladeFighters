"""
Attack Manager - Central Coordinator for Attack System

This module provides the main interface for the attack system, coordinating
between the calculator, payload tracker, and game engine integration.

Key Features:
- Processes combo events from the game engine
- Generates attacks using the calculator
- Manages attack queues and delivery
- Provides clean integration interface
"""

import time
import math
from typing import List, Dict, Any, Optional, Tuple
from .attack_calculator import AttackCalculator
from .data_structures import (
    ComboData, ClusterData, AttackPayload, GarbageBlockPayload,
    ClusterStrikePayload, ClusterType, AttackType
)


class AttackManager:
    """
    Central coordinator for the attack system.
    
    This class provides the main interface between the game engine and the
    attack system, handling combo processing, attack generation, and delivery.
    """
    
    def __init__(self, player1_grid=None, player2_grid=None):
        """
        Initialize the attack manager.
        
        Args:
            player1_grid: Reference to player 1's puzzle grid
            player2_grid: Reference to player 2's puzzle grid
        """
        self.player1_grid = player1_grid
        self.player2_grid = player2_grid
        
        # Attack queues for each player
        self.player1_attacks: List[AttackPayload] = []
        self.player2_attacks: List[AttackPayload] = []
        
        # Column rotation state for attack placement (shared across both players per spec)
        self.column_rotation_state = 0
        # Column rotation sequence per spec (1-indexed): 1,6,2,5,3,4
        # Converted to 0-based in get_next_column_for_attack
        self.column_sequence = [1, 6, 2, 5, 3, 4]

        # Handedness alternation R,L,R,L shared between opponents
        self.handedness_index = 0  # 0=Right, 1=Left

        # Deterministic vertical drop patterns (1-based columns from spec), avoiding column 4
        # 1-wide pattern: 2, 3, 5, 5, 6, 1
        # 2-wide pattern: (2/3), (2/3), (5/6), (5/6), (1/2), (2/3), (5/6), (2/3), (5/6), (1/2)
        # 3-wide pattern: always (1/2/3), repeated length 4 for index advancement
        self.vertical_patterns = {
            1: [2, 3, 5, 5, 6, 1],
            2: [(2, 3), (2, 3), (5, 6), (5, 6), (1, 2), (2, 3), (5, 6), (2, 3), (5, 6), (1, 2)],
            3: [(1, 2, 3), (1, 2, 3), (1, 2, 3), (1, 2, 3)],
        }
        self.vertical_pattern_indices = {1: 0, 2: 0, 3: 0}
        
        # Attack statistics
        self.attack_stats = {
            'total_attacks_sent': 0,
            'total_garbage_blocks_sent': 0,
            'total_strikes_sent': 0,
            'chains_processed': 0
        }
        
        # Configuration
        self.attack_delay = 1.0  # Seconds before attack delivery
        self.garbage_transform_time = 3.0  # Seconds for garbage transformation
        self.strike_transform_time = 4.0  # Seconds for strike transformation
        
        
    
    def process_combo(self, broken_blocks: List[Tuple[int, int, str]], 
                     is_cluster: bool, combo_multiplier: int,
                     player_id: int = 1) -> Dict[str, Any]:
        """
        Process a combo event from the game engine.
        
        Args:
            broken_blocks: List of (x, y, color) tuples for broken blocks
            is_cluster: Whether this was a cluster break
            combo_multiplier: Chain multiplier (1=single, 2=double, etc.)
            player_id: ID of the player who made the combo (1 or 2)
            
        Returns:
            Dictionary with attack generation results
        """
        
        
        # Update statistics
        self.attack_stats['chains_processed'] += 1
        
        # Detect all valid rectangular sub-clusters inside the broken set (per color)
        clusters, covered_positions = self._detect_subrectangle_clusters(broken_blocks)
        
        # Garbage should NOT count cluster cells. Compute garbage pool as non-cluster broken cells.
        total_broken = len(broken_blocks)
        non_cluster_cells = 0
        if covered_positions:
            # covered_positions contains (x,y) cells used by clusters
            broken_pos = {(x, y) for (x, y, _c) in broken_blocks}
            non_cluster_cells = max(0, len(broken_pos - covered_positions))
        else:
            non_cluster_cells = total_broken
        
        # FIXED: Justin's formula: (blocks × combo) ÷ 2
        garbage_count = (non_cluster_cells * combo_multiplier) // 2
        
        
        # Log cluster detection results
        
        
        # Generate attacks
        attacks_generated = []
        
        # Generate garbage block attack if we have blocks
        if garbage_count > 0:
            garbage_attack = self._create_garbage_attack(
                garbage_count, player_id, combo_multiplier
            )
            attacks_generated.append(garbage_attack)
            self.attack_stats['total_garbage_blocks_sent'] += garbage_count
        
        # Generate cluster strikes if we have clusters
        if clusters:
            for i, cluster in enumerate(clusters):
                cluster.position_in_chain = i + 1  # Set position in cluster chain
                cluster.combo_level = combo_multiplier  # Set combo level
                
                # Calculate what the strike should be
                calculator = AttackCalculator()
                expected_strike = calculator.calculate_cluster_strike(cluster.cluster_type.value, cluster.combo_level)
                
                strike_attack = self._create_cluster_strike(
                    cluster, player_id, combo_multiplier
                )
                attacks_generated.append(strike_attack)
                self.attack_stats['total_strikes_sent'] += 1
        
        # Add attacks to appropriate queue
        target_player = 2 if player_id == 1 else 1
        self._add_attacks_to_queue(attacks_generated, target_player)
        
        # Update statistics
        self.attack_stats['total_attacks_sent'] += len(attacks_generated)
        
        return {
            'attacks_generated': len(attacks_generated),
            'garbage_blocks': garbage_count,
            'cluster_strikes': len(clusters),
            'target_player': target_player,
            'attacks': attacks_generated
        }
    
    def _detect_clusters_in_broken_blocks(self, broken_blocks: List[Tuple[int, int, str]]) -> List[ClusterData]:
        """
        Detect clusters in the broken blocks using proper spatial analysis.
        
        Args:
            broken_blocks: List of (x, y, color) tuples
            
        Returns:
            List of detected clusters
        """
        clusters = []
        
        if len(broken_blocks) < 4:
            return clusters
        
        # Extract positions and analyze spatial arrangement
        positions = [(x, y) for x, y, _ in broken_blocks]
        
        # Find bounding box
        min_x = min(pos[0] for pos in positions)
        max_x = max(pos[0] for pos in positions)
        min_y = min(pos[1] for pos in positions)
        max_y = max(pos[1] for pos in positions)
        
        # Calculate actual dimensions
        width = max_x - min_x + 1
        height = max_y - min_y + 1
        
        # Check if all positions within bounding box are filled (true rectangular cluster)
        expected_blocks = width * height
        position_set = set(positions)
        
        # Generate all positions in the bounding box
        all_positions_in_box = set()
        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                all_positions_in_box.add((x, y))
        
        # Verify it's a complete rectangular cluster
        if position_set == all_positions_in_box and len(positions) == expected_blocks:
            # Determine cluster type based on actual dimensions
            # Reject skinny rectangles (must be at least 2x2)
            if width < 2 or height < 2:
                print(f"   Spatial analysis: rectangle {width}x{height} is too thin for a cluster")
                return clusters
            if width == 2 and height == 2:
                cluster_type = ClusterType.CLUSTER_2x2
            elif width == 3 and height == 3:
                cluster_type = ClusterType.CLUSTER_3x3
            elif width == 3 and height == 2:
                cluster_type = ClusterType.CLUSTER_3x2
            elif width == 2 and height == 3:
                cluster_type = ClusterType.CLUSTER_2x3
            elif width == 4 and height == 4:
                cluster_type = ClusterType.CLUSTER_4x4
            elif width == 5 and height == 2:
                cluster_type = ClusterType.CLUSTER_5x2
            elif width == 2 and height == 5:
                cluster_type = ClusterType.CLUSTER_2x5
            elif width == 6 and height == 2:
                cluster_type = ClusterType.CLUSTER_6x2
            elif width == 2 and height == 6:
                cluster_type = ClusterType.CLUSTER_2x6
            else:
                # Unrecognized rectangle size; not a valid cluster
                print(f"   Spatial analysis: rectangle {width}x{height} not a recognized cluster size")
                return clusters
            
            cluster = ClusterData(
                cluster_type=cluster_type,
                width=width,
                height=height,
                position_in_chain=1,
                combo_level=1,
                blocks_broken=len(broken_blocks)
            )
            clusters.append(cluster)
            
            print(f"   Spatial analysis: {min_x},{min_y} to {max_x},{max_y} = {width}x{height} cluster")
        else:
            print(f"   Spatial analysis: Not a complete rectangular cluster (scattered or non-rectangular)")
        
        return clusters

    def _detect_subrectangle_clusters(self, broken_blocks: List[Tuple[int, int, str]]) -> Tuple[List[ClusterData], set]:
        """Find all rectangular sub-clusters (permitted sizes) within the broken set, per color.
        Returns (clusters, covered_positions_set).
        """
        if not broken_blocks:
            return [], set()

        # Allowed cluster dimensions (width, height) with normalized width>=height
        # Include both orientations so 2x3 is detected and normalized to 3x2
        allowed_dims = [(4, 4), (6, 2), (2, 6), (5, 2), (2, 5), (3, 3), (3, 2), (2, 3), (2, 2)]

        # Group positions by color
        color_to_positions: Dict[str, set] = {}
        for x, y, color in broken_blocks:
            color_to_positions.setdefault(color, set()).add((x, y))

        detected: List[ClusterData] = []
        covered: set = set()

        # Greedy detection: larger areas first, non-overlapping
        for color, positions in color_to_positions.items():
            # Work on a mutable copy
            remaining = set(positions)

            # Precompute bounds to scan potential top-left corners
            if not remaining:
                continue
            xs = [p[0] for p in remaining]
            ys = [p[1] for p in remaining]
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)

            # Try each allowed dimension, largest first
            for width, height in allowed_dims:
                # Scan top-left candidates
                x = min_x
                while x <= max_x - (width - 1):
                    y = min_y
                    while y <= max_y - (height - 1):
                        # Build rectangle cells
                        rect_cells = {(x + dx, y + dy) for dx in range(width) for dy in range(height)}
                        # Check all cells of this color are in remaining
                        if rect_cells.issubset(remaining):
                            # Record cluster
                            cluster_type = None
                            if width == 2 and height == 2:
                                cluster_type = ClusterType.CLUSTER_2x2
                            elif width == 3 and height == 3:
                                cluster_type = ClusterType.CLUSTER_3x3
                            elif width == 3 and height == 2:
                                cluster_type = ClusterType.CLUSTER_3x2
                            elif width == 4 and height == 4:
                                cluster_type = ClusterType.CLUSTER_4x4
                            elif width == 5 and height == 2:
                                cluster_type = ClusterType.CLUSTER_5x2
                            elif width == 2 and height == 5:
                                cluster_type = ClusterType.CLUSTER_2x5
                            elif width == 6 and height == 2:
                                cluster_type = ClusterType.CLUSTER_6x2
                            elif width == 2 and height == 6:
                                cluster_type = ClusterType.CLUSTER_2x6
                            elif width == 2 and height == 3:
                                cluster_type = ClusterType.CLUSTER_2x3
                            
                            if cluster_type is not None:
                                detected.append(ClusterData(
                                    cluster_type=cluster_type,
                                    width=width,
                                    height=height,
                                    position_in_chain=1,
                                    combo_level=1,
                                    blocks_broken=width * height
                                ))
                                # Remove cells to avoid overlap
                                remaining.difference_update(rect_cells)
                                covered.update(rect_cells)
                                # Advance y past this rectangle to reduce rescans
                                y += height
                                continue
                        y += 1
                    x += 1

        return detected, covered
    
    def _create_garbage_attack(self, block_count: int, source_player: int, 
                              combo_multiplier: int) -> GarbageBlockPayload:
        """Create a garbage block attack payload."""
        # Create dummy combo data for the payload
        dummy_combo = ComboData(
            size=block_count,
            chain_length=combo_multiplier,
            position_in_chain=combo_multiplier,
            clusters=[],
            garbage_blocks=block_count,
            target_player=2 if source_player == 1 else 1
        )
        
        return GarbageBlockPayload(
            attack_type=AttackType.GARBAGE_BLOCKS,
            target_player=2 if source_player == 1 else 1,
            delivery_delay=self.attack_delay,
            source_combo=dummy_combo,
            block_count=block_count
        )
    
    def _create_cluster_strike(self, cluster: ClusterData, source_player: int,
                              combo_multiplier: int) -> ClusterStrikePayload:
        """Create a cluster strike attack payload."""
        # Calculate strike pattern
        calculator = AttackCalculator()
        # Use actual orientation (width x height) so vertical clusters (e.g., 2x3) scale correctly
        oriented_type = f"{cluster.width}x{cluster.height}"
        pattern, width, height = calculator.calculate_cluster_strike(
            oriented_type, cluster.combo_level
        )
        
        # Create dummy combo data for the payload
        dummy_combo = ComboData(
            size=cluster.blocks_broken,
            chain_length=combo_multiplier,
            position_in_chain=combo_multiplier,
            clusters=[cluster],
            garbage_blocks=0,
            target_player=2 if source_player == 1 else 1
        )
        
        return ClusterStrikePayload(
            attack_type=AttackType.CLUSTER_STRIKE,
            target_player=2 if source_player == 1 else 1,
            delivery_delay=self.attack_delay,
            source_combo=dummy_combo,
            strike_pattern=pattern,
            strike_count=1,
            strike_width=width,
            strike_height=height,
            source_cluster=cluster
        )
    
    def _create_fallback_cluster(self, broken_blocks: List[Tuple[int, int, str]]) -> List[ClusterData]:
        """
        Create a fallback cluster when game engine detects cluster but spatial analysis fails.
        
        Args:
            broken_blocks: List of (x, y, color) tuples
            
        Returns:
            List with one fallback cluster
        """
        positions = [(x, y) for x, y, _ in broken_blocks]
        
        # Find approximate dimensions
        min_x = min(pos[0] for pos in positions)
        max_x = max(pos[0] for pos in positions)
        min_y = min(pos[1] for pos in positions)
        max_y = max(pos[1] for pos in positions)
        
        width = max_x - min_x + 1
        height = max_y - min_y + 1
        block_count = len(broken_blocks)
        
        # Determine cluster type based on approximate dimensions and block count
        if block_count == 4 and width == 2 and height == 2:
            cluster_type = ClusterType.CLUSTER_2x2
        elif block_count >= 9 and width == 3 and height == 3:
            cluster_type = ClusterType.CLUSTER_3x3
        elif block_count >= 6 and ((width == 3 and height == 2) or (width == 2 and height == 3)):
            cluster_type = ClusterType.CLUSTER_3x2
            # Normalize to 3x2 format
            if width == 2 and height == 3:
                width, height = 3, 2
        elif block_count >= 16 and width == 4 and height == 4:
            cluster_type = ClusterType.CLUSTER_4x4
        elif block_count >= 10 and ((width == 5 and height == 2) or (width == 2 and height == 5)):
            cluster_type = ClusterType.CLUSTER_5x2
            # Normalize to 5x2 format
            if width == 2 and height == 5:
                width, height = 5, 2
        elif block_count >= 12 and ((width == 6 and height == 2) or (width == 2 and height == 6)):
            cluster_type = ClusterType.CLUSTER_6x2
            # Normalize to 6x2 format
            if width == 2 and height == 6:
                width, height = 6, 2
        elif block_count == 6 and ((width == 2 and height == 3) or (width == 3 and height == 2)):
            cluster_type = ClusterType.CLUSTER_3x2
            if width == 2 and height == 3:
                width, height = 3, 2
        else:
            # Default fallback based on block count
            if block_count >= 9:
                cluster_type = ClusterType.CLUSTER_3x3
                width, height = 3, 3
            elif block_count >= 6:
                cluster_type = ClusterType.CLUSTER_3x2
                width, height = 3, 2
            else:
                cluster_type = ClusterType.CLUSTER_2x2
                width, height = 2, 2
        
        cluster = ClusterData(
            cluster_type=cluster_type,
            width=width,
            height=height,
            position_in_chain=1,
            combo_level=1,
            blocks_broken=block_count
        )
        
        print(f"   Fallback cluster: {width}x{height} ({cluster_type.name}) from {block_count} blocks")
        return [cluster]

    def _add_attacks_to_queue(self, attacks: List[AttackPayload], target_player: int):
        """Add attacks to the appropriate player's queue."""
        if target_player == 1:
            self.player1_attacks.extend(attacks)
        elif target_player == 2:
            self.player2_attacks.extend(attacks)
        
        print(f"🎯 Added {len(attacks)} attacks to player {target_player}'s queue")
        # Breaker-order: attacks are appended in generation order to preserve strict queueing semantics
    
    def get_next_handedness(self) -> str:
        """Return next handedness in shared sequence (R, L, R, L, ...)."""
        hand = 'R' if (self.handedness_index % 2 == 0) else 'L'
        self.handedness_index = (self.handedness_index + 1) % 2
        return hand

    def advance_column_rotation(self) -> None:
        """Advance the shared column rotation by one (counts as a turn in the pattern)."""
        self.column_rotation_state = (self.column_rotation_state + 1) % len(self.column_sequence)

    def get_next_column_for_attack(self, target_player: int) -> int:
        """
        Get the next column for attack placement using rotation.
        
        Args:
            target_player: Player to target (1 or 2)
            
        Returns:
            Column index (0-based)
        """
        current_index = self.column_rotation_state
        column = self.column_sequence[current_index]
        # Advance to next column (shared)
        self.column_rotation_state = (current_index + 1) % len(self.column_sequence)
        # Convert to 0-based indexing
        return column - 1
    
    def process_attack_queue(self, current_time: float) -> Dict[str, List[AttackPayload]]:
        """
        Process attack queues and return ready attacks.
        
        Args:
            current_time: Current game time
            
        Returns:
            Dictionary with ready attacks for each player
        """
        ready_attacks = {'player1': [], 'player2': []}
        
        # Process player 1's attacks
        remaining_attacks = []
        for attack in self.player1_attacks:
            if hasattr(attack, 'creation_time'):
                if current_time - attack.creation_time >= attack.delivery_delay:
                    ready_attacks['player1'].append(attack)
                else:
                    remaining_attacks.append(attack)
            else:
                # Set creation time if not set - set it to a time that makes the attack ready
                attack.creation_time = current_time - attack.delivery_delay
                remaining_attacks.append(attack)
        self.player1_attacks = remaining_attacks
        
        # Process player 2's attacks
        remaining_attacks = []
        for attack in self.player2_attacks:
            if hasattr(attack, 'creation_time'):
                time_diff = current_time - attack.creation_time
                if time_diff >= attack.delivery_delay:
                    ready_attacks['player2'].append(attack)
                else:
                    remaining_attacks.append(attack)
            else:
                # Set creation time if not set - set it to a time that makes the attack ready
                attack.creation_time = current_time - attack.delivery_delay
                # Check if it's ready now
                time_diff = current_time - attack.creation_time
                if time_diff >= attack.delivery_delay:
                    ready_attacks['player2'].append(attack)
                else:
                    remaining_attacks.append(attack)
        self.player2_attacks = remaining_attacks
        
        return ready_attacks
    
    def get_pending_attacks(self, target_player: int) -> List[AttackPayload]:
        """
        Get pending attacks for a specific player.
        
        Args:
            target_player: Player to get attacks for (1 or 2)
            
        Returns:
            List of pending attacks
        """
        if target_player == 1:
            return self.player1_attacks.copy()
        elif target_player == 2:
            return self.player2_attacks.copy()
        else:
            return []

    def pop_attacks_for_player(self, target_player: int) -> List[AttackPayload]:
        """Return and clear pending attacks for the specified player only."""
        if target_player == 1:
            attacks = self.player1_attacks.copy()
            self.player1_attacks.clear()
            return attacks
        if target_player == 2:
            attacks = self.player2_attacks.copy()
            self.player2_attacks.clear()
            return attacks
        return []
    
    def get_attack_statistics(self) -> Dict[str, Any]:
        """Get attack system statistics."""
        return {
            **self.attack_stats,
            'pending_attacks_p1': len(self.player1_attacks),
            'pending_attacks_p2': len(self.player2_attacks),
            'column_rotation_index': self.column_rotation_state,
            'handedness_next': 'R' if (self.handedness_index % 2 == 0) else 'L'
        }
    
    def reset_statistics(self):
        """Reset attack statistics."""
        self.attack_stats = {
            'total_attacks_sent': 0,
            'total_garbage_blocks_sent': 0,
            'total_strikes_sent': 0,
            'chains_processed': 0
        }
        print("🎯 Attack statistics reset")
    
    def clear_attack_queues(self):
        """Clear all attack queues."""
        self.player1_attacks.clear()
        self.player2_attacks.clear()
        print("🎯 Attack queues cleared")
    
    def update(self, current_time: float) -> Dict[str, Any]:
        """
        Update the attack manager.
        
        Args:
            current_time: Current game time
            
        Returns:
            Dictionary with update results
        """
        # Process attack queues
        ready_attacks = self.process_attack_queue(current_time)
        
        # Store the last ready attacks for legacy compatibility
        self._last_ready_attacks = ready_attacks
        
        # Return status
        return {
            'ready_attacks': ready_attacks,
            'statistics': self.get_attack_statistics(),
            'timestamp': current_time
        }


# Utility functions for integration
def create_attack_manager(player1_grid=None, player2_grid=None) -> AttackManager:
    """Factory function to create an AttackManager instance."""
    return AttackManager(player1_grid, player2_grid)


def process_combo_simple(broken_blocks: List[Tuple[int, int, str]], 
                        combo_multiplier: int, player_id: int = 1) -> Dict[str, Any]:
    """
    Simple combo processing function for quick integration.
    
    Args:
        broken_blocks: List of (x, y, color) tuples
        combo_multiplier: Chain multiplier
        player_id: Player who made the combo
        
    Returns:
        Dictionary with attack results
    """
    manager = AttackManager()
    is_cluster = len(broken_blocks) >= 4
    return manager.process_combo(broken_blocks, is_cluster, combo_multiplier, player_id) 