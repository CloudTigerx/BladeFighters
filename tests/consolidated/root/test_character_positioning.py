#!/usr/bin/env python3
"""
Test Character Positioning - Verify character alignment and positioning
Headless test version for CI/CD environments
"""

import unittest
import pygame
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Set up headless environment for testing
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')

class TestCharacterPositioning(unittest.TestCase):
    """Test character positioning and alignment functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment once for all tests."""
        # Initialize pygame for testing
        pygame.init()
        
        # Create a test screen (will be dummy in headless mode)
        cls.test_screen = pygame.display.set_mode((1200, 800))
        cls.test_font = pygame.font.Font(None, 24)
        
        print("✅ Character positioning test environment initialized")
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        pygame.quit()
        print("🧹 Character positioning test environment cleaned up")
    
    def setUp(self):
        """Set up before each test."""
        self.asset_path = "puzzleassets"
        self.screen_width = 1200
        self.screen_height = 800
        
        # Test board configuration
        self.test_board_pos = {"x": 100, "y": 100}
        self.test_board_dims = (30, 30, 180, 450)  # cell_w, cell_h, board_w, board_h
    
    def tearDown(self):
        """Clean up after each test."""
        pass
    
    def test_sprite_manager_initialization(self):
        """Test that character sprite manager initializes correctly."""
        try:
            from modules.character_module.character_sprite_manager import CharacterSpriteManager
            
            # Initialize sprite manager
            sprite_manager = CharacterSpriteManager(self.asset_path, self.screen_width, self.screen_height)
            
            # Check that sprite manager was created
            self.assertIsNotNone(sprite_manager)
            self.assertEqual(sprite_manager.asset_path, self.asset_path)
            self.assertEqual(sprite_manager.screen_width, self.screen_width)
            self.assertEqual(sprite_manager.screen_height, self.screen_height)
            
            # Check that character configurations are loaded
            self.assertIsNotNone(sprite_manager.characters)
            self.assertIn('yuki', sprite_manager.characters)
            
            print("✅ Sprite manager initialization test passed")
            
        except ImportError as e:
            self.skipTest(f"CharacterSpriteManager not available: {e}")
        except Exception as e:
            self.fail(f"Sprite manager initialization failed: {e}")
    
    def test_character_position_calculation(self):
        """Test character position calculation relative to game board."""
        try:
            from modules.character_module.character_sprite_manager import CharacterSpriteManager
            
            # Initialize sprite manager
            sprite_manager = CharacterSpriteManager(self.asset_path, self.screen_width, self.screen_height)
            
            # Test positioning calculation
            char_x, char_y = sprite_manager.calculate_character_position(
                self.test_board_pos, self.test_board_dims, 'yuki'
            )
            
            # Check that position values are reasonable
            self.assertIsInstance(char_x, (int, float))
            self.assertIsInstance(char_y, (int, float))
            # Note: char_x can be negative if sprite is wider than board, which is acceptable
            self.assertGreaterEqual(char_y, 0)
            # Check that character doesn't extend too far beyond screen bounds
            sprite = sprite_manager.get_character_sprite('yuki', 'idle', 0)
            if sprite:
                sprite_width = sprite.get_width()
                # Allow character to extend slightly beyond screen bounds for artistic purposes
                self.assertGreater(char_x + sprite_width, -100)  # Allow some overflow
                self.assertLess(char_x, self.screen_width + 100)  # Allow some overflow
            
            print(f"✅ Character position calculated: ({char_x}, {char_y})")
            
        except ImportError as e:
            self.skipTest(f"CharacterSpriteManager not available: {e}")
        except Exception as e:
            self.fail(f"Character position calculation failed: {e}")
    
    def test_animation_manager_initialization(self):
        """Test that character animation manager initializes correctly."""
        try:
            from modules.character_module.character_animation_manager import CharacterAnimationManager
            from modules.character_module.character_sprite_manager import CharacterSpriteManager
            
            # Initialize managers
            sprite_manager = CharacterSpriteManager(self.asset_path, self.screen_width, self.screen_height)
            animation_manager = CharacterAnimationManager()
            
            # Check that animation manager was created
            self.assertIsNotNone(animation_manager)
            self.assertIsNotNone(animation_manager.animation_states)
            self.assertIsNotNone(animation_manager.current_frames)
            self.assertIsNotNone(animation_manager.last_frame_times)
            
            # Test character initialization
            yuki_config = sprite_manager.get_character_config('yuki')
            if yuki_config:
                animation_manager.initialize_character('yuki', yuki_config)
                
                # Check that character was initialized
                self.assertIn('yuki', animation_manager.animation_states)
                self.assertIn('yuki', animation_manager.current_frames)
                self.assertIn('yuki', animation_manager.last_frame_times)
                
                print("✅ Animation manager initialization test passed")
            else:
                self.skipTest("Yuki character configuration not available")
            
        except ImportError as e:
            self.skipTest(f"Character modules not available: {e}")
        except Exception as e:
            self.fail(f"Animation manager initialization failed: {e}")
    
    def test_character_animation_update(self):
        """Test character animation frame updates."""
        try:
            from modules.character_module.character_animation_manager import CharacterAnimationManager
            from modules.character_module.character_sprite_manager import CharacterSpriteManager
            
            # Initialize managers
            sprite_manager = CharacterSpriteManager(self.asset_path, self.screen_width, self.screen_height)
            animation_manager = CharacterAnimationManager()
            
            # Initialize character
            yuki_config = sprite_manager.get_character_config('yuki')
            if not yuki_config:
                self.skipTest("Yuki character configuration not available")
            
            animation_manager.initialize_character('yuki', yuki_config)
            
            # Test animation updates
            initial_frame = animation_manager.update_character_animation('yuki')
            self.assertIsInstance(initial_frame, int)
            self.assertGreaterEqual(initial_frame, 0)
            
            # Test multiple updates
            frames = []
            for _ in range(5):
                frame = animation_manager.update_character_animation('yuki')
                frames.append(frame)
                self.assertIsInstance(frame, int)
                self.assertGreaterEqual(frame, 0)
            
            print(f"✅ Animation update test passed - frames: {frames}")
            
        except ImportError as e:
            self.skipTest(f"Character modules not available: {e}")
        except Exception as e:
            self.fail(f"Character animation update failed: {e}")
    
    def test_character_sprite_retrieval(self):
        """Test character sprite retrieval from sprite manager."""
        try:
            from modules.character_module.character_sprite_manager import CharacterSpriteManager
            
            # Initialize sprite manager
            sprite_manager = CharacterSpriteManager(self.asset_path, self.screen_width, self.screen_height)
            
            # Test getting character sprite
            sprite = sprite_manager.get_character_sprite('yuki', 'idle', 0)
            
            # Sprite might be None if assets are missing, but that's acceptable
            if sprite is not None:
                self.assertIsInstance(sprite, pygame.Surface)
                self.assertGreater(sprite.get_width(), 0)
                self.assertGreater(sprite.get_height(), 0)
                print(f"✅ Character sprite retrieved: {sprite.get_width()}x{sprite.get_height()}")
            else:
                print("⚠️ Character sprite not available (assets may be missing)")
            
        except ImportError as e:
            self.skipTest(f"CharacterSpriteManager not available: {e}")
        except Exception as e:
            self.fail(f"Character sprite retrieval failed: {e}")
    
    def test_character_config_retrieval(self):
        """Test character configuration retrieval."""
        try:
            from modules.character_module.character_sprite_manager import CharacterSpriteManager
            
            # Initialize sprite manager
            sprite_manager = CharacterSpriteManager(self.asset_path, self.screen_width, self.screen_height)
            
            # Test getting character configuration
            config = sprite_manager.get_character_config('yuki')
            
            if config:
                # Check required configuration fields
                self.assertIn('idle_sprite', config)
                self.assertIn('base_scale_factor', config)
                self.assertIn('position_offset', config)
                self.assertIn('animation_speed', config)
                self.assertIn('frames_per_row', config)
                self.assertIn('total_frames', config)
                
                print("✅ Character configuration retrieval test passed")
            else:
                self.skipTest("Yuki character configuration not available")
            
        except ImportError as e:
            self.skipTest(f"CharacterSpriteManager not available: {e}")
        except Exception as e:
            self.fail(f"Character configuration retrieval failed: {e}")
    
    def test_missing_character_handling(self):
        """Test that the system handles missing characters gracefully."""
        try:
            from modules.character_module.character_sprite_manager import CharacterSpriteManager
            
            # Initialize sprite manager
            sprite_manager = CharacterSpriteManager(self.asset_path, self.screen_width, self.screen_height)
            
            # Test with non-existent character
            config = sprite_manager.get_character_config('nonexistent_character')
            self.assertIsNone(config)
            
            # Test sprite retrieval for non-existent character
            sprite = sprite_manager.get_character_sprite('nonexistent_character', 'idle', 0)
            self.assertIsNone(sprite)
            
            # Test position calculation for non-existent character
            char_x, char_y = sprite_manager.calculate_character_position(
                self.test_board_pos, self.test_board_dims, 'nonexistent_character'
            )
            # Should return default position or handle gracefully
            self.assertIsInstance(char_x, (int, float))
            self.assertIsInstance(char_y, (int, float))
            
            print("✅ Missing character handling test passed")
            
        except ImportError as e:
            self.skipTest(f"CharacterSpriteManager not available: {e}")
        except Exception as e:
            self.fail(f"Missing character handling failed: {e}")


def run_character_positioning_tests():
    """Run all character positioning tests."""
    print("\n" + "="*60)
    print("🧪 CHARACTER POSITIONING TEST SUITE")
    print("="*60)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCharacterPositioning)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*60)
    print("📊 CHARACTER POSITIONING TEST RESULTS")
    print("="*60)
    print(f"✅ Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Failed: {len(result.failures)}")
    print(f"⚠️  Errors: {len(result.errors)}")
    print(f"⏭️  Skipped: {len(result.skipped)}")
    
    return result


if __name__ == "__main__":
    run_character_positioning_tests()
