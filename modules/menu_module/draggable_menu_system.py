"""
Draggable Menu System - Allows real-time positioning of menu elements
Perfect for fine-tuning UI layout without code changes.
"""

import pygame
import json
import os
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from .scaled_menu_system import ScaledMenuSystem, MenuButton

@dataclass
class DraggableElement:
    """Represents a draggable UI element."""
    name: str
    rect: pygame.Rect
    element_type: str  # 'button', 'title', 'background'
    is_dragging: bool = False
    drag_offset: Tuple[int, int] = (0, 0)
    original_position: Tuple[int, int] = (0, 0)


class DraggableMenuSystem(ScaledMenuSystem):
    """
    Enhanced menu system with draggable elements for perfect positioning.
    """
    
    def __init__(self, screen, font, audio, asset_path: str = "puzzleassets", game_mode: str = "default"):
        super().__init__(screen, font, audio, asset_path, game_mode)
        
        # Draggable system state
        self.draggable_mode = False
        self.draggable_elements: Dict[str, DraggableElement] = {}
        self.dragging_element = None
        
        # Position save file
        self.positions_file = os.path.join(asset_path, "menus", "saved_positions.json")
        
        # Load saved positions or use defaults
        self.load_positions()
        
        # Initialize draggable elements
        self._setup_draggable_elements()
        print(f"🎯 DraggableMenuSystem initialized with {len(self.draggable_elements)} elements")
        
        # Toggle key
        self.toggle_key = pygame.K_F2  # F2 to toggle draggable mode
        
    def _setup_draggable_elements(self):
        """Setup all draggable elements."""
        # Clear existing elements
        self.draggable_elements.clear()
        
        # Add buttons as draggable elements
        if "main" in self.buttons:
            print(f"🎯 Found {len(self.buttons['main'])} main menu buttons")
            for i, button in enumerate(self.buttons["main"]):
                element_name = f"button_{button.text.lower().replace(' ', '_')}"
                self.draggable_elements[element_name] = DraggableElement(
                    name=element_name,
                    rect=button.rect.copy(),
                    element_type="button",
                    original_position=(button.rect.x, button.rect.y)
                )
                print(f"🎯 Added draggable element: {element_name} at {button.rect.x}, {button.rect.y}")
        else:
            print("⚠️ No main menu buttons found!")
        
        # Add title as draggable element
        # Calculate title position based on the actual title drawing logic
        button_width, button_height = self._get_button_size()
        buttons_data = [
            ("Quickplay", "quickplay"),
            ("Story Mode", "story"),
            ("Test Mode", "test"),
            ("Smithing", "smithing"),
            ("Inventory", "inventory"),
            ("Settings", "settings"),
            ("Quit", "quit")
        ]
        spacing = 35
        button_stack_start_y = 800
        
        # Try to use title wordmark if available
        if hasattr(self, 'title_wordmark') and self.title_wordmark:
            tw = 480  # Fixed width for 4K
            ratio = self.title_wordmark.get_height() / max(1, self.title_wordmark.get_width())
            th = max(1, int(tw * ratio))
            tx = (self.width - tw) // 2
            ty = button_stack_start_y - th - 30
            title_rect = pygame.Rect(tx, ty, tw, th)
        else:
            # Fallback to text title area
            title_rect = pygame.Rect(0, 0, 600, 100)
            title_rect.centerx = self.width // 2
            title_rect.bottom = button_stack_start_y - 20
        
        self.draggable_elements["title"] = DraggableElement(
            name="title",
            rect=title_rect,
            element_type="title",
            original_position=(title_rect.x, title_rect.y)
        )
        
        # Background is not draggable - it stays fixed
        # Removed background from draggable elements
    
    def load_positions(self):
        """Load saved positions from file."""
        try:
            if os.path.exists(self.positions_file):
                with open(self.positions_file, 'r') as f:
                    self.saved_positions = json.load(f)
                print(f"✅ Loaded saved positions from {self.positions_file}")
            else:
                self.saved_positions = {}
                print("📝 No saved positions found, using defaults")
        except Exception as e:
            print(f"⚠️ Error loading positions: {e}")
            self.saved_positions = {}
    
    def save_positions(self):
        """Save current positions to file."""
        try:
            positions = {}
            print(f"🎯 Saving {len(self.draggable_elements)} elements...")
            for name, element in self.draggable_elements.items():
                positions[name] = {
                    "x": element.rect.x,
                    "y": element.rect.y,
                    "type": element.element_type
                }
                print(f"  - {name}: ({element.rect.x}, {element.rect.y})")
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.positions_file), exist_ok=True)
            
            with open(self.positions_file, 'w') as f:
                json.dump(positions, f, indent=2)
            
            print(f"💾 Saved positions to {self.positions_file}")
            return True
        except Exception as e:
            print(f"❌ Error saving positions: {e}")
            return False
    
    def apply_saved_positions(self):
        """Apply saved positions to elements."""
        for name, element in self.draggable_elements.items():
            if name in self.saved_positions:
                pos = self.saved_positions[name]
                element.rect.x = pos["x"]
                element.rect.y = pos["y"]
                
                # Update corresponding button positions
                if element.element_type == "button":
                    self._update_button_position(name, pos["x"], pos["y"])
        
        # Also update the title position in the parent class if needed
        if "title" in self.draggable_elements and "title" in self.saved_positions:
            title_element = self.draggable_elements["title"]
            # Store the title position for use in drawing
            self._title_draggable_position = (title_element.rect.x, title_element.rect.y, 
                                            title_element.rect.width, title_element.rect.height)
    
    def _update_button_position(self, element_name: str, x: int, y: int):
        """Update the actual button position."""
        button_name = element_name.replace("button_", "").replace("_", " ")
        
        # Find and update the corresponding button
        if "main" in self.buttons:
            for button in self.buttons["main"]:
                if button.text.lower().replace(" ", "_") == button_name:
                    old_pos = (button.rect.x, button.rect.y)
                    button.rect.x = x
                    button.rect.y = y
                    if self.draggable_mode:
                        print(f"🎯 Updated button '{button.text}' from {old_pos} to ({x}, {y})")
                    break
    
    def toggle_draggable_mode(self):
        """Toggle draggable mode on/off."""
        self.draggable_mode = not self.draggable_mode
        status = "ON" if self.draggable_mode else "OFF"
        print(f"🎯 Draggable mode: {status}")
        print(f"🎯 Available elements: {list(self.draggable_elements.keys())}")
        
        if not self.draggable_mode:
            # Save positions when exiting draggable mode
            self.save_positions()
    
    def process_events(self, events: List) -> Optional[str]:
        """Process events with draggable functionality."""
        # Check for toggle key
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == self.toggle_key:
                    self.toggle_draggable_mode()
                elif event.key == pygame.K_F3 and self.draggable_mode:
                    # F3 to save positions manually
                    self.save_positions()
                elif event.key == pygame.K_F4 and self.draggable_mode:
                    # F4 to reset positions
                    self._reset_positions()
        
        if self.draggable_mode:
            return self._process_draggable_events(events)
        else:
            return super().process_events(events)
    
    def _process_draggable_events(self, events: List) -> Optional[str]:
        """Process events in draggable mode."""
        mouse_pos = pygame.mouse.get_pos()
        keys = pygame.key.get_pressed()
        
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:  # E key pressed
                    # Check if E is pressed over a draggable element
                    for element in self.draggable_elements.values():
                        if element.rect.collidepoint(mouse_pos):
                            element.is_dragging = True
                            element.drag_offset = (
                                mouse_pos[0] - element.rect.x,
                                mouse_pos[1] - element.rect.y
                            )
                            self.dragging_element = element
                            break
            
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_e:  # E key released
                    if self.dragging_element:
                        print(f"🎯 Stopped dragging: {self.dragging_element.name}")
                        self.dragging_element.is_dragging = False
                        # Auto-save when you stop dragging
                        success = self.save_positions()
                        if success:
                            print("💾 Auto-saved positions after dragging")
                        else:
                            print("❌ Failed to auto-save positions")
                        self.dragging_element = None
            
            elif event.type == pygame.MOUSEMOTION:
                if self.dragging_element and self.dragging_element.is_dragging and keys[pygame.K_e]:
                    # Update element position only if E is still held
                    new_x = mouse_pos[0] - self.dragging_element.drag_offset[0]
                    new_y = mouse_pos[1] - self.dragging_element.drag_offset[1]
                    
                    # Keep element on screen
                    new_x = max(0, min(new_x, self.width - self.dragging_element.rect.width))
                    new_y = max(0, min(new_y, self.height - self.dragging_element.rect.height))
                    
                    self.dragging_element.rect.x = new_x
                    self.dragging_element.rect.y = new_y
                    
                    # Update corresponding button if it's a button element
                    if self.dragging_element.element_type == "button":
                        self._update_button_position(
                            self.dragging_element.name, new_x, new_y
                        )
                    elif self.dragging_element.element_type == "title":
                        # Update title position for drawing
                        self._title_draggable_position = (new_x, new_y, 
                                                        self.dragging_element.rect.width, 
                                                        self.dragging_element.rect.height)
        
        return None
    
    def _reset_positions(self):
        """Reset all elements to their original positions."""
        for element in self.draggable_elements.values():
            element.rect.x, element.rect.y = element.original_position
            if element.element_type == "button":
                self._update_button_position(
                    element.name, element.original_position[0], element.original_position[1]
                )
        print("🔄 Reset all positions to original")
    
    def draw_main_menu(self, on_start_action=None, on_story_action=None, on_test_action=None, on_test_lab_action=None, version=None):
        """Draw main menu with draggable overlay."""
        # Apply saved positions only when NOT in draggable mode
        if not self.draggable_mode:
            self.apply_saved_positions()
        
        # Draw normal menu
        buttons = super().draw_main_menu(on_start_action, on_story_action, on_test_action, on_test_lab_action, version)
        
        # Draw draggable overlay if in draggable mode
        if self.draggable_mode:
            self._draw_draggable_overlay()
        
        return buttons
    
    def _draw_title(self, title_text="Blade Fighters"):
        """Override title drawing to use draggable position."""
        # Get the draggable title element position
        title_element = self.draggable_elements.get("title")
        if title_element:
            # Always use the draggable position if available
            tx, ty = title_element.rect.x, title_element.rect.y
            tw, th = title_element.rect.width, title_element.rect.height
            if self.draggable_mode:
                print(f"🎯 Drawing title at draggable position: ({tx}, {ty}) size: ({tw}, {th})")
        else:
            # Fallback to original positioning
            return super()._draw_title(title_text)
        
        # Try to use title wordmark image if available
        if hasattr(self, 'title_wordmark') and self.title_wordmark:
            try:
                # Scale the wordmark to fit the draggable rect
                scaled_wordmark = pygame.transform.scale(self.title_wordmark, (tw, th))
                self.screen.blit(scaled_wordmark, (tx, ty))
                return
            except Exception as e:
                print(f"Failed to draw title wordmark: {e}")
        
        # Fallback to text title
        title_font = pygame.font.SysFont(None, 72)  # Fixed font size for 4K
        
        # Render title text
        title_surface = title_font.render(title_text, True, self.WHITE)
        title_rect = title_surface.get_rect()
        
        # Center within the draggable rect
        title_rect.center = (tx + tw // 2, ty + th // 2)
        
        # Draw title
        self.screen.blit(title_surface, title_rect)
    
    def _draw_draggable_overlay(self):
        """Draw draggable mode overlay."""
        # Draw element outlines
        for element in self.draggable_elements.values():
            color = (255, 255, 0) if element.is_dragging else (0, 255, 0)  # Yellow if dragging, green if not
            pygame.draw.rect(self.screen, color, element.rect, 2)
            
            # Draw element name
            font = pygame.font.SysFont(None, 24)
            text = font.render(element.name, True, color)
            text_rect = text.get_rect(center=element.rect.center)
            self.screen.blit(text, text_rect)
        
        # Draw instructions
        instruction_font = pygame.font.SysFont(None, 32)
        instructions = [
            "F2: Toggle Draggable Mode",
            "F3: Save Positions",
            "F4: Reset Positions",
            "Hold E + Mouse to drag elements"
        ]
        
        for i, instruction in enumerate(instructions):
            text = instruction_font.render(instruction, True, (255, 255, 255))
            self.screen.blit(text, (10, 10 + i * 30))
        
        # Draw status
        status_text = instruction_font.render("DRAGGABLE MODE ACTIVE", True, (255, 255, 0))
        self.screen.blit(status_text, (self.width - 300, 10))
