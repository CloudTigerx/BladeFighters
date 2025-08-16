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
        
        # Supported resolutions (only the 4 we have assets for)
        self.supported_resolutions = [
            (800, 600),     # Low resolution assets
            (1536, 1024),   # Medium resolution assets  
            (1920, 1080),   # High resolution assets
            (3840, 2160),   # Ultra resolution assets
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
        
        # Only use our 4 supported resolutions
        max_width = self.display_info['current_w']
        max_height = self.display_info['current_h']
        
        for width, height in self.supported_resolutions:
            if width <= max_width and height <= max_height:
                res = Resolution(width, height, width/height, (width*height)/(1920*1080))
                self.available_resolutions.append(res)
        
        # Sort by pixel density (highest first)
        self.available_resolutions.sort(key=lambda r: r.pixel_density, reverse=True)
        
        print(f"📐 Available resolutions: {len(self.available_resolutions)} options")
        for i, res in enumerate(self.available_resolutions):
            print(f"   {i+1}. {res.width} x {res.height} ({res.aspect_ratio:.2f})")
    
    def _set_optimal_resolution(self) -> None:
        """Set the optimal resolution for this display."""
        if not self.available_resolutions:
            self._fallback_setup()
            return
        
        # Use the native resolution for better UI scaling on large monitors
        # This ensures the UI elements are properly sized for the actual display
        if self.native_resolution:
            self.current_resolution = self.native_resolution
        else:
            # Fallback to the highest resolution available
            self.current_resolution = self.available_resolutions[0]  # Highest (first in sorted list)
        
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
        
        # Use the average scale for better visibility on large monitors
        # This prevents UI elements from being too small on wide screens
        self.ui_scale_factor = (scale_x + scale_y) / 2
        
        # Apply display-specific adjustments
        if self.display_type == DisplayType.RETINA:
            self.ui_scale_factor *= 0.7  # Slightly less aggressive for Retina
        
        # Clamp to reasonable range - more generous for better visibility
        self.ui_scale_factor = max(0.8, min(1.5, self.ui_scale_factor))
    
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