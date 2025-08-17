# 🧩 Puzzle Engine Documentation

## 📋 Overview

The Puzzle Engine is the core game mechanics system for BladeFighters, handling the puzzle game logic, piece movement, cluster detection, and rendering. This documentation provides a comprehensive guide to understanding, using, and extending the puzzle engine.

## 🏗️ Architecture

### Core Components

#### 1. PuzzleEngine (`core/puzzle_module.py`)
The main puzzle game engine that handles:
- Game state management
- Piece movement and physics
- Cluster detection and breaking
- Game mechanics (scoring, levels, etc.)
- Input processing for puzzle controls

#### 2. PuzzleRenderer (`core/puzzle_renderer.py`)
Handles all visual aspects of the puzzle game:
- Block rendering and animations
- Visual effects (explosions, particle effects)
- Screen transitions and effects
- Animation state management

#### 3. PuzzleStateIntegrator (`modules/game_state_module/puzzle_integration.py`)
Integration layer that connects the puzzle engine to the unified state management system:
- Bidirectional state synchronization
- State mapping and validation
- Performance optimization
- Error handling and recovery

### Class Relationships

```
GameClient
├── PuzzleEngine
│   ├── PuzzleRenderer
│   ├── AssetLoader
│   ├── InputHandler
│   ├── BasicPhysics
│   └── PieceMovement
└── GameStateManager
    └── PuzzleStateIntegrator
```

## 🎮 Core Features

### Game Mechanics

#### Piece System
- **Main Pieces**: Primary puzzle pieces that fall from the top
- **Attached Pieces**: Secondary pieces connected to main pieces
- **Piece Types**: Red, Blue, Green, Yellow blocks with different properties
- **Special Blocks**: Garbage blocks, strike blocks, and special effects

#### Movement System
- **Horizontal Movement**: Left/right piece movement with wall detection
- **Rotation**: Piece rotation with wall kick system
- **Falling**: Gravity-based falling with acceleration
- **Sliding**: Smooth horizontal sliding animations

#### Cluster Detection
- **Color Matching**: Groups of 3+ same-color blocks
- **Chain Reactions**: Cascading cluster breaks
- **Scoring**: Points based on cluster size and chain length
- **Special Effects**: Explosions and visual feedback

#### Game States
- **Active**: Normal gameplay
- **Breaking**: Cluster breaking animations
- **Chain Reaction**: Multi-cluster breaking
- **Game Over**: End game conditions

### Performance Features

#### Optimization
- **Frame Rate Control**: 60fps target with adaptive timing
- **Update Throttling**: Smart update frequency based on game state
- **Memory Management**: Efficient asset loading and cleanup
- **State Caching**: Cached state access for performance

#### Scalability
- **Configurable Grid Size**: Adjustable board dimensions
- **Asset Quality Levels**: High/medium/low quality assets
- **Performance Profiling**: Built-in performance monitoring
- **Memory Tracking**: Memory usage optimization

## 🔧 API Reference

### PuzzleEngine Class

#### Initialization
```python
class PuzzleEngine:
    def __init__(self, screen, font, audio=None, asset_path="puzzleassets", 
                 settings_system=None):
        """
        Initialize the puzzle engine.
        
        Args:
            screen: Pygame display surface
            font: Pygame font for text rendering
            audio: Audio system for sound effects (optional)
            asset_path: Path to puzzle assets directory
            settings_system: Settings system for custom controls (optional)
        """
```

#### Core Methods

##### Game Control
```python
def start_game(self):
    """Start a new puzzle game."""
    
def pause_game(self):
    """Pause the current game."""
    
def resume_game(self):
    """Resume a paused game."""
    
def end_game(self):
    """End the current game."""
```

##### State Management
```python
def update(self):
    """Update game state for one frame."""
    
def get_state(self) -> Dict[str, Any]:
    """Get current game state."""
    
def set_state(self, state: Dict[str, Any]):
    """Set game state from dictionary."""
```

