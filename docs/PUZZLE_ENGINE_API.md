# 🧩 Puzzle Engine API Reference

## 📋 Overview

This document provides a comprehensive API reference for the BladeFighters Puzzle Engine. It covers all public methods, classes, and interfaces that developers can use to interact with the puzzle system.

## 🏗️ Core Classes

### PuzzleEngine

The main puzzle game engine class that handles all game mechanics and state management.

#### Class Definition
```python
class PuzzleEngine:
    """
    Puzzle game engine for the BladeFighters game.
    This module handles the puzzle game mechanics and rendering.
    """
```

#### Constructor
```python
def __init__(self, screen, font, audio=None, asset_path="puzzleassets", 
             settings_system=None, clock=None):
    """
    Initialize the puzzle engine.
    
    Args:
        screen: Pygame display surface
        font: Pygame font for text rendering
        audio: Audio system for sound effects (optional)
        asset_path: Path to puzzle assets directory
        settings_system: Settings system for custom controls (optional)
        clock: Time source for animations (optional)
    """
```

#### Game Control Methods

##### start_game()
```python
def start_game(self):
    """
    Start a new puzzle game.
    
    Initializes the game state, creates new pieces, and begins gameplay.
    Sets game_active to True and resets all game variables.
    """
```

##### pause_game()
```python
def pause_game(self):
    """
    Pause the current game.
    
    Stops game updates while maintaining the current state.
    Can be resumed with resume_game().
    """
```

##### resume_game()
```python
def resume_game(self):
    """
    Resume a paused game.
    
    Restarts game updates from the paused state.
    """
```

##### end_game()
```python
def end_game(self):
    """
    End the current game.
    
    Stops gameplay and sets game_active to False.
    Cleans up game state and triggers game over sequence.
    """
```

##### reset_game(self)
```python
def reset_game(self):
    """
    Reset the game to initial state.
    
    Clears the grid, resets score and level, and prepares for a new game.
    """
```

#### State Management Methods

##### update()
```python
def update(self):
    """
    Update game state for one frame.
    
    Processes input, updates piece positions, checks for clusters,
    and manages game timing. Should be called every frame.
    """
```

##### get_state()
```python
def get_state(self) -> Dict[str, Any]:
    """
    Get current game state as a dictionary.
    
    Returns:
        Dictionary containing all current game state variables
    """
```

##### set_state()
```python
def set_state(self, state: Dict[str, Any]):
    """
    Set game state from a dictionary.
    
    Args:
        state: Dictionary containing game state variables
    """
```

##### get_score()
```python
def get_score(self) -> int:
    """
    Get current game score.
    
    Returns:
        Current score value
    """
```

##### add_score()
```python
def add_score(self, points: int):
    """
    Add points to the current score.
    
    Args:
        points: Points to add to the score
    """
```

#### Piece Control Methods

##### move_piece()
```python
def move_piece(self, direction: str):
    """
    Move current piece in specified direction.
    
    Args:
        direction: Direction to move ("left", "right", "down")
    """
```

##### rotate_piece()
```python
def rotate_piece(self, direction: str):
    """
    Rotate current piece in specified direction.
    
    Args:
        direction: Rotation direction ("clockwise", "counterclockwise")
    """
```

##### drop_piece()
```python
def drop_piece(self):
    """
    Drop current piece to the bottom of the grid.
    
    Instantly moves the piece to the lowest possible position.
    """
```

##### hard_drop()
```python
def hard_drop(self):
    """
    Perform a hard drop of the current piece.
    
    Drops the piece and locks it in place immediately.
    """
```

#### Grid Management Methods

##### get_grid()
```python
def get_grid(self) -> List[List[int]]:
    """
    Get the current puzzle grid.
    
    Returns:
        2D list representing the grid state
    """
```

##### set_grid()
```python
def set_grid(self, grid: List[List[int]]):
    """
    Set the puzzle grid to a specific state.
    
    Args:
        grid: 2D list representing the desired grid state
    """
```

##### clear_grid()
```python
def clear_grid(self):
    """
    Clear the entire puzzle grid.
    
    Removes all blocks from the grid.
    """
```

##### is_valid_position()
```python
def is_valid_position(self, piece, x: int, y: int) -> bool:
    """
    Check if a piece position is valid.
    
    Args:
        piece: Piece to check
        x: X coordinate
        y: Y coordinate
    
    Returns:
        True if position is valid, False otherwise
    """
```

#### Cluster Detection Methods

##### find_clusters()
```python
def find_clusters(self) -> List[List[Tuple[int, int]]]:
    """
    Find all clusters in the current grid.
    
    Returns:
        List of clusters, where each cluster is a list of (x, y) coordinates
    """
```

##### break_clusters()
```python
def break_clusters(self, clusters: List[List[Tuple[int, int]]]):
    """
    Break specified clusters and trigger animations.
    
    Args:
        clusters: List of clusters to break
    """
```

