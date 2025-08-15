# Module Integration Guide

## Overview

This guide provides comprehensive examples of how to integrate different modules in the BladeFighters project. It covers common integration patterns, best practices, and working examples for combining multiple modules effectively.

## 🎯 Integration Patterns

### 1. State-Driven Integration

The most common pattern is using the GameStateManager as the central hub for module communication.

```python
from modules.game_state_module.game_state_manager import GameStateManager
from modules.audio_module.audio_system import AudioSystem
from modules.input_module import UnifiedInputManager
from modules.settings_module.unified_config import UnifiedConfigManager

# Initialize core systems
state_manager = GameStateManager()
config_manager = UnifiedConfigManager()
audio_system = AudioSystem(state_manager=state_manager)
input_manager = UnifiedInputManager(config_manager, clock, state_manager)

# All modules now share state through the state manager
```

### 2. Event-Driven Integration

Modules can communicate through events and callbacks.

```python
from modules.attack_module.attack_manager import AttackManager
from modules.audio_module.audio_system import AudioSystem

class GameEngine:
    def __init__(self):
        self.attack_manager = AttackManager()
        self.audio_system = AudioSystem()
        
        # Set up event callbacks
        self.attack_manager.on_attack_triggered = self.handle_attack
        self.attack_manager.on_attack_completed = self.handle_attack_complete
    
    def handle_attack(self, attack_data):
        # Play attack sound
        self.audio_system.play_sound("attack")
    
    def handle_attack_complete(self, result):
        # Play completion sound based on result
        if result.success:
            self.audio_system.play_sound("attack_success")
        else:
            self.audio_system.play_sound("attack_fail")
```

### 3. Configuration-Driven Integration

Modules can be configured to work together through shared configuration.

```python
from modules.settings_module.unified_config import UnifiedConfigManager
from modules.audio_module.audio_system import AudioSystem
from modules.input_module import UnifiedInputManager

# Initialize with shared configuration
config_manager = UnifiedConfigManager()
config_manager.load_config("game_settings.json")

# Initialize modules with shared config
audio_system = AudioSystem()
audio_system.apply_config(config_manager.get_audio_settings())

input_manager = UnifiedInputManager(config_manager, clock)
```

## 🔧 Common Integration Scenarios

### 1. Audio + Input Integration

```python
from modules.audio_module.audio_system import AudioSystem
from modules.input_module import UnifiedInputManager
from modules.game_state_module.game_state_manager import GameStateManager

class AudioInputIntegration:
    def __init__(self):
        self.state_manager = GameStateManager()
        self.audio_system = AudioSystem(state_manager=self.state_manager)
        self.input_manager = UnifiedInputManager(state_manager=self.state_manager)
        
        # Set up input-to-audio mappings
        self.input_audio_map = {
            "KEY_SPACE": "click",
            "KEY_ENTER": "confirm",
            "KEY_ESCAPE": "cancel",
            "MOUSE_CLICK": "click"
        }
    
    def process_input(self, events):
        processed_events = self.input_manager.process_events(events)
        
        for event in processed_events:
            # Play corresponding audio for input events
            if event.type in self.input_audio_map:
                sound_name = self.input_audio_map[event.type]
                self.audio_system.play_sound(sound_name)
        
        return processed_events
```

### 2. Attack + Audio + Screen Integration

