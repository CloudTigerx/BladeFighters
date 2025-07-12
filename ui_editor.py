import pygame
import os
import json

class UIEditor:
    def __init__(self, screen, font, audio, asset_path):
        """Initialize the UI Editor."""
        print("UI Editor: Starting initialization")
        self.screen = screen
        self.font = font
        self.audio = audio
        self.asset_path = asset_path
        
        # Get screen dimensions
        self.width = screen.get_width()
        self.height = screen.get_height()
        print(f"UI Editor: Screen dimensions - {self.width}x{self.height}")
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GRAY = (100, 100, 100)
        self.LIGHT_GRAY = (200, 200, 200)
        self.RED = (255, 0, 0)
        self.BLUE = (0, 100, 255)
        
        # Load puzzle background
        try:
            self.puzzle_background = pygame.image.load(os.path.join(asset_path, "puzzlebackground.jpg"))
            print("UI Editor: Successfully loaded puzzle background")
        except pygame.error as e:
            print(f"UI Editor: Failed to load puzzle background - {e}")
            self.puzzle_background = None
        
        # Initialize draggable elements
        self.draggable_elements = []
        self.selected_element = None
        self.dragging = False
        self.drag_offset = (0, 0)
        
        # Load saved positions
        self.load_positions()
        
        # Create back button
        self.back_button = self.create_button(20, 20, 120, 40, "Back", None)
        print("UI Editor: Initialization complete")
    
    def create_button(self, x, y, width, height, text, action=None):
        """Create a button with text and optional action."""
        button = {
            "rect": pygame.Rect(x, y, width, height),
            "text": text,
            "action": action,
            "type": "button"
        }
        return button
    
    def load_positions(self):
        """Load saved positions from file."""
        try:
            with open('ui_positions.json', 'r') as f:
                positions = json.load(f)
                
                # Create draggable elements if they don't exist
                if not self.draggable_elements:
                    # Note: These positions include border offsets which are reflected in TestMode's drawing
                    # The border_size in TestMode should match the visual representation here
                    
                    # Add player board background
                    self.draggable_elements.append({
                        "type": "player_board_background",
                        "rect": pygame.Rect(100, 100, 200, 300),
                        "color": self.BLUE,
                        "text": "Player Board Background"
                    })
                    
                    # Add player puzzle grid
                    self.draggable_elements.append({
                        "type": "player_puzzle_grid",
                        "rect": pygame.Rect(100, 100, 180, 270),
                        "color": self.WHITE,
                        "text": "Player Puzzle Grid"
                    })
                    
                    # Add enemy board background
                    self.draggable_elements.append({
                        "type": "enemy_board_background",
                        "rect": pygame.Rect(400, 100, 200, 300),
                        "color": self.RED,
                        "text": "Enemy Board Background"
                    })
                    
                    # Add enemy puzzle grid
                    self.draggable_elements.append({
                        "type": "enemy_puzzle_grid",
                        "rect": pygame.Rect(400, 100, 180, 270),
                        "color": self.WHITE,
                        "text": "Enemy Puzzle Grid"
                    })
                    
                    # Add MP3 player elements
                    base_x = self.width - 280
                    base_y = self.height - 320
                    
                    # MP3 player background
                    self.draggable_elements.append({
                        "type": "mp3_background",
                        "rect": pygame.Rect(base_x, base_y, 260, 300),
                        "color": (30, 30, 50),  # Dark blue color
                        "text": "MP3 Background"
                    })
                    
                    # MP3 player title
                    self.draggable_elements.append({
                        "type": "mp3_title",
                        "rect": pygame.Rect(base_x + 100, base_y - 25, 100, 30),
                        "color": (240, 240, 255),  # Light white color
                        "text": "MP3 Title"
                    })
                    
                    # MP3 player song info
                    self.draggable_elements.append({
                        "type": "mp3_song_info",
                        "rect": pygame.Rect(base_x + 20, base_y + 30, 220, 40),
                        "color": (255, 255, 255),  # White color
                        "text": "Song Info"
                    })
                    
                    # MP3 player buttons
                    button_size = 28
                    button_y = base_y + 235
                    
                    # Previous button
                    self.draggable_elements.append({
                        "type": "mp3_prev_button",
                        "rect": pygame.Rect(base_x + 60, button_y, button_size, button_size),
                        "color": (60, 60, 100),  # Dark blue color
                        "text": "Prev"
                    })
                    
                    # Play/Pause button
                    self.draggable_elements.append({
                        "type": "mp3_play_button",
                        "rect": pygame.Rect(base_x + 110, button_y, button_size, button_size),
                        "color": (60, 60, 100),  # Dark blue color
                        "text": "Play"
                    })
                    
                    # Next button
                    self.draggable_elements.append({
                        "type": "mp3_next_button",
                        "rect": pygame.Rect(base_x + 160, button_y, button_size, button_size),
                        "color": (60, 60, 100),  # Dark blue color
                        "text": "Next"
                    })
                    
                    # Volume Up button
                    self.draggable_elements.append({
                        "type": "mp3_volume_up",
                        "rect": pygame.Rect(base_x + 30, button_y - 45, button_size, button_size),
                        "color": (60, 60, 100),  # Dark blue color
                        "text": "Vol+"
                    })
                    
                    # Volume Down button
                    self.draggable_elements.append({
                        "type": "mp3_volume_down",
                        "rect": pygame.Rect(base_x + 190, button_y - 45, button_size, button_size),
                        "color": (60, 60, 100),  # Dark blue color
                        "text": "Vol-"
                    })
                
                # Update positions from saved file
                element_types = [
                    "player_board_background",
                    "player_puzzle_grid",
                    "enemy_board_background",
                    "enemy_puzzle_grid",
                    "mp3_background",
                    "mp3_title",
                    "mp3_song_info",
                    "mp3_prev_button",
                    "mp3_play_button",
                    "mp3_next_button",
                    "mp3_volume_up",
                    "mp3_volume_down"
                ]
                
                for i, element_type in enumerate(element_types):
                    if element_type in positions and i < len(self.draggable_elements):
                        self.draggable_elements[i]["rect"].x = positions[element_type]["x"]
                        self.draggable_elements[i]["rect"].y = positions[element_type]["y"]
                    
            print("UI positions loaded successfully")
        except FileNotFoundError:
            print("No saved UI positions found, using defaults")
        except Exception as e:
            print(f"Error loading UI positions: {e}")
    
    def save_positions(self):
        """Save current positions to file."""
        # Note: These saved positions are used directly in TestMode
        # When saving board positions, we're saving the actual grid positions
        # including any border offsets that were applied in TestMode's setup
        positions = {
            "player_board_background": {
                "x": self.draggable_elements[0]["rect"].x,
                "y": self.draggable_elements[0]["rect"].y
            },
            "player_puzzle_grid": {
                "x": self.draggable_elements[1]["rect"].x,
                "y": self.draggable_elements[1]["rect"].y
            },
            "enemy_board_background": {
                "x": self.draggable_elements[2]["rect"].x,
                "y": self.draggable_elements[2]["rect"].y
            },
            "enemy_puzzle_grid": {
                "x": self.draggable_elements[3]["rect"].x,
                "y": self.draggable_elements[3]["rect"].y
            },
            "mp3_background": {
                "x": self.draggable_elements[4]["rect"].x,
                "y": self.draggable_elements[4]["rect"].y
            },
            "mp3_title": {
                "x": self.draggable_elements[5]["rect"].x,
                "y": self.draggable_elements[5]["rect"].y
            },
            "mp3_song_info": {
                "x": self.draggable_elements[6]["rect"].x,
                "y": self.draggable_elements[6]["rect"].y
            },
            "mp3_prev_button": {
                "x": self.draggable_elements[7]["rect"].x,
                "y": self.draggable_elements[7]["rect"].y
            },
            "mp3_play_button": {
                "x": self.draggable_elements[8]["rect"].x,
                "y": self.draggable_elements[8]["rect"].y
            },
            "mp3_next_button": {
                "x": self.draggable_elements[9]["rect"].x,
                "y": self.draggable_elements[9]["rect"].y
            },
            "mp3_volume_up": {
                "x": self.draggable_elements[10]["rect"].x,
                "y": self.draggable_elements[10]["rect"].y
            },
            "mp3_volume_down": {
                "x": self.draggable_elements[11]["rect"].x,
                "y": self.draggable_elements[11]["rect"].y
            }
        }
        
        try:
            with open('ui_positions.json', 'w') as f:
                json.dump(positions, f)
            print("UI positions saved successfully")
        except Exception as e:
            print(f"Error saving UI positions: {e}")
    
    def draw(self):
        """Draw the UI Editor interface."""
        print("UI Editor: Starting draw")
        # Draw background
        self.screen.fill((30, 30, 50))
        
        # Draw title
        title_font = pygame.font.SysFont(None, 48)
        title_text = title_font.render("UI Editor - Puzzle Board Positions", True, self.WHITE)
        title_rect = title_text.get_rect(midtop=(self.width // 2, 20))
        self.screen.blit(title_text, title_rect)
        
        # Draw back button
        pygame.draw.rect(self.screen, self.BLUE, self.back_button["rect"])
        pygame.draw.rect(self.screen, self.WHITE, self.back_button["rect"], 2)
        back_text = self.font.render("Back", True, self.WHITE)
        text_rect = back_text.get_rect(center=self.back_button["rect"].center)
        self.screen.blit(back_text, text_rect)
        
        # Border size for visualization (should match TestMode.border_size)
        border_size = 10
        
        # Draw draggable elements
        print(f"UI Editor: Drawing {len(self.draggable_elements)} draggable elements")
        for element in self.draggable_elements:
            # Draw puzzle background if available
            if element["type"] in ["player_board_background", "enemy_board_background"] and self.puzzle_background:
                # Scale background to fit the board size
                scaled_bg = pygame.transform.scale(
                    self.puzzle_background,
                    (element["rect"].width, element["rect"].height)
                )
                self.screen.blit(scaled_bg, element["rect"])
                
                # Draw dashed border to indicate board border
                border_rect = pygame.Rect(
                    element["rect"].x - border_size,
                    element["rect"].y - border_size,
                    element["rect"].width + (border_size * 2),
                    element["rect"].height + (border_size * 2)
                )
                # Draw dashed border with 5px dashes
                for i in range(0, border_rect.width, 10):
                    pygame.draw.line(self.screen, (150, 150, 255), 
                                   (border_rect.x + i, border_rect.y), 
                                   (border_rect.x + i + 5, border_rect.y), 2)
                    pygame.draw.line(self.screen, (150, 150, 255), 
                                   (border_rect.x + i, border_rect.y + border_rect.height), 
                                   (border_rect.x + i + 5, border_rect.y + border_rect.height), 2)
                for i in range(0, border_rect.height, 10):
                    pygame.draw.line(self.screen, (150, 150, 255), 
                                   (border_rect.x, border_rect.y + i), 
                                   (border_rect.x, border_rect.y + i + 5), 2)
                    pygame.draw.line(self.screen, (150, 150, 255), 
                                   (border_rect.x + border_rect.width, border_rect.y + i), 
                                   (border_rect.x + border_rect.width, border_rect.y + i + 5), 2)
            
            # Draw element border with different colors for grid and background
            if "grid" in element["type"]:
                # Draw grid with dashed lines
                rect = element["rect"]
                for i in range(0, rect.width, 10):
                    pygame.draw.line(self.screen, element["color"], 
                                   (rect.x + i, rect.y), 
                                   (rect.x + i, rect.y + rect.height), 1)
                for i in range(0, rect.height, 10):
                    pygame.draw.line(self.screen, element["color"], 
                                   (rect.x, rect.y + i), 
                                   (rect.x + rect.width, rect.y + i), 1)
                                   
                # Also draw dashed border to indicate grid border
                border_rect = pygame.Rect(
                    rect.x - border_size,
                    rect.y - border_size,
                    rect.width + (border_size * 2),
                    rect.height + (border_size * 2)
                )
                # Draw dashed border with 5px dashes (different color)
                for i in range(0, border_rect.width, 10):
                    pygame.draw.line(self.screen, (255, 150, 150), 
                                   (border_rect.x + i, border_rect.y), 
                                   (border_rect.x + i + 5, border_rect.y), 2)
                    pygame.draw.line(self.screen, (255, 150, 150), 
                                   (border_rect.x + i, border_rect.y + border_rect.height), 
                                   (border_rect.x + i + 5, border_rect.y + border_rect.height), 2)
                for i in range(0, border_rect.height, 10):
                    pygame.draw.line(self.screen, (255, 150, 150), 
                                   (border_rect.x, border_rect.y + i), 
                                   (border_rect.x, border_rect.y + i + 5), 2)
                    pygame.draw.line(self.screen, (255, 150, 150), 
                                   (border_rect.x + border_rect.width, border_rect.y + i), 
                                   (border_rect.x + border_rect.width, border_rect.y + i + 5), 2)
            elif "mp3" in element["type"]:
                # Special handling for MP3 player elements
                if "background" in element["type"]:
                    # Draw MP3 background with semi-transparent effect
                    surface = pygame.Surface((element["rect"].width, element["rect"].height), pygame.SRCALPHA)
                    surface.fill((30, 30, 50, 220))  # Semi-transparent dark blue
                    pygame.draw.rect(surface, element["color"], (0, 0, element["rect"].width, element["rect"].height), 2, border_radius=10)
                    self.screen.blit(surface, element["rect"])
                elif "button" in element["type"]:
                    # Draw MP3 buttons with rounded corners and hover effect
                    button_color = (80, 80, 120) if element == self.selected_element else element["color"]
                    pygame.draw.rect(self.screen, button_color, element["rect"], 0, border_radius=6)
                    pygame.draw.rect(self.screen, (150, 150, 220), element["rect"], 2, border_radius=6)
                else:
                    # Draw other MP3 elements (title, song info) with simple border
                    pygame.draw.rect(self.screen, element["color"], element["rect"], 2)
            else:
                # Draw solid border for background
                pygame.draw.rect(self.screen, element["color"], element["rect"], 2)
            
            # Draw text label
            if "text" in element:
                text = self.font.render(element["text"], True, element["color"])
                text_rect = text.get_rect(midtop=(element["rect"].centerx, element["rect"].top - 25))
                self.screen.blit(text, text_rect)
            
            # Highlight selected element
            if element == self.selected_element:
                pygame.draw.rect(self.screen, self.RED, element["rect"], 3)
        
        # Draw instructions
        instruction_font = pygame.font.SysFont(None, 24)
        instructions = [
            "Drag the puzzle boards and grids to position them",
            "Click a board or grid to select it",
            "Press S to save positions",
            "Press ESC or click Back to return",
            "Dashed lines show board borders (10px)"
        ]
        
        for i, text in enumerate(instructions):
            instruction_text = instruction_font.render(text, True, self.LIGHT_GRAY)
            self.screen.blit(instruction_text, (20, self.height - 120 + i * 25))
        
        print("UI Editor: Draw complete")
    
    def process_events(self, events):
        """Process events for the UI Editor."""
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_pos = pygame.mouse.get_pos()
                    
                    # Check if back button was clicked
                    if self.back_button["rect"].collidepoint(mouse_pos):
                        if self.audio:
                            self.audio.play_sound('click')
                        return "back_to_settings"
                    
                    # Check if any draggable element was clicked
                    for element in self.draggable_elements:
                        if element["rect"].collidepoint(mouse_pos):
                            self.selected_element = element
                            self.drag_offset = (
                                mouse_pos[0] - element["rect"].x,
                                mouse_pos[1] - element["rect"].y
                            )
                            break
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left click release
                    self.selected_element = None
            
            elif event.type == pygame.MOUSEMOTION:
                if self.selected_element:
                    # Update element position
                    self.selected_element["rect"].x = event.pos[0] - self.drag_offset[0]
                    self.selected_element["rect"].y = event.pos[1] - self.drag_offset[1]
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "back_to_settings"
                elif event.key == pygame.K_s:  # Save positions
                    self.save_positions()
                    if self.audio:
                        self.audio.play_sound('click')
        
        return None 