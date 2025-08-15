#!/usr/bin/env python3
"""
Test Script for BladeFighters Scaling System
Tests resolution detection, UI scaling, asset scaling, and coordinate transformations.
"""

import pygame
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_scaling_system():
    """Test the comprehensive scaling system."""
    print("🧪 Testing BladeFighters Scaling System")
    print("=" * 50)
    
    # Initialize pygame
    pygame.init()
    
    try:
        # Import the scaling system
        from core.scaling import resolution_manager, ui_scaler, asset_scaler, coordinate_system
        
        print("✅ Scaling system imported successfully")
        
        # Test resolution detection
        print("\n📐 Testing Resolution Detection:")
        current_res = resolution_manager.get_current_resolution()
        print(f"   Current resolution: {current_res.width} x {current_res.height}")
        print(f"   Display type: {resolution_manager.get_display_type().value}")
        print(f"   Scale factor: {resolution_manager.get_scale_factor()}")
        print(f"   UI scale factor: {resolution_manager.get_ui_scale_factor():.2f}")
        
        # Test available resolutions
        available_res = resolution_manager.get_available_resolutions()
        print(f"   Available resolutions: {len(available_res)}")
        for i, res in enumerate(available_res[:5]):
            print(f"     {i+1}. {res.width} x {res.height} (density: {res.pixel_density:.2f})")
        
        # Test UI scaling
        print("\n🎨 Testing UI Scaling:")
        ui_scale = ui_scaler.get_ui_scale("button")
        print(f"   Button font size: {ui_scale.font_size}")
        print(f"   Button padding: {ui_scale.padding}")
        print(f"   Button border radius: {ui_scale.border_radius}")
        
        # Test font scaling
        font = ui_scaler.get_font("title_font")
        print(f"   Title font size: {font.get_height()}")
        
        # Test asset scaling
        print("\n🖼️ Testing Asset Scaling:")
        block_size = asset_scaler.get_block_size()
        print(f"   Block size: {block_size}")
        
        grid_dims = asset_scaler.get_grid_dimensions()
        print(f"   Grid dimensions: {grid_dims[0]} x {grid_dims[1]} blocks")
        
        grid_pixel_size = asset_scaler.get_grid_pixel_size()
        print(f"   Grid pixel size: {grid_pixel_size[0]} x {grid_pixel_size[1]} pixels")
        
        # Test coordinate system
        print("\n📍 Testing Coordinate System:")
        coordinate_system.set_block_size(block_size)
        
        # Test grid positioning
        screen_size = (1920, 1080)  # Test with 1080p
        grid_pos = asset_scaler.calculate_grid_position(screen_size)
        coordinate_system.set_grid_offset(grid_pos)
        print(f"   Grid position: {grid_pos}")
        
        # Test coordinate conversion
        test_screen_pos = (grid_pos[0] + block_size, grid_pos[1] + block_size)
        grid_pos_result = coordinate_system.screen_to_grid(test_screen_pos)
        if grid_pos_result:
            print(f"   Screen ({test_screen_pos[0]}, {test_screen_pos[1]}) -> Grid ({grid_pos_result.x}, {grid_pos_result.y})")
        
        # Test dual grid layout
        dual_layout = asset_scaler.calculate_dual_grid_layout(screen_size)
        print(f"   Dual grid layout:")
        print(f"     Player: {dual_layout['player']}")
        print(f"     Enemy: {dual_layout['enemy']}")
        print(f"     Spacing: {dual_layout['spacing']}")
        
        # Test resolution switching
        print("\n🔄 Testing Resolution Switching:")
        if len(available_res) > 1:
            test_res = available_res[1]  # Try second resolution
            if resolution_manager.set_resolution(test_res):
                print(f"   Switched to: {test_res.width} x {test_res.height}")
                
                # Update scalers
                ui_scaler.update_scale()
                asset_scaler.update_scale()
                
                new_block_size = asset_scaler.get_block_size()
                print(f"   New block size: {new_block_size}")
                
                # Switch back
                resolution_manager.set_resolution(current_res)
                ui_scaler.update_scale()
                asset_scaler.update_scale()
                print(f"   Switched back to: {current_res.width} x {current_res.height}")
            else:
                print("   Resolution switching failed")
        else:
            print("   Only one resolution available, skipping switch test")
        
        # Test asset loading (if assets exist)
        print("\n📦 Testing Asset Loading:")
        test_assets = ['redblock.png', 'blueblock.png', 'puzzlebackground.jpg']
        for asset in test_assets:
            if os.path.exists(os.path.join('puzzleassets', asset)):
                print(f"   ✅ {asset} exists")
            else:
                print(f"   ❌ {asset} not found")
        
        print("\n🎉 All scaling system tests completed successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        pygame.quit()

def test_visual_demo():
    """Create a visual demo of the scaling system."""
    print("\n🎨 Creating Visual Demo...")
    
    # Initialize pygame
    pygame.init()
    
    try:
        from core.scaling import resolution_manager, ui_scaler, asset_scaler, coordinate_system
        
        # Create a test window
        screen_size = (800, 600)
        screen = pygame.display.set_mode(screen_size, pygame.RESIZABLE)
        pygame.display.set_caption("BladeFighters Scaling System Demo")
        
        # Initialize scaling system
        block_size = asset_scaler.get_block_size()
        coordinate_system.set_block_size(block_size)
        
        # Calculate grid position
        grid_pos = asset_scaler.calculate_grid_position(screen_size)
        coordinate_system.set_grid_offset(grid_pos)
        
        # Colors
        BLACK = (0, 0, 0)
        WHITE = (255, 255, 255)
        GRAY = (100, 100, 100)
        BLUE = (0, 100, 255)
        
        clock = pygame.time.Clock()
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    screen_size = (event.w, event.h)
                    screen = pygame.display.set_mode(screen_size, pygame.RESIZABLE)
                    # Recalculate grid position for new size
                    grid_pos = asset_scaler.calculate_grid_position(screen_size)
                    coordinate_system.set_grid_offset(grid_pos)
            
            # Clear screen
            screen.fill(BLACK)
            
            # Draw grid
            grid_rect = coordinate_system.get_grid_bounds()
            pygame.draw.rect(screen, GRAY, grid_rect, 2)
            
            # Draw grid lines
            for col in range(7):
                x = grid_rect.x + (col * block_size)
                pygame.draw.line(screen, GRAY, (x, grid_rect.y), (x, grid_rect.bottom))
            
            for row in range(16):
                y = grid_rect.y + (row * block_size)
                pygame.draw.line(screen, GRAY, (grid_rect.x, y), (grid_rect.right, y))
            
            # Draw some test blocks
            test_positions = [(0, 14), (1, 14), (2, 13), (3, 13), (4, 12), (5, 12)]
            for i, (col, row) in enumerate(test_positions):
                from core.scaling.coordinate_system import GridPosition
                grid_pos = GridPosition(col, row)
                screen_pos = coordinate_system.grid_to_screen(grid_pos)
                color = [(255, 0, 0), (0, 0, 255), (0, 255, 0), (255, 255, 0)][i % 4]
                pygame.draw.rect(screen, color, (screen_pos.x, screen_pos.y, block_size, block_size))
            
            # Draw UI elements
            button_rect = ui_scaler.create_button_rect(10, 10, 200, 40)
            pygame.draw.rect(screen, BLUE, button_rect, border_radius=5)
            
            # Draw text
            font = ui_scaler.get_font("body_font")
            text = font.render(f"Block Size: {block_size}", True, WHITE)
            screen.blit(text, (10, 60))
            
            text2 = font.render(f"Resolution: {screen_size[0]} x {screen_size[1]}", True, WHITE)
            screen.blit(text2, (10, 90))
            
            text3 = font.render("Resize window to test scaling!", True, WHITE)
            screen.blit(text3, (10, 120))
            
            pygame.display.flip()
            clock.tick(60)
        
        return True
        
    except Exception as e:
        print(f"❌ Visual demo error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        pygame.quit()

if __name__ == "__main__":
    print("🚀 BladeFighters Scaling System Test")
    print("=" * 50)
    
    # Run basic tests
    success = test_scaling_system()
    
    if success:
        print("\n" + "=" * 50)
        print("🎯 Basic tests passed! Starting visual demo...")
        print("Press any key to continue...")
        input()
        
        # Run visual demo
        test_visual_demo()
    else:
        print("\n❌ Basic tests failed. Please check the errors above.")
        sys.exit(1) 