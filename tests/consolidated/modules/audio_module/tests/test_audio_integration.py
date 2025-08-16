"""
Audio Integration Tests
Tests for the AudioStateIntegrator and audio system state management integration.
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

from modules.game_state_module.game_state_manager import GameStateManager
from modules.audio_module.audio_integration import AudioStateIntegrator, AudioStateMapping


class MockAudioSystem:
    """Mock audio system for testing."""
    
    def __init__(self):
        # Core audio state
        self.master_volume = 0.7
        self.music_volume = 0.6
        self.sfx_volume = 0.8
        self.music_enabled = True
        self.sfx_enabled = True
        
        # MP3 player state
        self.mp3_player_visible = False
        self.current_music = None
        self.music_playing = False
        
        # Audio system state
        self.auto_play_music = True
        self.fade_transitions = True
        
        # Methods
        self.set_master_volume = Mock()
        self.set_music_volume = Mock()
        self.set_sfx_volume = Mock()
        self.play_sound = Mock()
        self.play_music = Mock()
        self.stop_music = Mock()
    
    def get_audio_state(self):
        """Get current audio state."""
        return {
            "master_volume": self.master_volume,
            "music_volume": self.music_volume,
            "sfx_volume": self.sfx_volume,
            "music_enabled": self.music_enabled,
            "sfx_enabled": self.sfx_enabled,
            "mp3_player_visible": self.mp3_player_visible,
            "current_music": self.current_music,
            "music_playing": self.music_playing,
            "auto_play_music": self.auto_play_music,
            "fade_transitions": self.fade_transitions,
        }


class TestAudioStateMapping:
    """Test the AudioStateMapping dataclass."""
    
    def test_audio_state_mapping_creation(self):
        """Test creating an AudioStateMapping."""
        mapping = AudioStateMapping(
            system_attr="master_volume",
            state_path="audio.master_volume",
            description="Master volume level",
            default_value=0.7
        )
        
        assert mapping.system_attr == "master_volume"
        assert mapping.state_path == "audio.master_volume"
        assert mapping.description == "Master volume level"
        assert mapping.default_value == 0.7
    
    def test_audio_state_mapping_defaults(self):
        """Test AudioStateMapping with default values."""
        mapping = AudioStateMapping(
            system_attr="music_enabled",
            state_path="audio.music_enabled",
            description="Music enabled status"
        )
        
        assert mapping.system_attr == "music_enabled"
        assert mapping.state_path == "audio.music_enabled"
        assert mapping.description == "Music enabled status"
        assert mapping.default_value is None


class TestAudioStateIntegrator:
    """Test the AudioStateIntegrator class."""
    
    @pytest.fixture
    def state_manager(self):
        """Create a fresh state manager for each test."""
        return GameStateManager()
    
    @pytest.fixture
    def audio_system(self):
        """Create a mock audio system for each test."""
        return MockAudioSystem()
    
    @pytest.fixture
    def integrator(self, state_manager, audio_system):
        """Create an audio state integrator for each test."""
        return AudioStateIntegrator(state_manager, audio_system)
    
    def test_initialization(self, integrator, state_manager, audio_system):
        """Test that the integrator initializes correctly."""
        assert integrator.state_manager == state_manager
        assert integrator.audio_system == audio_system
        assert integrator.integration_active == False
        assert len(integrator.state_mappings) > 0
        assert integrator.sync_interval == 0.016  # 60fps
    
    def test_create_state_mappings(self, integrator):
        """Test that state mappings are created correctly."""
        mappings = integrator.state_mappings
        
        # Check that all expected mappings exist
        mapping_paths = [m.state_path for m in mappings]
        
        expected_paths = [
            "audio.master_volume",
            "audio.music_volume", 
            "audio.sfx_volume",
            "audio.music_enabled",
            "audio.sfx_enabled",
            "audio.mp3_player_visible",
            "audio.current_music",
            "audio.music_playing",
            "audio.auto_play_music",
            "audio.fade_transitions"
        ]
        
        for path in expected_paths:
            assert path in mapping_paths
    
    def test_start_integration(self, integrator):
        """Test starting the integration process."""
        integrator.start_integration()
        assert integrator.integration_active == True
    
    def test_stop_integration(self, integrator):
        """Test stopping the integration process."""
        integrator.start_integration()
        integrator.stop_integration()
        assert integrator.integration_active == False
    
    def test_initial_sync(self, integrator, state_manager, audio_system):
        """Test initial sync of audio system state."""
        integrator.start_integration()
        
        # Check that state was synced
        assert state_manager.get("audio.master_volume") == 0.7
        assert state_manager.get("audio.music_volume") == 0.6
        assert state_manager.get("audio.sfx_volume") == 0.8
        assert state_manager.get("audio.music_enabled") == True
        assert state_manager.get("audio.sfx_enabled") == True
    
    def test_sync_to_state_manager(self, integrator, state_manager, audio_system):
        """Test syncing audio system state to state manager."""
        integrator.start_integration()
        
        # Change values in audio system
        audio_system.master_volume = 0.9
        audio_system.music_volume = 0.5
        
        # Sync to state manager
        integrator.sync_to_state_manager()
        
        # Check that values were synced
        assert state_manager.get("audio.master_volume") == 0.9
        assert state_manager.get("audio.music_volume") == 0.5
    
    def test_sync_from_state_manager(self, integrator, state_manager, audio_system):
        """Test syncing state manager values to audio system."""
        integrator.start_integration()
        
        # Set values in state manager
        state_manager.set("audio.master_volume", 0.8, source="test")
        state_manager.set("audio.music_enabled", False, source="test")
        
        # Sync from state manager
        integrator.sync_from_state_manager()
        
        # Check that values were synced to audio system
        assert audio_system.master_volume == 0.8
        assert audio_system.music_enabled == False
    
    def test_set_master_volume(self, integrator, state_manager):
        """Test setting master volume."""
        integrator.set_master_volume(0.8)
        
        assert state_manager.get("audio.master_volume") == 0.8
        integrator.audio_system.set_master_volume.assert_called_once_with(0.8)
    
    def test_get_master_volume(self, integrator, state_manager):
        """Test getting master volume."""
        state_manager.set("audio.master_volume", 0.9, source="test")
        
        volume = integrator.get_master_volume()
        assert volume == 0.9
    
    def test_get_master_volume_default(self, integrator):
        """Test getting master volume with default value."""
        volume = integrator.get_master_volume()
        assert volume == 0.7  # Default value
    
    def test_set_music_volume(self, integrator, state_manager):
        """Test setting music volume."""
        integrator.set_music_volume(0.5)
        
        assert state_manager.get("audio.music_volume") == 0.5
        integrator.audio_system.set_music_volume.assert_called_once_with(0.5)
    
    def test_get_music_volume(self, integrator, state_manager):
        """Test getting music volume."""
        state_manager.set("audio.music_volume", 0.4, source="test")
        
        volume = integrator.get_music_volume()
        assert volume == 0.4
    
    def test_set_sfx_volume(self, integrator, state_manager):
        """Test setting SFX volume."""
        integrator.set_sfx_volume(0.9)
        
        assert state_manager.get("audio.sfx_volume") == 0.9
        integrator.audio_system.set_sfx_volume.assert_called_once_with(0.9)
    
    def test_get_sfx_volume(self, integrator, state_manager):
        """Test getting SFX volume."""
        state_manager.set("audio.sfx_volume", 0.3, source="test")
        
        volume = integrator.get_sfx_volume()
        assert volume == 0.3
    
    def test_set_music_enabled(self, integrator, state_manager):
        """Test setting music enabled status."""
        integrator.set_music_enabled(False)
        
        assert state_manager.get("audio.music_enabled") == False
    
    def test_is_music_enabled(self, integrator, state_manager):
        """Test checking if music is enabled."""
        state_manager.set("audio.music_enabled", False, source="test")
        
        enabled = integrator.is_music_enabled()
        assert enabled == False
    
    def test_set_sfx_enabled(self, integrator, state_manager):
        """Test setting SFX enabled status."""
        integrator.set_sfx_enabled(False)
        
        assert state_manager.get("audio.sfx_enabled") == False
    
    def test_is_sfx_enabled(self, integrator, state_manager):
        """Test checking if SFX is enabled."""
        state_manager.set("audio.sfx_enabled", False, source="test")
        
        enabled = integrator.is_sfx_enabled()
        assert enabled == False
    
    def test_set_mp3_player_visible(self, integrator, state_manager):
        """Test setting MP3 player visibility."""
        integrator.set_mp3_player_visible(True)
        
        assert state_manager.get("audio.mp3_player_visible") == True
    
    def test_is_mp3_player_visible(self, integrator, state_manager):
        """Test checking if MP3 player is visible."""
        state_manager.set("audio.mp3_player_visible", True, source="test")
        
        visible = integrator.is_mp3_player_visible()
        assert visible == True
    
    def test_set_current_music(self, integrator, state_manager):
        """Test setting current music track."""
        integrator.set_current_music("test_song.mp3")
        
        assert state_manager.get("audio.current_music") == "test_song.mp3"
    
    def test_get_current_music(self, integrator, state_manager):
        """Test getting current music track."""
        state_manager.set("audio.current_music", "background.mp3", source="test")
        
        music = integrator.get_current_music()
        assert music == "background.mp3"
    
    def test_set_music_playing(self, integrator, state_manager):
        """Test setting music playing status."""
        integrator.set_music_playing(True)
        
        assert state_manager.get("audio.music_playing") == True
    
    def test_is_music_playing(self, integrator, state_manager):
        """Test checking if music is playing."""
        state_manager.set("audio.music_playing", True, source="test")
        
        playing = integrator.is_music_playing()
        assert playing == True
    
    def test_play_sound_enabled(self, integrator, state_manager):
        """Test playing sound when SFX is enabled."""
        integrator.set_sfx_enabled(True)
        
        integrator.play_sound("click")
        
        integrator.audio_system.play_sound.assert_called_once_with("click")
        assert state_manager.get("audio.sounds_played") == 1
    
    def test_play_sound_disabled(self, integrator, state_manager):
        """Test playing sound when SFX is disabled."""
        integrator.set_sfx_enabled(False)
        
        integrator.play_sound("click")
        
        # Should not play sound when disabled
        integrator.audio_system.play_sound.assert_not_called()
        assert state_manager.get("audio.sounds_played") == 0
    
    def test_play_music_enabled(self, integrator, state_manager):
        """Test playing music when music is enabled."""
        integrator.set_music_enabled(True)
        
        integrator.play_music("background.mp3")
        
        integrator.audio_system.play_music.assert_called_once_with("background.mp3")
        assert state_manager.get("audio.current_music") == "background.mp3"
        assert state_manager.get("audio.music_playing") == True
        assert state_manager.get("audio.music_tracks_played") == 1
    
    def test_play_music_disabled(self, integrator, state_manager):
        """Test playing music when music is disabled."""
        integrator.set_music_enabled(False)
        
        integrator.play_music("background.mp3")
        
        # Should not play music when disabled
        integrator.audio_system.play_music.assert_not_called()
        assert state_manager.get("audio.music_tracks_played") == 0
    
    def test_reset_audio_state(self, integrator, state_manager):
        """Test resetting all audio state variables."""
        # Set some non-default values
        state_manager.set("audio.master_volume", 0.9, source="test")
        state_manager.set("audio.music_enabled", False, source="test")
        state_manager.set("audio.sounds_played", 10, source="test")
        
        integrator.reset_audio_state()
        
        # Check that values were reset to defaults
        assert state_manager.get("audio.master_volume") == 0.7
        assert state_manager.get("audio.music_volume") == 0.6
        assert state_manager.get("audio.sfx_volume") == 0.8
        assert state_manager.get("audio.music_enabled") == True
        assert state_manager.get("audio.sfx_enabled") == True
        assert state_manager.get("audio.sounds_played") == 0
        assert state_manager.get("audio.music_tracks_played") == 0
        assert state_manager.get("audio.volume_changes") == 0
    
    def test_register_state_callbacks(self, integrator, state_manager):
        """Test registering state change callbacks."""
        integrator.register_state_callbacks()
        
        # Check that callbacks were registered
        callbacks = state_manager._callbacks
        
        expected_fields = [
            "audio.master_volume",
            "audio.music_volume", 
            "audio.sfx_volume",
            "audio.music_enabled",
            "audio.sfx_enabled"
        ]
        
        for field in expected_fields:
            assert field in callbacks
            assert len(callbacks[field]) > 0
    
    def test_master_volume_callback(self, integrator, state_manager):
        """Test master volume change callback."""
        integrator.register_state_callbacks()
        
        # Trigger volume change
        state_manager.set("audio.master_volume", 0.8, source="test")
        
        # Check that audio system was updated
        integrator.audio_system.set_master_volume.assert_called_once_with(0.8)
        
        # Check that metrics were updated
        assert state_manager.get("audio.volume_changes") == 1
    
    def test_music_volume_callback(self, integrator, state_manager):
        """Test music volume change callback."""
        integrator.register_state_callbacks()
        
        # Trigger volume change
        state_manager.set("audio.music_volume", 0.5, source="test")
        
        # Check that audio system was updated
        integrator.audio_system.set_music_volume.assert_called_once_with(0.5)
    
    def test_sfx_volume_callback(self, integrator, state_manager):
        """Test SFX volume change callback."""
        integrator.register_state_callbacks()
        
        # Trigger volume change
        state_manager.set("audio.sfx_volume", 0.9, source="test")
        
        # Check that audio system was updated
        integrator.audio_system.set_sfx_volume.assert_called_once_with(0.9)
    
    def test_music_enabled_callback_stop_music(self, integrator, state_manager):
        """Test music enabled callback when stopping music."""
        integrator.register_state_callbacks()
        
        # Set music as playing
        state_manager.set("audio.music_playing", True, source="test")
        
        # Disable music
        state_manager.set("audio.music_enabled", False, source="test")
        
        # Check that music was stopped
        assert state_manager.get("audio.music_playing") == False
        integrator.audio_system.stop_music.assert_called_once()
    
    def test_get_audio_state_summary(self, integrator, state_manager):
        """Test getting audio state summary."""
        # Set some state values
        state_manager.set("audio.master_volume", 0.8, source="test")
        state_manager.set("audio.sounds_played", 5, source="test")
        state_manager.set("audio.music_tracks_played", 3, source="test")
        state_manager.set("audio.volume_changes", 10, source="test")
        
        summary = integrator.get_audio_state_summary()
        
        expected_keys = [
            "master_volume", "music_volume", "sfx_volume",
            "music_enabled", "sfx_enabled", "mp3_player_visible",
            "current_music", "music_playing", "sounds_played",
            "music_tracks_played", "volume_changes"
        ]
        
        for key in expected_keys:
            assert key in summary
        
        assert summary["master_volume"] == 0.8
        assert summary["sounds_played"] == 5
        assert summary["music_tracks_played"] == 3
        assert summary["volume_changes"] == 10
    
    def test_sync_with_settings_module(self, integrator, state_manager):
        """Test syncing with settings module."""
        settings = {
            "master_volume": 0.9,
            "music_volume": 0.4,
            "sfx_volume": 0.7
        }
        
        integrator.sync_with_settings_module(settings)
        
        assert state_manager.get("audio.master_volume") == 0.9
        assert state_manager.get("audio.music_volume") == 0.4
        assert state_manager.get("audio.sfx_volume") == 0.7
    
    def test_get_settings_dict(self, integrator, state_manager):
        """Test getting settings dictionary."""
        # Set some values
        state_manager.set("audio.master_volume", 0.8, source="test")
        state_manager.set("audio.music_volume", 0.5, source="test")
        state_manager.set("audio.sfx_volume", 0.9, source="test")
        
        settings = integrator.get_settings_dict()
        
        assert settings["master_volume"] == 0.8
        assert settings["music_volume"] == 0.5
        assert settings["sfx_volume"] == 0.9
    
    def test_sync_throttling(self, integrator, state_manager, audio_system):
        """Test that sync operations are throttled."""
        integrator.start_integration()
        
        # Change audio system values
        audio_system.master_volume = 0.9
        
        # First sync should work
        integrator.sync_to_state_manager()
        assert state_manager.get("audio.master_volume") == 0.9
        
        # Change again immediately
        audio_system.master_volume = 0.8
        
        # Second sync should be throttled
        integrator.sync_to_state_manager()
        assert state_manager.get("audio.master_volume") == 0.9  # Should not change
    
    def test_sync_integration_inactive(self, integrator, state_manager, audio_system):
        """Test that sync operations don't work when integration is inactive."""
        # Don't start integration
        assert integrator.integration_active == False
        
        # Change audio system values
        audio_system.master_volume = 0.9
        
        # Sync should not work
        integrator.sync_to_state_manager()
        assert state_manager.get("audio.master_volume") != 0.9  # Should not be synced


