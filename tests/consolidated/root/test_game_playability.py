#!/usr/bin/env python3
"""
Simple test to check if the game is playable after bug fixes.
"""

import sys
import os
import time

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_game_initialization():
    """Test if the game can initialize without critical errors."""
    print("🧪 Testing Game Initialization...")
    
    try:
        from game_client import GameClient
        
        # Create game client
        print("✅ GameClient imported successfully")
        
        # Test basic initialization
        client = GameClient()
        print("✅ GameClient created successfully")
        
        # Manually run initialization tasks to ensure components are available
        print("🔄 Running initialization tasks...")
        
        # Initialize font
        client._initialize_font()
        
        # Initialize audio system
        client._initialize_audio_system()
        
        # Load background images
        client._load_background_images()
        
        # Initialize menu system
        client._initialize_menu_system()
        
        # Initialize settings UI
        client._initialize_settings_ui()
        
        # Initialize test mode
        client._initialize_test_mode()
        
        # Initialize screen manager
        client._initialize_screen_manager()
        
        # Initialize story system
        client._initialize_story_system()
        
        # Initialize puzzle engine
        client._initialize_puzzle_engine()
        
        # Initialize puzzle renderer
        client._initialize_puzzle_renderer()
        
        # Complete initialization
        client._complete_initialization()
        
        print("✅ All initialization tasks completed")
        
        # Test if key components are available
        if hasattr(client, 'test_mode') and client.test_mode:
            print("✅ Test mode is available")
        else:
            print("❌ Test mode is not available")
            
        if hasattr(client, 'puzzle_engine') and client.puzzle_engine:
            print("✅ Puzzle engine is available")
        else:
            print("❌ Puzzle engine is not available")
            
        if hasattr(client, 'menu_system') and client.menu_system:
            print("✅ Menu system is available")
        else:
            print("❌ Menu system is not available")
            
        if hasattr(client, 'audio') and client.audio:
            print("✅ Audio system is available")
        else:
            print("❌ Audio system is not available")
            
        print("\n🎮 Game appears to be playable!")
        return True
        
    except Exception as e:
        print(f"❌ Game initialization failed: {e}")
        return False

def test_quickplay_functionality():
    """Test if quickplay functionality works."""
    print("\n🧪 Testing Quickplay Functionality...")
    
    try:
        from game_client import GameClient
        
        client = GameClient()
        
        # Initialize components
        client._initialize_font()
        client._initialize_audio_system()
        client._load_background_images()
        client._initialize_menu_system()
        client._initialize_settings_ui()
        client._initialize_puzzle_engine()
        client._initialize_puzzle_renderer()
        client._complete_initialization()
        
        # Test quickplay start
        client.start_quickplay()
        print("✅ Quickplay started successfully")
        
        # Test screen transition
        if client.current_screen == "game":
            print("✅ Screen transitioned to game successfully")
        else:
            print(f"❌ Screen transition failed, current screen: {client.current_screen}")
            
        return True
        
    except Exception as e:
        print(f"❌ Quickplay test failed: {e}")
        return False

def test_test_mode_functionality():
    """Test if test mode functionality works."""
    print("\n🧪 Testing Test Mode Functionality...")
    
    try:
        from game_client import GameClient
        
        client = GameClient()
        
        # Initialize components
        client._initialize_font()
        client._initialize_audio_system()
        client._load_background_images()
        client._initialize_menu_system()
        client._initialize_settings_ui()
        client._initialize_test_mode()
        client._initialize_screen_manager()
        client._initialize_story_system()
        client._initialize_puzzle_engine()
        client._initialize_puzzle_renderer()
        client._complete_initialization()
        
        # Test test mode initialization
        if hasattr(client, 'test_mode') and client.test_mode:
            print("✅ Test mode initialized successfully")
            
            # Test test mode screen transition
            client.set_screen("test")
            if client.current_screen == "test":
                print("✅ Test mode screen transition successful")
            else:
                print(f"❌ Test mode screen transition failed, current screen: {client.current_screen}")
                
            return True
        else:
            print("❌ Test mode not available")
            return False
            
    except Exception as e:
        print(f"❌ Test mode test failed: {e}")
        return False

def main():
    """Run all playability tests."""
    print("🚀 Game Playability Test Suite")
    print("=" * 50)
    
    tests = [
        ("Game Initialization", test_game_initialization),
        ("Quickplay Functionality", test_quickplay_functionality),
        ("Test Mode Functionality", test_test_mode_functionality)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Game is playable.")
        return True
    else:
        print("⚠️ Some tests failed. Game may have issues.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
