#!/usr/bin/env python3
"""
Test Attack Fixes

Quick test to verify:
1. Strikes are properly separated from garbage blocks
2. Breakers are excluded from attack output
3. Mixed combos generate both strikes and garbage
"""

import sys
import os

# Add the modules directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

from attack_module import SimpleAttackSystem


def test_mixed_combo_with_breakers():
    """Test mixed combo with breakers to verify proper separation."""
    print("=== Testing Mixed Combo with Breakers ===")
    
    attack_system = SimpleAttackSystem()
    
    # 2x2 cluster (4 blocks) + 2 individual blocks + 1 breaker
    # Should generate: 1 strike + 1 garbage block (2 individual - 1 breaker)
    broken_blocks = [
        # 2x2 cluster
        (1, 1, 'red'),
        (2, 1, 'red'),
        (1, 2, 'red'),
        (2, 2, 'red'),
        # Individual blocks
        (4, 1, 'blue'),
        (5, 2, 'green'),
        # Breaker
        (3, 3, 'yellow_breaker'),
    ]
    
    print(f"   Breaking mixed combo: {len(broken_blocks)} blocks (4 cluster + 2 individual + 1 breaker)")
    
    # Detect clusters
    clusters = attack_system.detect_clusters(broken_blocks)
    print(f"   Detected clusters: {clusters}")
    
    # Process combo
    attack_system.process_combo(broken_blocks, clusters, 1)
    
    # Get attacks
    attacks = attack_system.get_pending_attacks()
    
    print(f"   Generated {len(attacks)} attack(s):")
    for i, attack in enumerate(attacks):
        print(f"     Attack {i+1}: {attack.attack_type} - {attack.count} blocks")
    
    # Verify: 1 strike + 1 garbage block
    strikes = sum(a.count for a in attacks if a.attack_type == "strike")
    garbage = sum(a.count for a in attacks if a.attack_type == "garbage")
    
    if strikes == 1 and garbage == 1:
        print(f"   ✅ PASS: Mixed combo generates 1 strike + 1 garbage block (breaker excluded)")
    else:
        print(f"   ❌ FAIL: Expected 1 strike + 1 garbage block, got {strikes} strikes + {garbage} garbage blocks")
    
    attack_system.clear_attacks()
    print()


def test_pure_breakers():
    """Test that pure breakers generate no attack output."""
    print("=== Testing Pure Breakers ===")
    
    attack_system = SimpleAttackSystem()
    
    # 2 breakers - should generate 0 attacks
    broken_blocks = [
        (1, 1, 'red_breaker'),
        (2, 1, 'blue_breaker'),
    ]
    
    print(f"   Breaking {len(broken_blocks)} breakers")
    
    # Detect clusters
    clusters = attack_system.detect_clusters(broken_blocks)
    print(f"   Detected clusters: {clusters}")
    
    # Process combo
    attack_system.process_combo(broken_blocks, clusters, 1)
    
    # Get attacks
    attacks = attack_system.get_pending_attacks()
    
    print(f"   Generated {len(attacks)} attack(s)")
    
    # Verify: 0 attacks
    if len(attacks) == 0:
        print(f"   ✅ PASS: Pure breakers generate no attacks")
    else:
        print(f"   ❌ FAIL: Expected 0 attacks, got {len(attacks)}")
    
    attack_system.clear_attacks()
    print()


def main():
    """Run attack fix tests."""
    print("🎯 Attack Fixes Test")
    print("=" * 40)
    
    test_mixed_combo_with_breakers()
    test_pure_breakers()
    
    print("=" * 40)
    print("✅ Attack fix tests completed!")
    print("\nThe fixes address:")
    print("- Strikes are properly separated from garbage blocks")
    print("- Breakers are excluded from attack output")
    print("- Mixed combos generate both strikes and garbage")
    print("- Garbage blocks fill vacant slots when columns are full")


if __name__ == "__main__":
    main() 