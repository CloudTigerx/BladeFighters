#!/usr/bin/env python3
"""
Game flow test to catch real transformation and cluster issues.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pygame

def main():
    """Test the actual game flow."""
    print("🎮 GAME FLOW TEST - Catching Real Issues")
    print("="*50)
    
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    font = pygame.font.Font(None, 36)
    
    try:
        from modules.testmode_module.test_mode import TestModeRefactored
        from modules.items_module.item_system import create_rusted_sword
        
        # Create test mode
        test_mode = TestModeRefactored(screen, font, None, "puzzleassets")
        
        # Get enemy engine
        engine = test_mode.enemy_engine
        grid = engine.puzzle_grid
        
        print("✅ TestMode initialized")
        
        # Test 1: Simulate actual attack delivery
        print("\n🧪 Test 1: Attack delivery simulation")
        
        # Create weapon and equip it
        weapon = create_rusted_sword()
        enemy_items = test_mode.get_enemy_items()
        enemy_items.equip_weapon(weapon)
        
        # Queue an attack that creates garbage blocks
        test_mode.queue_attack_spawn('enemy', 'garbage_blocks', 3)
        
        # Update the game to process the attack
        for i in range(15):  # Update more frames to ensure attack processing
            test_mode.update()
            if i % 5 == 0:
                print(f"  🔄 Update frame {i}")
        
        # Check what blocks were actually placed
        print("\n📊 Checking placed blocks:")
        garbage_blocks = 0
        strike_blocks = 0
        normal_blocks = 0
        untracked_blocks = 0
        
        for y in range(len(grid)):
            for x in range(len(grid[0])):
                cell = grid[y][x]
                if cell:
                    if '_garbage' in str(cell):
                        garbage_blocks += 1
                        # Check if this block is tracked
                        pos_key = (x, y, 2)  # enemy player_id = 2
                        if pos_key in test_mode.garbage_block_brightness:
                            tracking = test_mode.garbage_block_brightness[pos_key]
                            print(f"  ✅ Garbage at ({x}, {y}): {cell} - tracked: {tracking}")
                        else:
                            print(f"  ❌ Garbage at ({x}, {y}): {cell} - NOT TRACKED!")
                            untracked_blocks += 1
                    elif '_strike' in str(cell):
                        strike_blocks += 1
                        # Check if this block is tracked
                        pos_key = (x, y, 2)
                        if pos_key in test_mode.garbage_block_brightness:
                            tracking = test_mode.garbage_block_brightness[pos_key]
                            print(f"  ✅ Strike at ({x}, {y}): {cell} - tracked: {tracking}")
                        else:
                            print(f"  ❌ Strike at ({x}, {y}): {cell} - NOT TRACKED!")
                            untracked_blocks += 1
                    elif '_block' in str(cell):
                        normal_blocks += 1
        
        print(f"  📊 Summary: {garbage_blocks} garbage, {strike_blocks} strikes, {normal_blocks} normal, {untracked_blocks} untracked")
        
        # Test 2: Simulate piece landing and check transformations
        print("\n🧪 Test 2: Piece landing simulation")
        
        # Simulate multiple piece landings
        for landing in range(3):
            print(f"  🔄 Landing {landing + 1}")
            test_mode._on_piece_landed(2)
            
            # Check transformations
            transformed_count = 0
            for y in range(len(grid)):
                for x in range(len(grid[0])):
                    cell = grid[y][x]
                    if cell and '_garbage' in str(cell):
                        pos_key = (x, y, 2)
                        if pos_key in test_mode.garbage_block_brightness:
                            tracking = test_mode.garbage_block_brightness[pos_key]
                            print(f"    📍 ({x}, {y}): {cell} - landings: {tracking['landings']}")
                        else:
                            print(f"    ❌ ({x}, {y}): {cell} - NOT TRACKED!")
            
            # Update a few frames
            for _ in range(5):
                test_mode.update()
        
        # Test 3: Check cluster detection with garbage blocks
        print("\n🧪 Test 3: Cluster detection with garbage")
        
        # Create a mixed cluster scenario
        # Place normal blocks in a cluster pattern
        cluster_positions = [(1, 8), (2, 8), (1, 9), (2, 9)]
        for x, y in cluster_positions:
            if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
                grid[y][x] = 'green_block'
        
        # Place garbage blocks nearby
        garbage_positions = [(0, 8), (3, 8), (1, 7), (2, 7)]
        for x, y in garbage_positions:
            if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
                grid[y][x] = 'red_garbage'
                # Ensure tracking
                pos_key = (x, y, 2)
                if pos_key not in test_mode.garbage_block_brightness:
                    test_mode.garbage_block_brightness[pos_key] = {
                        'landings': 0,
                        'color': 'red',
                        'is_strike': False
                    }
        
        # Check cluster detection
        clusters = engine.find_rectangular_clusters_for_render()
        print(f"  📊 Found {len(clusters)} clusters")
        
        for i, cluster in enumerate(clusters):
            print(f"  📊 Cluster {i}: {len(cluster)} blocks")
            garbage_in_cluster = 0
            for x, y in cluster:
                if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
                    cell = grid[y][x]
                    if cell and '_garbage' in str(cell):
                        garbage_in_cluster += 1
                        print(f"    ❌ Garbage in cluster at ({x}, {y}): {cell}")
                    else:
                        print(f"    ✅ Normal block at ({x}, {y}): {cell}")
            
            if garbage_in_cluster > 0:
                print(f"    ⚠️  WARNING: Cluster {i} contains {garbage_in_cluster} garbage blocks!")
        
        # Test 4: Check cluster glow colors
        print("\n🧪 Test 4: Cluster glow colors")
        renderer = test_mode.enemy_renderer
        renderer.update_visual_state()
        
        glow_effects = renderer.cluster_glow_effects
        print(f"  📊 Found {len(glow_effects)} cluster glow effects")
        
        white_glows = 0
        for cluster_id, glow_data in glow_effects.items():
            color = glow_data['color']
            blocks = glow_data['blocks']
            print(f"  📊 Glow {cluster_id}: color={color}, blocks={len(blocks)}")
            
            # Check for white/silver glows
            if color == (255, 255, 255) or color == (128, 128, 128):
                white_glows += 1
                print(f"    ❌ WHITE/SILVER GLOW DETECTED: {color}")
            
            # Check if any blocks in glow are garbage/strike
            for x, y in blocks:
                if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
                    cell = grid[y][x]
                    if cell and ('_garbage' in str(cell) or '_strike' in str(cell)):
                        print(f"    ❌ Glow contains attack block at ({x}, {y}): {cell}")
        
        # Test 5: Check for any dark blue blocks (old grey blocks)
        print("\n🧪 Test 5: Dark blue block detection")
        
        dark_blue_blocks = []
        for y in range(len(grid)):
            for x in range(len(grid[0])):
                cell = grid[y][x]
                if cell:
                    color = renderer._get_block_color((x, y))
                    if color == (0, 0, 255):  # Pure blue
                        dark_blue_blocks.append((x, y, cell, color))
        
        print(f"  📊 Found {len(dark_blue_blocks)} dark blue blocks:")
        for x, y, cell, color in dark_blue_blocks:
            print(f"    📍 ({x}, {y}): {cell} -> {color}")
        
        # Summary
        print("\n" + "="*50)
        print("📊 GAME FLOW SUMMARY")
        print("="*50)
        
        issues = []
        
        # Check tracking issues
        if untracked_blocks > 0:
            issues.append(f"❌ Found {untracked_blocks} untracked attack blocks")
        else:
            print("✅ All attack blocks properly tracked")
        
        # Check cluster issues
        garbage_in_clusters = 0
        for cluster in clusters:
            for x, y in cluster:
                if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
                    cell = grid[y][x]
                    if cell and ('_garbage' in str(cell) or '_strike' in str(cell)):
                        garbage_in_clusters += 1
        
        if garbage_in_clusters > 0:
            issues.append(f"❌ Found {garbage_in_clusters} garbage blocks in clusters")
        else:
            print("✅ Clusters exclude garbage blocks")
        
        # Check glow issues
        if white_glows > 0:
            issues.append(f"❌ Found {white_glows} white/silver glows")
        else:
            print("✅ No white/silver glows found")
        
        # Check color issues
        if dark_blue_blocks:
            issues.append(f"❌ Found {len(dark_blue_blocks)} dark blue blocks")
        else:
            print("✅ No dark blue blocks found")
        
        if issues:
            print("\n⚠️  ISSUES FOUND:")
            for issue in issues:
                print(f"  {issue}")
        else:
            print("\n🎉 NO ISSUES FOUND!")
        
        return len(issues) == 0
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        pygame.quit()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
