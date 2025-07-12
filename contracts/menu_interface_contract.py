"""
Menu System Interface Contract
Defines the exact interface requirements for MenuSystem extraction.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any, Tuple

class MenuSystemInterface(ABC):
    """Abstract base class defining the MenuSystem interface contract."""
    
    @abstractmethod
    def __init__(self, screen, font, audio, asset_path: str):
        """Initialize the menu system.
        
        Args:
            screen: Pygame screen surface
            font: Font for rendering text
            audio: Audio system instance
            asset_path: Path to game assets
        """
        pass
    
    @abstractmethod
    def load_background(self, filename: str):
        """Load a background image from the asset path.
        
        Args:
            filename: Name of the background image file
            
        Returns:
            Pygame surface or None if loading fails
        """
        pass
    
    @abstractmethod
    def load_image(self, filename: str):
        """Load an image from the asset path.
        
        Args:
            filename: Name of the image file
            
        Returns:
            Pygame surface or None if loading fails
        """
        pass
    
    @abstractmethod
    def create_button(self, x: int, y: int, width: int, height: int, 
                     text: str, action=None, params=None) -> Dict:
        """Create a button with text and optional action.
        
        Args:
            x: X coordinate of the button
            y: Y coordinate of the button
            width: Width of the button
            height: Height of the button
            text: Button text
            action: Optional action callback
            params: Optional parameters for action
            
        Returns:
            Dictionary containing button information
        """
        pass
    
    @abstractmethod
    def draw_main_menu(self, on_start_action=None, on_settings_action=None, 
                      on_story_action=None, on_test_action=None, version=None) -> List:
        """Draw the main menu screen.
        
        Args:
            on_start_action: Callback for quickplay button
            on_settings_action: Callback for settings button
            on_story_action: Callback for story button
            on_test_action: Callback for test button
            version: Game version string
            
        Returns:
            List of menu buttons for interaction
        """
        pass
    
    @abstractmethod
    def process_main_menu_events(self, events: List) -> Optional[str]:
        """Process events for the main menu.
        
        Args:
            events: List of pygame events
            
        Returns:
            Action string if an action is triggered, None otherwise
        """
        pass
    
    @abstractmethod
    def draw_story_menu(self, on_back_action=None) -> List:
        """Draw the story menu screen.
        
        Args:
            on_back_action: Callback for back button
            
        Returns:
            List of interactive elements
        """
        pass
    
    @abstractmethod
    def process_story_menu_events(self, events: List) -> Optional[str]:
        """Process events for the story menu.
        
        Args:
            events: List of pygame events
            
        Returns:
            Action string if an action is triggered, None otherwise
        """
        pass

class MenuSystemRequirements:
    """Defines the exact requirements for MenuSystem implementation."""
    
    # Required menu buttons
    REQUIRED_BUTTONS = ["Quickplay", "Story Mode", "Test Mode", "Settings", "Quit"]
    
    # Required background images
    REQUIRED_BACKGROUNDS = ["colorful.png", "storybackground.png"]
    
    # Required button images
    REQUIRED_BUTTON_IMAGES = ["banner.png", "mainmenutitle.png"]
    
    # Required menu actions
    REQUIRED_ACTIONS = ["quickplay", "story", "test", "settings", "quit", "back"]
    
    # Color constants that must be available
    REQUIRED_COLORS = {
        "BLACK": (0, 0, 0),
        "WHITE": (255, 255, 255),
        "GRAY": (100, 100, 100),
        "LIGHT_GRAY": (200, 200, 200),
        "BLUE": (0, 100, 255),
        "LIGHT_BLUE": (100, 150, 255),
        "BORDER_COLOR": (100, 150, 255),
        "HOVER_BORDER_COLOR": (150, 200, 255)
    }
    
    @staticmethod
    def validate_initialization(menu_system: MenuSystemInterface) -> bool:
        """Validate that MenuSystem is properly initialized.
        
        Args:
            menu_system: MenuSystem instance to validate
            
        Returns:
            True if valid, False otherwise
        """
        required_attributes = ['screen', 'font', 'audio', 'asset_path', 'width', 'height']
        
        for attr in required_attributes:
            if not hasattr(menu_system, attr):
                return False
        
        return True
    
    @staticmethod
    def validate_button_creation(menu_system: MenuSystemInterface) -> bool:
        """Validate button creation functionality.
        
        Args:
            menu_system: MenuSystem instance to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Test creating a button
            button = menu_system.create_button(0, 0, 100, 50, "Test")
            
            # Check that button has required structure
            required_keys = ['rect', 'text', 'action', 'params', 'hover', 'id']
            for key in required_keys:
                if key not in button:
                    return False
            
            return True
        except Exception:
            return False
    
    @staticmethod
    def validate_menu_drawing(menu_system: MenuSystemInterface) -> bool:
        """Validate menu drawing functionality.
        
        Args:
            menu_system: MenuSystem instance to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Test main menu drawing
            buttons = menu_system.draw_main_menu()
            
            # Should return a list of buttons
            if not isinstance(buttons, list):
                return False
            
            # Should have 5 buttons
            if len(buttons) != 5:
                return False
            
            # Check button texts
            button_texts = [btn.get('text', '') for btn in buttons]
            for required_text in MenuSystemRequirements.REQUIRED_BUTTONS:
                if required_text not in button_texts:
                    return False
            
            return True
        except Exception:
            return False
    
    @staticmethod
    def validate_event_processing(menu_system: MenuSystemInterface) -> bool:
        """Validate event processing functionality.
        
        Args:
            menu_system: MenuSystem instance to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Test with empty events list
            result = menu_system.process_main_menu_events([])
            
            # Should return None for no events
            if result is not None:
                return False
            
            return True
        except Exception:
            return False

class MenuSystemTestContract:
    """Defines test contract for MenuSystem validation."""
    
    @staticmethod
    def validate_core_functionality(menu_system: MenuSystemInterface) -> bool:
        """Validate core MenuSystem functionality.
        
        Args:
            menu_system: MenuSystem instance to validate
            
        Returns:
            True if all validations pass, False otherwise
        """
        validations = [
            MenuSystemRequirements.validate_initialization,
            MenuSystemRequirements.validate_button_creation,
            MenuSystemRequirements.validate_menu_drawing,
            MenuSystemRequirements.validate_event_processing
        ]
        
        for validation in validations:
            if not validation(menu_system):
                return False
        
        return True

def validate_menu_interface(cls):
    """Decorator to validate MenuSystem interface compliance."""
    def wrapper(*args, **kwargs):
        instance = cls(*args, **kwargs)
        
        if MenuSystemTestContract.validate_core_functionality(instance):
            print("✅ MenuSystem interface validation passed")
        else:
            print("❌ MenuSystem interface validation failed")
        
        return instance
    return wrapper 