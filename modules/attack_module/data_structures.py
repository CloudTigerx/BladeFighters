"""
Data Structures for Attack System

Defines the core data structures used throughout the attack system:
- ComboData: Information about combo chains and clusters
- AttackPayload: Base class for all attack types
- GarbageBlockPayload: Garbage block attack data
- ClusterStrikePayload: Cluster strike attack data
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum


class ClusterType(Enum):
    """Enum for different cluster types"""
    CLUSTER_2x2 = "2x2"
    CLUSTER_3x3 = "3x3"
    CLUSTER_3x2 = "3x2"
    CLUSTER_4x4 = "4x4"
    CLUSTER_5x2 = "5x2"
    CLUSTER_6x2 = "6x2"


class AttackType(Enum):
    """Enum for different attack types"""
    GARBAGE_BLOCKS = "garbage_blocks"
    CLUSTER_STRIKE = "cluster_strike"


@dataclass
class ClusterData:
    """Data structure for cluster information"""
    cluster_type: ClusterType
    width: int
    height: int
    position_in_chain: int
    combo_level: int
    blocks_broken: int
    
    @property
    def is_horizontal(self) -> bool:
        """Check if cluster is wider than tall (horizontal)"""
        return self.width > self.height
    
    @property
    def is_vertical(self) -> bool:
        """Check if cluster is taller than wide (vertical)"""
        return self.height > self.width
    
    @property
    def is_square(self) -> bool:
        """Check if cluster is equal width and height"""
        return self.width == self.height


@dataclass
class ComboData:
    """Data structure for combo information"""
    size: int                           # Total blocks broken
    chain_length: int                   # Length of the chain
    position_in_chain: int              # Position of this combo in the chain
    clusters: List[ClusterData]         # List of clusters in this combo
    garbage_blocks: int                 # Number of garbage blocks
    target_player: int                  # Which player to target
    
    @property
    def has_clusters(self) -> bool:
        """Check if combo contains clusters"""
        return len(self.clusters) > 0
    
    @property
    def has_garbage_blocks(self) -> bool:
        """Check if combo has garbage blocks"""
        return self.garbage_blocks > 0


@dataclass
class AttackPayload:
    """Base class for all attack payloads"""
    attack_type: AttackType
    target_player: int
    delivery_delay: float
    source_combo: ComboData
    
    def __post_init__(self):
        """Validate payload data"""
        if self.delivery_delay < 0:
            raise ValueError("Delivery delay cannot be negative")
        if self.target_player < 0:
            raise ValueError("Target player must be valid")


@dataclass
class GarbageBlockPayload(AttackPayload):
    """Payload for garbage block attacks"""
    block_count: int
    column_rotation_state: int = 0
    transformation_stage: int = 1
    
    def __post_init__(self):
        super().__post_init__()
        if self.block_count <= 0:
            raise ValueError("Block count must be positive")
        
        # Auto-set attack type
        self.attack_type = AttackType.GARBAGE_BLOCKS


@dataclass
class ClusterStrikePayload(AttackPayload):
    """Payload for cluster strike attacks"""
    strike_pattern: str                 # e.g., "2x6_vertical", "3x2_horizontal"
    strike_count: int
    strike_width: int
    strike_height: int
    column_rotation_state: int = 0
    transformation_stage: int = 1
    source_cluster: ClusterData = None
    
    def __post_init__(self):
        super().__post_init__()
        if self.strike_count <= 0:
            raise ValueError("Strike count must be positive")
        if self.strike_width <= 0 or self.strike_height <= 0:
            raise ValueError("Strike dimensions must be positive")
        
        # Auto-set attack type
        self.attack_type = AttackType.CLUSTER_STRIKE
    
    @property
    def is_horizontal_strike(self) -> bool:
        """Check if strike is horizontal"""
        return "horizontal" in self.strike_pattern.lower()
    
    @property
    def is_vertical_strike(self) -> bool:
        """Check if strike is vertical"""
        return "vertical" in self.strike_pattern.lower()


# Utility functions for creating data structures
def create_combo_data(size: int, chain_length: int, position: int, target_player: int) -> ComboData:
    """Factory function to create ComboData"""
    return ComboData(
        size=size,
        chain_length=chain_length,
        position_in_chain=position,
        clusters=[],
        garbage_blocks=0,
        target_player=target_player
    )


def create_cluster_data(cluster_type: str, width: int, height: int, position: int, combo_level: int) -> ClusterData:
    """Factory function to create ClusterData"""
    return ClusterData(
        cluster_type=ClusterType(cluster_type),
        width=width,
        height=height,
        position_in_chain=position,
        combo_level=combo_level,
        blocks_broken=width * height
    ) 