##### Piece Control
```python
def move_piece(self, direction: str):
    """Move current piece in specified direction."""
    
def rotate_piece(self, direction: str):
    """Rotate current piece in specified direction."""
    
def drop_piece(self):
    """Drop current piece to bottom."""
```

### PuzzleRenderer Class

#### Initialization
```python
class PuzzleRenderer:
    def __init__(self, engine, clock: Clock = None):
        """
        Initialize the puzzle renderer.
        
        Args:
            engine: Reference to the puzzle engine
            clock: Time source for animations (optional)
        """
```

#### Rendering Methods
```python
def render(self):
    """Render the current game state."""
    
def render_grid(self):
    """Render the puzzle grid."""
    
def render_pieces(self):
    """Render falling pieces."""
    
def render_effects(self):
    """Render visual effects and animations."""
```

### PuzzleStateIntegrator Class

#### Initialization
```python
class PuzzleStateIntegrator:
    def __init__(self, state_manager: GameStateManager, puzzle_engine):
        """
        Initialize the puzzle state integrator.
        
        Args:
            state_manager: Reference to the game state manager
            puzzle_engine: Reference to the puzzle engine
        """
```

#### Integration Methods
```python
def start_integration(self):
    """Start state integration."""
    
def stop_integration(self):
    """Stop state integration."""
    
def sync_to_state_manager(self):
    """Sync puzzle engine state to state manager."""
    
def sync_from_state_manager(self):
    """Sync state manager state to puzzle engine."""
```

## 🎯 Integration Guide

### Basic Integration

#### 1. Initialize Puzzle Engine
```python
# Create puzzle engine with state integration
puzzle_engine = PuzzleEngine(screen, font, audio_system)
state_manager = GameStateManager()
integrator = PuzzleStateIntegrator(state_manager, puzzle_engine)

# Start integration
integrator.start_integration()
```

#### 2. Game Loop Integration
```python
def game_loop():
    # Update puzzle engine
    puzzle_engine.update()
    
    # Sync state
    integrator.sync_to_state_manager()
    
    # Render
    puzzle_engine.renderer.render()
```

#### 3. State Access
```python
# Get game state
score = state_manager.get("puzzle.score")
level = state_manager.get("puzzle.level")
game_active = state_manager.get("puzzle.game_active")

# Set game state
state_manager.set("puzzle.score", new_score)
state_manager.set("puzzle.level", new_level)
```

### Advanced Integration

#### Custom State Mappings
```python
# Add custom state mappings
custom_mappings = [
    PuzzleStateMapping("custom_attr", "puzzle.custom_state", "Custom state"),
    PuzzleStateMapping("debug_mode", "puzzle.debug.enabled", "Debug mode")
]

integrator.add_custom_mappings(custom_mappings)
```

#### State Change Callbacks
```python
def on_score_changed(field_path, old_value, new_value):
    print(f"Score changed: {old_value} -> {new_value}")

# Register callback
state_manager.register_callback("puzzle.score", on_score_changed)
```

## 🧪 Testing

### Unit Testing
```python
# Test puzzle engine functionality
def test_piece_movement():
    engine = PuzzleEngine(screen, font)
    engine.start_game()
    
    # Test piece movement
    initial_pos = engine.piece_position
    engine.move_piece("right")
    assert engine.piece_position != initial_pos
```

### Integration Testing
```python
# Test state integration
def test_state_integration():
    engine = PuzzleEngine(screen, font)
    state_manager = GameStateManager()
    integrator = PuzzleStateIntegrator(state_manager, engine)
    
    # Test state synchronization
    engine.score = 100
    integrator.sync_to_state_manager()
    assert state_manager.get("puzzle.score") == 100
```

### Performance Testing
```python
# Test performance
def test_performance():
    engine = PuzzleEngine(screen, font)
    
    # Measure update performance
    start_time = time.time()
    for _ in range(1000):
        engine.update()
    end_time = time.time()
    
    assert (end_time - start_time) < 1.0  # Should complete in under 1 second
```

## 🔍 Debugging

### Common Issues

