"""Guard against accidentally importing a stale Trash copy of the project.

If this test fails with a path containing '.Trash', your PYTHONPATH / cwd
is pointed at an old copy. Run tests from the active workspace directory.
"""
import swordfighting_new.mechanics.breaker as breaker_mod


def test_not_trash_copy():
    assert '.Trash' not in breaker_mod.__file__, f"Imported stale copy: {breaker_mod.__file__}"
