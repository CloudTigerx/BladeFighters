"""garbage_pattern.py - Structured garbage pattern system for Blade Fighters

Implements multiple sword drop patterns for future inventory/equipment system.
Each sword type has its own unique drop pattern for sprinkles and strikes.

Based on classic Puzzle Pirates sword patterns that can be swapped per player.
"""
from typing import List, Tuple, Optional, Dict
from enum import Enum

class SwordType(Enum):
    """Different sword types with unique drop patterns."""
    # Core archetypes
    CUTLASS = "cutlass"
    SABER = "saber" 
    RAPIER = "rapier"
    DAGGER = "dagger"
    BROADSWORD = "broadsword"

    # Special weapons
    FISTS = "fists"

    # Weapon PNG-backed entries (assets/Weapons/*.png)
    RUSTY_SWORD = "rusty_sword"
    AZURE_RAPIER = "azure_rapier"
    CRIMSON_DIVIDER = "crimson_divider"
    DEEP_CURRENT = "deep_current"
    EMBER_BLADE = "ember_blade"
    FOREST_CLEAVER = "forest_cleaver"
    VERDANT_WALL = "verdant_wall"

class SwordPattern:
    """Represents a single sword's drop pattern."""
    
    def __init__(self, name: str, pattern: List[List[str]], description: str = ""):
        self.name = name
        self.pattern = pattern  # 6 wide, variable height (3-6 rows)
        self.description = description
        self.sprinkle_rows = 2  # Always use bottom 2 rows for sprinkles
    
    def get_sprinkle_color(self, x: int, y: int, layer: int = 1) -> str:
        """Get sprinkle color for this sword's pattern."""
        if not (0 <= x < 6):
            return "yellow"  # fallback
        
        # Sprinkles cycle through bottom 2 rows: layer 1->2->1->2...
        pattern_row = ((layer - 1) % self.sprinkle_rows)
        pattern_col = x % len(self.pattern[0])
        
        return self.pattern[pattern_row][pattern_col]
    
    def get_strike_color(self, x: int, y: int, strike_width: int, strike_height: int,
                        block_x_offset: int, block_y_offset: int, is_horizontal: bool = False,
                        from_right: bool = False) -> str:
        """Get strike color for this sword's pattern."""
        if not self.pattern or not self.pattern[0]:
            return "yellow"

        pattern_h = int(len(self.pattern))
        pattern_w = int(len(self.pattern[0]))

        def _fold_row_1based(requested_row_1based: int) -> int:
            """Apply PATTERN_MASTER fold rule for strikes.

            - Use rows 1..H once.
            - If requested exceeds H:
              - If H < 4: repeat from row 1.
              - Else: repeat only the top 4 rows (4th from top .. top).
            """
            try:
                rr = int(requested_row_1based)
            except Exception:
                rr = 1
            if rr <= 0:
                rr = 1
            if rr <= pattern_h:
                return rr
            if pattern_h < 4:
                return ((rr - 1) % pattern_h) + 1
            repeat_start = pattern_h - 3  # 4th row from top (1-based)
            k = rr - pattern_h  # 1.. infinite
            return int(repeat_start + ((k - 1) % 4))

        if is_horizontal:
            # PATTERN_MASTER: horizontal strikes use a rotated version of the drop pattern.
            # - Left-entry uses a 90° clockwise rotation.
            # - Right-entry uses a 90° counter-clockwise rotation.
            # The sword uses the TOP rows of the rotated pattern:
            #   top row of the strike matches pattern column 1 (left) / column 6 (right).
            # Along the sword's length, we walk the rotated pattern's columns (count == pattern_h).
            # If length exceeds pattern_h, repeat per side:
            #   - from_right (CCW): repeat columns 4..1
            #   - from_left  (CW): repeat the last 4 columns (3..6 when pattern_h==6)

            try:
                off = int(block_x_offset)
            except Exception:
                off = 0
            try:
                rows = int(strike_height)
            except Exception:
                rows = 1
            rows = max(1, min(6, rows))

            # Compute rotated column index c' (0..pattern_h-1) along length.
            if pattern_h <= 0:
                return "yellow"

            if off < pattern_h:
                c_prime = int(off)
            else:
                if pattern_h < 4:
                    c_prime = int(off % pattern_h)
                else:
                    if from_right:
                        seq = [min(3, pattern_h - 1), min(2, pattern_h - 1), min(1, pattern_h - 1), 0]
                        c_prime = int(seq[(off - pattern_h) % 4])
                    else:
                        start = max(0, pattern_h - 4)
                        seq = [start + i for i in range(min(4, pattern_h - start))]
                        c_prime = int(seq[(off - pattern_h) % len(seq)])

            c_prime = max(0, min(pattern_h - 1, int(c_prime)))

            # Compute rotated row index r' (0..5) along thickness, aligning sword TOP to r'=5.
            try:
                by = int(block_y_offset)
            except Exception:
                by = 0
            by = max(0, min(max(0, rows - 1), by))
            r_prime = int((6 - rows) + by)
            r_prime = max(0, min(5, int(r_prime)))

            # Map rotated coords back to original (row=r, col=c) without materializing the rotation.
            if from_right:
                # CCW rotation: (r,c) -> (r'=c, c'=H-1-r) => inverse: c=r', r=H-1-c'
                c0 = int(r_prime)
                r0 = int((pattern_h - 1) - c_prime)
            else:
                # CW rotation: (r,c) -> (r'=W-1-c, c'=r) => inverse: r=c', c=W-1-r'
                r0 = int(c_prime)
                c0 = int((pattern_w - 1) - r_prime)

            r0 = max(0, min(pattern_h - 1, int(r0)))
            c0 = max(0, min(pattern_w - 1, int(c0)))
            return self.pattern[r0][c0]

        # Vertical strikes: pattern columns match board columns; rows map upward from row 1 with fold.
        try:
            bx = int(block_x_offset)
        except Exception:
            bx = 0
        # Caller should pass x as the strike's left edge; block_x_offset as 0..(width-1).
        col0 = int(x) + int(bx)
        col0 = max(0, min(pattern_w - 1, int(col0)))

        try:
            by = int(block_y_offset)
        except Exception:
            by = 0
        row1 = _fold_row_1based(by + 1)
        row0 = max(0, min(pattern_h - 1, int(row1 - 1)))
        return self.pattern[row0][col0]
    
    def preview(self) -> str:
        """Generate a preview of this sword's pattern."""
        color_symbols = {"red": "R", "blue": "B", "yellow": "Y", "green": "G"}
        
        preview = [f"=== {self.name.upper()} PATTERN ==="]
        if self.description:
            preview.append(f"Description: {self.description}")
        
        # Show full pattern
        for row in range(len(self.pattern)-1, -1, -1):
            row_str = ""
            for col in range(len(self.pattern[row])):
                color = self.pattern[row][col]
                symbol = color_symbols.get(color, "?")
                row_str += f"{symbol} "
            preview.append(f"Row {row+1:2d}: {row_str}")
        
        preview.append(f"\nSprinkle Rows: 1-2 | Strike Rows: 1-{len(self.pattern)}")
        return "\n".join(preview)

