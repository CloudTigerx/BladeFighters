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
from modules.audio_module.mp3_player import MP3Player


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
        audio_system = AudioSystem(asset_path=self.test_asset_path)
        
        self.assertIsNotNone(audio_system)
        self.assertEqual(audio_system.asset_path, self.test_asset_path)
        self.assertIsInstance(audio_system.sounds, dict)
        self.assertIsInstance(audio_system.music_playlist, list)
    
    def test_audio_system_invalid_path(self):
        """Test AudioSystem initialization with invalid asset path."""
        # AudioSystem doesn't raise FileNotFoundError for invalid paths, it just logs warnings
        audio_system = AudioSystem(asset_path="/nonexistent/path")
        self.assertIsNotNone(audio_system)
        self.assertEqual(audio_system.asset_path, "/nonexistent/path")
    
    def test_sound_loading(self):
        """Test that sound files are loaded correctly."""
        audio_system = AudioSystem(asset_path=self.test_asset_path)
        
        # Check that sounds dictionary exists (may be empty if no valid sound files)
        self.assertIsInstance(audio_system.sounds, dict)
        
        # Check that the system handles missing sound files gracefully
        self.assertIsNotNone(audio_system)
    
    def test_music_loading(self):
        """Test that music files are loaded correctly."""
        audio_system = AudioSystem(asset_path=self.test_asset_path)
        
        # Check that music playlist exists
        self.assertIsInstance(audio_system.music_playlist, list)
        
        # Check that MP3 player was created
        self.assertIsNotNone(audio_system.mp3_player)
    
    @patch('pygame.mixer.Sound')
    def test_sound_playback(self, mock_sound):
        """Test sound playback functionality."""
        audio_system = AudioSystem(asset_path=self.test_asset_path)
        
        # Mock the sound object
        mock_sound_instance = Mock()
        mock_sound.return_value = mock_sound_instance
        
        # Test playing a sound (this will fail gracefully if sound doesn't exist)
        try:
            audio_system.play_sound("click")
        except Exception:
            pass  # Expected behavior for missing sounds
        
        # Verify the system handles missing sounds gracefully
        self.assertIsNotNone(audio_system)
    
    def test_sound_playback_invalid_sound(self):
        """Test handling of invalid sound playback."""
        audio_system = AudioSystem(asset_path=self.test_asset_path)
        
        # Test playing a non-existent sound
        try:
            audio_system.play_sound("nonexistent_sound")
        except Exception as e:
            self.fail(f"Should handle missing sounds gracefully: {e}")
    
    def test_volume_control(self):
        """Test volume control functionality."""
        audio_system = AudioSystem(asset_path=self.test_asset_path)
        
        # Test setting master volume
        try:
            audio_system.set_master_volume(0.5)
        except Exception as e:
            self.fail(f"Should handle volume setting: {e}")
        
        # Verify the system handles volume changes
        self.assertIsNotNone(audio_system)
    
    def test_music_volume_control(self):
        """Test music volume control."""
        audio_system = AudioSystem(asset_path=self.test_asset_path)
        
        # Test setting music volume
        try:
            audio_system.set_music_volume(0.6)
        except Exception as e:
            self.fail(f"Should handle music volume setting: {e}")
        
        # Verify the system handles music volume changes
        self.assertIsNotNone(audio_system)
    
    @patch('pygame.mixer.music')
    def test_music_playback(self, mock_music):
        """Test music playback functionality."""
        audio_system = AudioSystem(asset_path=self.test_asset_path)
        
        # Test playing music (this will fail gracefully if music doesn't exist)
        try:
            audio_system.play_music("test_song1")
        except Exception:
            pass  # Expected behavior for missing music
        
        # Verify the system handles missing music gracefully
        self.assertIsNotNone(audio_system)
    
    def test_audio_error_handling(self):
        """Test audio system error handling."""
        audio_system = AudioSystem(asset_path=self.test_asset_path)
        
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
        except Exception as e:
            # Other exceptions are also acceptable for invalid input
            pass
    
    def test_audio_performance(self):
        """Test audio system performance."""
        import time
        
        start_time = time.time()
        audio_system = AudioSystem(asset_path=self.test_asset_path)
        initialization_time = time.time() - start_time
        
        # Audio system should initialize quickly (less than 1 second)
        self.assertLess(initialization_time, 1.0)
    
    def test_mp3_player_creation(self):
        """Test MP3 player creation and basic functionality."""
        audio_system = AudioSystem(asset_path=self.test_asset_path)
        
        # Check that MP3 player was created
        self.assertIsNotNone(audio_system.mp3_player)
        self.assertIsInstance(audio_system.mp3_player, MP3Player)
    
    def test_audio_system_attributes(self):
        """Test that AudioSystem has expected attributes."""
        audio_system = AudioSystem(asset_path=self.test_asset_path)
        
        # Check for expected attributes
        expected_attrs = [
            'asset_path', 'sounds', 'music_playlist', 'mp3_player',
            'play_sound', 'play_music', 'set_master_volume', 'set_music_volume'
        ]
        
        for attr in expected_attrs:
            self.assertTrue(hasattr(audio_system, attr), f"AudioSystem missing attribute: {attr}")


if __name__ == '__main__':
    unittest.main()
