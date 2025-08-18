"""
Scaled Menu System - Enhanced menu system using the new scaling system
Provides precise positioning and sizing across all resolutions.
"""

import pygame
import sys
import os
import math
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass
import random

# 4K version - no scaling needed!
from .menu_system import MenuSystem
from ..logging_module.error_handler import (
    safe_file_operation
)
from ..logging_module.logger import get_logger

logger = get_logger(__name__)


@dataclass
class MenuButton:
    """Represents a menu button with precise positioning."""
    text: str
    rect: pygame.Rect
    action: str
    is_hovered: bool = False
    is_pressed: bool = False


class ScaledMenuSystem(MenuSystem):
    """
    Enhanced menu system using the comprehensive scaling system.
    Provides precise positioning and sizing across all resolutions.
    """
    
    def __init__(self, screen, font, audio, asset_path: str = "puzzleassets", game_mode: str = "default"):
        super().__init__(screen, font, audio, asset_path, game_mode)
        
        self.width = screen.get_width()
        self.height = screen.get_height()
        
        # 4K version - no scaling needed!
        # self.ui_scaler = None  # Not needed for fixed 4K version
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GRAY = (100, 100, 100)
        self.LIGHT_GRAY = (200, 200, 200)
        self.BLUE = (0, 100, 255)
        self.LIGHT_BLUE = (100, 150, 255)
        self.BORDER_COLOR = (100, 150, 255)
        self.HOVER_BORDER_COLOR = (150, 200, 255)
        
        # Character breathing animation variables
        self.breathing_time = 0
        self.breathing_speed = 0.003  # Speed of breathing cycle
        self.breathing_scale_min = 1.0
        self.breathing_scale_max = 1.02  # Very subtle scale change
        self.breathing_color_intensity = 0.05  # Very subtle color change
        
        # Katana particle system variables
        self.particles = []
        self.particle_time = 0
        self.particle_spawn_rate = 0.1  # Particles per frame
        self.max_particles = 20
        self.particle_lifetime = 3.0  # seconds
        self.particle_speed = 0.5
        self.particle_size_range = (2, 6)
        self.particle_color = (255, 200, 100, 180)  # Golden-orange with alpha
        
        # Load scaled assets
        self._load_scaled_assets()
        
        # Menu state
        self.current_menu = "main"
        self.buttons: Dict[str, List[MenuButton]] = {}
        self.hovered_button = None
        
        # Create menus
        self._create_main_menu()
        self._create_story_menu()
        # Note: Settings and inventory menus are handled by the base class
        
        logger.info("ScaledMenuSystem initialized with UI scaling support")
    
    def _update_particles(self, dt):
        """Update particle system."""
        self.particle_time += dt
        
        # Spawn new particles
        if len(self.particles) < self.max_particles and random.random() < self.particle_spawn_rate:
            self._spawn_particle()
        
        # Update existing particles
        for particle in self.particles[:]:
            particle['life'] -= dt
            particle['x'] += particle['vx'] * dt
            particle['y'] += particle['vy'] * dt
            particle['alpha'] = int(255 * (particle['life'] / self.particle_lifetime))
            
            # Remove dead particles
            if particle['life'] <= 0:
                self.particles.remove(particle)
    
    def _spawn_particle(self):
        """Spawn a new katana particle."""
        # Choose left or right side randomly
        side = random.choice(['left', 'right'])
        
        if side == 'left':
            # Left character area (roughly 1/4 of screen width)
            x = random.uniform(0, self.width * 0.25)
        else:
            # Right character area (roughly 3/4 to full screen width)
            x = random.uniform(self.width * 0.75, self.width)
        
        # Vertical position around character height
        y = random.uniform(self.height * 0.2, self.height * 0.8)
        
        # Particle velocity (gentle upward drift)
        vx = random.uniform(-10, 10)
        vy = random.uniform(-20, -5)
        
        # Particle size
        size = random.uniform(*self.particle_size_range)
        
        particle = {
            'x': x,
            'y': y,
            'vx': vx,
            'vy': vy,
            'size': size,
            'life': self.particle_lifetime,
            'alpha': 255
        }
        
        self.particles.append(particle)
    
    def _draw_particles(self):
        """Draw all katana particles."""
        for particle in self.particles:
            # Create particle surface with alpha
            particle_surface = pygame.Surface((particle['size'] * 2, particle['size'] * 2), pygame.SRCALPHA)
            
            # Draw particle as a glowing dot
            color = (*self.particle_color[:3], particle['alpha'])
            pygame.draw.circle(particle_surface, color, 
                             (particle['size'], particle['size']), particle['size'])
            
            # Add glow effect
            glow_color = (*self.particle_color[:3], particle['alpha'] // 3)
            pygame.draw.circle(particle_surface, glow_color, 
                             (particle['size'], particle['size']), particle['size'] * 1.5)
            
            # Draw particle
            self.screen.blit(particle_surface, 
                           (particle['x'] - particle['size'], particle['y'] - particle['size']))
    
    def get_scaled_font(self, font_type: str = "body_font") -> pygame.font.Font:
        """Get a fixed font for 4K resolution."""
        # Fixed font sizes for 4K
        font_sizes = {
            "title_font": 72,
            "body_font": 36,
            "small_font": 24
        }
        size = font_sizes.get(font_type, 36)
        return pygame.font.SysFont(None, size)
    
    def draw_button(self, button: Dict[str, Any]) -> Dict[str, Any]:
        """Override button drawing to use scaled fonts and proper text positioning."""
        x, y, width, height = button["rect"]
        
        # Create button surface
        button_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Try to use scaled button images if available
        button_image = None
        if button["hover"] and self.button_hover:
            button_image = self.button_hover
        elif self.button_normal:
            button_image = self.button_normal
        
        if button_image:
            # 4K version - no scaling needed!
            button_surface.blit(button_image, (0, 0))
            
            # Add hover overlay if needed
            if button["hover"]:
                hover_overlay = pygame.Surface((width, height), pygame.SRCALPHA)
                hover_overlay.fill((255, 255, 255, 30))
                button_surface.blit(hover_overlay, (0, 0))
        else:
            # Fallback to colored rectangle if no images available
            base_color = self.LIGHT_BLUE if button["hover"] else self.BLUE
            pygame.draw.rect(button_surface, base_color, (0, 0, width, height), border_radius=10)
            
            # Draw border
            border_color = self.HOVER_BORDER_COLOR if button["hover"] else self.BORDER_COLOR
            pygame.draw.rect(button_surface, border_color, (0, 0, width, height), 2, border_radius=10)
        
        # Draw button surface
        self.screen.blit(button_surface, (x, y))
        
        # Draw text with scaled font
        text = button["text"]
        scaled_font = self.get_scaled_font("body_font")
        
        # Calculate text position (center the text)
        text_surface = scaled_font.render(text, True, self.WHITE)
        text_rect = text_surface.get_rect()
        text_rect.center = (x + width // 2, y + height // 2)
        
        # Draw text
        self.screen.blit(text_surface, text_rect)
        
        return button
    
    def _load_scaled_assets(self):
        """Load and scale all menu assets."""
        # Load background images using base class methods
        self.main_background = self.load_background("menus/Official_mainmenu_background.png")
        self.story_background = self.load_background("storybackground.png")
        
        # Load menu-specific assets
        self.title_wordmark = self._load_menu_asset("title_wordmark.png")
        self.bg_noise_tile = self._load_menu_asset("bg_noise_tile.png")
        
        # Load button assets
        self.button_normal = self._load_menu_asset("button_normal.png")
        self.button_hover = self._load_menu_asset("button_hover.png")
        self.button_pressed = self._load_menu_asset("button_pressed.png")
        
        # For now, use the base class button loading
        # The scaling will be handled by the UI scaler during rendering
    
    @safe_file_operation("load menu asset", None, "WARNING")
    def _load_menu_asset(self, filename: str) -> Optional[pygame.Surface]:
        """Load a menu asset from the menus directory."""
        try:
            menus_path = os.path.join(self.asset_path, "menus")
            full_path = os.path.join(menus_path, filename)
            if os.path.exists(full_path):
                return pygame.image.load(full_path).convert_alpha()
        except Exception as e:
            logger.warning(f"Failed to load menu asset {filename}: {str(e)}")
        return None
    
    def _get_button_size(self) -> Tuple[int, int]:
        """Get the native button size for 4K resolution."""
        # Native button size for 4K version - no scaling needed!
        return (600, 180)
    
    def _create_main_menu(self):
        """Create the main menu for 4K resolution."""
        # Fixed button size for 4K version
        button_width, button_height = self._get_button_size()
        
        # Create button layout
        buttons_data = [
            ("Quickplay", "quickplay"),
            ("Story Mode", "story"),
            ("Test Mode", "test"),
            ("Smithing", "smithing"),
            ("Inventory", "inventory"),
            ("Settings", "settings"),
            ("Quit", "quit")
        ]
        
        # Fixed spacing for 4K version - no scaling needed!
        spacing = 35  # Reduced spacing for better fit
        total_height = len(buttons_data) * button_height + (len(buttons_data) - 1) * spacing
        
        # Fixed positioning for 4K version - better centered
        start_y = 800  # Moved up from 720 for better centering
        center_x = self.width // 2
        
        self.buttons["main"] = []
        
        for i, (text, action) in enumerate(buttons_data):
            # Calculate button position
            button_x = center_x - button_width // 2
            button_y = start_y + i * (button_height + spacing)
            
            # Create button rect using responsive scaling
            button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
            
            # Create button object
            button = MenuButton(
                text=text,
                rect=button_rect,
                action=action
            )
            
            self.buttons["main"].append(button)
    
    def _create_story_menu(self):
        """Create the story menu for 4K resolution."""
        # Fixed button size for 4K version
        button_width, button_height = self._get_button_size()
        
        # Create button layout
        buttons_data = [
            ("Saga 1: The Forge Keeper's Legacy", "saga1"),
            ("Back to Main Menu", "back_to_main")
        ]
        
        # Fixed spacing for 4K version - no scaling needed!
        spacing = 35  # Reduced spacing for better fit
        total_height = len(buttons_data) * button_height + (len(buttons_data) - 1) * spacing
        
        # Fixed positioning for 4K version - better centered
        start_y = 800  # Moved up from 720 for better centering
        center_x = self.width // 2
        
        self.buttons["story"] = []
        
        for i, (text, action) in enumerate(buttons_data):
            # Calculate button position
            button_x = center_x - button_width // 2
            button_y = start_y + i * (button_height + spacing)
            
            # Create button rect using responsive scaling
            button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
            
            # Create button object
            button = MenuButton(
                text=text,
                rect=button_rect,
                action=action
            )
            
            self.buttons["story"].append(button)
    
    def draw_main_menu(self, on_start_action=None, on_story_action=None, on_test_action=None, on_test_lab_action=None, version=None):
        """Draw the main menu with precise scaling."""
        # Clear screen
        self.screen.fill(self.BLACK)
        
        # Update breathing animation
        self.breathing_time += self.breathing_speed
        breathing_cycle = (math.sin(self.breathing_time) + 1) / 2  # 0 to 1
        
        # Calculate breathing scale and color adjustments
        current_scale = self.breathing_scale_min + (self.breathing_scale_max - self.breathing_scale_min) * breathing_cycle
        color_adjustment = int(255 * self.breathing_color_intensity * breathing_cycle)
        
        # Update particle system (assuming 60 FPS for dt)
        self._update_particles(1/60)
        
        # Draw background for 4K - no scaling needed!
        if self.main_background:
            # For 4K version, assume background is already 3840x2160
            # Just center it on screen
            bg_x = (self.width - self.main_background.get_width()) // 2
            bg_y = (self.height - self.main_background.get_height()) // 2
            
            # Draw the background directly - no scaling!
            self.screen.blit(self.main_background, (bg_x, bg_y))
        
        # Draw katana particles
        self._draw_particles()
        
        # Draw title
        self._draw_title()
        
        # Draw buttons
        self._draw_buttons("main")
        
        # Draw version info
        if version:
            self._draw_version_info(version)
        
        return self.buttons["main"]
    
    def draw_story_menu(self, on_back_action=None):
        """Draw the story menu with precise scaling."""
        # Clear screen
        self.screen.fill(self.BLACK)
        
        # Draw background for 4K - no scaling needed!
        if self.story_background:
            # For 4K version, assume background is already 3840x2160
            # Just center it on screen
            bg_x = (self.width - self.story_background.get_width()) // 2
            bg_y = (self.height - self.story_background.get_height()) // 2
            
            # Draw the background directly - no scaling!
            self.screen.blit(self.story_background, (bg_x, bg_y))
        
        # Draw title
        self._draw_title("Story Mode")
        
        # Draw buttons
        self._draw_buttons("story")
        
        return self.buttons["story"]
    
    def _draw_title(self, title_text="Blade Fighters"):
        """Draw the title for 4K resolution."""
        # Fixed positioning for 4K
        button_width, button_height = self._get_button_size()
        
        # Get button data to calculate total height
        buttons_data = [
            ("Quickplay", "quickplay"),
            ("Story Mode", "story"),
            ("Test Mode", "test"),
            ("Smithing", "smithing"),
            ("Inventory", "inventory"),
            ("Settings", "settings"),
            ("Quit", "quit")
        ]
        
        # Fixed spacing for 4K
        spacing = 35
        total_height = len(buttons_data) * button_height + (len(buttons_data) - 1) * spacing
        button_stack_start_y = 800  # Fixed start Y for 4K - better centered
        
        # Try to use title wordmark image if available
        if hasattr(self, 'title_wordmark') and self.title_wordmark:
            try:
                # Fixed title size for 4K
                tw = 480  # Fixed width for 4K
                ratio = self.title_wordmark.get_height() / max(1, self.title_wordmark.get_width())
                th = max(1, int(tw * ratio))
                
                # Center horizontally and position above button stack
                tx = (self.width - tw) // 2
                ty = button_stack_start_y - th - 30  # Fixed spacing for 4K
                self.screen.blit(self.title_wordmark, (tx, ty))
                return
            except Exception as e:
                logger.warning(f"Failed to draw title wordmark: {e}")
        
        # Fallback to text title
        title_font = pygame.font.SysFont(None, 72)  # Fixed font size for 4K
        
        # Render title text
        title_surface = title_font.render(title_text, True, self.WHITE)
        title_rect = title_surface.get_rect()
        
        # Center horizontally and position above button stack
        title_rect.centerx = self.width // 2
        title_rect.bottom = button_stack_start_y - 20  # Fixed spacing for 4K
        
        # Draw title
        self.screen.blit(title_surface, title_rect)
    
    def _draw_buttons(self, menu_type: str):
        """Draw buttons for the specified menu for 4K resolution."""
        if menu_type not in self.buttons:
            return
        
        # Fixed font for 4K
        button_font = pygame.font.SysFont(None, 36)
        
        for button in self.buttons[menu_type]:
            # Determine button appearance
            if button.is_pressed and self.button_pressed:
                button_image = self.button_pressed
            elif button.is_hovered and self.button_hover:
                button_image = self.button_hover
            elif self.button_normal:
                button_image = self.button_normal
            else:
                button_image = None
            
            # Draw button background - no scaling needed for 4K!
            if button_image:
                # Direct blit - button image is already 600x180
                self.screen.blit(button_image, button.rect)
            else:
                # Fallback: draw colored rectangle
                color = self.HOVER_BORDER_COLOR if button.is_hovered else self.BORDER_COLOR
                pygame.draw.rect(self.screen, color, button.rect, border_radius=10)
            
            # Draw button text
            text_color = self.WHITE if button.is_hovered else self.LIGHT_GRAY
            text_surface = button_font.render(button.text, True, text_color)
            text_rect = text_surface.get_rect(center=button.rect.center)
            self.screen.blit(text_surface, text_rect)
    
    def _draw_version_info(self, version: str):
        """Draw version info for 4K resolution."""
        # Fixed font for 4K
        small_font = pygame.font.SysFont(None, 24)
        
        # Render version text
        version_surface = small_font.render(f"v{version}", True, self.GRAY)
        version_rect = version_surface.get_rect()
        
        # Fixed margin for 4K
        margin = 20
        version_rect.bottomright = (self.width - margin, self.height - margin)
        
        # Draw version
        self.screen.blit(version_surface, version_rect)
    
    def process_events(self, events: List) -> Optional[str]:
        """Process events and return action if button is clicked."""
        mouse_pos = pygame.mouse.get_pos()
        
        # Reset hover states
        for menu_buttons in self.buttons.values():
            for button in menu_buttons:
                button.is_hovered = False
        
        # Check for hover
        current_buttons = self.buttons.get(self.current_menu, [])
        for button in current_buttons:
            if button.rect.collidepoint(mouse_pos):
                button.is_hovered = True
                self.hovered_button = button
                break
        else:
            self.hovered_button = None
        
        # Process click events
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    if self.hovered_button:
                        self.hovered_button.is_pressed = True
                        return self.hovered_button.action
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left click release
                    for button in current_buttons:
                        button.is_pressed = False
        
        return None
    
    def process_main_menu_events(self, events: List) -> Optional[str]:
        """Compatibility method for main menu events."""
        self.current_menu = "main"
        return self.process_events(events)
    
    def process_story_menu_events(self, events: List) -> Optional[str]:
        """Compatibility method for story menu events."""
        self.current_menu = "story"
        return self.process_events(events)
    
    def set_menu(self, menu_type: str):
        """Switch to a different menu."""
        if menu_type in self.buttons:
            self.current_menu = menu_type
    
    def update_scale(self):
        """4K version - no scaling updates needed."""
        # This method is kept for compatibility but does nothing
        print("4K version - no scaling updates needed") 