"""
Settings System Interface Contract
Defines the exact interface requirements for SettingsSystem extraction.
"""

from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Any, Dict

class SettingsSystemInterface(ABC):
    """Abstract base class defining the SettingsSystem interface contract."""
    
    @abstractmethod
    def __init__(self, screen, font, audio, asset_path: str):
        """Initialize the settings system.
        
        Args:
            screen: Pygame screen surface
            font: Font for rendering text
            audio: Audio system instance
            asset_path: Path to game assets
        """
        pass
    
    @abstractmethod
    def create_button(self, x: int, y: int, width: int, height: int, text: str, 
                     action=None, params=None) -> Dict[str, Any]:
        """Create a button with text and optional action.
        
        Args:
            x: Button x position
            y: Button y position
            width: Button width
            height: Button height
            text: Button text
            action: Optional action callback
            params: Optional parameters for action
            
        Returns:
            Dictionary containing button properties
        """
        pass
    
    @abstractmethod
    def draw_settings_menu(self, on_back_action, current_resolution: Tuple[int, int], 
                          resolutions: List[Tuple[int, int]], on_resolution_change) -> List[Dict[str, Any]]:
        """Draw the settings menu screen with resolution options.
        
        Args:
            on_back_action: Callback for back button
            current_resolution: Current screen resolution tuple
            resolutions: List of available resolution tuples
            on_resolution_change: Callback for resolution changes
            
        Returns:
            List of button dictionaries for interaction
        """
        pass
    
    @abstractmethod
    def set_screen(self, screen_name: str) -> None:
        """Set the current screen.
        
        Args:
            screen_name: Name of screen to switch to ("settings" or "ui_editor")
        """
        pass
    
    @abstractmethod
    def process_settings_events(self, events: List[Any]) -> Optional[str]:
        """Process events for the settings menu.
        
        Args:
            events: List of pygame events
            
        Returns:
            Action string if an action is triggered, None otherwise
        """
        pass


class SettingsSystemRequirements:
    """Detailed requirements for SettingsSystem implementation."""
    
    REQUIRED_COLORS = {
        'BLACK': (0, 0, 0),
        'WHITE': (255, 255, 255),
        'GRAY': (100, 100, 100),
        'LIGHT_GRAY': (200, 200, 200),
        'BLUE': (0, 100, 255),
        'LIGHT_BLUE': (100, 150, 255)
    }
    
    REQUIRED_GLOW_COLORS = [
        (210, 100, 240),  # Bright Purple
        (180, 60, 220),   # Medium Purple
        (150, 40, 200),   # Dark Purple
        (220, 120, 255)   # Pink-Purple
    ]
    
    REQUIRED_RESOLUTIONS = [
        (800, 600),
        (1024, 768),
        (1280, 720),
        (1366, 768),
        (1600, 900),
        (1920, 1080)
    ]
    
    REQUIRED_SCREENS = ["settings", "ui_editor"]
    
    REQUIRED_BACKGROUND_FILE = "settingsbcg.jfif"
    
    REQUIRED_ACTIONS = [
        "back",
        "resolution:WIDTH:HEIGHT",
        "ui_editor"
    ]
    
    @staticmethod
    def validate_button_structure(button: Dict[str, Any]) -> bool:
        """Validate button dictionary structure.
        
        Args:
            button: Button dictionary to validate
            
        Returns:
            True if valid, False otherwise
        """
        required_keys = ["rect", "text", "action", "params", "hover"]
        return all(key in button for key in required_keys)
    
    @staticmethod
    def validate_resolution(resolution: Tuple[int, int]) -> bool:
        """Validate resolution tuple.
        
        Args:
            resolution: Resolution tuple to validate
            
        Returns:
            True if valid, False otherwise
        """
        return (isinstance(resolution, tuple) and 
                len(resolution) == 2 and 
                all(isinstance(x, int) and x > 0 for x in resolution))
    
    @staticmethod
    def validate_screen_name(screen_name: str) -> bool:
        """Validate screen name.
        
        Args:
            screen_name: Screen name to validate
            
        Returns:
            True if valid, False otherwise
        """
        return screen_name in SettingsSystemRequirements.REQUIRED_SCREENS


class SettingsSystemTestContract:
    """Test contract for validating SettingsSystem implementation."""
    
    @staticmethod
    def validate_initialization(settings_system: SettingsSystemInterface) -> bool:
        """Validate that the settings system initializes correctly.
        
        Args:
            settings_system: SettingsSystem instance to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Check required attributes exist
        required_attrs = ['screen', 'font', 'audio', 'asset_path', 'width', 'height']
        for attr in required_attrs:
            if not hasattr(settings_system, attr):
                return False
        
        # Check colors are set correctly
        for color_name, expected_value in SettingsSystemRequirements.REQUIRED_COLORS.items():
            if not hasattr(settings_system, color_name):
                return False
            if getattr(settings_system, color_name) != expected_value:
                return False
        
        return True
    
    @staticmethod
    def validate_button_creation(settings_system: SettingsSystemInterface) -> bool:
        """Validate button creation functionality.
        
        Args:
            settings_system: SettingsSystem instance to validate
            
        Returns:
            True if valid, False otherwise
        """
        button = settings_system.create_button(10, 10, 100, 50, "Test", None, None)
        return SettingsSystemRequirements.validate_button_structure(button)
    
    @staticmethod
    def validate_screen_switching(settings_system: SettingsSystemInterface) -> bool:
        """Validate screen switching functionality.
        
        Args:
            settings_system: SettingsSystem instance to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Test valid screen names
            for screen_name in SettingsSystemRequirements.REQUIRED_SCREENS:
                settings_system.set_screen(screen_name)
                # Check if the implementation has current_screen attribute
                if hasattr(settings_system, 'current_screen'):
                    if getattr(settings_system, 'current_screen') != screen_name:
                        return False
            return True
        except Exception:
            return False
    
    @staticmethod
    def validate_resolution_support(settings_system: SettingsSystemInterface) -> bool:
        """Validate resolution support functionality.
        
        Args:
            settings_system: SettingsSystem instance to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Test with required resolutions
        test_resolutions = SettingsSystemRequirements.REQUIRED_RESOLUTIONS
        current_resolution = test_resolutions[0]
        
        try:
            # This should not raise an exception
            buttons = settings_system.draw_settings_menu(
                lambda: None,  # dummy back action
                current_resolution,
                test_resolutions,
                lambda res: None  # dummy resolution change action
            )
            
            # Should return a list of buttons
            if not isinstance(buttons, list):
                return False
            
            # All buttons should have valid structure
            for button in buttons:
                if not SettingsSystemRequirements.validate_button_structure(button):
                    return False
            
            return True
        except Exception:
            return False


# Runtime validation decorator
def validate_settings_interface(cls):
    """Decorator to validate SettingsSystem interface compliance at runtime."""
    original_init = cls.__init__
    
    def validated_init(self, *args, **kwargs):
        # Call original constructor
        original_init(self, *args, **kwargs)
        
        # Validate interface compliance
        if not SettingsSystemTestContract.validate_initialization(self):
            raise RuntimeError("SettingsSystem initialization validation failed")
        
        print("✅ SettingsSystem interface validation passed")
    
    cls.__init__ = validated_init
    return cls 