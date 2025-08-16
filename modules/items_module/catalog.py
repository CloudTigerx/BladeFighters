"""
Curated weapon catalog (initial 60 patterns).
Each entry defines bottom-row column colors; vertical pattern is flat for v0.
"""

from typing import List, Dict, Optional
from .item_system import Weapon, WeaponPattern, VALID_COLORS


def create_weapon_by_name(name: str) -> Optional[Weapon]:
    """Create a weapon by name from the curated catalog."""
    for weapon_data in CURATED_WEAPONS:
        if weapon_data["name"] == name:
            return _build_weapon_from_data(weapon_data)
    return None


def _build_weapon_from_data(weapon_data: Dict) -> Weapon:
    """Build a Weapon object from catalog data."""
    name = weapon_data["name"]
    cols = weapon_data["columns"]
    
    # Validate and sanitize column colors
    if isinstance(cols, list) and len(cols) == 6:
        col_map = {i: (c if c in VALID_COLORS else VALID_COLORS[i % len(VALID_COLORS)]) for i, c in enumerate(cols)}
    else:
        # Fallback to default pattern
        col_map = {i: VALID_COLORS[i % len(VALID_COLORS)] for i in range(6)}
    
    # Handle row_cycles if present
    rows_per_column = None
    row_cycles = weapon_data.get('row_cycles')
    if isinstance(row_cycles, list) and len(row_cycles) == 6:
        rows_per_column = {}
        for i in range(6):
            cycle = row_cycles[i] if isinstance(row_cycles[i], list) else []
            if not cycle:
                base = col_map.get(i, VALID_COLORS[i % len(VALID_COLORS)])
                cycle = [base]
            # Sanitize colors
            cycle = [c if c in VALID_COLORS else col_map.get(i, VALID_COLORS[i % len(VALID_COLORS)]) for c in cycle]
            # Expand to 12 rows
            rows = [cycle[r % len(cycle)] for r in range(12)]
            rows_per_column[i] = rows
    
    pattern = WeaponPattern(column_to_color=col_map, rows_per_column=rows_per_column)
    return Weapon(name=name, pattern=pattern)


