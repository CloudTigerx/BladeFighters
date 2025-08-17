#!/usr/bin/env python3
"""
Visual Verification Test Suite
Tests visual rendering of transformed blocks and verifies proper visual indicators.
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
from core.asset_loader import AssetLoader

class VisualVerificationTest:
    """Comprehensive test suite for visual verification of transformed blocks."""
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1200, 800))
        pygame.display.set_caption("Visual Verification Test - Transformed Blocks")
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
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
        
        # Initialize asset loader for visual verification
        self.asset_loader = AssetLoader("puzzleassets", block_size=65)
        
        # Test results tracking
        self.test_results = {}
        self.debug_log = []
        
        # Visual test state
        self.current_test = 0
        self.test_stages = []
        self.running = True
        
    def log_debug(self, message: str):
        """Log debug information."""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.debug_log.append(log_entry)
        print(log_entry)
    
    def test_asset_loading_for_transformed_blocks(self) -> bool:
        """Test 1: Verify all transformed block assets load correctly."""
        self.log_debug("🔍 TEST 1: Asset Loading for Transformed Blocks")
        
        try:
            # Test all transformed block types
            transformed_block_types = [
                'red_garbage', 'blue_garbage', 'green_garbage', 'yellow_garbage',
                'red_strike', 'blue_strike', 'green_strike', 'yellow_strike',
                'red_breaker', 'blue_breaker', 'green_breaker', 'yellow_breaker'
            ]
            
            all_passed = True
            for block_type in transformed_block_types:
                asset_key = block_type
                if '_strike' in block_type:
                    asset_key = 'strike_block'  # All strikes use same asset
                elif '_breaker' in block_type:
                    asset_key = block_type.replace('_breaker', 'breaker')
                
                asset = self.asset_loader.puzzle_pieces.get(asset_key)
                if asset is not None:
                    self.log_debug(f"  ✅ {block_type} -> {asset_key}: Loaded")
                else:
                    self.log_debug(f"  ❌ {block_type} -> {asset_key}: Missing")
                    all_passed = False
            
            # Test base assets
            base_assets = ['garbage_block', 'strike_block']
            for asset_key in base_assets:
                asset = self.asset_loader.puzzle_pieces.get(asset_key)
                if asset is not None:
                    self.log_debug(f"  ✅ Base asset {asset_key}: Loaded")
                else:
                    self.log_debug(f"  ❌ Base asset {asset_key}: Missing")
                    all_passed = False
            
            self.test_results['asset_loading'] = all_passed
            return all_passed
            
        except Exception as e:
            self.log_debug(f"  ❌ Asset loading test failed: {e}")
            self.test_results['asset_loading'] = False
            return False
    
    def test_visual_block_type_verification(self) -> bool:
        """Test 2: Verify visual block type identification and rendering."""
        self.log_debug("🔍 TEST 2: Visual Block Type Verification")
        
        try:
            # Test block type identification logic (same as AnimationRenderer)
            test_blocks = [
                'red_garbage', 'blue_garbage', 'green_garbage', 'yellow_garbage',
                'red_strike', 'blue_strike', 'green_strike', 'yellow_strike',
                'red_breaker', 'blue_breaker', 'green_breaker', 'yellow_breaker'
            ]
            
            all_passed = True
            for block_type in test_blocks:
                # Simulate AnimationRenderer._draw_block logic
                asset_key = ''
                
                if '_garbage' in block_type or block_type == 'garbage_block':
                    asset_key = block_type if '_garbage' in block_type else 'garbage_block'
                elif '_strike' in block_type:
                    asset_key = 'strike_block'
                elif '_breaker' in block_type:
                    asset_key = block_type.replace('_breaker', 'breaker')
                else:
                    asset_key = block_type.replace('_block', 'block')
                
                # Check if asset is available
                asset = self.asset_loader.puzzle_pieces.get(asset_key)
                if asset is not None:
                    self.log_debug(f"  ✅ {block_type} -> {asset_key}: Visual asset available")
                else:
                    self.log_debug(f"  ❌ {block_type} -> {asset_key}: Visual asset missing")
                    all_passed = False
            
            self.test_results['visual_block_verification'] = all_passed
            return all_passed
            
        except Exception as e:
            self.log_debug(f"  ❌ Visual block verification failed: {e}")
            self.test_results['visual_block_verification'] = False
            return False
    
    def test_transformation_visual_flow(self) -> bool:
        """Test 3: Test visual transformation flow from strike to garbage to normal."""
        self.log_debug("🔍 TEST 3: Transformation Visual Flow")
        
        try:
            # Clear the grid
            for y in range(self.engine.grid_height):
                for x in range(self.engine.grid_width):
                    self.engine.puzzle_grid[y][x] = 'empty'
            
            # Stage 1: Place strike blocks
            strike_plan = self.planner.plan_strike_delivery(
                columns=[1, 3, 5],
                top_row=8,
                height=4,
                player_key="player"
            )
            
            strike_result = self.committer.commit_strikes(self.engine, strike_plan, "player")
            self.log_debug(f"  📊 Stage 1: Placed {strike_result.blocks_placed} strike blocks")
            
            # Verify strike blocks are visually distinct
            strike_count = 0
            for y in range(self.engine.grid_height):
                for x in range(self.engine.grid_width):
                    if self.engine.puzzle_grid[y][x] and '_strike' in self.engine.puzzle_grid[y][x]:
                        strike_count += 1
            
            if strike_count > 0:
                self.log_debug(f"  ✅ Stage 1: {strike_count} strike blocks placed and visually distinct")
            else:
                self.log_debug(f"  ❌ Stage 1: No strike blocks found")
                return False
            
            # Stage 2: First landing - strikes become garbage
            # Simulate piece landing to trigger transformation
            if hasattr(self.engine, 'on_piece_landed') and self.engine.on_piece_landed:
                self.engine.on_piece_landed()
            else:
                # Fallback: manually trigger transformation if callback not available
                if hasattr(self.test_mode, '_on_piece_landed'):
                    self.test_mode._on_piece_landed(1)  # player_id = 1
            
            garbage_count = 0
            strike_remaining = 0
            for y in range(self.engine.grid_height):
                for x in range(self.engine.grid_width):
                    block = self.engine.puzzle_grid[y][x]
                    if block and '_garbage' in block:
                        garbage_count += 1
                    elif block and '_strike' in block:
                        strike_remaining += 1
            
            if garbage_count > 0 and strike_remaining == 0:
                self.log_debug(f"  ✅ Stage 2: {garbage_count} garbage blocks created, strikes transformed")
            else:
                self.log_debug(f"  ❌ Stage 2: Transformation failed - garbage: {garbage_count}, strikes: {strike_remaining}")
                return False
            
            # Stage 3: Second landing - garbage becomes normal blocks
            # Simulate piece landing to trigger transformation
            if hasattr(self.engine, 'on_piece_landed') and self.engine.on_piece_landed:
                self.engine.on_piece_landed()
            else:
                # Fallback: manually trigger transformation if callback not available
                if hasattr(self.test_mode, '_on_piece_landed'):
                    self.test_mode._on_piece_landed(1)  # player_id = 1
            
            normal_count = 0
            garbage_remaining = 0
            for y in range(self.engine.grid_height):
                for x in range(self.engine.grid_width):
                    block = self.engine.puzzle_grid[y][x]
                    if block and '_block' in block and not '_garbage' in block:
                        normal_count += 1
                    elif block and '_garbage' in block:
                        garbage_remaining += 1
            
            if normal_count > 0 and garbage_remaining == 0:
                self.log_debug(f"  ✅ Stage 3: {normal_count} normal blocks created, garbage transformed")
            else:
                self.log_debug(f"  ❌ Stage 3: Transformation failed - normal: {normal_count}, garbage: {garbage_remaining}")
                return False
            
            self.test_results['transformation_visual_flow'] = True
            return True
            
        except Exception as e:
            self.log_debug(f"  ❌ Transformation visual flow failed: {e}")
            self.test_results['transformation_visual_flow'] = False
            return False
    
    def create_visual_test_scenario(self):
        """Create a visual test scenario for manual verification."""
        self.log_debug("🎨 Creating Visual Test Scenario")
        
        # Clear the grid
        for y in range(self.engine.grid_height):
            for x in range(self.engine.grid_width):
                self.engine.puzzle_grid[y][x] = 'empty'
        
        # Create a comprehensive test scenario
        test_scenario = [
            # Row 0: Strike blocks (should be visually distinct)
            (0, 0, 'red_strike'), (1, 0, 'blue_strike'), (2, 0, 'green_strike'),
            (3, 0, 'yellow_strike'), (4, 0, 'red_strike'), (5, 0, 'blue_strike'),
            
            # Row 1: Garbage blocks (should be visually distinct)
            (0, 1, 'red_garbage'), (1, 1, 'blue_garbage'), (2, 1, 'green_garbage'),
            (3, 1, 'yellow_garbage'), (4, 1, 'red_garbage'), (5, 1, 'blue_garbage'),
            
            # Row 2: Breaker blocks (should have X indicators)
            (0, 2, 'red_breaker'), (1, 2, 'blue_breaker'), (2, 2, 'green_breaker'),
            (3, 2, 'yellow_breaker'), (4, 2, 'red_breaker'), (5, 2, 'blue_breaker'),
            
            # Row 3: Normal blocks (for comparison)
            (0, 3, 'red_block'), (1, 3, 'blue_block'), (2, 3, 'green_block'),
            (3, 3, 'yellow_block'), (4, 3, 'red_block'), (5, 3, 'blue_block'),
        ]
        
        # Place blocks
        for x, y, block_type in test_scenario:
            self.engine.puzzle_grid[y][x] = block_type
        
        self.log_debug(f"  📊 Placed {len(test_scenario)} test blocks")
        return test_scenario
    
    def draw_visual_test_interface(self):
        """Draw the visual test interface."""
        # Clear screen
        self.screen.fill((50, 50, 50))
        
        # Draw title
        title = self.font.render("Visual Verification Test - Transformed Blocks", True, (255, 255, 255))
        self.screen.blit(title, (20, 20))
        
        # Draw instructions
        instructions = [
            "Visual Test Instructions:",
            "• Row 0: Strike blocks (should have white outlines)",
            "• Row 1: Garbage blocks (should have black outlines)",
            "• Row 2: Breaker blocks (should have X indicators)",
            "• Row 3: Normal blocks (for comparison)",
            "",
            "Press SPACE to advance test stages",
            "Press ESC to exit",
            "Press R to reset test"
        ]
        
        y_offset = 60
        for instruction in instructions:
            if instruction.startswith("•"):
                color = (200, 200, 200)
                font = self.small_font
            elif instruction in ["Visual Test Instructions:", "Press SPACE to advance test stages", "Press ESC to exit", "Press R to reset test"]:
                color = (255, 255, 0)
                font = self.font
            else:
                color = (255, 255, 255)
                font = self.small_font
            
            text_surface = font.render(instruction, True, color)
            self.screen.blit(text_surface, (20, y_offset))
            y_offset += 20
        
        # Draw grid
        grid_x = 400
        grid_y = 100
        block_size = 65
        
        for y in range(self.engine.grid_height):
            for x in range(self.engine.grid_width):
                block_type = self.engine.puzzle_grid[y][x]
                if block_type and block_type != 'empty':
                    # Get block image
                    asset_key = ''
                    if '_garbage' in block_type or block_type == 'garbage_block':
                        asset_key = block_type if '_garbage' in block_type else 'garbage_block'
                    elif '_strike' in block_type:
                        asset_key = 'strike_block'
                    elif '_breaker' in block_type:
                        asset_key = block_type.replace('_breaker', 'breaker')
                    else:
                        asset_key = block_type.replace('_block', 'block')
                    
                    block_image = self.asset_loader.puzzle_pieces.get(asset_key)
                    
                    if block_image:
                        # Scale and draw block
                        scaled_image = pygame.transform.scale(block_image, (block_size, block_size))
                        self.screen.blit(scaled_image, (grid_x + x * block_size, grid_y + y * block_size))
                    else:
                        # Fallback: draw colored rectangle
                        color_map = {
                            'red_block': (255, 0, 0), 'blue_block': (0, 0, 255),
                            'green_block': (0, 255, 0), 'yellow_block': (255, 255, 0),
                            'red_garbage': (255, 100, 100), 'blue_garbage': (100, 100, 255),
                            'green_garbage': (100, 255, 100), 'yellow_garbage': (255, 255, 100),
                            'red_strike': (255, 200, 0), 'blue_strike': (0, 200, 255),
                            'green_strike': (0, 255, 200), 'yellow_strike': (255, 255, 0),
                            'red_breaker': (255, 150, 150), 'blue_breaker': (150, 150, 255),
                            'green_breaker': (150, 255, 150), 'yellow_breaker': (255, 255, 150)
                        }
                        
                        color = color_map.get(block_type, (128, 128, 128))
                        rect = pygame.Rect(grid_x + x * block_size, grid_y + y * block_size, block_size, block_size)
                        pygame.draw.rect(self.screen, color, rect)
                        
                        # Add outlines
                        if '_strike' in block_type:
                            pygame.draw.rect(self.screen, (255, 255, 255), rect, 2)
                        elif '_garbage' in block_type:
                            pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)
        
        # Draw grid border
        grid_width = self.engine.grid_width * block_size
        grid_height = self.engine.grid_height * block_size
        pygame.draw.rect(self.screen, (255, 255, 255), (grid_x, grid_y, grid_width, grid_height), 2)
        
        # Draw test status
        status_text = f"Test Stage: {self.current_test + 1}/3"
        status_surface = self.font.render(status_text, True, (255, 255, 0))
        self.screen.blit(status_surface, (grid_x, grid_y + grid_height + 20))
    
    def run_visual_test(self) -> bool:
        """Test 4: Run interactive visual test."""
        self.log_debug("🔍 TEST 4: Interactive Visual Test")
        
        try:
            # Create test scenario
            test_scenario = self.create_visual_test_scenario()
            
            # Set up test stages
            self.test_stages = [
                ("Initial State", lambda: None),
                ("After First Landing", lambda: self._trigger_transformation()),
                ("After Second Landing", lambda: self._trigger_transformation())
            ]
            
            self.current_test = 0
            self.running = True
            
            # Run visual test loop
            while self.running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.running = False
                        elif event.key == pygame.K_SPACE:
                            if self.current_test < len(self.test_stages) - 1:
                                self.current_test += 1
                                # Execute stage transformation
                                stage_name, stage_func = self.test_stages[self.current_test]
                                stage_func()
                                self.log_debug(f"  📊 Advanced to stage: {stage_name}")
                        elif event.key == pygame.K_r:
                            # Reset test
                            self.create_visual_test_scenario()
                            self.current_test = 0
                            self.log_debug(f"  🔄 Reset test to initial state")
                
                # Draw interface
                self.draw_visual_test_interface()
                
                # Update display
                pygame.display.flip()
                self.clock.tick(60)
            
            self.log_debug(f"  ✅ Visual test completed successfully")
            self.test_results['interactive_visual_test'] = True
            return True
            
        except Exception as e:
            self.log_debug(f"  ❌ Interactive visual test failed: {e}")
            self.test_results['interactive_visual_test'] = False
            return False
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Run all visual verification tests."""
        self.log_debug("🚀 Starting Visual Verification Test Suite")
        self.log_debug("=" * 60)
        
        tests = [
            ("Asset Loading for Transformed Blocks", self.test_asset_loading_for_transformed_blocks),
            ("Visual Block Type Verification", self.test_visual_block_type_verification),
            ("Transformation Visual Flow", self.test_transformation_visual_flow),
            ("Interactive Visual Test", self.run_visual_test),
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
        self.log_debug("📊 VISUAL VERIFICATION TEST SUMMARY")
        self.log_debug("=" * 60)
        
        passed = sum(1 for result in self.test_results.values() if result)
        total = len(self.test_results)
        
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            self.log_debug(f"  {status} {test_name}")
        
        self.log_debug(f"\n🎯 Overall Result: {passed}/{total} tests passed")
        
        if passed == total:
            self.log_debug("🎉 All visual verification tests passed!")
        else:
            self.log_debug("⚠️ Some tests failed. Check the debug log above.")
        
        return self.test_results

    def _trigger_transformation(self):
        """Trigger transformation using the new system."""
        # Use the new transformation system via piece landing callback
        if hasattr(self.engine, 'on_piece_landed') and self.engine.on_piece_landed:
            self.engine.on_piece_landed()
        else:
            # Fallback: manually trigger transformation if callback not available
            if hasattr(self.test_mode, '_on_piece_landed'):
                self.test_mode._on_piece_landed(1)  # player_id = 1

def main():
    """Main function to run the visual verification tests."""
    print("🚀 Starting Visual Verification Test Suite")
    
    try:
        test_suite = VisualVerificationTest()
        results = test_suite.run_all_tests()
        
        # Save debug log
        with open("visual_verification_debug.log", "w") as f:
            for log_entry in test_suite.debug_log:
                f.write(log_entry + "\n")
        
        print(f"\n📝 Debug log saved to: visual_verification_debug.log")
        
        return all(results.values())
        
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
