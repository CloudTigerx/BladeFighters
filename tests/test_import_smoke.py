from __future__ import annotations


def test_import_smoke() -> None:
    # Smoke imports to catch missing deps / stale references.
    import swordfighting_new  # noqa: F401

