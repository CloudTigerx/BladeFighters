#!/usr/bin/env python3
"""
GARBAGE VS STRIKES DEBUG SCRIPT
===============================

This script specifically looks for cases where:
- Garbage blocks = Strike count
- Improper strikes are generated
- Weird edge cases that shouldn't happen

Run this to catch the specific issues you mentioned!
"""

import sys
import os
from typing import List, Tuple, Dict, Any

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.attack_module.attack_calculator import AttackCalculator

def find_garbage_equals_strikes():
    """Find all cases where garbage equals strikes"""
    print("🔍 SEARCHING FOR GARBAGE = STRIKES CASES...")
    print("=" * 60)
    
    calculator = AttackCalculator()
    found_cases = []
    
    # Test a wide range of inputs
    for blocks in range(1, 21):  # 1 to 20 blocks
        for combo in range(1, 11):  # 1x to 10x combo
            garbage = calculator.calculate_garbage_attack(blocks, combo)
            strikes = calculator.calculate_strike_attack(blocks, combo)
            
            if garbage == strikes and strikes > 0:
                found_cases.append({
                    'blocks': blocks,
                    'combo': combo,
                    'garbage': garbage,
                    'strikes': strikes,
                    'formula_garbage': f"({blocks} × {combo}) ÷ 2 = {garbage}",
                    'formula_strikes': f"{blocks} × {combo} = {strikes}"
                })
    
    if found_cases:
        print(f"❌ FOUND {len(found_cases)} CASES WHERE GARBAGE = STRIKES!")
        print()
        
        for i, case in enumerate(found_cases, 1):
            print(f"Case {i}:")
            print(f"  Blocks: {case['blocks']}, Combo: {case['combo']}x")
            print(f"  Garbage: {case['formula_garbage']}")
            print(f"  Strikes: {case['formula_strikes']}")
            print(f"  Both = {case['garbage']}")
            print()
    else:
        print("✅ NO GARBAGE = STRIKES CASES FOUND!")
        print("This is good - garbage and strikes should be different.")
    
    return found_cases

def test_cluster_patterns():
    """Test cluster patterns for consistency"""
    print("\n⚔️ TESTING CLUSTER PATTERNS...")
    print("=" * 60)
    
    calculator = AttackCalculator()
    
    # Test all cluster types
    cluster_types = ["2x2", "3x3", "3x2", "4x4", "2x3", "3x4"]
    
    for cluster_type in cluster_types:
        print(f"\n{cluster_type} Clusters:")
        for combo in range(1, 6):
            try:
                pattern, width, height = calculator.calculate_cluster_strike(cluster_type, combo)
                print(f"  {combo}x combo: {width}×{height} ({pattern})")
                
                # Check for weird patterns
                if width <= 0 or height <= 0:
                    print(f"    ⚠️  WARNING: Invalid dimensions {width}×{height}")
                if width > 10 or height > 20:
                    print(f"    ⚠️  WARNING: Very large dimensions {width}×{height}")
                    
            except Exception as e:
                print(f"  {combo}x combo: ERROR - {e}")

def test_formula_consistency():
    """Test that formulas are consistent"""
    print("\n📊 TESTING FORMULA CONSISTENCY...")
    print("=" * 60)
    
    calculator = AttackCalculator()
    
    # Test garbage formula: (blocks × combo) ÷ 2
    print("Garbage Formula Tests:")
    test_cases = [
        (4, 1, 2),   # 4 blocks, 1x combo = 2 garbage
        (6, 2, 6),   # 6 blocks, 2x combo = 6 garbage
        (8, 3, 12),  # 8 blocks, 3x combo = 12 garbage
        (10, 4, 20), # 10 blocks, 4x combo = 20 garbage
    ]
    
    for blocks, combo, expected in test_cases:
        actual = calculator.calculate_garbage_attack(blocks, combo)
        passed = actual == expected
        status = "✅" if passed else "❌"
        print(f"  {status} ({blocks} × {combo}) ÷ 2 = {actual} (expected {expected})")
    
    # Test strike formula: cluster_size × combo
    print("\nStrike Formula Tests:")
    strike_cases = [
        (4, 1, 4),   # 2x2 cluster, 1x combo = 4 strikes
        (9, 2, 18),  # 3x3 cluster, 2x combo = 18 strikes
        (16, 3, 48), # 4x4 cluster, 3x combo = 48 strikes
    ]
    
    for cluster_size, combo, expected in strike_cases:
        actual = calculator.calculate_strike_attack(cluster_size, combo)
        passed = actual == expected
        status = "✅" if passed else "❌"
        print(f"  {status} {cluster_size} × {combo} = {actual} strikes (expected {expected})")

def test_edge_cases():
    """Test edge cases that might cause issues"""
    print("\n🔍 TESTING EDGE CASES...")
    print("=" * 60)
    
    calculator = AttackCalculator()
    
    # Test minimum strike size
    print("Minimum Strike Size Test:")
    for blocks in [1, 2, 3, 4, 5]:
        strikes = calculator.calculate_strike_attack(blocks, 1)
        status = "✅" if (blocks < 4 and strikes == 0) or (blocks >= 4 and strikes > 0) else "❌"
        print(f"  {status} {blocks} blocks = {strikes} strikes")
    
    # Test zero and negative combos
    print("\nZero/Negative Combo Test:")
    try:
        zero_garbage = calculator.calculate_garbage_attack(4, 0)
        zero_strikes = calculator.calculate_strike_attack(4, 0)
        print(f"  Zero combo: garbage={zero_garbage}, strikes={zero_strikes}")
    except Exception as e:
        print(f"  ❌ Zero combo error: {e}")
    
    # Test very large values
    print("\nLarge Value Test:")
    try:
        large_garbage = calculator.calculate_garbage_attack(100, 10)
        large_strikes = calculator.calculate_strike_attack(100, 10)
        print(f"  Large values: garbage={large_garbage}, strikes={large_strikes}")
    except Exception as e:
        print(f"  ❌ Large value error: {e}")

def main():
    """Run all debug tests"""
    print("🔥 GARBAGE VS STRIKES DEBUG SCRIPT")
    print("=" * 60)
    print()
    
    # Run all tests
    garbage_equals_strikes = find_garbage_equals_strikes()
    test_cluster_patterns()
    test_formula_consistency()
    test_edge_cases()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 DEBUG SUMMARY")
    print("=" * 60)
    
    if garbage_equals_strikes:
        print(f"❌ FOUND {len(garbage_equals_strikes)} PROBLEMATIC CASES")
        print("These cases need investigation:")
        for case in garbage_equals_strikes:
            print(f"  • {case['blocks']} blocks, {case['combo']}x combo → both = {case['garbage']}")
    else:
        print("✅ NO GARBAGE = STRIKES CASES FOUND")
    
    print("\n🔧 RECOMMENDATIONS:")
    if garbage_equals_strikes:
        print("• Review the cases above")
        print("• Check if these are intended edge cases")
        print("• Consider adjusting formulas if needed")
        print("• Test these specific cases in-game")
    else:
        print("• Formulas look good")
        print("• Run the full validation suite for deeper testing")
        print("• Monitor in-game behavior for any issues")

if __name__ == "__main__":
    main()