CURATED_WEAPONS: List[Dict] = [
    # Mono-bias (12)
    {"name": "Rusted Sword", "slug": "rusty_sword", "columns": ["red", "red", "blue", "blue", "green", "green"]},
    {"name": "Ember Blade", "slug": "ember_blade", "columns": ["red", "red", "red", "blue", "green", "green"]},
    {"name": "Crimson Divider", "slug": "crimson_divider", "columns": ["red", "red", "red", "red", "blue", "green"]},
    {"name": "Azure Rapier", "slug": "azure_rapier", "columns": ["blue", "blue", "yellow", "blue", "blue", "yellow"]},
    {"name": "Deep Current", "slug": "deep_current", "columns": ["blue", "blue", "blue", "green", "yellow", "blue"]},
    {"name": "Forest Cleaver", "slug": "forest_cleaver", "columns": ["green", "green", "red", "green", "green", "red"]},
    {"name": "Verdant Wall", "slug": "verdant_wall", "columns": ["green", "green", "green", "yellow", "red", "green"]},
    {"name": "Sun Spear", "slug": "sun_spear", "columns": ["red", "yellow", "yellow", "yellow", "yellow", "red"]},
    {"name": "Golden Veil", "slug": "golden_veil", "columns": ["yellow", "yellow", "blue", "yellow", "yellow", "green"]},
    {"name": "Ruby Spine", "slug": "ruby_spine", "columns": ["red", "red", "red", "red", "yellow", "yellow"]},
    {"name": "Azure Crest", "slug": "azure_crest", "columns": ["blue", "blue", "blue", "blue", "red", "red"]},
    {"name": "Verdant Crest", "slug": "verdant_crest", "columns": ["green", "green", "green", "green", "blue", "blue"]},

    # Dual-split (16)
    {"name": "Fire-Ice Wall", "slug": "fire_ice_wall", "columns": ["red", "red", "red", "blue", "blue", "blue"]},
    {"name": "Grove-Sun Wall", "slug": "grove_sun_wall", "columns": ["green", "green", "green", "yellow", "yellow", "yellow"]},
    {"name": "Edge Fire, Center Ice", "slug": "edge_fire_center_ice", "columns": ["red", "blue", "blue", "blue", "blue", "red"]},
    {"name": "Edge Grove, Center Sun", "slug": "edge_grove_center_sun", "columns": ["green", "yellow", "yellow", "yellow", "yellow", "green"]},
    {"name": "Outer Flame", "slug": "outer_flame", "columns": ["red", "red", "blue", "blue", "red", "red"]},
    {"name": "Outer Frost", "slug": "outer_frost", "columns": ["blue", "blue", "red", "red", "blue", "blue"]},
    {"name": "Outer Grove", "slug": "outer_grove", "columns": ["green", "green", "blue", "blue", "green", "green"]},
    {"name": "Outer Sun", "slug": "outer_sun", "columns": ["yellow", "yellow", "green", "green", "yellow", "yellow"]},
    {"name": "Inner Flame", "slug": "inner_flame", "columns": ["blue", "red", "red", "red", "red", "blue"]},
    {"name": "Inner Frost", "slug": "inner_frost", "columns": ["red", "blue", "blue", "blue", "blue", "red"]},
    {"name": "Inner Grove", "slug": "inner_grove", "columns": ["blue", "green", "green", "green", "green", "blue"]},
    {"name": "Inner Sun", "slug": "inner_sun", "columns": ["green", "yellow", "yellow", "yellow", "yellow", "green"]},
    {"name": "Left Warm, Right Cool", "slug": "left_warm_right_cool", "columns": ["red", "yellow", "yellow", "blue", "blue", "green"]},
    {"name": "Left Cool, Right Warm", "slug": "left_cool_right_warm", "columns": ["blue", "green", "blue", "yellow", "yellow", "red"]},
    {"name": "Flame Ramp", "slug": "flame_ramp", "columns": ["red", "red", "yellow", "yellow", "green", "green"]},
    {"name": "Frost Ramp", "slug": "frost_ramp", "columns": ["blue", "blue", "green", "green", "yellow", "yellow"]},

    # Tri-split (12)
    {"name": "RGB Bands", "slug": "rgb_bands", "columns": ["red", "red", "green", "green", "blue", "blue"]},
    {"name": "RBY Bands", "slug": "rby_bands", "columns": ["red", "red", "blue", "blue", "yellow", "yellow"]},
    {"name": "GYR Bands", "slug": "gyr_bands", "columns": ["green", "green", "yellow", "yellow", "red", "red"]},
    {"name": "Spiral Warm", "slug": "spiral_warm", "columns": ["red", "yellow", "red", "yellow", "red", "yellow"],
     "row_cycles": [["red","yellow"],["yellow","red"],["red","yellow"],["yellow","red"],["red","yellow"],["yellow","red"]]},
    {"name": "Spiral Cool", "slug": "spiral_cool", "columns": ["blue", "green", "blue", "green", "blue", "green"],
     "row_cycles": [["blue","green"],["green","blue"],["blue","green"],["green","blue"],["blue","green"],["green","blue"]]},
    {"name": "Warm to Cool", "slug": "warm_to_cool", "columns": ["red", "yellow", "green", "green", "blue", "blue"]},
    {"name": "Cool to Warm", "slug": "cool_to_warm", "columns": ["blue", "blue", "green", "green", "yellow", "red"]},
    {"name": "Fire-Wood-Steel", "slug": "fire_wood_steel", "columns": ["red", "red", "green", "blue", "blue", "green"]},
    {"name": "Sun-Sea-Grove", "slug": "sun_sea_grove", "columns": ["yellow", "yellow", "blue", "green", "green", "blue"]},
    {"name": "Ember-Leaf-Sky", "slug": "ember_leaf_sky", "columns": ["red", "green", "blue", "red", "green", "blue"]},
    {"name": "Sky-Leaf-Ember", "slug": "sky_leaf_ember", "columns": ["blue", "green", "red", "blue", "green", "red"]},
    {"name": "Grove-Sun-Sky", "slug": "grove_sun_sky", "columns": ["green", "yellow", "blue", "green", "yellow", "blue"]},

    # Periodic/alternating (12)
    {"name": "Checker Warm", "slug": "checker_warm", "columns": ["red", "yellow", "red", "yellow", "red", "yellow"]},
    {"name": "Checker Cool", "slug": "checker_cool", "columns": ["blue", "green", "blue", "green", "blue", "green"]},
    {"name": "Stripe 2-step Warm", "slug": "stripe2_warm", "columns": ["red", "red", "yellow", "yellow", "red", "red"]},
    {"name": "Stripe 2-step Cool", "slug": "stripe2_cool", "columns": ["blue", "blue", "green", "green", "blue", "blue"]},
    {"name": "3-Cycle RGB", "slug": "cycle3_rgb", "columns": ["red", "green", "blue", "red", "green", "blue"],
     "row_cycles": [["red","green","blue"]]*6},
    {"name": "3-Cycle YBG", "slug": "cycle3_ybg", "columns": ["yellow", "blue", "green", "yellow", "blue", "green"],
     "row_cycles": [["yellow","blue","green"]]*6},
    {"name": "6-Cycle RG BY RG", "slug": "cycle6_rgbyrg", "columns": ["red", "green", "blue", "yellow", "red", "green"],
     "row_cycles": [["red","green","blue","yellow","red","green"]]*6},
    {"name": "6-Cycle BY GR BY", "slug": "cycle6_bygrby", "columns": ["blue", "yellow", "green", "red", "blue", "yellow"],
     "row_cycles": [["blue","yellow","green","red","blue","yellow"]]*6},
    {"name": "Pinstripe Warm Edge", "slug": "pinstripe_warm_edge", "columns": ["red", "yellow", "yellow", "yellow", "yellow", "red"]},
    {"name": "Pinstripe Cool Edge", "slug": "pinstripe_cool_edge", "columns": ["blue", "green", "green", "green", "green", "blue"]},
    {"name": "Alternating Lanes A", "slug": "alternating_lanes_a", "columns": ["red", "blue", "red", "blue", "green", "yellow"]},
    {"name": "Alternating Lanes B", "slug": "alternating_lanes_b", "columns": ["yellow", "green", "yellow", "green", "blue", "red"]},

    # Specialty (8)
    {"name": "Center Flame Tower", "slug": "center_flame_tower", "columns": ["blue", "red", "red", "red", "red", "blue"],
     "row_cycles": [
         ["blue","blue","blue","blue","blue","blue","blue","blue","blue","blue","blue","blue"],
         ["red","red","red","yellow","yellow","yellow","red","red","red","yellow","yellow","yellow"],
         ["red","red","red","yellow","yellow","yellow","red","red","red","yellow","yellow","yellow"],
         ["red","red","red","yellow","yellow","yellow","red","red","red","yellow","yellow","yellow"],
         ["red","red","red","yellow","yellow","yellow","red","red","red","yellow","yellow","yellow"],
         ["blue","blue","blue","blue","blue","blue","blue","blue","blue","blue","blue","blue"],
     ]},
    {"name": "Twin Ember Spires", "slug": "twin_ember_spires", "columns": ["red", "red", "yellow", "yellow", "red", "red"]},
    {"name": "Center Grove Tower", "slug": "center_grove_tower", "columns": ["blue", "green", "green", "green", "green", "blue"]},
    {"name": "Twin Grove Spires", "slug": "twin_grove_spires", "columns": ["green", "green", "blue", "blue", "green", "green"]},
    {"name": "Edge Suns", "slug": "edge_suns", "columns": ["yellow", "blue", "green", "green", "blue", "yellow"]},
    {"name": "Center Suns", "slug": "center_suns", "columns": ["blue", "yellow", "yellow", "yellow", "yellow", "blue"]},
    {"name": "Mirror Flame/Grove", "slug": "mirror_flame_grove", "columns": ["red", "green", "yellow", "yellow", "green", "red"]},
    {"name": "Mirror Ice/Sun", "slug": "mirror_ice_sun", "columns": ["blue", "yellow", "green", "green", "yellow", "blue"]},
]

