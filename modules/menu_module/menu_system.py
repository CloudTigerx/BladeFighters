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

@validate_menu_interface
class MenuSystem(MenuSystemInterface):
    """Extracted MenuSystem class with interface validation."""
    
    def __init__(self, screen, font, audio, asset_path: str):
        """Initialize the menu system."""
        self.screen = screen
        self.font = font
        self.audio = audio
        self.asset_path = asset_path
        
        # Get screen dimensions
        self.width = screen.get_width()
        self.height = screen.get_height()
        
        # Track button states
        self.main_menu_buttons = []
        self.settings_buttons = []
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
        
        # Load background images
        self.main_background = self.load_background("colorful.png")
        self.story_background = self.load_background("storybackground.png")
        
        # Load main menu title image
        self.main_menu_title = self.load_image("mainmenutitle.png")
        
        # Load button images
        self.button_images = {
            "Quickplay": self.load_image("banner.png"),
            "Story Mode": self.load_image("banner.png"),
            "Test Mode": self.load_image("banner.png"),
            "Settings": self.load_image("banner.png"),
            "Quit": self.load_image("banner.png")
        }
        
        # Fallback to banner.png if any button image is missing
        self.button_normal = self.load_image("banner.png")
        self.button_hover = self.load_image("banner.png")
        
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
        
        print("✅ MenuSystem initialized with core functionality")
    
    def load_background(self, filename: str):
        """Load a background image from the asset path."""
        try:
            return pygame.image.load(os.path.join(self.asset_path, filename))
        except pygame.error as e:
            print(f"Error loading background {filename}: {e}")
            return None
            
    def load_image(self, filename: str):
        """Load an image from the asset path."""
        try:
            full_path = os.path.join(self.asset_path, filename)
            print(f"Attempting to load image: {full_path}")
            image = pygame.image.load(full_path)
            print(f"Successfully loaded image: {filename}")
            return image
        except pygame.error as e:
            print(f"Error loading image {filename}: {e}")
            return None
    
    # Add a class variable to track which buttons we've already logged
    _logged_buttons = set()

    def create_button(self, x: int, y: int, width: int, height: int, 
                     text: str, action=None, params=None) -> Dict:
        """Create a button with text and optional action."""
        # Try to load custom button image if not already loaded
        if text not in self._logged_buttons:
            try:
                button_image_path = os.path.join(self.asset_path, f"button_{text.lower().replace(' ', '_')}.png")
                if os.path.exists(button_image_path):
                    # Only log once per button text
                    self._logged_buttons.add(text)
            except:
                pass

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
        
        # Get the appropriate button image
        button_image = self.button_images.get(text, self.button_normal)
        if button_image:
            # Scale the image to fit the button size
            scaled_image = pygame.transform.scale(button_image, (width, height))
            button_surface.blit(scaled_image, (0, 0))
            
            # Add hover effect by adjusting brightness
            if button["hover"]:
                # Create a bright overlay for hover effect
                hover_overlay = pygame.Surface((width, height), pygame.SRCALPHA)
                hover_overlay.fill((255, 255, 255, 30))  # White overlay with 30/255 alpha
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
        
        # Add static glow effect (no animation)
        glow_surface = pygame.Surface((width + 20, height + 20), pygame.SRCALPHA)
        glow_color = self.HOVER_BORDER_COLOR if button["hover"] else self.BORDER_COLOR
        glow_alpha = int(80)  # Static alpha value
        
        # Draw outer glow (static)
        glow_color_with_alpha = (*glow_color[:3], glow_alpha)
        pygame.draw.rect(glow_surface, glow_color_with_alpha, 
                        (10, 10, width, height), 
                        border_radius=10)
        
        # Draw button surface
        self.screen.blit(glow_surface, (x-10, y-10))
        self.screen.blit(button_surface, (x, y))
        
        # Draw static border (no pulse animation)
        border_color = self.HOVER_BORDER_COLOR if button["hover"] else self.BORDER_COLOR
        pygame.draw.rect(self.screen, border_color, 
                        (x, y, width, height), 
                        2, border_radius=10)
        
        # Draw text with fire effect but ensure readability
        text = button["text"]
        
        # Main text color (bright orange)
        main_color = (255, 140, 0)  # Bright orange
        
        # Create outline effect for better readability
        outline_color = (0, 0, 0)  # Black outline
        outline_size = 3  # Thickness of outline
        
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
        
        # Add subtle glow
        glow_color = (255, 100, 0, 30)  # Semi-transparent orange
        glow_surf = pygame.Surface((main_text.get_width() + 10, main_text.get_height() + 10), pygame.SRCALPHA)
        glow_text = self.font.render(text, True, glow_color)
        glow_surf.blit(glow_text, (5, 5))
        self.screen.blit(glow_surf, (text_x - 5, text_y - 5))
        
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
    
    def draw_main_menu(self, on_start_action=None, on_settings_action=None, 
                      on_story_action=None, on_test_action=None, on_test_lab_action=None, version=None) -> List:
        """Draw the main menu screen."""
        # Draw background
        if hasattr(self, 'main_background') and self.main_background:
            # Scale background to fill screen while maintaining aspect ratio
            bg_aspect = self.main_background.get_width() / self.main_background.get_height()
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
            scaled_bg = pygame.transform.scale(self.main_background, (bg_width, bg_height))
            self.screen.blit(scaled_bg, (bg_x, bg_y))
            
            # Add semi-transparent overlay for better contrast with text
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 100))  # Black with 100/255 alpha
            self.screen.blit(overlay, (0, 0))
        else:
            # Use a solid color if no background image
            gradient_rect = pygame.Rect(0, 0, self.width, self.height)
            pygame.draw.rect(self.screen, (20, 20, 50), gradient_rect)
        
        # Calculate button positions based on screen size
        button_width = 300
        button_height = 50
        button_margin = 20
        start_y = self.height // 3
        button_x = (self.width - button_width) // 2
        
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
            ("Test Laboratory", on_test_lab_action),  # Add Test Laboratory button
            ("Settings", on_settings_action),
            ("Quit", sys.exit)
        ]
        
        for i, (text, action) in enumerate(button_configs):
            button_y = start_y + i * (button_height + button_margin)
            button = self.create_button(
                button_x, button_y,
                button_width, button_height,
                text, action
            )
            self.main_menu_buttons.append(button)
        
        # Draw title image
        if hasattr(self, 'main_menu_title') and self.main_menu_title:
            # Scale the title image to a reasonable size (e.g., 400px wide)
            title_width = 400
            title_height = int(title_width * (self.main_menu_title.get_height() / self.main_menu_title.get_width()))
            scaled_title = pygame.transform.scale(self.main_menu_title, (title_width, title_height))
            
            # Center the title at the top
            title_x = (self.width - title_width) // 2
            title_y = 50
            self.screen.blit(scaled_title, (title_x, title_y))
        
        # Draw version number
        if version:
            version_font = pygame.font.SysFont(None, 20)
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
                        elif button["text"] == "Test Laboratory":
                            return "test_lab"
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