from swordfighting_new.mechanics.timing import DEFAULT_TIMING
from swordfighting_new.pieces.piece import Block
from swordfighting_new.strike_test_harness import StrikeTestHarness


def _place_2x2(h: StrikeTestHarness) -> None:
    # Place a 2x2 block rectangle near the bottom of the input board.
    for x in (0, 1):
        for y in (h.input_board.HEIGHT - 2, h.input_board.HEIGHT - 1):
            h.input_board.set_piece(x, y, Block('red', is_breaker=False))


def _place_3x2(h: StrikeTestHarness) -> None:
    # Place a 3x2 block rectangle near the bottom of the input board.
    for x in (0, 1, 2):
        for y in (h.input_board.HEIGHT - 2, h.input_board.HEIGHT - 1):
            h.input_board.set_piece(x, y, Block('red', is_breaker=False))


def _strike_cells(h: StrikeTestHarness) -> list[tuple[int, int]]:
    out = []
    for x in range(h.output_board.WIDTH):
        for y in range(h.output_board.HEIGHT):
            b = h.output_board.get_piece(x, y)
            if b in (None, h.output_board.EMPTY):
                continue
            if getattr(b, 'attack_state', None) == 'strike':
                out.append((int(x), int(y)))
    return out


def test_strike_test_harness_chain_scaling_2x2() -> None:
    h = StrikeTestHarness(DEFAULT_TIMING)
    _place_2x2(h)

    attacks = h.run_once(chain_len=2)
    assert attacks and attacks[0].meta.get('sword_shape') == (2, 4)

    # Force immediate inbound delivery and settle.
    h.output_inbound.inbound_delay = 0
    h.settle(max_frames=1200)

    cells = _strike_cells(h)
    assert len(cells) == 8
    minx = min(x for x, _y in cells)
    maxx = max(x for x, _y in cells)
    miny = min(y for _x, y in cells)
    maxy = max(y for _x, y in cells)
    assert (maxx - minx + 1) == 2
    assert (maxy - miny + 1) == 4


def test_strike_test_harness_chain_1_is_baseline_2x2() -> None:
    h = StrikeTestHarness(DEFAULT_TIMING)
    _place_2x2(h)

    attacks = h.run_once(chain_len=1)
    assert attacks and attacks[0].meta.get('sword_shape') == (2, 2)

    h.output_inbound.inbound_delay = 0
    h.settle(max_frames=1200)

    cells = _strike_cells(h)
    assert len(cells) == 4
    minx = min(x for x, _y in cells)
    maxx = max(x for x, _y in cells)
    miny = min(y for _x, y in cells)
    maxy = max(y for _x, y in cells)
    assert (maxx - minx + 1) == 2
    assert (maxy - miny + 1) == 2


def test_strike_test_harness_3x2_chain_3_converts_to_vertical_2x6() -> None:
    h = StrikeTestHarness(DEFAULT_TIMING)
    _place_3x2(h)

    attacks = h.run_once(chain_len=3)
    assert attacks and attacks[0].meta.get('sword_shape') == (2, 6)
    assert attacks[0].meta.get('orientation') == 'vertical'

    h.output_inbound.inbound_delay = 0
    h.settle(max_frames=1400)

    cells = _strike_cells(h)
    assert len(cells) == 12
    minx = min(x for x, _y in cells)
    maxx = max(x for x, _y in cells)
    miny = min(y for _x, y in cells)
    maxy = max(y for _x, y in cells)
    assert (maxx - minx + 1) == 2
    assert (maxy - miny + 1) == 6


def test_strike_test_harness_live_chain_two_2x2_rectangles_one_pass() -> None:
    h = StrikeTestHarness(DEFAULT_TIMING)

    # Two separate 2x2 clusters on the bottom rows.
    for x in (0, 1):
        for y in (h.input_board.HEIGHT - 2, h.input_board.HEIGHT - 1):
            h.input_board.set_piece(x, y, Block('red', is_breaker=False))
    for x in (4, 5):
        for y in (h.input_board.HEIGHT - 2, h.input_board.HEIGHT - 1):
            h.input_board.set_piece(x, y, Block('red', is_breaker=False))

    # A breaker adjacent to each cluster so both trigger in the same pass.
    h.input_board.set_piece(0, h.input_board.HEIGHT - 3, Block('red', is_breaker=True))
    h.input_board.set_piece(4, h.input_board.HEIGHT - 3, Block('red', is_breaker=True))

    attacks = h.run_live(max_chain_frames=2400)
    assert int(getattr(h, 'last_live_chain_passes', 0) or 0) >= 1
    assert len(attacks) == 2
    shapes = []
    for a in attacks:
        meta = dict(getattr(a, 'meta', None) or {})
        shapes.append(tuple(meta.get('sword_shape') or meta.get('horizontal_sword_shape') or ()))
    assert sorted(shapes) == [(2, 2), (2, 2)]
