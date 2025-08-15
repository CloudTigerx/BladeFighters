"""
Game State Manager
Main interface for unified game state management with performance optimization.
"""

from typing import Dict, Any, Optional, List, Callable, Union
import time
from dataclasses import dataclass, field
import copy

from .state_schema import GameState, ScreenType, GameMode, PuzzleState
from .state_validator import StateValidator, ValidationError
from .state_history import StateHistory, StateSnapshot, StateChange
from .performance_profiler import get_performance_profiler, PerformanceProfiler
from .state_cache import StateCacheManager
from .state_batcher import StateBatchingManager
from modules.logging_module.logger import get_logger


@dataclass
class StateChangeCallback:
    """Represents a callback for state changes."""
    field_path: str
    callback: Callable[[str, Any, Any], None]
    description: str = ""


class GameStateManager:
    """
    Unified game state manager.
    Provides centralized state management with validation, history, and callbacks.
    """
    
    def __init__(self, initial_state: Optional[GameState] = None, enable_performance_optimization: bool = True):
        """Initialize the game state manager."""
        self.logger = get_logger(__name__)
        
        # Initialize state
        self._state = initial_state or GameState()
        self._previous_state = copy.deepcopy(self._state)
        
        # Initialize subsystems
        self.validator = StateValidator()
        self.history = StateHistory()
        
        # Initialize callbacks BEFORE performance optimization systems
        self._change_callbacks: List[StateChangeCallback] = []
        self._global_callbacks: List[Callable[[GameState, GameState], None]] = []
        
        # Performance optimization systems
        self.performance_optimization_enabled = enable_performance_optimization
        if enable_performance_optimization:
            self.profiler = get_performance_profiler()
            self.cache_manager = StateCacheManager(self)
            self.batching_manager = StateBatchingManager(self)
            
            # Set global instances
            from .state_cache import set_global_cache_manager
            from .state_batcher import set_global_batching_manager
            set_global_cache_manager(self.cache_manager)
            set_global_batching_manager(self.batching_manager)
        else:
            self.profiler = None
            self.cache_manager = None
            self.batching_manager = None
        
        # Performance tracking
        self._change_count = 0
        self._last_snapshot_time = time.time()
        self._snapshot_interval = 5.0  # Create snapshots every 5 seconds
        
        # Setup history callbacks
        self.history.on_snapshot_created = self._on_snapshot_created
        self.history.on_change_recorded = self._on_change_recorded
        
        # Create initial snapshot
        self.history.create_snapshot(self._state, "Initial state", ["initial"])
        
        self.logger.info("GameStateManager initialized with performance optimization: {enable_performance_optimization}")
    
    @property
    def state(self) -> GameState:
        """Get the current game state."""
        return self._state
    
    def get(self, field_path: str, default: Any = None) -> Any:
        """Get a value from the state using dot notation."""
        return self._get_nested_value(self._state, field_path, default)
    
    def set(self, field_path: str, value: Any, source: str = "unknown", 
            description: str = "", validate: bool = True) -> bool:
        """
        Set a value in the state.
        
        Args:
            field_path: Dot notation path to the field
            value: New value
            source: Source of the change
            description: Description of the change
            validate: Whether to validate the change
            
        Returns:
            True if the change was successful, False otherwise
        """
        try:
            # Start performance profiling
            if self.profiler:
                self.profiler.start_operation(f"state_set_{field_path}")
            
            # Get current value
            old_value = self.get(field_path)
            
            # Validate the change
            if validate:
                errors = self.validator.validate_state_change(self._state, field_path, value)
                if errors:
                    for error in errors:
                        self.logger.warning(f"State validation error: {error.message}")
                    return False
            
            # Apply the change
            self._set_nested_value(self._state, field_path, value)
            
            # Record the change
            self.history.record_change(field_path, old_value, value, description, source)
            
            # Notify callbacks
            self._notify_callbacks(field_path, old_value, value)
            
            # Update change count
            self._change_count += 1
            
            # Create periodic snapshots
            current_time = time.time()
            if current_time - self._last_snapshot_time >= self._snapshot_interval:
                self.history.create_snapshot(self._state, f"Periodic snapshot ({self._change_count} changes)")
                self._last_snapshot_time = current_time
                self._change_count = 0
            
            # End performance profiling
            if self.profiler:
                self.profiler.end_operation(f"state_set_{field_path}")
                self.profiler.record_state_change(field_path, 0.0)  # Duration will be calculated by profiler
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting state field {field_path}: {e}")
            return False
    
    def update(self, updates: Dict[str, Any], source: str = "unknown", 
               description: str = "", validate: bool = True) -> Dict[str, bool]:
        """
        Update multiple state fields at once.
        
        Args:
            updates: Dictionary of field_path -> value mappings
            source: Source of the changes
            description: Description of the changes
            validate: Whether to validate the changes
            
        Returns:
            Dictionary of field_path -> success status
        """
        results = {}
        
        for field_path, value in updates.items():
            results[field_path] = self.set(field_path, value, source, description, validate)
        
        return results
    
    def snapshot(self, description: str = "", tags: List[str] = None, 
                metadata: Dict[str, Any] = None) -> StateSnapshot:
        """Create a state snapshot."""
        return self.history.create_snapshot(self._state, description, tags, metadata)
    
    def rollback_to_snapshot(self, snapshot: StateSnapshot) -> bool:
        """Rollback to a specific snapshot."""
        try:
            self._previous_state = copy.deepcopy(self._state)
            self._state = copy.deepcopy(snapshot.state)
            
            self.logger.info(f"Rolled back to snapshot: {snapshot.description}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error rolling back to snapshot: {e}")
            return False
    
    def rollback_to_timestamp(self, timestamp: float) -> bool:
        """Rollback to the state at a specific timestamp."""
        try:
            rolled_back_state = self.history.rollback_to_timestamp(timestamp)
            if rolled_back_state:
                self._previous_state = copy.deepcopy(self._state)
                self._state = rolled_back_state
                
                self.logger.info(f"Rolled back to timestamp: {timestamp}")
                return True
            else:
                self.logger.warning(f"No snapshot found for timestamp: {timestamp}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error rolling back to timestamp: {e}")
            return False
    
    def add_change_callback(self, field_path: str, callback: Callable[[str, Any, Any], None], 
                           description: str = "") -> None:
        """Add a callback for state changes on a specific field."""
        change_callback = StateChangeCallback(field_path, callback, description)
        self._change_callbacks.append(change_callback)
    
    def add_global_callback(self, callback: Callable[[GameState, GameState], None]) -> None:
        """Add a global callback for any state change."""
        self._global_callbacks.append(callback)
    
    def remove_change_callback(self, field_path: str, callback: Callable[[str, Any, Any], None]) -> bool:
        """Remove a specific change callback."""
        for i, change_callback in enumerate(self._change_callbacks):
            if (change_callback.field_path == field_path and 
                change_callback.callback == callback):
                self._change_callbacks.pop(i)
                return True
        return False
    
    def remove_global_callback(self, callback: Callable[[GameState, GameState], None]) -> bool:
        """Remove a global callback."""
        try:
            self._global_callbacks.remove(callback)
            return True
        except ValueError:
            return False
    
    def get_state_summary(self) -> Dict[str, Any]:
        """Get a summary of the current state."""
        # Use cached version if available
        if self.cache_manager:
            cached_summary = self.cache_manager.get_computed("game_state_summary")
            if cached_summary:
                return cached_summary
        
        # Fallback to direct access
        summary = {
            'current_screen': self._state.screen.current_screen.value,
            'game_running': self._state.game_running,
            'game_active': self._state.puzzle.game_active,
            'game_mode': self._state.puzzle.game_mode.value,
            'score': self._state.puzzle.score,
            'level': self._state.puzzle.level,
            'master_volume': self._state.audio.master_volume,
            'ui_scale': self._state.ui.ui_scale,
            'fps': self._state.fps,
            'initialized': self._state.initialized,
            'loading_complete': self._state.loading_complete,
            'error_state': self._state.error_state
        }
        
        # Cache the result
        if self.cache_manager:
            self.cache_manager.set_cached("game_state_summary", summary, ttl=1.0)
        
        return summary
    
    def get_history_summary(self) -> Dict[str, Any]:
        """Get a summary of the state history."""
        return self.history.get_state_summary()
    
    def validate_state(self) -> List[ValidationError]:
        """Validate the current state."""
        return self.validator.validate_full_state(self._state)
    
    def is_state_valid(self) -> bool:
        """Check if the current state is valid."""
        return self.validator.is_valid_state(self._state)
    
    def export_state(self) -> Dict[str, Any]:
        """Export the current state for debugging."""
        export_data = {
            'state_summary': self.get_state_summary(),
            'history_summary': self.get_history_summary(),
            'validation_errors': [str(error) for error in self.validate_state()],
            'change_callbacks': len(self._change_callbacks),
            'global_callbacks': len(self._global_callbacks)
        }
        
        # Add performance data if available
        if self.profiler:
            export_data['performance_summary'] = self.profiler.get_performance_summary()
            export_data['optimization_recommendations'] = self.profiler.get_optimization_recommendations()
        
        if self.cache_manager:
            export_data['cache_stats'] = self.cache_manager.get_cache_stats()
        
        if self.batching_manager:
            export_data['batching_stats'] = self.batching_manager.get_batching_stats()
        
        return export_data
    
    def _get_nested_value(self, obj: Any, field_path: str, default: Any = None) -> Any:
        """Get a nested value from an object using dot notation."""
        parts = field_path.split('.')
        current = obj
        
        for part in parts:
            if hasattr(current, part):
                current = getattr(current, part)
            else:
                return default
        
        return current
    
    def _set_nested_value(self, obj: Any, field_path: str, value: Any) -> None:
        """Set a nested value in an object using dot notation."""
        parts = field_path.split('.')
        current = obj
        
        # Navigate to the parent of the target field
        for part in parts[:-1]:
            if hasattr(current, part):
                current = getattr(current, part)
            else:
                raise AttributeError(f"Field path {field_path} is invalid")
        
        # Set the value on the target field
        setattr(current, parts[-1], value)
    
    def _notify_callbacks(self, field_path: str, old_value: Any, new_value: Any) -> None:
        """Notify all relevant callbacks of a state change."""
        # Notify field-specific callbacks
        for callback_info in self._change_callbacks:
            if callback_info.field_path == field_path:
                try:
                    callback_info.callback(field_path, old_value, new_value)
                except Exception as e:
                    self.logger.error(f"Error in change callback: {e}")
        
        # Notify global callbacks
        for callback in self._global_callbacks:
            try:
                callback(self._previous_state, self._state)
            except Exception as e:
                self.logger.error(f"Error in global callback: {e}")
    
    def _on_snapshot_created(self, snapshot: StateSnapshot) -> None:
        """Called when a snapshot is created."""
        self.logger.debug(f"Snapshot created: {snapshot.description}")
    
    def _on_change_recorded(self, change: StateChange) -> None:
        """Called when a change is recorded."""
        self.logger.debug(f"State change: {change.field_path} = {change.new_value} (from {change.source})")
    
    def record_frame(self) -> None:
        """Record frame-level performance metrics."""
        if self.profiler:
            self.profiler.record_frame()
    
    def optimize_state_management(self) -> Dict[str, Any]:
        """Apply automatic optimizations to state management."""
        if not self.profiler:
            return {}
        
        optimizations = self.profiler.optimize_state_management(self)
        
        # Apply batching optimizations
        if self.batching_manager:
            # Apply any pending batches
            applied_batches = self.batching_manager.apply_all_pending()
            if applied_batches > 0:
                optimizations['applied_batches'] = f"Applied {applied_batches} pending batches"
        
        return optimizations
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get a comprehensive performance report."""
        report = {
            'performance_optimization_enabled': self.performance_optimization_enabled
        }
        
        if self.profiler:
            report['profiler'] = self.profiler.get_performance_summary()
            report['recommendations'] = self.profiler.get_optimization_recommendations()
        
        if self.cache_manager:
            report['cache'] = self.cache_manager.get_cache_stats()
        
        if self.batching_manager:
            report['batching'] = self.batching_manager.get_batching_stats()
        
        return report


# Convenience functions for common state operations
def create_game_state_manager() -> GameStateManager:
    """Create a new game state manager with default state."""
    return GameStateManager()


def get_game_state_manager() -> Optional[GameStateManager]:
    """Get the global game state manager instance."""
    return getattr(GameStateManager, '_global_instance', None)


def set_global_game_state_manager(manager: GameStateManager) -> None:
    """Set the global game state manager instance."""
    GameStateManager._global_instance = manager 