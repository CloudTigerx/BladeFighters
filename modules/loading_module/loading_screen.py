import pygame
import os
import sys
import time
from typing import List, Tuple, Callable, Optional
from ..logging_module.error_handler import (
    safe_operation,
    safe_file_operation
)
from ..logging_module.logger import get_logger

logger = get_logger(__name__)


class LoadingScreen:
    """
    Loading screen with progress bar and task display.
    Provides visual feedback during game initialization.
    """

    def __init__(self, screen: pygame.Surface, asset_path: str = "puzzleassets"):
        self.screen = screen
        self.asset_path = asset_path
        self.width = screen.get_width()
        self.height = screen.get_height()
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.BLUE = (0, 100, 255)
        self.LIGHT_BLUE = (100, 150, 255)
        self.GRAY = (50, 50, 50)
        
        # Progress bar dimensions
        self.progress_bar_width = int(self.width * 0.6)
        self.progress_bar_height = 20
        self.progress_bar_x = (self.width - self.progress_bar_width) // 2
        self.progress_bar_y = self.height // 2
        
        # State
        self.is_loading = False
        self.progress = 0.0
        self.current_task = "Initializing..."
        
        # Funny loading messages
        self.loading_messages = [
            "Building Your Blade...",
            "Assembling Blocks...", 
            "Deny Defend Depose...",
            "Sharpening Swords...",
            "Forging the Future...",
            "Loading Legendary Loot...",
            "Preparing Puzzle Pieces...",
            "Crafting Combat Code...",
            "Summoning Sword Spirits...",
            "Loading Lethal Logic...",
            "Preparing for Battle...",
            "Sharpening Your Skills...",
            "Loading the Legend...",
            "Preparing the Arena...",
            "Summoning Your Sword...",
            "Loading Combat Code...",
            "Preparing Puzzle Power...",
            "Sharpening Your Strategy...",
            "Loading Lethal Moves...",
            "Preparing for Glory..."
        ]
        
        self.current_message_index = 0
        self.message_change_timer = 0
        self.message_change_interval = 1500  # 1.5 seconds per message
        
        # Load loading background image
        self.loading_image = None
        self._load_loading_image()
        
        logger.info("LoadingScreen initialized")
    
    def _update_loading_message(self) -> None:
        """Update the loading message periodically."""
        current_time = pygame.time.get_ticks()
        
        if current_time - self.message_change_timer > self.message_change_interval:
            self.current_message_index = (self.current_message_index + 1) % len(self.loading_messages)
            self.message_change_timer = current_time

    def get_current_loading_message(self) -> str:
        """Get the current loading message."""
        return self.loading_messages[self.current_message_index]
    
    def _load_loading_image(self):
        """Load the loading background image."""
        try:
            # Try to load loading.png as loading image
            image_path = os.path.join(self.asset_path, "fonts", "loading.png")
            if os.path.exists(image_path):
                self.loading_image = pygame.image.load(image_path).convert_alpha()
                logger.info("✅ Loaded loading background image: loading.png")
            else:
                logger.warning("⚠️ Loading background image not found: loading.png")
        except Exception as e:
            logger.warning(f"⚠️ Failed to load loading background image: {e}")
            self.loading_image = None

    def update_screen(self, new_screen: pygame.Surface) -> None:
        """Update the screen reference if it changes."""
        self.screen = new_screen
        self.width = new_screen.get_width()
        self.height = new_screen.get_height()
        
        # Recalculate progress bar position
        self.progress_bar_x = (self.width - self.progress_bar_width) // 2
        self.progress_bar_y = self.height // 2

    def update_progress(self, progress: float, task: str) -> None:
        """Update the loading progress and current task."""
        self.progress = max(0.0, min(1.0, progress))
        self.current_task = task

    def draw(self) -> None:
        """Draw the loading screen."""
        # Clear screen
        self.screen.fill(self.BLACK)
        
        # Draw loading background image if available
        if self.loading_image:
            # Scale image to fit screen while maintaining aspect ratio
            img_width, img_height = self.loading_image.get_size()
            screen_ratio = self.width / self.height
            img_ratio = img_width / img_height
            
            if img_ratio > screen_ratio:
                # Image is wider than screen, fit to width
                new_width = self.width
                new_height = int(self.width / img_ratio)
            else:
                # Image is taller than screen, fit to height
                new_height = self.height
                new_width = int(self.height * img_ratio)
            
            # Scale the image
            scaled_image = pygame.transform.smoothscale(self.loading_image, (new_width, new_height))
            
            # Center the image
            x = (self.width - new_width) // 2
            y = (self.height - new_height) // 2
            
            # Draw the background image
            self.screen.blit(scaled_image, (x, y))
            
            # Add a semi-transparent overlay for better text readability
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))  # Semi-transparent black
            self.screen.blit(overlay, (0, 0))
        
        # Draw title
        title_font = self._get_font(36)
        title_surface = title_font.render("BladeFighters", True, self.WHITE)
        title_rect = title_surface.get_rect(center=(self.width // 2, self.height // 4))
        self.screen.blit(title_surface, title_rect)
        
        # Draw progress bar background
        progress_bg_rect = pygame.Rect(
            self.progress_bar_x, 
            self.progress_bar_y, 
            self.progress_bar_width, 
            self.progress_bar_height
        )
        pygame.draw.rect(self.screen, self.GRAY, progress_bg_rect)
        
        # Draw progress bar fill
        progress_fill_width = int(self.progress_bar_width * self.progress)
        if progress_fill_width > 0:
            progress_fill_rect = pygame.Rect(
                self.progress_bar_x, 
                self.progress_bar_y, 
                progress_fill_width, 
                self.progress_bar_height
            )
            pygame.draw.rect(self.screen, self.BLUE, progress_fill_rect)
        
        # Draw progress bar border
        pygame.draw.rect(self.screen, self.WHITE, progress_bg_rect, 2)
        
        # Draw progress text
        progress_text = f"{int(self.progress * 100)}%"
        progress_font = self._get_font(24)
        
        progress_surface = progress_font.render(progress_text, True, self.WHITE)
        progress_rect = progress_surface.get_rect(center=(
            self.width // 2, 
            self.progress_bar_y + self.progress_bar_height + 30
        ))
        self.screen.blit(progress_surface, progress_rect)
        
        # Draw current task
        task_surface = progress_font.render(self.current_task, True, self.LIGHT_BLUE)
        task_rect = task_surface.get_rect(center=(
            self.width // 2, 
            self.progress_bar_y - 30
        ))
        self.screen.blit(task_surface, task_rect)
        
        # Draw funny loading message
        self._update_loading_message()
        loading_message = self.get_current_loading_message()
        message_surface = progress_font.render(loading_message, True, self.LIGHT_BLUE)
        message_rect = message_surface.get_rect(center=(
            self.width // 2, 
            self.progress_bar_y + self.progress_bar_height + 80  # Below progress text
        ))
        self.screen.blit(message_surface, message_rect)
        
        # Update display
        pygame.display.flip()

    @safe_file_operation("load font", None, "WARNING")
    def _get_font(self, size: int) -> pygame.font.Font:
        """Get a font with fallback to system font."""
        try:
            font_path = os.path.join(self.asset_path, "fonts", "PermanentMarker-Regular.ttf")
            if os.path.exists(font_path):
                return pygame.font.Font(font_path, size)
        except Exception as e:
            logger.warning(f"Failed to load custom font: {str(e)}")
        
        # Fallback to system font
        return pygame.font.SysFont('Arial', size)
    
    def start_loading(self, loading_tasks: List[Tuple[str, Callable]], on_complete: Callable = None):
        """
        Start the loading process with a list of tasks.
        
        Args:
            loading_tasks: List of (task_name, task_function) tuples
            on_complete: Callback function to run when loading is complete
        """
        self.is_loading = True
        self.progress = 0.0
        total_tasks = len(loading_tasks)
        
        # Execute tasks sequentially with progress updates
        for i, (task_name, task_func) in enumerate(loading_tasks):
            # Update progress
            progress = i / total_tasks
            self.update_progress(progress, task_name)
            
            # Draw loading screen
            self.draw()
            
            # Execute task with error handling
            self._execute_loading_task(task_name, task_func)
            
            # If the display surface changed during the task (e.g., set_mode), update reference
            self._update_screen_reference()
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
            # Small delay to show progress
            time.sleep(0.1)
        
        # Complete
        self.update_progress(1.0, "Loading Complete!")
        self.draw()
        time.sleep(0.5)
        
        self.is_loading = False
        if on_complete:
            on_complete()

    @safe_operation("execute loading task", None, "ERROR")
    def _execute_loading_task(self, task_name: str, task_func: Callable) -> None:
        """Execute a loading task with error handling."""
        try:
            task_func()
        except Exception as e:
            logger.error(f"Error in loading task '{task_name}': {str(e)}")

    @safe_operation("update screen reference", None, "WARNING")
    def _update_screen_reference(self) -> None:
        """Update screen reference if it changed during task execution."""
        try:
            current_surface = pygame.display.get_surface()
            if current_surface and current_surface is not self.screen:
                self.update_screen(current_surface)
        except Exception as e:
            logger.warning(f"Failed to update screen reference: {str(e)}") 