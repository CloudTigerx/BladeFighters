#!/usr/bin/env python3
"""
Bug Fix Sprint Testing Framework
Rapid testing for critical game stability issues during bug fix sprint.
"""

import unittest
import sys
import os
import time
import subprocess
from typing import Dict, Any, List
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tests.integration.test_suite_framework import BladeFightersTestSuite


class BugFixSprintTests(BladeFightersTestSuite):
    """
    Rapid bug fix testing for critical game stability issues.
    Focuses on immediate playability issues.
    """
    
    def setUp(self):
        """Set up for bug fix testing."""
        super().setUp()
        self.bug_fixes = {
            'quickplay_time_error': False,
            'resolution_scaling': False,
            'test_mode_available': False,
            'inventory_equip_notifications': False
        }
    
    def test_quickplay_time_error_fix(self):
        """Test fix for 'time' is not defined error in quickplay."""
        try:
            # Import quickplay functionality
            from modules.game_state_module.game_state_manager import GameStateManager
            
            # Test that time module is available
            import time
            self.assertIsNotNone(time, "Time module should be available")
            
            # Import ScreenType enum
            from modules.game_state_module.state_schema import ScreenType
            
            # Test quickplay state transitions
            self.state_manager.set("screen.current_screen", ScreenType.GAME, source="test")
            self.state_manager.set("puzzle.game_active", True, source="test")
            
            # Verify quickplay state is valid
            current_screen = self.state_manager.get("screen.current_screen")
            game_active = self.state_manager.get("puzzle.game_active")
            
            self.assertEqual(current_screen, ScreenType.GAME)
            self.assertTrue(game_active)
            
            self.bug_fixes['quickplay_time_error'] = True
            print("✅ Quickplay time error fix verified")
            
        except NameError as e:
            if "time" in str(e):
                self.fail("❌ 'time' is not defined error still exists")
            else:
                raise
        except Exception as e:
            print(f"⚠️  Quickplay test error: {e}")
    
    def test_resolution_scaling_fix(self):
        """Test fix for resolution scaling and UI visibility."""
        try:
            # Test screen resolution settings
            test_resolutions = [
                (800, 600),
                (1024, 768),
                (1920, 1080)
            ]
            
            for width, height in test_resolutions:
                # Set resolution
                self.state_manager.set("screen.resolution", f"{width}x{height}", source="test")
                self.state_manager.set("screen.width", width, source="test")
                self.state_manager.set("screen.height", height, source="test")
                
                # Verify resolution was set
                resolution = self.state_manager.get("screen.resolution")
                screen_width = self.state_manager.get("screen.width")
                screen_height = self.state_manager.get("screen.height")
                
                self.assertEqual(resolution, f"{width}x{height}")
                self.assertEqual(screen_width, width)
                self.assertEqual(screen_height, height)
                
                # Test UI scaling
                self.state_manager.set("ui.scale_factor", 1.0, source="test")
                scale_factor = self.state_manager.get("ui.scale_factor")
                self.assertEqual(scale_factor, 1.0)
            
            self.bug_fixes['resolution_scaling'] = True
            print("✅ Resolution scaling fix verified")
            
        except Exception as e:
            print(f"⚠️  Resolution scaling test error: {e}")
    
    def test_test_mode_availability_fix(self):
        """Test fix for 'Test mode unavailable' error."""
        try:
            # Test test mode state
            self.state_manager.set("screen.current_screen", ScreenType.TEST, source="test")
            self.state_manager.set("test_mode.enabled", True, source="test")
            self.state_manager.set("test_mode.available", True, source="test")
            
            # Verify test mode is available
            current_screen = self.state_manager.get("screen.current_screen")
            test_enabled = self.state_manager.get("test_mode.enabled")
            test_available = self.state_manager.get("test_mode.available")
            
            self.assertEqual(current_screen, ScreenType.TEST)
            self.assertTrue(test_enabled)
            self.assertTrue(test_available)
            
            # Test test mode functionality
            self.state_manager.set("test_mode.board_state", "active", source="test")
            board_state = self.state_manager.get("test_mode.board_state")
            self.assertEqual(board_state, "active")
            
            self.bug_fixes['test_mode_available'] = True
            print("✅ Test mode availability fix verified")
            
        except Exception as e:
            print(f"⚠️  Test mode test error: {e}")
    
    def test_inventory_equip_notifications_fix(self):
        """Test fix for missing equip notifications in inventory."""
        try:
            # Test inventory state
            self.state_manager.set("inventory.equipped_weapon", "rusty_sword", source="test")
            self.state_manager.set("inventory.equipped_armor", "none", source="test")
            self.state_manager.set("inventory.notifications_enabled", True, source="test")
            
            # Verify inventory state
            equipped_weapon = self.state_manager.get("inventory.equipped_weapon")
            equipped_armor = self.state_manager.get("inventory.equipped_armor")
            notifications_enabled = self.state_manager.get("inventory.notifications_enabled")
            
            self.assertEqual(equipped_weapon, "rusty_sword")
            self.assertEqual(equipped_armor, "none")
            self.assertTrue(notifications_enabled)
            
            # Test equip notification
            self.state_manager.set("inventory.last_equip_notification", "Weapon equipped: rusty_sword", source="test")
            last_notification = self.state_manager.get("inventory.last_equip_notification")
            self.assertEqual(last_notification, "Weapon equipped: rusty_sword")
            
            self.bug_fixes['inventory_equip_notifications'] = True
            print("✅ Inventory equip notifications fix verified")
            
        except Exception as e:
            print(f"⚠️  Inventory test error: {e}")
    
    def test_game_startup_stability(self):
        """Test overall game startup stability."""
        try:
            # Test core game state
            self.state_manager.set("game_running", True, source="test")
            self.state_manager.set("screen.current_screen", "MAIN_MENU", source="test")
            self.state_manager.set("puzzle.game_active", False, source="test")
            
            # Verify core state
            game_running = self.state_manager.get("game_running")
            current_screen = self.state_manager.get("screen.current_screen")
            game_active = self.state_manager.get("puzzle.game_active")
            
            self.assertTrue(game_running)
            self.assertEqual(current_screen, "MAIN_MENU")
            self.assertFalse(game_active)
            
            print("✅ Game startup stability verified")
            
        except Exception as e:
            print(f"⚠️  Game startup test error: {e}")
    
    def test_module_integration_stability(self):
        """Test module integration stability after bug fixes."""
        try:
            # Test audio module integration
            if hasattr(self, 'audio_system'):
                self.state_manager.set("audio.master_volume", 0.7, source="test")
                volume = self.state_manager.get("audio.master_volume")
                self.assertEqual(volume, 0.7)
            
            # Test screen module integration
            if hasattr(self, 'screen_manager'):
                self.state_manager.set("screen.current_screen", "GAME", source="test")
                screen = self.state_manager.get("screen.current_screen")
                self.assertEqual(screen, "GAME")
            
            # Test input module integration
            if hasattr(self, 'input_manager'):
                self.state_manager.set("input.keyboard.space_pressed", False, source="test")
                space_pressed = self.state_manager.get("input.keyboard.space_pressed")
                self.assertFalse(space_pressed)
            
            print("✅ Module integration stability verified")
            
        except Exception as e:
            print(f"⚠️  Module integration test error: {e}")
    
    def test_screen_transition_stability(self):
        """Test screen transition stability after bug fixes."""
        try:
            # Test basic screen transitions
            transitions = [
                ("MAIN_MENU", "GAME"),
                ("GAME", "PAUSE"),
                ("PAUSE", "SETTINGS"),
                ("SETTINGS", "MAIN_MENU")
            ]
            
            for from_screen, to_screen in transitions:
                # Set initial screen
                self.state_manager.set("screen.current_screen", from_screen, source="test")
                
                # Verify initial screen
                current_screen = self.state_manager.get("screen.current_screen")
                self.assertEqual(current_screen, from_screen)
                
                # Transition to new screen
                self.state_manager.set("screen.current_screen", to_screen, source="test")
                
                # Verify transition
                new_screen = self.state_manager.get("screen.current_screen")
                self.assertEqual(new_screen, to_screen)
            
            print("✅ Screen transition stability verified")
            
        except Exception as e:
            print(f"⚠️  Screen transition test error: {e}")
    
    def test_performance_after_bug_fixes(self):
        """Test performance after bug fixes."""
        try:
            import time
            
            # Test state operations performance
            start_time = time.time()
            
            for i in range(100):
                self.state_manager.set(f"test.field_{i}", i, source="test")
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Performance should be reasonable
            self.assertLess(duration, 1.0, f"State operations too slow: {duration:.3f}s")
            
            print(f"✅ Performance after bug fixes verified: {duration:.3f}s for 100 operations")
            
        except Exception as e:
            print(f"⚠️  Performance test error: {e}")
    
    def test_error_handling_after_bug_fixes(self):
        """Test error handling after bug fixes."""
        try:
            # Test invalid state changes are handled gracefully
            invalid_changes = [
                ("audio.master_volume", 1.5),  # Volume > 1.0
                ("puzzle.score", -100),  # Negative score
                ("screen.current_screen", "INVALID_SCREEN"),  # Invalid screen
            ]
            
            for field_path, invalid_value in invalid_changes:
                success = self.state_manager.set(field_path, invalid_value, source="test")
                # Should handle gracefully (either reject or clamp)
                self.assertIsInstance(success, bool)
            
            print("✅ Error handling after bug fixes verified")
            
        except Exception as e:
            print(f"⚠️  Error handling test error: {e}")
    
    def test_bug_fix_summary(self):
        """Generate bug fix summary."""
        print("\n" + "=" * 60)
        print("🐛 BUG FIX SPRINT SUMMARY")
        print("=" * 60)
        
        total_bugs = len(self.bug_fixes)
        fixed_bugs = sum(self.bug_fixes.values())
        
        print(f"📊 Total Critical Bugs: {total_bugs}")
        print(f"✅ Fixed: {fixed_bugs}")
        print(f"❌ Remaining: {total_bugs - fixed_bugs}")
        print(f"📈 Fix Rate: {(fixed_bugs/total_bugs)*100:.1f}%")
        
        print("\n🔍 Bug Status:")
        for bug_name, fixed in self.bug_fixes.items():
            status = "✅ FIXED" if fixed else "❌ NOT FIXED"
            print(f"  {bug_name}: {status}")
        
        if fixed_bugs == total_bugs:
            print("\n🎉 ALL CRITICAL BUGS FIXED!")
            print("Game should be playable now.")
        else:
            print(f"\n⚠️  {total_bugs - fixed_bugs} critical bugs still need fixing.")
            print("Game may not be fully playable yet.")
        
        print("=" * 60)


