import json
from pathlib import Path

import pygame

from modules.asset_module.preflight import AssetPreflight
from modules.logging_module.logger import configure_logging, get_logger


def _make_dummy_png(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    surf = pygame.Surface((4, 4))
    pygame.image.save(surf, str(path))


def test_preflight_ok(tmp_path, monkeypatch):
    pygame.init()
    assets = tmp_path / "puzzleassets"
    assets.mkdir()
    # image
    _make_dummy_png(assets / "puzzlebackground.png")
    # sounds dir exists but can be empty; we only validate size>0 if present
    (tmp_path / "sounds" / "effects").mkdir(parents=True, exist_ok=True)
    (tmp_path / "sounds" / "songs").mkdir(parents=True, exist_ok=True)
    # configs
    (tmp_path / "game_settings.json").write_text(json.dumps({}), encoding="utf-8")
    (tmp_path / "game_controls.json").write_text(json.dumps({}), encoding="utf-8")
    (tmp_path / "ui_positions.json").write_text(json.dumps({}), encoding="utf-8")
    (assets / "items_config.json").write_text(json.dumps({}), encoding="utf-8")
    # fonts optional
    (assets / "fonts").mkdir(parents=True, exist_ok=True)

    configure_logging("ERROR")
    logger = get_logger("test")
    preflight = AssetPreflight(asset_root=assets, logger=logger)
    report = preflight.run_checks()
    assert report["ok"] is True
    assert report["errors"] == []


def test_preflight_missing_file(tmp_path):
    pygame.init()
    assets = tmp_path / "puzzleassets"
    assets.mkdir()
    # Deliberately do not create images
    # configs missing
    configure_logging("ERROR")
    logger = get_logger("test")
    preflight = AssetPreflight(asset_root=assets, logger=logger)
    report = preflight.run_checks()
    assert report["ok"] is False
    assert any("Config missing" in e for e in report["errors"]) or any("parse" in e for e in report["errors"])  # robust


def test_preflight_bad_json(tmp_path):
    pygame.init()
    assets = tmp_path / "puzzleassets"
    assets.mkdir()
    # image ok
    _make_dummy_png(assets / "puzzlebackground.png")
    # bad json
    (tmp_path / "game_settings.json").write_text("{ bad json }", encoding="utf-8")
    (tmp_path / "game_controls.json").write_text(json.dumps({}), encoding="utf-8")
    (tmp_path / "ui_positions.json").write_text(json.dumps({}), encoding="utf-8")
    (assets / "items_config.json").write_text(json.dumps({}), encoding="utf-8")

    configure_logging("ERROR")
    logger = get_logger("test")
    preflight = AssetPreflight(asset_root=assets, logger=logger)
    report = preflight.run_checks()
    assert report["ok"] is False
    assert any("Config parse failed" in e for e in report["errors"]) 

