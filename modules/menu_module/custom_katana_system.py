import pygame
import math
import random
import os
from dataclasses import dataclass
from typing import List, Tuple, Optional
import os

@dataclass
class KatanaButton:
    """Custom katana button with asset integration"""
    text: str
    action: str
    x: int
    y: int
    width: int
    height: int
    hover: bool = False
    click_animation: float = 0.0
    glow_intensity: float = 0.0

class CustomKatanaSystem:
    """Advanced katana menu system with custom assets and perfect math"""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.center_x = width // 2
        self.center_y = height // 2
        
        # Mathematical constants for perfect placement
        self.GOLDEN_RATIO = 1.618
        self.GRID_SIZE = 64
        
        # Animation variables
        self.time = 0.0
        self.breathing_animation = 0.0
        self.particle_timer = 0.0
        
        # Asset paths
        self.asset_path = "puzzleassets/menus/"
        
        # Load custom assets
        self._load_custom_assets()
        
        # Calculate perfect layout
        self._calculate_perfect_layout()
        
        # Create buttons
        self._create_katana_buttons()
        
        # Initialize effects
        self.particles = []
        self._generate_initial_effects()
        
        print(f"🗡️ Custom Katana System initialized for {width}x{height}")
        print(f"📐 Perfect layout calculated with Golden Ratio")
        print(f"🎨 Loaded {len(self.assets)} custom assets")
    
    def _load_custom_assets(self):
        """Load all custom assets with error handling"""
        self.assets = {}
        asset_files = {
            'background': ('Official_mainmenu_background.png', 'puzzleassets/menus/'),
            'panel_pattern': ('japanesebkg.png', 'puzzleassets/menus/newmenu/'),
            'title_wordmark': ('title_wordmark.png', 'puzzleassets/menus/'),
            'glow': ('glowingball.png', 'puzzleassets/menus/newmenu/'),
            'particles': ('particles.png', 'puzzleassets/menus/newmenu/'),
            'star_particles': ('starparticles.png', 'puzzleassets/menus/newmenu/'),
            'katana_button': ('katanabutton.png', 'puzzleassets/menus/newmenu/'),
            'hilt': ('hilttxt.png', 'puzzleassets/menus/newmenu/'),
            'shine': ('katanashine.png', 'puzzleassets/menus/newmenu/')
        }
        
        for key, (filename, path) in asset_files.items():
            try:
                full_path = os.path.join(path, filename)
                if os.path.exists(full_path):
                    self.assets[key] = pygame.image.load(full_path).convert_alpha()
                    print(f"✅ Loaded {key}: {filename}")
                else:
                    print(f"⚠️ Asset not found: {full_path}")
                    self.assets[key] = self._create_fallback_texture(key)
            except Exception as e:
                print(f"❌ Error loading {key}: {e}")
                self.assets[key] = self._create_fallback_texture(key)
    
    def _create_fallback_texture(self, asset_type: str) -> pygame.Surface:
        """Create fallback textures if assets fail to load"""
        size = 256 if asset_type in ['background'] else 128
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        if asset_type == 'background':
            # Dark blue gradient
            for y in range(size):
                alpha = int(255 * (1 - y / size))
                color = (0, 0, 51, alpha)
                pygame.draw.line(surface, color, (0, y), (size, y))
        elif asset_type == 'lightning':
            # Blue lightning effect
            points = [(0, 0), (64, 32), (32, 64), (96, 96), (64, 128)]
            pygame.draw.lines(surface, (0, 191, 255), False, points, 3)
        elif asset_type == 'glow':
            # Radial glow
            pygame.draw.circle(surface, (0, 255, 255), (64, 64), 60)
        else:
            # Generic texture
            surface.fill((100, 100, 100))
        
        return surface
    
    def _calculate_perfect_layout(self):
        """Calculate perfect button layout using Golden Ratio"""
        # Screen proportions
        screen_ratio = self.width / self.height
        
        # Calculate total space needed for 6 buttons
        total_buttons = 6
        available_height = self.height * 0.6  # Use 60% of screen height for buttons
        
        # Button sizing to fit all buttons
        button_height = int(available_height / (total_buttons + 1))  # +1 for spacing
        button_width = int(button_height * self.GOLDEN_RATIO)
        
        # Ensure button width doesn't exceed screen width
        max_button_width = int(self.width * 0.4)  # Max 40% of screen width
        if button_width > max_button_width:
            button_width = max_button_width
            button_height = int(button_width / self.GOLDEN_RATIO)
        
        # Spacing
        button_spacing = int(button_height * 0.3)  # 30% of button height for spacing
        
        # Starting position (centered)
        total_button_area = (button_height * total_buttons) + (button_spacing * (total_buttons - 1))
        start_y = self.center_y - (total_button_area // 2)
        
        self.layout = {
            'button_width': button_width,
            'button_height': button_height,
            'button_spacing': button_spacing,
            'start_y': start_y,
            'grid_size': self.GRID_SIZE
        }
        
        print(f"📐 Layout: {button_width}x{button_height} buttons, spacing: {button_spacing}")
        print(f"📐 Total button area: {total_button_area}px, starting at Y: {start_y}")
    
    def _create_katana_buttons(self):
        """Create katana-themed buttons with perfect positioning"""
        button_configs = [
            ("⚔️ QUICKPLAY", "quickplay"),
            ("🗡️ STORY MODE", "story"),
            ("⚙️ SETTINGS", "settings"),
            ("🎮 TEST MODE", "testmode"),
            ("🎒 INVENTORY", "inventory"),
            ("❌ EXIT", "exit")
        ]
        
        self.buttons = []
        y_pos = self.layout['start_y']
        
        for text, action in button_configs:
            button = KatanaButton(
                text=text,
                action=action,
                x=self.center_x - self.layout['button_width'] // 2,
                y=int(y_pos),
                width=self.layout['button_width'],
                height=self.layout['button_height']
            )
            self.buttons.append(button)
            y_pos += self.layout['button_height'] + self.layout['button_spacing']
        
        print(f"🗡️ Created {len(self.buttons)} katana buttons")
    
    def _generate_initial_effects(self):
        """Generate initial particle effects"""
        # Particles
        for _ in range(20):
            self._generate_particles()
    

    
    def _generate_particles(self):
        """Generate atmospheric particles"""
        self.particles.append({
            'x': random.randint(0, self.width),
            'y': random.randint(0, self.height),
            'vx': random.uniform(-20, 20),
            'vy': random.uniform(-30, -10),
            'life': random.uniform(2.0, 5.0),
            'size': random.uniform(2, 8),
            'alpha': random.randint(100, 255)
        })
    
    def update(self, dt: float):
        """Update animations and effects"""
        self.time += dt
        self.breathing_animation = math.sin(self.time * 2) * 0.5 + 0.5
        self.particle_timer += dt
        
        # Update buttons
        for button in self.buttons:
            if button.hover:
                button.glow_intensity = min(1.0, button.glow_intensity + dt * 3)
            else:
                button.glow_intensity = max(0.0, button.glow_intensity - dt * 2)
            
            if button.click_animation > 0:
                button.click_animation -= dt * 5
        

        
        # Update particles
        for particle in self.particles[:]:
            particle['x'] += particle['vx'] * dt
            particle['y'] += particle['vy'] * dt
            particle['life'] -= dt
            particle['alpha'] = int(255 * (particle['life'] / 5.0))
            
            if particle['life'] <= 0 or particle['y'] < -50:
                self.particles.remove(particle)
        
        # Generate new particles
        if self.particle_timer > 0.5:
            self._generate_particles()
            self.particle_timer = 0
    
    def handle_event(self, event) -> Optional[str]:
        """Handle pygame events and return button actions"""
        if event.type == pygame.MOUSEMOTION:
            mouse_x, mouse_y = event.pos
            for button in self.buttons:
                button.hover = (
                    button.x <= mouse_x <= button.x + button.width and
                    button.y <= mouse_y <= button.y + button.height
                )
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_x, mouse_y = event.pos
                for button in self.buttons:
                    if (
                        button.x <= mouse_x <= button.x + button.width and
                        button.y <= mouse_y <= button.y + button.height
                    ):
                        button.click_animation = 1.0
                        return button.action
        
        return None
    
    def draw(self, screen: pygame.Surface):
        """Draw the complete katana menu"""
        # Draw background
        self._draw_background(screen)
        
        # Draw menu panel container (Japanese pattern) behind buttons
        self._draw_menu_panel(screen)
        
        # Draw effects
        self._draw_particles(screen)
        
        # Draw buttons
        for button in self.buttons:
            self._draw_katana_button(screen, button)
        
        # Draw title
        self._draw_title(screen)
        
        # Draw UI info
        self._draw_ui_info(screen)
    
    def _draw_background(self, screen: pygame.Surface):
        """Draw the official main menu background"""
        try:
            # Try to load the official main menu background
            bg_path = os.path.join("puzzleassets", "menus", "Official_mainmenu_background.png")
            if os.path.exists(bg_path):
                bg_surface = pygame.image.load(bg_path).convert_alpha()
                # Scale background to fit screen
                scaled_bg = pygame.transform.scale(bg_surface, (self.width, self.height))
                screen.blit(scaled_bg, (0, 0))
            else:
                # Fallback to dark background
                screen.fill((10, 15, 25))
        except Exception as e:
            print(f"⚠️ Failed to load official background: {e}")
            # Fallback to dark background
            screen.fill((10, 15, 25))
    
    def _draw_menu_panel(self, screen: pygame.Surface):
        """Draw a centered panel using the Japanese background as texture."""
        panel_margin_x = int(self.width * 0.28)  # leave background visible at sides
        panel_margin_y = int(self.height * 0.18)
        panel_rect = pygame.Rect(
            panel_margin_x,
            panel_margin_y,
            self.width - panel_margin_x * 2,
            self.height - panel_margin_y * 2,
        )
        
        # Shadow
        shadow = pygame.Surface((panel_rect.width + 20, panel_rect.height + 20), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, 120), shadow.get_rect(), border_radius=18)
        screen.blit(shadow, (panel_rect.x - 10, panel_rect.y - 10))
        
        # Base translucent panel
        panel_surface = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, (15, 25, 35, 190), panel_surface.get_rect(), border_radius=14)
        
        # Japanese pattern texture clipped inside panel
        if 'panel_pattern' in self.assets:
            pattern = pygame.transform.scale(self.assets['panel_pattern'], (panel_rect.width, panel_rect.height))
            pattern.set_alpha(140)
            panel_surface.blit(pattern, (0, 0))
        
        # Subtle border
        pygame.draw.rect(panel_surface, (0, 255, 255, 80), panel_surface.get_rect(), width=2, border_radius=14)
        
        screen.blit(panel_surface, panel_rect.topleft)


    
    def _draw_particles(self, screen: pygame.Surface):
        """Draw atmospheric particles using custom particle assets"""
        # Draw regular particles
        if 'particles' in self.assets:
            particle_surface = self.assets['particles']
            for particle in self.particles:
                # Scale particle based on size (make them more prominent)
                scaled_size = int(particle['size'] * 4)  # Increased size
                scaled_particle = pygame.transform.scale(particle_surface, (scaled_size, scaled_size))
                scaled_particle.set_alpha(particle['alpha'])
                screen.blit(scaled_particle, (particle['x'] - scaled_size//2, particle['y'] - scaled_size//2))
        
        # Draw star particles (additional effect)
        if 'star_particles' in self.assets:
            star_surface = self.assets['star_particles']
            for i, particle in enumerate(self.particles):
                if i % 3 == 0:  # Every 3rd particle is a star
                    star_size = int(particle['size'] * 3)
                    scaled_star = pygame.transform.scale(star_surface, (star_size, star_size))
                    scaled_star.set_alpha(particle['alpha'] // 2)  # Half alpha for stars
                    screen.blit(scaled_star, (particle['x'] - star_size//2, particle['y'] - star_size//2))
        
        # Fallback if no assets
        if 'particles' not in self.assets and 'star_particles' not in self.assets:
            for particle in self.particles:
                color = (0, 255, 255, particle['alpha'])
                pygame.draw.circle(screen, color, (int(particle['x']), int(particle['y'])), int(particle['size']))
    
    def _draw_katana_button(self, screen: pygame.Surface, button: KatanaButton):
        """Draw a katana-themed button with custom assets"""
        # Button background
        if 'katana_button' in self.assets:
            button_surface = pygame.transform.scale(self.assets['katana_button'], (button.width, button.height))
            screen.blit(button_surface, (button.x, button.y))
        else:
            # Fallback button
            color = (50, 50, 100) if button.hover else (30, 30, 70)
            pygame.draw.rect(screen, color, (button.x, button.y, button.width, button.height))
            pygame.draw.rect(screen, (100, 100, 200), (button.x, button.y, button.width, button.height), 2)
        
        # Glow effect (make it more prominent)
        if button.glow_intensity > 0 and 'glow' in self.assets:
            glow_size = int(button.width * 2.0 * button.glow_intensity)  # Increased size
            glow_surface = pygame.transform.scale(self.assets['glow'], (glow_size, glow_size))
            glow_surface.set_alpha(int(150 * button.glow_intensity))  # Increased alpha
            glow_x = button.x + button.width//2 - glow_size//2
            glow_y = button.y + button.height//2 - glow_size//2
            screen.blit(glow_surface, (glow_x, glow_y))
        
        # Click animation
        if button.click_animation > 0:
            flash_color = (255, 255, 255, int(100 * button.click_animation))
            flash_surface = pygame.Surface((button.width, button.height), pygame.SRCALPHA)
            flash_surface.fill(flash_color)
            screen.blit(flash_surface, (button.x, button.y))
        
        # Button text
        font_size = max(16, button.height // 4)
        try:
            font = pygame.font.Font(None, font_size)
        except:
            font = pygame.font.SysFont('arial', font_size)
        
        text_color = (255, 255, 255) if button.hover else (200, 200, 200)
        text_surface = font.render(button.text, True, text_color)
        text_rect = text_surface.get_rect(center=(button.x + button.width//2, button.y + button.height//2))
        screen.blit(text_surface, text_rect)
        
        # Hilt decoration
        if button.hover and 'hilt' in self.assets:
            hilt_size = button.height // 3
            hilt_surface = pygame.transform.scale(self.assets['hilt'], (hilt_size, hilt_size))
            hilt_x = button.x + button.width - hilt_size - 10
            hilt_y = button.y + button.height//2 - hilt_size//2
            screen.blit(hilt_surface, (hilt_x, hilt_y))
    
    def _draw_title(self, screen: pygame.Surface):
        """Draw the game title using the wordmark image"""
        if 'title_wordmark' in self.assets:
            # Scale the title wordmark to fit nicely
            title_width = int(self.width * 0.4)  # 40% of screen width
            title_height = int(title_width * 0.3)  # Maintain aspect ratio
            scaled_title = pygame.transform.scale(self.assets['title_wordmark'], (title_width, title_height))
            
            # Position at top center
            title_rect = scaled_title.get_rect(center=(self.center_x, 120))
            screen.blit(scaled_title, title_rect)
        else:
            # Fallback to text if image not found
            try:
                title_font = pygame.font.Font(None, 72)
                title_surface = title_font.render("BLADE FIGHTERS", True, (255, 255, 255))
                title_rect = title_surface.get_rect(center=(self.center_x, 120))
                screen.blit(title_surface, title_rect)
            except:
                pass
    
    def _draw_ui_info(self, screen: pygame.Surface):
        """Draw UI information and debug info"""
        info_lines = [
            f"Resolution: {self.width}x{self.height}",
            f"Golden Ratio: {self.GOLDEN_RATIO:.3f}",
            f"Grid Size: {self.GRID_SIZE}",
            f"Particles: {len(self.particles)}",
            f"Assets: {len(self.assets)} loaded"
        ]
        
        try:
            info_font = pygame.font.Font(None, 24)
        except:
            info_font = pygame.font.SysFont('arial', 24)
        
        y_offset = self.height - 150
        for i, line in enumerate(info_lines):
            text_surface = info_font.render(line, True, (150, 150, 150))
            screen.blit(text_surface, (20, y_offset + i * 25))
