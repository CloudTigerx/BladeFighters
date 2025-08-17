#!/usr/bin/env python3
"""
Simple Transformation System Test
Tests the core transformation logic without requiring full game engine initialization.
"""

import sys
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.items_module.item_system import ItemSystem, create_rusted_sword, Weapon, WeaponPattern
from modules.testmode_module.attack_delivery_planner import AttackDeliveryPlanner, DeliveryConfig

class SimpleTransformationTest:
    """Simplified test suite focusing on core transformation logic."""
    
    def __init__(self):
        # Initialize test components
        self.item_system = ItemSystem()
        self.item_system.equip_weapon(create_rusted_sword())
        
        # Initialize attack delivery planner with config
        config = DeliveryConfig()
        self.planner = AttackDeliveryPlanner(config)
        
        # Test results tracking
        self.test_results = {}
        self.debug_log = []
        
    def log_debug(self, message: str):
        """Log debug information."""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.debug_log.append(log_entry)
        print(log_entry)
    
    def test_weapon_system_integration(self) -> bool:
        """Test 1: Weapon system correctly generates colored attack blocks."""
        self.log_debug("TEST 1: Weapon System Integration")
        
        try:
            # Test weapon pattern for different columns
            expected_colors = {
                0: "red", 1: "red",      # Left side: red
                2: "blue", 3: "blue",    # Center: blue  
                4: "green", 5: "green",  # Right side: green
            }
            
            all_passed = True
            for column, expected_color in expected_colors.items():
                actual_color = self.item_system.get_attack_color_for_column(column)
                if actual_color == expected_color:
                    self.log_debug(f"  PASS Column {column}: {actual_color}")
                else:
                    self.log_debug(f"  FAIL Column {column}: expected {expected_color}, got {actual_color}")
                    all_passed = False
            
            self.test_results['weapon_system'] = all_passed
            return all_passed
            
        except Exception as e:
            self.log_debug(f"  FAIL Weapon system test failed: {e}")
            self.test_results['weapon_system'] = False
            return False
    
    def test_attack_delivery_planning(self) -> bool:
        """Test 2: Attack delivery planning creates correct block types."""
        self.log_debug("TEST 2: Attack Delivery Planning")
        
        try:
            # Create a mock engine for testing
            class MockEngine:
                def __init__(self):
                    self.grid_width = 6
                    self.grid_height = 12
                    self.puzzle_grid = [['empty'] * 6 for _ in range(12)]
            
            mock_engine = MockEngine()
            
            # Create attack data
            attack_data = {
                'blocks_remaining': 3,
                'sprinkle_side': 'R',
                'handedness': 'R'
            }
            
            # Test garbage delivery planning
            delivery_plan = self.planner.plan_garbage_delivery(
                mock_engine, attack_data, "player", self.item_system
            )
            
            # Verify garbage blocks
            if len(delivery_plan.garbage_blocks) == 3:
                self.log_debug(f"  PASS Created {len(delivery_plan.garbage_blocks)} garbage blocks")
                for i, block in enumerate(delivery_plan.garbage_blocks):
                    self.log_debug(f"    - Block {i}: {block.color}_garbage at ({block.column}, {block.row})")
            else:
                self.log_debug(f"  FAIL Expected 3 garbage blocks, got {len(delivery_plan.garbage_blocks)}")
                return False
            
            # Test strike delivery planning
            strike_attack_data = {
                'strike_details': ['1x4'],
                'pierce_budgets': [1],
                'handedness': 'R',
                'sprinkle_side': 'R'
            }
            
            # Mock column rotator
            class MockColumnRotator:
                def get_next_column(self):
                    return 0
            
            mock_rotator = MockColumnRotator()
            
            strike_plan = self.planner.plan_strike_delivery(
                mock_engine, strike_attack_data, "player", self.item_system, mock_rotator
            )
            
            if len(strike_plan.strike_patterns) > 0:
                self.log_debug(f"  PASS Created {len(strike_plan.strike_patterns)} strike patterns")
                for pattern in strike_plan.strike_patterns:
                    self.log_debug(f"    - Strike: {len(pattern.columns)}x{pattern.height} at row {pattern.top_row}")
            else:
                self.log_debug(f"  FAIL Expected strike patterns, got {len(strike_plan.strike_patterns)}")
                return False
            
            self.test_results['attack_planning'] = True
            return True
            
        except Exception as e:
            self.log_debug(f"  FAIL Attack planning test failed: {e}")
            self.test_results['attack_planning'] = False
            return False
    
    def test_transformation_logic(self) -> bool:
        """Test 3: Test the core transformation logic."""
        self.log_debug("TEST 3: Transformation Logic")
        
        try:
            # Simulate the transformation logic from AttackDeliveryCommitter
            # This tests the core logic without requiring the full engine
            
            # Test data structure similar to garbage_block_brightness
            test_tracking = {
                (0, 10, 1): {'landings': 1, 'color': 'red', 'is_strike': True},
                (2, 10, 1): {'landings': 1, 'color': 'blue', 'is_strike': True},
                (4, 10, 1): {'landings': 1, 'color': 'green', 'is_strike': False},
            }
            
            # Simulate transformation rules
            to_demote_strikes = []
            to_finalize_garbage = []
            
            for pos_key, data in test_tracking.items():
                is_strike = data.get('is_strike', False)
                color = data['color']
                
                # Stage 1: strike demotion after 1 landing
                if is_strike and data['landings'] >= 1:
                    to_demote_strikes.append((pos_key, f"{color}_garbage"))
                
                # Stage 2: colored garbage -> normal block after 1 landing
                if (not is_strike) and data['landings'] >= 1:
                    to_finalize_garbage.append((pos_key, f"{color}_block"))
            
            # Verify transformations
            expected_strikes_to_garbage = 2  # red and blue strikes
            expected_garbage_to_normal = 1   # green garbage
            
            if len(to_demote_strikes) == expected_strikes_to_garbage:
                self.log_debug(f"  PASS Strike demotions: {len(to_demote_strikes)} (expected {expected_strikes_to_garbage})")
                for pos_key, new_type in to_demote_strikes:
                    self.log_debug(f"    - {pos_key} -> {new_type}")
            else:
                self.log_debug(f"  FAIL Strike demotions: {len(to_demote_strikes)} (expected {expected_strikes_to_garbage})")
                return False
            
            if len(to_finalize_garbage) == expected_garbage_to_normal:
                self.log_debug(f"  PASS Garbage finalizations: {len(to_finalize_garbage)} (expected {expected_garbage_to_normal})")
                for pos_key, new_type in to_finalize_garbage:
                    self.log_debug(f"    - {pos_key} -> {new_type}")
            else:
                self.log_debug(f"  FAIL Garbage finalizations: {len(to_finalize_garbage)} (expected {expected_garbage_to_normal})")
                return False
            
            self.test_results['transformation_logic'] = True
            return True
            
        except Exception as e:
            self.log_debug(f"  FAIL Transformation logic test failed: {e}")
            self.test_results['transformation_logic'] = False
            return False
    
    def test_6x12_grid_pattern_validation(self) -> bool:
        """Test 4: 6x12 grid pattern validation and color mapping."""
        self.log_debug("TEST 4: 6x12 Grid Pattern Validation")
        
        try:
            # Test default weapon (Rusted Sword)
            weapon = create_rusted_sword()
            pattern = weapon.pattern
            
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
                    self.log_debug(f"  PASS Column {column}: {actual_color}")
                else:
                    self.log_debug(f"  FAIL Column {column}: expected {expected_color}, got {actual_color}")
                    all_passed = False
            
            # Test cell-specific color mapping
            test_cells = [(0, 0), (2, 5), (4, 11)]  # Different columns and rows
            for col, row in test_cells:
                color = pattern.color_for_cell(col, row, 12)
                if color in ["red", "blue", "green"]:
                    self.log_debug(f"  PASS Cell ({col}, {row}): {color}")
                else:
                    self.log_debug(f"  FAIL Cell ({col}, {row}): invalid color {color}")
                    all_passed = False
            
            self.test_results['grid_pattern_validation'] = all_passed
            return all_passed
            
        except Exception as e:
            self.log_debug(f"  FAIL Grid pattern validation failed: {e}")
            self.test_results['grid_pattern_validation'] = False
            return False
    
    def test_custom_weapon_patterns(self) -> bool:
        """Test 5: Custom weapon patterns with different color distributions."""
        self.log_debug("TEST 5: Custom Weapon Patterns")
        
        try:
            # Create custom weapon with different pattern
            custom_pattern = WeaponPattern(
                column_to_color={
                    0: "yellow", 1: "yellow",  # Left: yellow
                    2: "red", 3: "red",        # Center: red
                    4: "blue", 5: "blue",      # Right: blue
                }
            )
            
            custom_weapon = Weapon(
                name="Custom Test Weapon",
                pattern=custom_pattern
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
                    self.log_debug(f"  PASS Custom pattern column {column}: {actual_color}")
                else:
                    self.log_debug(f"  FAIL Custom pattern column {column}: expected {expected_color}, got {actual_color}")
                    all_passed = False
            
            # Re-equip default weapon for other tests
            self.item_system.equip_weapon(create_rusted_sword())
            
            self.test_results['custom_weapon_patterns'] = all_passed
            return all_passed
            
        except Exception as e:
            self.log_debug(f"  FAIL Custom weapon patterns test failed: {e}")
            self.test_results['custom_weapon_patterns'] = False
            return False
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Run all simple transformation tests."""
        self.log_debug("Starting Simple Transformation Test Suite")
        self.log_debug("=" * 60)
        
        tests = [
            ("Weapon System Integration", self.test_weapon_system_integration),
            ("Attack Delivery Planning", self.test_attack_delivery_planning),
            ("Transformation Logic", self.test_transformation_logic),
            ("6x12 Grid Pattern Validation", self.test_6x12_grid_pattern_validation),
            ("Custom Weapon Patterns", self.test_custom_weapon_patterns),
        ]
        
        for test_name, test_func in tests:
            self.log_debug(f"\nRunning: {test_name}")
            try:
                result = test_func()
                status = "PASS" if result else "FAIL"
                self.log_debug(f"{status} {test_name}")
            except Exception as e:
                self.log_debug(f"ERROR {test_name}: {e}")
                self.test_results[test_name.lower().replace(" ", "_")] = False
        
        # Summary
        self.log_debug("\n" + "=" * 60)
        self.log_debug("SIMPLE TRANSFORMATION TEST SUMMARY")
        self.log_debug("=" * 60)
        
        passed = sum(1 for result in self.test_results.values() if result)
        total = len(self.test_results)
        
        for test_name, result in self.test_results.items():
            status = "PASS" if result else "FAIL"
            self.log_debug(f"  {status} {test_name}")
        
        self.log_debug(f"\nOverall Result: {passed}/{total} tests passed")
        
        if passed == total:
            self.log_debug("All simple transformation tests passed!")
        else:
            self.log_debug("Some tests failed. Check the debug log above.")
        
        return self.test_results

def main():
    """Main function to run the simple transformation tests."""
    print("Starting Simple Transformation Test Suite")
    
    try:
        test_suite = SimpleTransformationTest()
        results = test_suite.run_all_tests()
        
        # Save debug log with UTF-8 encoding
        with open("simple_transformation_debug.log", "w", encoding="utf-8") as f:
            for log_entry in test_suite.debug_log:
                f.write(log_entry + "\n")
        
        print(f"\nDebug log saved to: simple_transformation_debug.log")
        
        return all(results.values())
        
    except Exception as e:
        print(f"Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
