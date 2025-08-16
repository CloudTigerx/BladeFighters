# Future Enhancements & Follow-up Tasks

## 🚀 Immediate Follow-ups

### Optional Enemy-Side Input Lock Toggle
**Priority**: High  
**Status**: Planned

```python
# Configuration for PvP input locking
"attacks.enemy_input_lock": true  # Lock enemy input during attacks
```

**Implementation**:
- Add configuration option to `unified_config.py`
- Extend lock logic in `_place_garbage_attack()` and `_place_strike_attack()`
- Add tests for enemy-side locking behavior

### Configurable Spawn Height
**Priority**: Medium  
**Status**: Planned

```json
{
  "attacks.spawn_height": -3
}
```

**Implementation**:
- Add configuration schema to `unified_config.py`
- Replace hardcoded `spawn_height = -3` with configurable value
- Add validation for reasonable spawn height ranges
- Update tests to verify configurable behavior

### Replay Integration
**Priority**: Medium  
**Status**: Planned

```python
# Record pending_landings and lock timing in replays
replay_data = {
    "pending_landings": pending_landings,
    "lock_timing": lock_timing,
    "animation_duration": animation_duration
}
```

**Implementation**:
- Extend replay system to capture attack delivery timing
- Record `pending_landings` state for replay accuracy
- Include lock timing information for precise replay
- Add tests for replay fidelity

## 🎯 Dev 3 Tasks (Uneven-column Sliding)

### Smooth Sliding Animation
**Priority**: High  
**Status**: Pending

**Goal**: When pieces separate on uneven columns, animate the continued fall at the same pace as breaking/normal fall (no teleport).

**Implementation**:
```python
# In core/puzzle_module.PuzzleEngine._handle_piece_sliding
for any block that must descend more than 1 row due to separation:
    enqueue a visual fall via animation_state_manager.visual_falling_blocks[(x, target_y)] with:
        duration = asm.fall_animation_duration * (target_y - current_y)
        start_y = current_y
```

**Tests**:
- Add scenario-based test mirroring `UNEVEN_COLUMN_TELEPORTATION_FIX.md`
- Set uneven columns; drop a pair where one lands and the other should slide down
- Assert no intermediate teleport: animation exists and completes before block is at final grid pos

## 🎯 Dev 4 Tasks (Scaling and Resolution)

### Cross-Resolution Testing
**Priority**: High  
**Status**: Planned

**Goal**: Ensure attack spawn and animation use grid-space (rows), not pixels.

**Implementation**:
```python
# Parametrize integration test over two resolutions
@pytest.mark.parametrize("resolution", [(1280, 720), (2560, 1440)])
def test_attack_delivery_resolution_independent(resolution):
    # Queue the same attack
    # Verify identical landing columns/rows
    # Verify identical pending_landings contents
    # Verify only visual positions differ by pixel scale, not by grid cell
```

**Audit Points**:
- Attack spawn and animation use grid-space (rows), not pixels
- `start_y = -3` remains constant across resolutions
- Board offsets come from `asset_scaler.calculate_dual_grid_layout`
- No hardcoded pixel math in spawn/land paths
- `core/scaling/coordinate_system.py` and renderer conversions are the only pixel-space conversions

## 🔧 Technical Improvements

### Enhanced Error Handling
**Priority**: Medium  
**Status**: Planned

**Areas**:
- Attack delivery failure recovery
- Animation state corruption handling
- Lock timing edge cases
- Cross-component communication errors

### Performance Optimization
**Priority**: Low  
**Status**: Planned

**Areas**:
- Animation batch processing optimization
- Memory usage optimization for pending queues
- Lock management performance
- Cross-resolution rendering optimization

### Code Quality
**Priority**: Low  
**Status**: Planned

**Areas**:
- Type annotations completion
- Documentation coverage
- Code complexity reduction
- Test coverage expansion

## 🎮 Gameplay Enhancements

### Visual Feedback
**Priority**: Medium  
**Status**: Planned

**Features**:
- Attack preview indicators
- Lock duration visual feedback
- Animation smoothness improvements
- Resolution-specific visual optimizations

### Accessibility
**Priority**: Low  
**Status**: Planned

**Features**:
- Configurable animation speeds
- Visual lock indicators
- Audio feedback for attack delivery
- High contrast mode support

## 📊 Monitoring & Analytics

### Performance Metrics
**Priority**: Medium  
**Status**: Planned

**Metrics**:
- Animation frame rates
- Lock timing accuracy
- Memory usage patterns
- Cross-resolution performance

### Debug Tools
**Priority**: Low  
**Status**: Planned

**Tools**:
- Attack delivery timing visualization
- Lock state debugging tools
- Animation state inspection
- Performance profiling integration

## 🔄 Integration Tasks

### Module Integration
**Priority**: High  
**Status**: Planned

**Tasks**:
- Integrate with audio module for attack sound effects
- Connect with UI module for visual feedback
- Integrate with settings module for configuration
- Connect with replay module for timing accuracy

### External Systems
**Priority**: Low  
**Status**: Planned

**Tasks**:
- Network synchronization for multiplayer
- Save/load system integration
- Modding support for custom animations
- Plugin system for attack delivery extensions

## 📋 Implementation Checklist

### Dev 3 (Sliding)
- [ ] Implement smooth sliding animation in `_handle_piece_sliding`
- [ ] Add visual fall animation for multi-row separation
- [ ] Create scenario-based test for uneven column behavior
- [ ] Verify no teleportation during sliding

### Dev 4 (Scaling)
- [ ] Audit all spawn/land paths for grid-space usage
- [ ] Create cross-resolution parametrized tests
- [ ] Verify resolution independence of attack delivery
- [ ] Document coordinate system usage

### Configuration
- [ ] Add enemy input lock configuration
- [ ] Add configurable spawn height
- [ ] Add validation for configuration values
- [ ] Update configuration documentation

### Replay System
- [ ] Extend replay data structure
- [ ] Record pending landings timing
- [ ] Record lock timing information
- [ ] Add replay fidelity tests

## 🎯 Success Criteria

### Functional Requirements
- ✅ Animated delivery with no on-grid spawn
- ✅ Windowed input locks aligned with animation
- ✅ Resolution-independent grid coordinates
- ✅ Smooth sliding without teleportation
- ✅ Configurable attack delivery behavior

### Quality Requirements
- ✅ Comprehensive test coverage
- ✅ Performance validation
- ✅ Cross-resolution invariance
- ✅ Backward compatibility
- ✅ Documentation completeness

### Technical Requirements
- ✅ Component-based architecture
- ✅ Proper error handling
- ✅ Memory management
- ✅ Code quality standards
- ✅ Debugging capabilities

## 📈 Metrics & KPIs

### Performance Metrics
- Animation frame rate: Target 60 FPS
- Lock timing accuracy: Target ±1ms
- Memory usage: Target <1MB per board
- Cross-resolution performance: Target <5% variance

### Quality Metrics
- Test coverage: Target >90%
- Code complexity: Target <10 cyclomatic complexity
- Documentation coverage: Target 100%
- Bug rate: Target <1 bug per 1000 lines

### User Experience Metrics
- Animation smoothness: Target 60 FPS
- Input responsiveness: Target <16ms latency
- Visual consistency: Target identical behavior across resolutions
- Accessibility compliance: Target WCAG 2.1 AA
