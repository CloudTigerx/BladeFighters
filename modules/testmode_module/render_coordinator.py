"""
Render Coordinator - Handles visual state coordination and attack indicators
Extracted from TestMode to manage rendering coordination.
"""

import pygame
import logging
from typing import Dict, List, Optional, Any, Tuple

# Set up logging
logger = logging.getLogger(__name__)

# Import transformation system
from core.transformation_events import transformation_manager, EventType

class RenderCoordinator:
    """
    Manages visual state coordination and attack indicators.
    Handles rendering coordination between boards and attack visualization.
    """
    
    def __init__(self, screen: pygame.Surface, board_manager):
        """Initialize the render coordinator."""
        self.screen = screen
        self.board_manager = board_manager
        
        # Garbage block tracking removed - ready for new replacement system
        
        # Attack indicators
        self.pending_attacks = {'player': [], 'enemy': []}
        self.attack_spawn_delay = 3000  # 3 seconds
        
        # Character system
        self.character_sprite_manager = None
        self.character_animation_manager = None
        self._initialize_character_system()
        
        # Initialize transformation event handlers
        self._initialize_transformation_handlers()
        
    def _initialize_character_system(self):
        """Initialize the character sprite and animation systems."""
        try:
            from ..character_module.character_sprite_manager import CharacterSpriteManager
            from ..character_module.character_animation_manager import CharacterAnimationManager
            
            # Get screen dimensions
            screen_width = self.screen.get_width()
            screen_height = self.screen.get_height()
            
            # Initialize character systems
            self.character_sprite_manager = CharacterSpriteManager(
                self.board_manager.asset_path, screen_width, screen_height
            )
            
            self.character_animation_manager = CharacterAnimationManager(
                self.board_manager.clock
            )
            
            # Initialize animations for available characters
            for character_name in self.character_sprite_manager.get_available_characters():
                config = self.character_sprite_manager.get_character_config(character_name)
                if config:
                    self.character_animation_manager.initialize_character(character_name, config)
            
            logger.info("Character system initialized successfully")
            
        except Exception as e:
            logger.warning(f"Character system initialization failed: {e}")
            self.character_sprite_manager = None
            self.character_animation_manager = None
    
    def _initialize_transformation_handlers(self):
        """Initialize transformation event handlers for visual updates."""
        # Register handlers for transformation events
        transformation_manager.register_handler(EventType.TRANSFORMATION_PROGRESS, self._on_transformation_progress)
        transformation_manager.register_handler(EventType.TRANSFORMATION_COMPLETE, self._on_transformation_complete)
        logger.info("Transformation event handlers initialized")
    
    def _on_transformation_progress(self, event):
        """Handle transformation progress events."""
        logger.debug(f"Transformation progress: {event.position} -> {event.stage.name}")
        # Trigger visual update for the affected board
        self.update_renderers()
    
    def _on_transformation_complete(self, event):
        """Handle transformation completion events."""
        logger.debug(f"Transformation complete: {event.position} -> {event.stage.name}")
        # Trigger visual update for the affected board
        self.update_renderers()
        
    def update_renderers(self):
        """Update both renderers."""
        self.board_manager.update_renderers()
        
    def draw_boards(self):
        """Draw both boards with containers and backgrounds."""
        self.board_manager.draw_boards()
        
    def draw_attack_indicators(self):
        """Draw visual indicators for pending attacks above the boards."""
        current_time = self._now_ms()
        
        # Get board positions
        player_pos, enemy_pos = self.board_manager.get_board_positions()
        _, _, board_w, board_h = self.board_manager.get_board_dimensions()
        
        # Draw indicators for player board (enemy attacks)
        if self.pending_attacks['player']:
            self._draw_attack_indicator(player_pos, self.pending_attacks['player'], current_time, board_w)
        
        # Draw indicators for enemy board (player attacks)
        if self.pending_attacks['enemy']:
            self._draw_attack_indicator(enemy_pos, self.pending_attacks['enemy'], current_time, board_w)
    
    def draw_characters(self):
        """Draw character sprites beneath the puzzle boards."""
        if not self.character_sprite_manager or not self.character_animation_manager:
            return
        
        # Get board positions and dimensions
        player_pos, enemy_pos = self.board_manager.get_board_positions()
        board_dimensions = self.board_manager.get_board_dimensions()
        
        # Draw player character (Yuki)
        self._draw_character('yuki', player_pos, board_dimensions)
        
        # Draw enemy character (placeholder for future)
        # self._draw_character('enemy_character', enemy_pos, board_dimensions)
    
    def _draw_character(self, character_name: str, board_position: Dict[str, int], 
                       board_dimensions: Tuple[int, int, int, int]):
        """Draw a character sprite at the calculated position."""
        try:
            # Update character animation and get current frame
            current_frame = 0
            if self.character_animation_manager:
                current_frame = self.character_animation_manager.update_character_animation(character_name)
            
            # Get character sprite for current frame
            sprite = self.character_sprite_manager.get_character_sprite(character_name, 'idle', current_frame)
            if not sprite:
                return
            
            # Calculate character position
            char_x, char_y = self.character_sprite_manager.calculate_character_position(
                board_position, board_dimensions, character_name
            )
            
            # Draw the character sprite
            self.screen.blit(sprite, (char_x, char_y))
            
        except Exception as e:
            logger.warning(f"Error drawing character {character_name}: {e}")
            
    def _draw_attack_indicator(self, board_position: Dict, attacks: List, current_time: int, board_width: int):
        """Draw attack indicators above a specific board."""
        indicator_y = board_position["y"] - 20  # Above the board
        
        for i, attack in enumerate(attacks):
            # Calculate time until spawn
            time_until_spawn = max(0, self.attack_spawn_delay - (current_time - attack['spawn_time']))
            
            if time_until_spawn > 0:
                # Show countdown
                countdown_text = f"Attack in {time_until_spawn // 1000}s"
                color = (255, 255, 0) if time_until_spawn < 1000 else (255, 100, 100)  # Yellow then red
            else:
                # Show falling indicator
                countdown_text = f"Falling: {attack['blocks_remaining']} blocks"
                color = (100, 255, 100)  # Green
            
            # Draw the indicator
            indicator_font = pygame.font.SysFont(None, 16)
            indicator_surface = indicator_font.render(countdown_text, True, color)
            indicator_rect = indicator_surface.get_rect(
                center=(board_position["x"] + board_width // 2, indicator_y + i * 15)
            )
            self.screen.blit(indicator_surface, indicator_rect)
            
    def reset_garbage_block_state(self):
        """Reset garbage block state - transformation system removed."""
        # Garbage block tracking removed - ready for new replacement system
        
    def reconcile_garbage_tracking_with_grid(self, player_engine, enemy_engine):
        """Reconcile tracked strike/garbage with actual grid state to avoid visual desyncs."""
        # This is a safety check to ensure visual consistency
        # Implementation would depend on the specific garbage tracking logic
        pass
        
    def set_pending_attacks(self, player_attacks: List, enemy_attacks: List):
        """Set pending attacks for both boards."""
        self.pending_attacks['player'] = player_attacks
        self.pending_attacks['enemy'] = enemy_attacks
        
    def get_pending_attacks(self) -> Dict[str, List]:
        """Get pending attacks for both boards."""
        return self.pending_attacks.copy()
        
    def _now_ms(self) -> int:
        """Get current time in milliseconds."""
        import pygame
        return pygame.time.get_ticks() 