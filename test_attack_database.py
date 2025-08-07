#!/usr/bin/env python3
"""
Test Attack Database System

Demonstrates the comprehensive attack database that maps all possible
combinations to their attack outputs for predictable, balanced gameplay.
"""

import sys
import os

# Add the modules directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

from attack_module import AttackDatabase, AttackCombo, AttackOutput, SimpleAttackSystem


def test_database_creation():
    """Test creating and populating the attack database."""
    print("=== Testing Database Creation ===")
    
    # Create database
    db = AttackDatabase("test_attack_database.json")
    
    # Show statistics
    stats = db.get_statistics()
    print(f"📊 Database Statistics:")
    print(f"   Total rules: {stats['total_rules']}")
    print(f"   Combo types: {stats['combo_types']}")
    print(f"   Damage range: {stats['damage_stats']['min']} - {stats['damage_stats']['max']}")
    print(f"   Average damage: {stats['damage_stats']['average']:.1f}")
    
    return db


def test_specific_combos(db):
    """Test specific combo lookups."""
    print("\n=== Testing Specific Combos ===")
    
    test_cases = [
        # Your example: 2x2 cluster + 2 individual + 1 breaker
        AttackCombo([4], 2, 1, 1),
        
        # Pure cluster combos
        AttackCombo([4], 0, 0, 1),      # 2x2 cluster
        AttackCombo([6], 0, 0, 1),      # 2x3 cluster
        AttackCombo([8], 0, 0, 1),      # 2x4 cluster
        AttackCombo([4, 4], 0, 0, 1),   # Two 2x2 clusters
        
        # Mixed combos
        AttackCombo([4], 1, 0, 1),      # 2x2 + 1 individual
        AttackCombo([4], 2, 1, 1),      # 2x2 + 2 individual - 1 breaker
        AttackCombo([6], 3, 2, 1),      # 2x3 + 3 individual - 2 breakers
        
        # Chain multipliers
        AttackCombo([4], 0, 0, 2),      # 2x2 cluster at 2x chain
        AttackCombo([4], 0, 0, 3),      # 2x2 cluster at 3x chain
        
        # Pure individual blocks
        AttackCombo([], 3, 0, 1),       # 3 individual blocks
        AttackCombo([], 5, 2, 1),       # 5 individual - 2 breakers
        
        # Breaker only
        AttackCombo([], 0, 3, 1),       # 3 breakers only
    ]
    
    print("🎯 Testing Combo Lookups:")
    for combo in test_cases:
        output = db.calculate_attack_output(combo)
        print(f"   {combo} → {output}")
        print(f"      Type: {output.combo_type}")
        print(f"      Description: {output.description}")


def test_pattern_analysis(db):
    """Test pattern analysis and insights."""
    print("\n=== Testing Pattern Analysis ===")
    
    # Analyze patterns
    db.analyze_patterns()
    
    # Search for specific patterns
    print("\n🔍 Searching for High-Damage Combos:")
    high_damage = db.search_combos({"min_damage": 5})
    for key, output in high_damage[:5]:  # Show top 5
        print(f"   {key} → {output}")
    
    print("\n🔍 Searching for Pure Cluster Combos:")
    pure_clusters = db.search_combos({"combo_type": "pure_cluster"})
    for key, output in pure_clusters[:3]:  # Show top 3
        print(f"   {key} → {output}")
    
    print("\n🔍 Searching for 3x Chain Combos:")
    chain_3x = db.search_combos({"chain_multiplier": 3})
    for key, output in chain_3x[:3]:  # Show top 3
        print(f"   {key} → {output}")


