# State Management Patterns Guide

## Overview

This guide provides comprehensive patterns and best practices for integrating modules with the unified Game State Module. It covers state management patterns, integration strategies, performance optimization, and common use cases.

## 🎯 Core State Management Patterns

### 1. Basic State Access Pattern

```python
from modules.game_state_module.game_state_manager import GameStateManager

class YourModule:
    def __init__(self, state_manager: GameStateManager):
        self.state_manager = state_manager
    
    def get_some_value(self):
        """Get a value from the state manager."""
        return self.state_manager.get("your_module.some_field", default_value)
    
    def set_some_value(self, value):
        """Set a value in the state manager."""
        return self.state_manager.set(
            "your_module.some_field", 
            value, 
            source="your_module",
            description="Some field updated"
        )
```

### 2. State Validation Pattern

```python
def set_volume(self, volume: float) -> bool:
    """Set volume with validation."""
    # Validate input
    if not isinstance(volume, (int, float)) or volume < 0.0 or volume > 1.0:
        return False
    
    # Set state with validation
    return self.state_manager.set(
        "audio.master_volume",
        volume,
        source="audio_module",
        description=f"Master volume set to {volume}"
    )
```

### 3. State Change Tracking Pattern

```python
def track_state_changes(self):
    """Track state changes for debugging."""
    changes = self.state_manager.history.get_changes_for_field("your_module.some_field")
    
    for change in changes:
        print(f"Field: {change.field_path}")
        print(f"Old value: {change.old_value}")
        print(f"New value: {change.new_value}")
        print(f"Source: {change.source}")
        print(f"Timestamp: {change.timestamp}")
        print(f"Description: {change.description}")
```

### 4. Callback Registration Pattern

```python
def __init__(self, state_manager: GameStateManager):
    self.state_manager = state_manager
    
    # Register callbacks for state changes
    self.state_manager.add_change_callback(
        "your_module.some_field",
        self._on_some_field_changed
    )
    
    self.state_manager.add_change_callback(
        "your_module.another_field",
        self._on_another_field_changed
    )

def _on_some_field_changed(self, field_path: str, old_value: Any, new_value: Any):
    """Handle state change callback."""
    print(f"Field {field_path} changed from {old_value} to {new_value}")
    # Update your module's internal state
    self._update_internal_state(new_value)
```

## 🔧 Module Integration Patterns

### 1. Audio Module Integration

```python
class AudioStateManager:
    """Manages audio state through the unified state manager."""
    
    def __init__(self, state_manager: GameStateManager):
        self.state_manager = state_manager
        self._register_callbacks()
    
    def _register_callbacks(self):
        """Register callbacks for audio state changes."""
        audio_fields = [
            "audio.master_volume",
            "audio.music_volume",
            "audio.sfx_volume",
            "audio.music_enabled",
            "audio.sfx_enabled"
        ]
        
        for field in audio_fields:
            self.state_manager.add_change_callback(field, self._on_audio_state_change)
    
    def set_master_volume(self, volume: float, source: str = "audio_manager") -> bool:
        """Set the master volume."""
        return self.state_manager.set(
            "audio.master_volume",
            volume,
            source=source,
            description=f"Master volume set to {volume}"
        )
    
    def get_master_volume(self) -> float:
        """Get the master volume."""
        return self.state_manager.get("audio.master_volume", 0.6)
    
    def _on_audio_state_change(self, field_path: str, old_value: Any, new_value: Any):
        """Handle audio state changes."""
        # Update audio system when state changes
        self._update_audio_system(field_path, new_value)
```

### 2. Screen Module Integration

