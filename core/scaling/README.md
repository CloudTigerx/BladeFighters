# Scaling System

## Overview

The Scaling System provides comprehensive resolution management and UI scaling capabilities for the BladeFighters game. This system ensures consistent gameplay experience across different screen resolutions and aspect ratios, with special optimizations for mobile devices.

## 🎯 Key Features

- **Resolution Management** - Dynamic resolution detection and management
- **UI Scaling** - Automatic UI element scaling based on screen resolution
- **Asset Scaling** - Intelligent asset scaling for different screen sizes
- **Mobile Enhancements** - Special optimizations for mobile devices
- **Coordinate System** - Unified coordinate system for consistent positioning
- **Performance Optimization** - Efficient scaling algorithms with minimal performance impact

## 📁 Module Structure

```
core/scaling/
├── __init__.py                    # Module initialization and exports
├── README.md                      # This documentation file
├── resolution_manager.py          # Primary resolution management system
├── ui_scaler.py                   # UI element scaling utilities
├── asset_scaler.py                # Asset scaling and optimization
├── coordinate_system.py           # Unified coordinate system
├── mobile_enhancements.py         # Mobile-specific optimizations
└── integration_example.py         # Working integration example
```

## 🚀 Quick Start

### Basic Usage

```python
from core.scaling.resolution_manager import ResolutionManager
from core.scaling.ui_scaler import UIScaler

# Initialize the scaling system
resolution_manager = ResolutionManager()
ui_scaler = UIScaler(resolution_manager)

# Get current screen dimensions
width, height = resolution_manager.get_screen_size()

# Scale UI elements
scaled_width = ui_scaler.scale_width(100)
scaled_height = ui_scaler.scale_height(50)
```

### Advanced Usage with Mobile Support

```python
from core.scaling.resolution_manager import ResolutionManager
from core.scaling.mobile_enhancements import MobileEnhancements

# Initialize with mobile support
resolution_manager = ResolutionManager()
mobile_enhancements = MobileEnhancements(resolution_manager)

# Check if running on mobile
if mobile_enhancements.is_mobile_device():
    # Apply mobile-specific optimizations
    mobile_enhancements.apply_mobile_optimizations()
```

## 📋 API Reference

### ResolutionManager

The primary class for resolution management and screen size detection.

#### Constructor

```python
ResolutionManager()
```

**Returns:**
- `ResolutionManager`: Initialized resolution manager instance

#### Methods

##### `get_screen_size() -> Tuple[int, int]`

Get the current screen dimensions.

**Returns:**
- `Tuple[int, int]`: (width, height) of the current screen

##### `get_aspect_ratio() -> float`

Get the current screen aspect ratio.

**Returns:**
- `float`: Aspect ratio (width / height)

##### `is_high_dpi() -> bool`

Check if the current screen is high DPI.

**Returns:**
- `bool`: True if high DPI, False otherwise

### UIScaler

Utility class for scaling UI elements based on screen resolution.

#### Constructor

```python
UIScaler(resolution_manager: ResolutionManager)
```

**Parameters:**
- `resolution_manager` (ResolutionManager): Resolution manager instance

**Returns:**
- `UIScaler`: Initialized UI scaler instance

#### Methods

##### `scale_width(width: int) -> int`

Scale a width value based on current screen resolution.

**Parameters:**
- `width` (int): Original width value

**Returns:**
- `int`: Scaled width value

##### `scale_height(height: int) -> int`

Scale a height value based on current screen resolution.

**Parameters:**
- `height` (int): Original height value

**Returns:**
- `int`: Scaled height value

##### `scale_position(x: int, y: int) -> Tuple[int, int]`

Scale position coordinates based on current screen resolution.

**Parameters:**
- `x` (int): Original x coordinate
- `y` (int): Original y coordinate

**Returns:**
- `Tuple[int, int]`: Scaled (x, y) coordinates

### AssetScaler

Utility class for scaling game assets.

#### Constructor

```python
AssetScaler(resolution_manager: ResolutionManager)
```

**Parameters:**
- `resolution_manager` (ResolutionManager): Resolution manager instance

**Returns:**
- `AssetScaler`: Initialized asset scaler instance

#### Methods

##### `scale_surface(surface: pygame.Surface, target_size: Tuple[int, int]) -> pygame.Surface`

Scale a pygame surface to target size.

**Parameters:**
- `surface` (pygame.Surface): Original surface to scale
- `target_size` (Tuple[int, int]): Target (width, height)

**Returns:**
- `pygame.Surface`: Scaled surface

### MobileEnhancements

Special optimizations for mobile devices.

#### Constructor

```python
MobileEnhancements(resolution_manager: ResolutionManager)
```

**Parameters:**
- `resolution_manager` (ResolutionManager): Resolution manager instance

**Returns:**
- `MobileEnhancements`: Initialized mobile enhancements instance

#### Methods

##### `is_mobile_device() -> bool`

Check if the current device is mobile.

**Returns:**
- `bool`: True if mobile device, False otherwise

##### `apply_mobile_optimizations()`

Apply mobile-specific optimizations to the scaling system.

## 🔧 Integration Examples

### Basic Integration

```python
from core.scaling.resolution_manager import ResolutionManager
from core.scaling.ui_scaler import UIScaler

class GameRenderer:
    def __init__(self):
        self.resolution_manager = ResolutionManager()
        self.ui_scaler = UIScaler(self.resolution_manager)
    
    def render_ui_element(self, x, y, width, height):
        # Scale all dimensions
        scaled_x, scaled_y = self.ui_scaler.scale_position(x, y)
        scaled_width = self.ui_scaler.scale_width(width)
        scaled_height = self.ui_scaler.scale_height(height)
        
        # Render with scaled dimensions
        return (scaled_x, scaled_y, scaled_width, scaled_height)
```

### Advanced Integration with Mobile Support

```python
from core.scaling.resolution_manager import ResolutionManager
from core.scaling.mobile_enhancements import MobileEnhancements
from core.scaling.asset_scaler import AssetScaler

class GameEngine:
    def __init__(self):
        self.resolution_manager = ResolutionManager()
        self.mobile_enhancements = MobileEnhancements(self.resolution_manager)
        self.asset_scaler = AssetScaler(self.resolution_manager)
        
        # Apply mobile optimizations if needed
        if self.mobile_enhancements.is_mobile_device():
            self.mobile_enhancements.apply_mobile_optimizations()
    
    def load_and_scale_asset(self, asset_path, target_size):
        # Load asset
        original_surface = pygame.image.load(asset_path)
        
        # Scale to target size
        scaled_surface = self.asset_scaler.scale_surface(original_surface, target_size)
        
        return scaled_surface
```

## 🧪 Testing

The scaling system includes comprehensive tests to ensure proper functionality:

```bash
# Run scaling system tests
python -m pytest core/scaling/tests/ -v
```

## 📝 Notes

- The scaling system automatically detects screen resolution on initialization
- Mobile optimizations are applied automatically when a mobile device is detected
- All scaling operations maintain aspect ratios to prevent distortion
- Performance optimizations are built-in for smooth gameplay

## 🔗 Related Documentation

- **[Core Module Documentation](../README.md)** - Core system documentation
- **[UI System Documentation](../ui/README.md)** - UI system integration
- **[Asset Loading Documentation](../asset_loader.py)** - Asset loading integration

*This module is part of the BladeFighters project. For project-wide documentation, see the [Documentation Index](../../docs/README.md).*
