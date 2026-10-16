from swordfighting_new.controllers.settings_controller import SettingsController
from swordfighting_new.save_system import SaveManager
import pytest


class _DummyClient:
    def __init__(self) -> None:
        self._save_manager = SaveManager()
        self._coin_panel_size_override = {}
        self._coin_panel_size_override_frac = {}


def test_coin_panel_size_override_persists_and_loads(tmp_path, monkeypatch):
    monkeypatch.setenv("BF_SAVE_DIR", str(tmp_path))

    c1 = _DummyClient()
    c1._coin_panel_size_override = {"hud": (420, 90), "menu": (360, 72), "story": (500, 120)}
    c1._coin_panel_size_override_frac = {"hud": (0.25, 0.10), "menu": (0.20, 0.08), "story": (0.30, 0.14)}

    sc = SettingsController()
    sc.persist_coin_panel_size_override(c1)

    c2 = _DummyClient()
    saved = sc.load_saved_preferences(c2)

    raw = saved.get("saved_coin_panel_size_override")
    assert isinstance(raw, dict)
    assert list(raw["hud"]) == [420, 90]
    assert list(raw["menu"]) == [360, 72]
    assert list(raw["story"]) == [500, 120]

    raw_f = saved.get("saved_coin_panel_size_override_frac")
    assert isinstance(raw_f, dict)
    assert raw_f["hud"][0] == pytest.approx(0.25)
    assert raw_f["hud"][1] == pytest.approx(0.10)
    assert raw_f["menu"][0] == pytest.approx(0.20)
    assert raw_f["menu"][1] == pytest.approx(0.08)
    assert raw_f["story"][0] == pytest.approx(0.30)
    assert raw_f["story"][1] == pytest.approx(0.14)
