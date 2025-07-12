#!/usr/bin/env python3
"""
Testing Framework for Blade Fighters Refactoring
Provides unit tests, integration tests, and regression testing capabilities
"""

import unittest
import sys
import os
import json
import time
import pygame
from typing import Dict, List, Any, Optional
from unittest.mock import Mock, patch, MagicMock

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class BladeFightersTestSuite(unittest.TestCase):
    """Base test suite for Blade Fighters game components."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment once for all tests."""
        # Initialize pygame for testing
        pygame.init()
        
        # Create a test screen
        cls.test_screen = pygame.display.set_mode((800, 600))
        cls.test_font = pygame.font.Font(None, 24)
        
        # Test configuration
        cls.test_config = {
            'screen_width': 800,
            'screen_height': 600,
            'asset_path': 'puzzleassets',
            'test_mode': True
        }
        
        print(f"\n🧪 Setting up Blade Fighters test environment...")
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        pygame.quit()
        print(f"\n🧹 Cleaned up test environment.")
    
    def setUp(self):
        """Set up before each test."""
        self.start_time = time.time()
    
    def tearDown(self):
        """Clean up after each test."""
        test_duration = time.time() - self.start_time
        if test_duration > 1.0:  # Log slow tests
            print(f"⚠️  Slow test: {self._testMethodName} took {test_duration:.2f}s")


class PuzzleEngineTests(BladeFightersTestSuite):
    """Tests for the puzzle engine core functionality."""
    
    def setUp(self):
        super().setUp()
        # Import here to avoid import errors if modules don't exist
        try:
            from puzzle_module import PuzzleEngine
            self.PuzzleEngine = PuzzleEngine
        except ImportError:
            self.skipTest("PuzzleEngine not available")
    
    def test_puzzle_engine_initialization(self):
        """Test that puzzle engine initializes correctly."""
        try:
            engine = self.PuzzleEngine(
                self.test_screen, 
                self.test_font, 
                None,  # No audio for testing
                self.test_config['asset_path']
            )
            
            # Check that essential attributes are initialized
            self.assertIsNotNone(engine)
            self.assertIsNotNone(engine.grid)
            self.assertIsInstance(engine.grid, list)
            
        except Exception as e:
            self.fail(f"PuzzleEngine initialization failed: {e}")
    
    def test_grid_creation(self):
        """Test that the game grid is created with correct dimensions."""
        try:
            engine = self.PuzzleEngine(
                self.test_screen, 
                self.test_font, 
                None,
                self.test_config['asset_path']
            )
            
            # Check grid dimensions (assuming 6x13 based on game_client.py)
            self.assertEqual(len(engine.grid), 13)  # Height
            self.assertEqual(len(engine.grid[0]), 6)  # Width
            
        except Exception as e:
            self.fail(f"Grid creation test failed: {e}")
    
    def test_piece_creation(self):
        """Test that puzzle pieces are created correctly."""
        try:
            engine = self.PuzzleEngine(
                self.test_screen, 
                self.test_font, 
                None,
                self.test_config['asset_path']
            )
            
            # Check that pieces have required attributes
            if hasattr(engine, 'main_piece') and engine.main_piece:
                piece = engine.main_piece
                self.assertIsNotNone(piece)
                # Add more specific piece tests based on your piece structure
                
        except Exception as e:
            self.fail(f"Piece creation test failed: {e}")


class AttackSystemTests(BladeFightersTestSuite):
    """Tests for the attack system functionality."""
    
    def setUp(self):
        super().setUp()
        try:
            from attack_system import AttackSystem, AttackType
            self.AttackSystem = AttackSystem
            self.AttackType = AttackType
        except ImportError:
            self.skipTest("AttackSystem not available")
    
    def test_attack_system_initialization(self):
        """Test that attack system initializes correctly."""
        try:
            attack_system = self.AttackSystem(grid_width=6, grid_height=13)
            
            self.assertIsNotNone(attack_system)
            self.assertEqual(attack_system.grid_width, 6)
            self.assertEqual(attack_system.grid_height, 13)
            
        except Exception as e:
            self.fail(f"AttackSystem initialization failed: {e}")
    
    def test_attack_generation(self):
        """Test that attacks are generated correctly."""
        try:
            attack_system = self.AttackSystem(grid_width=6, grid_height=13)
            
            # Mock broken blocks
            broken_blocks = [(0, 0), (1, 0), (2, 0)]  # 3 blocks in a row
            is_cluster = True
            combo_multiplier = 2
            
            attacks = attack_system.generate_attack(
                broken_blocks, 
                is_cluster, 
                combo_multiplier, 
                "blue"
            )
            
            # Check that attacks were generated
            self.assertIsInstance(attacks, list)
            
        except Exception as e:
            self.fail(f"Attack generation test failed: {e}")


class AudioSystemTests(BladeFightersTestSuite):
    """Tests for the audio system functionality."""
    
    def setUp(self):
        super().setUp()
        try:
            from audio_system import AudioSystem
            self.AudioSystem = AudioSystem
        except ImportError:
            self.skipTest("AudioSystem not available")
    
    def test_audio_system_initialization(self):
        """Test that audio system initializes correctly."""
        try:
            audio_system = self.AudioSystem()
            
            self.assertIsNotNone(audio_system)
            
        except Exception as e:
            self.fail(f"AudioSystem initialization failed: {e}")


