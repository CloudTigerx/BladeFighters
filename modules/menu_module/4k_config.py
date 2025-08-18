"""
4K Resolution Configuration for BladeFighters
This version is optimized for 3840x2160 resolution with no scaling.
"""

# 4K Resolution Settings
RESOLUTION = (3840, 2160)

# Button Settings (native size - no scaling)
BUTTON_WIDTH = 600
BUTTON_HEIGHT = 180
BUTTON_SPACING = 40

# Menu Positioning (fixed for 4K)
MAIN_MENU_START_Y = 720  # 2160 // 3
STORY_MENU_START_Y = 720

# Font Sizes (fixed for 4K)
TITLE_FONT_SIZE = 72
BODY_FONT_SIZE = 36
SMALL_FONT_SIZE = 24

# Performance Benefits:
# - No pygame.transform.smoothscale() calls
# - Direct blitting of native-sized assets
# - Eliminated scaling overhead
# - Simplified codebase
# - Better performance and responsiveness
