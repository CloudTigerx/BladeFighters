# Attack Delivery Flow Documentation

## Overview
The attack delivery system provides animated, paced delivery of attacks from spawn to landing with configurable input locking and commit-on-landing behavior.

## Flow Architecture

### 1. Attack Spawning
- **Spawn Height**: Configurable via `attacks.spawn_height` (default: -3)
- **Spawn Mode**: Configurable via `attacks.spawn_mode` (default: "animated")
  - `animated`: Attacks spawn above grid and fall with animation
  - `instant`: Attacks appear directly on grid (legacy mode)

### 2. Pending Landings System
- Attacks are tracked in `pending_landings` during fall animation
- Each pending landing includes:
  - `target_player`: 'player' or 'enemy'
  - `attack_type`: 'garbage' or 'strike'
  - `count`: Number of blocks
  - `pattern`: Block arrangement
  - `created_ms`: Timestamp when attack was created
  - `start_y`: Initial spawn position
  - `current_y`: Current fall position

### 3. Commit-on-Landing
- Attacks are committed to the grid only when they reach the landing position
- No on-grid spawning - all attacks must fall from above
- Grid state is updated atomically when landing occurs

### 4. Input Lock Window
- Input is locked during attack delivery to prevent interference
- Lock duration matches animation timing
- Configurable per-board via runtime locks
- Optional enemy-side toggle for PvP scenarios

## Configuration Keys

### Core Attack Settings
```json
{
  "attacks.spawn_mode": "animated",
  "attacks.spawn_height": -3,
  "attacks.input_lock_enabled": true,
  "attacks.enemy_input_lock": false
}
```

### Animation Timing
- **Fall Duration**: 1.1 seconds from top to bottom (13 rows)
- **Per-Row Duration**: ~85ms per row
- **Lock Window**: Aligned with animation duration

## Cross-Resolution Invariants

### Grid Coordinates
- All grid operations use logical coordinates (0-11 x 0-12)
- Resolution scaling handles visual rendering
- Attack patterns and positions are resolution-independent

### Testing Approach
- Unit tests use logical coordinates
- Integration tests verify cross-resolution behavior
- Performance tests validate timing consistency

## Replay System Integration

### Pending Landings Recording
- Replay system records `pending_landings` state
- Lock timing is preserved for accurate replay
- Animation state is captured for visual consistency

### Timing Preservation
- All timestamps are stored in milliseconds
- Relative timing is maintained across replay sessions
- Input lock windows are faithfully reproduced

## Follow-up Features

### Optional Enemy Input Lock
- Configurable toggle for enemy-side input locking
- Useful for PvP scenarios where enemy should maintain control
- Default: disabled (enemy keeps input during attacks)

### Configurable Spawn Height
- `attacks.spawn_height` allows customization
- Default: -3 (3 rows above visible grid)
- Range: -10 to 0 (safety limits)

### Replay Enhancement
- Ensure replay records include pending_landings timing
- Preserve lock window information
- Maintain animation state for visual accuracy

## Implementation Notes

### Performance Considerations
- Minimal impact during normal gameplay
- Only active during attack delivery windows
- Efficient state management for pending landings

### Compatibility
- No breaking changes to existing APIs
- Backward compatible with instant spawn mode
- Graceful fallback for missing configuration

### Testing Strategy
- Unit tests for individual components
- Integration tests for full delivery flow
- Cross-resolution validation tests
- Performance benchmarks for timing consistency
