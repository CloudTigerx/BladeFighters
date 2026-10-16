import pytest


class _TimingStub:
    target_fps = 60
    autonomous_fall_interval_frames = 6


def _find_inbound_attack_handler():
    from swordfighting_new.fighters.inbound_attack_handler import InboundAttackHandler

    return InboundAttackHandler


def _find_board_class():
    from swordfighting_new.core.board import Board

    return Board


@pytest.mark.unit
def test_vertical_strike_clusters_spawned_same_frame_have_distinct_ids():
    """Multiple vertical strike clusters spawned in the same frame must not share an id.

    If they share a `strike_cluster_id`, the inbound fall update will group them and treat
    separate swords as one rigid cluster, which is both inaccurate and unfair.
    """

    Board = _find_board_class()
    InboundAttackHandler = _find_inbound_attack_handler()

    board = Board()
    handler = InboundAttackHandler(
        board=board,
        timing=_TimingStub(),
        piece_mover=None,
        gravity_manager=None,
    )

    handler.set_frame(123)

    # Spawn two separate 1x2 strike clusters in the same frame.
    handler._spawn_strike_cluster_at(left=0, width=1, height=2)
    handler._spawn_strike_cluster_at(left=4, width=1, height=2)

    ids = []
    for p in handler.garbage_fallers:
        cid = getattr(p, "strike_cluster_id", None)
        if cid is not None:
            ids.append(int(cid))

    # We expect at least two distinct ids (one per cluster).
    assert len(set(ids)) >= 2


@pytest.mark.unit
def test_three_2wide_vertical_swords_pack_into_three_column_pairs_on_6wide_board():
    """Three 2-wide vertical swords arriving the same tick should not stack.

    On the default 6-wide board, the expected non-overlapping packing is the three
    column pairs: (0,1), (2,3), (4,5). A previous placement strategy could pick
    (1,2) and (4,5) first (due to spawn-column avoidance/rotation), leaving no
    room for the third sword and forcing a delayed spawn that could overlap.
    """

    from swordfighting_new.core.board import Board
    from swordfighting_new.fighters.inbound_attack_handler import InboundAttackHandler

    board = Board()
    assert int(board.WIDTH) == 6

    handler = InboundAttackHandler(
        board=board,
        timing=_TimingStub(),
        piece_mover=None,
        gravity_manager=None,
    )

    # Choose a frame that previously deterministically rotated to pick left=1 then left=4,
    # which made the 3rd sword impossible to place without delay.
    handler.set_frame(6)

    # Three vertical swords: width=2, height=6.
    handler._pending_in_strike_clusters = [
        ('sword', (2, 6)),
        ('sword', (2, 6)),
        ('sword', (2, 6)),
    ]

    class _DummyHorizontalSwords:
        def spawn_horizontal_sword(self, rows, length, frame=0):
            return

    reserved_cols = handler._spawn_multiple_strike_clusters(_DummyHorizontalSwords())

    # Nothing should be delayed; all three should fit simultaneously.
    assert len(getattr(handler, '_delayed_clusters', []) or []) == 0

    # Group fallers by strike_cluster_id -> each should occupy exactly 2 columns.
    by_id: dict[int, list[int]] = {}
    for p in handler.garbage_fallers:
        cid = int(getattr(p, 'strike_cluster_id'))
        by_id.setdefault(cid, []).append(int(getattr(p, 'x')))

    assert len(by_id) == 3

    lefts = set()
    all_cols = set()
    for cid, xs in by_id.items():
        cols = set(xs)
        assert len(cols) == 2
        left = min(cols)
        assert cols == {left, left + 1}
        lefts.add(left)
        all_cols.update(cols)

    assert lefts == {0, 2, 4}
    assert all_cols == set(range(6))
    assert set(reserved_cols) == set(range(6))
