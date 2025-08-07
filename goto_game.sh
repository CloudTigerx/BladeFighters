#!/bin/bash

echo "🎮 Navigating to BladeFighters..."
echo "=================================="

# Define the game directory
GAME_DIR="$HOME/Downloads/BladeFighters-cluster-fix-working"

# Check if the directory exists
if [ ! -d "$GAME_DIR" ]; then
    echo "❌ Game directory not found: $GAME_DIR"
    echo "   Please make sure the game is in your Downloads folder"
    exit 1
fi

# Change to the game directory
cd "$GAME_DIR"

echo "✅ Now in game directory: $(pwd)"
echo ""
echo "🚀 Available commands:"
echo "  ./run_mac.sh      - Run the game"
echo "  ./setup_mac.sh    - Install dependencies"
echo "  ./navigate.sh     - Show navigation help"
echo "  ./open_in_finder.sh - Open in Finder"
echo ""

# Show current files
echo "📁 Game files:"
ls -la | grep -E "\.(py|sh|txt|md)$" | head -10
echo ""

echo "🎮 Ready to play! Use './run_mac.sh' to start the game." 