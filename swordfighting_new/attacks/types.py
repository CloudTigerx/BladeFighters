"""Core attack type definitions.

This module purposefully contains only small, dependency-light dataclasses so
other systems (UI, networking, AI) can import attack metadata without pulling
in generation logic.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict

DEFAULT_ATTACK_DELAY = 4  # frames (tunable by caller after creation)


class AttackKind(str, Enum):
    """Enumerated attack categories.

    Using an ``Enum`` (that subclasses ``str``) preserves JSON friendliness
    while giving type-checkers a closed set of values. Existing code that used
    literal strings ("sprinkle" / "strike") will continue to work because the
    enum inherits from ``str``.
    """

    SPRINKLE = "sprinkle"
    STRIKE = "strike"


@dataclass(slots=True)
class Attack:
    """Outbound garbage attack scheduled for future delivery.

    Attributes:
        kind: ``AttackKind`` value (sprinkle or strike).
        amount: Magnitude / block count represented by the attack.
        delay: Frames until the attack becomes active / deliverable.
        meta: Free-form dictionary with generation context (e.g. pass index,
              rectangle dimensions). Keep values JSON-serializable.
    """

    kind: AttackKind
    amount: int
    delay: int = DEFAULT_ATTACK_DELAY
    meta: Dict[str, Any] = field(default_factory=dict)

    def tick(self):  # small convenience helper
        if self.delay > 0:
            self.delay -= 1
        return self.delay

    @property
    def ready(self) -> bool:
        return self.delay <= 0
