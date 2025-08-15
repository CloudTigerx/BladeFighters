"""
Audio Settings Integration
Connects the settings module with the audio state management system.
"""

from typing import Dict, Any, Optional, Callable
from ..audio_module.audio_state_manager import AudioStateManager
from ..game_state_module.game_state_manager import GameStateManager
from ..logging_module.logger import get_logger


class AudioSettingsIntegration:
    """
    Integrates audio settings with the unified state management system.
    Provides callbacks and synchronization between settings UI and audio state.
    """
    
    def __init__(self, state_manager: GameStateManager, audio_state_manager: AudioStateManager):
        """Initialize the audio settings integration."""
        self.state_manager = state_manager
        self.audio_state_manager = audio_state_manager
        self.logger = get_logger(__name__)
        
        # Settings change callbacks
        self._settings_callbacks: Dict[str, Callable] = {}
        
        self.logger.info("AudioSettingsIntegration initialized")
    
    def get_audio_settings_callbacks(self) -> Dict[str, Callable]:
        """
        Get callbacks for audio settings that can be used by the settings UI.
        
        Returns:
            Dict[str, Callable]: Dictionary of setting keys to callback functions
        """
        return {
            "master_volume": self._on_master_volume_change,
            "music_volume": self._on_music_volume_change,
            "sfx_volume": self._on_sfx_volume_change,
            "music_enabled": self._on_music_enabled_change,
            "sfx_enabled": self._on_sfx_enabled_change
        }
    
    def _on_master_volume_change(self, value: float) -> bool:
        """Handle master volume setting change."""
        success = self.audio_state_manager.set_master_volume(value, "settings_ui")
        if success:
            self.logger.info(f"Master volume changed to {value}")
        return success
    
    def _on_music_volume_change(self, value: float) -> bool:
        """Handle music volume setting change."""
        success = self.audio_state_manager.set_music_volume(value, "settings_ui")
        if success:
            self.logger.info(f"Music volume changed to {value}")
        return success
    
    def _on_sfx_volume_change(self, value: float) -> bool:
        """Handle sound effects volume setting change."""
        success = self.audio_state_manager.set_sfx_volume(value, "settings_ui")
        if success:
            self.logger.info(f"SFX volume changed to {value}")
        return success
    
    def _on_music_enabled_change(self, value: bool) -> bool:
        """Handle music enabled setting change."""
        success = self.audio_state_manager.set_music_enabled(value, "settings_ui")
        if success:
            self.logger.info(f"Music {'enabled' if value else 'disabled'}")
        return success
    
    def _on_sfx_enabled_change(self, value: bool) -> bool:
        """Handle sound effects enabled setting change."""
        success = self.audio_state_manager.set_sfx_enabled(value, "settings_ui")
        if success:
            self.logger.info(f"SFX {'enabled' if value else 'disabled'}")
        return success
    
    def sync_settings_to_state(self, settings: Dict[str, Any]) -> None:
        """
        Sync settings configuration to the audio state manager.
        
        Args:
            settings: Dictionary containing audio settings
        """
        self.audio_state_manager.sync_from_settings(settings)
        self.logger.info("Audio settings synced to state manager")
    
    def get_current_settings(self) -> Dict[str, Any]:
        """
        Get current audio settings from the state manager.
        
        Returns:
            Dict[str, Any]: Current audio settings
        """
        return self.audio_state_manager.get_settings_dict()
    
    def create_settings_snapshot(self, description: str = "Settings change") -> None:
        """Create a snapshot of the current audio state."""
        self.audio_state_manager.create_snapshot(description)
    
    def get_audio_state_summary(self) -> Dict[str, Any]:
        """Get a summary of the current audio state for debugging."""
        return self.audio_state_manager.get_state_summary() 