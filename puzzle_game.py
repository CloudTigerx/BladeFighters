import pygame
import sys
import time
from puzzle_module import PuzzleEngine
from puzzle_renderer import PuzzleRenderer

def main():
    """Main function to run the puzzle game."""
    # Initialize pygame
    pygame.init()
    
    # Set up the display
    screen_width = 800
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Blade Fighters - Puzzle Mode")
    
    # Initialize the clock for controlling frame rate
    clock = pygame.time.Clock()
    
    # Load a font for text rendering
    try:
        font = pygame.font.Font(None, 24)  # Use default font
    except:
        font = pygame.font.SysFont(None, 24)  # Fallback
    
    # Create the game engine
    puzzle_engine = PuzzleEngine(screen, font)
    
    # Create the renderer
    renderer = PuzzleRenderer(puzzle_engine)
    
    # Start the game
    puzzle_engine.start_game()
    
    # Main game loop
    running = True
    last_time = time.time()
    
    while running:
        current_time = time.time()
        delta_time = current_time - last_time
        last_time = current_time
        
        # Get all events
        events = pygame.event.get()
        
        # Check for quit event
        for event in events:
            if event.type == pygame.QUIT:
                running = False
        
        # Process game events
        action = puzzle_engine.process_events(events)
        
        # Handle any actions
        if action == "quit" or action == "back_to_menu":
            running = False
        
        # Update game state
        puzzle_engine.update()
        
        # Update animations in the renderer
        renderer.update_visual_state()
        renderer.update_animations()
        
        # Draw the game
        renderer.draw_game_screen()
        
        # Update the display
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(60)
    
    # Clean up
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 