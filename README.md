# Blade Fighters - Puzzle Fighting Game

A complex puzzle fighting game with real-time combat mechanics, currently undergoing architectural refactoring from monolithic to modular design.

## 🎮 Game Overview

Blade Fighters is a puzzle-based fighting game where players compete by solving puzzles to generate attacks against their opponents. The game features:

- **Real-time puzzle solving** with falling block mechanics
- **Attack system** that generates offensive moves based on puzzle performance
- **Multiple game modes** including test mode, story mode, and quickplay
- **Audio system** with music and sound effects
- **Menu system** with settings and customization options

## 🎮 Core Game Files

- **main.py** - Game entry point
- **game_client.py** - Main game client and state management
- **core/puzzle_module.py** - Core puzzle game engine
- **core/input_handler.py** - Input processing and controls
- **core/piece_movement.py** - Piece movement and collision detection
- **core/basic_physics.py** - Gravity and physics simulation
- **core/asset_loader.py** - Asset loading and management
- **modules/attack_module/** - Modular attack system (replaces attack_system.py)

## 🏗️ Current Architecture

### Status: Monolithic (Under Refactoring)
The codebase is currently a monolithic structure with tight coupling between components:

- **game_client.py** (1632 lines) - Main game loop and coordination
- **puzzle_module.py** - Core puzzle engine
- **attack_system.py** - Attack generation and management
- **audio_system.py** - Audio playback and management
- **menu_system.py** - Menu interface and navigation
- **settings_system.py** - Game settings and configuration
- **puzzle_renderer.py** - Visual rendering of puzzle elements

### Known Issues (Resolved)
- ✅ Alpha value clamping (was 303, now clamped to 255)
- ✅ Screen shake attribute missing (fixed)
- ✅ Invalid color argument errors (resolved)

## 🚀 Refactoring Goals

### Target Architecture: Modular Design
Transform the monolithic codebase into a clean, modular architecture:

1. **Core Engine** - Extracted puzzle engine with clean interfaces
2. **Event System** - Decoupled communication between modules
3. **Plugin Architecture** - Swappable components (audio, rendering, etc.)
4. **Data Contracts** - Clear interfaces between modules
5. **Testing Infrastructure** - Comprehensive test coverage

### Refactoring Tools Created
- **dependency_analyzer.py** - Analyzes module dependencies and coupling
- **test_framework.py** - Comprehensive testing suite
- **session_manager.py** - Progress tracking and context management
- **REFACTORING_TRACKER.md** - Detailed progress tracking

## 🛠️ Development Setup

### Prerequisites
- Python 3.8+
- Pygame
- Git

### Installation
```bash
# Clone the repository
git clone https://github.com/CloudTigerx/BladeFighters.git
cd BladeFighters

# Install dependencies (when requirements.txt is created)
pip install -r requirements.txt
```

### Running the Game
```bash
# Run the main game
python main.py

# Run in test mode (for development)
python main.py --test-mode
```

### Running Refactoring Tools
```bash
# Analyze dependencies
python dependency_analyzer.py

# Run tests
python test_framework.py

# Start session management
python session_manager.py
```

## 📁 Project Structure

```
BladeFighters-modular/
├── main.py                 # Entry point
├── game_client.py          # Main game client
├── core/                   # Core game engine
│   ├── puzzle_module.py    # Puzzle engine
│   ├── input_handler.py    # Input processing
│   ├── piece_movement.py   # Piece movement logic
│   ├── basic_physics.py    # Physics simulation
│   ├── asset_loader.py     # Asset management
│   └── Animations/         # Animation system
├── modules/                # Modular systems
│   ├── attack_module/      # 🆕 Modular attack system
│   │   ├── attack_manager.py
│   │   ├── attack_calculator.py
│   │   ├── payload_tracker.py
│   │   └── data_structures.py
│   ├── audio_module/       # Audio system
│   ├── menu_module/        # Menu interface
│   ├── screen_module/      # Screen management
│   ├── story_module/       # Story mode
│   └── testmode_module/    # Test mode
├── puzzleassets/           # Game assets
│   ├── magic/              # Magic effects
│   ├── fonts/              # Font files
│   ├── Enemys/             # Enemy sprites
│   └── sounds/             # Audio files
├── stories/                # Story content
├── sounds/                 # Sound effects and music
├── contracts/              # Interface contracts
├── utils/                  # Utility tools
└── docs/                   # Documentation
```

## 🔧 Refactoring Process

### Phase 1: Foundation & Analysis ✅
- [x] Create architecture documentation
- [x] Identify core dependencies
- [x] Set up tracking system
- [ ] Create dependency graph
- [ ] Define module boundaries
- [ ] Set up testing framework

### Phase 2: Core Engine Extraction
- [ ] Extract puzzle engine core
- [ ] Create clean interfaces
- [ ] Implement event system
- [ ] Add dependency injection
- [ ] Create data contracts

### Phase 3: Module Separation
- [ ] Separate attack system
- [ ] Modularize rendering
- [ ] Extract audio system
- [ ] Separate menu system
- [ ] Extract settings system

### Phase 4: Integration & Testing
- [ ] Reintegrate modules
- [ ] Comprehensive testing
- [ ] Performance optimization
- [ ] Documentation

## 🧪 Testing

The project includes a comprehensive testing framework:

```bash
# Run all tests
python test_framework.py

# Run specific test categories
python test_framework.py --category puzzle
python test_framework.py --category attack
python test_framework.py --category integration
```

## 📊 Progress Tracking

- **Current Phase**: Foundation & Analysis
- **Progress**: 0% - Planning Phase
- **Next Milestone**: Dependency analysis and module boundary definition

See `REFACTORING_TRACKER.md` for detailed progress information.

## 🤝 Contributing

This project is currently in active refactoring. The focus is on:

1. **Architectural improvements** - Modularization and clean design
2. **Code quality** - Testing, documentation, and maintainability
3. **Performance optimization** - Maintaining game performance during refactoring

## 📝 License

[Add your license information here]

## 🐛 Known Issues

- Attack system tightly coupled to grid and game state
- High cyclomatic complexity in main game client
- Limited test coverage
- Monolithic architecture making maintenance difficult

## 🎯 Roadmap

1. **Short term** (1-2 weeks): Complete dependency analysis and core engine extraction
2. **Medium term** (1-2 months): Complete module separation and integration
3. **Long term** (3+ months): Performance optimization and production readiness

---

**Note**: This project is actively being refactored. The current codebase is functional but monolithic. The refactoring process aims to transform it into a maintainable, modular architecture while preserving all existing functionality. 