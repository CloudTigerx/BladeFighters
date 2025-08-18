#!/usr/bin/env python3
"""
Mac Display Helper for BladeFighters
This script helps users understand and configure their display settings for optimal gaming.
"""

import subprocess
import json
import sys
import os

def get_display_info():
    """Get detailed display information from macOS."""
    try:
        result = subprocess.run(['system_profiler', 'SPDisplaysDataType'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout
    except Exception as e:
        print(f"Error getting display info: {e}")
    return None

def parse_display_info(info_text):
    """Parse the display information to extract useful details."""
    displays = []
    current_display = {}
    
    for line in info_text.split('\n'):
        line = line.strip()
        if 'Display:' in line:
            if current_display:
                displays.append(current_display)
            current_display = {'name': line.split('Display:')[1].strip()}
        elif 'Resolution:' in line:
            resolution = line.split('Resolution:')[1].strip()
            current_display['resolution'] = resolution
        elif 'Pixel Depth:' in line:
            depth = line.split('Pixel Depth:')[1].strip()
            current_display['depth'] = depth
        elif 'Main Display:' in line:
            current_display['main'] = 'Yes' in line
    
    if current_display:
        displays.append(current_display)
    
    return displays

def get_current_scaling():
    """Get current display scaling settings."""
    try:
        result = subprocess.run(['defaults', 'read', '-g', 'AppleDisplayScaleFactor'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            return float(result.stdout.strip())
    except:
        pass
    
    # Try alternative method
    try:
        result = subprocess.run(['defaults', 'read', 'com.apple.dock', 'tilesize'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            tile_size = int(result.stdout.strip())
            # Rough estimation of scaling based on dock size
            if tile_size > 100:
                return 2.0
            elif tile_size > 60:
                return 1.5
            else:
                return 1.0
    except:
        pass
    
    return 1.0

def recommend_settings(displays):
    """Recommend optimal settings for BladeFighters."""
    print("🎮 BladeFighters Display Configuration Helper")
    print("=" * 50)
    
    for display in displays:
        if display.get('main'):
            print(f"\n📺 Main Display: {display.get('name', 'Unknown')}")
            print(f"   Native Resolution: {display.get('resolution', 'Unknown')}")
            print(f"   Color Depth: {display.get('depth', 'Unknown')}")
            
            # Parse resolution
            resolution = display.get('resolution', '')
            if 'x' in resolution:
                try:
                    width, height = resolution.split('x')
                    width = int(width.strip())
                    height = int(height.strip())
                    
                    print(f"\n💡 Recommendations:")
                    
                    if width >= 3000:  # High-DPI display
                        print(f"   ✅ Your display is high-DPI ({width}x{height})")
                        print(f"   🎯 Enable 'force_native_resolution' in game settings")
                        print(f"   📱 Set macOS scaling to 'Default' for best results")
                        print(f"   🖥️  Game will use native resolution: {width}x{height}")
                        
                        # Check current scaling
                        current_scale = get_current_scaling()
                        if current_scale > 1.0:
                            print(f"   ⚠️  Current macOS scaling: {current_scale}x")
                            print(f"   💡 Consider setting macOS to 'Default' scaling")
                        else:
                            print(f"   ✅ macOS scaling looks good")
                            
                    else:
                        print(f"   📺 Standard resolution display ({width}x{height})")
                        print(f"   🎯 Use default game settings")
                        print(f"   📱 macOS scaling should work fine")
                        
                except ValueError:
                    print(f"   ⚠️  Could not parse resolution: {resolution}")
            
            break

def update_game_settings(force_native=True):
    """Update the game settings file."""
    settings_file = "game_settings.json"
    
    if not os.path.exists(settings_file):
        print(f"❌ Settings file not found: {settings_file}")
        return False
    
    try:
        with open(settings_file, 'r') as f:
            settings = json.load(f)
        
        settings['force_native_resolution'] = force_native
        
        with open(settings_file, 'w') as f:
            json.dump(settings, f, indent=2)
        
        print(f"✅ Updated {settings_file}")
        print(f"   force_native_resolution: {force_native}")
        return True
        
    except Exception as e:
        print(f"❌ Error updating settings: {e}")
        return False

def main():
    """Main function."""
    print("🔍 Detecting your display configuration...")
    
    # Get display information
    display_info = get_display_info()
    if not display_info:
        print("❌ Could not get display information")
        return
    
    # Parse display info
    displays = parse_display_info(display_info)
    if not displays:
        print("❌ No displays found")
        return
    
    # Show recommendations
    recommend_settings(displays)
    
    # Ask user what they want to do
    print(f"\n🎮 What would you like to do?")
    print(f"   1. Enable native resolution mode (recommended for high-DPI)")
    print(f"   2. Use standard resolution mode")
    print(f"   3. Just show information (no changes)")
    
    try:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            if update_game_settings(force_native=True):
                print(f"\n✅ Native resolution mode enabled!")
                print(f"   Restart BladeFighters to apply changes")
        elif choice == "2":
            if update_game_settings(force_native=False):
                print(f"\n✅ Standard resolution mode enabled!")
                print(f"   Restart BladeFighters to apply changes")
        elif choice == "3":
            print(f"\nℹ️  No changes made")
        else:
            print(f"\n❌ Invalid choice")
            
    except KeyboardInterrupt:
        print(f"\n\n👋 Goodbye!")

if __name__ == "__main__":
    main()
