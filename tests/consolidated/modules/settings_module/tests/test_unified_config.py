"""
Tests for the Unified Configuration Management System
====================================================

Tests the new unified configuration system and its compatibility layer.
"""

import json
import tempfile
import os
from pathlib import Path
import pytest

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from modules.settings_module.unified_config import UnifiedConfigManager, ConfigCategory, ConfigSchema
from modules.settings_module.compatibility_layer import ConfigServiceCompat, ControlsServiceCompat


class TestUnifiedConfigManager:
    """Test the unified configuration manager."""
    
    def test_initialization(self, tmp_path):
        """Test basic initialization."""
        config = UnifiedConfigManager(str(tmp_path))
        assert config is not None
        assert len(config._schema) > 0
        
        # Check that we have settings in each category
        summary = config.get_summary()
        assert summary["total_settings"] > 0
        assert len(summary["categories"]) > 0
    
    def test_schema_validation(self, tmp_path):
        """Test schema validation."""
        config = UnifiedConfigManager(str(tmp_path))
        
        # Test valid values
        assert config.set("master_volume", 0.5) == True
        assert config.get("master_volume") == 0.5
        
        # Test invalid values (should be clamped)
        assert config.set("master_volume", 2.0) == True
        assert config.get("master_volume") == 1.0  # Clamped to max
        
        assert config.set("master_volume", -1.0) == True
        assert config.get("master_volume") == 0.0  # Clamped to min
    
    def test_type_conversion(self, tmp_path):
        """Test automatic type conversion."""
        config = UnifiedConfigManager(str(tmp_path))
        
        # Test string to int conversion
        assert config.set("repeat_interval_ms", "100") == True
        assert config.get("repeat_interval_ms") == 100
        assert isinstance(config.get("repeat_interval_ms"), int)
        
        # Test string to float conversion
        assert config.set("ui_scale", "1.2") == True
        assert config.get("ui_scale") == 1.2
        assert isinstance(config.get("ui_scale"), float)
        
        # Test string to bool conversion
        assert config.set("vsync", "true") == True
        assert config.get("vsync") == True
        assert isinstance(config.get("vsync"), bool)
    
    def test_allowed_values(self, tmp_path):
        """Test allowed values validation."""
        config = UnifiedConfigManager(str(tmp_path))
        
        # Test valid value
        assert config.set("attacks.spawn_mode", "animated") == True
        assert config.get("attacks.spawn_mode") == "animated"
        
        # Test invalid value (should revert to default)
        assert config.set("attacks.spawn_mode", "invalid_mode") == True
        assert config.get("attacks.spawn_mode") == "animated"  # Default
    
    def test_category_access(self, tmp_path):
        """Test getting settings by category."""
        config = UnifiedConfigManager(str(tmp_path))
        
        audio_settings = config.get_category(ConfigCategory.AUDIO)
        assert len(audio_settings) > 0
        assert "master_volume" in audio_settings
        assert "music_volume" in audio_settings
        
        input_settings = config.get_category(ConfigCategory.INPUT)
        assert len(input_settings) > 0
        assert "sensitivity" in input_settings
    
    def test_change_callbacks(self, tmp_path):
        """Test configuration change callbacks."""
        config = UnifiedConfigManager(str(tmp_path))
        changes = []
        
        def callback(key, old_value, new_value):
            changes.append((key, old_value, new_value))
        
        config.register_change_callback("master_volume", callback)
        
        # Make a change
        config.set("master_volume", 0.7)
        
        assert len(changes) == 1
        assert changes[0][0] == "master_volume"
        assert changes[0][2] == 0.7
    
    def test_file_loading(self, tmp_path):
        """Test loading configuration from files."""
        # Create test config files
        settings_file = tmp_path / "game_settings.json"
        controls_file = tmp_path / "game_controls.json"
        
        settings_data = {
            "master_volume": 0.8,
            "brightness": 0.9,
            "vsync": False
        }
        
        controls_data = {
            "move_up": 1073741906,
            "action": 32
        }
        
        with open(settings_file, "w") as f:
            json.dump(settings_data, f)
        
        with open(controls_file, "w") as f:
            json.dump(controls_data, f)
        
        # Load configuration
        config = UnifiedConfigManager(str(tmp_path))
        
        # Check that values were loaded
        assert config.get("master_volume") == 0.8
        assert config.get("brightness") == 0.9
        assert config.get("vsync") == False
        assert config.get("move_up") == 1073741906
        assert config.get("action") == 32
    
    def test_file_saving(self, tmp_path):
        """Test saving configuration to files."""
        config = UnifiedConfigManager(str(tmp_path))
        
        # Set some values
        config.set("master_volume", 0.7)
        config.set("brightness", 0.8)
        config.set("move_up", 1073741906)
        
        # Save all files
        config.save_all()
        
        # Check that files were created
        settings_file = tmp_path / "game_settings.json"
        controls_file = tmp_path / "game_controls.json"
        
        assert settings_file.exists()
        assert controls_file.exists()
        
        # Check file contents
        with open(settings_file, "r") as f:
            settings_data = json.load(f)
            assert settings_data["master_volume"] == 0.7
            assert settings_data["brightness"] == 0.8
        
        with open(controls_file, "r") as f:
            controls_data = json.load(f)
            assert controls_data["move_up"] == 1073741906


