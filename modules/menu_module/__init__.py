"""
Menu Module - Extracted Menu System
Provides clean menu functionality for BladeFighters including main menu, story menu, and button creation.
"""

# Version and metadata
__version__ = "1.0.0"
__author__ = "BladeFighters Development Team"
__description__ = "Extracted Menu System Module"

# Import and export the main class
from .menu_system import MenuSystem

# Public API exports
__all__ = [
    "MenuSystem",
    "__version__",
    "__author__",
    "__description__"
]

# Module initialization message
print("🎮 Menu Module v{} initialized".format(__version__)) 