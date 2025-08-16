"""
Character Animation Manager - Handles character animation timing and state
Professional animation management for character sprites.
"""

import pygame
from typing import Dict, Optional, Tuple
from ..logging_module.logger import get_logger

logger = get_logger(__name__)


class CharacterAnimationManager:
    """
    Manages character animation timing and state.
    Handles frame timing, animation loops, and state transitions.
    """
    
    def __init__(self, clock=None):
        """Initialize the character animation manager."""
        self.clock = clock or pygame.time.Clock()
        
        # Animation states for each character
        self.animation_states: Dict[str, Dict] = {}
        
        # Current animation frame for each character
        self.current_frames: Dict[str, int] = {}
        
        # Last frame update time for each character
        self.last_frame_times: Dict[str, int] = {}
        
    def initialize_character(self, character_name: str, config: Dict) -> None:
        """
        Initialize animation state for a character.
        
        Args:
            character_name: Name of the character
            config: Character configuration with animation settings
        """
        self.animation_states[character_name] = {
            'current_animation': 'idle',
            'frame_count': config.get('total_frames', 1),
            'frames_per_row': config.get('frames_per_row', 1),
            'animation_speed': config.get('animation_speed', 1000),
            'loop': True
        }
        
        self.current_frames[character_name] = 0
        self.last_frame_times[character_name] = self._now_ms()
        
        logger.info(f"✅ Initialized animation for character: {character_name}")
    
    def update_character_animation(self, character_name: str) -> int:
        """
        Update character animation and return current frame.
        
        Args:
            character_name: Name of the character to update
            
        Returns:
            Current frame number (0-based)
        """
        if character_name not in self.animation_states:
            return 0
        
        current_time = self._now_ms()
        state = self.animation_states[character_name]
        last_time = self.last_frame_times[character_name]
        
        # Check if it's time to advance to next frame
        if current_time - last_time >= state['animation_speed']:
            # Advance frame
            self.current_frames[character_name] += 1
            
            # Handle frame wrapping
            if self.current_frames[character_name] >= state['frame_count']:
                if state['loop']:
                    self.current_frames[character_name] = 0
                else:
                    self.current_frames[character_name] = state['frame_count'] - 1
            
            # Update last frame time
            self.last_frame_times[character_name] = current_time
        
        return self.current_frames[character_name]
    
    def set_character_animation(self, character_name: str, animation_name: str, 
                               config: Optional[Dict] = None) -> bool:
        """
        Set a character's current animation.
        
        Args:
            character_name: Name of the character
            animation_name: Name of the animation to set
            config: Optional animation configuration
            
        Returns:
            True if animation was set successfully
        """
        if character_name not in self.animation_states:
            logger.warning(f"⚠️ Character not initialized: {character_name}")
            return False
        
        # Update animation state
        self.animation_states[character_name]['current_animation'] = animation_name
        
        # Reset frame counter
        self.current_frames[character_name] = 0
        self.last_frame_times[character_name] = self._now_ms()
        
        # Update config if provided
        if config:
            self.animation_states[character_name].update(config)
        
        logger.info(f"✅ Set animation '{animation_name}' for character: {character_name}")
        return True
    
    def get_character_frame(self, character_name: str) -> int:
        """Get current frame for a character."""
        return self.current_frames.get(character_name, 0)
    
    def get_character_animation_state(self, character_name: str) -> Optional[Dict]:
        """Get animation state for a character."""
        return self.animation_states.get(character_name)
    
    def reset_character_animation(self, character_name: str) -> None:
        """Reset animation state for a character."""
        if character_name in self.animation_states:
            self.current_frames[character_name] = 0
            self.last_frame_times[character_name] = self._now_ms()
            logger.info(f"🔄 Reset animation for character: {character_name}")
    
    def pause_character_animation(self, character_name: str) -> None:
        """Pause animation for a character."""
        if character_name in self.animation_states:
            self.animation_states[character_name]['paused'] = True
            logger.info(f"⏸️ Paused animation for character: {character_name}")
    
    def resume_character_animation(self, character_name: str) -> None:
        """Resume animation for a character."""
        if character_name in self.animation_states:
            self.animation_states[character_name]['paused'] = False
            self.last_frame_times[character_name] = self._now_ms()
            logger.info(f"▶️ Resumed animation for character: {character_name}")
    
    def _now_ms(self) -> int:
        """Get current time in milliseconds."""
        if hasattr(self.clock, 'now_ms'):
            return self.clock.now_ms()
        return pygame.time.get_ticks()
