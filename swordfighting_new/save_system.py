from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Optional


SAVE_VERSION = 1


def _find_project_root() -> Path:
    """Best-effort workspace root discovery.

    We want saves to live alongside the project (not in site-packages).
    """
    current_dir = Path.cwd()
    temp = current_dir
    while temp != temp.parent:
        if (temp / "assets").exists() and (temp / "swordfighting_new").exists():
            return temp
        temp = temp.parent
    return current_dir


def _save_dir() -> Path:
    env = (os.getenv("BF_SAVE_DIR", "") or "").strip()
    if env:
        return Path(env)
    return _find_project_root() / "saves"


def _save_file() -> Path:
    return _save_dir() / "save.json"


@dataclass
class GameSettings:
    # Master game volume (0..1). Applies to SFX/music.
    game_volume: float = 0.65

    # Display preference: start in exclusive fullscreen when True.
    # Default is windowed for better dev/streaming ergonomics.
    fullscreen: bool = False

    # Horizontal movement key-hold auto-repeat interval in milliseconds.
    # Lower = faster repeated left/right movement.
    horizontal_move_repeat_ms: int = 70


class SaveManager:
    """Minimal save/load for 2D client.

    This keeps the existing `saves/save.json` location and schema (a top-level
    dict containing a `settings` object), but intentionally avoids any 3D-client
    specific character/profile concepts.
    """

    def __init__(self) -> None:
        self._cache: Optional[dict[str, Any]] = None

    def load(self) -> dict[str, Any]:
        path = _save_file()
        data: dict[str, Any]
        try:
            if not path.exists():
                data = {"version": SAVE_VERSION, "settings": asdict(GameSettings())}
            else:
                raw = path.read_text(encoding="utf-8")
                parsed = json.loads(raw)
                if not isinstance(parsed, dict):
                    raise ValueError("Save file root must be an object")
                data = dict(parsed)
        except Exception:
            data = {"version": SAVE_VERSION, "settings": asdict(GameSettings())}

        data.setdefault("version", SAVE_VERSION)
        if not isinstance(data.get("settings"), dict):
            data["settings"] = asdict(GameSettings())

        self._cache = data
        return dict(data)

    def save(self, data: dict[str, Any]) -> None:
        self._cache = dict(data)
        folder = _save_dir()
        folder.mkdir(parents=True, exist_ok=True)

        path = _save_file()
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self._cache, indent=2, sort_keys=True), encoding="utf-8")
        tmp.replace(path)

    def get_settings(self) -> GameSettings:
        data = self._cache or self.load()
        st = data.get("settings")
        if isinstance(st, dict):
            try:
                v = float(st.get("game_volume", GameSettings.game_volume))
                v = max(0.0, min(1.0, v))
                try:
                    rep = int(st.get("horizontal_move_repeat_ms", GameSettings.horizontal_move_repeat_ms))
                except Exception:
                    rep = int(GameSettings.horizontal_move_repeat_ms)
                rep = max(30, min(250, int(rep)))

                raw_fs = st.get("fullscreen", getattr(GameSettings, "fullscreen", False))
                if isinstance(raw_fs, str):
                    fs = raw_fs.strip().lower() not in ("", "0", "false", "no", "off")
                else:
                    fs = bool(raw_fs)

                return GameSettings(game_volume=float(v), horizontal_move_repeat_ms=int(rep), fullscreen=bool(fs))
            except Exception:
                pass
        return GameSettings()

    def set_settings(self, settings: GameSettings) -> None:
        data = self._cache or self.load()
        try:
            v = float(getattr(settings, "game_volume", GameSettings.game_volume))
        except Exception:
            v = GameSettings.game_volume
        v = max(0.0, min(1.0, float(v)))

        try:
            rep = int(getattr(settings, "horizontal_move_repeat_ms", GameSettings.horizontal_move_repeat_ms))
        except Exception:
            rep = int(GameSettings.horizontal_move_repeat_ms)
        rep = max(30, min(250, int(rep)))

        try:
            fs = bool(getattr(settings, "fullscreen", getattr(GameSettings, "fullscreen", False)))
        except Exception:
            fs = bool(getattr(GameSettings, "fullscreen", False))

        data["settings"] = asdict(GameSettings(game_volume=float(v), horizontal_move_repeat_ms=int(rep), fullscreen=bool(fs)))
        self.save(data)
