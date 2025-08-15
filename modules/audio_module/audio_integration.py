"""
Audio State Integration
Handles integration of audio system state with the unified GameStateManager.
This module provides a clean interface for migrating audio state variables.
"""

import time
from typing import Dict, Any, Optional, List, Tuple
import pygame
from dataclasses import dataclass

from ..game_state_module.game_state_manager import GameStateManager
from ..game_state_module.state_schema import GameState, AudioState
from ..logging_module.logger import get_logger


@dataclass
class AudioStateMapping:
    """Maps audio system variables to state manager paths."""
    system_attr: str
    state_path: str
    description: str
    default_value: Any = None


class AudioStateIntegrator:
    """
    Integrates audio system state with the unified GameStateManager.
    Provides methods to sync state between the audio system and state manager.
    """
    
    def __init__(self, state_manager: GameStateManager, audio_system):
        """Initialize the audio state integrator."""
        self.state_manager = state_manager
        self.audio_system = audio_system
        self.logger = get_logger(__name__)
        
        # Define state mappings
        self.state_mappings = self._create_state_mappings()
        
        # Track integration status
        self.integration_active = False
        self.last_sync_time = 0
        self.sync_interval = 0.016  # 60fps sync rate
        
        self.logger.info("AudioStateIntegrator initialized")
    
    def _create_state_mappings(self) -> List[AudioStateMapping]:
        """Create mappings between audio system variables and state manager paths."""
        return [
            # Volume state
            AudioStateMapping("master_volume", "audio.master_volume", "Master volume level"),
            AudioStateMapping("music_volume", "audio.music_volume", "Music volume level"),
            AudioStateMapping("sfx_volume", "audio.sfx_volume", "Sound effects volume level"),
            
            # Audio enable/disable state
            AudioStateMapping("music_enabled", "audio.music_enabled", "Music enabled status"),
            AudioStateMapping("sfx_enabled", "audio.sfx_enabled", "Sound effects enabled status"),
            
            # MP3 player state
            AudioStateMapping("mp3_player_visible", "audio.mp3_player_visible", "MP3 player visibility"),
            AudioStateMapping("current_music", "audio.current_music", "Current music track"),
            AudioStateMapping("music_playing", "audio.music_playing", "Music playing status"),
            
            # Audio system state
            AudioStateMapping("auto_play_music", "audio.auto_play_music", "Auto-play music on startup"),
            AudioStateMapping("fade_transitions", "audio.fade_transitions", "Volume fade transitions"),
        ]
    
    def start_integration(self):
        """Start the state integration process."""
        self.integration_active = True
        self._initial_sync()
        self.logger.info("Audio state integration started")
    
    def stop_integration(self):
        """Stop the state integration process."""
        self.integration_active = False
        self.logger.info("Audio state integration stopped")
    
    def _initial_sync(self):
        """Perform initial sync of all state variables."""
        for mapping in self.state_mappings:
            try:
                if hasattr(self.audio_system, mapping.system_attr):
                    value = getattr(self.audio_system, mapping.system_attr)
                    self.state_manager.set(
                        mapping.state_path, 
                        value, 
                        source="audio_integration",
                        description=f"Initial sync: {mapping.description}"
                    )
            except Exception as e:
                self.logger.warning(f"Failed to sync {mapping.system_attr}: {e}")
    
    def sync_to_state_manager(self):
        """Sync audio system state to the state manager."""
        if not self.integration_active:
            return
        
        current_time = time.time()
        if current_time - self.last_sync_time < self.sync_interval:
            return
        
        self.last_sync_time = current_time
        
        for mapping in self.state_mappings:
            try:
                if hasattr(self.audio_system, mapping.system_attr):
                    value = getattr(self.audio_system, mapping.system_attr)
                    current_state_value = self.state_manager.get(mapping.state_path)
                    
                    # Only update if value has changed
                    if value != current_state_value:
                        self.state_manager.set(
                            mapping.state_path,
                            value,
                            source="audio_system",
                            description=f"Sync: {mapping.description}"
                        )
            except Exception as e:
                self.logger.warning(f"Failed to sync {mapping.system_attr}: {e}")
    
    def sync_from_state_manager(self):
        """Sync state manager values back to the audio system."""
        if not self.integration_active:
            return
        
        for mapping in self.state_mappings:
            try:
                if hasattr(self.audio_system, mapping.system_attr):
                    state_value = self.state_manager.get(mapping.state_path)
                    if state_value is not None:
                        setattr(self.audio_system, mapping.system_attr, state_value)
            except Exception as e:
                self.logger.warning(f"Failed to sync from state manager: {mapping.system_attr}: {e}")
    
    def set_master_volume(self, volume: float):
        """Set the master volume level."""
        self.state_manager.set(
            "audio.master_volume",
            volume,
            source="audio_integration",
            description=f"Master volume set to {volume}"
        )
        # Also update the audio system directly for immediate effect
        if hasattr(self.audio_system, 'set_master_volume'):
            self.audio_system.set_master_volume(volume)
    
    def get_master_volume(self) -> float:
        """Get the current master volume level."""
        return self.state_manager.get("audio.master_volume", 0.7)
    
    def set_music_volume(self, volume: float):
        """Set the music volume level."""
        self.state_manager.set(
            "audio.music_volume",
            volume,
            source="audio_integration",
            description=f"Music volume set to {volume}"
        )
        # Also update the audio system directly for immediate effect
        if hasattr(self.audio_system, 'set_music_volume'):
            self.audio_system.set_music_volume(volume)
    
    def get_music_volume(self) -> float:
        """Get the current music volume level."""
        return self.state_manager.get("audio.music_volume", 0.6)
    
    def set_sfx_volume(self, volume: float):
        """Set the sound effects volume level."""
        self.state_manager.set(
            "audio.sfx_volume",
            volume,
            source="audio_integration",
            description=f"SFX volume set to {volume}"
        )
        # Also update the audio system directly for immediate effect
        if hasattr(self.audio_system, 'set_sfx_volume'):
            self.audio_system.set_sfx_volume(volume)
    
    def get_sfx_volume(self) -> float:
        """Get the current sound effects volume level."""
        return self.state_manager.get("audio.sfx_volume", 0.8)
    
    def set_music_enabled(self, enabled: bool):
        """Enable or disable music."""
        self.state_manager.set(
            "audio.music_enabled",
            enabled,
            source="audio_integration",
            description=f"Music {'enabled' if enabled else 'disabled'}"
        )
    
    def is_music_enabled(self) -> bool:
        """Check if music is enabled."""
        return self.state_manager.get("audio.music_enabled", True)
    
    def set_sfx_enabled(self, enabled: bool):
        """Enable or disable sound effects."""
        self.state_manager.set(
            "audio.sfx_enabled",
            enabled,
            source="audio_integration",
            description=f"SFX {'enabled' if enabled else 'disabled'}"
        )
    
    def is_sfx_enabled(self) -> bool:
        """Check if sound effects are enabled."""
        return self.state_manager.get("audio.sfx_enabled", True)
    
    def set_mp3_player_visible(self, visible: bool):
        """Set MP3 player visibility."""
        self.state_manager.set(
            "audio.mp3_player_visible",
            visible,
            source="audio_integration",
            description=f"MP3 player {'shown' if visible else 'hidden'}"
        )
    
    def is_mp3_player_visible(self) -> bool:
        """Check if MP3 player is visible."""
        return self.state_manager.get("audio.mp3_player_visible", False)
    
    def set_current_music(self, music_name: Optional[str]):
        """Set the current music track."""
        self.state_manager.set(
            "audio.current_music",
            music_name,
            source="audio_integration",
            description=f"Current music set to {music_name}"
        )
    
    def get_current_music(self) -> Optional[str]:
        """Get the current music track."""
        return self.state_manager.get("audio.current_music")
    
    def set_music_playing(self, playing: bool):
        """Set music playing status."""
        self.state_manager.set(
            "audio.music_playing",
            playing,
            source="audio_integration",
            description=f"Music {'started' if playing else 'stopped'}"
        )
    
    def is_music_playing(self) -> bool:
        """Check if music is currently playing."""
        return self.state_manager.get("audio.music_playing", False)
    
    def play_sound(self, sound_name: str):
        """Play a sound effect with state-aware volume."""
        if not self.is_sfx_enabled():
            return
        
        # Get current volume settings
        master_volume = self.get_master_volume()
        sfx_volume = self.get_sfx_volume()
        
        # Play sound through audio system
        if hasattr(self.audio_system, 'play_sound'):
            self.audio_system.play_sound(sound_name)
        
        # Update metrics
        self.state_manager.set(
            "audio.sounds_played",
            self.state_manager.get("audio.sounds_played", 0) + 1,
            source="audio_integration",
            description=f"Sound played: {sound_name}"
        )
    
    def play_music(self, music_name: str):
        """Play music with state-aware settings."""
        if not self.is_music_enabled():
            return
        
        # Set current music
        self.set_current_music(music_name)
        self.set_music_playing(True)
        
        # Play music through audio system
        if hasattr(self.audio_system, 'play_music'):
            self.audio_system.play_music(music_name)
        
        # Update metrics
        self.state_manager.set(
            "audio.music_tracks_played",
            self.state_manager.get("audio.music_tracks_played", 0) + 1,
            source="audio_integration",
            description=f"Music track played: {music_name}"
        )
    
    def reset_audio_state(self):
        """Reset all audio state variables to defaults."""
        reset_values = {
            "audio.master_volume": 0.7,
            "audio.music_volume": 0.6,
            "audio.sfx_volume": 0.8,
            "audio.music_enabled": True,
            "audio.sfx_enabled": True,
            "audio.mp3_player_visible": False,
            "audio.current_music": None,
            "audio.music_playing": False,
            "audio.auto_play_music": True,
            "audio.fade_transitions": True,
            "audio.sounds_played": 0,
            "audio.music_tracks_played": 0,
            "audio.volume_changes": 0,
        }
        
        for path, value in reset_values.items():
            self.state_manager.set(
                path,
                value,
                source="audio_integration",
                description="Audio state reset"
            )
        
        self.logger.info("Audio state reset")
    
    def register_state_callbacks(self):
        """Register callbacks for important state changes."""
        # Register callback for volume changes
        self.state_manager.register_callback(
            "audio.master_volume",
            self._on_master_volume_changed,
            "Handle master volume changes"
        )
        
        # Register callback for music volume changes
        self.state_manager.register_callback(
            "audio.music_volume",
            self._on_music_volume_changed,
            "Handle music volume changes"
        )
        
        # Register callback for SFX volume changes
        self.state_manager.register_callback(
            "audio.sfx_volume",
            self._on_sfx_volume_changed,
            "Handle SFX volume changes"
        )
        
        # Register callback for music enabled changes
        self.state_manager.register_callback(
            "audio.music_enabled",
            self._on_music_enabled_changed,
            "Handle music enabled changes"
        )
        
        # Register callback for SFX enabled changes
        self.state_manager.register_callback(
            "audio.sfx_enabled",
            self._on_sfx_enabled_changed,
            "Handle SFX enabled changes"
        )
    
    def _on_master_volume_changed(self, field_path: str, old_value: float, new_value: float):
        """Handle master volume changes."""
        self.logger.info(f"Master volume changed: {old_value} -> {new_value}")
        # Update audio system volume if method exists
        if hasattr(self.audio_system, 'set_master_volume'):
            self.audio_system.set_master_volume(new_value)
        
        # Update metrics
        self.state_manager.set(
            "audio.volume_changes",
            self.state_manager.get("audio.volume_changes", 0) + 1,
            source="audio_integration",
            description="Volume change tracked"
        )
    
    def _on_music_volume_changed(self, field_path: str, old_value: float, new_value: float):
        """Handle music volume changes."""
        self.logger.info(f"Music volume changed: {old_value} -> {new_value}")
        # Update audio system volume if method exists
        if hasattr(self.audio_system, 'set_music_volume'):
            self.audio_system.set_music_volume(new_value)
    
    def _on_sfx_volume_changed(self, field_path: str, old_value: float, new_value: float):
        """Handle SFX volume changes."""
        self.logger.info(f"SFX volume changed: {old_value} -> {new_value}")
        # Update audio system volume if method exists
        if hasattr(self.audio_system, 'set_sfx_volume'):
            self.audio_system.set_sfx_volume(new_value)
    
    def _on_music_enabled_changed(self, field_path: str, old_value: bool, new_value: bool):
        """Handle music enabled changes."""
        self.logger.info(f"Music enabled changed: {old_value} -> {new_value}")
        if not new_value and self.is_music_playing():
            # Stop music if disabled
            self.set_music_playing(False)
            if hasattr(self.audio_system, 'stop_music'):
                self.audio_system.stop_music()
    
    def _on_sfx_enabled_changed(self, field_path: str, old_value: bool, new_value: bool):
        """Handle SFX enabled changes."""
        self.logger.info(f"SFX enabled changed: {old_value} -> {new_value}")
    
    def get_audio_state_summary(self) -> Dict[str, Any]:
        """Get a summary of current audio state."""
        return {
            "master_volume": self.get_master_volume(),
            "music_volume": self.get_music_volume(),
            "sfx_volume": self.get_sfx_volume(),
            "music_enabled": self.is_music_enabled(),
            "sfx_enabled": self.is_sfx_enabled(),
            "mp3_player_visible": self.is_mp3_player_visible(),
            "current_music": self.get_current_music(),
            "music_playing": self.is_music_playing(),
            "sounds_played": self.state_manager.get("audio.sounds_played", 0),
            "music_tracks_played": self.state_manager.get("audio.music_tracks_played", 0),
            "volume_changes": self.state_manager.get("audio.volume_changes", 0),
        }
    
    def sync_with_settings_module(self, settings_dict: Dict[str, Any]):
        """Sync audio state with settings module configuration."""
        # Map settings keys to audio state paths
        settings_mapping = {
            "master_volume": "audio.master_volume",
            "music_volume": "audio.music_volume",
            "sfx_volume": "audio.sfx_volume",
        }
        
        for settings_key, state_path in settings_mapping.items():
            if settings_key in settings_dict:
                value = settings_dict[settings_key]
                self.state_manager.set(
                    state_path,
                    value,
                    source="settings_module",
                    description=f"Synced from settings: {settings_key}"
                )
        
        self.logger.info("Audio state synced with settings module")
    
    def get_settings_dict(self) -> Dict[str, Any]:
        """Get audio state as settings dictionary for persistence."""
        return {
            "master_volume": self.get_master_volume(),
            "music_volume": self.get_music_volume(),
            "sfx_volume": self.get_sfx_volume(),
        }
