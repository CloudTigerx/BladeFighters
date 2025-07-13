# Blade Fighters Game Overview

## Game Architecture

The Blade Fighters game is built with Python using Pygame for rendering. It's a puzzle battle game where players match colored blocks while sending attacks to opponents.

### Core Components

- **Game Client** (`game_client.py`): Main entry point and controller
- **Puzzle Engine** (`puzzle_module.py`): Core puzzle game mechanics
- **Puzzle Renderer** (`puzzle_renderer.py`): Visualization of puzzle elements
- **Menu System** (`menu_system.py`): UI navigation and menu screens
- **Attack System** (`attack_system.py`): Combat mechanics
- **Audio System** (`audio_system.py`): Sound effects and music playback

### Game Flow

1. `main.py` initializes the game client
2. `run_modular.bat` launches the game via `main.py`
3. Game client manages screens (menu, settings, game)
4. Puzzle gameplay occurs through the PuzzleEngine class

## Puzzle Mechanics (Based on Actual Implementation)

The puzzle component operates as follows:

- Players control pairs of colored blocks (main piece + attached piece)
- Blocks fall from the top of a 6×15 grid
- When blocks are placed, they don't disappear immediately
- The game searches for "clusters" - connected blocks of the same color
- When a cluster forms, the blocks break and send attacks to the opponent
- Chain reactions occur when breaking blocks cause other blocks to fall and form new clusters
- "Breaker" blocks have special properties that affect nearby blocks
- Gravity is applied after blocks break, causing blocks to fall into empty spaces

### Block Types

- **Regular blocks**: Red, blue, green, yellow
- **Breaker blocks**: Special versions of the regular colors that can trigger chain reactions
- **Garbage blocks**: Grey blocks sent by opponents to interfere with gameplay
- **Strike blocks**: Special attack blocks that appear as a 1x4 vertical column with distinctive visuals

## Strike Mechanics

Strikes are a specialized attack type that functions differently from regular garbage blocks:

### Strike Generation
- Created when a 2x2 cluster of the same color blocks is broken **without a combo** (combo multiplier ≤ 1)
- Each 2x2 cluster break generates one strike attack of the same color as the broken blocks
- Strike attacks enter the opponent's attack queue and are processed when attacks are delivered

### Strike Placement
- Strikes appear as 1x4 vertical columns ("strike_1x4") in the opponent's grid
- They follow the same column placement pattern as garbage blocks (2,3,4,5,6,1)
- Unlike garbage blocks, strikes occupy multiple vertical positions simultaneously
- Visually distinct from regular blocks with a special sprite (puzzleassets/strikes/1x4.png)

### Strike Transformation
- Strikes remain active for half the time of regular garbage blocks (1.6 seconds vs 3.2 seconds)
- After this timer expires, they transform into colored garbage blocks matching their original color
- Transformation occurs through the process_strike_to_garbage_transformation method
- Once transformed, they behave like regular garbage blocks with the standard transformation timer

### Strike Visual Effects
- When strikes land on the opponent's grid, they should create distinctive spark/electric effects
- Strike blocks are visually represented with a special sprite that makes them stand out
- If the sprite is unavailable, a fallback orange color with a distinctive crossed pattern is used
- Yellow spark particles are generated when strikes first appear on the grid

### Strategic Impact
- Strikes provide a faster way to attack opponents compared to regular garbage blocks
- They occupy multiple rows at once, creating more disruption to the opponent's game
- The distinctive visual appearance serves as a warning to the opponent
- Their faster transformation time creates urgency for the opponent to deal with them

## Detailed Chain Reaction System

The chain reaction system is implemented as a state machine with the following states:
1. **Idle**: Looking for breakers to activate
2. **Breaking**: Animation when blocks are being destroyed 
3. **Applying Gravity**: Moving blocks down to fill gaps
4. **Waiting for Gravity**: Pause after gravity is applied

When blocks form clusters:
- Chain counter tracks consecutive reactions
- Higher chain counts produce more powerful attacks
- Animations highlight active clusters
- The system automatically detects and processes new clusters that form

