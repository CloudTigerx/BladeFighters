#!/usr/bin/env python3
"""
Test Script for 4K Asset Loading
Demonstrates the true resolution scaling system with your 4K assets.
"""

import pygame
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_4k_asset_loading():
    """Test the 4K asset loading system."""
    print("🎮 Testing 4K Asset Loading System")
    print("=" * 50)
    
    # Initialize pygame
    pygame.init()
    
    try:
        # Import the scaling system
        from core.scaling import resolution_manager, true_resolution_scaler
        
        print("✅ True resolution scaler imported successfully")
        
        # Test resolution detection
        print("\n📐 Current Resolution:")
        current_res = resolution_manager.get_current_resolution()
        print(f"   Resolution: {current_res.width} x {current_res.height}")
        print(f"   Display type: {resolution_manager.get_display_type().value}")
        
        # Test 4K asset loading
        print("\n🖼️ Testing 4K Asset Loading:")
        
        # Test loading your main menu background
        background = true_resolution_scaler.load_background(
            'Official_mainmenu_background',
            fallback_path='puzzleassets/menus/Official_mainmenu_background.png'
        )
        
        if background:
            print(f"   ✅ Background loaded successfully!")
            print(f"   📏 Background size: {background.get_width()} x {background.get_height()}")
            print(f"   🎯 Expected for 4K: 3840 x 2160")
            
            # Check if it's actually 4K
            if background.get_width() >= 3840 and background.get_height() >= 2160:
                print("   🏆 SUCCESS: 4K asset loaded!")
            else:
                print("   ⚠️ Loaded asset is not 4K resolution")
        else:
            print("   ❌ Failed to load background")
        
        # Test cache info
        print("\n💾 Cache Information:")
        cache_info = true_resolution_scaler.get_cache_info()
        print(f"   Total cached assets: {cache_info['total_assets']}")
        if cache_info['cached_keys']:
            print(f"   Cached keys: {cache_info['cached_keys']}")
        
        # Test different asset types
        print("\n🧪 Testing Different Asset Types:")
        
        # Test UI element loading
        ui_element = true_resolution_scaler.load_ui_element(
            'button_hover',
            fallback_path='puzzleassets/menus/button_hover.png'
        )
        if ui_element:
            print(f"   ✅ UI element loaded: {ui_element.get_size()}")
        
        # Test block loading
        block = true_resolution_scaler.load_block(
            '1x4',
            fallback_path='puzzleassets/strikes/1x4.png'
        )
        if block:
            print(f"   ✅ Block loaded: {block.get_size()}")
        
        print("\n🎉 4K Asset Loading Test Complete!")
        print("\n📝 Next Steps:")
        print("   1. Rename your assets to follow the pattern:")
        print("      Official_mainmenu_background_ultra.png")
        print("      Official_mainmenu_background_medium.png") 
        print("      Official_mainmenu_background_low.png")
        print("   2. Create similar versions for other assets")
        print("   3. The system will automatically pick the best one!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        pygame.quit()

if __name__ == "__main__":
    test_4k_asset_loading()
