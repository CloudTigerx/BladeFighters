#!/usr/bin/env python3
"""
Test Script for Refactored TestMode Components
Tests the extracted components to ensure they work correctly.
"""

import pygame
import sys
import os

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, project_root)

def test_refactored_components():
    """Test the refactored TestMode components."""
    print("🧪 Testing Refactored TestMode Components")
    print("=" * 50)

    # Initialize pygame
    pygame.init()

    try:
        # Import the refactored components
        from modules.testmode_module.board_manager import BoardManager
        from modules.testmode_module.ai_manager import AIManager
        from modules.game_state_module.game_state_manager import GameStateManager
        from modules.testmode_module.input_handler import InputHandler

        print("✅ All refactored components imported successfully")

        # Create a test screen
        screen = pygame.display.set_mode((800, 600))
        font = pygame.font.SysFont(None, 24)
        from utils.clock import PygameClock
        clock = PygameClock()

        # Test BoardManager
        print("\n📐 Testing BoardManager:")
        board_manager = BoardManager(screen, font, None, "puzzleassets", None, clock)
        print(f"   ✅ BoardManager created successfully")
        
        player_pos, enemy_pos = board_manager.get_board_positions()
        print(f"   📍 Player position: {player_pos}")
        print(f"   📍 Enemy position: {enemy_pos}")
        
        cell_w, cell_h, board_w, board_h = board_manager.get_board_dimensions()
        print(f"   📏 Cell size: {cell_w}x{cell_h}")
        print(f"   📏 Board size: {board_w}x{board_h}")

        # Test AIManager
        print("\n🤖 Testing AIManager:")
        ai_manager = AIManager(initial_difficulty=5)
        print(f"   ✅ AIManager created successfully")
        print(f"   🎯 Initial difficulty: {ai_manager.get_difficulty()}")
        
        ai_manager.set_difficulty(8)
        print(f"   🎯 Difficulty set to: {ai_manager.get_difficulty()}")
        
        ai_manager.adjust_difficulty(1)
        print(f"   🎯 Difficulty adjusted to: {ai_manager.get_difficulty()}")

        # Test GameStateManager
        print("\n🎮 Testing GameStateManager:")
        game_state_manager = GameStateManager("puzzleassets", clock)
        print(f"   ✅ GameStateManager created successfully")
        
        flags = game_state_manager.get_flags()
        print(f"   🚩 Feature flags: {len(flags)} flags loaded")
        
        player_items = game_state_manager.get_player_items()
        enemy_items = game_state_manager.get_enemy_items()
        print(f"   🛡️ Player items: {type(player_items).__name__}")
        print(f"   🛡️ Enemy items: {type(enemy_items).__name__}")

        # Test InputHandler
        print("\n⌨️ Testing InputHandler:")
        input_handler = InputHandler(ai_manager, game_state_manager)
        print(f"   ✅ InputHandler created successfully")

        # Test component integration
        print("\n🔗 Testing Component Integration:")
        
        # Test board manager with engines
        player_engine, enemy_engine = board_manager.get_engines()
        print(f"   ✅ Player engine: {type(player_engine).__name__}")
        print(f"   ✅ Enemy engine: {type(enemy_engine).__name__}")
        
        # Test renderers
        player_renderer, enemy_renderer = board_manager.get_renderers()
        print(f"   ✅ Player renderer: {type(player_renderer).__name__}")
        print(f"   ✅ Enemy renderer: {type(enemy_renderer).__name__}")

        # Test AI integration
        current_time = clock.now_ms()
        ai_manager.update_ai(enemy_engine, current_time)
        print(f"   ✅ AI update completed")

        # Test game state reset
        game_state_manager.reset_chain_states()
        print(f"   ✅ Chain states reset")

        # Test input processing
        test_events = []
        result = input_handler.process_events(test_events, player_engine, current_time)
        print(f"   ✅ Input processing completed (result: {result})")

        print("\n🎉 All refactored components working correctly!")
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

def test_component_creation():
    """Test creating components with minimal dependencies."""
    print("\n🔧 Testing Component Creation:")
    
    try:
        # Test AIManager (minimal dependencies)
        from modules.testmode_module.ai_manager import AIManager
        ai_manager = AIManager(initial_difficulty=3)
        print(f"   ✅ AIManager created with difficulty {ai_manager.get_difficulty()}")
        
        # Test GameStateManager (requires asset_path)
        from modules.game_state_module.game_state_manager import GameStateManager
        game_state = GameStateManager("puzzleassets")
        print(f"   ✅ GameStateManager created")
        
        print("   ✅ Component creation tests passed")
        return True
        
    except Exception as e:
        print(f"   ❌ Component creation error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 TestMode Component Refactoring Test")
    print("=" * 50)

    # Run component creation tests first
    creation_success = test_component_creation()
    
    if creation_success:
        print("\n" + "=" * 50)
        print("🎯 Component creation passed! Starting full integration test...")
        print("Press any key to continue...")
        input()
        
        # Run full integration test
        integration_success = test_refactored_components()
        
        if integration_success:
            print("\n🎉 All tests passed! Refactoring is working correctly.")
        else:
            print("\n❌ Integration tests failed. Please check the errors above.")
            sys.exit(1)
    else:
        print("\n❌ Component creation failed. Please check the errors above.")
        sys.exit(1) 