## Battle System Details

The battle system works through:

- **Attack Generation**: Breaking blocks generates garbage blocks to send to opponents
- **Combo System**: Chain reactions multiply attack power
- **Attack Queue**: Attacks are stored until they can be processed
- **Column Targeting**: Attacks target specific columns in a pattern (2,3,4,5,6,1)
- **Garbage Blocks**: Grey blocks that obstruct gameplay
- **Transformation Timer**: Garbage blocks transform after 3.2 seconds

### Attack Calculation
- Base garbage blocks = number of broken blocks ÷ 2
- Cluster bonus: +1 garbage block
- Chain multiplier: Garbage blocks × chain count
- AI difficulty scaling: Higher difficulties generate extra attacks

## Game Controls (Directly from Code)

### Menu Navigation:
- **Mouse**: Click on buttons to navigate menus
- **Escape**: Return to previous menu

### Puzzle Game Controls:
- **Left/Right Arrow**: Move current piece horizontally
- **Up/Down Arrow**: Rotate the attached piece (counter-clockwise/clockwise)
- **Spacebar**: Accelerate piece falling

## AI System

The AI opponent has these characteristics:
- Controlled by `PuzzleAI` class in TestMode
- Difficulty levels from 1-10 affect:
  - Attack strength
  - Movement frequency
  - Decision making
- Different "styles" of play:
  - Water (blue attacks)
  - Fire (red attacks)
  - Earth (green attacks)
  - Lightning (yellow attacks)

## UI Components

- Main menu with particle effects
- Settings menu for resolution control
- Game screen with puzzle grid
- Story display system for narrative content
- Custom MP3 player integration

## Assets and Resources

- Puzzle pieces stored in `puzzleassets/` directory
- Sounds managed by audio system
- Story content in `stories/` directory

## Technical Implementation Notes

### Visual Effects System

The renderer implements several visual effects:
- Block falling animations
- Cluster highlight animations
- Breaking block effects
- Combo text display
- Background images and UI elements

### Code Organization

The original implementation is contained in these key files:
- `puzzle_module.py`: Core game mechanics
- `puzzle_renderer.py`: Visualization system
- `attack_system.py`: Battle mechanics

While a refactored version exists in the `puzzle_engine/` directory, the game currently uses the original implementation.

## Installation and Setup

1. **Requirements:**
   - Python (version 3.6 or higher recommended)
   - Pygame library (`pip install pygame`)

2. **Running the Game:**
   - Execute the `run_modular.bat` file to start the game
   - Alternatively, run `python main.py` from the command line

3. **Troubleshooting:**
   - If Python is not in your PATH, the batch file will display an error message
   - Make sure all asset directories (`puzzleassets/`, `sounds/`, etc.) are present

## Lessons and Story Mode

The game includes a lesson system (`blade_fighter_lessons.py`) that provides tutorials or guided gameplay experiences. Story content is loaded from the `stories/` directory and displayed through a dedicated story content viewer.

## MP3 Player Integration

A custom MP3 player (`mp3_player.py`) is integrated into the game, allowing for custom music playback during gameplay.

## Known Issues and Technical Debt

- The refactored puzzle engine in `puzzle_engine/` directory is incomplete or non-functional
- Debug log statements (e.g., "DEBUG: No blocks moved due to gravity") appear during gameplay
- Potential performance issues with particle effects or chain reaction processing
- **Attack System**: The attack system is currently in a bad state with issues in garbage block generation and physics. Development is moving in another direction for now, and the current implementation should be considered temporary.

## Future Development Considerations

If development resumes, consider:

1. Complete the refactoring of the puzzle engine for better maintenance
2. Implement additional attack types and battle mechanics
3. Enhance the AI system for more challenging opponents
4. Improve asset loading with fallback mechanisms
5. Add configuration options for gameplay parameters

## Testing Mode

The game includes a "TestMode" class in `game_client.py` specifically for testing AI puzzle battle mechanics. This provides a controlled environment for evaluating gameplay without going through the full game flow. 