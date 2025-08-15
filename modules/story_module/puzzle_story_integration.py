"""
Puzzle-Story Mode Integration
Coordinates between story system and puzzle engine for seamless gameplay transitions.
"""

import time
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum

class StoryPuzzleTransition(Enum):
    """Types of transitions between story and puzzle modes."""
    STORY_TO_PUZZLE = "story_to_puzzle"
    PUZZLE_TO_STORY = "puzzle_to_story"
    STORY_COMPLETE = "story_complete"
    PUZZLE_COMPLETE = "puzzle_complete"

@dataclass
class StoryPuzzleState:
    """State management for story-puzzle integration."""
    current_story_id: int = 1
    current_chapter: int = 1
    puzzle_completed: bool = False
    story_progress: Dict[int, bool] = None  # story_id -> completed
    last_transition_time: float = 0.0
    transition_duration: float = 1.0  # seconds
    
    def __post_init__(self):
        if self.story_progress is None:
            self.story_progress = {1: False}  # Only first story available initially

class PuzzleStoryIntegrator:
    """
    Integrates puzzle engine with story system for seamless gameplay.
    Handles transitions, state management, and coordination between modes.
    """
    
    def __init__(self, puzzle_engine=None, story_system=None, state_manager=None):
        """Initialize the puzzle-story integrator."""
        self.puzzle_engine = puzzle_engine
        self.story_system = story_system
        self.state_manager = state_manager
        
        # Integration state
        self.integration_state = StoryPuzzleState()
        
        # Transition management
        self.transitioning = False
        self.transition_start_time = 0.0
        
        # Callbacks for state changes
        self.on_story_complete_callbacks = []
        self.on_puzzle_complete_callbacks = []
        self.on_transition_callbacks = []
        
        print("🎭 Puzzle-Story Integrator initialized")
    
    def set_puzzle_engine(self, puzzle_engine):
        """Set the puzzle engine for integration."""
        self.puzzle_engine = puzzle_engine
        print("✅ Puzzle engine connected to story integrator")
    
    def set_story_system(self, story_system):
        """Set the story system for integration."""
        self.story_system = story_system
        print("✅ Story system connected to puzzle integrator")
    
    def set_state_manager(self, state_manager):
        """Set the state manager for integration."""
        self.state_manager = state_manager
        print("✅ State manager connected to story integrator")
    
    def add_story_complete_callback(self, callback):
        """Add callback for when story is completed."""
        self.on_story_complete_callbacks.append(callback)
    
    def add_puzzle_complete_callback(self, callback):
        """Add callback for when puzzle is completed."""
        self.on_puzzle_complete_callbacks.append(callback)
    
    def add_transition_callback(self, callback):
        """Add callback for transitions."""
        self.on_transition_callbacks.append(callback)
    
    def start_story_to_puzzle_transition(self, story_id: int, chapter: int = 1):
        """Start transition from story to puzzle mode."""
        if self.transitioning:
            return False
        
        self.transitioning = True
        self.transition_start_time = time.time()
        self.integration_state.current_story_id = story_id
        self.integration_state.current_chapter = chapter
        self.integration_state.puzzle_completed = False
        
        # Notify callbacks
        for callback in self.on_transition_callbacks:
            try:
                callback(StoryPuzzleTransition.STORY_TO_PUZZLE, story_id, chapter)
            except Exception as e:
                print(f"⚠️ Transition callback error: {e}")
        
        # Update state manager if available
        if self.state_manager:
            try:
                self.state_manager.set("story.current_story_id", story_id, source="puzzle_story_integration")
                self.state_manager.set("story.current_chapter", chapter, source="puzzle_story_integration")
                self.state_manager.set("story.puzzle_completed", False, source="puzzle_story_integration")
            except Exception as e:
                print(f"⚠️ State manager update error: {e}")
        
        print(f"🎭 Starting story-to-puzzle transition: Story {story_id}, Chapter {chapter}")
        return True
    
    def start_puzzle_to_story_transition(self):
        """Start transition from puzzle back to story mode."""
        if self.transitioning:
            return False
        
        self.transitioning = True
        self.transition_start_time = time.time()
        
        # Notify callbacks
        for callback in self.on_transition_callbacks:
            try:
                callback(StoryPuzzleTransition.PUZZLE_TO_STORY, 
                        self.integration_state.current_story_id, 
                        self.integration_state.current_chapter)
            except Exception as e:
                print(f"⚠️ Transition callback error: {e}")
        
        print(f"🎭 Starting puzzle-to-story transition")
        return True
    
    def mark_puzzle_completed(self):
        """Mark the current puzzle as completed."""
        self.integration_state.puzzle_completed = True
        
        # Update story progress
        story_id = self.integration_state.current_story_id
        self.integration_state.story_progress[story_id] = True
        
        # Notify callbacks
        for callback in self.on_puzzle_complete_callbacks:
            try:
                callback(story_id, self.integration_state.current_chapter)
            except Exception as e:
                print(f"⚠️ Puzzle complete callback error: {e}")
        
        # Update state manager if available
        if self.state_manager:
            try:
                self.state_manager.set("story.puzzle_completed", True, source="puzzle_story_integration")
                self.state_manager.set(f"story.progress.{story_id}", True, source="puzzle_story_integration")
            except Exception as e:
                print(f"⚠️ State manager update error: {e}")
        
        print(f"✅ Puzzle completed for Story {story_id}, Chapter {self.integration_state.current_chapter}")
    
    def mark_story_completed(self, story_id: int):
        """Mark a story as completed."""
        self.integration_state.story_progress[story_id] = True
        
        # Unlock next story if available
        next_story_id = story_id + 1
        if next_story_id <= 10:  # Assuming 10 stories total
            self.integration_state.story_progress[next_story_id] = False  # Available but not completed
        
        # Notify callbacks
        for callback in self.on_story_complete_callbacks:
            try:
                callback(story_id)
            except Exception as e:
                print(f"⚠️ Story complete callback error: {e}")
        
        # Update state manager if available
        if self.state_manager:
            try:
                self.state_manager.set(f"story.progress.{story_id}", True, source="puzzle_story_integration")
                if next_story_id <= 10:
                    self.state_manager.set(f"story.progress.{next_story_id}", False, source="puzzle_story_integration")
            except Exception as e:
                print(f"⚠️ State manager update error: {e}")
        
        print(f"📖 Story {story_id} completed")
    
    def update_transition(self, current_time: float) -> bool:
        """Update transition state and return True if transition is complete."""
        if not self.transitioning:
            return True
        
        elapsed = current_time - self.transition_start_time
        if elapsed >= self.integration_state.transition_duration:
            self.transitioning = False
            print("✅ Transition completed")
            return True
        
        return False
    
    def get_available_stories(self) -> List[Dict[str, Any]]:
        """Get list of available stories based on progress."""
        if not self.story_system:
            return []
        
        all_stories = self.story_system.get_story_list()
        available_stories = []
        
        for story in all_stories:
            story_id = story["id"]
            is_available = self.integration_state.story_progress.get(story_id, False) is not None
            is_completed = self.integration_state.story_progress.get(story_id, False)
            
            story["available"] = is_available
            story["completed"] = is_completed
            available_stories.append(story)
        
        return available_stories
    
    def get_current_story_info(self) -> Dict[str, Any]:
        """Get information about the current story."""
        return {
            "story_id": self.integration_state.current_story_id,
            "chapter": self.integration_state.current_chapter,
            "puzzle_completed": self.integration_state.puzzle_completed,
            "progress": self.integration_state.story_progress.copy()
        }
    
    def reset_integration_state(self):
        """Reset the integration state."""
        self.integration_state = StoryPuzzleState()
        self.transitioning = False
        print("🔄 Puzzle-Story integration state reset")
    
    def handle_puzzle_events(self, events: List) -> Optional[str]:
        """Handle puzzle events and return action if needed."""
        if not self.puzzle_engine:
            return None
        
        # Check for story mode return key
        for event in events:
            if hasattr(event, 'type') and event.type == 768:  # KEYDOWN
                if hasattr(event, 'key') and event.key == 27:  # ESC key
                    return "return_to_story"
        
        return None
    
    def handle_story_events(self, events: List) -> Optional[str]:
        """Handle story events and return action if needed."""
        if not self.story_system:
            return None
        
        # Check for puzzle mode start key
        for event in events:
            if hasattr(event, 'type') and event.type == 768:  # KEYDOWN
                if hasattr(event, 'key') and event.key == 13:  # ENTER key
                    return "start_puzzle"
        
        return None
