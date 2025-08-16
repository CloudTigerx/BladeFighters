"""
TestMode Module - Comprehensive PvP Testing Environment
"""

import logging

# Version and metadata
__version__ = "1.0.0"
__author__ = "BladeFighters Development Team"
__description__ = "Extracted Core Puzzle Battle Module"

# Set up logging
logger = logging.getLogger(__name__)

# Import and export the main class
from .test_mode import TestModeRefactored as TestMode

# Public API exports
__all__ = [
    "TestMode",
    "__version__",
    "__author__",
    "__description__"
]

# Module initialization message
logger.info("TestMode Module v{} initialized".format(__version__)) 