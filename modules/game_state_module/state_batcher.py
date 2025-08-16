"""
State Batching System
Optimizes multiple state changes by batching them together to reduce overhead.
"""

import time
import threading
from typing import Dict, List, Any, Optional, Callable, Tuple, Set
from dataclasses import dataclass, field
from collections import defaultdict, deque
import weakref

from .state_schema import GameState
from modules.logging_module.logger import get_logger


@dataclass
class BatchedChange:
    """Represents a batched state change."""
    field_path: str
    value: Any
    source: str
    description: str
    timestamp: float
    priority: int = 0  # Higher priority changes are applied first


@dataclass
class BatchGroup:
    """Represents a group of related state changes."""
    group_id: str
    changes: List[BatchedChange] = field(default_factory=list)
    created_time: float = field(default_factory=time.time)
    max_wait_time: float = 0.1  # Maximum time to wait before applying batch
    dependencies: Set[str] = field(default_factory=set)
    callback: Optional[Callable[[List[BatchedChange]], None]] = None


class StateBatcher:
    """
    Batches state changes to optimize performance by reducing individual change overhead.
    """
    
    def __init__(self, state_manager, max_batch_size: int = 50, max_wait_time: float = 0.05):
        self.state_manager = state_manager
        self.max_batch_size = max_batch_size
        self.max_wait_time = max_wait_time
        self.logger = get_logger(__name__)
        
        # Batch storage
        self._pending_batches: Dict[str, BatchGroup] = {}
        self._batch_queue: deque = deque()
        self._batch_counter = 0
        
        # Performance tracking
        self._total_batches = 0
        self._total_changes_batched = 0
        self._avg_batch_size = 0.0
        self._batch_times: deque = deque(maxlen=100)
        
        # Threading
        self._lock = threading.RLock()
        self._batch_thread = None
        self._batch_active = False
        
        # Callbacks
        self._batch_callbacks: List[Callable[[List[BatchedChange]], None]] = []
        
        # Start batch processing thread
        self._start_batch_thread()
    
    def add_change(self, field_path: str, value: Any, source: str = "unknown", 
                   description: str = "", group_id: Optional[str] = None, 
                   priority: int = 0, max_wait_time: Optional[float] = None) -> str:
        """
        Add a state change to the batch queue.
        
        Returns:
            The batch ID for tracking
        """
        with self._lock:
            # Generate batch ID if not provided
            if group_id is None:
                group_id = f"batch_{self._batch_counter}"
                self._batch_counter += 1
            
            # Create or get batch group
            if group_id not in self._pending_batches:
                self._pending_batches[group_id] = BatchGroup(
                    group_id=group_id,
                    max_wait_time=max_wait_time or self.max_wait_time
                )
            
            batch_group = self._pending_batches[group_id]
            
            # Add change to batch
            change = BatchedChange(
                field_path=field_path,
                value=value,
                source=source,
                description=description,
                timestamp=time.time(),
                priority=priority
            )
            
            batch_group.changes.append(change)
            
            # Check if batch should be applied immediately
            if len(batch_group.changes) >= self.max_batch_size:
                self._apply_batch(group_id)
            
            return group_id
    
    def add_changes(self, changes: List[Tuple[str, Any]], source: str = "unknown", 
                    group_id: Optional[str] = None, priority: int = 0) -> str:
        """
        Add multiple state changes at once.
        
        Args:
            changes: List of (field_path, value) tuples
            source: Source of the changes
            group_id: Optional batch group ID
            priority: Priority for all changes
            
        Returns:
            The batch ID for tracking
        """
        with self._lock:
            if group_id is None:
                group_id = f"batch_{self._batch_counter}"
                self._batch_counter += 1
            
            for field_path, value in changes:
                self.add_change(field_path, value, source, "", group_id, priority)
            
            return group_id
    
    def set_batch_callback(self, group_id: str, callback: Callable[[List[BatchedChange]], None]) -> bool:
        """Set a callback to be called when a batch is applied."""
        with self._lock:
            if group_id in self._pending_batches:
                self._pending_batches[group_id].callback = callback
                return True
            return False
    
    def apply_batch(self, group_id: str) -> bool:
        """Manually apply a specific batch."""
        with self._lock:
            return self._apply_batch(group_id)
    
    def apply_all_pending(self) -> int:
        """Apply all pending batches."""
        with self._lock:
            applied_count = 0
            group_ids = list(self._pending_batches.keys())
            
            for group_id in group_ids:
                if self._apply_batch(group_id):
                    applied_count += 1
            
            return applied_count
    
    def cancel_batch(self, group_id: str) -> bool:
        """Cancel a pending batch."""
        with self._lock:
            if group_id in self._pending_batches:
                del self._pending_batches[group_id]
                return True
            return False
    
    def get_batch_status(self, group_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific batch."""
        with self._lock:
            if group_id not in self._pending_batches:
                return None
            
            batch = self._pending_batches[group_id]
            return {
                'group_id': group_id,
                'change_count': len(batch.changes),
                'created_time': batch.created_time,
                'age_seconds': time.time() - batch.created_time,
                'max_wait_time': batch.max_wait_time,
                'has_callback': batch.callback is not None
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get batching performance statistics."""
        with self._lock:
            pending_batches = len(self._pending_batches)
            pending_changes = sum(len(batch.changes) for batch in self._pending_batches.values())
            
            avg_batch_time = 0.0
            if self._batch_times:
                avg_batch_time = sum(self._batch_times) / len(self._batch_times)
            
            return {
                'total_batches': self._total_batches,
                'total_changes_batched': self._total_changes_batched,
                'avg_batch_size': self._avg_batch_size,
                'avg_batch_time_ms': avg_batch_time * 1000,
                'pending_batches': pending_batches,
                'pending_changes': pending_changes,
                'max_batch_size': self.max_batch_size,
                'max_wait_time': self.max_wait_time
            }
    
    def _apply_batch(self, group_id: str) -> bool:
        """Apply a specific batch group."""
        if group_id not in self._pending_batches:
            return False
        
        batch_group = self._pending_batches[group_id]
        changes = batch_group.changes
        
        if not changes:
            del self._pending_batches[group_id]
            return False
        
        start_time = time.time()
        
        try:
            # Sort changes by priority (higher priority first)
            changes.sort(key=lambda c: c.priority, reverse=True)
            
            # Apply changes in batch
            results = {}
            for change in changes:
                success = self.state_manager.set(
                    change.field_path,
                    change.value,
                    change.source,
                    change.description,
                    validate=True
                )
                results[change.field_path] = success
            
            # Call batch callback if set
            if batch_group.callback:
                try:
                    batch_group.callback(changes)
                except Exception as e:
                    self.logger.error(f"Error in batch callback: {e}")
            
            # Update statistics
            batch_time = time.time() - start_time
            self._batch_times.append(batch_time)
            self._total_batches += 1
            self._total_changes_batched += len(changes)
            self._avg_batch_size = self._total_changes_batched / self._total_batches
            
            # Remove batch from pending
            del self._pending_batches[group_id]
            
            self.logger.debug(f"Applied batch {group_id}: {len(changes)} changes in {batch_time*1000:.2f}ms")
            return True
            
        except Exception as e:
            self.logger.error(f"Error applying batch {group_id}: {e}")
            return False
    
    def _start_batch_thread(self) -> None:
        """Start background batch processing thread."""
        if self._batch_thread is None or not self._batch_thread.is_alive():
            self._batch_active = True
            self._batch_thread = threading.Thread(target=self._batch_loop, daemon=True)
            self._batch_thread.start()
    
    def _batch_loop(self) -> None:
        """Background batch processing loop."""
        while self._batch_active:
            try:
                time.sleep(0.01)  # Check every 10ms
                
                with self._lock:
                    current_time = time.time()
                    expired_batches = []
                    
                    # Check for expired batches
                    for group_id, batch_group in self._pending_batches.items():
                        if current_time - batch_group.created_time >= batch_group.max_wait_time:
                            expired_batches.append(group_id)
                    
                    # Apply expired batches
                    for group_id in expired_batches:
                        self._apply_batch(group_id)
                
            except Exception as e:
                self.logger.error(f"Error in batch loop: {e}")
    
    def cleanup(self) -> None:
        """Clean up resources."""
        self._batch_active = False
        if self._batch_thread and self._batch_thread.is_alive():
            self._batch_thread.join(timeout=1.0)


class StateBatchingManager:
    """
    High-level batching manager that provides convenient interfaces for common batching patterns.
    """
    
    def __init__(self, state_manager):
        self.state_manager = state_manager
        self.batcher = StateBatcher(state_manager)
        self.logger = get_logger(__name__)
        
        # Common batch patterns
        self._ui_batch_group = None
        self._game_batch_group = None
        self._audio_batch_group = None
    
    def batch_ui_changes(self, changes: List[Tuple[str, Any]], 
                        description: str = "UI update") -> str:
        """Batch UI-related state changes."""
        return self.batcher.add_changes(
            changes, 
            source="ui_system", 
            group_id="ui_batch",
            priority=1
        )
    
    def batch_game_changes(self, changes: List[Tuple[str, Any]], 
                          description: str = "Game update") -> str:
        """Batch game-related state changes."""
        return self.batcher.add_changes(
            changes, 
            source="game_system", 
            group_id="game_batch",
            priority=2
        )
    
    def batch_audio_changes(self, changes: List[Tuple[str, Any]], 
                           description: str = "Audio update") -> str:
        """Batch audio-related state changes."""
        return self.batcher.add_changes(
            changes, 
            source="audio_system", 
            group_id="audio_batch",
            priority=0
        )
    
    def batch_puzzle_updates(self, score: Optional[int] = None, 
                           level: Optional[int] = None,
                           chain_count: Optional[int] = None,
                           game_active: Optional[bool] = None) -> str:
        """Batch common puzzle state updates."""
        changes = []
        
        if score is not None:
            changes.append(("puzzle.score", score))
        if level is not None:
            changes.append(("puzzle.level", level))
        if chain_count is not None:
            changes.append(("puzzle.chain_count", chain_count))
        if game_active is not None:
            changes.append(("puzzle.game_active", game_active))
        
        if changes:
            return self.batcher.add_changes(
                changes,
                source="puzzle_system",
                description="Puzzle state update",
                priority=3
            )
        
        return None
    
    def batch_screen_transition(self, new_screen: str, 
                               cleanup_required: bool = False) -> str:
        """Batch screen transition changes."""
        changes = [
            ("screen.current_screen", new_screen),
            ("screen.screen_transition_time", time.time()),
            ("screen.screen_cleanup_required", cleanup_required)
        ]
        
        return self.batcher.add_changes(
            changes,
            source="screen_system",
            description=f"Screen transition to {new_screen}",
            priority=4
        )
    
    def batch_audio_settings(self, master_volume: Optional[float] = None,
                           music_volume: Optional[float] = None,
                           sfx_volume: Optional[float] = None) -> str:
        """Batch audio setting changes."""
        changes = []
        
        if master_volume is not None:
            changes.append(("audio.master_volume", master_volume))
        if music_volume is not None:
            changes.append(("audio.music_volume", music_volume))
        if sfx_volume is not None:
            changes.append(("audio.sfx_volume", sfx_volume))
        
        if changes:
            return self.batcher.add_changes(
                changes,
                source="settings_system",
                description="Audio settings update",
                priority=1
            )
        
        return None
    
    def apply_all_pending(self) -> int:
        """Apply all pending batches."""
        return self.batcher.apply_all_pending()
    
    def get_batching_stats(self) -> Dict[str, Any]:
        """Get batching performance statistics."""
        return self.batcher.get_stats()


# Global batching manager instance
_global_batching_manager: Optional[StateBatchingManager] = None


def get_state_batching_manager() -> Optional[StateBatchingManager]:
    """Get the global state batching manager instance."""
    return _global_batching_manager


def set_global_batching_manager(batching_manager: StateBatchingManager) -> None:
    """Set the global state batching manager instance."""
    global _global_batching_manager
    _global_batching_manager = batching_manager 