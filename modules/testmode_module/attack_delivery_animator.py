"""
Attack Delivery Animator
Handles falling animations for garbage blocks and strike patterns.
Extracted from TestMode to separate animation logic from planning and committing.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import time


@dataclass
class AnimationState:
    """State of an attack animation."""
    is_active: bool = False
    start_time: float = 0.0
    end_time: float = 0.0
    animation_keys: List[tuple] = None  # List of (col, row) positions being animated


class AttackDeliveryAnimator:
    """Handles falling animations for attack payloads."""
    
    def __init__(self, config):
        self.config = config
    
    def start_garbage_animation(self, engine, plan, current_time: float) -> AnimationState:
        """Start falling animation for garbage blocks."""
        if not hasattr(engine, 'renderer') or not hasattr(engine.renderer, 'animation_state_manager'):
            return AnimationState()
        
        asm = engine.renderer.animation_state_manager
        animation_keys = []
        
        # Calculate animation duration based on fall speed
        base_per_row = getattr(asm, 'fall_animation_duration', 0.085)
        per_row = base_per_row * max(0.25, float(self.config.fall_speed_scale))
        
        # Start animations for each planned block
        for block in plan.garbage_blocks:
            key = (block.column, block.row)
            animation_keys.append(key)
            
            if key not in asm.visual_falling_blocks:
                total_dur = max(0.06, per_row * (int(block.row) + 1))
                asm.visual_falling_blocks[key] = {
                    'start_time': current_time,
                    'duration': total_dur,
                    'start_y': -1,  # Start above the board
                    'block_type': 'garbage_block',
                    'payload': True,
                    'phase': 'spawning',
                }
        
        # Calculate conservative end time
        max_rows = max((block.row + 1) for block in plan.garbage_blocks) if plan.garbage_blocks else 0
        max_duration = max(0.06, per_row * max_rows) + 0.12
        
        return AnimationState(
            is_active=True,
            start_time=current_time,
            end_time=current_time + max_duration,
            animation_keys=animation_keys
        )
    
    def start_strike_animation(self, engine, plan, current_time: float) -> AnimationState:
        """Start falling animation for strike patterns."""
        if not hasattr(engine, 'renderer') or not hasattr(engine.renderer, 'animation_state_manager'):
            return AnimationState()
        
        asm = engine.renderer.animation_state_manager
        animation_keys = []
        
        # Calculate animation duration
        base_per_row = getattr(asm, 'fall_animation_duration', 0.085)
        per_row = base_per_row * max(0.25, float(self.config.fall_speed_scale))
        
        # Start animations for strike patterns (animate top and bottom cells per column)
        for pattern in plan.strike_patterns:
            top = pattern.top_row
            h = pattern.height
            
            # Animate top and bottom cells per column for visibility
            for col in pattern.columns:
                animation_keys.append((col, top))
                if h > 1:
                    animation_keys.append((col, top + h - 1))
                
                if (col, top) not in asm.visual_falling_blocks:
                    total_dur = max(0.06, per_row * (top + 1))
                    asm.visual_falling_blocks[(col, top)] = {
                        'start_time': current_time,
                        'duration': total_dur,
                        'start_y': -h,  # Start above the board
                        'block_type': 'orange_strike',
                        'payload': True,
                        'phase': 'spawning',
                    }
                
                if h > 1 and (col, top + h - 1) not in asm.visual_falling_blocks:
                    total_dur = max(0.06, per_row * (top + h))
                    asm.visual_falling_blocks[(col, top + h - 1)] = {
                        'start_time': current_time,
                        'duration': total_dur,
                        'start_y': -h,
                        'block_type': 'orange_strike',
                        'payload': True,
                        'phase': 'spawning',
                    }
        
        # Calculate conservative end time
        max_rows = max((pattern.top_row + pattern.height) for pattern in plan.strike_patterns) if plan.strike_patterns else 0
        max_duration = max(0.08, per_row * max_rows) + 0.12
        
        return AnimationState(
            is_active=True,
            start_time=current_time,
            end_time=current_time + max_duration,
            animation_keys=animation_keys
        )
    
    def is_animation_complete(self, engine, animation_state: AnimationState, current_time: float) -> bool:
        """Check if animation is complete."""
        if not animation_state.is_active:
            return True
        
        # Check timeout
        if current_time >= animation_state.end_time:
            return True
        
        # Check if any planned animations are still active
        if not hasattr(engine, 'renderer') or not hasattr(engine.renderer, 'animation_state_manager'):
            return True
        
        asm = engine.renderer.animation_state_manager
        active_count = 0
        for key in animation_state.animation_keys:
            if key in getattr(asm, 'visual_falling_blocks', {}):
                active_count += 1
        
        return active_count == 0
    
    def cleanup_animation(self, engine, animation_state: AnimationState):
        """Clean up animation state."""
        if not hasattr(engine, 'renderer') or not hasattr(engine.renderer, 'animation_state_manager'):
            return
        
        asm = engine.renderer.animation_state_manager
        for key in animation_state.animation_keys or []:
            asm.visual_falling_blocks.pop(key, None) 