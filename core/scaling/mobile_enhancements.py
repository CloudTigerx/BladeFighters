"""
Mobile Enhancements for BladeFighters Scaling System
Additional features needed for mobile deployment.
"""

from enum import Enum
from typing import Tuple, Dict, Optional
from dataclasses import dataclass

class DeviceType(Enum):
    DESKTOP = "desktop"
    TABLET = "tablet"
    PHONE = "phone"
    PHONE_LARGE = "phone_large"  # iPhone Pro Max, etc.

class Orientation(Enum):
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"

@dataclass
class MobileConfig:
    """Mobile-specific configuration."""
    device_type: DeviceType
    orientation: Orientation
    touch_enabled: bool
    safe_area_top: int
    safe_area_bottom: int
    safe_area_left: int
    safe_area_right: int
    min_touch_target: int = 44  # Apple's minimum touch target size

class MobileScalingEnhancements:
    """
    Mobile-specific enhancements for the scaling system.
    These would be added to the existing scaling system.
    """
    
    def __init__(self):
        # Common mobile resolutions
        self.mobile_resolutions = {
            # Phones
            'iphone_se': (375, 667),      # 4.7"
            'iphone_12': (390, 844),      # 6.1"
            'iphone_12_pro_max': (428, 926), # 6.7"
            'pixel_5': (393, 851),        # 6.0"
            'galaxy_s21': (360, 800),     # 6.2"
            
            # Tablets
            'ipad': (768, 1024),          # 9.7"
            'ipad_pro_11': (834, 1194),   # 11"
            'ipad_pro_12': (1024, 1366),  # 12.9"
            'galaxy_tab_s7': (800, 1280), # 11"
        }
        
        # Touch-friendly UI adjustments
        self.touch_adjustments = {
            'button_min_height': 44,      # Apple's minimum
            'button_min_width': 44,
            'button_spacing': 8,          # Minimum spacing between buttons
            'text_min_size': 16,          # Minimum readable text
            'icon_min_size': 24,          # Minimum tappable icon
        }
    
    def detect_mobile_device(self, width: int, height: int) -> DeviceType:
        """Detect if this is a mobile device based on screen size."""
        # Simple detection based on screen size
        if width < 600 or height < 600:
            if width > 400 or height > 400:
                return DeviceType.PHONE_LARGE
            else:
                return DeviceType.PHONE
        elif width < 1200 or height < 1200:
            return DeviceType.TABLET
        else:
            return DeviceType.DESKTOP
    
    def get_orientation(self, width: int, height: int) -> Orientation:
        """Determine screen orientation."""
        return Orientation.LANDSCAPE if width > height else Orientation.PORTRAIT
    
    def calculate_safe_areas(self, device_type: DeviceType, orientation: Orientation) -> Dict[str, int]:
        """Calculate safe areas for different devices."""
        safe_areas = {
            'top': 0,
            'bottom': 0,
            'left': 0,
            'right': 0
        }
        
        if device_type == DeviceType.PHONE:
            if orientation == Orientation.PORTRAIT:
                safe_areas['top'] = 47    # Status bar
                safe_areas['bottom'] = 34 # Home indicator
            else:
                safe_areas['left'] = 47   # Status bar
                safe_areas['right'] = 34  # Home indicator
        
        elif device_type == DeviceType.PHONE_LARGE:
            if orientation == Orientation.PORTRAIT:
                safe_areas['top'] = 47
                safe_areas['bottom'] = 34
            else:
                safe_areas['left'] = 47
                safe_areas['right'] = 34
        
        elif device_type == DeviceType.TABLET:
            # Tablets typically have smaller safe areas
            safe_areas['top'] = 20
            safe_areas['bottom'] = 20
        
        return safe_areas
    
    def adjust_ui_for_touch(self, base_sizes: Dict[str, int], device_type: DeviceType) -> Dict[str, int]:
        """Adjust UI sizes for touch interaction."""
        adjusted = base_sizes.copy()
        
        if device_type in [DeviceType.PHONE, DeviceType.PHONE_LARGE]:
            # Ensure minimum touch targets
            adjusted['button_height'] = max(adjusted.get('button_height', 60), 44)
            adjusted['button_padding'] = max(adjusted.get('button_padding', 20), 12)
            adjusted['icon_size'] = max(adjusted.get('icon_size', 32), 24)
            
            # Increase text sizes for readability
            adjusted['body_font'] = max(adjusted.get('body_font', 24), 16)
            adjusted['small_font'] = max(adjusted.get('small_font', 16), 14)
        
        elif device_type == DeviceType.TABLET:
            # Moderate adjustments for tablets
            adjusted['button_height'] = max(adjusted.get('button_height', 60), 40)
            adjusted['button_padding'] = max(adjusted.get('button_padding', 20), 16)
        
        return adjusted
    
    def calculate_mobile_grid_layout(self, screen_size: Tuple[int, int], device_type: DeviceType, 
                                   orientation: Orientation) -> Dict[str, any]:
        """Calculate optimal grid layout for mobile devices."""
        width, height = screen_size
        safe_areas = self.calculate_safe_areas(device_type, orientation)
        
        # Available space after safe areas
        available_width = width - safe_areas['left'] - safe_areas['right']
        available_height = height - safe_areas['top'] - safe_areas['bottom']
        
        # Calculate block size based on available space
        if orientation == Orientation.PORTRAIT:
            # In portrait, grid might be smaller or need different layout
            max_block_size = min(available_width // 6, available_height // 15)
            grid_width = 6
            grid_height = 15
        else:
            # In landscape, we have more horizontal space
            max_block_size = min(available_width // 12, available_height // 15)  # Dual grid
            grid_width = 12  # Two 6-column grids side by side
            grid_height = 15
        
        # Ensure minimum block size
        block_size = max(max_block_size, 20)  # Minimum 20px blocks
        
        # Calculate grid position
        grid_x = safe_areas['left'] + (available_width - (grid_width * block_size)) // 2
        grid_y = safe_areas['top'] + (available_height - (grid_height * block_size)) // 2
        
        return {
            'block_size': block_size,
            'grid_width': grid_width,
            'grid_height': grid_height,
            'grid_x': grid_x,
            'grid_y': grid_y,
            'safe_areas': safe_areas,
            'available_space': (available_width, available_height)
        }
    
    def create_touch_friendly_layout(self, container_size: Tuple[int, int], 
                                   element_count: int, device_type: DeviceType) -> list:
        """Create a touch-friendly layout for UI elements."""
        width, height = container_size
        
        if device_type in [DeviceType.PHONE, DeviceType.PHONE_LARGE]:
            # Stack vertically on phones
            element_height = 44  # Minimum touch target
            spacing = 8
            total_height = (element_count * element_height) + ((element_count - 1) * spacing)
            
            elements = []
            y = (height - total_height) // 2
            for i in range(element_count):
                x = (width - 200) // 2  # 200px wide buttons
                elements.append((x, y, 200, element_height))
                y += element_height + spacing
            
            return elements
        
        else:
            # Use grid layout for tablets/desktop
            cols = min(3, element_count)
            rows = (element_count + cols - 1) // cols
            
            element_width = 150
            element_height = 44
            spacing = 16
            
            total_width = (cols * element_width) + ((cols - 1) * spacing)
            total_height = (rows * element_height) + ((rows - 1) * spacing)
            
            start_x = (width - total_width) // 2
            start_y = (height - total_height) // 2
            
            elements = []
            for row in range(rows):
                for col in range(cols):
                    if len(elements) >= element_count:
                        break
                    x = start_x + col * (element_width + spacing)
                    y = start_y + row * (element_height + spacing)
                    elements.append((x, y, element_width, element_height))
            
            return elements

# Example integration with existing scaling system:
"""
# In ResolutionManager._detect_display_type():
def _detect_display_type(self) -> None:
    width = self.display_info['current_w']
    height = self.display_info['current_h']
    
    # Add mobile detection
    mobile_enhancements = MobileScalingEnhancements()
    device_type = mobile_enhancements.detect_mobile_device(width, height)
    orientation = mobile_enhancements.get_orientation(width, height)
    
    if device_type in [DeviceType.PHONE, DeviceType.PHONE_LARGE, DeviceType.TABLET]:
        self.display_type = DisplayType.MOBILE
        self.device_type = device_type
        self.orientation = orientation
        self.touch_enabled = True
    else:
        # Existing desktop detection logic
        ...

# In UIScaler.__init__():
def __init__(self, resolution_manager: ResolutionManager):
    # ... existing code ...
    
    # Add mobile adjustments
    if hasattr(resolution_manager, 'device_type'):
        mobile_enhancements = MobileScalingEnhancements()
        self.base_sizes = mobile_enhancements.adjust_ui_for_touch(
            self.base_sizes, resolution_manager.device_type
        )
""" 