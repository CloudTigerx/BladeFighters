# Audio System State Integration Guide

## Overview

This guide explains how to integrate the audio system with the unified game state management system. The integration provides centralized state management, validation, history tracking, and proper separation of concerns.

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   AudioSystem   │◄──►│ AudioStateManager│◄──►│ GameStateManager│
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Settings UI    │◄──►│AudioSettingsInt. │◄──►│  State History  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Key Components

### 1. AudioStateManager
- **Purpose**: Manages audio state through the unified state manager
- **Location**: `modules/audio_module/audio_state_manager.py`
- **Features**:
  - Type-safe state access
  - Validation through state manager
  - Change tracking and history
  - Callback registration

### 2. AudioSystem (Updated)
- **Purpose**: Audio playback and UI management
- **Location**: `modules/audio_module/audio_system.py`
- **Changes**:
  - Removed local state variables
  - Added state manager integration
  - Added convenience methods
  - Maintains backward compatibility

### 3. AudioSettingsIntegration
- **Purpose**: Connects settings UI with audio state
- **Location**: `modules/settings_module/audio_settings_integration.py`
- **Features**:
  - Settings change callbacks
  - State synchronization
  - Settings persistence

## Migration Steps

### Step 1: Initialize State Management

```python
# Before: Direct AudioSystem initialization
audio_system = AudioSystem()

# After: With state manager integration
from modules.game_state_module.game_state_manager import GameStateManager
from modules.audio_module.audio_system import AudioSystem

state_manager = GameStateManager()
audio_system = AudioSystem(state_manager=state_manager)
```

### Step 2: Update Audio State Access

```python
# Before: Direct property access
volume = audio_system.master_volume
audio_system.master_volume = 0.8

# After: Through state manager
volume = audio_system.audio_state_manager.get_master_volume()
audio_system.audio_state_manager.set_master_volume(0.8, "source_name")

# Or use convenience methods
volume = audio_system.get_audio_state_summary()["master_volume"]
audio_system.set_master_volume(0.8)
```

### Step 3: Update Settings Integration

```python
# Before: Direct settings access
settings = {"master_volume": 0.7, "music_volume": 0.5}

# After: Through settings integration
from modules.settings_module.audio_settings_integration import AudioSettingsIntegration

settings_integration = AudioSettingsIntegration(state_manager, audio_state_manager)

# Get callbacks for settings UI
callbacks = settings_integration.get_audio_settings_callbacks()

# Sync settings to state
settings_integration.sync_settings_to_state(settings)
```

### Step 4: Handle State Changes

```python
# State changes are automatically tracked and validated
# You can listen for changes using callbacks

def on_volume_change(field_path: str, old_value: Any, new_value: Any):
    print(f"Volume changed: {old_value} -> {new_value}")

# Register callback (done automatically by AudioStateManager)
state_manager.register_callback("audio.master_volume", on_volume_change)
```

## API Reference

### AudioStateManager Methods

#### Volume Control
```python
# Master volume
audio_state_manager.set_master_volume(volume: float, source: str) -> bool
audio_state_manager.get_master_volume() -> float

# Music volume
audio_state_manager.set_music_volume(volume: float, source: str) -> bool
audio_state_manager.get_music_volume() -> float

# Sound effects volume
audio_state_manager.set_sfx_volume(volume: float, source: str) -> bool
audio_state_manager.get_sfx_volume() -> float
```

#### Enable/Disable Control
```python
# Music
audio_state_manager.set_music_enabled(enabled: bool, source: str) -> bool
audio_state_manager.is_music_enabled() -> bool

# Sound effects
audio_state_manager.set_sfx_enabled(enabled: bool, source: str) -> bool
audio_state_manager.is_sfx_enabled() -> bool
```

#### Music State
```python
# Current music track
audio_state_manager.set_current_music(music_name: Optional[str], source: str) -> bool
audio_state_manager.get_current_music() -> Optional[str]

# Music playing state
audio_state_manager.set_music_playing(playing: bool, source: str) -> bool
audio_state_manager.is_music_playing() -> bool

# MP3 player visibility
audio_state_manager.set_mp3_player_visible(visible: bool, source: str) -> bool
audio_state_manager.is_mp3_player_visible() -> bool
```

#### State Management
```python
# Get complete audio state
audio_state_manager.get_audio_state() -> AudioState

# Get state summary
audio_state_manager.get_state_summary() -> Dict[str, Any]

# Create snapshots
audio_state_manager.create_snapshot(description: str) -> None

# Settings sync
audio_state_manager.sync_from_settings(settings: Dict[str, Any]) -> None
audio_state_manager.get_settings_dict() -> Dict[str, Any]
```

