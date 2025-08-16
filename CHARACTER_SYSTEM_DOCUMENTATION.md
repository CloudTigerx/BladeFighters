# Character Sprite System Documentation

## Overview

The Character Sprite System is a professional, modular implementation for handling character sprites in BladeFighters. It provides sprite loading, caching, positioning, and animation management with a clean, extensible architecture.

## Architecture

### Core Components

1. **CharacterSpriteManager** - Handles sprite loading, caching, and positioning
2. **CharacterAnimationManager** - Manages animation timing and state
3. **RenderCoordinator Integration** - Integrates character rendering into the game loop

### File Structure

```
modules/character_module/
├── __init__.py                           # Module exports
├── character_sprite_manager.py          # Sprite loading and positioning
└── character_animation_manager.py       # Animation timing and state
```

## Features

### ✅ Implemented Features

- **Professional Sprite Caching** - Avoids reloading sprites for performance
- **Automatic Scaling** - Configurable scale factors for different screen sizes
- **Smart Positioning** - Calculates character positions relative to puzzle boards
- **Animation Framework** - Ready for multi-frame animations
- **Error Handling** - Graceful fallbacks for missing sprites
- **Logging Integration** - Comprehensive logging for debugging
- **Modular Design** - Easy to extend with new characters and animations

### 🚧 Future Features

- **Multi-frame Animations** - Support for sprite sheets with multiple frames
- **Animation Transitions** - Smooth transitions between different animations
- **Character States** - Different sprites for idle, attacking, defending, etc.
- **Dynamic Loading** - Load sprites on-demand for memory efficiency

## Usage

### Basic Setup

The character system is automatically initialized when TestMode starts. No additional setup required.

### Adding New Characters

1. **Place sprite file** in `puzzleassets/characters/`
2. **Add character configuration** to `CharacterSpriteManager.characters`
3. **Initialize animation** in the render coordinator

Example configuration:
```python
'new_character': {
    'idle_sprite': 'characters/NewCharacter_idle.png',
    'scale_factor': 0.8,
    'position_offset': {'x': 0, 'y': 20},
    'animation_speed': 1000,
    'frames_per_row': 1,
    'total_frames': 1
}
```

### Character Positioning

Characters are automatically positioned beneath puzzle boards:
- **Horizontal**: Centered relative to the board
- **Vertical**: Below the board with configurable offset
- **Scaling**: Automatically scaled based on configuration

## Current Implementation

### Yuki Character

- **Sprite**: `puzzleassets/characters/Yuki_idle_sprite.png`
- **Position**: Beneath player puzzle board
- **Scale**: 80% of original size
- **Animation**: Single frame idle (ready for expansion)

### Integration Points

1. **TestMode Draw Loop** - Characters render after boards and attack indicators
2. **RenderCoordinator** - Centralized rendering coordination
3. **Board Manager** - Provides positioning context

## Performance Considerations

### Optimizations

- **Sprite Caching** - Sprites loaded once and cached
- **Efficient Positioning** - Calculated once per frame
- **Minimal Overhead** - Lightweight animation system
- **Error Isolation** - Failures don't affect game performance

### Memory Usage

- **Cached Sprites** - ~1.6MB for Yuki sprite (scaled)
- **Animation State** - Minimal memory footprint
- **Configurable Scaling** - Control memory usage through scale factors

## Testing

### Test Script

Run the character system test:
```bash
python test_character_system.py
```

This test verifies:
- Sprite loading and caching
- Position calculation
- Animation timing
- Rendering integration

### Manual Testing

1. **Launch TestMode** - Characters should appear beneath boards
2. **Check Positioning** - Characters should be centered and properly spaced
3. **Verify Scaling** - Characters should be appropriately sized
4. **Monitor Performance** - No noticeable impact on frame rate

## Configuration

### Character Configuration Options

```python
{
    'idle_sprite': 'path/to/sprite.png',    # Sprite file path
    'scale_factor': 0.8,                    # Scale multiplier (0.1 - 2.0)
    'position_offset': {'x': 0, 'y': 20},   # Position adjustment
    'animation_speed': 1000,                # Milliseconds per frame
    'frames_per_row': 1,                    # Frames per row in sprite sheet
    'total_frames': 1                       # Total animation frames
}
```

### Position Offset

- **x**: Horizontal offset from center (-100 to +100 pixels)
- **y**: Vertical offset from board bottom (-50 to +100 pixels)

## Troubleshooting

### Common Issues

1. **Sprite Not Loading**
   - Check file path in character configuration
   - Verify sprite file exists in `puzzleassets/characters/`
   - Check file permissions

2. **Character Not Visible**
   - Verify character system initialization
   - Check position calculation
   - Ensure sprite is not transparent

3. **Performance Issues**
   - Reduce scale factor for large sprites
   - Check for memory leaks in sprite cache
   - Monitor frame rate impact

### Debug Information

Enable debug logging to see:
- Sprite loading status
- Position calculations
- Animation updates
- Error messages

## Future Enhancements

### Planned Features

1. **Sprite Sheet Support**
   - Multi-frame animations
   - Automatic frame extraction
   - Configurable frame layouts

2. **Animation States**
   - Idle, attack, defend, victory animations
   - State transition system
   - Trigger-based animations

3. **Character Interactions**
   - Character-specific effects
   - Board interaction animations
   - Victory/defeat sequences

4. **Advanced Positioning**
   - Dynamic positioning based on game state
   - Character movement animations
   - Screen edge detection

### Extension Points

The system is designed for easy extension:
- Add new character types
- Implement custom animation systems
- Create character-specific behaviors
- Integrate with game events

## Conclusion

The Character Sprite System provides a solid foundation for character integration in BladeFighters. It's designed to be:

- **Professional** - Clean, maintainable code
- **Performant** - Efficient sprite management
- **Extensible** - Easy to add new features
- **Reliable** - Comprehensive error handling

The system successfully integrates Yuki as the first character and provides a framework for adding more characters and animations in the future.
