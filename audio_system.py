import pygame
import os
import random
import time
from mp3_player import MP3Player

class AudioSystem:
    def __init__(self, asset_path):
        """Initialize audio system with support for sound effects and music."""
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
        self.mp3_player_background = self.load_mp3_player_background()
        
        # Load sounds
        self.load_sounds()
        
        # Load songs
        self.load_songs()
        
        # Initialize the MP3 player
        self.mp3_player = MP3Player(self.songs, self.mp3_player_background)
        self.mp3_player.set_sounds(self.sounds)
        
    def load_mp3_player_background(self):
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
    
    def load_sounds(self):
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
                            
                            # Set volume
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
                self.create_silent_dummy_sound(sound_name)
        
    def create_silent_dummy_sound(self, name):
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
    
    def load_songs(self):
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
    
    def play_music(self, music_name):
        """Play background music."""
        if music_name == 'music' and hasattr(self, 'mp3_player') and self.mp3_player.songs:
            self.mp3_player.play_song()
    
    def draw_mp3_player(self, screen, width, height):
        """Draw the MP3 player on screen (delegates to MP3Player)."""
        if hasattr(self, 'mp3_player'):
            return self.mp3_player.draw(screen, width, height)
        return {}
    
    def handle_audio_events(self, event):
        """Handle pygame events related to audio."""
        # First let the MP3 player try to handle the event
        if hasattr(self, 'mp3_player') and self.mp3_player.handle_events(event):
            return True
            
        return False  # Event wasn't handled
        
    def play_sound(self, sound_name):
        """Play a sound by name."""
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