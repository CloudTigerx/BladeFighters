"""Lightweight debug helpers.

This project intentionally uses simple, dependency-free debug gating.
Use env flags ("0"/"1", "false"/"true") to enable verbose logging without
changing gameplay behavior.
"""

from __future__ import annotations

import os
from typing import Any


def env_flag(name: str, default: bool = False) -> bool:
    """Read a boolean-ish environment variable."""
    raw = os.getenv(name)
    if raw is None:
        return bool(default)
    s = str(raw).strip().lower()
    if s in {"1", "true", "t", "yes", "y", "on"}:
        return True
    if s in {"0", "false", "f", "no", "n", "off", ""}:
        return False
    return bool(default)


def dprint(enabled: bool, *args: Any, **kwargs: Any) -> None:
    """Print only when enabled."""
    if not enabled:
        return
    try:
        print(*args, **kwargs)
    except Exception:
        return
