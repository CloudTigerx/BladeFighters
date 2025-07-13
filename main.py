import sys

# Import the GameClient class from our new module
from game_client import GameClient

def main():
    """
    Main entry point for the Blade Fighters game.
    This function initializes the game client and starts the game loop.
    """
    # Create a game client instance
    client = GameClient()
    
    # Start the game
    client.run()

if __name__ == "__main__":
    main() 