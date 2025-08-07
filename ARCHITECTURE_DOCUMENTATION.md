# Blade Fighters - Current Architecture Documentation

## Overview

Blade Fighters is a puzzle-based fighting game with a monolithic architecture. This document maps out how all components interact and depend on each other.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        GAME CLIENT                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Main Menu     │  │   Settings      │  │   Quickplay     │ │
│  │   System        │  │   System        │  │   Mode          │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        TEST MODE                                │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │  Player Engine  │  │  Enemy Engine   │  │  Attack System  │ │
│  │  (PuzzleEngine) │  │  (PuzzleEngine) │  │                 │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
│           │                     │                     │         │
│           ▼                     ▼                     ▼         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ Player Renderer │  │ Enemy Renderer  │  │  AI Controller  │ │
│  │                 │  │                 │  │                 │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. GameClient (game_client.py)
**Purpose:** Main application controller and screen manager
**Dependencies:**
- TestMode (for testing mode)
- Menu systems
- Audio system
- Asset management

**Key Methods:**
- `run()` - Main game loop
- `set_screen()` - Screen transitions
- `process_events()` - Event handling

**Integration Points:**
```python
# Creates TestMode instance
self.test_mode = TestMode(self.screen, self.font, self.audio, self.asset_path)

# Manages screen transitions
self.current_screen = "main_menu" | "settings" | "game"
```

### 2. TestMode (game_client.py)
**Purpose:** Battle mode controller for AI vs Player
**Dependencies:**
- Two PuzzleEngine instances (player/enemy)
- Two PuzzleRenderer instances
- AttackSystem
- AI controller

**Key Methods:**
- `draw()` - Main rendering loop
- `update()` - Game state updates
- `handle_player_blocks_broken()` - Attack generation
- `handle_enemy_blocks_broken()` - AI attack generation

**Integration Points:**
```python
# Creates engines and renderers
self.player_engine = PuzzleEngine(screen, font, audio, asset_path)
self.enemy_engine = PuzzleEngine(screen, font, None, asset_path)
self.player_renderer = PuzzleRenderer(self.player_engine)
self.enemy_renderer = PuzzleRenderer(self.enemy_engine)

# Sets up attack system
self.attack_system = AttackSystem(grid_width=6, grid_height=13)
```

### 3. PuzzleEngine (puzzle_module.py)
**Purpose:** Core game logic and state management
**Dependencies:**
- AttackSystem (via test_mode reference)
- Audio system
- Asset loading

**Key Methods:**
- `update()` - Game loop updates
- `place_piece_on_grid()` - Piece placement logic
- `detect_clusters()` - Combo detection
- `apply_gravity()` - Physics simulation

**Integration Points:**
```python
# References to external systems
self.test_mode = None  # Set by TestMode
self.audio = audio     # Audio system reference
self.renderer = None   # Set by PuzzleRenderer

# Attack system integration
if hasattr(self, 'test_mode') and hasattr(self.test_mode, 'attack_system'):
    updated_blocks = self.test_mode.attack_system.decrement_garbage_block_turns(player_number)
```

### 4. PuzzleRenderer (puzzle_renderer.py)
**Purpose:** Visual rendering and effects
**Dependencies:**
- PuzzleEngine (for game state)
- Pygame (for rendering)
- Asset loading

**Key Methods:**
- `draw_game_screen()` - Main rendering
- `draw_grid_blocks()` - Grid rendering
- `show_combo_text()` - Combo effects
- `update_combo_texts()` - Particle effects

**Integration Points:**
```python
# Engine reference
self.engine = puzzle_engine
self.engine.renderer = self  # Circular reference

# Attack system integration for garbage blocks
if hasattr(self.engine, 'attack_system') and self.engine.attack_system:
    if (grid_x, grid_y) in self.engine.attack_system.garbage_blocks:
        # Render garbage block states
```

### 5. AttackSystem (attack_system.py)
**Purpose:** Combat mechanics and attack generation
**Dependencies:**
- Grid structure (tightly coupled)
- Time-based transformations

**Key Methods:**
- `generate_attack()` - Attack creation
- `process_attack_queue()` - Attack execution
- `update_garbage_blocks()` - Block transformations

**Integration Points:**
```python
# Direct grid modification (tight coupling)
target_grid[target_y][column] = block_type

# Shared state with engines
self.garbage_blocks = {}  # (x, y) -> (start_time, color)
```

## Data Flow

### 1. Game Loop Flow
```
GameClient.run()
    ↓
TestMode.update()
    ↓
PlayerEngine.update() + EnemyEngine.update()
    ↓
AttackSystem.process_attack_queue()
    ↓
TestMode.draw()
    ↓
PlayerRenderer.draw_game_screen() + EnemyRenderer.draw_game_screen()
```

