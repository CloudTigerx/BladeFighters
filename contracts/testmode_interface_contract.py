"""
TestMode Interface Contract
Defines the exact interface requirements for TestMode extraction.
Focuses on core puzzle battle functionality: 2 grids, piece previews, backgrounds.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any, Tuple

class TestModeInterface(ABC):
    """Abstract base class defining the TestMode interface contract."""
    
    @abstractmethod
    def __init__(self, screen, font, audio, asset_path: str):
        """Initialize the test mode with core puzzle battle setup.
        
        Args:
            screen: Pygame screen surface
            font: Font for rendering text
            audio: Audio system instance
            asset_path: Path to game assets
        """
        pass
    
    @abstractmethod
    def setup_board_positions(self):
        """Set up the positions for the player and enemy puzzle boards.
        
        This should calculate proper positioning for both grids on screen.
        """
        pass
    
    @abstractmethod
    def initialize_test(self):
        """Initialize or reset the test mode game state.
        
        This should reset both puzzle engines and prepare for a new battle.
        """
        pass
    
    @abstractmethod
    def update(self) -> Optional[str]:
        """Update the test mode state.
        
        Returns:
            Optional[str]: "game_over" if game should end, None to continue
        """
        pass
    
    @abstractmethod
    def process_events(self, events: List) -> Optional[str]:
        """Process input events for the test mode.
        
        Args:
            events: List of pygame events
            
        Returns:
            Optional[str]: "back_to_menu" if should return to menu, None otherwise
        """
        pass
    
    @abstractmethod
    def draw(self):
        """Draw the complete test mode interface.
        
        This should draw:
        - Background
        - Both puzzle grids (player and enemy)  
        - Falling pieces on both grids
        - Next piece previews
        - Basic UI elements
        """
        pass

class TestModeRequirements:
    """Defines the exact requirements for TestMode implementation."""
    
    # Required core components
    REQUIRED_ENGINES = 2  # Player and enemy puzzle engines
    REQUIRED_RENDERERS = 2  # Player and enemy renderers
    
    # Grid specifications
    GRID_WIDTH = 6
    GRID_HEIGHT = 13
    CELL_WIDTH = 68
    CELL_HEIGHT = 54
    
    # Required background images
    REQUIRED_BACKGROUNDS = ["puzzlebackground.jpg"]
    
    # Core colors
    REQUIRED_COLORS = {
        "BLACK": (0, 0, 0),
        "WHITE": (255, 255, 255),
        "GRAY": (100, 100, 100),
        "LIGHT_BLUE": (100, 150, 255),
        "BACKGROUND_COLOR": (10, 10, 30)
    }
    
    # Required game states
    REQUIRED_GAME_STATES = ["active", "game_over"]
    
    @staticmethod
    def validate_initialization(test_mode: TestModeInterface) -> bool:
        """Validate that TestMode is properly initialized.
        
        Args:
            test_mode: TestMode instance to validate
            
        Returns:
            True if valid, False otherwise
        """
        required_attributes = [
            'screen', 'font', 'audio', 'asset_path', 'width', 'height',
            'player_engine', 'enemy_engine', 'player_renderer', 'enemy_renderer'
        ]
        
        for attr in required_attributes:
            if not hasattr(test_mode, attr):
                return False
        
        return True
    
    @staticmethod
    def validate_board_positioning(test_mode: TestModeInterface) -> bool:
        """Validate board positioning functionality.
        
        Args:
            test_mode: TestMode instance to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Check that board positions are set
            required_positions = ['player_grid_position', 'enemy_grid_position']
            for pos in required_positions:
                if not hasattr(test_mode, pos):
                    return False
                position = getattr(test_mode, pos)
                if not isinstance(position, dict) or 'x' not in position or 'y' not in position:
                    return False
            
            return True
        except Exception:
            return False
    
    @staticmethod
    def validate_game_engines(test_mode: TestModeInterface) -> bool:
        """Validate that game engines are properly configured.
        
        Args:
            test_mode: TestMode instance to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Check that engines exist first
            if not (hasattr(test_mode, 'player_engine') and hasattr(test_mode, 'enemy_engine')):
                return False
            
            engines = [getattr(test_mode, 'player_engine'), getattr(test_mode, 'enemy_engine')]
            required_methods = ['update', 'start_game', 'process_events']
            
            for engine in engines:
                for method in required_methods:
                    if not hasattr(engine, method):
                        return False
            
            return True
        except Exception:
            return False
    
    @staticmethod
    def validate_rendering(test_mode: TestModeInterface) -> bool:
        """Validate rendering functionality.
        
        Args:
            test_mode: TestMode instance to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Check that renderers exist first
            if not (hasattr(test_mode, 'player_renderer') and hasattr(test_mode, 'enemy_renderer')):
                return False
            
            renderers = [getattr(test_mode, 'player_renderer'), getattr(test_mode, 'enemy_renderer')]
            required_methods = ['draw_grid_blocks', 'draw_falling_piece', 'draw_next_piece_preview']
            
            for renderer in renderers:
                for method in required_methods:
                    if not hasattr(renderer, method):
                        return False
            
            return True
        except Exception:
            return False

class TestModeTestContract:
    """Defines test contract for TestMode validation."""
    
    @staticmethod
    def validate_core_functionality(test_mode: TestModeInterface) -> bool:
        """Validate core TestMode functionality.
        
        Args:
            test_mode: TestMode instance to validate
            
        Returns:
            True if all validations pass, False otherwise
        """
        validations = [
            TestModeRequirements.validate_initialization,
            TestModeRequirements.validate_board_positioning,
            TestModeRequirements.validate_game_engines,
            TestModeRequirements.validate_rendering
        ]
        
        for validation in validations:
            if not validation(test_mode):
                return False
        
        return True

def validate_testmode_interface(cls):
    """Decorator to validate TestMode interface compliance."""
    def wrapper(*args, **kwargs):
        instance = cls(*args, **kwargs)
        
        if TestModeTestContract.validate_core_functionality(instance):
            print("✅ TestMode interface validation passed")
        else:
            print("❌ TestMode interface validation failed")
        
        return instance
    return wrapper 