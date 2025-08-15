"""
Performance Monitoring Overlay
Displays real-time performance metrics and optimization recommendations in-game.
"""

import pygame
import time
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass

from .game_state_manager import GameStateManager
from modules.logging_module.logger import get_logger


@dataclass
class PerformanceDisplayConfig:
    """Configuration for the performance overlay display."""
    enabled: bool = True
    position: Tuple[int, int] = (10, 50)  # Top-left position
    width: int = 400
    height: int = 300
    background_alpha: int = 180
    text_color: Tuple[int, int, int] = (255, 255, 255)
    warning_color: Tuple[int, int, int] = (255, 255, 0)
    error_color: Tuple[int, int, int] = (255, 100, 100)
    good_color: Tuple[int, int, int] = (100, 255, 100)
    font_size: int = 14
    line_height: int = 18
    update_interval: float = 0.5  # Update every 0.5 seconds


class PerformanceOverlay:
    """
    In-game overlay for displaying performance metrics and optimization recommendations.
    """
    
    def __init__(self, state_manager: GameStateManager, config: Optional[PerformanceDisplayConfig] = None):
        self.state_manager = state_manager
        self.config = config or PerformanceDisplayConfig()
        self.logger = get_logger(__name__)
        
        # Display state
        self.visible = False
        self.last_update_time = 0.0
        self.current_data: Dict[str, Any] = {}
        self.font = None
        self.surface = None
        
        # Performance tracking
        self.frame_times: List[float] = []
        self.max_frame_times = 60  # Track last 60 frames
        
        # Toggle key
        self.toggle_key = pygame.K_F10
    
    def toggle(self) -> None:
        """Toggle the overlay visibility."""
        self.visible = not self.visible
        if self.visible:
            self.logger.info("Performance overlay enabled")
        else:
            self.logger.info("Performance overlay disabled")
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events for the overlay."""
        if event.type == pygame.KEYDOWN:
            if event.key == self.toggle_key:
                self.toggle()
                return True
        return False
    
    def update(self, current_time: float) -> None:
        """Update the overlay data."""
        if not self.visible or not self.config.enabled:
            return
        
        # Update at specified interval
        if current_time - self.last_update_time < self.config.update_interval:
            return
        
        self.last_update_time = current_time
        
        try:
            # Get performance data
            self.current_data = self.state_manager.get_performance_report()
            
            # Update frame time tracking
            if hasattr(self.state_manager, 'profiler') and self.state_manager.profiler:
                if self.state_manager.profiler.frame_times:
                    self.frame_times = list(self.state_manager.profiler.frame_times)[-self.max_frame_times:]
            
        except Exception as e:
            self.logger.error(f"Error updating performance overlay: {e}")
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the performance overlay."""
        if not self.visible or not self.config.enabled:
            return
        
        try:
            # Initialize font if needed
            if self.font is None:
                self.font = pygame.font.SysFont(None, self.config.font_size)
            
            # Create or update surface
            if self.surface is None:
                self.surface = pygame.Surface((self.config.width, self.config.height), pygame.SRCALPHA)
            
            # Clear surface
            self.surface.fill((0, 0, 0, 0))
            
            # Draw background
            background = pygame.Surface((self.config.width, self.config.height), pygame.SRCALPHA)
            background.fill((20, 20, 20, self.config.background_alpha))
            pygame.draw.rect(background, (60, 60, 60), background.get_rect(), 2)
            self.surface.blit(background, (0, 0))
            
            # Draw content
            y_offset = 10
            y_offset = self._draw_header(y_offset)
            y_offset = self._draw_frame_rate_section(y_offset)
            y_offset = self._draw_state_changes_section(y_offset)
            y_offset = self._draw_memory_section(y_offset)
            y_offset = self._draw_cache_section(y_offset)
            y_offset = self._draw_batching_section(y_offset)
            y_offset = self._draw_recommendations_section(y_offset)
            
            # Draw to screen
            screen.blit(self.surface, self.config.position)
            
        except Exception as e:
            self.logger.error(f"Error drawing performance overlay: {e}")
    
    def _draw_header(self, y_offset: int) -> int:
        """Draw the overlay header."""
        title = self.font.render("Performance Monitor", True, self.config.text_color)
        self.surface.blit(title, (10, y_offset))
        
        # Draw toggle instruction
        instruction = self.font.render(f"Press F10 to toggle", True, (150, 150, 150))
        self.surface.blit(instruction, (10, y_offset + 20))
        
        return y_offset + 40
    
    def _draw_frame_rate_section(self, y_offset: int) -> int:
        """Draw frame rate information."""
        if 'profiler' not in self.current_data:
            return y_offset
        
        profiler_data = self.current_data['profiler']
        frame_rate = profiler_data.get('frame_rate', {})
        
        # Section title
        title = self.font.render("Frame Rate:", True, self.config.text_color)
        self.surface.blit(title, (10, y_offset))
        y_offset += self.config.line_height
        
        # FPS
        current_fps = frame_rate.get('current_fps', 0)
        fps_color = self._get_fps_color(current_fps)
        fps_text = self.font.render(f"FPS: {current_fps:.1f}", True, fps_color)
        self.surface.blit(fps_text, (20, y_offset))
        y_offset += self.config.line_height
        
        # Frame time
        avg_frame_time = frame_rate.get('avg_frame_time_ms', 0)
        frame_time_text = self.font.render(f"Frame Time: {avg_frame_time:.1f}ms", True, self.config.text_color)
        self.surface.blit(frame_time_text, (20, y_offset))
        y_offset += self.config.line_height
        
        return y_offset + 5
    
    def _draw_state_changes_section(self, y_offset: int) -> int:
        """Draw state change information."""
        if 'profiler' not in self.current_data:
            return y_offset
        
        profiler_data = self.current_data['profiler']
        state_changes = profiler_data.get('state_changes', {})
        
        # Section title
        title = self.font.render("State Changes:", True, self.config.text_color)
        self.surface.blit(title, (10, y_offset))
        y_offset += self.config.line_height
        
        # Changes per frame
        avg_per_frame = state_changes.get('avg_per_frame', 0)
        changes_color = self._get_changes_color(avg_per_frame)
        changes_text = self.font.render(f"Per Frame: {avg_per_frame:.1f}", True, changes_color)
        self.surface.blit(changes_text, (20, y_offset))
        y_offset += self.config.line_height
        
        # Total fields tracked
        total_fields = state_changes.get('total_fields_tracked', 0)
        fields_text = self.font.render(f"Fields Tracked: {total_fields}", True, self.config.text_color)
        self.surface.blit(fields_text, (20, y_offset))
        y_offset += self.config.line_height
        
        return y_offset + 5
    
    def _draw_memory_section(self, y_offset: int) -> int:
        """Draw memory usage information."""
        if 'profiler' not in self.current_data:
            return y_offset
        
        profiler_data = self.current_data['profiler']
        memory = profiler_data.get('memory', {})
        
        # Section title
        title = self.font.render("Memory:", True, self.config.text_color)
        self.surface.blit(title, (10, y_offset))
        y_offset += self.config.line_height
        
        # Current memory
        current_mb = memory.get('current_mb', 0)
        memory_color = self._get_memory_color(current_mb)
        memory_text = self.font.render(f"Current: {current_mb:.1f} MB", True, memory_color)
        self.surface.blit(memory_text, (20, y_offset))
        y_offset += self.config.line_height
        
        # Peak memory
        peak_mb = memory.get('peak_mb', 0)
        peak_text = self.font.render(f"Peak: {peak_mb:.1f} MB", True, self.config.text_color)
        self.surface.blit(peak_text, (20, y_offset))
        y_offset += self.config.line_height
        
        return y_offset + 5
    
    def _draw_cache_section(self, y_offset: int) -> int:
        """Draw cache performance information."""
        if 'cache' not in self.current_data:
            return y_offset
        
        cache_data = self.current_data['cache']
        
        # Section title
        title = self.font.render("Cache:", True, self.config.text_color)
        self.surface.blit(title, (10, y_offset))
        y_offset += self.config.line_height
        
        # Hit rate
        hit_rate = cache_data.get('hit_rate_percent', 0)
        hit_rate_color = self._get_hit_rate_color(hit_rate)
        hit_rate_text = self.font.render(f"Hit Rate: {hit_rate:.1f}%", True, hit_rate_color)
        self.surface.blit(hit_rate_text, (20, y_offset))
        y_offset += self.config.line_height
        
        # Total entries
        total_entries = cache_data.get('total_entries', 0)
        entries_text = self.font.render(f"Entries: {total_entries}", True, self.config.text_color)
        self.surface.blit(entries_text, (20, y_offset))
        y_offset += self.config.line_height
        
        return y_offset + 5
    
    def _draw_batching_section(self, y_offset: int) -> int:
        """Draw batching performance information."""
        if 'batching' not in self.current_data:
            return y_offset
        
        batching_data = self.current_data['batching']
        
        # Section title
        title = self.font.render("Batching:", True, self.config.text_color)
        self.surface.blit(title, (10, y_offset))
        y_offset += self.config.line_height
        
        # Average batch size
        avg_batch_size = batching_data.get('avg_batch_size', 0)
        batch_text = self.font.render(f"Avg Batch: {avg_batch_size:.1f}", True, self.config.text_color)
        self.surface.blit(batch_text, (20, y_offset))
        y_offset += self.config.line_height
        
        # Pending changes
        pending_changes = batching_data.get('pending_changes', 0)
        pending_text = self.font.render(f"Pending: {pending_changes}", True, self.config.text_color)
        self.surface.blit(pending_text, (20, y_offset))
        y_offset += self.config.line_height
        
        return y_offset + 5
    
    def _draw_recommendations_section(self, y_offset: int) -> int:
        """Draw optimization recommendations."""
        if 'recommendations' not in self.current_data:
            return y_offset
        
        recommendations = self.current_data['recommendations']
        
        if not recommendations:
            return y_offset
        
        # Section title
        title = self.font.render("Recommendations:", True, self.config.warning_color)
        self.surface.blit(title, (10, y_offset))
        y_offset += self.config.line_height
        
        # Show first few recommendations
        for i, recommendation in enumerate(recommendations[:3]):
            if y_offset + self.config.line_height > self.config.height - 20:
                break
            
            # Truncate long recommendations
            if len(recommendation) > 50:
                recommendation = recommendation[:47] + "..."
            
            rec_text = self.font.render(recommendation, True, self.config.warning_color)
            self.surface.blit(rec_text, (20, y_offset))
            y_offset += self.config.line_height
        
        return y_offset
    
    def _get_fps_color(self, fps: float) -> Tuple[int, int, int]:
        """Get color for FPS display."""
        if fps >= 55:
            return self.config.good_color
        elif fps >= 45:
            return self.config.warning_color
        else:
            return self.config.error_color
    
    def _get_changes_color(self, changes_per_frame: float) -> Tuple[int, int, int]:
        """Get color for state changes display."""
        if changes_per_frame <= 10:
            return self.config.good_color
        elif changes_per_frame <= 30:
            return self.config.warning_color
        else:
            return self.config.error_color
    
    def _get_memory_color(self, memory_mb: float) -> Tuple[int, int, int]:
        """Get color for memory usage display."""
        if memory_mb <= 300:
            return self.config.good_color
        elif memory_mb <= 500:
            return self.config.warning_color
        else:
            return self.config.error_color
    
    def _get_hit_rate_color(self, hit_rate: float) -> Tuple[int, int, int]:
        """Get color for cache hit rate display."""
        if hit_rate >= 80:
            return self.config.good_color
        elif hit_rate >= 60:
            return self.config.warning_color
        else:
            return self.config.error_color


# Global overlay instance
_global_overlay: Optional[PerformanceOverlay] = None


def get_performance_overlay() -> Optional[PerformanceOverlay]:
    """Get the global performance overlay instance."""
    return _global_overlay


def set_global_overlay(overlay: PerformanceOverlay) -> None:
    """Set the global performance overlay instance."""
    global _global_overlay
    _global_overlay = overlay 