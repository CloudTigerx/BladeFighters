#!/bin/bash

echo "🎮 Setting up BladeFighters for Mac..."
echo "======================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    echo "   You can download it from https://www.python.org/downloads/"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3 first."
    exit 1
fi

echo "✅ pip3 found: $(pip3 --version)"

# Upgrade pip to latest version
echo "📦 Upgrading pip..."
python3 -m pip install --upgrade pip

# Install pygame
echo "🎮 Installing pygame..."
python3 -m pip install pygame

# Verify pygame installation
echo "🔍 Verifying pygame installation..."
python3 -c "import pygame; print(f'✅ pygame {pygame.version.ver} installed successfully')"

echo ""
echo "🎉 Setup complete! You can now run the game with:"
echo "   python3 main.py"
echo ""
echo "Or use the run script:"
echo "   ./run_mac.sh" 