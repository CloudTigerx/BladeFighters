#!/usr/bin/env python3
"""
Unit Tests for Audio Module
Comprehensive testing of audio system functionality, performance, and edge cases.
"""

import unittest
import sys
import os
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from modules.audio_module import AudioSystem
from modules.audio_module.audio_manager import AudioManager
from modules.audio_module.sound_manager import SoundManager
from modules.audio_module.music_manager import MusicManager


class AudioModuleUnitTests(unittest.TestCase):
    """Comprehensive unit tests for Audio Module components."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_asset_path = tempfile.mkdtemp()
        self.create_test_audio_files()
        
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_asset_path, ignore_errors=True)
    
    def create_test_audio_files(self):
        """Create mock audio files for testing."""
        # Create test sound files
        sounds_dir = os.path.join(self.test_asset_path, "sounds", "effects")
        os.makedirs(sounds_dir, exist_ok=True)
        
        # Create empty audio files
        test_sounds = ["click.wav", "clusterformed.mp3", "double.mp3"]
        for sound in test_sounds:
            with open(os.path.join(sounds_dir, sound), 'w') as f:
                f.write("mock audio data")
        
        # Create test music files
        songs_dir = os.path.join(self.test_asset_path, "sounds", "songs")
        os.makedirs(songs_dir, exist_ok=True)
        
        test_songs = ["test_song1.mp3", "test_song2.mp3"]
        for song in test_songs:
            with open(os.path.join(songs_dir, song), 'w') as f:
                f.write("mock music data")
    
    def test_audio_system_initialization(self):
        """Test AudioSystem initialization with valid asset path."""
        audio_system = AudioSystem(self.test_asset_path)
        
        self.assertIsNotNone(audio_system)
        self.assertEqual(audio_system.asset_path, self.test_asset_path)
        self.assertIsInstance(audio_system.sounds, dict)
        self.assertIsInstance(audio_system.songs, list)
    
    def test_audio_system_invalid_path(self):
        """Test AudioSystem initialization with invalid asset path."""
        with self.assertRaises(FileNotFoundError):
            AudioSystem("/nonexistent/path")
    
    def test_sound_loading(self):
        """Test that sound files are loaded correctly."""
        audio_system = AudioSystem(self.test_asset_path)
        
        # Check that sounds were loaded
        self.assertGreater(len(audio_system.sounds), 0)
        
        # Check specific sound files
        expected_sounds = ["click", "clusterformed", "double"]
        for sound_name in expected_sounds:
            self.assertIn(sound_name, audio_system.sounds)
    
    def test_music_loading(self):
        """Test that music files are loaded correctly."""
        audio_system = AudioSystem(self.test_asset_path)
        
        # Check that songs were loaded
        self.assertGreater(len(audio_system.songs), 0)
        
        # Check specific song files
        expected_songs = ["test_song1", "test_song2"]
        for song_name in expected_songs:
            self.assertIn(song_name, [os.path.splitext(s)[0] for s in audio_system.songs])
    
    @patch('pygame.mixer.Sound')
    def test_sound_playback(self, mock_sound):
        """Test sound playback functionality."""
        audio_system = AudioSystem(self.test_asset_path)
        
        # Mock the sound object
        mock_sound_instance = Mock()
        mock_sound.return_value = mock_sound_instance
        
        # Test playing a sound
        audio_system.play_sound("click")
        
        # Verify sound was created and played
        mock_sound.assert_called()
        mock_sound_instance.play.assert_called()
    
    def test_sound_playback_invalid_sound(self):
        """Test sound playback with invalid sound name."""
        audio_system = AudioSystem(self.test_asset_path)
        
        # Should not raise exception for invalid sound
        try:
            audio_system.play_sound("nonexistent_sound")
        except Exception as e:
            self.fail(f"Should handle invalid sound gracefully: {e}")
    
    @patch('pygame.mixer.music')
    def test_music_playback(self, mock_music):
        """Test music playback functionality."""
        audio_system = AudioSystem(self.test_asset_path)
        
        # Test playing music
        audio_system.play_music("test_song1")
        
        # Verify music was loaded and played
        mock_music.load.assert_called()
        mock_music.play.assert_called()
    
    def test_volume_control(self):
        """Test volume control functionality."""
        audio_system = AudioSystem(self.test_asset_path)
        
        # Test setting master volume
        audio_system.set_master_volume(0.5)
        self.assertEqual(audio_system.get_master_volume(), 0.5)
        
        # Test volume clamping
        audio_system.set_master_volume(1.5)  # Should clamp to 1.0
        self.assertEqual(audio_system.get_master_volume(), 1.0)
        
        audio_system.set_master_volume(-0.5)  # Should clamp to 0.0
        self.assertEqual(audio_system.get_master_volume(), 0.0)
    
    def test_sound_volume_control(self):
        """Test individual sound volume control."""
        audio_system = AudioSystem(self.test_asset_path)
        
        # Test setting sound volume
        audio_system.set_sound_volume("click", 0.7)
        self.assertEqual(audio_system.get_sound_volume("click"), 0.7)
    
    def test_music_volume_control(self):
        """Test music volume control."""
        audio_system = AudioSystem(self.test_asset_path)
        
        # Test setting music volume
        audio_system.set_music_volume(0.6)
        self.assertEqual(audio_system.get_music_volume(), 0.6)
    
    def test_audio_state_management(self):
        """Test audio state management and persistence."""
        audio_system = AudioSystem(self.test_asset_path)
        
        # Set various audio states
        audio_system.set_master_volume(0.8)
        audio_system.set_sound_volume("click", 0.9)
        audio_system.set_music_volume(0.7)
        
        # Get audio state
        state = audio_system.get_audio_state()
        
        # Verify state contains expected values
        self.assertEqual(state["master_volume"], 0.8)
        self.assertEqual(state["sound_volumes"]["click"], 0.9)
        self.assertEqual(state["music_volume"], 0.7)
    
    def test_audio_state_restoration(self):
        """Test audio state restoration from saved state."""
        audio_system = AudioSystem(self.test_asset_path)
        
        # Create test state
        test_state = {
            "master_volume": 0.75,
            "sound_volumes": {"click": 0.8, "double": 0.6},
            "music_volume": 0.65
        }
        
        # Restore state
        audio_system.restore_audio_state(test_state)
        
        # Verify state was restored
        self.assertEqual(audio_system.get_master_volume(), 0.75)
        self.assertEqual(audio_system.get_sound_volume("click"), 0.8)
        self.assertEqual(audio_system.get_sound_volume("double"), 0.6)
        self.assertEqual(audio_system.get_music_volume(), 0.65)
    
    def test_audio_events(self):
        """Test audio event handling."""
        audio_system = AudioSystem(self.test_asset_path)
        
        # Test audio event registration
        test_event = "test_event"
        test_sound = "click"
        
        audio_system.register_audio_event(test_event, test_sound)
        
        # Verify event was registered
        self.assertIn(test_event, audio_system.audio_events)
        self.assertEqual(audio_system.audio_events[test_event], test_sound)
    
    @patch('pygame.mixer.Sound')
    def test_audio_event_triggering(self, mock_sound):
        """Test audio event triggering."""
        audio_system = AudioSystem(self.test_asset_path)
        
        # Mock sound
        mock_sound_instance = Mock()
        mock_sound.return_value = mock_sound_instance
        
        # Register and trigger event
        audio_system.register_audio_event("piece_landed", "click")
        audio_system.trigger_audio_event("piece_landed")
        
        # Verify sound was played
        mock_sound_instance.play.assert_called()
    
    def test_audio_performance(self):
        """Test audio system performance characteristics."""
        audio_system = AudioSystem(self.test_asset_path)
        
        # Test initialization performance
        import time
        start_time = time.time()
        
        # Create multiple audio systems to test performance
        for _ in range(10):
            AudioSystem(self.test_asset_path)
        
        duration = time.time() - start_time
        
        # Should complete within reasonable time
        self.assertLess(duration, 5.0, f"Audio system initialization took {duration:.2f}s")
    
    def test_audio_memory_usage(self):
        """Test audio system memory usage."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Create audio system
        audio_system = AudioSystem(self.test_asset_path)
        
        # Load multiple sounds
        for i in range(10):
            audio_system.load_sound(f"test_sound_{i}")
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 50MB)
        self.assertLess(memory_increase, 50 * 1024 * 1024, 
                       f"Memory usage increased by {memory_increase / 1024 / 1024:.1f}MB")
    
    def test_audio_error_handling(self):
        """Test audio system error handling."""
        audio_system = AudioSystem(self.test_asset_path)
        
        # Test handling of missing sound files
        try:
            audio_system.play_sound("nonexistent")
        except Exception as e:
            self.fail(f"Should handle missing sounds gracefully: {e}")
        
        # Test handling of invalid volume values
        try:
            audio_system.set_master_volume("invalid")
        except (TypeError, ValueError):
            pass  # Expected behavior
        else:
            self.fail("Should handle invalid volume values")
    
    def test_audio_cleanup(self):
        """Test audio system cleanup functionality."""
        audio_system = AudioSystem(self.test_asset_path)
        
        # Test cleanup method
        try:
            audio_system.cleanup()
        except Exception as e:
            self.fail(f"Cleanup should not raise exceptions: {e}")