# Predefined sword patterns for the inventory system
SWORD_PATTERNS: Dict[SwordType, SwordPattern] = {
    SwordType.CUTLASS: SwordPattern(
        name="Cutlass",
        description="Cutlass pattern (derived from reference grid)",
        pattern=[
            # Row 1 (bottom)
            ["yellow", "yellow", "blue", "blue", "red", "red"],
            # Row 2
            ["green", "yellow", "yellow", "blue", "red", "red"],
            # Row 3
            ["green", "green", "yellow", "yellow", "blue", "blue"],
            # Row 4
            ["green", "green", "yellow", "yellow", "blue", "blue"],
            # Row 5
            ["blue", "blue", "red", "yellow", "yellow", "yellow"],
            # Row 6 (top)
            ["red", "red", "blue", "blue", "green", "green"],
        ]
    ),
    
    SwordType.SABER: SwordPattern(
        name="Saber", 
        description="Saber pattern (derived from reference grid)",
        pattern=[
            # Row 1 (bottom)
            ["red", "blue", "blue", "red", "red", "red"],
            # Row 2
            ["red", "red", "red", "blue", "blue", "red"],
            # Row 3
            ["green", "red", "red", "blue", "blue", "yellow"],
            # Row 4
            ["green", "green", "green", "yellow", "yellow", "yellow"],
            # Row 5
            ["green", "green", "green", "yellow", "yellow", "yellow"],
            # Row 6 (top)
            ["green", "blue", "blue", "red", "red", "yellow"],
        ]
    ),
    
    SwordType.DAGGER: SwordPattern(
        name="Dagger",
        description="Compact dagger pattern (derived from reference grid)",
        pattern=[
            # Row 1 (bottom)
            ["red", "blue", "yellow", "yellow", "green", "red"],
            # Row 2
            ["red", "red", "blue", "green", "red", "red"],
            # Row 3
            ["yellow", "red", "blue", "green", "red", "yellow"],
            # Row 4
            ["yellow", "red", "blue", "green", "red", "yellow"],
            # Row 5 (top)
            ["yellow", "yellow", "blue", "green", "yellow", "yellow"],
        ]
    ),

    # --- PNG-backed swords (initial patterns; can be tuned later) ---
    SwordType.RUSTY_SWORD: SwordPattern(
        name="Rusty Sword",
        description="Starter blade; steady, predictable",
        pattern=[
            ["red", "red", "blue", "blue", "green", "green"],
            ["red", "red", "blue", "blue", "green", "green"],
            ["red", "red", "blue", "blue", "green", "green"],
            ["red", "red", "blue", "blue", "green", "green"],
        ],
    ),
    SwordType.AZURE_RAPIER: SwordPattern(
        name="Azure Rapier",
        description="Azure Rapier pattern (derived from reference grid)",
        pattern=[
            # Row 1 (bottom)
            ["red", "red", "blue", "blue", "green", "green"],
            # Row 2
            ["red", "yellow", "yellow", "blue", "yellow", "green"],
            # Row 3
            ["green", "yellow", "blue", "yellow", "yellow", "red"],
            # Row 4 (top)
            ["green", "green", "blue", "blue", "red", "red"],
        ],
    ),
    SwordType.CRIMSON_DIVIDER: SwordPattern(
        name="Crimson Divider",
        description="Crimson Divider pattern (derived from reference grid)",
        pattern=[
            # Row 1 (bottom)
            ["red", "red", "green", "yellow", "red", "red"],
            # Row 2
            ["red", "blue", "green", "yellow", "blue", "red"],
            # Row 3
            ["green", "green", "green", "yellow", "yellow", "yellow"],
            # Row 4 (top)
            ["green", "blue", "blue", "blue", "blue", "yellow"],
        ],
    ),
    SwordType.DEEP_CURRENT: SwordPattern(
        name="Deep Current",
        description="Deep Current pattern (derived from reference grid)",
        pattern=[
            # Row 1 (bottom)
            ["green", "green", "blue", "blue", "green", "green"],
            # Row 2
            ["green", "green", "blue", "blue", "green", "green"],
            # Row 3
            ["red", "yellow", "yellow", "red", "red", "yellow"],
            # Row 4
            ["yellow", "red", "red", "yellow", "yellow", "red"],
            # Row 5
            ["blue", "green", "green", "blue", "blue", "green"],
            # Row 6 (top)
            ["green", "blue", "blue", "green", "green", "blue"],
        ],
    ),
    SwordType.EMBER_BLADE: SwordPattern(
        name="Ember Blade",
        description="Ember Blade pattern (derived from reference grid)",
        pattern=[
            # Row 1 (bottom)
            ["green", "red", "red", "blue", "blue", "green"],
            # Row 2
            ["red", "green", "red", "blue", "green", "green"],
            # Row 3
            ["red", "red", "green", "yellow", "yellow", "green"],
            # Row 4
            ["yellow", "red", "red", "yellow", "blue", "blue"],
            # Row 5
            ["red", "yellow", "red", "red", "red", "blue"],
            # Row 6 (top)
            ["red", "red", "yellow", "red", "blue", "blue"],
        ],
    ),
    SwordType.FOREST_CLEAVER: SwordPattern(
        name="Forest Cleaver",
        description="Forest Cleaver pattern (derived from reference grid)",
        pattern=[
            # Row 1 (bottom)
            ["yellow", "green", "green", "blue", "blue", "yellow"],
            # Row 2
            ["red", "red", "green", "blue", "red", "red"],
            # Row 3
            ["red", "yellow", "yellow", "yellow", "yellow", "red"],
            # Row 4
            ["red", "yellow", "green", "blue", "yellow", "red"],
            # Row 5 (top)
            ["green", "green", "green", "blue", "blue", "blue"],
        ],
    ),
    SwordType.VERDANT_WALL: SwordPattern(
        name="Verdant Wall",
        description="Verdant Wall pattern (derived from reference grid)",
        pattern=[
            # Row 1 (bottom)
            ["red", "red", "yellow", "yellow", "red", "red"],
            # Row 2
            ["red", "blue", "blue", "green", "green", "red"],
            # Row 3
            ["yellow", "red", "blue", "green", "red", "yellow"],
            # Row 4
            ["yellow", "red", "blue", "green", "red", "yellow"],
            # Row 5 (top)
            ["yellow", "red", "red", "red", "red", "yellow"],
        ],
    ),

    # Fists: preview is a single solid color; actual color randomizes per game.
    SwordType.FISTS: SwordPattern(
        name="Fists",
        description="All one color (randomizes per game)",
        pattern=[
            ["yellow", "yellow", "yellow", "yellow", "yellow", "yellow"],
            ["yellow", "yellow", "yellow", "yellow", "yellow", "yellow"],
            ["yellow", "yellow", "yellow", "yellow", "yellow", "yellow"],
            ["yellow", "yellow", "yellow", "yellow", "yellow", "yellow"],
        ],
    ),
}

