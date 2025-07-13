"""
Screen Management Interface Contract
Defines the interface for screen coordination, transitions, and state management.
Screens handle their own events - this manages coordination between them.
"""

import pygame
from typing import Dict, List, Optional, Tuple, Any, Protocol
from abc import ABC, abstractmethod
import time


class ScreenManagerInterface(Protocol):
    """Interface for screen management system."""
    
    def __init__(self, screen: pygame.Surface, font: pygame.font.Font, width: int, height: int):
        """
        Initialize the screen manager.
        
        Args:
            screen: Pygame display surface
            font: Font for UI elements
            width: Screen width
            height: Screen height
        """
        pass
    
    def set_screen(self, screen_name: str) -> None:
        """
        Set the current screen with proper initialization.
        
        Args:
            screen_name: Name of screen to switch to
        """
        pass
    
    def get_current_screen(self) -> str:
        """
        Get the name of the current screen.
        
        Returns:
            Current screen name
        """
        pass
    
    def is_game_running(self) -> bool:
        """
        Check if the game is still running.
        
        Returns:
            True if game should continue running
        """
        pass
    
    def shutdown(self) -> None:
        """
        Shutdown the screen manager and cleanup.
        """
        pass
    
    def handle_resolution_change(self, width: int, height: int) -> None:
        """
        Handle screen resolution changes.
        
        Args:
            width: New screen width
            height: New screen height
        """
        pass
    
    def get_version(self) -> str:
        """
        Get the game version.
        
        Returns:
            Version string
        """
        pass


class ScreenSystemInterface(ABC):
    """Abstract base class for screen systems."""
    
    @abstractmethod
    def initialize(self) -> None:
        """Initialize the screen system."""
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """Cleanup the screen system."""
        pass
    
    @abstractmethod
    def update_resolution(self, width: int, height: int) -> None:
        """Update screen resolution."""
        pass


def validate_screen_manager(screen_manager_class) -> bool:
    """
    Validate that a screen manager class implements the required interface.
    
    Args:
        screen_manager_class: Class to validate
        
    Returns:
        True if class implements the interface correctly
    """
    required_methods = [
        'set_screen', 'get_current_screen', 'is_game_running', 
        'shutdown', 'handle_resolution_change', 'get_version'
    ]
    
    for method_name in required_methods:
        if not hasattr(screen_manager_class, method_name):
            print(f"❌ ScreenManager missing required method: {method_name}")
            return False
        
        method = getattr(screen_manager_class, method_name)
        if not callable(method):
            print(f"❌ ScreenManager.{method_name} is not callable")
            return False
    
    print("✅ ScreenManager interface validation passed")
    return True


# Runtime validation decorator
def validate_screen_interface(cls):
    """Decorator to validate screen manager interface at runtime."""
    if not validate_screen_manager(cls):
        raise TypeError(f"Class {cls.__name__} does not implement ScreenManagerInterface correctly")
    return cls


# Screen Manager Requirements
SCREEN_MANAGER_REQUIREMENTS = {
    "core_functionality": [
        "Screen transition management",
        "Screen state tracking", 
        "Game running state",
        "Resolution change handling",
        "Version management"
    ],
    "coordination_features": [
        "Screen initialization on transitions",
        "Cleanup on screen changes",
        "Global state management",
        "Cross-screen data persistence"
    ],
    "integration_points": [
        "Works with extracted modules (Menu, Settings, TestMode)", 
        "Preserves MP3 player in game_client",
        "Supports story system integration",
        "Handles fallback scenarios"
    ]
}

# Screen types and their responsibilities
SCREEN_TYPES = {
    "main_menu": "Main game menu with navigation",
    "settings": "Settings configuration screen", 
    "game": "Main gameplay screen",
    "test": "Test mode for puzzle battles",
    "story": "Story menu selection",
    "story_content": "Story content display with scrolling"
} 