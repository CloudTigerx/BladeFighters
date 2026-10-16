from swordfighting_new.mechanics.scoring import compute_chain_points, ScoringManager


def test_compute_chain_points_matches_example() -> None:
    # Example requirement: 4 blocks broken at 4x combo => 20 points.
    # With the implemented equation, pass index is 1-based and multiplier is (pass + 1).
    # So 4 blocks cleared on pass 4 => 4 * (4 + 1) = 20.
    total, per_pass = compute_chain_points([0, 0, 0, 4])
    assert total == 20
    assert per_pass == [0, 0, 0, 20]


def test_record_chain_accumulates_points_total() -> None:
    sm = ScoringManager()
    sm.player.record_chain(passes=2, total_cleared=5, per_pass=[2, 3], garbage_removed=0)
    # pass1: 2 * 2 = 4, pass2: 3 * 3 = 9
    assert sm.player.points_total == 13
    assert sm.player.last_chain_points == 13