#### 1. State Inconsistency
**Problem**: Engine and state manager have different values.
**Solution**: Force sync and validate state consistency.
```python
integrator.sync_to_state_manager()
integrator.sync_from_state_manager()
assert engine.score == state_manager.get("puzzle.score")
```

#### 2. Performance Issues
**Problem**: Frame rate drops during gameplay.
**Solution**: Adjust sync interval and enable performance monitoring.
```python
integrator.sync_interval = 0.033  # 30fps instead of 60fps
engine.enable_performance_monitoring = True
```

#### 3. Memory Leaks
**Problem**: Memory usage growing over time.
**Solution**: Configure history limits and cleanup.
```python
state_manager.history.max_entries = 500
state_manager.history.clear_old_entries()
```

### Debug Tools

#### State Monitoring
```python
# Enable debug logging
import logging
logging.getLogger("modules.game_state_module").setLevel(logging.DEBUG)

# Monitor state changes
def debug_callback(field_path, old_value, new_value):
    print(f"State change: {field_path} = {old_value} -> {new_value}")

state_manager.register_callback("*", debug_callback)
```

#### Performance Monitoring
```python
# Monitor sync performance
import time

start_time = time.time()
integrator.sync_to_state_manager()
end_time = time.time()

print(f"Sync took {(end_time - start_time) * 1000:.3f}ms")
```

## 🚀 Performance Optimization

### Best Practices

#### 1. Efficient State Access
```python
# Good: Batch state changes
integrator.batch_update([
    ("puzzle.score", new_score),
    ("puzzle.level", new_level)
])

# Avoid: Individual state changes in loops
for i in range(100):
    state_manager.set(f"puzzle.block_{i}", value)
```

#### 2. Smart Sync Intervals
```python
# Adjust sync frequency based on game state
if game_active:
    integrator.sync_interval = 0.016  # 60fps during gameplay
else:
    integrator.sync_interval = 0.1   # 10fps when paused
```

#### 3. Memory Management
```python
# Configure appropriate history limits
state_manager.history.max_entries = 1000  # For debugging
state_manager.history.max_entries = 100   # For production
```

### Performance Benchmarks

| Operation | Time (ms) | Notes |
|-----------|-----------|-------|
| Engine Update | 0.5 | Full game logic update |
| State Sync | 0.016 | Full state synchronization |
| Rendering | 2.0 | Complete frame rendering |
| State Get | 0.001 | Direct state access |
| State Set | 0.002 | With validation |

## 🔮 Future Enhancements

### Planned Features

#### 1. Multiplayer Support
- Network state synchronization
- Conflict resolution
- Player state management

#### 2. Advanced AI
- AI opponent integration
- Difficulty scaling
- Adaptive gameplay

#### 3. Enhanced Visual Effects
- Particle systems
- Advanced animations
- Custom themes

#### 4. State Persistence
- Save/load game states
- Replay system
- State analytics

## 📚 Related Documentation

### Core Documentation
- **[Technical Notes](technical_notes/puzzle_engine_notes.md)** - Detailed technical implementation notes
- **[Integration Guide](../modules/game_state_module/PUZZLE_INTEGRATION_GUIDE.md)** - Step-by-step integration instructions
- **[State Schema](../modules/game_state_module/state_schema.py)** - State structure definitions

### Development Resources
- **[Developer Logs](developer_logs/developer_2_log.md)** - Development progress and insights
- **[Test Suite](../tests/consolidated/modules/game_state_module/tests/test_puzzle_integration.py)** - Comprehensive test coverage
- **[Performance Tests](../tests/consolidated/performance/test_performance_framework.py)** - Performance benchmarking

### Architecture Documents
- **[System Architecture](../ARCHITECTURE.md)** - Overall system design
- **[Module Integration](../MODULE_INTEGRATION_GUIDE.md)** - Cross-module communication
- **[State Management](../modules/game_state_module/README.md)** - State system overview

---

**Documentation**: Puzzle Engine  
**Version**: 2.0.0  
**Last Updated**: 2024-01-XX  
**Status**: Complete ✅
