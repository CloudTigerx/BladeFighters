"""
Settings System for Blade Fighters
A clean, Python-based settings system with modern UI components.
"""

import pygame
import json
import os
from typing import Dict, List, Tuple, Optional
import math
import time

class SettingsSystem:
    """
    Modern settings system with clean Python implementation.
    Provides sliders, buttons, and a beautiful UI.
    """
    
    def __init__(self, screen: pygame.Surface, font: pygame.font.Font, audio_system, asset_path: str, game_client=None):
        self.screen = screen
        self.font = font
        self.audio = audio_system
        self.asset_path = asset_path
        self.game_client = game_client  # Reference to game client for advanced settings
        self.width = screen.get_width()
        self.height = screen.get_height()
        
        # Settings data
        self.settings = {
            'audio_volume': 0.8,
            'music_volume': 0.6,
            'screen_resolution': (1600, 900),
            'fullscreen': False,
            'vsync': True,
            'particle_effects': True,
            'brightness': 1.0,
            'sensitivity': 1.0
        }
        
        # Control mappings
        self.controls = {
            'move_up': pygame.K_UP,
            'move_down': pygame.K_DOWN,
            'move_left': pygame.K_LEFT,
            'move_right': pygame.K_RIGHT,
            'action': pygame.K_SPACE,
            'menu_confirm': pygame.K_RETURN,
            'menu_cancel': pygame.K_ESCAPE,
            'menu_tab': pygame.K_TAB,
            'music_next': pygame.K_RIGHTBRACKET,  # ]
            'music_prev': pygame.K_LEFTBRACKET,   # [
            'music_pause': pygame.K_p,
            'fullscreen_toggle': pygame.K_F11
        }
        
        # UI state
        self.is_visible = False
        self.animation_time = 0.0
        self.fade_alpha = 0.0
        self.target_fade_alpha = 0.0
        
        # Interactive elements
        self.sliders = {}
        self.buttons = {}
        self.hovered_element = None
        
        # Control customization state
        self.showing_controls = False
        self.waiting_for_key = False
        self.selected_control = None
        self.control_buttons = {}
        
        # Load settings from file
        self.load_settings()
        self.load_controls() # Load controls on initialization
        
        # Initialize UI elements
        self.setup_ui_elements()
        self.setup_control_ui()
        
        print("🔧 Settings system initialized successfully")
    
    def setup_control_ui(self):
        """Setup control customization UI elements."""
        # Define control categories and their actions
        control_categories = {
            'Movement': [
                ('move_up', 'Move Up'),
                ('move_down', 'Move Down'),
                ('move_left', 'Move Left'),
                ('move_right', 'Move Right')
            ],
            'Actions': [
                ('action', 'Action/Drop'),
                ('menu_confirm', 'Confirm'),
                ('menu_cancel', 'Cancel/Back')
            ],
            'Music': [
                ('music_next', 'Next Song'),
                ('music_prev', 'Previous Song'),
                ('music_pause', 'Pause/Play')
            ],
            'System': [
                ('fullscreen_toggle', 'Toggle Fullscreen'),
                ('menu_tab', 'Tab Navigation')
            ]
        }
        
        # Create control buttons for each category
        y_start = 200
        button_width = 200
        button_height = 40
        spacing = 50
        
        for category, controls in control_categories.items():
            # Category label
            category_y = y_start
            y_start += 30
            
            # Control buttons for this category
            for i, (action, label) in enumerate(controls):
                x = self.width//2 - 300 + (i % 2) * (button_width + 20)
                y = y_start + (i // 2) * (button_height + 10)
                
                self.control_buttons[action] = {
                    'label': label,
                    'rect': pygame.Rect(x, y, button_width, button_height),
                    'action': action,
                    'is_hovered': False,
                    'is_selected': False
                }
            
            y_start += len(controls) * (button_height + 10) + spacing
    
    def setup_ui_elements(self):
        """Setup all UI elements (sliders and buttons)."""
        # Define slider positions and properties
        slider_configs = [
            {'name': 'audio_volume', 'label': 'Audio Volume', 'y': 200, 'min': 0.0, 'max': 1.0},
            {'name': 'music_volume', 'label': 'Music Volume', 'y': 280, 'min': 0.0, 'max': 1.0},
            {'name': 'brightness', 'label': 'Brightness', 'y': 360, 'min': 0.5, 'max': 1.5},
            {'name': 'sensitivity', 'label': 'Mouse Sensitivity', 'y': 440, 'min': 0.1, 'max': 2.0}
        ]
        
        # Create sliders - centered within expanded panel
        for config in slider_configs:
            self.sliders[config['name']] = {
                'label': config['label'],
                'rect': pygame.Rect(self.width//2 - 350, config['y'], 700, 30),
                'min': config['min'],
                'max': config['max'],
                'value': self.settings[config['name']],
                'is_hovered': False,
                'is_dragging': False
            }
        
        # Define button positions and properties - properly spaced like web layout
        # Calculate button spacing: 4 buttons with proper gaps
        button_width = 140  # Wider buttons for better text fit
        button_spacing = 30  # Space between buttons
        total_button_width = (button_width * 4) + (button_spacing * 3)  # 4 buttons + 3 gaps
        start_x = self.width//2 - (total_button_width // 2)  # Center the entire button row
        
        button_configs = [
            {'name': 'fullscreen', 'label': 'Fullscreen', 'x': start_x, 'y': 520},
            {'name': 'vsync', 'label': 'V-Sync', 'x': start_x + button_width + button_spacing, 'y': 520},
            {'name': 'particle_effects', 'label': 'Particles', 'x': start_x + (button_width + button_spacing) * 2, 'y': 520},
            {'name': 'controls', 'label': 'Controls', 'x': start_x + (button_width + button_spacing) * 3, 'y': 520}
        ]
        
        # Create buttons with proper sizing
        for config in button_configs:
            self.buttons[config['name']] = {
                'label': config['label'],
                'rect': pygame.Rect(config['x'], config['y'], button_width, 40),
                'is_pressed': self.settings.get(config['name'], False),
                'is_hovered': False
            }
        
        # Add reset button below the main buttons
        self.buttons['reset'] = {
            'label': 'Reset All',
            'rect': pygame.Rect(self.width//2 - 60, 580, 120, 40),
            'is_pressed': False,
            'is_hovered': False
        }
    
    def load_settings(self):
        """Load settings from JSON file."""
        settings_file = 'game_settings.json'
        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r') as f:
                    loaded_settings = json.load(f)
                    self.settings.update(loaded_settings)
                print("✅ Settings loaded from file")
            except Exception as e:
                print(f"⚠️  Could not load settings: {e}")
    
    def save_settings(self):
        """Save settings to JSON file."""
        settings_file = 'game_settings.json'
        try:
            with open(settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            print("💾 Settings saved to file")
        except Exception as e:
            print(f"❌ Could not save settings: {e}")
    
    def update(self, delta_time: float):
        """Update animations and UI state."""
        self.animation_time += delta_time
        
        # Update fade animation
        if self.target_fade_alpha > self.fade_alpha:
            self.fade_alpha = min(self.fade_alpha + delta_time * 3.0, self.target_fade_alpha)
        elif self.target_fade_alpha < self.fade_alpha:
            self.fade_alpha = max(self.fade_alpha - delta_time * 3.0, self.target_fade_alpha)
    
    def show(self):
        """Show the settings screen."""
        self.is_visible = True
        self.target_fade_alpha = 1.0
        # Print current settings status for user reference
        self.print_settings_status()
        self.print_controls_status()
    
    def hide(self):
        """Hide the settings screen."""
        self.target_fade_alpha = 0.0
    
    def draw(self):
        """Draw the settings screen."""
        if not self.is_visible:
            return
        
        # Handle fade animation
        if self.fade_alpha != self.target_fade_alpha:
            if self.fade_alpha < self.target_fade_alpha:
                self.fade_alpha = min(self.target_fade_alpha, self.fade_alpha + 0.1)
            else:
                self.fade_alpha = max(self.target_fade_alpha, self.fade_alpha - 0.1)
        
        # Draw appropriate screen
        if self.showing_controls:
            self.draw_controls_screen()
        else:
            self.draw_settings_screen()
        
        # Apply fade effect
        if self.fade_alpha < 1.0:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, int(255 * (1.0 - self.fade_alpha))))
            self.screen.blit(overlay, (0, 0))
    
    def draw_settings_screen(self):
        """Draw the main settings screen."""
        # Clear screen with dark background
        self.screen.fill((20, 20, 50))
        
        # Draw title (simplified - no unnecessary text)
        title_font = pygame.font.SysFont('Arial', 48, bold=True)
        title_text = "Settings"
        title_surf = title_font.render(title_text, True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(self.width//2, 80))
        self.screen.blit(title_surf, title_rect)
        
        # Draw settings panel background
        # Expanded panel to properly contain all UI elements including the Reset button
        panel_rect = pygame.Rect(self.width//2 - 450, 150, 900, 500)
        pygame.draw.rect(self.screen, (40, 40, 60, 200), panel_rect, border_radius=20)
        pygame.draw.rect(self.screen, (100, 150, 255, 50), panel_rect, 2, border_radius=20)
        
        # Draw section headers and dividers
        self.draw_section_headers()
        
        # Draw sliders
        for name, slider in self.sliders.items():
            self.draw_slider(slider)
        
        # Draw buttons
        for name, button in self.buttons.items():
            self.draw_button(button)
        
        # Draw instructions - positioned below the expanded panel
        instruction_font = pygame.font.SysFont('Arial', 16)
        instructions = [
            "✨ Drag sliders to adjust settings",
            "🎮 Click buttons to toggle options",
            "💾 Settings save automatically",
            "🚀 Press ESC to return"
        ]
        
        for i, instruction in enumerate(instructions):
            inst_surf = instruction_font.render(instruction, True, (180, 180, 180))
            inst_rect = inst_surf.get_rect(center=(self.width//2, 680 + i * 25))
            self.screen.blit(inst_surf, inst_rect)
    
    def draw_section_headers(self):
        """Draw section headers with icons and dividers."""
        # Define sections with their positions and content
        sections = [
            {
                'title': '🔊 Audio',
                'y': 180,
                'color': (100, 150, 255),
                'items': ['audio_volume', 'music_volume']
            },
            {
                'title': '🖥️ Display',
                'y': 260,
                'color': (150, 200, 255),
                'items': ['brightness', 'sensitivity']
            },
            {
                'title': '⚡ Performance',
                'y': 340,
                'color': (200, 150, 255),
                'items': ['fullscreen', 'vsync', 'particle_effects', 'controls']
            },
            {
                'title': '🔄 System',
                'y': 500,
                'color': (255, 150, 100),
                'items': ['reset']
            }
        ]
        
        for section in sections:
            # Draw section header
            header_font = pygame.font.SysFont('Arial', 20, bold=True)
            header_surf = header_font.render(section['title'], True, section['color'])
            header_rect = header_surf.get_rect(left=self.width//2 - 400, top=section['y'])
            self.screen.blit(header_surf, header_rect)
            
            # Draw divider line
            divider_y = section['y'] + 30
            divider_color = (80, 80, 100)
            pygame.draw.line(self.screen, divider_color, 
                           (self.width//2 - 400, divider_y), 
                           (self.width//2 + 400, divider_y), 2)
    
    def draw_slider(self, slider: Dict):
        """Draw a modern slider with better visual feedback."""
        rect = slider['rect']
        value = slider['value']
        min_val = slider['min']
        max_val = slider['max']
        is_hovered = slider['is_hovered']
        
        # Calculate normalized value
        normalized = (value - min_val) / (max_val - min_val)
        
        # Draw background track with better styling
        track_color = (50, 50, 70) if not is_hovered else (70, 70, 90)
        pygame.draw.rect(self.screen, track_color, rect, border_radius=rect.height//2)
        
        # Draw track border
        border_color = (90, 90, 110) if is_hovered else (70, 70, 90)
        pygame.draw.rect(self.screen, border_color, rect, 2, border_radius=rect.height//2)
        
        # Draw filled portion with gradient effect
        fill_width = int(rect.width * normalized)
        if fill_width > 0:
            fill_rect = pygame.Rect(rect.x, rect.y, fill_width, rect.height)
            # Create gradient effect
            fill_color = (120, 170, 255) if not is_hovered else (140, 190, 255)
            pygame.draw.rect(self.screen, fill_color, fill_rect, border_radius=rect.height//2)
            
            # Add highlight to filled portion
            highlight_rect = pygame.Rect(rect.x, rect.y, fill_width, rect.height//2)
            highlight_color = (160, 200, 255)
            pygame.draw.rect(self.screen, highlight_color, highlight_rect, border_radius=rect.height//2)
        
        # Draw handle with better styling
        handle_x = rect.x + int(rect.width * normalized)
        handle_size = rect.height + 6 if is_hovered else rect.height + 2
        
        # Handle shadow
        pygame.draw.circle(self.screen, (30, 30, 50), (handle_x + 2, rect.centery + 2), handle_size//2)
        # Main handle
        handle_color = (180, 220, 255) if not is_hovered else (220, 240, 255)
        pygame.draw.circle(self.screen, handle_color, (handle_x, rect.centery), handle_size//2)
        # Handle highlight
        highlight_radius = handle_size//4
        pygame.draw.circle(self.screen, (255, 255, 255), (handle_x - highlight_radius//2, rect.centery - highlight_radius//2), highlight_radius)
        # Handle border
        pygame.draw.circle(self.screen, (255, 255, 255), (handle_x, rect.centery), handle_size//2, 2)
        
        # Draw label with better positioning and styling
        label_font = pygame.font.SysFont('Arial', 16, bold=True)
        label_text = f"{slider['label']}: {value:.1f}"
        label_surf = label_font.render(label_text, True, (240, 240, 240))
        label_rect = label_surf.get_rect()
        label_rect.midleft = (rect.x, rect.y - 30)
        self.screen.blit(label_surf, label_rect)
    
    def draw_button(self, button: Dict):
        """Draw a modern button."""
        rect = button['rect']
        is_pressed = button['is_pressed']
        is_hovered = button['is_hovered']
        
        # Calculate animation scale
        scale = 1.0
        if is_hovered:
            scale = 1.05 + 0.02 * math.sin(self.animation_time * 6.0)
        
        # Apply scale
        scaled_width = int(rect.width * scale)
        scaled_height = int(rect.height * scale)
        scaled_x = rect.x - (scaled_width - rect.width) // 2
        scaled_y = rect.y - (scaled_height - rect.height) // 2
        
        # Draw button background
        if is_pressed:
            bg_color = (80, 120, 200)
        elif is_hovered:
            bg_color = (100, 140, 220)
        else:
            bg_color = (60, 100, 180)
        
        button_rect = pygame.Rect(scaled_x, scaled_y, scaled_width, scaled_height)
        pygame.draw.rect(self.screen, bg_color, button_rect, border_radius=10)
        
        # Draw border
        border_color = (120, 160, 240) if is_hovered else (80, 120, 200)
        pygame.draw.rect(self.screen, border_color, button_rect, 2, border_radius=10)
        
        # Draw text
        text_font = pygame.font.SysFont('Arial', 18, bold=True)
        text_surf = text_font.render(button['label'], True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=button_rect.center)
        self.screen.blit(text_surf, text_rect)
    
    def handle_click(self, pos: Tuple[int, int]):
        """Handle mouse clicks on settings UI elements."""
        if not self.is_visible:
            return
        
        # Handle control screen clicks
        if self.showing_controls:
            self.handle_control_click(pos)
            return
        
        x, y = pos
        
        # Check slider clicks
        for name, slider in self.sliders.items():
            if slider['rect'].collidepoint(x, y):
                # Start dragging
                slider['is_dragging'] = True
                # Update value immediately
                normalized = (x - slider['rect'].x) / slider['rect'].width
                normalized = max(0.0, min(1.0, normalized))
                new_value = slider['min'] + normalized * (slider['max'] - slider['min'])
                slider['value'] = max(slider['min'], min(slider['max'], new_value))
                self.settings[name] = slider['value']
                self.apply_setting(name, slider['value'])
                break
        
        # Check button clicks
        for name, button in self.buttons.items():
            if button['rect'].collidepoint(x, y):
                # Play click sound
                if self.audio and hasattr(self.audio, 'play_sound'):
                    self.audio.play_sound('click')
                
                # Handle button actions
                if name == 'reset':
                    self.reset_settings()
                elif name == 'controls':
                    self.show_controls_screen()
                else:
                    button['is_pressed'] = not button['is_pressed']
                    self.settings[name] = button['is_pressed']
                    self.apply_setting(name, button['is_pressed'])
                break
    
    def handle_mouse_drag(self, pos: Tuple[int, int]):
        """Handle mouse drag for slider interaction."""
        x, y = pos
        
        # Check if any slider is being dragged
        for name, slider in self.sliders.items():
            if slider['is_dragging']:
                # Calculate new value based on drag position
                normalized = (x - slider['rect'].x) / slider['rect'].width
                normalized = max(0.0, min(1.0, normalized))  # Clamp to slider bounds
                new_value = slider['min'] + normalized * (slider['max'] - slider['min'])
                slider['value'] = max(slider['min'], min(slider['max'], new_value))
                self.settings[name] = slider['value']
                
                # Apply setting immediately
                self.apply_setting(name, slider['value'])
                break
    
    def handle_mouse_release(self):
        """Handle mouse release to stop dragging."""
        # Stop all slider dragging
        for name, slider in self.sliders.items():
            slider['is_dragging'] = False
    
    def handle_mouse_move(self, pos: Tuple[int, int]):
        """Handle mouse movement for hover effects."""
        x, y = pos
        self.hovered_element = None
        
        # Check slider hovers
        for name, slider in self.sliders.items():
            slider['is_hovered'] = slider['rect'].collidepoint(x, y)
            if slider['is_hovered']:
                self.hovered_element = f"slider_{name}"
        
        # Check button hovers
        for name, button in self.buttons.items():
            button['is_hovered'] = button['rect'].collidepoint(x, y)
            if button['is_hovered']:
                self.hovered_element = f"button_{name}"
    
    def apply_setting(self, name: str, value):
        """Apply a setting change."""
        if name == 'audio_volume':
            if self.audio and hasattr(self.audio, 'set_volume'):
                self.audio.set_volume(value)
                print(f"🔊 Applied audio volume setting: {value:.1f}")
        elif name == 'music_volume':
            if self.audio and hasattr(self.audio, 'set_music_volume'):
                self.audio.set_music_volume(value)
                print(f"🎵 Applied music volume setting: {value:.1f}")
        elif name == 'fullscreen':
            # Handle fullscreen toggle through game client
            print(f"🖥️ Fullscreen setting changed to: {value}")
            if self.game_client and hasattr(self.game_client, 'toggle_fullscreen'):
                self.game_client.toggle_fullscreen()
        elif name == 'vsync':
            # Handle V-Sync toggle through game client
            print(f"🔄 V-Sync setting changed to: {value}")
            if self.game_client and hasattr(self.game_client, 'toggle_vsync'):
                self.game_client.toggle_vsync()
        elif name == 'particle_effects':
            # Handle particle effects toggle through game client
            print(f"✨ Particle effects setting changed to: {value}")
            if self.game_client and hasattr(self.game_client, 'set_particle_effects'):
                self.game_client.set_particle_effects(value)
        elif name == 'brightness':
            # This would need to be handled by the game client
            print(f"💡 Brightness setting changed to: {value:.1f}")
        elif name == 'sensitivity':
            # This would need to be handled by the game client
            print(f"🖱️ Mouse sensitivity setting changed to: {value:.1f}")
            # The sensitivity can be used to adjust input responsiveness
            # For now, we'll just log it, but it could be used for:
            # - Mouse movement speed in menus
            # - Input lag compensation
            # - Touch sensitivity for mobile
        
        # Save settings after each change
        self.save_settings()
    
    def show_controls_screen(self):
        """Switch to control customization screen."""
        self.showing_controls = True
        print("🎮 Switching to control customization screen")
    
    def hide_controls_screen(self):
        """Return to main settings screen."""
        self.showing_controls = False
        self.waiting_for_key = False
        self.selected_control = None
        print("🔧 Returning to main settings screen")
    
    def handle_control_click(self, pos: Tuple[int, int]):
        """Handle clicks on control buttons."""
        x, y = pos
        
        # Check reset controls button
        if hasattr(self, 'reset_controls_rect') and self.reset_controls_rect.collidepoint(x, y):
            self.reset_controls()
            # Play sound
            if self.audio and hasattr(self.audio, 'play_sound'):
                self.audio.play_sound('click')
            return
        
        # Check if any control button was clicked
        for action, button in self.control_buttons.items():
            if button['rect'].collidepoint(x, y):
                # Start waiting for key input
                self.waiting_for_key = True
                self.selected_control = action
                button['is_selected'] = True
                
                # Play sound
                if self.audio and hasattr(self.audio, 'play_sound'):
                    self.audio.play_sound('click')
                break
    
    def handle_key_input(self, key_code: int):
        """Handle key input when rebinding controls."""
        if self.waiting_for_key and self.selected_control:
            # Set the new control binding
            self.set_control(self.selected_control, key_code)
            
            # Reset selection state
            self.waiting_for_key = False
            if self.selected_control in self.control_buttons:
                self.control_buttons[self.selected_control]['is_selected'] = False
            self.selected_control = None
            
            # Play sound
            if self.audio and hasattr(self.audio, 'play_sound'):
                self.audio.play_sound('click')
    
    def handle_control_mouse_move(self, pos: Tuple[int, int]):
        """Handle mouse movement for control button hover effects."""
        x, y = pos
        
        # Reset all hover states
        for button in self.control_buttons.values():
            button['is_hovered'] = False
        
        # Check which button is hovered
        for button in self.control_buttons.values():
            if button['rect'].collidepoint(x, y):
                button['is_hovered'] = True
                break
    
    def draw_controls_screen(self):
        """Draw the control customization screen."""
        # Clear screen with dark background
        self.screen.fill((20, 20, 50))
        
        # Draw title
        title_font = pygame.font.SysFont('Arial', 48, bold=True)
        title_text = "🎮 Control Settings"
        title_surf = title_font.render(title_text, True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(self.width//2, 80))
        self.screen.blit(title_surf, title_rect)
        
        # Draw subtitle
        subtitle_font = pygame.font.SysFont('Arial', 16)
        subtitle_text = "Click any control to rebind • Press ESC to return"
        subtitle_surf = subtitle_font.render(subtitle_text, True, (100, 255, 100))
        subtitle_rect = subtitle_surf.get_rect(center=(self.width//2, 110))
        self.screen.blit(subtitle_surf, subtitle_rect)
        
        # Draw control categories and buttons
        control_categories = {
            'Movement': ['move_up', 'move_down', 'move_left', 'move_right'],
            'Actions': ['action', 'menu_confirm', 'menu_cancel'],
            'Music': ['music_next', 'music_prev', 'music_pause'],
            'System': ['fullscreen_toggle', 'menu_tab']
        }
        
        y_start = 160
        category_spacing = 120
        
        for category, actions in control_categories.items():
            # Draw category label
            category_font = pygame.font.SysFont('Arial', 24, bold=True)
            category_surf = category_font.render(category, True, (200, 200, 255))
            category_rect = category_surf.get_rect(center=(self.width//2, y_start))
            self.screen.blit(category_surf, category_rect)
            
            y_start += 40
            
            # Draw control buttons for this category
            for i, action in enumerate(actions):
                if action in self.control_buttons:
                    button = self.control_buttons[action]
                    self.draw_control_button(button, y_start + i * 50)
            
            y_start += len(actions) * 50 + category_spacing
        
        # Draw back button
        back_font = pygame.font.SysFont('Arial', 20)
        back_text = "Press ESC to return to settings"
        back_surf = back_font.render(back_text, True, (150, 150, 150))
        back_rect = back_surf.get_rect(center=(self.width//2, self.height - 50))
        self.screen.blit(back_surf, back_rect)
        
        # Draw reset controls button
        reset_font = pygame.font.SysFont('Arial', 18)
        reset_text = "Reset to Defaults"
        reset_surf = reset_font.render(reset_text, True, (255, 200, 100))
        reset_rect = reset_surf.get_rect(center=(self.width//2, self.height - 80))
        self.screen.blit(reset_surf, reset_rect)
        
        # Store reset button rect for click detection
        self.reset_controls_rect = reset_rect
    
    def draw_control_button(self, button: Dict, y_pos: int):
        """Draw a single control button."""
        # Update button position
        button['rect'].y = y_pos
        
        rect = button['rect']
        is_hovered = button['is_hovered']
        is_selected = button['is_selected']
        action = button['action']
        
        # Get current key binding
        current_key = self.get_control(action)
        key_name = self.get_key_name(current_key)
        
        # Determine button color
        if is_selected:
            bg_color = (255, 100, 100)  # Red when waiting for input
        elif is_hovered:
            bg_color = (100, 140, 220)
        else:
            bg_color = (60, 100, 180)
        
        # Draw button background
        pygame.draw.rect(self.screen, bg_color, rect, border_radius=8)
        pygame.draw.rect(self.screen, (120, 160, 240), rect, 2, border_radius=8)
        
        # Draw label and key
        label_font = pygame.font.SysFont('Arial', 16)
        key_font = pygame.font.SysFont('Arial', 14, bold=True)
        
        # Draw action label
        label_surf = label_font.render(button['label'], True, (255, 255, 255))
        label_rect = label_surf.get_rect(midleft=(rect.x + 10, rect.centery))
        self.screen.blit(label_surf, label_rect)
        
        # Draw key binding
        if is_selected:
            key_text = "Press any key..."
            key_color = (255, 255, 255)
        else:
            key_text = key_name
            key_color = (200, 255, 200)
        
        key_surf = key_font.render(key_text, True, key_color)
        key_rect = key_surf.get_rect(midright=(rect.right - 10, rect.centery))
        self.screen.blit(key_surf, key_rect)
    
    def reset_settings(self):
        """Reset all settings to defaults."""
        default_settings = {
            'audio_volume': 0.8,
            'music_volume': 0.6,
            'screen_resolution': (1600, 900),
            'fullscreen': False,
            'vsync': True,
            'particle_effects': True,
            'brightness': 1.0,
            'sensitivity': 1.0
        }
        
        self.settings.update(default_settings)
        
        # Update UI elements
        for name, slider in self.sliders.items():
            if name in self.settings:
                slider['value'] = self.settings[name]
        
        for name, button in self.buttons.items():
            if name in self.settings:
                button['is_pressed'] = self.settings[name]
        
        print("🔄 Settings reset to defaults")
    
    def get_setting(self, name: str):
        """Get a setting value."""
        return self.settings.get(name)
    
    def set_setting(self, name: str, value):
        """Set a setting value."""
        self.settings[name] = value
        if name in self.sliders:
            self.sliders[name]['value'] = value
        if name in self.buttons:
            self.buttons[name]['is_pressed'] = value
    
    def get_key_name(self, key_code: int) -> str:
        """Convert pygame key code to readable name."""
        key_names = {
            pygame.K_UP: "↑ Up",
            pygame.K_DOWN: "↓ Down", 
            pygame.K_LEFT: "← Left",
            pygame.K_RIGHT: "→ Right",
            pygame.K_SPACE: "Space",
            pygame.K_RETURN: "Enter",
            pygame.K_ESCAPE: "Escape",
            pygame.K_TAB: "Tab",
            pygame.K_RIGHTBRACKET: "]",
            pygame.K_LEFTBRACKET: "[",
            pygame.K_p: "P",
            pygame.K_F11: "F11",
            pygame.K_w: "W",
            pygame.K_s: "S",
            pygame.K_a: "A",
            pygame.K_d: "D",
            pygame.K_z: "Z",
            pygame.K_x: "X",
            pygame.K_c: "C",
            pygame.K_v: "V",
            pygame.K_b: "B",
            pygame.K_n: "N",
            pygame.K_m: "M",
            pygame.K_q: "Q",
            pygame.K_e: "E",
            pygame.K_r: "R",
            pygame.K_f: "F",
            pygame.K_g: "G",
            pygame.K_h: "H",
            pygame.K_j: "J",
            pygame.K_k: "K",
            pygame.K_l: "L",
            pygame.K_y: "Y",
            pygame.K_u: "U",
            pygame.K_i: "I",
            pygame.K_o: "O",
            pygame.K_0: "0",
            pygame.K_1: "1",
            pygame.K_2: "2",
            pygame.K_3: "3",
            pygame.K_4: "4",
            pygame.K_5: "5",
            pygame.K_6: "6",
            pygame.K_7: "7",
            pygame.K_8: "8",
            pygame.K_9: "9"
        }
        return key_names.get(key_code, f"Key {key_code}")
    
    def get_control(self, action: str) -> int:
        """Get the key code for a specific action."""
        return self.controls.get(action, pygame.K_UNKNOWN)
    
    def set_control(self, action: str, key_code: int):
        """Set a control mapping."""
        self.controls[action] = key_code
        print(f"🎮 {action} bound to {self.get_key_name(key_code)}")
        self.save_controls()
    
    def save_controls(self):
        """Save control mappings to file."""
        try:
            with open('game_controls.json', 'w') as f:
                json.dump(self.controls, f, indent=2)
            print("💾 Controls saved to file")
        except Exception as e:
            print(f"❌ Could not save controls: {e}")
    
    def load_controls(self):
        """Load control mappings from file."""
        try:
            with open('game_controls.json', 'r') as f:
                loaded_controls = json.load(f)
                self.controls.update(loaded_controls)
            print("✅ Controls loaded from file")
        except FileNotFoundError:
            print("📝 No saved controls found, using defaults")
        except Exception as e:
            print(f"⚠️ Could not load controls: {e}")
    
    def reset_controls(self):
        """Reset controls to defaults."""
        self.controls = {
            'move_up': pygame.K_UP,
            'move_down': pygame.K_DOWN,
            'move_left': pygame.K_LEFT,
            'move_right': pygame.K_RIGHT,
            'action': pygame.K_SPACE,
            'menu_confirm': pygame.K_RETURN,
            'menu_cancel': pygame.K_ESCAPE,
            'menu_tab': pygame.K_TAB,
            'music_next': pygame.K_RIGHTBRACKET,
            'music_prev': pygame.K_LEFTBRACKET,
            'music_pause': pygame.K_p,
            'fullscreen_toggle': pygame.K_F11
        }
        print("🔄 Controls reset to defaults")
        self.save_controls()
    
    def get_settings_summary(self) -> Dict[str, any]:
        """Get a summary of all current settings."""
        return {
            'audio_volume': self.settings.get('audio_volume', 0.8),
            'music_volume': self.settings.get('music_volume', 0.6),
            'brightness': self.settings.get('brightness', 1.0),
            'sensitivity': self.settings.get('sensitivity', 1.0),
            'fullscreen': self.settings.get('fullscreen', False),
            'vsync': self.settings.get('vsync', True),
            'particle_effects': self.settings.get('particle_effects', True)
        }
    
    def print_settings_status(self):
        """Print the current status of all settings."""
        summary = self.get_settings_summary()
        print("\n🔧 Current Settings Status:")
        print(f"   🔊 Audio Volume: {summary['audio_volume']:.1f}")
        print(f"   🎵 Music Volume: {summary['music_volume']:.1f}")
        print(f"   💡 Brightness: {summary['brightness']:.1f}")
        print(f"   🖱️ Mouse Sensitivity: {summary['sensitivity']:.1f}")
        print(f"   🖥️ Fullscreen: {'ON' if summary['fullscreen'] else 'OFF'}")
        print(f"   🔄 V-Sync: {'ON' if summary['vsync'] else 'OFF'}")
        print(f"   ✨ Particle Effects: {'ON' if summary['particle_effects'] else 'OFF'}")
        print() 
    
    def get_controls_summary(self) -> Dict[str, str]:
        """Get a summary of all current control mappings."""
        return {
            'move_up': self.get_key_name(self.get_control('move_up')),
            'move_down': self.get_key_name(self.get_control('move_down')),
            'move_left': self.get_key_name(self.get_control('move_left')),
            'move_right': self.get_key_name(self.get_control('move_right')),
            'action': self.get_key_name(self.get_control('action')),
            'music_next': self.get_key_name(self.get_control('music_next')),
            'music_prev': self.get_key_name(self.get_control('music_prev')),
            'music_pause': self.get_key_name(self.get_control('music_pause'))
        }
    
    def print_controls_status(self):
        """Print the current status of all controls."""
        summary = self.get_controls_summary()
        print("\n🎮 Current Control Mappings:")
        print(f"   ↑ Move Up: {summary['move_up']}")
        print(f"   ↓ Move Down: {summary['move_down']}")
        print(f"   ← Move Left: {summary['move_left']}")
        print(f"   → Move Right: {summary['move_right']}")
        print(f"   🎯 Action: {summary['action']}")
        print(f"   ⏭️ Next Song: {summary['music_next']}")
        print(f"   ⏮️ Previous Song: {summary['music_prev']}")
        print(f"   ⏸️ Pause/Play: {summary['music_pause']}")
        print() 