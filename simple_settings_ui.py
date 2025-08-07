"""
Simple Settings UI for BladeFighters
A clean, functional settings interface that actually works
"""

import pygame
import json
import os
from typing import Dict, List, Tuple

class SimpleSettingsUI:
    """A simplified, functional settings UI."""
    
    def __init__(self, screen: pygame.Surface, font: pygame.font.Font, audio_system, game_client=None):
        self.screen = screen
        self.font = font
        self.audio = audio_system
        self.game_client = game_client
        self.width = screen.get_width()
        self.height = screen.get_height()
        
        # Load settings
        self.settings = self.load_settings()
        
        # UI state
        self.is_visible = False
        self.selected_setting = None
        self.hovered_button = None
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GRAY = (100, 100, 100)
        self.LIGHT_GRAY = (200, 200, 200)
        self.BLUE = (0, 100, 255)
        self.LIGHT_BLUE = (100, 150, 255)
        self.GREEN = (0, 255, 0)
        self.RED = (255, 0, 0)
        
        # Settings categories
        self.categories = [
            {
                'name': 'Audio',
                'settings': [
                    {'name': 'audio_volume', 'label': 'Sound Volume', 'type': 'slider', 'min': 0.0, 'max': 1.0, 'step': 0.1},
                    {'name': 'music_volume', 'label': 'Music Volume', 'type': 'slider', 'min': 0.0, 'max': 1.0, 'step': 0.1}
                ]
            },
            {
                'name': 'Display',
                'settings': [
                    {'name': 'fullscreen', 'label': 'Fullscreen', 'type': 'toggle'},
                    {'name': 'vsync', 'label': 'V-Sync', 'type': 'toggle'}
                ]
            },
            {
                'name': 'Gameplay',
                'settings': [
                    {'name': 'particle_effects', 'label': 'Particle Effects', 'type': 'toggle'},
                    {'name': 'brightness', 'label': 'Brightness', 'type': 'slider', 'min': 0.5, 'max': 1.5, 'step': 0.1}
                ]
            }
        ]
        
        print("🔧 Simple Settings UI initialized")
    
    def load_settings(self) -> Dict:
        """Load settings from file."""
        try:
            with open('game_settings.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Default settings
            default_settings = {
                'audio_volume': 0.7,
                'music_volume': 0.5,
                'fullscreen': True,
                'vsync': True,
                'particle_effects': True,
                'brightness': 1.0
            }
            self.save_settings(default_settings)
            return default_settings
    
    def save_settings(self, settings: Dict = None):
        """Save settings to file."""
        if settings is None:
            settings = self.settings
        with open('game_settings.json', 'w') as f:
            json.dump(settings, f, indent=2)
    
    def show(self):
        """Show the settings UI."""
        self.is_visible = True
        print("🔧 Settings UI shown")
    
    def hide(self):
        """Hide the settings UI."""
        self.is_visible = False
        self.selected_setting = None
        print("🔧 Settings UI hidden")
    
    def draw(self):
        """Draw the settings UI."""
        if not self.is_visible:
            return
        
        # Draw background overlay
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Draw settings panel
        panel_width = 600
        panel_height = 500
        panel_x = (self.width - panel_width) // 2
        panel_y = (self.height - panel_height) // 2
        
        # Panel background
        panel_surface = pygame.Surface((panel_width, panel_height))
        panel_surface.fill((50, 50, 70))
        pygame.draw.rect(panel_surface, (100, 100, 120), (0, 0, panel_width, panel_height), 3)
        self.screen.blit(panel_surface, (panel_x, panel_y))
        
        # Title
        title_font = pygame.font.Font(None, 48)
        title_text = title_font.render("Settings", True, self.WHITE)
        title_rect = title_text.get_rect(center=(self.width // 2, panel_y + 40))
        self.screen.blit(title_text, title_rect)
        
        # Draw categories
        y_offset = panel_y + 80
        for category in self.categories:
            # Category header
            cat_font = pygame.font.Font(None, 32)
            cat_text = cat_font.render(category['name'], True, self.LIGHT_BLUE)
            cat_rect = cat_text.get_rect(left=panel_x + 30, top=y_offset)
            self.screen.blit(cat_text, cat_rect)
            y_offset += 40
            
            # Category settings
            for setting in category['settings']:
                self.draw_setting(setting, panel_x + 30, y_offset, panel_width - 60)
                y_offset += 60
        
        # Draw close button
        close_rect = pygame.Rect(panel_x + panel_width - 60, panel_y + 20, 40, 30)
        close_color = self.RED if self.hovered_button == 'close' else self.GRAY
        pygame.draw.rect(self.screen, close_color, close_rect)
        close_text = self.font.render("X", True, self.WHITE)
        close_text_rect = close_text.get_rect(center=close_rect.center)
        self.screen.blit(close_text, close_text_rect)
    
    def draw_setting(self, setting: Dict, x: int, y: int, width: int):
        """Draw a single setting."""
        setting_name = setting['name']
        setting_label = setting['label']
        setting_type = setting['type']
        current_value = self.settings.get(setting_name, 0)
        
        # Setting label
        label_text = self.font.render(setting_label, True, self.WHITE)
        self.screen.blit(label_text, (x, y))
        
        if setting_type == 'slider':
            self.draw_slider(setting, x + 200, y, width - 200, current_value)
        elif setting_type == 'toggle':
            self.draw_toggle(setting, x + 200, y, current_value)
    
    def draw_slider(self, setting: Dict, x: int, y: int, width: int, value: float):
        """Draw a slider setting."""
        # Slider background
        slider_rect = pygame.Rect(x, y + 10, width - 100, 20)
        pygame.draw.rect(self.screen, self.GRAY, slider_rect)
        
        # Slider value
        min_val = setting.get('min', 0.0)
        max_val = setting.get('max', 1.0)
        normalized_value = (value - min_val) / (max_val - min_val)
        slider_pos = x + normalized_value * (width - 100)
        
        # Slider handle
        handle_rect = pygame.Rect(slider_pos - 5, y + 5, 10, 30)
        pygame.draw.rect(self.screen, self.BLUE, handle_rect)
        
        # Value text
        value_text = self.font.render(f"{value:.1f}", True, self.WHITE)
        self.screen.blit(value_text, (x + width - 80, y))
    
    def draw_toggle(self, setting: Dict, x: int, y: int, value: bool):
        """Draw a toggle setting."""
        # Toggle background
        toggle_rect = pygame.Rect(x, y + 5, 60, 30)
        toggle_color = self.GREEN if value else self.GRAY
        pygame.draw.rect(self.screen, toggle_color, toggle_rect)
        
        # Toggle text
        toggle_text = self.font.render("ON" if value else "OFF", True, self.WHITE)
        toggle_text_rect = toggle_text.get_rect(center=toggle_rect.center)
        self.screen.blit(toggle_text, toggle_text_rect)
    
    def handle_click(self, pos: Tuple[int, int]):
        """Handle mouse clicks."""
        if not self.is_visible:
            return False
        
        x, y = pos
        
        # Check close button
        panel_width = 600
        panel_height = 500
        panel_x = (self.width - panel_width) // 2
        panel_y = (self.height - panel_height) // 2
        close_rect = pygame.Rect(panel_x + panel_width - 60, panel_y + 20, 40, 30)
        
        if close_rect.collidepoint(x, y):
            self.hide()
            if self.audio and hasattr(self.audio, 'play_sound'):
                self.audio.play_sound('click')
            return True
        
        # Check settings
        y_offset = panel_y + 80
        for category in self.categories:
            y_offset += 40  # Category header
            for setting in category['settings']:
                setting_rect = pygame.Rect(panel_x + 30, y_offset, panel_width - 60, 50)
                if setting_rect.collidepoint(x, y):
                    self.handle_setting_click(setting, x, y)
                    return True
                y_offset += 60
        
        return False
    
    def handle_setting_click(self, setting: Dict, x: int, y: int):
        """Handle clicks on specific settings."""
        setting_name = setting['name']
        setting_type = setting['type']
        current_value = self.settings.get(setting_name, 0)
        
        if setting_type == 'toggle':
            # Toggle boolean value
            new_value = not current_value
            self.settings[setting_name] = new_value
            self.apply_setting(setting_name, new_value)
            
        elif setting_type == 'slider':
            # Handle slider click (simplified - just toggle between min/max)
            min_val = setting.get('min', 0.0)
            max_val = setting.get('max', 1.0)
            new_value = max_val if current_value <= min_val else min_val
            self.settings[setting_name] = new_value
            self.apply_setting(setting_name, new_value)
        
        # Play sound
        if self.audio and hasattr(self.audio, 'play_sound'):
            self.audio.play_sound('click')
        
        # Save settings
        self.save_settings()
    
    def apply_setting(self, name: str, value):
        """Apply a setting change."""
        print(f"🔧 Applying setting: {name} = {value}")
        
        if name == 'audio_volume':
            if self.audio and hasattr(self.audio, 'set_volume'):
                self.audio.set_volume(value)
                print(f"🔊 Audio volume set to {value:.1f}")
        
        elif name == 'music_volume':
            if self.audio and hasattr(self.audio, 'set_music_volume'):
                self.audio.set_music_volume(value)
                print(f"🎵 Music volume set to {value:.1f}")
        
        elif name == 'fullscreen':
            if self.game_client and hasattr(self.game_client, 'toggle_fullscreen'):
                self.game_client.toggle_fullscreen()
                print(f"🖥️ Fullscreen toggled")
        
        elif name == 'vsync':
            if self.game_client and hasattr(self.game_client, 'toggle_vsync'):
                self.game_client.toggle_vsync()
                print(f"🔄 V-Sync toggled")
        
        elif name == 'particle_effects':
            if self.game_client and hasattr(self.game_client, 'set_particle_effects'):
                self.game_client.set_particle_effects(value)
                print(f"✨ Particle effects {'enabled' if value else 'disabled'}")
        
        elif name == 'brightness':
            print(f"💡 Brightness set to {value:.1f}")
            # Brightness would need to be applied to the renderer
    
    def handle_mouse_move(self, pos: Tuple[int, int]):
        """Handle mouse movement for hover effects."""
        if not self.is_visible:
            return
        
        x, y = pos
        
        # Check close button hover
        panel_width = 600
        panel_height = 500
        panel_x = (self.width - panel_width) // 2
        panel_y = (self.height - panel_height) // 2
        close_rect = pygame.Rect(panel_x + panel_width - 60, panel_y + 20, 40, 30)
        
        if close_rect.collidepoint(x, y):
            self.hovered_button = 'close'
        else:
            self.hovered_button = None 