class AudioManagerUnitTests(unittest.TestCase):
    """Unit tests for AudioManager component."""
    
    def setUp(self):
        """Set up test environment."""
        self.audio_manager = AudioManager()
    
    def test_audio_manager_initialization(self):
        """Test AudioManager initialization."""
        self.assertIsNotNone(self.audio_manager)
        self.assertIsInstance(self.audio_manager.volume, float)
        self.assertIsInstance(self.audio_manager.enabled, bool)
    
    def test_volume_control(self):
        """Test AudioManager volume control."""
        self.audio_manager.set_volume(0.5)
        self.assertEqual(self.audio_manager.get_volume(), 0.5)
    
    def test_enable_disable(self):
        """Test AudioManager enable/disable functionality."""
        self.audio_manager.disable()
        self.assertFalse(self.audio_manager.is_enabled())
        
        self.audio_manager.enable()
        self.assertTrue(self.audio_manager.is_enabled())


class SoundManagerUnitTests(unittest.TestCase):
    """Unit tests for SoundManager component."""
    
    def setUp(self):
        """Set up test environment."""
        self.sound_manager = SoundManager()
    
    def test_sound_manager_initialization(self):
        """Test SoundManager initialization."""
        self.assertIsNotNone(self.sound_manager)
        self.assertIsInstance(self.sound_manager.sounds, dict)
    
    def test_sound_registration(self):
        """Test sound registration functionality."""
        self.sound_manager.register_sound("test_sound", "test_path.wav")
        self.assertIn("test_sound", self.sound_manager.sounds)
        self.assertEqual(self.sound_manager.sounds["test_sound"], "test_path.wav")


class MusicManagerUnitTests(unittest.TestCase):
    """Unit tests for MusicManager component."""
    
    def setUp(self):
        """Set up test environment."""
        self.music_manager = MusicManager()
    
    def test_music_manager_initialization(self):
        """Test MusicManager initialization."""
        self.assertIsNotNone(self.music_manager)
        self.assertIsInstance(self.music_manager.current_track, str)
        self.assertIsInstance(self.music_manager.volume, float)
    
    def test_track_management(self):
        """Test music track management."""
        self.music_manager.set_track("test_track.mp3")
        self.assertEqual(self.music_manager.get_current_track(), "test_track.mp3")


def run_audio_unit_tests():
    """Run all audio module unit tests."""
    print("🎵 Running Audio Module Unit Tests...")
    print("=" * 50)
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        AudioModuleUnitTests,
        AudioManagerUnitTests,
        SoundManagerUnitTests,
        MusicManagerUnitTests
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n📊 Audio Module Unit Test Results:")
    print(f"✅ Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Failed: {len(result.failures)}")
    print(f"⚠️  Errors: {len(result.errors)}")
    print(f"📊 Total: {result.testsRun}")
    
    return result


if __name__ == "__main__":
    run_audio_unit_tests()
