from __future__ import annotations

from collections.abc import Callable


def compute_sword_grid(*, swords_rect, n: int, ui_scale: float) -> dict:
    """Shared grid sizing math for menu sword tiles."""
    n = int(max(0, int(n)))
    ui_scale = float(ui_scale)
    gap = int(max(8, round(10 * ui_scale)))
    min_tile_h = int(max(66, round(92 * ui_scale)))

    cols = 1
    max_cols = 3
    for c in range(1, max_cols + 1):
        tile_w = int((int(swords_rect.w) - (c - 1) * gap) / max(1, c))
        if tile_w >= int(max(64, round(120 * ui_scale))) or c == 1:
            cols = c
    cols = int(max(1, min(max_cols, int(cols))))
    rows = int((n + cols - 1) // cols) if n > 0 else 0

    tile_w = int((int(swords_rect.w) - (cols - 1) * gap) / max(1, cols))
    tile_w = int(max(40, int(tile_w)))
    tile_h = int(min_tile_h)

    content_h = int(rows * tile_h + max(0, rows - 1) * gap)
    max_scroll = int(max(0, content_h - int(swords_rect.h)))

    return {
        'gap': int(gap),
        'cols': int(cols),
        'rows': int(rows),
        'tile_w': int(tile_w),
        'tile_h': int(tile_h),
        'max_scroll': int(max_scroll),
    }


def menu_scroll_key_for_side(side: str) -> str:
    return 'a' if str(side).lower() in ('left', 'a', 'bot_a') else 'b'


def get_and_clamp_scroll(*, scroll_dict: dict, side: str, max_scroll: int) -> int:
    k = menu_scroll_key_for_side(side)
    try:
        cur = int(scroll_dict.get(k, 0) or 0)
    except Exception:
        cur = 0
    cur = int(max(0, min(int(cur), int(max_scroll))))
    try:
        scroll_dict[k] = int(cur)
    except Exception:
        pass
    return int(cur)


def build_sword_tiles(
    *,
    swords: list,
    swords_rect,
    cols: int,
    tile_w: int,
    tile_h: int,
    gap: int,
    cur_scroll: int,
    friendly_name_fn: Callable[[str], str],
    rect_factory: Callable[[int, int, int, int], object],
) -> list[dict]:
    tiles: list[dict] = []
    for i, st in enumerate(swords or []):
        r = int(i // max(1, int(cols)))
        c = int(i % max(1, int(cols)))
        x = int(swords_rect.x + c * (int(tile_w) + int(gap)))
        y = int(swords_rect.y + r * (int(tile_h) + int(gap)) - int(cur_scroll))
        rect = rect_factory(int(x), int(y), int(tile_w), int(tile_h))
        value = str(getattr(st, 'value', st) or '').strip().lower()
        nm = str(friendly_name_fn(value) or value)
        tiles.append({'rect': rect, 'value': value, 'name': nm, 'sword_type': st})
    return tiles


def sword_tile_at_from_layouts(*, pos, lay_a: dict, lay_b: dict) -> tuple[str, str] | None:
    try:
        x, y = int(pos[0]), int(pos[1])
    except Exception:
        return None
    p = (x, y)

    for side, lay in (('a', lay_a), ('b', lay_b)):
        try:
            sword_rect = lay.get('swords_rect')
            if sword_rect is None or (not sword_rect.collidepoint(p)):
                continue
            for t in (lay.get('tiles') or []):
                rr = t.get('rect')
                if rr is not None and rr.collidepoint(p) and sword_rect.colliderect(rr):
                    return (side, str(t.get('value', '') or ''))
        except Exception:
            continue
    return None
