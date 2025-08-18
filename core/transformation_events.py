"""
Transformation Event System

This module provides the event-driven architecture for handling garbage and strike block
transformations in the puzzle game. It defines the event types, data structures, and
handlers for the transformation system.

Author: Transformation System Rebuild
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional, Tuple
from enum import Enum


class TransformationStage(Enum):
    """Enumeration of transformation stages for blocks."""
    INITIAL = 0          # Initial state (garbage_block.png or 1x4.png)
    NEUTRAL_GARBAGE = 1  # garbage_block.png (for strikes)
    COLORED_GARBAGE = 2  # {color}_garbage.png
    NORMAL_BLOCK = 3     # {color}_block (final state)


class BlockType(Enum):
    """Enumeration of block types that can transform."""
    GARBAGE = "garbage"
    STRIKE = "strike"


class EventType(Enum):
    """Enumeration of transformation event types."""
    PAYLOAD_DELIVERED = "payload_delivered"
    PIECE_LANDED = "piece_landed"
    TRANSFORMATION_PROGRESS = "transformation_progress"
    TRANSFORMATION_COMPLETE = "transformation_complete"


@dataclass
class TransformationState:
    """Represents the current state of a transforming block."""
    position: Tuple[int, int]
    player_id: int
    block_type: BlockType
    current_stage: TransformationStage
    color: str
    landings_required: int
    landings_received: int
    
    def __post_init__(self):
        """Set default landings required based on block type and stage."""
        if self.block_type == BlockType.STRIKE:
            # Strike: 1x4.png -> garbage_block -> {color}_garbage -> {color}_block
            stage_requirements = {
                TransformationStage.INITIAL: 1,        # 1x4.png -> garbage_block
                TransformationStage.NEUTRAL_GARBAGE: 1, # garbage_block -> {color}_garbage
                TransformationStage.COLORED_GARBAGE: 1  # {color}_garbage -> {color}_block
            }
        else:  # GARBAGE
            # Garbage: garbage_block -> {color}_garbage -> {color}_block
            stage_requirements = {
                TransformationStage.INITIAL: 1,        # garbage_block -> {color}_garbage
                TransformationStage.COLORED_GARBAGE: 1  # {color}_garbage -> {color}_block
            }
        
        if self.landings_required == 0:
            self.landings_required = stage_requirements.get(self.current_stage, 1)


@dataclass
class TransformationEvent:
    """Represents a transformation-related event."""
    event_type: EventType
    position: Tuple[int, int]
    player_id: int
    block_type: BlockType
    color: str
    stage: TransformationStage
    timestamp: float
    metadata: Optional[Dict[str, Any]] = None


class TransformationEventManager:
    """Manages transformation events and state tracking."""
    
    def __init__(self):
        """Initialize the transformation event manager."""
        self.transformation_states: Dict[Tuple[int, int, int], TransformationState] = {}
        self.event_handlers: Dict[EventType, list] = {event_type: [] for event_type in EventType}
        self.event_history: list = []
    
    def register_handler(self, event_type: EventType, handler):
        """Register an event handler for a specific event type."""
        self.event_handlers[event_type].append(handler)
    
    def emit_event(self, event: TransformationEvent):
        """Emit a transformation event to all registered handlers."""
        self.event_history.append(event)
        
        # Call all registered handlers for this event type
        for handler in self.event_handlers[event.event_type]:
            try:
                handler(event)
            except Exception as e:
                print(f"Error in transformation event handler: {e}")
    
    def create_payload_delivered_event(self, position: Tuple[int, int], player_id: int, 
                                     block_type: BlockType, color: str) -> TransformationEvent:
        """Create a payload delivered event."""
        return TransformationEvent(
            event_type=EventType.PAYLOAD_DELIVERED,
            position=position,
            player_id=player_id,
            block_type=block_type,
            color=color,
            stage=TransformationStage.INITIAL,
            timestamp=self._get_current_time()
        )
    
    def create_piece_landed_event(self, position: Tuple[int, int], player_id: int) -> TransformationEvent:
        """Create a piece landed event."""
        # Find the transformation state for this position
        state = self.get_transformation_state(position, player_id)
        if not state:
            return None
            
        return TransformationEvent(
            event_type=EventType.PIECE_LANDED,
            position=position,
            player_id=player_id,
            block_type=state.block_type,
            color=state.color,
            stage=state.current_stage,
            timestamp=self._get_current_time()
        )
    
    def add_transformation_state(self, state: TransformationState):
        """Add a transformation state to tracking."""
        key = (state.position[0], state.position[1], state.player_id)
        self.transformation_states[key] = state
    
    def get_transformation_state(self, position: Tuple[int, int], player_id: int) -> Optional[TransformationState]:
        """Get the transformation state for a specific position and player."""
        key = (position[0], position[1], player_id)
        return self.transformation_states.get(key)
    
    def update_transformation_state(self, position: Tuple[int, int], player_id: int, 
                                  new_stage: TransformationStage, landings_increment: int = 1):
        """Update the transformation state for a block."""
        key = (position[0], position[1], player_id)
        if key in self.transformation_states:
            state = self.transformation_states[key]
            state.landings_received += landings_increment
            
            # Check if we should progress to next stage
            if state.landings_received >= state.landings_required:
                state.current_stage = new_stage
                state.landings_received = 0
                
                # Emit progress event
                progress_event = TransformationEvent(
                    event_type=EventType.TRANSFORMATION_PROGRESS,
                    position=position,
                    player_id=player_id,
                    block_type=state.block_type,
                    color=state.color,
                    stage=new_stage,
                    timestamp=self._get_current_time()
                )
                self.emit_event(progress_event)
                
                # Check if transformation is complete
                if new_stage == TransformationStage.NORMAL_BLOCK:
                    complete_event = TransformationEvent(
                        event_type=EventType.TRANSFORMATION_COMPLETE,
                        position=position,
                        player_id=player_id,
                        block_type=state.block_type,
                        color=state.color,
                        stage=new_stage,
                        timestamp=self._get_current_time()
                    )
                    self.emit_event(complete_event)
                    # Remove from tracking
                    del self.transformation_states[key]
    
    def remove_transformation_state(self, position: Tuple[int, int], player_id: int):
        """Remove a transformation state from tracking."""
        key = (position[0], position[1], player_id)
        if key in self.transformation_states:
            del self.transformation_states[key]
    
    def get_block_display_name(self, state: TransformationState) -> str:
        """Get the display name for a block based on its transformation state."""
        if state.block_type == BlockType.STRIKE:
            if state.current_stage == TransformationStage.INITIAL:
                return "1x4.png"  # Strike initial state
            elif state.current_stage == TransformationStage.NEUTRAL_GARBAGE:
                return "garbage_block"  # Strike becomes neutral garbage
            elif state.current_stage == TransformationStage.COLORED_GARBAGE:
                return f"{state.color}_garbage"  # Colored garbage
            else:  # NORMAL_BLOCK
                return f"{state.color}_block"  # Normal colored block
        else:  # GARBAGE
            if state.current_stage == TransformationStage.INITIAL:
                return "garbage_block"  # Garbage initial state
            elif state.current_stage == TransformationStage.COLORED_GARBAGE:
                return f"{state.color}_garbage"  # Colored garbage
            else:  # NORMAL_BLOCK
                return f"{state.color}_block"  # Normal colored block
    
    def get_next_stage(self, state: TransformationState) -> TransformationStage:
        """Get the next stage for a transformation state."""
        if state.block_type == BlockType.STRIKE:
            stage_progression = {
                TransformationStage.INITIAL: TransformationStage.NEUTRAL_GARBAGE,
                TransformationStage.NEUTRAL_GARBAGE: TransformationStage.COLORED_GARBAGE,
                TransformationStage.COLORED_GARBAGE: TransformationStage.NORMAL_BLOCK
            }
        else:  # GARBAGE
            stage_progression = {
                TransformationStage.INITIAL: TransformationStage.COLORED_GARBAGE,
                TransformationStage.COLORED_GARBAGE: TransformationStage.NORMAL_BLOCK
            }
        
        return stage_progression.get(state.current_stage, TransformationStage.NORMAL_BLOCK)
    
    def _get_current_time(self) -> float:
        """Get current time for event timestamps."""
        import time
        return time.time()


# Global instance for easy access
transformation_manager = TransformationEventManager()
