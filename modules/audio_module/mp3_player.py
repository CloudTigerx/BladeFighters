import pygame
import os
import json

class MP3Player:
    def __init__(self, songs=None, background_image=None):
        """
        Initialize the MP3 player with a list of songs.
        
        Parameters:
        - songs: A list of song dictionaries, each containing 'path', 'title', 'artist', 'source', 'license', etc.
        - background_image: Optional custom background image for the MP3 player
        """
        # Initialize pygame mixer if not already done
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        
        # Songs list and current song index
        self.songs = songs or []
        self.current_song_index = 0 if self.songs else -1
        
        # Player state
        self.is_playing = False
        self.song_info = None
        if self.songs:
            self.song_info = {
                'title': self.songs[0]['title'],
                'artist': self.songs[0]['artist'],
                'source': self.songs[0].get('source', ''),
                'license': self.songs[0].get('license', '')
            }
            # Load the first song but don't start playing automatically (paused on start)
            self._load_song_without_playing()
        
        # UI tracking
        self.mp3_player_buttons = {}
        self.hovered_buttons = set()
        self.last_hover_sound_time = 0
        self.hover_sound_cooldown = 300  # ms between hover sounds
        
        # Sounds for UI interactions
        self.sounds = {}
        
        # Custom background image
        self.background_image = background_image
    
    def set_songs(self, songs):
        """Set the list of songs for the MP3 player."""
        self.songs = songs
        if songs:
            self.current_song_index = 0
            self.song_info = {
                'title': songs[0]['title'],
                'artist': songs[0]['artist'],
                'source': songs[0].get('source', ''),
                'license': songs[0].get('license', '')
            }
            # Load the first song but don't start playing (paused on start)
            self._load_song_without_playing()
        else:
            self.current_song_index = -1
            self.song_info = None
            self.is_playing = False
    
    def set_sounds(self, sounds):
        """Set the sound effects for UI interactions."""
        self.sounds = sounds
    
    def set_background_image(self, image):
        """Set a custom background image for the MP3 player."""
        self.background_image = image
    
    def _load_song_without_playing(self):
        """Load the current song without starting playback (for paused start)."""
        if not self.songs:
            print("No songs available to load")
            return
            
        try:
            # Load the current song without playing it
            current_song = self.songs[self.current_song_index]
            print(f"Loading song (paused): {current_song['path']}")
            
            # Make sure the file exists
            if not os.path.exists(current_song['path']):
                print(f"Error: Song file not found: {current_song['path']}")
                return
                
            # Load the song but don't play it
            try:
                pygame.mixer.music.load(current_song['path'])
                pygame.mixer.music.set_volume(0.5)  # Set to 50% volume
                
                # Update song info with attribution
                self.song_info = {
                    'title': current_song['title'],
                    'artist': current_song['artist'],
                    'source': current_song.get('source', ''),
                    'license': current_song.get('license', '')
                }
                
                self.is_playing = False  # Keep it paused
                print(f"Song loaded (paused): {current_song['artist']} - {current_song['title']}")
                print("🎵 Music is paused. Press 'P' or click the pause/play button to start music!")
                
                # Print attribution
                if current_song.get('source') and current_song.get('license'):
                    print(f"Attribution: {current_song['source']} | License: {current_song['license']}")
                    
            except pygame.error as e:
                print(f"Pygame error loading music: {e}")
                
        except Exception as e:
            print(f"Error loading song: {e}")
            self.is_playing = False
    
    def play_song(self):
        """Play the current song."""
        if not self.songs:
            print("No songs available to play")
            return
            
        try:
            # Stop any currently playing music
            pygame.mixer.music.stop()
            
            # Load and play the current song
            current_song = self.songs[self.current_song_index]
            print(f"Attempting to play: {current_song['path']}")
            
            # Make sure the file exists
            if not os.path.exists(current_song['path']):
                print(f"Error: Song file not found: {current_song['path']}")
                return
                
            # Load and play the song with error checking
            try:
                pygame.mixer.music.load(current_song['path'])
                pygame.mixer.music.set_volume(0.5)  # Set to 50% volume
                pygame.mixer.music.play(-1)  # -1 means loop indefinitely
                
                # Update song info with attribution
                self.song_info = {
                    'title': current_song['title'],
                    'artist': current_song['artist'],
                    'source': current_song.get('source', ''),
                    'license': current_song.get('license', '')
                }
                
                self.is_playing = True
                print(f"Now playing: {current_song['artist']} - {current_song['title']}")
                
                # Print attribution
                if current_song.get('source') and current_song.get('license'):
                    print(f"Attribution: {current_song['source']} | License: {current_song['license']}")
                    
            except pygame.error as e:
                print(f"Pygame error loading music: {e}")
                # Try alternative approach for MP3 files
                try:
                    sound = pygame.mixer.Sound(current_song['path'])
                    sound.play(-1)  # Loop indefinitely
                    self.sounds['current_song'] = sound  # Store reference to prevent garbage collection
                    self.is_playing = True
                    print(f"Playing as Sound object instead: {current_song['artist']} - {current_song['title']}")
                except Exception as alt_e:
                    print(f"Alternative playback also failed: {alt_e}")
                    
        except Exception as e:
            print(f"Error playing song: {e}")
            self.is_playing = False
    
    def pause_song(self):
        """Pause or unpause the current song."""
        if not self.songs:
            return
            
        if self.is_playing:
            pygame.mixer.music.pause()
            self.is_playing = False
            print("Music paused")
        else:
            pygame.mixer.music.unpause()
            self.is_playing = True
            print("Music resumed")
    
    def next_song(self):
        """Play the next song in the playlist."""
        if not self.songs:
            return
            
        # Move to next song
        self.current_song_index = (self.current_song_index + 1) % len(self.songs)
        if self.is_playing:
            self.play_song()
        else:
            self._load_song_without_playing()
    
    def prev_song(self):
        """Play the previous song in the playlist."""
        if not self.songs:
            return
            
        # Move to previous song
        self.current_song_index = (self.current_song_index - 1) % len(self.songs)
        if self.is_playing:
            self.play_song()
        else:
            self._load_song_without_playing()
    
    def volume_up(self):
        """Increase the volume of the music."""
        if not self.songs:
            return
            
        # Get current volume and increase it (max 1.0)
        current_volume = pygame.mixer.music.get_volume()
        new_volume = min(current_volume + 0.1, 1.0)
        pygame.mixer.music.set_volume(new_volume)
        print(f"Volume increased to {new_volume:.1f}")
    
    def volume_down(self):
        """Decrease the volume of the music."""
        if not self.songs:
            return
            
        # Get current volume and decrease it (min 0.0)
        current_volume = pygame.mixer.music.get_volume()
        new_volume = max(current_volume - 0.1, 0.0)
        pygame.mixer.music.set_volume(new_volume)
        print(f"Volume decreased to {new_volume:.1f}")
    
    def draw(self, screen, width, height):
        """Draw the MP3 player using the saved positions from UI settings."""
        if not self.songs:
            print("No songs available, not drawing MP3 player")
            return
            
        # Try to load saved positions from UI settings
        try:
            with open('ui_positions.json', 'r') as f:
                positions = json.load(f)
                
                # Get positions for each element, with fallbacks
                background_pos = positions.get("mp3_background", {"x": width - 280, "y": height - 320})
                title_pos = positions.get("mp3_title", {"x": background_pos["x"] + 100, "y": background_pos["y"] - 25})
                song_info_pos = positions.get("mp3_song_info", {"x": background_pos["x"] + 20, "y": background_pos["y"] + 30})
                
                # Get button positions
                prev_button_pos = positions.get("mp3_prev_button", {"x": background_pos["x"] + 60, "y": background_pos["y"] + 235})
                play_button_pos = positions.get("mp3_play_button", {"x": background_pos["x"] + 110, "y": background_pos["y"] + 235})
                next_button_pos = positions.get("mp3_next_button", {"x": background_pos["x"] + 160, "y": background_pos["y"] + 235})
                volume_up_pos = positions.get("mp3_volume_up", {"x": background_pos["x"] + 30, "y": background_pos["y"] + 190})
                volume_down_pos = positions.get("mp3_volume_down", {"x": background_pos["x"] + 190, "y": background_pos["y"] + 190})
                
                button_size = 28
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            # Default positions if file doesn't exist or invalid
            background_pos = {"x": width - 280, "y": height - 320}
            title_pos = {"x": background_pos["x"] + 100, "y": background_pos["y"] - 25}
            song_info_pos = {"x": background_pos["x"] + 20, "y": background_pos["y"] + 30}
            
            # Default button positions
            button_size = 28
            prev_button_pos = {"x": background_pos["x"] + 60, "y": background_pos["y"] + 235}
            play_button_pos = {"x": background_pos["x"] + 110, "y": background_pos["y"] + 235}
            next_button_pos = {"x": background_pos["x"] + 160, "y": background_pos["y"] + 235}
            volume_up_pos = {"x": background_pos["x"] + 30, "y": background_pos["y"] + 190}
            volume_down_pos = {"x": background_pos["x"] + 190, "y": background_pos["y"] + 190}
        
        # Draw background
        if self.background_image:
            scaled_bg = pygame.transform.scale(self.background_image, (260, 300))
            screen.blit(scaled_bg, (background_pos["x"], background_pos["y"]))
        else:
            # Draw semi-transparent background
            surface = pygame.Surface((260, 300), pygame.SRCALPHA)
            surface.fill((30, 30, 50, 220))
            pygame.draw.rect(surface, (150, 100, 200), (0, 0, 260, 300), 2, border_radius=10)
            screen.blit(surface, (background_pos["x"], background_pos["y"]))
        
        # Draw song info
        if self.song_info:
            song_font = pygame.font.SysFont(None, 22)
            title = self.song_info['title']
            title_text = song_font.render(f"Title: {title}", True, (255, 255, 255))
            screen.blit(title_text, (song_info_pos["x"], song_info_pos["y"]))
            
            artist = self.song_info['artist']
            artist_text = song_font.render(f"Artist: {artist}", True, (220, 220, 255))
            screen.blit(artist_text, (song_info_pos["x"], song_info_pos["y"] + 25))
        
        # Draw control buttons
        button_positions = {
            'prev': prev_button_pos,
            'play': play_button_pos,
            'next': next_button_pos,
            'volume_up': volume_up_pos,
            'volume_down': volume_down_pos
        }
        
        # Draw each button with full transparency
        for btn_type in ['prev', 'play', 'next', 'volume_up', 'volume_down']:
            button_x = button_positions[btn_type]['x']
            button_y = button_positions[btn_type]['y']
            
            # Create a transparent surface for the button
            btn_surface = pygame.Surface((button_size, button_size), pygame.SRCALPHA)
            btn_surface.fill((0, 0, 0, 0))  # Fully transparent
            
            # Draw button symbols with full transparency
            if btn_type == 'prev':
                pygame.draw.polygon(btn_surface, (0, 0, 0, 0), [
                    (button_size//2 - 2, button_size//2),
                    (10, 8),
                    (10, button_size - 8)
                ])
                pygame.draw.polygon(btn_surface, (0, 0, 0, 0), [
                    (button_size//2 - 8, button_size//2),
                    (button_size//2, 8),
                    (button_size//2, button_size - 8)
                ])
            elif btn_type == 'play':
                if self.is_playing:
                    pygame.draw.rect(btn_surface, (0, 0, 0, 0), 
                                  (9, 8, 4, button_size - 16))
                    pygame.draw.rect(btn_surface, (0, 0, 0, 0), 
                                  (16, 8, 4, button_size - 16))
                else:
                    pygame.draw.polygon(btn_surface, (0, 0, 0, 0), [
                        (10, 8),
                        (20, button_size//2),
                        (10, button_size - 8)
                    ])
            elif btn_type == 'next':
                pygame.draw.polygon(btn_surface, (0, 0, 0, 0), [
                    (button_size//2 + 2, button_size//2),
                    (button_size - 10, 8),
                    (button_size - 10, button_size - 8)
                ])
                pygame.draw.polygon(btn_surface, (0, 0, 0, 0), [
                    (button_size//2 + 8, button_size//2),
                    (button_size//2, 8),
                    (button_size//2, button_size - 8)
                ])
            elif btn_type == 'volume_up':
                # Volume up button - invisible but functional
                # No visual representation needed
                pass
            elif btn_type == 'volume_down':
                # Volume down button - invisible but functional
                # No visual representation needed
                pass
            
            # Draw the transparent button surface
            screen.blit(btn_surface, (button_x, button_y))
        
        # Store button positions for hit detection
        self.mp3_player_buttons = {
            'prev': pygame.Rect(prev_button_pos['x'], prev_button_pos['y'], button_size, button_size),
            'play': pygame.Rect(play_button_pos['x'], play_button_pos['y'], button_size, button_size),
            'next': pygame.Rect(next_button_pos['x'], next_button_pos['y'], button_size, button_size),
            'volume_up': pygame.Rect(volume_up_pos['x'], volume_up_pos['y'], button_size, button_size),
            'volume_down': pygame.Rect(volume_down_pos['x'], volume_down_pos['y'], button_size, button_size)
        }
        
        return self.mp3_player_buttons
    
    def handle_events(self, event):
        """Handle pygame events related to the MP3 player (button clicks and keyboard controls)"""
        if not self.songs:
            return False
            
        # Handle keyboard controls (work on all screens)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:  # P key for pause/play
                self.pause_song()
                return True
            elif event.key == pygame.K_RIGHTBRACKET:  # ] key for next song
                self.next_song()
                return True
            elif event.key == pygame.K_LEFTBRACKET:  # [ key for previous song
                self.prev_song()
                return True
            elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:  # + or = for volume up
                self.volume_up()
                return True
            elif event.key == pygame.K_MINUS:  # - for volume down
                self.volume_down()
                return True
            
        # Handle mouse events (only if buttons are available)
        if not self.mp3_player_buttons:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
            # Check if any MP3 player buttons were clicked
            for button_name, button_rect in self.mp3_player_buttons.items():
                if button_rect.collidepoint(event.pos):
                    # Play click sound if available
                    if 'click' in self.sounds:
                        self.sounds['click'].play()
                        
                    # Handle button actions
                    if button_name == 'play':
                        self.pause_song()
                    elif button_name == 'prev':
                        self.prev_song()
                    elif button_name == 'next':
                        self.next_song()
                    elif button_name == 'volume_up':
                        self.volume_up()
                    elif button_name == 'volume_down':
                        self.volume_down()
                    return True  # Event was handled
                    
        # Check for hovering over MP3 player buttons
        if event.type == pygame.MOUSEMOTION:
            current_time = pygame.time.get_ticks()
            currently_hovered = set()
            
            for button_name, button_rect in self.mp3_player_buttons.items():
                if button_rect.collidepoint(event.pos):
                    currently_hovered.add(button_name)
                    
                    # Play hover sound if this is a new hover and cooldown has passed
                    if (button_name not in self.hovered_buttons and 
                        'hover' in self.sounds and 
                        current_time - self.last_hover_sound_time > self.hover_sound_cooldown):
                        self.sounds['hover'].play()
                        self.last_hover_sound_time = current_time
                        
            # Update hovered buttons set
            self.hovered_buttons = currently_hovered
            
        return False  # Event wasn't handled 