"""
TestMode Module - Extracted Core Puzzle Battle System
Provides clean puzzle battle functionality: 2 grids, piece previews, backgrounds.
Simplified to focus on core gameplay without attack system complexity.
"""

# Version and metadata
__version__ = "1.0.0"
__author__ = "BladeFighters Development Team"
__description__ = "Extracted Core Puzzle Battle Module"

# Import and export the main class
from .test_mode import TestMode

# Public API exports
__all__ = [
    "TestMode",
    "__version__",
    "__author__",
    "__description__"
]

# Module initialization message
print("🎮 TestMode Module v{} initialized".format(__version__)) 