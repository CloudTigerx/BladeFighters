"""
AudioSystem Implementation
=========================

Extracted audio system providing sound effects and music playback functionality.
This implementation integrates with the unified game state management system.

Author: Blade Fighters Refactoring Team
Created: During Phase 1 refactoring
Updated: Phase 2 - Audio State Integration
"""

import os
import pygame
import random
from typing import Dict, List, Optional, Any
try:
    from ..logging_module.error_handler import (
        safe_file_operation,
        safe_operation
    )
    from ..logging_module.logger import get_logger
    from .audio_state_manager import AudioStateManager
    from .mp3_player import MP3Player
except ImportError:
    # Fallback for testing or when running as standalone
    def safe_file_operation(operation_name, default_return, log_level):
        def decorator(func):
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"Error in {operation_name}: {e}")
                    return default_return
            return wrapper
        return decorator
    
    def safe_operation(operation_name, default_return, log_level):
        def decorator(func):
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"Error in {operation_name}: {e}")
                    return default_return
            return wrapper
        return decorator
    
    def get_logger(name):
        import logging
        return logging.getLogger(name)
    
    # Mock AudioStateManager for testing
    class AudioStateManager:
        def __init__(self, state_manager):
            self.state_manager = state_manager
    
    # Mock MP3Player for testing
    class MP3Player:
        def __init__(self, songs=None, background_image=None):
            self.songs = songs or []
            self.background_image = background_image
            self.mp3_player_buttons = {}
        
        def draw(self, screen, width, height):
            return {}
        
        def pause_song(self):
            pass
        
        def next_song(self):
            pass
        
        def prev_song(self):
            pass
        
        def volume_up(self):
            pass
        
        def volume_down(self):
            pass

logger = get_logger(__name__)


