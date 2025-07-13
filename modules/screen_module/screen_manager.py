"""
Screen Manager Implementation
Handles screen coordination, transitions, and state management.
"""

import pygame
import sys
from typing import Dict, List, Optional, Tuple, Any

# Try importing the interface contract
try:
    from contracts.screen_interface_contract import ScreenManagerInterface, validate_screen_interface
    interface_available = True
except ImportError:
    # Create a dummy interface if not available
    class ScreenManagerInterface:
        pass
    
    def validate_screen_interface(cls):
        return cls
    
    interface_available = False
    print("⚠️  Screen interface contract not available, running without validation")


@validate_screen_interface
class ScreenManager:
    """
    Screen Manager implementation for coordinating screen transitions and state.
    """
    
    def __init__(self, screen: pygame.Surface, font: pygame.font.Font, width: int, height: int):
        """
        Initialize the screen manager.
        
        Args:
            screen: Pygame display surface
            font: Font for UI elements
            width: Screen width
            height: Screen height
        """
        self.screen = screen
        self.font = font
        self.width = width
        self.height = height
        
        # Screen state
        self.current_screen = "main_menu"
        self.game_running = True
        self.version = "1.0.0"
        
        # Screen initialization hooks
        self.screen_init_hooks = {}
        self.screen_cleanup_hooks = {}
        
        # Colors for UI consistency
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GRAY = (100, 100, 100)
        self.LIGHT_GRAY = (200, 200, 200)
        
        print("✅ ScreenManager initialized with core functionality")
    
    def set_screen(self, screen_name: str) -> None:
        """
        Set the current screen with proper initialization.
        
        Args:
            screen_name: Name of screen to switch to
        """
        print(f"Screen Manager: Setting screen to {screen_name}")
        
        # Run cleanup for current screen
        if self.current_screen in self.screen_cleanup_hooks:
            self.screen_cleanup_hooks[self.current_screen]()
        
        # Update current screen
        old_screen = self.current_screen
        self.current_screen = screen_name
        
        # Run initialization for new screen
        if screen_name in self.screen_init_hooks:
            self.screen_init_hooks[screen_name]()
        
        # Screen-specific initialization logic
        if screen_name == "game":
            print("Screen Manager: Initializing game screen")
        elif screen_name == "test":
            print("Screen Manager: Initializing test screen")
        elif screen_name == "settings":
            print("Screen Manager: Initializing settings screen")
        elif screen_name == "story":
            print("Screen Manager: Initializing story screen")
        elif screen_name == "story_content":
            print("Screen Manager: Initializing story content screen")
        elif screen_name == "main_menu":
            print("Screen Manager: Initializing main menu screen")
        
        print(f"Screen Manager: Transitioned from {old_screen} to {screen_name}")
    
    def get_current_screen(self) -> str:
        """
        Get the name of the current screen.
        
        Returns:
            Current screen name
        """
        return self.current_screen
    
    def is_game_running(self) -> bool:
        """
        Check if the game is still running.
        
        Returns:
            True if game should continue running
        """
        return self.game_running
    
    def shutdown(self) -> None:
        """
        Shutdown the screen manager and cleanup.
        """
        print("Screen Manager: Shutting down")
        
        # Run cleanup for current screen
        if self.current_screen in self.screen_cleanup_hooks:
            self.screen_cleanup_hooks[self.current_screen]()
        
        self.game_running = False
    
    def handle_resolution_change(self, width: int, height: int) -> None:
        """
        Handle screen resolution changes.
        
        Args:
            width: New screen width
            height: New screen height
        """
        print(f"Screen Manager: Resolution changed to {width}x{height}")
        
        # Update internal state
        self.width = width
        self.height = height
        
        # Update screen reference
        self.screen = pygame.display.set_mode((width, height))
        
        # Notify all registered systems of resolution change
        # This would be handled by the game client calling update methods
        # on individual systems
    
    def get_version(self) -> str:
        """
        Get the game version.
        
        Returns:
            Version string
        """
        return self.version
    
    def register_screen_init_hook(self, screen_name: str, hook_func: callable) -> None:
        """
        Register a function to call when a screen is initialized.
        
        Args:
            screen_name: Name of the screen
            hook_func: Function to call on screen initialization
        """
        self.screen_init_hooks[screen_name] = hook_func
    
    def register_screen_cleanup_hook(self, screen_name: str, hook_func: callable) -> None:
        """
        Register a function to call when a screen is cleaned up.
        
        Args:
            screen_name: Name of the screen
            hook_func: Function to call on screen cleanup
        """
        self.screen_cleanup_hooks[screen_name] = hook_func
    
    def get_screen_info(self) -> Dict[str, Any]:
        """
        Get information about the current screen state.
        
        Returns:
            Dictionary containing screen information
        """
        return {
            "current_screen": self.current_screen,
            "game_running": self.game_running,
            "version": self.version,
            "resolution": (self.width, self.height),
            "registered_screens": list(self.screen_init_hooks.keys())
        }
    
    def create_error_screen(self, error_message: str) -> None:
        """
        Create a fallback error screen.
        
        Args:
            error_message: Error message to display
        """
        self.screen.fill(self.BLACK)
        
        # Draw error message
        error_font = pygame.font.SysFont('Arial', 48)
        error_text = error_font.render("Error", True, (255, 0, 0))
        error_rect = error_text.get_rect(center=(self.width // 2, self.height // 2 - 50))
        self.screen.blit(error_text, error_rect)
        
        # Draw error details
        detail_font = pygame.font.SysFont('Arial', 24)
        detail_text = detail_font.render(error_message, True, self.WHITE)
        detail_rect = detail_text.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(detail_text, detail_rect)
        
        # Draw instruction
        instruction_text = detail_font.render("Press ESC to return to main menu", True, self.LIGHT_GRAY)
        instruction_rect = instruction_text.get_rect(center=(self.width // 2, self.height // 2 + 50))
        self.screen.blit(instruction_text, instruction_rect)


# Interface validation
if interface_available:
    print("✅ ScreenManager interface validation passed")
else:
    print("⚠️  ScreenManager running without interface validation") 