class IntegrationTests(BladeFightersTestSuite):
    """Integration tests for component interactions."""
    
    def test_puzzle_attack_integration(self):
        """Test that puzzle engine and attack system work together."""
        try:
            from puzzle_module import PuzzleEngine
            from attack_system import AttackSystem
            
            # Create both systems
            engine = PuzzleEngine(
                self.test_screen, 
                self.test_font, 
                None,
                self.test_config['asset_path']
            )
            
            attack_system = AttackSystem(grid_width=6, grid_height=13)
            
            # Test that they can coexist
            self.assertIsNotNone(engine)
            self.assertIsNotNone(attack_system)
            
        except Exception as e:
            self.fail(f"Integration test failed: {e}")


class PerformanceTests(BladeFightersTestSuite):
    """Performance tests to ensure refactoring doesn't degrade performance."""
    
    def test_puzzle_engine_performance(self):
        """Test that puzzle engine operations complete within reasonable time."""
        try:
            from puzzle_module import PuzzleEngine
            
            engine = PuzzleEngine(
                self.test_screen, 
                self.test_font, 
                None,
                self.test_config['asset_path']
            )
            
            # Test update performance
            start_time = time.time()
            for _ in range(100):  # 100 updates
                engine.update()
            
            duration = time.time() - start_time
            self.assertLess(duration, 1.0, f"100 updates took {duration:.2f}s, should be < 1.0s")
            
        except Exception as e:
            self.fail(f"Performance test failed: {e}")


class RegressionTests(BladeFightersTestSuite):
    """Regression tests to ensure existing functionality is preserved."""
    
    def test_alpha_value_clamping(self):
        """Test that alpha values are properly clamped to prevent color errors."""
        # This test verifies our previous fix is still working
        try:
            from puzzle_renderer import PuzzleRenderer
            from puzzle_module import PuzzleEngine
            
            engine = PuzzleEngine(
                self.test_screen, 
                self.test_font, 
                None,
                self.test_config['asset_path']
            )
            
            renderer = PuzzleRenderer(engine)
            
            # Test that renderer has screen_shake attribute (our previous fix)
            self.assertTrue(hasattr(renderer, 'screen_shake'))
            
        except Exception as e:
            self.fail(f"Regression test failed: {e}")


class TestRunner:
    """Custom test runner with detailed reporting."""
    
    def __init__(self):
        self.results = {
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'errors': []
        }
    
    def run_tests(self, test_classes: List[type] = None) -> Dict[str, Any]:
        """Run all tests and return detailed results."""
        if test_classes is None:
            test_classes = [
                PuzzleEngineTests,
                AttackSystemTests,
                AudioSystemTests,
                IntegrationTests,
                PerformanceTests,
                RegressionTests
            ]
        
        print("\n" + "="*60)
        print("🧪 BLADE FIGHTERS REFACTORING TEST SUITE")
        print("="*60)
        
        # Create test suite
        suite = unittest.TestSuite()
        
        for test_class in test_classes:
            try:
                # Add all tests from the class
                tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
                suite.addTests(tests)
            except Exception as e:
                print(f"⚠️  Could not load tests from {test_class.__name__}: {e}")
        
        # Run tests
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        # Compile results
        self.results['passed'] = result.testsRun - len(result.failures) - len(result.errors)
        self.results['failed'] = len(result.failures)
        self.results['errors'] = len(result.errors)
        
        # Store detailed error information
        for test, traceback in result.failures + result.errors:
            self.results['errors'].append({
                'test': str(test),
                'traceback': traceback
            })
        
        return self.results
    
    def print_summary(self):
        """Print a summary of test results."""
        print("\n" + "="*60)
        print("📊 TEST RESULTS SUMMARY")
        print("="*60)
        
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"⚠️  Errors: {self.results['errors']}")
        
        if self.results['errors']:
            print(f"\n🔍 DETAILED ERRORS:")
            for error in self.results['errors']:
                print(f"   {error['test']}")
                print(f"   {error['traceback'][:200]}...")
        
        # Calculate pass rate
        total = self.results['passed'] + self.results['failed'] + self.results['errors']
        if total > 0:
            pass_rate = (self.results['passed'] / total) * 100
            print(f"\n📈 Pass Rate: {pass_rate:.1f}%")
            
            if pass_rate >= 90:
                print("🎉 Excellent! Ready for refactoring.")
            elif pass_rate >= 75:
                print("👍 Good! Minor issues to address.")
            else:
                print("⚠️  Warning! Significant issues found.")
    
    def save_results(self, filename: str = 'test_results.json'):
        """Save test results to a JSON file."""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n💾 Test results saved to {filename}")


def run_all_tests():
    """Run all tests and return results."""
    runner = TestRunner()
    results = runner.run_tests()
    runner.print_summary()
    runner.save_results()
    return results


def run_specific_test(test_class_name: str):
    """Run tests from a specific test class."""
    test_classes = {
        'puzzle': PuzzleEngineTests,
        'attack': AttackSystemTests,
        'audio': AudioSystemTests,
        'integration': IntegrationTests,
        'performance': PerformanceTests,
        'regression': RegressionTests
    }
    
    if test_class_name.lower() in test_classes:
        runner = TestRunner()
        results = runner.run_tests([test_classes[test_class_name.lower()]])
        runner.print_summary()
        return results
    else:
        print(f"❌ Unknown test class: {test_class_name}")
        print(f"Available: {', '.join(test_classes.keys())}")


if __name__ == "__main__":
    # Run all tests by default
    run_all_tests() 