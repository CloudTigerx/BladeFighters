"""
Animation Utilities
Self-contained animation helper functions extracted from puzzle_renderer.py
"""

import math
import time
from typing import Tuple, Union

def lerp(start: float, end: float, progress: float) -> float:
    """
    Linear interpolation between start and end values.
    
    Args:
        start: Starting value
        end: Ending value
        progress: Progress from 0.0 to 1.0
        
    Returns:
        Interpolated value
    """
    return start + (end - start) * progress

def ease_out_quad(progress: float) -> float:
    """
    Quadratic easing out - decelerating to zero velocity.
    
    Args:
        progress: Progress from 0.0 to 1.0
        
    Returns:
        Eased progress value
    """
    return -progress * (progress - 2)

def ease_in_out_cubic(progress: float) -> float:
    """
    Cubic easing in and out - acceleration until halfway, then deceleration.
    
    Args:
        progress: Progress from 0.0 to 1.0
        
    Returns:
        Eased progress value
    """
    if progress < 0.5:
        return 4 * progress * progress * progress
    else:
        p = 2 * progress - 2
        return 1 + p * p * p / 2

def calculate_animation_progress(start_time: float, duration: float, current_time: float = None) -> float:
    """
    Calculate animation progress based on timing.
    
    Args:
        start_time: When the animation started
        duration: How long the animation should last
        current_time: Current time (defaults to time.time())
        
    Returns:
        Progress from 0.0 to 1.0, clamped
    """
    if current_time is None:
        current_time = time.time()
        
    elapsed = current_time - start_time
    progress = elapsed / duration if duration > 0 else 1.0
    return max(0.0, min(1.0, progress))

def calculate_fall_position(start_y: float, target_y: float, progress: float, easing_func=ease_out_quad) -> float:
    """
    Calculate the visual position of a falling block.
    
    Args:
        start_y: Starting Y position
        target_y: Target Y position
        progress: Animation progress (0.0 to 1.0)
        easing_func: Easing function to apply
        
    Returns:
        Current visual Y position
    """
    eased_progress = easing_func(progress)
    return lerp(start_y, target_y, eased_progress)

def rgb_to_hsv(r: int, g: int, b: int) -> Tuple[float, float, float]:
    """Convert RGB color to HSV."""
    r, g, b = r/255.0, g/255.0, b/255.0
    mx = max(r, g, b)
    mn = min(r, g, b)
    diff = mx-mn
    
    if mx == mn:
        h = 0
    elif mx == r:
        h = (60 * ((g-b)/diff) + 360) % 360
    elif mx == g:
        h = (60 * ((b-r)/diff) + 120) % 360
    elif mx == b:
        h = (60 * ((r-g)/diff) + 240) % 360
    
    if mx == 0:
        s = 0
    else:
        s = diff/mx
        
    v = mx
    return h, s, v

def hsv_to_rgb(h: float, s: float, v: float) -> Tuple[int, int, int]:
    """Convert HSV color to RGB."""
    c = v * s
    x = c * (1 - abs(((h / 60) % 2) - 1))
    m = v - c
    
    if 0 <= h < 60:
        r, g, b = c, x, 0
    elif 60 <= h < 120:
        r, g, b = x, c, 0
    elif 120 <= h < 180:
        r, g, b = 0, c, x
    elif 180 <= h < 240:
        r, g, b = 0, x, c
    elif 240 <= h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
    
    r = int((r + m) * 255)
    g = int((g + m) * 255)
    b = int((b + m) * 255)
    
    return r, g, b

def create_rainbow_color(progress: float, saturation: float = 1.0, value: float = 1.0) -> Tuple[int, int, int]:
    """
    Create a rainbow color based on progress.
    
    Args:
        progress: Progress from 0.0 to 1.0
        saturation: Color saturation (0.0 to 1.0)
        value: Color value/brightness (0.0 to 1.0)
        
    Returns:
        RGB tuple
    """
    hue = (progress * 360) % 360
    return hsv_to_rgb(hue, saturation, value)

# Test functions to ensure utilities work correctly
def test_animation_utilities():
    """Test all utility functions for correctness."""
    print("🧪 Testing Animation Utilities...")
    
    # Test lerp
    assert abs(lerp(0, 10, 0.5) - 5) < 0.001, "lerp test failed"
    assert abs(lerp(0, 10, 0) - 0) < 0.001, "lerp start test failed"
    assert abs(lerp(0, 10, 1) - 10) < 0.001, "lerp end test failed"
    
    # Test easing
    assert abs(ease_out_quad(0) - 0) < 0.001, "ease_out_quad start test failed"
    assert abs(ease_out_quad(1) - 1) < 0.001, "ease_out_quad end test failed"
    
    # Test animation progress
    start_time = time.time()
    progress = calculate_animation_progress(start_time, 1.0, start_time + 0.5)
    assert abs(progress - 0.5) < 0.001, "animation progress test failed"
    
    # Test color conversion
    r, g, b = hsv_to_rgb(0, 1, 1)  # Pure red
    assert r == 255 and g == 0 and b == 0, "HSV to RGB test failed"
    
    print("✅ All Animation Utilities tests passed!")

if __name__ == "__main__":
    test_animation_utilities()
