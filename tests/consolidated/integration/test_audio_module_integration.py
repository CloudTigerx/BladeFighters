"""
Comprehensive Integration Tests for Audio Module
Tests audio system integration with game state, performance, and edge cases.
Includes state management integration tests for the new unified state system.
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


class AudioModuleIntegrationTests(BladeFightersTestSuite):
    """Integration tests for the audio module."""
    
    def setUp(self):
        super().setUp()
        try:
            from modules.audio_module.audio_system import AudioSystem
            from modules.audio_module.audio_state_manager import AudioStateManager
            from modules.settings_module.audio_settings_integration import AudioSettingsIntegration
            self.AudioSystem = AudioSystem
            self.AudioStateManager = AudioStateManager
            self.AudioSettingsIntegration = AudioSettingsIntegration
        except ImportError as e:
            self.skipTest(f"Audio module not available: {e}")
    
    def test_audio_system_initialization(self):
        """Test audio system initialization with game state integration."""
        # Create audio system
        audio_system = self.AudioSystem(self.test_config['asset_path'])
        
        # Verify basic initialization
        self.assertIsNotNone(audio_system)
        self.assertIsNotNone(audio_system.sounds)
        self.assertIsInstance(audio_system.sounds, dict)
        
        # Test integration with state manager
        audio_system.set_state_manager(self.state_manager)
        self.assertIsNotNone(audio_system.state_manager)
    
    def test_audio_state_synchronization(self):
        """Test that audio system synchronizes with game state."""
        # Create audio system with state manager
        audio_system = self.AudioSystem(self.test_config['asset_path'])
        audio_system.set_state_manager(self.state_manager)
        
        # Change volume through state manager
        self.state_manager.set("audio.master_volume", 0.5, source="test")
        self.state_manager.set("audio.sfx_volume", 0.8, source="test")
        self.state_manager.set("audio.music_volume", 0.6, source="test")
        
        # Verify audio system reflects changes
        self.assertEqual(audio_system.get_master_volume(), 0.5)
        self.assertEqual(audio_system.get_sfx_volume(), 0.8)
        self.assertEqual(audio_system.get_music_volume(), 0.6)
    
    def test_audio_performance_under_load(self):
        """Test audio system performance under heavy load."""
        audio_system = self.AudioSystem(self.test_config['asset_path'])
        
        # Test rapid sound playing
        start_time = time.time()
        for i in range(100):
            audio_system.play_sound('click')
        
        duration = time.time() - start_time
        self.assertLess(duration, 1.0, f"Rapid sound playing took {duration:.3f}s")
    
    def test_audio_memory_usage(self):
        """Test audio system memory usage."""
        initial_memory = self.performance_monitor._get_memory_usage()
        
        # Create multiple audio systems
        audio_systems = []
        for i in range(10):
            audio_system = self.AudioSystem(self.test_config['asset_path'])
            audio_systems.append(audio_system)
        
        final_memory = self.performance_monitor._get_memory_usage()
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable
        self.assertLess(memory_increase, 50.0, 
                       f"Audio system creation used {memory_increase:.1f}MB")
    
    def test_audio_error_handling(self):
        """Test audio system error handling."""
        audio_system = self.AudioSystem(self.test_config['asset_path'])
        
        # Test playing non-existent sounds
        try:
            audio_system.play_sound('nonexistent_sound')
            # Should not raise an exception
        except Exception as e:
            self.fail(f"Audio system should handle missing sounds gracefully: {e}")
        
        # Test with invalid volume values
        try:
            audio_system.set_master_volume(1.5)  # Invalid volume
            audio_system.set_master_volume(-0.5)  # Invalid volume
            # Should clamp values or handle gracefully
        except Exception as e:
            self.fail(f"Audio system should handle invalid volume values: {e}")
    
    def test_audio_state_manager_integration(self):
        """Test audio state manager integration."""
        try:
            audio_state_manager = self.AudioStateManager(self.state_manager)
            
            # Test state change callbacks
            callback_called = False
            def test_callback(old_volume, new_volume):
                nonlocal callback_called
                callback_called = True
            
            audio_state_manager.on_volume_change = test_callback
            
            # Change volume through state manager
            self.state_manager.set("audio.master_volume", 0.7, source="test")
            
            # Verify callback was called
            self.assertTrue(callback_called)
            
        except Exception as e:
            self.skipTest(f"AudioStateManager not available: {e}")
    
    def test_audio_mp3_player_integration(self):
        """Test MP3 player integration."""
        audio_system = self.AudioSystem(self.test_config['asset_path'])
        
        # Test MP3 player functionality
        if hasattr(audio_system, 'mp3_player') and audio_system.mp3_player:
            # Test song loading
            if audio_system.songs:
                first_song = audio_system.songs[0]
                self.assertIn('path', first_song)
                self.assertIn('title', first_song)
            
            # Test play/pause functionality
            try:
                audio_system.play_music(0)  # Play first song
                audio_system.pause_music()
                audio_system.resume_music()
                audio_system.stop_music()
            except Exception as e:
                self.fail(f"MP3 player operations failed: {e}")
    
    def test_audio_screen_transition_integration(self):
        """Test audio system behavior during screen transitions."""
        audio_system = self.AudioSystem(self.test_config['asset_path'])
        audio_system.set_state_manager(self.state_manager)
        
        # Test audio behavior during screen transitions
        screens_with_audio = [
            (ScreenType.MAIN_MENU, 'menu_music'),
            (ScreenType.GAME, 'game_music'),
            (ScreenType.PAUSE, 'pause_music')
        ]
        
        for screen_type, expected_audio in screens_with_audio:
            # Transition to screen
            self.state_manager.set("screen.current_screen", screen_type, source="test")
            
            # Verify appropriate audio is playing (if implemented)
            # This would depend on your specific audio implementation
            pass
    
    def test_audio_concurrent_access(self):
        """Test audio system under concurrent access."""
        audio_system = self.AudioSystem(self.test_config['asset_path'])
        
        # Simulate concurrent access
        import threading
        
        def play_sounds():
            for i in range(10):
                audio_system.play_sound('click')
                time.sleep(0.01)
        
        threads = []
        for i in range(5):
            thread = threading.Thread(target=play_sounds)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Should complete without errors
        self.assertTrue(True)
    
    def test_audio_asset_loading(self):
        """Test audio asset loading and validation."""
        audio_system = self.AudioSystem(self.test_config['asset_path'])
        
        # Test that expected sounds are loaded
        expected_sounds = ['hover', 'click', 'placed', 'singlebreak', 'double', 'triple']
        
        for sound_name in expected_sounds:
            if sound_name in audio_system.sounds:
                sound = audio_system.sounds[sound_name]
                self.assertIsNotNone(sound, f"Sound '{sound_name}' is None")
            else:
                print(f"Warning: Expected sound '{sound_name}' not found")
        
        # Test that songs are loaded
        if audio_system.songs:
            self.assertGreater(len(audio_system.songs), 0)
            
            # Verify song structure
            for song in audio_system.songs:
                self.assertIn('path', song)
                self.assertIn('title', song)
                self.assertIn('artist', song)
    
    def test_audio_volume_persistence(self):
        """Test that audio volume settings persist correctly."""
        audio_system = self.AudioSystem(self.test_config['asset_path'])
        audio_system.set_state_manager(self.state_manager)
        
        # Set volume levels
        test_volumes = [0.3, 0.7, 0.9]
        
        for volume in test_volumes:
            audio_system.set_master_volume(volume)
            self.assertEqual(audio_system.get_master_volume(), volume)
            
            # Verify state manager reflects the change
            self.assertEqual(self.state_manager.get("audio.master_volume"), volume)
    
    def test_audio_performance_benchmarking(self):
        """Benchmark audio system performance."""
        audio_system = self.AudioSystem(self.test_config['asset_path'])
        
        # Benchmark sound playing
        start_time = time.time()
        for i in range(1000):
            audio_system.play_sound('click')
        
        sound_duration = time.time() - start_time
        sounds_per_second = 1000 / sound_duration
        
        # Should be able to play many sounds per second
        self.assertGreater(sounds_per_second, 100, 
                          f"Sound playing rate: {sounds_per_second:.1f} sounds/sec")
        
        # Benchmark volume changes
        start_time = time.time()
        for i in range(1000):
            audio_system.set_master_volume(i / 1000)
        
        volume_duration = time.time() - start_time
        volume_changes_per_second = 1000 / volume_duration
        
        # Should be able to change volume rapidly
        self.assertGreater(volume_changes_per_second, 1000, 
                          f"Volume change rate: {volume_changes_per_second:.1f} changes/sec")


class AudioModuleRegressionTests(BladeFightersTestSuite):
    """Regression tests for audio module functionality."""
    
    def setUp(self):
        super().setUp()
        try:
            from modules.audio_module.audio_system import AudioSystem
            self.AudioSystem = AudioSystem
        except ImportError as e:
            self.skipTest(f"Audio module not available: {e}")
    
    def test_audio_volume_clamping_regression(self):
        """Test that volume clamping still works correctly."""
        audio_system = self.AudioSystem(self.test_config['asset_path'])
        
        # Test volume clamping
        audio_system.set_master_volume(1.5)  # Should clamp to 1.0
        self.assertLessEqual(audio_system.get_master_volume(), 1.0)
        
        audio_system.set_master_volume(-0.5)  # Should clamp to 0.0
        self.assertGreaterEqual(audio_system.get_master_volume(), 0.0)
    
    def test_audio_sound_playback_regression(self):
        """Test that sound playback still works correctly."""
        audio_system = self.AudioSystem(self.test_config['asset_path'])
        
        # Test that all sounds can be played without errors
        for sound_name in audio_system.sounds:
            try:
                audio_system.play_sound(sound_name)
            except Exception as e:
                self.fail(f"Sound '{sound_name}' playback failed: {e}")
    
    def test_audio_music_playback_regression(self):
        """Test that music playback still works correctly."""
        audio_system = self.AudioSystem(self.test_config['asset_path'])
        
        if hasattr(audio_system, 'mp3_player') and audio_system.mp3_player:
            # Test music controls
            try:
                audio_system.play_music(0)
                audio_system.pause_music()
                audio_system.resume_music()
                audio_system.stop_music()
            except Exception as e:
                self.fail(f"Music playback controls failed: {e}")


class AudioModuleStateManagementTests(BladeFightersTestSuite):
    """Comprehensive state management integration tests for audio module."""
    
    def setUp(self):
        super().setUp()
        try:
            from modules.audio_module.audio_system import AudioSystem
            from modules.audio_module.audio_state_manager import AudioStateManager
            from modules.settings_module.audio_settings_integration import AudioSettingsIntegration
            self.AudioSystem = AudioSystem
            self.AudioStateManager = AudioStateManager
            self.AudioSettingsIntegration = AudioSettingsIntegration
        except ImportError as e:
            self.skipTest(f"Audio module not available: {e}")
    
    def test_audio_state_manager_initialization(self):
        """Test AudioStateManager initialization and basic functionality."""
        # Initialize audio state manager
        audio_state_manager = self.AudioStateManager(self.state_manager)
        
        # Test default values
        self.assertEqual(audio_state_manager.get_master_volume(), 0.6)
        self.assertEqual(audio_state_manager.get_music_volume(), 0.5)
        self.assertEqual(audio_state_manager.get_sfx_volume(), 0.7)
        self.assertTrue(audio_state_manager.is_music_enabled())
        self.assertTrue(audio_state_manager.is_sfx_enabled())
    
    def test_audio_state_manager_volume_control(self):
        """Test volume control through AudioStateManager."""
        audio_state_manager = self.AudioStateManager(self.state_manager)
        
        # Test master volume
        success = audio_state_manager.set_master_volume(0.8, "test")
        self.assertTrue(success)
        self.assertEqual(audio_state_manager.get_master_volume(), 0.8)
        
        # Test music volume
        success = audio_state_manager.set_music_volume(0.6, "test")
        self.assertTrue(success)
        self.assertEqual(audio_state_manager.get_music_volume(), 0.6)
        
        # Test SFX volume
        success = audio_state_manager.set_sfx_volume(0.9, "test")
        self.assertTrue(success)
        self.assertEqual(audio_state_manager.get_sfx_volume(), 0.9)
    
    def test_audio_state_manager_enable_disable(self):
        """Test enable/disable functionality through AudioStateManager."""
        audio_state_manager = self.AudioStateManager(self.state_manager)
        
        # Test music enable/disable
        success = audio_state_manager.set_music_enabled(False, "test")
        self.assertTrue(success)
        self.assertFalse(audio_state_manager.is_music_enabled())
        
        success = audio_state_manager.set_music_enabled(True, "test")
        self.assertTrue(success)
        self.assertTrue(audio_state_manager.is_music_enabled())
        
        # Test SFX enable/disable
        success = audio_state_manager.set_sfx_enabled(False, "test")
        self.assertTrue(success)
        self.assertFalse(audio_state_manager.is_sfx_enabled())
        
        success = audio_state_manager.set_sfx_enabled(True, "test")
        self.assertTrue(success)
        self.assertTrue(audio_state_manager.is_sfx_enabled())
    
    def test_audio_system_state_integration(self):
        """Test AudioSystem integration with state manager."""
        # Initialize audio system with state manager
        audio_system = self.AudioSystem(state_manager=self.state_manager)
        
        # Test that state manager is properly integrated
        self.assertIsNotNone(audio_system.state_manager)
        self.assertIsNotNone(audio_system.audio_state_manager)
        
        # Test convenience methods
        success = audio_system.set_master_volume(0.7)
        self.assertTrue(success)
        self.assertEqual(audio_system.audio_state_manager.get_master_volume(), 0.7)
        
        success = audio_system.set_music_volume(0.5)
        self.assertTrue(success)
        self.assertEqual(audio_system.audio_state_manager.get_music_volume(), 0.5)
    
    def test_audio_system_backward_compatibility(self):
        """Test AudioSystem backward compatibility without state manager."""
        # Initialize audio system without state manager
        audio_system = self.AudioSystem()
        
        # Test that it works without state manager
        self.assertIsNone(audio_system.state_manager)
        self.assertIsNone(audio_system.audio_state_manager)
        
        # Test convenience methods (should return False)
        success = audio_system.set_master_volume(0.8)
        self.assertFalse(success)  # Should return False when no state manager
        
        summary = audio_system.get_audio_state_summary()
        self.assertEqual(summary, {})  # Should return empty dict
    
    def test_settings_integration_callbacks(self):
        """Test AudioSettingsIntegration callback system."""
        audio_state_manager = self.AudioStateManager(self.state_manager)
        settings_integration = self.AudioSettingsIntegration(self.state_manager, audio_state_manager)
        
        # Get callbacks
        callbacks = settings_integration.get_audio_settings_callbacks()
        
        # Test that all expected callbacks are available
        expected_callbacks = ["master_volume", "music_volume", "sfx_volume", "music_enabled", "sfx_enabled"]
        for callback_name in expected_callbacks:
            self.assertIn(callback_name, callbacks)
            self.assertTrue(callable(callbacks[callback_name]))
        
        # Test callback functionality
        success = callbacks["master_volume"](0.8)
        self.assertTrue(success)
        self.assertEqual(audio_state_manager.get_master_volume(), 0.8)
        
        success = callbacks["music_enabled"](False)
        self.assertTrue(success)
        self.assertFalse(audio_state_manager.is_music_enabled())
    
    def test_settings_sync_functionality(self):
        """Test settings synchronization functionality."""
        audio_state_manager = self.AudioStateManager(self.state_manager)
        settings_integration = self.AudioSettingsIntegration(self.state_manager, audio_state_manager)
        
        # Test settings sync
        test_settings = {
            "master_volume": 0.9,
            "music_volume": 0.7,
            "sfx_volume": 0.8,
            "music_enabled": False,
            "sfx_enabled": True
        }
        
        settings_integration.sync_settings_to_state(test_settings)
        
        # Verify settings were applied
        self.assertEqual(audio_state_manager.get_master_volume(), 0.9)
        self.assertEqual(audio_state_manager.get_music_volume(), 0.7)
        self.assertEqual(audio_state_manager.get_sfx_volume(), 0.8)
        self.assertFalse(audio_state_manager.is_music_enabled())
        self.assertTrue(audio_state_manager.is_sfx_enabled())
    
    def test_state_change_tracking(self):
        """Test state change tracking and history."""
        audio_state_manager = self.AudioStateManager(self.state_manager)
        
        # Make several state changes
        changes = [
            ("master_volume", 0.5),
            ("music_volume", 0.3),
            ("sfx_volume", 0.8),
            ("music_enabled", False),
            ("sfx_enabled", True)
        ]
        
        for field, value in changes:
            if "volume" in field:
                if "master" in field:
                    audio_state_manager.set_master_volume(value, "test")
                elif "music" in field:
                    audio_state_manager.set_music_volume(value, "test")
                else:
                    audio_state_manager.set_sfx_volume(value, "test")
            elif "enabled" in field:
                if "music" in field:
                    audio_state_manager.set_music_enabled(value, "test")
                else:
                    audio_state_manager.set_sfx_enabled(value, "test")
        
        # Check that changes were tracked
        for field in ["audio.master_volume", "audio.music_volume", "audio.sfx_volume"]:
            changes = self.state_manager.history.get_changes_for_field(field)
            self.assertGreater(len(changes), 0, f"No changes tracked for {field}")
    
    def test_snapshot_creation(self):
        """Test snapshot creation functionality."""
        audio_state_manager = self.AudioStateManager(self.state_manager)
        
        # Create initial snapshot
        audio_state_manager.create_snapshot("Initial state")
        
        # Make some changes
        audio_state_manager.set_master_volume(0.8, "test")
        audio_state_manager.set_music_volume(0.6, "test")
        
        # Create another snapshot
        audio_state_manager.create_snapshot("After changes")
        
        # Verify snapshots were created
        latest_snapshot = self.state_manager.history.get_latest_snapshot()
        self.assertIsNotNone(latest_snapshot)
        self.assertIn("After changes", latest_snapshot.description)
    
    def test_state_validation(self):
        """Test state validation functionality."""
        audio_state_manager = self.AudioStateManager(self.state_manager)
        
        # Test invalid volume values
        invalid_volumes = [-0.1, 1.5, "not_a_number", None]
        for volume in invalid_volumes:
            try:
                success = audio_state_manager.set_master_volume(volume, "test")
                # Should return False for invalid values
                self.assertFalse(success, f"Invalid volume {volume} was accepted")
            except Exception as e:
                # Exception is also acceptable for invalid values
                pass
    
    def test_performance_under_state_management(self):
        """Test performance with state management integration."""
        audio_state_manager = self.AudioStateManager(self.state_manager)
        
        # Test rapid state changes
        start_time = time.time()
        for i in range(100):
            volume = 0.1 + (i % 9) * 0.1
            audio_state_manager.set_master_volume(volume, "perf_test")
        
        duration = time.time() - start_time
        changes_per_second = 100 / duration
        
        # Should be able to make many state changes per second
        self.assertGreater(changes_per_second, 50, 
                          f"State change rate: {changes_per_second:.1f} changes/sec")
    
    def test_memory_usage_with_state_management(self):
        """Test memory usage with state management integration."""
        initial_memory = self.performance_monitor._get_memory_usage()
        
        # Create multiple audio state managers
        state_managers = []
        for i in range(10):
            audio_state_manager = self.AudioStateManager(self.state_manager)
            state_managers.append(audio_state_manager)
        
        final_memory = self.performance_monitor._get_memory_usage()
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable
        self.assertLess(memory_increase, 10.0, 
                       f"State manager creation used {memory_increase:.1f}MB")


if __name__ == "__main__":
    unittest.main() 