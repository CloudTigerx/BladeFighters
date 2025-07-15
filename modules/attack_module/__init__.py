"""
Attack Module - Modular Attack System for Blade Fighters

This module provides a complete attack system with:
- Garbage block attacks
- Cluster strike attacks  
- Attack calculation formulas
- Event-driven architecture

Created: Phase 1 - Foundation Building
"""

from .attack_calculator import AttackCalculator
from .data_structures import ComboData, AttackPayload, GarbageBlockPayload, ClusterStrikePayload

__version__ = "1.0.0"
__author__ = "Blade Fighters Team"

# Module exports
__all__ = [
    "AttackCalculator",
    "ComboData", 
    "AttackPayload",
    "GarbageBlockPayload",
    "ClusterStrikePayload"
] 