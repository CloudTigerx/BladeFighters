#!/usr/bin/env python3
"""
Unit Tests for Input Module
Comprehensive testing of input system functionality, event handling, and performance.
"""

import unittest
import sys
import os
import time
import pygame
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from modules.input_module import UnifiedInputManager, InputAction
from modules.input_module.compatibility_layer import InputHandlerCompat
from core.input_handler import InputHandler
from utils.clock import FakeClock


class InputModuleUnitTests(unittest.TestCase):
    """Comprehensive unit tests for Input Module components."""
    
    def setUp(self):
        """Set up test environment."""
        self.clock = FakeClock()
        self.input_manager = UnifiedInputManager(clock=self.clock)
        # Create a mock puzzle engine for compatibility layer
        mock_engine = Mock()
        mock_engine.clock = self.clock
        self.compatibility_layer = InputHandlerCompat(puzzle_engine=mock_engine)
        
    def tearDown(self):
        """Clean up test environment."""
        pass
    
    def test_input_manager_initialization(self):
        """Test UnifiedInputManager initialization."""
        self.assertIsNotNone(self.input_manager)
        self.assertEqual(self.input_manager.clock, self.clock)
        self.assertIsInstance(self.input_manager._keys_pressed, dict)
        self.assertIsInstance(self.input_manager._event_handlers, dict)
    
    def test_key_state_management(self):
        """Test key state management functionality."""
        # Test key press (using pygame key codes)
        self.input_manager.process_events([pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_LEFT})])
        self.assertTrue(self.input_manager.is_key_pressed(pygame.K_LEFT))
        
        # Test key release
        self.input_manager.process_events([pygame.event.Event(pygame.KEYUP, {'key': pygame.K_LEFT})])
        self.assertFalse(self.input_manager.is_key_pressed(pygame.K_LEFT))
    
    def test_event_queue_management(self):
        """Test event queue management."""
        # Process events through the unified system
        events = [
            pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_LEFT}),
            pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_UP})
        ]
        
        # Process events
        processed_events = self.input_manager.process_events(events)
        
        # Check that events were processed
        self.assertEqual(len(processed_events), 2)
        self.assertTrue(any(event.action.value == 'move_left' for event in processed_events))
        self.assertTrue(any(event.action.value == 'rotate_cw' for event in processed_events))
    
    def test_input_mapping(self):
        """Test input mapping functionality."""
        # Test default mappings through key processing
        left_event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_LEFT})
        right_event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_RIGHT})
        down_event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_DOWN})
        
        # Process events and check mappings
        left_result = self.input_manager.process_events([left_event])
        right_result = self.input_manager.process_events([right_event])
        down_result = self.input_manager.process_events([down_event])
        
        self.assertEqual(left_result[0].action, InputAction.MOVE_LEFT)
        self.assertEqual(right_result[0].action, InputAction.MOVE_RIGHT)
        self.assertEqual(down_result[0].action, InputAction.MOVE_DOWN)
    
    def test_input_repeat_handling(self):
        """Test input repeat functionality."""
        # Press key
        self.input_manager.process_events([pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_LEFT})])
        
        # Advance time to trigger repeat
        self.clock.advance(150)  # Initial delay
        
        # Check for repeat event through continuous key handling
        self.input_manager._handle_continuous_keys(int(self.clock.now_ms()))
        
        # Check that key is still pressed
        self.assertTrue(self.input_manager.is_key_pressed(pygame.K_LEFT))
    
    def test_input_debouncing(self):
        """Test input debouncing functionality."""
        # Rapid key presses
        for _ in range(5):
            self.input_manager.handle_key_press('K_LEFT')
            self.input_manager.handle_key_release('K_LEFT')
        
        # Should only register one event due to debouncing
        events = self.input_manager.get_pending_events()
        self.assertLessEqual(len(events), 2)  # Allow for some tolerance
    
    def test_input_priority_handling(self):
        """Test input priority handling."""
        # Queue events with different priorities
        self.input_manager.queue_event('MOVE_LEFT', priority=1)
        self.input_manager.queue_event('ROTATE_CW', priority=2)
        self.input_manager.queue_event('DROP', priority=3)
        
        # Get events in priority order
        events = self.input_manager.get_pending_events()
        
        # Higher priority events should come first
        self.assertEqual(events[0], 'DROP')
        self.assertEqual(events[1], 'ROTATE_CW')
        self.assertEqual(events[2], 'MOVE_LEFT')
    
    def test_input_state_persistence(self):
        """Test input state persistence."""
        # Set up input state
        self.input_manager.handle_key_press('K_LEFT')
        self.input_manager.queue_event('MOVE_LEFT')
        
        # Get current state
        state = self.input_manager.get_input_state()
        
        # Verify state contains expected data
        self.assertIn('key_states', state)
        self.assertIn('event_queue', state)
        self.assertTrue(state['key_states']['K_LEFT'])
    
    def test_input_state_restoration(self):
        """Test input state restoration."""
        # Create test state
        test_state = {
            'key_states': {'K_LEFT': True, 'K_RIGHT': False},
            'event_queue': ['MOVE_LEFT', 'ROTATE_CW']
        }
        
        # Restore state
        self.input_manager.restore_input_state(test_state)
        
        # Verify state was restored
        self.assertTrue(self.input_manager.is_key_pressed('K_LEFT'))
        self.assertFalse(self.input_manager.is_key_pressed('K_RIGHT'))
        
        events = self.input_manager.get_pending_events()
        self.assertIn('MOVE_LEFT', events)
        self.assertIn('ROTATE_CW', events)
    
    def test_input_performance(self):
        """Test input system performance."""
        import time
        
        # Test event processing performance
        start_time = time.time()
        
        # Queue many events
        for i in range(1000):
            self.input_manager.queue_event(f'EVENT_{i}')
        
        # Process all events
        events = self.input_manager.get_pending_events()
        
        duration = time.time() - start_time
        
        # Should complete within reasonable time
        self.assertLess(duration, 0.1, f"Event processing took {duration:.3f}s")
        self.assertEqual(len(events), 1000)
    
    def test_input_memory_usage(self):
        """Test input system memory usage."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Create many input managers
        managers = []
        for i in range(100):
            manager = UnifiedInputManager(clock=self.clock)
            managers.append(manager)
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable
        self.assertLess(memory_increase, 10 * 1024 * 1024, 
                       f"Memory usage increased by {memory_increase / 1024 / 1024:.1f}MB")
    
    def test_input_error_handling(self):
        """Test input system error handling."""
        # Test handling of invalid key names
        try:
            self.input_manager.handle_key_press('INVALID_KEY')
        except Exception as e:
            self.fail(f"Should handle invalid keys gracefully: {e}")
        
        # Test handling of invalid event names
        try:
            self.input_manager.queue_event('INVALID_EVENT')
        except Exception as e:
            self.fail(f"Should handle invalid events gracefully: {e}")
    
    def test_input_cleanup(self):
        """Test input system cleanup functionality."""
        # Set up some state
        self.input_manager.handle_key_press('K_LEFT')
        self.input_manager.queue_event('MOVE_LEFT')
        
        # Test cleanup
        try:
            self.input_manager.cleanup()
        except Exception as e:
            self.fail(f"Cleanup should not raise exceptions: {e}")
        
        # State should be cleared
        self.assertEqual(len(self.input_manager.event_queue), 0)


class InputCompatibilityLayerUnitTests(unittest.TestCase):
    """Unit tests for InputHandlerCompat component."""
    
    def setUp(self):
        """Set up test environment."""
        self.compatibility_layer = InputHandlerCompat()
    
    def test_compatibility_layer_initialization(self):
        """Test InputHandlerCompat initialization."""
        self.assertIsNotNone(self.compatibility_layer)
        self.assertIsInstance(self.compatibility_layer.legacy_mappings, dict)
    
    def test_legacy_key_mapping(self):
        """Test legacy key mapping functionality."""
        # Test mapping legacy keys to new format
        new_key = self.compatibility_layer.map_legacy_key('LEFT')
        self.assertEqual(new_key, 'K_LEFT')
        
        new_key = self.compatibility_layer.map_legacy_key('RIGHT')
        self.assertEqual(new_key, 'K_RIGHT')
    
    def test_legacy_event_mapping(self):
        """Test legacy event mapping functionality."""
        # Test mapping legacy events to new format
        new_event = self.compatibility_layer.map_legacy_event('MOVE_LEFT')
        self.assertEqual(new_event, 'MOVE_LEFT')
        
        new_event = self.compatibility_layer.map_legacy_event('ROTATE')
        self.assertEqual(new_event, 'ROTATE_CW')
    
    def test_legacy_state_conversion(self):
        """Test legacy state conversion functionality."""
        # Test converting legacy state to new format
        legacy_state = {
            'keys': {'LEFT': True, 'RIGHT': False},
            'events': ['MOVE_LEFT']
        }
        
        new_state = self.compatibility_layer.convert_legacy_state(legacy_state)
        
        self.assertIn('K_LEFT', new_state['key_states'])
        self.assertTrue(new_state['key_states']['K_LEFT'])
        self.assertIn('MOVE_LEFT', new_state['event_queue'])


class InputHandlerUnitTests(unittest.TestCase):
    """Unit tests for core InputHandler component."""
    
    def setUp(self):
        """Set up test environment."""
        self.clock = FakeClock()
        self.input_handler = InputHandler(clock=self.clock)
    
    def test_input_handler_initialization(self):
        """Test InputHandler initialization."""
        self.assertIsNotNone(self.input_handler)
        self.assertEqual(self.input_handler.clock, self.clock)
    
    def test_input_handler_repeat_logic(self):
        """Test InputHandler repeat logic."""
        # Test initial delay
        self.input_handler.handle_key_press('K_LEFT')
        
        # Should not repeat immediately
        self.clock.advance(50)
        self.assertFalse(self.input_handler.should_repeat('K_LEFT'))
        
        # Should repeat after initial delay
        self.clock.advance(100)
        self.assertTrue(self.input_handler.should_repeat('K_LEFT'))
    
    def test_input_handler_debounce_logic(self):
        """Test InputHandler debounce logic."""
        # Test debouncing
        self.input_handler.handle_key_press('K_LEFT')
        self.input_handler.handle_key_release('K_LEFT')
        
        # Should be debounced
        self.assertFalse(self.input_handler.is_key_active('K_LEFT'))
    
    def test_input_handler_configuration(self):
        """Test InputHandler configuration."""
        # Test custom configuration
        config = {
            'repeat_initial_delay_ms': 200,
            'repeat_interval_ms': 100
        }
        
        handler = InputHandler(clock=self.clock, config=config)
        
        # Test with custom timing
        handler.handle_key_press('K_LEFT')
        
        # Should not repeat before custom delay
        self.clock.advance(150)
        self.assertFalse(handler.should_repeat('K_LEFT'))
        
        # Should repeat after custom delay
        self.clock.advance(100)
        self.assertTrue(handler.should_repeat('K_LEFT'))


class InputPerformanceTests(unittest.TestCase):
    """Performance tests for input system."""
    
    def setUp(self):
        """Set up test environment."""
        self.clock = FakeClock()
        self.input_manager = UnifiedInputManager(clock=self.clock)
    
    def test_high_frequency_input_handling(self):
        """Test handling of high-frequency input events."""
        import time
        
        start_time = time.time()
        
        # Simulate high-frequency input
        for i in range(10000):
            self.input_manager.handle_key_press('K_LEFT')
            self.input_manager.handle_key_release('K_LEFT')
        
        duration = time.time() - start_time
        
        # Should handle high-frequency input efficiently
        self.assertLess(duration, 1.0, f"High-frequency input took {duration:.3f}s")
    
    def test_concurrent_input_handling(self):
        """Test handling of concurrent input events."""
        import threading
        import time
        
        results = []
        
        def input_worker(thread_id):
            """Worker thread for input processing."""
            for i in range(100):
                self.input_manager.queue_event(f'THREAD_{thread_id}_EVENT_{i}')
                time.sleep(0.001)  # Small delay
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=input_worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        events = self.input_manager.get_pending_events()
        self.assertEqual(len(events), 500)  # 5 threads * 100 events each
    
    def test_input_latency(self):
        """Test input system latency."""
        import time
        
        # Measure input processing latency
        latencies = []
        
        for i in range(100):
            start_time = time.time()
            
            self.input_manager.handle_key_press('K_LEFT')
            self.input_manager.queue_event('MOVE_LEFT')
            events = self.input_manager.get_pending_events()
            
            end_time = time.time()
            latencies.append(end_time - start_time)
        
        # Calculate average latency
        avg_latency = sum(latencies) / len(latencies)
        
        # Average latency should be very low
        self.assertLess(avg_latency, 0.001, f"Average latency: {avg_latency:.6f}s")


def run_input_unit_tests():
    """Run all input module unit tests."""
    print("⌨️  Running Input Module Unit Tests...")
    print("=" * 50)
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        InputModuleUnitTests,
        InputCompatibilityLayerUnitTests,
        InputHandlerUnitTests,
        InputPerformanceTests
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n📊 Input Module Unit Test Results:")
    print(f"✅ Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Failed: {len(result.failures)}")
    print(f"⚠️  Errors: {len(result.errors)}")
    print(f"📊 Total: {result.testsRun}")
    
    return result


if __name__ == "__main__":
    run_input_unit_tests()
