# BladeFighters - Puzzle Combat Game

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Pygame](https://img.shields.io/badge/Pygame-2.0+-green.svg)](https://pygame.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A sophisticated puzzle combat game featuring Tetris-style gameplay with advanced attack mechanics, state management, and modular architecture.

## 🎮 Overview

BladeFighters combines classic puzzle gameplay with innovative combat mechanics. Players clear blocks to generate attacks against opponents, using strategic thinking and quick reflexes to dominate the battlefield.

### Latest Release (v2.0.0)
- **🎬 Animated Attack Delivery**: Smooth, paced attack spawning with no teleportation
- **🔒 Input Lock Windows**: Synchronized input locking during attack animations
- **📐 Resolution Independence**: Consistent grid coordinates across all screen sizes
- **🎯 Paced Sliding**: Smooth horizontal block sliding during cluster breaks
- **🧪 Comprehensive Testing**: 200+ tests covering core mechanics and edge cases
- **📚 Complete Documentation**: Full API docs, integration guides, and developer references

### Key Features

- **🎯 Advanced Combat System**: Mathematical attack calculations with cluster strikes and garbage blocks
- **🏗️ Modular Architecture**: Clean, maintainable codebase with 15+ specialized modules
- **🎵 Audio Integration**: Comprehensive audio system with state management
- **📱 Responsive UI**: Scaled interface system for multiple screen sizes
- **🎲 AI Opponents**: Multiple AI difficulty levels with heuristic and random strategies
- **📹 Replay System**: Record and replay gameplay sessions
- **🔧 Test Mode**: Comprehensive testing and debugging tools
- **📖 Story Mode**: Immersive narrative experience
- **⚙️ Settings Management**: Unified configuration system

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- Pygame 2.0 or higher
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd BladeFighters-cluster-fix-working-copy-6
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements-dev.txt
   ```

4. **Run the game**
   ```bash
   python main.py
   ```

### Alternative Launch Methods

- **macOS/Linux**: `./run_mac.sh`
- **Windows**: `run_bladefighters.bat`
- **Direct**: `python game_client.py`

## 🎮 Game Controls

### Basic Controls
- **Arrow Keys**: Move pieces left/right/down
- **Z/X**: Rotate pieces
- **Space**: Hard drop
- **C**: Hold piece
- **P**: Pause

### Advanced Controls
- **F9**: Input tuner overlay (tune input feel)
- **F10**: Debug mode
- **F11**: Fullscreen toggle

### Menu Navigation
- **Arrow Keys**: Navigate menus
- **Enter**: Select option
- **Escape**: Back/Cancel

## 🏗️ Architecture

BladeFighters uses a modular architecture with clear separation of concerns:

```
BladeFighters/
├── core/                    # Core game engine
├── modules/                 # Specialized modules
│   ├── attack_module/       # Combat system
│   ├── audio_module/        # Audio management
│   ├── game_state_module/   # State management
│   ├── input_module/        # Input handling
│   ├── menu_module/         # UI systems
│   ├── screen_module/       # Screen management
│   ├── settings_module/     # Configuration
│   ├── testmode_module/     # Testing tools
│   └── ...                  # Additional modules
├── puzzleassets/            # Game assets
├── sounds/                  # Audio files
├── contracts/               # Interface contracts
└── tests/                   # Test suites
```

For detailed architecture information, see [ARCHITECTURE.md](ARCHITECTURE.md).

## 📚 Documentation

### 📖 [Documentation Index](DOCUMENTATION_SPECIALIST_REPORT.md)
Complete guide to all project documentation and knowledge management.

### 🏗️ [System Architecture](ARCHITECTURE.md)
Technical architecture overview including time management, input handling, and system integration.

### 📋 Progress Reports
- [Audio Integration Completion](AUDIO_INTEGRATION_COMPLETION_REPORT.md)
- [Error Handling Refactor Progress](ERROR_HANDLING_REFACTOR_PROGRESS.md)

### 🎯 Module Documentation
- [Attack Module](modules/attack_module/README.md) - Combat system
- [Screen Module](modules/screen_module/README.md) - Screen management
- [Audio Module](modules/audio_module/AUDIO_STATE_INTEGRATION_GUIDE.md) - Audio integration
- [Game State Module](modules/game_state_module/MIGRATION_GUIDE.md) - State management
- [Settings Module](modules/settings_module/MIGRATION_GUIDE.md) - Configuration
- [Input Module](modules/input_module/MIGRATION_GUIDE.md) - Input handling

## 🧪 Testing

### Run All Tests
```bash
python -m pytest
```

### Run Specific Test Suites
```bash
# Attack module tests
python -m pytest modules/attack_module/tests/

# Screen module tests
python -m pytest modules/screen_module/tests/

# Audio module tests
python -m pytest modules/audio_module/tests/
```

### Test Coverage
```bash
python -m pytest --cov=modules --cov-report=html
```

## 🔧 Development

### Code Style
- **Line Length**: 100 characters
- **Formatter**: Black
- **Linter**: Ruff
- **Type Checking**: MyPy

### Pre-commit Hooks
```bash
pre-commit install
pre-commit run --all-files
```

### Development Tools
- **Asset Packer**: `python tools/packer/pack.py`
- **Asset Preflight**: `python modules/asset_module/preflight.py`
- **Repro Token**: `python tools/repro_token.py`

## 🎯 Key Systems

### Combat System
The attack module implements sophisticated combat mechanics:
- **Garbage Blocks**: Standard block flooding
- **Cluster Strikes**: Special attack patterns (2x2, 3x3, 4x4)
- **Chain Mechanics**: Position-based combo levels
- **Attack Queuing**: Proper timing and delivery

### State Management
Unified state management across all modules:
- **Game State Manager**: Central state coordination
- **Audio State**: Volume, music, and SFX management
- **Screen State**: Screen transitions and history
- **Input State**: Input processing and validation

### Audio System
Comprehensive audio integration:
- **Volume Control**: Master, music, and SFX volumes
- **Music Management**: Playlist and playback control
- **SFX System**: Sound effects with spatial audio
- **State Persistence**: Settings and preferences

## 🚨 Troubleshooting

### Common Issues

**Game won't start**
- Check Python version (3.11+ required)
- Verify Pygame installation
- Check virtual environment activation

**Audio issues**
- Verify audio files in `sounds/` directory
- Check system audio settings
- Review audio module logs

**Performance problems**
- Check frame rate with F10 debug mode
- Review asset preflight results
- Monitor memory usage

### Getting Help
1. Check the [troubleshooting guide](docs/TROUBLESHOOTING.md)
2. Review relevant module documentation
3. Check test results for your specific issue
4. Create an issue with detailed error information

## 🤝 Contributing

### Development Workflow
1. **Fork the repository**
2. **Create a feature branch**
3. **Follow code style guidelines**
4. **Write tests for new features**
5. **Update documentation**
6. **Submit a pull request**

### Module Development
- Follow the established module structure
- Use the module documentation template
- Implement comprehensive testing
- Update integration guides

### Documentation Standards
- Use clear, concise language
- Include code examples
- Provide migration guides for changes
- Update the documentation index

## 📊 Project Status

### ✅ Completed
- Core game engine
- Attack system implementation
- Audio system integration
- Screen management
- Error handling refactor
- State management system

### 🚧 In Progress
- Module documentation standardization
- User documentation creation
- Performance optimization
- Advanced AI features

### 📋 Planned
- Mobile platform support
- Multiplayer networking
- Advanced visual effects
- Additional game modes

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Pygame Community**: For the excellent game development framework
- **Python Community**: For the robust programming language
- **Open Source Contributors**: For inspiration and best practices

## 📞 Support

- **Documentation**: [Documentation Index](DOCUMENTATION_SPECIALIST_REPORT.md)
- **Issues**: Create an issue on GitHub
- **Discussions**: Use GitHub Discussions for questions

---

**BladeFighters** - Where puzzle meets combat! ⚔️🎮

*Built with ❤️ and Python* 