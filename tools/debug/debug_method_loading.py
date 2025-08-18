#!/usr/bin/env python3
"""
Debug Method Loading
==================

Debug script to understand why transformation methods aren't being loaded.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def debug_method_loading():
    """Debug why methods aren't being loaded"""
    print("🔍 DEBUGGING METHOD LOADING...")
    
    try:
        # Import the module
        import modules.testmode_module.test_mode
        
        # Get the class
        TestModeRefactored = modules.testmode_module.test_mode.TestModeRefactored
        
        print(f"✅ Successfully imported TestModeRefactored")
        print(f"✅ Class has {len(dir(TestModeRefactored))} methods/attributes")
        
        # List all methods
        all_methods = [m for m in dir(TestModeRefactored) if not m.startswith('_') or m.startswith('__')]
        print(f"✅ Public methods: {len(all_methods)}")
        
        # List all private methods
        private_methods = [m for m in dir(TestModeRefactored) if m.startswith('_') and not m.startswith('__')]
        print(f"✅ Private methods: {len(private_methods)}")
        
        # Check for transformation-related methods
        transformation_methods = [m for m in private_methods if 'garbage' in m.lower() or 'transform' in m.lower()]
        print(f"✅ Transformation methods: {transformation_methods}")
        
        # Check the source file directly
        print("\n🔍 CHECKING SOURCE FILE...")
        with open("modules/testmode_module/test_mode.py", "r") as f:
            content = f.read()
        
        # Count method definitions
        method_count = content.count("def _process_garbage_transformations")
        print(f"✅ _process_garbage_transformations definitions: {method_count}")
        
        method_count = content.count("def _track_garbage_landings")
        print(f"✅ _track_garbage_landings definitions: {method_count}")
        
        method_count = content.count("def _apply_garbage_finalization")
        print(f"✅ _apply_garbage_finalization definitions: {method_count}")
        
        # Check if methods are in the class
        class_content = content[content.find("class TestModeRefactored"):]
        method_in_class = "_process_garbage_transformations" in class_content
        print(f"✅ Method in class content: {method_in_class}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_method_loading()