```python
class ScreenStateManager:
    """Manages screen state through the unified state manager."""
    
    def __init__(self, state_manager: GameStateManager):
        self.state_manager = state_manager
        self._register_callbacks()
    
    def transition_to_screen(self, screen_type: ScreenType, source: str = "screen_manager"):
        """Transition to a new screen."""
        # Set previous screen
        current_screen = self.state_manager.get("screen.current_screen")
        if current_screen:
            self.state_manager.set(
                "screen.previous_screen",
                current_screen,
                source=source,
                description=f"Previous screen set to {current_screen}"
            )
        
        # Set new screen
        self.state_manager.set(
            "screen.current_screen",
            screen_type,
            source=source,
            description=f"Screen transitioned to {screen_type}"
        )
        
        # Set transition timestamp
        self.state_manager.set(
            "screen.screen_transition_time",
            time.time(),
            source=source,
            description="Screen transition timestamp"
        )
    
    def get_current_screen(self) -> ScreenType:
        """Get the current screen."""
        return self.state_manager.get("screen.current_screen", ScreenType.LOADING)
```

### 3. Input Module Integration

```python
class InputStateManager:
    """Manages input state through the unified state manager."""
    
    def __init__(self, state_manager: GameStateManager):
        self.state_manager = state_manager
        self._register_callbacks()
    
    def process_key_press(self, key: str, source: str = "input_manager"):
        """Process a key press event."""
        current_keys = set(self.state_manager.get("input.keys_pressed", set()))
        current_keys.add(key)
        
        self.state_manager.set(
            "input.keys_pressed",
            current_keys,
            source=source,
            description=f"Key {key} pressed"
        )
        
        # Update last input time
        self.state_manager.set(
            "input.last_input_time",
            time.time(),
            source=source,
            description="Last input timestamp updated"
        )
    
    def process_key_release(self, key: str, source: str = "input_manager"):
        """Process a key release event."""
        current_keys = set(self.state_manager.get("input.keys_pressed", set()))
        current_keys.discard(key)
        
        self.state_manager.set(
            "input.keys_pressed",
            current_keys,
            source=source,
            description=f"Key {key} released"
        )
    
    def get_pressed_keys(self) -> set:
        """Get currently pressed keys."""
        return set(self.state_manager.get("input.keys_pressed", set()))
```

### 4. Puzzle Module Integration

```python
class PuzzleStateManager:
    """Manages puzzle game state through the unified state manager."""
    
    def __init__(self, state_manager: GameStateManager):
        self.state_manager = state_manager
        self._register_callbacks()
    
    def start_game(self, game_mode: GameMode, source: str = "puzzle_manager"):
        """Start a new puzzle game."""
        self.state_manager.set(
            "puzzle.game_active",
            True,
            source=source,
            description="Puzzle game started"
        )
        
        self.state_manager.set(
            "puzzle.game_mode",
            game_mode,
            source=source,
            description=f"Game mode set to {game_mode}"
        )
        
        self.state_manager.set(
            "puzzle.puzzle_state",
            PuzzleState.ACTIVE,
            source=source,
            description="Puzzle state set to active"
        )
        
        # Reset game statistics
        self.state_manager.set("puzzle.score", 0, source=source, description="Score reset")
        self.state_manager.set("puzzle.lines_cleared", 0, source=source, description="Lines cleared reset")
        self.state_manager.set("puzzle.chain_count", 0, source=source, description="Chain count reset")
    
    def update_score(self, points: int, source: str = "puzzle_manager"):
        """Update the puzzle score."""
        current_score = self.state_manager.get("puzzle.score", 0)
        new_score = current_score + points
        
        self.state_manager.set(
            "puzzle.score",
            new_score,
            source=source,
            description=f"Score updated: {current_score} + {points} = {new_score}"
        )
    
    def set_current_piece(self, piece_data: dict, source: str = "puzzle_manager"):
        """Set the current puzzle piece."""
        self.state_manager.set(
            "puzzle.current_piece",
            piece_data,
            source=source,
            description="Current piece updated"
        )
    
    def get_game_state(self) -> dict:
        """Get the complete puzzle game state."""
        return {
            "game_active": self.state_manager.get("puzzle.game_active", False),
            "game_mode": self.state_manager.get("puzzle.game_mode", GameMode.MENU),
            "puzzle_state": self.state_manager.get("puzzle.puzzle_state", PuzzleState.IDLE),
            "score": self.state_manager.get("puzzle.score", 0),
            "lines_cleared": self.state_manager.get("puzzle.lines_cleared", 0),
            "chain_count": self.state_manager.get("puzzle.chain_count", 0),
            "current_piece": self.state_manager.get("puzzle.current_piece"),
            "next_piece": self.state_manager.get("puzzle.next_piece")
        }
```

