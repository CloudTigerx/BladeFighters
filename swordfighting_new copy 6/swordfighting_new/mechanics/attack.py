"""Legacy compatibility shim for relocated attack system.

The attack implementation now lives in ``swordfighting_new.attacks``. Importing
from this legacy module continues to work but will emit a gentle runtime note
once (can be removed after codebase finishes migration).
"""
from __future__ import annotations
from warnings import warn

from swordfighting_new.attacks import Attack, AttackManager  # re-export

warn(
    "Import path 'swordfighting_new.mechanics.attack' is deprecated. Use 'swordfighting_new.attacks' instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["Attack", "AttackManager"]

