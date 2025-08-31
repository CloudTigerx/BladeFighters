"""Attacks package.

Defines outbound garbage attack objects produced from breaker chain pass
statistics. Two canonical attack categories are supported:
 - Sprinkle: derived from non-cluster single clears ("sprinkles").
 - Strike: derived from cleared solid rectangles / clusters.

The public entry point is ``AttackManager`` in ``manager.py``. For legacy
imports (``swordfighting_new.mechanics.attack``) a compatibility shim is kept
so existing code continues to function while the project migrates to the new
package layout.
"""

from .types import Attack, AttackKind
from .manager import AttackManager

__all__ = ["Attack", "AttackKind", "AttackManager"]
