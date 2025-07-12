import pygame
import sys
import os
import math
import random
import time
import argparse
import json

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
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
ASSET_PATH = "puzzleassets"
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

class GameClient:
    def __init__(self):
        """Initialize the game client."""
        # Initialize pygame
        pygame.init()
        
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
        
        # Create font
        self.font = pygame.font.SysFont('Arial', 36)
        
        # Initialize audio system
        self.audio = AudioSystem(ASSET_PATH)
        
        # Create menu system
        self.menu_system = MenuSystem(self.screen, self.font, self.audio, self.asset_path)
        
        # Create test mode first
        self.test_mode = TestMode(self.screen, self.font, self.audio, self.asset_path)
        
        # Create settings system
        self.settings_system = SettingsSystem(self.screen, self.font, self.audio, self.asset_path)
        
        # Create screen manager
        self.screen_manager = ScreenManager(self.screen, self.font, self.width, self.height)
        
        # Create story system
        self.story_system = StorySystem(self.screen, self.font, self.width, self.height, self.menu_system)
        
        # Create puzzle engine
        parser = argparse.ArgumentParser()
        parser.add_argument('--debug', action='store_true', help='Enable debugging mode')
        args = parser.parse_args()

        if args.debug:
            # This line was removed as per the edit hint to remove legacy TestMode
            # self.puzzle_engine = DebuggingPuzzleEngine(self.screen, self.font, self.audio, self.asset_path)
            pass # No debugging engine defined in the new_code
        else:
            self.puzzle_engine = PuzzleEngine(self.screen, self.font, self.audio, self.asset_path)
        
        # Create puzzle renderer
        self.puzzle_renderer = PuzzleRenderer(self.puzzle_engine)
        
        # Current screen (main_menu, settings, game)
        self.current_screen = "main_menu"
        
        # Game state
        self.game_running = True
        
        # Game version
        self.version = "1.0.0"
        
        # Story content view variables
        self.story_scroll_position = 0
        self.current_story = {"title": "No Story Selected", "content": []}
        
        # Load background images
        try:
            self.main_background = pygame.image.load(os.path.join(ASSET_PATH, "colorful.png"))
        except pygame.error:
            self.main_background = None
            
        try:
            self.settings_background = pygame.image.load(os.path.join(ROOT_PATH, "settingsbcg.jfif"))
        except pygame.error:
            self.settings_background = None
            
        try:
            self.puzzle_background = pygame.image.load(os.path.join(ASSET_PATH, "bkg.png"))
        except pygame.error:
            self.puzzle_background = None
            
        try:
            self.story_background = pygame.image.load(os.path.join(ASSET_PATH, "storybackground.png"))
        except pygame.error:
            self.story_background = None
        
        # Menu particles for visual effects
        self.menu_particles = []
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GRAY = (100, 100, 100)
        self.LIGHT_GRAY = (200, 200, 200)
        self.BLUE = (0, 100, 255)
        self.LIGHT_BLUE = (100, 150, 255)
        
        # Border glow colors
        self.GLOW_COLORS = [
            (210, 100, 240),  # Bright Purple
            (180, 60, 220),   # Medium Purple
            (150, 40, 200),   # Dark Purple
            (220, 120, 255)   # Pink-Purple
        ]
        self.glow_index = 0
        self.glow_direction = 1
        self.glow_intensity = 0.6
        self.glow_speed = 0.03
        
    def create_button(self, x, y, width, height, text, action=None, params=None):
        """Create a button with text and optional action."""
        button = {
            "rect": pygame.Rect(x, y, width, height),
            "text": text,
            "action": action,
            "params": params,
            "hover": False
        }
        
        # Draw the button
        pygame.draw.rect(self.screen, self.GRAY, button["rect"])
        pygame.draw.rect(self.screen, self.LIGHT_GRAY, button["rect"], 2)
        
        # Draw button text
        text_surf = self.font.render(text, True, self.WHITE)
        text_rect = text_surf.get_rect(center=button["rect"].center)
        self.screen.blit(text_surf, text_rect)
        
        return button
    
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
                self.settings_system = SettingsSystem(self.screen, self.font, self.audio, self.asset_path)
        elif screen_name == "ui_editor":
            print("Game Client: Switching to UI editor")
            if hasattr(self, 'settings_system') and self.settings_system:
                self.settings_system.set_screen("ui_editor")
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
    
    def update_menu_particles(self):
        """Update the menu particles position and life."""
        # Create new particles occasionally
        if random.random() < 0.1 and len(self.menu_particles) < 50:
            particle = {
                "x": random.randint(0, self.width),
                "y": random.randint(0, self.height),
                "size": random.randint(2, 5),
                "speed": random.uniform(0.5, 2.0),
                "angle": random.uniform(0, 2 * math.pi),
                "color": random.choice(self.GLOW_COLORS),
                "life": random.randint(60, 180)  # Frames of life
            }
            self.menu_particles.append(particle)
        
        # Update existing particles
        for particle in self.menu_particles[:]:
            # Move the particle
            particle["x"] += math.cos(particle["angle"]) * particle["speed"]
            particle["y"] += math.sin(particle["angle"]) * particle["speed"]
            
            # Reduce life
            particle["life"] -= 1
            
            # Remove if it's off-screen or dead
            if (particle["x"] < 0 or particle["x"] > self.width or
                particle["y"] < 0 or particle["y"] > self.height or
                particle["life"] <= 0):
                self.menu_particles.remove(particle)
    
    def draw_menu_particles(self):
        """Draw menu particles on the screen."""
        for particle in self.menu_particles:
            # Calculate opacity based on remaining life
            alpha = int(255 * (particle["life"] / 180.0))
            color = list(particle["color"])
            
            # Create a surface with per-pixel alpha
            surf = pygame.Surface((particle["size"], particle["size"]), pygame.SRCALPHA)
            surf.fill((color[0], color[1], color[2], alpha))
            
            # Draw the particle
            self.screen.blit(surf, (int(particle["x"]), int(particle["y"])))
    
    def draw_main_menu(self):
        """Draw the main menu screen."""
        # Draw background
        if self.main_background:
            # Scale to fit screen
            scaled_bg = pygame.transform.scale(self.main_background, (self.width, self.height))
            self.screen.blit(scaled_bg, (0, 0))
        else:
            # Use a solid color if no background image
            gradient_rect = pygame.Rect(0, 0, self.width, self.height)
            pygame.draw.rect(self.screen, (20, 20, 50), gradient_rect)
        
        # Add some animated particles in the background
        self.draw_menu_particles()
        
        # Calculate button positions based on screen size
        button_width = 300
        button_height = 50
        button_margin = 20
        start_y = self.height // 3
        
        # Create buttons if they don't exist
        if not hasattr(self, 'main_menu_buttons'):
            self.main_menu_buttons = []
            
            # Clear any existing buttons
            self.main_menu_buttons = []
            
            # Center buttons horizontally
            button_x = (self.width - button_width) // 2
            
            # Play Game button
            play_button = self.create_button(
                button_x, start_y,
                button_width, button_height,
                "Play Game", self.start_quickplay
            )
            self.main_menu_buttons.append(play_button)
            
            # Settings button
            settings_button = self.create_button(
                button_x, start_y + button_height + button_margin,
                button_width, button_height,
                "Settings", self.set_screen, ["settings"]
            )
            self.main_menu_buttons.append(settings_button)
            
            # Story button
            story_button = self.create_button(
                button_x, start_y + (button_height + button_margin) * 2,
                button_width, button_height,
                "Story", self.set_screen, ["story"]
            )
            self.main_menu_buttons.append(story_button)
            
            # Test button
            test_button = self.create_button(
                button_x, start_y + (button_height + button_margin) * 3,
                button_width, button_height,
                "Test", self.set_screen, ["test"]
            )
            self.main_menu_buttons.append(test_button)
            
            # Quit button
            quit_button = self.create_button(
                button_x, start_y + (button_height + button_margin) * 4,
                button_width, button_height,
                "Quit", sys.exit
            )
            self.main_menu_buttons.append(quit_button)
        
        # Draw each button and check for hover
        mouse_pos = pygame.mouse.get_pos()
        for button in self.main_menu_buttons:
            # Determine if the mouse is hovering over this button
            button["hover"] = button["rect"].collidepoint(mouse_pos)
            
            # Change color based on hover state
            color = self.LIGHT_BLUE if button["hover"] else self.BLUE
            
            # Draw button background
            pygame.draw.rect(self.screen, color, button["rect"])
            
            # Draw border with glow effect if hovering
            if button["hover"]:
                # Draw glowing border
                glow_color = self.GLOW_COLORS[self.glow_index]
                pygame.draw.rect(self.screen, glow_color, button["rect"], 3)
            else:
                # Draw normal border
                pygame.draw.rect(self.screen, self.WHITE, button["rect"], 2)
            
            # Draw button text
            text_surf = self.font.render(button["text"], True, self.WHITE)
            text_rect = text_surf.get_rect(center=button["rect"].center)
            self.screen.blit(text_surf, text_rect)
        
        # Draw title
        title_font = pygame.font.SysFont('Arial', 72)
        title_surf = title_font.render("Blade Fighters", True, self.WHITE)
        title_rect = title_surf.get_rect(midtop=(self.width // 2, 50))
        self.screen.blit(title_surf, title_rect)
        
        # Draw version number
        version_font = pygame.font.SysFont('Arial', 20)
        version_surf = version_font.render(f"v{self.version}", True, self.LIGHT_GRAY)
        version_rect = version_surf.get_rect(bottomright=(self.width - 10, self.height - 10))
        self.screen.blit(version_surf, version_rect)
        
        # Animate the glow colors
        self.glow_intensity += self.glow_speed * self.glow_direction
        if self.glow_intensity >= 1.0:
            self.glow_intensity = 1.0
            self.glow_direction = -1
            self.glow_index = (self.glow_index + 1) % len(self.GLOW_COLORS)
        elif self.glow_intensity <= 0.3:
            self.glow_intensity = 0.3
            self.glow_direction = 1
    
    def draw_settings_menu(self):
        """Draw the settings menu screen using the MenuSystem."""
        # Use the MenuSystem to draw the settings menu
        if hasattr(self, 'menu_system') and self.menu_system:
            settings_buttons = self.menu_system.draw_settings_menu(
                on_back_action=lambda: self.set_screen("main_menu"),
                current_resolution=(self.width, self.height),
                resolutions=self.resolutions,
                on_resolution_change=self.change_resolution
            )
        else:
            # Fallback if no menu system available
            settings_buttons = []
        
        # Check for hover on buttons
        mouse_pos = pygame.mouse.get_pos()
        for button in settings_buttons:
            if button["rect"].collidepoint(mouse_pos):
                button["hover"] = True
            else:
                button["hover"] = False
        
        # Instead, use the custom MP3 player display method
        if hasattr(self, 'audio') and self.audio:
            self.display_custom_mp3_player()
        
        return settings_buttons
    
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
        if hasattr(self, 'settings_system') and self.settings_system:
            self.settings_system.screen = self.screen
            self.settings_system.width = self.width
            self.settings_system.height = self.height
        
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
        self.puzzle_engine.start_game()
    
    def draw_game_screen(self):
        """Draw the game screen. Placeholder for now."""
        # Draw background
        if self.puzzle_background:
            # Scale to fit screen
            scaled_bg = pygame.transform.scale(self.puzzle_background, (self.width, self.height))
            self.screen.blit(scaled_bg, (0, 0))
        else:
            # Use a solid color if no background image
            self.screen.fill((20, 20, 50))
            
        # Draw game placeholder text
        title_font = pygame.font.SysFont('Arial', 72)
        title_surf = title_font.render("Game Screen", True, self.WHITE)
        title_rect = title_surf.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(title_surf, title_rect)
        
        # Draw instruction
        instruction_font = pygame.font.SysFont('Arial', 36)
        instruction_surf = instruction_font.render("Press ESC to return to menu", True, self.WHITE)
        instruction_rect = instruction_surf.get_rect(center=(self.width // 2, self.height // 2 + 60))
        self.screen.blit(instruction_surf, instruction_rect)
        
        # Instead, use the custom MP3 player display method
        if hasattr(self, 'audio') and self.audio:
            self.display_custom_mp3_player()
    
    def display_custom_mp3_player(self):
        """Display only the custom MP3 player image with functional buttons."""
        if not hasattr(self.audio, 'mp3_player') or not self.audio.mp3_player:
            return
        
        # Simply use the MP3 player's own draw method
        # This will draw the MP3 player with consistent button positioning
        self.mp3_player_buttons = self.audio.mp3_player.draw(self.screen, self.width, self.height)
        
        return self.mp3_player_buttons
    
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
        
        try:
            # Main game loop
            while self.game_running:
                # Get all events
                events = pygame.event.get()
                
                # Process window close events
                for event in events:
                    if event.type == pygame.QUIT:
                        # Save UI positions before closing
                        if hasattr(self, 'settings_system') and self.settings_system and hasattr(self.settings_system, 'ui_editor') and self.settings_system.ui_editor:
                            self.settings_system.ui_editor.save_positions()
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
                    
                    # Display MP3 player
                    if hasattr(self, 'audio') and self.audio:
                        self.display_custom_mp3_player()
                
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
                        
                        # Draw the test mode
                        self.test_mode.draw()
                        
                        # Display MP3 player in test mode too
                        if hasattr(self, 'audio') and self.audio:
                            self.display_custom_mp3_player()
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
                    
                    # Display MP3 player in story menu too
                    if hasattr(self, 'audio') and self.audio:
                        self.display_custom_mp3_player()
                
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
                    
                    # Display MP3 player in story content view too
                    if hasattr(self, 'audio') and self.audio:
                        self.display_custom_mp3_player()
                
                elif self.current_screen == "settings":
                    # Process settings events using the settings system
                    if hasattr(self, 'settings_system') and self.settings_system:
                        settings_action = self.settings_system.process_settings_events(events)
                        
                        # Handle settings actions
                        if settings_action == "back":
                            self.set_screen("main_menu")
                        elif isinstance(settings_action, str) and settings_action.startswith("resolution:"):
                            # Extract resolution from action string
                            parts = settings_action.split(":")
                            if len(parts) == 3:
                                width, height = int(parts[1]), int(parts[2])
                                self.change_resolution(width, height)
                        
                        # Draw the settings menu using the settings system
                        self.settings_buttons = self.settings_system.draw_settings_menu(
                            on_back_action=lambda: self.set_screen("main_menu"),
                            current_resolution=(self.width, self.height),
                            resolutions=self.resolutions,
                            on_resolution_change=self.change_resolution
                        )
                    else:
                        # Fallback if settings system is not available
                        self.screen.fill(self.BLACK)
                        error_text = self.font.render("Settings system not available", True, self.WHITE)
                        error_rect = error_text.get_rect(center=(self.width // 2, self.height // 2))
                        self.screen.blit(error_text, error_rect)
                        
                        # Handle escape key to go back
                        for event in events:
                            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                                self.set_screen("main_menu")
                    
                    # Display MP3 player in settings too
                    if hasattr(self, 'audio') and self.audio:
                        self.display_custom_mp3_player()
                
                elif self.current_screen == "game":
                    # Process game events
                    game_action = self.puzzle_engine.process_events(events)
                    
                    # Handle game actions
                    if game_action == "back_to_menu":
                        self.set_screen("main_menu")
                    
                    # Calculate delta time for smooth animations
                    current_time = time.time()
                    if not hasattr(self, 'last_frame_time'):
                        self.last_frame_time = current_time
                    delta_time = current_time - self.last_frame_time
                    self.last_frame_time = current_time
                    
                    # Update game state
                    self.puzzle_engine.update()
                    
                    # Update renderer animations
                    self.puzzle_renderer.update_visual_state()
                    self.puzzle_renderer.update_animations()
                    
                    # Draw the game using our renderer
                    self.puzzle_renderer.draw_game_screen()
                    
                    # Instead, use the custom MP3 player display method
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
            return
        
        # Legacy story loading
        # Map story IDs to filenames
        story_files = {
            1: "stories/saga1_the_forge_keepers_legacy.txt",
            2: "stories/saga2_crimson_dawn.txt",
            3: "stories/saga3_azure_storm.txt",
            4: "stories/saga4_emerald_shadows.txt",
            5: "stories/saga5_golden_ascension.txt",
            6: "stories/saga6_twilight_vendetta.txt",
            7: "stories/saga7_crystal_prophecy.txt",
            8: "stories/saga8_obsidian_heart.txt",
            9: "stories/saga9_silver_alliance.txt",
            10: "stories/saga10_radiant_finale.txt"
        }
        
        # Default content if file not found
        self.current_story = {
            "title": f"Story {story_id}",
            "content": ["No story content available yet.", "Check back later for updates!"]
        }
        
        # Try to load the story file
        if story_id in story_files:
            try:
                with open(story_files[story_id], "r") as f:
                    lines = f.readlines()
                    
                # Parse the content
                title = "Unknown Story"
                content = []
                in_chapter = False
                
                for line in lines:
                    line = line.strip()
                    if line.startswith("# "):
                        # This is the title
                        title = line[2:]
                    elif line.startswith("## "):
                        # This is a chapter title
                        in_chapter = True
                        content.append(line)
                    elif line or in_chapter:
                        # Only add non-empty lines or lines after we've started a chapter
                        # This skips any blank lines at the beginning
                        content.append(line)
                
                self.current_story = {
                    "title": title,
                    "content": content
                }
                
                print(f"Loaded story: {title}")
            except Exception as e:
                print(f"Error loading story {story_id}: {e}")
        
        # Reset scroll position
        self.story_scroll_position = 0
        
    def display_story_content(self):
        """Display the current story content with scrolling."""
        # Clear the screen
        self.screen.fill(self.BLACK)
        
        # Draw a nice background
        if hasattr(self, 'story_background') and self.story_background:
            # Scale to fit screen
            scaled_bg = pygame.transform.scale(self.story_background, (self.width, self.height))
            self.screen.blit(scaled_bg, (0, 0))
        
        # Add a semi-transparent overlay for better readability
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Black with 180/255 alpha
        self.screen.blit(overlay, (0, 0))
        
        # Draw some menu particles for visual appeal
        if hasattr(self, 'menu_system') and self.menu_system:
            self.menu_system.draw_menu_particles()
        
        # Create a surface for the content
        content_width = int(self.width * 0.8)
        content_x = (self.width - content_width) // 2
        padding = 20
        
        # Initialize fonts
        title_font = pygame.font.SysFont(None, 56)
        chapter_font = pygame.font.SysFont(None, 36)
        text_font = pygame.font.SysFont(None, 24)
        
        # Render the title
        title_surf = title_font.render(self.current_story["title"], True, self.WHITE)
        title_rect = title_surf.get_rect(midtop=(self.width // 2, padding))
        self.screen.blit(title_surf, title_rect)
        
        # Calculate total content height (for scrolling limits)
        total_height = title_rect.height + padding * 2
        content_surfaces = []
        
        # Render all content lines
        y_offset = title_rect.bottom + padding
        for line in self.current_story["content"]:
            if not line:
                # Add spacing for empty lines
                y_offset += 15
                continue
                
            if line.startswith("## "):
                # Chapter title
                surf = chapter_font.render(line[3:], True, (220, 180, 255))
                y_offset += 30  # Extra space before chapters
            else:
                # Regular text
                surf = text_font.render(line, True, self.WHITE)
            
            rect = surf.get_rect(topleft=(content_x, y_offset - self.story_scroll_position))
            content_surfaces.append((surf, rect, y_offset))
            y_offset += surf.get_height() + 5
        
        total_height = y_offset + padding
        
        # Draw only visible content
        visible_area = pygame.Rect(0, 0, self.width, self.height)
        for surf, rect, original_y in content_surfaces:
            if original_y - self.story_scroll_position < 0:
                continue  # Skip if above the view
            if original_y - self.story_scroll_position > self.height:
                continue  # Skip if below the view
                
            self.screen.blit(surf, rect)
        
        # Limit scrolling
        max_scroll = max(0, total_height - self.height)
        self.story_scroll_position = min(self.story_scroll_position, max_scroll)
        
        # Draw scroll indicators if needed
        if total_height > self.height:
            # Up indicator
            if self.story_scroll_position > 0:
                pygame.draw.polygon(self.screen, (180, 180, 255), [
                    (self.width // 2, 15),
                    (self.width // 2 - 10, 25),
                    (self.width // 2 + 10, 25)
                ])
            
            # Down indicator
            if self.story_scroll_position < max_scroll:
                pygame.draw.polygon(self.screen, (180, 180, 255), [
                    (self.width // 2, self.height - 15),
                    (self.width // 2 - 10, self.height - 25),
                    (self.width // 2 + 10, self.height - 25)
                ])
                
        # Draw instruction
        instruction_font = pygame.font.SysFont(None, 20)
        instruction_text = "Use arrow keys or mouse wheel to scroll. Press ESC to return to story menu."
        instruction_surf = instruction_font.render(instruction_text, True, self.LIGHT_GRAY)
        instruction_rect = instruction_surf.get_rect(midbottom=(self.width // 2, self.height - 10))
        self.screen.blit(instruction_surf, instruction_rect)

if __name__ == "__main__":
    client = GameClient()
    client.run() 