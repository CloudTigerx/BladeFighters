#!/usr/bin/env python3
"""
Simple Input State Integration Test
==================================

A simple test to verify that the input system integrates properly with the state manager.
This test avoids the problematic imports and focuses on core functionality.
"""

import sys
import os
import time
from unittest.mock import Mock, MagicMock

# Add the project root to the path
sys.path.insert(0, os.path.dirname(__file__))

# Import the modules we need
from modules.game_state_module.game_state_manager import GameStateManager
from modules.game_state_module.state_schema import GameState
from modules.settings_module.unified_config import UnifiedConfigManager
from utils.clock import FakeClock


def test_basic_state_integration():
    """Test basic state manager functionality."""
    print("Testing basic state manager functionality...")
    
    # Create state manager
    state_manager = GameStateManager()
    
    # Test that input state exists
    assert state_manager.get("input") is not None
    assert isinstance(state_manager.get("input.keys_pressed"), set)
    assert isinstance(state_manager.get("input.keys_held"), set)
    assert isinstance(state_manager.get("input.mouse_position"), tuple)
    assert isinstance(state_manager.get("input.mouse_buttons"), set)
    
    # Test default values
    assert state_manager.get("input.input_locked") == False
    assert state_manager.get("input.input_lock_reason") is None
    assert state_manager.get("input.last_input_time") == 0.0
    
    print("✓ Basic state manager functionality works")


def test_input_state_updates():
    """Test that input state can be updated."""
    print("Testing input state updates...")
    
    # Create state manager
    state_manager = GameStateManager()
    
    # Update input state
    state_manager.set("input.keys_pressed", {65, 66, 67}, source="test")  # A, B, C keys
    state_manager.set("input.input_locked", True, source="test")
    state_manager.set("input.input_lock_reason", "test_lock", source="test")
    state_manager.set("input.last_input_time", 1234.5, source="test")
    
    # Verify updates
    assert state_manager.get("input.keys_pressed") == {65, 66, 67}
    assert state_manager.get("input.input_locked") == True
    assert state_manager.get("input.input_lock_reason") == "test_lock"
    assert state_manager.get("input.last_input_time") == 1234.5
    
    print("✓ Input state updates work")


def test_state_history():
    """Test that state changes are tracked in history."""
    print("Testing state history...")
    
    # Create state manager
    state_manager = GameStateManager()
    
    # Make several changes
    state_manager.set("input.input_locked", True, source="test")
    state_manager.set("input.input_locked", False, source="test")
    state_manager.set("input.keys_pressed", {65}, source="test")
    
    # Check that changes are recorded
    history = state_manager.history.get_changes_since(time.time() - 1)  # Last second
    input_changes = [change for change in history if change.field_path.startswith("input.")]
    assert len(input_changes) >= 3
    
    print("✓ State history tracking works")


def test_legacy_state_migration():
    """Test that legacy input state can be migrated."""
    print("Testing legacy state migration...")
    
    # Create state manager
    state_manager = GameStateManager()
    
    # Simulate legacy input state
    legacy_state = {
        "keys_pressed": {37, 39},  # Left, Right arrows
        "last_key_action_time": {37: 1000.0},
        "key_press_time": {37: 950.0},
        "_external_lock": True,
        "key_repeat_delay": 120,
        "key_repeat_interval": 80,
        "is_falling": True
    }
    
    # Migrate to state manager
    state_manager.set("input.keys_pressed", legacy_state["keys_pressed"])
    state_manager.set("input.input_locked", legacy_state["_external_lock"])
    state_manager.set("input.das_delay", legacy_state["key_repeat_delay"] / 1000.0)
    state_manager.set("input.arr_delay", legacy_state["key_repeat_interval"] / 1000.0)
    
    # Verify migration
    assert state_manager.get("input.keys_pressed") == {37, 39}
    assert state_manager.get("input.input_locked") == True
    assert state_manager.get("input.das_delay") == 0.12
    assert state_manager.get("input.arr_delay") == 0.08
    
    print("✓ Legacy state migration works")


def test_state_validation():
    """Test that state validation works."""
    print("Testing state validation...")
    
    # Create state manager
    state_manager = GameStateManager()
    
    # Test valid updates
    try:
        state_manager.set("input.keys_pressed", {65, 66, 67})
        state_manager.set("input.input_locked", True)
        state_manager.set("input.last_input_time", 1234.5)
        print("✓ Valid state updates work")
    except Exception as e:
        print(f"✗ Valid state updates failed: {e}")
        return False
    
    # Test invalid updates (should be handled gracefully)
    try:
        state_manager.set("input.invalid_field", "invalid_value")
        print("✓ Invalid field handling works")
    except Exception as e:
        print(f"✗ Invalid field handling failed: {e}")
        return False
    
    return True


def main():
    """Run all tests."""
    print("Input State Integration Tests")
    print("=" * 40)
    
    tests = [
        test_basic_state_integration,
        test_input_state_updates,
        test_state_history,
        test_legacy_state_migration,
        test_state_validation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ {test.__name__} failed: {e}")
    
    print("\n" + "=" * 40)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed!")
        return True
    else:
        print("❌ Some tests failed!")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 