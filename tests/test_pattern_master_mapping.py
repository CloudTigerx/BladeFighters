from __future__ import annotations


def test_vertical_strike_fold_repeats_top4_rows() -> None:
    from swordfighting_new.attacks.garbage_pattern import SwordPattern

    # Pattern 6 rows high, 6 columns wide. Each row has a unique marker per column.
    # Row numbering is bottom-to-top in the data structure.
    pattern = []
    for r in range(6):
        pattern.append([f"r{r+1}c{c+1}" for c in range(6)])

    sp = SwordPattern(name="T", pattern=pattern)

    # Vertical sword in columns 5-6 (0-based cols 4-5), height 8.
    # Rows 1..6 map directly. Rows 7..8 repeat from 4th-from-top => rows 3..6 repeat.
    # So row7 -> pattern row3, row8 -> pattern row4.
    left_x = 4  # columns 5-6
    assert sp.get_strike_color(left_x, 0, 2, 8, 0, 0, is_horizontal=False) == "r1c5"
    assert sp.get_strike_color(left_x, 0, 2, 8, 0, 5, is_horizontal=False) == "r6c5"
    assert sp.get_strike_color(left_x, 0, 2, 8, 0, 6, is_horizontal=False) == "r3c5"
    assert sp.get_strike_color(left_x, 0, 2, 8, 0, 7, is_horizontal=False) == "r4c5"


def test_sprinkles_alternate_rows_1_and_2_within_turn_per_column() -> None:
    from swordfighting_new.attacks.attack_lifecycle import InboundAttackLifecycle
    from swordfighting_new.core.board import Board
    from swordfighting_new.pieces.piece import Block

    b = Board()
    lc = InboundAttackLifecycle(color_provider=lambda *_args: "x", board=b)

    # Three sprinkles in the same column and same turn.
    turn_id = 123
    x = 2
    ys = [9, 8, 7]  # bottom to top (higher y is lower on board)
    blocks = []
    for y in ys:
        blk = Block(color="red", is_garbage=False, is_strike=False, attack_state="sprinkle")
        blk.x = x
        blk.y = y
        blk.inbound_kind = "sprinkle"
        blk.inbound_turn_id = turn_id
        b.set_piece(x, y, blk)
        blocks.append(blk)

    # Bottom-most should be layer 1, then 2, then 3.
    assert lc._compute_sprinkle_layer(blocks[0]) == 1
    assert lc._compute_sprinkle_layer(blocks[1]) == 2
    assert lc._compute_sprinkle_layer(blocks[2]) == 3


def test_horizontal_strike_top_row_maps_to_pattern_columns() -> None:
    from swordfighting_new.attacks.garbage_pattern import SwordPattern

    # 4 rows tall, so horizontal length may exceed height.
    pattern = []
    for r in range(4):
        pattern.append([f"r{r+1}c{c+1}" for c in range(6)])
    sp = SwordPattern(name="T", pattern=pattern)

    # A 2-row horizontal sword: verify TOP row picks pattern col 1 (left-entry, CW)
    # and pattern col 6 (right-entry, CCW).
    rows = 2
    top_by = rows - 1  # block_y_offset is bottom-up

    # Left-entry, top row should map to column 1.
    c = sp.get_strike_color(
        x=0,
        y=0,
        strike_width=4,
        strike_height=rows,
        block_x_offset=0,
        block_y_offset=top_by,
        is_horizontal=True,
        from_right=False,
    )
    assert c.endswith("c1")

    # Right-entry, top row should map to column 6.
    c = sp.get_strike_color(
        x=0,
        y=0,
        strike_width=4,
        strike_height=rows,
        block_x_offset=0,
        block_y_offset=top_by,
        is_horizontal=True,
        from_right=True,
    )
    assert c.endswith("c6")


def test_horizontal_strike_length_overflow_repeats_columns_per_side() -> None:
    from swordfighting_new.attacks.garbage_pattern import SwordPattern

    # Height 6 so we can talk about columns 1..6 of the rotated pattern.
    pattern = []
    for r in range(6):
        pattern.append([f"r{r+1}c{c+1}" for c in range(6)])
    sp = SwordPattern(name="T", pattern=pattern)

    rows = 1
    by = rows - 1

    # Left-entry: once off>=H, repeats last 4 rotated columns (rows 3..6 in original)
    # which correspond to original rows 3..6 => r3..r6 at off=6..9.
    c6 = sp.get_strike_color(0, 0, 10, rows, 6, by, is_horizontal=True, from_right=False)
    c7 = sp.get_strike_color(0, 0, 10, rows, 7, by, is_horizontal=True, from_right=False)
    assert c6.startswith("r3")
    assert c7.startswith("r4")

    # Right-entry: once off>=H, repeats rotated columns 4..1 (reverse) => original rows 3..6 in reverse.
    c6 = sp.get_strike_color(0, 0, 10, rows, 6, by, is_horizontal=True, from_right=True)
    c7 = sp.get_strike_color(0, 0, 10, rows, 7, by, is_horizontal=True, from_right=True)
    assert c6.startswith("r3")
    assert c7.startswith("r4") or c7.startswith("r2")
