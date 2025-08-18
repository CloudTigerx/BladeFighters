"""
Item System - Manages weapons and their patterns
Provides weapon creation, pattern validation, and color management.
"""

from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from ..logging_module.error_handler import (
    safe_operation
)
from ..logging_module.logger import get_logger

logger = get_logger(__name__)


# Valid colors for weapon patterns
VALID_COLORS = ["red", "blue", "green", "yellow"]


@dataclass
class WeaponPattern:
    """Represents a weapon's attack pattern across columns and rows."""
    column_to_color: Dict[int, str]
    rows_per_column: Optional[Dict[int, List[str]]] = None

    def color_for_column(self, column_index: int) -> str:
        """Get the base color for a column."""
        try:
            color = self.column_to_color.get(column_index % 6, VALID_COLORS[column_index % len(VALID_COLORS)])
            # Safety check: ensure color is valid
            if not color or not isinstance(color, str) or color not in VALID_COLORS:
                return VALID_COLORS[0]  # Default to red
            return color
        except Exception:
            return VALID_COLORS[0]  # Default to red

    def color_for_cell(self, column_index: int, grid_row_index: int, grid_height: int) -> str:
        """Get the color for a specific cell in the grid."""
        try:
            col = column_index % 6
            if self.rows_per_column and col in self.rows_per_column:
                # Use row-specific pattern if available
                relative_from_bottom = (grid_height - 1 - grid_row_index) % 12
                color = self.rows_per_column[col][relative_from_bottom]
                # Safety check: ensure color is valid
                if not color or not isinstance(color, str) or color not in VALID_COLORS:
                    return VALID_COLORS[0]  # Default to red
                return color
            else:
                # Fall back to column color
                return self.color_for_column(column_index)
        except Exception:
            return VALID_COLORS[0]  # Default to red


@dataclass
class Weapon:
    """Represents a weapon with a name and attack pattern."""
    name: str
    pattern: WeaponPattern


class ItemSystem:
    """
    Manages weapon equipment and ownership for a player.
    Handles weapon validation, color management, and ownership tracking.
    """

    def __init__(self):
        self._equipped_weapon: Optional[Weapon] = None
        self._owned_weapons: List[str] = ["Rusted Sword"]  # Default weapon
        self._equip_callbacks: List[Callable[[Weapon], None]] = []

    def add_equip_callback(self, callback: Callable[[Weapon], None]) -> None:
        """Add a callback to be called when a weapon is equipped."""
        self._equip_callbacks.append(callback)

    def equip_weapon(self, weapon: Weapon) -> None:
        """Equip a weapon with pattern validation and notifications."""
        # Optional: validate pattern policy here
        self._validate_weapon_pattern(weapon)
        self._equipped_weapon = weapon
        
        # Notify all callbacks about the equipment change
        for callback in self._equip_callbacks:
            try:
                callback(weapon)
            except Exception as e:
                logger.warning(f"Equip callback failed: {e}")
        
        # Log the equipment change
        logger.info(f"Equipped weapon: {weapon.name}")
        print(f"⚔️ Equipped: {weapon.name}")

    @safe_operation("validate weapon pattern", None, "WARNING")
    def _validate_weapon_pattern(self, weapon: Weapon) -> None:
        """Validate weapon pattern against rules."""
        try:
            from .pattern_rules import is_pattern_allowed
            allowed, reason = is_pattern_allowed(weapon.pattern, grid_height=12)
            if not allowed:
                logger.warning(f"Weapon pattern rejected: {reason}")
        except Exception as e:
            logger.warning(f"Failed to validate weapon pattern: {str(e)}")
            # If rule module not available or raises, proceed (non-fatal)

    def get_equipped_weapon(self) -> Optional[Weapon]:
        return self._equipped_weapon

    def get_attack_color_for_column(self, column_index: int) -> str:
        """
        Returns the color to use for attack blocks (garbage/strike)
        landing in the given column.
        """
        if self._equipped_weapon is not None:
            return self._equipped_weapon.pattern.color_for_column(column_index)
        # Default fallback if no weapon equipped
        return VALID_COLORS[column_index % len(VALID_COLORS)]

    def get_garbage_color_for_column(self, column_index: int) -> str:
        """Bottom-row color for garbage blocks."""
        return self.get_attack_color_for_column(column_index)

    def get_strike_color_for_cell(self, column_index: int, grid_row_index: int, grid_height: int) -> str:
        """Per-cell color for strikes using the full 12-row pattern."""
        if self._equipped_weapon is not None:
            return self._equipped_weapon.pattern.color_for_cell(column_index, grid_row_index, grid_height)
        # Fallback: use column cycle
        relative_from_bottom = (grid_height - 1 - grid_row_index) % 12
        base_color = VALID_COLORS[column_index % len(VALID_COLORS)]
        return base_color
    
    def get_color_for_position(self, position: tuple) -> str:
        """Get the color for a position based on equipped weapon pattern."""
        if not self._equipped_weapon:
            return VALID_COLORS[0]  # Default to red
        
        x, y = position
        # Use column-based color assignment for transformation system
        return self._equipped_weapon.pattern.color_for_column(x)
    
    def get_weapon_pattern(self) -> Optional[WeaponPattern]:
        """Get the current weapon pattern for transformation system."""
        if not self._equipped_weapon:
            return None
        return self._equipped_weapon.pattern

    # Ownership management
    def set_owned_weapons(self, names: List[str]) -> None:
        self._owned_weapons = list(dict.fromkeys(names))  # de-duplicate preserve order

    def get_owned_weapons(self) -> List[str]:
        return list(self._owned_weapons)

    def add_weapon(self, name: str) -> None:
        if name not in self._owned_weapons:
            self._owned_weapons.append(name)


