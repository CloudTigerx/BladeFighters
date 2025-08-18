#!/usr/bin/env python3
"""
Inventory Persistence Test
Tests that weapons persist in inventory and no color errors occur when equipping.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import pygame
from modules.game_state_module.game_state_manager import GameStateManager
from modules.items_module.item_system import create_weapon_by_name
from modules.items_module.catalog import CURATED_WEAPONS

def test_inventory_persistence():
    """Test that weapons persist in inventory across multiple accesses."""
    print("🧪 Testing Inventory Persistence...")
    
    # Initialize game state manager
    game_state_manager = GameStateManager()
    
    # Get player items system
    player_items = game_state_manager.get_player_items()
    
    # Test 1: Check initial state
    print("  📋 Test 1: Initial state")
    initial_weapons = player_items.get_owned_weapons()
    print(f"    Initial weapons: {len(initial_weapons)} weapons")
    print(f"    First few: {initial_weapons[:3]}")
    
    # Test 2: Add weapons
    print("  📋 Test 2: Adding weapons")
    test_weapons = ["Ember Blade", "Azure Rapier", "Crimson Divider"]  # Skip Rusted Sword since it's already there
    for weapon_name in test_weapons:
        player_items.add_weapon(weapon_name)
        print(f"    Added: {weapon_name}")
    
    # Test 3: Verify weapons persist across multiple get_player_items() calls
    print("  📋 Test 3: Persistence across multiple calls")
    expected_count = len(initial_weapons) + len(test_weapons)  # Should be 1 + 3 = 4
    for i in range(5):
        current_items = game_state_manager.get_player_items()
        current_weapons = current_items.get_owned_weapons()
        print(f"    Call {i+1}: {len(current_weapons)} weapons")
        if len(current_weapons) != expected_count:
            print(f"    ❌ ERROR: Weapons lost! Expected {expected_count}, got {len(current_weapons)}")
            return False
    
    # Test 4: Equip weapons and verify no color errors
    print("  📋 Test 4: Equipping weapons (color error test)")
    all_test_weapons = ["Rusted Sword"] + test_weapons  # Include Rusted Sword for equipping test
    for weapon_name in all_test_weapons:
        try:
            weapon = create_weapon_by_name(weapon_name)
            if weapon:
                player_items.equip_weapon(weapon)
                print(f"    ✅ Equipped: {weapon_name}")
                
                # Test pattern colors
                pattern = weapon.pattern
                for col in range(6):
                    color = pattern.color_for_column(col)
                    if not color or not isinstance(color, str):
                        print(f"    ❌ ERROR: Invalid color for column {col}: {color}")
                        return False
                    print(f"      Column {col}: {color}")
            else:
                print(f"    ❌ ERROR: Could not create weapon: {weapon_name}")
                return False
        except Exception as e:
            print(f"    ❌ ERROR: Exception equipping {weapon_name}: {e}")
            return False
    
    print("  ✅ All persistence tests passed!")
    return True

def test_color_safety():
    """Test that color generation is safe and doesn't cause pygame errors."""
    print("🎨 Testing Color Safety...")
    
    # Test weapon creation and color generation
    test_weapons = ["Rusted Sword", "Ember Blade", "Azure Rapier", "Crimson Divider"]
    
    for weapon_name in test_weapons:
        print(f"  📋 Testing {weapon_name}")
        try:
            weapon = create_weapon_by_name(weapon_name)
            if not weapon:
                print(f"    ❌ ERROR: Could not create weapon: {weapon_name}")
                return False
            
            # Test pattern colors
            pattern = weapon.pattern
            for col in range(6):
                color = pattern.color_for_column(col)
                if not color or not isinstance(color, str):
                    print(f"    ❌ ERROR: Invalid color for column {col}: {color}")
                    return False
                
                # Test cell colors
                for row in range(12):
                    cell_color = pattern.color_for_cell(col, row, 12)
                    if not cell_color or not isinstance(cell_color, str):
                        print(f"    ❌ ERROR: Invalid cell color at ({col}, {row}): {cell_color}")
                        return False
                
                print(f"    ✅ Column {col}: {color}")
            
        except Exception as e:
            print(f"    ❌ ERROR: Exception testing {weapon_name}: {e}")
            return False
    
    print("  ✅ All color safety tests passed!")
    return True

def test_catalog_weapons():
    """Test that catalog weapons can be created and have valid colors."""
    print("📚 Testing Catalog Weapons...")
    
    # Test first 10 weapons from catalog
    test_count = min(10, len(CURATED_WEAPONS))
    
    for i in range(test_count):
        weapon_data = CURATED_WEAPONS[i]
        weapon_name = weapon_data['name']
        print(f"  📋 Testing catalog weapon: {weapon_name}")
        
        try:
            weapon = create_weapon_by_name(weapon_name)
            if not weapon:
                print(f"    ❌ ERROR: Could not create weapon: {weapon_name}")
                return False
            
            # Test pattern colors
            pattern = weapon.pattern
            for col in range(6):
                color = pattern.color_for_column(col)
                if not color or not isinstance(color, str):
                    print(f"    ❌ ERROR: Invalid color for column {col}: {color}")
                    return False
            
            print(f"    ✅ {weapon_name}: Valid pattern")
            
        except Exception as e:
            print(f"    ❌ ERROR: Exception testing {weapon_name}: {e}")
            return False
    
    print("  ✅ All catalog weapon tests passed!")
    return True

def main():
    """Run all inventory persistence tests."""
    print("🔍 INVENTORY PERSISTENCE AND COLOR SAFETY TEST")
    print("=" * 50)
    
    # Initialize pygame for testing
    pygame.init()
    
    try:
        # Run all tests
        tests = [
            test_inventory_persistence,
            test_color_safety,
            test_catalog_weapons
        ]
        
        all_passed = True
        for test in tests:
            if not test():
                all_passed = False
            print()
        
        if all_passed:
            print("🎉 ALL TESTS PASSED!")
            print("✅ Inventory persistence is working correctly")
            print("✅ Color generation is safe")
            print("✅ No pygame color errors should occur")
        else:
            print("❌ SOME TESTS FAILED!")
            print("❌ Issues need to be addressed")
        
        return all_passed
        
    finally:
        pygame.quit()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
