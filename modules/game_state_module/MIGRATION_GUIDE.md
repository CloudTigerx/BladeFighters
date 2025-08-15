# Game State Management Unification - Migration Guide

## Overview

The Game State Management Unification introduces a centralized, type-safe, and validated state management system that replaces the scattered state variables across the codebase.

## Key Benefits

- **Centralized State**: All game state in one place with clear structure
- **Type Safety**: Dataclass-based schema prevents type errors
- **Validation**: Automatic validation of state changes
- **History**: Complete state change history with rollback capability
- **Callbacks**: Reactive state changes with callback system
- **Debugging**: Comprehensive state export and debugging tools

## Architecture

### Core Components

1. **GameStateManager**: Main interface for state operations
2. **GameState**: Complete state container with nested subsystems
3. **StateValidator**: Validates state changes and consistency
4. **StateHistory**: Tracks changes and enables rollbacks

### State Schema

```python
@dataclass
class GameState:
    # Core state
    game_running: bool = True
    version: str = "1.0.0"
    
    # Subsystem states
    screen: ScreenState
    puzzle: PuzzleState
    audio: AudioState
    input: InputState
    ui: UIState
```

## Migration Steps

### Step 1: Initialize State Manager

Replace scattered state initialization with centralized state manager:

**Before:**
```python
class GameClient:
    def __init__(self):
        self.game_running = True
        self.current_screen = "loading"
        self.menu_system = None
        # ... many more scattered variables
```

**After:**
```python
from modules.game_state_module import GameStateManager

class GameClient:
    def __init__(self):
        self.state_manager = GameStateManager()
        # Access state through manager
        self.state_manager.set("game_running", True, source="GameClient")
        self.state_manager.set("screen.current_screen", ScreenType.LOADING, source="GameClient")
```

### Step 2: Replace Direct State Access

Replace direct attribute access with state manager calls:

**Before:**
```python
def some_method(self):
    if self.game_active:
        self.score += 100
    self.current_screen = "game"
```

**After:**
```python
def some_method(self):
    if self.state_manager.get("puzzle.game_active"):
        current_score = self.state_manager.get("puzzle.score", 0)
        self.state_manager.set("puzzle.score", current_score + 100, source="some_method")
    self.state_manager.set("screen.current_screen", ScreenType.GAME, source="some_method")
```

### Step 3: Add State Change Callbacks

Use callbacks for reactive state changes:

**Before:**
```python
def set_volume(self, volume):
    self.master_volume = volume
    # Manually update audio system
    if self.audio:
        self.audio.set_volume(volume)
```

**After:**
```python
def __init__(self):
    # ... other init code ...
    
    # Add callback for volume changes
    self.state_manager.add_change_callback(
        "audio.master_volume", 
        self._on_volume_changed,
        "Update audio system when volume changes"
    )

def set_volume(self, volume):
    self.state_manager.set("audio.master_volume", volume, source="set_volume")

def _on_volume_changed(self, field_path, old_value, new_value):
    if self.audio:
        self.audio.set_volume(new_value)
```

### Step 4: Replace Screen Management

**Before:**
```python
def set_screen(self, screen_name):
    self.current_screen = screen_name
    # Manual cleanup and initialization
```

**After:**
```python
def set_screen(self, screen_type: ScreenType):
    self.state_manager.set("screen.current_screen", screen_type, source="set_screen")
    # Validation ensures valid transitions
```

### Step 5: Add State Snapshots

Add strategic snapshots for debugging and rollback:

```python
# Before starting a game
self.state_manager.snapshot("Before starting game", ["game_start"])

# After completing a level
self.state_manager.snapshot("Level completed", ["level_complete", f"level_{level}"])

# For debugging
if debug_mode:
    self.state_manager.snapshot("Debug checkpoint", ["debug"])
```

## API Reference

### Basic Operations

```python
# Get state value
value = state_manager.get("puzzle.score", default=0)

# Set state value
success = state_manager.set("puzzle.score", 1000, source="player_action")

# Update multiple values
updates = {
    "puzzle.score": 1000,
    "puzzle.level": 5,
    "audio.master_volume": 0.8
}
results = state_manager.update(updates, source="level_complete")
```

### Validation

```python
# Check if state is valid
if not state_manager.is_state_valid():
    errors = state_manager.validate_state()
    for error in errors:
        print(f"Validation error: {error.message}")

# Validate specific change
errors = state_manager.validator.validate_state_change(
    state_manager.state, "puzzle.score", -100
)
```

### History and Rollback

```python
# Create snapshot
snapshot = state_manager.snapshot("Checkpoint", ["important"])

# Rollback to snapshot
success = state_manager.rollback_to_snapshot(snapshot)

# Rollback to timestamp
success = state_manager.rollback_to_timestamp(time.time() - 60)  # 1 minute ago

# Get history summary
summary = state_manager.get_history_summary()
```

### Callbacks

```python
# Add field-specific callback
def on_score_changed(field_path, old_value, new_value):
    print(f"Score changed from {old_value} to {new_value}")

state_manager.add_change_callback("puzzle.score", on_score_changed)

# Add global callback
def on_any_change(old_state, new_state):
    print("State changed")

state_manager.add_global_callback(on_any_change)
```

