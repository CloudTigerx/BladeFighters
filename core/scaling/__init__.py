"""
Simplified Scaling System for BladeFighters
Handles resolution detection and asset scaling for 4 supported resolutions.
"""

from .resolution_manager import ResolutionManager
from .true_resolution_scaler import TrueResolutionScaler

# Global instances - only what we need
resolution_manager = ResolutionManager()
true_resolution_scaler = TrueResolutionScaler(resolution_manager)

__all__ = [
    'ResolutionManager',
    'TrueResolutionScaler',
    'resolution_manager',
    'true_resolution_scaler'
] 