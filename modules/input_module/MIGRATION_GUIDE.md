# Input System Migration Guide

## 🎯 Overview

The Input System Consolidation introduces a unified input management system that consolidates all game input handling into a single, robust service. This guide explains the changes, migration paths, and new features.

## 🚀 What's New

### **Unified Input Management System**

The new system provides:

- **Single Input Manager**: All input handling consolidated into `UnifiedInputManager`
- **Event Routing with Priorities**: System events, UI overlays, game input, and background systems
- **Unified Key Repeat Management**: Consistent DAS/ARR timing across all systems
- **Input Locking and Gating**: Robust input control for game states
- **Configuration Integration**: Seamless integration with the unified configuration system
- **Comprehensive Event Logging**: Detailed input diagnostics and debugging
- **Hot-reload Capability**: Dynamic configuration updates without restart

### **Key Components**

1. **`UnifiedInputManager`**: Core input management system
2. **`InputHandlerCompat`**: Backward compatibility layer
3. **`InputAction`**: Standardized input actions
4. **`InputEvent`**: Processed input events
5. **`InputPriority`**: Event processing priorities

## 🔄 Migration Paths

### **Option 1: Backward Compatibility (Recommended)**

**For existing code that uses `InputHandler`:**

```python
# OLD CODE (still works)
from core.input_handler import InputHandler

input_handler = InputHandler(puzzle_engine, settings_ui)
result = input_handler.process_events(events)
```

**What happens:**
- The old `InputHandler` is now an alias for `InputHandlerCompat`
- All existing code continues to work without changes
- The new unified system runs underneath
- Gradual migration is possible

### **Option 2: Direct Migration**

**For new code or when ready to migrate:**

```python
# NEW CODE
from modules.input_module import UnifiedInputManager, InputAction

# Create unified input manager
input_manager = UnifiedInputManager(config_manager, clock)

# Register action handlers
def handle_move_left(event):
    engine.move_piece(-1, 0)

input_manager.register_action_handler(InputAction.MOVE_LEFT, handle_move_left)

# Process events
processed_events = input_manager.process_events(events)
```

## 📋 API Changes

### **New UnifiedInputManager API**

```python
class UnifiedInputManager:
    def __init__(self, config_manager=None, clock=None)
    def register_event_handler(self, priority: InputPriority, handler: Callable)
    def register_action_handler(self, action: InputAction, handler: Callable)
    def process_events(self, events: List[pygame.event.Event]) -> List[InputEvent]
    def lock_input(self, duration_ms: int, reason: str = "")
    def unlock_input(self)
    def set_movement_gate(self, enabled: bool)
    def reload_config(self)
    def get_status(self) -> Dict[str, Any]
```

### **Standardized Input Actions**

```python
class InputAction(Enum):
    # Movement actions
    MOVE_LEFT = "move_left"
    MOVE_RIGHT = "move_right"
    MOVE_UP = "move_up"
    MOVE_DOWN = "move_down"
    ROTATE_CW = "rotate_cw"
    ROTATE_CCW = "rotate_ccw"
    FLIP = "flip"
    DROP = "drop"
    
    # Game actions
    ACTION = "action"
    PAUSE = "pause"
    MENU_CONFIRM = "menu_confirm"
    MENU_CANCEL = "menu_cancel"
    
    # Audio controls
    MUSIC_PAUSE = "music_pause"
    MUSIC_NEXT = "music_next"
    MUSIC_PREV = "music_prev"
    
    # System controls
    FULLSCREEN_TOGGLE = "fullscreen_toggle"
    SETTINGS_TOGGLE = "settings_toggle"
    INPUT_TUNER_TOGGLE = "input_tuner_toggle"
    
    # Test mode controls
    AI_DIFFICULTY_1 = "ai_difficulty_1"
    AI_DIFFICULTY_2 = "ai_difficulty_2"
    # ... up to AI_DIFFICULTY_10
    AI_DIFFICULTY_INC = "ai_difficulty_inc"
    AI_DIFFICULTY_DEC = "ai_difficulty_dec"
```

### **Event Processing Priorities**

```python
class InputPriority(Enum):
    CRITICAL = 0      # System events (quit, resize)
    HIGH = 1          # UI overlays (settings, tuner)
    NORMAL = 2        # Game input (movement, actions)
    LOW = 3           # Background systems (audio, etc.)
```

## 🔧 Configuration Integration

### **Key Repeat Configuration**

The new system uses the unified configuration system:

```python
# Configuration keys
"repeat_initial_delay_ms": 120    # DAS (Delayed Auto Shift)
"repeat_interval_ms": 80          # ARR (Auto Repeat Rate)
"repeat_rotate_interval_ms": 600  # Rotation repeat interval
"tap_grace_ms": 120              # Tap grace period
```

### **Key Bindings**

Key bindings are now managed through the unified configuration system:

```python
# Example key bindings in configuration
"move_up": pygame.K_UP
"move_down": pygame.K_DOWN
"move_left": pygame.K_LEFT
"move_right": pygame.K_RIGHT
"action": pygame.K_SPACE
"menu_cancel": pygame.K_ESCAPE
```