class TestIntegrationWithRealStateManager:
    """Test integration with real GameStateManager."""
    
    @pytest.fixture
    def state_manager(self):
        """Create a real state manager for integration testing."""
        return GameStateManager()
    
    @pytest.fixture
    def audio_system(self):
        """Create a mock audio system."""
        return MockAudioSystem()
    
    @pytest.fixture
    def integrator(self, state_manager, audio_system):
        """Create an integrator with real state manager."""
        return AudioStateIntegrator(state_manager, audio_system)
    
    def test_full_integration_workflow(self, integrator, state_manager, audio_system):
        """Test a complete integration workflow."""
        # Start integration
        integrator.start_integration()
        integrator.register_state_callbacks()
        
        # Set volume through integrator
        integrator.set_master_volume(0.8)
        integrator.set_music_volume(0.6)
        integrator.set_sfx_volume(0.9)
        
        # Check state manager
        assert state_manager.get("audio.master_volume") == 0.8
        assert state_manager.get("audio.music_volume") == 0.6
        assert state_manager.get("audio.sfx_volume") == 0.9
        
        # Check audio system was updated
        audio_system.set_master_volume.assert_called_with(0.8)
        audio_system.set_music_volume.assert_called_with(0.6)
        audio_system.set_sfx_volume.assert_called_with(0.9)
        
        # Play audio
        integrator.play_sound("click")
        integrator.play_music("background.mp3")
        
        # Check metrics
        assert state_manager.get("audio.sounds_played") == 1
        assert state_manager.get("audio.music_tracks_played") == 1
        assert state_manager.get("audio.current_music") == "background.mp3"
        assert state_manager.get("audio.music_playing") == True
        
        # Check audio system methods were called
        audio_system.play_sound.assert_called_with("click")
        audio_system.play_music.assert_called_with("background.mp3")
    
    def test_state_persistence(self, integrator, state_manager):
        """Test that state persists across operations."""
        integrator.start_integration()
        
        # Set some state
        integrator.set_master_volume(0.8)
        integrator.set_music_enabled(False)
        integrator.play_sound("click")
        
        # Check state persists
        assert state_manager.get("audio.master_volume") == 0.8
        assert state_manager.get("audio.music_enabled") == False
        assert state_manager.get("audio.sounds_played") == 1
        
        # Reset state
        integrator.reset_audio_state()
        
        # Check state was reset
        assert state_manager.get("audio.master_volume") == 0.7  # Default
        assert state_manager.get("audio.music_enabled") == True  # Default
        assert state_manager.get("audio.sounds_played") == 0  # Reset
    
    def test_settings_coordination(self, integrator, state_manager):
        """Test coordination with settings module."""
        integrator.start_integration()
        
        # Simulate settings from settings module
        settings = {
            "master_volume": 0.9,
            "music_volume": 0.4,
            "sfx_volume": 0.7
        }
        
        integrator.sync_with_settings_module(settings)
        
        # Check state was updated
        assert state_manager.get("audio.master_volume") == 0.9
        assert state_manager.get("audio.music_volume") == 0.4
        assert state_manager.get("audio.sfx_volume") == 0.7
        
        # Get settings back
        settings_dict = integrator.get_settings_dict()
        
        assert settings_dict["master_volume"] == 0.9
        assert settings_dict["music_volume"] == 0.4
        assert settings_dict["sfx_volume"] == 0.7


