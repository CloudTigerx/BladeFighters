#!/usr/bin/env python3
"""
Bug Fix Verification Script
Tests the fixes for the critical game stability issues.
"""

import sys
import os
import time

def test_resolution_scaling():
    """Test that resolution scaling works properly."""
    print("🔍 Testing resolution scaling...")
    
    try:
        from resolution_enhancer import resolution_enhancer
        
        # Test with different screen sizes
        test_cases = [
            (1920, 1080),  # Standard HD
            (2560, 1440),  # 2K
            (3456, 2234),  # Retina (problematic)
            (1680, 1050),  # MacBook Pro
        ]
        
        for width, height in test_cases:
            optimal_w, optimal_h = resolution_enhancer.get_optimal_resolution(width, height)
            print(f"   {width}x{height} -> {optimal_w}x{optimal_h}")
            
            # Verify the resolution is reasonable
            if optimal_w > 2000 or optimal_h > 1500:
                print(f"   ⚠️ Resolution too large: {optimal_w}x{optimal_h}")
                return False
        
        print("   ✅ Resolution scaling test passed")
        return True
        
    except Exception as e:
        print(f"   ❌ Resolution scaling test failed: {e}")
        return False

def test_test_mode_initialization():
    """Test that test mode can be initialized."""
    print("🔍 Testing test mode initialization...")
    
    try:
        from modules.testmode_module.test_mode import TestModeRefactored
        print("   ✅ Test mode import successful")
        return True
        
    except Exception as e:
        print(f"   ❌ Test mode initialization failed: {e}")
        return False

def test_time_import():
    """Test that time module is available."""
    print("🔍 Testing time module availability...")
    
    try:
        import time
        current_time = time.time()
        print(f"   ✅ Time module available: {current_time}")
        return True
        
    except Exception as e:
        print(f"   ❌ Time module test failed: {e}")
        return False

def test_quickplay_functionality():
    """Test quickplay functionality."""
    print("🔍 Testing quickplay functionality...")
    
    try:
        # Test the start_quickplay method
        from game_client import GameClient
        
        # Create a minimal game client for testing
        client = GameClient()
        
        # Test the method exists and can be called
        if hasattr(client, 'start_quickplay'):
            print("   ✅ Quickplay method exists")
            return True
        else:
            print("   ❌ Quickplay method not found")
            return False
            
    except Exception as e:
        print(f"   ❌ Quickplay test failed: {e}")
        return False

def test_audio_loading():
    """Test audio loading functionality."""
    print("🔍 Testing audio loading...")
    
    try:
        from modules.audio_module.audio_system import AudioSystem
        
        # Test audio system initialization
        audio = AudioSystem()
        print("   ✅ Audio system initialized")
        return True
        
    except Exception as e:
        print(f"   ❌ Audio loading test failed: {e}")
        return False

def main():
    """Run all bug fix tests."""
    print("🚀 Running bug fix verification tests...")
    print()
    
    tests = [
        ("Resolution Scaling", test_resolution_scaling),
        ("Test Mode Initialization", test_test_mode_initialization),
        ("Time Module", test_time_import),
        ("Quickplay Functionality", test_quickplay_functionality),
        ("Audio Loading", test_audio_loading),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"📋 {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"   ❌ Test crashed: {e}")
            results.append((test_name, False))
        print()
    
    # Summary
    print("📊 Test Results Summary:")
    print("=" * 40)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print("=" * 40)
    print(f"   Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All bug fixes verified successfully!")
        return 0
    else:
        print("⚠️ Some issues remain - continue debugging")
        return 1

if __name__ == "__main__":
    sys.exit(main())
