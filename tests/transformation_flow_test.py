#!/usr/bin/env python3
"""
Transformation Flow End-to-End Test Suite
Tests the complete flow: Weapon System → Attack Delivery → Block Placement → Transformation
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
from modules.items_module.item_system import ItemSystem, create_rusted_sword
from modules.testmode_module.attack_delivery_committer import AttackDeliveryCommitter
from modules.testmode_module.attack_delivery_planner import AttackDeliveryPlanner
from modules.testmode_module.test_mode import TestModeRefactored
from core.puzzle_module import PuzzleEngine

class TransformationFlowTest:
    """Comprehensive test suite for the transformation flow."""
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        self.font = pygame.font.Font(None, 24)
        self.clock = pygame.time.Clock()
        
        # Initialize test components
        self.item_system = ItemSystem()
        self.item_system.equip_weapon(create_rusted_sword())
        
        # Initialize test mode and engine
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
    
    def test_weapon_system_integration(self) -> bool:
        """Test 1: Weapon system correctly generates colored attack blocks."""
        self.log_debug("🔍 TEST 1: Weapon System Integration")
        
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
                    self.log_debug(f"  ✅ Column {column}: {actual_color}")
                else:
                    self.log_debug(f"  ❌ Column {column}: expected {expected_color}, got {actual_color}")
                    all_passed = False
            
            self.test_results['weapon_system'] = all_passed
            return all_passed
            
        except Exception as e:
            self.log_debug(f"  ❌ Weapon system test failed: {e}")
            self.test_results['weapon_system'] = False
            return False
    
    def test_attack_delivery_planning(self) -> bool:
        """Test 2: Attack delivery planning creates correct block types."""
        self.log_debug("🔍 TEST 2: Attack Delivery Planning")
        
        try:
            # Create a simple attack plan
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
            
            # Verify garbage blocks
            expected_garbage_colors = ["red", "blue", "green"]
            for i, block in enumerate(garbage_plan.garbage_blocks):
                expected_color = expected_garbage_colors[i]
                if block.color == expected_color:
                    self.log_debug(f"  ✅ Garbage block {i}: {block.color}_garbage")
                else:
                    self.log_debug(f"  ❌ Garbage block {i}: expected {expected_color}, got {block.color}")
                    return False
            
            # Verify strike blocks
            expected_strike_colors = ["red", "blue", "green"]
            for pattern in strike_plan.strike_patterns:
                for col in pattern.columns:
                    color = pattern.color_map.get((col, pattern.top_row), 'unknown')
                    if color in expected_strike_colors:
                        self.log_debug(f"  ✅ Strike pattern: {color}_strike at column {col}")
                    else:
                        self.log_debug(f"  ❌ Strike pattern: unexpected color {color}")
                        return False
            
            self.test_results['attack_planning'] = True
            return True
            
        except Exception as e:
            self.log_debug(f"  ❌ Attack planning test failed: {e}")
            self.test_results['attack_planning'] = False
            return False
    
    def test_block_placement_and_tracking(self) -> bool:
        """Test 3: Block placement and tracking initialization."""
        self.log_debug("🔍 TEST 3: Block Placement and Tracking")
        
        try:
            # Clear the grid first
            for y in range(self.engine.grid_height):
                for x in range(self.engine.grid_width):
                    self.engine.puzzle_grid[y][x] = 'empty'
            
            # Create and commit a simple attack
            garbage_plan = self.planner.plan_garbage_delivery(
                columns=[0, 2, 4],
                rows=[10, 10, 10],
                player_key="player"
            )
            
            result = self.committer.commit_garbage(self.engine, garbage_plan, "player")
            
            # Verify blocks were placed
            if result.blocks_placed == 3:
                self.log_debug(f"  ✅ Placed {result.blocks_placed} garbage blocks")
            else:
                self.log_debug(f"  ❌ Expected 3 blocks, placed {result.blocks_placed}")
                return False
            
            # Verify tracking was initialized
            tracking_count = len(self.test_mode.garbage_block_brightness)
            if tracking_count == 3:
                self.log_debug(f"  ✅ Initialized tracking for {tracking_count} blocks")
            else:
                self.log_debug(f"  ❌ Expected 3 tracked blocks, got {tracking_count}")
                return False
            
            # Verify block types in grid
            expected_blocks = ["red_garbage", "blue_garbage", "green_garbage"]
            for i, expected_block in enumerate(expected_blocks):
                col = [0, 2, 4][i]
                row = 10
                actual_block = self.engine.puzzle_grid[row][col]
                if actual_block == expected_block:
                    self.log_debug(f"  ✅ Grid position ({col}, {row}): {actual_block}")
                else:
                    self.log_debug(f"  ❌ Grid position ({col}, {row}): expected {expected_block}, got {actual_block}")
                    return False
            
            self.test_results['block_placement'] = True
            return True
            
        except Exception as e:
            self.log_debug(f"  ❌ Block placement test failed: {e}")
            self.test_results['block_placement'] = False
            return False
    
    def test_strike_to_garbage_transformation(self) -> bool:
        """Test 4: Strike blocks transform to colored garbage after landing."""
        self.log_debug("🔍 TEST 4: Strike to Garbage Transformation")
        
        try:
            # Clear the grid
            for y in range(self.engine.grid_height):
                for x in range(self.engine.grid_width):
                    self.engine.puzzle_grid[y][x] = 'empty'
            
            # Place strike blocks
            strike_plan = self.planner.plan_strike_delivery(
                columns=[1, 3, 5],
                top_row=8,
                height=4,
                player_key="player"
            )
            
            result = self.committer.commit_strikes(self.engine, strike_plan, "player")
            self.log_debug(f"  📊 Placed {result.blocks_placed} strike blocks")
            
            # Verify initial state
            initial_strikes = 0
            for y in range(self.engine.grid_height):
                for x in range(self.engine.grid_width):
                    if self.engine.puzzle_grid[y][x] and '_strike' in self.engine.puzzle_grid[y][x]:
                        initial_strikes += 1
            
            self.log_debug(f"  📊 Initial strike blocks: {initial_strikes}")
            
            # Simulate piece landing (trigger transformation)
            # Use the new transformation system via piece landing callback
            if hasattr(self.engine, 'on_piece_landed') and self.engine.on_piece_landed:
                self.engine.on_piece_landed()
            else:
                # Fallback: manually trigger transformation if callback not available
                if hasattr(self.test_mode, '_on_piece_landed'):
                    self.test_mode._on_piece_landed(1)  # player_id = 1
            
            # Verify transformation
            strikes_remaining = 0
            garbage_created = 0
            for y in range(self.engine.grid_height):
                for x in range(self.engine.grid_width):
                    block = self.engine.puzzle_grid[y][x]
                    if block and '_strike' in block:
                        strikes_remaining += 1
                    elif block and '_garbage' in block:
                        garbage_created += 1
            
            self.log_debug(f"  📊 After landing: {strikes_remaining} strikes, {garbage_created} garbage")
            
            # Check transformation results
            if strikes_remaining == 0 and garbage_created > 0:
                self.log_debug(f"  ✅ Strike blocks transformed to garbage")
                self.test_results['strike_transformation'] = True
                return True
            else:
                self.log_debug(f"  ❌ Transformation failed: strikes={strikes_remaining}, garbage={garbage_created}")
                self.test_results['strike_transformation'] = False
                return False
                
        except Exception as e:
            self.log_debug(f"  ❌ Strike transformation test failed: {e}")
            self.test_results['strike_transformation'] = False
            return False
    
    def test_garbage_to_normal_transformation(self) -> bool:
        """Test 5: Colored garbage transforms to normal blocks after landing."""
        self.log_debug("🔍 TEST 5: Garbage to Normal Transformation")
        
        try:
            # Clear the grid
            for y in range(self.engine.grid_height):
                for x in range(self.engine.grid_width):
                    self.engine.puzzle_grid[y][x] = 'empty'
            
            # Place colored garbage blocks directly
            garbage_positions = [(0, 10, "red"), (2, 10, "blue"), (4, 10, "green")]
            for col, row, color in garbage_positions:
                self.engine.puzzle_grid[row][col] = f"{color}_garbage"
                # Initialize tracking
                self.test_mode.garbage_block_brightness[(col, row, 1)] = {
                    'landings': 0,
                    'color': color,
                    'is_strike': False
                }
            
            self.log_debug(f"  📊 Placed {len(garbage_positions)} colored garbage blocks")
            
            # Simulate piece landing (trigger transformation)
            # Use the new transformation system via piece landing callback
            if hasattr(self.engine, 'on_piece_landed') and self.engine.on_piece_landed:
                self.engine.on_piece_landed()
            else:
                # Fallback: manually trigger transformation if callback not available
                if hasattr(self.test_mode, '_on_piece_landed'):
                    self.test_mode._on_piece_landed(1)  # player_id = 1
            
            # Verify transformation
            garbage_remaining = 0
            normal_blocks = 0
            for y in range(self.engine.grid_height):
                for x in range(self.engine.grid_width):
                    block = self.engine.puzzle_grid[y][x]
                    if block and '_garbage' in block:
                        garbage_remaining += 1
                    elif block and '_block' in block and not '_garbage' in block:
                        normal_blocks += 1
            
            self.log_debug(f"  📊 After landing: {garbage_remaining} garbage, {normal_blocks} normal blocks")
            
            # Check transformation results
            if garbage_remaining == 0 and normal_blocks > 0:
                self.log_debug(f"  ✅ Garbage blocks transformed to normal blocks")
                self.test_results['garbage_transformation'] = True
                return True
            else:
                self.log_debug(f"  ❌ Transformation failed: garbage={garbage_remaining}, normal={normal_blocks}")
                self.test_results['garbage_transformation'] = False
                return False
                
        except Exception as e:
            self.log_debug(f"  ❌ Garbage transformation test failed: {e}")
            self.test_results['garbage_transformation'] = False
            return False
    
    def test_complete_transformation_flow(self) -> bool:
        """Test 6: Complete end-to-end transformation flow."""
        self.log_debug("🔍 TEST 6: Complete Transformation Flow")
        
        try:
            # Clear the grid
            for y in range(self.engine.grid_height):
                for x in range(self.engine.grid_width):
                    self.engine.puzzle_grid[y][x] = 'empty'
            
            # Step 1: Place strike blocks
            strike_plan = self.planner.plan_strike_delivery(
                columns=[1, 3, 5],
                top_row=8,
                height=4,
                player_key="player"
            )
            
            strike_result = self.committer.commit_strikes(self.engine, strike_plan, "player")
            self.log_debug(f"  📊 Step 1: Placed {strike_result.blocks_placed} strike blocks")
            
            # Step 2: First landing - strikes become garbage
            # Use the new transformation system via piece landing callback
            if hasattr(self.engine, 'on_piece_landed') and self.engine.on_piece_landed:
                self.engine.on_piece_landed()
            else:
                # Fallback: manually trigger transformation if callback not available
                if hasattr(self.test_mode, '_on_piece_landed'):
                    self.test_mode._on_piece_landed(1)  # player_id = 1
            
            strikes_after_first = 0
            garbage_after_first = 0
            for y in range(self.engine.grid_height):
                for x in range(self.engine.grid_width):
                    block = self.engine.puzzle_grid[y][x]
                    if block and '_strike' in block:
                        strikes_after_first += 1
                    elif block and '_garbage' in block:
                        garbage_after_first += 1
            
            self.log_debug(f"  📊 Step 2: After first landing - strikes: {strikes_after_first}, garbage: {garbage_after_first}")
            
            # Step 3: Second landing - garbage becomes normal blocks
            # Use the new transformation system via piece landing callback
            if hasattr(self.engine, 'on_piece_landed') and self.engine.on_piece_landed:
                self.engine.on_piece_landed()
            else:
                # Fallback: manually trigger transformation if callback not available
                if hasattr(self.test_mode, '_on_piece_landed'):
                    self.test_mode._on_piece_landed(1)  # player_id = 1
            
            strikes_final = 0
            garbage_final = 0
            normal_final = 0
            for y in range(self.engine.grid_height):
                for x in range(self.engine.grid_width):
                    block = self.engine.puzzle_grid[y][x]
                    if block and '_strike' in block:
                        strikes_final += 1
                    elif block and '_garbage' in block:
                        garbage_final += 1
                    elif block and '_block' in block and not '_garbage' in block:
                        normal_final += 1
            
            self.log_debug(f"  📊 Step 3: After second landing - strikes: {strikes_final}, garbage: {garbage_final}, normal: {normal_final}")
            
            # Verify complete transformation
            if strikes_final == 0 and garbage_final == 0 and normal_final > 0:
                self.log_debug(f"  ✅ Complete transformation flow successful")
                self.test_results['complete_flow'] = True
                return True
            else:
                self.log_debug(f"  ❌ Complete transformation failed")
                self.test_results['complete_flow'] = False
                return False
                
        except Exception as e:
            self.log_debug(f"  ❌ Complete flow test failed: {e}")
            self.test_results['complete_flow'] = False
            return False
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Run all transformation flow tests."""
        self.log_debug("🚀 Starting Transformation Flow Test Suite")
        self.log_debug("=" * 60)
        
        tests = [
            ("Weapon System Integration", self.test_weapon_system_integration),
            ("Attack Delivery Planning", self.test_attack_delivery_planning),
            ("Block Placement and Tracking", self.test_block_placement_and_tracking),
            ("Strike to Garbage Transformation", self.test_strike_to_garbage_transformation),
            ("Garbage to Normal Transformation", self.test_garbage_to_normal_transformation),
            ("Complete Transformation Flow", self.test_complete_transformation_flow),
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
        self.log_debug("📊 TRANSFORMATION FLOW TEST SUMMARY")
        self.log_debug("=" * 60)
        
        passed = sum(1 for result in self.test_results.values() if result)
        total = len(self.test_results)
        
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            self.log_debug(f"  {status} {test_name}")
        
        self.log_debug(f"\n🎯 Overall Result: {passed}/{total} tests passed")
        
        if passed == total:
            self.log_debug("🎉 All transformation flow tests passed!")
        else:
            self.log_debug("⚠️ Some tests failed. Check the debug log above.")
        
        return self.test_results

def main():
    """Main function to run the transformation flow tests."""
    print("🚀 Starting Transformation Flow End-to-End Test Suite")
    
    try:
        test_suite = TransformationFlowTest()
        results = test_suite.run_all_tests()
        
        # Save debug log
        with open("transformation_flow_debug.log", "w") as f:
            for log_entry in test_suite.debug_log:
                f.write(log_entry + "\n")
        
        print(f"\n📝 Debug log saved to: transformation_flow_debug.log")
        
        return all(results.values())
        
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
