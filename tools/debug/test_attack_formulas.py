#!/usr/bin/env python3
"""
TEST ATTACK FORMULAS
===================

Quick test to verify attack formulas are working correctly.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_attack_formulas():
    """Test the attack formulas"""
    print("🎯 TESTING ATTACK FORMULAS...")
    print("=" * 60)
    
    try:
        from modules.attack_module.attack_calculator import AttackCalculator
        
        calculator = AttackCalculator()
        
        # Test cases
        test_cases = [
            # (blocks, combo, expected_garbage, expected_strikes)
            (4, 1, 2, 4),   # 4 blocks, 1x combo
            (6, 2, 6, 12),  # 6 blocks, 2x combo  
            (8, 3, 12, 24), # 8 blocks, 3x combo
            (10, 4, 20, 40), # 10 blocks, 4x combo
        ]
        
        all_passed = True
        
        for blocks, combo, expected_garbage, expected_strikes in test_cases:
            actual_garbage = calculator.calculate_garbage_attack(blocks, combo)
            actual_strikes = calculator.calculate_strike_attack(blocks, combo)
            
            garbage_correct = actual_garbage == expected_garbage
            strikes_correct = actual_strikes == expected_strikes
            
            status = "✅" if garbage_correct and strikes_correct else "❌"
            print(f"{status} {blocks}×{combo}: Garbage={actual_garbage}({expected_garbage}), Strikes={actual_strikes}({expected_strikes})")
            
            if not garbage_correct or not strikes_correct:
                all_passed = False
        
        # Check for garbage = strikes edge cases
        print("\n🔍 CHECKING FOR GARBAGE = STRIKES EDGE CASES...")
        edge_cases = []
        
        for blocks in range(1, 11):
            for combo in range(1, 6):
                garbage = calculator.calculate_garbage_attack(blocks, combo)
                strikes = calculator.calculate_strike_attack(blocks, combo)
                
                if garbage == strikes and strikes > 0:
                    edge_cases.append(f"{blocks}×{combo} = {garbage}")
        
        if edge_cases:
            print("❌ FOUND GARBAGE = STRIKES CASES:")
            for case in edge_cases:
                print(f"   - {case}")
            all_passed = False
        else:
            print("✅ No garbage = strikes edge cases found")
        
        print(f"\n📊 OVERALL RESULT: {'✅ PASSED' if all_passed else '❌ FAILED'}")
        return all_passed
        
    except Exception as e:
        print(f"❌ Error testing attack formulas: {e}")
        return False

if __name__ == "__main__":
    test_attack_formulas()
