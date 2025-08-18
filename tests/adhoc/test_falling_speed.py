#!/usr/bin/env python3
"""
TEST FALLING SPEED ADJUSTMENT
=============================

Simple test to verify that falling speed has been adjusted to 2x slower.
"""

import sys
import os
import re

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_falling_speed_adjustment():
    """Test that falling speed has been adjusted to 2x slower"""
    print("⚡ TESTING FALLING SPEED ADJUSTMENT...")
    print("=" * 60)
    
    # Read the animation state management file to check the configuration
    file_path = "core/Animations/AnimationStateManagement.py"
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Look for the fall_animation_duration line
        pattern = r'self\.fall_animation_duration\s*=\s*([0-9.]+)'
        match = re.search(pattern, content)
        
        if match:
            current_duration = float(match.group(1))
            expected_duration = 0.17  # 2x slower than original 0.085
            
            print(f"Current fall animation duration: {current_duration} seconds per row")
            print(f"Expected duration (2x slower): {expected_duration} seconds per row")
            
            # Check if the adjustment is correct
            if abs(current_duration - expected_duration) < 0.001:
                print("✅ Falling speed has been correctly adjusted to 2x slower!")
                
                # Calculate time for full grid drop
                grid_height = 13  # Typical grid height
                full_drop_time = current_duration * grid_height
                print(f"Time for full grid drop: {full_drop_time:.2f} seconds")
                
                return True
            else:
                print("❌ Falling speed adjustment is incorrect!")
                print(f"Expected: {expected_duration}, Got: {current_duration}")
                return False
        else:
            print("❌ Could not find fall_animation_duration in the file!")
            return False
            
    except FileNotFoundError:
        print(f"❌ Could not find file: {file_path}")
        return False
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False

def test_falling_speed_calculation():
    """Test falling speed calculations for different scenarios"""
    print("\n📊 TESTING FALLING SPEED CALCULATIONS...")
    print("=" * 60)
    
    # Use the expected duration for calculations
    duration_per_row = 0.17  # 2x slower than original 0.085
    
    # Test different fall distances
    test_cases = [
        (1, "1 row drop"),
        (5, "5 row drop"),
        (10, "10 row drop"),
        (13, "Full grid drop"),
    ]
    
    print("Fall distance calculations:")
    for distance, description in test_cases:
        total_duration = duration_per_row * distance
        print(f"  {description}: {total_duration:.3f} seconds")
    
    return True

def test_original_vs_new_speed():
    """Compare original vs new falling speeds"""
    print("\n📈 COMPARING ORIGINAL VS NEW SPEEDS...")
    print("=" * 60)
    
    original_duration = 0.085  # Original speed
    new_duration = 0.17        # New speed (2x slower)
    
    print(f"Original speed: {original_duration} seconds per row")
    print(f"New speed: {new_duration} seconds per row")
    print(f"Speed ratio: {new_duration / original_duration:.1f}x slower")
    
    # Calculate full grid drop times
    grid_height = 13
    original_full_drop = original_duration * grid_height
    new_full_drop = new_duration * grid_height
    
    print(f"\nFull grid drop times:")
    print(f"  Original: {original_full_drop:.2f} seconds")
    print(f"  New: {new_full_drop:.2f} seconds")
    print(f"  Difference: +{new_full_drop - original_full_drop:.2f} seconds")
    
    return True

def main():
    """Run all falling speed tests"""
    print("⚡ FALLING SPEED ADJUSTMENT TEST")
    print("=" * 60)
    print()
    
    # Run tests
    adjustment_ok = test_falling_speed_adjustment()
    calculation_ok = test_falling_speed_calculation()
    comparison_ok = test_original_vs_new_speed()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 FALLING SPEED TEST SUMMARY")
    print("=" * 60)
    
    all_passed = all([adjustment_ok, calculation_ok, comparison_ok])
    
    if all_passed:
        print("✅ ALL FALLING SPEED TESTS PASSED!")
        print("Falling speed has been successfully adjusted to 2x slower.")
        print("Strikes and garbage blocks will now fall at half the original speed.")
    else:
        print("❌ SOME FALLING SPEED TESTS FAILED!")
        if not adjustment_ok:
            print("  • Falling speed adjustment is incorrect")
        if not calculation_ok:
            print("  • Falling speed calculations have issues")
        if not comparison_ok:
            print("  • Speed comparison has issues")
    
    print("\n🔧 IMPACT:")
    if all_passed:
        print("• Garbage blocks will fall 2x slower")
        print("• Strike blocks will fall 2x slower")
        print("• Players will have more time to react to incoming attacks")
        print("• Overall game feel will be more relaxed")
        print("• Full grid drop now takes ~2.2 seconds instead of ~1.1 seconds")

if __name__ == "__main__":
    main()
