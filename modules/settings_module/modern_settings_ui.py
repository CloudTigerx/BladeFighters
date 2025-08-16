"""
Modern Settings UI System
A beautiful, animated settings interface with modern design patterns.
"""

import pygame
import math
import time
from typing import Dict, Optional, Tuple, List, Callable, Any
from dataclasses import dataclass
from enum import Enum
import os

# Define ASSET_PATH
ASSET_PATH = "puzzleassets"

# Color scheme for modern UI
class Colors:
    # Primary colors
    PRIMARY = (52, 152, 219)      # Blue
    SECONDARY = (155, 89, 182)    # Purple
    SUCCESS = (46, 204, 113)      # Green
    WARNING = (241, 196, 15)      # Yellow
    DANGER = (231, 76, 60)        # Red
    
    # Background colors
    BG_DARK = (44, 62, 80)        # Dark blue-gray
    BG_LIGHT = (52, 73, 94)       # Lighter blue-gray
    BG_PANEL = (41, 128, 185)     # Panel background
    
    # Text colors
    TEXT_PRIMARY = (236, 240, 241)   # Light gray
    TEXT_SECONDARY = (189, 195, 199) # Medium gray
    TEXT_DISABLED = (127, 140, 141)  # Dark gray
    
    # Accent colors
    ACCENT_1 = (26, 188, 156)     # Turquoise
    ACCENT_2 = (230, 126, 34)     # Orange
    ACCENT_3 = (142, 68, 173)     # Purple
    ACCENT = (52, 152, 219)       # Blue accent
    SUCCESS = (46, 204, 113)      # Green success
    TEXT_DARK = (127, 140, 141)   # Dark text

class AnimationState(Enum):
    """Animation states for UI elements."""
    IDLE = "idle"
    HOVER = "hover"
    ACTIVE = "active"
    DISABLED = "disabled"

@dataclass
class AnimationData:
    """Data for smooth animations."""
    start_value: float
    target_value: float
    start_time: float
    duration: float
    easing: str = "ease_out"

