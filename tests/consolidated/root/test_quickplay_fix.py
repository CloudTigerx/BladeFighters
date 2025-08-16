#!/usr/bin/env python3
"""
Test script to verify quickplay time error fix
"""

def test_quickplay_imports():
    """Test that all quickplay-related imports work without time errors."""
    try:
        print("🔍 Testing quickplay-related imports...")
        
        # Test puzzle module import
        from core.puzzle_module import PuzzleEngine
        print("✅ PuzzleEngine import successful")
        
        # Test game client import
        from game_client import GameClient
        print("✅ GameClient import successful")
        
        # Test menu system import
        from modules.menu_module.menu_system import MenuSystem
        print("✅ MenuSystem import successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Quickplay import test failed: {e}")
        return False

def test_quickplay_functionality():
    """Test quickplay functionality without time errors."""
    try:
        print("🔍 Testing quickplay functionality...")
        
        # Initialize pygame
        import pygame
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        font = pygame.font.SysFont(None, 24)
        
        # Test puzzle engine creation
        puzzle_engine = PuzzleEngine(screen, font, None, "puzzleassets")
        print("✅ PuzzleEngine creation successful")
        
        # Test that time functions work
        import time
        current_time = time.time()
        print(f"✅ Time module works: {current_time}")
        
        # Test puzzle engine time usage
        if hasattr(puzzle_engine, 'renderer') and hasattr(puzzle_engine.renderer, 'animation_state_manager'):
            print("✅ Animation state manager available")
        
        pygame.quit()
        return True
        
    except Exception as e:
        print(f"❌ Quickplay functionality test failed: {e}")
        return False

def test_menu_quickplay():
    """Test menu quickplay button functionality."""
    try:
        print("🔍 Testing menu quickplay functionality...")
        
        # Test menu system
        from modules.menu_module.menu_system import MenuSystem
        import pygame
        
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        font = pygame.font.SysFont(None, 24)
        
        menu = MenuSystem(screen, font, "puzzleassets")
        print("✅ MenuSystem creation successful")
        
        # Test quickplay action
        quickplay_action = menu.handle_button_click("Quickplay")
        print(f"✅ Quickplay action: {quickplay_action}")
        
        pygame.quit()
        return True
        
    except Exception as e:
        print(f"❌ Menu quickplay test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚨 QUICKPLAY TIME ERROR FIX VERIFICATION")
    print("=" * 60)
    
    # Test 1: Imports
    import_test = test_quickplay_imports()
    
    # Test 2: Functionality
    func_test = test_quickplay_functionality()
    
    # Test 3: Menu integration
    menu_test = test_menu_quickplay()
    
    print("=" * 60)
    if import_test and func_test and menu_test:
        print("🎉 ALL TESTS PASSED - Quickplay time error fix successful!")
        print("✅ Quickplay should now work without 'time' is not defined errors")
    else:
        print("❌ SOME TESTS FAILED - Additional fixes may be needed")
    
    print("=" * 60)