### 2. Combo/Attack Flow
```
PuzzleEngine.place_piece_on_grid()
    ↓
PuzzleEngine.detect_clusters()
    ↓
PuzzleEngine.clear_breaking_blocks()
    ↓
TestMode.handle_player_blocks_broken()
    ↓
AttackSystem.generate_attack()
    ↓
AttackSystem.add_attacks_to_queue()
    ↓
AttackSystem.process_attack_queue() (next frame)
```

### 3. Rendering Flow
```
TestMode.draw()
    ↓
PlayerRenderer.draw_grid_blocks()
    ↓
PuzzleRenderer._draw_block()
    ↓
PuzzleRenderer.show_combo_text() (if combo)
    ↓
PuzzleRenderer.update_combo_texts() (particle effects)
```

## Dependencies Analysis

### Tight Couplings (Hard to Separate)

1. **PuzzleEngine ↔ AttackSystem**
   - Engine directly calls attack system methods
   - Attack system directly modifies engine's grid
   - Shared state (garbage_blocks)

2. **PuzzleEngine ↔ PuzzleRenderer**
   - Circular references
   - Renderer accesses engine's internal state
   - Engine sets renderer reference

3. **TestMode ↔ PuzzleEngine**
   - TestMode creates and manages engines
   - Engines reference back to TestMode
   - Shared attack system instance

### Loose Couplings (Easier to Separate)

1. **Audio System**
   - Simple interface (play_sound method)
   - Optional dependency
   - No shared state

2. **Asset Loading**
   - File-based loading
   - No runtime dependencies
   - Can be replaced easily

## State Management

### Global State
- `GameClient.current_screen` - Current game mode
- `TestMode.ai_difficulty` - AI behavior settings
- `TestMode.ai_style` - AI personality

### Engine State
- `PuzzleEngine.puzzle_grid` - Game board
- `PuzzleEngine.main_piece` - Current falling piece
- `PuzzleEngine.chain_reaction_in_progress` - Combo state

### Attack System State
- `AttackSystem.player1_attacks` - Attack queues
- `AttackSystem.garbage_blocks` - Block transformation timers
- `AttackSystem.strike_blocks` - Strike block timers

### Renderer State
- `PuzzleRenderer.combo_texts` - Active combo effects
- `PuzzleRenderer.particle_surfaces` - Cached particle graphics
- `PuzzleRenderer.breaking_blocks_animations` - Animation state

## Error Handling

### Current Error Handling
- **Minimal** - Most errors crash the game
- **Debug prints** - Console output for debugging
- **Try/catch blocks** - Recently added for pygame drawing

### Error Propagation
```
Pygame Error → PuzzleRenderer → PuzzleEngine → TestMode → GameClient
```

## Performance Considerations

### Bottlenecks
1. **Particle effects** - Many small pygame.draw calls
2. **Grid rendering** - Redraws entire grid every frame
3. **Combo detection** - Scans entire grid for clusters
4. **Animation updates** - Multiple animation systems running

### Optimizations
1. **Surface caching** - Cached particle graphics
2. **Batch rendering** - Grouped pygame.draw calls
3. **Dirty rectangles** - Partial screen updates (planned)
4. **Frame limiting** - 60 FPS cap

## Testing Strategy

### Current Testing
- **Manual testing** - Play the game
- **Debug prints** - Console output
- **Visual verification** - Check if it looks right

### Missing Testing
- **Unit tests** - Individual component testing
- **Integration tests** - Component interaction testing
- **Automated testing** - CI/CD pipeline
- **Performance testing** - Frame rate monitoring

## Configuration Management

### Hardcoded Values
- Grid dimensions (6x13)
- Block sizes (65px)
- Animation timings
- Audio file paths

### Configurable Values
- AI difficulty (1-10)
- AI style (water/fire/earth/lightning)
- Screen resolution
- Audio volume

## Security Considerations

### Current Security
- **File loading** - Direct file system access
- **No input validation** - Assumes valid data
- **No network security** - Local only

### Potential Issues
- **Asset loading** - Could load malicious files
- **Save files** - No validation
- **Configuration** - No sanitization

## Future Considerations

### Scalability Issues
1. **Monolithic structure** - Hard to scale individual components
2. **Tight coupling** - Changes affect multiple systems
3. **State management** - Complex state interactions
4. **Performance** - Single-threaded architecture

### Modularization Opportunities
1. **Event system** - Decouple components
2. **Plugin architecture** - Extensible features
3. **Service layer** - Abstract external dependencies
4. **Configuration system** - External configuration files

## Conclusion

The current architecture is functional but tightly coupled. While it works for the current scope, it would benefit from:

1. **Interface abstraction** - Define clear contracts between components
2. **Event-driven architecture** - Reduce direct dependencies
3. **Configuration externalization** - Make settings configurable
4. **Testing infrastructure** - Automated verification
5. **Documentation** - This document is a start!

The system is not impossible to refactor, but it requires careful planning and incremental changes to avoid breaking existing functionality. 