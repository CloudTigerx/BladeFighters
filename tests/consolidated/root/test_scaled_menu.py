#!/usr/bin/env python3
"""
Test Script for Scaled Menu System
Demonstrates the difference between old and new menu positioning.
"""

import pygame
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_scaled_menu():
    """Test the scaled menu system."""
    print("🧪 Testing Scaled Menu System")
    print("=" * 50)
    
    # Initialize pygame
    pygame.init()
    
    try:
        # Import both menu systems
        from modules.menu_module.menu_system import MenuSystem
        from modules.menu_module.scaled_menu_system import ScaledMenuSystem
        
        print("✅ Both menu systems imported successfully")
        
        # Test different resolutions
        test_resolutions = [
            (1920, 1080),  # Standard 1080p
            (2560, 1440),  # 2K
            (3456, 2234),  # Your Retina Mac
            (800, 600),    # Low resolution
        ]
        
        for width, height in test_resolutions:
            print(f"\n📐 Testing resolution: {width} x {height}")
            
            # Create test screen
            screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
            pygame.display.set_caption(f"Menu Test - {width}x{height}")
            
            # Create font
            font = pygame.font.SysFont(None, 24)
            
            # Test scaled menu system
            try:
                scaled_menu = ScaledMenuSystem(screen, font, None, "puzzleassets")
                print(f"   ✅ Scaled menu created successfully")
                print(f"   📏 UI scale factor: {scaled_menu.ui_scaler.get_scale_factor():.2f}")
                print(f"   🎯 Button count: {len(scaled_menu.buttons.get('main', []))}")
                
                # Draw the menu
                scaled_menu.draw_main_menu(version="1.0.0")
                pygame.display.flip()
                
                # Wait a moment to see the result
                pygame.time.wait(2000)
                
            except Exception as e:
                print(f"   ❌ Scaled menu error: {e}")
        
        print("\n🎉 Scaled menu system test completed!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        pygame.quit()

def compare_positioning():
    """Compare positioning between old and new systems."""
    print("\n🔍 Positioning Comparison")
    print("=" * 50)
    
    # Example: Button positioning on different resolutions
    resolutions = [
        (1920, 1080),
        (3456, 2234),  # Your Retina Mac
    ]
    
    for width, height in resolutions:
        print(f"\n📐 Resolution: {width} x {height}")
        
        # Old way (hardcoded)
        old_button_x = 100
        old_button_y = 200
        old_button_width = 200
        old_button_height = 60
        
        print(f"   Old way (hardcoded):")
        print(f"     Button: ({old_button_x}, {old_button_y}) {old_button_width}x{old_button_height}")
        print(f"     Center: ({old_button_x + old_button_width//2}, {old_button_y + old_button_height//2})")
        
        # New way (scaled)
        # Simulate scaling calculation
        scale_factor = min(width / 1920, height / 1080)
        new_button_x = int((width - 200 * scale_factor) // 2)  # Centered
        new_button_y = int((height - 240 * scale_factor) // 2)  # Centered
        new_button_width = int(200 * scale_factor)
        new_button_height = int(60 * scale_factor)
        
        print(f"   New way (scaled):")
        print(f"     Scale factor: {scale_factor:.2f}")
        print(f"     Button: ({new_button_x}, {new_button_y}) {new_button_width}x{new_button_height}")
        print(f"     Center: ({new_button_x + new_button_width//2}, {new_button_y + new_button_height//2})")
        
        # Show the difference
        old_center_x = old_button_x + old_button_width//2
        old_center_y = old_button_y + old_button_height//2
        new_center_x = new_button_x + new_button_width//2
        new_center_y = new_button_y + new_button_height//2
        
        print(f"   Difference:")
        print(f"     X offset: {new_center_x - old_center_x} pixels")
        print(f"     Y offset: {new_center_y - old_center_y} pixels")

if __name__ == "__main__":
    print("🚀 Scaled Menu System Test")
    print("=" * 50)
    
    # Run positioning comparison
    compare_positioning()
    
    print("\n" + "=" * 50)
    print("🎯 Starting visual menu test...")
    print("Press any key to continue...")
    input()
    
    # Run visual test
    test_scaled_menu() 