## ⚡ Performance Optimization Patterns

### 1. State Batching Pattern

```python
def batch_state_updates(self, updates: dict, source: str = "your_module"):
    """Batch multiple state updates for better performance."""
    results = {}
    
    for field_path, value in updates.items():
        result = self.state_manager.set(
            field_path,
            value,
            source=source,
            description=f"Batched update: {field_path}"
        )
        results[field_path] = result
    
    return results

# Usage example
updates = {
    "puzzle.score": 1500,
    "puzzle.lines_cleared": 5,
    "puzzle.chain_count": 2,
    "audio.master_volume": 0.8
}

results = self.batch_state_updates(updates, source="game_system")
```

### 2. State Caching Pattern

```python
class CachedStateManager:
    """State manager with caching for frequently accessed values."""
    
    def __init__(self, state_manager: GameStateManager):
        self.state_manager = state_manager
        self._cache = {}
        self._cache_timestamps = {}
        self._cache_ttl = 0.1  # 100ms cache TTL
    
    def get_cached(self, field_path: str, default_value=None):
        """Get a value with caching."""
        current_time = time.time()
        
        # Check if we have a valid cached value
        if (field_path in self._cache and 
            field_path in self._cache_timestamps and
            current_time - self._cache_timestamps[field_path] < self._cache_ttl):
            return self._cache[field_path]
        
        # Get fresh value from state manager
        value = self.state_manager.get(field_path, default_value)
        
        # Cache the value
        self._cache[field_path] = value
        self._cache_timestamps[field_path] = current_time
        
        return value
    
    def invalidate_cache(self, field_path: str = None):
        """Invalidate cache for a specific field or all fields."""
        if field_path:
            self._cache.pop(field_path, None)
            self._cache_timestamps.pop(field_path, None)
        else:
            self._cache.clear()
            self._cache_timestamps.clear()
```

### 3. Lazy State Loading Pattern

```python
class LazyStateManager:
    """State manager with lazy loading for expensive operations."""
    
    def __init__(self, state_manager: GameStateManager):
        self.state_manager = state_manager
        self._loaded_states = set()
    
    def ensure_state_loaded(self, state_category: str):
        """Ensure a state category is loaded."""
        if state_category not in self._loaded_states:
            self._load_state_category(state_category)
            self._loaded_states.add(state_category)
    
    def _load_state_category(self, state_category: str):
        """Load a specific state category."""
        # This would contain the logic to load the state category
        # For example, loading puzzle state from save file
        pass
    
    def get_with_lazy_load(self, field_path: str, default_value=None):
        """Get a value with lazy loading."""
        state_category = field_path.split('.')[0]
        self.ensure_state_loaded(state_category)
        
        return self.state_manager.get(field_path, default_value)
```

## 🔄 State Synchronization Patterns

### 1. Bidirectional Sync Pattern

