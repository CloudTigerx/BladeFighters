"""
Story System Interface Contract
Defines the interface for story content management, loading, and beautiful UI display.
"""

import pygame
from typing import Dict, List, Optional, Tuple, Any, Protocol
from abc import ABC, abstractmethod


class StorySystemInterface(Protocol):
    """Interface for story management system."""
    
    def __init__(self, screen: pygame.Surface, font: pygame.font.Font, width: int, height: int, menu_system: Any = None):
        """
        Initialize the story system.
        
        Args:
            screen: Pygame display surface
            font: Font for UI elements
            width: Screen width
            height: Screen height
            menu_system: Optional menu system for particle effects
        """
        pass
    
    def load_story(self, story_id: int) -> Dict[str, Any]:
        """
        Load story content from file based on story ID.
        
        Args:
            story_id: ID of the story to load
            
        Returns:
            Dictionary containing story title and content
        """
        pass
    
    def display_story_content(self, story_data: Dict[str, Any], scroll_position: int) -> int:
        """
        Display story content with beautiful UI and scrolling.
        
        Args:
            story_data: Story data dictionary
            scroll_position: Current scroll position
            
        Returns:
            Updated scroll position
        """
        pass
    
    def handle_story_events(self, events: List[pygame.event.Event], scroll_position: int) -> Tuple[Optional[str], int]:
        """
        Handle story content events (scrolling, navigation).
        
        Args:
            events: List of pygame events
            scroll_position: Current scroll position
            
        Returns:
            Tuple of (action, new_scroll_position)
        """
        pass
    
    def get_story_list(self) -> List[Dict[str, Any]]:
        """
        Get list of available stories.
        
        Returns:
            List of story metadata
        """
        pass
    
    def update_resolution(self, width: int, height: int) -> None:
        """
        Update story system for new resolution.
        
        Args:
            width: New screen width
            height: New screen height
        """
        pass


def validate_story_system(story_system_class) -> bool:
    """
    Validate that a story system class implements the required interface.
    
    Args:
        story_system_class: Class to validate
        
    Returns:
        True if class implements the interface correctly
    """
    required_methods = [
        'load_story', 'display_story_content', 'handle_story_events',
        'get_story_list', 'update_resolution'
    ]
    
    for method_name in required_methods:
        if not hasattr(story_system_class, method_name):
            print(f"❌ StorySystem missing required method: {method_name}")
            return False
        
        method = getattr(story_system_class, method_name)
        if not callable(method):
            print(f"❌ StorySystem.{method_name} is not callable")
            return False
    
    print("✅ StorySystem interface validation passed")
    return True


# Runtime validation decorator
def validate_story_interface(cls):
    """Decorator to validate story system interface at runtime."""
    if not validate_story_system(cls):
        raise TypeError(f"Class {cls.__name__} does not implement StorySystemInterface correctly")
    return cls


# Story System Requirements
STORY_SYSTEM_REQUIREMENTS = {
    "core_functionality": [
        "Story file loading from stories/ directory",
        "Story content parsing and display",
        "Beautiful scrolling interface",
        "Story navigation and selection"
    ],
    "ui_features": [
        "Semi-transparent overlay for readability",
        "Menu particles for visual appeal",
        "Chapter and text formatting",
        "Scroll indicators",
        "Multiple font sizes for hierarchy"
    ],
    "interaction_features": [
        "Keyboard scrolling (arrow keys, WASD)",
        "Mouse wheel scrolling",
        "Escape key navigation",
        "Story selection from menu"
    ],
    "integration_points": [
        "Works with MenuSystem for story menu",
        "Preserves beautiful UI design",
        "Supports story file formats",
        "Handles missing stories gracefully"
    ]
}

# Story file structure
STORY_FILE_FORMAT = {
    "title_format": "# Story Title",
    "chapter_format": "## Chapter Title", 
    "content_format": "Regular text content",
    "file_locations": "stories/saga{id}_{name}.txt"
}

# Story display settings
STORY_DISPLAY_CONFIG = {
    "fonts": {
        "title": 56,
        "chapter": 36,
        "text": 24,
        "instruction": 20
    },
    "colors": {
        "title": (255, 255, 255),
        "chapter": (220, 180, 255),
        "text": (255, 255, 255),
        "instruction": (200, 200, 200),
        "overlay": (0, 0, 0, 180)
    },
    "spacing": {
        "content_width_ratio": 0.8,
        "padding": 20,
        "line_spacing": 5,
        "chapter_spacing": 30
    }
} 