## Common Patterns

### State Synchronization

```python
class AudioSystem:
    def __init__(self, state_manager):
        self.state_manager = state_manager
        
        # Sync with state changes
        self.state_manager.add_change_callback(
            "audio.master_volume", 
            self._sync_volume
        )
        self.state_manager.add_change_callback(
            "audio.music_volume", 
            self._sync_music_volume
        )
    
    def _sync_volume(self, field_path, old_value, new_value):
        self.set_volume(new_value)
    
    def _sync_music_volume(self, field_path, old_value, new_value):
        self.set_music_volume(new_value)
```

### Conditional State Updates

```python
def process_input(self, input_event):
    if self.state_manager.get("puzzle.game_active"):
        # Process game input
        self.handle_game_input(input_event)
    elif self.state_manager.get("screen.current_screen") == ScreenType.MAIN_MENU:
        # Process menu input
        self.handle_menu_input(input_event)
```

### State-Dependent Rendering

```python
def render(self):
    current_screen = self.state_manager.get("screen.current_screen")
    
    if current_screen == ScreenType.GAME:
        self.render_game()
    elif current_screen == ScreenType.MAIN_MENU:
        self.render_menu()
    elif current_screen == ScreenType.SETTINGS:
        self.render_settings()
```

## Testing

### Unit Tests

```python
def test_state_management():
    state_manager = GameStateManager()
    
    # Test basic operations
    assert state_manager.set("puzzle.score", 1000, source="test")
    assert state_manager.get("puzzle.score") == 1000
    
    # Test validation
    assert not state_manager.set("puzzle.score", -100, source="test")
    
    # Test callbacks
    callback_called = False
    def test_callback(field_path, old_value, new_value):
        nonlocal callback_called
        callback_called = True
    
    state_manager.add_change_callback("puzzle.score", test_callback)
    state_manager.set("puzzle.score", 2000, source="test")
    assert callback_called
```

### Integration Tests

```python
def test_game_flow():
    state_manager = GameStateManager()
    
    # Start game
    state_manager.set("screen.current_screen", ScreenType.MAIN_MENU, source="test")
    state_manager.set("puzzle.game_mode", GameMode.QUICKPLAY, source="test")
    state_manager.set("screen.current_screen", ScreenType.GAME, source="test")
    state_manager.set("puzzle.game_active", True, source="test")
    
    # Verify state consistency
    assert state_manager.is_state_valid()
    
    # Test rollback
    snapshot = state_manager.snapshot("Game started")
    state_manager.set("puzzle.score", 1000, source="test")
    state_manager.rollback_to_snapshot(snapshot)
    assert state_manager.get("puzzle.score") == 0
```

## Debugging

### State Export

```python
# Export complete state for debugging
export = state_manager.export_state()
print(json.dumps(export, indent=2))

# Get state summary
summary = state_manager.get_state_summary()
print(f"Current screen: {summary['current_screen']}")
print(f"Game active: {summary['game_active']}")
print(f"Score: {summary['score']}")
```

### History Analysis

```python
# Analyze state changes
history = state_manager.get_history_summary()
print(f"Total changes: {history['total_changes']}")
print(f"Most changed field: {history['most_changed_field']}")
print(f"Change frequency: {history['change_frequency']:.2f}/sec")

# Get recent changes
recent_changes = state_manager.history.get_changes_since(time.time() - 60)
for change in recent_changes:
    print(f"{change.field_path}: {change.old_value} -> {change.new_value}")
```

## Performance Considerations

- **Snapshot Frequency**: Adjust `_snapshot_interval` based on needs
- **History Limits**: Configure `max_snapshots` and `max_changes` appropriately
- **Callback Performance**: Keep callbacks lightweight
- **Validation**: Disable validation in production if needed

## Migration Checklist

- [ ] Initialize GameStateManager in main classes
- [ ] Replace direct state access with state manager calls
- [ ] Add state change callbacks for reactive updates
- [ ] Replace screen management with ScreenType enum
- [ ] Add strategic snapshots for debugging
- [ ] Update tests to use new state management
- [ ] Add validation rules for critical state changes
- [ ] Implement rollback functionality where needed
- [ ] Update documentation and examples

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all modules are properly imported
2. **Validation Failures**: Check state consistency rules
3. **Callback Errors**: Verify callback signatures and error handling
4. **Performance Issues**: Adjust snapshot frequency and history limits

### Debug Commands

```python
# Check state validity
print(f"State valid: {state_manager.is_state_valid()}")

# List validation errors
for error in state_manager.validate_state():
    print(f"Error: {error.message}")

# Export state for analysis
export = state_manager.export_state()
```

## Future Enhancements

- **State Persistence**: Save/load state to/from files
- **State Replay**: Replay state changes for debugging
- **State Analytics**: Analyze state patterns and usage
- **State Optimization**: Automatic state optimization
- **State Synchronization**: Multi-player state sync 