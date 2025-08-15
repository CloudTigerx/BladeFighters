"""
Resolution Manager - Core resolution detection and management
Handles display capabilities, resolution selection, and scaling factors.
"""

import pygame
import sys
import subprocess
from typing import List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class DisplayType(Enum):
    STANDARD = "standard"
    RETINA = "retina"
    HIGH_DPI = "high_dpi"
    ULTRA_WIDE = "ultra_wide"

@dataclass
class Resolution:
    width: int
    height: int
    aspect_ratio: float
    pixel_density: float
    is_native: bool = False
    
    def __post_init__(self):
        self.aspect_ratio = self.width / self.height
        self.pixel_density = (self.width * self.height) / (1920 * 1080)  # Relative to 1080p

class ResolutionManager:
    """
    Comprehensive resolution management system.
    Handles detection, selection, and scaling for all display types.
    """
    
    def __init__(self):
        self.display_info = None
        self.current_resolution = None
        self.native_resolution = None
        self.available_resolutions = []
        self.display_type = DisplayType.STANDARD
        self.scale_factor = 1.0
        self.ui_scale_factor = 1.0
        
        # Standard resolutions (16:9, 16:10, 4:3)
        self.standard_resolutions = [
            (800, 600),    # 4:3
            (1024, 768),   # 4:3
            (1280, 720),   # 16:9
            (1366, 768),   # 16:9
            (1440, 900),   # 16:10
            (1600, 900),   # 16:9
            (1680, 1050),  # 16:10
            (1920, 1080),  # 16:9
            (1920, 1200),  # 16:10
            (2560, 1440),  # 16:9
            (2560, 1600),  # 16:10
            (3840, 2160),  # 16:9
        ]
        
        self.detect_display()
    
    def detect_display(self) -> None:
        """Detect display capabilities and set up resolution options."""
        try:
            pygame.init()
            info = pygame.display.Info()
            
            # Store display info
            self.display_info = {
                'current_w': info.current_w,
                'current_h': info.current_h,
                'desktop_w': getattr(info, 'desktop_w', info.current_w),
                'desktop_h': getattr(info, 'desktop_h', info.current_h),
            }
            
            print(f"🖥️ Display detected: {self.display_info['current_w']} x {self.display_info['current_h']}")
            
            # Detect display type
            self._detect_display_type()
            
            # Get native resolution
            self._get_native_resolution()
            
            # Generate available resolutions
            self._generate_resolution_list()
            
            # Set optimal resolution
            self._set_optimal_resolution()
            
        except Exception as e:
            print(f"⚠️ Error detecting display: {e}")
            self._fallback_setup()
    
    def _detect_display_type(self) -> None:
        """Detect the type of display (Retina, High DPI, etc.)."""
        width = self.display_info['current_w']
        height = self.display_info['current_h']
        
        # Check for Retina (Mac)
        if sys.platform == "darwin":
            try:
                result = subprocess.run(['system_profiler', 'SPDisplaysDataType'], 
                                      capture_output=True, text=True, timeout=5)
                if 'Retina' in result.stdout or width > 2000:
                    self.display_type = DisplayType.RETINA
                    self.scale_factor = 2.0
                    print("🍎 Retina display detected")
                    return
            except:
                pass
        
        # Check for High DPI (Windows/Linux)
        if width > 1920 or height > 1080:
            self.display_type = DisplayType.HIGH_DPI
            self.scale_factor = 1.5
            print("🖥️ High DPI display detected")
            return
        
        # Check for Ultra Wide
        aspect_ratio = width / height
        if aspect_ratio > 2.0:
            self.display_type = DisplayType.ULTRA_WIDE
            print("📐 Ultra-wide display detected")
        
        # Default to standard
        self.display_type = DisplayType.STANDARD
        self.scale_factor = 1.0
        print("🖥️ Standard display detected")
    
    def _get_native_resolution(self) -> None:
        """Get the native resolution of the display."""
        width = self.display_info['current_w']
        height = self.display_info['current_h']
        
        # For Retina displays, the reported resolution might be scaled
        if self.display_type == DisplayType.RETINA:
            # Try to get actual native resolution
            try:
                result = subprocess.run(['system_profiler', 'SPDisplaysDataType'], 
                                      capture_output=True, text=True, timeout=5)
                # Parse for actual resolution (this is simplified)
                if '3456 x 2234' in result.stdout:
                    width, height = 3456, 2234
                elif '3072 x 1920' in result.stdout:
                    width, height = 3072, 1920
                elif '2560 x 1600' in result.stdout:
                    width, height = 2560, 1600
            except:
                pass
        
        self.native_resolution = Resolution(width, height, width/height, (width*height)/(1920*1080), True)
        print(f"📐 Native resolution: {width} x {height}")
    
    def _generate_resolution_list(self) -> None:
        """Generate list of available resolutions for this display."""
        self.available_resolutions = []
        
        # Add standard resolutions that fit the display
        max_width = self.display_info['current_w']
        max_height = self.display_info['current_h']
        
        for width, height in self.standard_resolutions:
            if width <= max_width and height <= max_height:
                res = Resolution(width, height, width/height, (width*height)/(1920*1080))
                self.available_resolutions.append(res)
        
        # Add native resolution if not already included
        if self.native_resolution not in self.available_resolutions:
            self.available_resolutions.append(self.native_resolution)
        
        # Sort by pixel density (highest first)
        self.available_resolutions.sort(key=lambda r: r.pixel_density, reverse=True)
        
        print(f"📐 Available resolutions: {len(self.available_resolutions)} options")
        for i, res in enumerate(self.available_resolutions[:5]):
            print(f"   {i+1}. {res.width} x {res.height} ({res.aspect_ratio:.2f})")
    
    def _set_optimal_resolution(self) -> None:
        """Set the optimal resolution for this display."""
        if not self.available_resolutions:
            self._fallback_setup()
            return
        
        # Find a reasonable resolution that's not too large
        max_reasonable_width = 1920
        max_reasonable_height = 1080
        
        # Look for a resolution that's not too large
        reasonable_resolution = None
        for res in self.available_resolutions:
            if res.width <= max_reasonable_width and res.height <= max_reasonable_height:
                reasonable_resolution = res
                break
        
        # If no reasonable resolution found, use the smallest available
        if reasonable_resolution is None:
            reasonable_resolution = self.available_resolutions[-1]  # Smallest (last in sorted list)
        
        self.current_resolution = reasonable_resolution
        
        # Calculate UI scale factor
        self._calculate_ui_scale()
        
        print(f"🎯 Selected resolution: {self.current_resolution.width} x {self.current_resolution.height}")
        print(f"📏 UI scale factor: {self.ui_scale_factor:.2f}")
    
    def _calculate_ui_scale(self) -> None:
        """Calculate UI scaling factor based on current resolution."""
        if not self.current_resolution:
            self.ui_scale_factor = 1.0
            return
        
        # Base scaling on 1920x1080
        base_width, base_height = 1920, 1080
        scale_x = self.current_resolution.width / base_width
        scale_y = self.current_resolution.height / base_height
        
        # Use the smaller scale to maintain proportions
        self.ui_scale_factor = min(scale_x, scale_y)
        
        # Apply display-specific adjustments
        if self.display_type == DisplayType.RETINA:
            self.ui_scale_factor *= 0.6  # Retina displays need smaller UI elements
        
        # Clamp to reasonable range - more conservative for better visibility
        self.ui_scale_factor = max(0.6, min(1.2, self.ui_scale_factor))
    
    def _fallback_setup(self) -> None:
        """Fallback setup when display detection fails."""
        self.display_type = DisplayType.STANDARD
        self.scale_factor = 1.0
        self.ui_scale_factor = 1.0
        self.current_resolution = Resolution(1920, 1080, 16/9, 1.0)
        self.native_resolution = self.current_resolution
        self.available_resolutions = [self.current_resolution]
        print("⚠️ Using fallback resolution: 1920x1080")
    
    def get_current_resolution(self) -> Resolution:
        """Get the current resolution."""
        return self.current_resolution
    
    def get_ui_scale_factor(self) -> float:
        """Get the UI scaling factor."""
        return self.ui_scale_factor
    
    def get_scale_factor(self) -> float:
        """Get the display scale factor."""
        return self.scale_factor
    
    def get_available_resolutions(self) -> List[Resolution]:
        """Get list of available resolutions."""
        return self.available_resolutions.copy()
    
    def set_resolution(self, resolution: Resolution) -> bool:
        """Set a new resolution."""
        if resolution in self.available_resolutions:
            self.current_resolution = resolution
            self._calculate_ui_scale()
            return True
        return False
    
    def is_high_resolution(self) -> bool:
        """Check if this is a high-resolution display."""
        return self.display_type in [DisplayType.RETINA, DisplayType.HIGH_DPI]
    
    def get_display_type(self) -> DisplayType:
        """Get the display type."""
        return self.display_type 