```python
class BidirectionalStateSync:
    """Bidirectional synchronization between module and state manager."""
    
    def __init__(self, state_manager: GameStateManager, module_instance):
        self.state_manager = state_manager
        self.module = module_instance
        self._syncing = False  # Prevent infinite loops
    
    def sync_to_state_manager(self):
        """Sync module state to state manager."""
        if self._syncing:
            return
        
        self._syncing = True
        
        try:
            # Get module state
            module_state = self.module.get_state()
            
            # Update state manager
            for field_path, value in module_state.items():
                self.state_manager.set(
                    field_path,
                    value,
                    source="module_sync",
                    description=f"Synced from module: {field_path}"
                )
        finally:
            self._syncing = False
    
    def sync_from_state_manager(self):
        """Sync state manager state to module."""
        if self._syncing:
            return
        
        self._syncing = True
        
        try:
            # Get state manager state
            state_summary = self.state_manager.get_state_summary()
            
            # Update module
            self.module.update_from_state(state_summary)
        finally:
            self._syncing = False
```

### 2. Periodic Sync Pattern

```python
import threading
import time

class PeriodicStateSync:
    """Periodic synchronization between module and state manager."""
    
    def __init__(self, state_manager: GameStateManager, module_instance, sync_interval: float = 0.1):
        self.state_manager = state_manager
        self.module = module_instance
        self.sync_interval = sync_interval
        self._sync_thread = None
        self._running = False
    
    def start_sync(self):
        """Start periodic synchronization."""
        if self._running:
            return
        
        self._running = True
        self._sync_thread = threading.Thread(target=self._sync_loop, daemon=True)
        self._sync_thread.start()
    
    def stop_sync(self):
        """Stop periodic synchronization."""
        self._running = False
        if self._sync_thread:
            self._sync_thread.join()
    
    def _sync_loop(self):
        """Main sync loop."""
        while self._running:
            try:
                self.module.sync_to_state_manager()
                time.sleep(self.sync_interval)
            except Exception as e:
                print(f"Sync error: {e}")
                time.sleep(self.sync_interval)
```

## 📊 State Monitoring Patterns

### 1. State Change Monitoring

```python
class StateChangeMonitor:
    """Monitor state changes for debugging and analytics."""
    
    def __init__(self, state_manager: GameStateManager):
        self.state_manager = state_manager
        self._change_counts = {}
        self._last_changes = {}
    
    def monitor_field(self, field_path: str):
        """Start monitoring a specific field."""
        self.state_manager.add_change_callback(field_path, self._on_field_changed)
    
    def _on_field_changed(self, field_path: str, old_value: Any, new_value: Any):
        """Handle field change for monitoring."""
        # Count changes
        self._change_counts[field_path] = self._change_counts.get(field_path, 0) + 1
        
        # Store last change
        self._last_changes[field_path] = {
            'old_value': old_value,
            'new_value': new_value,
            'timestamp': time.time()
        }
        
        # Log significant changes
        if self._is_significant_change(field_path, old_value, new_value):
            print(f"Significant change detected: {field_path} = {old_value} -> {new_value}")
    
    def _is_significant_change(self, field_path: str, old_value: Any, new_value: Any) -> bool:
        """Determine if a change is significant."""
        # Define significance criteria for different fields
        if "score" in field_path:
            return abs(new_value - old_value) > 100
        elif "volume" in field_path:
            return abs(new_value - old_value) > 0.1
        elif "screen" in field_path:
            return old_value != new_value
        return False
    
    def get_monitoring_report(self) -> dict:
        """Get a monitoring report."""
        return {
            'change_counts': self._change_counts.copy(),
            'last_changes': self._last_changes.copy()
        }
```

### 2. Performance Monitoring

```python
class StatePerformanceMonitor:
    """Monitor state management performance."""
    
    def __init__(self, state_manager: GameStateManager):
        self.state_manager = state_manager
        self._operation_times = []
        self._operation_counts = 0
    
    def time_operation(self, operation_name: str):
        """Decorator to time state operations."""
        def decorator(func):
            def wrapper(*args, **kwargs):
                start_time = time.time()
                result = func(*args, **kwargs)
                end_time = time.time()
                
                operation_time = end_time - start_time
                self._operation_times.append(operation_time)
                self._operation_counts += 1
                
                # Alert on slow operations
                if operation_time > 0.01:  # 10ms threshold
                    print(f"Slow operation detected: {operation_name} took {operation_time:.3f}s")
                
                return result
            return wrapper
        return decorator
    
    def get_performance_report(self) -> dict:
        """Get a performance report."""
        if not self._operation_times:
            return {'average_time': 0, 'total_operations': 0}
        
        return {
            'average_time': sum(self._operation_times) / len(self._operation_times),
            'max_time': max(self._operation_times),
            'min_time': min(self._operation_times),
            'total_operations': self._operation_counts,
            'recent_operations': self._operation_times[-10:]  # Last 10 operations
        }
```