class ModernSlider:
    """Modern animated slider component."""
    
    def __init__(self, x: int, y: int, width: int, height: int, min_val: float, max_val: float, initial_val: float):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.target_value = initial_val
        
        # Animation
        self.animation = None
        self.hover_scale = 1.0
        self.target_hover_scale = 1.0
        
        # Interaction
        self.dragging = False
        self.hovered = False
        
    def update(self, dt: float):
        """Update slider animations."""
        # Update value animation
        if self.animation:
            elapsed = time.time() - self.animation.start_time
            progress = min(elapsed / self.animation.duration, 1.0)
            
            if progress >= 1.0:
                self.value = self.animation.target_value
                self.animation = None
            else:
                # Easing function
                if self.animation.easing == "ease_out":
                    progress = 1 - (1 - progress) ** 3
                elif self.animation.easing == "ease_in":
                    progress = progress ** 3
                
                self.value = self.animation.start_value + (self.animation.target_value - self.animation.start_value) * progress
        
        # Update hover animation
        if self.hovered:
            self.target_hover_scale = 1.1
        else:
            self.target_hover_scale = 1.0
            
        self.hover_scale += (self.target_hover_scale - self.hover_scale) * 10 * dt
    
    def set_value(self, value: float, animate: bool = True):
        """Set slider value with optional animation."""
        value = max(self.min_val, min(self.max_val, value))
        if animate and abs(value - self.value) > 0.01:
            self.animation = AnimationData(
                start_value=self.value,
                target_value=value,
                start_time=time.time(),
                duration=0.3
            )
        else:
            self.value = value
    
    def handle_event(self, event) -> bool:
        """Handle pygame events for the slider."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.get_rect().collidepoint(event.pos):
                self.dragging = True
                self._update_value_from_pos(event.pos[0])
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            # Update hover state
            was_hovered = self.hovered
            self.hovered = self.get_rect().collidepoint(event.pos)
            
            # Update value if dragging
            if self.dragging:
                self._update_value_from_pos(event.pos[0])
                return True
        
        return False
    
    def _update_value_from_pos(self, x: int):
        """Update slider value based on mouse position."""
        knob_x = max(self.x, min(self.x + self.width, x))
        progress = (knob_x - self.x) / self.width
        new_value = self.min_val + (self.max_val - self.min_val) * progress
        self.set_value(new_value, animate=False)
    
    def get_rect(self) -> pygame.Rect:
        """Get the slider's bounding rectangle."""
        return pygame.Rect(self.x - 10, self.y - 10, self.width + 20, self.height + 20)
    
    def draw(self, surface: pygame.Surface):
        """Draw the slider with modern styling."""
        # Calculate positions
        progress = (self.value - self.min_val) / (self.max_val - self.min_val)
        knob_x = self.x + progress * self.width
        
        # Draw track
        track_rect = pygame.Rect(self.x, self.y + self.height // 2 - 2, self.width, 4)
        pygame.draw.rect(surface, Colors.BG_LIGHT, track_rect, border_radius=2)
        
        # Draw filled track
        filled_width = int(self.width * progress)
        if filled_width > 0:
            filled_rect = pygame.Rect(self.x, self.y + self.height // 2 - 2, filled_width, 4)
            pygame.draw.rect(surface, Colors.PRIMARY, filled_rect, border_radius=2)
        
        # Draw knob
        knob_radius = int(8 * self.hover_scale)
        knob_color = Colors.PRIMARY if self.hovered or self.dragging else Colors.TEXT_SECONDARY
        pygame.draw.circle(surface, knob_color, (int(knob_x), self.y + self.height // 2), knob_radius)
        
        # Draw knob border
        pygame.draw.circle(surface, Colors.TEXT_PRIMARY, (int(knob_x), self.y + self.height // 2), knob_radius, 2)

class ModernDropdown:
    """Modern dropdown component for resolution selection."""
    
    def __init__(self, x: int, y: int, width: int, height: int, options: List[str], initial_value: str = None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.options = options
        self.selected_value = initial_value or options[0] if options else ""
        self.is_open = False
        self.hovered = False
        
        # Animation
        self.hover_scale = 1.0
        self.target_hover_scale = 1.0
        
    def update(self, dt: float):
        """Update dropdown animations."""
        if self.hovered:
            self.target_hover_scale = 1.02
        else:
            self.target_hover_scale = 1.0
            
        self.hover_scale += (self.target_hover_scale - self.hover_scale) * 8 * dt
    
    def handle_event(self, event) -> bool:
        """Handle pygame events for the dropdown."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.get_rect().collidepoint(event.pos):
                self.is_open = not self.is_open
                return True
            elif self.is_open:
                # Check if click is on dropdown options
                dropdown_y = self.y + self.height
                for i, option in enumerate(self.options):
                    option_rect = pygame.Rect(self.x, dropdown_y + i * 30, self.width, 30)
                    if option_rect.collidepoint(event.pos):
                        self.selected_value = option
                        self.is_open = False
                        return True
                # Click outside dropdown, close it
                self.is_open = False
        elif event.type == pygame.MOUSEMOTION:
            self.hovered = self.get_rect().collidepoint(event.pos)
        
        return False
    
    def get_rect(self) -> pygame.Rect:
        """Get the dropdown's bounding rectangle."""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def draw(self, surface: pygame.Surface, font: pygame.font.Font):
        """Draw the dropdown with modern styling."""
        # Draw main dropdown button
        button_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        # Background color
        bg_color = Colors.SECONDARY if self.hovered else Colors.BG_PANEL
        pygame.draw.rect(surface, bg_color, button_rect, border_radius=6)
        pygame.draw.rect(surface, Colors.PRIMARY, button_rect, 2, border_radius=6)
        
        # Draw selected value text
        text_surface = font.render(self.selected_value, True, Colors.TEXT_PRIMARY)
        text_rect = text_surface.get_rect(midleft=(self.x + 10, self.y + self.height // 2))
        surface.blit(text_surface, text_rect)
        
        # Draw dropdown arrow
        arrow_points = [
            (self.x + self.width - 20, self.y + self.height // 2 - 3),
            (self.x + self.width - 20, self.y + self.height // 2 + 3),
            (self.x + self.width - 15, self.y + self.height // 2)
        ]
        pygame.draw.polygon(surface, Colors.TEXT_PRIMARY, arrow_points)
        
        # Draw dropdown options if open
        if self.is_open:
            dropdown_y = self.y + self.height
            for i, option in enumerate(self.options):
                option_rect = pygame.Rect(self.x, dropdown_y + i * 30, self.width, 30)
                
                # Background for option
                option_bg = Colors.PRIMARY if option == self.selected_value else Colors.BG_DARK
                pygame.draw.rect(surface, option_bg, option_rect, border_radius=4)
                pygame.draw.rect(surface, Colors.BG_LIGHT, option_rect, 1, border_radius=4)
                
                # Option text
                option_text = font.render(option, True, Colors.TEXT_PRIMARY)
                option_text_rect = option_text.get_rect(midleft=(self.x + 10, dropdown_y + i * 30 + 15))
                surface.blit(option_text, option_text_rect)


class ModernToggle:
    """Modern toggle switch component."""
    
    def __init__(self, x: int, y: int, width: int, height: int, label: str, value: bool = False):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.label = label
        self.value = value
        
        # Animation
        self.animation_time = 0
        self.target_scale = 1.0
        self.current_scale = 1.0
        self.knob_offset = 0 if not value else width - height
        
        # Colors
        self.bg_color = Colors.BG_DARK
        self.border_color = Colors.PRIMARY
        self.text_color = Colors.TEXT_PRIMARY
        self.knob_color = Colors.ACCENT if value else Colors.TEXT_DARK
        self.active_color = Colors.SUCCESS
        
        # Font
        self.font = pygame.font.SysFont('Arial', 16)
    
    def handle_event(self, event) -> bool:
        """Handle pygame events. Returns True if event was handled."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.get_rect().collidepoint(event.pos):
                self.value = not self.value
                self.knob_offset = 0 if not self.value else self.width - self.height
                self.knob_color = Colors.ACCENT if self.value else Colors.TEXT_DARK
                return True
        return False
    
    def update(self, dt: float):
        """Update animations."""
        # Smooth scale animation
        self.current_scale += (self.target_scale - self.current_scale) * dt * 10
        self.animation_time += dt
        
        # Smooth knob animation
        target_offset = 0 if not self.value else self.width - self.height
        self.knob_offset += (target_offset - self.knob_offset) * dt * 15
    
    def get_rect(self) -> pygame.Rect:
        """Get the toggle's bounding rectangle."""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def draw(self, surface: pygame.Surface):
        """Draw the toggle switch."""
        # Draw toggle background
        toggle_rect = self.get_rect()
        toggle_rect.width = int(toggle_rect.width * self.current_scale)
        toggle_rect.height = int(toggle_rect.height * self.current_scale)
        toggle_rect.center = self.get_rect().center
        
        # Background
        bg_color = self.active_color if self.value else self.bg_color
        pygame.draw.rect(surface, bg_color, toggle_rect, border_radius=toggle_rect.height // 2)
        pygame.draw.rect(surface, self.border_color, toggle_rect, 2, border_radius=toggle_rect.height // 2)
        
        # Knob
        knob_size = toggle_rect.height - 4
        knob_rect = pygame.Rect(
            toggle_rect.x + 2 + self.knob_offset * (toggle_rect.width / self.width),
            toggle_rect.y + 2,
            knob_size,
            knob_size
        )
        pygame.draw.rect(surface, self.knob_color, knob_rect, border_radius=knob_size // 2)
        
        # Label
        label_surface = self.font.render(self.label, True, self.text_color)
        label_rect = label_surface.get_rect(midleft=(toggle_rect.right + 15, toggle_rect.centery))
        surface.blit(label_surface, label_rect)


class ModernButton:
    """Modern animated button component."""
    
    def __init__(self, x: int, y: int, width: int, height: int, text: str, action: str = None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.action = action
        
        # Animation
        self.hover_scale = 1.0
        self.target_hover_scale = 1.0
        self.press_scale = 1.0
        self.target_press_scale = 1.0
        
        # State
        self.hovered = False
        self.pressed = False
        self.disabled = False
        
    def update(self, dt: float):
        """Update button animations."""
        # Update hover animation
        if self.hovered and not self.disabled:
            self.target_hover_scale = 1.05
        else:
            self.target_hover_scale = 1.0
            
        self.hover_scale += (self.target_hover_scale - self.hover_scale) * 10 * dt
        
        # Update press animation
        if self.pressed:
            self.target_press_scale = 0.95
        else:
            self.target_press_scale = 1.0
            
        self.press_scale += (self.target_press_scale - self.press_scale) * 15 * dt
    
    def handle_event(self, event) -> Optional[str]:
        """Handle pygame events for the button."""
        if self.disabled:
            return None
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.get_rect().collidepoint(event.pos):
                self.pressed = True
                return None
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.pressed and self.get_rect().collidepoint(event.pos):
                self.pressed = False
                return self.action
            self.pressed = False
        elif event.type == pygame.MOUSEMOTION:
            self.hovered = self.get_rect().collidepoint(event.pos)
        
        return None
    
    def get_rect(self) -> pygame.Rect:
        """Get the button's bounding rectangle."""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def draw(self, surface: pygame.Surface, font: pygame.font.Font):
        """Draw the button with modern styling."""
        # Calculate final scale
        final_scale = self.hover_scale * self.press_scale
        
        # Calculate scaled dimensions
        scaled_width = int(self.width * final_scale)
        scaled_height = int(self.height * final_scale)
        scaled_x = self.x + (self.width - scaled_width) // 2
        scaled_y = self.y + (self.height - scaled_height) // 2
        
        # Determine colors
        if self.disabled:
            bg_color = Colors.BG_LIGHT
            text_color = Colors.TEXT_DISABLED
        elif self.pressed:
            bg_color = Colors.PRIMARY
            text_color = Colors.TEXT_PRIMARY
        elif self.hovered:
            bg_color = Colors.SECONDARY
            text_color = Colors.TEXT_PRIMARY
        else:
            bg_color = Colors.BG_PANEL
            text_color = Colors.TEXT_PRIMARY
        
        # Draw button background
        button_rect = pygame.Rect(scaled_x, scaled_y, scaled_width, scaled_height)
        pygame.draw.rect(surface, bg_color, button_rect, border_radius=8)
        
        # Draw border
        border_color = Colors.PRIMARY if self.hovered else Colors.BG_LIGHT
        pygame.draw.rect(surface, border_color, button_rect, 2, border_radius=8)
        
        # Draw text
        text_surface = font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=button_rect.center)
        surface.blit(text_surface, text_rect)

class ModernSettingsUI:
    """
    Modern, animated settings interface with beautiful design.
    """
    
    def __init__(self, screen: pygame.Surface, config_service, on_apply_callbacks: Dict[str, Callable] = None):
        self.screen = screen
        self.config = config_service
        self.on_apply = on_apply_callbacks or {}
        
        # Screen dimensions
        self.width = screen.get_width()
        self.height = screen.get_height()
        
        # Fonts
        self.font_title = pygame.font.SysFont('Arial', 32, bold=True)
        self.font_subtitle = pygame.font.SysFont('Arial', 24, bold=True)
        self.font_body = pygame.font.SysFont('Arial', 18)
        self.font_small = pygame.font.SysFont('Arial', 14)
        
        # UI state
        self.visible = False
        self.active_tab = 'Graphics'
        self.tabs = ['Graphics', 'Audio', 'Controls', 'Gameplay']
        
        # Animation
        self.animation_start_time = 0
        self.animation_duration = 0.5
        self.panel_scale = 0.0
        self.background_alpha = 0
        
        # UI components
        self.sliders = {}
        self.buttons = {}
        self.toggles = {}
        self.dropdowns = {}
        
        # Load menu assets
        self._load_menu_assets()
        
        # Initialize UI components
        self._create_ui_components()
        
        # Settings categories
        self.settings = {
            'Graphics': {
                'brightness': {'min': 0.3, 'max': 1.0, 'default': 1.0},
                'resolution': {'options': [
                    '3840x2160',  # Ultra (4K) - Ultra resolution assets
                    '1920x1080',  # High (Full HD) - High resolution assets
                    '1536x1024',  # Medium - Medium resolution assets
                    '800x600'     # Low - Low resolution assets
                ], 'default': '1920x1080'},
                'fullscreen': {'type': 'toggle', 'default': False},
                'native_fullscreen': {'type': 'toggle', 'default': False},
                'borderless': {'type': 'toggle', 'default': False},
                'vsync': {'type': 'toggle', 'default': True},
                'particle_effects': {'type': 'toggle', 'default': True},
                'show_fps': {'type': 'toggle', 'default': False}
            },
            'Audio': {
                'master_volume': {'min': 0.0, 'max': 1.0, 'default': 0.8},
                'music_volume': {'min': 0.0, 'max': 1.0, 'default': 0.7},
                'sfx_volume': {'min': 0.0, 'max': 1.0, 'default': 0.9},
                'music_enabled': {'type': 'toggle', 'default': True},
                'sfx_enabled': {'type': 'toggle', 'default': True}
            },
            'Controls': {
                'mouse_sensitivity': {'min': 0.5, 'max': 2.0, 'default': 1.0}
            },
            'Gameplay': {
                'difficulty': {'min': 1, 'max': 10, 'default': 5},
                'auto_save': {'type': 'toggle', 'default': True},
                'tutorial_enabled': {'type': 'toggle', 'default': True}
            }
        }
    
    def _load_menu_assets(self):
        """Load menu assets for the settings UI."""
        try:
            # Load 9-panel image for settings container
            self.panel_9slice = pygame.image.load(os.path.join(ASSET_PATH, "menus", "panel_9slice.png")).convert_alpha()
            print("✅ Loaded 9-panel settings container")
            
            # Load button assets
            self.button_normal = pygame.image.load(os.path.join(ASSET_PATH, "menus", "button_normal.png")).convert_alpha()
            self.button_hover = pygame.image.load(os.path.join(ASSET_PATH, "menus", "button_hover.png")).convert_alpha()
            self.button_pressed = pygame.image.load(os.path.join(ASSET_PATH, "menus", "button_ pressed.png")).convert_alpha()
            print("✅ Loaded button assets")
            
            # Load tab assets
            self.tab_active = pygame.image.load(os.path.join(ASSET_PATH, "menus", "tab_active.png")).convert_alpha()
            self.tab_inactive = pygame.image.load(os.path.join(ASSET_PATH, "menus", "tab_inactive.png")).convert_alpha()
            print("✅ Loaded tab assets")
            
        except Exception as e:
            print(f"⚠️ Failed to load menu assets: {e}")
            self.panel_9slice = None
            self.button_normal = None
            self.button_hover = None
            self.button_pressed = None
            self.tab_active = None
            self.tab_inactive = None
    
    def _create_ui_components(self):
        """Create all UI components."""
        # Calculate panel dimensions - use 70% of screen width
        panel_width = int(self.width * 0.7)
        panel_height = min(600, self.height - 120)  # Increased height for better spacing
        panel_x = (self.width - panel_width) // 2
        panel_y = (self.height - panel_height) // 2
        
        # Create tab buttons
        tab_width = panel_width // len(self.tabs)
        for i, tab in enumerate(self.tabs):
            x = panel_x + i * tab_width
            y = panel_y - 40
            self.buttons[f'tab_{tab}'] = ModernButton(x, y, tab_width, 40, tab, f'switch_tab_{tab}')
        
        # Create action buttons
        button_width = 120
        button_height = 40
        button_spacing = 20
        
        # Apply button
        apply_x = panel_x + panel_width - button_width - button_spacing
        apply_y = panel_y + panel_height - button_height - 20
        self.buttons['apply'] = ModernButton(apply_x, apply_y, button_width, button_height, "Apply", "apply")
        
        # Cancel button
        cancel_x = apply_x - button_width - button_spacing
        cancel_y = apply_y
        self.buttons['cancel'] = ModernButton(cancel_x, cancel_y, button_width, button_height, "Cancel", "cancel")
        
        # Reset button
        reset_x = cancel_x - button_width - button_spacing
        reset_y = apply_y
        self.buttons['reset'] = ModernButton(reset_x, reset_y, button_width, button_height, "Reset", "reset")
    
    def _create_sliders_for_tab(self, tab: str):
        """Create sliders, dropdowns, and toggles for the current tab."""
        self.sliders.clear()
        self.dropdowns.clear()
        self.toggles.clear()
        
        if tab not in self.settings:
            return
        
        # Calculate positions - use 70% of screen width
        panel_width = int(self.width * 0.7)
        panel_height = min(600, self.height - 120)
        panel_x = (self.width - panel_width) // 2
        panel_y = (self.height - panel_height) // 2
        
        content_x = panel_x + 50  # Increased margin for better spacing
        content_y = panel_y + 100  # Increased top margin
        slider_width = panel_width - 100  # Increased margin
        slider_height = 20
        spacing = 70  # Increased spacing between elements
        
        # Create sliders, dropdowns, and toggles for current tab
        for i, (setting_name, setting_data) in enumerate(self.settings[tab].items()):
            y = content_y + i * spacing
            
            if 'min' in setting_data and 'max' in setting_data:  # Numeric slider
                current_value = self.config.get(setting_name, setting_data['default'])
                
                slider = ModernSlider(
                    content_x, y, slider_width, slider_height,
                    setting_data['min'], setting_data['max'], current_value
                )
                self.sliders[setting_name] = slider
            elif 'options' in setting_data:  # Dropdown
                current_value = self.config.get(setting_name, setting_data['default'])
                
                dropdown = ModernDropdown(
                    content_x, y, slider_width, 30,
                    setting_data['options'], current_value
                )
                self.dropdowns[setting_name] = dropdown
            elif setting_data.get('type') == 'toggle':  # Toggle switch
                current_value = self.config.get(setting_name, setting_data['default'])
                
                # Create a friendly label for the toggle
                label_map = {
                    'fullscreen': 'Fullscreen',
                    'native_fullscreen': 'Native Fullscreen',
                    'borderless': 'Borderless Windowed',
                    'vsync': 'V-Sync',
                    'particle_effects': 'Particle Effects',
                    'show_fps': 'Show FPS',
                    'music_enabled': 'Music Enabled',
                    'sfx_enabled': 'Sound Effects Enabled',
                    'auto_save': 'Auto Save',
                    'tutorial_enabled': 'Tutorial Enabled'
                }
                label = label_map.get(setting_name, setting_name.replace('_', ' ').title())
                
                toggle = ModernToggle(
                    content_x + 200, y, 60, 30, label, current_value  # Position toggle to the right
                )
                self.toggles[setting_name] = toggle
    
    def open(self):
        """Open the settings UI with animation."""
        self.visible = True
        self.animation_start_time = time.time()
        self._create_sliders_for_tab(self.active_tab)
    
    def update_screen(self, new_screen):
        """Update the screen reference when resolution changes."""
        self.screen = new_screen
        # Recalculate positions based on new screen size
        self._create_ui_components()
        
    def close(self):
        """Close the settings UI."""
        self.visible = False
    
    def is_open(self) -> bool:
        """Check if settings UI is open."""
        return self.visible
    
    def update(self, dt: float):
        """Update settings UI animations."""
        if not self.visible:
            return
        
        # Update panel animation
        elapsed = time.time() - self.animation_start_time
        progress = min(elapsed / self.animation_duration, 1.0)
        
        # Easing function for smooth animation
        progress = 1 - (1 - progress) ** 3  # Ease out cubic
        
        self.panel_scale = progress
        self.background_alpha = int(progress * 128)
        
        # Update all components
        for slider in self.sliders.values():
            slider.update(dt)
        
        for button in self.buttons.values():
            button.update(dt)
        
        for dropdown in self.dropdowns.values():
            dropdown.update(dt)
        
        for toggle in self.toggles.values():
            toggle.update(dt)
    
    def handle_events(self, events) -> Optional[str]:
        """Handle pygame events."""
        if not self.visible:
            return None
        
        for event in events:
            # Handle dropdowns first (they need priority for click detection)
            for setting_name, dropdown in self.dropdowns.items():
                if dropdown.handle_event(event):
                    # Update config immediately for live preview
                    self.config.set(setting_name, dropdown.selected_value)
                    # Call apply callback if available
                    if setting_name in self.on_apply:
                        try:
                            self.on_apply[setting_name](dropdown.selected_value)
                        except Exception as e:
                            print(f"Error applying setting {setting_name}: {e}")
                    return None
            
            # Handle toggles
            for setting_name, toggle in self.toggles.items():
                if toggle.handle_event(event):
                    # Update config immediately for live preview
                    self.config.set(setting_name, toggle.value)
                    # Call apply callback if available
                    if setting_name in self.on_apply:
                        try:
                            self.on_apply[setting_name](toggle.value)
                        except Exception as e:
                            print(f"Error applying setting {setting_name}: {e}")
                    return None
            
            # Handle tab switching
            for button in self.buttons.values():
                action = button.handle_event(event)
                if action and action.startswith('switch_tab_'):
                    tab_name = action.replace('switch_tab_', '')
                    self.active_tab = tab_name
                    self._create_sliders_for_tab(tab_name)
                    return None
                elif action in ['apply', 'cancel', 'reset']:
                    if action == 'apply':
                        self._apply_settings()
                    elif action == 'cancel':
                        self.close()
                    elif action == 'reset':
                        self._reset_settings()
                    return action
            
            # Handle sliders
            for setting_name, slider in self.sliders.items():
                if slider.handle_event(event):
                    # Update config immediately for live preview
                    self.config.set(setting_name, slider.value)
                    # Call apply callback if available
                    if setting_name in self.on_apply:
                        try:
                            self.on_apply[setting_name](slider.value)
                        except Exception as e:
                            print(f"Error applying setting {setting_name}: {e}")
                    return None
            
            # Handle escape key
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.close()
                return "close"
        
        return None
    
    def _apply_settings(self):
        """Apply current settings."""
        for setting_name, slider in self.sliders.items():
            self.config.set(setting_name, slider.value)
            
            # Call apply callback if available
            if setting_name in self.on_apply:
                try:
                    self.on_apply[setting_name](slider.value)
                except Exception as e:
                    print(f"Error applying setting {setting_name}: {e}")
        
        for setting_name, dropdown in self.dropdowns.items():
            self.config.set(setting_name, dropdown.selected_value)
            
            # Call apply callback if available
            if setting_name in self.on_apply:
                try:
                    self.on_apply[setting_name](dropdown.selected_value)
                except Exception as e:
                    print(f"Error applying setting {setting_name}: {e}")
        
        for setting_name, toggle in self.toggles.items():
            self.config.set(setting_name, toggle.value)
            
            # Call apply callback if available
            if setting_name in self.on_apply:
                try:
                    self.on_apply[setting_name](toggle.value)
                except Exception as e:
                    print(f"Error applying setting {setting_name}: {e}")
        
        self.close()
    
    def _reset_settings(self):
        """Reset settings to defaults."""
        if self.active_tab in self.settings:
            for setting_name, setting_data in self.settings[self.active_tab].items():
                if setting_name in self.sliders:
                    default_value = setting_data['default']
                    self.sliders[setting_name].set_value(default_value)
                    self.config.set(setting_name, default_value)
                elif setting_name in self.dropdowns:
                    default_value = setting_data['default']
                    self.dropdowns[setting_name].selected_value = default_value
                    self.config.set(setting_name, default_value)
                elif setting_name in self.toggles:
                    default_value = setting_data['default']
                    self.toggles[setting_name].value = default_value
                    self.config.set(setting_name, default_value)
    
    def _draw_9slice_panel(self, surface: pygame.Surface, rect: pygame.Rect):
        """Draw a 9-slice panel using the panel_9slice image."""
        if not self.panel_9slice:
            # Fallback to simple rectangle with better transparency
            panel_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            pygame.draw.rect(panel_surface, (*Colors.BG_DARK, 230), panel_surface.get_rect(), border_radius=12)
            pygame.draw.rect(panel_surface, (*Colors.PRIMARY, 255), panel_surface.get_rect(), 3, border_radius=12)
            surface.blit(panel_surface, rect)
            return
        
        # Get panel dimensions
        panel_w, panel_h = rect.width, rect.height
        
        # Get the 9-slice image dimensions
        img_w, img_h = self.panel_9slice.get_size()
        
        # Define slice sizes (assuming the image is divided into 3x3 grid)
        slice_w = img_w // 3
        slice_h = img_h // 3
        
        # Create a surface for the panel with transparency
        panel_surface = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        
        # Fill with semi-transparent background first
        pygame.draw.rect(panel_surface, (*Colors.BG_DARK, 200), panel_surface.get_rect(), border_radius=12)
        
        # Draw 9 slices
        # Top-left corner
        panel_surface.blit(self.panel_9slice, (0, 0), (0, 0, slice_w, slice_h))
        
        # Top edge
        for x in range(slice_w, panel_w - slice_w, slice_w):
            panel_surface.blit(self.panel_9slice, (x, 0), (slice_w, 0, slice_w, slice_h))
        
        # Top-right corner
        panel_surface.blit(self.panel_9slice, (panel_w - slice_w, 0), (slice_w * 2, 0, slice_w, slice_h))
        
        # Left edge
        for y in range(slice_h, panel_h - slice_h, slice_h):
            panel_surface.blit(self.panel_9slice, (0, y), (0, slice_h, slice_w, slice_h))
        
        # Center - fill the middle area
        center_rect = pygame.Rect(slice_w, slice_h, panel_w - 2*slice_w, panel_h - 2*slice_h)
        if center_rect.width > 0 and center_rect.height > 0:
            # Tile the center slice
            for x in range(slice_w, panel_w - slice_w, slice_w):
                for y in range(slice_h, panel_h - slice_h, slice_h):
                    panel_surface.blit(self.panel_9slice, (x, y), (slice_w, slice_h, slice_w, slice_h))
        
        # Right edge
        for y in range(slice_h, panel_h - slice_h, slice_h):
            panel_surface.blit(self.panel_9slice, (panel_w - slice_w, y), (slice_w * 2, slice_h, slice_w, slice_h))
        
        # Bottom-left corner
        panel_surface.blit(self.panel_9slice, (0, panel_h - slice_h), (0, slice_h * 2, slice_w, slice_h))
        
        # Bottom edge
        for x in range(slice_w, panel_w - slice_w, slice_w):
            panel_surface.blit(self.panel_9slice, (x, panel_h - slice_h), (slice_w, slice_h * 2, slice_w, slice_h))
        
        # Bottom-right corner
        panel_surface.blit(self.panel_9slice, (panel_w - slice_w, panel_h - slice_h), (slice_w * 2, slice_h * 2, slice_w, slice_h))
        
        # Draw the panel surface
        surface.blit(panel_surface, rect)
    
    def draw(self, surface: pygame.Surface):
        """Draw the settings UI."""
        if not self.visible:
            return
        
        # Draw background overlay
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, self.background_alpha))
        surface.blit(overlay, (0, 0))
        
        # Calculate panel dimensions - use 70% of screen width
        panel_width = int(self.width * 0.7)
        panel_height = min(600, self.height - 120)
        panel_x = (self.width - panel_width) // 2
        panel_y = (self.height - panel_height) // 2
        
        # Scale panel based on animation
        scaled_width = int(panel_width * self.panel_scale)
        scaled_height = int(panel_height * self.panel_scale)
        scaled_x = panel_x + (panel_width - scaled_width) // 2
        scaled_y = panel_y + (panel_height - scaled_height) // 2
        
        # Draw main panel using 9-slice
        panel_rect = pygame.Rect(scaled_x, scaled_y, scaled_width, scaled_height)
        self._draw_9slice_panel(surface, panel_rect)
        
        # Draw title
        title_text = f"Settings - {self.active_tab}"
        title_surface = self.font_title.render(title_text, True, Colors.TEXT_PRIMARY)
        title_rect = title_surface.get_rect(midtop=(panel_x + panel_width // 2, scaled_y + 20))
        surface.blit(title_surface, title_rect)
        
        # Draw tab buttons
        for button in self.buttons.values():
            if button.text in self.tabs:
                button.draw(surface, self.font_body)
        
        # Draw sliders, dropdowns and labels
        content_x = panel_x + 50  # Increased margin for better spacing
        content_y = panel_y + 120  # Increased spacing from title
        spacing = 70  # Increased spacing between items
        
        for i, (setting_name, slider) in enumerate(self.sliders.items()):
            y = content_y + i * spacing
            
            # Draw setting label
            label_text = setting_name.replace('_', ' ').title()
            label_surface = self.font_body.render(label_text, True, Colors.TEXT_PRIMARY)
            surface.blit(label_surface, (content_x, y - 30))
            
            # Draw value
            value_text = f"{slider.value:.2f}" if isinstance(slider.value, float) else str(int(slider.value))
            value_surface = self.font_small.render(value_text, True, Colors.TEXT_SECONDARY)
            value_rect = value_surface.get_rect(midright=(content_x + slider.width, y + slider.height // 2))
            surface.blit(value_surface, value_rect)
            
            # Draw slider
            slider.draw(surface)
        
        for i, (setting_name, dropdown) in enumerate(self.dropdowns.items()):
            y = content_y + (len(self.sliders) + i) * spacing
            
            # Draw setting label
            label_text = setting_name.replace('_', ' ').title()
            label_surface = self.font_body.render(label_text, True, Colors.TEXT_PRIMARY)
            surface.blit(label_surface, (content_x, y - 30))
            
            # Draw dropdown
            dropdown.draw(surface, self.font_body)
        
        for i, (setting_name, toggle) in enumerate(self.toggles.items()):
            y = content_y + (len(self.sliders) + len(self.dropdowns) + i) * spacing
            
            # Update toggle position
            toggle.y = y
            toggle.x = content_x + 200  # Position toggle to the right of label
            
            # Draw toggle label
            label_text = toggle.label
            label_surface = self.font_body.render(label_text, True, Colors.TEXT_PRIMARY)
            surface.blit(label_surface, (content_x, y - 30))
            
            # Draw toggle
            toggle.draw(surface)
        
        # Draw action buttons
        for button in self.buttons.values():
            if button.text not in self.tabs:
                button.draw(surface, self.font_body)
        
        # Draw help text - moved to bottom of panel
        help_text = "Use sliders, dropdowns, and toggles to adjust settings. Changes are applied immediately."
        help_surface = self.font_small.render(help_text, True, Colors.TEXT_SECONDARY)
        help_rect = help_surface.get_rect(midbottom=(panel_x + panel_width // 2, panel_y + panel_height - 25))
        surface.blit(help_surface, help_rect)
