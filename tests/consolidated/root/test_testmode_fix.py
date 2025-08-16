#!/usr/bin/env python3
"""
Quick test to verify test mode time import fix
"""

def test_testmode_import():
    """Test that test mode imports correctly without time errors."""
    try:
        print("🔍 Testing test mode import...")
        from modules.testmode_module.test_mode import TestModeRefactored
        print("✅ TestModeRefactored import successful")
        
        # Test that we can create an instance (with mock parameters)
        import pygame
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        font = pygame.font.SysFont(None, 24)
        
        test_mode = TestModeRefactored(screen, font, None, "puzzleassets")
        print("✅ TestModeRefactored instantiation successful")
        
        pygame.quit()
        return True
        
    except Exception as e:
        print(f"❌ Test mode import failed: {e}")
        return False

def test_time_import():
    """Test that time module is available in test mode."""
    try:
        print("🔍 Testing time import in test mode...")
        from modules.testmode_module.test_mode import time
        print("✅ Time import successful in test mode")
        return True
    except Exception as e:
        print(f"❌ Time import failed: {e}")
        return False

if __name__ == "__main__":
    print("🚨 CRITICAL FIX VERIFICATION - Test Mode Time Import")
    print("=" * 60)
    
    # Test 1: Time import
    time_test = test_time_import()
    
    # Test 2: Full test mode import
    import_test = test_testmode_import()
    
    print("=" * 60)
    if time_test and import_test:
        print("🎉 ALL TESTS PASSED - Test mode time import fix successful!")
        print("✅ Test mode should now work without 'time' is not defined errors")
    else:
        print("❌ SOME TESTS FAILED - Additional fixes may be needed")
    
    print("=" * 60)
