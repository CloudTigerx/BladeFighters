"""
Integration Tests for Audio State Management
Tests the integration between AudioSystem, AudioStateManager, and GameStateManager.
"""

import pytest
import pygame
from unittest.mock import Mock, patch
from typing import Dict, Any

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from modules.game_state_module.game_state_manager import GameStateManager
from modules.game_state_module.state_schema import GameState, AudioState
from modules.audio_module.audio_state_manager import AudioStateManager
from modules.audio_module.audio_system import AudioSystem
from modules.settings_module.audio_settings_integration import AudioSettingsIntegration


class TestAudioStateIntegration:
    """Test audio state integration with the unified state management system."""
    
    @pytest.fixture
    def state_manager(self):
        """Create a game state manager for testing."""
        return GameStateManager()
    
    @pytest.fixture
    def audio_state_manager(self, state_manager):
        """Create an audio state manager for testing."""
        return AudioStateManager(state_manager)
    
    @pytest.fixture
    def audio_system(self, state_manager):
        """Create an audio system with state manager integration."""
        with patch('pygame.mixer.Sound'):
            return AudioSystem(state_manager=state_manager)
    
    @pytest.fixture
    def settings_integration(self, state_manager, audio_state_manager):
        """Create an audio settings integration for testing."""
        return AudioSettingsIntegration(state_manager, audio_state_manager)
    
    def test_audio_state_manager_initialization(self, audio_state_manager):
        """Test that AudioStateManager initializes correctly."""
        assert audio_state_manager.state_manager is not None
        assert audio_state_manager.logger is not None
    
    def test_audio_state_defaults(self, audio_state_manager):
        """Test that audio state has correct default values."""
        assert audio_state_manager.get_master_volume() == 0.6
        assert audio_state_manager.get_music_volume() == 0.5
        assert audio_state_manager.get_sfx_volume() == 0.7
        assert audio_state_manager.is_music_enabled() == True
        assert audio_state_manager.is_sfx_enabled() == True
        assert audio_state_manager.get_current_music() is None
        assert audio_state_manager.is_music_playing() == False
        assert audio_state_manager.is_mp3_player_visible() == False
    
    def test_master_volume_setting(self, audio_state_manager):
        """Test setting and getting master volume."""
        # Test valid volume
        success = audio_state_manager.set_master_volume(0.8, "test")
        assert success == True
        assert audio_state_manager.get_master_volume() == 0.8
        
        # Test volume in state manager
        assert audio_state_manager.state_manager.get("audio.master_volume") == 0.8
    
    def test_music_volume_setting(self, audio_state_manager):
        """Test setting and getting music volume."""
        success = audio_state_manager.set_music_volume(0.3, "test")
        assert success == True
        assert audio_state_manager.get_music_volume() == 0.3
        
        # Test volume in state manager
        assert audio_state_manager.state_manager.get("audio.music_volume") == 0.3
    
    def test_sfx_volume_setting(self, audio_state_manager):
        """Test setting and getting sound effects volume."""
        success = audio_state_manager.set_sfx_volume(0.9, "test")
        assert success == True
        assert audio_state_manager.get_sfx_volume() == 0.9
        
        # Test volume in state manager
        assert audio_state_manager.state_manager.get("audio.sfx_volume") == 0.9
    
    def test_music_enabled_setting(self, audio_state_manager):
        """Test enabling and disabling music."""
        # Test disable
        success = audio_state_manager.set_music_enabled(False, "test")
        assert success == True
        assert audio_state_manager.is_music_enabled() == False
        
        # Test enable
        success = audio_state_manager.set_music_enabled(True, "test")
        assert success == True
        assert audio_state_manager.is_music_enabled() == True
    
    def test_sfx_enabled_setting(self, audio_state_manager):
        """Test enabling and disabling sound effects."""
        # Test disable
        success = audio_state_manager.set_sfx_enabled(False, "test")
        assert success == True
        assert audio_state_manager.is_sfx_enabled() == False
        
        # Test enable
        success = audio_state_manager.set_sfx_enabled(True, "test")
        assert success == True
        assert audio_state_manager.is_sfx_enabled() == True
    
    def test_current_music_setting(self, audio_state_manager):
        """Test setting and getting current music."""
        success = audio_state_manager.set_current_music("test_track.mp3", "test")
        assert success == True
        assert audio_state_manager.get_current_music() == "test_track.mp3"
        
        # Test clearing music
        success = audio_state_manager.set_current_music(None, "test")
        assert success == True
        assert audio_state_manager.get_current_music() is None
    
    def test_music_playing_setting(self, audio_state_manager):
        """Test setting and getting music playing state."""
        success = audio_state_manager.set_music_playing(True, "test")
        assert success == True
        assert audio_state_manager.is_music_playing() == True
        
        success = audio_state_manager.set_music_playing(False, "test")
        assert success == True
        assert audio_state_manager.is_music_playing() == False
    
    def test_mp3_player_visibility_setting(self, audio_state_manager):
        """Test setting and getting MP3 player visibility."""
        success = audio_state_manager.set_mp3_player_visible(True, "test")
        assert success == True
        assert audio_state_manager.is_mp3_player_visible() == True
        
        success = audio_state_manager.set_mp3_player_visible(False, "test")
        assert success == True
        assert audio_state_manager.is_mp3_player_visible() == False
    
    def test_audio_system_integration(self, audio_system):
        """Test that AudioSystem integrates correctly with state manager."""
        assert audio_system.state_manager is not None
        assert audio_system.audio_state_manager is not None
        
        # Test convenience methods
        success = audio_system.set_master_volume(0.7)
        assert success == True
        assert audio_system.audio_state_manager.get_master_volume() == 0.7
    
    def test_audio_system_state_sync(self, audio_system):
        """Test that AudioSystem syncs state correctly."""
        # Set volume through state manager
        audio_system.audio_state_manager.set_master_volume(0.8, "test")
        
        # Verify sync method exists
        assert hasattr(audio_system, '_sync_from_state')
        assert callable(audio_system._sync_from_state)
    
    def test_settings_integration_callbacks(self, settings_integration):
        """Test that settings integration provides correct callbacks."""
        callbacks = settings_integration.get_audio_settings_callbacks()
        
        expected_callbacks = [
            "master_volume", "music_volume", "sfx_volume", 
            "music_enabled", "sfx_enabled"
        ]
        
        for callback_name in expected_callbacks:
            assert callback_name in callbacks
            assert callable(callbacks[callback_name])
    
    def test_settings_integration_volume_changes(self, settings_integration):
        """Test that settings integration handles volume changes correctly."""
        callbacks = settings_integration.get_audio_settings_callbacks()
        
        # Test master volume callback
        success = callbacks["master_volume"](0.75)
        assert success == True
        assert settings_integration.audio_state_manager.get_master_volume() == 0.75
        
        # Test music volume callback
        success = callbacks["music_volume"](0.4)
        assert success == True
        assert settings_integration.audio_state_manager.get_music_volume() == 0.4
    
    def test_settings_integration_enabled_changes(self, settings_integration):
        """Test that settings integration handles enabled/disabled changes correctly."""
        callbacks = settings_integration.get_audio_settings_callbacks()
        
        # Test music enabled callback
        success = callbacks["music_enabled"](False)
        assert success == True
        assert settings_integration.audio_state_manager.is_music_enabled() == False
        
        # Test SFX enabled callback
        success = callbacks["sfx_enabled"](False)
        assert success == True
        assert settings_integration.audio_state_manager.is_sfx_enabled() == False
    
    def test_settings_sync(self, settings_integration):
        """Test syncing settings to state manager."""
        test_settings = {
            "master_volume": 0.8,
            "music_volume": 0.6
        }
        
        settings_integration.sync_settings_to_state(test_settings)
        
        assert settings_integration.audio_state_manager.get_master_volume() == 0.8
        assert settings_integration.audio_state_manager.get_music_volume() == 0.6
    
    def test_get_current_settings(self, settings_integration):
        """Test getting current settings from state manager."""
        # Set some values
        settings_integration.audio_state_manager.set_master_volume(0.9, "test")
        settings_integration.audio_state_manager.set_music_volume(0.7, "test")
        settings_integration.audio_state_manager.set_sfx_volume(0.8, "test")
        
        current_settings = settings_integration.get_current_settings()
        
        assert current_settings["master_volume"] == 0.9
        assert current_settings["music_volume"] == 0.7
        assert current_settings["sfx_volume"] == 0.8
        assert "music_enabled" in current_settings
        assert "sfx_enabled" in current_settings
    
    def test_state_summary(self, audio_state_manager):
        """Test getting audio state summary."""
        summary = audio_state_manager.get_state_summary()
        
        expected_keys = [
            "master_volume", "music_volume", "sfx_volume",
            "music_enabled", "sfx_enabled", "current_music",
            "music_playing", "mp3_player_visible"
        ]
        
        for key in expected_keys:
            assert key in summary
    
    def test_snapshot_creation(self, audio_state_manager):
        """Test creating audio state snapshots."""
        # Set some values
        audio_state_manager.set_master_volume(0.8, "test")
        audio_state_manager.set_music_volume(0.6, "test")
        
        # Create snapshot
        audio_state_manager.create_snapshot("Test audio state")
        
        # Verify snapshot was created in history
        latest_snapshot = audio_state_manager.state_manager.history.get_latest_snapshot()
        assert latest_snapshot is not None
        assert "Test audio state" in latest_snapshot.description
    
    def test_state_change_tracking(self, audio_state_manager):
        """Test that state changes are properly tracked."""
        # Make a change
        audio_state_manager.set_master_volume(0.7, "test")
        
        # Check that change was recorded
        changes = audio_state_manager.state_manager.history.get_changes_for_field("audio.master_volume")
        assert len(changes) >= 1
        
        latest_change = changes[-1]
        assert latest_change.field_path == "audio.master_volume"
        assert latest_change.old_value == 0.6  # Default value
        assert latest_change.new_value == 0.7
        assert latest_change.source == "test"
    
    def test_audio_system_without_state_manager(self):
        """Test that AudioSystem works without state manager (backward compatibility)."""
        with patch('pygame.mixer.Sound'):
            audio_system = AudioSystem()  # No state_manager parameter
        
        assert audio_system.state_manager is None
        assert audio_system.audio_state_manager is None
        
        # Convenience methods should return False when no state manager
        assert audio_system.set_master_volume(0.8) == False
        assert audio_system.get_audio_state_summary() == {} 