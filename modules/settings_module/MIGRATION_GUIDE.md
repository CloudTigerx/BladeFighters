# Configuration Management Unification - Migration Guide

## Overview

The Configuration Management Unification refactoring consolidates all game configuration into a single, robust system with proper validation, schema enforcement, and error handling.

## What Changed

### Before (Fragmented Configuration)
- Multiple configuration files: `game_settings.json`, `game_controls.json`, `ui_positions.json`, `items_config.json`
- Separate services: `ConfigService`, `ControlsService`
- Inconsistent error handling and validation
- Scattered defaults and validation logic

### After (Unified Configuration)
- Single `UnifiedConfigManager` handles all configuration
- Schema-based validation with automatic type conversion and range clamping
- Centralized defaults and validation rules
- Change notification system
- Comprehensive error handling

## Migration Path

### Option 1: Backward Compatibility (Recommended)
The existing `ConfigService` and `ControlsService` classes now use the unified system underneath, so **no code changes are required**. Your existing code will automatically benefit from the new features.

```python
# This still works exactly the same
from modules.settings_module.config_service import ConfigService
from modules.settings_module.controls_service import ControlsService

config = ConfigService("game_settings.json")
controls = ControlsService("game_controls.json")

# All existing methods work as before
config.get("master_volume")
config.set("brightness", 0.8)
controls.get("move_up")
```

### Option 2: Direct Migration to Unified System
For new code or when you want to use advanced features:

```python
from modules.settings_module.unified_config import UnifiedConfigManager, ConfigCategory

# Create unified config manager
config = UnifiedConfigManager()

# Basic usage (same as before)
volume = config.get("master_volume")
config.set("brightness", 0.8)

# Advanced features
# Get all audio settings
audio_settings = config.get_category(ConfigCategory.AUDIO)

# Register change callbacks
def on_volume_change(key, old_value, new_value):
    print(f"Volume changed from {old_value} to {new_value}")

config.register_change_callback("master_volume", on_volume_change)

# Get configuration summary
summary = config.get_summary()
print(f"Total settings: {summary['total_settings']}")
```

## New Features

### 1. Schema-Based Validation
All configuration values are automatically validated against schemas:

```python
# Automatic type conversion
config.set("repeat_interval_ms", "100")  # String -> int
config.set("ui_scale", "1.2")           # String -> float
config.set("vsync", "true")             # String -> bool

# Range clamping
config.set("master_volume", 2.0)        # Clamped to 1.0
config.set("master_volume", -1.0)       # Clamped to 0.0

# Allowed values
config.set("attacks.spawn_mode", "invalid")  # Reverts to "animated"
```

### 2. Configuration Categories
Settings are organized into categories for easier management:

```python
# Get all settings in a category
audio_settings = config.get_category(ConfigCategory.AUDIO)
video_settings = config.get_category(ConfigCategory.VIDEO)
input_settings = config.get_category(ConfigCategory.INPUT)
```

### 3. Change Notifications
Register callbacks to be notified when settings change:

```python
def on_setting_change(key, old_value, new_value):
    print(f"{key} changed: {old_value} -> {new_value}")

config.register_change_callback("master_volume", on_setting_change)
config.register_change_callback("brightness", on_setting_change)
```

### 4. Configuration Summary
Get an overview of the current configuration state:

```python
summary = config.get_summary()
print(f"Total settings: {summary['total_settings']}")
print(f"Categories: {summary['categories']}")
print(f"Files loaded: {summary['files']}")
```

## Configuration Schema

The unified system defines schemas for all configuration values:

```python
# Example schema definition
ConfigSchema(
    key="master_volume",
    category=ConfigCategory.AUDIO,
    default=0.6,
    type=float,
    min_value=0.0,
    max_value=1.0,
    description="Master audio volume (0.0-1.0)",
    file_path="game_settings.json"
)
```

### Schema Fields
- `key`: Configuration key name
- `category`: Organizational category
- `default`: Default value if not specified
- `type`: Expected data type
- `min_value`: Minimum allowed value (for numeric types)
- `max_value`: Maximum allowed value (for numeric types)
- `allowed_values`: List of allowed values (for enums)
- `description`: Human-readable description
- `file_path`: Which file this setting is stored in

## Error Handling

The unified system provides comprehensive error handling:

```python
# Safe configuration access
try:
    volume = config.get("master_volume", 0.5)  # Fallback default
    success = config.set("brightness", 0.8)
    if not success:
        print("Failed to set brightness")
except Exception as e:
    print(f"Configuration error: {e}")
```

## File Management

The unified system automatically manages multiple configuration files:

```python
# Save all configuration files
config.save_all()

# Reload from files
config.reload()

# Save specific file
config._save_config_file("game_settings.json")
```

## Testing

The unified system includes comprehensive tests:

```bash
# Run all configuration tests
python3 -m pytest modules/settings_module/tests/test_unified_config.py -v

# Run specific test categories
python3 -m pytest modules/settings_module/tests/test_unified_config.py::TestUnifiedConfigManager -v
python3 -m pytest modules/settings_module/tests/test_unified_config.py::TestConfigServiceCompat -v
```

## Benefits

### For Developers
1. **Single Source of Truth**: All configuration in one place
2. **Type Safety**: Automatic validation and type conversion
3. **Better Debugging**: Comprehensive logging and error messages
4. **Change Tracking**: Notifications when settings change
5. **Schema Documentation**: Self-documenting configuration

### For Users
1. **Consistent Behavior**: All settings follow the same validation rules
2. **Better Error Messages**: Clear feedback when settings are invalid
3. **Automatic Recovery**: Invalid settings are automatically corrected
4. **No Data Loss**: Settings are automatically backed up and restored

## Migration Checklist

- [ ] Existing code continues to work (backward compatibility)
- [ ] New features are available for advanced use cases
- [ ] All configuration files are properly loaded and saved
- [ ] Validation rules are applied consistently
- [ ] Error handling is comprehensive
- [ ] Tests pass for all functionality
- [ ] Documentation is updated

## Future Enhancements

The unified configuration system provides a foundation for future enhancements:

1. **Configuration UI**: Build settings screens using the schema
2. **Configuration Profiles**: Save/load different configuration sets
3. **Remote Configuration**: Sync settings across devices
4. **Configuration Analytics**: Track which settings are used most
5. **Dynamic Configuration**: Hot-reload configuration changes

## Support

If you encounter issues during migration:

1. Check the test suite for examples
2. Review the schema definitions in `unified_config.py`
3. Use the compatibility layer for gradual migration
4. Enable debug logging to see detailed configuration operations

The unified configuration system is designed to be robust and maintainable, providing a solid foundation for the game's configuration needs. 