```python
from modules.attack_module.attack_manager import AttackManager
from modules.audio_module.audio_system import AudioSystem
from modules.screen_module.screen_manager import ScreenManager
from modules.game_state_module.game_state_manager import GameStateManager

class CombatSystem:
    def __init__(self):
        self.state_manager = GameStateManager()
        self.attack_manager = AttackManager()
        self.audio_system = AudioSystem(state_manager=self.state_manager)
        self.screen_manager = ScreenManager(state_manager=self.state_manager)
        
        # Set up attack callbacks
        self.attack_manager.on_attack_start = self.handle_attack_start
        self.attack_manager.on_attack_hit = self.handle_attack_hit
        self.attack_manager.on_attack_miss = self.handle_attack_miss
    
    def handle_attack_start(self, attack_data):
        # Play attack start sound
        self.audio_system.play_sound("attack_start")
        
        # Update screen state
        self.screen_manager.set_combat_state("attacking")
    
    def handle_attack_hit(self, hit_data):
        # Play hit sound
        self.audio_system.play_sound("attack_hit")
        
        # Show hit effect on screen
        self.screen_manager.show_hit_effect(hit_data.position)
    
    def handle_attack_miss(self, miss_data):
        # Play miss sound
        self.audio_system.play_sound("attack_miss")
        
        # Show miss effect on screen
        self.screen_manager.show_miss_effect(miss_data.position)
```

### 3. Menu + Settings + Audio Integration

```python
from modules.menu_module.menu_system import MenuSystem
from modules.settings_module.unified_config import UnifiedConfigManager
from modules.audio_module.audio_system import AudioSystem
from modules.game_state_module.game_state_manager import GameStateManager

class MenuSettingsIntegration:
    def __init__(self):
        self.state_manager = GameStateManager()
        self.config_manager = UnifiedConfigManager()
        self.audio_system = AudioSystem(state_manager=self.state_manager)
        self.menu_system = MenuSystem()
        
        # Set up menu callbacks
        self.menu_system.on_setting_changed = self.handle_setting_change
        self.menu_system.on_menu_navigation = self.handle_menu_navigation
    
    def handle_setting_change(self, setting_name, new_value):
        # Update configuration
        self.config_manager.set(setting_name, new_value)
        
        # Apply setting to audio system
        if setting_name.startswith("audio."):
            self.audio_system.apply_setting(setting_name, new_value)
        
        # Save configuration
        self.config_manager.save()
        
        # Play confirmation sound
        self.audio_system.play_sound("setting_changed")
    
    def handle_menu_navigation(self, direction):
        # Play navigation sound
        self.audio_system.play_sound("menu_navigate")
        
        # Update menu state
        self.state_manager.set("menu.current_selection", direction)
```

### 4. Complete Game Loop Integration

```python
from modules.game_state_module.game_state_manager import GameStateManager
from modules.input_module import UnifiedInputManager
from modules.audio_module.audio_system import AudioSystem
from modules.screen_module.screen_manager import ScreenManager
from modules.attack_module.attack_manager import AttackManager
from modules.settings_module.unified_config import UnifiedConfigManager

class GameEngine:
    def __init__(self):
        # Initialize core systems
        self.state_manager = GameStateManager()
        self.config_manager = UnifiedConfigManager()
        
        # Initialize modules with state integration
        self.audio_system = AudioSystem(state_manager=self.state_manager)
        self.input_manager = UnifiedInputManager(self.config_manager, clock, self.state_manager)
        self.screen_manager = ScreenManager(state_manager=self.state_manager)
        self.attack_manager = AttackManager()
        
        # Set up module interactions
        self.setup_module_interactions()
    
    def setup_module_interactions(self):
        # Audio responds to input
        self.input_manager.on_key_press = self.handle_key_press
        self.input_manager.on_mouse_click = self.handle_mouse_click
        
        # Attack system responds to input
        self.input_manager.on_attack_input = self.handle_attack_input
        
        # Screen updates based on game state
        self.state_manager.on_state_change = self.handle_state_change
    
    def handle_key_press(self, key):
        # Play key press sound
        self.audio_system.play_sound("key_press")
        
        # Update input state
        self.state_manager.set("input.last_key", key)
    
    def handle_mouse_click(self, position):
        # Play click sound
        self.audio_system.play_sound("click")
        
        # Update mouse state
        self.state_manager.set("input.mouse_position", position)
    
    def handle_attack_input(self, attack_data):
        # Trigger attack
        result = self.attack_manager.execute_attack(attack_data)
        
        # Play attack sound
        if result.success:
            self.audio_system.play_sound("attack_success")
        else:
            self.audio_system.play_sound("attack_fail")
        
        # Update game state
        self.state_manager.set("combat.last_attack", result)
    
    def handle_state_change(self, key, old_value, new_value):
        # Update screen based on state changes
        if key == "game.current_screen":
            self.screen_manager.switch_screen(new_value)
        elif key == "audio.volume":
            self.audio_system.set_master_volume(new_value)
    
    def run_game_loop(self):
        while True:
            # Process input
            events = pygame.event.get()
            processed_events = self.input_manager.process_events(events)
            
            # Update game state
            self.state_manager.update()
            
            # Update modules
            self.audio_system.update()
            self.screen_manager.update()
            self.attack_manager.update()
            
            # Render
            self.screen_manager.render()
            
            # Handle frame timing
            clock.tick(60)
```