## 🎯 Best Practices

### 1. State Naming Conventions

```python
# Use dot notation for hierarchical state
"puzzle.score"           # Puzzle game score
"puzzle.lines_cleared"   # Lines cleared in puzzle
"audio.master_volume"    # Master audio volume
"screen.current_screen"  # Current screen
"input.keys_pressed"     # Currently pressed keys

# Use descriptive field names
"puzzle.game_active"     # Not "puzzle.active"
"audio.music_enabled"    # Not "audio.music"
"screen.transition_time" # Not "screen.time"
```

### 2. Source Tracking

```python
# Always provide a source for state changes
state_manager.set("puzzle.score", 1000, source="game_system")
state_manager.set("audio.volume", 0.8, source="settings_ui")
state_manager.set("screen.current", ScreenType.GAME, source="screen_manager")

# Use consistent source names
"game_system"      # Core game logic
"settings_ui"      # Settings user interface
"screen_manager"   # Screen management system
"input_manager"    # Input handling system
"audio_manager"    # Audio system
"puzzle_manager"   # Puzzle game logic
```

### 3. Error Handling

```python
def safe_state_set(self, field_path: str, value: Any, source: str = "unknown"):
    """Safely set a state value with error handling."""
    try:
        return self.state_manager.set(field_path, value, source=source)
    except Exception as e:
        print(f"Error setting state {field_path}: {e}")
        return False

def safe_state_get(self, field_path: str, default_value=None):
    """Safely get a state value with error handling."""
    try:
        return self.state_manager.get(field_path, default_value)
    except Exception as e:
        print(f"Error getting state {field_path}: {e}")
        return default_value
```

### 4. State Validation

```python
def validate_state_value(self, field_path: str, value: Any) -> bool:
    """Validate a state value before setting it."""
    if "volume" in field_path:
        return isinstance(value, (int, float)) and 0.0 <= value <= 1.0
    elif "score" in field_path:
        return isinstance(value, int) and value >= 0
    elif "screen" in field_path:
        return isinstance(value, ScreenType)
    elif "keys" in field_path:
        return isinstance(value, (set, list, tuple))
    
    return True

def set_with_validation(self, field_path: str, value: Any, source: str = "unknown"):
    """Set state value with validation."""
    if not self.validate_state_value(field_path, value):
        print(f"Invalid value for {field_path}: {value}")
        return False
    
    return self.state_manager.set(field_path, value, source=source)
```

## 📋 Integration Checklist

Before integrating your module with the Game State Module:

- [ ] **State Schema Defined** - All state fields defined in state_schema.py
- [ ] **Validation Rules** - Validation rules implemented for all state fields
- [ ] **Source Tracking** - All state changes include source information
- [ ] **Error Handling** - Robust error handling for state operations
- [ ] **Performance Optimization** - State batching and caching implemented
- [ ] **Callback Registration** - Callbacks registered for relevant state changes
- [ ] **State Synchronization** - Bidirectional sync with module state
- [ ] **Testing** - Comprehensive tests for state integration
- [ ] **Documentation** - Integration patterns documented

---

**State Management Patterns Guide**  
**Version**: 1.0.0  
**Last Updated**: 2024-01-XX  
**Maintainer**: Game State Module Team

*This guide is part of the BladeFighters project. For project-wide documentation, see the [Documentation Index](../../README.md).*
