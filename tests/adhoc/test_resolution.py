#!/usr/bin/env python3
"""
Test script to verify resolution detection and display
"""

import pygame
import sys
import subprocess

def get_native_resolution():
    """Get the native resolution from system."""
    try:
        result = subprocess.run(['system_profiler', 'SPDisplaysDataType'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            for line in lines:
                if 'Resolution:' in line:
                    parts = line.split(':')[1].strip().split('x')
                    if len(parts) == 2:
                        try:
                            width = int(parts[0].strip())
                            height_part = parts[1].strip()
                            height = int(height_part.split()[0])
                            return width, height
                        except ValueError:
                            continue
    except Exception as e:
        print(f"Error getting native resolution: {e}")
    return None

def main():
    """Test resolution detection and display."""
    pygame.init()
    
    print("🔍 Resolution Detection Test")
    print("=" * 40)
    
    # Get pygame's reported resolution
    info = pygame.display.Info()
    pygame_width, pygame_height = info.current_w, info.current_h
    print(f"📱 Pygame reports: {pygame_width}x{pygame_height}")
    
    # Get native resolution
    native = get_native_resolution()
    if native:
        native_width, native_height = native
        print(f"🖥️ Native resolution: {native_width}x{native_height}")
        
        if pygame_width != native_width or pygame_height != native_height:
            print(f"⚠️ Mismatch detected!")
            print(f"   Pygame: {pygame_width}x{pygame_height}")
            print(f"   Native: {native_width}x{native_height}")
            print(f"   This indicates macOS scaling is affecting pygame")
        else:
            print(f"✅ Resolution match - no scaling issues")
    else:
        print(f"❌ Could not detect native resolution")
    
    # Test creating a window
    print(f"\n🎮 Testing window creation...")
    
    # Test with pygame resolution
    print(f"   Creating window with pygame resolution: {pygame_width}x{pygame_height}")
    screen1 = pygame.display.set_mode((pygame_width, pygame_height), pygame.RESIZABLE)
    pygame.display.set_caption("Pygame Resolution Test")
    
    # Wait a moment
    pygame.time.wait(2000)
    
    # Test with native resolution (if different)
    if native and (native_width != pygame_width or native_height != pygame_height):
        print(f"   Creating window with native resolution: {native_width}x{native_height}")
        screen2 = pygame.display.set_mode((native_width, native_height), pygame.FULLSCREEN)
        pygame.display.set_caption("Native Resolution Test")
        
        # Wait a moment
        pygame.time.wait(2000)
    
    pygame.quit()
    print(f"✅ Test complete!")

if __name__ == "__main__":
    main()
