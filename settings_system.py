import pygame
import os
from ui_editor import UIEditor

class SettingsSystem:
    def __init__(self, screen, font, audio, asset_path):
        """Initialize the settings system."""
        self.screen = screen
        self.font = font
        self.audio = audio
        self.asset_path = asset_path
        
        # Get screen dimensions
        self.width = screen.get_width()
        self.height = screen.get_height()
        
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
        
        # Settings buttons
        self.settings_buttons = []
        
        # Load settings background
        try:
            self.settings_background = pygame.image.load(os.path.join(os.path.dirname(asset_path), "settingsbcg.jfif"))
        except pygame.error:
            self.settings_background = None
            
        # Initialize UI Editor
        self.ui_editor = None
        self.current_screen = "settings"  # Can be "settings" or "ui_editor"
    
    def create_button(self, x, y, width, height, text, action=None, params=None):
        """Create a button with text and optional action."""
        button = {
            "rect": pygame.Rect(x, y, width, height),
            "text": text,
            "action": action,
            "params": params,
            "hover": False
        }
        return button
    
    def draw_settings_menu(self, on_back_action, current_resolution, resolutions, on_resolution_change):
        """Draw the settings menu screen with resolution options."""
        # If we're in the UI Editor, draw that instead
        if self.current_screen == "ui_editor":
            print("Drawing UI Editor screen")
            if not self.ui_editor:
                print("Initializing UI Editor")
                self.ui_editor = UIEditor(self.screen, self.font, self.audio, self.asset_path)
                # Load positions when initializing the editor
                self.ui_editor.load_positions()
            self.ui_editor.draw()
            return self.settings_buttons
        
        print("Drawing Settings screen")
        # Clear screen
        self.screen.fill(self.BLACK)
        
        # Clear previous buttons
        self.settings_buttons = []
        
        # Draw settings background if available
        if self.settings_background:
            scaled_bg = pygame.transform.scale(self.settings_background, (self.width, self.height))
            self.screen.blit(scaled_bg, (0, 0))
        
        # Draw settings menu box
        menu_width = 800
        menu_height = 600
        menu_x = (self.width - menu_width) // 2
        menu_y = (self.height - menu_height) // 2
        
        # Draw menu background with glow effect
        menu_surface = pygame.Surface((menu_width, menu_height), pygame.SRCALPHA)
        menu_surface.fill((0, 0, 0, 180))  # Semi-transparent black
        
        # Add glow effect to menu border
        glow_color = self.GLOW_COLORS[self.glow_index]
        glow_alpha = int(255 * self.glow_intensity)
        glow_surface = pygame.Surface((menu_width + 4, menu_height + 4), pygame.SRCALPHA)
        pygame.draw.rect(glow_surface, (*glow_color, glow_alpha), (0, 0, menu_width + 4, menu_height + 4), border_radius=10)
        self.screen.blit(glow_surface, (menu_x - 2, menu_y - 2))
        
        # Draw menu box
        pygame.draw.rect(self.screen, (30, 30, 50), (menu_x, menu_y, menu_width, menu_height), border_radius=10)
        pygame.draw.rect(self.screen, (100, 100, 255), (menu_x, menu_y, menu_width, menu_height), 2, border_radius=10)
        
        # Draw title
        title_text = self.font.render("Settings", True, self.WHITE)
        title_rect = title_text.get_rect(center=(menu_x + menu_width // 2, menu_y + 40))
        self.screen.blit(title_text, title_rect)
        
        # Draw resolution label
        label_x = menu_x + 50
        label_y = menu_y + 100
        label_text = self.font.render("Resolution:", True, self.WHITE)
        self.screen.blit(label_text, (label_x, label_y))
        
        # Draw resolution buttons
        button_width = 120
        button_height = 40
        button_x = label_x + 150
        button_y = label_y - 10
        
        # Draw each resolution option
        for res in resolutions:
            res_text = f"{res[0]}x{res[1]}"
            
            # Highlight current resolution with different color
            if res == current_resolution:
                button_color = (0, 180, 255)  # Brighter blue for selected
            else:
                button_color = (0, 100, 180)
                
            # Create button for this resolution
            res_button = self.create_button(
                button_x, button_y, button_width, button_height, 
                res_text, on_resolution_change, params=res
            )
            
            # Set custom colors for this button
            pygame.draw.rect(self.screen, button_color, res_button["rect"], border_radius=5)
            pygame.draw.rect(self.screen, (200, 200, 255), res_button["rect"], 2, border_radius=5)
            
            # Draw button text
            button_font = pygame.font.SysFont(None, 24)
            button_text = button_font.render(res_text, True, (255, 255, 255))
            text_x = button_x + (button_width - button_text.get_width()) // 2
            text_y = button_y + (button_height - button_text.get_height()) // 2
            self.screen.blit(button_text, (text_x, text_y))
            
            # Add to settings buttons list
            self.settings_buttons.append(res_button)
            
            # Move to next button position
            button_x += button_width + 10
            if button_x + button_width > menu_x + menu_width - 50:
                button_x = label_x + 150
                button_y += button_height + 10
        
        # Draw UI Editor button
        ui_editor_button = self.create_button(
            menu_x + 50, button_y + 60, 200, 50,
            "UI Editor", lambda: self.set_screen("ui_editor")
        )
        pygame.draw.rect(self.screen, (0, 150, 255), ui_editor_button["rect"], border_radius=10)
        pygame.draw.rect(self.screen, (255, 255, 255), ui_editor_button["rect"], 2, border_radius=10)
        button_text = self.font.render("UI Editor", True, self.WHITE)
        text_rect = button_text.get_rect(center=ui_editor_button["rect"].center)
        self.screen.blit(button_text, text_rect)
        self.settings_buttons.append(ui_editor_button)
        
        # Draw Back button
        button_width = 200
        button_height = 50
        button_x = menu_x + (menu_width - button_width) // 2
        button_y = menu_y + menu_height - 80
        
        back_button = self.create_button(
            button_x, button_y, button_width, button_height,
            "Back to Menu", on_back_action
        )
        
        # Apply custom styling to back button
        pygame.draw.rect(self.screen, (0, 100, 255), back_button["rect"], border_radius=10)
        pygame.draw.rect(self.screen, (255, 255, 255), back_button["rect"], 3, border_radius=10)
        
        # Draw button text
        button_font = pygame.font.SysFont(None, 36)
        button_text = button_font.render("Back to Menu", True, (255, 255, 255))
        text_x = button_x + (button_width - button_text.get_width()) // 2
        text_y = button_y + (button_height - button_text.get_height()) // 2
        self.screen.blit(button_text, (text_x, text_y))
        
        # Add back button to settings buttons list
        self.settings_buttons.append(back_button)
        
        # Draw MP3 player if available
        if hasattr(self, 'audio') and self.audio and hasattr(self.audio, 'mp3_player'):
            self.audio.mp3_player.draw(self.screen, self.width, self.height)
        
        # Return all settings buttons
        return self.settings_buttons
    
    def set_screen(self, screen_name):
        """Set the current screen."""
        print(f"Setting screen to: {screen_name}")
        self.current_screen = screen_name
        if screen_name == "ui_editor":
            print("Creating new UI Editor instance")
            self.ui_editor = UIEditor(self.screen, self.font, self.audio, self.asset_path)
            self.ui_editor.load_positions()
    
    def process_settings_events(self, events):
        """Process events for the settings menu.
        Returns action string if an action is triggered, None otherwise."""
        # If we're in the UI Editor, process its events
        if self.current_screen == "ui_editor":
            if not self.ui_editor:
                self.ui_editor = UIEditor(self.screen, self.font, self.audio, self.asset_path)
                # Load positions when initializing the editor
                self.ui_editor.load_positions()
            ui_action = self.ui_editor.process_events(events)
            if ui_action == "back_to_settings":
                # Always save positions when exiting the UI editor
                if self.ui_editor:
                    self.ui_editor.save_positions()
                self.current_screen = "settings"
                self.ui_editor = None
                # Reload UI positions when returning from UI editor
                if hasattr(self, 'test_mode'):
                    self.test_mode.setup_board_positions()
            return None
        
        # Process settings menu events
        for event in events:
            # Handle clicks on settings buttons
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
                mouse_pos = pygame.mouse.get_pos()
                
                # First check if MP3 player buttons were clicked
                if hasattr(self, 'audio') and self.audio and hasattr(self.audio, 'mp3_player'):
                    if self.audio.mp3_player.handle_events(event):
                        continue  # Skip further processing if MP3 player handled the event
                
                # Check for back button
                for button in self.settings_buttons:
                    if button["rect"].collidepoint(mouse_pos):
                        # Play click sound if available
                        if self.audio:
                            self.audio.play_sound('click')
                        
                        # Handle action based on button text
                        if button["text"] == "Back to Menu":
                            return "back"
                        # Handle resolution buttons
                        elif "x" in button["text"]:  # Resolution format: "WIDTHxHEIGHT"
                            width, height = map(int, button["text"].split("x"))
                            return f"resolution:{width}:{height}"
                        # Handle UI Editor button
                        elif button["text"] == "UI Editor":
                            self.set_screen("ui_editor")
            
            # Handle escape key to go back
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.current_screen == "ui_editor":
                        # Save positions when exiting with escape key
                        if self.ui_editor:
                            self.ui_editor.save_positions()
                        self.current_screen = "settings"
                        self.ui_editor = None
                    else:
                        return "back"
            
            # Handle MP3 player events (hover effects, etc.)
            elif event.type == pygame.MOUSEMOTION:
                if hasattr(self, 'audio') and self.audio and hasattr(self.audio, 'mp3_player'):
                    self.audio.mp3_player.handle_events(event)
        
        return None 