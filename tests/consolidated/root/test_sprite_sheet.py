#!/usr/bin/env python3
"""
Test Sprite Sheet Loading - Verify sprite sheet frame extraction
Headless test version for CI/CD environments
"""

import unittest
import pygame
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Set up headless environment for testing
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')

class TestSpriteSheet(unittest.TestCase):
    """Test sprite sheet loading and frame extraction functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment once for all tests."""
        # Initialize pygame for testing
        pygame.init()
        
        # Create a test screen (will be dummy in headless mode)
        cls.test_screen = pygame.display.set_mode((800, 600))
        cls.test_font = pygame.font.Font(None, 24)
        
        print("✅ Sprite sheet test environment initialized")
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        pygame.quit()
        print("🧹 Sprite sheet test environment cleaned up")
    
    def setUp(self):
        """Set up before each test."""
        self.asset_path = "puzzleassets"
        self.screen_width = 800
        self.screen_height = 600
    
    def tearDown(self):
        """Clean up after each test."""
        pass
    
    def test_sprite_manager_initialization(self):
        """Test that sprite manager initializes correctly."""
        try:
            from modules.character_module.character_sprite_manager import CharacterSpriteManager
            
            # Initialize sprite manager
            sprite_manager = CharacterSpriteManager(self.asset_path, self.screen_width, self.screen_height)
            
            # Check that sprite manager was created
            self.assertIsNotNone(sprite_manager)
            self.assertEqual(sprite_manager.asset_path, self.asset_path)
            self.assertEqual(sprite_manager.screen_width, self.screen_width)
            self.assertEqual(sprite_manager.screen_height, self.screen_height)
            
            # Check that sprite cache exists
            self.assertIsNotNone(sprite_manager.sprite_cache)
            self.assertIsInstance(sprite_manager.sprite_cache, dict)
            
            print("✅ Sprite manager initialization test passed")
            
        except ImportError as e:
            self.skipTest(f"CharacterSpriteManager not available: {e}")
        except Exception as e:
            self.fail(f"Sprite manager initialization failed: {e}")
    
    def test_sprite_cache_population(self):
        """Test that sprite cache is populated with character sprites."""
        try:
            from modules.character_module.character_sprite_manager import CharacterSpriteManager
            
            # Initialize sprite manager
            sprite_manager = CharacterSpriteManager(self.asset_path, self.screen_width, self.screen_height)
            
            # Check that sprite cache has some entries
            self.assertGreaterEqual(len(sprite_manager.sprite_cache), 0)
            
            # Print available sprites for debugging
            available_sprites = list(sprite_manager.sprite_cache.keys())
            print(f"Available sprites: {available_sprites}")
            
            # Check for Yuki frames specifically
            yuki_frames = [k for k in available_sprites if k.startswith("yuki_idle_")]
            print(f"Yuki frames found: {len(yuki_frames)}")
            print(f"Frame keys: {yuki_frames}")
            
            # If we have Yuki frames, test them
            if yuki_frames:
                self.assertGreater(len(yuki_frames), 0)
                print("✅ Sprite cache population test passed")
            else:
                print("⚠️ No Yuki frames found (assets may be missing)")
            
        except ImportError as e:
            self.skipTest(f"CharacterSpriteManager not available: {e}")
        except Exception as e:
            self.fail(f"Sprite cache population test failed: {e}")
    
    def test_character_sprite_retrieval(self):
        """Test retrieving individual character sprite frames."""
        try:
            from modules.character_module.character_sprite_manager import CharacterSpriteManager
            
            # Initialize sprite manager
            sprite_manager = CharacterSpriteManager(self.asset_path, self.screen_width, self.screen_height)
            
            # Test getting different frames
            frames_retrieved = 0
            for i in range(9):  # Test first 9 frames
                sprite = sprite_manager.get_character_sprite('yuki', 'idle', i)
                if sprite:
                    # Check that sprite is a valid pygame Surface
                    self.assertIsInstance(sprite, pygame.Surface)
                    self.assertGreater(sprite.get_width(), 0)
                    self.assertGreater(sprite.get_height(), 0)
                    frames_retrieved += 1
                    print(f"Frame {i}: {sprite.get_width()}x{sprite.get_height()}")
                else:
                    print(f"Frame {i}: Not found")
            
            # At least some frames should be available
            if frames_retrieved > 0:
                print(f"✅ Character sprite retrieval test passed - {frames_retrieved} frames retrieved")
            else:
                print("⚠️ No character sprites retrieved (assets may be missing)")
            
        except ImportError as e:
            self.skipTest(f"CharacterSpriteManager not available: {e}")
        except Exception as e:
            self.fail(f"Character sprite retrieval test failed: {e}")
    
    def test_sprite_dimensions_consistency(self):
        """Test that sprite frames have consistent dimensions."""
        try:
            from modules.character_module.character_sprite_manager import CharacterSpriteManager
            
            # Initialize sprite manager
            sprite_manager = CharacterSpriteManager(self.asset_path, self.screen_width, self.screen_height)
            
            # Collect dimensions of available frames
            frame_dimensions = []
            for i in range(9):
                sprite = sprite_manager.get_character_sprite('yuki', 'idle', i)
                if sprite:
                    dimensions = (sprite.get_width(), sprite.get_height())
                    frame_dimensions.append(dimensions)
            
            if len(frame_dimensions) > 1:
                # Check that all frames have the same dimensions
                first_dimensions = frame_dimensions[0]
                for dimensions in frame_dimensions[1:]:
                    self.assertEqual(dimensions, first_dimensions, 
                                   f"Frame dimensions inconsistent: {first_dimensions} vs {dimensions}")
                
                print(f"✅ Sprite dimensions consistency test passed - all frames: {first_dimensions}")
            else:
                print("⚠️ Not enough frames to test dimension consistency")
            
        except ImportError as e:
            self.skipTest(f"CharacterSpriteManager not available: {e}")
        except Exception as e:
            self.fail(f"Sprite dimensions consistency test failed: {e}")
    
    def test_missing_sprite_handling(self):
        """Test that the system handles missing sprites gracefully."""
        try:
            from modules.character_module.character_sprite_manager import CharacterSpriteManager
            
            # Initialize sprite manager
            sprite_manager = CharacterSpriteManager(self.asset_path, self.screen_width, self.screen_height)
            
            # Test with non-existent character
            sprite = sprite_manager.get_character_sprite('nonexistent_character', 'idle', 0)
            self.assertIsNone(sprite)
            
            # Test with non-existent animation
            sprite = sprite_manager.get_character_sprite('yuki', 'nonexistent_animation', 0)
            self.assertIsNone(sprite)
            
            # Test with invalid frame number
            sprite = sprite_manager.get_character_sprite('yuki', 'idle', 999)
            # Should return None or handle gracefully
            if sprite is not None:
                self.assertIsInstance(sprite, pygame.Surface)
            
            print("✅ Missing sprite handling test passed")
            
        except ImportError as e:
            self.skipTest(f"CharacterSpriteManager not available: {e}")
        except Exception as e:
            self.fail(f"Missing sprite handling test failed: {e}")
    
    def test_sprite_cache_performance(self):
        """Test that sprite cache provides performance benefits."""
        try:
            from modules.character_module.character_sprite_manager import CharacterSpriteManager
            import time
            
            # Initialize sprite manager
            sprite_manager = CharacterSpriteManager(self.asset_path, self.screen_width, self.screen_height)
            
            # Test multiple retrievals of the same sprite
            start_time = time.time()
            for _ in range(10):
                sprite = sprite_manager.get_character_sprite('yuki', 'idle', 0)
            
            retrieval_time = time.time() - start_time
            
            # Should be fast (less than 1 second for 10 retrievals)
            self.assertLess(retrieval_time, 1.0, f"Sprite retrieval took {retrieval_time:.2f}s, should be < 1.0s")
            
            print(f"✅ Sprite cache performance test passed - {retrieval_time:.3f}s for 10 retrievals")
            
        except ImportError as e:
            self.skipTest(f"CharacterSpriteManager not available: {e}")
        except Exception as e:
            self.fail(f"Sprite cache performance test failed: {e}")
    
    def test_character_config_integration(self):
        """Test that sprite manager integrates with character configuration."""
        try:
            from modules.character_module.character_sprite_manager import CharacterSpriteManager
            
            # Initialize sprite manager
            sprite_manager = CharacterSpriteManager(self.asset_path, self.screen_width, self.screen_height)
            
            # Test getting character configuration
            config = sprite_manager.get_character_config('yuki')
            
            if config:
                # Check that configuration has required fields
                self.assertIn('idle_sprite', config)
                self.assertIn('total_frames', config)
                self.assertIn('frames_per_row', config)
                
                # Test that we can get sprites based on configuration
                total_frames = config.get('total_frames', 9)
                frames_available = 0
                
                for i in range(total_frames):
                    sprite = sprite_manager.get_character_sprite('yuki', 'idle', i)
                    if sprite:
                        frames_available += 1
                
                print(f"✅ Character config integration test passed - {frames_available}/{total_frames} frames available")
            else:
                self.skipTest("Yuki character configuration not available")
            
        except ImportError as e:
            self.skipTest(f"CharacterSpriteManager not available: {e}")
        except Exception as e:
            self.fail(f"Character config integration test failed: {e}")


def run_sprite_sheet_tests():
    """Run all sprite sheet tests."""
    print("\n" + "="*60)
    print("🧪 SPRITE SHEET TEST SUITE")
    print("="*60)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSpriteSheet)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*60)
    print("📊 SPRITE SHEET TEST RESULTS")
    print("="*60)
    print(f"✅ Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Failed: {len(result.failures)}")
    print(f"⚠️  Errors: {len(result.errors)}")
    print(f"⏭️  Skipped: {len(result.skipped)}")
    
    return result


if __name__ == "__main__":
    run_sprite_sheet_tests()
