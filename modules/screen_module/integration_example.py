"""
Screen State Integration Example
Demonstrates how to integrate the new screen state management with existing code.
"""

import pygame
from modules.game_state_module.game_state_manager import GameStateManager
from modules.game_state_module.state_schema import ScreenType
from modules.screen_module.screen_state_integration import ScreenStateIntegration
from modules.logging_module.logger import get_logger


class GameClientIntegrationExample:
    """
    Example of how to integrate screen state management with an existing game client.
    This shows the migration from scattered screen state to unified state management.
    """
    
    def __init__(self):
        """Initialize the game client with screen state integration."""
        self.logger = get_logger(__name__)
        
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        self.font = pygame.font.SysFont('Arial', 24)
        
        self.state_manager = GameStateManager()
        self.screen_integration = ScreenStateIntegration(self.state_manager)
        
        # Set global instances for convenience
        from modules.game_state_module.game_state_manager import set_global_game_state_manager
        from modules.screen_module.screen_state_integration import set_global_screen_integration
        
        set_global_game_state_manager(self.state_manager)
        set_global_screen_integration(self.screen_integration)
        
        # Register screen callbacks
        self._register_screen_callbacks()
        
        self.screen_manager = self._create_screen_manager()
        
        self.logger.info("GameClientIntegrationExample initialized")
    
    def _register_screen_callbacks(self):
        """Register callbacks for screen transitions."""
        
        # Main menu callbacks
        self.screen_integration.register_screen_transition_callback(
            ScreenType.MAIN_MENU,
            self._on_main_menu_enter
        )
        
        # Game screen callbacks
        self.screen_integration.register_screen_transition_callback(
            ScreenType.GAME,
            self._on_game_enter
        )
        
        # Test screen callbacks
        self.screen_integration.register_screen_transition_callback(
            ScreenType.TEST,
            self._on_test_enter
        )
        
        # Story screen callbacks
        self.screen_integration.register_screen_transition_callback(
            ScreenType.STORY,
            self._on_story_enter
        )
        
        # Cleanup callbacks
        self.screen_integration.register_screen_cleanup_callback(
            ScreenType.GAME,
            self._on_game_exit
        )
        
        self.screen_integration.register_screen_cleanup_callback(
            ScreenType.TEST,
            self._on_test_exit
        )
    
    def _create_screen_manager(self):
        """Create a screen manager that works with the new integration."""
        class IntegratedScreenManager:
            def __init__(self, screen_integration):
                self.screen_integration = screen_integration
            
            def set_screen(self, screen_name: str) -> None:
                """Set the current screen using the new integration."""
                # Map string screen names to ScreenType enum
                screen_mapping = {
                    "main_menu": ScreenType.MAIN_MENU,
                    "game": ScreenType.GAME,
                    "test": ScreenType.TEST,
                    "story": ScreenType.STORY,
                    "story_content": ScreenType.STORY_CONTENT,
                    "settings": ScreenType.SETTINGS,
                    "smithing": ScreenType.SMITHING,
                    "inventory": ScreenType.INVENTORY,
                    "ui_editor": ScreenType.UI_EDITOR,
                    "loading": ScreenType.LOADING
                }
                
                screen_type = screen_mapping.get(screen_name, ScreenType.LOADING)
                
                success = self.screen_integration.set_screen(
                    screen_type, 
                    "screen_manager", 
                    f"Screen manager transition to {screen_name}"
                )
                
                if not success:
                    print(f"Screen Manager: Failed to set screen to {screen_name}")
            
            def get_current_screen(self) -> str:
                """Get the name of the current screen."""
                return self.screen_integration.get_current_screen().value
        
        return IntegratedScreenManager(self.screen_integration)
    
    def set_screen(self, screen_name: str):
        """Set the current screen using the new state management system."""
        # Use screen manager if available
        if hasattr(self, 'screen_manager') and self.screen_manager:
            self.screen_manager.set_screen(screen_name)
        else:
            # Fallback to direct integration
            screen_mapping = {
                "main_menu": ScreenType.MAIN_MENU,
                "game": ScreenType.GAME,
                "test": ScreenType.TEST,
                "story": ScreenType.STORY,
                "story_content": ScreenType.STORY_CONTENT,
                "settings": ScreenType.SETTINGS,
                "smithing": ScreenType.SMITHING,
                "inventory": ScreenType.INVENTORY,
                "ui_editor": ScreenType.UI_EDITOR,
                "loading": ScreenType.LOADING
            }
            
            screen_type = screen_mapping.get(screen_name, ScreenType.LOADING)
            
            success = self.screen_integration.set_screen(
                screen_type, 
                "game_client", 
                f"Screen transition to {screen_name}"
            )
            
            if success:
                self._handle_screen_specific_logic(screen_name)
            else:
                self.logger.error(f"Failed to set screen to {screen_name}")
    
    def _handle_screen_specific_logic(self, screen_name: str):
        """Handle screen-specific initialization logic."""
        if screen_name == "settings":
            # Open settings overlay on top of main menu
            print("Opening settings overlay")
        elif screen_name == "test":
            print("Initializing test mode")
            # self.test_mode.initialize_test()
            # self.test_mode.setup_board_positions()
        elif screen_name == "game":
            print("Starting game")
            # self.puzzle_engine.start_game()
    
    def _on_main_menu_enter(self):
        """Called when entering main menu."""
        self.logger.info("Entering main menu")
        # Initialize menu system if needed
        print("Main menu entered - initializing menu system")
    
    def _on_game_enter(self):
        """Called when entering game screen."""
        self.logger.info("Entering game screen")
        # Initialize game systems
        print("Game screen entered - initializing game systems")
    
    def _on_test_enter(self):
        """Called when entering test screen."""
        self.logger.info("Entering test screen")
        # Initialize test mode
        print("Test screen entered - initializing test mode")
    
    def _on_story_enter(self):
        """Called when entering story screen."""
        self.logger.info("Entering story screen")
        # Load story content
        story_data = {
            "title": "The Forge Keeper's Legacy",
            "content": [
                "Chapter 1: The Beginning",
                "In a world where magic and technology coexist...",
                "Chapter 2: The Journey",
                "Our hero embarks on an epic quest..."
            ]
        }
        self.screen_integration.set_story_state(story_data, "story_system")
        print("Story screen entered - loading story content")
    
    def _on_game_exit(self):
        """Called when exiting game screen."""
        self.logger.info("Exiting game screen")
        # Clean up game resources
        print("Game screen exited - cleaning up game resources")
    
    def _on_test_exit(self):
        """Called when exiting test screen."""
        self.logger.info("Exiting test screen")
        # Clean up test resources
        print("Test screen exited - cleaning up test resources")
    
    def run_demo(self):
        """Run a demonstration of the screen integration."""
        print("=== Screen State Integration Demo ===")
        
        # Show initial state
        print(f"Initial screen: {self.screen_integration.get_current_screen().value}")
        
        # Demonstrate screen transitions
        screens_to_test = ["main_menu", "game", "test", "story", "main_menu"]
        
        for screen_name in screens_to_test:
            print(f"\n--- Transitioning to {screen_name} ---")
            self.set_screen(screen_name)
            
            # Show current state
            current_screen = self.screen_integration.get_current_screen()
            previous_screen = self.screen_integration.get_previous_screen()
            
            print(f"Current screen: {current_screen.value}")
            if previous_screen:
                print(f"Previous screen: {previous_screen.value}")
            
            # Show screen info
            screen_info = self.screen_integration.get_screen_info()
            print(f"Screen info: {screen_info}")
            
            # Show state summary
            state_summary = self.state_manager.get_state_summary()
            print(f"State summary: {state_summary}")
        
        # Demonstrate story state management
        print("\n--- Story State Management ---")
        if self.screen_integration.is_screen(ScreenType.STORY):
            # Set scroll position
            self.screen_integration.set_story_scroll_position(100, "demo", "User scrolled")
            
            # Get updated story info
            story_info = self.screen_integration.get_screen_info()
            print(f"Story scroll position: {story_info['story_scroll_position']}")
            print(f"Current story: {story_info['current_story']}")
        
        # Demonstrate state history
        print("\n--- State History ---")
        history_summary = self.state_manager.get_history_summary()
        print(f"Total changes: {history_summary['total_changes']}")
        print(f"Most changed field: {history_summary['most_changed_field']}")
        
        # Show recent changes
        changes = self.state_manager.history.get_changes_for_field("screen.current_screen")
        print(f"Screen changes: {len(changes)}")
        for change in changes[-3:]:  # Last 3 changes
            print(f"  {change.timestamp}: {change.old_value.value if change.old_value else 'None'} -> {change.new_value.value}")
        
        print("\n=== Demo Complete ===")
    
    def cleanup(self):
        """Clean up resources."""
        pygame.quit()


def main():
    """Main function to run the integration example."""
    try:
        # Create and run the integration example
        game_client = GameClientIntegrationExample()
        game_client.run_demo()
        
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    except Exception as e:
        print(f"Error during demo: {e}")
    finally:
        if 'game_client' in locals():
            game_client.cleanup()


if __name__ == "__main__":
    main() 