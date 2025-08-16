#!/usr/bin/env python3
"""
Game State Module Integration Examples
Comprehensive examples for all module integrations with the unified state management system.
"""

import sys
import os
import time
from typing import Dict, Any, Optional

# Add the project root to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from modules.game_state_module.game_state_manager import GameStateManager
from modules.game_state_module.state_schema import GameState, ScreenType, GameMode, PuzzleState


class GameStateIntegrationExamples:
    """
    Comprehensive integration examples for all modules.
    Demonstrates how each module can integrate with the unified state management system.
    """
    
    def __init__(self):
        """Initialize the integration examples."""
        print("🎮 Game State Module Integration Examples")
        print("=" * 60)
        
        # Initialize the unified state manager
        self.state_manager = GameStateManager(enable_performance_optimization=True)
        print("✅ GameStateManager initialized with performance optimizations")
        
        print("🎉 Integration examples ready!\n")
    
    def demonstrate_audio_module_integration(self):
        """Demonstrate audio module integration patterns."""
        print("🔊 Audio Module Integration Example")
        print("-" * 40)
        
        # Audio state management patterns
        print("📊 Setting audio state through state manager...")
        
        # Set audio volumes
        self.state_manager.set("audio.master_volume", 0.8, source="audio_integration", description="Master volume set")
        self.state_manager.set("audio.music_volume", 0.6, source="audio_integration", description="Music volume set")
        self.state_manager.set("audio.sfx_volume", 0.9, source="audio_integration", description="SFX volume set")
        
        # Set audio enable/disable states
        self.state_manager.set("audio.music_enabled", True, source="audio_integration", description="Music enabled")
        self.state_manager.set("audio.sfx_enabled", True, source="audio_integration", description="SFX enabled")
        
        # Set current music track
        self.state_manager.set("audio.current_music", "main_theme.mp3", source="audio_integration", description="Current music track")
        self.state_manager.set("audio.music_playing", True, source="audio_integration", description="Music playing")
        
        # Verify audio state
        audio_state = self.state_manager.get_state_summary()["audio"]
        print(f"✅ Audio state set: {audio_state}")
        
        # Demonstrate state change tracking
        changes = self.state_manager.history.get_changes_for_field("audio.master_volume")
        print(f"📋 State changes tracked: {len(changes)} changes for master volume")
        
        print("✅ Audio module integration example complete!\n")
    
    def demonstrate_screen_module_integration(self):
        """Demonstrate screen module integration patterns."""
        print("🖥️ Screen Module Integration Example")
        print("-" * 40)
        
        # Screen state management patterns
        print("📊 Managing screen transitions through state manager...")
        
        # Set current screen
        self.state_manager.set("screen.current_screen", ScreenType.MAIN_MENU, source="screen_integration", description="Screen set to main menu")
        self.state_manager.set("screen.previous_screen", ScreenType.LOADING, source="screen_integration", description="Previous screen was loading")
        
        # Set screen transition timing
        self.state_manager.set("screen.screen_transition_time", time.time(), source="screen_integration", description="Screen transition timestamp")
        self.state_manager.set("screen.screen_cleanup_required", False, source="screen_integration", description="No cleanup required")
        
        # Set story-specific screen state
        self.state_manager.set("screen.story_scroll_position", 0, source="screen_integration", description="Story scroll position reset")
        self.state_manager.set("screen.current_story", {
            "title": "The Forge Keeper's Legacy",
            "content": ["Chapter 1: The Beginning", "Chapter 2: The Journey"]
        }, source="screen_integration", description="Current story set")
        
        # Verify screen state
        screen_state = self.state_manager.get_state_summary()["screen"]
        print(f"✅ Screen state set: {screen_state}")
        
        # Demonstrate screen transition
        print("🔄 Simulating screen transition...")
        self.state_manager.set("screen.previous_screen", ScreenType.MAIN_MENU, source="screen_integration", description="Previous screen updated")
        self.state_manager.set("screen.current_screen", ScreenType.GAME, source="screen_integration", description="Screen transitioned to game")
        
        print("✅ Screen module integration example complete!\n")
    
    def demonstrate_input_module_integration(self):
        """Demonstrate input module integration patterns."""
        print("⌨️ Input Module Integration Example")
        print("-" * 40)
        
        # Input state management patterns
        print("📊 Managing input state through state manager...")
        
        # Set input state
        self.state_manager.set("input.keys_pressed", {"SPACE", "LEFT", "RIGHT"}, source="input_integration", description="Keys currently pressed")
        self.state_manager.set("input.keys_held", {"DOWN"}, source="input_integration", description="Keys held down")
        self.state_manager.set("input.input_locked", False, source="input_integration", description="Input not locked")
        
        # Set input timing
        self.state_manager.set("input.last_input_time", time.time(), source="input_integration", description="Last input timestamp")
        self.state_manager.set("input.input_delay", 0.016, source="input_integration", description="Input delay set")
        
        # Set input configuration
        self.state_manager.set("input.das_time", 0.133, source="input_integration", description="DAS time configured")
        self.state_manager.set("input.arr_time", 0.016, source="input_integration", description="ARR time configured")
        
        # Verify input state
        input_state = self.state_manager.get_state_summary()["input"]
        print(f"✅ Input state set: {input_state}")
        
        # Demonstrate input processing
        print("🔄 Simulating input processing...")
        self.state_manager.set("input.keys_pressed", {"SPACE"}, source="input_integration", description="Space key pressed")
        self.state_manager.set("input.last_input_time", time.time(), source="input_integration", description="Input timestamp updated")
        
        print("✅ Input module integration example complete!\n")
    
    def demonstrate_puzzle_module_integration(self):
        """Demonstrate puzzle module integration patterns."""
        print("🧩 Puzzle Module Integration Example")
        print("-" * 40)
        
        # Puzzle state management patterns
        print("📊 Managing puzzle game state through state manager...")
        
        # Set puzzle game state
        self.state_manager.set("puzzle.game_active", True, source="puzzle_integration", description="Puzzle game active")
        self.state_manager.set("puzzle.game_mode", GameMode.QUICKPLAY, source="puzzle_integration", description="Quickplay mode")
        self.state_manager.set("puzzle.puzzle_state", PuzzleState.ACTIVE, source="puzzle_integration", description="Puzzle in active state")
        
        # Set grid state
        self.state_manager.set("puzzle.grid_width", 6, source="puzzle_integration", description="Grid width set")
        self.state_manager.set("puzzle.grid_height", 15, source="puzzle_integration", description="Grid height set")
        self.state_manager.set("puzzle.total_grid_height", 16, source="puzzle_integration", description="Total grid height")
        self.state_manager.set("puzzle.block_size", 40, source="puzzle_integration", description="Block size set")
        
        # Set piece state
        self.state_manager.set("puzzle.current_piece", {"type": "I", "rotation": 0, "position": [3, 0]}, source="puzzle_integration", description="Current piece set")
        self.state_manager.set("puzzle.next_piece", {"type": "O", "rotation": 0}, source="puzzle_integration", description="Next piece set")
        
        # Set game mechanics state
        self.state_manager.set("puzzle.clusters", {(1, 1), (2, 2), (3, 3)}, source="puzzle_integration", description="Clusters detected")
        self.state_manager.set("puzzle.chain_reaction_in_progress", False, source="puzzle_integration", description="No chain reaction")
        self.state_manager.set("puzzle.chain_count", 0, source="puzzle_integration", description="Chain count reset")
        self.state_manager.set("puzzle.combo_multiplier", 1, source="puzzle_integration", description="Combo multiplier reset")
        
        # Set timing state
        self.state_manager.set("puzzle.last_fall_time", time.time(), source="puzzle_integration", description="Last fall time")
        self.state_manager.set("puzzle.current_fall_speed", 640000, source="puzzle_integration", description="Current fall speed")
        self.state_manager.set("puzzle.normal_fall_speed", 640000, source="puzzle_integration", description="Normal fall speed")
        self.state_manager.set("puzzle.accelerated_fall_speed", 2400, source="puzzle_integration", description="Accelerated fall speed")
        
        # Set statistics
        self.state_manager.set("puzzle.score", 1500, source="puzzle_integration", description="Score updated")
        self.state_manager.set("puzzle.lines_cleared", 5, source="puzzle_integration", description="Lines cleared")
        
        # Verify puzzle state
        puzzle_state = self.state_manager.get_state_summary()["puzzle"]
        print(f"✅ Puzzle state set: {puzzle_state}")
        
        # Demonstrate puzzle state changes
        print("🔄 Simulating puzzle state changes...")
        self.state_manager.set("puzzle.score", 2000, source="puzzle_integration", description="Score increased")
        self.state_manager.set("puzzle.lines_cleared", 7, source="puzzle_integration", description="More lines cleared")
        self.state_manager.set("puzzle.chain_count", 2, source="puzzle_integration", description="Chain reaction started")
        
        print("✅ Puzzle module integration example complete!\n")
    
    def demonstrate_settings_module_integration(self):
        """Demonstrate settings module integration patterns."""
        print("⚙️ Settings Module Integration Example")
        print("-" * 40)
        
        # Settings state management patterns
        print("📊 Managing settings through state manager...")
        
        # Set game settings
        self.state_manager.set("settings.master_volume", 0.8, source="settings_integration", description="Master volume setting")
        self.state_manager.set("settings.music_volume", 0.6, source="settings_integration", description="Music volume setting")
        self.state_manager.set("settings.sfx_volume", 0.9, source="settings_integration", description="SFX volume setting")
        
        # Set display settings
        self.state_manager.set("settings.fullscreen", False, source="settings_integration", description="Fullscreen setting")
        self.state_manager.set("settings.resolution", "1920x1080", source="settings_integration", description="Resolution setting")
        self.state_manager.set("settings.vsync", True, source="settings_integration", description="VSync setting")
        
        # Set control settings
        self.state_manager.set("settings.das_time", 0.133, source="settings_integration", description="DAS time setting")
        self.state_manager.set("settings.arr_time", 0.016, source="settings_integration", description="ARR time setting")
        self.state_manager.set("settings.input_delay", 0.016, source="settings_integration", description="Input delay setting")
        
        # Set performance settings
        self.state_manager.set("settings.target_fps", 60, source="settings_integration", description="Target FPS setting")
        self.state_manager.set("settings.performance_overlay", True, source="settings_integration", description="Performance overlay setting")
        self.state_manager.set("settings.debug_mode", False, source="settings_integration", description="Debug mode setting")
        
        # Verify settings state
        settings_state = self.state_manager.get_state_summary()["settings"]
        print(f"✅ Settings state set: {settings_state}")
        
        # Demonstrate settings persistence
        print("💾 Simulating settings persistence...")
        settings_for_save = {
            "master_volume": self.state_manager.get("settings.master_volume"),
            "music_volume": self.state_manager.get("settings.music_volume"),
            "sfx_volume": self.state_manager.get("settings.sfx_volume"),
            "fullscreen": self.state_manager.get("settings.fullscreen"),
            "resolution": self.state_manager.get("settings.resolution"),
            "target_fps": self.state_manager.get("settings.target_fps")
        }
        print(f"📄 Settings for save: {settings_for_save}")
        
        print("✅ Settings module integration example complete!\n")
    
    def demonstrate_performance_monitoring(self):
        """Demonstrate performance monitoring integration."""
        print("⚡ Performance Monitoring Integration Example")
        print("-" * 40)
        
        # Performance monitoring patterns
        print("📊 Monitoring performance through state manager...")
        
        # Record performance metrics
        self.state_manager.set("performance.current_fps", 60.0, source="performance_monitor", description="Current FPS")
        self.state_manager.set("performance.target_fps", 60, source="performance_monitor", description="Target FPS")
        self.state_manager.set("performance.frame_time", 0.016, source="performance_monitor", description="Frame time")
        self.state_manager.set("performance.frame_count", 1000, source="performance_monitor", description="Frame count")
        
        # Record memory usage
        self.state_manager.set("performance.memory_usage", 128.5, source="performance_monitor", description="Memory usage in MB")
        self.state_manager.set("performance.memory_peak", 150.2, source="performance_monitor", description="Peak memory usage")
        self.state_manager.set("performance.memory_delta", 2.1, source="performance_monitor", description="Memory delta")
        
        # Record CPU usage
        self.state_manager.set("performance.cpu_usage", 25.5, source="performance_monitor", description="CPU usage percentage")
        self.state_manager.set("performance.cpu_peak", 45.2, source="performance_monitor", description="Peak CPU usage")
        
        # Record state management performance
        self.state_manager.set("performance.state_operations_per_second", 1000, source="performance_monitor", description="State operations per second")
        self.state_manager.set("performance.state_cache_hit_rate", 0.95, source="performance_monitor", description="State cache hit rate")
        self.state_manager.set("performance.state_validation_time", 0.001, source="performance_monitor", description="State validation time")
        
        # Verify performance state
        performance_state = self.state_manager.get_state_summary()["performance"]
        print(f"✅ Performance state set: {performance_state}")
        
        # Demonstrate performance optimization
        print("🔧 Simulating performance optimization...")
        optimizations = self.state_manager.optimize_state_management()
        print(f"📈 Applied optimizations: {optimizations}")
        
        print("✅ Performance monitoring integration example complete!\n")
    
    def demonstrate_state_history_and_rollback(self):
        """Demonstrate state history and rollback functionality."""
        print("📜 State History and Rollback Example")
        print("-" * 40)
        
        # State history patterns
        print("📊 Demonstrating state history and rollback...")
        
        # Create initial snapshot
        self.state_manager.create_snapshot("Initial state", ["puzzle", "audio"])
        print("📸 Created initial snapshot")
        
        # Make several state changes
        print("🔄 Making state changes...")
        changes = [
            ("puzzle.score", 2000),
            ("puzzle.lines_cleared", 10),
            ("audio.master_volume", 0.9),
            ("screen.current_screen", ScreenType.GAME),
            ("input.keys_pressed", {"SPACE", "LEFT"})
        ]
        
        for field, value in changes:
            self.state_manager.set(field, value, source="history_demo", description=f"History demo change: {field}")
            print(f"  Changed {field} to {value}")
        
        # Create another snapshot
        self.state_manager.create_snapshot("After changes", ["puzzle", "audio", "screen", "input"])
        print("📸 Created snapshot after changes")
        
        # Show state history
        print("\n📋 State change history:")
        for field in ["puzzle.score", "audio.master_volume", "screen.current_screen"]:
            changes = self.state_manager.history.get_changes_for_field(field)
            if changes:
                latest = changes[-1]
                print(f"  {field}: {latest.old_value} -> {latest.new_value} (source: {latest.source})")
        
        # Demonstrate rollback
        print("\n⏪ Demonstrating rollback...")
        snapshots = self.state_manager.history.get_snapshots()
        if len(snapshots) >= 2:
            initial_snapshot = snapshots[0]
            self.state_manager.rollback_to_snapshot(initial_snapshot.id)
            print(f"🔄 Rolled back to snapshot: {initial_snapshot.description}")
            
            # Verify rollback
            current_score = self.state_manager.get("puzzle.score")
            current_volume = self.state_manager.get("audio.master_volume")
            print(f"✅ Rollback verified - Score: {current_score}, Volume: {current_volume}")
        
        print("✅ State history and rollback example complete!\n")
    
    def demonstrate_validation_and_error_handling(self):
        """Demonstrate validation and error handling."""
        print("✅ Validation and Error Handling Example")
        print("-" * 40)
        
        # Validation patterns
        print("📊 Demonstrating validation and error handling...")
        
        # Test valid state changes
        print("✅ Testing valid state changes...")
        valid_changes = [
            ("puzzle.score", 1000),
            ("audio.master_volume", 0.5),
            ("screen.current_screen", ScreenType.MAIN_MENU),
            ("input.keys_pressed", {"SPACE"})
        ]
        
        for field, value in valid_changes:
            try:
                success = self.state_manager.set(field, value, source="validation_demo", description=f"Valid change: {field}")
                print(f"  ✅ {field} = {value}: {'Success' if success else 'Failed'}")
            except Exception as e:
                print(f"  ❌ {field} = {value}: Error - {e}")
        
        # Test invalid state changes
        print("\n❌ Testing invalid state changes...")
        invalid_changes = [
            ("puzzle.score", -100),  # Negative score
            ("audio.master_volume", 1.5),  # Volume > 1.0
            ("screen.current_screen", "invalid_screen"),  # Invalid screen type
            ("input.keys_pressed", 123)  # Wrong type
        ]
        
        for field, value in invalid_changes:
            try:
                success = self.state_manager.set(field, value, source="validation_demo", description=f"Invalid change: {field}")
                print(f"  {'❌' if success else '✅'} {field} = {value}: {'Accepted (should be rejected)' if success else 'Rejected (correct)'}")
            except Exception as e:
                print(f"  ✅ {field} = {value}: Rejected with error - {type(e).__name__}")
        
        print("✅ Validation and error handling example complete!\n")
    
    def demonstrate_callback_system(self):
        """Demonstrate callback system for state changes."""
        print("🔄 Callback System Example")
        print("-" * 40)
        
        # Callback patterns
        print("📊 Demonstrating callback system...")
        
        # Define callback functions
        def audio_volume_changed(field_path: str, old_value: Any, new_value: Any):
            print(f"  🔊 Audio volume changed: {field_path} = {old_value} -> {new_value}")
        
        def puzzle_score_changed(field_path: str, old_value: Any, new_value: Any):
            print(f"  🎯 Puzzle score changed: {field_path} = {old_value} -> {new_value}")
        
        def screen_changed(field_path: str, old_value: Any, new_value: Any):
            print(f"  🖥️ Screen changed: {field_path} = {old_value} -> {new_value}")
        
        # Register callbacks
        print("📝 Registering callbacks...")
        self.state_manager.add_change_callback("audio.master_volume", audio_volume_changed)
        self.state_manager.add_change_callback("puzzle.score", puzzle_score_changed)
        self.state_manager.add_change_callback("screen.current_screen", screen_changed)
        
        # Trigger state changes to demonstrate callbacks
        print("🔄 Triggering state changes...")
        self.state_manager.set("audio.master_volume", 0.7, source="callback_demo", description="Volume change for callback")
        self.state_manager.set("puzzle.score", 2500, source="callback_demo", description="Score change for callback")
        self.state_manager.set("screen.current_screen", ScreenType.SETTINGS, source="callback_demo", description="Screen change for callback")
        
        print("✅ Callback system example complete!\n")
    
    def run_all_examples(self):
        """Run all integration examples."""
        print("🚀 Running all Game State Module integration examples...\n")
        
        try:
            # Run all examples
            self.demonstrate_audio_module_integration()
            self.demonstrate_screen_module_integration()
            self.demonstrate_input_module_integration()
            self.demonstrate_puzzle_module_integration()
            self.demonstrate_settings_module_integration()
            self.demonstrate_performance_monitoring()
            self.demonstrate_state_history_and_rollback()
            self.demonstrate_validation_and_error_handling()
            self.demonstrate_callback_system()
            
            print("🎉 All integration examples completed successfully!")
            print("\n📋 Summary:")
            print("  ✅ Audio module integration patterns demonstrated")
            print("  ✅ Screen module integration patterns demonstrated")
            print("  ✅ Input module integration patterns demonstrated")
            print("  ✅ Puzzle module integration patterns demonstrated")
            print("  ✅ Settings module integration patterns demonstrated")
            print("  ✅ Performance monitoring integration demonstrated")
            print("  ✅ State history and rollback demonstrated")
            print("  ✅ Validation and error handling demonstrated")
            print("  ✅ Callback system demonstrated")
            
            # Show final state summary
            final_summary = self.state_manager.get_state_summary()
            print(f"\n📊 Final state summary: {len(final_summary)} state categories managed")
            
        except Exception as e:
            print(f"❌ Example failed with error: {e}")
            import traceback
            traceback.print_exc()


def main():
    """Main function to run the integration examples."""
    print("🎮 Game State Module Integration Examples")
    print("=" * 60)
    print("This demonstrates how all modules can integrate with the unified state management system.\n")
    
    # Create and run the examples
    examples = GameStateIntegrationExamples()
    examples.run_all_examples()
    
    print("\n🏁 Integration examples completed!")


if __name__ == "__main__":
    main()
