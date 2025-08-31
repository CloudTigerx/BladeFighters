#!/usr/bin/env python3
"""Test script to verify horizontal sword generation."""

from swordfighting_new.attacks.manager import default_strike_formula

def test_horizontal_sword_generation():
    print("Testing horizontal sword generation...")

    # Test case 1: horizontal cluster (w > h, h >= 2)
    # 4x2 cluster with chain index 1
    rect1 = {'width': 4, 'height': 2, 'size': 8}
    result1 = default_strike_formula(rect1, 1)
    print(f"4x2 cluster, chain=1: {result1}")

    # Test case 2: horizontal cluster (w > h, h >= 2)
    # 5x2 cluster with chain index 2
    rect2 = {'width': 5, 'height': 2, 'size': 10}
    result2 = default_strike_formula(rect2, 2)
    print(f"5x2 cluster, chain=2: {result2}")

    # Test case 3: horizontal cluster that should convert to vertical
    # 6x2 cluster with chain index 3 (6*3=18 >= 12, should convert)
    rect3 = {'width': 6, 'height': 2, 'size': 12}
    result3 = default_strike_formula(rect3, 3)
    print(f"6x2 cluster, chain=3: {result3}")

    # Test case 4: vertical cluster (should create vertical sword)
    rect4 = {'width': 2, 'height': 4, 'size': 8}
    result4 = default_strike_formula(rect4, 1)
    print(f"2x4 cluster, chain=1: {result4}")

if __name__ == "__main__":
    test_horizontal_sword_generation()
