#!/usr/bin/env python3
"""
Debug script to monitor crash conditions and bounce behavior
"""

import sys
import traceback
import time
from typing import Dict, Any

# Add the project root to the path
sys.path.insert(0, '.')

def monitor_game_state():
    """Monitor game state for potential crash conditions and bounce behavior"""
    
    try:
        # Import core modules
        from core.puzzle_module import PuzzleEngine
        from core.Animations.AnimationStateManagement import AnimationStateManager
        from modules.game_state_module.game_state_manager import GameStateManager
        
        print("🔍 **DEBUG: Monitoring Game State**")
        print("=" * 50)
        
        # Check GameStateManager methods
        print("\n📋 **GameStateManager Method Check:**")
        gsm = GameStateManager()
        available_methods = [method for method in dir(gsm) if not method.startswith('_')]
        print(f"Available methods: {len(available_methods)}")
        
        # Check for critical methods
        critical_methods = ['lock_player_input', 'lock_player_chain', 'is_player_input_locked']
        for method in critical_methods:
            has_method = hasattr(gsm, method)
            print(f"  {method}: {'✅' if has_method else '❌'}")
        
        # Check AnimationStateManager
        print("\n🎬 **AnimationStateManager Check:**")
        asm = AnimationStateManager()
        print(f"fall_animation_duration: {getattr(asm, 'fall_animation_duration', 'NOT FOUND')}")
        print(f"breaking_animation_duration: {getattr(asm, 'breaking_animation_duration', 'NOT FOUND')}")
        print(f"visual_sliding_blocks: {type(getattr(asm, 'visual_sliding_blocks', None))}")
        print(f"visual_falling_blocks: {type(getattr(asm, 'visual_falling_blocks', None))}")
        
        # Check PuzzleEngine sliding method
        print("\n🧩 **PuzzleEngine Sliding Method Check:**")
        try:
            # Create a minimal puzzle engine for inspection
            class MockRenderer:
                def __init__(self):
                    self.animation_state_manager = asm
            
            class MockAudio:
                def play_sound(self, sound):
                    pass
            
            pe = PuzzleEngine()
            pe.renderer = MockRenderer()
            pe.audio = MockAudio()
            
            # Check if sliding method exists and inspect its code
            if hasattr(pe, '_handle_piece_sliding'):
                method = pe._handle_piece_sliding
                source_lines = method.__code__.co_consts
                print(f"✅ _handle_piece_sliding method exists")
                print(f"   Method constants: {len(source_lines)} items")
                
                # Check for early return conditions
                if 'return' in str(source_lines):
                    print("   ⚠️  Contains early return (may be disabled)")
                else:
                    print("   ✅ No early return found")
            else:
                print("❌ _handle_piece_sliding method not found")
                
        except Exception as e:
            print(f"❌ Error inspecting PuzzleEngine: {e}")
        
        print("\n" + "=" * 50)
        print("🔍 **Ready to monitor for crashes and bounce behavior**")
        print("Start the game and reproduce the issues...")
        
        return True
        
    except Exception as e:
        print(f"❌ **CRITICAL ERROR during setup:** {e}")
        traceback.print_exc()
        return False

def create_bounce_monitor():
    """Create a script to monitor bounce behavior during gameplay"""
    
    bounce_monitor_code = '''
import sys
import time
from typing import Dict, Any

def monitor_bounce_behavior():
    """Monitor for bounce behavior during gameplay"""
    
    try:
        # This would be called from within the game loop
        # For now, we'll create a standalone monitor
        
        print("🎯 **BOUNCE MONITOR ACTIVE**")
        print("=" * 40)
        
        # Monitor animation states
        from core.Animations.AnimationStateManagement import AnimationStateManager
        
        asm = AnimationStateManager()
        
        while True:
            try:
                # Check for active animations that might cause bounce
                sliding_count = len(getattr(asm, 'visual_sliding_blocks', {}))
                falling_count = len(getattr(asm, 'visual_falling_blocks', {}))
                
                if sliding_count > 0 or falling_count > 0:
                    print(f"🎬 Active animations - Sliding: {sliding_count}, Falling: {falling_count}")
                    
                    # Log animation details
                    if sliding_count > 0:
                        print(f"   Sliding blocks: {list(asm.visual_sliding_blocks.keys())}")
                    if falling_count > 0:
                        print(f"   Falling blocks: {list(asm.visual_falling_blocks.keys())}")
                
                time.sleep(0.1)  # Check every 100ms
                
            except KeyboardInterrupt:
                print("\\n🛑 Bounce monitor stopped")
                break
            except Exception as e:
                print(f"❌ Monitor error: {e}")
                break
                
    except Exception as e:
        print(f"❌ **CRITICAL ERROR in bounce monitor:** {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    monitor_bounce_behavior()
'''
    
    with open('bounce_monitor.py', 'w') as f:
        f.write(bounce_monitor_code)
    
    print("✅ Created bounce_monitor.py")
    print("Run: python3 bounce_monitor.py in a separate terminal while playing")

if __name__ == "__main__":
    print("🚀 **BladeFighters Debug Suite**")
    print("=" * 50)
    
    # Run initial checks
    if monitor_game_state():
        print("\n✅ **Initial checks passed**")
        
        # Create bounce monitor
        create_bounce_monitor()
        
        print("\n📋 **Next Steps:**")
        print("1. Start the game: python3 main.py")
        print("2. In another terminal, run: python3 bounce_monitor.py")
        print("3. Reproduce the crash and bounce behavior")
        print("4. Check both terminals for error messages")
        
    else:
        print("\n❌ **Initial checks failed - cannot proceed**")
        sys.exit(1)
