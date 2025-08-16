"""
Integration Example - How to use the scaling system
Demonstrates how to integrate the scaling system into existing game components.
"""

import pygame
from . import resolution_manager, ui_scaler, asset_scaler, coordinate_system

class ScalingIntegrationExample:
    """
    Example of how to integrate the scaling system into game components.
    This shows the pattern for updating existing code to use the new scaling system.
    """
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.screen_size = (screen.get_width(), screen.get_height())
        
        # Initialize scaling system
        self.resolution_manager = resolution_manager
        self.ui_scaler = ui_scaler
        self.asset_scaler = asset_scaler
        self.coordinate_system = coordinate_system
        
        # Update coordinate system with current block size
        block_size = self.asset_scaler.get_block_size()
        self.coordinate_system.set_block_size(block_size)
        
        # Calculate grid position
        grid_pos = self.asset_scaler.calculate_grid_position(self.screen_size)
        self.coordinate_system.set_grid_offset(grid_pos)
        
        print(f"🎯 Scaling system initialized:")
        print(f"   Resolution: {self.resolution_manager.get_current_resolution().width} x {self.resolution_manager.get_current_resolution().height}")
        print(f"   UI Scale: {self.ui_scaler.get_scale_factor():.2f}")
        print(f"   Block Size: {self.asset_scaler.get_block_size()}")
        print(f"   Grid Position: {grid_pos}")
    
    def draw_scaled_ui(self):
        """Example of drawing scaled UI elements."""
        # Get UI scale configuration
        button_scale = self.ui_scaler.get_ui_scale("button")
        
        # Create scaled button
        button_rect = self.ui_scaler.create_button_rect(100, 100, 200, 60)
        
        # Get scaled font
        font = self.ui_scaler.get_font("body_font")
        
        # Draw button (example)
        pygame.draw.rect(self.screen, (100, 100, 100), button_rect, border_radius=button_scale.border_radius)
        
        # Draw text
        text_surface = font.render("Scaled Button", True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=button_rect.center)
        self.screen.blit(text_surface, text_rect)
    
    def draw_scaled_grid(self):
        """Example of drawing scaled grid elements."""
        # Get scaled block size
        block_size = self.asset_scaler.get_block_size()
        
        # Get grid bounds
        grid_rect = self.coordinate_system.get_grid_bounds()
        
        # Draw grid background
        pygame.draw.rect(self.screen, (50, 50, 50), grid_rect)
        
        # Draw grid lines
        for col in range(7):  # 6 columns + 1 for right edge
            x = grid_rect.x + (col * block_size)
            pygame.draw.line(self.screen, (100, 100, 100), (x, grid_rect.y), (x, grid_rect.bottom))
        
        for row in range(16):  # 15 rows + 1 for bottom edge
            y = grid_rect.y + (row * block_size)
            pygame.draw.line(self.screen, (100, 100, 100), (grid_rect.x, y), (grid_rect.right, y))
    
    def draw_scaled_block(self, grid_pos, block_type: str):
        """Example of drawing a scaled block."""
        # Get scaled block image
        block_image = self.asset_scaler.get_block_image(block_type)
        if not block_image:
            return
        
        # Get screen position
        screen_pos = self.coordinate_system.grid_to_screen(grid_pos)
        
        # Draw block
        self.screen.blit(block_image, (screen_pos.x, screen_pos.y))
    
    def handle_mouse_click(self, mouse_pos: tuple):
        """Example of handling mouse input with coordinate conversion."""
        # Convert screen coordinates to grid coordinates
        grid_pos = self.coordinate_system.screen_to_grid(mouse_pos)
        
        if grid_pos:
            print(f"🖱️ Clicked grid position: ({grid_pos.x}, {grid_pos.y})")
            # Handle grid click
            return grid_pos
        
        return None
    
    def update_resolution(self, new_resolution):
        """Example of updating resolution at runtime."""
        # Update resolution manager
        if self.resolution_manager.set_resolution(new_resolution):
            # Update all scalers
            self.ui_scaler.update_scale()
            self.asset_scaler.update_scale()
            
            # Update coordinate system
            block_size = self.asset_scaler.get_block_size()
            self.coordinate_system.update_block_size(block_size)
            
            # Recalculate grid position
            grid_pos = self.asset_scaler.calculate_grid_position(self.screen_size)
            self.coordinate_system.set_grid_offset(grid_pos)
            
            print(f"🔄 Resolution updated to: {new_resolution.width} x {new_resolution.height}")

# Example usage in existing code:
"""
# In PuzzleEngine.__init__():
def __init__(self, screen, font, audio, asset_path, settings_system=None):
    # ... existing code ...
    
    # Replace manual block size calculation with scaling system
    from core.scaling import asset_scaler
    self.block_size = asset_scaler.get_block_size()
    
    # Replace manual grid positioning with coordinate system
    from core.scaling import coordinate_system
    grid_pos = asset_scaler.calculate_grid_position((screen.get_width(), screen.get_height()))
    coordinate_system.set_grid_offset(grid_pos)
    self.grid_x_offset = grid_pos[0]
    self.grid_y_offset = grid_pos[1]

# In TestMode.__init__():
def __init__(self, screen, font, audio, asset_path, settings_system=None, clock=None):
    # ... existing code ...
    
    # Replace manual dual grid calculation with scaling system
    from core.scaling import asset_scaler
    layout = asset_scaler.calculate_dual_grid_layout((screen.get_width(), screen.get_height()))
    
    self.player_grid_position = {"x": layout['player'][0], "y": layout['player'][1]}
    self.enemy_grid_position = {"x": layout['enemy'][0], "y": layout['enemy'][1]}
    
    # Update engine grid offsets
    self.player_engine.grid_x_offset = layout['player'][0]
    self.player_engine.grid_y_offset = layout['player'][1]
    self.enemy_engine.grid_x_offset = layout['enemy'][0]
    self.enemy_engine.grid_y_offset = layout['enemy'][1]

# In menu rendering:
def draw_menu_button(self, text, x, y, width, height):
    # Replace manual scaling with UI scaler
    from core.scaling import ui_scaler
    
    button_rect = ui_scaler.create_button_rect(x, y, width, height)
    font = ui_scaler.get_font("body_font")
    
    # Draw button and text...
""" 