"""
Blade Fighters Academy Lessons Module
This module provides lesson content for the Blade Fighters game.
"""

import pygame
import math

class LessonManager:
    """Manages lessons for Blade Fighters Academy."""
    
    def __init__(self, game_client):
        """Initialize with a reference to the game client."""
        self.client = game_client
        
        # Track completed lessons
        self.completed_lessons = set()
        
        # Initialize lesson list for School of Blade Fighters
        self.basic_lessons = [
            {
                "id": "basics_1",
                "name": "Lesson 1: Controls & Movement",
                "description": "Learn how to move and control your Blade Fighter pieces.",
                "status": "unlocked"
            },
            {
                "id": "basics_2",
                "name": "Lesson 2: Forming Clusters",
                "description": "Master the art of forming clusters for powerful attacks.",
                "status": "locked"
            },
            {
                "id": "basics_3",
                "name": "Lesson 3: Using Breakers",
                "description": "Understand the strategic use of breaker pieces.",
                "status": "locked"
            },
            {
                "id": "basics_4",
                "name": "Lesson 4: Gravity & Support",
                "description": "Learn how gravity affects pieces and clusters.",
                "status": "locked"
            },
            {
                "id": "basics_5",
                "name": "Lesson 5: Basic Combos",
                "description": "Create simple combinations to defeat opponents.",
                "status": "locked"
            },
        ]
    
    def mark_lesson_completed(self, lesson_id):
        """Mark a lesson as completed and unlock the next one."""
        self.completed_lessons.add(lesson_id)
        
        # Find and unlock the next lesson
        if lesson_id.startswith("basics_"):
            lesson_num = int(lesson_id.split("_")[1])
            next_lesson_id = f"basics_{lesson_num + 1}"
            
            # Find and unlock the next lesson if it exists
            for lesson in self.basic_lessons:
                if lesson["id"] == next_lesson_id:
                    lesson["status"] = "unlocked"
                    break
    
    def draw_basic_lessons_menu(self):
        """Draw the School of Blade Fighters lesson selection screen."""
        # Fill the screen with background
        if self.client.puzzle_background:
            # Scale background to fit the screen
            scaled_bg = pygame.transform.scale(self.client.puzzle_background, (self.client.width, self.client.height))
            self.client.screen.blit(scaled_bg, (0, 0))
        else:
            # Fallback to solid color if no background image
            self.client.screen.fill((30, 30, 50))
        
        # Add a semi-transparent overlay to make text more readable
        overlay = pygame.Surface((self.client.width, self.client.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))  # Black with 60% transparency
        self.client.screen.blit(overlay, (0, 0))
        
        # Draw title
        title_font = pygame.font.SysFont(None, 72)
        title = title_font.render("School of Blade Fighters", True, (200, 200, 255))
        self.client.screen.blit(title, (self.client.width // 2 - title.get_width() // 2, 80))
        
        # Draw subtitle
        subtitle_font = pygame.font.SysFont(None, 36)
        subtitle = subtitle_font.render("Select a Lesson", True, (220, 220, 255))
        self.client.screen.blit(subtitle, (self.client.width // 2 - subtitle.get_width() // 2, 150))
        
        # Description
        description_font = pygame.font.SysFont(None, 24)
        desc = "Complete the fundamental lessons in order to become a skilled Blade Fighter."
        desc_text = description_font.render(desc, True, (200, 200, 200))
        self.client.screen.blit(desc_text, (self.client.width // 2 - desc_text.get_width() // 2, 190))
        
        # Draw the lesson list
        lesson_y_start = 240
        lesson_height = 80
        lesson_spacing = 20
        lesson_width = 700
        
        for i, lesson in enumerate(self.basic_lessons):
            y_pos = lesson_y_start + (lesson_height + lesson_spacing) * i
            
            # Lesson box
            lesson_rect = pygame.Rect(
                self.client.width // 2 - lesson_width // 2,
                y_pos,
                lesson_width,
                lesson_height
            )
            
            # Different styling based on lesson status
            if lesson["status"] == "unlocked":
                # Unlocked lesson
                pygame.draw.rect(self.client.screen, (50, 70, 90), lesson_rect)
                pygame.draw.rect(self.client.screen, (100, 200, 255), lesson_rect, 2)
                title_color = (255, 255, 255)
                desc_color = (200, 200, 200)
                
                # Make it clickable
                mouse_pos = pygame.mouse.get_pos()
                mouse_click = pygame.mouse.get_pressed()
                
                if lesson_rect.collidepoint(mouse_pos):
                    # Highlight on hover
                    pygame.draw.rect(self.client.screen, (70, 90, 110), lesson_rect)
                    pygame.draw.rect(self.client.screen, (150, 220, 255), lesson_rect, 2)
                    
                    if mouse_click[0]:
                        # Launch the specific lesson
                        self.client.current_lesson = lesson["id"]
                        self.client.current_screen = f"lesson_{lesson['id']}"
            else:
                # Locked lesson
                pygame.draw.rect(self.client.screen, (50, 50, 60), lesson_rect)
                pygame.draw.rect(self.client.screen, (100, 100, 120), lesson_rect, 2)
                title_color = (150, 150, 150)
                desc_color = (120, 120, 120)
                
                # Draw lock icon
                lock_x = self.client.width // 2 - lesson_width // 2 + 30
                lock_y = y_pos + lesson_height // 2
                pygame.draw.circle(self.client.screen, (100, 100, 120), (lock_x, lock_y), 12)
                pygame.draw.rect(self.client.screen, (100, 100, 120), (lock_x - 8, lock_y, 16, 10))
            
            # Lesson title
            lesson_name = subtitle_font.render(lesson["name"], True, title_color)
            self.client.screen.blit(lesson_name, (self.client.width // 2 - lesson_width // 2 + 60, y_pos + 15))
            
            # Lesson description
            lesson_desc = description_font.render(lesson["description"], True, desc_color)
            self.client.screen.blit(lesson_desc, (self.client.width // 2 - lesson_width // 2 + 60, y_pos + 50))
        
        # Back button
        button_width = 200
        button_height = 50
        self.client.create_button(
            self.client.width // 2 - button_width // 2,
            self.client.height - 100,
            button_width,
            button_height,
            "Back to Main Menu",
            self.client.set_screen,
            ["main_menu"]
        )
    
    def draw_lesson_controls(self):
        """Draw Lesson 1: Controls & Movement for the School of Blade Fighters."""
        # Fill the screen with background
        if self.client.puzzle_background:
            # Scale background to fit the screen
            scaled_bg = pygame.transform.scale(self.client.puzzle_background, (self.client.width, self.client.height))
            self.client.screen.blit(scaled_bg, (0, 0))
        else:
            # Fallback to solid color if no background image
            self.client.screen.fill((30, 30, 50))
        
        # Add a semi-transparent overlay to make text more readable
        overlay = pygame.Surface((self.client.width, self.client.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))  # Black with 60% transparency
        self.client.screen.blit(overlay, (0, 0))
        
        # Draw lesson title
        title_font = pygame.font.SysFont(None, 72)
        title = title_font.render("Lesson 1: Controls & Movement", True, (200, 200, 255))
        self.client.screen.blit(title, (self.client.width // 2 - title.get_width() // 2, 80))
        
        # Content section
        content_font = pygame.font.SysFont(None, 32)
        instruction_font = pygame.font.SysFont(None, 28)
        content_x = self.client.width // 2 - 400
        content_y = 160
        line_height = 40
        
        # Lesson content
        lesson_sections = [
            ("Welcome to your first lesson, Blade Fighter!",
             "In this lesson, you'll learn the basic controls to move and position your pieces."),
            ("The Playing Field:",
             "Blade Fighters uses a grid where you'll place and manipulate puzzle pieces."),
            ("Piece Movement:",
             "• Use LEFT and RIGHT arrow keys to move pieces horizontally"),
            ("",
             "• Press DOWN arrow key to accelerate piece descent"),
            ("",
             "• Press SPACE to instantly drop the piece to the bottom (hard drop)"),
            ("Piece Rotation:",
             "• Press UP arrow key to rotate the attached piece clockwise"),
            ("Piece Flipping:",
             "• Press F key to flip your pieces vertically"),
            ("",
             "This can be critical for fitting into tight spaces or creating clusters!"),
            ("Next Piece Preview:",
             "The 'Next' window shows the upcoming piece, helping you plan your moves."),
        ]
        
        # Draw each lesson section
        for section in lesson_sections:
            # Draw section heading (if any)
            if section[0]:
                heading = content_font.render(section[0], True, (255, 220, 100))
                self.client.screen.blit(heading, (content_x, content_y))
                content_y += line_height
            
            # Draw section content
            content = instruction_font.render(section[1], True, self.client.WHITE)
            content_indent = 0 if section[0] else 30  # Indent continuation lines
            self.client.screen.blit(content, (content_x + content_indent, content_y))
            content_y += line_height + 5
        
        # Visual example section
        example_y = content_y + 20
        example_title = content_font.render("Visual Examples:", True, (255, 220, 100))
        self.client.screen.blit(example_title, (content_x, example_y))
        
        # Draw control visuals
        key_size = 60
        key_spacing = 80
        keys_y = example_y + 60
        
        # Arrow keys visual
        for i, (key, label) in enumerate([
            ("←", "Move Left"), 
            ("→", "Move Right"), 
            ("↑", "Rotate"), 
            ("↓", "Move Down")
        ]):
            # Key background
            key_x = content_x + 100 + (i * key_spacing)
            key_rect = pygame.Rect(key_x, keys_y, key_size, key_size)
            pygame.draw.rect(self.client.screen, (50, 50, 70), key_rect)
            pygame.draw.rect(self.client.screen, (150, 150, 200), key_rect, 2)
            
            # Key label
            key_label = content_font.render(key, True, self.client.WHITE)
            self.client.screen.blit(key_label, (key_x + key_size//2 - key_label.get_width()//2, 
                                      keys_y + key_size//2 - key_label.get_height()//2))
            
            # Action label
            action_label = instruction_font.render(label, True, (200, 200, 200))
            self.client.screen.blit(action_label, (key_x + key_size//2 - action_label.get_width()//2, 
                                         keys_y + key_size + 10))
        
        # Space bar visual
        space_rect = pygame.Rect(content_x + 150, keys_y + 150, 300, key_size)
        pygame.draw.rect(self.client.screen, (50, 50, 70), space_rect)
        pygame.draw.rect(self.client.screen, (150, 150, 200), space_rect, 2)
        
        space_label = content_font.render("SPACE", True, self.client.WHITE)
        self.client.screen.blit(space_label, (content_x + 300 - space_label.get_width()//2, 
                                   keys_y + 150 + key_size//2 - space_label.get_height()//2))
        
        space_action = instruction_font.render("Hard Drop", True, (200, 200, 200))
        self.client.screen.blit(space_action, (content_x + 300 - space_action.get_width()//2, 
                                    keys_y + 150 + key_size + 10))
        
        # F key visual
        f_rect = pygame.Rect(content_x + 500, keys_y, key_size, key_size)
        pygame.draw.rect(self.client.screen, (50, 50, 70), f_rect)
        pygame.draw.rect(self.client.screen, (150, 150, 200), f_rect, 2)
        
        f_label = content_font.render("F", True, self.client.WHITE)
        self.client.screen.blit(f_label, (content_x + 500 + key_size//2 - f_label.get_width()//2, 
                                keys_y + key_size//2 - f_label.get_height()//2))
        
        f_action = instruction_font.render("Flip Vertically", True, (200, 200, 200))
        self.client.screen.blit(f_action, (content_x + 500 + key_size//2 - f_action.get_width()//2, 
                                 keys_y + key_size + 10))
        
        # Navigation buttons
        button_width = 200
        button_height = 50
        
        # Back button
        self.client.create_button(
            self.client.width // 4 - button_width // 2,
            self.client.height - 80,
            button_width,
            button_height,
            "Back to Lessons",
            self.client.set_screen,
            ["academy_basics"]
        )
        
        # Practice button
        self.client.create_button(
            self.client.width // 2,
            self.client.height - 80,
            button_width,
            button_height,
            "Practice Controls",
            self.client.start_lesson_practice,
            ["basics_1"]
        )
        
        # Next lesson button (disabled if not completed or unlocked)
        next_button_color = (100, 100, 100)
        if "basics_1" in self.completed_lessons:
            next_button_color = (150, 220, 255)
            
        next_button_rect = pygame.Rect(
            3 * self.client.width // 4 - button_width // 2,
            self.client.height - 80,
            button_width,
            button_height
        )
        
        if "basics_1" in self.completed_lessons:
            # Enabled next button
            if self.client.create_button(
                3 * self.client.width // 4 - button_width // 2,
                self.client.height - 80,
                button_width,
                button_height,
                "Next Lesson",
                self.client.set_screen,
                ["lesson_basics_2"]
            ):
                pass
        else:
            # Disabled next button
            pygame.draw.rect(self.client.screen, (40, 40, 50), next_button_rect)
            pygame.draw.rect(self.client.screen, next_button_color, next_button_rect, 2)
            
            next_button_text = self.client.font.render("Next Lesson", True, next_button_color)
            self.client.screen.blit(next_button_text, (
                3 * self.client.width // 4 - next_button_text.get_width() // 2,
                self.client.height - 80 + button_height // 2 - next_button_text.get_height() // 2
            ))
    
    def draw_lesson_clusters(self):
        """Draw Lesson 2: Forming Clusters for the School of Blade Fighters."""
        # Fill the screen with background
        if self.client.puzzle_background:
            # Scale background to fit the screen
            scaled_bg = pygame.transform.scale(self.client.puzzle_background, (self.client.width, self.client.height))
            self.client.screen.blit(scaled_bg, (0, 0))
        else:
            # Fallback to solid color if no background image
            self.client.screen.fill((30, 30, 50))
        
        # Add a semi-transparent overlay to make text more readable
        overlay = pygame.Surface((self.client.width, self.client.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))  # Black with 60% transparency
        self.client.screen.blit(overlay, (0, 0))
        
        # Draw lesson title
        title_font = pygame.font.SysFont(None, 72)
        title = title_font.render("Lesson 2: Forming Clusters", True, (200, 200, 255))
        self.client.screen.blit(title, (self.client.width // 2 - title.get_width() // 2, 80))
        
        # Content section
        content_font = pygame.font.SysFont(None, 32)
        instruction_font = pygame.font.SysFont(None, 28)
        content_x = self.client.width // 2 - 400
        content_y = 160
        line_height = 40
        
        # Lesson content
        lesson_sections = [
            ("Building the Foundation of Combat:",
             "Clusters are the primary offensive weapon in Blade Fighters."),
            ("What is a Cluster?",
             "A cluster is formed when 4 or more blocks of the same color are arranged"),
            ("",
             "in a 2x2 or larger formation. Clusters are your primary attack mechanism."),
            ("Cluster Properties:",
             "• Clusters are groups of 4+ matching blocks"),
            ("",
             "• Clusters can interact with breaker pieces of the same color"),
            ("",
             "• Clusters have special gravity properties - they fall as a unit"),
            ("",
             "• Clusters will only fall if NO part of the cluster has support"),
            ("Strategic Formations:",
             "Different cluster shapes offer tactical advantages:"),
            ("",
             "• 2x2 Square: Basic cluster, quick to form and deploy"),
            ("",
             "• L-Shape: Covers more area, can connect to multiple breakers"),
            ("",
             "• Line Shape: Can reach across the field to create chain reactions"),
            ("Connecting Clusters:",
             "Clusters can be connected with breakers to create powerful chain reactions."),
            ("",
             "Plan your formations with future connections in mind."),
        ]
        
        # Draw each lesson section
        for section in lesson_sections:
            # Draw section heading (if any)
            if section[0]:
                heading = content_font.render(section[0], True, (255, 220, 100))
                self.client.screen.blit(heading, (content_x, content_y))
                content_y += line_height
            
            # Draw section content
            content = instruction_font.render(section[1], True, self.client.WHITE)
            content_indent = 0 if section[0] else 30  # Indent continuation lines
            self.client.screen.blit(content, (content_x + content_indent, content_y))
            content_y += line_height + 5
        
        # Visual example section
        example_y = content_y + 20
        example_title = content_font.render("Cluster Examples:", True, (255, 220, 100))
        self.client.screen.blit(example_title, (content_x, example_y))
        
        # Draw example clusters
        cluster_examples = [
            {"name": "2x2 Square", "formation": [(0,0), (0,1), (1,0), (1,1)]},
            {"name": "L-Shape", "formation": [(0,0), (0,1), (0,2), (1,0)]},
            {"name": "Line Shape", "formation": [(0,0), (1,0), (2,0), (3,0)]}
        ]
        
        example_spacing = 250
        block_display_size = 30
        
        # Draw each example cluster
        for i, example in enumerate(cluster_examples):
            # Calculate position for this example
            example_x = content_x + (i * example_spacing)
            example_y = example_y + 50
            
            # Draw example name
            name_surface = instruction_font.render(example["name"], True, self.client.WHITE)
            name_rect = name_surface.get_rect(centerx=example_x + (block_display_size * 2), 
                                            bottom=example_y - 10)
            self.client.screen.blit(name_surface, name_rect)
            
            # Draw grid for this example
            grid_size = 4
            for y in range(grid_size):
                for x in range(grid_size):
                    grid_x = example_x + (x * block_display_size)
                    grid_y = example_y + (y * block_display_size)
                    
                    # Draw grid cell
                    pygame.draw.rect(
                        self.client.screen, 
                        (50, 50, 50), 
                        (grid_x, grid_y, block_display_size, block_display_size),
                        1
                    )
                    
                    # If this position is part of the formation, draw a colored block
                    if (x, y) in example["formation"]:
                        block_rect = pygame.Rect(
                            grid_x + 2, grid_y + 2, 
                            block_display_size - 4, block_display_size - 4
                        )
                        # Use red color for examples
                        pygame.draw.rect(self.client.screen, (200, 80, 80), block_rect)
        
        # Actual game example
        example_desc = instruction_font.render("Examples of cluster formations in gameplay:", True, (200, 200, 200))
        self.client.screen.blit(example_desc, (content_x, example_y + 200))
        
        # Display a sample of actual gameplay cluster (using game pieces)
        # We'll create a 2x2 cluster of red blocks
        display_x = content_x + 200
        display_y = example_y + 250
        display_size = self.client.block_size * 1.5  # Slightly larger for visibility
        
        # Draw 2x2 cluster of red blocks with glow effect
        for dx in range(2):
            for dy in range(2):
                x_pos = display_x + (dx * display_size)
                y_pos = display_y + (dy * display_size)
                
                # Scale up the actual game piece
                if 'red' in self.client.puzzle_pieces:
                    sample_piece = pygame.transform.scale(
                        self.client.puzzle_pieces['red'], 
                        (int(display_size), int(display_size))
                    )
                    self.client.screen.blit(sample_piece, (x_pos, y_pos))
                    
                    # Add pulsing glow effect
                    current_time = pygame.time.get_ticks()
                    pulse = (math.sin(current_time / 200) + 1) / 2  # Value between 0 and 1
                    glow_alpha = int(100 + (pulse * 100))  # Pulsing alpha value
                    
                    glow_surface = pygame.Surface(
                        (int(display_size), int(display_size)), 
                        pygame.SRCALPHA
                    )
                    pygame.draw.rect(
                        glow_surface, 
                        (255, 100, 100, glow_alpha), 
                        (0, 0, int(display_size), int(display_size)),
                        4  # Border width
                    )
                    self.client.screen.blit(glow_surface, (x_pos, y_pos))
        
        # Navigation buttons
        button_width = 200
        button_height = 50
        
        # Back button
        self.client.create_button(
            self.client.width // 4 - button_width // 2,
            self.client.height - 80,
            button_width,
            button_height,
            "Back to Lessons",
            self.client.set_screen,
            ["academy_basics"]
        )
        
        # Practice button
        self.client.create_button(
            self.client.width // 2,
            self.client.height - 80,
            button_width,
            button_height,
            "Practice Clusters",
            self.client.start_lesson_practice,
            ["basics_2"]
        )
        
        # Next lesson button (disabled if not completed or unlocked)
        next_button_color = (100, 100, 100)
        if "basics_2" in self.completed_lessons:
            next_button_color = (150, 220, 255)
            
        next_button_rect = pygame.Rect(
            3 * self.client.width // 4 - button_width // 2,
            self.client.height - 80,
            button_width,
            button_height
        )
        
        if "basics_2" in self.completed_lessons:
            # Enabled next button
            if self.client.create_button(
                3 * self.client.width // 4 - button_width // 2,
                self.client.height - 80,
                button_width,
                button_height,
                "Next Lesson",
                self.client.set_screen,
                ["lesson_basics_3"]
            ):
                pass
        else:
            # Disabled next button
            pygame.draw.rect(self.client.screen, (40, 40, 50), next_button_rect)
            pygame.draw.rect(self.client.screen, next_button_color, next_button_rect, 2)
            
            next_button_text = self.client.font.render("Next Lesson", True, next_button_color)
            self.client.screen.blit(next_button_text, (
                3 * self.client.width // 4 - next_button_text.get_width() // 2,
                self.client.height - 80 + button_height // 2 - next_button_text.get_height() // 2
            )) 