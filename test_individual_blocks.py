#!/usr/bin/env python3
"""
Test Individual Blocks Attack Generation
"""

import sys
import os

# Add the modules directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

from attack_module import SimpleAttackSystem, AttackCombo
from attack_module.attack_database import AttackDatabase

def test_individual_blocks():
    """Test that individual blocks generate correct garbage output."""
    print("=== TESTING INDIVIDUAL BLOCKS ===")
    print("Expected: 1:1 ratio - 1 block = 1 garbage block")
    print()
    
    # Create attack system
    attack_system = SimpleAttackSystem(grid_width=6)
    attack_system.enable_database("attack_database.json")
    
    # Test cases
    test_cases = [
        (1, "1 individual block"),
        (2, "2 individual blocks"), 
        (3, "3 individual blocks"),
        (4, "4 individual blocks"),
        (5, "5 individual blocks")
    ]
    
    for block_count, description in test_cases:
        print(f"🧪 Testing {description}:")
        
        # Create broken blocks (individual, no clusters)
        broken_blocks = []
        for i in range(block_count):
            broken_blocks.append((i, 0, f"color_{i}"))
        
        # No clusters detected
        clusters = []
        
        # Process combo
        attack_system.process_combo(broken_blocks, clusters, 1)
        
        # Get attacks
        attacks = attack_system.get_pending_attacks()
        
        # Count garbage blocks
        garbage_count = sum(a.count for a in attacks if a.attack_type == "garbage")
        strike_count = sum(a.count for a in attacks if a.attack_type == "strike")
        
        print(f"   Blocks broken: {block_count}")
        print(f"   Garbage generated: {garbage_count}")
        print(f"   Strikes generated: {strike_count}")
        
        if garbage_count == block_count and strike_count == 0:
            print(f"   ✅ PASS: {block_count} blocks → {garbage_count} garbage blocks")
        else:
            print(f"   ❌ FAIL: Expected {block_count} garbage blocks, got {garbage_count}")
        
        print()
        attack_system.clear_attacks()
    
    print("=== TESTING WITH BREAKERS ===")
    print("Expected: Breakers should be excluded from garbage count")
    print()
    
    # Test with breakers
    test_cases_with_breakers = [
        (3, 1, "3 individual + 1 breaker"),
        (4, 2, "4 individual + 2 breakers"),
        (5, 1, "5 individual + 1 breaker")
    ]
    
    for total_blocks, breaker_count, description in test_cases_with_breakers:
        print(f"🧪 Testing {description}:")
        
        # Create broken blocks
        broken_blocks = []
        for i in range(total_blocks - breaker_count):
            broken_blocks.append((i, 0, f"color_{i}"))
        
        # Add breakers
        for i in range(breaker_count):
            broken_blocks.append((i + total_blocks - breaker_count, 0, f"color_{i}_breaker"))
        
        # No clusters detected
        clusters = []
        
        # Process combo
        attack_system.process_combo(broken_blocks, clusters, 1)
        
        # Get attacks
        attacks = attack_system.get_pending_attacks()
        
        # Count garbage blocks
        garbage_count = sum(a.count for a in attacks if a.attack_type == "garbage")
        strike_count = sum(a.count for a in attacks if a.attack_type == "strike")
        expected_garbage = total_blocks - breaker_count
        
        print(f"   Total blocks: {total_blocks}")
        print(f"   Breakers: {breaker_count}")
        print(f"   Expected garbage: {expected_garbage}")
        print(f"   Actual garbage: {garbage_count}")
        print(f"   Strikes: {strike_count}")
        
        if garbage_count == expected_garbage and strike_count == 0:
            print(f"   ✅ PASS: {expected_garbage} garbage blocks (breakers excluded)")
        else:
            print(f"   ❌ FAIL: Expected {expected_garbage} garbage blocks, got {garbage_count}")
        
        print()
        attack_system.clear_attacks()

if __name__ == "__main__":
    test_individual_blocks() 