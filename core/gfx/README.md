# Graphics System

## Overview

The Graphics System provides the core rendering and graphics management capabilities for the BladeFighters game. This system handles sprite management, animation playback, and optimized rendering operations with comprehensive testing support.

## 🎯 Key Features

- **Sprite Management** - Efficient sprite loading and caching
- **Animation Player** - Advanced animation playback with frame control
- **Rendering Optimization** - Optimized rendering operations for smooth performance
- **Memory Management** - Efficient memory usage for graphics assets
- **Testing Support** - Comprehensive test suite for graphics functionality
- **Integration Ready** - Easy integration with other game systems

## 📁 Module Structure

```
core/gfx/
├── README.md                      # This documentation file
├── anim_player.py                 # Animation player implementation
└── tests/
    └── test_anim_player.py        # Animation player test suite
```

## 🚀 Quick Start

### Basic Usage

```python
from core.gfx.anim_player import AnimationPlayer

# Initialize the animation player
anim_player = AnimationPlayer()

# Load and play an animation
animation = anim_player.load_animation("player_idle", "assets/player_idle.png", 8)
anim_player.play(animation)
```

### Advanced Usage with Frame Control

```python
from core.gfx.anim_player import AnimationPlayer

# Initialize with custom settings
anim_player = AnimationPlayer(fps=60)

# Load multiple animations
idle_anim = anim_player.load_animation("idle", "assets/idle.png", 4)
walk_anim = anim_player.load_animation("walk", "assets/walk.png", 8)

# Control animation playback
anim_player.play(idle_anim, loop=True)
anim_player.pause()
anim_player.resume()
anim_player.stop()
```

## 📋 API Reference

### AnimationPlayer

The primary class for animation playback and sprite management.

#### Constructor

```python
AnimationPlayer(fps: int = 30)
```

**Parameters:**
- `fps` (int, optional): Target frame rate for animations (default: 30)

**Returns:**
- `AnimationPlayer`: Initialized animation player instance

#### Methods

##### `load_animation(name: str, sprite_sheet_path: str, frames: int) -> str`

Load an animation from a sprite sheet.

**Parameters:**
- `name` (str): Name identifier for the animation
- `sprite_sheet_path` (str): Path to the sprite sheet image
- `frames` (int): Number of frames in the animation

**Returns:**
- `str`: Animation ID for referencing the loaded animation

##### `play(animation_id: str, loop: bool = True)`

Start playing an animation.

**Parameters:**
- `animation_id` (str): ID of the animation to play
- `loop` (bool, optional): Whether to loop the animation (default: True)

##### `stop(animation_id: str)`

Stop playing an animation.

**Parameters:**
- `animation_id` (str): ID of the animation to stop

##### `pause(animation_id: str)`

Pause an animation.

**Parameters:**
- `animation_id` (str): ID of the animation to pause

##### `resume(animation_id: str)`

Resume a paused animation.

**Parameters:**
- `animation_id` (str): ID of the animation to resume

##### `get_current_frame(animation_id: str) -> pygame.Surface`

Get the current frame of an animation.

**Parameters:**
- `animation_id` (str): ID of the animation

**Returns:**
- `pygame.Surface`: Current frame surface

##### `update(delta_time: float)`

Update all animations with elapsed time.

**Parameters:**
- `delta_time` (float): Time elapsed since last update in seconds

##### `is_playing(animation_id: str) -> bool`

Check if an animation is currently playing.

**Parameters:**
- `animation_id` (str): ID of the animation to check

**Returns:**
- `bool`: True if animation is playing, False otherwise

##### `get_progress(animation_id: str) -> float`

Get the progress of an animation (0.0 to 1.0).

**Parameters:**
- `animation_id` (str): ID of the animation

**Returns:**
- `float`: Animation progress from 0.0 to 1.0

## 🔧 Integration Examples

### Basic Game Integration

```python
from core.gfx.anim_player import AnimationPlayer

class GameSprite:
    def __init__(self):
        self.anim_player = AnimationPlayer()
        
        # Load sprite animations
        self.idle_anim = self.anim_player.load_animation("idle", "assets/sprite_idle.png", 4)
        self.walk_anim = self.anim_player.load_animation("walk", "assets/sprite_walk.png", 8)
        
        # Start with idle animation
        self.anim_player.play(self.idle_anim)
    
    def update(self, delta_time):
        # Update animation
        self.anim_player.update(delta_time)
    
    def render(self, screen, position):
        # Get current frame and render
        current_frame = self.anim_player.get_current_frame(self.idle_anim)
        screen.blit(current_frame, position)
    
    def change_animation(self, animation_id):
        # Stop current animation and start new one
        self.anim_player.stop(self.idle_anim)
        self.anim_player.play(animation_id)
```

### Advanced Integration with Multiple Animations

```python
from core.gfx.anim_player import AnimationPlayer

class Character:
    def __init__(self):
        self.anim_player = AnimationPlayer(fps=60)
        
        # Load character animations
        self.animations = {
            "idle": self.anim_player.load_animation("idle", "assets/char_idle.png", 6),
            "walk": self.anim_player.load_animation("walk", "assets/char_walk.png", 8),
            "attack": self.anim_player.load_animation("attack", "assets/char_attack.png", 10),
            "death": self.anim_player.load_animation("death", "assets/char_death.png", 12)
        }
        
        # Set initial state
        self.current_anim = "idle"
        self.anim_player.play(self.animations[self.current_anim])
    
    def update(self, delta_time):
        # Update current animation
        self.anim_player.update(delta_time)
        
        # Check if non-looping animation finished
        if not self.anim_player.is_playing(self.animations[self.current_anim]):
            if self.current_anim in ["attack", "death"]:
                # Return to idle after non-looping animations
                self.set_animation("idle")
    
    def set_animation(self, anim_name):
        if anim_name in self.animations and anim_name != self.current_anim:
            # Stop current animation
            self.anim_player.stop(self.animations[self.current_anim])
            
            # Start new animation
            self.current_anim = anim_name
            loop = anim_name not in ["attack", "death"]
            self.anim_player.play(self.animations[self.current_anim], loop=loop)
    
    def render(self, screen, position):
        # Render current animation frame
        current_frame = self.anim_player.get_current_frame(self.animations[self.current_anim])
        screen.blit(current_frame, position)
```

## 🧪 Testing

The graphics system includes comprehensive tests to ensure proper functionality:

```bash
# Run graphics system tests
python -m pytest core/gfx/tests/ -v
```

### Test Coverage

The test suite covers:
- Animation loading and playback
- Frame timing and progression
- Animation state management
- Error handling and edge cases
- Performance benchmarks

## 📝 Notes

- Animations are automatically optimized for performance
- Frame rates can be adjusted per animation player instance
- Memory usage is optimized for sprite sheet animations
- The system supports both looping and non-looping animations
- All animations are cached for efficient memory usage

## 🔗 Related Documentation

- **[Core Module Documentation](../README.md)** - Core system documentation
- **[Animation System Documentation](../Animations/README.md)** - Animation system integration
- **[Asset Loading Documentation](../asset_loader.py)** - Asset loading integration

*This module is part of the BladeFighters project. For project-wide documentation, see the [Documentation Index](../../docs/README.md).*
