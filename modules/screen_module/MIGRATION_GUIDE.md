# Screen Management Integration Migration Guide

## Overview

This guide provides step-by-step instructions for migrating from the old scattered screen state management to the new unified GameStateManager-based system.

## Before vs After

### Before: Scattered Screen State
```python
# game_client.py
self.current_screen = "main_menu"

# screen_manager.py
self.current_screen = "main_menu"

# Multiple places checking screen state
if self.current_screen == "game":
    # game logic
elif self.current_screen == "main_menu":
    # menu logic
```

### After: Unified State Management
```python
# Using the new screen integration
from modules.screen_module.screen_state_integration import ScreenStateIntegration
from modules.game_state_module.state_schema import ScreenType

# Set screen
screen_integration.set_screen(ScreenType.MAIN_MENU, "menu_system", "User clicked main menu")

# Check screen
if screen_integration.is_screen(ScreenType.GAME):
    # game logic
elif screen_integration.is_screen(ScreenType.MAIN_MENU):
    # menu logic
```

## Migration Steps

### Step 1: Initialize Screen Integration

Add screen integration to your game client initialization:

```python
# In game_client.py __init__ method
from modules.screen_module.screen_state_integration import ScreenStateIntegration
from modules.game_state_module.game_state_manager import GameStateManager

def __init__(self):
    # ... existing initialization ...
    
    # Initialize state manager
    self.state_manager = GameStateManager()
    
    # Initialize screen integration
    self.screen_integration = ScreenStateIntegration(self.state_manager)
    
    # Set global instances for convenience
    from modules.game_state_module.game_state_manager import set_global_game_state_manager
    from modules.screen_module.screen_state_integration import set_global_screen_integration
    
    set_global_game_state_manager(self.state_manager)
    set_global_screen_integration(self.screen_integration)
```

### Step 2: Replace Screen Setting Logic

Replace the old `set_screen` method in `game_client.py`:

```python
# OLD CODE
def set_screen(self, screen_name):
    if hasattr(self, 'screen_manager') and self.screen_manager:
        self.screen_manager.set_screen(screen_name)
        self.current_screen = self.screen_manager.get_current_screen()
    else:
        self.current_screen = screen_name

# NEW CODE
def set_screen(self, screen_name):
    """Set the current screen using the new state management system."""
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
    
    # Use the new screen integration
    success = self.screen_integration.set_screen(
        screen_type, 
        "game_client", 
        f"Screen transition to {screen_name}"
    )
    
    if success:
        # Handle screen-specific initialization
        self._handle_screen_specific_logic(screen_name)
    else:
        print(f"Failed to set screen to {screen_name}")

def _handle_screen_specific_logic(self, screen_name):
    """Handle screen-specific initialization logic."""
    if screen_name == "settings":
        if hasattr(self, 'settings_ui') and self.settings_ui:
            self.settings_ui.open()
    elif screen_name == "test":
        if hasattr(self, 'test_mode') and self.test_mode:
            self.test_mode.initialize_test()
            self.test_mode.setup_board_positions()
    elif screen_name == "game":
        try:
            if hasattr(self, 'puzzle_renderer') and self.puzzle_renderer:
                self.puzzle_renderer.preview_side = 'left'
        except Exception:
            pass
        self.puzzle_engine.start_game()
```

### Step 3: Replace Screen Checking Logic

Replace all instances of `self.current_screen` checks:

```python
# OLD CODE
if self.current_screen == "main_menu":
    # menu logic

# NEW CODE
if self.screen_integration.is_screen(ScreenType.MAIN_MENU):
    # menu logic

# OR for multiple checks
current_screen = self.screen_integration.get_current_screen()
if current_screen == ScreenType.MAIN_MENU:
    # menu logic
elif current_screen == ScreenType.GAME:
    # game logic
```

### Step 4: Update Screen Manager Integration

Update the screen manager to work with the new state system:

```python
# In screen_manager.py
class ScreenManager:
    def __init__(self, screen: pygame.Surface, font: pygame.font.Font, width: int, height: int):
        # ... existing initialization ...
        
        # Get reference to screen integration
        from modules.screen_module.screen_state_integration import get_screen_integration
        self.screen_integration = get_screen_integration()
    
    def set_screen(self, screen_name: str) -> None:
        """Set the current screen with proper initialization."""
        print(f"Screen Manager: Setting screen to {screen_name}")
        
        # Use the new screen integration if available
        if self.screen_integration:
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
        else:
            # Fallback to old behavior
            print("Screen Manager: No screen integration available, using fallback")
            self.current_screen = screen_name
    
    def get_current_screen(self) -> str:
        """Get the name of the current screen."""
        if self.screen_integration:
            return self.screen_integration.get_current_screen().value
        else:
            return self.current_screen
```