class TestErrorHandling:
    """Test error handling in audio integration."""
    
    @pytest.fixture
    def state_manager(self):
        return GameStateManager()
    
    @pytest.fixture
    def audio_system(self):
        return MockAudioSystem()
    
    @pytest.fixture
    def integrator(self, state_manager, audio_system):
        return AudioStateIntegrator(state_manager, audio_system)
    
    def test_initial_sync_with_missing_attributes(self, integrator, state_manager):
        """Test initial sync when audio system is missing attributes."""
        # Create audio system without some attributes
        audio_system = MockAudioSystem()
        delattr(audio_system, 'master_volume')
        
        integrator = AudioStateIntegrator(state_manager, audio_system)
        
        # Should not raise exception
        integrator.start_integration()
        
        # Missing attributes should not be synced
        assert state_manager.get("audio.master_volume") != 0.7
    
    def test_sync_with_invalid_values(self, integrator, state_manager):
        """Test sync with invalid values."""
        integrator.start_integration()
        
        # Set invalid values in state manager
        state_manager.set("audio.master_volume", "invalid", source="test")
        state_manager.set("audio.music_enabled", "not_boolean", source="test")
        
        # Should not raise exception
        integrator.sync_from_state_manager()
    
    def test_audio_system_method_errors(self, integrator, state_manager):
        """Test handling of audio system method errors."""
        integrator.start_integration()
        
        # Make audio system methods raise exceptions
        integrator.audio_system.set_master_volume.side_effect = Exception("Audio error")
        
        # Should not raise exception
        integrator.set_master_volume(0.8)
        
        # State should still be updated
        assert state_manager.get("audio.master_volume") == 0.8


