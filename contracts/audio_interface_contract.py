"""
AudioSystem Interface Contract
============================

This document defines the public interface contract for the AudioSystem module.
All implementations must adhere to this contract to ensure compatibility.

Author: Blade Fighters Refactoring Team
Created: During Phase 1 refactoring
Purpose: Safe extraction of AudioSystem from monolithic architecture
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import pygame


class AudioSystemInterface(ABC):
    """
    Abstract interface defining the contract for AudioSystem implementations.
    
    This interface ensures that any AudioSystem implementation provides
    the exact same functionality expected by the rest of the game.
    """
    
    @abstractmethod
    def __init__(self, asset_path: str):
        """
        Initialize the audio system with the given asset path.
        
        Args:
            asset_path (str): Path to the game assets directory
            
        Postconditions:
            - Audio system is fully initialized
            - All available sounds are loaded
            - MP3 player is ready with available songs
            - Fallback behavior is established for missing files
        """
        pass
    
    @abstractmethod
    def play_sound(self, sound_name: str) -> None:
        """
        Play a sound effect by name.
        
        Args:
            sound_name (str): Name of the sound to play
                Expected values: 'hover', 'click', 'placed', 'singlebreak',
                               'double', 'triple', 'tripormore'
                               
        Behavior:
            - If sound exists: Play the sound at appropriate volume
            - If sound missing: Handle gracefully (no crash)
            - Invalid sound names: Handle gracefully (no crash)
        """
        pass
    
    @abstractmethod  
    def play_music(self, music_name: str) -> None:
        """
        Play background music.
        
        Args:
            music_name (str): Name of music to play
                Expected values: 'music' (starts MP3 player)
                
        Behavior:
            - Starts the MP3 player if available
            - Handles missing MP3 player gracefully
        """
        pass
    
    @abstractmethod
    def handle_audio_events(self, event: pygame.event.Event) -> bool:
        """
        Handle pygame events related to audio.
        
        Args:
            event (pygame.event.Event): Pygame event to process
            
        Returns:
            bool: True if event was handled, False otherwise
            
        Behavior:
            - Process MP3 player related events
            - Return True only if event was actually handled
        """
        pass
    
    @abstractmethod
    def draw_mp3_player(self, screen: pygame.Surface, width: int, height: int) -> Dict[str, pygame.Rect]:
        """
        Draw the MP3 player interface on screen.
        
        Args:
            screen (pygame.Surface): Surface to draw on
            width (int): Screen width
            height (int): Screen height
            
        Returns:
            Dict[str, pygame.Rect]: Dictionary of button names to their rects
                                   for click detection
                                   
        Behavior:
            - Draw the MP3 player UI if available
            - Return button rects for interaction
            - Handle missing MP3 player gracefully
        """
        pass


class AudioSystemRequirements:
    """
    Defines the specific requirements and expected behavior of the AudioSystem.
    
    This class documents the exact behavior that must be preserved during refactoring.
    """
    
    # Expected sound types that must be supported
    REQUIRED_SOUNDS = [
        'hover',      # Menu hover effects (volume: 0.3)
        'click',      # Button click sounds (volume: 0.4) 
        'placed',     # Piece placement sound (volume: 0.5)
        'singlebreak', # Single block break (volume: 0.6)
        'double',     # Double combo sound
        'triple',     # Triple combo sound
        'tripormore'  # 3+ combo sound
    ]
    
    # Expected sound file formats (in order of preference)
    SOUND_FILE_FORMATS = ['.mp3', '.wav', '.ogg']
    
    # Expected directory structure for sound loading
    SOUND_DIRECTORIES = [
        'sounds/effects',    # Primary location
        'sounds',           # Secondary location  
        'puzzleassets/sounds' # Fallback location
    ]
    
    # MP3 player requirements
    MP3_PLAYER_FEATURES = [
        'background_music_playback',
        'song_selection',
        'play_pause_controls', 
        'next_previous_navigation',
        'song_info_display',
        'volume_control'
    ]
    
    # Error handling requirements
    ERROR_HANDLING = {
        'missing_sound_files': 'Create silent dummy sounds',
        'missing_asset_directory': 'Graceful degradation',
        'pygame_initialization_failure': 'Handle with try/catch',
        'invalid_sound_requests': 'Log and continue'
    }
    
    # Integration requirements
    INTEGRATION_POINTS = {
        'game_client': 'Must initialize AudioSystem with asset_path',
        'menu_system': 'Must support play_sound for hover/click',
        'puzzle_module': 'Must support play_sound for game events',
        'mp3_player_ui': 'Must support draw_mp3_player and handle_audio_events'
    }
    
    # Performance requirements
    PERFORMANCE_REQUIREMENTS = {
        'initialization_time': 'Must complete in < 3 seconds',
        'sound_playback_latency': 'Must be < 50ms',
        'memory_usage': 'Must not exceed 50MB for sound cache',
        'file_loading': 'Must handle gracefully if files missing'
    }


class AudioSystemTestContract:
    """
    Defines the test contract that validates AudioSystem behavior.
    
    All AudioSystem implementations must pass these test requirements.
    """
    
    @staticmethod
    def get_required_tests():
        """Return the list of required tests for AudioSystem validation."""
        return [
            'test_audio_system_initialization',
            'test_sound_loading', 
            'test_sound_playback',
            'test_mp3_player_integration',
            'test_volume_control',
            'test_fallback_behavior',
            'test_audio_event_handling',
            'test_audio_integration_with_menu',
            'test_audio_integration_with_puzzle'
        ]
    
    @staticmethod
    def get_success_criteria():
        """Return the success criteria for AudioSystem extraction."""
        return {
            'test_pass_rate': '100%',
            'no_functionality_loss': True,
            'error_handling_preserved': True,
            'integration_points_maintained': True,
            'performance_not_degraded': True
        }


# Export the interface and requirements for use during extraction
__all__ = [
    'AudioSystemInterface',
    'AudioSystemRequirements', 
    'AudioSystemTestContract'
] 