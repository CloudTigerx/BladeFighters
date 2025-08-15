#!/usr/bin/env python3
"""
Quick startup diagnostic to identify blocking issues.
"""

import sys
import os
import time
import traceback
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

def test_imports():
    """Test basic imports."""
    print("🔍 Testing imports...")
    
    try:
        import pygame
        print("✅ Pygame imported successfully")
    except Exception as e:
        print(f"❌ Pygame import failed: {e}")
        return False
    
    try:
        import time
        print("✅ Time module imported successfully")
    except Exception as e:
        print(f"❌ Time module import failed: {e}")
        return False
    
    return True

def test_game_state_manager():
    """Test game state manager initialization."""
    print("\n🔍 Testing GameStateManager...")
    
    try:
        from modules.game_state_module.game_state_manager import GameStateManager
        state_manager = GameStateManager()
        print("✅ GameStateManager initialized successfully")
        return True
    except Exception as e:
        print(f"❌ GameStateManager initialization failed: {e}")
        traceback.print_exc()
        return False

def test_audio_system():
    """Test audio system initialization."""
    print("\n🔍 Testing AudioSystem...")
    
    try:
        from modules.audio_module.audio_system import AudioSystem
        audio_system = AudioSystem("puzzleassets")
        print("✅ AudioSystem initialized successfully")
        return True
    except Exception as e:
        print(f"❌ AudioSystem initialization failed: {e}")
        traceback.print_exc()
        return False

def test_screen_manager():
    """Test screen manager initialization."""
    print("\n🔍 Testing ScreenManager...")
    
    try:
        import pygame
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        font = pygame.font.Font(None, 24)
        
        from modules.screen_module.screen_manager import ScreenManager
        from modules.game_state_module.game_state_manager import GameStateManager
        
        state_manager = GameStateManager()
        screen_manager = ScreenManager(screen, font, state_manager, "puzzleassets")
        print("✅ ScreenManager initialized successfully")
        
        pygame.quit()
        return True
    except Exception as e:
        print(f"❌ ScreenManager initialization failed: {e}")
        traceback.print_exc()
        return False

def test_input_manager():
    """Test input manager initialization."""
    print("\n🔍 Testing UnifiedInputManager...")
    
    try:
        from modules.input_module.unified_input_manager import UnifiedInputManager
        from modules.game_state_module.game_state_manager import GameStateManager
        
        state_manager = GameStateManager()
        input_manager = UnifiedInputManager(state_manager)
        print("✅ UnifiedInputManager initialized successfully")
        return True
    except Exception as e:
        print(f"❌ UnifiedInputManager initialization failed: {e}")
        traceback.print_exc()
        return False

def test_main_game_client():
    """Test main game client initialization."""
    print("\n🔍 Testing GameClient...")
    
    try:
        from game_client import GameClient
        
        # Test with minimal initialization
        client = GameClient()
        print("✅ GameClient initialized successfully")
        return True
    except Exception as e:
        print(f"❌ GameClient initialization failed: {e}")
        traceback.print_exc()
        return False

def test_quickplay_functionality():
    """Test quickplay functionality for time module issue."""
    print("\n🔍 Testing Quickplay functionality...")
    
    try:
        # Check if there are any quickplay-related files
        quickplay_files = list(Path(".").glob("**/*quickplay*"))
        print(f"Found {len(quickplay_files)} quickplay-related files")
        
        # Look for time module usage in main files
        main_files = ["main.py", "game_client.py"]
        for file_path in main_files:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    content = f.read()
                    if "time" in content:
                        print(f"✅ Time module found in {file_path}")
                    else:
                        print(f"⚠️  Time module not found in {file_path}")
        
        return True
    except Exception as e:
        print(f"❌ Quickplay test failed: {e}")
        return False

def main():
    """Run all diagnostics."""
    print("🚨 STARTUP DIAGNOSTIC")
    print("=" * 60)
    
    tests = [
        ("Basic Imports", test_imports),
        ("GameStateManager", test_game_state_manager),
        ("AudioSystem", test_audio_system),
        ("ScreenManager", test_screen_manager),
        ("InputManager", test_input_manager),
        ("GameClient", test_main_game_client),
        ("Quickplay", test_quickplay_functionality),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            start_time = time.time()
            result = test_func()
            duration = time.time() - start_time
            
            results[test_name] = {
                'passed': result,
                'duration': duration
            }
            
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name} ({duration:.2f}s)")
            
        except Exception as e:
            results[test_name] = {
                'passed': False,
                'duration': 0,
                'error': str(e)
            }
            print(f"💥 ERROR {test_name}: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 DIAGNOSTIC SUMMARY")
    print("=" * 60)
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results.values() if r['passed'])
    
    print(f"📊 Total Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {total_tests - passed_tests}")
    print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    print("\n🔍 Detailed Results:")
    for test_name, result in results.items():
        status = "✅ PASS" if result['passed'] else "❌ FAIL"
        duration = result.get('duration', 0)
        print(f"  {test_name}: {status} ({duration:.2f}s)")
        if 'error' in result:
            print(f"    Error: {result['error']}")
    
    if passed_tests == total_tests:
        print("\n🎉 All tests passed!")
        print("Startup should work correctly.")
    else:
        print(f"\n⚠️  {total_tests - passed_tests} tests failed.")
        print("Fix the failing tests before proceeding.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