##### check_chain_reaction()
```python
def check_chain_reaction(self) -> bool:
    """
    Check if a chain reaction should occur.
    
    Returns:
        True if chain reaction should occur, False otherwise
    """
```

#### Configuration Methods

##### set_difficulty()
```python
def set_difficulty(self, difficulty: str):
    """
    Set the game difficulty level.
    
    Args:
        difficulty: Difficulty level ("easy", "normal", "hard")
    """
```

##### set_fall_speed()
```python
def set_fall_speed(self, speed: float):
    """
    Set the piece falling speed.
    
    Args:
        speed: Fall speed in seconds per grid cell
    """
```

##### enable_debug_mode()
```python
def enable_debug_mode(self, enabled: bool):
    """
    Enable or disable debug mode.
    
    Args:
        enabled: True to enable debug mode, False to disable
    """
```

### PuzzleRenderer

Handles all visual rendering and animation for the puzzle game.

#### Class Definition
```python
class PuzzleRenderer:
    """
    Handles rendering and visual effects for the puzzle game.
    This class separates rendering logic from game mechanics.
    """
```

#### Constructor
```python
def __init__(self, engine, clock: Clock = None):
    """
    Initialize the puzzle renderer.
    
    Args:
        engine: Reference to the puzzle engine
        clock: Time source for animations (optional)
    """
```

#### Rendering Methods

##### render()
```python
def render(self):
    """
    Render the current game state.
    
    Renders the grid, pieces, effects, and UI elements.
    Should be called every frame after engine.update().
    """
```

##### render_grid()
```python
def render_grid(self):
    """
    Render the puzzle grid.
    
    Draws all blocks in the grid with their current states.
    """
```

##### render_pieces()
```python
def render_pieces(self):
    """
    Render falling pieces.
    
    Draws the current and next pieces with their positions.
    """
```

##### render_effects()
```python
def render_effects(self):
    """
    Render visual effects and animations.
    
    Draws explosions, particle effects, and other visual feedback.
    """
```

##### render_ui()
```python
def render_ui(self):
    """
    Render user interface elements.
    
    Draws score, level, next piece preview, and other UI elements.
    """
```

#### Animation Methods

##### start_breaking_animation()
```python
def start_breaking_animation(self, blocks: List[Tuple[int, int]]):
    """
    Start breaking animation for specified blocks.
    
    Args:
        blocks: List of (x, y) coordinates of blocks to animate
    """
```

##### update_animations()
```python
def update_animations(self):
    """
    Update all active animations.
    
    Advances animation frames and removes completed animations.
    """
```

##### is_animation_active()
```python
def is_animation_active(self) -> bool:
    """
    Check if any animations are currently active.
    
    Returns:
        True if animations are active, False otherwise
    """
```

### PuzzleStateIntegrator

Integration layer that connects the puzzle engine to the unified state management system.

#### Class Definition
```python
class PuzzleStateIntegrator:
    """
    Integrates puzzle engine state with the unified GameStateManager.
    Provides methods to sync state between the puzzle engine and state manager.
    """
```

#### Constructor
```python
def __init__(self, state_manager: GameStateManager, puzzle_engine):
    """
    Initialize the puzzle state integrator.
    
    Args:
        state_manager: Reference to the game state manager
        puzzle_engine: Reference to the puzzle engine
    """
```

#### Integration Methods

##### start_integration()
```python
def start_integration(self):
    """
    Start state integration.
    
    Begins bidirectional synchronization between puzzle engine and state manager.
    """
```

##### stop_integration()
```python
def stop_integration(self):
    """
    Stop state integration.
    
    Stops synchronization between puzzle engine and state manager.
    """
```

##### sync_to_state_manager()
```python
def sync_to_state_manager(self):
    """
    Sync puzzle engine state to state manager.
    
    Updates state manager with current puzzle engine state.
    """
```

##### sync_from_state_manager()
```python
def sync_from_state_manager(self):
    """
    Sync state manager state to puzzle engine.
    
    Updates puzzle engine with current state manager state.
    """
```

##### add_custom_mappings()
```python
def add_custom_mappings(self, mappings: List[PuzzleStateMapping]):
    """
    Add custom state mappings.
    
    Args:
        mappings: List of custom state mappings to add
    """
```

##### get_state_value()
```python
def get_state_value(self, path: str, default: Any = None) -> Any:
    """
    Get a value from the state manager.
    
    Args:
        path: State path to retrieve
        default: Default value if path doesn't exist
    
    Returns:
        Value at the specified path
    """
```

##### set_state_value()
```python
def set_state_value(self, path: str, value: Any):
    """
    Set a value in the state manager.
    
    Args:
        path: State path to set
        value: Value to set
    """
```

## 📊 Data Structures

### PuzzleStateMapping

Represents a mapping between puzzle engine attributes and state manager paths.

```python
@dataclass
class PuzzleStateMapping:
    """Maps puzzle engine variables to state manager paths."""
    engine_attr: str      # Puzzle engine attribute name
    state_path: str       # State manager path
    description: str      # Human-readable description
    default_value: Any    # Default value (optional)
```

