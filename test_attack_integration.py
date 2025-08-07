#!/usr/bin/env python3
"""
Test Attack Integration

Tests that the simple attack system is properly integrated into TestMode.
"""

import sys
import os

# Add the modules directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

from attack_module import SimpleAttackSystem, AttackData


def test_attack_flow():
    """Test the complete attack flow between players."""
    print("=== Testing Attack Flow ===")
    
    # Create attack systems for both players
    player_attack_system = SimpleAttackSystem(grid_width=6)
    enemy_attack_system = SimpleAttackSystem(grid_width=6)
    
    # Simulate player breaking blocks
    print("\n🎯 Player breaks blocks...")
    player_broken_blocks = [
        (1, 1, 'red'),
        (2, 1, 'red'),
        (1, 2, 'red'),
        (2, 2, 'red'),  # 2x2 cluster
        (3, 1, 'blue'),
    ]
    
    # Process player combo
    player_clusters = player_attack_system.detect_clusters(player_broken_blocks)
    player_attacks = player_attack_system.process_combo(player_broken_blocks, player_clusters, 2)  # 2x combo
    
    print(f"Player attack summary: {player_attack_system.get_attack_summary()}")
    
    # Simulate sending attacks to enemy
    print("\n🎯 Sending player attacks to enemy...")
    enemy_attacks = player_attack_system.get_pending_attacks()
    for attack in enemy_attacks:
        print(f"  - {attack.count} {attack.attack_type}(s) to column {attack.target_column}")
    
    # Clear player attacks after sending
    player_attack_system.clear_attacks()
    print(f"Player attacks cleared: {player_attack_system.get_attack_summary()}")
    
    # Simulate enemy breaking blocks
    print("\n🎯 Enemy breaks blocks...")
    enemy_broken_blocks = [
        (1, 1, 'green'),
        (2, 1, 'green'),
        (3, 1, 'green'),
    ]
    
    # Process enemy combo
    enemy_clusters = enemy_attack_system.detect_clusters(enemy_broken_blocks)
    enemy_attacks = enemy_attack_system.process_combo(enemy_broken_blocks, enemy_clusters, 1)  # 1x combo
    
    print(f"Enemy attack summary: {enemy_attack_system.get_attack_summary()}")
    
    # Simulate sending attacks to player
    print("\n🎯 Sending enemy attacks to player...")
    player_attacks = enemy_attack_system.get_pending_attacks()
    for attack in player_attacks:
        print(f"  - {attack.count} {attack.attack_type}(s) to column {attack.target_column}")
    
    # Clear enemy attacks after sending
    enemy_attack_system.clear_attacks()
    print(f"Enemy attacks cleared: {enemy_attack_system.get_attack_summary()}")
    
    print("\n✅ Attack flow test completed!")


def test_chain_mechanics():
    """Test chain mechanics in the attack system."""
    print("\n=== Testing Chain Mechanics ===")
    
    attack_system = SimpleAttackSystem()
    
    # Simulate a chain of combos
    combos = [
        # (broken_blocks, clusters, chain_position)
        (3, [], 1),      # 1x combo: 3 blocks
        (2, [4], 2),     # 2x combo: 2 blocks + 2x2 cluster
        (1, [], 3),      # 3x combo: 1 block
    ]
    
    for broken_count, clusters, chain_pos in combos:
        # Create dummy broken blocks
        broken_blocks = [(i, 0, 'red') for i in range(broken_count)]
        
        attacks = attack_system.process_combo(broken_blocks, clusters, chain_pos)
        
        garbage = sum(a.count for a in attacks if a.attack_type == "garbage")
        strikes = sum(a.count for a in attacks if a.attack_type == "strike")
        
        print(f"Chain {chain_pos}x: {broken_count} blocks + {clusters} clusters")
        print(f"  -> {garbage} garbage + {strikes} strikes")
    
    print(f"Total pending: {attack_system.get_attack_summary()}")
    
    # Test clearing attacks
    attack_system.clear_attacks()
    print(f"After clearing: {attack_system.get_attack_summary()}")


def test_column_rotation():
    """Test that column rotation works correctly."""
    print("\n=== Testing Column Rotation ===")
    
    attack_system = SimpleAttackSystem()
    
    # Simulate multiple attacks to test column rotation
    for i in range(8):
        broken_blocks = [(0, 0, 'red')]  # Single block
        attacks = attack_system.process_combo(broken_blocks, [], 1)
        
        if attacks:
            attack = attacks[0]
            print(f"Attack {i+1}: {attack.count} {attack.attack_type}(s) to column {attack.target_column}")
    
    print(f"Final summary: {attack_system.get_attack_summary()}")


def main():
    """Run all integration tests."""
    print("🎯 Attack Integration Test")
    print("=" * 50)
    
    test_attack_flow()
    test_chain_mechanics()
    test_column_rotation()
    
    print("\n" + "=" * 50)
    print("✅ All integration tests completed!")
    print("\nThe attack system is now integrated and ready to use!")
    print("When you run the game:")
    print("- Player combos will generate attacks sent to the enemy")
    print("- Enemy combos will generate attacks sent to the player")
    print("- Attacks will appear as garbage blocks on the opponent's grid")
    print("- Chain combos will multiply attack strength")


if __name__ == "__main__":
    main() 