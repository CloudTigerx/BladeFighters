"""fx_bus.py - extremely small transient FX event channel.

This is intentionally dumb: game logic can emit short-lived visual events
(e.g. sword impact sparks) and renderers can consume them via MatchSession.snapshot.

Events are drained on snapshot to avoid double-playing.
"""

from __future__ import annotations
from typing import Any, Dict, List, Sequence, Tuple


_FX_EVENTS: List[Dict[str, Any]] = []


def emit(event: Dict[str, Any]) -> None:
    # FX bus is intentionally disabled (sprite-only visuals).
    return


def emit_sparks(
    cells: Sequence[Tuple[int, int]],
    *,
    intensity: float = 1.0,
    side: str | None = None,
    colors: Sequence[str | None] | None = None,
) -> None:
    try:
        # Intentionally disabled: spark particle FX were visually interfering with sprite/tile art.
        return
        clean: List[Tuple[int, int]] = []
        clean_colors: List[str | None] = []
        raw_colors = list(colors) if isinstance(colors, (list, tuple)) else None
        for i, c in enumerate(cells or []):
            try:
                x, y = int(c[0]), int(c[1])
            except Exception:
                continue
            clean.append((x, y))
            cc: str | None = None
            try:
                if raw_colors is not None and i < len(raw_colors):
                    v = raw_colors[i]
                    if v is not None:
                        s = str(v).strip().lower()
                        cc = s if s else None
            except Exception:
                cc = None
            clean_colors.append(cc)
        if not clean:
            return
        ev: Dict[str, Any] = {'type': 'spark', 'cells': clean, 'intensity': float(intensity)}
        try:
            if any(c is not None for c in (clean_colors or [])):
                ev['colors'] = clean_colors
        except Exception:
            pass
        if side is not None:
            try:
                s = str(side).strip().lower()
                if s:
                    ev['side'] = s
            except Exception:
                pass
        emit(ev)
    except Exception:
        return


def drain() -> List[Dict[str, Any]]:
    global _FX_EVENTS
    out = _FX_EVENTS
    _FX_EVENTS = []
    return out