### BlockType

Enumeration of block types in the puzzle game.

```python
class BlockType(Enum):
    EMPTY = auto()        # Empty space
    RED = auto()          # Red block
    BLUE = auto()         # Blue block
    GREEN = auto()        # Green block
    YELLOW = auto()       # Yellow block
```

### GameState

Represents the complete game state structure.

```python
@dataclass
class PuzzleState:
    game_active: bool = False
    score: int = 0
    level: int = 1
    grid: List[List[int]] = field(default_factory=list)
    current_piece: Optional[Dict] = None
    next_piece: Optional[Dict] = None
    # ... additional fields
```

## 🔧 Configuration

### Engine Configuration

The puzzle engine can be configured through various methods:

```python
# Set difficulty
puzzle_engine.set_difficulty("normal")

# Set fall speed
puzzle_engine.set_fall_speed(1.0)

# Enable debug mode
puzzle_engine.enable_debug_mode(True)

# Configure grid size
puzzle_engine.grid_width = 6
puzzle_engine.grid_height = 12
```

### Renderer Configuration

The renderer can be configured for different visual effects:

```python
# Set animation speed
puzzle_engine.renderer.animation_speed = 1.0

# Enable/disable effects
puzzle_engine.renderer.enable_particles = True
puzzle_engine.renderer.enable_screen_shake = False

# Set quality level
puzzle_engine.renderer.quality_level = "high"
```

### State Integration Configuration

The state integrator can be configured for performance:

```python
# Set sync interval
integrator.sync_interval = 0.016  # 60fps

# Enable performance optimization
integrator.enable_performance_optimization = True

# Set batch update size
integrator.batch_size = 10
```

## 🎯 Usage Examples

### Basic Game Setup

```python
# Initialize puzzle engine
puzzle_engine = PuzzleEngine(screen, font, audio_system)
state_manager = GameStateManager()
integrator = PuzzleStateIntegrator(state_manager, puzzle_engine)

# Start integration
integrator.start_integration()

# Start game
puzzle_engine.start_game()
```

### Game Loop

```python
def game_loop():
    # Handle input
    handle_input()
    
    # Update game state
    puzzle_engine.update()
    
    # Sync state
    integrator.sync_to_state_manager()
    
    # Render
    puzzle_engine.renderer.render()
    
    # Update display
    pygame.display.flip()
```

### State Access

```python
# Get game state
score = state_manager.get("puzzle.score")
level = state_manager.get("puzzle.level")
game_active = state_manager.get("puzzle.game_active")

# Set game state
state_manager.set("puzzle.score", new_score)
state_manager.set("puzzle.level", new_level)

# Listen for state changes
def on_score_changed(field_path, old_value, new_value):
    print(f"Score changed: {old_value} -> {new_value}")

state_manager.register_callback("puzzle.score", on_score_changed)
```

### Custom State Integration

```python
# Add custom state mappings
custom_mappings = [
    PuzzleStateMapping("custom_attr", "puzzle.custom_state", "Custom state"),
    PuzzleStateMapping("debug_mode", "puzzle.debug.enabled", "Debug mode")
]

integrator.add_custom_mappings(custom_mappings)

# Access custom state
custom_value = integrator.get_state_value("puzzle.custom_state")
integrator.set_state_value("puzzle.debug.enabled", True)
```

## 🚨 Error Handling

### Common Exceptions

#### ValidationError
Raised when state validation fails.

```python
try:
    state_manager.set("puzzle.score", -100)
except ValidationError as e:
    print(f"Invalid score value: {e}")
```

#### IntegrationError
Raised when state integration fails.

```python
try:
    integrator.sync_to_state_manager()
except IntegrationError as e:
    print(f"Integration failed: {e}")
```

#### RenderingError
Raised when rendering operations fail.

```python
try:
    puzzle_engine.renderer.render()
except RenderingError as e:
    print(f"Rendering failed: {e}")
```

### Error Recovery

```python
# Graceful error handling
def safe_update():
    try:
        puzzle_engine.update()
        integrator.sync_to_state_manager()
        puzzle_engine.renderer.render()
    except Exception as e:
        logger.error(f"Game update failed: {e}")
        # Fallback to safe state
        puzzle_engine.pause_game()
```

## 📚 Related Documentation

- **[Puzzle Engine Documentation](PUZZLE_ENGINE_DOCUMENTATION.md)** - Comprehensive puzzle engine guide
- **[Technical Notes](technical_notes/puzzle_engine_notes.md)** - Technical implementation details
- **[Integration Guide](../modules/game_state_module/PUZZLE_INTEGRATION_GUIDE.md)** - Integration instructions
- **[State Schema](../modules/game_state_module/state_schema.py)** - State structure definitions

---

**API Reference**: Puzzle Engine  
**Version**: 2.0.0  
**Last Updated**: 2024-01-XX  
**Status**: Complete ✅
