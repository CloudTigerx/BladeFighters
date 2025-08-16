# Unified Configuration Management System
# This module now uses the new unified configuration system with backward compatibility

from .compatibility_layer import ConfigServiceCompat

# Re-export the compatibility class as ConfigService for backward compatibility
ConfigService = ConfigServiceCompat

