"""Additional breaker tests focused on stats, rectangles, and cohesion gravity."""
from swordfighting_new.core.board import Board
from swordfighting_new.mechanics.breaker import BreakerManager
from swordfighting_new.pieces.piece import Block


def _place(board: Board, placements):
    for x, y, block in placements:
        board.set_piece(x, y, block)


def test_rectangle_detection_and_stats():
    b = Board()
    # 2x2 red square above a red breaker neighbor so it all clears in one pass.
    # Layout (x from 4..5, y from 10..11) with breaker at (4,12) touching (4,11).
    _place(b, [
        (4, 12, Block("red", is_breaker=True)),
        (4, 11, Block("red")), (5, 11, Block("red")),
        (4, 10, Block("red")), (5, 10, Block("red")),
    ])
    bm = BreakerManager(b)
    cleared = bm.apply_breakers()
    assert cleared == 5, f"Expected breaker + 4 rectangle normals, got {cleared}"
    stats = bm.last_pass_stats
    assert stats is not None
    # One rectangle of size 4
    assert len(stats['rectangles']) == 1
    r = stats['rectangles'][0]
    assert r['width'] * r['height'] == 4
    assert stats['breaker_cleared'] == 1
    assert stats['normal_cleared'] == 4
    assert stats['sprinkles'] == 0


def test_chain_stats_consistency_multi_pass():
    b = Board()
    # Two separate vertical pairs that become adjacent only after first clears & cascade.
    _place(b, [
        (6, 15, Block("blue", is_breaker=True)), (6, 14, Block("blue")),
        (6, 7, Block("blue", is_breaker=True)), (6, 5, Block("blue")),
    ])
    bm = BreakerManager(b)
    chains, total, per_pass = bm.apply_breaker_chain()
    assert chains == 2
    assert total == sum(per_pass)
    # Inspect last_pass_stats reflects final pass; breaker_cleared should be 2 overall by summing passes.


def test_simple_rectangle_falls_step_mode():
    b = Board()
    # Create a 2x2 green square with empty space beneath so step cascade should move blocks down individually.
    _place(b, [
        (3, 5, Block("green")), (4, 5, Block("green")),
        (3, 4, Block("green")), (4, 4, Block("green")),
    ])
    bm = BreakerManager(b)
    # Perform one step cascade - only bottom blocks can fall in first step
    moved = bm.cascade_step(mode='step')
    # Only the bottom two blocks (at Y=5) can move down initially
    assert moved == 2, f"Expected 2 moves (bottom row only), got {moved}"
    # Verify bottom blocks moved down to Y=6, top blocks stayed at Y=4
    assert b.get_piece(3, 6) != b.EMPTY and getattr(b.get_piece(3, 6), 'color', None) == 'green'
    assert b.get_piece(4, 6) != b.EMPTY and getattr(b.get_piece(4, 6), 'color', None) == 'green'
    assert b.get_piece(3, 4) != b.EMPTY and getattr(b.get_piece(3, 4), 'color', None) == 'green'
    assert b.get_piece(4, 4) != b.EMPTY and getattr(b.get_piece(4, 4), 'color', None) == 'green'
    # Y=5 should now be empty
    assert b.get_piece(3, 5) == b.EMPTY
    assert b.get_piece(4, 5) == b.EMPTY


def test_garbage_barrier_no_overreach():
    b = Board()
    # Breaker should clear only itself + immediate red normal below; garbage blocks flood.
    _place(b, [
        (2, 10, Block("yellow", is_breaker=True)),
        (2, 9, Block("yellow")),
        (2, 8, Block("yellow", is_garbage=True)),
        (2, 7, Block("yellow")),  # isolated past garbage
    ])
    bm = BreakerManager(b)
    cleared = bm.apply_breakers()
    assert cleared == 2, f"Expected 2 cleared (breaker + one normal), got {cleared}"
    assert b.get_piece(2, 7) != b.EMPTY, "Cell beyond garbage incorrectly cleared"


def test_multiple_color_regions_same_pass():
    b = Board()
    _place(b, [
        (1, 10, Block("red", is_breaker=True)), (1, 9, Block("red")),
        (8, 12, Block("blue", is_breaker=True)), (9, 12, Block("blue")),
    ])
    bm = BreakerManager(b)
    cleared = bm.apply_breakers()
    assert cleared == 4
    stats = bm.last_pass_stats
    assert stats['breaker_cleared'] == 2 and stats['normal_cleared'] == 2


def test_fast_cascade_full_compression():
    b = Board()
    # Column with three separated blocks; fast mode now fully compresses column in a single step.
    _place(b, [
        (3, 5, Block("red")),
        (3, 3, Block("red")),
        (3, 1, Block("red")),
    ])
    bm = BreakerManager(b)
    before_positions = [y for y in range(b.HEIGHT) if b.get_piece(3, y) != b.EMPTY]
    moved = bm.cascade_step(mode='fast')
    after_positions = [y for y in range(b.HEIGHT) if b.get_piece(3, y) != b.EMPTY]
    # All three blocks should end up contiguous at bottom (y=21,22,23).
    assert moved == 3, f"Expected 3 moves (all blocks repositioned), got {moved}"
    assert after_positions == [b.HEIGHT - 3, b.HEIGHT - 2, b.HEIGHT - 1]
    assert len(before_positions) == len(after_positions) == 3
