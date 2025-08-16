# Release Notes v1.1.0 - Attack Delivery & Locking System

## 🎯 Overview

This release introduces a comprehensive refactor of the attack delivery system, providing animated delivery with proper input locking and resolution-independent coordinates. The system now ensures smooth gameplay with no on-grid spawns and proper timing controls.

## ✨ New Features

### Animated Attack Delivery
- **Spawn Above Board**: Attacks now spawn 3 rows above the visible board
- **Falling Animation**: Visual falling animation using `animation_state_manager`
- **Pending Landings**: Blocks are queued until animation completes
- **Commit on Landing**: Grid is only updated after animation finishes

### Windowed Input Locking
- **Full Animation Coverage**: Input locks persist for the entire animation duration
- **Spawn Pause**: New piece spawning is paused during attack delivery
- **Runtime Management**: Locks managed via `BoardRuntime` objects with proper expiration

### Resolution Independence
- **Grid Coordinates**: All logic operates on grid coordinates (rows/columns)
- **Pixel Conversion**: Only rendering converts to pixel coordinates
- **Cross-Resolution Testing**: Same attacks produce identical grid results across resolutions

## 🔧 Configuration

### Default Settings
```json
{
  "attacks.spawn_mode": "animated"
}
```

### Spawn Height
- **Default**: -3 (3 rows above visible board)
- **Resolution-independent**: Same behavior across all screen sizes

## 🧪 Testing

### Comprehensive Test Coverage
- **Lock Window Testing**: Verifies input locks persist during animation
- **Delivery Animation Testing**: Ensures no grid changes until animation completes
- **Cross-Resolution Testing**: Validates identical behavior across resolutions
- **Strike Block Testing**: Confirms proper placement after falling animation

### Test Results
- ✅ `test_locks_per_board.py`: 4/4 tests passing
- ✅ `test_attacks_delivery_animated.py`: 2/2 tests passing
- ✅ Cross-resolution invariance verified
- ✅ Smoke tests completed

## 🏗️ Architecture Improvements

### Component-Based Design
- **TestModeRefactored**: Main orchestrator with component-based architecture
- **BoardRuntime**: Manages time-based input and chain locks
- **AttackCoordinator**: Coordinates attack flow and delivery
- **GameStateManager**: Manages overall game state and runtime locks

### Backward Compatibility
- **TestMode Alias**: `TestMode = TestModeRefactored` for legacy imports
- **Runtime Shims**: `player_runtime`, `enemy_runtime` exposed for tests
- **Service Access**: `attacks_service` available via coordinator

## 🐛 Bug Fixes

### Critical Fixes
- **Runtime Object Initialization**: Fixed `BoardRuntime` creation and linking
- **Lock Application**: Resolved input lock not being applied during attacks
- **Attack Queue Management**: Fixed pending attacks not being processed
- **Strike Block Type**: Updated to `'orange_strike'` for proper detection

### Performance Improvements
- **Animation Performance**: Visual animations don't block game logic
- **Batch Processing**: Multiple attacks processed together efficiently
- **Memory Management**: Automatic cleanup of expired animations and states

## 📚 Documentation

### New Documentation
- **Attack Delivery Flow**: Comprehensive guide to the new system
- **Configuration Guide**: Details on spawn modes and settings
- **Testing Strategy**: Cross-resolution and lock window testing approach
- **Migration Notes**: Guide for transitioning from legacy system

### Updated Documentation
- **API Documentation**: Updated for new component interfaces
- **Developer Notes**: Added debugging and troubleshooting guides

## 🚀 Future Enhancements

### Planned Features
- **Optional Enemy-Side Input Lock**: Toggle for PvP input locking
- **Configurable Spawn Height**: Runtime configuration of spawn position
- **Replay Integration**: Record pending landings and lock timing in replays

### Technical Debt
- **Code Cleanup**: Removed debug print statements, using proper logging
- **Error Handling**: Enhanced exception handling throughout the system
- **Type Safety**: Improved type annotations and validation

## 🔄 Migration Guide

### From Legacy System
1. **On-Grid Spawn**: Direct `grid[0][col]` writes have been removed
2. **Instant Placement**: Replaced with animated delivery system
3. **Simple Freezes**: Enhanced with windowed locks for better timing

### Breaking Changes
- **Attack Placement**: Attacks now spawn above board instead of on-grid
- **Lock Timing**: Input locks now cover full animation duration
- **Runtime Objects**: New `BoardRuntime` objects for lock management

### Compatibility
- **Test Compatibility**: All existing tests updated and passing
- **API Compatibility**: Backward-compatible shims provided
- **Configuration**: Default settings ensure smooth transition

## 📊 Performance Metrics

### Animation Performance
- **Visual Only**: Animations don't impact game logic performance
- **Batch Processing**: Efficient handling of multiple simultaneous attacks
- **Memory Usage**: Minimal overhead for animation state management

### Lock Performance
- **Time-Based**: Efficient timestamp-based lock management
- **Automatic Cleanup**: Expired locks automatically cleared
- **Minimal Overhead**: Runtime objects have minimal memory footprint

## 🎮 Gameplay Impact

### Player Experience
- **Smooth Animations**: Visual feedback for incoming attacks
- **Predictable Timing**: Consistent lock duration across all attacks
- **No Teleportation**: Attacks smoothly fall into place

### Competitive Play
- **Fair Timing**: All players experience same lock duration
- **Visual Clarity**: Clear indication of incoming attacks
- **Consistent Behavior**: Same behavior across all resolutions

## 🔍 Debugging

### Common Issues
1. **Lock Not Applied**: Check `game_state_manager.player_runtime` initialization
2. **Attacks Not Delivered**: Verify `pending_attacks` queue population
3. **Animation Not Visible**: Check `animation_state_manager` setup

### Debug Tools
- **Logging**: Enhanced logging throughout the system
- **Test Coverage**: Comprehensive test suite for validation
- **Configuration**: Flexible configuration for different scenarios

## 📋 Release Checklist

- ✅ All tests passing
- ✅ Cross-resolution testing completed
- ✅ Performance validation passed
- ✅ Documentation updated
- ✅ Code cleanup completed
- ✅ Backward compatibility verified
- ✅ Smoke tests completed

## 🎉 Summary

This release delivers a robust, animated attack delivery system with proper input locking and resolution independence. The system provides smooth gameplay with predictable timing and comprehensive test coverage. All targets are green and ready for production deployment.
