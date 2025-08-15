# Unified Configuration Management System
# This module now uses the new unified configuration system with backward compatibility

from .compatibility_layer import ControlsServiceCompat

# Re-export the compatibility class as ControlsService for backward compatibility
ControlsService = ControlsServiceCompat

