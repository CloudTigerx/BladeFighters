"""
Comprehensive Scaling System for BladeFighters
Handles resolution detection, UI scaling, asset scaling, and coordinate transformations.
"""

from .resolution_manager import ResolutionManager
from .ui_scaler import UIScaler
from .asset_scaler import AssetScaler
from .coordinate_system import CoordinateSystem

# Global instances
resolution_manager = ResolutionManager()
ui_scaler = UIScaler(resolution_manager)
asset_scaler = AssetScaler(resolution_manager)
coordinate_system = CoordinateSystem(resolution_manager)

__all__ = [
    'ResolutionManager',
    'UIScaler', 
    'AssetScaler',
    'CoordinateSystem',
    'resolution_manager',
    'ui_scaler',
    'asset_scaler',
    'coordinate_system'
] 