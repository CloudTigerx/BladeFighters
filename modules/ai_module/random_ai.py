import random
import pygame

from .base import EnemyAIConfig, PuzzleAI
from ..logging_module.error_handler import (
    safe_operation
)
from ..logging_module.logger import get_logger

logger = get_logger(__name__)


class RandomAI:
    """Minimal random-move AI with throttled actions and optional soft-drop."""

    def __init__(self, config: EnemyAIConfig | None = None):
        self.config = config or EnemyAIConfig()
        self._last_action_ms: int = 0

    def update(self, engine, now_ms: int) -> None:
        # Throttle actions
        if now_ms - self._last_action_ms < self.config.action_interval_ms:
            return

        self._last_action_ms = now_ms

        # Occasionally choose a random action
        if random.random() < 0.33:
            self._perform_random_action(engine)

    @safe_operation("perform random action", None, "WARNING")
    def _perform_random_action(self, engine) -> None:
        """Perform a random action with error handling."""
        move_choice = random.random()
        if move_choice < 0.45:
            engine.move_piece(random.choice([-1, 1]), 0)
        elif move_choice < 0.7:
            engine.rotate_attached_piece(random.choice([-1, 1]))
        else:
            if self.config.soft_drop:
                engine.move_piece(0, 1)
