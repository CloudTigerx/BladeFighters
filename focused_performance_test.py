#!/usr/bin/env python3
"""
Focused Performance Test
Targeted performance testing to identify specific bottlenecks.
"""

import sys
import os
import time
import psutil
from typing import Dict, List, Any

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_state_management_bottleneck():
    """Test state management performance with valid field paths."""
    print("🔍 Testing State Management Bottleneck...")
    
    from modules.game_state_module.game_state_manager import GameStateManager
    
    manager = GameStateManager(enable_performance_optimization=True)
    
    # Test with valid field paths
    operations = 1000
    start_time = time.time()
    
    for i in range(operations):
        # Use valid field paths that match the schema
        manager.set(f"puzzle.test_field_{i}", i, source="performance_test")
        value = manager.get(f"puzzle.test_field_{i}")
    
    end_time = time.time()
    operation_time_ms = (end_time - start_time) * 1000
    
    print(f"   ✅ State operations: {operations} in {operation_time_ms:.2f}ms")
    print(f"   📊 Average time per operation: {operation_time_ms/operations:.3f}ms")
    
    return operation_time_ms / operations


def test_game_initialization_breakdown():
    """Break down game initialization to identify slow components."""
    print("\n🔍 Testing Game Initialization Breakdown...")
    
    from game_client import GameClient
    import pygame
    
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    
    client = GameClient()
    
    # Test each initialization step separately
    steps = [
        ("Font", lambda: client._initialize_font()),
        ("Audio", lambda: client._initialize_audio_system()),
        ("Backgrounds", lambda: client._load_background_images()),
        ("Menu", lambda: client._initialize_menu_system()),
        ("Settings UI", lambda: client._initialize_settings_ui()),
        ("Puzzle Engine", lambda: client._initialize_puzzle_engine()),
    ]
    
    for step_name, step_func in steps:
        start_time = time.time()
        try:
            step_func()
            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000
            print(f"   ⏱️ {step_name}: {duration_ms:.2f}ms")
        except Exception as e:
            print(f"   ❌ {step_name}: Failed - {e}")
    
    pygame.quit()


def test_memory_usage_patterns():
    """Test memory usage patterns during different operations."""
    print("\n🔍 Testing Memory Usage Patterns...")
    
    import psutil
    process = psutil.Process()
    
    # Test memory usage during different operations
    operations = [
        ("Import GameClient", lambda: __import__('game_client')),
        ("Create GameClient", lambda: __import__('game_client').GameClient()),
        ("Import StateManager", lambda: __import__('modules.game_state_module.game_state_manager')),
        ("Create StateManager", lambda: __import__('modules.game_state_module.game_state_manager').GameStateManager()),
    ]
    
    for op_name, op_func in operations:
        memory_before = process.memory_info().rss / 1024 / 1024
        try:
            op_func()
            memory_after = process.memory_info().rss / 1024 / 1024
            delta = memory_after - memory_before
            print(f"   📊 {op_name}: {memory_before:.1f}MB → {memory_after:.1f}MB (Δ{delta:+.1f}MB)")
        except Exception as e:
            print(f"   ❌ {op_name}: Failed - {e}")


def test_cpu_usage_optimization():
    """Test CPU usage optimization opportunities."""
    print("\n🔍 Testing CPU Usage Optimization...")
    
    import psutil
    process = psutil.Process()
    
    # Test CPU usage during different operations
    def test_operation(name, operation, iterations=100):
        cpu_before = process.cpu_percent()
        start_time = time.time()
        
        for _ in range(iterations):
            operation()
        
        end_time = time.time()
        cpu_after = process.cpu_percent()
        
        duration_ms = (end_time - start_time) * 1000
        avg_cpu = (cpu_before + cpu_after) / 2
        
        print(f"   🔥 {name}: {duration_ms:.2f}ms, CPU: {avg_cpu:.1f}%")
        return duration_ms, avg_cpu
    
    # Test different operations
    from modules.game_state_module.game_state_manager import GameStateManager
    
    manager = GameStateManager(enable_performance_optimization=True)
    
    test_operation("State Set", lambda: manager.set("test.field", 1, source="test"))
    test_operation("State Get", lambda: manager.get("test.field"))
    test_operation("State History", lambda: manager.history.get_changes_since(time.time() - 60))


def main():
    """Run focused performance tests."""
    print("🎯 Focused Performance Test Suite")
    print("=" * 50)
    
    # Test state management bottleneck
    avg_state_time = test_state_management_bottleneck()
    
    # Test game initialization breakdown
    test_game_initialization_breakdown()
    
    # Test memory usage patterns
    test_memory_usage_patterns()
    
    # Test CPU usage optimization
    test_cpu_usage_optimization()
    
    # Performance recommendations
    print("\n📋 PERFORMANCE RECOMMENDATIONS")
    print("=" * 50)
    
    if avg_state_time > 0.1:
        print("   ⚠️ State operations are slow (>0.1ms avg)")
        print("   💡 Consider: Optimize state validation, reduce field path complexity")
    else:
        print("   ✅ State operations are fast")
    
    print("   💡 General optimizations:")
    print("      • Lazy load components that aren't immediately needed")
    print("      • Cache frequently accessed state values")
    print("      • Reduce initialization overhead in non-critical paths")
    print("      • Consider async loading for heavy assets")
    print("      • Profile and optimize hot paths in puzzle engine")


if __name__ == "__main__":
    main()

