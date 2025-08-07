#!/usr/bin/env python3
"""
Test Competitive Stacked Cluster Combos

Testing the system's ability to handle competitive stacked cluster combinations
that reward skill and don't reduce damage for "breaking the rules".
"""

import sys
import os

# Add the modules directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

from attack_module import AttackDatabase, AttackCombo, AttackOutput


def test_stacked_2x2_combos():
    """Test stacked 2x2 cluster combinations."""
    print("=== Testing Stacked 2x2 Combos ===")
    
    db = AttackDatabase("test_competitive_database.json")
    
    # Test increasingly difficult stacked 2x2 combos
    test_cases = [
        # Basic stacked combos
        (AttackCombo([4], 0, 0, 1), "Single 2x2"),
        (AttackCombo([4, 4], 0, 0, 1), "Two 2x2s"),
        (AttackCombo([4, 4, 4], 0, 0, 1), "Three 2x2s"),
        (AttackCombo([4, 4, 4, 4], 0, 0, 1), "Four 2x2s"),
        (AttackCombo([4, 4, 4, 4, 4], 0, 0, 1), "Five 2x2s (Competitive)"),
        (AttackCombo([4, 4, 4, 4, 4, 4], 0, 0, 1), "Six 2x2s (Master Level)"),
        
        # With chain multipliers
        (AttackCombo([4, 4, 4, 4, 4], 0, 0, 3), "Five 2x2s at 3x chain"),
        (AttackCombo([4, 4, 4, 4, 4], 0, 0, 5), "Five 2x2s at 5x chain"),
        
        # With individual blocks
        (AttackCombo([4, 4, 4, 4, 4], 2, 0, 1), "Five 2x2s + 2 individual"),
        (AttackCombo([4, 4, 4, 4, 4], 2, 1, 1), "Five 2x2s + 2 individual - 1 breaker"),
    ]
    
    print("🎯 Testing Stacked 2x2 Combinations:")
    for combo, description in test_cases:
        output = db.calculate_attack_output(combo)
        print(f"   {description}: {combo} → {output}")
        print()


def test_stacked_3x2_combos():
    """Test stacked 3x2 cluster combinations."""
    print("=== Testing Stacked 3x2 Combos ===")
    
    db = AttackDatabase("test_competitive_database.json")
    
    test_cases = [
        (AttackCombo([6], 0, 0, 1), "Single 3x2"),
        (AttackCombo([6, 6], 0, 0, 1), "Two 3x2s"),
        (AttackCombo([6, 6, 6], 0, 0, 1), "Three 3x2s"),
        (AttackCombo([6, 6, 6, 6], 0, 0, 1), "Four 3x2s"),
        
        # With chain multipliers
        (AttackCombo([6, 6, 6], 0, 0, 4), "Three 3x2s at 4x chain"),
        (AttackCombo([6, 6, 6, 6], 0, 0, 5), "Four 3x2s at 5x chain"),
    ]
    
    print("🎯 Testing Stacked 3x2 Combinations:")
    for combo, description in test_cases:
        output = db.calculate_attack_output(combo)
        print(f"   {description}: {combo} → {output}")
        print()


def test_stacked_3x3_combos():
    """Test stacked 3x3 cluster combinations."""
    print("=== Testing Stacked 3x3 Combos ===")
    
    db = AttackDatabase("test_competitive_database.json")
    
    test_cases = [
        (AttackCombo([9], 0, 0, 1), "Single 3x3"),
        (AttackCombo([9, 9], 0, 0, 1), "Two 3x3s"),
        (AttackCombo([9, 9, 9], 0, 0, 1), "Three 3x3s"),
        (AttackCombo([9, 9, 9, 9], 0, 0, 1), "Four 3x3s"),
        
        # With chain multipliers
        (AttackCombo([9, 9, 9], 0, 0, 3), "Three 3x3s at 3x chain"),
        (AttackCombo([9, 9, 9, 9], 0, 0, 4), "Four 3x3s at 4x chain"),
    ]
    
    print("🎯 Testing Stacked 3x3 Combinations:")
    for combo, description in test_cases:
        output = db.calculate_attack_output(combo)
        print(f"   {description}: {combo} → {output}")
        print()


def test_4x4_splitting_combos():
    """Test 4x4 splitting with competitive chains."""
    print("=== Testing 4x4 Splitting Combos ===")
    
    db = AttackDatabase("test_competitive_database.json")
    
    test_cases = [
        (AttackCombo([16], 0, 0, 1), "Single 4x4"),
        (AttackCombo([16], 0, 0, 2), "4x4 at 2x chain (splits to 2x4 + 2x4)"),
        (AttackCombo([16], 0, 0, 3), "4x4 at 3x chain (splits to 2x6 + 2x6)"),
        (AttackCombo([16], 0, 0, 4), "4x4 at 4x chain (splits to 2x8 + 2x8)"),
        (AttackCombo([16], 0, 0, 5), "4x4 at 5x chain (splits to 2x10 + 2x10)"),
        
        # Multiple 4x4s
        (AttackCombo([16, 16], 0, 0, 1), "Two 4x4s"),
        (AttackCombo([16, 16], 0, 0, 2), "Two 4x4s at 2x chain"),
        (AttackCombo([16, 16, 16], 0, 0, 1), "Three 4x4s"),
    ]
    
    print("🎯 Testing 4x4 Splitting Combinations:")
    for combo, description in test_cases:
        output = db.calculate_attack_output(combo)
        print(f"   {description}: {combo} → {output}")
        print()


def test_competitive_damage_scaling():
    """Test damage scaling for competitive play."""
    print("=== Testing Competitive Damage Scaling ===")
    
    db = AttackDatabase("test_competitive_database.json")
    
    # Test how damage scales with chain multipliers
    base_combo = AttackCombo([4, 4, 4, 4, 4], 0, 0, 1)  # Five 2x2s
    print(f"🎯 Base combo: {base_combo} → {db.calculate_attack_output(base_combo)}")
    
    for chain in [2, 3, 4, 5, 6, 7, 8]:
        combo = AttackCombo([4, 4, 4, 4, 4], 0, 0, chain)
        output = db.calculate_attack_output(combo)
        print(f"   Chain {chain}x: {combo} → {output}")
    
    print()


def main():
    """Run competitive combo tests."""
    print("🎯 Competitive Stacked Cluster Combo Test")
    print("=" * 70)
    print("Testing the system's ability to handle competitive stacked combos")
    print("that reward skill and don't reduce damage for 'breaking the rules'")
    print("=" * 70)
    
    test_stacked_2x2_combos()
    test_stacked_3x2_combos()
    test_stacked_3x3_combos()
    test_4x4_splitting_combos()
    test_competitive_damage_scaling()
    
    print("=" * 70)
    print("✅ Competitive Combo Test Complete!")
    print("\n🎮 Key Competitive Features:")
    print("   • Stacked clusters reward skill (no damage reduction)")
    print("   • High chain multipliers (up to 8x) for competitive play")
    print("   • Multiple clusters of same size in one combo")
    print("   • 4x4 splitting scales with chain multipliers")
    print("   • Mixed combos with stacked clusters + individual blocks")
    print("\n🏆 This system rewards competitive skill and fast building!")


if __name__ == "__main__":
    main() 