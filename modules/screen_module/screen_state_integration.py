"""
Screen State Integration Module
Bridges existing screen management with the new GameStateManager.
Handles screen transitions and UI state management.
"""

from typing import Optional, Callable, Dict, Any
from ..game_state_module.game_state_manager import GameStateManager
from ..game_state_module.state_schema import ScreenType
from ..logging_module.logger import get_logger


class ScreenStateIntegration:
    """
    Integrates screen management with the unified state system.
    Replaces scattered screen state variables with centralized state management.
    """
    
    def __init__(self, state_manager: GameStateManager):
        """Initialize the screen state integration."""
        self.logger = get_logger(__name__)
        self.state_manager = state_manager
        
        # Register callbacks for screen state changes
        self._register_screen_callbacks()
        
        # Track screen transition callbacks
        self._screen_transition_callbacks: Dict[ScreenType, Callable] = {}
        self._screen_cleanup_callbacks: Dict[ScreenType, Callable] = {}
        
        self.logger.info("ScreenStateIntegration initialized")
    
    def set_screen(self, screen_type: ScreenType, source: str = "screen_integration", 
                   description: str = "") -> bool:
        """
        Set the current screen using the state manager.
        
        Args:
            screen_type: The screen type to switch to
            source: Source of the screen change
            description: Description of the change
            
        Returns:
            True if the change was successful
        """
        try:
            # Get current screen before change
            current_screen = self.state_manager.get("screen.current_screen")
            
            # Run cleanup for current screen
            if current_screen and current_screen in self._screen_cleanup_callbacks:
                try:
                    self._screen_cleanup_callbacks[current_screen]()
                    self.logger.debug(f"Ran cleanup for screen: {current_screen.value}")
                except Exception as e:
                    self.logger.error(f"Error in screen cleanup for {current_screen.value}: {e}")
            
            # Update previous screen
            self.state_manager.set("screen.previous_screen", current_screen, source, 
                                  f"Previous screen set to {current_screen.value if current_screen else 'None'}")
            
            # Update current screen
            success = self.state_manager.set("screen.current_screen", screen_type, source, description)
            
            if success:
                # Update transition time
                import time
                self.state_manager.set("screen.screen_transition_time", time.time(), source, 
                                      f"Transition time updated for {screen_type.value}")
                
                # Run transition callback for new screen
                if screen_type in self._screen_transition_callbacks:
                    try:
                        self._screen_transition_callbacks[screen_type]()
                        self.logger.debug(f"Ran transition callback for screen: {screen_type.value}")
                    except Exception as e:
                        self.logger.error(f"Error in screen transition callback for {screen_type.value}: {e}")
                
                self.logger.info(f"Screen transition: {current_screen.value if current_screen else 'None'} -> {screen_type.value}")
                return True
            else:
                self.logger.error(f"Failed to set screen to {screen_type.value}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error in set_screen: {e}")
            return False
    
    def get_current_screen(self) -> ScreenType:
        """Get the current screen from the state manager."""
        return self.state_manager.get("screen.current_screen", ScreenType.LOADING)
    
    def get_previous_screen(self) -> Optional[ScreenType]:
        """Get the previous screen from the state manager."""
        return self.state_manager.get("screen.previous_screen")
    
    def is_screen(self, screen_type: ScreenType) -> bool:
        """Check if the current screen matches the given type."""
        return self.get_current_screen() == screen_type
    
    def register_screen_transition_callback(self, screen_type: ScreenType, callback: Callable) -> None:
        """Register a callback to run when transitioning to a specific screen."""
        self._screen_transition_callbacks[screen_type] = callback
        self.logger.debug(f"Registered transition callback for screen: {screen_type.value}")
    
    def register_screen_cleanup_callback(self, screen_type: ScreenType, callback: Callable) -> None:
        """Register a callback to run when cleaning up a specific screen."""
        self._screen_cleanup_callbacks[screen_type] = callback
        self.logger.debug(f"Registered cleanup callback for screen: {screen_type.value}")
    
    def get_screen_info(self) -> Dict[str, Any]:
        """Get comprehensive screen information from the state manager."""
        return {
            "current_screen": self.get_current_screen().value,
            "previous_screen": self.get_previous_screen().value if self.get_previous_screen() else None,
            "transition_time": self.state_manager.get("screen.screen_transition_time"),
            "cleanup_required": self.state_manager.get("screen.screen_cleanup_required", False),
            "story_scroll_position": self.state_manager.get("screen.story_scroll_position", 0),
            "current_story": self.state_manager.get("screen.current_story", {})
        }
    
    def set_story_state(self, story_data: Dict[str, Any], source: str = "screen_integration") -> bool:
        """Set the current story state."""
        try:
            self.state_manager.set("screen.current_story", story_data, source, "Story state updated")
            return True
        except Exception as e:
            self.logger.error(f"Error setting story state: {e}")
            return False
    
    def set_story_scroll_position(self, position: int, source: str = "screen_integration") -> bool:
        """Set the story scroll position."""
        try:
            self.state_manager.set("screen.story_scroll_position", position, source, 
                                  f"Story scroll position set to {position}")
            return True
        except Exception as e:
            self.logger.error(f"Error setting story scroll position: {e}")
            return False
    
    def mark_cleanup_required(self, required: bool = True, source: str = "screen_integration") -> bool:
        """Mark that screen cleanup is required."""
        try:
            self.state_manager.set("screen.screen_cleanup_required", required, source, 
                                  f"Screen cleanup required set to {required}")
            return True
        except Exception as e:
            self.logger.error(f"Error marking cleanup required: {e}")
            return False
    
    def _register_screen_callbacks(self) -> None:
        """Register callbacks for screen state changes."""
        # Register callback for screen changes
        self.state_manager.add_change_callback(
            "screen.current_screen",
            self._on_screen_changed,
            "Screen state integration callback"
        )
        
        # Register callback for story state changes
        self.state_manager.add_change_callback(
            "screen.current_story",
            self._on_story_changed,
            "Story state integration callback"
        )
    
    def _on_screen_changed(self, field_path: str, old_value: Any, new_value: Any) -> None:
        """Called when the screen changes."""
        old_screen = old_value.value if old_value else "None"
        new_screen = new_value.value if new_value else "None"
        self.logger.debug(f"Screen changed: {old_screen} -> {new_screen}")
    
    def _on_story_changed(self, field_path: str, old_value: Any, new_value: Any) -> None:
        """Called when the story state changes."""
        self.logger.debug(f"Story state changed: {len(new_value) if new_value else 0} story items")


# Convenience functions for common screen operations
def create_screen_integration(state_manager: GameStateManager) -> ScreenStateIntegration:
    """Create a new screen state integration instance."""
    return ScreenStateIntegration(state_manager)


def get_screen_integration() -> Optional[ScreenStateIntegration]:
    """Get the global screen integration instance."""
    return getattr(ScreenStateIntegration, '_global_instance', None)


def set_global_screen_integration(integration: ScreenStateIntegration) -> None:
    """Set the global screen integration instance."""
    ScreenStateIntegration._global_instance = integration 