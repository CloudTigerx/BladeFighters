"""
State History Management
Tracks state changes and enables rollback functionality.
"""

from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
import time
import copy
from .state_schema import GameState


@dataclass
class StateSnapshot:
    """Represents a snapshot of the game state at a point in time."""
    timestamp: float
    state: GameState
    description: str
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StateChange:
    """Represents a single state change."""
    timestamp: float
    field_path: str
    old_value: Any
    new_value: Any
    description: str
    source: str  # Which system made the change


class StateHistory:
    """Manages state history and provides rollback functionality."""
    
    def __init__(self, max_snapshots: int = 100, max_changes: int = 1000):
        self.max_snapshots = max_snapshots
        self.max_changes = max_changes
        
        # History storage
        self.snapshots: List[StateSnapshot] = []
        self.changes: List[StateChange] = []
        
        # Callbacks
        self.on_snapshot_created: Optional[Callable[[StateSnapshot], None]] = None
        self.on_change_recorded: Optional[Callable[[StateChange], None]] = None
    
    def create_snapshot(self, state: GameState, description: str = "", 
                       tags: List[str] = None, metadata: Dict[str, Any] = None) -> StateSnapshot:
        """Create a new state snapshot."""
        snapshot = StateSnapshot(
            timestamp=time.time(),
            state=copy.deepcopy(state),
            description=description,
            tags=tags or [],
            metadata=metadata or {}
        )
        
        self.snapshots.append(snapshot)
        
        # Maintain max snapshots
        if len(self.snapshots) > self.max_snapshots:
            self.snapshots.pop(0)
        
        # Notify callback
        if self.on_snapshot_created:
            self.on_snapshot_created(snapshot)
        
        return snapshot
    
    def record_change(self, field_path: str, old_value: Any, new_value: Any, 
                     description: str = "", source: str = "unknown") -> StateChange:
        """Record a state change."""
        change = StateChange(
            timestamp=time.time(),
            field_path=field_path,
            old_value=old_value,
            new_value=new_value,
            description=description,
            source=source
        )
        
        self.changes.append(change)
        
        # Maintain max changes
        if len(self.changes) > self.max_changes:
            self.changes.pop(0)
        
        # Notify callback
        if self.on_change_recorded:
            self.on_change_recorded(change)
        
        return change
    
    def get_latest_snapshot(self) -> Optional[StateSnapshot]:
        """Get the most recent snapshot."""
        return self.snapshots[-1] if self.snapshots else None
    
    def get_snapshot_by_tag(self, tag: str) -> Optional[StateSnapshot]:
        """Get the most recent snapshot with a specific tag."""
        for snapshot in reversed(self.snapshots):
            if tag in snapshot.tags:
                return snapshot
        return None
    
    def get_snapshot_by_description(self, description: str) -> Optional[StateSnapshot]:
        """Get the most recent snapshot with a specific description."""
        for snapshot in reversed(self.snapshots):
            if description in snapshot.description:
                return snapshot
        return None
    
    def get_changes_since(self, timestamp: float) -> List[StateChange]:
        """Get all changes since a specific timestamp."""
        return [change for change in self.changes if change.timestamp >= timestamp]
    
    def get_changes_for_field(self, field_path: str) -> List[StateChange]:
        """Get all changes for a specific field."""
        return [change for change in self.changes if change.field_path == field_path]
    
    def rollback_to_snapshot(self, snapshot: StateSnapshot) -> GameState:
        """Rollback to a specific snapshot."""
        return copy.deepcopy(snapshot.state)
    
    def rollback_to_timestamp(self, timestamp: float) -> Optional[GameState]:
        """Rollback to the state at a specific timestamp."""
        # Find the snapshot closest to the timestamp
        target_snapshot = None
        min_diff = float('inf')
        
        for snapshot in self.snapshots:
            diff = abs(snapshot.timestamp - timestamp)
            if diff < min_diff:
                min_diff = diff
                target_snapshot = snapshot
        
        if target_snapshot:
            return copy.deepcopy(target_snapshot.state)
        
        return None
    
    def get_state_summary(self) -> Dict[str, Any]:
        """Get a summary of the state history."""
        return {
            'total_snapshots': len(self.snapshots),
            'total_changes': len(self.changes),
            'oldest_snapshot': self.snapshots[0].timestamp if self.snapshots else None,
            'newest_snapshot': self.snapshots[-1].timestamp if self.snapshots else None,
            'oldest_change': self.changes[0].timestamp if self.changes else None,
            'newest_change': self.changes[-1].timestamp if self.changes else None,
            'most_changed_field': self._get_most_changed_field(),
            'change_frequency': self._get_change_frequency()
        }
    
    def _get_most_changed_field(self) -> Optional[str]:
        """Get the field that has been changed most often."""
        field_counts = {}
        for change in self.changes:
            field_counts[change.field_path] = field_counts.get(change.field_path, 0) + 1
        
        if field_counts:
            return max(field_counts, key=field_counts.get)
        return None
    
    def _get_change_frequency(self) -> float:
        """Get the average number of changes per second."""
        if not self.changes:
            return 0.0
        
        time_span = self.changes[-1].timestamp - self.changes[0].timestamp
        if time_span <= 0:
            return 0.0
        
        return len(self.changes) / time_span
    
    def clear_history(self):
        """Clear all history."""
        self.snapshots.clear()
        self.changes.clear()
    
    def export_history(self) -> Dict[str, Any]:
        """Export the history for debugging or analysis."""
        return {
            'snapshots': [
                {
                    'timestamp': s.timestamp,
                    'description': s.description,
                    'tags': s.tags,
                    'metadata': s.metadata
                }
                for s in self.snapshots
            ],
            'changes': [
                {
                    'timestamp': c.timestamp,
                    'field_path': c.field_path,
                    'old_value': str(c.old_value),
                    'new_value': str(c.new_value),
                    'description': c.description,
                    'source': c.source
                }
                for c in self.changes
            ]
        } 