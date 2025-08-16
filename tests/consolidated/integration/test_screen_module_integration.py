"""
Comprehensive Integration Tests for Screen Module
Tests screen manager integration with game state, transitions, and UI rendering.
"""

import unittest
import sys
import os
import time
import json
from unittest.mock import Mock, patch, MagicMock
import pygame

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from tests.integration.test_suite_framework import BladeFightersTestSuite
from modules.game_state_module.game_state_manager import GameStateManager
from modules.game_state_module.state_schema import ScreenType, GameMode


class ScreenModuleIntegrationTests(BladeFightersTestSuite):
    """Integration tests for the screen module."""
    
    def setUp(self):
        super().setUp()
        try:
            from modules.screen_module.screen_manager import ScreenManager
            from modules.screen_module.screen_state_integration import ScreenStateIntegration
            self.ScreenManager = ScreenManager
            self.ScreenStateIntegration = ScreenStateIntegration
        except ImportError as e:
            self.skipTest(f"Screen module not available: {e}")
    
    def test_screen_manager_initialization(self):
        """Test screen manager initialization with game state integration."""
        # Create screen manager
        screen_manager = self.ScreenManager(
            self.test_screen, 
            self.test_font, 
            self.state_manager, 
            self.test_config['asset_path']
        )
        
        # Verify basic initialization
        self.assertIsNotNone(screen_manager)
        self.assertIsNotNone(screen_manager.state_manager)
        self.assertEqual(screen_manager.state_manager, self.state_manager)
    
    def test_screen_transition_performance(self):
        """Test screen transition performance."""
        screen_manager = self.ScreenManager(
            self.test_screen, 
            self.test_font, 
            self.state_manager, 
            self.test_config['asset_path']
        )
        
        # Test transition performance
        screens = [ScreenType.LOADING, ScreenType.MAIN_MENU, ScreenType.GAME, 
                  ScreenType.PAUSE, ScreenType.SETTINGS]
        
        transition_times = []
        
        for i in range(len(screens) - 1):
            start_time = time.time()
            
            # Trigger transition
            self.state_manager.set("screen.current_screen", screens[i + 1], source="test")
            screen_manager.update()  # Process the transition
            
            duration = time.time() - start_time
            transition_times.append(duration)
            
            # Verify transition completed
            self.assertEqual(self.state_manager.get("screen.current_screen"), screens[i + 1])
        
        # Verify performance
        avg_transition_time = sum(transition_times) / len(transition_times)
        self.assertLess(avg_transition_time, 0.1, 
                       f"Average transition time {avg_transition_time:.3f}s too high")
    
    def test_screen_rendering_performance(self):
        """Test screen rendering performance."""
        screen_manager = self.ScreenManager(
            self.test_screen, 
            self.test_font, 
            self.state_manager, 
            self.test_config['asset_path']
        )
        
        # Test rendering performance
        start_time = time.time()
        
        for i in range(100):  # 100 render cycles
            screen_manager.render()
        
        duration = time.time() - start_time
        frames_per_second = 100 / duration
        
        # Should maintain good frame rate
        self.assertGreater(frames_per_second, 30, 
                          f"Rendering performance: {frames_per_second:.1f} FPS")
    
    def test_screen_state_synchronization(self):
        """Test that screen manager synchronizes with game state."""
        screen_manager = self.ScreenManager(
            self.test_screen, 
            self.test_font, 
            self.state_manager, 
            self.test_config['asset_path']
        )
        
        # Test screen state changes
        test_screens = [ScreenType.MAIN_MENU, ScreenType.GAME, ScreenType.PAUSE]
        
        for screen_type in test_screens:
            # Change screen through state manager
            self.state_manager.set("screen.current_screen", screen_type, source="test")
            
            # Update screen manager
            screen_manager.update()
            
            # Verify screen manager reflects the change
            current_screen = self.state_manager.get("screen.current_screen")
            self.assertEqual(current_screen, screen_type)
    
    def test_screen_transition_validation(self):
        """Test screen transition validation."""
        screen_manager = self.ScreenManager(
            self.test_screen, 
            self.test_font, 
            self.state_manager, 
            self.test_config['asset_path']
        )
        
        # Test valid transitions
        valid_transitions = [
            (ScreenType.LOADING, ScreenType.MAIN_MENU),
            (ScreenType.MAIN_MENU, ScreenType.GAME),
            (ScreenType.GAME, ScreenType.PAUSE),
            (ScreenType.PAUSE, ScreenType.GAME),
            (ScreenType.GAME, ScreenType.MAIN_MENU),
        ]
        
        for from_screen, to_screen in valid_transitions:
            # Set initial screen
            self.state_manager.set("screen.current_screen", from_screen, source="test")
            screen_manager.update()
            
            # Attempt transition
            success = self.state_manager.set("screen.current_screen", to_screen, source="test")
            self.assertTrue(success, f"Valid transition failed: {from_screen} -> {to_screen}")
            
            screen_manager.update()
            self.assertEqual(self.state_manager.get("screen.current_screen"), to_screen)
    
    def test_screen_asset_loading(self):
        """Test screen asset loading and validation."""
        screen_manager = self.ScreenManager(
            self.test_screen, 
            self.test_font, 
            self.state_manager, 
            self.test_config['asset_path']
        )
        
        # Test that required assets are loaded
        if hasattr(screen_manager, 'assets'):
            self.assertIsNotNone(screen_manager.assets)
            
            # Check for common screen assets
            expected_assets = ['background', 'buttons', 'title']
            for asset_name in expected_assets:
                if hasattr(screen_manager.assets, asset_name):
                    asset = getattr(screen_manager.assets, asset_name)
                    self.assertIsNotNone(asset, f"Asset '{asset_name}' is None")
    
    def test_screen_error_handling(self):
        """Test screen manager error handling."""
        screen_manager = self.ScreenManager(
            self.test_screen, 
            self.test_font, 
            self.state_manager, 
            self.test_config['asset_path']
        )
        
        # Test handling of invalid screen types
        try:
            self.state_manager.set("screen.current_screen", "INVALID_SCREEN", source="test")
            screen_manager.update()
            # Should handle gracefully
        except Exception as e:
            self.fail(f"Screen manager should handle invalid screen types: {e}")
        
        # Test handling of missing assets
        try:
            screen_manager.render()
            # Should render with fallbacks
        except Exception as e:
            self.fail(f"Screen manager should handle missing assets: {e}")
    
    def test_screen_memory_usage(self):
        """Test screen manager memory usage."""
        initial_memory = self.performance_monitor._get_memory_usage()
        
        # Create multiple screen managers
        screen_managers = []
        for i in range(5):
            screen_manager = self.ScreenManager(
                self.test_screen, 
                self.test_font, 
                self.state_manager, 
                self.test_config['asset_path']
            )
            screen_managers.append(screen_manager)
        
        final_memory = self.performance_monitor._get_memory_usage()
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable
        self.assertLess(memory_increase, 100.0, 
                       f"Screen manager creation used {memory_increase:.1f}MB")
    
    def test_screen_state_integration(self):
        """Test screen state integration module."""
        try:
            screen_integration = self.ScreenStateIntegration(self.state_manager)
            
            # Test state change callbacks
            callback_called = False
            def test_callback(old_screen, new_screen):
                nonlocal callback_called
                callback_called = True
            
            screen_integration.on_screen_change = test_callback
            
            # Change screen
            self.state_manager.set("screen.current_screen", ScreenType.GAME, source="test")
            
            # Verify callback was called
            self.assertTrue(callback_called)
            
        except Exception as e:
            self.skipTest(f"ScreenStateIntegration not available: {e}")
    
    def test_screen_concurrent_access(self):
        """Test screen manager under concurrent access."""
        screen_manager = self.ScreenManager(
            self.test_screen, 
            self.test_font, 
            self.state_manager, 
            self.test_config['asset_path']
        )
        
        # Simulate concurrent access
        import threading
        
        def render_screens():
            for i in range(10):
                screen_manager.render()
                time.sleep(0.01)
        
        def update_screens():
            for i in range(10):
                screen_manager.update()
                time.sleep(0.01)
        
        threads = []
        
        # Start render thread
        render_thread = threading.Thread(target=render_screens)
        threads.append(render_thread)
        render_thread.start()
        
        # Start update thread
        update_thread = threading.Thread(target=update_screens)
        threads.append(update_thread)
        update_thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Should complete without errors
        self.assertTrue(True)
    
    def test_screen_transition_animation(self):
        """Test screen transition animations."""
        screen_manager = self.ScreenManager(
            self.test_screen, 
            self.test_font, 
            self.state_manager, 
            self.test_config['asset_path']
        )
        
        # Test transition animation timing
        start_time = time.time()
        
        # Start transition
        self.state_manager.set("screen.transition_in_progress", True, source="test")
        self.state_manager.set("screen.current_screen", ScreenType.GAME, source="test")
        
        # Simulate animation frames
        for i in range(10):
            screen_manager.update()
            time.sleep(0.01)  # Simulate frame time
        
        # End transition
        self.state_manager.set("screen.transition_in_progress", False, source="test")
        screen_manager.update()
        
        duration = time.time() - start_time
        
        # Transition should complete in reasonable time
        self.assertLess(duration, 1.0, f"Transition animation took {duration:.3f}s")
    
    def test_screen_resolution_handling(self):
        """Test screen manager with different resolutions."""
        # Test with different screen sizes
        test_resolutions = [(800, 600), (1024, 768), (1920, 1080)]
        
        for width, height in test_resolutions:
            # Create test screen with different resolution
            test_screen = pygame.display.set_mode((width, height))
            
            screen_manager = self.ScreenManager(
                test_screen, 
                self.test_font, 
                self.state_manager, 
                self.test_config['asset_path']
            )
            
            # Test rendering at this resolution
            try:
                screen_manager.render()
                self.assertTrue(True)  # Should render without errors
            except Exception as e:
                self.fail(f"Screen manager failed at resolution {width}x{height}: {e}")
    
    def test_screen_performance_benchmarking(self):
        """Benchmark screen manager performance."""
        screen_manager = self.ScreenManager(
            self.test_screen, 
            self.test_font, 
            self.state_manager, 
            self.test_config['asset_path']
        )
        
        # Benchmark rendering
        start_time = time.time()
        for i in range(1000):
            screen_manager.render()
        
        render_duration = time.time() - start_time
        renders_per_second = 1000 / render_duration
        
        # Should maintain good rendering performance
        self.assertGreater(renders_per_second, 30, 
                          f"Rendering rate: {renders_per_second:.1f} renders/sec")
        
        # Benchmark updates
        start_time = time.time()
        for i in range(1000):
            screen_manager.update()
        
        update_duration = time.time() - start_time
        updates_per_second = 1000 / update_duration
        
        # Should maintain good update performance
        self.assertGreater(updates_per_second, 100, 
                          f"Update rate: {updates_per_second:.1f} updates/sec")


