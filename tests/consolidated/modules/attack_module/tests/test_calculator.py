#!/usr/bin/env python3
"""
Comprehensive test suite for AttackCalculator
Tests all formulas and complex scenarios from Attack Plans document
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from modules.attack_module.attack_calculator import AttackCalculator
from modules.attack_module.data_structures import ComboData, ClusterData, AttackPayload, ClusterType

def run_comprehensive_tests():
    """Run comprehensive attack calculator tests"""
    print("🎯 Testing AttackCalculator - COMPREHENSIVE SUITE...")
    print("="*70)
    
    passed = 0
    failed = 0
    
    # Basic garbage block calculations
    print("\n🗑️  Testing Garbage Block Calculations...")
    test_cases = [
        (5, 1, 5, "5 blocks single"),
        (5, 3, 15, "5 blocks triple"),
        (1, 1, 1, "1 block single"),
        (10, 3, 30, "10 blocks triple"),
        (7, 2, 14, "7 blocks double"),
        (12, 4, 48, "12 blocks quad"),
        (15, 5, 75, "15 blocks penta"),
        (20, 6, 120, "20 blocks hexa")
    ]
    
    for size, chain, expected, desc in test_cases:
        result = AttackCalculator.calculate_garbage_blocks(size, chain)
        if result == expected:
            print(f"✅ {desc} = {result} garbage blocks")
            passed += 1
        else:
            print(f"❌ {desc} = {result}, expected {expected}")
            failed += 1
    
    # Test all cluster patterns with extended combo levels
    print("\n⚔️  Testing 2x2 Cluster Patterns (Extended)...")
    test_cases = [
        (1, "1x4_vertical", "2x2 level 1"),
        (2, "2x4_vertical", "2x2 level 2"),
        (3, "2x6_vertical", "2x2 level 3"),
        (4, "2x8_vertical", "2x2 level 4"),
        (5, "2x10_vertical", "2x2 level 5"),
        (6, "2x12_vertical", "2x2 level 6"),
        (7, "2x12_vertical", "2x2 level 7 (max)"),
        (10, "2x12_vertical", "2x2 level 10 (max)")
    ]
    
    for level, expected, desc in test_cases:
        result = AttackCalculator.get_2x2_pattern(level)
        if result == expected:
            print(f"✅ {desc} = {result}")
            passed += 1
        else:
            print(f"❌ {desc} = {result}, expected {expected}")
            failed += 1
    
    print("\n⚔️  Testing 3x3 Cluster Patterns (Extended)...")
    test_cases = [
        (1, "2x4_vertical", "3x3 level 1"),
        (2, "3x6_vertical", "3x3 level 2"),
        (3, "3x9_vertical", "3x3 level 3"),
        (4, "3x12_vertical", "3x3 level 4"),
        (5, "3x12_vertical", "3x3 level 5 (max)"),
        (8, "3x12_vertical", "3x3 level 8 (max)")
    ]
    
    for level, expected, desc in test_cases:
        result = AttackCalculator.get_3x3_pattern(level)
        if result == expected:
            print(f"✅ {desc} = {result}")
            passed += 1
        else:
            print(f"❌ {desc} = {result}, expected {expected}")
            failed += 1
    
    print("\n⚔️  Testing 3x2 Cluster Patterns (Extended)...")
    test_cases = [
        (1, "3x2_horizontal", "3x2 level 1"),
        (2, "6x2_horizontal", "3x2 level 2"),
        (3, "2x12_vertical", "3x2 level 3 (converts to vertical)"),
        (4, "2x12_vertical", "3x2 level 4 (stays vertical)"),
        (5, "2x12_vertical", "3x2 level 5 (stays vertical)")
    ]
    
    for level, expected, desc in test_cases:
        result = AttackCalculator.get_3x2_pattern(level)
        if result == expected:
            print(f"✅ {desc} = {result}")
            passed += 1
        else:
            print(f"❌ {desc} = {result}, expected {expected}")
            failed += 1
    
    print("\n⚔️  Testing 4x4 Cluster Patterns (TWO SWORDS)...")
    test_cases = [
        (1, "two_1x4_vertical", "4x4 single = two 1x4"),
        (2, "two_2x4_vertical", "4x4 double = two 2x4"),
        (3, "two_2x6_vertical", "4x4 triple = two 2x6"),
        (4, "two_2x8_vertical", "4x4 quad = two 2x8"),
        (5, "two_2x10_vertical", "4x4 penta = two 2x10"),
        (6, "two_2x12_vertical", "4x4 hexa = two 2x12")
    ]
    
    for level, expected, desc in test_cases:
        result = AttackCalculator.get_4x4_pattern(level)
        if result == expected:
            print(f"✅ {desc} = {result}")
            passed += 1
        else:
            print(f"❌ {desc} = {result}, expected {expected}")
            failed += 1
    
    # Test complex chain scenarios
    print("\n🔗 Testing Complex Chain Scenarios...")
    
    # Test 1: Mixed cluster chain (2x2 → 3x3 → 2x2)
    print("\n📊 Complex Chain Test 1: 2x2 → 3x3 → 2x2")
    clusters = [
        ClusterData(
            cluster_type=ClusterType.CLUSTER_2x2,
            width=2, height=2,
            position_in_chain=1,
            combo_level=1,
            blocks_broken=4
        ),
        ClusterData(
            cluster_type=ClusterType.CLUSTER_3x3,
            width=3, height=3,
            position_in_chain=2,
            combo_level=2,
            blocks_broken=9
        ),
        ClusterData(
            cluster_type=ClusterType.CLUSTER_2x2,
            width=2, height=2,
            position_in_chain=3,
            combo_level=3,
            blocks_broken=4
        )
    ]
    combo_data = ComboData(
        size=17,  # 4 + 9 + 4
        chain_length=3,
        position_in_chain=3,
        clusters=clusters,
        garbage_blocks=0,
        target_player=1
    )
    
    # Create a simplified version that matches our test expectations
    simplified_clusters = []
    for cluster in clusters:
        simplified_cluster = type('SimpleCluster', (), {
            'type': cluster.cluster_type.value,
            'position': cluster.position_in_chain
        })()
        simplified_clusters.append(simplified_cluster)
    
    simplified_combo = type('SimpleCombo', (), {
        'clusters': simplified_clusters
    })()
    
    attacks = AttackCalculator.calculate_chain_attacks(simplified_combo)
    
    expected_patterns = ["1x4_vertical", "3x6_vertical", "2x6_vertical"]
    if len(attacks) == 3:
        all_correct = True
        for i, attack in enumerate(attacks):
            if attack.pattern == expected_patterns[i]:
                print(f"✅ Position {i+1}: {attack.pattern}")
                passed += 1
            else:
                print(f"❌ Position {i+1}: {attack.pattern}, expected {expected_patterns[i]}")
                all_correct = False
                failed += 1
    else:
        print(f"❌ Expected 3 attacks, got {len(attacks)}")
        failed += 1
    
    # Test 2: 3x3 → 2x2 → 3x3 → 4x4 chain
    print("\n📊 Complex Chain Test 2: 3x3 → 2x2 → 3x3 → 4x4")
    simplified_clusters = [
        type('SimpleCluster', (), {'type': "3x3", 'position': 1})(),
        type('SimpleCluster', (), {'type': "2x2", 'position': 2})(),
        type('SimpleCluster', (), {'type': "3x3", 'position': 3})(),
        type('SimpleCluster', (), {'type': "4x4", 'position': 4})()
    ]
    
    simplified_combo = type('SimpleCombo', (), {
        'clusters': simplified_clusters
    })()
    
    attacks = AttackCalculator.calculate_chain_attacks(simplified_combo)
    
    expected_patterns = ["2x4_vertical", "2x4_vertical", "3x9_vertical", "two_2x8_vertical"]
    if len(attacks) == 4:
        for i, attack in enumerate(attacks):
            if attack.pattern == expected_patterns[i]:
                print(f"✅ Position {i+1}: {attack.pattern}")
                passed += 1
            else:
                print(f"❌ Position {i+1}: {attack.pattern}, expected {expected_patterns[i]}")
                failed += 1
    else:
        print(f"❌ Expected 4 attacks, got {len(attacks)}")
        failed += 1
    
    # Test 3: Instant kill scenario (3x3 + 2x2 in 4-chain)
    print("\n📊 Complex Chain Test 3: Instant Kill Scenario")
    simplified_clusters = [
        type('SimpleCluster', (), {'type': "3x3", 'position': 1})(),
        type('SimpleCluster', (), {'type': "2x2", 'position': 2})(),
        type('SimpleCluster', (), {'type': "3x3", 'position': 3})(),
        type('SimpleCluster', (), {'type': "3x3", 'position': 4})()
    ]
    
    simplified_combo = type('SimpleCombo', (), {
        'clusters': simplified_clusters
    })()
    
    attacks = AttackCalculator.calculate_chain_attacks(simplified_combo)
    
    expected_patterns = ["2x4_vertical", "2x4_vertical", "3x9_vertical", "3x12_vertical"]
    lethal_check = attacks[-1].pattern == "3x12_vertical"  # 3x12 can fill entire board
    
    if len(attacks) == 4 and lethal_check:
        for i, attack in enumerate(attacks):
            if attack.pattern == expected_patterns[i]:
                status = "🔥 LETHAL!" if i == 3 else "✅"
                print(f"{status} Position {i+1}: {attack.pattern}")
                passed += 1
            else:
                print(f"❌ Position {i+1}: {attack.pattern}, expected {expected_patterns[i]}")
                failed += 1
    else:
        print(f"❌ Expected 4 attacks with lethal finale, got {len(attacks)}")
        failed += 1
    
    # Test 4: All 4x4 clusters creating multiple swords
    print("\n📊 Complex Chain Test 4: Multiple 4x4 Clusters")
    simplified_clusters = [
        type('SimpleCluster', (), {'type': "4x4", 'position': 1})(),
        type('SimpleCluster', (), {'type': "4x4", 'position': 2})(),
        type('SimpleCluster', (), {'type': "4x4", 'position': 3})()
    ]
    
    simplified_combo = type('SimpleCombo', (), {
        'clusters': simplified_clusters
    })()
    
    attacks = AttackCalculator.calculate_chain_attacks(simplified_combo)
    
    expected_patterns = ["two_1x4_vertical", "two_2x4_vertical", "two_2x6_vertical"]
    if len(attacks) == 3:
        total_swords = 0
        for i, attack in enumerate(attacks):
            if attack.pattern == expected_patterns[i]:
                sword_count = 2  # All 4x4 create 2 swords
                total_swords += sword_count
                print(f"✅ Position {i+1}: {attack.pattern} ({sword_count} swords)")
                passed += 1
            else:
                print(f"❌ Position {i+1}: {attack.pattern}, expected {expected_patterns[i]}")
                failed += 1
        print(f"📊 Total swords generated: {total_swords}")
    
    # Test 5: Mixed garbage + cluster scenario (from original test)
    print("\n📊 Complex Mixed Test: Original 2x3 Scenario")
    print("Input: 1 garbage + (2x3 cluster + 3 garbage)*2 + 10 garbage*3")
    print("Expected: 1×2x6 horizontal + 37 garbage blocks")
    
    attacks = []
    total_garbage = 0
    
    # 1 garbage single
    total_garbage += AttackCalculator.calculate_garbage_blocks(1, 1)
    
    # (2x3 cluster + 3 garbage)*2 = 2x3 double + 6 garbage
    cluster_attack = AttackCalculator.get_3x2_pattern(2)  # 2x3 doubled
    attacks.append(type('SimpleAttack', (), {
        'attack_type': "cluster_strike",
        'pattern': cluster_attack,
        'width': 6 if "6x2" in cluster_attack else 2,
        'height': 2 if "6x2" in cluster_attack else 12
    })())
    total_garbage += AttackCalculator.calculate_garbage_blocks(3, 2)
    
    # 10 garbage*3 = 30 garbage
    total_garbage += AttackCalculator.calculate_garbage_blocks(10, 3)
    
    print(f"📊 Results:")
    print(f"   Total garbage blocks: {total_garbage}")
    print(f"   Strikes: {[{'pattern': attack.pattern, 'width': attack.width, 'height': attack.height} for attack in attacks]}")
    
    if total_garbage == 37:
        print("✅ Total garbage blocks = 37")
        passed += 1
    else:
        print(f"❌ Total garbage blocks = {total_garbage}, expected 37")
        failed += 1
    
    if len(attacks) == 1 and attacks[0].pattern == "6x2_horizontal":
        print("✅ Strike pattern = 6x2_horizontal")
        passed += 1
    else:
        print(f"❌ Strike pattern = {attacks[0].pattern if attacks else 'none'}, expected 6x2_horizontal")
        failed += 1
    
    # Test 6: Extreme combo level scenarios
    print("\n📊 Extreme Combo Level Tests...")
    extreme_tests = [
        ("2x2", 10, "2x12_vertical", "2x2 level 10 (max capped)"),
        ("3x3", 15, "3x12_vertical", "3x3 level 15 (max capped)"),
        ("3x2", 8, "2x12_vertical", "3x2 level 8 (vertical conversion)"),
        ("4x4", 7, "two_2x12_vertical", "4x4 level 7 (two max swords)")
    ]
    
    for cluster_type, level, expected, desc in extreme_tests:
        if cluster_type == "2x2":
            result = AttackCalculator.get_2x2_pattern(level)
        elif cluster_type == "3x3":
            result = AttackCalculator.get_3x3_pattern(level)
        elif cluster_type == "3x2":
            result = AttackCalculator.get_3x2_pattern(level)
        elif cluster_type == "4x4":
            result = AttackCalculator.get_4x4_pattern(level)
        
        if result == expected:
            print(f"✅ {desc} = {result}")
            passed += 1
        else:
            print(f"❌ {desc} = {result}, expected {expected}")
            failed += 1
    
    # Test 7: Edge case - empty and single cluster chains
    print("\n📊 Edge Case Tests...")
    
    # Empty chain
    empty_combo = type('SimpleCombo', (), {'clusters': []})()
    empty_attacks = AttackCalculator.calculate_chain_attacks(empty_combo)
    if len(empty_attacks) == 0:
        print("✅ Empty chain produces no attacks")
        passed += 1
    else:
        print(f"❌ Empty chain produced {len(empty_attacks)} attacks")
        failed += 1
    
    # Single cluster chain
    single_combo = type('SimpleCombo', (), {
        'clusters': [type('SimpleCluster', (), {'type': "2x2", 'position': 1})()]
    })()
    single_attacks = AttackCalculator.calculate_chain_attacks(single_combo)
    if len(single_attacks) == 1 and single_attacks[0].pattern == "1x4_vertical":
        print("✅ Single 2x2 cluster produces 1x4_vertical")
        passed += 1
    else:
        print(f"❌ Single 2x2 cluster produced {single_attacks[0].pattern if single_attacks else 'none'}")
        failed += 1
    
    print("\n" + "="*70)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {passed + failed}")
    
    if failed == 0:
        print("🎉 All comprehensive tests passed! Attack calculator is fully validated.")
    else:
        print(f"⚠️  {failed} test(s) failed. Please review attack calculation logic.")
    
    return failed == 0

if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1) 