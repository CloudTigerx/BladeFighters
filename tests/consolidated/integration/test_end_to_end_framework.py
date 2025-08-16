#!/usr/bin/env python3
"""
End-to-End Testing Framework for BladeFighters
Comprehensive testing of complete game flow and module interactions.
"""

import unittest
import sys
import os
import time
import json
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.clock import FakeClock
from modules.audio_module import AudioSystem
from modules.input_module import UnifiedInputManager
from modules.screen_module import ScreenManager
from modules.game_state_module.game_state_manager import GameStateManager
from modules.menu_module.scaled_menu_system import ScaledMenuSystem
from modules.testmode_module import TestMode
from core.puzzle_module import PuzzleEngine
from core.puzzle_renderer import PuzzleRenderer


class EndToEndTestFramework:
    """Framework for end-to-end testing of the complete game."""
    
    def __init__(self):
        self.clock = FakeClock()
        self.test_asset_path = tempfile.mkdtemp()
        self.create_test_assets()
        
        # Initialize core systems
        self.screen = Mock()
        self.font = Mock()
        self.audio_system = AudioSystem(self.test_asset_path)
        self.input_manager = UnifiedInputManager(clock=self.clock)
        self.state_manager = GameStateManager()
        self.screen_manager = ScreenManager()
        
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_asset_path, ignore_errors=True)
    
    def create_test_assets(self):
        """Create test assets for end-to-end testing."""
        # Create test audio files
        sounds_dir = os.path.join(self.test_asset_path, "sounds", "effects")
        os.makedirs(sounds_dir, exist_ok=True)
        
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
    
    def simulate_game_startup(self) -> Dict[str, Any]:
        """Simulate complete game startup process."""
        start_time = time.time()
        
        # Initialize all systems
        systems = {
            "audio": self.audio_system,
            "input": self.input_manager,
            "state": self.state_manager,
            "screen": self.screen_manager
        }
        
        # Verify all systems initialized
        for name, system in systems.items():
            self.assertIsNotNone(system, f"{name} system failed to initialize")
        
        # Set initial game state
        initial_state = {
            "puzzle.score": 0,
            "puzzle.level": 1,
            "audio.master_volume": 0.8,
            "screen.current": "main_menu"
        }
        
        self.state_manager.update(initial_state, source="startup")
        
        duration = time.time() - start_time
        
        return {
            "duration": duration,
            "systems_initialized": len(systems),
            "state_set": len(initial_state)
        }
    
    def simulate_menu_navigation(self) -> Dict[str, Any]:
        """Simulate menu navigation flow."""
        start_time = time.time()
        
        # Navigate through menu options
        menu_actions = [
            ("main_menu", "play_game"),
            ("play_game", "test_mode"),
            ("test_mode", "game_start")
        ]
        
        for current_screen, next_screen in menu_actions:
            # Update screen state
            self.state_manager.set("screen.current", next_screen, source="menu_navigation")
            
            # Simulate input events
            self.input_manager.queue_event("MENU_SELECT")
            
            # Process events
            events = self.input_manager.get_pending_events()
            self.assertIn("MENU_SELECT", events)
            
            # Verify screen transition
            current_screen_state = self.state_manager.get("screen.current")
            self.assertEqual(current_screen_state, next_screen)
        
        duration = time.time() - start_time
        
        return {
            "duration": duration,
            "menu_transitions": len(menu_actions),
            "events_processed": len(menu_actions)
        }
    
    def simulate_gameplay_session(self, duration_seconds: int = 10) -> Dict[str, Any]:
        """Simulate a complete gameplay session."""
        start_time = time.time()
        
        # Initialize puzzle engine
        puzzle_engine = PuzzleEngine(self.screen, self.font, self.audio_system, self.test_asset_path)
        
        # Game loop simulation
        frame_count = 0
        input_events = 0
        audio_events = 0
        
        while time.time() - start_time < duration_seconds:
            # Simulate input
            if frame_count % 30 == 0:  # Every 30 frames
                self.input_manager.queue_event("MOVE_LEFT")
                input_events += 1
            
            if frame_count % 60 == 0:  # Every 60 frames
                self.input_manager.queue_event("ROTATE_CW")
                input_events += 1
            
            # Process input
            events = self.input_manager.get_pending_events()
            
            # Update game state based on events
            for event in events:
                if event == "MOVE_LEFT":
                    self.state_manager.set("puzzle.piece_x", 
                                         self.state_manager.get("puzzle.piece_x", 0) - 1, 
                                         source="gameplay")
                elif event == "ROTATE_CW":
                    self.state_manager.set("puzzle.piece_rotation", 
                                         (self.state_manager.get("puzzle.piece_rotation", 0) + 1) % 4, 
                                         source="gameplay")
            
            # Update puzzle engine
            puzzle_engine.update()
            
            # Simulate audio events
            if frame_count % 120 == 0:  # Every 120 frames
                self.audio_system.trigger_audio_event("piece_landed")
                audio_events += 1
            
            # Advance time
            self.clock.advance(16)  # ~60 FPS
            frame_count += 1
        
        total_duration = time.time() - start_time
        
        return {
            "duration": total_duration,
            "frames_processed": frame_count,
            "input_events": input_events,
            "audio_events": audio_events,
            "fps": frame_count / total_duration
        }
    
    def simulate_screen_transitions(self) -> Dict[str, Any]:
        """Simulate screen transitions and state management."""
        start_time = time.time()
        
        # Define screen flow
        screen_flow = [
            "loading",
            "main_menu", 
            "settings",
            "main_menu",
            "play_game",
            "test_mode",
            "game_over"
        ]
        
        transitions = []
        
        for screen in screen_flow:
            # Update screen state
            self.state_manager.set("screen.current", screen, source="transition")
            
            # Verify transition
            current_screen = self.state_manager.get("screen.current")
            self.assertEqual(current_screen, screen)
            
            transitions.append({
                "from": transitions[-1]["to"] if transitions else "none",
                "to": screen,
                "timestamp": time.time()
            })
        
        duration = time.time() - start_time
        
        return {
            "duration": duration,
            "transitions": len(transitions),
            "screens_visited": len(set(screen_flow))
        }
    
    def simulate_audio_integration(self) -> Dict[str, Any]:
        """Test audio system integration with game events."""
        start_time = time.time()
        
        # Register audio events
        audio_events = [
            ("piece_landed", "click"),
            ("line_cleared", "clusterformed"),
            ("combo_formed", "double"),
            ("game_over", "game_over_sound")
        ]
        
        for event_name, sound_name in audio_events:
            self.audio_system.register_audio_event(event_name, sound_name)
        
        # Trigger events and verify audio responses
        events_triggered = 0
        
        for event_name, sound_name in audio_events:
            # Trigger event
            self.audio_system.trigger_audio_event(event_name)
            events_triggered += 1
            
            # Verify event was registered
            self.assertIn(event_name, self.audio_system.audio_events)
            self.assertEqual(self.audio_system.audio_events[event_name], sound_name)
        
        duration = time.time() - start_time
        
        return {
            "duration": duration,
            "events_registered": len(audio_events),
            "events_triggered": events_triggered
        }
    
    def simulate_input_integration(self) -> Dict[str, Any]:
        """Test input system integration with game state."""
        start_time = time.time()
        
        # Define input mappings
        input_mappings = {
            "K_LEFT": "MOVE_LEFT",
            "K_RIGHT": "MOVE_RIGHT", 
            "K_DOWN": "MOVE_DOWN",
            "K_UP": "ROTATE_CW",
            "K_SPACE": "DROP"
        }
        
        # Test input processing
        inputs_processed = 0
        
        for key, action in input_mappings.items():
            # Simulate key press
            self.input_manager.handle_key_press(key)
            
            # Verify key state
            self.assertTrue(self.input_manager.is_key_pressed(key))
            
            # Queue corresponding action
            self.input_manager.queue_event(action)
            
            # Process events
            events = self.input_manager.get_pending_events()
            self.assertIn(action, events)
            
            inputs_processed += 1
        
        duration = time.time() - start_time
        
        return {
            "duration": duration,
            "inputs_mapped": len(input_mappings),
            "inputs_processed": inputs_processed
        }
    
    def simulate_state_synchronization(self) -> Dict[str, Any]:
        """Test state synchronization between modules."""
        start_time = time.time()
        
        # Create state changes from different sources
        state_changes = [
            ("puzzle.score", 1000, "gameplay"),
            ("audio.master_volume", 0.7, "settings"),
            ("screen.current", "pause_menu", "ui"),
            ("puzzle.level", 5, "gameplay"),
            ("input.repeat_rate", 80, "settings")
        ]
        
        changes_applied = 0
        
        for field_path, value, source in state_changes:
            # Apply state change
            success = self.state_manager.set(field_path, value, source=source)
            self.assertTrue(success, f"Failed to set {field_path}")
            
            # Verify state change
            retrieved_value = self.state_manager.get(field_path)
            self.assertEqual(retrieved_value, value, f"State mismatch for {field_path}")
            
            changes_applied += 1
        
        # Test bulk updates
        bulk_updates = {
            "puzzle.score": 2000,
            "puzzle.level": 10,
            "audio.master_volume": 0.9
        }
        
        results = self.state_manager.update(bulk_updates, source="bulk_update")
        self.assertTrue(all(results.values()), "Bulk update failed")
        
        duration = time.time() - start_time
        
        return {
            "duration": duration,
            "individual_changes": changes_applied,
            "bulk_changes": len(bulk_updates)
        }
    
    def simulate_error_recovery(self) -> Dict[str, Any]:
        """Test error recovery and system resilience."""
        start_time = time.time()
        
        recovery_tests = 0
        successful_recoveries = 0
        
        # Test 1: Invalid state changes
        try:
            self.state_manager.set("invalid.field", "value", source="test")
            recovery_tests += 1
        except Exception:
            successful_recoveries += 1
        
        # Test 2: Invalid audio events
        try:
            self.audio_system.trigger_audio_event("nonexistent_event")
            recovery_tests += 1
        except Exception:
            successful_recoveries += 1
        
        # Test 3: Invalid input events
        try:
            self.input_manager.handle_key_press("INVALID_KEY")
            recovery_tests += 1
        except Exception:
            successful_recoveries += 1
        
        # Test 4: System state corruption recovery
        try:
            # Corrupt state
            self.state_manager._state = None
            
            # Attempt recovery
            self.state_manager.get("puzzle.score", default=0)
            recovery_tests += 1
        except Exception:
            successful_recoveries += 1
        
        duration = time.time() - start_time
        
        return {
            "duration": duration,
            "recovery_tests": recovery_tests,
            "successful_recoveries": successful_recoveries
        }
    
    def run_complete_game_flow(self) -> Dict[str, Any]:
        """Run a complete game flow simulation."""
        print("🎮 Running Complete Game Flow Simulation...")
        
        results = {}
        
        # Phase 1: Startup
        print("  📋 Phase 1: Game Startup")
        results["startup"] = self.simulate_game_startup()
        
        # Phase 2: Menu Navigation
        print("  📋 Phase 2: Menu Navigation")
        results["menu_navigation"] = self.simulate_menu_navigation()
        
        # Phase 3: Audio Integration
        print("  📋 Phase 3: Audio Integration")
        results["audio_integration"] = self.simulate_audio_integration()
        
        # Phase 4: Input Integration
        print("  📋 Phase 4: Input Integration")
        results["input_integration"] = self.simulate_input_integration()
        
        # Phase 5: State Synchronization
        print("  📋 Phase 5: State Synchronization")
        results["state_synchronization"] = self.simulate_state_synchronization()
        
        # Phase 6: Screen Transitions
        print("  📋 Phase 6: Screen Transitions")
        results["screen_transitions"] = self.simulate_screen_transitions()
        
        # Phase 7: Gameplay Session
        print("  📋 Phase 7: Gameplay Session")
        results["gameplay_session"] = self.simulate_gameplay_session(duration_seconds=5)
        
        # Phase 8: Error Recovery
        print("  📋 Phase 8: Error Recovery")
        results["error_recovery"] = self.simulate_error_recovery()
        
        # Calculate totals
        total_duration = sum(phase["duration"] for phase in results.values())
        results["summary"] = {
            "total_duration": total_duration,
            "phases_completed": len(results),
            "overall_success": True
        }
        
        return results


