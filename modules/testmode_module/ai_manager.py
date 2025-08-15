"""
AI Manager - Handles enemy AI configuration and updates
Extracted from TestMode to manage AI difficulty and behavior.
"""

from typing import Optional
from modules.ai_module import EnemyAIConfig, HeuristicAI, config_for_difficulty

class AIManager:
    """
    Manages enemy AI configuration, difficulty settings, and updates.
    Handles AI difficulty changes and provides AI update functionality.
    """
    
    def __init__(self, initial_difficulty: int = 10):
        """Initialize the AI manager with default difficulty."""
        self.ai_difficulty: int = initial_difficulty
        self.enemy_ai = HeuristicAI(config_for_difficulty(self.ai_difficulty))
        
    def set_difficulty(self, difficulty: int):
        """Set the AI difficulty level (1-10)."""
        self.ai_difficulty = max(1, min(10, difficulty))
        self.enemy_ai.config = config_for_difficulty(self.ai_difficulty)
        
    def adjust_difficulty(self, delta: int):
        """Adjust the AI difficulty by a delta value."""
        new_difficulty = self.ai_difficulty + delta
        self.set_difficulty(new_difficulty)
        
    def get_difficulty(self) -> int:
        """Get the current AI difficulty level."""
        return self.ai_difficulty
        
    def get_ai(self) -> HeuristicAI:
        """Get the enemy AI instance."""
        return self.enemy_ai
        
    def update_ai(self, enemy_engine, current_time: int):
        """Update the enemy AI if it exists and the game is active."""
        if self.enemy_ai and enemy_engine.game_active:
            self.enemy_ai.update(enemy_engine, current_time)
            
    def disable_ai(self):
        """Disable the enemy AI by setting it to None."""
        self.enemy_ai = None
        
    def enable_ai(self, difficulty: Optional[int] = None):
        """Enable the enemy AI with optional difficulty setting."""
        if difficulty is not None:
            self.set_difficulty(difficulty)
        else:
            self.enemy_ai = HeuristicAI(config_for_difficulty(self.ai_difficulty)) 