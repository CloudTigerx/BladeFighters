#!/usr/bin/env python3
"""
Simple test for Rust UI module
"""

import sys
import os

# Add the rust_ui target directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'rust_ui', 'target', 'debug'))

try:
    import rust_ui
    print("✅ Module imported successfully!")
    
    # Try to access the module directly
    print(f"Module type: {type(rust_ui)}")
    print(f"Module name: {rust_ui.__name__}")
    
    # Try to call any function
    try:
        result = rust_ui.load_settings()
        print(f"✅ load_settings worked: {result}")
    except AttributeError:
        print("❌ load_settings not found")
    except Exception as e:
        print(f"❌ load_settings failed: {e}")
        
except Exception as e:
    print(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc() 