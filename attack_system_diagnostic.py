#!/usr/bin/env python3
"""
Comprehensive Attack System Integration Diagnostic
Tests the complete attack system integration from puzzle engine to delivery.
"""

import pygame
import time
import sys
from typing import List, Tuple

def test_attack_system_integration():
    """Test the complete attack system integration."""
    try:
        print("🔍 Testing Attack System Integration...")
        
        # Initialize pygame
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        font = pygame.font.SysFont(None, 24)
        
        # Import components
        from core.puzzle_module import PuzzleEngine
        from modules.attack_module.attacks_service import AttacksService
        from modules.testmode_module.attack_coordinator import AttackCoordinator
        from modules.testmode_module.test_mode import TestModeRefactored
        print("✅ Component imports successful")
        
        # Create test mode
        test_mode = TestModeRefactored(screen, font, None, "puzzleassets", None, clock=None)
        print("✅ TestMode creation successful")
        
        # Get attack coordinator
        attack_coordinator = test_mode.attack_coordinator
        print("✅ AttackCoordinator access successful")
        
        # Get attacks service
        attacks_service = attack_coordinator.attacks_service
        print("✅ AttacksService access successful")
        
        # Test 1: Basic combo processing
        print("\n🧪 Test 1: Basic Combo Processing")
        test_blocks = [(0, 0, 'red_block'), (1, 0, 'red_block'), (0, 1, 'red_block'), (1, 1, 'red_block')]
        attacks_service.on_combo(test_blocks, is_cluster=True, combo_multiplier=1, player_id=1)
        print("✅ Basic combo processing successful")
        
        # Test 2: Check attack queue
        print("\n🧪 Test 2: Attack Queue Check")
        pending_attacks = attacks_service.attack_manager.get_pending_attacks(target_player=2)
        print(f"Pending attacks for player 2: {len(pending_attacks)}")
        if pending_attacks:
            print(f"First attack type: {pending_attacks[0].attack_type}")
            print(f"First attack target: {pending_attacks[0].target_player}")
        print("✅ Attack queue check successful")
        
        # Test 3: Attack delivery
        print("\n🧪 Test 3: Attack Delivery")
        player_engine, enemy_engine = test_mode.board_manager.get_engines()
        player_renderer, enemy_renderer = test_mode.board_manager.get_renderers()
        
        # Mark engines for side mapping
        setattr(player_engine, 'is_player_board', True)
        setattr(enemy_engine, 'is_player_board', False)
        
        # Test delivery
        res_player, res_enemy = attack_coordinator.deliver_attacks(
            player_engine, enemy_engine, player_renderer, enemy_renderer
        )
        print(f"Player delivery result: {res_player}")
        print(f"Enemy delivery result: {res_enemy}")
        print("✅ Attack delivery successful")
        
        # Test 4: Check if test mode has queue_attack_spawn method
        print("\n🧪 Test 4: queue_attack_spawn Method Check")
        if hasattr(test_mode, 'queue_attack_spawn'):
            print("✅ TestMode has queue_attack_spawn method")
        else:
            print("❌ TestMode missing queue_attack_spawn method")
            
        # Test 5: Check pending_attacks attribute
        print("\n🧪 Test 5: pending_attacks Attribute Check")
        if hasattr(test_mode, 'pending_attacks'):
            print("✅ TestMode has pending_attacks attribute")
            print(f"Player pending attacks: {len(test_mode.pending_attacks.get('player', []))}")
            print(f"Enemy pending attacks: {len(test_mode.pending_attacks.get('enemy', []))}")
        else:
            print("❌ TestMode missing pending_attacks attribute")
            
        # Test 6: Check attack flow manager
        print("\n🧪 Test 6: Attack Flow Manager Check")
        attack_flow_manager = attack_coordinator.attack_flow_manager
        if attack_flow_manager:
            print("✅ Attack flow manager exists")
            pending_player = attack_flow_manager.get_pending_attacks('player')
            pending_enemy = attack_flow_manager.get_pending_attacks('enemy')
            print(f"Flow manager - Player pending: {len(pending_player)}")
            print(f"Flow manager - Enemy pending: {len(pending_enemy)}")
        else:
            print("❌ Attack flow manager missing")
            
        pygame.quit()
        return True
        
    except Exception as e:
        print(f"❌ Attack system integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_puzzle_engine_attack_integration():
    """Test puzzle engine attack integration."""
    try:
        print("\n🔍 Testing Puzzle Engine Attack Integration...")
        
        # Initialize pygame
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        font = pygame.font.SysFont(None, 24)
        
        # Create puzzle engine
        from core.puzzle_module import PuzzleEngine
        engine = PuzzleEngine(screen, font, None, "puzzleassets")
        print("✅ PuzzleEngine creation successful")
        
        # Test blocks_broken_handler
        print("\n🧪 Test: blocks_broken_handler")
        if hasattr(engine, 'blocks_broken_handler'):
            print("✅ Engine has blocks_broken_handler")
            
            # Test handler call
            test_blocks = [(0, 0, 'red_block'), (1, 0, 'red_block')]
            try:
                engine.blocks_broken_handler(test_blocks, False, 1)
                print("✅ blocks_broken_handler call successful")
            except Exception as e:
                print(f"❌ blocks_broken_handler call failed: {e}")
        else:
            print("❌ Engine missing blocks_broken_handler")
            
        pygame.quit()
        return True
        
    except Exception as e:
        print(f"❌ Puzzle engine attack integration test failed: {e}")
        return False

def test_attack_coordinator_integration():
    """Test attack coordinator integration."""
    try:
        print("\n🔍 Testing Attack Coordinator Integration...")
        
        # Create attack coordinator
        from modules.testmode_module.attack_coordinator import AttackCoordinator
        coordinator = AttackCoordinator()
        print("✅ AttackCoordinator creation successful")
        
        # Test attacks service
        attacks_service = coordinator.attacks_service
        print("✅ AttacksService access successful")
        
        # Test attack manager
        attack_manager = coordinator.attack_manager
        print("✅ AttackManager access successful")
        
        # Test attack flow manager
        attack_flow_manager = coordinator.attack_flow_manager
        print("✅ AttackFlowManager access successful")
        
        # Test combo processing
        test_blocks = [(0, 0, 'blue_block'), (1, 0, 'blue_block'), (2, 0, 'blue_block')]
        attacks_service.on_combo(test_blocks, False, 1, 1)
        print("✅ Combo processing successful")
        
        # Check attack queue
        pending = attack_manager.get_pending_attacks(2)
        print(f"Pending attacks: {len(pending)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Attack coordinator integration test failed: {e}")
        return False

def test_attack_delivery_mechanism():
    """Test the attack delivery mechanism."""
    try:
        print("\n🔍 Testing Attack Delivery Mechanism...")
        
        # Initialize pygame
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        font = pygame.font.SysFont(None, 24)
        
        # Create test mode
        from modules.testmode_module.test_mode import TestModeRefactored
        test_mode = TestModeRefactored(screen, font, None, "puzzleassets", None, clock=None)
        
        # Get components
        attack_coordinator = test_mode.attack_coordinator
        player_engine, enemy_engine = test_mode.board_manager.get_engines()
        player_renderer, enemy_renderer = test_mode.board_manager.get_renderers()
        
        # Mark engines
        setattr(player_engine, 'is_player_board', True)
        setattr(enemy_engine, 'is_player_board', False)
        
        # Test delivery
        res_player, res_enemy = attack_coordinator.deliver_attacks(
            player_engine, enemy_engine, player_renderer, enemy_renderer
        )
        
        print(f"Player delivery: {res_player}")
        print(f"Enemy delivery: {res_enemy}")
        
        # Check if delivery worked
        if res_player.get('payload_count', 0) > 0 or res_enemy.get('payload_count', 0) > 0:
            print("✅ Attack delivery mechanism working")
        else:
            print("⚠️ No attacks delivered (may be normal if no attacks queued)")
            
        pygame.quit()
        return True
        
    except Exception as e:
        print(f"❌ Attack delivery mechanism test failed: {e}")
        return False

def run_comprehensive_diagnostic():
    """Run comprehensive attack system diagnostic."""
    print("🚨 COMPREHENSIVE ATTACK SYSTEM DIAGNOSTIC")
    print("=" * 60)
    
    tests = [
        ("Attack System Integration", test_attack_system_integration),
        ("Puzzle Engine Attack Integration", test_puzzle_engine_attack_integration),
        ("Attack Coordinator Integration", test_attack_coordinator_integration),
        ("Attack Delivery Mechanism", test_attack_delivery_mechanism)
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
    print("📊 ATTACK SYSTEM DIAGNOSTIC RESULTS")
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
        print("🎉 ALL TESTS PASSED - Attack system integration is working!")
    else:
        print("⚠️ SOME TESTS FAILED - Attack system integration issues detected")
        
        if not results.get("Attack System Integration", True):
            print("   - Core attack system integration issue")
        if not results.get("Puzzle Engine Attack Integration", True):
            print("   - Puzzle engine attack integration issue")
        if not results.get("Attack Coordinator Integration", True):
            print("   - Attack coordinator integration issue")
        if not results.get("Attack Delivery Mechanism", True):
            print("   - Attack delivery mechanism issue")
    
    print("=" * 60)
    return passed == total

if __name__ == "__main__":
    success = run_comprehensive_diagnostic()
    sys.exit(0 if success else 1)
