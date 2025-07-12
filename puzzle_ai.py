import random
import time

class PuzzleAI:
    """Base class for puzzle game AI opponents."""
    def __init__(self, engine, difficulty=1, style="fire"):
        self.engine = engine
        self.difficulty = difficulty  # 1-10
        self.style = style  # "water", "fire", "earth", "lightning"
        self.last_action_time = time.time()
        self.action_delay = self._calculate_delay()  # Base delay between actions
        
    def _calculate_delay(self):
        """Calculate delay between actions based on difficulty."""
        # Harder difficulties act faster
        # Difficulty 1: 1.0 second delay
        # Difficulty 10: 0.1 second delay
        return 1.0 - (self.difficulty * 0.09)
        
    def update(self):
        """Update the AI state and make decisions."""
        raise NotImplementedError("Subclasses must implement update()")
        
    def can_act(self):
        """Check if enough time has passed for the AI to act again."""
        current_time = time.time()
        if current_time - self.last_action_time >= self.action_delay:
            self.last_action_time = current_time
            return True
        return False

class WeakAI(PuzzleAI):
    """
    A weak AI that immediately uses breaker blocks and makes simple moves.
    This AI:
    - Uses breaker blocks as soon as they appear
    - Makes random movements
    - Doesn't plan combos
    - Has slower reaction time
    """
    def __init__(self, engine, difficulty=1, style="fire"):
        super().__init__(engine, difficulty, style)
        self.movement_weights = {
            'left': 0.3,    # 30% chance to move left
            'right': 0.3,   # 30% chance to move right
            'rotate': 0.3,  # 30% chance to rotate
            'none': 0.1     # 10% chance to do nothing
        }
        
    def update(self):
        """Update the weak AI's state and make decisions."""
        if not self.can_act():
            return
            
        # If we have a falling piece
        if self.engine.main_piece:
            # Check if either piece is a breaker
            main_is_breaker = '_breaker' in self.engine.main_piece
            attached_is_breaker = '_breaker' in self.engine.attached_piece
            
            if main_is_breaker or attached_is_breaker:
                # Try to place the breaker immediately by accelerating down
                self.engine.current_fall_speed = self.engine.accelerated_fall_speed
                return
                
            # Random movement based on weights
            action = random.choices(
                list(self.movement_weights.keys()),
                list(self.movement_weights.values())
            )[0]
            
            if action == 'left':
                self.engine.move_piece(-1, 0)
            elif action == 'right':
                self.engine.move_piece(1, 0)
            elif action == 'rotate':
                # Random rotation direction
                self.engine.rotate_attached_piece(random.choice([-1, 1]))
            # 'none' action: do nothing
            
            # Occasionally speed up falling
            if random.random() < 0.1:
                self.engine.current_fall_speed = self.engine.accelerated_fall_speed
            else:
                self.engine.current_fall_speed = self.engine.normal_fall_speed 