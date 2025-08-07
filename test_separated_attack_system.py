#!/usr/bin/env python3
"""
Test Separated Attack System

Tests the new attack system that properly separates:
- Clusters → Strikes
- Individual blocks → Garbage blocks  
- Breakers → No attack output
"""

import sys
import os

# Add the modules directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

from attack_module import SimpleAttackSystem


def test_pure_cluster_attack():
    """Test that pure clusters generate only strikes, no garbage blocks."""
    print("=== Testing Pure Cluster Attack ===")
    
    attack_system = SimpleAttackSystem()
    
    # 2x2 cluster (4 blocks) - should generate 1 strike, 0 garbage blocks
    broken_blocks = [
        (1, 1, 'red'),
        (2, 1, 'red'),
        (1, 2, 'red'),
        (2, 2, 'red'),
    ]
    
    print(f"   Breaking 2x2 cluster: {len(broken_blocks)} blocks")
    
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
    
    # Verify: 1 strike, 0 garbage blocks
    strikes = sum(a.count for a in attacks if a.attack_type == "strike")
    garbage = sum(a.count for a in attacks if a.attack_type == "garbage")
    
    if strikes == 1 and garbage == 0:
        print(f"   ✅ PASS: Pure cluster generates 1 strike, 0 garbage blocks")
    else:
        print(f"   ❌ FAIL: Expected 1 strike, 0 garbage blocks, got {strikes} strikes, {garbage} garbage blocks")
    
    attack_system.clear_attacks()
    print()


def test_pure_individual_blocks():
    """Test that individual blocks generate only garbage blocks, no strikes."""
    print("=== Testing Pure Individual Blocks ===")
    
    attack_system = SimpleAttackSystem()
    
    # 3 individual blocks - should generate 3 garbage blocks, 0 strikes
    broken_blocks = [
        (1, 1, 'red'),
        (3, 2, 'blue'),
        (5, 3, 'green'),
    ]
    
    print(f"   Breaking {len(broken_blocks)} individual blocks")
    
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
    
    # Verify: 0 strikes, 3 garbage blocks
    strikes = sum(a.count for a in attacks if a.attack_type == "strike")
    garbage = sum(a.count for a in attacks if a.attack_type == "garbage")
    
    if strikes == 0 and garbage == 3:
        print(f"   ✅ PASS: Individual blocks generate 0 strikes, 3 garbage blocks")
    else:
        print(f"   ❌ FAIL: Expected 0 strikes, 3 garbage blocks, got {strikes} strikes, {garbage} garbage blocks")
    
    attack_system.clear_attacks()
    print()


def test_mixed_cluster_and_individual():
    """Test that mixed combos generate both strikes and garbage blocks."""
    print("=== Testing Mixed Cluster + Individual Blocks ===")
    
    attack_system = SimpleAttackSystem()
    
    # 2x2 cluster (4 blocks) + 2 individual blocks
    # Should generate: 1 strike + 2 garbage blocks
    broken_blocks = [
        # 2x2 cluster
        (1, 1, 'red'),
        (2, 1, 'red'),
        (1, 2, 'red'),
        (2, 2, 'red'),
        # Individual blocks
        (4, 1, 'blue'),
        (5, 2, 'green'),
    ]
    
    print(f"   Breaking mixed combo: {len(broken_blocks)} blocks (4 cluster + 2 individual)")
    
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
    
    # Verify: 1 strike + 2 garbage blocks
    strikes = sum(a.count for a in attacks if a.attack_type == "strike")
    garbage = sum(a.count for a in attacks if a.attack_type == "garbage")
    
    if strikes == 1 and garbage == 2:
        print(f"   ✅ PASS: Mixed combo generates 1 strike + 2 garbage blocks")
    else:
        print(f"   ❌ FAIL: Expected 1 strike + 2 garbage blocks, got {strikes} strikes + {garbage} garbage blocks")
    
    attack_system.clear_attacks()
    print()


