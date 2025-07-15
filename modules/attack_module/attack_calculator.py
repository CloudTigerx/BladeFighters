"""
Attack Calculator - Core Math Engine for Attack System

This module contains all the mathematical formulas and logic for calculating
attack outputs based on combo data. It implements the complete attack system
as documented in the Attack Plans.

Key Features:
- Garbage block attack calculations
- Cluster strike pattern calculations  
- Horizontal to vertical conversions
- Chain combo mechanics
- All formulas from Attack Plans document
"""

from typing import List, Tuple, Dict, Any
from .data_structures import (
    ComboData, ClusterData, AttackPayload, GarbageBlockPayload, 
    ClusterStrikePayload, ClusterType, AttackType
)


class AttackCalculator:
    """Core calculator for all attack types"""
    
    def __init__(self):
        """Initialize the attack calculator"""
        self.garbage_formula_enabled = True
        self.board_state_modifier_enabled = False  # Disabled per user request
    
    # ========== GARBAGE BLOCK CALCULATIONS ==========
    
    @staticmethod
    def calculate_garbage_blocks(combo_size: int, chain_length: int, 
                               enemy_board_height: int = None) -> int:
        """
        Calculate garbage block count using the formula:
        blocks_sent = combo_size * chain_length
        
        Args:
            combo_size: Number of blocks in the combo
            chain_length: Position in the chain (1=single, 2=double, etc.)
            enemy_board_height: Height of enemy board (unused - disabled)
            
        Returns:
            Number of garbage blocks to send
        """
        if combo_size <= 0 or chain_length <= 0:
            return 0
            
        total_blocks = combo_size * chain_length
        
        # Board state modifier is disabled per user request
        # if enemy_board_height and enemy_board_height < 6:  # Half of 12
        #     total_blocks = total_blocks // 2
                
        return total_blocks
    
    def calculate_garbage_attack(self, combo_size: int, chain_length: int, 
                               enemy_board_height: int = None) -> int:
        """
        Calculate garbage block count using the formula:
        blocks_sent = combo_size * chain_length
        
        Args:
            combo_size: Number of blocks in the combo
            chain_length: Position in the chain (1=single, 2=double, etc.)
            enemy_board_height: Height of enemy board (unused - disabled)
            
        Returns:
            Number of garbage blocks to send
        """
        return self.calculate_garbage_blocks(combo_size, chain_length, enemy_board_height)
    
    # ========== CLUSTER STRIKE CALCULATIONS ==========
    
    def calculate_cluster_strike(self, cluster_type: str, combo_level: int) -> Tuple[str, int, int]:
        """
        Calculate cluster strike pattern based on cluster type and combo level
        
        Args:
            cluster_type: Type of cluster (2x2, 3x3, 3x2, 4x4, etc.)
            combo_level: Level of combo (1=single, 2=double, etc.)
            
        Returns:
            Tuple of (pattern, width, height)
        """
        if cluster_type == "2x2":
            return self.get_2x2_pattern_full(combo_level)
        elif cluster_type == "3x3":
            return self.get_3x3_pattern_full(combo_level)
        elif cluster_type == "3x2":
            return self.get_3x2_pattern_full(combo_level)
        elif cluster_type == "4x4":
            return self.get_4x4_pattern_full(combo_level)
        elif cluster_type == "5x2":
            return self.get_5x2_pattern_full(combo_level)
        elif cluster_type == "6x2":
            return self.get_6x2_pattern_full(combo_level)
        else:
            # Default fallback
            return "1x4_vertical", 1, 4
    
    # ========== STATIC PATTERN METHODS (for testing) ==========
    
    @staticmethod
    def get_2x2_pattern(combo_level: int) -> str:
        """
        2x2 cluster scaling: 1x4 → 2x4 → 2x6 → 2x8 → 2x10 → 2x12
        """
        patterns = {
            1: "1x4_vertical",
            2: "2x4_vertical",
            3: "2x6_vertical",
            4: "2x8_vertical",
            5: "2x10_vertical",
            6: "2x12_vertical"
        }
        return patterns.get(combo_level, "2x12_vertical")
    
    @staticmethod
    def get_3x3_pattern(combo_level: int) -> str:
        """
        3x3 cluster scaling: 2x4 → 3x6 → 3x9 → 3x12+
        """
        patterns = {
            1: "2x4_vertical",
            2: "3x6_vertical",
            3: "3x9_vertical",
            4: "3x12_vertical"
        }
        return patterns.get(combo_level, "3x12_vertical")
    
    @staticmethod
    def get_3x2_pattern(combo_level: int) -> str:
        """
        3x2 cluster: horizontal → converts to vertical at triple+
        Single: 3x2 horizontal
        Double: 6x2 horizontal (but only 6 blocks can enter screen)
        Triple+: 2x12 vertical (conversion rule)
        """
        if combo_level == 1:
            return "3x2_horizontal"
        elif combo_level == 2:
            return "6x2_horizontal"
        else:  # Triple and beyond
            return "2x12_vertical"
    
    @staticmethod
    def get_4x4_pattern(combo_level: int) -> str:
        """
        4x4 cluster: Always creates TWO 2x? vertical swords
        """
        base_pattern = AttackCalculator.get_2x2_pattern(combo_level)
        return f"two_{base_pattern}"
    
    # ========== INSTANCE PATTERN METHODS (for full tuple data) ==========
    
    def get_2x2_pattern_full(self, combo_level: int) -> Tuple[str, int, int]:
        """
        2x2 cluster scaling: 1x4 → 2x4 → 2x6 → 2x8 → 2x10 → 2x12
        """
        patterns = {
            1: ("1x4_vertical", 1, 4),
            2: ("2x4_vertical", 2, 4),
            3: ("2x6_vertical", 2, 6),
            4: ("2x8_vertical", 2, 8),
            5: ("2x10_vertical", 2, 10),
            6: ("2x12_vertical", 2, 12)
        }
        return patterns.get(combo_level, ("2x12_vertical", 2, 12))
    
    def get_3x3_pattern_full(self, combo_level: int) -> Tuple[str, int, int]:
        """
        3x3 cluster scaling: 2x4 → 3x6 → 3x9 → 3x12+
        """
        patterns = {
            1: ("2x4_vertical", 2, 4),
            2: ("3x6_vertical", 3, 6),
            3: ("3x9_vertical", 3, 9),
            4: ("3x12_vertical", 3, 12)
        }
        return patterns.get(combo_level, ("3x12_vertical", 3, 12))
    
    def get_3x2_pattern_full(self, combo_level: int) -> Tuple[str, int, int]:
        """
        3x2 cluster: horizontal → converts to vertical at triple+
        Single: 3x2 horizontal
        Double: 6x2 horizontal (but only 6 blocks can enter screen)
        Triple+: 2x12 vertical (conversion rule)
        """
        if combo_level == 1:
            return ("3x2_horizontal", 3, 2)
        elif combo_level == 2:
            return ("6x2_horizontal", 6, 2)
        else:  # Triple and beyond
            return ("2x12_vertical", 2, 12)
    
    def get_4x4_pattern_full(self, combo_level: int) -> Tuple[str, int, int]:
        """
        4x4 cluster: Always creates TWO 2x? vertical swords
        """
        base_pattern = self.get_2x2_pattern_full(combo_level)
        return (f"two_{base_pattern[0]}_swords", base_pattern[1], base_pattern[2])
    
    def get_5x2_pattern_full(self, combo_level: int) -> Tuple[str, int, int]:
        """
        5x2 cluster: Similar to 3x2 but converts earlier
        Following the >3 width rule from original system
        """
        if combo_level == 1:
            return ("5x2_horizontal", 5, 2)
        else:  # Double and beyond - convert to vertical
            return ("2x12_vertical", 2, 12)
    
    def get_6x2_pattern_full(self, combo_level: int) -> Tuple[str, int, int]:
        """
        6x2 cluster: Exactly fills board width, converts on double
        """
        if combo_level == 1:
            return ("6x2_horizontal", 6, 2)
        else:  # Double and beyond - convert to vertical
            return ("2x12_vertical", 2, 12)
    
    # ========== CHAIN COMBO CALCULATIONS ==========
    
    @staticmethod
    def calculate_chain_attacks(combo_data) -> List[ClusterStrikePayload]:
        """
        Calculate all attacks for a chain of clusters
        
        Args:
            combo_data: ComboData containing cluster chain information
            
        Returns:
            List of ClusterStrikePayload objects
        """
        all_attacks = []
        
        # Process each cluster in the chain
        for cluster in combo_data.clusters:
            # Each cluster gets combo level equal to its position in the chain
            pattern = AttackCalculator.get_cluster_pattern_by_type(cluster.type, cluster.position)
            
            # Determine dimensions from pattern
            width, height = AttackCalculator.parse_pattern_dimensions(pattern)
            
            # Create a dummy ComboData for source_combo (required by ClusterStrikePayload)
            dummy_combo = type('DummyCombo', (), {
                'size': 0,
                'chain_length': 1,
                'position_in_chain': cluster.position,
                'clusters': [],
                'garbage_blocks': 0,
                'target_player': 1
            })()
            
            # Create cluster strike payload
            attack_payload = ClusterStrikePayload(
                attack_type=AttackType.CLUSTER_STRIKE,
                target_player=1,  # Default target
                delivery_delay=1.0,
                source_combo=dummy_combo,
                strike_pattern=pattern,
                strike_count=1,
                strike_width=width,
                strike_height=height
            )
            
            # Add a pattern property for backward compatibility with tests
            attack_payload.pattern = pattern
            attack_payload.width = width
            attack_payload.height = height
            
            all_attacks.append(attack_payload)
        
        return all_attacks
    
    @staticmethod
    def get_cluster_pattern_by_type(cluster_type: str, combo_level: int) -> str:
        """Get cluster pattern by type and combo level"""
        if cluster_type == "2x2":
            return AttackCalculator.get_2x2_pattern(combo_level)
        elif cluster_type == "3x3":
            return AttackCalculator.get_3x3_pattern(combo_level)
        elif cluster_type == "3x2":
            return AttackCalculator.get_3x2_pattern(combo_level)
        elif cluster_type == "4x4":
            return AttackCalculator.get_4x4_pattern(combo_level)
        else:
            return "1x4_vertical"  # Default fallback
    
    @staticmethod
    def parse_pattern_dimensions(pattern: str) -> Tuple[int, int]:
        """Parse width and height from pattern string"""
        if "two_" in pattern:
            # Handle 4x4 patterns that create two swords
            inner_pattern = pattern.replace("two_", "")
            width, height = AttackCalculator.parse_pattern_dimensions(inner_pattern)
            return width, height  # Return dimensions of one sword
        
        # Extract dimensions from pattern like "2x4_vertical" or "6x2_horizontal"
        if "x" in pattern:
            dimension_part = pattern.split("_")[0]  # Get "2x4" from "2x4_vertical"
            if "x" in dimension_part:
                width_str, height_str = dimension_part.split("x")
                return int(width_str), int(height_str)
        
        # Default fallback
        return 1, 4
    
    def calculate_chain_attacks_old(self, combo_chain: List[ComboData]) -> List[AttackPayload]:
        """
        Calculate all attacks for a chain of combos (old method)
        
        Args:
            combo_chain: List of ComboData in chain order
            
        Returns:
            List of AttackPayload objects
        """
        all_attacks = []
        
        for combo in combo_chain:
            # Calculate garbage block attacks
            if combo.has_garbage_blocks:
                garbage_payload = self.create_garbage_payload(combo)
                all_attacks.append(garbage_payload)
            
            # Calculate cluster strike attacks
            if combo.has_clusters:
                for cluster in combo.clusters:
                    strike_payload = self.create_cluster_payload(cluster, combo)
                    all_attacks.append(strike_payload)
        
        return all_attacks
    
    def create_garbage_payload(self, combo: ComboData) -> GarbageBlockPayload:
        """Create garbage block payload from combo data"""
        block_count = self.calculate_garbage_attack(
            combo.garbage_blocks, 
            combo.position_in_chain
        )
        
        return GarbageBlockPayload(
            attack_type=AttackType.GARBAGE_BLOCKS,
            target_player=combo.target_player,
            delivery_delay=1.0,  # After enemy places next piece
            source_combo=combo,
            block_count=block_count
        )
    
    def create_cluster_payload(self, cluster: ClusterData, combo: ComboData) -> ClusterStrikePayload:
        """Create cluster strike payload from cluster data"""
        pattern, width, height = self.calculate_cluster_strike(
            cluster.cluster_type.value,
            cluster.combo_level
        )
        
        return ClusterStrikePayload(
            attack_type=AttackType.CLUSTER_STRIKE,
            target_player=combo.target_player,
            delivery_delay=1.0,  # After enemy places next piece
            source_combo=combo,
            strike_pattern=pattern,
            strike_count=1,
            strike_width=width,
            strike_height=height,
            source_cluster=cluster
        )
    
    # ========== ANALYSIS METHODS ==========
    
    def analyze_combo_scenario(self, scenario_description: str) -> Dict[str, Any]:
        """
        Analyze a combo scenario and return attack breakdown
        
        Args:
            scenario_description: Description of the combo scenario
            
        Returns:
            Dictionary with attack analysis
        """
        # This is a utility method for testing scenarios
        # Will be used to test the 2x3 cluster scenario
        return {
            "scenario": scenario_description,
            "implemented": True,
            "status": "Ready for testing"
        }
    
    # ========== UTILITY METHODS ==========
    
    def get_attack_summary(self, attacks: List[AttackPayload]) -> Dict[str, Any]:
        """
        Get a summary of all attacks in a list
        
        Args:
            attacks: List of attack payloads
            
        Returns:
            Dictionary with attack summary
        """
        summary = {
            "total_attacks": len(attacks),
            "garbage_blocks": 0,
            "strikes": [],
            "total_garbage_blocks": 0
        }
        
        for attack in attacks:
            if isinstance(attack, GarbageBlockPayload):
                summary["garbage_blocks"] += 1
                summary["total_garbage_blocks"] += attack.block_count
            elif isinstance(attack, ClusterStrikePayload):
                summary["strikes"].append({
                    "pattern": attack.strike_pattern,
                    "width": attack.strike_width,
                    "height": attack.strike_height
                })
        
        return summary 