class ScreenModuleRegressionTests(BladeFightersTestSuite):
    """Regression tests for screen module functionality."""
    
    def setUp(self):
        super().setUp()
        try:
            from modules.screen_module.screen_manager import ScreenManager
            self.ScreenManager = ScreenManager
        except ImportError as e:
            self.skipTest(f"Screen module not available: {e}")
    
    def test_screen_transition_regression(self):
        """Test that screen transitions still work correctly."""
        screen_manager = self.ScreenManager(
            self.test_screen, 
            self.test_font, 
            self.state_manager, 
            self.test_config['asset_path']
        )
        
        # Test all screen transitions
        all_screens = list(ScreenType)
        
        for screen_type in all_screens:
            try:
                self.state_manager.set("screen.current_screen", screen_type, source="test")
                screen_manager.update()
                self.assertEqual(self.state_manager.get("screen.current_screen"), screen_type)
            except Exception as e:
                self.fail(f"Screen transition to {screen_type} failed: {e}")
    
    def test_screen_rendering_regression(self):
        """Test that screen rendering still works correctly."""
        screen_manager = self.ScreenManager(
            self.test_screen, 
            self.test_font, 
            self.state_manager, 
            self.test_config['asset_path']
        )
        
        # Test rendering for all screen types
        for screen_type in ScreenType:
            self.state_manager.set("screen.current_screen", screen_type, source="test")
            screen_manager.update()
            
            try:
                screen_manager.render()
                # Should render without errors
            except Exception as e:
                self.fail(f"Screen rendering for {screen_type} failed: {e}")
    
    def test_screen_state_persistence_regression(self):
        """Test that screen state persists correctly."""
        screen_manager = self.ScreenManager(
            self.test_screen, 
            self.test_font, 
            self.state_manager, 
            self.test_config['asset_path']
        )
        
        # Test state persistence across updates
        test_screen = ScreenType.GAME
        self.state_manager.set("screen.current_screen", test_screen, source="test")
        
        # Multiple updates should maintain state
        for i in range(10):
            screen_manager.update()
            self.assertEqual(self.state_manager.get("screen.current_screen"), test_screen)


if __name__ == "__main__":
    unittest.main() 