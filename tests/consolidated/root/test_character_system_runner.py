#!/usr/bin/env python3
"""
Character System Test Runner - Run all character system tests in headless environment
"""

import unittest
import sys
import os

# Set up headless environment for testing
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')

def run_character_system_tests():
    """Run all character system tests."""
    print("\n" + "="*80)
    print("🧪 CHARACTER SYSTEM TEST SUITE")
    print("="*80)
    
    # Import test modules
    try:
        from test_character_positioning import TestCharacterPositioning
        from test_sprite_sheet import TestSpriteSheet
        print("✅ All character test modules imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import character test modules: {e}")
        return None
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add character positioning tests
    positioning_tests = unittest.TestLoader().loadTestsFromTestCase(TestCharacterPositioning)
    suite.addTests(positioning_tests)
    print(f"✅ Added {positioning_tests.countTestCases()} character positioning tests")
    
    # Add sprite sheet tests
    sprite_tests = unittest.TestLoader().loadTestsFromTestCase(TestSpriteSheet)
    suite.addTests(sprite_tests)
    print(f"✅ Added {sprite_tests.countTestCases()} sprite sheet tests")
    
    # Run tests
    print(f"\n🚀 Running {suite.countTestCases()} total character system tests...")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print detailed summary
    print("\n" + "="*80)
    print("📊 CHARACTER SYSTEM TEST RESULTS")
    print("="*80)
    
    passed = result.testsRun - len(result.failures) - len(result.errors)
    failed = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped)
    
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"⚠️  Errors: {errors}")
    print(f"⏭️  Skipped: {skipped}")
    print(f"📊 Total: {result.testsRun}")
    
    # Calculate pass rate
    if result.testsRun > 0:
        pass_rate = (passed / result.testsRun) * 100
        print(f"📈 Pass Rate: {pass_rate:.1f}%")
        
        if pass_rate >= 90:
            print("🎉 Excellent! Character system is working well.")
        elif pass_rate >= 75:
            print("👍 Good! Minor issues to address.")
        else:
            print("⚠️  Warning! Significant issues found.")
    
    # Print detailed error information
    if result.failures or result.errors:
        print(f"\n🔍 DETAILED ERROR INFORMATION:")
        
        for test, traceback in result.failures:
            print(f"\n❌ FAILED: {test}")
            print(f"   {traceback[:300]}...")
        
        for test, traceback in result.errors:
            print(f"\n⚠️  ERROR: {test}")
            print(f"   {traceback[:300]}...")
    
    # Print skipped test information
    if result.skipped:
        print(f"\n⏭️  SKIPPED TESTS:")
        for test, reason in result.skipped:
            print(f"   {test}: {reason}")
    
    return result


def run_specific_test_category(category):
    """Run tests from a specific category."""
    categories = {
        'positioning': 'test_character_positioning',
        'sprite': 'test_sprite_sheet',
        'all': 'all'
    }
    
    if category.lower() not in categories:
        print(f"❌ Unknown test category: {category}")
        print(f"Available categories: {', '.join(categories.keys())}")
        return None
    
    if category.lower() == 'all':
        return run_character_system_tests()
    
    # Run specific category
    test_module = categories[category.lower()]
    print(f"\n🧪 Running {category} tests...")
    
    try:
        if category.lower() == 'positioning':
            from test_character_positioning import TestCharacterPositioning
            suite = unittest.TestLoader().loadTestsFromTestCase(TestCharacterPositioning)
        elif category.lower() == 'sprite':
            from test_sprite_sheet import TestSpriteSheet
            suite = unittest.TestLoader().loadTestsFromTestCase(TestSpriteSheet)
        
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        # Print summary
        passed = result.testsRun - len(result.failures) - len(result.errors)
        print(f"\n📊 {category.title()} Test Results: {passed}/{result.testsRun} passed")
        
        return result
        
    except ImportError as e:
        print(f"❌ Failed to import {category} test module: {e}")
        return None


def main():
    """Main entry point for character system tests."""
    if len(sys.argv) > 1:
        category = sys.argv[1]
        run_specific_test_category(category)
    else:
        run_character_system_tests()


if __name__ == "__main__":
    main()
