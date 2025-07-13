"""
Screen Management Module
Provides screen coordination, transitions, and state management.
"""

from .screen_manager import ScreenManager

__version__ = "1.0.0"
__all__ = ["ScreenManager"]

# Module metadata
MODULE_INFO = {
    "name": "Screen Management Module",
    "version": __version__,
    "description": "Screen coordination and transition management system",
    "author": "BladeFighters Refactoring Team",
    "dependencies": ["pygame"]
}

print(f"📺 Screen Module v{__version__} initialized") 