# Optional: link sword types to weapon PNG art.
SWORD_ASSET_FILES: Dict[SwordType, str] = {
    SwordType.RUSTY_SWORD: "rusty_sword.png",
    SwordType.AZURE_RAPIER: "azure_rapier.png",
    SwordType.CRIMSON_DIVIDER: "crimson_divider.png",
    SwordType.DEEP_CURRENT: "deep_current.png",
    SwordType.EMBER_BLADE: "ember_blade.png",
    SwordType.FOREST_CLEAVER: "forest_cleaver.png",
    SwordType.VERDANT_WALL: "verdant_wall.png",
    SwordType.FISTS: "fists.png",
}


def get_sword_asset_filename(sword_type: SwordType) -> str | None:
    """Return the PNG filename for this sword type (if available)."""
    try:
        return SWORD_ASSET_FILES.get(sword_type)
    except Exception:
        return None
    
class PatternManager:
    """Manages sword patterns for fighters - supports inventory system."""
    
    def __init__(self, default_sword: SwordType = SwordType.CUTLASS):
        self.player_sword = SWORD_PATTERNS[default_sword]
        self.ai_sword = SWORD_PATTERNS[default_sword]  # Can be different
    
    def set_player_sword(self, sword_type: SwordType):
        """Set the player's current sword pattern (for inventory system)."""
        self.player_sword = SWORD_PATTERNS[sword_type]
    
    def set_ai_sword(self, sword_type: SwordType):
        """Set the AI's current sword pattern."""
        self.ai_sword = SWORD_PATTERNS[sword_type]
    
    def get_pattern_for_fighter(self, is_player: bool) -> SwordPattern:
        """Get the appropriate pattern for the given fighter."""
        return self.player_sword if is_player else self.ai_sword
    
    def preview_all_patterns(self) -> str:
        """Preview all available sword patterns."""
        previews = []
        for sword_type in SwordType:
            if sword_type in SWORD_PATTERNS:
                previews.append(SWORD_PATTERNS[sword_type].preview())
        return "\n\n".join(previews)

