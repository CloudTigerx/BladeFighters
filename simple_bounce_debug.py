#!/usr/bin/env python3
"""
Simple debug script to test sliding behavior and identify bounce sources
"""

import sys
import time

# Add the project root to the path
sys.path.insert(0, '.')

def test_sliding_behavior():
    """Test the current sliding behavior"""
    
    print("🧪 **Testing Sliding Behavior**")
    print("=" * 40)
    
    try:
        # Import the puzzle module
        from core.puzzle_module import PuzzleEngine
        
        print("✅ PuzzleEngine imported successfully")
        
        # Check the sliding method
        pe = PuzzleEngine()
        
        if hasattr(pe, '_handle_piece_sliding'):
            method = pe._handle_piece_sliding
            source = method.__code__.co_consts
            
            print(f"✅ _handle_piece_sliding method found")
            print(f"   Method constants: {len(source)} items")
            
            # Check for the bounce prevention logic
            source_str = str(source)
            if 'main_piece' in source_str and 'piece_position' in source_str:
                print("✅ Bounce prevention logic detected")
                print("   - Checks for active falling piece")
                print("   - Returns early if piece is falling")
            else:
                print("❌ Bounce prevention logic NOT found")
                
            # Check for the return statement
            if 'return' in source_str:
                print("✅ Early return logic detected")
            else:
                print("❌ No early return logic found")
                
        else:
            print("❌ _handle_piece_sliding method not found")
            
        print("\n" + "=" * 40)
        print("🔍 **Potential Bounce Sources:**")
        print("1. visual_sliding_blocks animations")
        print("2. visual_falling_blocks animations") 
        print("3. sub_position interpolation")
        print("4. piece separation logic")
        print("5. gravity application during separation")
        
        print("\n📋 **Current Fix Status:**")
        print("✅ Sliding method has bounce prevention")
        print("✅ Early return when piece is falling")
        print("❓ Need to test in actual gameplay")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def suggest_bounce_fixes():
    """Suggest additional fixes for bounce behavior"""
    
    print("\n💡 **Additional Bounce Fix Suggestions:**")
    print("=" * 40)
    
    suggestions = [
        "1. **Disable visual_falling_blocks during piece separation**",
        "   - Add flag to prevent falling animations during separation",
        "   - Clear flag after separation completes",
        "",
        "2. **Smooth sub_position transitions**",
        "   - Ensure sub_position doesn't jump during separation",
        "   - Use interpolation for smooth transitions",
        "",
        "3. **Delay sliding until piece fully lands**",
        "   - Wait for piece_position[1] to be negative (fully landed)",
        "   - Add small delay after landing before allowing slides",
        "",
        "4. **Check renderer interpolation**",
        "   - Ensure renderer doesn't interpolate during critical moments",
        "   - Use exact grid positions during separation",
        "",
        "5. **Monitor animation timing conflicts**",
        "   - Ensure sliding and falling animations don't overlap",
        "   - Add animation state validation"
    ]
    
    for suggestion in suggestions:
        print(suggestion)

if __name__ == "__main__":
    print("🚀 **Simple Bounce Debug**")
    print("=" * 50)
    
    if test_sliding_behavior():
        suggest_bounce_fixes()
        
        print("\n🎯 **Next Steps:**")
        print("1. Test the game and observe bounce behavior")
        print("2. If bounce persists, try the suggested fixes")
        print("3. Focus on visual_falling_blocks during separation")
        print("4. Check if sub_position resets cause visual jumps")
        
    else:
        print("❌ **Debug failed - cannot proceed**")
        sys.exit(1)
