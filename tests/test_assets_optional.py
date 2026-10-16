from __future__ import annotations

from pathlib import Path

import pytest


def test_optional_chi_girl_glb_exists() -> None:
    glb = Path("assets/characters/chi_girl/Anime_character.glb")
    if not glb.exists():
        pytest.skip("Optional asset missing: assets/characters/chi_girl/Anime_character.glb")
