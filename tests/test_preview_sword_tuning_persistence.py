from swordfighting_new.controllers.settings_controller import SettingsController
from swordfighting_new.save_system import SaveManager


class _DummyClient:
    def __init__(self) -> None:
        self._save_manager = SaveManager()
        self._preview_sword_scale = 1.0
        self._preview_sword_scale_by_weapon = {}


def test_preview_sword_tuning_persists_and_loads(tmp_path, monkeypatch):
    # Keep test isolated from the repo's real saves/save.json.
    monkeypatch.setenv("BF_SAVE_DIR", str(tmp_path))

    c1 = _DummyClient()
    c1._preview_sword_scale = 1.75
    c1._preview_sword_scale_by_weapon = {"rusty_sword": 1.25, "cutlass": 0.9}

    sc = SettingsController()
    sc.persist_preview_sword_tuning(c1)

    # New client + new SaveManager instance should read persisted values.
    c2 = _DummyClient()
    saved = sc.load_saved_preferences(c2)

    assert abs(float(saved.get("saved_preview_sword_scale")) - 1.75) < 1e-6
    per = saved.get("saved_preview_sword_scale_by_weapon")
    assert isinstance(per, dict)
    assert abs(float(per.get("rusty_sword")) - 1.25) < 1e-6
    assert abs(float(per.get("cutlass")) - 0.9) < 1e-6
