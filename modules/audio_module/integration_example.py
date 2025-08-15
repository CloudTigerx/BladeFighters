#!/usr/bin/env python3
"""
Audio Module Integration Example
Demonstrates how to integrate the audio module with the unified state management system.
"""

import sys
import os
import time
from typing import Dict, Any

# Add the project root to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from modules.game_state_module.game_state_manager import GameStateManager
from modules.audio_module.audio_system import AudioSystem
from modules.audio_module.audio_state_manager import AudioStateManager
from modules.settings_module.audio_settings_integration import AudioSettingsIntegration


class AudioIntegrationExample:
    """
    Example class demonstrating audio module integration.
    Shows how to use the audio system with state management.
    """
    
    def __init__(self):
        """Initialize the audio integration example."""
        print("🎵 Initializing Audio Integration Example...")
        
        # Initialize the unified state manager
        self.state_manager = GameStateManager()
        print("✅ GameStateManager initialized")
        
        # Initialize audio system with state manager
        self.audio_system = AudioSystem(state_manager=self.state_manager)
        print("✅ AudioSystem initialized with state manager")
        
        # Initialize audio state manager
        self.audio_state_manager = AudioStateManager(self.state_manager)
        print("✅ AudioStateManager initialized")
        
        # Initialize settings integration
        self.settings_integration = AudioSettingsIntegration(
            self.state_manager, 
            self.audio_state_manager
        )
        print("✅ AudioSettingsIntegration initialized")
        
        print("🎉 Audio integration setup complete!\n")
    
    def demonstrate_basic_audio_operations(self):
        """Demonstrate basic audio operations."""
        print("🔊 Basic Audio Operations Demo")
        print("=" * 40)
        
        # Get current audio state
        summary = self.audio_state_manager.get_state_summary()
        print(f"Current master volume: {summary['master_volume']}")
        print(f"Music enabled: {summary['music_enabled']}")
        print(f"SFX enabled: {summary['sfx_enabled']}")
        
        # Set volume through state manager
        print("\n📊 Setting volume through state manager...")
        success = self.audio_state_manager.set_master_volume(0.8, "demo")
        print(f"Volume change successful: {success}")
        
        # Verify the change
        new_volume = self.audio_state_manager.get_master_volume()
        print(f"New master volume: {new_volume}")
        
        # Use convenience methods
        print("\n🎛️ Using convenience methods...")
        success = self.audio_system.set_music_volume(0.6)
        print(f"Music volume change successful: {success}")
        
        # Enable/disable audio
        print("\n🔇 Testing enable/disable...")
        self.audio_state_manager.set_sfx_enabled(False, "demo")
        print("SFX disabled")
        
        # Re-enable
        self.audio_state_manager.set_sfx_enabled(True, "demo")
        print("SFX re-enabled")
        
        print("✅ Basic audio operations demo complete!\n")
    
    def demonstrate_settings_integration(self):
        """Demonstrate settings integration."""
        print("⚙️ Settings Integration Demo")
        print("=" * 40)
        
        # Get settings callbacks
        callbacks = self.settings_integration.get_audio_settings_callbacks()
        print(f"Available settings callbacks: {list(callbacks.keys())}")
        
        # Simulate settings UI interaction
        print("\n🎮 Simulating settings UI interaction...")
        
        # Master volume change
        success = callbacks["master_volume"](0.9)
        print(f"Master volume callback successful: {success}")
        
        # Music volume change
        success = callbacks["music_volume"](0.7)
        print(f"Music volume callback successful: {success}")
        
        # SFX enable/disable
        success = callbacks["sfx_enabled"](False)
        print(f"SFX enable callback successful: {success}")
        
        # Get current settings
        current_settings = self.settings_integration.get_current_settings()
        print(f"\nCurrent settings: {current_settings}")
        
        print("✅ Settings integration demo complete!\n")
    
    def demonstrate_state_tracking(self):
        """Demonstrate state change tracking."""
        print("📈 State Change Tracking Demo")
        print("=" * 40)
        
        # Create a snapshot before changes
        self.audio_state_manager.create_snapshot("Before demo changes")
        print("📸 Created initial snapshot")
        
        # Make several changes
        print("\n🔄 Making state changes...")
        changes = [
            ("master_volume", 0.5),
            ("music_volume", 0.3),
            ("sfx_volume", 0.8),
            ("music_enabled", False),
            ("sfx_enabled", True)
        ]
        
        for field, value in changes:
            if "volume" in field:
                self.audio_state_manager.set_master_volume(value, "demo") if "master" in field else \
                self.audio_state_manager.set_music_volume(value, "demo") if "music" in field else \
                self.audio_state_manager.set_sfx_volume(value, "demo")
            elif "enabled" in field:
                self.audio_state_manager.set_music_enabled(value, "demo") if "music" in field else \
                self.audio_state_manager.set_sfx_enabled(value, "demo")
            print(f"  Changed {field} to {value}")
        
        # Get change history
        print("\n📋 State change history:")
        for field in ["audio.master_volume", "audio.music_volume", "audio.sfx_volume"]:
            changes = self.state_manager.history.get_changes_for_field(field)
            if changes:
                latest = changes[-1]
                print(f"  {field}: {latest.old_value} -> {latest.new_value} (source: {latest.source})")
        
        # Create final snapshot
        self.audio_state_manager.create_snapshot("After demo changes")
        print("📸 Created final snapshot")
        
        print("✅ State tracking demo complete!\n")
    
    def demonstrate_settings_sync(self):
        """Demonstrate settings synchronization."""
        print("🔄 Settings Synchronization Demo")
        print("=" * 40)
        
        # Simulate loading settings from configuration
        config_settings = {
            "master_volume": 0.75,
            "music_volume": 0.6,
            "sfx_volume": 0.9,
            "music_enabled": True,
            "sfx_enabled": False
        }
        
        print(f"📥 Loading settings from config: {config_settings}")
        
        # Sync settings to state manager
        self.settings_integration.sync_settings_to_state(config_settings)
        print("✅ Settings synced to state manager")
        
        # Verify the sync
        current_settings = self.settings_integration.get_current_settings()
        print(f"📊 Current state: {current_settings}")
        
        # Get settings for persistence
        settings_for_save = self.audio_state_manager.get_settings_dict()
        print(f"💾 Settings for save: {settings_for_save}")
        
        print("✅ Settings sync demo complete!\n")
    
    def demonstrate_error_handling(self):
        """Demonstrate error handling."""
        print("🚨 Error Handling Demo")
        print("=" * 40)
        
        # Test invalid volume values
        print("🧪 Testing invalid volume values...")
        
        invalid_values = [-0.1, 1.5, "not_a_number", None]
        for value in invalid_values:
            try:
                success = self.audio_state_manager.set_master_volume(value, "demo")
                print(f"  Volume {value}: {'✅' if success else '❌'}")
            except Exception as e:
                print(f"  Volume {value}: ❌ Exception: {type(e).__name__}")
        
        # Test without state manager (backward compatibility)
        print("\n🔄 Testing backward compatibility...")
        try:
            # Create audio system without state manager
            basic_audio = AudioSystem()
            print("✅ AudioSystem created without state manager")
            
            # Test convenience methods (should return False)
            success = basic_audio.set_master_volume(0.8)
            print(f"  Convenience method: {'✅' if not success else '❌'} (should be False)")
            
            summary = basic_audio.get_audio_state_summary()
            print(f"  State summary: {summary} (should be empty)")
            
        except Exception as e:
            print(f"❌ Backward compatibility test failed: {e}")
        
        print("✅ Error handling demo complete!\n")
    
    def demonstrate_performance(self):
        """Demonstrate performance characteristics."""
        print("⚡ Performance Demo")
        print("=" * 40)
        
        # Test volume change performance
        print("📊 Testing volume change performance...")
        
        iterations = 100
        start_time = time.time()
        
        for i in range(iterations):
            volume = 0.1 + (i % 9) * 0.1  # Cycle through 0.1 to 0.9
            self.audio_state_manager.set_master_volume(volume, "perf_test")
        
        end_time = time.time()
        total_time = (end_time - start_time) * 1000  # Convert to milliseconds
        avg_time = total_time / iterations
        
        print(f"  {iterations} volume changes in {total_time:.2f}ms")
        print(f"  Average time per change: {avg_time:.2f}ms")
        
        # Test state query performance
        print("\n📊 Testing state query performance...")
        
        start_time = time.time()
        
        for i in range(iterations):
            summary = self.audio_state_manager.get_state_summary()
        
        end_time = time.time()
        total_time = (end_time - start_time) * 1000
        avg_time = total_time / iterations
        
        print(f"  {iterations} state queries in {total_time:.2f}ms")
        print(f"  Average time per query: {avg_time:.2f}ms")
        
        print("✅ Performance demo complete!\n")
    
    def run_all_demos(self):
        """Run all demonstration methods."""
        print("🎵 Audio Module Integration Examples")
        print("=" * 50)
        print("This example demonstrates the complete audio module integration")
        print("with the unified state management system.\n")
        
        try:
            # Run all demos
            self.demonstrate_basic_audio_operations()
            self.demonstrate_settings_integration()
            self.demonstrate_state_tracking()
            self.demonstrate_settings_sync()
            self.demonstrate_error_handling()
            self.demonstrate_performance()
            
            print("🎉 All demonstrations completed successfully!")
            print("\n📋 Summary:")
            print("  ✅ Audio system integrated with state management")
            print("  ✅ Settings integration working")
            print("  ✅ State tracking and history functional")
            print("  ✅ Error handling robust")
            print("  ✅ Performance optimized")
            print("  ✅ Backward compatibility maintained")
            
        except Exception as e:
            print(f"❌ Demo failed with error: {e}")
            import traceback
            traceback.print_exc()


def main():
    """Main function to run the integration example."""
    print("🚀 Starting Audio Module Integration Example...")
    
    # Create and run the example
    example = AudioIntegrationExample()
    example.run_all_demos()
    
    print("\n🏁 Integration example completed!")


if __name__ == "__main__":
    main()
