"""
Settings Module - Extracted Settings System
Provides clean settings management functionality for BladeFighters.
"""

# Version and metadata
__version__ = "1.0.0"
__author__ = "BladeFighters Development Team"
__description__ = "Extracted Settings System Module"

# Import and export the main class
from .settings_system import SettingsSystem

# Public API exports
__all__ = [
    "SettingsSystem",
    "__version__",
    "__author__",
    "__description__"
]

# Module initialization message
print("🎛️  Settings Module v{} initialized".format(__version__)) 