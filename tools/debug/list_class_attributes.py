#!/usr/bin/env python3
"""
List Class Attributes
===================

List all class attributes to understand what's happening.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def list_class_attributes():
    """List all class attributes"""
    print("🔍 LISTING CLASS ATTRIBUTES...")
    
    try:
        # Import the module
        import modules.testmode_module.test_mode
        
        # Get the class
        TestModeRefactored = modules.testmode_module.test_mode.TestModeRefactored
        
        print(f"✅ Successfully imported TestModeRefactored")
        
        # List all attributes
        all_attrs = dir(TestModeRefactored)
        print(f"✅ Total attributes: {len(all_attrs)}")
        
        print("\n📋 ALL ATTRIBUTES:")
        for i, attr in enumerate(all_attrs):
            attr_value = getattr(TestModeRefactored, attr)
            attr_type = type(attr_value).__name__
            is_callable = callable(attr_value)
            print(f"{i+1:2d}. {attr} ({attr_type}, callable: {is_callable})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    list_class_attributes()
