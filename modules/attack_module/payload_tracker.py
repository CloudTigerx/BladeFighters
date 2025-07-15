"""
Payload Tracker - Advanced Attack Queuing and Delivery System

This module handles sophisticated attack payload tracking, timing, and delivery.
It manages attack states, delivery delays, and transformation stages.

Key Features:
- Advanced attack queuing with priority
- Delivery timing and state management
- Attack transformation stages
- Column rotation and placement logic
- Attack conflict resolution
"""

import time
from typing import List, Dict, Any, Optional, Set, Tuple
from enum import Enum
from dataclasses import dataclass, field
from .data_structures import AttackPayload, GarbageBlockPayload, ClusterStrikePayload, AttackType


class PayloadState(Enum):
    """Enum for payload states during delivery"""
    QUEUED = "queued"
    PENDING = "pending"
    DELIVERING = "delivering"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


@dataclass
class TrackedPayload:
    """Enhanced payload with tracking information"""
    payload: AttackPayload
    state: PayloadState = PayloadState.QUEUED
    creation_time: float = field(default_factory=time.time)
    delivery_time: Optional[float] = None
    priority: int = 0  # Higher priority = delivered first
    attempts: int = 0
    max_attempts: int = 3
    
    def __post_init__(self):
        """Calculate delivery time based on payload delay"""
        if self.delivery_time is None:
            self.delivery_time = self.creation_time + self.payload.delivery_delay


