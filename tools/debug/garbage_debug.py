#!/usr/bin/env python3
"""
GARBAGE DEBUG SCRIPT
====================

This script specifically tests garbage-related issues:
- Garbage formula accuracy
- Garbage vs strikes differentiation
- Garbage edge cases
- Garbage delivery issues

Run this to catch garbage-specific problems!
"""

import sys
import os
from typing import List, Tuple, Dict, Any

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.attack_module.attack_calculator import AttackCalculator

def test_garbage_formula():
    """Test garbage formula accuracy"""
    print("📊 TESTING GARBAGE FORMULA...")
    print("=" * 60)
    
    calculator = AttackCalculator()
    
    # Test basic formula: (blocks × combo) ÷ 2
    test_cases = [
        (1, 1, 0, "1 block, 1x combo"),
        (2, 1, 1, "2 blocks, 1x combo"),
        (3, 1, 1, "3 blocks, 1x combo"),
        (4, 1, 2, "4 blocks, 1x combo"),
        (5, 1, 2, "5 blocks, 1x combo"),
        (6, 1, 3, "6 blocks, 1x combo"),
        (7, 1, 3, "7 blocks, 1x combo"),
        (8, 1, 4, "8 blocks, 1x combo"),
        (9, 1, 4, "9 blocks, 1x combo"),
        (10, 1, 5, "10 blocks, 1x combo"),
    ]
    
    passed = 0
    failed = 0
    
    for blocks, combo, expected, desc in test_cases:
        actual = calculator.calculate_garbage_attack(blocks, combo)
        if actual == expected:
            print(f"✅ {desc} = {actual} garbage")
            passed += 1
        else:
            print(f"❌ {desc} = {actual}, expected {expected}")
            failed += 1
    
    print(f"\n📊 Basic Formula Results: {passed} passed, {failed} failed")
    return failed == 0

def test_garbage_scaling():
    """Test garbage scaling with combos"""
    print("\n📈 TESTING GARBAGE SCALING...")
    print("=" * 60)
    
    calculator = AttackCalculator()
    
    # Test combo scaling
    scaling_tests = [
        (4, 1, 2, "4 blocks, 1x combo"),
        (4, 2, 4, "4 blocks, 2x combo"),
        (4, 3, 6, "4 blocks, 3x combo"),
        (4, 4, 8, "4 blocks, 4x combo"),
        (4, 5, 10, "4 blocks, 5x combo"),
        (6, 1, 3, "6 blocks, 1x combo"),
        (6, 2, 6, "6 blocks, 2x combo"),
        (6, 3, 9, "6 blocks, 3x combo"),
        (8, 1, 4, "8 blocks, 1x combo"),
        (8, 2, 8, "8 blocks, 2x combo"),
        (8, 3, 12, "8 blocks, 3x combo"),
    ]
    
    passed = 0
    failed = 0
    
    for blocks, combo, expected, desc in scaling_tests:
        actual = calculator.calculate_garbage_attack(blocks, combo)
        if actual == expected:
            print(f"✅ {desc} = {actual} garbage")
            passed += 1
        else:
            print(f"❌ {desc} = {actual}, expected {expected}")
            failed += 1
    
    print(f"\n📊 Scaling Results: {passed} passed, {failed} failed")
    return failed == 0

def test_garbage_vs_strikes():
    """Test garbage vs strikes differentiation"""
    print("\n⚖️ TESTING GARBAGE VS STRIKES...")
    print("=" * 60)
    
    calculator = AttackCalculator()
    
    # Test that garbage and strikes are properly differentiated
    test_cases = [
        (4, 1, "4 blocks, 1x combo"),
        (6, 2, "6 blocks, 2x combo"),
        (8, 3, "8 blocks, 3x combo"),
        (10, 4, "10 blocks, 4x combo"),
    ]
    
    passed = 0
    failed = 0
    
    for blocks, combo, desc in test_cases:
        garbage = calculator.calculate_garbage_attack(blocks, combo)
        strikes = calculator.calculate_strike_attack(blocks, combo)
        
        # Garbage should be less than strikes for normal cases
        if garbage < strikes:
            print(f"✅ {desc}: Garbage={garbage} < Strikes={strikes}")
            passed += 1
        else:
            print(f"❌ {desc}: Garbage={garbage} >= Strikes={strikes}")
            failed += 1
        
        # Check formula accuracy
        expected_garbage = (blocks * combo) // 2
        if garbage == expected_garbage:
            print(f"  ✅ Formula correct: ({blocks} × {combo}) ÷ 2 = {garbage}")
        else:
            print(f"  ❌ Formula wrong: expected {expected_garbage}, got {garbage}")
            failed += 1
    
    print(f"\n📊 Garbage vs Strikes Results: {passed} passed, {failed} failed")
    return failed == 0

