#!/usr/bin/env python3
"""
Test Class Structure
==================

Test to understand the class structure and why methods aren't being loaded.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_class_structure():
    """Test the class structure"""
    print("🔍 TESTING CLASS STRUCTURE...")
    
    try:
        # Import the module
        import modules.testmode_module.test_mode
        
        # Get the class
        TestModeRefactored = modules.testmode_module.test_mode.TestModeRefactored
        
        print(f"✅ Successfully imported TestModeRefactored")
        
        # List all methods and their types
        all_attrs = dir(TestModeRefactored)
        print(f"✅ Total attributes: {len(all_attrs)}")
        
        # Check if methods are callable
        callable_methods = [attr for attr in all_attrs if callable(getattr(TestModeRefactored, attr)) and not attr.startswith('__')]
        print(f"✅ Callable methods: {len(callable_methods)}")
        
        # Check for transformation methods specifically
        transformation_methods = [attr for attr in callable_methods if 'garbage' in attr.lower() or 'transform' in attr.lower()]
        print(f"✅ Transformation methods: {transformation_methods}")
        
        # Try to access the methods directly
        print("\n🔍 TRYING TO ACCESS METHODS DIRECTLY...")
        
        try:
            method = getattr(TestModeRefactored, '_process_garbage_transformations', None)
            if method:
                print("✅ _process_garbage_transformations found")
            else:
                print("❌ _process_garbage_transformations not found")
        except Exception as e:
            print(f"❌ Error accessing _process_garbage_transformations: {e}")
        
        try:
            method = getattr(TestModeRefactored, '_track_garbage_landings', None)
            if method:
                print("✅ _track_garbage_landings found")
            else:
                print("❌ _track_garbage_landings not found")
        except Exception as e:
            print(f"❌ Error accessing _track_garbage_landings: {e}")
        
        try:
            method = getattr(TestModeRefactored, '_apply_garbage_finalization', None)
            if method:
                print("✅ _apply_garbage_finalization found")
            else:
                print("❌ _apply_garbage_finalization not found")
        except Exception as e:
            print(f"❌ Error accessing _apply_garbage_finalization: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_class_structure()
