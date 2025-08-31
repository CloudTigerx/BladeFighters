"""debug.py - Lightweight opt-in debug logging helpers.

Enable by launching with environment variable:
  BF_DEBUG=1 python -m swordfighting_new.pygame_client

Optional env flags:
  BF_DEBUG=1            master switch
  BF_DEBUG_BOARD=1      include column height summaries after cascades
"""
from __future__ import annotations
import os, time

DEBUG_ENABLED = os.getenv("BF_DEBUG", "0") not in ("0", "", None)
BOARD_ENABLED = DEBUG_ENABLED and os.getenv("BF_DEBUG_BOARD", "0") not in ("0", "", None)

_t0 = time.time()

def _ts() -> str:
    return f"{(time.time()-_t0):6.3f}s"

def log(tag: str, msg: str):
    if DEBUG_ENABLED:
        print(f"[{_ts()}][{tag}] {msg}")

def board_heights(board) -> list[int]:  # for summaries
    heights = []
    for x in range(board.WIDTH):
        top = 0
        for y in range(board.HEIGHT):
            if board.get_piece(x, y) != board.EMPTY:
                top = y + 1
        heights.append(top)
    return heights

def log_board_heights(tag: str, board):
    if BOARD_ENABLED:
        h = board_heights(board)
        print(f"[{_ts()}][{tag}] heights={h}")

def find_floating_blocks(board):
    """Return list of (x,y) blocks that have at least one empty cell below them in same column.

    A valid settled column has the form [empties...][solids...]. Any EMPTY encountered *below* a solid
    indicates a cascade failure (floating block).
    """
    floaters = []
    for x in range(board.WIDTH):
        seen_solid = False
        for y in range(board.HEIGHT-1, -1, -1):  # bottom -> top
            cell = board.get_piece(x, y)
            if cell == board.EMPTY:
                if seen_solid:
                    # we have an empty below previously seen solid => floating above
                    # mark all solids above that empty as floaters (simpler: mark later when encountered)
                    pass
                continue
            # solid
            seen_solid = True
            # scan below for any empty
            for by in range(y+1, board.HEIGHT):
                if board.get_piece(x, by) == board.EMPTY:
                    floaters.append((x, y))
                    break
    return floaters

def assert_no_floaters(tag: str, board):
    if not DEBUG_ENABLED:
        return
    fl = find_floating_blocks(board)
    if fl:
        print(f"[{_ts()}][{tag}] FLOATERS count={len(fl)} sample={fl[:8]}")
