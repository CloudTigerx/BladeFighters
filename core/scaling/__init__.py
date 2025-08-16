"""
Simplified Scaling System for BladeFighters
Handles resolution detection and asset scaling for 4 supported resolutions.
Exports convenient singletons used by game modules and tests.
"""

from .resolution_manager import ResolutionManager
from .true_resolution_scaler import TrueResolutionScaler
from .asset_scaler import AssetScaler
from .coordinate_system import CoordinateSystem
from .ui_scaler import UIScaler

# Global instances
resolution_manager = ResolutionManager()
true_resolution_scaler = TrueResolutionScaler(resolution_manager)

# Provide asset and coordinate singletons for modules/tests
asset_scaler = AssetScaler(resolution_manager)
coordinate_system = CoordinateSystem(resolution_manager)
ui_scaler = UIScaler(resolution_manager)

__all__ = [
    'ResolutionManager',
    'TrueResolutionScaler',
    'AssetScaler',
    'CoordinateSystem',
    'UIScaler',
    'resolution_manager',
    'true_resolution_scaler',
    'asset_scaler',
    'coordinate_system',
    'ui_scaler'
]