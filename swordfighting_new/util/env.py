from __future__ import annotations

import os
from typing import Iterable, TypeVar


_T = TypeVar("_T")


def _raw_env(name: str) -> str | None:
    try:
        v = os.getenv(name)
    except Exception:
        v = None
    if v is None:
        return None
    s = str(v)
    if not s.strip():
        return None
    return s


def env_str(name: str, default: str) -> str:
    raw = _raw_env(name)
    return str(default) if raw is None else str(raw)


def env_int(name: str, default: int, *, lo: int | None = None, hi: int | None = None) -> int:
    raw = _raw_env(name)
    if raw is None:
        v = int(default)
    else:
        try:
            # Allow "10.0" etc.
            v = int(float(str(raw).strip()))
        except Exception:
            v = int(default)

    if lo is not None:
        v = max(int(lo), int(v))
    if hi is not None:
        v = min(int(hi), int(v))
    return int(v)


def env_float(name: str, default: float, *, lo: float | None = None, hi: float | None = None) -> float:
    raw = _raw_env(name)
    if raw is None:
        v = float(default)
    else:
        try:
            v = float(str(raw).strip())
        except Exception:
            v = float(default)

    if lo is not None:
        v = max(float(lo), float(v))
    if hi is not None:
        v = min(float(hi), float(v))
    return float(v)


def env_bool(name: str, default: bool) -> bool:
    raw = _raw_env(name)
    if raw is None:
        return bool(default)

    s = str(raw).strip().lower()
    if s in ("1", "true", "yes", "y", "on"):
        return True
    if s in ("0", "false", "no", "n", "off"):
        return False

    return bool(default)


def env_choice(name: str, default: _T, choices: Iterable[_T]) -> _T:
    raw = _raw_env(name)
    if raw is None:
        return default
    for c in choices:
        if str(c).lower() == str(raw).strip().lower():
            return c
    return default
