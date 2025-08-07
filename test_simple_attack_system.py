#!/usr/bin/env python3
"""
Test Simple Attack System

Demonstrates how the simplified attack system works.
"""

import sys
import os

# Add the modules directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

from attack_module import SimpleAttackSystem, AttackCalculator, ColumnRotator


def test_basic_attacks():
    """Test basic attack calculations."""
    print("=== Testing Basic Attacks ===")
    
    calculator = AttackCalculator()
    
    # Test garbage block calculation (1:1 ratio, no chain multiplier)
    print(f"3 blocks broken in 1x combo: {calculator.calculate_garbage_attack(3, 1)} garbage blocks")
    print(f"3 blocks broken in 3x combo: {calculator.calculate_garbage_attack(3, 3)} garbage blocks")
    print(f"5 blocks broken in 2x combo: {calculator.calculate_garbage_attack(5, 2)} garbage blocks")
    
    # Test strike calculation (mirror + chain multiplier)
    print(f"2x2 cluster (4 blocks) in 1x combo: {calculator.calculate_strike_attack(4, 1)} strikes")
    print(f"2x2 cluster (4 blocks) in 3x combo: {calculator.calculate_strike_attack(4, 3)} strikes")
    print(f"3x3 cluster (9 blocks) in 2x combo: {calculator.calculate_strike_attack(9, 2)} strikes")
    print(f"4x4 cluster (16 blocks) in 1x combo: {calculator.calculate_strike_attack(16, 1)} strikes")
    
    print()


def test_attack_system():
    """Test the complete attack system."""
    print("=== Testing Attack System ===")
    
    attack_system = SimpleAttackSystem()
    
    # Simulate breaking blocks
    broken_blocks = [
        (1, 1, 'red'),
        (2, 1, 'red'),
        (1, 2, 'red'),
        (2, 2, 'red'),  # This forms a 2x2 cluster
        (3, 1, 'blue'),
        (4, 1, 'blue'),
    ]
    
    # Detect clusters
    clusters = attack_system.detect_clusters(broken_blocks)
    print(f"Broken blocks: {len(broken_blocks)}")
    print(f"Detected clusters: {clusters}")
    
    # Process combo
    attacks = attack_system.process_combo(broken_blocks, clusters, 2)  # 2x combo
    print(f"Generated attacks: {len(attacks)}")
    
    for attack in attacks:
        print(f"  - {attack}")
    
    print(f"Attack summary: {attack_system.get_attack_summary()}")
    print()


def test_chain_combos():
    """Test chain combo mechanics."""
    print("=== Testing Chain Combos ===")
    
    attack_system = SimpleAttackSystem()
    
    # Simulate a chain of combos
    combos = [
        # (broken_blocks, clusters, chain_position)
        (3, [], 1),      # 1x combo: 3 blocks
        (2, [4], 2),     # 2x combo: 2 blocks + 2x2 cluster
        (1, [], 3),      # 3x combo: 1 block
    ]
    
    total_garbage = 0
    total_strikes = 0
    
    for broken_count, clusters, chain_pos in combos:
        # Create dummy broken blocks
        broken_blocks = [(i, 0, 'red') for i in range(broken_count)]
        
        attacks = attack_system.process_combo(broken_blocks, clusters, chain_pos)
        
        garbage = sum(a.count for a in attacks if a.attack_type == "garbage")
        strikes = sum(a.count for a in attacks if a.attack_type == "strike")
        
        total_garbage += garbage
        total_strikes += strikes
        
        print(f"Chain {chain_pos}x: {broken_count} blocks + {clusters} clusters")
        print(f"  -> {garbage} garbage + {strikes} strikes")
    
    print(f"Total attack: {total_garbage} garbage + {total_strikes} strikes")
    print()


def test_cluster_scaling():
    """Test cluster scaling with chain multipliers."""
    print("=== Testing Cluster Scaling ===")
    
    calculator = AttackCalculator()
    
    # Test different cluster sizes and chain multipliers
    test_cases = [
        (4, 1, "2x2 cluster, 1x combo"),
        (4, 2, "2x2 cluster, 2x combo"),
        (4, 3, "2x2 cluster, 3x combo"),
        (9, 1, "3x3 cluster, 1x combo"),
        (9, 2, "3x3 cluster, 2x combo"),
        (16, 1, "4x4 cluster, 1x combo"),
        (16, 3, "4x4 cluster, 3x combo"),
    ]
    
    for cluster_size, chain_multiplier, description in test_cases:
        strikes = calculator.calculate_strike_attack(cluster_size, chain_multiplier)
        print(f"{description}: {strikes} strikes")
    
    print()


def test_column_rotation():
    """Test column rotation."""
    print("=== Testing Column Rotation ===")
    
    rotator = ColumnRotator()
    
    print("Column rotation pattern:")
    for i in range(10):
        column = rotator.get_next_column()
        print(f"  Attack {i+1}: Column {column}")
    
    print()


def test_significant_attacks():
    """Test significant attack detection."""
    print("=== Testing Significant Attacks ===")
    
    calculator = AttackCalculator()
    
    test_cases = [
        (3, [], 1, "Small 1x combo"),
        (5, [], 3, "Medium 3x combo"),
        (2, [4], 2, "2x2 cluster in 2x combo"),
        (10, [], 5, "Large 5x combo"),
        (1, [9], 4, "3x3 cluster in 4x combo"),
    ]
    
    for broken_blocks, clusters, chain_multiplier, description in test_cases:
        is_significant = calculator.is_significant_attack(broken_blocks, clusters, chain_multiplier)
        attack_desc = calculator.get_attack_description(broken_blocks, clusters, chain_multiplier)
        
        status = "SIGNIFICANT" if is_significant else "normal"
        print(f"{description}: {attack_desc} ({status})")
    
    print()


def main():
    """Run all tests."""
    print("🎯 Simple Attack System Test (Updated)")
    print("=" * 50)
    
    test_basic_attacks()
    test_attack_system()
    test_chain_combos()
    test_cluster_scaling()
    test_column_rotation()
    test_significant_attacks()
    
    print("✅ All tests completed!")
    print()
    print("Updated attack system:")
    print("- Garbage blocks: 1:1 ratio (no chain multiplier)")
    print("- Strikes: Mirror cluster size + chain multiplier")
    print("- 2x2 cluster (4 blocks) = 1 strike base")
    print("- 3x3 cluster (9 blocks) = 2 strikes base")
    print("- Chain combos multiply strike damage, not garbage")
    print("- Much more balanced and predictable!")


if __name__ == "__main__":
    main() 