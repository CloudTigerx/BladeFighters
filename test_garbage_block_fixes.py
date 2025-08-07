#!/usr/bin/env python3
"""
Test Garbage Block Fixes

Tests the fixes for:
1. 1:1 ratio (3 blocks broken = 3 garbage blocks sent)
2. Column alternation (each garbage block goes to different column)
"""

import sys
import os

# Add the modules directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

from attack_module import SimpleAttackSystem, AttackCalculator, ColumnRotator


def test_garbage_block_calculation():
    """Test that garbage block calculation is 1:1 ratio."""
    print("=== Testing Garbage Block Calculation ===")
    
    calculator = AttackCalculator()
    
    test_cases = [
        {"broken": 3, "chain": 1, "expected": 3},
        {"broken": 5, "chain": 2, "expected": 5},  # Chain multiplier shouldn't affect garbage
        {"broken": 2, "chain": 3, "expected": 2},
        {"broken": 10, "chain": 1, "expected": 10},
    ]
    
    for test_case in test_cases:
        result = calculator.calculate_garbage_attack(
            test_case["broken"], test_case["chain"]
        )
        
        print(f"   {test_case['broken']} blocks broken in {test_case['chain']}x combo:")
        print(f"   Expected: {test_case['expected']} garbage blocks")
        print(f"   Got: {result} garbage blocks")
        
        if result == test_case["expected"]:
            print(f"   ✅ PASS: 1:1 ratio maintained")
        else:
            print(f"   ❌ FAIL: Expected {test_case['expected']}, got {result}")
        print()


def test_column_rotation():
    """Test that column rotation works correctly."""
    print("=== Testing Column Rotation ===")
    
    rotator = ColumnRotator(grid_width=6)
    
    # Test the rotation pattern: 1→6→2→5→3→4 (0-based: 0→5→1→4→2→3)
    expected_pattern = [0, 5, 1, 4, 2, 3]
    
    print(f"   Expected pattern: {expected_pattern}")
    print(f"   Testing rotation:")
    
    actual_pattern = []
    for i in range(6):
        column = rotator.get_next_column()
        actual_pattern.append(column)
        print(f"   Step {i+1}: Column {column}")
    
    print(f"   Actual pattern: {actual_pattern}")
    
    if actual_pattern == expected_pattern:
        print(f"   ✅ PASS: Column rotation correct")
    else:
        print(f"   ❌ FAIL: Expected {expected_pattern}, got {actual_pattern}")
    print()


def test_attack_system_integration():
    """Test the complete attack system integration."""
    print("=== Testing Attack System Integration ===")
    
    attack_system = SimpleAttackSystem()
    
    # Simulate breaking 3 blocks
    broken_blocks = [
        (1, 1, 'red'),
        (2, 1, 'blue'),
        (3, 1, 'green'),
    ]
    
    print(f"   Simulating: {len(broken_blocks)} blocks broken")
    
    # Process the combo
    attack_system.process_combo(broken_blocks, [], 1)  # No clusters, 1x combo
    
    # Get pending attacks
    attacks = attack_system.get_pending_attacks()
    
    print(f"   Generated {len(attacks)} attack(s)")
    
    for i, attack in enumerate(attacks):
        print(f"   Attack {i+1}: {attack.attack_type} - {attack.count} blocks at column {attack.target_column}")
    
    # Verify we have exactly one garbage attack with 3 blocks
    if len(attacks) == 1 and attacks[0].attack_type == "garbage" and attacks[0].count == 3:
        print(f"   ✅ PASS: Correct attack generation")
    else:
        print(f"   ❌ FAIL: Expected 1 garbage attack with 3 blocks")
    print()


def test_garbage_block_placement_simulation():
    """Simulate garbage block placement to verify column alternation."""
    print("=== Testing Garbage Block Placement Simulation ===")
    
    # Simulate placing 3 garbage blocks
    count = 3
    column_rotator = ColumnRotator(grid_width=6)
    
    print(f"   Placing {count} garbage blocks:")
    
    placement_columns = []
    for i in range(count):
        column = column_rotator.get_next_column()
        placement_columns.append(column)
        print(f"   Block {i+1}: Column {column}")
    
    print(f"   Placement columns: {placement_columns}")
    
    # Check that columns are different (no stacking)
    if len(set(placement_columns)) == len(placement_columns):
        print(f"   ✅ PASS: No stacking - each block in different column")
    else:
        print(f"   ❌ FAIL: Blocks are stacking in same columns")
    
    # Check that we're following the rotation pattern
    expected_columns = [0, 5, 1]  # First 3 columns in rotation
    if placement_columns == expected_columns:
        print(f"   ✅ PASS: Following correct rotation pattern")
    else:
        print(f"   ❌ FAIL: Expected {expected_columns}, got {placement_columns}")
    print()


def main():
    """Run all garbage block fix tests."""
    print("🎯 Garbage Block Fixes Test")
    print("=" * 50)
    
    test_garbage_block_calculation()
    test_column_rotation()
    test_attack_system_integration()
    test_garbage_block_placement_simulation()
    
    print("=" * 50)
    print("✅ All garbage block fix tests completed!")
    print("\nThe fixes address:")
    print("- 1:1 ratio: 3 blocks broken = 3 garbage blocks sent")
    print("- Column alternation: Each garbage block goes to different column")
    print("- No stacking: Garbage blocks don't pile on top of each other")
    print("- Proper rotation: Following 1→6→2→5→3→4 pattern")


if __name__ == "__main__":
    main() 