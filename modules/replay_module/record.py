"""
Input Recorder - Records game input events for replay functionality
Provides event recording with validation and error handling.
"""

from typing import Dict, List, Any, Optional
from ..logging_module.error_handler import (
    safe_operation
)
from ..logging_module.logger import get_logger

logger = get_logger(__name__)


class InputRecorder:
    """
    Records game input events for replay functionality.
    Handles event validation and recording with error handling.
    """

    def __init__(self):
        self._seed: Optional[int] = None
        self._settings: Dict[str, Any] = {}
        self._events: List[Dict[str, Any]] = []
        self._started: bool = False

    def start(self, seed: int, settings: Dict[str, Any]) -> None:
        """Start recording with seed and settings."""
        self._seed = int(seed)
        self._settings = dict(settings or {})
        self._events = []
        self._started = True
        logger.debug(f"Started input recording with seed: {seed}")

    def record(self, event: Dict[str, Any]) -> None:
        """Record an input event with validation."""
        if not self._started:
            return
        
        self._validate_and_record_event(event)

    @safe_operation("validate and record event", None, "WARNING")
    def _validate_and_record_event(self, event: Dict[str, Any]) -> None:
        """Validate and record an input event."""
        try:
            # Normalize expected schema: {t_ms:int, intent:str, data:dict}
            t_ms = int(event.get('t_ms'))
            intent = str(event.get('intent'))
            data = dict(event.get('data') or {})
            if intent:
                self._events.append({'t_ms': t_ms, 'intent': intent, 'data': data})
        except Exception as e:
            logger.warning(f"Failed to record event: {str(e)}")
            # Do not throw in recorder path

    def stop(self) -> Dict[str, Any]:
        """Stop recording and return the recorded data."""
        self._started = False
        result = {
            'seed': int(self._seed if self._seed is not None else 0),
            'settings': dict(self._settings),
            'events': list(self._events),
        }
        logger.debug(f"Stopped input recording with {len(self._events)} events")
        return result