def test_integration_with_attack_system():
    """Test integration with the SimpleAttackSystem."""
    print("\n=== Testing Integration with Attack System ===")
    
    # Create attack system with database
    attack_system = SimpleAttackSystem()
    attack_system.enable_database("test_attack_database.json")
    
    # Test some combos
    test_combos = [
        # 2x2 cluster + 2 individual + 1 breaker (your example)
        [
            # 2x2 cluster
            (1, 1, 'red'), (2, 1, 'red'), (1, 2, 'red'), (2, 2, 'red'),
            # Individual blocks
            (4, 1, 'blue'), (5, 2, 'green'),
            # Breaker
            (3, 3, 'yellow_breaker'),
        ],
        
        # Pure 2x3 cluster
        [
            (1, 1, 'red'), (2, 1, 'red'), (3, 1, 'red'),
            (1, 2, 'red'), (2, 2, 'red'), (3, 2, 'red'),
        ],
        
        # Mixed: 2x2 + 3 individual - 1 breaker
        [
            # 2x2 cluster
            (1, 1, 'red'), (2, 1, 'red'), (1, 2, 'red'), (2, 2, 'red'),
            # Individual blocks
            (4, 1, 'blue'), (5, 2, 'green'), (0, 3, 'yellow'),
            # Breaker
            (3, 3, 'blue_breaker'),
        ],
    ]
    
    print("🎯 Testing Attack System with Database:")
    for i, broken_blocks in enumerate(test_combos):
        print(f"\n   Test {i+1}: {len(broken_blocks)} blocks")
        
        # Detect clusters
        clusters = attack_system.detect_clusters(broken_blocks)
        print(f"   Detected clusters: {clusters}")
        
        # Process combo
        attacks = attack_system.process_combo(broken_blocks, clusters, 1)
        
        # Show results
        print(f"   Generated {len(attacks)} attack(s):")
        for attack in attacks:
            print(f"     {attack.attack_type}: {attack.count} blocks")
        
        # Clear for next test
        attack_system.clear_attacks()


def test_custom_rules():
    """Test adding custom attack rules to the database."""
    print("\n=== Testing Custom Rules ===")
    
    db = AttackDatabase("test_custom_database.json")
    
    # Add some custom rules
    custom_rules = [
        # Make 2x2 clusters more powerful
        (AttackCombo([4], 0, 0, 1), AttackOutput(2, 0, 2, "pure_cluster", "Powerful 2x2 cluster")),
        
        # Make mixed combos with breakers more balanced
        (AttackCombo([4], 2, 1, 1), AttackOutput(1, 2, 3, "mixed", "Balanced mixed combo")),
        
        # Add a special rule for large clusters
        (AttackCombo([12], 0, 0, 1), AttackOutput(4, 0, 4, "pure_cluster", "Massive cluster attack")),
    ]
    
    print("📝 Adding Custom Rules:")
    for combo, output in custom_rules:
        db.add_attack_rule(combo, output)
    
    # Test the custom rules
    print("\n🧪 Testing Custom Rules:")
    for combo, expected_output in custom_rules:
        actual_output = db.calculate_attack_output(combo)
        print(f"   {combo} → {actual_output}")
        if actual_output.strikes == expected_output.strikes and actual_output.garbage_blocks == expected_output.garbage_blocks:
            print(f"      ✅ Custom rule working correctly")
        else:
            print(f"      ❌ Custom rule not applied (got {actual_output} instead of {expected_output})")
    
    # Save the custom database
    db.save_database()


def main():
    """Run comprehensive attack database tests."""
    print("🎯 Attack Database System Test")
    print("=" * 60)
    
    # Test database creation
    db = test_database_creation()
    
    # Test specific combos
    test_specific_combos(db)
    
    # Test pattern analysis
    test_pattern_analysis(db)
    
    # Test integration
    test_integration_with_attack_system()
    
    # Test custom rules
    test_custom_rules()
    
    print("\n" + "=" * 60)
    print("✅ Attack Database System Test Complete!")
    print("\n🎮 Benefits of the Database System:")
    print("   • Predictable attack outputs for all combinations")
    print("   • Easy balance adjustments by modifying rules")
    print("   • Pattern recognition and analysis")
    print("   • Custom rules for special scenarios")
    print("   • Fallback to original calculations if needed")
    print("\n📊 The database contains hundreds of pre-calculated")
    print("   attack combinations for consistent gameplay!")


if __name__ == "__main__":
    main() 