def create_rusted_sword() -> Weapon:
    """
    Rusted Sword pattern:
    columns 0,1 -> red
    columns 2,3 -> blue
    columns 4,5 -> green
    """
    pattern = WeaponPattern(
        column_to_color={
            0: "red",
            1: "red",
            2: "blue",
            3: "blue",
            4: "green",
            5: "green",
        }
    )
    return Weapon(name="Rusted Sword", pattern=pattern)


# Registry for scalable weapon creation by name
WEAPON_FACTORIES: Dict[str, Callable[[], Weapon]] = {
    "Rusted Sword": create_rusted_sword,
}


@safe_operation("create weapon by name", None, "WARNING")
def create_weapon_by_name(name: str) -> Optional[Weapon]:
    """Create a Weapon by display name.
    Falls back to curated catalog if not in hardcoded factories.
    """
    # Safety check: ensure name is valid
    if not name or not isinstance(name, str):
        logger.warning(f"Invalid weapon name: {name}")
        return None
    
    factory = WEAPON_FACTORIES.get(name)
    if factory:
        try:
            weapon = factory()
            # Validate the created weapon
            if weapon and hasattr(weapon, 'name') and hasattr(weapon, 'pattern'):
                return weapon
            else:
                logger.warning(f"Factory created invalid weapon for {name}")
                return None
        except Exception as e:
            logger.warning(f"Factory failed to create weapon {name}: {str(e)}")
            return None
    
    # Fallback: use catalog's create_weapon_by_name function
    try:
        from .catalog import create_weapon_by_name as catalog_create_weapon
        weapon = catalog_create_weapon(name)
        if weapon and hasattr(weapon, 'name') and hasattr(weapon, 'pattern'):
            return weapon
        else:
            logger.warning(f"Catalog created invalid weapon for {name}")
            return None
    except Exception as e:
        logger.warning(f"Failed to create weapon from catalog for {name}: {str(e)}")
    
    return None


# --- Placeholder weapon ideas ---
def create_ember_blade() -> Weapon:
    # Heavy red bias on left, blue mid, green right
    pattern = WeaponPattern({0: "red", 1: "red", 2: "red", 3: "blue", 4: "green", 5: "green"})
    return Weapon(name="Ember Blade", pattern=pattern)


def create_azure_rapier() -> Weapon:
    # Blue dominance, with yellow accents
    pattern = WeaponPattern({0: "blue", 1: "blue", 2: "yellow", 3: "blue", 4: "blue", 5: "yellow"})
    return Weapon(name="Azure Rapier", pattern=pattern)


def create_forest_cleaver() -> Weapon:
    # Green dominance, with red spikes
    pattern = WeaponPattern({0: "green", 1: "green", 2: "red", 3: "green", 4: "green", 5: "red"})
    return Weapon(name="Forest Cleaver", pattern=pattern)


def create_sun_spear() -> Weapon:
    # Yellow core, with flanking reds
    pattern = WeaponPattern({0: "red", 1: "yellow", 2: "yellow", 3: "yellow", 4: "yellow", 5: "red"})
    return Weapon(name="Sun Spear", pattern=pattern)


def create_prism_katana() -> Weapon:
    # Rainbow across columns
    pattern = WeaponPattern({0: "red", 1: "yellow", 2: "green", 3: "blue", 4: "yellow", 5: "green"})
    return Weapon(name="Prism Katana", pattern=pattern)


# Register placeholders
WEAPON_FACTORIES.update({
    "Ember Blade": create_ember_blade,
    "Azure Rapier": create_azure_rapier,
    "Forest Cleaver": create_forest_cleaver,
    "Sun Spear": create_sun_spear,
    "Prism Katana": create_prism_katana,
})

