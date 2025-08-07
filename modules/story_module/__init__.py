"""
Story System Module
Provides beautiful story content loading, display, and scrolling functionality.
"""

from .story_system import StorySystem

__version__ = "1.0.0"
__all__ = ["StorySystem"]

# Module metadata
MODULE_INFO = {
    "name": "Story System Module",
    "version": __version__,
    "description": "Beautiful story content management and display system",
    "author": "BladeFighters Refactoring Team",
    "dependencies": ["pygame"]
}

print(f"📚 Story Module v{__version__} initialized") 