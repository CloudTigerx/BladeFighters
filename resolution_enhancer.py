"""
Resolution Enhancement Module for BladeFighters
Handles high-resolution displays and Retina scaling on Mac
"""

import pygame
import os
import sys

class ResolutionEnhancer:
    def __init__(self):
        self.is_mac = sys.platform == "darwin"
        self.is_retina = False
        self.scale_factor = 1.0
        self.original_resolutions = [
            (800, 600),
            (1024, 768),
            (1280, 720),
            (1366, 768),
            (1600, 900),
            (1920, 1080)
        ]
        self.enhanced_resolutions = []
        self.detect_display_capabilities()
    
    def detect_display_capabilities(self):
        """Detect display capabilities and set up appropriate resolutions."""
        try:
            # Initialize pygame display to get info
            pygame.init()
            info = pygame.display.Info()
            
            # Get actual screen dimensions
            screen_width = info.current_w
            screen_height = info.current_h
            
            print(f"🖥️ Detected screen: {screen_width} x {screen_height}")
            
            # On Mac, check for Retina display and get native resolution
            if self.is_mac:
                # Try to get the native resolution using system commands
                try:
                    import subprocess
                    result = subprocess.run(['system_profiler', 'SPDisplaysDataType'], 
                                          capture_output=True, text=True)
                    if '3456 x 2234' in result.stdout:
                        print("🍎 Native Retina display detected: 3456 x 2234")
                        self.is_retina = True
                        self.scale_factor = 2.0
                        # Use native resolution for high-quality rendering
                        screen_width = 3456
                        screen_height = 2234
                except:
                    pass
                
                # Check if current resolution suggests Retina scaling
                if screen_width > 1600 and screen_width < 2000:
                    print("🍎 Scaled Retina display detected")
                    self.is_retina = True
                    self.scale_factor = 2.0
            
            # Create enhanced resolution list
            self.create_enhanced_resolutions(screen_width, screen_height)
            
        except Exception as e:
            print(f"⚠️ Error detecting display: {e}")
            self.enhanced_resolutions = self.original_resolutions.copy()
    
    def create_enhanced_resolutions(self, screen_width, screen_height):
        """Create a list of resolutions appropriate for the current display."""
        self.enhanced_resolutions = []
        
        # Add original resolutions
        self.enhanced_resolutions.extend(self.original_resolutions)
        
        # Add high-resolution options for Retina displays
        if self.is_retina:
            high_res_options = [
                (2560, 1440),  # 2K
                (2880, 1800),  # MacBook Pro Retina
                (3072, 1920),  # MacBook Pro 16"
                (3456, 2234),  # Your Mac's resolution
                (3840, 2160),  # 4K
            ]
            
            for res in high_res_options:
                if res[0] <= screen_width and res[1] <= screen_height:
                    if res not in self.enhanced_resolutions:
                        self.enhanced_resolutions.append(res)
        
        # Add common Mac resolutions
        mac_resolutions = [
            (1440, 900),   # MacBook Air
            (1680, 1050),  # MacBook Pro 15"
            (1792, 1120),  # MacBook Air 13"
            (1920, 1200),  # MacBook Pro 13"
            (2048, 1280),  # MacBook Air 13" Retina
            (2304, 1440),  # MacBook Pro 13" Retina
            (2560, 1600),  # MacBook Pro 15" Retina
        ]
        
        for res in mac_resolutions:
            if res[0] <= screen_width and res[1] <= screen_height:
                if res not in self.enhanced_resolutions:
                    self.enhanced_resolutions.append(res)
        
        # Sort resolutions by area (largest first)
        self.enhanced_resolutions.sort(key=lambda x: x[0] * x[1], reverse=True)
        
        print(f"📐 Available resolutions: {len(self.enhanced_resolutions)} options")
        for i, res in enumerate(self.enhanced_resolutions[:5]):  # Show top 5
            print(f"   {i+1}. {res[0]} x {res[1]}")
    
    def get_optimal_resolution(self, screen_width, screen_height):
        """Get the optimal resolution for the current display."""
        # Find the best resolution that fits the screen
        for res in self.enhanced_resolutions:
            if res[0] <= screen_width and res[1] <= screen_height:
                return res
        
        # Fallback to the highest available resolution
        return self.enhanced_resolutions[0] if self.enhanced_resolutions else (1920, 1080)
    
    def get_resolution_list(self):
        """Get the list of available resolutions."""
        return self.enhanced_resolutions
    
    def is_high_resolution_display(self):
        """Check if this is a high-resolution display."""
        return self.is_retina or any(res[0] > 1920 for res in self.enhanced_resolutions)
    
    def get_scale_factor(self):
        """Get the display scale factor."""
        return self.scale_factor
    
    def create_scaled_surface(self, surface, target_size):
        """Create a scaled surface for high-resolution displays."""
        if not self.is_retina:
            return surface
        
        # Scale the surface for Retina displays
        scaled_surface = pygame.transform.smoothscale(surface, target_size)
        return scaled_surface
    
    def get_font_size_for_resolution(self, base_size, width, height):
        """Calculate appropriate font size for the given resolution."""
        # Base font size on screen height
        scale_factor = min(width / 1920, height / 1080)
        return max(int(base_size * scale_factor), 12)  # Minimum 12px
    
    def get_ui_scale_factor(self, width, height):
        """Get UI scaling factor for the given resolution."""
        # Base scaling on 1920x1080
        base_width, base_height = 1920, 1080
        scale_x = width / base_width
        scale_y = height / base_height
        return min(scale_x, scale_y)  # Use the smaller scale to maintain proportions

# Global instance
resolution_enhancer = ResolutionEnhancer() 