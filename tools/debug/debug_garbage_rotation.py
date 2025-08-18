#!/usr/bin/env python3
"""
DEBUG GARBAGE ROTATION
======================

Simple debug script to test garbage rotation logic step by step.
"""

def test_garbage_rotation_logic():
    """Test the garbage rotation logic directly"""
    print("🔄 TESTING GARBAGE ROTATION LOGIC...")
    print("=" * 60)
    
    # Expected rotation pattern: 0,5,1,4,2,3 (0-based)
    expected_pattern = [0, 5, 1, 4, 2, 3]
    print("Expected pattern:", expected_pattern)
    
    # Simulate the rotation logic
    column_rotation = [0, 5, 1, 4, 2, 3]  # 0-based columns
    current_rotation_index = 0
    
    print("\nSimulating 6 blocks placement:")
    actual_pattern = []
    
    for i in range(6):
        column = column_rotation[current_rotation_index]
        current_rotation_index = (current_rotation_index + 1) % len(column_rotation)
        actual_pattern.append(column)
        print(f"  Block {i+1}: Column {column}")
    
    print(f"\nActual pattern: {actual_pattern}")
    
    # Check if pattern matches
    pattern_correct = actual_pattern == expected_pattern
    
    if pattern_correct:
        print("✅ Rotation logic is correct!")
    else:
        print("❌ Rotation logic is incorrect!")
        print(f"Expected: {expected_pattern}")
        print(f"Actual: {actual_pattern}")
    
    return pattern_correct

def test_garbage_rotation_with_full_columns():
    """Test rotation when some columns are full"""
    print("\n📍 TESTING ROTATION WITH FULL COLUMNS...")
    print("=" * 60)
    
    # Expected rotation pattern: 0,5,1,4,2,3 (0-based)
    expected_pattern = [0, 5, 1, 4, 2, 3]
    
    # Simulate grid with some full columns
    grid = [None] * 6  # 6 columns
    grid[0] = 'full'  # Column 0 is full
    grid[1] = 'full'  # Column 1 is full
    
    print("Grid state (full columns: 0, 1):", grid)
    
    # Simulate the rotation logic with full column handling
    column_rotation = [0, 5, 1, 4, 2, 3]  # 0-based columns
    current_rotation_index = 0
    
    print("\nSimulating 6 blocks placement (skipping full columns):")
    actual_pattern = []
    blocks_placed = 0
    attempts = 0
    
    while blocks_placed < 6 and attempts < 20:  # Prevent infinite loop
        column = column_rotation[current_rotation_index]
        current_rotation_index = (current_rotation_index + 1) % len(column_rotation)
        attempts += 1
        
        # Check if column is full
        if grid[column] == 'full':
            print(f"  Attempt {attempts}: Column {column} is full, skipping")
            continue
        
        # Place block
        actual_pattern.append(column)
        blocks_placed += 1
        print(f"  Block {blocks_placed}: Column {column}")
    
    print(f"\nActual pattern: {actual_pattern}")
    
    # Expected: Should skip columns 0 and 1, so pattern should be [5, 4, 2, 3, 5, 4]
    expected_with_full = [5, 4, 2, 3, 5, 4]
    pattern_correct = actual_pattern == expected_with_full
    
    if pattern_correct:
        print("✅ Rotation with full columns is correct!")
    else:
        print("❌ Rotation with full columns is incorrect!")
        print(f"Expected: {expected_with_full}")
        print(f"Actual: {actual_pattern}")
    
    return pattern_correct

def main():
    """Run all rotation tests"""
    print("🔄 GARBAGE ROTATION DEBUG")
    print("=" * 60)
    print()
    
    # Run tests
    basic_ok = test_garbage_rotation_logic()
    full_columns_ok = test_garbage_rotation_with_full_columns()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 ROTATION DEBUG SUMMARY")
    print("=" * 60)
    
    all_passed = all([basic_ok, full_columns_ok])
    
    if all_passed:
        print("✅ ALL ROTATION TESTS PASSED!")
        print("The rotation logic is working correctly.")
    else:
        print("❌ SOME ROTATION TESTS FAILED!")
        if not basic_ok:
            print("  • Basic rotation logic has issues")
        if not full_columns_ok:
            print("  • Full column handling has issues")
    
    print("\n🔧 NEXT STEPS:")
    if all_passed:
        print("• The rotation logic is correct")
        print("• The issue might be in the TestMode implementation")
        print("• Check if rotation state is being reset between calls")
    else:
        print("• Fix the rotation logic")
        print("• Test the corrected implementation")

if __name__ == "__main__":
    main()
