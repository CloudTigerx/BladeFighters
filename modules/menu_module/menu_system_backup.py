"""
Extracted Menu System Module
Provides menu functionality including main menu, story menu, and button creation.
Simplified to focus on core functionality: buttons, backgrounds, and basic interaction.
"""

import pygame
import sys
import math
import random
import os
from typing import List, Dict, Optional, Any, Tuple
from ..logging_module.error_handler import (
    safe_operation,
    safe_file_operation
)
from ..logging_module.logger import get_logger
# from core.scaling import true_resolution_scaler, resolution_manager  # Disabled - using simple system

# Import asset loader for proper background loading
try:
    from core.asset_loader import AssetLoader
    asset_loader_available = True
except ImportError:
    asset_loader_available = False
    print("⚠️ AssetLoader not available, falling back to direct loading")

logger = get_logger(__name__)

# Try to import the interface contract
try:
    from contracts.menu_interface_contract import MenuSystemInterface, validate_menu_interface
    interface_available = True
except ImportError:
    # Create a dummy interface if not available
    class MenuSystemInterface:
        pass
    
    def validate_menu_interface(cls):
        return cls
    
    interface_available = False
    print("⚠️  MenuSystem interface contract not found, running without validation")

# @validate_menu_interface
class MenuSystem(MenuSystemInterface):
    """Extracted MenuSystem class with interface validation."""
    
    def __init__(self, screen, font, audio, asset_path: str, game_mode: str = "default"):
        """Initialize the menu system."""
        self.screen = screen
        self.font = font
        self.audio = audio
        self.asset_path = asset_path
        self.game_mode = game_mode
        
        # Get screen dimensions
        self.width = screen.get_width()
        self.height = screen.get_height()
        
        # Track button states
        self.main_menu_buttons = []
        # Settings removed
        self.hovered_buttons = set()
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GRAY = (100, 100, 100)
        self.LIGHT_GRAY = (200, 200, 200)
        self.BLUE = (0, 100, 255)
        self.LIGHT_BLUE = (100, 150, 255)
        
        # Static border color (removed animated glow colors)
        self.BORDER_COLOR = (100, 150, 255)  # Light blue border
        self.HOVER_BORDER_COLOR = (150, 200, 255)  # Lighter blue for hover
        
        # Remove glow animation variables
        self.glow_intensity = 0.3  # Static glow intensity
        
        # Load background images using asset loader for proper game mode handling
        if asset_loader_available:
            # Use asset loader for proper background selection based on game mode
            self.asset_loader = AssetLoader(asset_path, game_mode=game_mode)
            self.main_background = self.asset_loader.get_background('puzzle_background')
            self.story_background = self.load_background("storybackground.png")
            logger.info(f"🎨 Menu system using asset loader for {game_mode} mode")
        else:
            # Fallback to direct loading
            self.main_background = self.load_background("puzzlebackground.png")
            self.story_background = self.load_background("storybackground.png")
            logger.warning("⚠️ Using fallback background loading")
        # Menus asset path and optional assets
        self.menus_path = os.path.join(self.asset_path, "menus")
        self.title_wordmark = self._load_menu_asset("title_wordmark.png")
        self.bg_noise_tile = self._load_menu_asset("bg_noise_tile.png")
        
        # Load button images
        self.button_images = {
            "Quickplay": self.load_image("banner.png"),
            "Story Mode": self.load_image("banner.png"),
            "Test Mode": self.load_image("banner.png"),
            # Settings removed
            "Quit": self.load_image("banner.png")
        }
        # Use simplified scaling system
        self.ui_scale = 1.0  # Simple fixed scale
        
        # Fallback to banner.png if any button image is missing
        self.button_normal = self.load_image("banner.png")
        self.button_hover = self.load_image("banner.png")

        # Optional skinned buttons
        self.button_skin_normal = self._load_menu_asset("button_normal.png")
        self.button_skin_hover = self._load_menu_asset("button_hover.png")
        self.button_skin_pressed = self._load_menu_asset("button_pressed.png")

        # Add visual weight styles at the top of the class, after the color definitions
        # Visual weight styles
        self.visual_weight_style = "heavy"  # Options: "heavy", "light", "modern", "minimal"
        
        # Visual weight configurations
        self.visual_styles = {
            "heavy": {
                "glow_size": 20,
                "border_width": 2,
                "text_outline_size": 3,
                "text_glow_size": 10,
                "text_color": (255, 140, 0),  # Orange
                "glow_color": (255, 100, 0, 30)
            },
            "light": {
                "glow_size": 5,
                "border_width": 1,
                "text_outline_size": 1,
                "text_glow_size": 3,
                "text_color": (255, 255, 255),  # White
                "glow_color": (255, 255, 255, 20)
            },
            "modern": {
                "glow_size": 0,
                "border_width": 1,
                "text_outline_size": 0,
                "text_glow_size": 0,
                "text_color": (235, 235, 245),  # Light gray
                "glow_color": None
            },
            "minimal": {
                "glow_size": 0,
                "border_width": 0,
                "text_outline_size": 0,
                "text_glow_size": 0,
                "text_color": (200, 200, 200),  # Gray
                "glow_color": None
            }
        }
    
    @safe_file_operation("load menu asset", None, "WARNING")
    def _load_menu_asset(self, filename: str) -> Optional[pygame.Surface]:
        """Load a menu asset with proper error handling."""
        try:
            full_path = os.path.join(self.menus_path, filename)
            if os.path.exists(full_path):
                return pygame.image.load(full_path)
        except Exception as e:
            logger.warning(f"Failed to load menu asset {filename}: {str(e)}")
        return None
        
        # Initialize story container states for story menu
        self.story_containers = []
        for i in range(10):
            self.story_containers.append({
                "rect": pygame.Rect(0, 0, 0, 0),  # Will be set properly below
                "original_size": (200, 300),  # Default size
                "hover_size": (240, 360),     # Expanded size when hovered
                "current_size": (200, 300),   # Current size (will be animated)
                "hover": False,
                "id": f"story_{i}",
                "action": None,  # Could be set to open specific story
                "transition_progress": 0.0    # For smooth size transitions
            })
        
        # Load story saga image
        self.saga_image = self.load_image("saga.png")
        
        logger.info("MenuSystem initialized with core functionality")
    
    @safe_file_operation("load background", None, "WARNING")
    def load_background(self, filename: str) -> Optional[pygame.Surface]:
        """Load a background image using the new resolution-aware system."""
        try:
            # Use simple direct loading
            background = pygame.image.load(os.path.join(self.asset_path, filename))
            if background:
                logger.info(f"✅ Loaded background: {filename}")
                return background
            else:
                # Fallback to old method
                return pygame.image.load(os.path.join(self.asset_path, filename))
        except Exception as e:
            logger.warning(f"Error loading background {filename}: {str(e)}")
            return None
            
    @safe_file_operation("load image", None, "WARNING")
    def load_image(self, filename: str) -> Optional[pygame.Surface]:
        """Load an image from the asset path."""
        try:
            full_path = os.path.join(self.asset_path, filename)
            logger.debug(f"Attempting to load image: {full_path}")
            image = pygame.image.load(full_path)
            logger.debug(f"Successfully loaded image: {filename}")
            return image
        except pygame.error as e:
            logger.warning(f"Error loading image {filename}: {str(e)}")
            return None
    
    # Add a class variable to track which buttons we've already logged
    _logged_buttons = set()

    def create_button(self, x: int, y: int, width: int, height: int, 
                     text: str, action=None, params=None) -> Dict:
        """Create a button with text and optional action."""
        # Try to load custom button image if not already loaded
        if text not in self._logged_buttons:
            self._try_load_custom_button(text)

        # Create button dictionary
        button = {
            "rect": pygame.Rect(x, y, width, height),
            "text": text,
            "action": action,
            "params": params,
            "hover": False,
            "id": f"{text}_{x}_{y}"  # Create unique ID for tracking
        }
        
        # Check if already hovering (for sound purposes)
        mouse_pos = pygame.mouse.get_pos()
        if button["rect"].collidepoint(mouse_pos):
            button["hover"] = True
            self.hovered_buttons.add(button["id"])
        
        # Create button surface
        button_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Use skinned button images if available, else fallback to banner/gradient
        skinned = False
        skin_img = None
        if pygame.mouse.get_pressed()[0] and button["hover"] and self.button_skin_pressed:
            skin_img = self.button_skin_pressed
        elif button["hover"] and self.button_skin_hover:
            skin_img = self.button_skin_hover
        elif self.button_skin_normal:
            skin_img = self.button_skin_normal
        if skin_img:
            skinned = True
            # 4K version - no scaling needed!
            button_surface.blit(skin_img, (0, 0))
        else:
            button_image = self.button_images.get(text, self.button_normal)
            if button_image:
                # 4K version - no scaling needed!
                button_surface.blit(button_image, (0, 0))
                if button["hover"]:
                    hover_overlay = pygame.Surface((width, height), pygame.SRCALPHA)
                    hover_overlay.fill((255, 255, 255, 30))
                    button_surface.blit(hover_overlay, (0, 0))
            else:
                # Fallback to gradient if no images available
                base_color = self.LIGHT_BLUE if button["hover"] else self.BLUE
                gradient_start = (min(base_color[0] + 30, 255), min(base_color[1] + 30, 255), min(base_color[2] + 30, 255))
                gradient_end = (max(base_color[0] - 30, 0), max(base_color[1] - 30, 0), max(base_color[2] - 30, 0))
                
                for i in range(height):
                    progress = i / height
                    r = int(gradient_start[0] + (gradient_end[0] - gradient_start[0]) * progress)
                    g = int(gradient_start[1] + (gradient_end[1] - gradient_start[1]) * progress)
                    b = int(gradient_start[2] + (gradient_end[2] - gradient_start[2]) * progress)
                    color = (r, g, b)
                    pygame.draw.line(button_surface, color, (0, i), (width, i))
        
        # Get current visual weight style
        style = self.visual_styles[self.visual_weight_style]
        
        # Add static glow effect (no animation) unless skinned
        if not skinned and style["glow_size"] > 0:
            glow_surface = pygame.Surface((width + style["glow_size"] * 2, height + style["glow_size"] * 2), pygame.SRCALPHA)
            glow_color = self.HOVER_BORDER_COLOR if button["hover"] else self.BORDER_COLOR
            # Note: pygame.draw.rect doesn't support alpha, so we use the base color
            pygame.draw.rect(glow_surface, glow_color[:3], (style["glow_size"], style["glow_size"], width, height), border_radius=10)
            self.screen.blit(glow_surface, (x - style["glow_size"], y - style["glow_size"]))
        
        # Draw button surface
        self.screen.blit(button_surface, (x, y))
        
        # Draw static border unless skinned provides it
        if not skinned and style["border_width"] > 0:
            border_color = self.HOVER_BORDER_COLOR if button["hover"] else self.BORDER_COLOR
            pygame.draw.rect(self.screen, border_color, (x, y, width, height), style["border_width"], border_radius=10)
        
        # Draw text with fire effect but ensure readability
        text = button["text"]
        
        # Main text color (adjusted for skinned)
        main_color = style["text_color"] if not skinned else (235, 235, 245)
        
        # Create outline effect for better readability
        outline_color = (0, 0, 0)  # Black outline
        outline_size = style["text_outline_size"]  # Thickness of outline
        
        # Calculate text position
        text_x = x + (width - self.font.size(text)[0]) // 2
        text_y = y + (height - self.font.size(text)[1]) // 2
        
        # Draw outline by offsetting text in all directions
        for offset_x in range(-outline_size, outline_size + 1):
            for offset_y in range(-outline_size, outline_size + 1):
                if offset_x * offset_x + offset_y * offset_y <= outline_size * outline_size:
                    outline_text = self.font.render(text, True, outline_color)
                    self.screen.blit(outline_text, (text_x + offset_x, text_y + offset_y))
        
        # Draw main text
        main_text = self.font.render(text, True, main_color)
        self.screen.blit(main_text, (text_x, text_y))
        
        # Add subtle glow unless skinned
        if not skinned and style["text_glow_size"] > 0 and style["glow_color"]:
            glow_color = style["glow_color"]
            glow_surf = pygame.Surface((main_text.get_width() + style["text_glow_size"] * 2, main_text.get_height() + style["text_glow_size"] * 2), pygame.SRCALPHA)
            glow_text = self.font.render(text, True, glow_color)
            glow_surf.blit(glow_text, (style["text_glow_size"], style["text_glow_size"]))
            self.screen.blit(glow_surf, (text_x - style["text_glow_size"], text_y - style["text_glow_size"]))
        
        # Check if button is clicked
        clicked = False
        if button["hover"] and pygame.mouse.get_pressed()[0]:
            # Play click sound
            if self.audio:
                self.audio.play_sound('click')
            clicked = True
        
        # Add hover/click logic to button object
        button["clicked"] = clicked
        
        return button

    @safe_operation("try load custom button", None, "WARNING")
    def _try_load_custom_button(self, text: str) -> None:
        """Try to load a custom button image for the given text."""
        try:
            button_image_path = os.path.join(self.asset_path, f"button_{text.lower().replace(' ', '_')}.png")
            if os.path.exists(button_image_path):
                # Only log once per button text
                self._logged_buttons.add(text)
        except Exception as e:
            logger.warning(f"Failed to load custom button for {text}: {str(e)}")
    
    def set_visual_weight_style(self, style: str):
        """Set the visual weight style for buttons."""
        if style in self.visual_styles:
            self.visual_weight_style = style
            print(f"🎨 Visual weight style changed to: {style}")
        else:
            print(f"⚠️ Unknown visual weight style: {style}")
    
    def cycle_visual_weight_style(self):
        """Cycle through visual weight styles for demonstration."""
        styles = list(self.visual_styles.keys())
        current_index = styles.index(self.visual_weight_style)
        next_index = (current_index + 1) % len(styles)
        next_style = styles[next_index]
        self.set_visual_weight_style(next_style)
        return next_style

    def draw_main_menu(self, on_start_action=None, on_story_action=None, on_test_action=None, on_test_lab_action=None, version=None) -> List:
        """Draw the main menu screen."""
        # Update known dimensions from screen (important after fullscreen toggle)
        try:
            self.width = self.screen.get_width()
            self.height = self.screen.get_height()
        except Exception:
            pass
        
        # Handle visual weight style cycling with keyboard
        keys = pygame.key.get_pressed()
        if keys[pygame.K_v]:  # Press V to cycle visual weight styles
            self.cycle_visual_weight_style()
        # Draw background for 4K - no scaling needed!
        if hasattr(self, 'main_background') and self.main_background:
            # For 4K version, assume background is already 3840x2160
            # Just center it on screen
            bg_x = (self.width - self.main_background.get_width()) // 2
            bg_y = (self.height - self.main_background.get_height()) // 2
            # Direct blit - no scaling!
            self.screen.blit(self.main_background, (bg_x, bg_y))
            # Optional tiled noise overlay
            if getattr(self, 'bg_noise_tile', None):
                tile = self.bg_noise_tile
                tw, th = tile.get_width(), tile.get_height()
                for ty in range(0, self.height, th):
                    for tx in range(0, self.width, tw):
                        self.screen.blit(tile, (tx, ty))
            # Contrast overlay
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 100))
            self.screen.blit(overlay, (0, 0))
        else:
            # Use a solid color if no background image
            gradient_rect = pygame.Rect(0, 0, self.width, self.height)
            pygame.draw.rect(self.screen, (20, 20, 50), gradient_rect)
        
        # Draw visual weight style indicator
        style_font = pygame.font.SysFont(None, 36)
        style_text = f"Visual Weight: {self.visual_weight_style.upper()} (Press V to cycle)"
        style_surface = style_font.render(style_text, True, (255, 255, 255))
        self.screen.blit(style_surface, (50, 50))
        
        # Optional title wordmark drawn first; compute buttons start below it
        title_bottom = 0
        if getattr(self, 'title_wordmark', None):
            try:
                # Fixed title size for 4K
                tw = 480  # Fixed width for 4K
                ratio = self.title_wordmark.get_height() / max(1, self.title_wordmark.get_width())
                th = max(1, int(tw * ratio))
                
                # Center the title
                tx = (self.width - tw) // 2
                ty = 40  # Fixed Y position for 4K
                self.screen.blit(self.title_wordmark, (tx, ty))
                title_bottom = ty + th
            except Exception:
                title_bottom = 0

        # Calculate button positions using responsive coordinate system
        base_button_width = 300
        base_button_height = 50
        base_button_margin = 20
        base_default_top = 360  # 1080 // 3
        base_start_y = max(base_default_top, title_bottom + 40)
        base_button_x = 810  # (1920 - 300) // 2
        
        # Scale using responsive system
        button_width = int(base_button_width * self.ui_scale)
        button_height = int(base_button_height * self.ui_scale)
        button_margin = int(base_button_margin * self.ui_scale)
        start_y = int(base_start_y * self.ui_scale)
        button_x = int(base_button_x * self.ui_scale)
        
        # Initialize menu buttons list if it doesn't exist
        if not hasattr(self, 'main_menu_buttons'):
            self.main_menu_buttons = []
        
        # Clear existing buttons and create new ones each time
        self.main_menu_buttons = []
        
        # Create all buttons using create_button method
        button_configs = [
            ("Quickplay", on_start_action),
            ("Story Mode", on_story_action),
            ("Test Mode", on_test_action),
            ("Smithing", None),
            ("Inventory", None),
            ("Settings", None),
            ("Quit", sys.exit)
        ]
        # Ensure the full stack fits vertically; compress height/margin if needed
        count = len(button_configs)
        stack_h = count * button_height + (count - 1) * button_margin
        top_pad = start_y - title_bottom
        base_bottom_pad = 20
        bottom_pad = int(base_bottom_pad * self.ui_scale)
        available = max(0, self.height - (title_bottom + top_pad) - bottom_pad)
        if stack_h > available and available > 0:
            scale = available / stack_h
            # Clamp scale to a reasonable minimum
            scale = max(0.7, min(1.0, scale))
            button_height = max(32, int(button_height * scale))
            button_margin = max(10, int(button_margin * scale))
            stack_h = count * button_height + (count - 1) * button_margin
            # Center the compressed stack in the available region
            start_y = title_bottom + top_pad + max(0, (available - stack_h) // 2)

        for i, (text, action) in enumerate(button_configs):
            button_y = start_y + i * (button_height + button_margin)
            button = self.create_button(
                button_x, button_y,
                button_width, button_height,
                text, action
            )
            self.main_menu_buttons.append(button)
        # Draw version number
        if version:
            base_font_size = 20
            font_size = int(base_font_size * self.ui_scale)
            version_font = pygame.font.SysFont(None, max(16, font_size))
            version_surf = version_font.render(f"v{version}", True, self.LIGHT_GRAY)
            version_rect = version_surf.get_rect(bottomright=(self.width - 10, self.height - 10))
            self.screen.blit(version_surf, version_rect)
        
        # Return the current buttons for interaction
        return self.main_menu_buttons
    
    def process_main_menu_events(self, events: List) -> Optional[str]:
        """Process events for the main menu.
        Returns action string if an action is triggered, None otherwise."""
        for event in events:
            # Handle clicks on menu buttons
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
                mouse_pos = pygame.mouse.get_pos()
                
                for button in self.main_menu_buttons:
                    if button["rect"].collidepoint(mouse_pos):
                        # Play click sound if available
                        if hasattr(self, 'audio') and self.audio:
                            self.audio.play_sound('click')
                        
                        # Handle action
                        if button["text"] == "Quickplay":
                            return "quickplay"
                        elif button["text"] == "Story Mode":
                            return "story"
                        elif button["text"] == "Test Mode":
                            return "test"
                        elif button["text"] == "Smithing":
                            return "smithing"
                        elif button["text"] == "Inventory":
                            return "inventory"
                        elif button["text"] == "Settings":
                            return "settings"
                        elif button["text"] == "Quit":
                            return "quit"
            
            # Handle escape key
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "quit"
        
        return None
    
    def draw_story_menu(self, on_back_action=None) -> List:
        """Draw the story menu screen with 10 saga containers that expand on hover."""
        # Draw background
        if self.story_background:
            # Scale background to fill screen while maintaining aspect ratio
            bg_aspect = self.story_background.get_width() / self.story_background.get_height()
            screen_aspect = self.width / self.height
            
            if screen_aspect > bg_aspect:
                # Screen is wider, scale to width
                bg_width = self.width
                bg_height = int(bg_width / bg_aspect)
            else:
                # Screen is taller, scale to height
                bg_height = self.height
                bg_width = int(bg_height * bg_aspect)
            
            # Center the background
            bg_x = (self.width - bg_width) // 2
            bg_y = (self.height - bg_height) // 2
            
            # Draw the background
            scaled_bg = pygame.transform.scale(self.story_background, (bg_width, bg_height))
            self.screen.blit(scaled_bg, (bg_x, bg_y))
            
            # Add semi-transparent overlay for better contrast with containers
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 80))  # Black with 80/255 alpha
            self.screen.blit(overlay, (0, 0))
        else:
            # Use a solid color if no background image
            self.screen.fill((30, 30, 60))
        
        # Draw title
        title_font = pygame.font.SysFont(None, 72)
        title_surf = title_font.render("Story Mode", True, self.WHITE)
        title_rect = title_surf.get_rect(midtop=(self.width // 2, 50))
        self.screen.blit(title_surf, title_rect)
        
        # Define the layout for the saga containers (5 per row, 2 rows)
        # Calculate container spacing and positions
        container_margin = 30
        container_width = 200
        container_height = 300
        container_per_row = 5
        
        # Calculate total width of all containers in a row including margins
        total_row_width = (container_width * container_per_row) + (container_margin * (container_per_row - 1))
        
        # Calculate starting x position to center the containers
        start_x = (self.width - total_row_width) // 2
        start_y = 150  # Start below title
        
        # Track current mouse position for hover detection
        mouse_pos = pygame.mouse.get_pos()
        
        # Draw each container
        for i, container in enumerate(self.story_containers):
            # Calculate row and column for this container
            row = i // container_per_row
            col = i % container_per_row
            
            # Calculate base position for this container
            base_x = start_x + col * (container_width + container_margin)
            base_y = start_y + row * (container_height + container_margin)
            
            # Check if mouse is hovering
            container_rect = pygame.Rect(
                base_x, 
                base_y, 
                container["current_size"][0], 
                container["current_size"][1]
            )
            
            prev_hover = container["hover"]
            container["hover"] = container_rect.collidepoint(mouse_pos)
            
            # Handle hover sound when first hovering
            if container["hover"] and not prev_hover and hasattr(self, 'audio') and self.audio:
                self.audio.play_sound('hover')
            
            # Animate size transition
            target_size = container["hover_size"] if container["hover"] else container["original_size"]
            
            # Smooth transition between sizes
            if container["current_size"] != target_size:
                # Calculate interpolation factor
                transition_speed = 0.15  # Speed of the transition (0.0 to 1.0)
                
                # Interpolate width and height
                new_width = container["current_size"][0] + (target_size[0] - container["current_size"][0]) * transition_speed
                new_height = container["current_size"][1] + (target_size[1] - container["current_size"][1]) * transition_speed
                
                # Update current size
                container["current_size"] = (int(new_width), int(new_height))
            
            # Recalculate position to keep container centered while expanding
            width_diff = container["current_size"][0] - container["original_size"][0]
            height_diff = container["current_size"][1] - container["original_size"][1]
            
            container_x = base_x - width_diff // 2
            container_y = base_y - height_diff // 2
            
            # Update the container rect
            container["rect"] = pygame.Rect(container_x, container_y, *container["current_size"])
            
            # Draw container background with hover effect
            container_color = self.LIGHT_BLUE if container["hover"] else self.BLUE
            pygame.draw.rect(self.screen, container_color, container["rect"], border_radius=15)
            
            # Draw container border with static color
            border_color = self.HOVER_BORDER_COLOR if container["hover"] else self.BORDER_COLOR
            pygame.draw.rect(self.screen, border_color, container["rect"], 3, border_radius=15)
            
            # Draw saga image if available
            if self.saga_image:
                # Scale the image to fit the container
                image_width = container["current_size"][0] - 20  # Padding
                image_height = container["current_size"][1] - 50  # Space for text
                
                scaled_image = pygame.transform.scale(self.saga_image, (image_width, image_height))
                image_rect = scaled_image.get_rect(
                    midtop=(
                        container_x + container["current_size"][0] // 2,
                        container_y + 10
                    )
                )
                
                # Draw the image
                self.screen.blit(scaled_image, image_rect)
                
                # Draw story title text
                story_font = pygame.font.SysFont(None, 24)
                story_text = f"Story {i+1}"
                story_surf = story_font.render(story_text, True, self.WHITE)
                story_rect = story_surf.get_rect(
                    midtop=(
                        container_x + container["current_size"][0] // 2,
                        container_y + image_height + 15
                    )
                )
                self.screen.blit(story_surf, story_rect)
            else:
                # If no image, just show the story number
                story_font = pygame.font.SysFont(None, 36)
                story_text = f"Story {i+1}"
                story_surf = story_font.render(story_text, True, self.WHITE)
                story_rect = story_surf.get_rect(center=(
                    container_x + container["current_size"][0] // 2,
                    container_y + container["current_size"][1] // 2
                ))
                self.screen.blit(story_surf, story_rect)
        
        # Draw back button
        button_width = 200
        button_height = 50
        button_x = (self.width - button_width) // 2
        button_y = self.height - 80
        
        back_button = self.create_button(
            button_x, button_y, button_width, button_height,
            "Back to Menu", on_back_action
        )
        
        # Store back button in a separate attribute
        self.story_back_button = back_button
        
        # Return all interactive elements
        return self.story_containers + [self.story_back_button]
    
    def process_story_menu_events(self, events: List) -> Optional[str]:
        """Process events for the story menu.
        Returns action string if an action is triggered, None otherwise."""
        for event in events:
            # Handle clicks on story containers or back button
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
                mouse_pos = pygame.mouse.get_pos()
                
                # Check if back button was clicked
                if hasattr(self, 'story_back_button'):
                    if self.story_back_button["rect"].collidepoint(mouse_pos):
                        # Play click sound if available
                        if hasattr(self, 'audio') and self.audio:
                            self.audio.play_sound('click')
                        return "back"
                
                # Check if any story container was clicked
                if hasattr(self, 'story_containers'):
                    for i, container in enumerate(self.story_containers):
                        if container["rect"].collidepoint(mouse_pos):
                            # Play click sound if available
                            if hasattr(self, 'audio') and self.audio:
                                self.audio.play_sound('click')
                            return f"story:{i+1}"
            
            # Handle escape key to go back
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "back"
        
        return None 