"""
Story System Implementation
Handles story loading, content display, and beautiful UI with scrolling.
"""

import pygame
import os
from typing import Dict, List, Optional, Tuple, Any

# Try importing the interface contract
try:
    from contracts.story_interface_contract import StorySystemInterface, validate_story_interface
    interface_available = True
except ImportError:
    # Create a dummy interface if not available
    class StorySystemInterface:
        pass
    
    def validate_story_interface(cls):
        return cls
    
    interface_available = False
    print("⚠️  Story interface contract not available, running without validation")


@validate_story_interface
class StorySystem:
    """
    Story System implementation for beautiful story content management.
    Preserves the beautiful UI design with particles, overlays, and smooth scrolling.
    """
    
    def __init__(self, screen: pygame.Surface, font: pygame.font.Font, width: int, height: int, menu_system: Any = None):
        """
        Initialize the story system.
        
        Args:
            screen: Pygame display surface
            font: Font for UI elements
            width: Screen width
            height: Screen height
            menu_system: Optional menu system for particle effects
        """
        self.screen = screen
        self.font = font
        self.width = width
        self.height = height
        self.menu_system = menu_system
        
        # Colors for beautiful UI
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.LIGHT_GRAY = (200, 200, 200)
        self.CHAPTER_COLOR = (220, 180, 255)
        self.SCROLL_INDICATOR_COLOR = (180, 180, 255)
        
        # Load story background
        self.story_background = None
        try:
            self.story_background = pygame.image.load(os.path.join("puzzleassets", "storybackground.png"))
        except pygame.error:
            # Fallback - create a gradient background
            self.story_background = self._create_gradient_background()
        
        # Story file mapping
        self.story_files = {
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
        
        print("✅ StorySystem initialized with beautiful UI")
    
    def _create_gradient_background(self) -> pygame.Surface:
        """Create a beautiful gradient background as fallback."""
        background = pygame.Surface((self.width, self.height))
        for y in range(self.height):
            # Create a dark blue to purple gradient
            ratio = y / self.height
            r = int(20 + ratio * 40)
            g = int(10 + ratio * 30)
            b = int(50 + ratio * 80)
            color = (r, g, b)
            pygame.draw.line(background, color, (0, y), (self.width, y))
        return background
    
    def load_story(self, story_id: int) -> Dict[str, Any]:
        """
        Load story content from file based on story ID.
        
        Args:
            story_id: ID of the story to load
            
        Returns:
            Dictionary containing story title and content
        """
        # Default content if file not found
        story_data = {
            "title": f"Story {story_id}",
            "content": ["No story content available yet.", "Check back later for updates!"]
        }
        
        # Try to load the story file
        if story_id in self.story_files:
            try:
                with open(self.story_files[story_id], "r", encoding="utf-8") as f:
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
                        content.append(line)
                
                story_data = {
                    "title": title,
                    "content": content
                }
                
                print(f"Loaded story: {title}")
            except Exception as e:
                print(f"Error loading story {story_id}: {e}")
        
        return story_data
    
    def display_story_content(self, story_data: Dict[str, Any], scroll_position: int) -> int:
        """
        Display story content with beautiful UI and scrolling.
        
        Args:
            story_data: Story data dictionary
            scroll_position: Current scroll position
            
        Returns:
            Updated scroll position (limited to valid range)
        """
        # Clear the screen
        self.screen.fill(self.BLACK)
        
        # Draw beautiful background
        if self.story_background:
            # Scale to fit screen
            scaled_bg = pygame.transform.scale(self.story_background, (self.width, self.height))
            self.screen.blit(scaled_bg, (0, 0))
        
        # Add semi-transparent overlay for better readability
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Black with 180/255 alpha
        self.screen.blit(overlay, (0, 0))
        
        # Draw menu particles for visual appeal
        if self.menu_system and hasattr(self.menu_system, 'draw_menu_particles'):
            self.menu_system.draw_menu_particles()
        
        # Create content area
        content_width = int(self.width * 0.8)
        content_x = (self.width - content_width) // 2
        padding = 20
        
        # Initialize fonts
        title_font = pygame.font.SysFont('Arial', 56)
        chapter_font = pygame.font.SysFont('Arial', 36)
        text_font = pygame.font.SysFont('Arial', 24)
        
        # Render the title
        title_surf = title_font.render(story_data["title"], True, self.WHITE)
        title_rect = title_surf.get_rect(midtop=(self.width // 2, padding))
        self.screen.blit(title_surf, title_rect)
        
        # Calculate content positioning
        content_surfaces = []
        y_offset = title_rect.bottom + padding
        
        # Render all content lines
        for line in story_data["content"]:
            if not line:
                # Add spacing for empty lines
                y_offset += 15
                continue
                
            if line.startswith("## "):
                # Chapter title
                surf = chapter_font.render(line[3:], True, self.CHAPTER_COLOR)
                y_offset += 30  # Extra space before chapters
            else:
                # Regular text - wrap long lines
                wrapped_lines = self._wrap_text(line, text_font, content_width)
                for wrapped_line in wrapped_lines:
                    surf = text_font.render(wrapped_line, True, self.WHITE)
                    rect = surf.get_rect(topleft=(content_x, y_offset - scroll_position))
                    content_surfaces.append((surf, rect, y_offset))
                    y_offset += surf.get_height() + 5
                continue
            
            rect = surf.get_rect(topleft=(content_x, y_offset - scroll_position))
            content_surfaces.append((surf, rect, y_offset))
            y_offset += surf.get_height() + 5
        
        total_height = y_offset + padding
        
        # Draw only visible content
        for surf, rect, original_y in content_surfaces:
            if original_y - scroll_position < -50:
                continue  # Skip if well above the view
            if original_y - scroll_position > self.height + 50:
                continue  # Skip if well below the view
                
            self.screen.blit(surf, rect)
        
        # Limit scrolling to valid range
        max_scroll = max(0, total_height - self.height)
        scroll_position = max(0, min(scroll_position, max_scroll))
        
        # Draw scroll indicators if needed
        if total_height > self.height:
            # Up indicator
            if scroll_position > 0:
                pygame.draw.polygon(self.screen, self.SCROLL_INDICATOR_COLOR, [
                    (self.width // 2, 15),
                    (self.width // 2 - 10, 25),
                    (self.width // 2 + 10, 25)
                ])
            
            # Down indicator
            if scroll_position < max_scroll:
                pygame.draw.polygon(self.screen, self.SCROLL_INDICATOR_COLOR, [
                    (self.width // 2, self.height - 15),
                    (self.width // 2 - 10, self.height - 25),
                    (self.width // 2 + 10, self.height - 25)
                ])
        
        # Draw instruction
        instruction_font = pygame.font.SysFont('Arial', 20)
        instruction_text = "Use arrow keys or mouse wheel to scroll. Press ESC to return to story menu."
        instruction_surf = instruction_font.render(instruction_text, True, self.LIGHT_GRAY)
        instruction_rect = instruction_surf.get_rect(midbottom=(self.width // 2, self.height - 10))
        self.screen.blit(instruction_surf, instruction_rect)
        
        return scroll_position
    
    def _wrap_text(self, text: str, font: pygame.font.Font, max_width: int) -> List[str]:
        """
        Wrap text to fit within specified width.
        
        Args:
            text: Text to wrap
            font: Font to use for measurement
            max_width: Maximum width in pixels
            
        Returns:
            List of wrapped text lines
        """
        if not text:
            return [""]
        
        words = text.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines if lines else [""]
    
    def handle_story_events(self, events: List[pygame.event.Event], scroll_position: int) -> Tuple[Optional[str], int]:
        """
        Handle story content events (scrolling, navigation).
        
        Args:
            events: List of pygame events
            scroll_position: Current scroll position
            
        Returns:
            Tuple of (action, new_scroll_position)
        """
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return ("back_to_story", scroll_position)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    # Scroll down
                    scroll_position += 20
                elif event.key == pygame.K_UP or event.key == pygame.K_w:
                    # Scroll up
                    scroll_position = max(0, scroll_position - 20)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:  # Mouse wheel up
                    scroll_position = max(0, scroll_position - 40)
                elif event.button == 5:  # Mouse wheel down
                    scroll_position += 40
        
        return (None, scroll_position)
    
    def get_story_list(self) -> List[Dict[str, Any]]:
        """
        Get list of available stories.
        
        Returns:
            List of story metadata
        """
        stories = []
        for story_id, filename in self.story_files.items():
            stories.append({
                "id": story_id,
                "title": f"Saga {story_id}",
                "filename": filename,
                "available": os.path.exists(filename)
            })
        return stories
    
    def update_resolution(self, width: int, height: int) -> None:
        """
        Update story system for new resolution.
        
        Args:
            width: New screen width
            height: New screen height
        """
        self.width = width
        self.height = height
        
        # Recreate gradient background if needed
        if self.story_background and self.story_background.get_width() != width:
            if not os.path.exists(os.path.join("puzzleassets", "storybackground.png")):
                self.story_background = self._create_gradient_background()


# Interface validation
if interface_available:
    print("✅ StorySystem interface validation passed")
else:
    print("⚠️  StorySystem running without interface validation") 