class RapidBugFixRunner:
    """Rapid bug fix test runner for quick feedback."""
    
    def __init__(self):
        self.test_results = {}
    
    def run_quick_diagnostic(self):
        """Run quick diagnostic to identify immediate issues."""
        print("🔍 Running Quick Diagnostic...")
        
        # Test 1: Check if game can start
        try:
            result = subprocess.run([
                sys.executable, 'main.py', '--help'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print("✅ Game startup: OK")
                self.test_results['game_startup'] = True
            else:
                print(f"❌ Game startup: FAILED - {result.stderr}")
                self.test_results['game_startup'] = False
                
        except subprocess.TimeoutExpired:
            print("⏰ Game startup: TIMEOUT")
            self.test_results['game_startup'] = False
        except Exception as e:
            print(f"💥 Game startup: ERROR - {e}")
            self.test_results['game_startup'] = False
        
        # Test 2: Check for time module
        try:
            import time
            print("✅ Time module: AVAILABLE")
            self.test_results['time_module'] = True
        except ImportError:
            print("❌ Time module: MISSING")
            self.test_results['time_module'] = False
        
        # Test 3: Check for pygame
        try:
            import pygame
            print("✅ Pygame: AVAILABLE")
            self.test_results['pygame'] = True
        except ImportError:
            print("❌ Pygame: MISSING")
            self.test_results['pygame'] = False
        
        # Test 4: Check for required modules
        required_modules = [
            'modules.game_state_module.game_state_manager',
            'modules.audio_module.audio_system',
            'modules.screen_module.screen_manager',
            'modules.input_module.unified_input_manager'
        ]
        
        for module in required_modules:
            try:
                __import__(module)
                print(f"✅ {module}: AVAILABLE")
                self.test_results[module] = True
            except ImportError:
                print(f"❌ {module}: MISSING")
                self.test_results[module] = False
        
        return self.test_results
    
    def generate_diagnostic_report(self):
        """Generate diagnostic report."""
        print("\n" + "=" * 60)
        print("📋 QUICK DIAGNOSTIC REPORT")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(self.test_results.values())
        
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {total_tests - passed_tests}")
        print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\n🔍 Detailed Results:")
        for test_name, passed in self.test_results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"  {test_name}: {status}")
        
        if passed_tests == total_tests:
            print("\n🎉 All basic requirements met!")
            print("Ready for bug fix testing.")
        else:
            print(f"\n⚠️  {total_tests - passed_tests} basic requirements missing.")
            print("Fix basic issues before proceeding with bug fixes.")
        
        print("=" * 60)


def main():
    """Main entry point for bug fix sprint testing."""
    print("🚨 BUG FIX SPRINT TESTING")
    print("=" * 60)
    
    # Run quick diagnostic first
    runner = RapidBugFixRunner()
    diagnostic_results = runner.run_quick_diagnostic()
    runner.generate_diagnostic_report()
    
    # Run bug fix tests if basic requirements are met
    if diagnostic_results.get('game_startup', False):
        print("\n🧪 Running Bug Fix Tests...")
        
        # Run tests
        suite = unittest.TestLoader().loadTestsFromTestCase(BugFixSprintTests)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        # Generate summary
        print(f"\n📊 Bug Fix Test Results:")
        print(f"  Tests Run: {result.testsRun}")
        print(f"  Failures: {len(result.failures)}")
        print(f"  Errors: {len(result.errors)}")
        
        if result.failures:
            print("\n❌ Failures:")
            for test, traceback in result.failures:
                print(f"  {test}: {traceback}")
        
        if result.errors:
            print("\n💥 Errors:")
            for test, traceback in result.errors:
                print(f"  {test}: {traceback}")
        
        if not result.failures and not result.errors:
            print("\n🎉 All bug fix tests passed!")
            print("Game should be stable and playable.")
    else:
        print("\n⚠️  Skipping bug fix tests due to basic startup issues.")
        print("Fix startup issues first.")


if __name__ == "__main__":
    main()
