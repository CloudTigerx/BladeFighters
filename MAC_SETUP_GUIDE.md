# 🍎 Complete Mac Setup Guide for BladeFighters

## 🚀 Quick Start

### Option 1: One-Command Setup (Recommended)
```bash
cd ~/Downloads/BladeFighters-cluster-fix-working && ./setup_mac.sh && ./run_mac.sh
```

### Option 2: Step by Step
```bash
# 1. Go to game directory
cd ~/Downloads/BladeFighters-cluster-fix-working

# 2. Install dependencies
./setup_mac.sh

# 3. Run the game
./run_mac.sh
```

## 📁 Directory Navigation

### The Problem
Sometimes the terminal session changes and you end up in the wrong directory. The error:
```
can't open file '/Users/justinearp/main.py': [Errno 2] No such file or directory
```
Means you're in your home directory (`~`) instead of the game directory.

### The Solution

#### Method 1: Use the Navigation Script
```bash
# From anywhere, run:
./goto_game.sh
```

#### Method 2: Manual Navigation
```bash
# Go to your game directory
cd ~/Downloads/BladeFighters-cluster-fix-working

# Verify you're in the right place
ls main.py
```

#### Method 3: Use the Improved Run Script
The updated `run_mac.sh` automatically finds the correct directory.

## 🛠️ Available Scripts

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `./setup_mac.sh` | Install dependencies | First time setup |
| `./run_mac.sh` | Run the game | Every time you want to play |
| `./goto_game.sh` | Navigate to game directory | When you're lost |
| `./navigate.sh` | Show navigation help | When you need help |
| `./open_in_finder.sh` | Open folder in Finder | Visual navigation |

## 🔧 Troubleshooting

### "No such file or directory" Error
**Problem**: Terminal is in wrong directory
**Solution**: 
```bash
cd ~/Downloads/BladeFighters-cluster-fix-working
./run_mac.sh
```

### "pygame not installed" Error
**Problem**: Dependencies missing
**Solution**:
```bash
./setup_mac.sh
```

### "Permission denied" Error
**Problem**: Scripts not executable
**Solution**:
```bash
chmod +x *.sh
```

### Game won't start
**Problem**: Various issues
**Solution**:
```bash
# Check Python
python3 --version

# Check pygame
python3 -c "import pygame; print('pygame OK')"

# Check game files
ls -la main.py game_client.py
```

## 📂 File Structure

```
BladeFighters-cluster-fix-working/
├── main.py                    # Main game file
├── game_client.py            # Core game logic
├── requirements.txt          # Dependencies
├── setup_mac.sh             # Mac setup script
├── run_mac.sh               # Mac run script
├── goto_game.sh             # Navigation helper
├── navigate.sh              # Navigation guide
├── open_in_finder.sh        # Finder opener
├── puzzleassets/            # Game images
├── sounds/                  # Audio files
├── modules/                 # Game modules
└── core/                    # Core systems
```

## 🎮 Game Controls

- **Arrow Keys**: Navigate menus
- **Space**: Select/Action
- **P**: Pause/Play music
- **[ ]**: Previous/Next song
- **Escape**: Back/Exit

## 💡 Pro Tips

1. **Always start from the game directory**: `cd ~/Downloads/BladeFighters-cluster-fix-working`
2. **Use the scripts**: They handle directory issues automatically
3. **Check the terminal prompt**: It should show `BladeFighters-cluster-fix-working`
4. **Use Finder**: `./open_in_finder.sh` for visual navigation
5. **Keep Terminal open**: Don't close it while the game is running

## 🆘 Getting Help

If you're stuck:
1. Run `./navigate.sh` for navigation help
2. Run `./goto_game.sh` to get back to the game directory
3. Check this guide for troubleshooting steps
4. Make sure you're in the right directory: `pwd` should show the game path

## 🎯 Success Indicators

✅ **Setup Complete When**:
- `python3 --version` shows Python 3.x
- `python3 -c "import pygame"` works without errors
- `./run_mac.sh` starts the game
- Game window opens and you can navigate menus

�� **Ready to Play!** 