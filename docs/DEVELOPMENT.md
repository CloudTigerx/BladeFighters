# Development Setup Guide

This guide will help you set up a complete development environment for the BladeFighters project.

## 🎯 Prerequisites

### Required Software

- **Python 3.11 or higher** - [Download Python](https://python.org/downloads/)
- **Git** - [Download Git](https://git-scm.com/downloads)
- **Virtual Environment Tool** - Python's built-in `venv` module

### Recommended Software

- **VS Code** - [Download VS Code](https://code.visualstudio.com/)
  - Python extension
  - Git extension
  - Markdown extension
- **PyCharm** - [Download PyCharm](https://www.jetbrains.com/pycharm/)
- **Terminal/Command Prompt** - Your system's default terminal

### System Requirements

- **Operating System**: Windows 10+, macOS 10.15+, or Linux
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 2GB free space
- **Graphics**: Any modern graphics card (for Pygame)

## 🚀 Quick Setup

### 1. Clone the Repository

```bash
# Clone the repository
git clone <repository-url>
cd BladeFighters-cluster-fix-working-copy-6

# Verify you're in the right directory
ls
# Should show: main.py, game_client.py, modules/, etc.
```

### 2. Set Up Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate

# On macOS/Linux:
source .venv/bin/activate

# Verify activation (should show .venv in prompt)
which python  # Should point to .venv/bin/python
```

### 3. Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install development dependencies
pip install -r requirements-dev.txt

# Verify installation
python -c "import pygame; print('Pygame version:', pygame.version.ver)"
```

### 4. Run the Game

```bash
# Test that everything works
python main.py
```

You should see the BladeFighters game window appear!

## 🔧 IDE Setup

### VS Code Configuration

1. **Install Extensions**
   ```bash
   # Install recommended extensions
   code --install-extension ms-python.python
   code --install-extension ms-python.black-formatter
   code --install-extension ms-python.ruff
   code --install-extension yzhang.markdown-all-in-one
   ```

2. **Configure Python Interpreter**
   - Open VS Code in the project directory
   - Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (macOS)
   - Type "Python: Select Interpreter"
   - Choose the interpreter from `.venv/bin/python`

3. **Workspace Settings**
   Create `.vscode/settings.json`:
   ```json
   {
     "python.defaultInterpreterPath": "./.venv/bin/python",
     "python.formatting.provider": "black",
     "python.linting.enabled": true,
     "python.linting.ruffEnabled": true,
     "editor.formatOnSave": true,
     "editor.codeActionsOnSave": {
       "source.organizeImports": true
     }
   }
   ```

### PyCharm Configuration

1. **Open Project**
   - Open PyCharm
   - Select "Open" and choose the project directory

2. **Configure Interpreter**
   - Go to `File > Settings > Project > Python Interpreter`
   - Click the gear icon and select "Add"
   - Choose "Existing Environment"
   - Select `.venv/bin/python`

3. **Configure Code Style**
   - Go to `File > Settings > Editor > Code Style > Python`
   - Set line length to 100
   - Enable "Use tab character" if preferred

## 🧪 Testing Setup

### Install Testing Tools

```bash
# Install pytest and coverage tools
pip install pytest pytest-cov pytest-mock

# Install additional testing utilities
pip install black ruff mypy
```

### Run Tests

```bash
# Run all tests
python -m pytest

# Run tests with coverage
python -m pytest --cov=modules --cov-report=html

# Run specific module tests
python -m pytest modules/attack_module/tests/

# Run tests with verbose output
python -m pytest -v
```

### Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Install git hooks
pre-commit install

# Run hooks on all files
pre-commit run --all-files
```

## 🔍 Code Quality Tools

### Black (Code Formatter)

```bash
# Format all Python files
black .

# Check formatting without changing files
black --check .
```

### Ruff (Linter)

```bash
# Lint all Python files
ruff check .

# Fix auto-fixable issues
ruff check --fix .
```

### MyPy (Type Checker)

```bash
# Type check all Python files
mypy .

# Type check specific modules
mypy modules/attack_module/
```

## 🎮 Game Development Tools

### Asset Management

```bash
# Run asset preflight check
python modules/asset_module/preflight.py

# Pack sprites (if you have sprite assets)
python tools/packer/pack.py --in content/sprites/raw --out content/sprites/build
```

### Debug Tools

```bash
# Run with debug mode
python main.py --debug

# Run with specific seed
python main.py --seed 12345

# Run with replay
python main.py --replay path/to/replay.json
```

### Performance Profiling

```bash
# Install profiling tools
pip install cProfile-Viewer

# Profile the game
python -m cProfile -o profile.stats main.py

# View profile results
python -c "import pstats; p = pstats.Stats('profile.stats'); p.sort_stats('cumulative').print_stats(20)"
```

## 📁 Project Structure

### Key Directories

```
BladeFighters/
├── core/                    # Core game engine
│   ├── Animations/         # Animation system
│   ├── gfx/               # Graphics and rendering
│   ├── scaling/           # UI scaling system
│   └── tests/             # Core tests
├── modules/                # Specialized modules
│   ├── attack_module/      # Combat system
│   ├── audio_module/       # Audio management
│   ├── game_state_module/  # State management
│   ├── input_module/       # Input handling
│   ├── menu_module/        # UI systems
│   ├── screen_module/      # Screen management
│   ├── settings_module/    # Configuration
│   ├── testmode_module/    # Testing tools
│   └── ...                 # Additional modules
├── puzzleassets/           # Game assets
├── sounds/                 # Audio files
├── contracts/              # Interface contracts
├── tests/                  # Test suites
├── tools/                  # Development tools
└── utils/                  # Utility functions
```

### Important Files

- `main.py` - Game entry point
- `game_client.py` - Main game client
- `ARCHITECTURE.md` - System architecture
- `pyproject.toml` - Project configuration
- `requirements-dev.txt` - Development dependencies

## 🔄 Development Workflow

### 1. Daily Development

```bash
# Start your day
git pull origin main
source .venv/bin/activate

# Make changes and test
python main.py

# Run tests before committing
python -m pytest

# Format and lint code
black .
ruff check --fix .
```

### 2. Feature Development

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes
# ... edit files ...

# Test your changes
python -m pytest modules/your_module/tests/

# Commit with good message
git add .
git commit -m "feat: add new feature description"

# Push and create pull request
git push origin feature/your-feature-name
```

### 3. Bug Fixing

```bash
# Create bug fix branch
git checkout -b fix/bug-description

# Reproduce the bug
python main.py

# Fix the bug
# ... edit files ...

# Test the fix
python -m pytest

# Commit the fix
git add .
git commit -m "fix: description of the fix"

# Push and create pull request
git push origin fix/bug-description
```

## 🚨 Common Issues

### Python Version Issues

**Problem**: "Python version not found" or "pip not found"
**Solution**:
```bash
# Check Python version
python --version

# If wrong version, install Python 3.11+
# On macOS with Homebrew:
brew install python@3.11

# On Ubuntu/Debian:
sudo apt update
sudo apt install python3.11 python3.11-venv
```

### Virtual Environment Issues

**Problem**: "Module not found" errors
**Solution**:
```bash
# Ensure virtual environment is activated
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Reinstall dependencies
pip install -r requirements-dev.txt
```

### Pygame Issues

**Problem**: "pygame module not found"
**Solution**:
```bash
# Install pygame
pip install pygame

# On macOS, you might need:
brew install pkg-config sdl2 sdl2_image sdl2_mixer sdl2_ttf portmidi
```

### Import Issues

**Problem**: "ImportError: cannot import name X"
**Solution**:
```bash
# Check if you're in the right directory
pwd  # Should show project root

# Check Python path
python -c "import sys; print(sys.path)"

# Try running from project root
cd /path/to/BladeFighters
python main.py
```

## 📚 Learning Resources

### Project-Specific

- [Architecture Documentation](../ARCHITECTURE.md)
- [Module Documentation](../docs/README.md)
- [Code Style Guide](CODE_STYLE.md)

### Python Development

- [Python Official Documentation](https://docs.python.org/)
- [Pygame Documentation](https://pygame.org/docs/)
- [pytest Documentation](https://docs.pytest.org/)

### Game Development

- [Game Development Patterns](https://gameprogrammingpatterns.com/)
- [Clean Code Principles](https://clean-code-developer.com/)

## 🤝 Getting Help

### Before Asking for Help

1. **Check this guide** - Review this setup guide
2. **Check documentation** - Review project documentation
3. **Search issues** - Check existing GitHub issues
4. **Run tests** - Ensure tests pass locally

### When Asking for Help

Include the following information:

```bash
# System information
python --version
pip list
uname -a  # or systeminfo on Windows

# Error details
python main.py 2>&1 | tee error.log

# Test results
python -m pytest --tb=short
```

### Where to Get Help

- **GitHub Issues** - For bugs and feature requests
- **GitHub Discussions** - For questions and community support
- **Project Wiki** - For community-maintained documentation

## 🎯 Next Steps

After completing this setup:

1. **Run the game** - `python main.py`
2. **Explore the codebase** - Start with `main.py` and `game_client.py`
3. **Read the architecture** - Review `ARCHITECTURE.md`
4. **Pick a module** - Choose a module to work on
5. **Write tests** - Add tests for your changes
6. **Contribute** - Submit your first pull request!

---

**Happy coding!** 🎮⚔️

*This guide is maintained by the Documentation Specialist. If you find issues or have suggestions, please create an issue or contribute improvements.* 