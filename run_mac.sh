#!/bin/bash

echo "🎮 Launching BladeFighters..."
echo "=============================="

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "📍 Game directory: $SCRIPT_DIR"

# Change to the game directory
cd "$SCRIPT_DIR"

# Check if main.py exists
if [ ! -f "main.py" ]; then
    echo "❌ main.py not found in: $SCRIPT_DIR"
    echo "   Current directory: $(pwd)"
    echo "   Files in current directory:"
    ls -la
    exit 1
fi

# Check if pygame is installed
if ! python3 -c "import pygame" 2>/dev/null; then
    echo "❌ pygame is not installed. Please run setup first:"
    echo "   ./setup_mac.sh"
    exit 1
fi

# Check if user wants to configure display settings
if [ "$1" = "--configure-display" ]; then
    echo "🔧 Running display configuration helper..."
    python3 mac_display_helper.py
    exit 0
fi

# Show quick help
echo "💡 Tip: Run './run_mac.sh --configure-display' to optimize for your display"

# Run the game
echo "🚀 Starting BladeFighters..."
python3 main.py 