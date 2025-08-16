"""
Audio State Manager
Integrates audio system with the unified game state management.
"""

from typing import Optional, Dict, Any, List
from ..game_state_module.game_state_manager import GameStateManager
from ..game_state_module.state_schema import AudioState
from ..logging_module.logger import get_logger


class AudioStateManager:
    """
    Manages audio state through the unified game state manager.
    Provides a clean interface for audio state operations with proper validation.
    """
    
    def __init__(self, state_manager: GameStateManager):
        """Initialize the audio state manager."""
        self.state_manager = state_manager
        self.logger = get_logger(__name__)
        
        # Register callbacks for audio state changes
        self._register_callbacks()
        
        self.logger.info("AudioStateManager initialized")
    
    def _register_callbacks(self):
        """Register callbacks for audio state changes."""
        audio_fields = [
            "audio.master_volume",
            "audio.music_volume", 
            "audio.sfx_volume",
            "audio.music_enabled",
            "audio.sfx_enabled",
            "audio.current_music",
            "audio.music_playing",
            "audio.mp3_player_visible"
        ]
        
        for field in audio_fields:
            self.state_manager.add_change_callback(
                field,
                self._on_audio_state_change
            )
    
    def _on_audio_state_change(self, field_path: str, old_value: Any, new_value: Any):
        """Handle audio state changes."""
        self.logger.debug(f"Audio state changed: {field_path} = {old_value} -> {new_value}")
        
        # Notify audio system of changes
        if hasattr(self, 'audio_system') and self.audio_system:
            self.audio_system._sync_from_state()
    
    def set_master_volume(self, volume: float, source: str = "audio_manager") -> bool:
        """Set the master volume."""
        return self.state_manager.set(
            "audio.master_volume", 
            volume, 
            source=source,
            description=f"Master volume set to {volume}"
        )
    
    def get_master_volume(self) -> float:
        """Get the master volume."""
        return self.state_manager.get("audio.master_volume", 0.6)
    
    def set_music_volume(self, volume: float, source: str = "audio_manager") -> bool:
        """Set the music volume."""
        return self.state_manager.set(
            "audio.music_volume", 
            volume, 
            source=source,
            description=f"Music volume set to {volume}"
        )
    
    def get_music_volume(self) -> float:
        """Get the music volume."""
        return self.state_manager.get("audio.music_volume", 0.5)
    
    def set_sfx_volume(self, volume: float, source: str = "audio_manager") -> bool:
        """Set the sound effects volume."""
        return self.state_manager.set(
            "audio.sfx_volume", 
            volume, 
            source=source,
            description=f"SFX volume set to {volume}"
        )
    
    def get_sfx_volume(self) -> float:
        """Get the sound effects volume."""
        return self.state_manager.get("audio.sfx_volume", 0.7)
    
    def set_music_enabled(self, enabled: bool, source: str = "audio_manager") -> bool:
        """Enable or disable music."""
        return self.state_manager.set(
            "audio.music_enabled", 
            enabled, 
            source=source,
            description=f"Music {'enabled' if enabled else 'disabled'}"
        )
    
    def is_music_enabled(self) -> bool:
        """Check if music is enabled."""
        return self.state_manager.get("audio.music_enabled", True)
    
    def set_sfx_enabled(self, enabled: bool, source: str = "audio_manager") -> bool:
        """Enable or disable sound effects."""
        return self.state_manager.set(
            "audio.sfx_enabled", 
            enabled, 
            source=source,
            description=f"SFX {'enabled' if enabled else 'disabled'}"
        )
    
    def is_sfx_enabled(self) -> bool:
        """Check if sound effects are enabled."""
        return self.state_manager.get("audio.sfx_enabled", True)
    
    def set_current_music(self, music_name: Optional[str], source: str = "audio_manager") -> bool:
        """Set the current music track."""
        return self.state_manager.set(
            "audio.current_music", 
            music_name, 
            source=source,
            description=f"Current music set to {music_name or 'None'}"
        )
    
    def get_current_music(self) -> Optional[str]:
        """Get the current music track."""
        return self.state_manager.get("audio.current_music")
    
    def set_music_playing(self, playing: bool, source: str = "audio_manager") -> bool:
        """Set whether music is currently playing."""
        return self.state_manager.set(
            "audio.music_playing", 
            playing, 
            source=source,
            description=f"Music {'started' if playing else 'stopped'}"
        )
    
    def is_music_playing(self) -> bool:
        """Check if music is currently playing."""
        return self.state_manager.get("audio.music_playing", False)
    
    def set_mp3_player_visible(self, visible: bool, source: str = "audio_manager") -> bool:
        """Set MP3 player visibility."""
        return self.state_manager.set(
            "audio.mp3_player_visible", 
            visible, 
            source=source,
            description=f"MP3 player {'shown' if visible else 'hidden'}"
        )
    
    def is_mp3_player_visible(self) -> bool:
        """Check if MP3 player is visible."""
        return self.state_manager.get("audio.mp3_player_visible", False)
    
    def get_audio_state(self) -> AudioState:
        """Get the complete audio state."""
        return self.state_manager.state.audio
    
    def sync_from_settings(self, settings: Dict[str, Any]) -> None:
        """Sync audio state from settings configuration."""
        if "master_volume" in settings:
            self.set_master_volume(settings["master_volume"], "settings_sync")
        
        if "music_volume" in settings:
            self.set_music_volume(settings["music_volume"], "settings_sync")
    
    def get_settings_dict(self) -> Dict[str, Any]:
        """Get audio settings as a dictionary for persistence."""
        return {
            "master_volume": self.get_master_volume(),
            "music_volume": self.get_music_volume(),
            "sfx_volume": self.get_sfx_volume(),
            "music_enabled": self.is_music_enabled(),
            "sfx_enabled": self.is_sfx_enabled()
        }
    
    def create_snapshot(self, description: str = "Audio state snapshot") -> None:
        """Create a snapshot of the current audio state."""
        self.state_manager.create_snapshot(description, ["audio"])
    
    def get_state_summary(self) -> Dict[str, Any]:
        """Get a summary of the current audio state."""
        return {
            "master_volume": self.get_master_volume(),
            "music_volume": self.get_music_volume(),
            "sfx_volume": self.get_sfx_volume(),
            "music_enabled": self.is_music_enabled(),
            "sfx_enabled": self.is_sfx_enabled(),
            "current_music": self.get_current_music(),
            "music_playing": self.is_music_playing(),
            "mp3_player_visible": self.is_mp3_player_visible()
        } 