class PayloadTracker:
    """
    Advanced payload tracking and delivery system.
    
    This class provides sophisticated attack queuing with priority management,
    delivery timing, and attack state tracking.
    """
    
    def __init__(self, grid_width: int = 6, grid_height: int = 12):
        """
        Initialize the payload tracker.
        
        Args:
            grid_width: Width of the game grid
            grid_height: Height of the game grid
        """
        self.grid_width = grid_width
        self.grid_height = grid_height
        
        # Payload tracking
        self.tracked_payloads: Dict[int, TrackedPayload] = {}
        self.next_payload_id = 1
        
        # Player queues
        self.player1_queue: List[int] = []  # List of payload IDs
        self.player2_queue: List[int] = []
        
        # Column rotation state
        self.column_rotation = {
            1: 0,  # Player 1 rotation index
            2: 0   # Player 2 rotation index
        }
        
        # Column sequence (1-indexed, converted to 0-indexed)
        self.column_sequence = [1, 6, 2, 5, 3, 4]
        
        # Attack placement tracking
        self.blocked_columns: Dict[int, Set[int]] = {1: set(), 2: set()}
        
        # Statistics
        self.stats = {
            'total_tracked': 0,
            'total_delivered': 0,
            'total_cancelled': 0,
            'average_delivery_time': 0.0,
            'failed_deliveries': 0
        }
        
        print("📦 PayloadTracker initialized")
    
    def add_payload(self, payload: AttackPayload, priority: int = 0) -> int:
        """
        Add a payload to the tracking system.
        
        Args:
            payload: The attack payload to track
            priority: Priority level (higher = delivered first)
            
        Returns:
            Unique payload ID
        """
        payload_id = self.next_payload_id
        self.next_payload_id += 1
        
        # Create tracked payload
        tracked = TrackedPayload(
            payload=payload,
            priority=priority,
            creation_time=time.time()
        )
        
        self.tracked_payloads[payload_id] = tracked
        
        # Add to appropriate queue
        if payload.target_player == 1:
            self.player1_queue.append(payload_id)
        elif payload.target_player == 2:
            self.player2_queue.append(payload_id)
        
        # Update statistics
        self.stats['total_tracked'] += 1
        
        print(f"📦 Added payload {payload_id} for player {payload.target_player} "
              f"(type: {payload.attack_type.value}, priority: {priority})")
        
        return payload_id
    
    def get_ready_payloads(self, current_time: float) -> Dict[int, List[TrackedPayload]]:
        """
        Get payloads ready for delivery.
        
        Args:
            current_time: Current game time
            
        Returns:
            Dictionary with ready payloads for each player
        """
        ready_payloads = {1: [], 2: []}
        
        # Check player 1's queue
        for payload_id in self.player1_queue[:]:
            tracked = self.tracked_payloads.get(payload_id)
            if tracked and self._is_payload_ready(tracked, current_time):
                ready_payloads[1].append(tracked)
                tracked.state = PayloadState.DELIVERING
        
        # Check player 2's queue
        for payload_id in self.player2_queue[:]:
            tracked = self.tracked_payloads.get(payload_id)
            if tracked and self._is_payload_ready(tracked, current_time):
                ready_payloads[2].append(tracked)
                tracked.state = PayloadState.DELIVERING
        
        # Sort by priority (highest first)
        for player in [1, 2]:
            ready_payloads[player].sort(key=lambda x: x.priority, reverse=True)
        
        return ready_payloads
    
    def _is_payload_ready(self, tracked: TrackedPayload, current_time: float) -> bool:
        """Check if a payload is ready for delivery."""
        return (tracked.state == PayloadState.QUEUED and 
                tracked.delivery_time is not None and
                current_time >= tracked.delivery_time)
    
    def mark_payload_delivered(self, payload_id: int) -> bool:
        """
        Mark a payload as successfully delivered.
        
        Args:
            payload_id: ID of the delivered payload
            
        Returns:
            True if payload was found and marked delivered
        """
        tracked = self.tracked_payloads.get(payload_id)
        if tracked:
            tracked.state = PayloadState.DELIVERED
            
            # Remove from queues
            if payload_id in self.player1_queue:
                self.player1_queue.remove(payload_id)
            if payload_id in self.player2_queue:
                self.player2_queue.remove(payload_id)
            
            # Update statistics
            self.stats['total_delivered'] += 1
            delivery_time = time.time() - tracked.creation_time
            self._update_average_delivery_time(delivery_time)
            
            print(f"📦 Payload {payload_id} delivered successfully")
            return True
        return False
    
    def cancel_payload(self, payload_id: int, reason: str = "Unknown") -> bool:
        """
        Cancel a payload.
        
        Args:
            payload_id: ID of the payload to cancel
            reason: Reason for cancellation
            
        Returns:
            True if payload was found and cancelled
        """
        tracked = self.tracked_payloads.get(payload_id)
        if tracked:
            tracked.state = PayloadState.CANCELLED
            
            # Remove from queues
            if payload_id in self.player1_queue:
                self.player1_queue.remove(payload_id)
            if payload_id in self.player2_queue:
                self.player2_queue.remove(payload_id)
            
            # Update statistics
            self.stats['total_cancelled'] += 1
            
            print(f"📦 Payload {payload_id} cancelled: {reason}")
            return True
        return False
    
    def get_next_attack_column(self, target_player: int, 
                              attack_width: int = 1) -> Optional[int]:
        """
        Get the next column for attack placement using rotation.
        
        Args:
            target_player: Player to target (1 or 2)
            attack_width: Width of the attack (for placement validation)
            
        Returns:
            Column index (0-based) or None if no valid column
        """
        if target_player not in [1, 2]:
            return None
        
        original_index = self.column_rotation[target_player]
        attempts = 0
        
        while attempts < len(self.column_sequence):
            current_index = self.column_rotation[target_player]
            column = self.column_sequence[current_index]
            
            # Advance rotation
            self.column_rotation[target_player] = (current_index + 1) % len(self.column_sequence)
            
            # Convert to 0-based and validate
            column_0_based = column - 1
            
            if self._is_column_valid(target_player, column_0_based, attack_width):
                return column_0_based
            
            attempts += 1
        
        # If no valid column found, return center column as fallback
        return self.grid_width // 2
    
    def _is_column_valid(self, target_player: int, column: int, width: int) -> bool:
        """Check if a column is valid for attack placement."""
        # Check bounds
        if column < 0 or column + width > self.grid_width:
            return False
        
        # Check if column is blocked
        blocked = self.blocked_columns.get(target_player, set())
        for i in range(width):
            if column + i in blocked:
                return False
        
        return True
    
    def block_column(self, target_player: int, column: int):
        """Block a column from receiving attacks."""
        if target_player in [1, 2]:
            self.blocked_columns[target_player].add(column)
            print(f"📦 Column {column} blocked for player {target_player}")
    
    def unblock_column(self, target_player: int, column: int):
        """Unblock a column for receiving attacks."""
        if target_player in [1, 2]:
            self.blocked_columns[target_player].discard(column)
            print(f"📦 Column {column} unblocked for player {target_player}")
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get detailed queue status."""
        return {
            'player1_queue_length': len(self.player1_queue),
            'player2_queue_length': len(self.player2_queue),
            'total_tracked': len(self.tracked_payloads),
            'blocked_columns_p1': list(self.blocked_columns[1]),
            'blocked_columns_p2': list(self.blocked_columns[2]),
            'column_rotation_p1': self.column_rotation[1],
            'column_rotation_p2': self.column_rotation[2],
            'statistics': self.stats.copy()
        }
    
    def cleanup_delivered_payloads(self, max_age: float = 300.0):
        """
        Clean up old delivered payloads to prevent memory leaks.
        
        Args:
            max_age: Maximum age in seconds before cleanup
        """
        current_time = time.time()
        to_remove = []
        
        for payload_id, tracked in self.tracked_payloads.items():
            if (tracked.state in [PayloadState.DELIVERED, PayloadState.CANCELLED] and
                current_time - tracked.creation_time > max_age):
                to_remove.append(payload_id)
        
        for payload_id in to_remove:
            del self.tracked_payloads[payload_id]
        
        if to_remove:
            print(f"📦 Cleaned up {len(to_remove)} old payloads")
    
    def get_pending_attacks_for_player(self, player_id: int) -> List[TrackedPayload]:
        """Get all pending attacks for a specific player."""
        queue = self.player1_queue if player_id == 1 else self.player2_queue
        return [self.tracked_payloads[pid] for pid in queue 
                if pid in self.tracked_payloads]
    
    def _update_average_delivery_time(self, delivery_time: float):
        """Update the average delivery time statistic."""
        delivered = self.stats['total_delivered']
        if delivered == 1:
            self.stats['average_delivery_time'] = delivery_time
        else:
            current_avg = self.stats['average_delivery_time']
            self.stats['average_delivery_time'] = ((current_avg * (delivered - 1)) + delivery_time) / delivered
    
    def reset_statistics(self):
        """Reset all statistics."""
        self.stats = {
            'total_tracked': 0,
            'total_delivered': 0,
            'total_cancelled': 0,
            'average_delivery_time': 0.0,
            'failed_deliveries': 0
        }
        print("📦 PayloadTracker statistics reset")
    
    def clear_all_queues(self):
        """Clear all attack queues."""
        self.player1_queue.clear()
        self.player2_queue.clear()
        self.tracked_payloads.clear()
        self.blocked_columns = {1: set(), 2: set()}
        print("📦 All queues cleared")
    
    def update(self, current_time: float) -> Dict[str, Any]:
        """
        Update the payload tracker.
        
        Args:
            current_time: Current game time
            
        Returns:
            Dictionary with update results
        """
        # Clean up old payloads
        self.cleanup_delivered_payloads()
        
        # Get ready payloads
        ready_payloads = self.get_ready_payloads(current_time)
        
        # Update any expired payloads
        self._check_expired_payloads(current_time)
        
        return {
            'ready_payloads': ready_payloads,
            'queue_status': self.get_queue_status(),
            'timestamp': current_time
        }
    
    def _check_expired_payloads(self, current_time: float):
        """Check for and handle expired payloads."""
        max_age = 30.0  # 30 seconds max age
        
        for payload_id, tracked in list(self.tracked_payloads.items()):
            if (tracked.state == PayloadState.QUEUED and 
                current_time - tracked.creation_time > max_age):
                self.cancel_payload(payload_id, "Expired")


# Utility functions
def create_payload_tracker(grid_width: int = 6, grid_height: int = 12) -> PayloadTracker:
    """Factory function to create a PayloadTracker instance."""
    return PayloadTracker(grid_width, grid_height)


def track_attack_payload(tracker: PayloadTracker, payload: AttackPayload, 
                        priority: int = 0) -> int:
    """
    Convenience function to track an attack payload.
    
    Args:
        tracker: PayloadTracker instance
        payload: Attack payload to track
        priority: Priority level
        
    Returns:
        Payload ID
    """
    return tracker.add_payload(payload, priority) 