### Step 5: Register Screen Callbacks

Register callbacks for screen-specific initialization and cleanup:

```python
# In game_client.py initialization
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
    
    # Cleanup callbacks
    self.screen_integration.register_screen_cleanup_callback(
        ScreenType.GAME,
        self._on_game_exit
    )

def _on_main_menu_enter(self):
    """Called when entering main menu."""
    print("Entering main menu")
    # Initialize menu system if needed

def _on_game_enter(self):
    """Called when entering game screen."""
    print("Entering game screen")
    # Initialize game systems

def _on_test_enter(self):
    """Called when entering test screen."""
    print("Entering test screen")
    # Initialize test mode

def _on_game_exit(self):
    """Called when exiting game screen."""
    print("Exiting game screen")
    # Clean up game resources
```

### Step 6: Update Story State Management

Replace story state management with the new system:

```python
# OLD CODE
self.story_scroll_position = 0
self.current_story = {"title": "No Story Selected", "content": []}

# NEW CODE
# Set story state
self.screen_integration.set_story_state({
    "title": "The Forge Keeper's Legacy",
    "content": ["Chapter 1: The Beginning", "Chapter 2: The Journey"]
}, "story_system", "Loading story content")

# Set scroll position
self.screen_integration.set_story_scroll_position(100, "story_system", "User scrolled")

# Get story state
story_info = self.screen_integration.get_screen_info()
scroll_pos = story_info["story_scroll_position"]
current_story = story_info["current_story"]
```

### Step 7: Update Menu System

Update the menu system to use the new screen integration:

```python
# In menu_system.py
class MenuSystem:
    def __init__(self, screen, font, audio, asset_path: str):
        # ... existing initialization ...
        
        # Get screen integration
        from modules.screen_module.screen_state_integration import get_screen_integration
        self.screen_integration = get_screen_integration()
    
    def handle_button_click(self, button_name: str):
        """Handle button clicks with new screen management."""
        if button_name == "Quickplay":
            if self.screen_integration:
                self.screen_integration.set_screen(
                    ScreenType.GAME, 
                    "menu_system", 
                    "User clicked Quickplay"
                )
            else:
                # Fallback
                self.game_client.set_screen("game")
        
        elif button_name == "Story Mode":
            if self.screen_integration:
                self.screen_integration.set_screen(
                    ScreenType.STORY, 
                    "menu_system", 
                    "User clicked Story Mode"
                )
            else:
                # Fallback
                self.game_client.set_screen("story")
```

## Testing the Migration

### Run Integration Tests

```bash
# Run the screen integration tests
python -m pytest modules/screen_module/tests/test_screen_state_integration.py -v
```

### Manual Testing Checklist

- [ ] Main menu loads correctly
- [ ] Screen transitions work smoothly
- [ ] Story mode navigation works
- [ ] Test mode initialization works
- [ ] Game mode starts correctly
- [ ] Settings overlay works
- [ ] Screen state is properly tracked
- [ ] No console errors during transitions

### Debugging Tips

1. **Check State Manager Logs**: The state manager logs all changes. Look for screen-related entries.

2. **Use State Summary**: Call `self.state_manager.get_state_summary()` to see current state.

3. **Check Callbacks**: Ensure screen transition callbacks are registered and working.

4. **Validate State**: Use `self.state_manager.validate_state()` to check for state inconsistencies.

## Benefits of Migration

1. **Centralized State**: All screen state is now managed in one place
2. **History Tracking**: Screen transitions are automatically recorded
3. **Validation**: Screen changes are validated before being applied
4. **Callbacks**: Automatic cleanup and initialization on screen changes
5. **Debugging**: Better visibility into screen state changes
6. **Consistency**: All systems use the same screen state

## Rollback Plan

If issues arise during migration:

1. Keep the old `self.current_screen` variable as a fallback
2. Add feature flags to switch between old and new systems
3. Use the screen integration's fallback mode
4. Gradually migrate one screen at a time

## Next Steps

After completing the screen management migration:

1. Update other modules to use the new screen integration
2. Add more comprehensive screen state validation
3. Implement screen transition animations
4. Add screen state persistence
5. Create screen state analytics 