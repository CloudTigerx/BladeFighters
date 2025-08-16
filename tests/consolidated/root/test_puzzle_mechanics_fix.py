#!/usr/bin/env python3
"""
Test script to verify puzzle mechanics fixes:
1. Space bar acceleration
2. Up/Down rotation
3. Attack system functionality
"""

import pygame
import time
import sys

def test_space_bar_acceleration():
    """Test that space bar properly accelerates piece falling."""
    try:
        print("🔍 Testing space bar acceleration...")
        
        # Initialize pygame
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        font = pygame.font.SysFont(None, 24)
        
        # Import puzzle engine
        from core.puzzle_module import PuzzleEngine
        print("✅ PuzzleEngine import successful")
        
        # Create puzzle engine
        engine = PuzzleEngine(screen, font, None, "puzzleassets")
        print("✅ PuzzleEngine creation successful")
        
        # Start game
        engine.start_game()
        print("✅ Game started")
        
        # Check initial fall speed
        initial_speed = engine.current_fall_speed
        print(f"Initial fall speed: {initial_speed}")
        
        # Simulate space bar press
        engine.input_handler._handle_spacebar_press()
        
        # Check accelerated fall speed
        accelerated_speed = engine.current_fall_speed
        print(f"Accelerated fall speed: {accelerated_speed}")
        
        # Verify acceleration worked
        if accelerated_speed < initial_speed:
            print("✅ Space bar acceleration working")
        else:
            print("❌ Space bar acceleration failed")
            return False
        
        # Simulate space bar release
        engine.input_handler._handle_spacebar_release()
        
        # Check normal fall speed restored
        restored_speed = engine.current_fall_speed
        print(f"Restored fall speed: {restored_speed}")
        
        # Verify speed was restored
        if restored_speed == initial_speed:
            print("✅ Space bar release working")
        else:
            print("❌ Space bar release failed")
            return False
        
        pygame.quit()
        return True
        
    except Exception as e:
        print(f"❌ Space bar acceleration test failed: {e}")
        return False

def test_up_down_rotation():
    """Test that up/down keys rotate pieces instead of moving them."""
    try:
        print("🔍 Testing up/down rotation...")
        
        # Initialize pygame
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        font = pygame.font.SysFont(None, 24)
        
        # Import puzzle engine
        from core.puzzle_module import PuzzleEngine
        print("✅ PuzzleEngine import successful")
        
        # Create puzzle engine
        engine = PuzzleEngine(screen, font, None, "puzzleassets")
        print("✅ PuzzleEngine creation successful")
        
        # Start game
        engine.start_game()
        print("✅ Game started")
        
        # Check initial attached position
        initial_position = engine.attached_position
        print(f"Initial attached position: {initial_position}")
        
        # Test up key rotation (counter-clockwise)
        engine.rotate_attached_piece(-1)
        up_position = engine.attached_position
        print(f"After up key rotation: {up_position}")
        
        # Test down key rotation (clockwise)
        engine.rotate_attached_piece(1)
        down_position = engine.attached_position
        print(f"After down key rotation: {down_position}")
        
        # Verify rotations worked
        if up_position != initial_position or down_position != initial_position:
            print("✅ Up/down rotation working")
        else:
            print("❌ Up/down rotation failed")
            return False
        
        pygame.quit()
        return True
        
    except Exception as e:
        print(f"❌ Up/down rotation test failed: {e}")
        return False

def test_attack_system():
    """Test that attack system is functional."""
    try:
        print("🔍 Testing attack system...")
        
        # Import attack service
        from modules.attack_module.attacks_service import AttacksService
        print("✅ AttacksService import successful")
        
        # Create attack service
        service = AttacksService()
        print("✅ AttacksService creation successful")
        
        # Test on_combo method
        test_blocks = [(0, 0, 'red_block'), (1, 0, 'blue_block')]
        service.on_combo(test_blocks, is_cluster=False, combo_multiplier=1, player_id=1)
        print("✅ on_combo call successful")
        
        # Test process_combo method
        service.process_combo(test_blocks, is_cluster=False, chain_multiplier=1, player_id=1)
        print("✅ process_combo call successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Attack system test failed: {e}")
        return False

def test_continuous_key_handling():
    """Test that continuous key handling works properly."""
    try:
        print("🔍 Testing continuous key handling...")
        
        # Initialize pygame
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        font = pygame.font.SysFont(None, 24)
        
        # Import puzzle engine
        from core.puzzle_module import PuzzleEngine
        print("✅ PuzzleEngine import successful")
        
        # Create puzzle engine
        engine = PuzzleEngine(screen, font, None, "puzzleassets")
        print("✅ PuzzleEngine creation successful")
        
        # Start game
        engine.start_game()
        print("✅ Game started")
        
        # Test that continuous key handling can be called
        engine.input_handler._handle_continuous_keys()
        print("✅ Continuous key handling call successful")
        
        # Test that update method calls continuous key handling
        engine.update()
        print("✅ Update method with continuous key handling successful")
        
        pygame.quit()
        return True
        
    except Exception as e:
        print(f"❌ Continuous key handling test failed: {e}")
        return False

def run_mechanics_test():
    """Run all puzzle mechanics tests."""
    print("🚨 PUZZLE MECHANICS FIX VERIFICATION")
    print("=" * 60)
    
    tests = [
        ("Space Bar Acceleration", test_space_bar_acceleration),
        ("Up/Down Rotation", test_up_down_rotation),
        ("Attack System", test_attack_system),
        ("Continuous Key Handling", test_continuous_key_handling)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}")
        print("-" * 40)
        try:
            result = test_func()
            results[test_name] = result
            if result:
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
            results[test_name] = False
    
    print("\n" + "=" * 60)
    print("📊 MECHANICS FIX RESULTS")
    print("=" * 60)
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 OVERALL RESULT: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Puzzle mechanics are fixed!")
        print("✅ Space bar acceleration working")
        print("✅ Up/down rotation working")
        print("✅ Attack system functional")
        print("✅ Continuous key handling working")
    else:
        print("⚠️ SOME TESTS FAILED - Additional fixes may be needed")
        
        if not results.get("Space Bar Acceleration", True):
            print("   - Space bar acceleration issue")
        if not results.get("Up/Down Rotation", True):
            print("   - Up/down rotation issue")
        if not results.get("Attack System", True):
            print("   - Attack system issue")
        if not results.get("Continuous Key Handling", True):
            print("   - Continuous key handling issue")
    
    print("=" * 60)
    return passed == total

if __name__ == "__main__":
    success = run_mechanics_test()
    sys.exit(0 if success else 1)

