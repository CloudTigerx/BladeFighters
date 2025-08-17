#!/usr/bin/env python3
"""
Weapon Integration Test Suite
Tests weapon system integration with 6x12 grid patterns and attack delivery.
"""

import sys
import os
import time
import traceback
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pygame
from modules.items_module.item_system import ItemSystem, create_rusted_sword, Weapon, WeaponPattern
from modules.testmode_module.attack_delivery_committer import AttackDeliveryCommitter
from modules.testmode_module.attack_delivery_planner import AttackDeliveryPlanner
from modules.testmode_module.test_mode import TestModeRefactored

class WeaponIntegrationTest:
    """Comprehensive test suite for weapon system integration."""
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        self.font = pygame.font.Font(None, 24)
        self.clock = pygame.time.Clock()
        
        # Initialize test components
        self.item_system = ItemSystem()
        self.test_mode = TestModeRefactored(self.screen, self.font, None, "puzzleassets")
        self.engine = self.test_mode.puzzle_engine
        
        # Initialize attack delivery components
        self.planner = AttackDeliveryPlanner(self.item_system)
        self.committer = AttackDeliveryCommitter({})
        
        # Test results tracking
        self.test_results = {}
        self.debug_log = []
        
    def log_debug(self, message: str):
        """Log debug information."""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.debug_log.append(log_entry)
        print(log_entry)
    
    def test_6x12_grid_pattern_validation(self) -> bool:
        """Test 1: 6x12 grid pattern validation and color mapping."""
        self.log_debug("🔍 TEST 1: 6x12 Grid Pattern Validation")
        
        try:
            # Test default weapon (Rusted Sword)
            weapon = create_rusted_sword()
            pattern = weapon.pattern
            
            # Verify grid dimensions
            if pattern.grid_height == 12:
                self.log_debug(f"  ✅ Grid height: {pattern.grid_height}")
            else:
                self.log_debug(f"  ❌ Expected grid height 12, got {pattern.grid_height}")
                return False
            
            # Test column-to-color mapping for 6 columns
            expected_mapping = {
                0: "red", 1: "red",      # Left side: red
                2: "blue", 3: "blue",    # Center: blue  
                4: "green", 5: "green",  # Right side: green
            }
            
            all_passed = True
            for column in range(6):
                expected_color = expected_mapping[column]
                actual_color = pattern.color_for_column(column)
                if actual_color == expected_color:
                    self.log_debug(f"  ✅ Column {column}: {actual_color}")
                else:
                    self.log_debug(f"  ❌ Column {column}: expected {expected_color}, got {actual_color}")
                    all_passed = False
            
            # Test cell-specific color mapping
            test_cells = [(0, 0), (2, 5), (4, 11)]  # Different columns and rows
            for col, row in test_cells:
                color = pattern.color_for_cell(col, row, 12)
                if color in ["red", "blue", "green"]:
                    self.log_debug(f"  ✅ Cell ({col}, {row}): {color}")
                else:
                    self.log_debug(f"  ❌ Cell ({col}, {row}): invalid color {color}")
                    all_passed = False
            
            self.test_results['grid_pattern_validation'] = all_passed
            return all_passed
            
        except Exception as e:
            self.log_debug(f"  ❌ Grid pattern validation failed: {e}")
            self.test_results['grid_pattern_validation'] = False
            return False
    
    def test_weapon_pattern_integration(self) -> bool:
        """Test 2: Weapon pattern integration with item system."""
        self.log_debug("🔍 TEST 2: Weapon Pattern Integration")
        
        try:
            # Equip default weapon
            weapon = create_rusted_sword()
            self.item_system.equip_weapon(weapon)
            
            # Test attack color generation
            test_columns = [0, 1, 2, 3, 4, 5]
            expected_colors = ["red", "red", "blue", "blue", "green", "green"]
            
            all_passed = True
            for i, column in enumerate(test_columns):
                expected_color = expected_colors[i]
                actual_color = self.item_system.get_attack_color_for_column(column)
                if actual_color == expected_color:
                    self.log_debug(f"  ✅ Attack color column {column}: {actual_color}")
                else:
                    self.log_debug(f"  ❌ Attack color column {column}: expected {expected_color}, got {actual_color}")
                    all_passed = False
            
            # Test garbage color generation
            for i, column in enumerate(test_columns):
                expected_color = expected_colors[i]
                actual_color = self.item_system.get_garbage_color_for_column(column)
                if actual_color == expected_color:
                    self.log_debug(f"  ✅ Garbage color column {column}: {actual_color}")
                else:
                    self.log_debug(f"  ❌ Garbage color column {column}: expected {expected_color}, got {actual_color}")
                    all_passed = False
            
            # Test strike color generation
            test_cells = [(0, 0, 12), (2, 5, 12), (4, 11, 12)]  # (col, row, height)
            for col, row, height in test_cells:
                color = self.item_system.get_strike_color_for_cell(col, row, height)
                if color in ["red", "blue", "green"]:
                    self.log_debug(f"  ✅ Strike color cell ({col}, {row}): {color}")
                else:
                    self.log_debug(f"  ❌ Strike color cell ({col}, {row}): invalid color {color}")
                    all_passed = False
            
            self.test_results['weapon_pattern_integration'] = all_passed
            return all_passed
            
        except Exception as e:
            self.log_debug(f"  ❌ Weapon pattern integration failed: {e}")
            self.test_results['weapon_pattern_integration'] = False
            return False
    
    def test_attack_delivery_with_weapon_patterns(self) -> bool:
        """Test 3: Attack delivery using weapon patterns."""
        self.log_debug("🔍 TEST 3: Attack Delivery with Weapon Patterns")
        
        try:
            # Clear the grid
            for y in range(self.engine.grid_height):
                for x in range(self.engine.grid_width):
                    self.engine.puzzle_grid[y][x] = 'empty'
            
            # Create attack plans using weapon patterns
            garbage_plan = self.planner.plan_garbage_delivery(
                columns=[0, 2, 4],  # Red, Blue, Green columns
                rows=[10, 10, 10],  # Bottom row
                player_key="player"
            )
            
            strike_plan = self.planner.plan_strike_delivery(
                columns=[1, 3, 5],  # Red, Blue, Green columns
                top_row=8,          # 4-block high strike
                height=4,
                player_key="player"
            )
            
            # Commit attacks
            garbage_result = self.committer.commit_garbage(self.engine, garbage_plan, "player")
            strike_result = self.committer.commit_strikes(self.engine, strike_plan, "player")
            
            self.log_debug(f"  📊 Placed {garbage_result.blocks_placed} garbage blocks")
            self.log_debug(f"  📊 Placed {strike_result.blocks_placed} strike blocks")
            
            # Verify block types and colors
            expected_garbage = ["red_garbage", "blue_garbage", "green_garbage"]
            expected_strikes = ["red_strike", "blue_strike", "green_strike"]
            
            # Check garbage blocks
            garbage_found = []
            for col in [0, 2, 4]:
                block = self.engine.puzzle_grid[10][col]
                if block and '_garbage' in block:
                    garbage_found.append(block)
            
            if len(garbage_found) == 3:
                self.log_debug(f"  ✅ Found garbage blocks: {garbage_found}")
            else:
                self.log_debug(f"  ❌ Expected 3 garbage blocks, found {len(garbage_found)}")
                return False
            
            # Check strike blocks
            strike_found = []
            for col in [1, 3, 5]:
                for row in range(8, 12):
                    block = self.engine.puzzle_grid[row][col]
                    if block and '_strike' in block:
                        strike_found.append(block)
            
            if len(strike_found) >= 12:  # 4 blocks per column * 3 columns
                self.log_debug(f"  ✅ Found {len(strike_found)} strike blocks")
            else:
                self.log_debug(f"  ❌ Expected at least 12 strike blocks, found {len(strike_found)}")
                return False
            
            self.test_results['attack_delivery_patterns'] = True
            return True
            
        except Exception as e:
            self.log_debug(f"  ❌ Attack delivery test failed: {e}")
            self.test_results['attack_delivery_patterns'] = False
            return False
    
    def test_custom_weapon_patterns(self) -> bool:
        """Test 4: Custom weapon patterns with different color distributions."""
        self.log_debug("🔍 TEST 4: Custom Weapon Patterns")
        
        try:
            # Create custom weapon with different pattern
            custom_pattern = WeaponPattern(
                column_to_color={
                    0: "yellow", 1: "yellow",  # Left: yellow
                    2: "red", 3: "red",        # Center: red
                    4: "blue", 5: "blue",      # Right: blue
                },
                grid_height=12
            )
            
            custom_weapon = Weapon(
                name="Custom Test Weapon",
                pattern=custom_pattern,
                description="Test weapon for pattern validation"
            )
            
            # Equip custom weapon
            self.item_system.equip_weapon(custom_weapon)
            
            # Test custom pattern
            expected_mapping = {
                0: "yellow", 1: "yellow",
                2: "red", 3: "red",
                4: "blue", 5: "blue",
            }
            
            all_passed = True
            for column, expected_color in expected_mapping.items():
                actual_color = self.item_system.get_attack_color_for_column(column)
                if actual_color == expected_color:
                    self.log_debug(f"  ✅ Custom pattern column {column}: {actual_color}")
                else:
                    self.log_debug(f"  ❌ Custom pattern column {column}: expected {expected_color}, got {actual_color}")
                    all_passed = False
            
            # Test attack delivery with custom pattern
            garbage_plan = self.planner.plan_garbage_delivery(
                columns=[0, 2, 4],
                rows=[10, 10, 10],
                player_key="player"
            )
            
            # Verify custom colors
            expected_custom_colors = ["yellow", "red", "blue"]
            for i, block in enumerate(garbage_plan.garbage_blocks):
                expected_color = expected_custom_colors[i]
                if block.color == expected_color:
                    self.log_debug(f"  ✅ Custom garbage block {i}: {block.color}")
                else:
                    self.log_debug(f"  ❌ Custom garbage block {i}: expected {expected_color}, got {block.color}")
                    all_passed = False
            
            self.test_results['custom_weapon_patterns'] = all_passed
            return all_passed
            
        except Exception as e:
            self.log_debug(f"  ❌ Custom weapon patterns test failed: {e}")
            self.test_results['custom_weapon_patterns'] = False
            return False
    
    def test_weapon_fallback_behavior(self) -> bool:
        """Test 5: Weapon fallback behavior when no weapon is equipped."""
        self.log_debug("🔍 TEST 5: Weapon Fallback Behavior")
        
        try:
            # Unequip weapon
            self.item_system._equipped_weapon = None
            
            # Test fallback color generation
            test_columns = [0, 1, 2, 3, 4, 5]
            valid_colors = ["red", "blue", "green", "yellow"]
            
            all_passed = True
            for column in test_columns:
                color = self.item_system.get_attack_color_for_column(column)
                if color in valid_colors:
                    self.log_debug(f"  ✅ Fallback color column {column}: {color}")
                else:
                    self.log_debug(f"  ❌ Fallback color column {column}: invalid color {color}")
                    all_passed = False
            
            # Test fallback strike colors
            test_cells = [(0, 0, 12), (2, 5, 12), (4, 11, 12)]
            for col, row, height in test_cells:
                color = self.item_system.get_strike_color_for_cell(col, row, height)
                if color in valid_colors:
                    self.log_debug(f"  ✅ Fallback strike color cell ({col}, {row}): {color}")
                else:
                    self.log_debug(f"  ❌ Fallback strike color cell ({col}, {row}): invalid color {color}")
                    all_passed = False
            
            # Re-equip default weapon for other tests
            self.item_system.equip_weapon(create_rusted_sword())
            
            self.test_results['weapon_fallback_behavior'] = all_passed
            return all_passed
            
        except Exception as e:
            self.log_debug(f"  ❌ Weapon fallback test failed: {e}")
            self.test_results['weapon_fallback_behavior'] = False
            return False
    
    def test_6x12_grid_boundary_validation(self) -> bool:
        """Test 6: 6x12 grid boundary validation and edge cases."""
        self.log_debug("🔍 TEST 6: 6x12 Grid Boundary Validation")
        
        try:
            # Test boundary conditions
            boundary_tests = [
                (0, 0, 12),    # Top-left
                (5, 0, 12),    # Top-right
                (0, 11, 12),   # Bottom-left
                (5, 11, 12),   # Bottom-right
                (2, 5, 12),    # Center
            ]
            
            all_passed = True
            for col, row, height in boundary_tests:
                try:
                    color = self.item_system.get_strike_color_for_cell(col, row, height)
                    if color in ["red", "blue", "green", "yellow"]:
                        self.log_debug(f"  ✅ Boundary cell ({col}, {row}): {color}")
                    else:
                        self.log_debug(f"  ❌ Boundary cell ({col}, {row}): invalid color {color}")
                        all_passed = False
                except Exception as e:
                    self.log_debug(f"  ❌ Boundary cell ({col}, {row}) failed: {e}")
                    all_passed = False
            
            # Test invalid column/row combinations
            invalid_tests = [
                (-1, 0, 12),   # Negative column
                (6, 0, 12),    # Column out of bounds
                (0, -1, 12),   # Negative row
                (0, 12, 12),   # Row out of bounds
            ]
            
            for col, row, height in invalid_tests:
                try:
                    color = self.item_system.get_strike_color_for_cell(col, row, height)
                    self.log_debug(f"  ⚠️ Invalid cell ({col}, {row}) returned: {color}")
                    # This might be acceptable if the system handles invalid inputs gracefully
                except Exception as e:
                    self.log_debug(f"  ✅ Invalid cell ({col}, {row}) properly rejected: {e}")
            
            self.test_results['grid_boundary_validation'] = all_passed
            return all_passed
            
        except Exception as e:
            self.log_debug(f"  ❌ Grid boundary validation failed: {e}")
            self.test_results['grid_boundary_validation'] = False
            return False
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Run all weapon integration tests."""
        self.log_debug("🚀 Starting Weapon Integration Test Suite")
        self.log_debug("=" * 60)
        
        tests = [
            ("6x12 Grid Pattern Validation", self.test_6x12_grid_pattern_validation),
            ("Weapon Pattern Integration", self.test_weapon_pattern_integration),
            ("Attack Delivery with Weapon Patterns", self.test_attack_delivery_with_weapon_patterns),
            ("Custom Weapon Patterns", self.test_custom_weapon_patterns),
            ("Weapon Fallback Behavior", self.test_weapon_fallback_behavior),
            ("6x12 Grid Boundary Validation", self.test_6x12_grid_boundary_validation),
        ]
        
        for test_name, test_func in tests:
            self.log_debug(f"\n🎯 Running: {test_name}")
            try:
                result = test_func()
                status = "✅ PASS" if result else "❌ FAIL"
                self.log_debug(f"{status} {test_name}")
            except Exception as e:
                self.log_debug(f"❌ ERROR {test_name}: {e}")
                self.test_results[test_name.lower().replace(" ", "_")] = False
        
        # Summary
        self.log_debug("\n" + "=" * 60)
        self.log_debug("📊 WEAPON INTEGRATION TEST SUMMARY")
        self.log_debug("=" * 60)
        
        passed = sum(1 for result in self.test_results.values() if result)
        total = len(self.test_results)
        
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            self.log_debug(f"  {status} {test_name}")
        
        self.log_debug(f"\n🎯 Overall Result: {passed}/{total} tests passed")
        
        if passed == total:
            self.log_debug("🎉 All weapon integration tests passed!")
        else:
            self.log_debug("⚠️ Some tests failed. Check the debug log above.")
        
        return self.test_results

def main():
    """Main function to run the weapon integration tests."""
    print("🚀 Starting Weapon Integration Test Suite")
    
    try:
        test_suite = WeaponIntegrationTest()
        results = test_suite.run_all_tests()
        
        # Save debug log
        with open("weapon_integration_debug.log", "w") as f:
            for log_entry in test_suite.debug_log:
                f.write(log_entry + "\n")
        
        print(f"\n📝 Debug log saved to: weapon_integration_debug.log")
        
        return all(results.values())
        
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