class AudioSystem:
    """
    Comprehensive audio system for managing music and sound effects.
    Handles MP3 playback, sound effects, and audio controls.
    Now integrated with unified state management.
    """

    def __init__(self, root_path: str = ".", asset_path: str = "puzzleassets", 
                 state_manager=None):
        self.root_path = root_path
        self.asset_path = asset_path
        
        # State management integration
        self.state_manager = state_manager
        self.audio_state_manager = None
        if state_manager:
            self.audio_state_manager = AudioStateManager(state_manager)
            self.audio_state_manager.audio_system = self
        
        # Sound effects storage
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        
        # Music management
        self.music_playlist: List[str] = []
        self.music_index = 0
        
        # MP3 player UI
        self.mp3_player_background = self._load_mp3_player_background()
        self.mp3_player_buttons: Dict[str, pygame.Rect] = {}
        
        # Load sounds
        self._load_sounds()
        
        # Load songs and create MP3 player
        self._load_songs_and_create_mp3_player()
        
        # Sync initial state if state manager is available
        if self.audio_state_manager:
            self._sync_from_state()
        
        logger.info("AudioSystem initialized successfully")
    
    def _load_songs_and_create_mp3_player(self):
        """Load songs from the songs directory and create MP3 player instance."""
        try:
            songs = []
            songs_dir = os.path.join(self.root_path, "sounds", "songs")
            
            if os.path.exists(songs_dir):
                # Define song metadata
                song_metadata = {
                    "Alex-Productions - Revenge.mp3": {
                        "title": "Revenge",
                        "artist": "Alex Productions",
                        "source": "Pixabay",
                        "license": "Pixabay License"
                    },
                    "Lightning Traveler - Jungles.mp3.mp3": {
                        "title": "Jungles",
                        "artist": "Lightning Traveler",
                        "source": "Pixabay",
                        "license": "Pixabay License"
                    },
                    "Lowtone Music - Medicine Of The Future - Abstract Technology.mp3": {
                        "title": "Medicine Of The Future",
                        "artist": "Lowtone Music",
                        "source": "Pixabay",
                        "license": "Pixabay License"
                    },
                    "Nihilore - Single Lane Tunnel.mp3": {
                        "title": "Single Lane Tunnel",
                        "artist": "Nihilore",
                        "source": "Pixabay",
                        "license": "Pixabay License"
                    },
                    "Pufino - Vibing (Chill Lofi Royalty Free Music).mp3": {
                        "title": "Vibing",
                        "artist": "Pufino",
                        "source": "Pixabay",
                        "license": "Pixabay License"
                    },
                    "Soundwave Sphere - Gravity Breaks.mp3.mp3": {
                        "title": "Gravity Breaks",
                        "artist": "Soundwave Sphere",
                        "source": "Pixabay",
                        "license": "Pixabay License"
                    },
                    "snoozy beats - cat cafe.mp3": {
                        "title": "Cat Cafe",
                        "artist": "Snoozy Beats",
                        "source": "Pixabay",
                        "license": "Pixabay License"
                    },
                    "through-tge-horizon-sunocom-321414.mp3": {
                        "title": "Through The Horizon",
                        "artist": "Sunocom",
                        "source": "Pixabay",
                        "license": "Pixabay License"
                    }
                }
                
                # Load each song file
                for filename in os.listdir(songs_dir):
                    if filename.lower().endswith('.mp3'):
                        file_path = os.path.join(songs_dir, filename)
                        
                        # Get metadata for this song
                        metadata = song_metadata.get(filename, {
                            "title": filename.replace('.mp3', ''),
                            "artist": "Unknown Artist",
                            "source": "Unknown",
                            "license": "Unknown"
                        })
                        
                        songs.append({
                            "path": file_path,
                            "title": metadata["title"],
                            "artist": metadata["artist"],
                            "source": metadata["source"],
                            "license": metadata["license"]
                        })
                
                logger.info(f"Loaded {len(songs)} songs for MP3 player")
            else:
                logger.warning(f"Songs directory not found: {songs_dir}")
            
            # Create MP3 player instance
            self.mp3_player = MP3Player(songs, self.mp3_player_background)
            
            # Set sounds for MP3 player UI interactions
            if hasattr(self, 'sounds'):
                self.mp3_player.set_sounds(self.sounds)
            
            logger.info("MP3 player created successfully")
            
        except Exception as e:
            logger.error(f"Failed to load songs and create MP3 player: {e}")
            # Create empty MP3 player as fallback
            self.mp3_player = MP3Player([], self.mp3_player_background)
    
    def _sync_from_state(self):
        """Sync audio system state from the state manager."""
        if not self.audio_state_manager:
            return
        
        # Update local state from state manager
        self._update_sound_volumes()
    
    def _update_sound_volumes(self):
        """Update sound volumes based on state manager values."""
        if not self.audio_state_manager:
            return
        
        master_volume = self.audio_state_manager.get_master_volume()
        sfx_volume = self.audio_state_manager.get_sfx_volume()
        
        # Update all loaded sounds with new volume
        for sound_name, sound in self.sounds.items():
            base_volume = self._get_base_volume_for_sound(sound_name)
            final_volume = base_volume * sfx_volume * master_volume
            sound.set_volume(final_volume)
    
    def _get_base_volume_for_sound(self, sound_name: str) -> float:
        """Get the base volume for a specific sound type."""
        if 'hover' in sound_name:
            return 0.3
        elif 'click' in sound_name:
            return 0.4
        elif 'placed' in sound_name:
            return 0.5
        else:
            return 0.6

    @safe_file_operation("load MP3 player background", None, "WARNING")
    def _load_mp3_player_background(self) -> Optional[pygame.Surface]:
        """Load custom background image for the MP3 player."""
        # First, try themed skin under puzzleassets/menus/mp3_skin.png
        try:
            themed_path = os.path.join(self.asset_path, 'menus', 'mp3_skin.png')
            if os.path.exists(themed_path):
                return pygame.image.load(themed_path)
        except Exception as e:
            logger.warning(f"Failed to load themed MP3 skin: {str(e)}")
        
        # Check for the specific mp3player.png in puzzleassets
        specific_path = os.path.join(self.asset_path, "mp3player.png")
        if os.path.exists(specific_path):
            try:
                background_image = pygame.image.load(specific_path)
                return background_image
            except pygame.error as e:
                logger.warning(f"Failed to load MP3 player background: {str(e)}")
        
        # Check for other mp3_player_bg.png or mp3_player_bg.jpg in various directories
        image_filenames = ['mp3_player_bg.png', 'mp3_player_bg.jpg', 'mp3_background.png', 'mp3_background.jpg']
        image_dirs = [
            self.root_path,
            self.asset_path,
            os.path.join(self.root_path, 'sounds'),
            os.path.join(self.asset_path, 'sounds')
        ]
        
        for image_dir in image_dirs:
            for filename in image_filenames:
                image_path = os.path.join(image_dir, filename)
                if os.path.exists(image_path):
                    try:
                        background_image = pygame.image.load(image_path)
                        return background_image
                    except pygame.error as e:
                        logger.warning(f"Failed to load MP3 background {image_path}: {str(e)}")
        
        logger.info("No MP3 player background found, using default")
        return None
    
    def _load_sounds(self) -> None:
        """Load sound effects from sound files."""
        # Define sound files to look for in order of preference (.mp3 files first)
        sound_files = {
            'hover': ['menuhover.wav', 'menu_hover.wav', 'hover.wav', 'hover.mp3'],
            'click': ['click.mp3', 'click.wav', 'button_click.wav', 'button_click.mp3'],
            'placed': ['placed.wav'],
            'singlebreak': ['singlebreak.mp3'],
            'double': ['double.mp3'],
            'triple': ['triple.mp3'],
            'tripormore': ['tripormore.mp3']  # For 3+ chain combos
        }
        
        # List of possible sound directories - prioritize ROOT_PATH/sounds
        sound_dirs = [
            os.path.join(self.root_path, 'sounds', 'effects'),  # ROOT_PATH/sounds/effects (highest priority)
            os.path.join(self.root_path, 'sounds'),      # ROOT_PATH/sounds (secondary)
            os.path.join(self.asset_path, 'sounds')      # puzzleassets/sounds (fallback)
        ]
        
        # Load each sound from the first directory where it's found
        for sound_name, file_names in sound_files.items():
            sound_loaded = self._load_sound_file(sound_name, file_names, sound_dirs)
            if sound_loaded:
                logger.debug(f"Loaded sound: {sound_name}")
            else:
                logger.warning(f"Failed to load sound: {sound_name}")

    @safe_operation("load sound file", False, "WARNING")
    def _load_sound_file(self, sound_name: str, file_names: List[str], sound_dirs: List[str]) -> bool:
        """Load a specific sound file."""
        for file_name in file_names:
            for sound_dir in sound_dirs:
                file_path = os.path.join(sound_dir, file_name)
                
                if os.path.exists(file_path):
                    try:
                        # Check file size isn't zero
                        if os.path.getsize(file_path) == 0:
                            logger.warning(f"Sound file is empty: {file_path}")
                            continue
                            
                        # Load the sound file with proper error handling
                        sound = pygame.mixer.Sound(file_path)
                        
                        # Set volume based on sound type
                        if 'hover' in sound_name:
                            sound.set_volume(0.3)
                        elif 'click' in sound_name:
                            sound.set_volume(0.4)
                        elif 'placed' in sound_name:
                            sound.set_volume(0.5)
                        else:
                            sound.set_volume(0.6)
                        
                        self.sounds[sound_name] = sound
                        return True
                        
                    except pygame.error as e:
                        logger.warning(f"Failed to load sound {file_path}: {str(e)}")
                        continue
                    except Exception as e:
                        logger.warning(f"Unexpected error loading sound {file_path}: {str(e)}")
                        continue
        
        return False

    @safe_operation("play sound", None, "WARNING")
    def play_sound(self, sound_name: str) -> None:
        """
        Play a sound effect by name.
        
        Args:
            sound_name (str): Name of the sound to play
                Expected values: 'hover', 'click', 'placed', 'singlebreak',
                               'double', 'triple', 'tripormore'
        """
        # Check if sound effects are enabled via state manager
        if self.audio_state_manager and not self.audio_state_manager.is_sfx_enabled():
            return
        
        if sound_name in self.sounds:
            try:
                self.sounds[sound_name].play()
                logger.debug(f"Playing sound: {sound_name}")
            except Exception as e:
                logger.warning(f"Failed to play sound {sound_name}: {str(e)}")
        else:
            logger.debug(f"Sound not found: {sound_name}")

    @safe_operation("play music", None, "WARNING")
    def play_music(self, music_name: str) -> None:
        """
        Play background music.
        
        Args:
            music_name (str): Name of music to play
                Expected values: 'music' (starts MP3 player)
        """
        # Check if music is enabled via state manager
        if self.audio_state_manager and not self.audio_state_manager.is_music_enabled():
            return
            
        if music_name == 'music':
            # Toggle MP3 player visibility via state manager
            if self.audio_state_manager:
                current_visible = self.audio_state_manager.is_mp3_player_visible()
                self.audio_state_manager.set_mp3_player_visible(not current_visible, "audio_system")
            else:
                # Fallback to local state if no state manager
                logger.warning("No state manager available for MP3 player visibility")
        else:
            logger.debug(f"Unknown music: {music_name}")

    @safe_operation("handle audio events", False, "WARNING")
    def handle_audio_events(self, event: pygame.event.Event) -> bool:
        """
        Handle pygame events related to audio.
        
        Args:
            event (pygame.event.Event): Pygame event to process
            
        Returns:
            bool: True if event was handled, False otherwise
        """
        # Check if MP3 player exists and handle its events
        if hasattr(self, 'mp3_player') and self.mp3_player:
            return self.mp3_player.handle_events(event)
        
        return False

    def _handle_mp3_button_click(self, button_name: str) -> None:
        """Handle MP3 player button clicks."""
        logger.debug(f"MP3 button clicked: {button_name}")
        # Play click sound
        self.play_sound('click')
        
        # Handle different button actions using MP3 player instance
        if hasattr(self, 'mp3_player') and self.mp3_player:
            if button_name == 'play_pause':
                self.mp3_player.pause_song()
                logger.info("MP3 play/pause toggled")
            elif button_name == 'next':
                self.mp3_player.next_song()
                logger.info("MP3 next track")
            elif button_name == 'previous':
                self.mp3_player.prev_song()
                logger.info("MP3 previous track")
            elif button_name == 'volume_up':
                self.mp3_player.volume_up()
                logger.info("MP3 volume up")
            elif button_name == 'volume_down':
                self.mp3_player.volume_down()
                logger.info("MP3 volume down")

    @safe_operation("draw MP3 player", {}, "WARNING")
    def draw_mp3_player(self, screen: pygame.Surface, width: int, height: int) -> Dict[str, pygame.Rect]:
        """
        Draw the MP3 player interface on screen.
        
        Args:
            screen (pygame.Surface): Surface to draw on
            width (int): Screen width
            height (int): Screen height
            
        Returns:
            Dict[str, pygame.Rect]: Dictionary of button names to their rects
        """
        # Check if MP3 player exists and draw it
        if hasattr(self, 'mp3_player') and self.mp3_player:
            return self.mp3_player.draw(screen, width, height)
        
        return {}
    
    # State management convenience methods
    
    def set_master_volume(self, volume: float) -> bool:
        """Set master volume through state manager."""
        if self.audio_state_manager:
            return self.audio_state_manager.set_master_volume(volume, "audio_system")
        return False
    
    def set_music_volume(self, volume: float) -> bool:
        """Set music volume through state manager."""
        if self.audio_state_manager:
            return self.audio_state_manager.set_music_volume(volume, "audio_system")
        return False
    
    def set_sfx_volume(self, volume: float) -> bool:
        """Set sound effects volume through state manager."""
        if self.audio_state_manager:
            return self.audio_state_manager.set_sfx_volume(volume, "audio_system")
        return False
    
    def enable_music(self, enabled: bool) -> bool:
        """Enable or disable music through state manager."""
        if self.audio_state_manager:
            return self.audio_state_manager.set_music_enabled(enabled, "audio_system")
        return False
    
    def enable_sfx(self, enabled: bool) -> bool:
        """Enable or disable sound effects through state manager."""
        if self.audio_state_manager:
            return self.audio_state_manager.set_sfx_enabled(enabled, "audio_system")
        return False
    
    def get_audio_state_summary(self) -> Dict[str, Any]:
        """Get a summary of the current audio state."""
        if self.audio_state_manager:
            return self.audio_state_manager.get_state_summary()
        return {}
    
    def sync_from_settings(self, settings: Dict[str, Any]) -> None:
        """Sync audio state from settings configuration."""
        if self.audio_state_manager:
            self.audio_state_manager.sync_from_settings(settings)
            self._sync_from_state()