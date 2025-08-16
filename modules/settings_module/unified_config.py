"""
Unified Configuration Management System
======================================

Provides a single, robust configuration management system that consolidates
all game configuration into a unified interface with proper validation,
schema enforcement, and error handling.

Features:
- Single configuration service for all game settings
- Schema-based validation with defaults
- Type-safe configuration access
- Automatic file persistence
- Hot-reload capability
- Configuration change notifications
- Comprehensive error handling
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable, Union
from dataclasses import dataclass, field
from enum import Enum

from ..logging_module.error_handler import (
    safe_file_operation,
    safe_value_conversion,
    safe_range_clamp,
    ConfigurationError
)
from ..logging_module.logger import get_logger

logger = get_logger(__name__)


class ConfigCategory(Enum):
    """Configuration categories for organization."""
    AUDIO = "audio"
    VIDEO = "video"
    INPUT = "input"
    GAME = "game"
    UI = "ui"
    RENDERER = "renderer"
    ATTACKS = "attacks"


@dataclass
class ConfigSchema:
    """Schema definition for a configuration value."""
    key: str
    category: ConfigCategory
    default: Any
    type: type
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    allowed_values: Optional[List[Any]] = None
    description: str = ""
    file_path: Optional[str] = None  # Which file this setting comes from


class UnifiedConfigManager:
    """
    Unified configuration management system.
    
    Consolidates all game configuration into a single service with:
    - Schema-based validation
    - Type-safe access
    - Automatic persistence
    - Change notifications
    - Comprehensive error handling
    """
    
    def __init__(self, config_root: str = "."):
        self.config_root = Path(config_root)
        self._config: Dict[str, Any] = {}
        self._schema: Dict[str, ConfigSchema] = {}
        self._change_callbacks: Dict[str, List[Callable]] = {}
        self._file_paths: Dict[str, Path] = {}
        
        # Define configuration schema
        self._define_schema()
        
        # Load all configuration files
        self._load_all_configs()
    
    def _define_schema(self):
        """Define the complete configuration schema with validation rules."""
        
        # Audio settings
        self._add_schema(ConfigSchema(
            key="master_volume",
            category=ConfigCategory.AUDIO,
            default=0.6,
            type=float,
            min_value=0.0,
            max_value=1.0,
            description="Master audio volume (0.0-1.0)",
            file_path="game_settings.json"
        ))
        
        self._add_schema(ConfigSchema(
            key="music_volume",
            category=ConfigCategory.AUDIO,
            default=0.5,
            type=float,
            min_value=0.0,
            max_value=1.0,
            description="Music volume (0.0-1.0)",
            file_path="game_settings.json"
        ))
        
        # Video settings
        self._add_schema(ConfigSchema(
            key="brightness",
            category=ConfigCategory.VIDEO,
            default=1.0,
            type=float,
            min_value=0.3,
            max_value=1.0,
            description="Screen brightness (0.3-1.0)",
            file_path="game_settings.json"
        ))
        
        self._add_schema(ConfigSchema(
            key="ui_scale",
            category=ConfigCategory.VIDEO,
            default=1.0,
            type=float,
            min_value=0.8,
            max_value=1.5,
            description="UI scaling factor (0.8-1.5)",
            file_path="game_settings.json"
        ))
        
        self._add_schema(ConfigSchema(
            key="vsync",
            category=ConfigCategory.VIDEO,
            default=True,
            type=bool,
            description="Enable vertical sync",
            file_path="game_settings.json"
        ))
        
        self._add_schema(ConfigSchema(
            key="fullscreen",
            category=ConfigCategory.VIDEO,
            default=False,
            type=bool,
            description="Enable fullscreen mode",
            file_path="game_settings.json"
        ))
        
        self._add_schema(ConfigSchema(
            key="native_fullscreen",
            category=ConfigCategory.VIDEO,
            default=False,
            type=bool,
            description="Enable native fullscreen (macOS)",
            file_path="game_settings.json"
        ))
        
        self._add_schema(ConfigSchema(
            key="borderless",
            category=ConfigCategory.VIDEO,
            default=False,
            type=bool,
            description="Enable borderless windowed mode",
            file_path="game_settings.json"
        ))
        
        self._add_schema(ConfigSchema(
            key="show_fps",
            category=ConfigCategory.VIDEO,
            default=False,
            type=bool,
            description="Show FPS counter",
            file_path="game_settings.json"
        ))
        
        self._add_schema(ConfigSchema(
            key="particle_effects",
            category=ConfigCategory.VIDEO,
            default=True,
            type=bool,
            description="Enable particle effects",
            file_path="game_settings.json"
        ))
        
        self._add_schema(ConfigSchema(
            key="resolution",
            category=ConfigCategory.VIDEO,
            default=None,
            type=type(None),  # Allow None or list
            description="Screen resolution [width, height] or None for auto",
            file_path="game_settings.json"
        ))
        
        # Input settings
        self._add_schema(ConfigSchema(
            key="sensitivity",
            category=ConfigCategory.INPUT,
            default=1.0,
            type=float,
            min_value=0.1,
            max_value=2.0,
            description="Input sensitivity (0.1-2.0)",
            file_path="game_settings.json"
        ))
        
        self._add_schema(ConfigSchema(
            key="repeat_initial_delay_ms",
            category=ConfigCategory.INPUT,
            default=120,
            type=int,
            min_value=0,
            max_value=1000,
            description="Initial delay before key repeat (ms)",
            file_path="game_settings.json"
        ))
        
        self._add_schema(ConfigSchema(
            key="repeat_interval_ms",
            category=ConfigCategory.INPUT,
            default=80,
            type=int,
            min_value=10,
            max_value=500,
            description="Key repeat interval (ms)",
            file_path="game_settings.json"
        ))
        
        self._add_schema(ConfigSchema(
            key="repeat_move_interval_ms",
            category=ConfigCategory.INPUT,
            default=500,
            type=int,
            min_value=50,
            max_value=2000,
            description="Move key repeat interval (ms)",
            file_path="game_settings.json"
        ))
        
        self._add_schema(ConfigSchema(
            key="repeat_rotate_interval_ms",
            category=ConfigCategory.INPUT,
            default=600,
            type=int,
            min_value=50,
            max_value=2000,
            description="Rotate key repeat interval (ms)",
            file_path="game_settings.json"
        ))
        
        # Key bindings
        self._add_schema(ConfigSchema(
            key="move_up",
            category=ConfigCategory.INPUT,
            default=1073741906,  # pygame.K_UP
            type=int,
            description="Move up key code",
            file_path="game_controls.json"
        ))
        
        self._add_schema(ConfigSchema(
            key="move_down",
            category=ConfigCategory.INPUT,
            default=1073741905,  # pygame.K_DOWN
            type=int,
            description="Move down key code",
            file_path="game_controls.json"
        ))
        
        self._add_schema(ConfigSchema(
            key="move_left",
            category=ConfigCategory.INPUT,
            default=1073741904,  # pygame.K_LEFT
            type=int,
            description="Move left key code",
            file_path="game_controls.json"
        ))
        
        self._add_schema(ConfigSchema(
            key="move_right",
            category=ConfigCategory.INPUT,
            default=1073741903,  # pygame.K_RIGHT
            type=int,
            description="Move right key code",
            file_path="game_controls.json"
        ))
        
        self._add_schema(ConfigSchema(
            key="action",
            category=ConfigCategory.INPUT,
            default=32,  # pygame.K_SPACE
            type=int,
            description="Action key code",
            file_path="game_controls.json"
        ))
        
        self._add_schema(ConfigSchema(
            key="menu_cancel",
            category=ConfigCategory.INPUT,
            default=27,  # pygame.K_ESCAPE
            type=int,
            description="Menu cancel key code",
            file_path="game_controls.json"
        ))
        
        self._add_schema(ConfigSchema(
            key="menu_confirm",
            category=ConfigCategory.INPUT,
            default=13,  # pygame.K_RETURN
            type=int,
            description="Menu confirm key code",
            file_path="game_controls.json"
        ))
        
        self._add_schema(ConfigSchema(
            key="menu_tab",
            category=ConfigCategory.INPUT,
            default=9,  # pygame.K_TAB
            type=int,
            description="Menu tab key code",
            file_path="game_controls.json"
        ))
        
        self._add_schema(ConfigSchema(
            key="music_next",
            category=ConfigCategory.INPUT,
            default=93,  # pygame.K_RIGHTBRACKET
            type=int,
            description="Next music track key code",
            file_path="game_controls.json"
        ))
        
        self._add_schema(ConfigSchema(
            key="music_prev",
            category=ConfigCategory.INPUT,
            default=91,  # pygame.K_LEFTBRACKET
            type=int,
            description="Previous music track key code",
            file_path="game_controls.json"
        ))
        
        self._add_schema(ConfigSchema(
            key="music_pause",
            category=ConfigCategory.INPUT,
            default=112,  # pygame.K_p
            type=int,
            description="Music pause key code",
            file_path="game_controls.json"
        ))
        
        self._add_schema(ConfigSchema(
            key="fullscreen_toggle",
            category=ConfigCategory.INPUT,
            default=1073741892,  # pygame.K_F11
            type=int,
            description="Fullscreen toggle key code",
            file_path="game_controls.json"
        ))
        
        # Game settings
        self._add_schema(ConfigSchema(
            key="attack_freeze_ms_on_receive",
            category=ConfigCategory.GAME,
            default=150,
            type=int,
            min_value=0,
            max_value=1000,
            description="Freeze duration when receiving attacks (ms)",
            file_path="game_settings.json"
        ))
        
        # Renderer settings
        self._add_schema(ConfigSchema(
            key="renderer.snap_on_land",
            category=ConfigCategory.RENDERER,
            default=True,
            type=bool,
            description="Snap pieces to grid on landing",
            file_path="game_settings.json"
        ))
        
        self._add_schema(ConfigSchema(
            key="renderer.landing_epsilon_px",
            category=ConfigCategory.RENDERER,
            default=0,
            type=int,
            min_value=0,
            max_value=10,
            description="Landing position tolerance (pixels)",
            file_path="game_settings.json"
        ))
        
        # Attack settings
        self._add_schema(ConfigSchema(
            key="attacks.spawn_mode",
            category=ConfigCategory.ATTACKS,
            default="animated",
            type=str,
            allowed_values=["animated", "instant"],
            description="Attack spawn animation mode",
            file_path="game_settings.json"
        ))
        
        # UI positions (special handling for dynamic positions)
        self._add_schema(ConfigSchema(
            key="ui_positions",
            category=ConfigCategory.UI,
            default={},
            type=dict,
            description="UI element positions",
            file_path="ui_positions.json"
        ))
        
        # Item configurations (special handling)
        self._add_schema(ConfigSchema(
            key="items_config",
            category=ConfigCategory.GAME,
            default={},
            type=dict,
            description="Item and weapon configurations",
            file_path="puzzleassets/items_config.json"
        ))
    
    def _add_schema(self, schema: ConfigSchema):
        """Add a configuration schema definition."""
        self._schema[schema.key] = schema
    
    def _load_all_configs(self):
        """Load all configuration files and merge them."""
        try:
            # Apply defaults first
            self._apply_defaults()
            
            # Load each configuration file (this will override defaults)
            self._load_config_file("game_settings.json")
            self._load_config_file("game_controls.json")
            self._load_config_file("ui_positions.json")
            self._load_config_file("puzzleassets/items_config.json")
            
            # Validate all values
            self._validate_all()
            
            logger.info("Configuration loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            # Apply defaults even if loading fails
            self._apply_defaults()
    
    @safe_file_operation("load config file", {}, {})
    def _load_config_file(self, file_path: str) -> Dict[str, Any]:
        """Load a single configuration file."""
        full_path = self.config_root / file_path
        
        if not full_path.exists():
            logger.info(f"Configuration file not found: {file_path}, will use defaults")
            return {}
        
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            if not isinstance(data, dict):
                logger.warning(f"Invalid configuration format in {file_path}: expected dict")
                return {}
            
            # Store file path for this configuration
            self._file_paths[file_path] = full_path
            
            # Merge into main config
            for key, value in data.items():
                self._config[key] = value
            
            logger.debug(f"Loaded configuration from {file_path}")
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {file_path}: {e}")
            return {}
        except Exception as e:
            logger.error(f"Failed to load {file_path}: {e}")
            return {}
    
    def _apply_defaults(self):
        """Apply default values for missing configuration keys."""
        for key, schema in self._schema.items():
            if key not in self._config:
                self._config[key] = schema.default
                logger.debug(f"Applied default for {key}: {schema.default}")
    
    def _validate_all(self):
        """Validate all configuration values against their schemas."""
        for key, value in self._config.items():
            if key in self._schema:
                self._validate_value(key, value)
    
    def _validate_value(self, key: str, value: Any) -> bool:
        """Validate a single configuration value."""
        if key not in self._schema:
            return True  # Unknown keys are allowed
        
        schema = self._schema[key]
        
        # Type validation
        if schema.type != type(None) and not isinstance(value, schema.type):
            try:
                # Try to convert the value
                if schema.type == bool:
                    value = bool(value)
                elif schema.type == int:
                    value = int(value)
                elif schema.type == float:
                    value = float(value)
                elif schema.type == str:
                    value = str(value)
                else:
                    logger.warning(f"Invalid type for {key}: expected {schema.type.__name__}, got {type(value).__name__}")
                    return False
                
                # Update the converted value
                self._config[key] = value
                
            except (ValueError, TypeError):
                logger.warning(f"Invalid type for {key}: expected {schema.type.__name__}, got {type(value).__name__}")
                return False
        
        # Range validation
        if schema.min_value is not None and value < schema.min_value:
            logger.warning(f"Value for {key} ({value}) is below minimum ({schema.min_value})")
            value = schema.min_value
            self._config[key] = value
        
        if schema.max_value is not None and value > schema.max_value:
            logger.warning(f"Value for {key} ({value}) is above maximum ({schema.max_value})")
            value = schema.max_value
            self._config[key] = value
        
        # Allowed values validation
        if schema.allowed_values is not None and value not in schema.allowed_values:
            logger.warning(f"Value for {key} ({value}) is not in allowed values {schema.allowed_values}")
            value = schema.default
            self._config[key] = value
        
        return True
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value with fallback."""
        if key in self._config:
            return self._config[key]
        
        # Check schema for default
        if key in self._schema:
            return self._schema[key].default
        
        return default
    
    def set(self, key: str, value: Any) -> bool:
        """Set a configuration value with validation."""
        try:
            # Check if value actually changed (before validation)
            old_value = self._config.get(key)
            
            # Set the value first
            self._config[key] = value
            
            # Validate the value (this may modify the value)
            if not self._validate_value(key, value):
                return False
            
            # Get the validated value (may be different from input)
            validated_value = self._config.get(key)
            
            if old_value == validated_value:
                return True  # No change
            
            # Notify change callbacks
            self._notify_change(key, old_value, validated_value)
            
            # Auto-save if this is a persistent setting
            if key in self._schema:
                self._save_config_file(self._schema[key].file_path)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to set configuration {key}: {e}")
            return False
    
    def update(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update multiple configuration values."""
        results = {}
        for key, value in updates.items():
            results[key] = self.set(key, value)
        return results
    
    def get_category(self, category: ConfigCategory) -> Dict[str, Any]:
        """Get all configuration values for a specific category."""
        result = {}
        for key, value in self._config.items():
            if key in self._schema and self._schema[key].category == category:
                result[key] = value
        return result
    
    def get_schema(self, key: str) -> Optional[ConfigSchema]:
        """Get the schema for a configuration key."""
        return self._schema.get(key)
    
    def get_all_schemas(self) -> Dict[str, ConfigSchema]:
        """Get all configuration schemas."""
        return self._schema.copy()
    
    def register_change_callback(self, key: str, callback: Callable[[str, Any, Any], None]):
        """Register a callback for configuration changes."""
        if key not in self._change_callbacks:
            self._change_callbacks[key] = []
        self._change_callbacks[key].append(callback)
    
    def unregister_change_callback(self, key: str, callback: Callable[[str, Any, Any], None]):
        """Unregister a configuration change callback."""
        if key in self._change_callbacks:
            try:
                self._change_callbacks[key].remove(callback)
            except ValueError:
                pass
    
    def _notify_change(self, key: str, old_value: Any, new_value: Any):
        """Notify all registered callbacks of a configuration change."""
        if key in self._change_callbacks:
            for callback in self._change_callbacks[key]:
                try:
                    callback(key, old_value, new_value)
                except Exception as e:
                    logger.error(f"Error in configuration change callback for {key}: {e}")
    
    def _save_config_file(self, file_path: str):
        """Save configuration to a specific file."""
        if not file_path:
            return
        
        try:
            full_path = self.config_root / file_path
            
            # Ensure directory exists
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Collect all settings for this file
            file_config = {}
            for key, value in self._config.items():
                if key in self._schema and self._schema[key].file_path == file_path:
                    file_config[key] = value
            
            # Save to file
            with open(full_path, "w", encoding="utf-8") as f:
                json.dump(file_config, f, indent=2)
            
            logger.debug(f"Saved configuration to {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to save configuration to {file_path}: {e}")
    
    def save_all(self):
        """Save all configuration files."""
        try:
            # Group settings by file
            files_to_save = set()
            for key in self._config:
                if key in self._schema and self._schema[key].file_path:
                    files_to_save.add(self._schema[key].file_path)
            
            # Save each file
            for file_path in files_to_save:
                self._save_config_file(file_path)
            
            logger.info("All configuration files saved")
            
        except Exception as e:
            logger.error(f"Failed to save configuration files: {e}")
    
    def reload(self):
        """Reload all configuration files."""
        try:
            # Clear current configuration
            self._config.clear()
            
            # Reload all files
            self._load_all_configs()
            
            logger.info("Configuration reloaded")
            
        except Exception as e:
            logger.error(f"Failed to reload configuration: {e}")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the current configuration state."""
        summary = {
            "total_settings": len(self._config),
            "categories": {},
            "files": list(self._file_paths.keys()),
            "validation_errors": []
        }
        
        # Count by category
        for key, value in self._config.items():
            if key in self._schema:
                category = self._schema[key].category.value
                if category not in summary["categories"]:
                    summary["categories"][category] = 0
                summary["categories"][category] += 1
        
        return summary 