class EndToEndTestCases(unittest.TestCase):
    """End-to-end test cases for complete game functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.e2e_framework = EndToEndTestFramework()
    
    def tearDown(self):
        """Clean up test environment."""
        self.e2e_framework.tearDown()
    
    def test_complete_game_startup(self):
        """Test complete game startup process."""
        result = self.e2e_framework.simulate_game_startup()
        
        self.assertLess(result["duration"], 5.0, "Startup took too long")
        self.assertEqual(result["systems_initialized"], 4, "Not all systems initialized")
        self.assertEqual(result["state_set"], 4, "Initial state not set correctly")
    
    def test_menu_navigation_flow(self):
        """Test complete menu navigation flow."""
        result = self.e2e_framework.simulate_menu_navigation()
        
        self.assertLess(result["duration"], 2.0, "Menu navigation took too long")
        self.assertEqual(result["menu_transitions"], 3, "Menu transitions not completed")
        self.assertEqual(result["events_processed"], 3, "Menu events not processed")
    
    def test_audio_system_integration(self):
        """Test audio system integration with game events."""
        result = self.e2e_framework.simulate_audio_integration()
        
        self.assertLess(result["duration"], 1.0, "Audio integration took too long")
        self.assertEqual(result["events_registered"], 4, "Audio events not registered")
        self.assertEqual(result["events_triggered"], 4, "Audio events not triggered")
    
    def test_input_system_integration(self):
        """Test input system integration with game state."""
        result = self.e2e_framework.simulate_input_integration()
        
        self.assertLess(result["duration"], 1.0, "Input integration took too long")
        self.assertEqual(result["inputs_mapped"], 5, "Input mappings not complete")
        self.assertEqual(result["inputs_processed"], 5, "Input processing not complete")
    
    def test_state_synchronization(self):
        """Test state synchronization between modules."""
        result = self.e2e_framework.simulate_state_synchronization()
        
        self.assertLess(result["duration"], 1.0, "State synchronization took too long")
        self.assertEqual(result["individual_changes"], 5, "Individual changes not applied")
        self.assertEqual(result["bulk_changes"], 3, "Bulk changes not applied")
    
    def test_screen_transitions(self):
        """Test screen transitions and state management."""
        result = self.e2e_framework.simulate_screen_transitions()
        
        self.assertLess(result["duration"], 2.0, "Screen transitions took too long")
        self.assertEqual(result["transitions"], 7, "Screen transitions not complete")
        self.assertEqual(result["screens_visited"], 7, "Not all screens visited")
    
    def test_gameplay_session(self):
        """Test complete gameplay session."""
        result = self.e2e_framework.simulate_gameplay_session(duration_seconds=3)
        
        self.assertLess(result["duration"], 5.0, "Gameplay session took too long")
        self.assertGreater(result["frames_processed"], 150, "Not enough frames processed")
        self.assertGreater(result["fps"], 50, "Frame rate too low")
        self.assertGreater(result["input_events"], 0, "No input events processed")
        self.assertGreater(result["audio_events"], 0, "No audio events processed")
    
    def test_error_recovery(self):
        """Test error recovery and system resilience."""
        result = self.e2e_framework.simulate_error_recovery()
        
        self.assertLess(result["duration"], 2.0, "Error recovery took too long")
        self.assertGreater(result["recovery_tests"], 0, "No recovery tests performed")
        self.assertGreater(result["successful_recoveries"], 0, "No successful recoveries")
    
    def test_complete_game_flow(self):
        """Test complete game flow from startup to gameplay."""
        result = self.e2e_framework.run_complete_game_flow()
        
        # Verify all phases completed
        self.assertEqual(result["summary"]["phases_completed"], 8, "Not all phases completed")
        self.assertTrue(result["summary"]["overall_success"], "Game flow failed")
        self.assertLess(result["summary"]["total_duration"], 20.0, "Complete flow took too long")


class IntegrationStressTests(unittest.TestCase):
    """Stress tests for module integration."""
    
    def setUp(self):
        """Set up test environment."""
        self.e2e_framework = EndToEndTestFramework()
    
    def tearDown(self):
        """Clean up test environment."""
        self.e2e_framework.tearDown()
    
    def test_high_frequency_state_updates(self):
        """Test high-frequency state updates across modules."""
        start_time = time.time()
        
        # Perform many rapid state updates
        updates_performed = 0
        
        for i in range(1000):
            # Update multiple state fields
            updates = {
                f"puzzle.score": i,
                f"puzzle.level": i % 10,
                f"audio.volume": (i % 100) / 100.0,
                f"input.repeat_rate": 50 + (i % 50)
            }
            
            results = self.e2e_framework.state_manager.update(updates, source="stress_test")
            if all(results.values()):
                updates_performed += 1
        
        duration = time.time() - start_time
        
        # Should complete within reasonable time
        self.assertLess(duration, 5.0, f"High-frequency updates took {duration:.2f}s")
        self.assertGreater(updates_performed, 900, "Too many updates failed")
    
    def test_concurrent_module_operations(self):
        """Test concurrent operations across multiple modules."""
        import threading
        import time
        
        results = []
        
        def audio_worker():
            """Audio system worker thread."""
            for i in range(100):
                self.e2e_framework.audio_system.set_master_volume(i / 100.0)
                time.sleep(0.001)
            results.append("audio_complete")
        
        def input_worker():
            """Input system worker thread."""
            for i in range(100):
                self.e2e_framework.input_manager.queue_event(f"EVENT_{i}")
                time.sleep(0.001)
            results.append("input_complete")
        
        def state_worker():
            """State manager worker thread."""
            for i in range(100):
                self.e2e_framework.state_manager.set(f"stress.field_{i}", i, source="stress_test")
                time.sleep(0.001)
            results.append("state_complete")
        
        # Start concurrent workers
        threads = [
            threading.Thread(target=audio_worker),
            threading.Thread(target=input_worker),
            threading.Thread(target=state_worker)
        ]
        
        start_time = time.time()
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        duration = time.time() - start_time
        
        # Verify all workers completed
        self.assertEqual(len(results), 3, "Not all workers completed")
        self.assertLess(duration, 10.0, f"Concurrent operations took {duration:.2f}s")
    
    def test_memory_usage_stability(self):
        """Test memory usage stability during extended operations."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Perform extended operations
        for i in range(100):
            # Simulate gameplay session
            self.e2e_framework.simulate_gameplay_session(duration_seconds=0.1)
            
            # Simulate menu navigation
            self.e2e_framework.simulate_menu_navigation()
            
            # Simulate state updates
            self.e2e_framework.simulate_state_synchronization()
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable
        self.assertLess(memory_increase, 100.0, 
                       f"Memory usage increased by {memory_increase:.1f}MB")


def run_end_to_end_tests():
    """Run all end-to-end tests."""
    print("🔄 Running End-to-End Tests...")
    print("=" * 50)
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        EndToEndTestCases,
        IntegrationStressTests
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n📊 End-to-End Test Results:")
    print(f"✅ Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Failed: {len(result.failures)}")
    print(f"⚠️  Errors: {len(result.errors)}")
    print(f"📊 Total: {result.testsRun}")
    
    return result


if __name__ == "__main__":
    run_end_to_end_tests()
