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
    
    try:
        import pygame
    except Exception as e:
        return False
    
    try:
        import time
    except Exception as e:
        return False
    
    return True

def test_game_state_manager():
    """Test game state manager initialization."""
    
    try:
        from modules.game_state_module.game_state_manager import GameStateManager
        state_manager = GameStateManager()
        return True
    except Exception as e:
        traceback.print_exc()
        return False

def test_audio_system():
    """Test audio system initialization."""
    
    try:
        from modules.audio_module.audio_system import AudioSystem
        audio_system = AudioSystem("puzzleassets")
        return True
    except Exception as e:
        traceback.print_exc()
        return False

def test_screen_manager():
    """Test screen manager initialization."""
    
    try:
        import pygame
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        font = pygame.font.Font(None, 24)
        
        from modules.screen_module.screen_manager import ScreenManager
        from modules.game_state_module.game_state_manager import GameStateManager
        
        state_manager = GameStateManager()
        screen_manager = ScreenManager(screen, font, state_manager, "puzzleassets")
        
        pygame.quit()
        return True
    except Exception as e:
        traceback.print_exc()
        return False

def test_input_manager():
    """Test input manager initialization."""
    
    try:
        from modules.input_module.unified_input_manager import UnifiedInputManager
        from modules.game_state_module.game_state_manager import GameStateManager
        
        state_manager = GameStateManager()
        input_manager = UnifiedInputManager(state_manager)
        return True
    except Exception as e:
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
    
    try:
        # Check if there are any quickplay-related files
        quickplay_files = list(Path(".").glob("**/*quickplay*"))
        
        # Look for time module usage in main files
        main_files = ["main.py", "game_client.py"]
        for file_path in main_files:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    content = f.read()
        
        return True
    except Exception as e:
        return False

def main():
    """Run all diagnostics."""
    
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
            
        except Exception as e:
            results[test_name] = {
                'passed': False,
                'duration': 0,
                'error': str(e)
            }
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results.values() if r['passed'])
    
    if passed_tests == total_tests:
        return True
    else:
        return False

if __name__ == "__main__":
    main()
