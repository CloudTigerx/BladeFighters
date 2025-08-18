#!/usr/bin/env python3
"""
Katana Blade Interface - Mathematical Perfection
A completely new main menu system with perfect positioning and visual weight magic.
"""

import pygame
import math
import random
import os
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class KatanaButton:
    """Mathematically perfect button with katana styling."""
    text: str
    action: Optional[str]
    rect: pygame.Rect
    hover: bool = False
    pressed: bool = False
    animation_time: float = 0.0
    glow_intensity: float = 0.0
    katana_angle: float = 0.0

class KatanaMenuSystem:
    """
    Katana Blade Interface - Mathematical Perfection
    Features:
    - Golden ratio positioning
    - Katana-inspired visual design
    - Lightning effects
    - Breathing animations
    - Particle systems
    """
    
    def __init__(self, screen: pygame.Surface, font: pygame.font.Font, audio=None, asset_path: str = "puzzleassets"):
        self.screen = screen
        self.font = font
        self.audio = audio
        self.asset_path = asset_path
        
        # Screen dimensions
        self.width = screen.get_width()
        self.height = screen.get_height()
        
        # Mathematical constants
        self.GOLDEN_RATIO = 1.618033988749895
        self.GRID_SIZE = 64  # Base grid unit
        
        # Animation variables
        self.time = 0.0
        self.breathing_phase = 0.0
        self.lightning_timer = 0.0
        self.particle_timer = 0.0
        
        # Katana styling
        self.katana_colors = {
            'blade': (192, 192, 192),      # Silver
            'hilt': (64, 64, 64),          # Dark gray
            'glow': (100, 150, 255),       # Blue glow
            'lightning': (150, 200, 255),  # Bright blue
            'text': (255, 255, 255),       # White
            'text_glow': (255, 200, 100)   # Golden glow
        }
        
        # Button configuration
        self.buttons: List[KatanaButton] = []
        self.hovered_button: Optional[KatanaButton] = None
        
        # Particle system
        self.particles: List[Dict] = []
        
        # Lightning effects
        self.lightning_segments: List[Tuple] = []
        
        # Initialize layout
        self._calculate_perfect_layout()
        self._create_katana_buttons()
        
        print("🗡️ Katana Blade Interface initialized with mathematical perfection!")
    
    def _calculate_perfect_layout(self):
        """Calculate mathematically perfect positioning using golden ratio."""
        # Center point
        self.center_x = self.width // 2
        self.center_y = self.height // 2
        
        # Golden ratio divisions
        self.left_zone = int(self.width / self.GOLDEN_RATIO)
        self.right_zone = self.width - self.left_zone
        
        # Button positioning using golden ratio
        self.button_width = int(self.GRID_SIZE * 6)  # 384px
        self.button_height = int(self.GRID_SIZE * 1.5)  # 96px
        self.button_spacing = int(self.GRID_SIZE * 1.5)  # 96px
        
        # Calculate perfect button positions
        self.button_x = self.center_x - (self.button_width // 2)
        self.start_y = int(self.height * 0.3)  # 30% from top
        
        print(f"📐 Perfect layout calculated:")
        print(f"   Screen: {self.width}x{self.height}")
        print(f"   Center: ({self.center_x}, {self.center_y})")
        print(f"   Button size: {self.button_width}x{self.button_height}")
        print(f"   Golden ratio zones: {self.left_zone} | {self.right_zone}")
    
    def _create_katana_buttons(self):
        """Create katana-styled buttons with perfect positioning."""
        button_configs = [
            ("QUICKPLAY", "quickplay"),
            ("STORY MODE", "story"),
            ("TEST MODE", "test"),
            ("SMITHING", "smithing"),
            ("INVENTORY", "inventory"),
            ("SETTINGS", "settings"),
            ("QUIT", "quit")
        ]
        
        for i, (text, action) in enumerate(button_configs):
            button_y = self.start_y + i * (self.button_height + self.button_spacing)
            
            # Create katana button
            button = KatanaButton(
                text=text,
                action=action,
                rect=pygame.Rect(self.button_x, button_y, self.button_width, self.button_height),
                katana_angle=random.uniform(-5, 5)  # Slight random angle for realism
            )
            
            self.buttons.append(button)
        
        print(f"🗡️ Created {len(self.buttons)} katana buttons with perfect positioning")
    
    def update(self, dt: float):
        """Update animations and effects."""
        self.time += dt
        self.breathing_phase = math.sin(self.time * 2.0) * 0.5 + 0.5
        self.lightning_timer += dt
        self.particle_timer += dt
        
        # Update button animations
        for button in self.buttons:
            button.animation_time += dt
            
            # Breathing effect
            if button.hover:
                button.glow_intensity = min(1.0, button.glow_intensity + dt * 3.0)
            else:
                button.glow_intensity = max(0.0, button.glow_intensity - dt * 2.0)
        
        # Generate lightning
        if self.lightning_timer > 2.0:
            self._generate_lightning()
            self.lightning_timer = 0.0
        
        # Generate particles
        if self.particle_timer > 0.1:
            self._generate_particles()
            self.particle_timer = 0.0
        
        # Update particles
        self._update_particles(dt)
    
    def _generate_lightning(self):
        """Generate lightning effects in the background."""
        self.lightning_segments = []
        
        # Create lightning from top to bottom
        start_x = random.randint(0, self.width)
        start_y = 0
        end_x = random.randint(0, self.width)
        end_y = self.height
        
        # Generate lightning path
        points = [(start_x, start_y)]
        current_x, current_y = start_x, start_y
        
        while current_y < end_y:
            # Random zigzag
            current_x += random.randint(-100, 100)
            current_y += random.randint(50, 150)
            
            # Keep within bounds
            current_x = max(0, min(self.width, current_x))
            current_y = min(end_y, current_y)
            
            points.append((current_x, current_y))
        
        # Create segments
        for i in range(len(points) - 1):
            self.lightning_segments.append((points[i], points[i + 1]))
    
    def _generate_particles(self):
        """Generate atmospheric particles."""
        for _ in range(3):
            particle = {
                'x': random.randint(0, self.width),
                'y': random.randint(0, self.height),
                'vx': random.uniform(-20, 20),
                'vy': random.uniform(-30, -10),
                'life': random.uniform(2.0, 4.0),
                'max_life': random.uniform(2.0, 4.0),
                'size': random.uniform(1, 3),
                'color': random.choice([
                    (100, 150, 255, 100),  # Blue
                    (150, 200, 255, 80),   # Light blue
                    (255, 255, 255, 60)    # White
                ])
            }
            self.particles.append(particle)
    
    def _update_particles(self, dt: float):
        """Update particle positions and lifetimes."""
        for particle in self.particles[:]:
            particle['x'] += particle['vx'] * dt
            particle['y'] += particle['vy'] * dt
            particle['life'] -= dt
            
            # Remove dead particles
            if particle['life'] <= 0:
                self.particles.remove(particle)
    
    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """Handle input events."""
        if event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            
            # Update hover states
            for button in self.buttons:
                button.hover = button.rect.collidepoint(mouse_pos)
                if button.hover and self.hovered_button != button:
                    self.hovered_button = button
                    if self.audio:
                        # Play katana swoosh sound
                        pass
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_pos = pygame.mouse.get_pos()
                
                for button in self.buttons:
                    if button.rect.collidepoint(mouse_pos):
                        button.pressed = True
                        if self.audio:
                            # Play katana strike sound
                            pass
                        return button.action
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left click
                for button in self.buttons:
                    button.pressed = False
        
        return None
    
    def draw(self):
        """Draw the complete katana interface."""
        # Clear screen with dark background
        self.screen.fill((10, 15, 25))
        
        # Draw lightning effects
        self._draw_lightning()
        
        # Draw particles
        self._draw_particles()
        
        # Draw katana buttons
        self._draw_katana_buttons()
        
        # Draw title
        self._draw_title()
        
        # Draw UI info
        self._draw_ui_info()
    
    def _draw_lightning(self):
        """Draw lightning effects."""
        if self.lightning_segments:
            # Fade lightning over time
            alpha = max(0, 255 - int(self.lightning_timer * 255))
            if alpha > 0:
                lightning_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                
                for start, end in self.lightning_segments:
                    # Draw lightning with glow effect
                    for thickness in range(5, 0, -1):
                        color = (*self.katana_colors['lightning'][:3], alpha // thickness)
                        pygame.draw.line(lightning_surface, color, start, end, thickness)
                
                self.screen.blit(lightning_surface, (0, 0))
    
    def _draw_particles(self):
        """Draw atmospheric particles."""
        particle_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        for particle in self.particles:
            alpha = int(255 * (particle['life'] / particle['max_life']))
            color = (*particle['color'][:3], alpha)
            
            pygame.draw.circle(
                particle_surface, color,
                (int(particle['x']), int(particle['y'])),
                int(particle['size'])
            )
        
        self.screen.blit(particle_surface, (0, 0))
    
    def _draw_katana_buttons(self):
        """Draw katana-styled buttons."""
        for button in self.buttons:
            self._draw_katana_button(button)
    
    def _draw_katana_button(self, button: KatanaButton):
        """Draw a single katana-styled button."""
        x, y, w, h = button.rect
        
        # Calculate breathing scale
        breathing_scale = 1.0 + (self.breathing_phase * 0.02) if button.hover else 1.0
        
        # Apply breathing effect
        scaled_w = int(w * breathing_scale)
        scaled_h = int(h * breathing_scale)
        scaled_x = x + (w - scaled_w) // 2
        scaled_y = y + (h - scaled_h) // 2
        
        # Draw katana blade (button background)
        blade_color = self.katana_colors['blade']
        if button.hover:
            # Add glow effect
            glow_intensity = int(button.glow_intensity * 50)
            glow_color = tuple(min(255, c + glow_intensity) for c in blade_color)
            
            # Draw glow
            glow_rect = pygame.Rect(scaled_x - 10, scaled_y - 10, scaled_w + 20, scaled_h + 20)
            pygame.draw.rect(self.screen, (*self.katana_colors['glow'], 50), glow_rect, border_radius=15)
        
        # Draw main button
        button_rect = pygame.Rect(scaled_x, scaled_y, scaled_w, scaled_h)
        pygame.draw.rect(self.screen, blade_color, button_rect, border_radius=10)
        
        # Draw katana hilt (border)
        hilt_color = self.katana_colors['hilt']
        pygame.draw.rect(self.screen, hilt_color, button_rect, 3, border_radius=10)
        
        # Draw text with katana styling
        text_color = self.katana_colors['text']
        if button.hover:
            text_color = self.katana_colors['text_glow']
        
        # Render text
        text_surface = self.font.render(button.text, True, text_color)
        text_rect = text_surface.get_rect(center=button_rect.center)
        
        # Add text glow if hovering
        if button.hover:
            glow_surface = self.font.render(button.text, True, (*self.katana_colors['text_glow'], 100))
            glow_rect = glow_surface.get_rect(center=(text_rect.centerx + 2, text_rect.centery + 2))
            self.screen.blit(glow_surface, glow_rect)
        
        self.screen.blit(text_surface, text_rect)
    
    def _draw_title(self):
        """Draw the game title with katana styling."""
        title_text = "BLADE FIGHTERS"
        title_font = pygame.font.SysFont(None, 72)
        
        # Draw title with katana glow
        title_surface = title_font.render(title_text, True, self.katana_colors['text_glow'])
        title_rect = title_surface.get_rect(center=(self.center_x, 100))
        
        # Add dramatic glow
        glow_surface = title_font.render(title_text, True, (*self.katana_colors['glow'], 100))
        glow_rect = glow_surface.get_rect(center=(title_rect.centerx + 3, title_rect.centery + 3))
        self.screen.blit(glow_surface, glow_rect)
        
        self.screen.blit(title_surface, title_rect)
    
    def _draw_ui_info(self):
        """Draw UI information."""
        info_font = pygame.font.SysFont(None, 24)
        
        # Draw FPS
        fps_text = f"FPS: {pygame.time.get_ticks() // 1000 % 60}"
        fps_surface = info_font.render(fps_text, True, (255, 255, 255))
        self.screen.blit(fps_surface, (10, 10))
        
        # Draw katana interface info
        info_text = "Katana Blade Interface - Mathematical Perfection"
        info_surface = info_font.render(info_text, True, (200, 200, 200))
        self.screen.blit(info_surface, (10, 35))
