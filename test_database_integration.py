#!/usr/bin/env python3
"""
Test Database Integration

Verifies that the database is properly integrated and being used.
"""

import sys
import os

# Add the modules directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

from attack_module import SimpleAttackSystem, AttackCombo


def test_database_integration():
    """Test that the database is properly integrated."""
    print("=== Testing Database Integration ===")
    
    # Create attack system
    attack_system = SimpleAttackSystem()
    
    # Enable database
    attack_system.enable_database("attack_database.json")
    
    # Test some combos
    test_combos = [
        # 2x2 cluster
        [
            (1, 1, 'red'), (2, 1, 'red'), (1, 2, 'red'), (2, 2, 'red')
        ],
        
        # 2x2 cluster + 2 individual blocks
        [
            (1, 1, 'red'), (2, 1, 'red'), (1, 2, 'red'), (2, 2, 'red'),
            (3, 1, 'blue'), (4, 2, 'green')
        ],
        
        # 4x4 cluster
        [
            (1, 1, 'red'), (2, 1, 'red'), (3, 1, 'red'), (4, 1, 'red'),
            (1, 2, 'red'), (2, 2, 'red'), (3, 2, 'red'), (4, 2, 'red'),
            (1, 3, 'red'), (2, 3, 'red'), (3, 3, 'red'), (4, 3, 'red'),
            (1, 4, 'red'), (2, 4, 'red'), (3, 4, 'red'), (4, 4, 'red')
        ]
    ]
    
    print("🎯 Testing Database Integration:")
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
    
    print("\n✅ Database Integration Test Complete!")


if __name__ == "__main__":
    test_database_integration() 