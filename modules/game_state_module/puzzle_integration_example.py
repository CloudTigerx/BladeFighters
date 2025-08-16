"""
Puzzle Engine Integration Example
Shows how to integrate the puzzle state integration with the existing puzzle module.
This is a practical example that can be used as a reference for the actual integration.
"""

import pygame
from typing import Optional

from .puzzle_integration import PuzzleStateIntegrator
from .state_schema import PuzzleState


class PuzzleEngineWithStateIntegration:
    """
    Example of how to integrate state management with the existing puzzle engine.
    This shows the key changes needed to migrate from scattered state variables
    to unified state management.
    """
    
    def __init__(self, screen, font, audio=None, asset_path="puzzleassets", 
                 settings_system=None, state_manager=None):
        """
        Initialize puzzle engine with state integration.
        
        Args:
            screen: Pygame display surface
            font: Pygame font for text rendering
            audio: Audio system for sound effects (optional)
            asset_path: Path to puzzle assets directory
            settings_system: Settings system for custom controls (optional)
            state_manager: GameStateManager instance (optional)
        """
        self.screen = screen
        self.font = font
        self.audio = audio
        self.asset_path = asset_path
        self.settings_system = settings_system
        
        # Get screen dimensions
        self.width = screen.get_width()
        self.height = screen.get_height()
        
        # Grid dimensions
        self.grid_width = 6
        self.grid_height = 15
        self.total_grid_height = 16
        
        # Calculate block size based on screen dimensions
        max_block_height = (self.height - 100) // self.grid_height
        max_block_width = (self.width - 200) // self.grid_width
        self.block_size = min(max_block_height, max_block_width, 65)
        self.block_size = max(self.block_size, 30)
        
        # Initialize state integration if state manager is provided
        self.state_integrator = None
        if state_manager:
            self.state_integrator = PuzzleStateIntegrator(state_manager, self)
            self.state_integrator.start_integration()
            self.state_integrator.register_state_callbacks()
            print("🎯 Puzzle state integration initialized")
        
        # Initialize puzzle grid
        self.puzzle_grid = self.create_empty_grid(self.grid_width, self.total_grid_height)
        
        # Piece state (these will be synced with state manager)
        self.main_piece = None
        self.attached_piece = None
        self.piece_position = [0, 0]
        self.attached_position = 0
        
        # Sub-grid positioning
        self.sub_grid_positions = 20
        self.current_sub_position = 0
        
        # Timing state
        self.normal_fall_speed = 640000
        self.accelerated_fall_speed = 2400
        self.current_fall_speed = self.normal_fall_speed
        self.last_fall_time = 0
        self.micro_fall_time = self._calculate_micro_fall_time(self.current_fall_speed)
        
        # Wall kick state
        self.last_wall_kick_time = 0
        self.wall_kick_cooldown = 500
        self.wall_kick_count = 0
        self.max_wall_kicks = 2
        
        # Flip cooldown
        self.last_flip_time = 0
        self.flip_cooldown = 50
        
        # Piece generation
        self.next_main_piece = None
        self.next_attached_piece = None
        self.piece_types = ['red', 'blue', 'green', 'yellow', 
                           'red_breaker', 'blue_breaker', 'green_breaker', 'yellow_breaker']
        
        # Game mechanics state
        self.clusters = set()
        self.breaking_blocks = []
        self.breaking_animation_start = 0
        self.breaking_animation_duration = 160
        
        # Chain reaction state machine
        self.chain_reaction_in_progress = False
        self.chain_state = "idle"
        self.last_state_change = 0
        self.state_delay = 0.35
        self.chain_count = 0
        
        # Debug state
        self.debug_breaks = True
        self.enable_debug_logs = False
        
        # Game state (will be managed by state integrator)
        self.game_active = False
        
        # Initialize other components
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize other puzzle engine components."""
        # This would include asset loading, physics, input handling, etc.
        # For this example, we'll keep it simple
        pass
    
    def _calculate_micro_fall_time(self, fall_speed):
        """Calculate micro fall time based on fall speed."""
        return fall_speed / 1000000  # Convert to seconds
    
    def create_empty_grid(self, width, height):
        """Create an empty grid with None values."""
        return [[None for _ in range(width)] for _ in range(height)]
    
    def start_game(self):
        """Start a new puzzle game with state integration."""
        print(f"🔄 Starting new game for engine...")
        
        # Use state integrator if available, otherwise fall back to direct assignment
        if self.state_integrator:
            self.state_integrator.set_game_active(True)
            self.state_integrator.reset_game_state()
            self.state_integrator.update_puzzle_state(PuzzleState.ACTIVE)
        else:
            self.game_active = True
        
        # Reset grid
        self.puzzle_grid = self.create_empty_grid(self.grid_width, self.total_grid_height)
        
        # Reset game mechanics state
        self.clusters = set()
        self.breaking_blocks = []
        self.chain_reaction_in_progress = False
        self.chain_state = "idle"
        self.chain_count = 0
        self.last_state_change = 0
        
        # Generate new piece
        self.generate_new_piece()
        print(f"✅ New game started successfully")
    
    def generate_new_piece(self):
        """Generate a new piece for the game."""
        import random
        
        # Generate main piece
        self.main_piece = random.choice(self.piece_types)
        
        # Generate attached piece
        self.attached_piece = random.choice(self.piece_types)
        
        # Set initial position
        self.piece_position = [self.grid_width // 2, -1]
        self.attached_position = 0
        self.current_sub_position = 0
        
        # Update state manager if available
        if self.state_integrator:
            self.state_integrator.sync_to_state_manager()
    
    def update(self):
        """Main game update loop with state integration."""
        # Sync state to state manager if integration is active
        if self.state_integrator:
            self.state_integrator.sync_to_state_manager()
        
        # Check if game is active
        if not self._is_game_active():
            return
        
        # Update falling piece
        self.update_falling_piece()
        
        # Update chain reactions
        if self.chain_reaction_in_progress:
            self.update_chain_reaction()
        
        # Sync any changes back from state manager if needed
        if self.state_integrator:
            self.state_integrator.sync_from_state_manager()
    
    def _is_game_active(self):
        """Check if game is active using state integrator or direct access."""
        if self.state_integrator:
            return self.state_integrator.is_game_active()
        return self.game_active
    
    def update_falling_piece(self):
        """Update the position of the falling piece."""
        if not self.main_piece:
            self.generate_new_piece()
            return
        
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.last_fall_time
        
        if elapsed > self.micro_fall_time:
            # Move piece down
            if self.can_move_down():
                self.piece_position[1] += 1
                self.last_fall_time = current_time
            else:
                # Place piece on grid
                self.place_piece_on_grid()
    
    def can_move_down(self):
        """Check if the piece can move down."""
        # Simplified collision detection
        new_y = self.piece_position[1] + 1
        return new_y < self.grid_height and self.puzzle_grid[new_y][self.piece_position[0]] is None
    
    def place_piece_on_grid(self):
        """Place the current piece on the grid."""
        x, y = self.piece_position
        
        if 0 <= y < self.total_grid_height and 0 <= x < self.grid_width:
            self.puzzle_grid[y][x] = self.main_piece
        
        # Clear current piece
        self.main_piece = None
        self.attached_piece = None
        
        # Check for clusters
        self.check_for_clusters()
    
    def check_for_clusters(self):
        """Check for clusters and handle them."""
        # Simplified cluster detection
        new_clusters = self.find_clusters()
        
        if new_clusters:
            self.break_clusters(new_clusters)
        else:
            # Generate new piece
            self.generate_new_piece()
    
    def find_clusters(self):
        """Find clusters in the grid."""
        # Simplified cluster finding - just return empty for this example
        return set()
    
    def break_clusters(self, clusters):
        """Break clusters and award points."""
        points = len(clusters) * 100
        
        # Update score through state integrator if available
        if self.state_integrator:
            self.state_integrator.add_score(points)
            self.state_integrator.set_clusters(clusters)
            self.state_integrator.update_puzzle_state(PuzzleState.BREAKING)
        else:
            # Fallback to direct assignment
            if not hasattr(self, 'score'):
                self.score = 0
            self.score += points
            self.clusters = clusters
        
        print(f"🎯 Broke {len(clusters)} clusters: +{points} points")
        
        # Start chain reaction
        self.start_chain_reaction()
    
    def start_chain_reaction(self):
        """Start a chain reaction."""
        self.chain_reaction_in_progress = True
        self.chain_state = "breaking"
        
        # Update state through integrator if available
        if self.state_integrator:
            self.state_integrator.update_puzzle_state(PuzzleState.CHAIN_REACTION)
            current_count = self.state_integrator.state_manager.get("puzzle.chain_count", 0)
            self.state_integrator.state_manager.set("puzzle.chain_count", current_count + 1)
        else:
            self.chain_count += 1
        
        print(f"🔥 Chain reaction started! Count: {self.chain_count}")
    
    def update_chain_reaction(self):
        """Update chain reaction state machine."""
        current_time = pygame.time.get_ticks()
        
        if self.chain_state == "breaking":
            # Simulate breaking animation
            if current_time - self.last_state_change > self.state_delay * 1000:
                self.chain_state = "waiting_for_gravity"
                self.last_state_change = current_time
        
        elif self.chain_state == "waiting_for_gravity":
            # Simulate gravity application
            if current_time - self.last_state_change > self.state_delay * 1000:
                self.chain_state = "idle"
                self.chain_reaction_in_progress = False
                self.last_state_change = current_time
                
                # Update state through integrator if available
                if self.state_integrator:
                    self.state_integrator.update_puzzle_state(PuzzleState.ACTIVE)
    
    def handle_game_over(self):
        """Handle game over state."""
        if self.state_integrator:
            self.state_integrator.set_game_active(False)
            self.state_integrator.update_puzzle_state(PuzzleState.GAME_OVER)
        else:
            self.game_active = False
        
        print("💀 Game Over!")
    
    def get_game_status(self):
        """Get current game status."""
        if self.state_integrator:
            return self.state_integrator.get_state_summary()
        else:
            # Fallback status without state manager
            return {
                "game_active": self.game_active,
                "score": getattr(self, 'score', 0),
                "clusters": len(self.clusters),
                "chain_reaction": self.chain_reaction_in_progress,
                "chain_count": self.chain_count,
                "level": getattr(self, 'level', 1),
                "lines_cleared": getattr(self, 'lines_cleared', 0),
            }
    
    def process_events(self, events):
        """Process game events."""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "back_to_menu"
                elif event.key == pygame.K_SPACE:
                    # Quick drop piece
                    while self.can_move_down():
                        self.piece_position[1] += 1
                    self.place_piece_on_grid()
                elif event.key == pygame.K_LEFT:
                    # Move left
                    if self.piece_position[0] > 0:
                        self.piece_position[0] -= 1
                elif event.key == pygame.K_RIGHT:
                    # Move right
                    if self.piece_position[0] < self.grid_width - 1:
                        self.piece_position[0] += 1
                elif event.key == pygame.K_DOWN:
                    # Soft drop
                    self.current_fall_speed = self.accelerated_fall_speed
                    self.micro_fall_time = self._calculate_micro_fall_time(self.current_fall_speed)
            
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    # Return to normal fall speed
                    self.current_fall_speed = self.normal_fall_speed
                    self.micro_fall_time = self._calculate_micro_fall_time(self.current_fall_speed)
        
        return None
    
    def draw(self):
        """Draw the puzzle game."""
        # Clear screen
        self.screen.fill((0, 0, 0))
        
        # Draw grid
        self.draw_grid()
        
        # Draw current piece
        if self.main_piece:
            self.draw_piece()
        
        # Draw UI
        self.draw_ui()
    
    def draw_grid(self):
        """Draw the puzzle grid."""
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                if self.puzzle_grid[y][x]:
                    # Draw block
                    rect = pygame.Rect(
                        x * self.block_size,
                        y * self.block_size,
                        self.block_size,
                        self.block_size
                    )
                    pygame.draw.rect(self.screen, (255, 255, 255), rect)
                    pygame.draw.rect(self.screen, (100, 100, 100), rect, 1)
    
    def draw_piece(self):
        """Draw the current falling piece."""
        x, y = self.piece_position
        rect = pygame.Rect(
            x * self.block_size,
            y * self.block_size,
            self.block_size,
            self.block_size
        )
        pygame.draw.rect(self.screen, (255, 0, 0), rect)
        pygame.draw.rect(self.screen, (200, 0, 0), rect, 2)
    
    def draw_ui(self):
        """Draw game UI."""
        # Draw score
        score_text = self.font.render(f"Score: {self.get_score()}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))
        
        # Draw game status
        status = self.get_game_status()
        status_text = self.font.render(f"Game Active: {status['game_active']}", True, (255, 255, 255))
        self.screen.blit(status_text, (10, 30))
        
        # Draw chain count
        chain_text = self.font.render(f"Chain: {status['chain_count']}", True, (255, 255, 255))
        self.screen.blit(chain_text, (10, 50))
    
    def get_score(self):
        """Get current score."""
        if self.state_integrator:
            return self.state_integrator.get_score()
        return getattr(self, 'score', 0)


# Example usage
def create_puzzle_engine_with_state_integration(screen, font, state_manager):
    """
    Example function showing how to create a puzzle engine with state integration.
    
    Args:
        screen: Pygame display surface
        font: Pygame font
        state_manager: GameStateManager instance
    
    Returns:
        PuzzleEngineWithStateIntegration instance
    """
    return PuzzleEngineWithStateIntegration(
        screen=screen,
        font=font,
        asset_path="puzzleassets",
        state_manager=state_manager
    )


# Example of how to use the integrated puzzle engine
def example_usage():
    """Example of how to use the puzzle engine with state integration."""
    import pygame
    
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    font = pygame.font.Font(None, 36)
    
    # Create state manager
    from .game_state_manager import GameStateManager
    state_manager = GameStateManager()
    
    # Create puzzle engine with state integration
    puzzle_engine = create_puzzle_engine_with_state_integration(screen, font, state_manager)
    
    # Start game
    puzzle_engine.start_game()
    
    # Game loop
    running = True
    clock = pygame.time.Clock()
    
    while running:
        events = pygame.event.get()
        
        for event in events:
            if event.type == pygame.QUIT:
                running = False
        
        # Process events
        action = puzzle_engine.process_events(events)
        if action == "back_to_menu":
            running = False
        
        # Update game
        puzzle_engine.update()
        
        # Draw game
        puzzle_engine.draw()
        
        # Update display
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()


if __name__ == "__main__":
    # Run the example
    example_usage() 