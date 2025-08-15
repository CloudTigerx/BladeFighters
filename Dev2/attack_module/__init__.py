"""
Attack Module

Exports the primary attack system components used by the game:
- AttackManager (main orchestration)
- Data structures for payloads and combos
- Calculator and utilities
"""

from .attack_manager import AttackManager, create_attack_manager, process_combo_simple
from .attack_calculator import AttackCalculator
from .column_rotator import ColumnRotator
from .data_structures import (
    ComboData,
    ClusterData,
    AttackPayload,
    GarbageBlockPayload,
    ClusterStrikePayload,
    AttackType,
    ClusterType,
)
from .attacks_service import AttacksService

__all__ = [
    'AttackManager',
    'create_attack_manager',
    'process_combo_simple',
    'AttackCalculator',
    'ColumnRotator',
    'AttacksService',
    # AttackDatabase family removed (rule-based engine; file deleted)
    'ComboData',
    'ClusterData',
    'AttackPayload',
    'GarbageBlockPayload',
    'ClusterStrikePayload',
    'AttackType',
    'ClusterType',
]