def test_garbage_edge_cases():
    """Test garbage edge cases"""
    print("\n🔍 TESTING GARBAGE EDGE CASES...")
    print("=" * 60)
    
    calculator = AttackCalculator()
    
    # Test edge cases
    edge_tests = [
        (0, 1, 0, "Zero blocks"),
        (1, 0, 0, "Zero combo"),
        (0, 0, 0, "Zero blocks and combo"),
        (-1, 1, 0, "Negative blocks"),
        (1, -1, 0, "Negative combo"),
    ]
    
    passed = 0
    failed = 0
    
    for blocks, combo, expected, desc in edge_tests:
        try:
            actual = calculator.calculate_garbage_attack(blocks, combo)
            if actual == expected:
                print(f"✅ {desc} = {actual}")
                passed += 1
            else:
                print(f"❌ {desc} = {actual}, expected {expected}")
                failed += 1
        except Exception as e:
            print(f"❌ {desc} = Exception: {e}")
            failed += 1
    
    # Test fractional handling
    fractional_test = calculator.calculate_garbage_attack(3, 1)  # Should be 1, not 1.5
    if fractional_test == 1 and isinstance(fractional_test, int):
        print(f"✅ Fractional handling: 3 blocks, 1x combo = {fractional_test} (integer)")
        passed += 1
    else:
        print(f"❌ Fractional handling: 3 blocks, 1x combo = {fractional_test} (should be 1)")
        failed += 1
    
    print(f"\n📊 Edge Cases Results: {passed} passed, {failed} failed")
    return failed == 0

def test_garbage_consistency():
    """Test garbage consistency across different inputs"""
    print("\n🔄 TESTING GARBAGE CONSISTENCY...")
    print("=" * 60)
    
    calculator = AttackCalculator()
    
    # Test that same formula always produces same result
    consistency_tests = [
        (4, 2, "4 blocks, 2x combo"),
        (6, 3, "6 blocks, 3x combo"),
        (8, 4, "8 blocks, 4x combo"),
    ]
    
    passed = 0
    failed = 0
    
    for blocks, combo, desc in consistency_tests:
        # Run the same calculation multiple times
        results = []
        for i in range(5):
            result = calculator.calculate_garbage_attack(blocks, combo)
            results.append(result)
        
        # All results should be the same
        if len(set(results)) == 1:
            print(f"✅ {desc} = {results[0]} (consistent)")
            passed += 1
        else:
            print(f"❌ {desc} = {results} (inconsistent)")
            failed += 1
    
    print(f"\n📊 Consistency Results: {passed} passed, {failed} failed")
    return failed == 0

def main():
    """Run all garbage tests"""
    print("🗑️ GARBAGE DEBUG SCRIPT")
    print("=" * 60)
    print()
    
    # Run all tests
    formula_ok = test_garbage_formula()
    scaling_ok = test_garbage_scaling()
    vs_strikes_ok = test_garbage_vs_strikes()
    edge_cases_ok = test_garbage_edge_cases()
    consistency_ok = test_garbage_consistency()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 GARBAGE DEBUG SUMMARY")
    print("=" * 60)
    
    all_passed = all([formula_ok, scaling_ok, vs_strikes_ok, edge_cases_ok, consistency_ok])
    
    if all_passed:
        print("✅ ALL GARBAGE TESTS PASSED!")
        print("Your garbage system looks solid!")
    else:
        print("❌ SOME GARBAGE TESTS FAILED!")
        print("Issues found that need attention:")
        if not formula_ok:
            print("  • Basic garbage formula issues")
        if not scaling_ok:
            print("  • Garbage scaling issues")
        if not vs_strikes_ok:
            print("  • Garbage vs strikes differentiation issues")
        if not edge_cases_ok:
            print("  • Garbage edge case handling issues")
        if not consistency_ok:
            print("  • Garbage consistency issues")
    
    print("\n🔧 RECOMMENDATIONS:")
    if all_passed:
        print("• Garbage formulas look good")
        print("• Run the full validation suite for deeper testing")
        print("• Monitor in-game garbage behavior")
    else:
        print("• Review the failed tests above")
        print("• Check garbage formula implementation")
        print("• Test garbage delivery in-game")
        print("• Run the comprehensive garbage validation suite")

if __name__ == "__main__":
    main()
