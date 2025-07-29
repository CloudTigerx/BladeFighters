import pygame
import sys
import os
import math
import random
import time

# Import loading screen first
from modules.loading_module.loading_screen import LoadingScreen

# Import all extracted modules - all are working properly
from modules.audio_module import AudioSystem
from modules.settings_module import SettingsSystem
from modules.menu_module import MenuSystem
from modules.testmode_module import TestMode
from modules.screen_module import ScreenManager
from modules.story_module import StorySystem

print("✅ All extracted modules loaded successfully")

from core.puzzle_module import PuzzleEngine
from core.puzzle_renderer import PuzzleRenderer

# Constants
ASSET_PATH = "puzzleassets"
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

class GameClient:
    def __init__(self):
        """Initialize the game client."""
        # Initialize pygame
        pygame.init()
        
        # Set V-Sync environment variable at startup
        os.environ['SDL_VIDEO_VSYNC'] = '1'  # Default to V-Sync enabled
        
        # Set the asset path
        self.asset_path = ASSET_PATH
        
        # Define available resolutions (width, height)
        self.resolutions = [
            (800, 600),
            (1024, 768),
            (1280, 720),
            (1366, 768),
            (1600, 900),
            (1920, 1080)
        ]
        
        # Get desktop info for default resolution
        desktop_info = pygame.display.Info()
        desktop_width, desktop_height = desktop_info.current_w, desktop_info.current_h
        
        # Choose best resolution based on desktop size
        self.width, self.height = self.resolutions[0]  # Default to lowest
        for res in self.resolutions:
            if res[0] <= desktop_width and res[1] <= desktop_height:
                self.width, self.height = res  # Use the largest resolution that fits
        
        # Create window with default resolution
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Blade Fighters")
        
        # Initialize basic attributes
        self.font = None
        self.audio = None
        self.menu_system = None
        self.settings_system = None
        self.test_mode = None
        self.screen_manager = None
        self.story_system = None
        self.puzzle_engine = None
        self.puzzle_renderer = None
        
        # Game state
        self.game_running = True
        self.version = "1.0.0"
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GRAY = (100, 100, 100)
        self.LIGHT_GRAY = (200, 200, 200)
        self.BLUE = (0, 100, 255)
        self.LIGHT_BLUE = (100, 150, 255)
        
        # Story content view variables
        self.story_scroll_position = 0
        self.current_story = {"title": "No Story Selected", "content": []}
        
        # Background images (will be loaded during initialization)
        self.main_background = None
        self.puzzle_background = None
        self.story_background = None
        
        # Current screen (will be set after loading)
        self.current_screen = "loading"
        
        # Initialize brightness setting
        self.brightness = 1.0  # Default brightness
    
    def _initialize_font(self):
        """Initialize the font system."""
        try:
            font_path = os.path.join(ASSET_PATH, "fonts", "PermanentMarker-Regular.ttf")
            if os.path.exists(font_path):
                self.font = pygame.font.Font(font_path, 36)
                print(f"✅ Loaded PermanentMarker font from: {font_path}")
            else:
                self.font = pygame.font.SysFont('Arial', 36)
                print("⚠️ PermanentMarker font not found, using Arial fallback")
        except Exception as e:
            self.font = pygame.font.SysFont('Arial', 36)
            print(f"⚠️ Error loading PermanentMarker font: {e}, using Arial fallback")
    
    def _initialize_audio_system(self):
        """Initialize the audio system."""
        self.audio = AudioSystem(ASSET_PATH)
        print("✅ Audio system initialized")
    
    def _initialize_menu_system(self):
        """Initialize the menu system."""
        self.menu_system = MenuSystem(self.screen, self.font, self.audio, self.asset_path)
        print("✅ Menu system initialized")
    
    def _initialize_settings_system(self):
        """Initialize the settings system."""
        self.settings_system = SettingsSystem(self.screen, self.font, self.audio, self.asset_path, self)
        print("✅ Settings system initialized")
    
    def _initialize_test_mode(self):
        """Initialize the test mode."""
        self.test_mode = TestMode(self.screen, self.font, self.audio, self.asset_path, self.settings_system)
        print("✅ Test mode initialized")
    
    def _initialize_screen_manager(self):
        """Initialize the screen manager."""
        self.screen_manager = ScreenManager(self.screen, self.font, self.width, self.height)
        print("✅ Screen manager initialized")
    
    def _initialize_story_system(self):
        """Initialize the story system."""
        self.story_system = StorySystem(self.screen, self.font, self.width, self.height, self.menu_system)
        print("✅ Story system initialized")
    
    def _initialize_puzzle_engine(self):
        """Initialize the puzzle engine."""
        self.puzzle_engine = PuzzleEngine(self.screen, self.font, self.audio, self.asset_path, self.settings_system)
        print("✅ Puzzle engine initialized")
    
    def _initialize_puzzle_renderer(self):
        """Initialize the puzzle renderer."""
        self.puzzle_renderer = PuzzleRenderer(self.puzzle_engine)
        print("✅ Puzzle renderer initialized")
    
    def _load_background_images(self):
        """Load background images."""
        try:
            self.main_background = pygame.image.load(os.path.join(ASSET_PATH, "colorful.png"))
            print("✅ Loaded main background")
        except pygame.error:
            self.main_background = None
            print("⚠️ Failed to load main background")
        
        try:
            self.puzzle_background = pygame.image.load(os.path.join(ASSET_PATH, "bkg.png"))
            print("✅ Loaded puzzle background")
        except pygame.error:
            self.puzzle_background = None
            print("⚠️ Failed to load puzzle background")
        
        try:
            self.story_background = pygame.image.load(os.path.join(ASSET_PATH, "storybackground.png"))
            print("✅ Loaded story background")
        except pygame.error:
            self.story_background = None
            print("⚠️ Failed to load story background")
    
    def _complete_initialization(self):
        """Complete the initialization process."""
        self.current_screen = "main_menu"
        print("✅ Game initialization complete!")

    
    def set_screen(self, screen_name):
        """Set the current screen."""
        # Use screen manager if available
        if hasattr(self, 'screen_manager') and self.screen_manager:
            self.screen_manager.set_screen(screen_name)
            self.current_screen = self.screen_manager.get_current_screen()
        else:
            # Legacy screen management
            print(f"Game Client: Setting screen to {screen_name}")
            self.current_screen = screen_name
        
        # Screen-specific initialization
        if screen_name == "settings":
            print("Game Client: Initializing settings system")
            if hasattr(self, 'settings_system') and self.settings_system:
                self.settings_system.show()
        elif screen_name == "ui_editor":
            print("Game Client: Switching to UI editor")
            # if hasattr(self, 'settings_system') and self.settings_system: # REMOVED: Settings system being stripped out
            #     self.settings_system.set_screen("ui_editor") # REMOVED: Settings system being stripped out
        elif screen_name == "test":
            if hasattr(self, 'test_mode') and self.test_mode:
                self.test_mode.initialize_test()
                # Reload UI positions to ensure the latest positions are used
                self.test_mode.setup_board_positions()
        elif screen_name == "main_menu" and hasattr(self, 'test_mode') and self.test_mode:
            # Make sure the test mode has the latest UI positions when going back to main menu
            self.test_mode.setup_board_positions()
        elif screen_name == "game":
            self.puzzle_engine.start_game()
    


    
    def draw_placeholder_settings(self):
        """Draw a placeholder 'Coming Soon' settings screen."""
        # Fill with dark gradient background
        self.screen.fill((20, 20, 50))
        
        # Draw "Settings Coming Soon" message
        title_font = pygame.font.SysFont('Arial', 64, bold=True)
        title_text = title_font.render("Settings Coming Soon", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.width//2, self.height//2 - 100))
        self.screen.blit(title_text, title_rect)
        
        # Draw subtitle
        subtitle_font = pygame.font.SysFont('Arial', 32)
        subtitle_text = subtitle_font.render("The settings system is being redesigned", True, (200, 200, 200))
        subtitle_rect = subtitle_text.get_rect(center=(self.width//2, self.height//2 - 40))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Draw instructions
        instruction_font = pygame.font.SysFont('Arial', 28)
        instruction_text = instruction_font.render("Press ESC or click anywhere to return to main menu", True, (150, 150, 150))
        instruction_rect = instruction_text.get_rect(center=(self.width//2, self.height//2 + 50))
        self.screen.blit(instruction_text, instruction_rect)
        
        # Draw a nice border around the whole message
        border_rect = pygame.Rect(self.width//2 - 400, self.height//2 - 150, 800, 250)
        pygame.draw.rect(self.screen, (100, 100, 255), border_rect, 3, border_radius=10)
        
        # Add some visual flair with a subtle glow effect
        glow_rect = pygame.Rect(self.width//2 - 405, self.height//2 - 155, 810, 260)
        pygame.draw.rect(self.screen, (50, 50, 150), glow_rect, 2, border_radius=12)
    
    def change_resolution(self, width, height):
        """Change the game's resolution."""
        # Update the screen dimensions
        self.width = width
        self.height = height
        
        # Update the display mode
        self.screen = pygame.display.set_mode((self.width, self.height))
        
        # Update menu system with new screen
        if hasattr(self, 'menu_system') and self.menu_system:
            self.menu_system.screen = self.screen
        
        # Update settings system with new screen
        # if hasattr(self, 'settings_system') and self.settings_system: # REMOVED: Settings system being stripped out
        #     self.settings_system.screen = self.screen # REMOVED: Settings system being stripped out
        #     self.settings_system.width = self.width # REMOVED: Settings system being stripped out
        #     self.settings_system.height = self.height # REMOVED: Settings system being stripped out
        
        # Update screen manager with new resolution
        if hasattr(self, 'screen_manager') and self.screen_manager:
            self.screen_manager.handle_resolution_change(width, height)
        
        # Update story system with new resolution
        if hasattr(self, 'story_system') and self.story_system:
            self.story_system.update_resolution(width, height)
        
        # If we're in test mode, update the board positions
        if hasattr(self, 'test_mode'):
            self.test_mode.setup_board_positions()
        
        # Play click sound if available
        if hasattr(self.audio, 'sounds') and 'click' in self.audio.sounds:
            self.audio.sounds['click'].play()
    
    def start_quickplay(self):
        """Start the game in quickplay mode."""
        print("Starting quickplay mode")
        self.set_screen("game")
        self.puzzle_renderer.preview_side = 'left' # Configure for single player
        self.puzzle_engine.start_game()
    

    

    
    def display_custom_mp3_player(self):
        """Display only the custom MP3 player image with functional buttons."""
        if not hasattr(self.audio, 'mp3_player') or not self.audio.mp3_player:
            return
        
        # Simply use the MP3 player's own draw method
        # This will draw the MP3 player with consistent button positioning
        self.mp3_player_buttons = self.audio.mp3_player.draw(self.screen, self.width, self.height)
        
        return self.mp3_player_buttons
    
    def get_brightness(self) -> float:
        """Get the current brightness setting."""
        if hasattr(self, 'settings_system') and self.settings_system:
            return self.settings_system.get_setting('brightness')
        return 1.0  # Default brightness
    
    def apply_brightness_to_surface(self, surface: pygame.Surface) -> pygame.Surface:
        """Apply brightness adjustment to a surface."""
        brightness = self.get_brightness()
        if brightness == 1.0:
            return surface  # No adjustment needed
        
        # Create a copy of the surface to avoid modifying the original
        adjusted_surface = surface.copy()
        
        # Create a brightness overlay
        brightness_overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        
        # Calculate the darkness level (1.0 = no change, 0.0 = completely black)
        darkness = 1.0 - brightness
        alpha = int(255 * darkness)
        
        # Fill with black with appropriate alpha for darkening
        brightness_overlay.fill((0, 0, 0, alpha))
        
        # Apply the overlay using BLEND_MULT for darkening effect
        adjusted_surface.blit(brightness_overlay, (0, 0), special_flags=pygame.BLEND_MULT)
        
        return adjusted_surface
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode."""
        try:
            # Get current display info
            info = pygame.display.Info()
            
            # Toggle fullscreen flag
            if pygame.display.get_surface().get_flags() & pygame.FULLSCREEN:
                # Currently fullscreen, switch to windowed
                self.screen = pygame.display.set_mode((self.width, self.height))
                print("🖥️ Switched to windowed mode")
            else:
                # Currently windowed, switch to fullscreen
                self.screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
                print("🖥️ Switched to fullscreen mode")
            
            # Update screen references in other systems
            if hasattr(self, 'settings_system') and self.settings_system:
                self.settings_system.screen = self.screen
            if hasattr(self, 'menu_system') and self.menu_system:
                self.menu_system.screen = self.screen
            if hasattr(self, 'puzzle_engine') and self.puzzle_engine:
                self.puzzle_engine.screen = self.screen
            if hasattr(self, 'puzzle_renderer') and self.puzzle_renderer:
                self.puzzle_renderer.screen = self.screen
            
        except Exception as e:
            print(f"❌ Error toggling fullscreen: {e}")
    
    def get_mouse_sensitivity(self) -> float:
        """Get the current mouse sensitivity setting."""
        if hasattr(self, 'settings_system') and self.settings_system:
            return self.settings_system.get_setting('sensitivity')
        return 1.0  # Default sensitivity
    
    def toggle_vsync(self):
        """Toggle V-Sync mode using environment variables and display flags."""
        try:
            # Get current V-Sync state from settings
            current_vsync = self.settings_system.get_setting('vsync') if hasattr(self, 'settings_system') else True
            
            if current_vsync:
                # Disable V-Sync
                os.environ['SDL_VIDEO_VSYNC'] = '0'
                # Recreate display without V-Sync flags
                self.screen = pygame.display.set_mode((self.width, self.height), pygame.HWSURFACE)
                print("🔄 V-Sync disabled")
            else:
                # Enable V-Sync
                os.environ['SDL_VIDEO_VSYNC'] = '1'
                # Recreate display with V-Sync flags
                self.screen = pygame.display.set_mode((self.width, self.height), pygame.HWSURFACE | pygame.DOUBLEBUF)
                print("🔄 V-Sync enabled")
            
            # Update screen references in other systems
            if hasattr(self, 'settings_system') and self.settings_system:
                self.settings_system.screen = self.screen
            if hasattr(self, 'menu_system') and self.menu_system:
                self.menu_system.screen = self.screen
            if hasattr(self, 'puzzle_engine') and self.puzzle_engine:
                self.puzzle_engine.screen = self.screen
            if hasattr(self, 'puzzle_renderer') and self.puzzle_renderer:
                self.puzzle_renderer.screen = self.screen
                
        except Exception as e:
            print(f"❌ Error toggling V-Sync: {e}")
            print("💡 Note: V-Sync control may be limited by your graphics driver")
    
    def check_vsync_status(self) -> bool:
        """Check if V-Sync is currently enabled."""
        try:
            # Check environment variable
            vsync_env = os.environ.get('SDL_VIDEO_VSYNC', '0')
            return vsync_env == '1'
        except:
            return False
    
    def set_particle_effects(self, enabled: bool):
        """Enable or disable particle effects."""
        try:
            # Set particle effects in the puzzle renderer if available
            if hasattr(self, 'puzzle_renderer') and self.puzzle_renderer:
                if hasattr(self.puzzle_renderer, 'animation_renderer'):
                    # Store the setting for the renderer to use
                    self.puzzle_renderer.animation_renderer.particle_effects_enabled = enabled
                    print(f"✨ Particle effects {'enabled' if enabled else 'disabled'}")
        except Exception as e:
            print(f"❌ Error setting particle effects: {e}")
    
    def handle_mp3_player_click(self, pos):
        """Handle clicks on the custom MP3 player buttons."""
        if not hasattr(self, 'mp3_player_buttons') or not self.mp3_player_buttons:
            return False
        
        # Check if any button was clicked
        for btn_name, btn_rect in self.mp3_player_buttons.items():
            if btn_rect.collidepoint(pos):
                # Play click sound if available
                if hasattr(self.audio, 'sounds') and 'click' in self.audio.sounds:
                    self.audio.sounds['click'].play()
                
                # Handle button actions using the audio system's MP3 player
                if hasattr(self.audio, 'mp3_player'):
                    if btn_name == 'play':
                        self.audio.mp3_player.pause_song()  # Toggle play/pause
                    elif btn_name == 'prev':
                        self.audio.mp3_player.prev_song()
                    elif btn_name == 'next':
                        self.audio.mp3_player.next_song()
                        
                return True  # Click was handled
                
        return False  # Click was not on any MP3 player button
    
    def show_game_over_screen(self):
        """Display a dramatic game over screen."""
        # Create a semi-transparent black overlay
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Black with 180/255 alpha
        self.screen.blit(overlay, (0, 0))
        
        # Create a dramatic "GAME OVER" text with red glow effect
        game_over_font = pygame.font.SysFont(None, 72)
        game_over_text = game_over_font.render("GAME OVER", True, (255, 0, 0))
        game_over_rect = game_over_text.get_rect(center=(self.width // 2, self.height // 2))
        
        # Draw glow effect
        glow_surface = pygame.Surface((game_over_text.get_width() + 20, game_over_text.get_height() + 20), pygame.SRCALPHA)
        for i in range(10):
            alpha = 100 - (i * 10)
            glow_text = game_over_font.render("GAME OVER", True, (255, 0, 0))
            glow_rect = glow_text.get_rect(center=(glow_surface.get_width() // 2, glow_surface.get_height() // 2))
            glow_surface.blit(glow_text, glow_rect)
        self.screen.blit(glow_surface, (game_over_rect.x - 10, game_over_rect.y - 10))
        
        # Draw the main text
        self.screen.blit(game_over_text, game_over_rect)
        
        # Draw instruction text
        instruction_font = pygame.font.SysFont(None, 36)
        instruction_text = instruction_font.render("Press ESC to return to main menu", True, self.WHITE)
        instruction_rect = instruction_text.get_rect(center=(self.width // 2, self.height // 2 + 60))
        self.screen.blit(instruction_text, instruction_rect)
        
        # Update the display
        pygame.display.flip()
        
        # Wait for 2 seconds before returning to main menu
        pygame.time.wait(2000)
        
        # Return to main menu
        self.set_screen("main_menu")

    def run(self):
        """Main loop for the application."""
        # Set up the clock
        clock = pygame.time.Clock()
        
        # Create loading screen
        loading_screen = LoadingScreen(self.screen, self.asset_path)
        
        # Define loading tasks
        loading_tasks = [
            ("Loading Font System", self._initialize_font),
            ("Initializing Audio System", self._initialize_audio_system),
            ("Loading Background Images", self._load_background_images),
            ("Initializing Menu System", self._initialize_menu_system),
            ("Initializing Settings System", self._initialize_settings_system),
            ("Initializing Test Mode", self._initialize_test_mode),
            ("Initializing Screen Manager", self._initialize_screen_manager),
            ("Initializing Story System", self._initialize_story_system),
            ("Initializing Puzzle Engine", self._initialize_puzzle_engine),
            ("Initializing Puzzle Renderer", self._initialize_puzzle_renderer),
            ("Finalizing Setup", self._complete_initialization)
        ]
        
        # Start loading process
        loading_screen.start_loading(loading_tasks, on_complete=lambda: None)
        
        try:
            # Main game loop
            while self.game_running:
                # Get all events
                events = pygame.event.get()
                
                # Process window close events
                for event in events:
                    if event.type == pygame.QUIT:
                        # Save UI positions before closing
                        # if hasattr(self, 'settings_system') and self.settings_system and hasattr(self.settings_system, 'ui_editor') and self.settings_system.ui_editor: # REMOVED: Settings system being stripped out
                        #     self.settings_system.ui_editor.save_positions() # REMOVED: Settings system being stripped out
                        self.game_running = False
                    elif event.type == pygame.VIDEORESIZE:
                        # Update resolution if the window is resized
                        self.change_resolution(event.w, event.h)
                    # Handle mouse clicks for MP3 player buttons
                    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
                        # Check if click was on MP3 player buttons
                        if hasattr(self, 'mp3_player_buttons') and self.mp3_player_buttons:
                            if self.handle_mp3_player_click(event.pos):
                                # Click was handled by MP3 player, no need to process it further
                                continue
                    # Prevent escape from closing the game in main menu
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and self.current_screen == "main_menu":
                        continue
                    
                    # Let the audio system handle any audio-related events
                    if hasattr(self, 'audio') and self.audio:
                        self.audio.handle_audio_events(event)
                
                # Process events and update/draw the current screen
                if self.current_screen == "main_menu":
                    # Filter out escape key events in main menu BEFORE processing any events
                    filtered_events = []
                    for event in events:
                        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                            continue
                        filtered_events.append(event)
                    events = filtered_events
                    
                    # Process menu events with filtered event list
                    if hasattr(self, 'menu_system') and self.menu_system:
                        menu_action = self.menu_system.process_main_menu_events(events)
                        
                        # Handle menu actions
                        if menu_action == "quickplay":
                            self.set_screen("game")
                        elif menu_action == "settings":
                            self.set_screen("settings")
                        elif menu_action == "story":
                            self.set_screen("story")
                        elif menu_action == "test":
                            self.set_screen("test")
                        elif menu_action == "quit":
                            self.game_running = False
                        
                        # Draw the main menu
                        self.main_menu_buttons = self.menu_system.draw_main_menu(
                            on_start_action=self.start_quickplay,
                            on_settings_action=lambda: self.set_screen("settings"),
                            on_story_action=lambda: self.set_screen("story"),
                            on_test_action=lambda: self.set_screen("test"),
                            version=self.version
                        )
                    else:
                        # Fallback if menu system is not available
                        self.screen.fill(self.BLACK)
                        error_text = self.font.render("Menu system not available", True, self.WHITE)
                        error_rect = error_text.get_rect(center=(self.width // 2, self.height // 2))
                        self.screen.blit(error_text, error_rect)
                        
                        # Handle escape key to quit
                        for event in events:
                            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                                self.game_running = False
                    

                
                elif self.current_screen == "test":
                    if hasattr(self, 'test_mode') and self.test_mode:
                        # Process test mode events
                        test_action = self.test_mode.process_events(events)
                        
                        # Handle test mode actions
                        if test_action == "back_to_menu":
                            self.set_screen("main_menu")
                        
                        # Update the test mode
                        test_update_result = self.test_mode.update()
                        
                        # Handle game over state
                        if test_update_result == "game_over":
                            self.show_game_over_screen()
                            continue
                        
                        # Draw the test mode screen
                        self.test_mode.draw()
                        

                    else:
                        # Fallback if test mode is not available
                        self.screen.fill(self.BLACK)
                        error_text = self.font.render("Test mode not available", True, self.WHITE)
                        error_rect = error_text.get_rect(center=(self.width // 2, self.height // 2))
                        self.screen.blit(error_text, error_rect)
                        
                        # Handle escape key to go back
                        for event in events:
                            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                                self.set_screen("main_menu")
                
                elif self.current_screen == "story":
                    # Process story menu events
                    if hasattr(self, 'menu_system') and self.menu_system:
                        story_action = self.menu_system.process_story_menu_events(events)
                        
                        # Handle story menu actions
                        if story_action == "back":
                            self.set_screen("main_menu")
                        elif isinstance(story_action, str) and story_action.startswith("story:"):
                            # Extract story ID from action string
                            story_id = int(story_action.split(":")[1])
                            print(f"Selected story {story_id}")
                            # Load and display the selected story
                            if hasattr(self, 'story_system') and self.story_system:
                                self.current_story = self.story_system.load_story(story_id)
                            else:
                                self.load_story(story_id)
                            self.set_screen("story_content")
                        
                        # Draw the story menu
                        self.menu_system.draw_story_menu(
                            on_back_action=lambda: self.set_screen("main_menu")
                        )
                    else:
                        # Fallback if menu system is not available
                        self.screen.fill(self.BLACK)
                        error_text = self.font.render("Story menu not available", True, self.WHITE)
                        error_rect = error_text.get_rect(center=(self.width // 2, self.height // 2))
                        self.screen.blit(error_text, error_rect)
                        
                        # Handle escape key to go back
                        for event in events:
                            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                                self.set_screen("main_menu")
                    

                
                elif self.current_screen == "story_content":
                    # Use extracted story system if available
                    if hasattr(self, 'story_system') and self.story_system:
                        # Handle story events using the story system
                        story_action, new_scroll_position = self.story_system.handle_story_events(events, self.story_scroll_position)
                        self.story_scroll_position = new_scroll_position
                        
                        # Handle story actions
                        if story_action == "back_to_story":
                            self.set_screen("story")
                        
                        # Display the story content using the story system
                        self.story_scroll_position = self.story_system.display_story_content(self.current_story, self.story_scroll_position)
                    else:
                        # Legacy story content handling
                        for event in events:
                            if event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_ESCAPE:
                                    self.set_screen("story")
                                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                                    # Scroll down
                                    self.story_scroll_position += 20
                                elif event.key == pygame.K_UP or event.key == pygame.K_w:
                                    # Scroll up (with limit to prevent scrolling above the top)
                                    self.story_scroll_position = max(0, self.story_scroll_position - 20)
                            elif event.type == pygame.MOUSEBUTTONDOWN:
                                if event.button == 4:  # Mouse wheel up
                                    self.story_scroll_position = max(0, self.story_scroll_position - 40)
                                elif event.button == 5:  # Mouse wheel down
                                    self.story_scroll_position += 40
                        
                        # Display the story content using legacy method
                        self.display_story_content()
                    

                
                elif self.current_screen == "settings":
                    # Update settings system
                    current_time = time.time()
                    delta_time = current_time - getattr(self, 'last_settings_time', current_time)
                    self.last_settings_time = current_time
                    
                    if hasattr(self, 'settings_system') and self.settings_system:
                        self.settings_system.update(delta_time)
                        self.settings_system.draw()
                    
                    # Handle events for settings screen
                    for event in events:
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            # Handle UI interactions
                            if hasattr(self, 'settings_system') and self.settings_system:
                                self.settings_system.handle_click(event.pos)
                        elif event.type == pygame.MOUSEBUTTONUP:
                            if hasattr(self, 'settings_system') and self.settings_system:
                                self.settings_system.handle_mouse_release()
                        elif event.type == pygame.MOUSEMOTION:
                            if hasattr(self, 'settings_system') and self.settings_system:
                                self.settings_system.handle_mouse_move(event.pos)
                                if event.buttons[0]:  # Left mouse button is pressed
                                    self.settings_system.handle_mouse_drag(event.pos)
                                # Handle control screen mouse movement
                                if self.settings_system.showing_controls:
                                    self.settings_system.handle_control_mouse_move(event.pos)
                        elif event.type == pygame.KEYDOWN:
                            # Handle control rebinding
                            if hasattr(self, 'settings_system') and self.settings_system:
                                if self.settings_system.showing_controls and self.settings_system.waiting_for_key:
                                    self.settings_system.handle_key_input(event.key)
                                elif event.key == pygame.K_ESCAPE:
                                    # Return from control screen to settings
                                    if self.settings_system.showing_controls:
                                        self.settings_system.hide_controls_screen()
                                        # Don't continue to other checks - stay in settings
                                    # Return from settings to main menu
                                    elif self.current_screen == "settings":
                                        self.set_screen("main_menu")
                                    # Return from main menu (exit game)
                                    elif self.current_screen == "main_menu":
                                        self.game_running = False
                            
                            # Handle music controls using custom mappings
                            if hasattr(self, 'settings_system') and self.settings_system and hasattr(self, 'audio') and self.audio:
                                if event.key == self.settings_system.get_control('music_next'):
                                    if hasattr(self.audio, 'mp3_player'):
                                        self.audio.mp3_player.next_song()
                                        print("⏭️ Next song")
                                elif event.key == self.settings_system.get_control('music_prev'):
                                    if hasattr(self.audio, 'mp3_player'):
                                        self.audio.mp3_player.prev_song()
                                        print("⏮️ Previous song")
                                elif event.key == self.settings_system.get_control('music_pause'):
                                    if hasattr(self.audio, 'mp3_player'):
                                        self.audio.mp3_player.pause_song()
                                        print("⏸️ Music pause/play")
                

                
                elif self.current_screen == "game":
                    # Process game events
                    game_action = self.puzzle_engine.process_events(events)
                    
                    # Handle game actions
                    if game_action == "back_to_menu":
                        self.set_screen("main_menu")
                    
                    # Update game timing
                    current_time = time.time()
                    if not hasattr(self, 'last_frame_time'):
                        self.last_frame_time = current_time
                    self.last_frame_time = current_time
                    
                    # Update game state
                    self.puzzle_engine.update()
                    
                    # Update renderer animations
                    self.puzzle_renderer.update_visual_state()
                    self.puzzle_renderer.update_animations()
                    
                    # Draw the game using our renderer
                    self.puzzle_renderer.draw_game_screen()
                    

                
                # Display MP3 player on all screens
                if hasattr(self, 'audio') and self.audio:
                    self.display_custom_mp3_player()
                
                # Update the display
                pygame.display.flip()
                
                # Cap the frame rate
                clock.tick(60)
        except KeyboardInterrupt:
            print("Game interrupted by user")
        except Exception as e:
            print(f"Error occurred: {e}")
        finally:
            # Clean up
            pygame.quit()
            sys.exit()
            
    def load_story(self, story_id):
        """Load story content from file based on story ID (legacy fallback method)."""
        # Use extracted story system if available
        if hasattr(self, 'story_system') and self.story_system:
            self.current_story = self.story_system.load_story(story_id)
            self.story_scroll_position = 0
        else:
            # Simple fallback
            self.current_story = {
                "title": f"Story {story_id}",
                "content": ["Story system not available.", "Please check system configuration."]
            }
            self.story_scroll_position = 0
        
    def display_story_content(self):
        """Display the current story content with scrolling (legacy fallback)."""
        # Simple fallback display
        self.screen.fill(self.BLACK)
        
        # Draw title
        title_font = pygame.font.SysFont(None, 56)
        title_surf = title_font.render(self.current_story["title"], True, self.WHITE)
        title_rect = title_surf.get_rect(midtop=(self.width // 2, 50))
        self.screen.blit(title_surf, title_rect)
        
        # Draw simple content
        text_font = pygame.font.SysFont(None, 24)
        y_offset = title_rect.bottom + 50
        for line in self.current_story["content"][:10]:  # Limit to first 10 lines
            if line:
                surf = text_font.render(line, True, self.WHITE)
                rect = surf.get_rect(topleft=(50, y_offset))
                self.screen.blit(surf, rect)
                y_offset += 30
        
        # Draw instruction
        instruction_font = pygame.font.SysFont(None, 20)
        instruction_surf = instruction_font.render("Press ESC to return to story menu.", True, self.LIGHT_GRAY)
        instruction_rect = instruction_surf.get_rect(midbottom=(self.width // 2, self.height - 10))
        self.screen.blit(instruction_surf, instruction_rect)

if __name__ == "__main__":
    client = GameClient()
    client.run() 