## 🎮 Usage Examples

### **Basic Input Handling**

```python
from modules.input_module import UnifiedInputManager, InputAction

# Create input manager
input_manager = UnifiedInputManager(config_manager, clock)

# Register action handlers
def handle_movement(event):
    if event.action == InputAction.MOVE_LEFT:
        engine.move_piece(-1, 0)
    elif event.action == InputAction.MOVE_RIGHT:
        engine.move_piece(1, 0)

input_manager.register_action_handler(InputAction.MOVE_LEFT, handle_movement)
input_manager.register_action_handler(InputAction.MOVE_RIGHT, handle_movement)

# Process events
processed_events = input_manager.process_events(events)
```

### **Input Locking**

```python
# Lock input during animations
input_manager.lock_input(500, "animation_lock")

# Unlock input
input_manager.unlock_input()
```

### **Movement Gating**

```python
# Disable movement when piece is not falling
input_manager.set_movement_gate(False)

# Re-enable movement
input_manager.set_movement_gate(True)
```

### **Event Logging**

```python
# Enable event logging
input_manager.set_event_logging(True)

# Get recent events
recent_events = input_manager.get_event_log(limit=10)

# Clear event log
input_manager.clear_event_log()
```

## 🧪 Testing

### **Running Tests**

```bash
# Run all input system tests
pytest modules/input_module/tests/test_unified_input.py -v

# Run specific test class
pytest modules/input_module/tests/test_unified_input.py::TestUnifiedInputManager -v
```

### **Test Coverage**

The test suite covers:

- Core UnifiedInputManager functionality
- Compatibility layer integration
- TestMode input handler integration
- Event processing and routing
- Key repeat and timing
- Input locking and gating
- Configuration integration
- Error handling

## 🔍 Debugging

### **Status Reporting**

```python
# Get comprehensive status
status = input_manager.get_status()

print(f"Pressed keys: {status['pressed_keys_count']}")
print(f"Input locked: {status['is_input_locked']}")
print(f"Movement gate: {status['movement_gate_enabled']}")
print(f"Repeat config: {status['repeat_config']}")
```

### **Event Logging**

```python
# Get recent input events
events = input_manager.get_event_log(limit=5)

for event in events:
    print(f"{event['action']} at {event['timestamp']}ms")
```

## 🚨 Breaking Changes

### **None for Backward Compatibility**

The backward compatibility layer ensures that existing code continues to work without changes. However, there are some internal changes:

1. **Internal Implementation**: The old `InputHandler` now uses `UnifiedInputManager` underneath
2. **Configuration Access**: Input settings are now managed through the unified configuration system
3. **Event Processing**: Events are processed through the new priority-based system

### **Future Breaking Changes**

When ready to fully migrate:

1. **Direct API Usage**: Use `UnifiedInputManager` directly instead of `InputHandler`
2. **Action Handlers**: Register action handlers instead of checking key codes
3. **Event Routing**: Use the priority system for event handling

## 🎯 Benefits

### **Immediate Benefits**

- **Better Debugging**: Comprehensive event logging and status reporting
- **Consistent Timing**: Unified key repeat management across all systems
- **Configuration Integration**: Seamless integration with the unified configuration system
- **Input Locking**: Robust input control for game states

### **Long-term Benefits**

- **Maintainability**: Single input system instead of scattered implementations
- **Extensibility**: Easy to add new input actions and handlers
- **Testing**: Comprehensive test coverage and isolated testing
- **Performance**: Optimized event processing and routing

## 🔮 Future Enhancements

### **Planned Features**

1. **Input Profiles**: Save and load different input configurations
2. **Custom Key Bindings**: User-configurable key bindings
3. **Input Recording**: Record and replay input sequences
4. **Accessibility**: Support for alternative input methods
5. **Network Input**: Remote input handling for multiplayer

### **Integration Opportunities**

1. **UI System**: Integrate with the unified UI system
2. **Audio System**: Unified audio control handling
3. **Settings System**: Enhanced input configuration UI
4. **Replay System**: Input recording for replays

## 📞 Support

### **Getting Help**

- **Documentation**: This migration guide and inline documentation
- **Tests**: Comprehensive test suite with examples
- **Logging**: Detailed logging for debugging
- **Backward Compatibility**: Existing code continues to work

### **Reporting Issues**

When reporting issues:

1. **Include Logs**: Enable event logging and include relevant logs
2. **Describe Steps**: Provide detailed steps to reproduce
3. **Test Cases**: Include test cases if possible
4. **Configuration**: Mention any custom configuration

## 🎉 Conclusion

The Input System Consolidation provides a robust, maintainable, and extensible input management system while maintaining full backward compatibility. The new system offers better debugging, consistent timing, and seamless configuration integration.

**Next Steps:**
1. **Immediate**: Existing code continues to work - no action required
2. **Gradual**: Migrate to direct `UnifiedInputManager` usage when ready
3. **Future**: Leverage new features like action handlers and event routing

The foundation is now in place for advanced input features and better game responsiveness! 