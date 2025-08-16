"""
Board Runtime - Manages board state and input locks
Provides runtime state management for puzzle boards with error handling.
"""

from dataclasses import dataclass
from ..logging_module.error_handler import (
    safe_operation
)
from ..logging_module.logger import get_logger

logger = get_logger(__name__)


@dataclass
class BoardRuntime:
    """
    Manages runtime state for a puzzle board including input and chain locks.
    Provides safe time-based locking with error handling.
    """
    board_id: int
    input_lock_until_ms: int = 0
    chain_lock_until_ms: int = 0

    @safe_operation("check input lock", False, "WARNING")
    def is_input_locked(self, now_ms: int) -> bool:
        """Check if input is currently locked."""
        try:
            return int(now_ms) < int(max(self.input_lock_until_ms, self.chain_lock_until_ms))
        except Exception as e:
            logger.warning(f"Failed to check input lock for board {self.board_id}: {str(e)}")
            return False

    @safe_operation("lock input", None, "WARNING")
    def lock_input(self, ms: int, now_ms: int) -> None:
        """Lock input for a specified duration."""
        try:
            duration = max(0, int(ms))
            self.input_lock_until_ms = max(int(self.input_lock_until_ms), int(now_ms) + duration)
        except Exception as e:
            logger.warning(f"Failed to lock input for board {self.board_id}: {str(e)}")

    @safe_operation("lock chain", None, "WARNING")
    def lock_chain(self, ms: int, now_ms: int) -> None:
        """Lock chain reactions for a specified duration."""
        try:
            duration = max(0, int(ms))
            self.chain_lock_until_ms = max(int(self.chain_lock_until_ms), int(now_ms) + duration)
        except Exception as e:
            logger.warning(f"Failed to lock chain for board {self.board_id}: {str(e)}")

    @safe_operation("clear expired locks", None, "WARNING")
    def clear_expired(self, now_ms: int) -> None:
        """Clear expired input and chain locks."""
        try:
            if int(now_ms) >= int(self.input_lock_until_ms):
                self.input_lock_until_ms = 0
            if int(now_ms) >= int(self.chain_lock_until_ms):
                self.chain_lock_until_ms = 0
        except Exception as e:
            logger.warning(f"Failed to clear expired locks for board {self.board_id}: {str(e)}")

