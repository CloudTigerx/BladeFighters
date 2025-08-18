#!/usr/bin/env python3
"""
Diagnostic test to identify transformation and color issues.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pygame

def main():
    """Diagnose the issues."""
    print("🔍 DIAGNOSTIC TEST - Identifying Issues")
    print("="*50)
    
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    font = pygame.font.Font(None, 36)
    
    try:
        from modules.testmode_module.test_mode import TestModeRefactored
        
        # Create test mode
        test_mode = TestModeRefactored(screen, font, None, "puzzleassets")
        
        # Get enemy engine
        engine = test_mode.enemy_engine
        grid = engine.puzzle_grid
        
        print("✅ TestMode initialized")
        print(f"📊 Grid dimensions: {len(grid)} rows x {len(grid[0]) if grid else 0} columns")
        
        # Test 1: Check what blocks exist and their colors
        print("\n🧪 Test 1: Block inventory and colors")
        
        # Place various block types (using safe coordinates)
        test_blocks = [
            (3, 8, 'red_strike'),
            (4, 8, 'blue_garbage'),
            (5, 8, 'green_block'),
            (6, 8, 'yellow_block'),
            (3, 9, 'red_garbage'),
            (4, 9, 'blue_block')
        ]
        
        for x, y, block_type in test_blocks:
            if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
                grid[y][x] = block_type
                print(f"  📍 Placed {block_type} at ({x}, {y})")
            else:
                print(f"  ❌ Cannot place {block_type} at ({x}, {y}) - out of bounds")
        
        # Check colors for each block
        renderer = test_mode.enemy_renderer
        for x, y, block_type in test_blocks:
            if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
                color = renderer._get_block_color((x, y))
                print(f"  🎨 {block_type} color: {color}")
        
        # Test 2: Check transformation tracking
        print("\n🧪 Test 2: Transformation tracking")
        
        # Initialize tracking for strike and garbage
        strike_key = (3, 8, 2)
        garbage_key = (4, 8, 2)
        
        test_mode.garbage_block_brightness[strike_key] = {
            'landings': 0,
            'color': 'red',
            'is_strike': True
        }
        
        test_mode.garbage_block_brightness[garbage_key] = {
            'landings': 0,
            'color': 'blue',
            'is_strike': False
        }
        
        print(f"  📊 Strike tracking: {test_mode.garbage_block_brightness[strike_key]}")
        print(f"  📊 Garbage tracking: {test_mode.garbage_block_brightness[garbage_key]}")
        
        # Test 3: Simulate landing and check transformation
        print("\n🧪 Test 3: Landing simulation")
        test_mode._on_piece_landed(2)
        
        print(f"  📊 Strike tracking after landing: {test_mode.garbage_block_brightness.get(strike_key)}")
        print(f"  📊 Garbage tracking after landing: {test_mode.garbage_block_brightness.get(garbage_key)}")
        
        # Check actual grid state
        strike_cell = grid[8][3] if 0 <= 8 < len(grid) and 0 <= 3 < len(grid[0]) else None
        garbage_cell = grid[8][4] if 0 <= 8 < len(grid) and 0 <= 4 < len(grid[0]) else None
        print(f"  📊 Strike cell after landing: {strike_cell}")
        print(f"  📊 Garbage cell after landing: {garbage_cell}")
        
        # Test 4: Check cluster detection
        print("\n🧪 Test 4: Cluster detection")
        
        # Create a 2x2 cluster of normal blocks (using safe coordinates)
        safe_positions = [
            (1, 6, 'green_block'),
            (2, 6, 'green_block'),
            (1, 7, 'green_block'),
            (2, 7, 'green_block')
        ]
        
        for x, y, block_type in safe_positions:
            if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
                grid[y][x] = block_type
                print(f"  📍 Placed {block_type} at ({x}, {y})")
        
        # Place garbage nearby
        garbage_positions = [
            (0, 6, 'red_garbage'),
            (3, 6, 'blue_garbage')
        ]
        
        for x, y, block_type in garbage_positions:
            if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
                grid[y][x] = block_type
                print(f"  📍 Placed {block_type} at ({x}, {y})")
        
        clusters = engine.find_rectangular_clusters_for_render()
        print(f"  📊 Found {len(clusters)} clusters")
        
        for i, cluster in enumerate(clusters):
            print(f"  📊 Cluster {i}: {len(cluster)} blocks")
            for x, y in cluster:
                if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
                    cell = grid[y][x]
                    print(f"    📍 ({x}, {y}): {cell}")
        
        # Test 5: Check cluster glow colors
        print("\n🧪 Test 5: Cluster glow colors")
        renderer.update_visual_state()
        
        glow_effects = renderer.cluster_glow_effects
        print(f"  📊 Found {len(glow_effects)} cluster glow effects")
        
        for cluster_id, glow_data in glow_effects.items():
            color = glow_data['color']
            blocks = glow_data['blocks']
            print(f"  📊 Glow {cluster_id}: color={color}, blocks={len(blocks)}")
            
            # Check if any blocks in glow are garbage/strike
            for x, y in blocks:
                if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
                    cell = grid[y][x]
                    if cell and ('_garbage' in str(cell) or '_strike' in str(cell)):
                        print(f"    ⚠️  WARNING: Glow contains attack block at ({x}, {y}): {cell}")
        
        # Test 6: Check for any dark blue blocks (old grey blocks)
        print("\n🧪 Test 6: Dark blue block detection")
        
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
        print("📊 DIAGNOSTIC SUMMARY")
        print("="*50)
        
        issues = []
        
        # Check transformation issues
        if strike_cell != 'red_garbage':
            issues.append(f"❌ Strike not transformed: {strike_cell}")
        else:
            print("✅ Strike transformation working")
            
        if garbage_cell != 'blue_block':
            issues.append(f"❌ Garbage not transformed: {garbage_cell}")
        else:
            print("✅ Garbage transformation working")
        
        # Check color issues
        if dark_blue_blocks:
            issues.append(f"❌ Found {len(dark_blue_blocks)} dark blue blocks")
        else:
            print("✅ No dark blue blocks found")
        
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
        white_glows = 0
        for cluster_id, glow_data in glow_effects.items():
            color = glow_data['color']
            if color == (255, 255, 255) or color == (128, 128, 128):  # White or grey
                white_glows += 1
        
        if white_glows > 0:
            issues.append(f"❌ Found {white_glows} white/grey glows")
        else:
            print("✅ No white/grey glows found")
        
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
