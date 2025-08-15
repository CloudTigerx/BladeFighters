#!/usr/bin/env python3
"""
Puzzle Engine Diagnostic Script
Identifies issues with piece spawning and attack system integration.
"""

import pygame
import time
import sys
from typing import Dict, Any, List

def test_piece_spawning():
    """Test piece spawning functionality."""
    try:
        print("🔍 Testing piece spawning...")
        
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
        
        # Test piece generation
        print(f"Initial main piece: {engine.main_piece}")
        print(f"Initial attached piece: {engine.attached_piece}")
        print(f"Next main piece: {engine.next_main_piece}")
        print(f"Next attached piece: {engine.next_attached_piece}")
        
        # Check if pieces are generated
        if engine.main_piece and engine.attached_piece:
            print("✅ Both main and attached pieces generated")
        else:
            print("❌ Missing pieces - only one or none generated")
            return False
        
        # Test piece position
        print(f"Piece position: {engine.piece_position}")
        print(f"Attached position: {engine.attached_position}")
        
        # Test piece movement
        engine.update_falling_piece()
        print("✅ Piece movement update successful")
        
        pygame.quit()
        return True
        
    except Exception as e:
        print(f"❌ Piece spawning test failed: {e}")
        return False

def test_attack_system_integration():
    """Test attack system integration."""
    try:
        print("🔍 Testing attack system integration...")
        
        # Import attack service
        from modules.attack_module.attacks_service import AttacksService
        print("✅ AttacksService import successful")
        
        # Create attack service
        service = AttacksService()
        print("✅ AttacksService creation successful")
        
        # Test on_combo method
        if hasattr(service, 'on_combo'):
            print("✅ on_combo method exists")
            
            # Test on_combo call with correct data format (x, y, block_type)
            test_blocks = [(0, 0, 'red_block'), (1, 0, 'blue_block')]
            service.on_combo(test_blocks, is_cluster=False, combo_multiplier=1, player_id=1)
            print("✅ on_combo call successful")
        else:
            print("❌ on_combo method missing")
            return False
        
        # Test process_combo method
        if hasattr(service, 'process_combo'):
            print("✅ process_combo method exists")
        else:
            print("❌ process_combo method missing")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Attack system integration test failed: {e}")
        return False

def test_testmode_integration():
    """Test test mode integration with attack system."""
    try:
        print("🔍 Testing test mode integration...")
        
        # Initialize pygame
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        font = pygame.font.SysFont(None, 24)
        
        # Import test mode
        from modules.testmode_module.test_mode import TestModeRefactored
        print("✅ TestModeRefactored import successful")
        
        # Create test mode
        test_mode = TestModeRefactored(screen, font, None, "puzzleassets")
        print("✅ TestModeRefactored creation successful")
        
        # Test attack coordinator
        if hasattr(test_mode, 'attack_coordinator'):
            print("✅ Attack coordinator exists")
            
            # Test attacks service
            if hasattr(test_mode.attack_coordinator, 'attacks_service'):
                print("✅ Attacks service exists")
                
                # Test on_combo method
                if hasattr(test_mode.attack_coordinator.attacks_service, 'on_combo'):
                    print("✅ on_combo method available in test mode")
                else:
                    print("❌ on_combo method missing in test mode")
                    return False
            else:
                print("❌ Attacks service missing")
                return False
        else:
            print("❌ Attack coordinator missing")
            return False
        
        pygame.quit()
        return True
        
    except Exception as e:
        print(f"❌ Test mode integration test failed: {e}")
        return False

def test_piece_generation_logic():
    """Test the piece generation logic specifically."""
    try:
        print("🔍 Testing piece generation logic...")
        
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
        
        # Test generate_new_piece method
        success = engine.generate_new_piece()
        print(f"generate_new_piece result: {success}")
        
        # Check pieces after generation
        print(f"Main piece: {engine.main_piece}")
        print(f"Attached piece: {engine.attached_piece}")
        print(f"Next main piece: {engine.next_main_piece}")
        print(f"Next attached piece: {engine.next_attached_piece}")
        
        # Test generate_random_piece method
        piece1 = engine.generate_random_piece()
        piece2 = engine.generate_random_piece()
        print(f"Random piece 1: {piece1}")
        print(f"Random piece 2: {piece2}")
        
        # Verify both pieces are different types
        if piece1 != piece2:
            print("✅ Random piece generation working")
        else:
            print("⚠️ Random pieces are identical (might be coincidence)")
        
        pygame.quit()
        return True
        
    except Exception as e:
        print(f"❌ Piece generation logic test failed: {e}")
        return False

def run_diagnostic():
    """Run all diagnostic tests."""
    print("🚨 PUZZLE ENGINE DIAGNOSTIC - CRITICAL ISSUE INVESTIGATION")
    print("=" * 80)
    
    tests = [
        ("Piece Spawning", test_piece_spawning),
        ("Attack System Integration", test_attack_system_integration),
        ("Test Mode Integration", test_testmode_integration),
        ("Piece Generation Logic", test_piece_generation_logic)
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
    
    print("\n" + "=" * 80)
    print("📊 DIAGNOSTIC RESULTS")
    print("=" * 80)
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 OVERALL RESULT: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Issues may be intermittent or environment-specific")
    else:
        print("⚠️ ISSUES IDENTIFIED - Specific problems found:")
        
        if not results.get("Piece Spawning", True):
            print("   - Piece spawning issue confirmed")
        if not results.get("Attack System Integration", True):
            print("   - Attack system integration issue confirmed")
        if not results.get("Test Mode Integration", True):
            print("   - Test mode integration issue confirmed")
        if not results.get("Piece Generation Logic", True):
            print("   - Piece generation logic issue confirmed")
    
    print("=" * 80)
    return passed == total

if __name__ == "__main__":
    success = run_diagnostic()
    sys.exit(0 if success else 1)