def test_breakers_excluded():
    """Test that breakers don't generate any attack output."""
    print("=== Testing Breakers Excluded ===")
    
    attack_system = SimpleAttackSystem()
    
    # 1 individual block + 1 breaker
    # Should generate: 1 garbage block, 0 strikes (breaker excluded)
    broken_blocks = [
        (1, 1, 'red'),           # Individual block
        (2, 1, 'blue_breaker'),  # Breaker (should be excluded)
    ]
    
    print(f"   Breaking combo with breaker: {len(broken_blocks)} blocks (1 individual + 1 breaker)")
    
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
    
    # Verify: 0 strikes, 1 garbage block (breaker excluded)
    strikes = sum(a.count for a in attacks if a.attack_type == "strike")
    garbage = sum(a.count for a in attacks if a.attack_type == "garbage")
    
    if strikes == 0 and garbage == 1:
        print(f"   ✅ PASS: Breaker excluded, only 1 garbage block generated")
    else:
        print(f"   ❌ FAIL: Expected 0 strikes, 1 garbage block, got {strikes} strikes, {garbage} garbage blocks")
    
    attack_system.clear_attacks()
    print()


def test_cluster_with_breakers():
    """Test that clusters with breakers still generate strikes."""
    print("=== Testing Cluster with Breakers ===")
    
    attack_system = SimpleAttackSystem()
    
    # 2x2 cluster with 1 breaker in the middle
    # Should generate: 1 strike (cluster), 0 garbage blocks (breaker excluded)
    broken_blocks = [
        (1, 1, 'red'),
        (2, 1, 'red'),
        (1, 2, 'red'),
        (2, 2, 'red'),
        (1, 3, 'blue_breaker'),  # Breaker (should be excluded)
    ]
    
    print(f"   Breaking cluster with breaker: {len(broken_blocks)} blocks (4 cluster + 1 breaker)")
    
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
    
    # Verify: 1 strike, 0 garbage blocks
    strikes = sum(a.count for a in attacks if a.attack_type == "strike")
    garbage = sum(a.count for a in attacks if a.attack_type == "garbage")
    
    if strikes == 1 and garbage == 0:
        print(f"   ✅ PASS: Cluster with breaker generates 1 strike, 0 garbage blocks")
    else:
        print(f"   ❌ FAIL: Expected 1 strike, 0 garbage blocks, got {strikes} strikes, {garbage} garbage blocks")
    
    attack_system.clear_attacks()
    print()


def test_chain_multiplier_effects():
    """Test that chain multiplier affects strikes but not garbage blocks."""
    print("=== Testing Chain Multiplier Effects ===")
    
    attack_system = SimpleAttackSystem()
    
    # 2x2 cluster in 3x combo
    # Should generate: 3 strikes (1 * 3), 0 garbage blocks
    broken_blocks = [
        (1, 1, 'red'),
        (2, 1, 'red'),
        (1, 2, 'red'),
        (2, 2, 'red'),
    ]
    
    print(f"   Breaking 2x2 cluster in 3x combo: {len(broken_blocks)} blocks")
    
    # Detect clusters
    clusters = attack_system.detect_clusters(broken_blocks)
    print(f"   Detected clusters: {clusters}")
    
    # Process combo with 3x multiplier
    attack_system.process_combo(broken_blocks, clusters, 3)
    
    # Get attacks
    attacks = attack_system.get_pending_attacks()
    
    print(f"   Generated {len(attacks)} attack(s):")
    for i, attack in enumerate(attacks):
        print(f"     Attack {i+1}: {attack.attack_type} - {attack.count} blocks")
    
    # Verify: 3 strikes, 0 garbage blocks
    strikes = sum(a.count for a in attacks if a.attack_type == "strike")
    garbage = sum(a.count for a in attacks if a.attack_type == "garbage")
    
    if strikes == 3 and garbage == 0:
        print(f"   ✅ PASS: 3x combo generates 3 strikes, 0 garbage blocks")
    else:
        print(f"   ❌ FAIL: Expected 3 strikes, 0 garbage blocks, got {strikes} strikes, {garbage} garbage blocks")
    
    attack_system.clear_attacks()
    print()


def main():
    """Run all separated attack system tests."""
    print("🎯 Separated Attack System Test")
    print("=" * 50)
    
    test_pure_cluster_attack()
    test_pure_individual_blocks()
    test_mixed_cluster_and_individual()
    test_breakers_excluded()
    test_cluster_with_breakers()
    test_chain_multiplier_effects()
    
    print("=" * 50)
    print("✅ All separated attack system tests completed!")
    print("\nThe new system properly separates:")
    print("- Clusters → Strikes (not garbage blocks)")
    print("- Individual blocks → Garbage blocks")
    print("- Breakers → No attack output")
    print("- Mixed combos → Both strikes AND garbage blocks")
    print("- Chain multiplier affects strikes, not garbage blocks")


if __name__ == "__main__":
    main() 