#!/bin/bash

echo "🧭 BladeFighters Navigation Helper"
echo "=================================="
echo ""

# Show current location
echo "📍 Current location:"
pwd
echo ""

# Show available commands
echo "🚀 Quick Commands:"
echo "  ./run_mac.sh      - Run the game"
echo "  ./setup_mac.sh    - Install dependencies"
echo "  ls                - List files"
echo "  ls -la            - List files with details"
echo "  open .            - Open folder in Finder"
echo ""

# Show important files
echo "📁 Important Files:"
echo "  main.py           - Main game file"
echo "  game_client.py    - Core game logic"
echo "  requirements.txt  - Dependencies"
echo ""

# Show folders
echo "📂 Important Folders:"
echo "  puzzleassets/     - Game images and assets"
echo "  sounds/           - Audio files"
echo "  modules/          - Game modules"
echo "  core/             - Core game systems"
echo ""

# Show navigation shortcuts
echo "🔍 Navigation Shortcuts:"
echo "  cd ~/Downloads/BladeFighters-cluster-fix-working  - Go to game folder"
echo "  cd ~/Downloads                                    - Go to Downloads"
echo "  cd ~                                              - Go home"
echo "  pwd                                               - Show current location"
echo ""

# Show system info
echo "💻 System Info:"
echo "  Python: $(python3 --version)"
python3 -c "import pygame; print(f'  pygame: {pygame.version.ver}')" 2>/dev/null || echo "  pygame: Not installed"
echo ""

echo "🎮 Ready to develop! Use './run_mac.sh' to start the game." 