class TestPerformance:
    """Test performance characteristics of audio integration."""
    
    @pytest.fixture
    def state_manager(self):
        return GameStateManager()
    
    @pytest.fixture
    def audio_system(self):
        return MockAudioSystem()
    
    @pytest.fixture
    def integrator(self, state_manager, audio_system):
        return AudioStateIntegrator(state_manager, audio_system)
    
    def test_volume_change_performance(self, integrator):
        """Test performance of volume changes."""
        integrator.start_integration()
        
        start_time = time.time()
        
        # Perform multiple volume changes
        for i in range(100):
            integrator.set_master_volume(i / 100.0)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete in under 1 second
        assert duration < 1.0
    
    def test_sync_performance(self, integrator, audio_system):
        """Test performance of sync operations."""
        integrator.start_integration()
        
        # Change audio system values
        audio_system.master_volume = 0.8
        audio_system.music_volume = 0.6
        
        start_time = time.time()
        
        # Perform sync
        integrator.sync_to_state_manager()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete quickly
        assert duration < 0.01  # 10ms
    
    def test_state_summary_performance(self, integrator, state_manager):
        """Test performance of getting state summary."""
        integrator.start_integration()
        
        # Set some state
        for i in range(10):
            state_manager.set(f"audio.test_field_{i}", i, source="test")
        
        start_time = time.time()
        
        # Get state summary
        summary = integrator.get_audio_state_summary()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete quickly
        assert duration < 0.001  # 1ms
        assert isinstance(summary, dict)