## 🔗 Module Dependencies

### Core Dependencies

```
GameStateManager (Core)
├── AudioSystem
├── UnifiedInputManager
├── ScreenManager
└── UnifiedConfigManager

UnifiedConfigManager
├── UnifiedInputManager
├── AudioSystem
└── MenuSystem

AttackManager
├── AudioSystem (for sound effects)
└── ScreenManager (for visual effects)
```

### Integration Priority

1. **GameStateManager** - Initialize first as other modules depend on it
2. **UnifiedConfigManager** - Initialize early for configuration-driven modules
3. **AudioSystem** - Initialize before modules that need audio
4. **InputManager** - Initialize after config and audio
5. **ScreenManager** - Initialize after input for UI interactions
6. **Specialized Modules** - Initialize last (Attack, Menu, etc.)

## 🧪 Testing Integration

### Integration Test Example

```python
import pytest
from modules.game_state_module.game_state_manager import GameStateManager
from modules.audio_module.audio_system import AudioSystem
from modules.input_module import UnifiedInputManager

class TestModuleIntegration:
    def setup_method(self):
        self.state_manager = GameStateManager()
        self.audio_system = AudioSystem(state_manager=self.state_manager)
        self.input_manager = UnifiedInputManager(state_manager=self.state_manager)
    
    def test_audio_input_integration(self):
        # Simulate input event
        test_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
        
        # Process input
        processed_events = self.input_manager.process_events([test_event])
        
        # Verify audio state was updated
        assert self.state_manager.get("input.keys_pressed") == {pygame.K_SPACE}
        
        # Verify audio can respond to input state
        self.audio_system.play_sound("click")
        assert self.audio_system.is_sound_playing("click")
    
    def test_state_synchronization(self):
        # Set state in one module
        self.state_manager.set("audio.volume", 0.5)
        
        # Verify other modules can access the state
        assert self.audio_system.get_master_volume() == 0.5
        assert self.input_manager.get_state("audio.volume") == 0.5
```

## 📝 Best Practices

### 1. State Management
- Always use GameStateManager for shared state
- Avoid direct module-to-module communication when possible
- Use state change callbacks for reactive updates

### 2. Configuration
- Use UnifiedConfigManager for all configuration
- Load configuration before initializing dependent modules
- Apply configuration changes through the config manager

### 3. Audio Integration
- Always initialize AudioSystem with state manager
- Use consistent sound naming conventions
- Handle audio state changes through the state manager

### 4. Input Handling
- Use UnifiedInputManager for all input processing
- Process input events before updating other modules
- Use input state for module coordination

### 5. Error Handling
- Implement proper error handling in integration points
- Use logging for debugging integration issues
- Gracefully handle missing or failed modules

## 🔗 Related Documentation

- **[Module Documentation Index](README.md)** - Complete module documentation
- **[State Management Guide](STATE_MANAGEMENT.md)** - State management patterns
- **[Configuration Guide](CONFIGURATION.md)** - Configuration management
- **[Testing Guide](TESTING.md)** - Integration testing strategies

*This guide is part of the BladeFighters project. For project-wide documentation, see the [Documentation Index](README.md).*