# Global pattern manager - can be configured per game session
_pattern_manager = PatternManager()

# Convenience functions that work with current player/AI patterns
def get_sprinkle_color(x: int, y: int, layer: int = 1, is_player: bool = True) -> str:
    """Get sprinkle color using the appropriate fighter's sword pattern."""
    pattern = _pattern_manager.get_pattern_for_fighter(is_player)
    return pattern.get_sprinkle_color(x, y, layer)

def get_strike_color(x: int, y: int, strike_width: int, strike_height: int, 
                    block_x_offset: int, block_y_offset: int, is_horizontal: bool = False,
                    from_right: bool = False, is_player: bool = True) -> str:
    """Get strike color using the appropriate fighter's sword pattern."""
    pattern = _pattern_manager.get_pattern_for_fighter(is_player)
    return pattern.get_strike_color(x, y, strike_width, strike_height,
                                   block_x_offset, block_y_offset, 
                                   is_horizontal, from_right)

def get_strike_colors(x: int, y: int, width: int, height: int, 
                     is_horizontal: bool = False, from_right: bool = False,
                     is_player: bool = True) -> List[List[str]]:
    """Get strike pattern colors using the appropriate fighter's sword pattern."""
    pattern = _pattern_manager.get_pattern_for_fighter(is_player)
    
    strike_pattern = []
    for row in range(height):
        strike_row = []
        for col in range(width):
            color = pattern.get_strike_color(x, y, width, height, col, row, 
                                           is_horizontal, from_right)
            strike_row.append(color)
        strike_pattern.append(strike_row)
    
    return strike_pattern

