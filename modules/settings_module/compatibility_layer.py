"""
Configuration Compatibility Layer
================================

Provides backward compatibility with existing ConfigService and ControlsService
interfaces while using the new UnifiedConfigManager underneath.

This allows for a gradual migration to the unified configuration system
without breaking existing code.
"""

from typing import Dict, Any, Optional
from .unified_config import UnifiedConfigManager, ConfigCategory
from ..logging_module.logger import get_logger

logger = get_logger(__name__)


class ConfigServiceCompat:
    """
    Backward-compatible ConfigService that uses UnifiedConfigManager.
    
    Maintains the same interface as the original ConfigService while
    leveraging the new unified configuration system.
    """
    
    def __init__(self, config_path: str = "game_settings.json"):
        # Extract config root from path
        from pathlib import Path
        config_root = str(Path(config_path).parent)
        if config_root == ".":
            config_root = "."
        
        self.config_path = config_path
        self.unified_config = UnifiedConfigManager(config_root)
        self.settings = self.unified_config._config  # Direct access for compatibility
        
        logger.info(f"ConfigServiceCompat initialized with unified config manager")
    
    def load(self) -> Dict[str, Any]:
        """Load configuration with defaults and validation."""
        try:
            # The unified config manager already loads everything in __init__
            # Just return the current settings
            return self.settings
        except Exception as e:
            logger.error(f"Failed to load configuration: {str(e)}")
            return {}
    
    def save(self) -> None:
        """Save configuration with error handling."""
        try:
            self.unified_config.save_all()
            logger.debug("Configuration saved successfully")
        except Exception as e:
            logger.error(f"Failed to save configuration: {str(e)}")
    
    def update(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update configuration with new values."""
        try:
            results = self.unified_config.update(updates)
            # Update the settings dict for backward compatibility
            self.settings.update(updates)
            return self.settings
        except Exception as e:
            logger.error(f"Failed to update configuration: {str(e)}")
            return self.settings
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with fallback."""
        return self.unified_config.get(key, default)
    
    def set(self, key: str, value: Any) -> bool:
        """Set a configuration value."""
        try:
            success = self.unified_config.set(key, value)
            if success:
                # Update the settings dict for backward compatibility
                self.settings[key] = value
            return success
        except Exception as e:
            logger.error(f"Failed to set configuration {key}: {str(e)}")
            return False
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values."""
        return self.settings.copy()


class ControlsServiceCompat:
    """
    Backward-compatible ControlsService that uses UnifiedConfigManager.
    
    Maintains the same interface as the original ControlsService while
    leveraging the new unified configuration system.
    """
    
    def __init__(self, controls_path: str):
        # Extract config root from path
        from pathlib import Path
        config_root = str(Path(controls_path).parent)
        if config_root == ".":
            config_root = "."
        
        self.controls_path = controls_path
        self.unified_config = UnifiedConfigManager(config_root)
        self.bindings = {}  # Will be populated from unified config
        
        # Load controls from unified config
        self._load_controls()
        
        logger.info(f"ControlsServiceCompat initialized with unified config manager")
    
    def _load_controls(self):
        """Load control bindings from unified config."""
        try:
            # Get all input-related settings
            input_config = self.unified_config.get_category(ConfigCategory.INPUT)
            
            # Filter to just the key bindings (exclude sensitivity, repeat settings, etc.)
            key_bindings = [
                "move_up", "move_down", "move_left", "move_right",
                "action", "menu_cancel", "menu_confirm", "menu_tab",
                "music_next", "music_prev", "music_pause", "fullscreen_toggle"
            ]
            
            for key in key_bindings:
                value = input_config.get(key)
                if value is not None:
                    self.bindings[key] = value
            
            logger.debug(f"Loaded {len(self.bindings)} control bindings")
            
        except Exception as e:
            logger.error(f"Failed to load controls: {str(e)}")
            # Fall back to defaults
            self.bindings = {
                "move_up": 1073741906,
                "move_down": 1073741905,
                "move_left": 1073741904,
                "move_right": 1073741903,
                "action": 32,
                "menu_cancel": 27,
            }
    
    def load(self) -> Dict[str, int]:
        """Load controls with defaults and validation."""
        try:
            self._load_controls()
            return self.bindings
        except Exception as e:
            logger.error(f"Failed to load controls: {str(e)}")
            return {}
    
    def save(self) -> None:
        """Save controls with error handling."""
        try:
            self.unified_config.save_all()
            logger.debug("Controls saved successfully")
        except Exception as e:
            logger.error(f"Failed to save controls: {str(e)}")
    
    def get(self, key: str, default: int = 0) -> int:
        """Get control binding with fallback."""
        return self.bindings.get(key, default)
    
    def set(self, key: str, value: int) -> bool:
        """Set a control binding."""
        try:
            success = self.unified_config.set(key, value)
            if success:
                self.bindings[key] = value
            return success
        except Exception as e:
            logger.error(f"Failed to set control {key}: {str(e)}")
            return False
    
    def update(self, updates: Dict[str, int]) -> Dict[str, int]:
        """Update multiple control bindings."""
        try:
            results = self.unified_config.update(updates)
            # Update the bindings dict for backward compatibility
            self.bindings.update(updates)
            return self.bindings
        except Exception as e:
            logger.error(f"Failed to update controls: {str(e)}")
            return self.bindings


# Convenience functions for easy migration
def create_unified_config(config_root: str = ".") -> UnifiedConfigManager:
    """Create a new unified configuration manager."""
    return UnifiedConfigManager(config_root)


def migrate_to_unified_config() -> UnifiedConfigManager:
    """
    Create a unified configuration manager and log migration info.
    
    This function can be used to gradually migrate code to use the
    unified configuration system directly.
    """
    config = UnifiedConfigManager()
    summary = config.get_summary()
    
    logger.info("Migrated to unified configuration system")
    logger.info(f"Configuration summary: {summary}")
    
    return config 