#!/usr/bin/env python3
"""
Test Transformation Methods
==========================

Simple test to verify transformation methods exist.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_transformation_methods():
    """Test if transformation methods exist"""
    print("🔄 Testing transformation methods...")
    
    try:
        # Import the module
        import modules.testmode_module.test_mode
        
        # Get the class
        TestModeRefactored = modules.testmode_module.test_mode.TestModeRefactored
        
        print(f"✅ Successfully imported TestModeRefactored")
        print(f"✅ Class has {len(dir(TestModeRefactored))} methods/attributes")
        
        # Check for specific methods
        required_methods = [
            '_process_garbage_transformations',
            '_track_garbage_landings',
            '_apply_garbage_finalization'
        ]
        
        found_methods = []
        for method in required_methods:
            if hasattr(TestModeRefactored, method):
                found_methods.append(method)
                print(f"✅ Found method: {method}")
            else:
                print(f"❌ Missing method: {method}")
        
        # Check for garbage_block_brightness attribute
        if hasattr(TestModeRefactored, 'garbage_block_brightness'):
            print("✅ Found garbage_block_brightness attribute")
        else:
            print("❌ Missing garbage_block_brightness attribute")
        
        print(f"\n📊 Results: {len(found_methods)}/{len(required_methods)} methods found")
        
        return len(found_methods) == len(required_methods)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_transformation_methods()
