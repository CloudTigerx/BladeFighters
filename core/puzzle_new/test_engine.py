#!/usr/bin/env python3
"""
Test for New Clean Puzzle Engine

This demonstrates how much easier testing is with the clean architecture.
"""

import sys
import os

# Add the new puzzle engine to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine import PuzzleEngine, Piece, PieceType, Position, Grid

def test_piece_movement():
    """Test piece movement - simple and clear"""
    print("🧪 Testing piece movement...")
    
    # Create engine
    engine = PuzzleEngine(6, 12)
    engine.start_game()
    
    # Test basic movement
    success = engine.move_piece(1, 0)  # Move right
    assert success, "Piece should be able to move right"
    
    success = engine.move_piece(-1, 0)  # Move left
    assert success, "Piece should be able to move left"
    
    # Test boundary collision
    # Move to far right
    for _ in range(10):
        engine.move_piece(1, 0)
    
    # Try to move right again - should fail
    success = engine.move_piece(1, 0)
    assert not success, "Piece should not be able to move beyond boundary"
    
    print("✅ Piece movement tests passed!")

def test_piece_rotation():
    """Test piece rotation - simple and clear"""
    print("🧪 Testing piece rotation...")
    
    # Create engine
    engine = PuzzleEngine(6, 12)
    engine.start_game()
    
    # Test rotation
    success = engine.rotate_piece()
    assert success, "Piece should be able to rotate"
    
    print("✅ Piece rotation tests passed!")

def test_line_clearing():
    """Test line clearing - simple and clear"""
    print("🧪 Testing line clearing...")
    
    # Create grid
    grid = Grid(6, 12)
    
    # Fill a line completely
    for x in range(6):
        grid.cells[11][x] = PieceType.I  # Fill bottom row
    
    # Clear lines
    lines_cleared = grid.clear_lines()
    assert lines_cleared == 1, "Should clear 1 line"
    
    print("✅ Line clearing tests passed!")

def test_game_state():
    """Test game state management - simple and clear"""
    print("🧪 Testing game state...")
    
    # Create engine
    engine = PuzzleEngine(6, 12)
    
    # Test initial state
    state = engine.get_state()
    assert not state.game_active, "Game should not be active initially"
    assert state.score == 0, "Score should be 0 initially"
    assert state.level == 1, "Level should be 1 initially"
    
    # Start game
    engine.start_game()
    state = engine.get_state()
    assert state.game_active, "Game should be active after start"
    assert state.current_piece is not None, "Should have current piece"
    assert state.next_piece is not None, "Should have next piece"
    
    print("✅ Game state tests passed!")

def test_grid_operations():
    """Test grid operations - simple and clear"""
    print("🧪 Testing grid operations...")
    
    # Create grid
    grid = Grid(6, 12)
    
    # Test valid positions
    assert grid.is_valid_position(Position(3, 5)), "Position (3,5) should be valid"
    assert not grid.is_valid_position(Position(6, 5)), "Position (6,5) should be invalid (out of bounds)"
    assert not grid.is_valid_position(Position(3, 12)), "Position (3,12) should be invalid (out of bounds)"
    
    # Test piece placement
    piece = Piece(PieceType.O, Position(2, 10))
    assert grid.can_place_piece(piece), "Should be able to place O piece"
    
    grid.place_piece(piece)
    assert not grid.is_valid_position(Position(2, 10)), "Position should be occupied after placement"
    assert not grid.is_valid_position(Position(3, 10)), "Adjacent position should be occupied after placement"
    
    print("✅ Grid operation tests passed!")

def run_all_tests():
    """Run all tests"""
    print("🧪 RUNNING ALL TESTS FOR NEW CLEAN PUZZLE ENGINE")
    print("=" * 60)
    
    tests = [
        test_piece_movement,
        test_piece_rotation,
        test_line_clearing,
        test_game_state,
        test_grid_operations
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            test()
            passed += 1
            print()
        except Exception as e:
            print(f"❌ Test failed: {e}")
            print()
    
    print("=" * 60)
    print(f"📊 RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        print("✅ The new clean architecture is working perfectly!")
    else:
        print("❌ Some tests failed - but this is expected for a proof of concept")
    
    return passed == total

if __name__ == "__main__":
    run_all_tests()
