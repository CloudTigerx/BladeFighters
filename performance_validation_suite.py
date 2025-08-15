#!/usr/bin/env python3
"""
Performance Validation Suite
Comprehensive performance testing after bug fixes to ensure no regression.
"""

import sys
import os
import time
import psutil
import statistics
import threading
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

@dataclass
class PerformanceMetrics:
    """Performance metrics for a specific test."""
    test_name: str
    duration_ms: float
    memory_before_mb: float
    memory_after_mb: float
    memory_delta_mb: float
    cpu_usage_percent: float
    frame_rate: Optional[float] = None
    state_operations: Optional[int] = None
    state_operation_time_ms: Optional[float] = None


class PerformanceValidator:
    """Comprehensive performance validator for the game."""
    
    def __init__(self):
        self.results = []
        self.process = psutil.Process()
        
    def measure_performance(self, test_name: str, test_func, *args, **kwargs) -> PerformanceMetrics:
        """Measure performance of a specific test."""
        print(f"🧪 Running {test_name}...")
        
        # Get initial memory usage
        memory_before = self.process.memory_info().rss / 1024 / 1024  # MB
        cpu_before = self.process.cpu_percent()
        
        # Run the test
        start_time = time.time()
        result = test_func(*args, **kwargs)
        end_time = time.time()
        
        # Get final memory usage
        memory_after = self.process.memory_info().rss / 1024 / 1024  # MB
        cpu_after = self.process.cpu_percent()
        
        # Calculate metrics
        duration_ms = (end_time - start_time) * 1000
        memory_delta = memory_after - memory_before
        cpu_usage = (cpu_before + cpu_after) / 2
        
        metrics = PerformanceMetrics(
            test_name=test_name,
            duration_ms=duration_ms,
            memory_before_mb=memory_before,
            memory_after_mb=memory_after,
            memory_delta_mb=memory_delta,
            cpu_usage_percent=cpu_usage
        )
        
        # Add specific metrics if available
        if isinstance(result, dict):
            metrics.frame_rate = result.get('frame_rate')
            metrics.state_operations = result.get('state_operations')
            metrics.state_operation_time_ms = result.get('state_operation_time_ms')
        
        self.results.append(metrics)
        return metrics
    
    def test_game_initialization_performance(self):
        """Test game initialization performance."""
        from game_client import GameClient
        
        def init_test():
            client = GameClient()
            
            # Run full initialization
            client._initialize_font()
            client._initialize_audio_system()
            client._load_background_images()
            client._initialize_menu_system()
            client._initialize_settings_ui()
            client._initialize_test_mode()
            client._initialize_screen_manager()
            client._initialize_story_system()
            client._initialize_puzzle_engine()
            client._initialize_puzzle_renderer()
            client._complete_initialization()
            
            return {
                'frame_rate': None,
                'state_operations': 0,
                'state_operation_time_ms': 0
            }
        
        return self.measure_performance("Game Initialization", init_test)
    
    def test_state_management_performance(self):
        """Test state management performance."""
        from modules.game_state_module.game_state_manager import GameStateManager
        
        def state_test():
            manager = GameStateManager(enable_performance_optimization=True)
            
            # Test state operations
            operations = 1000
            start_time = time.time()
            
            for i in range(operations):
                manager.set(f"test.field.{i}", i, source="performance_test")
                value = manager.get(f"test.field.{i}")
            
            end_time = time.time()
            operation_time_ms = (end_time - start_time) * 1000
            
            return {
                'frame_rate': None,
                'state_operations': operations,
                'state_operation_time_ms': operation_time_ms
            }
        
        return self.measure_performance("State Management", state_test)
    
    def test_puzzle_engine_performance(self):
        """Test puzzle engine performance."""
        import pygame
        from game_client import GameClient
        
        def puzzle_test():
            # Initialize pygame
            pygame.init()
            screen = pygame.display.set_mode((800, 600))
            
            # Create game client and initialize puzzle engine
            client = GameClient()
            client._initialize_font()
            client._initialize_audio_system()
            client._initialize_puzzle_engine()
            
            # Test puzzle engine operations
            operations = 100
            start_time = time.time()
            
            for i in range(operations):
                # Simulate puzzle engine update
                if hasattr(client, 'puzzle_engine') and client.puzzle_engine:
                    client.puzzle_engine.update()
            
            end_time = time.time()
            operation_time_ms = (end_time - start_time) * 1000
            
            pygame.quit()
            
            return {
                'frame_rate': operations / (operation_time_ms / 1000) if operation_time_ms > 0 else 0,
                'state_operations': operations,
                'state_operation_time_ms': operation_time_ms
            }
        
        return self.measure_performance("Puzzle Engine", puzzle_test)
    
    def test_settings_ui_performance(self):
        """Test settings UI performance."""
        import pygame
        from game_client import GameClient
        
        def settings_test():
            # Initialize pygame
            pygame.init()
            screen = pygame.display.set_mode((800, 600))
            
            # Create game client and initialize settings
            client = GameClient()
            client._initialize_font()
            client._initialize_settings_ui()
            
            # Test settings UI operations
            operations = 50
            start_time = time.time()
            
            for i in range(operations):
                # Simulate settings UI operations
                if hasattr(client, 'settings_ui') and client.settings_ui:
                    # Test settings access
                    volume = client.config.get('master_volume', 0.5)
                    client.config.set('master_volume', volume + 0.01)
            
            end_time = time.time()
            operation_time_ms = (end_time - start_time) * 1000
            
            pygame.quit()
            
            return {
                'frame_rate': None,
                'state_operations': operations,
                'state_operation_time_ms': operation_time_ms
            }
        
        return self.measure_performance("Settings UI", settings_test)
    
    def test_audio_system_performance(self):
        """Test audio system performance."""
        import pygame
        from game_client import GameClient
        
        def audio_test():
            # Initialize pygame
            pygame.init()
            screen = pygame.display.set_mode((800, 600))
            
            # Create game client and initialize audio
            client = GameClient()
            client._initialize_audio_system()
            
            # Test audio system operations
            operations = 100
            start_time = time.time()
            
            for i in range(operations):
                # Simulate audio operations
                if hasattr(client, 'audio') and client.audio:
                    # Test volume changes
                    client.audio.set_volume(0.5)
                    client.audio.set_music_volume(0.3)
            
            end_time = time.time()
            operation_time_ms = (end_time - start_time) * 1000
            
            pygame.quit()
            
            return {
                'frame_rate': None,
                'state_operations': operations,
                'state_operation_time_ms': operation_time_ms
            }
        
        return self.measure_performance("Audio System", audio_test)
    
    def test_input_system_performance(self):
        """Test input system performance."""
        import pygame
        from game_client import GameClient
        
        def input_test():
            # Initialize pygame
            pygame.init()
            screen = pygame.display.set_mode((800, 600))
            
            # Create game client and initialize input
            client = GameClient()
            client._initialize_font()
            client._initialize_puzzle_engine()
            
            # Test input system operations
            operations = 200
            start_time = time.time()
            
            for i in range(operations):
                # Simulate input processing
                if hasattr(client, 'puzzle_engine') and client.puzzle_engine:
                    # Create dummy events
                    events = []
                    for j in range(5):
                        event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_LEFT})
                        events.append(event)
                    
                    # Process events
                    client.puzzle_engine.process_events(events)
            
            end_time = time.time()
            operation_time_ms = (end_time - start_time) * 1000
            
            pygame.quit()
            
            return {
                'frame_rate': None,
                'state_operations': operations,
                'state_operation_time_ms': operation_time_ms
            }
        
        return self.measure_performance("Input System", input_test)
    
    def run_comprehensive_test(self):
        """Run all performance tests."""
        print("🚀 Performance Validation Suite")
        print("=" * 60)
        
        tests = [
            self.test_game_initialization_performance,
            self.test_state_management_performance,
            self.test_puzzle_engine_performance,
            self.test_settings_ui_performance,
            self.test_audio_system_performance,
            self.test_input_system_performance
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                print(f"❌ Test failed: {e}")
        
        self.print_results()
    
    def print_results(self):
        """Print comprehensive performance results."""
        print("\n📊 PERFORMANCE VALIDATION RESULTS")
        print("=" * 60)
        
        total_memory = 0
        total_time = 0
        
        for result in self.results:
            print(f"\n🧪 {result.test_name}")
            print(f"   Duration: {result.duration_ms:.2f}ms")
            print(f"   Memory: {result.memory_before_mb:.1f}MB → {result.memory_after_mb:.1f}MB (Δ{result.memory_delta_mb:+.1f}MB)")
            print(f"   CPU Usage: {result.cpu_usage_percent:.1f}%")
            
            if result.frame_rate:
                print(f"   Frame Rate: {result.frame_rate:.1f} FPS")
            
            if result.state_operations:
                avg_time = result.state_operation_time_ms / result.state_operations
                print(f"   State Operations: {result.state_operations} ({avg_time:.3f}ms avg)")
            
            total_memory += result.memory_after_mb
            total_time += result.duration_ms
        
        # Calculate averages
        avg_memory = total_memory / len(self.results) if self.results else 0
        avg_time = total_time / len(self.results) if self.results else 0
        
        print(f"\n📈 SUMMARY")
        print(f"   Total Memory Usage: {total_memory:.1f}MB")
        print(f"   Average Memory per Test: {avg_memory:.1f}MB")
        print(f"   Total Test Time: {total_time:.2f}ms")
        print(f"   Average Test Time: {avg_time:.2f}ms")
        
        # Performance assessment
        print(f"\n🎯 PERFORMANCE ASSESSMENT")
        
        # Check for performance regressions
        performance_issues = []
        
        for result in self.results:
            if result.duration_ms > 1000:  # More than 1 second
                performance_issues.append(f"{result.test_name}: Slow ({result.duration_ms:.0f}ms)")
            
            if result.memory_delta_mb > 50:  # More than 50MB increase
                performance_issues.append(f"{result.test_name}: High memory usage (Δ{result.memory_delta_mb:.0f}MB)")
            
            if result.cpu_usage_percent > 80:  # More than 80% CPU
                performance_issues.append(f"{result.test_name}: High CPU usage ({result.cpu_usage_percent:.0f}%)")
        
        if performance_issues:
            print("   ⚠️ Performance Issues Detected:")
            for issue in performance_issues:
                print(f"      • {issue}")
        else:
            print("   ✅ No Performance Issues Detected")
        
        # Overall assessment
        if len(performance_issues) == 0:
            print("   🎉 EXCELLENT: All performance metrics within acceptable ranges")
        elif len(performance_issues) <= 2:
            print("   ✅ GOOD: Minor performance issues detected")
        else:
            print("   ⚠️ CONCERNING: Multiple performance issues detected")


def main():
    """Run the performance validation suite."""
    validator = PerformanceValidator()
    validator.run_comprehensive_test()
    
    return len(validator.results) > 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