class TestConfigServiceCompat:
    """Test the ConfigService compatibility layer."""
    
    def test_backward_compatibility(self, tmp_path):
        """Test that ConfigServiceCompat maintains the same interface."""
        config_path = str(tmp_path / "game_settings.json")
        
        # Create a test settings file
        settings_data = {"master_volume": 0.8, "brightness": 0.9}
        with open(config_path, "w") as f:
            json.dump(settings_data, f)
        
        # Use the compatibility layer
        config = ConfigServiceCompat(config_path)
        
        # Test the same interface as the original ConfigService
        assert config.config_path == config_path
        assert config.settings is not None
        
        # Test get method
        assert config.get("master_volume") == 0.8
        assert config.get("brightness") == 0.9
        assert config.get("nonexistent", "default") == "default"
        
        # Test set method
        assert config.set("ui_scale", 1.2) == True
        assert config.get("ui_scale") == 1.2
        
        # Test update method
        updates = {"vsync": False, "fullscreen": True}
        result = config.update(updates)
        assert config.get("vsync") == False
        assert config.get("fullscreen") == True
    
    def test_settings_dict_access(self, tmp_path):
        """Test that the settings dict is accessible for backward compatibility."""
        config = ConfigServiceCompat(str(tmp_path / "game_settings.json"))
        
        # The settings dict should be accessible
        assert hasattr(config, "settings")
        assert isinstance(config.settings, dict)
        
        # Changes should be reflected in the settings dict
        config.set("master_volume", 0.7)
        assert config.settings["master_volume"] == 0.7


class TestControlsServiceCompat:
    """Test the ControlsService compatibility layer."""
    
    def test_backward_compatibility(self, tmp_path):
        """Test that ControlsServiceCompat maintains the same interface."""
        controls_path = str(tmp_path / "game_controls.json")
        
        # Create a test controls file
        controls_data = {"move_up": 1073741906, "action": 32}
        with open(controls_path, "w") as f:
            json.dump(controls_data, f)
        
        # Use the compatibility layer
        controls = ControlsServiceCompat(controls_path)
        
        # Test the same interface as the original ControlsService
        assert controls.controls_path == controls_path
        assert controls.bindings is not None
        
        # Test get method
        assert controls.get("move_up") == 1073741906
        assert controls.get("action") == 32
        assert controls.get("nonexistent", 0) == 0
        
        # Test set method
        assert controls.set("move_down", 1073741905) == True
        assert controls.get("move_down") == 1073741905
        
        # Test update method
        updates = {"move_left": 1073741904, "move_right": 1073741903}
        result = controls.update(updates)
        assert controls.get("move_left") == 1073741904
        assert controls.get("move_right") == 1073741903
    
    def test_bindings_dict_access(self, tmp_path):
        """Test that the bindings dict is accessible for backward compatibility."""
        controls = ControlsServiceCompat(str(tmp_path / "game_controls.json"))
        
        # The bindings dict should be accessible
        assert hasattr(controls, "bindings")
        assert isinstance(controls.bindings, dict)
        
        # Changes should be reflected in the bindings dict
        controls.set("move_up", 1073741906)
        assert controls.bindings["move_up"] == 1073741906


class TestIntegration:
    """Integration tests for the unified configuration system."""
    
    def test_full_configuration_cycle(self, tmp_path):
        """Test a complete configuration cycle: load, modify, save, reload."""
        # Create initial config files
        settings_file = tmp_path / "game_settings.json"
        controls_file = tmp_path / "game_controls.json"
        
        initial_settings = {
            "master_volume": 0.6,
            "brightness": 1.0,
            "vsync": True
        }
        
        initial_controls = {
            "move_up": 1073741906,
            "action": 32
        }
        
        with open(settings_file, "w") as f:
            json.dump(initial_settings, f)
        
        with open(controls_file, "w") as f:
            json.dump(initial_controls, f)
        
        # Load configuration
        config = UnifiedConfigManager(str(tmp_path))
        
        # Verify initial values
        assert config.get("master_volume") == 0.6
        assert config.get("brightness") == 1.0
        assert config.get("vsync") == True
        assert config.get("move_up") == 1073741906
        assert config.get("action") == 32
        
        # Modify values
        config.set("master_volume", 0.8)
        config.set("brightness", 0.9)
        config.set("vsync", False)
        config.set("move_up", 1073741905)  # Different key
        
        # Save all changes
        config.save_all()
        
        # Create a new config manager to test reloading
        config2 = UnifiedConfigManager(str(tmp_path))
        
        # Verify that changes were persisted
        assert config2.get("master_volume") == 0.8
        assert config2.get("brightness") == 0.9
        assert config2.get("vsync") == False
        assert config2.get("move_up") == 1073741905
    
    def test_compatibility_layer_integration(self, tmp_path):
        """Test that the compatibility layer works with the unified system."""
        # Create test files
        settings_file = tmp_path / "game_settings.json"
        controls_file = tmp_path / "game_controls.json"
        
        with open(settings_file, "w") as f:
            json.dump({"master_volume": 0.7}, f)
        
        with open(controls_file, "w") as f:
            json.dump({"move_up": 1073741906}, f)
        
        # Use compatibility layers
        config = ConfigServiceCompat(str(settings_file))
        controls = ControlsServiceCompat(str(controls_file))
        
        # Test that they work together
        assert config.get("master_volume") == 0.7
        assert controls.get("move_up") == 1073741906
        
        # Test that changes are reflected in both systems
        config.set("brightness", 0.8)
        controls.set("action", 32)
        
        # Verify changes
        assert config.get("brightness") == 0.8
        assert controls.get("action") == 32
        
        # Test that the unified config underneath has the changes
        assert config.unified_config.get("brightness") == 0.8
        assert controls.unified_config.get("action") == 32


if __name__ == "__main__":
    pytest.main([__file__]) 