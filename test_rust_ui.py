#!/usr/bin/env python3
"""
Test script for Rust UI integration
"""

import json
import sys
import os

# Add the rust_ui target directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'rust_ui', 'target', 'debug'))

try:
    import rust_ui
    print("✅ Successfully imported rust_ui module!")
    
    # Test loading default settings
    print("\n🔧 Testing load_settings...")
    default_settings = rust_ui.load_settings()
    print(f"Default settings: {default_settings}")
    
    # Test rendering settings
    print("\n🎨 Testing render_settings...")
    test_settings = {
        "resolution": (2560, 1440),
        "volume": 0.7,
        "controls": {
            "up": "UP",
            "down": "DOWN", 
            "left": "LEFT",
            "right": "RIGHT",
            "action": "SPACE"
        }
    }
    
    settings_json = json.dumps(test_settings)
    result = rust_ui.render_settings(settings_json)
    print(f"Render result: {result}")
    
    # Test saving settings
    print("\n💾 Testing save_settings...")
    rust_ui.save_settings(settings_json)
    print("Settings saved successfully!")
    
    print("\n🎉 All Rust UI tests passed!")
    
except ImportError as e:
    print(f"❌ Failed to import rust_ui: {e}")
    print("Make sure you've built the Rust library with 'cargo build'")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc() 