# Inventory system functions
def set_player_sword(sword_type: SwordType):
    """Set player's sword pattern (for inventory/equipment system)."""
    _pattern_manager.set_player_sword(sword_type)

def set_ai_sword(sword_type: SwordType):
    """Set AI's sword pattern."""
    _pattern_manager.set_ai_sword(sword_type)

def get_available_swords() -> List[SwordType]:
    """Get list of available sword types for inventory."""
    return list(SWORD_PATTERNS.keys())

def preview_garbage_pattern(sword_type: SwordType = None) -> str:
    """Preview a specific sword pattern or current player pattern."""
    if sword_type:
        return SWORD_PATTERNS[sword_type].preview()
    else:
        return _pattern_manager.player_sword.preview()

# Backwards compatibility functions
def get_pattern_color(x: int, y: int) -> str:
    """Legacy function for backwards compatibility. 
    
    Uses sprinkle pattern (layer 1) for the current player's sword.
    This maintains compatibility with existing lifecycle code.
    """
    return get_sprinkle_color(x, y, layer=1, is_player=True)

if __name__ == "__main__":
    # Test the pattern system
    print("=== Garbage Pattern Preview ===")
    print(preview_garbage_pattern())
    
    print("\n=== Example Strike Pattern (2x4 at position 1,2) ===")
    strike_colors = get_strike_colors(1, 2, 2, 4)
    for i, row in enumerate(strike_colors):
        print(f"Strike Row {i}: {row}")
    
    print("\n=== Example Sprinkle Colors (Layer 1 and 2) ===")
    sprinkle_positions = [(0, 0), (2, 3), (4, 7), (1, 11)]
    print("Layer 1:")
    for pos in sprinkle_positions:
        color = get_sprinkle_color(pos[0], pos[1], layer=1)
        print(f"  Position {pos}: {color}")
    print("Layer 2:")
    for pos in sprinkle_positions:
        color = get_sprinkle_color(pos[0], pos[1], layer=2)
        print(f"  Position {pos}: {color}")
