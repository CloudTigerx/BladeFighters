#!/usr/bin/env python3
"""
Exact Error Reproduction Test
Simulates the exact user flow that causes the "invalid color argument" error.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import pygame
import time
import threading
from modules.game_state_module.game_state_manager import GameStateManager
from modules.items_module.item_system import create_weapon_by_name
from modules.testmode_module.test_mode import TestModeRefactored

def simulate_user_flow():
    """Simulate the exact user flow that causes the error."""
    print("🎮 Simulating User Flow...")
    
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((1200, 800))
    font = pygame.font.Font(None, 36)
    
    try:
        # Step 1: Create game state manager (like when game starts)
        print("  📋 Step 1: Game startup")
        game_state_manager = GameStateManager()
        
        # Step 2: Add weapons to inventory (like user clicking "Add All Curated")
        print("  📋 Step 2: Adding weapons to inventory")
        player_items = game_state_manager.get_player_items()
        
        # Add a large number of weapons to stress the system
        test_weapons = ["Rusted Sword", "Ember Blade", "Azure Rapier", "Crimson Divider", 
                       "Deep Current", "Forest Cleaver", "Verdant Wall", "Sun Spear"]
        
        for weapon_name in test_weapons:
            player_items.add_weapon(weapon_name)
        
        # Step 3: Rapidly equip different weapons (like user clicking weapons quickly)
        print("  📋 Step 3: Rapid weapon equipping")
        for i in range(10):  # Try multiple times to trigger race conditions
            weapon_name = test_weapons[i % len(test_weapons)]
            weapon = create_weapon_by_name(weapon_name)
            if weapon:
                player_items.equip_weapon(weapon)
                print(f"    Equipped: {weapon.name}")
                time.sleep(0.01)  # Small delay to simulate user clicking
        
        # Step 4: Create test mode immediately after equipping (like user going to test mode)
        print("  📋 Step 4: Creating test mode")
        test_mode = TestModeRefactored(screen, font, None, "puzzleassets")
        
        # Step 5: Immediately start rendering (like test mode starting)
        print("  📋 Step 5: Starting test mode rendering")
        
        # Simulate multiple rapid render cycles
        for frame in range(20):
            try:
                # Clear screen
                screen.fill((30, 20, 20))
                
                # Draw boards
                test_mode.render_coordinator.draw_boards()
                
                # Update display
                pygame.display.flip()
                
                # Small delay to simulate real-time rendering
                time.sleep(0.016)  # ~60fps
                
                if frame % 5 == 0:
                    print(f"    ✅ Frame {frame} rendered")
                    
            except Exception as e:
                print(f"    ❌ Error on frame {frame}: {e}")
                import traceback
                traceback.print_exc()
                return False
        
        print("  ✅ User flow simulation completed successfully!")
        return True
        
    except Exception as e:
        print(f"  ❌ Error during user flow simulation: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        pygame.quit()

def test_concurrent_access():
    """Test concurrent access to color-related functions."""
    print("🔄 Testing Concurrent Access...")
    
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    font = pygame.font.Font(None, 36)
    
    try:
        # Create test mode
        test_mode = TestModeRefactored(screen, font, None, "puzzleassets")
        
        # Get renderer
        renderer = test_mode.player_renderer
        
        # Test concurrent access to color functions
        def color_worker():
            """Worker thread that accesses color functions."""
            for i in range(100):
                try:
                    # Test _get_block_color with various positions
                    for x in range(6):
                        for y in range(12):
                            color = renderer._get_block_color((x, y))
                            if not isinstance(color, tuple) or len(color) != 3:
                                print(f"    ❌ Invalid color returned: {color}")
                                return False
                except Exception as e:
                    print(f"    ❌ Error in color worker: {e}")
                    return False
            return True
        
        # Run multiple threads
        threads = []
        results = []
        
        for i in range(3):
            thread = threading.Thread(target=lambda: results.append(color_worker()))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # Check results
        if all(results):
            print("  ✅ All concurrent color tests passed!")
            return True
        else:
            print("  ❌ Some concurrent color tests failed!")
            return False
            
    except Exception as e:
        print(f"  ❌ Error in concurrent test: {e}")
        return False
        
    finally:
        pygame.quit()

def test_color_edge_cases():
    """Test edge cases that might cause color errors."""
    print("🔍 Testing Color Edge Cases...")
    
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    font = pygame.font.Font(None, 36)
    
    try:
        # Create test mode
        test_mode = TestModeRefactored(screen, font, None, "puzzleassets")
        
        # Get renderer
        renderer = test_mode.player_renderer
        
        # Test edge cases
        edge_cases = [
            (-1, -1),    # Invalid negative coordinates
            (10, 10),    # Out of bounds coordinates
            (0, 0),      # Valid coordinates
            (5, 11),     # Edge of grid
        ]
        
        for pos in edge_cases:
            try:
                color = renderer._get_block_color(pos)
                print(f"    Position {pos}: {color}")
                
                # Verify color is valid
                if not isinstance(color, tuple) or len(color) != 3:
                    print(f"    ❌ Invalid color for position {pos}: {color}")
                    return False
                    
                # Verify color values are in valid range
                for component in color:
                    if not isinstance(component, int) or component < 0 or component > 255:
                        print(f"    ❌ Invalid color component for position {pos}: {component}")
                        return False
                        
            except Exception as e:
                print(f"    ❌ Error testing position {pos}: {e}")
                return False
        
        print("  ✅ All edge case tests passed!")
        return True
        
    except Exception as e:
        print(f"  ❌ Error in edge case test: {e}")
        return False
        
    finally:
        pygame.quit()

def main():
    """Run all tests."""
    print("🔍 EXACT ERROR REPRODUCTION TEST")
    print("=" * 50)
    
    tests = [
        test_color_edge_cases,
        test_concurrent_access,
        simulate_user_flow
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
        print("✅ Error reproduction unsuccessful - issue may be resolved")
    else:
        print("❌ SOME TESTS FAILED!")
        print("❌ Color errors detected - investigation needed")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


