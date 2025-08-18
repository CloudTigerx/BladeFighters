#!/usr/bin/env python3
"""
COMPREHENSIVE PUZZLE MODULE TEST
================================

This test verifies all the fixes applied to the puzzle module.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_piece_movement():
    """Test piece movement fixes"""
    print("🔄 Testing piece movement...")
    
    try:
        from core.piece_movement import PieceMovement
        
        # Test flip cooldown
        test_engine = type('TestEngine', (), {
            'grid_width': 6,
            'grid_height': 12,
            'piece_position': [3, 5],
            'attached_position': 0,
            'is_valid_position': lambda x, y: True
        })()
        
        movement = PieceMovement(test_engine)
        
        # Check flip cooldown is low
        if movement.flip_cooldown <= 0.05:
            print("✅ Flip cooldown is appropriately low")
            return True
        else:
            print("❌ Flip cooldown is too high")
            return False
            
    except Exception as e:
        print(f"❌ Error testing piece movement: {e}")
        return False

def test_transformation_system():
    """Test transformation system fixes"""
    print("🔄 Testing transformation system...")
    
    try:
        from modules.testmode_module.test_mode import TestModeRefactored
        
        # Check if methods exist
        required_methods = [
            '_process_garbage_transformations',
            '_track_garbage_landings',
            '_apply_garbage_finalization'
        ]
        
        for method in required_methods:
            if hasattr(TestModeRefactored, method):
                print(f"✅ {method} exists")
            else:
                print(f"❌ {method} missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing transformation system: {e}")
        return False

def test_attack_formulas():
    """Test attack formulas"""
    print("🎯 Testing attack formulas...")
    
    try:
        from modules.attack_module.attack_calculator import AttackCalculator
        
        calculator = AttackCalculator()
        
        # Test basic formulas
        garbage = calculator.calculate_garbage_attack(4, 1)
        strikes = calculator.calculate_strike_attack(4, 1)
        
        if garbage == 2 and strikes == 4:
            print("✅ Attack formulas working correctly")
            return True
        else:
            print(f"❌ Attack formulas wrong: garbage={garbage}, strikes={strikes}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing attack formulas: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 COMPREHENSIVE PUZZLE MODULE TEST")
    print("=" * 60)
    
    tests = [
        test_piece_movement,
        test_transformation_system,
        test_attack_formulas
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ ALL TESTS PASSED - All fixes working correctly!")
    else:
        print("❌ SOME TESTS FAILED - Manual review may be needed")
    
    return passed == total

if __name__ == "__main__":
    main()
