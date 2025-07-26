#!/usr/bin/env python3
"""
Debug script to see what's available in rust_ui module
"""

import sys
import os

# Add the rust_ui target directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'rust_ui', 'target', 'debug'))

try:
    import rust_ui
    print("✅ Successfully imported rust_ui module!")
    
    # List all attributes
    print("\n📋 Available attributes in rust_ui:")
    for attr in dir(rust_ui):
        if not attr.startswith('_'):
            print(f"  - {attr}")
    
    # Try to call a function if it exists
    if hasattr(rust_ui, 'load_settings'):
        print("\n🔧 Testing load_settings...")
        result = rust_ui.load_settings()
        print(f"Result: {result}")
    else:
        print("\n❌ load_settings function not found")
        
except Exception as e:
    print(f"❌ Debug failed: {e}")
    import traceback
    traceback.print_exc() 