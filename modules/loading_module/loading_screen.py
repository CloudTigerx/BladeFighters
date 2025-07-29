import pygame
import os
import time
import threading
from typing import Callable, List, Tuple
import sys

class LoadingScreen:
    """
    Manages the loading screen display with progress tracking and visual feedback.
    """
    
    def __init__(self, screen: pygame.Surface, asset_path: str):
        self.screen = screen
        self.asset_path = asset_path
        self.width, self.height = screen.get_size()
        
        # Loading screen image
        self.loading_image = None
        self.loading_image_path = os.path.join(asset_path, "fonts", "ChatGPT Image Jul 27, 2025, 05_01_16 AM.png")
        
        # Progress tracking
        self.progress = 0.0  # 0.0 to 1.0
        self.current_task = "Initializing..."
        self.is_loading = False
        
        # Visual elements
        self.progress_bar_width = int(self.width * 0.6)
        self.progress_bar_height = 20
        self.progress_bar_x = (self.width - self.progress_bar_width) // 2
        self.progress_bar_y = int(self.height * 0.8)
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.BLUE = (0, 100, 255)
        self.LIGHT_BLUE = (100, 150, 255)
        self.GRAY = (100, 100, 100)
        
        # Load the loading image
        self._load_loading_image()
    
    def _load_loading_image(self):
        """Load the loading screen background image."""
        try:
            if os.path.exists(self.loading_image_path):
                self.loading_image = pygame.image.load(self.loading_image_path)
                # Scale to fit screen while maintaining aspect ratio
                self.loading_image = self._scale_image_to_fit(self.loading_image)
                print(f"✅ Loaded loading screen image: {self.loading_image_path}")
            else:
                print(f"⚠️ Loading screen image not found: {self.loading_image_path}")
                self.loading_image = None
        except Exception as e:
            print(f"⚠️ Error loading loading screen image: {e}")
            self.loading_image = None
    
    def _scale_image_to_fit(self, image: pygame.Surface) -> pygame.Surface:
        """Scale image to fit screen while maintaining aspect ratio."""
        img_width, img_height = image.get_size()
        screen_width, screen_height = self.width, self.height
        
        # Calculate scaling factors
        scale_x = screen_width / img_width
        scale_y = screen_height / img_height
        scale = min(scale_x, scale_y)
        
        # Calculate new dimensions
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)
        
        # Scale the image
        return pygame.transform.scale(image, (new_width, new_height))
    
    def update_progress(self, progress: float, task: str = None):
        """Update the loading progress and current task."""
        self.progress = max(0.0, min(1.0, progress))
        if task:
            self.current_task = task
    
    def draw(self):
        """Draw the loading screen."""
        # Clear screen
        self.screen.fill(self.BLACK)
        
        # Draw background image if available
        if self.loading_image:
            # Center the image
            img_rect = self.loading_image.get_rect()
            img_rect.center = (self.width // 2, self.height // 2)
            self.screen.blit(self.loading_image, img_rect)
        
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
        try:
            font = pygame.font.Font(os.path.join(self.asset_path, "fonts", "PermanentMarker-Regular.ttf"), 24)
        except:
            font = pygame.font.SysFont('Arial', 24)
        
        progress_surface = font.render(progress_text, True, self.WHITE)
        progress_rect = progress_surface.get_rect(center=(
            self.width // 2, 
            self.progress_bar_y + self.progress_bar_height + 30
        ))
        self.screen.blit(progress_surface, progress_rect)
        
        # Draw current task
        task_surface = font.render(self.current_task, True, self.LIGHT_BLUE)
        task_rect = task_surface.get_rect(center=(
            self.width // 2, 
            self.progress_bar_y - 30
        ))
        self.screen.blit(task_surface, task_rect)
        
        # Update display
        pygame.display.flip()
    
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
            
            # Execute task
            try:
                task_func()
            except Exception as e:
                print(f"⚠️ Error in loading task '{task_name}': {e}")
            
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