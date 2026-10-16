from __future__ import annotations

import os
import sys
from pathlib import Path


def runtime_root() -> Path:
    """Return the root directory for runtime resources.

    - Normal dev run: project root (folder containing `assets/`).
    - PyInstaller frozen app: extraction root (sys._MEIPASS).
    """
    try:
        if bool(getattr(sys, "frozen", False)) and hasattr(sys, "_MEIPASS"):
            return Path(getattr(sys, "_MEIPASS"))
    except Exception:
        pass

    # swordfighting_new/util/resources.py -> swordfighting_new -> project root
    try:
        return Path(__file__).resolve().parents[2]
    except Exception:
        return Path.cwd()


def assets_dir() -> Path:
    return runtime_root() / "assets"


def asset_path(*parts: str) -> str:
    """Return an OS-native path to an asset inside `assets/`."""
    return os.fspath(assets_dir().joinpath(*parts))
