"""
Render Coordinator - Handles visual state coordination and attack indicators
Extracted from TestMode to manage rendering coordination.
"""

import pygame
from typing import Dict, List, Optional, Any

class RenderCoordinator:
    """
    Manages visual state coordination and attack indicators.
    Handles rendering coordination between boards and attack visualization.
    """
    
    def __init__(self, screen: pygame.Surface, board_manager):
        """Initialize the render coordinator."""
        self.screen = screen
        self.board_manager = board_manager
        
        # Garbage block tracking
        self.garbage_block_brightness = {}
        
        # Attack indicators
        self.pending_attacks = {'player': [], 'enemy': []}
        self.attack_spawn_delay = 3000  # 3 seconds
        
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
        """Reset garbage block brightness state."""
        self.garbage_block_brightness = {}
        
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