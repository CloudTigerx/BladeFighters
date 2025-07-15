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
        
        # Column rotation state for attack placement
        self.column_rotation_state = {
            1: 0,  # Player 1's rotation index
            2: 0   # Player 2's rotation index
        }
        
        # Column rotation sequence (1-indexed, will convert to 0-indexed)
        self.column_sequence = [1, 6, 2, 5, 3, 4]
        
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
        
        print("🎯 AttackManager initialized with attack calculator")
    
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
        print(f"🔍 ATTACK CALCULATION:")
        print(f"   Input: {len(broken_blocks)} blocks, cluster={is_cluster}, multiplier={combo_multiplier}")
        
        # Update statistics
        self.attack_stats['chains_processed'] += 1
        
        # Calculate garbage block attack with detailed logging
        garbage_count = AttackCalculator.calculate_garbage_blocks(
            len(broken_blocks), combo_multiplier
        )
        print(f"   Garbage formula: {len(broken_blocks)} blocks × {combo_multiplier} combo = {garbage_count} garbage blocks")
        
        # Detect clusters in broken blocks
        clusters = self._detect_clusters_in_broken_blocks(broken_blocks)
        
        # Log cluster detection results
        if clusters:
            print(f"   Clusters detected: {len(clusters)}")
            for i, cluster in enumerate(clusters):
                print(f"     Cluster {i+1}: {cluster.width}x{cluster.height} ({cluster.cluster_type.name})")
        else:
            print(f"   No clusters detected (non-cluster combo)")
        
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
            print(f"   Generating cluster strikes:")
            for i, cluster in enumerate(clusters):
                cluster.position_in_chain = i + 1  # Set position in cluster chain
                cluster.combo_level = combo_multiplier  # Set combo level
                
                # Calculate what the strike should be
                expected_strike = AttackCalculator.calculate_cluster_strike(cluster)
                print(f"     Cluster {i+1}: {cluster.width}x{cluster.height} level {combo_multiplier} → {expected_strike['pattern']}")
                
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
        Detect clusters in the broken blocks.
        
        This is a simplified cluster detection for now. In a full implementation,
        this would analyze the spatial arrangement of blocks.
        
        Args:
            broken_blocks: List of (x, y, color) tuples
            
        Returns:
            List of detected clusters
        """
        clusters = []
        
        # Simple cluster detection based on block count
        # In a full implementation, this would analyze spatial patterns
        block_count = len(broken_blocks)
        
        if block_count >= 4:
            # Determine cluster type based on block count
            if block_count == 4:
                cluster_type = ClusterType.CLUSTER_2x2
                width, height = 2, 2
            elif block_count >= 9:
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
            clusters.append(cluster)
        
        return clusters
    
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
        pattern, width, height = calculator.calculate_cluster_strike(
            cluster.cluster_type.value, cluster.combo_level
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
    
    def _add_attacks_to_queue(self, attacks: List[AttackPayload], target_player: int):
        """Add attacks to the appropriate player's queue."""
        if target_player == 1:
            self.player1_attacks.extend(attacks)
        elif target_player == 2:
            self.player2_attacks.extend(attacks)
        
        print(f"🎯 Added {len(attacks)} attacks to player {target_player}'s queue")
    
    def get_next_column_for_attack(self, target_player: int) -> int:
        """
        Get the next column for attack placement using rotation.
        
        Args:
            target_player: Player to target (1 or 2)
            
        Returns:
            Column index (0-based)
        """
        current_index = self.column_rotation_state[target_player]
        column = self.column_sequence[current_index]
        
        # Advance to next column
        self.column_rotation_state[target_player] = (current_index + 1) % len(self.column_sequence)
        
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
                # Set creation time if not set
                attack.creation_time = current_time
                remaining_attacks.append(attack)
        self.player1_attacks = remaining_attacks
        
        # Process player 2's attacks
        remaining_attacks = []
        for attack in self.player2_attacks:
            if hasattr(attack, 'creation_time'):
                if current_time - attack.creation_time >= attack.delivery_delay:
                    ready_attacks['player2'].append(attack)
                else:
                    remaining_attacks.append(attack)
            else:
                # Set creation time if not set
                attack.creation_time = current_time
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
    
    def get_attack_statistics(self) -> Dict[str, Any]:
        """Get attack system statistics."""
        return {
            **self.attack_stats,
            'pending_attacks_p1': len(self.player1_attacks),
            'pending_attacks_p2': len(self.player2_attacks),
            'column_rotation_p1': self.column_rotation_state[1],
            'column_rotation_p2': self.column_rotation_state[2]
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