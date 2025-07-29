"""
AudioSystem Implementation
=========================

Extracted audio system providing sound effects and music playback functionality.
This implementation adheres to the AudioSystemInterface contract.

Author: Blade Fighters Refactoring Team
Created: During Phase 1 refactoring
"""

import pygame
import os
import random
import time
from typing import Dict, Optional

# Import the interface contract for validation
try:
    from ..audio_interface_contract import AudioSystemInterface
    USE_INTERFACE_CONTRACT = True
except ImportError:
    # Fallback for when running standalone
    USE_INTERFACE_CONTRACT = False
    class AudioSystemInterface:
        pass

from .mp3_player import MP3Player


class AudioSystem(AudioSystemInterface):
    """
    Extracted AudioSystem implementation.
    
    Provides sound effects and music playback functionality with graceful
    error handling and fallback behavior.
    
    This class implements the AudioSystemInterface contract to ensure
    compatibility during the refactoring process.
    """
    
    def __init__(self, asset_path: str):
        """
        Initialize audio system with support for sound effects and music.
        
        Args:
            asset_path (str): Path to the game assets directory
        """
        # Initialize paths
        self.asset_path = asset_path
        self.root_path = os.path.dirname(asset_path)
        print(f"Audio system initialized with asset path: {asset_path}\nRoot path: {self.root_path}")
        
        # Initialize pygame mixer for sounds
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
        print("Audio system initialized with optimal parameters for MP3 playback")
        
        # Dictionaries to store loaded sounds and songs
        self.sounds = {}
        self.songs = []
        
        # Hover sound tracking
        self.hovered_buttons = set()
        self.last_hover_sound_time = 0
        self.hover_sound_cooldown = 300  # Minimum time (ms) between hover sounds
        
        # Load custom background image for MP3 player
        self.mp3_player_background = self._load_mp3_player_background()
        
        # Load sounds
        self._load_sounds()
        
        # Load songs
        self._load_songs()
        
        # Initialize the MP3 player
        self.mp3_player = MP3Player(self.songs, self.mp3_player_background)
        self.mp3_player.set_sounds(self.sounds)
    
    def play_sound(self, sound_name: str) -> None:
        """
        Play a sound effect by name.
        
        Args:
            sound_name (str): Name of the sound to play
        """
        print(f"Attempting to play sound: {sound_name}")
        print(f"Available sounds: {list(self.sounds.keys())}")
        
        if sound_name in self.sounds:
            try:
                self.sounds[sound_name].play()
                print(f"Successfully played sound: {sound_name}")
            except Exception as e:
                print(f"Error playing sound {sound_name}: {e}")
        else:
            print(f"Sound not found: {sound_name}")
    
    def play_music(self, music_name: str) -> None:
        """
        Play background music.
        
        Args:
            music_name (str): Name of music to play
        """
        if music_name == 'music' and hasattr(self, 'mp3_player') and self.mp3_player.songs:
            self.mp3_player.play_song()
    
    def handle_audio_events(self, event: pygame.event.Event) -> bool:
        """
        Handle pygame events related to audio.
        
        Args:
            event (pygame.event.Event): Pygame event to process
            
        Returns:
            bool: True if event was handled, False otherwise
        """
        # First let the MP3 player try to handle the event
        if hasattr(self, 'mp3_player') and self.mp3_player.handle_events(event):
            return True
            
        return False  # Event wasn't handled
    
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
        if hasattr(self, 'mp3_player'):
            return self.mp3_player.draw(screen, width, height)
        return {}
    
    # Private implementation methods
    
    def _load_mp3_player_background(self) -> Optional[pygame.Surface]:
        """Load custom background image for the MP3 player."""
        background_image = None
        
        # First, check for the specific mp3player.png in puzzleassets
        specific_path = os.path.join(self.asset_path, "mp3player.png")
        if os.path.exists(specific_path):
            try:
                background_image = pygame.image.load(specific_path)
                print(f"Loaded custom MP3 player background from {specific_path}")
                return background_image
            except pygame.error as e:
                print(f"Error loading specific MP3 player background {specific_path}: {e}")
        
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
                        print(f"Loaded MP3 player background image from {image_path}")
                        return background_image
                    except pygame.error as e:
                        print(f"Error loading MP3 player background image {image_path}: {e}")
        
        print("No custom MP3 player background image found, using default style")
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
        
        # Sound directory information
        for sound_dir in sound_dirs:
            if os.path.exists(sound_dir):
                print(f"Found sound directory: {sound_dir}")
            else:
                print(f"Sound directory not found: {sound_dir}")
        
        # Print sound system info
        print(f"Sound system initialized. Using sound files from '{sound_dirs[0]}' (primary) or '{sound_dirs[1]}' (fallback).")
        
        # Load each sound from the first directory where it's found
        for sound_name, file_names in sound_files.items():
            sound_loaded = False
            
            for file_name in file_names:
                for sound_dir in sound_dirs:
                    file_path = os.path.join(sound_dir, file_name)
                    print(f"Looking for {sound_name} sound at: {file_path}")
                    
                    if os.path.exists(file_path):
                        try:
                            # Check file size isn't zero
                            if os.path.getsize(file_path) == 0:
                                print(f"Warning: {file_path} has zero size")
                                continue
                                
                            # Load the sound file with proper error handling
                            sound = pygame.mixer.Sound(file_path)
                            
                            # Set volume based on sound type
                            if 'hover' in sound_name:
                                sound.set_volume(0.3)
                            elif 'click' in sound_name:
                                sound.set_volume(0.4)
                            elif 'placed' in sound_name:
                                sound.set_volume(0.5)  # Set placed sound to 50% volume
                            elif 'singlebreak' in sound_name:
                                sound.set_volume(0.6)  # Set single break sound to 60% volume
                                
                            self.sounds[sound_name] = sound
                            print(f"Loaded {sound_name} sound from {file_path}")
                            sound_loaded = True
                            break
                        except pygame.error as e:
                            print(f"Error loading sound {file_path}: {e}")
                
                if sound_loaded:
                    break
                    
            # Create dummy sounds as fallback for essential effects if they couldn't be loaded
            if not sound_loaded:
                print(f"No sound file found for '{sound_name}', using silent dummy sound")
                self._create_silent_dummy_sound(sound_name)
    
    def _create_silent_dummy_sound(self, name: str) -> None:
        """Create a silent dummy sound as a fallback."""
        print(f"Creating silent dummy sound for {name}")
        try:
            # Create a short, silent sound using numpy array
            buffer = pygame.sndarray.array([0] * 1000)  # 1000 samples of silence
            dummy_sound = pygame.sndarray.make_sound(buffer)
            dummy_sound.set_volume(0.0)  # Ensure it's silent
            self.sounds[name] = dummy_sound
        except:
            # Last resort: completely empty sound object
            print(f"Could not create dummy sound for {name}, using empty object")
            class DummySound:
                def play(self): pass
                def stop(self): pass
                def set_volume(self, volume): pass
            self.sounds[name] = DummySound()
    
    def set_volume(self, volume: float) -> None:
        """
        Set the volume for sound effects.
        
        Args:
            volume (float): Volume level between 0.0 and 1.0
        """
        volume = max(0.0, min(1.0, volume))  # Clamp between 0.0 and 1.0
        
        # Set volume for all loaded sounds
        for sound_name, sound in self.sounds.items():
            if hasattr(sound, 'set_volume'):
                sound.set_volume(volume)
        
        print(f"🔊 Sound effects volume set to {volume:.1f}")
    
    def set_music_volume(self, volume: float) -> None:
        """
        Set the volume for background music.
        
        Args:
            volume (float): Volume level between 0.0 and 1.0
        """
        volume = max(0.0, min(1.0, volume))  # Clamp between 0.0 and 1.0
        
        # Set volume for pygame mixer music
        pygame.mixer.music.set_volume(volume)
        
        print(f"🎵 Music volume set to {volume:.1f}")
    
    def _load_songs(self) -> None:
        """Load MP3 files from the songs directory."""
        try:
            # Define songs directories to check - prioritize ROOT_PATH/sounds/songs
            songs_dirs = [
                os.path.join(self.root_path, 'sounds', 'songs'),    # ROOT_PATH/sounds/songs (primary)
                os.path.join(self.asset_path, 'sounds', 'songs')    # puzzleassets/sounds/songs (fallback)
            ]
            
            # Find all MP3 files in songs directories
            self.songs = []
            
            for songs_dir in songs_dirs:
                if os.path.exists(songs_dir):
                    print(f"Scanning for songs in: {songs_dir}")
                    files = os.listdir(songs_dir)
                    print(f"Found {len(files)} files in songs directory: {songs_dir}")
                    
                    for file in files:
                        # Check for audio formats
                        if file.lower().endswith(('.mp3', '.wav', '.ogg')):
                            file_path = os.path.join(songs_dir, file)
                            
                            # Skip if already added to avoid duplicates
                            if any(song['path'] == file_path for song in self.songs):
                                continue
                                
                            # Extract title and artist from filename
                            file_name = os.path.splitext(file)[0]
                            parts = file_name.split(' - ', 1)
                            
                            artist = parts[0] if len(parts) > 1 else "Unknown Artist"
                            title = parts[1] if len(parts) > 1 else file_name
                            
                            # Default attribution
                            source = ""
                            license_type = ""
                            
                            # Known songs with proper attribution
                            if "cat cafe" in file_name.lower():
                                source = "Free Music Archive"
                                license_type = "CC BY"
                            elif "nihilore" in file_name.lower():
                                source = "nihilore.com"
                                license_type = "CC BY-NC-SA"
                            
                            self.songs.append({
                                'path': file_path,
                                'title': title,
                                'artist': artist,
                                'filename': file,
                                'source': source,
                                'license': license_type
                            })
                            print(f"Added song: {artist} - {title}")
                else:
                    print(f"Songs directory not found: {songs_dir}")
                    
            # Initialize the MP3 player with the songs
            if self.songs:
                print(f"Loaded {len(self.songs)} songs for the MP3 player")
                if hasattr(self, 'mp3_player'):
                    self.mp3_player.set_songs(self.songs)
            else:
                print("No songs found in any directory")
                
        except Exception as e:
            print(f"Error loading songs: {e}")


# Validate interface compliance at module load time
if USE_INTERFACE_CONTRACT:
    # Verify that AudioSystem implements all required methods
    required_methods = ['__init__', 'play_sound', 'play_music', 'handle_audio_events', 'draw_mp3_player']
    for method in required_methods:
        if not hasattr(AudioSystem, method):
            raise NotImplementedError(f"AudioSystem missing required method: {method}")
    
    print("✅ AudioSystem implementation validated against interface contract") 