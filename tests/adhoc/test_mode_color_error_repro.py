#!/usr/bin/env python3
"""
Test Mode Color Error Reproduction Test
Attempts to reproduce the "invalid color argument" error when transitioning from inventory to test mode.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import pygame
import time
from modules.game_state_module.game_state_manager import GameStateManager
from modules.items_module.item_system import create_weapon_by_name
from modules.testmode_module.test_mode import TestModeRefactored

def test_inventory_to_testmode_transition():
    """Test the exact scenario that causes the color error."""
    print("🔍 Testing Inventory to Test Mode Transition...")
    
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((1200, 800))
    font = pygame.font.Font(None, 36)
    
    try:
        # Step 1: Create game state manager
        print("  📋 Step 1: Creating game state manager")
        game_state_manager = GameStateManager()
        
        # Step 2: Add weapons to inventory
        print("  📋 Step 2: Adding weapons to inventory")
        player_items = game_state_manager.get_player_items()
        test_weapons = ["Rusted Sword", "Ember Blade", "Azure Rapier", "Crimson Divider"]
        
        for weapon_name in test_weapons:
            player_items.add_weapon(weapon_name)
            print(f"    Added: {weapon_name}")
        
        # Step 3: Equip a weapon (this triggers notifications)
        print("  📋 Step 3: Equipping weapon")
        weapon = create_weapon_by_name("Ember Blade")
        if weapon:
            player_items.equip_weapon(weapon)
            print(f"    ✅ Equipped: {weapon.name}")
        else:
            print(f"    ❌ Failed to create weapon")
            return False
        
        # Step 4: Create test mode (this is where the error occurs)
        print("  📋 Step 4: Creating test mode")
        try:
            test_mode = TestModeRefactored(screen, font, None, "puzzleassets")
            print("    ✅ TestMode created successfully")
        except Exception as e:
            print(f"    ❌ Error creating TestMode: {e}")
            return False
        
        # Step 5: Initialize test mode components
        print("  📋 Step 5: Initializing test mode components")
        try:
            # Get the board manager
            board_manager = test_mode.board_manager
            print("    ✅ Board manager accessed")
            
            # Get the render coordinator
            render_coordinator = test_mode.render_coordinator
            print("    ✅ Render coordinator accessed")
            
            # Get the engines
            player_engine, enemy_engine = board_manager.get_engines()
            print("    ✅ Engines accessed")
            
            # Get the renderers
            player_renderer, enemy_renderer = board_manager.get_renderers()
            print("    ✅ Renderers accessed")
            
        except Exception as e:
            print(f"    ❌ Error accessing components: {e}")
            return False
        
        # Step 6: Test rendering (this is where color errors often occur)
        print("  📋 Step 6: Testing rendering")
        try:
            # Clear screen
            screen.fill((30, 20, 20))
            
            # Test board rendering
            render_coordinator.draw_boards()
            print("    ✅ Board rendering completed")
            
            # Test a few frames
            for i in range(5):
                screen.fill((30, 20, 20))
                render_coordinator.draw_boards()
                pygame.display.flip()
                time.sleep(0.1)
                print(f"    ✅ Frame {i+1} rendered")
            
        except Exception as e:
            print(f"    ❌ Error during rendering: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        print("  ✅ All tests passed!")
        return True
        
    except Exception as e:
        print(f"  ❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        pygame.quit()

def test_weapon_pattern_colors():
    """Test weapon pattern color generation specifically."""
    print("🎨 Testing Weapon Pattern Colors...")
    
    test_weapons = ["Rusted Sword", "Ember Blade", "Azure Rapier", "Crimson Divider"]
    
    for weapon_name in test_weapons:
        print(f"  📋 Testing {weapon_name}")
        try:
            weapon = create_weapon_by_name(weapon_name)
            if not weapon:
                print(f"    ❌ Failed to create weapon: {weapon_name}")
                continue
            
            pattern = weapon.pattern
            
            # Test column colors
            for col in range(6):
                color = pattern.color_for_column(col)
                print(f"    Column {col}: {color}")
                
                # Test cell colors
                for row in range(12):
                    cell_color = pattern.color_for_cell(col, row, 12)
                    if not cell_color or not isinstance(cell_color, str):
                        print(f"    ❌ Invalid cell color at ({col}, {row}): {cell_color}")
                        return False
            
            print(f"    ✅ {weapon_name}: All colors valid")
            
        except Exception as e:
            print(f"    ❌ Error testing {weapon_name}: {e}")
            return False
    
    print("  ✅ All weapon pattern tests passed!")
    return True

def test_pygame_color_handling():
    """Test pygame color handling directly."""
    print("🎮 Testing Pygame Color Handling...")
    
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    
    try:
        # Test various color formats
        test_colors = [
            (255, 0, 0),      # Red
            (0, 255, 0),      # Green
            (0, 0, 255),      # Blue
            (255, 255, 0),    # Yellow
            (255, 255, 255),  # White
            (0, 0, 0),        # Black
        ]
        
        for color in test_colors:
            try:
                # Test pygame.draw.rect with this color
                rect = pygame.Rect(100, 100, 50, 50)
                pygame.draw.rect(screen, color, rect)
                print(f"    ✅ Color {color}: pygame.draw.rect works")
            except Exception as e:
                print(f"    ❌ Color {color}: pygame.draw.rect failed - {e}")
                return False
        
        # Test invalid colors that should be caught
        invalid_colors = [
            (255, 0, 0, 128),  # RGBA (should fail)
            None,               # None
            "red",              # String
            [255, 0, 0],       # List
        ]
        
        for color in invalid_colors:
            try:
                rect = pygame.Rect(200, 200, 50, 50)
                pygame.draw.rect(screen, color, rect)
                print(f"    ⚠️ Invalid color {color}: should have failed but didn't")
            except Exception as e:
                print(f"    ✅ Invalid color {color}: correctly failed - {e}")
        
        print("  ✅ All pygame color tests passed!")
        return True
        
    except Exception as e:
        print(f"  ❌ Error in pygame color tests: {e}")
        return False
        
    finally:
        pygame.quit()

def main():
    """Run all tests."""
    print("🔍 TEST MODE COLOR ERROR REPRODUCTION TEST")
    print("=" * 60)
    
    tests = [
        test_weapon_pattern_colors,
        test_pygame_color_handling,
        test_inventory_to_testmode_transition
    ]
    
    all_passed = True
    for test in tests:
        print()
        if not test():
            all_passed = False
        print()
    
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("✅ No color errors detected")
        print("✅ Test mode transition works correctly")
    else:
        print("❌ SOME TESTS FAILED!")
        print("❌ Color errors detected - investigation needed")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


