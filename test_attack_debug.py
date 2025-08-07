#!/usr/bin/env python3
"""
Attack System Debug Test

This script helps debug the attack system by simulating specific scenarios.
"""

import sys
import os

# Add the modules directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

from attack_module import SimpleAttackSystem, AttackCombo
from attack_module.attack_database import AttackDatabase


def test_2x4_triple_scenario():
    """Test the 2x4 triple scenario that should equal 2x12."""
    print("=== TESTING 2x4 TRIPLE SCENARIO ===")
    print("Expected: 2x4 triple should = 2x12")
    print()
    
    # Create attack system
    attack_system = SimpleAttackSystem(grid_width=6)
    attack_system.enable_database("attack_database.json")
    
    # Simulate breaking three 2x2 clusters (4 blocks each) at 3x chain
    print("🎯 SIMULATING 2x4 TRIPLE COMBO:")
    print("   - Three 2x2 clusters (4 blocks each)")
    print("   - 3x chain multiplier")
    print()
    
    # Create broken blocks for three 2x2 clusters
    broken_blocks = [
        # First 2x2 cluster (top-left)
        (0, 0, 'red'), (1, 0, 'red'),
        (0, 1, 'red'), (1, 1, 'red'),
        
        # Second 2x2 cluster (top-right)
        (4, 0, 'blue'), (5, 0, 'blue'),
        (4, 1, 'blue'), (5, 1, 'blue'),
        
        # Third 2x2 cluster (middle)
        (2, 2, 'green'), (3, 2, 'green'),
        (2, 3, 'green'), (3, 3, 'green'),
    ]
    
    print(f"🔍 BROKEN BLOCKS:")
    for i, (x, y, block_type) in enumerate(broken_blocks):
        print(f"   Block {i+1}: ({x}, {y}) = {block_type}")
    print()
    
    # Detect clusters
    clusters = attack_system.detect_clusters(broken_blocks)
    print(f"🔍 CLUSTER DETECTION: {clusters}")
    print()
    
    # Process the combo
    chain_position = 3  # 3x chain
    new_attacks = attack_system.process_combo(broken_blocks, clusters, chain_position)
    
    print(f"🎯 ATTACK GENERATION RESULT:")
    attack_summary = attack_system.get_attack_summary()
    print(f"   Summary: {attack_summary}")
    
    # Show detailed attacks
    attacks = attack_system.get_pending_attacks()
    if attacks:
        print(f"🔍 DETAILED ATTACKS:")
        for i, attack in enumerate(attacks):
            print(f"   Attack {i+1}:")
            print(f"     Type: {attack.attack_type}")
            print(f"     Count: {attack.count}")
            print(f"     Chain multiplier: {attack.chain_multiplier}")
            if hasattr(attack, 'strike_details') and attack.strike_details:
                print(f"     Strike details: {attack.strike_details}")
    else:
        print(f"   No attacks generated!")
    
    print()
    print("=== EXPECTED vs ACTUAL ===")
    print("Expected: 2x12 (one combined strike)")
    print(f"Actual: {attack_summary}")
    
    if "2x12" in attack_summary:
        print("✅ SUCCESS: Got expected 2x12!")
    else:
        print("❌ ISSUE: Did not get expected 2x12")
        print("   This suggests the attack system is not combining strikes properly")


def test_database_lookup():
    """Test direct database lookup for the 2x4 triple scenario."""
    print("\n=== TESTING DATABASE LOOKUP ===")
    
    # Create database
    db = AttackDatabase("attack_database.json")
    
    # Create the combo for three 4-block clusters at 3x chain
    combo = AttackCombo(
        cluster_sizes=[4, 4, 4],  # Three 4-block clusters
        individual_blocks=0,
        breaker_blocks=0,
        chain_multiplier=3
    )
    
    print(f"🔍 LOOKING UP COMBO: {combo}")
    
    # Get the database key
    key = db.get_attack_key(combo)
    print(f"🔍 DATABASE KEY: {key}")
    
    # Look up the attack output
    output = db.calculate_attack_output(combo)
    print(f"🎯 DATABASE OUTPUT: {output}")
    
    print()
    print("=== DATABASE ANALYSIS ===")
    print(f"Expected key: 4,4,4_0_0_3")
    print(f"Actual key: {key}")
    print(f"Expected: 2x12 (one combined strike)")
    print(f"Actual: {output.strike_details}")
    
    if key == "4,4,4_0_0_3" and output.strike_details == ["1x12", "1x12", "1x12"]:
        print("✅ DATABASE LOOKUP CORRECT")
        print("   The database is returning three separate 1x12 strikes")
        print("   This is the source of the issue - should be one 2x12")
    else:
        print("❌ DATABASE LOOKUP ISSUE")


if __name__ == "__main__":
    test_2x4_triple_scenario()
    test_database_lookup() 