### AudioSystem Convenience Methods

```python
# Volume control
audio_system.set_master_volume(volume: float) -> bool
audio_system.set_music_volume(volume: float) -> bool
audio_system.set_sfx_volume(volume: float) -> bool

# Enable/disable
audio_system.enable_music(enabled: bool) -> bool
audio_system.enable_sfx(enabled: bool) -> bool

# State access
audio_system.get_audio_state_summary() -> Dict[str, Any]
audio_system.sync_from_settings(settings: Dict[str, Any]) -> None
```

### AudioSettingsIntegration Methods

```python
# Get settings callbacks
settings_integration.get_audio_settings_callbacks() -> Dict[str, Callable]

# Settings sync
settings_integration.sync_settings_to_state(settings: Dict[str, Any]) -> None
settings_integration.get_current_settings() -> Dict[str, Any]

# State management
settings_integration.create_settings_snapshot(description: str) -> None
settings_integration.get_audio_state_summary() -> Dict[str, Any]
```

## State Schema

The audio state is defined in `modules/game_state_module/state_schema.py`:

```python
@dataclass
class AudioState:
    """Audio system state."""
    master_volume: float = 0.6
    music_volume: float = 0.5
    sfx_volume: float = 0.7
    music_enabled: bool = True
    sfx_enabled: bool = True
    current_music: Optional[str] = None
    music_playing: bool = False
    mp3_player_visible: bool = False
```

## Validation Rules

The state manager enforces the following validation rules:

- **Volume values**: Must be between 0.0 and 1.0
- **Boolean values**: Must be True or False
- **String values**: Must be valid strings or None
- **Type safety**: All values must match their defined types

## Error Handling

The integration includes comprehensive error handling:

```python
# Invalid volume value
success = audio_state_manager.set_master_volume(1.5, "test")
if not success:
    print("Volume change failed - value out of range")

# State validation errors are logged
# Check logs for validation failure details
```

## Testing

Run the integration tests:

```bash
# Run all audio state integration tests
pytest modules/audio_module/tests/test_audio_state_integration.py -v

# Run specific test
pytest modules/audio_module/tests/test_audio_state_integration.py::TestAudioStateIntegration::test_master_volume_setting -v
```

## Backward Compatibility

The AudioSystem maintains backward compatibility:

```python
# Old way still works (without state manager)
audio_system = AudioSystem()
audio_system.play_sound("click")  # Still works

# New way with state management
audio_system = AudioSystem(state_manager=state_manager)
audio_system.play_sound("click")  # Works with state tracking
```

## Performance Considerations

- State changes are batched and optimized
- Callbacks are only triggered when values actually change
- History tracking can be configured (max snapshots, max changes)
- Volume updates are applied efficiently to loaded sounds

## Debugging

### State Inspection
```python
# Get current audio state
summary = audio_state_manager.get_state_summary()
print(summary)

# Get state history
changes = state_manager.history.get_changes_for_field("audio.master_volume")
for change in changes:
    print(f"{change.timestamp}: {change.old_value} -> {change.new_value}")
```

### Logging
```python
# Enable debug logging
import logging
logging.getLogger("modules.audio_module").setLevel(logging.DEBUG)
```

## Migration Checklist

- [ ] Initialize GameStateManager
- [ ] Update AudioSystem initialization to include state_manager
- [ ] Replace direct property access with state manager calls
- [ ] Update settings UI to use AudioSettingsIntegration
- [ ] Add error handling for state validation failures
- [ ] Update tests to use new state management
- [ ] Verify backward compatibility
- [ ] Test state persistence and restoration
- [ ] Verify performance with high-frequency state changes

## Common Issues

### Issue: State changes not reflected in audio
**Solution**: Ensure `_sync_from_state()` is called after state changes

### Issue: Settings not persisting
**Solution**: Use `sync_from_settings()` to sync with configuration

### Issue: Performance problems with frequent changes
**Solution**: Batch state changes and use appropriate snapshot intervals

### Issue: Callbacks not firing
**Solution**: Verify callback registration and check for validation errors

## Support

For issues or questions about the audio state integration:

1. Check the integration tests for examples
2. Review the state schema for validation rules
3. Check logs for error messages
4. Verify state manager initialization
5. Test with minimal state changes first 