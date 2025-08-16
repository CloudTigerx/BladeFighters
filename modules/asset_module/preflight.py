"""
Asset Preflight - Validates game assets before startup
Provides comprehensive asset validation and reporting.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any

import pygame
from ..logging_module.error_handler import (
    safe_operation
)
from ..logging_module.logger import get_logger

logger = get_logger(__name__)


class AssetPreflight:
    """
    Validates game assets before startup to catch issues early.
    Checks images, sounds, configs, and fonts for validity.
    """

    def __init__(self, asset_root: Path, logger=None):
        self.asset_root = Path(asset_root)
        self.logger = logger or get_logger(__name__)
        self.config_root = self.asset_root.parent

    def run_checks(self) -> Dict[str, Any]:
        """Run comprehensive asset validation checks."""
        errors: List[str] = []
        warnings: List[str] = []

        counts = {
            "images_checked": 0,
            "sounds_checked": 0,
            "configs_checked": 0,
            "fonts_checked": 0,
            "orphan_assets_reported": 0,
        }

        # Ensure pygame is initialized enough for image loading
        self._initialize_pygame()

        # 1) Sprites exist and are loadable
        image_paths = self._collect_image_paths()
        for img_path in image_paths:
            counts["images_checked"] += 1
            self._check_image_load(img_path, errors)

        # 2) Sounds/music exist and are loadable (best-effort without mixer init)
        sound_paths = self._collect_sound_paths()
        for snd_path in sound_paths:
            counts["sounds_checked"] += 1
            self._check_sound_file(snd_path, errors)

        # 3) Config JSON files parse
        config_files = [
            self.config_root / "game_settings.json",
            self.config_root / "game_controls.json",
            self.config_root / "ui_positions.json",
            self.config_root / "puzzleassets/items_config.json",
        ]
        for cfg in config_files:
            counts["configs_checked"] += 1
            self._check_config_file(cfg, errors)

        # 4) Optional: fonts exist and can be opened
        self._check_fonts(counts, warnings)

        ok = len(errors) == 0
        report: Dict[str, Any] = {
            "ok": ok,
            "errors": errors,
            "warnings": warnings,
            "counts": counts,
        }

        # 5) Optional: include orphan asset count from cleanup report (non-fatal)
        self._check_orphan_assets(counts, warnings)

        return report

    @safe_operation("initialize pygame", None, "WARNING")
    def _initialize_pygame(self) -> None:
        """Initialize pygame for asset loading."""
        try:
            if not pygame.get_init():
                pygame.init()
        except Exception as e:
            self.logger.warning(f"Failed to initialize pygame: {str(e)}")

    @safe_operation("check image load", None, "WARNING")
    def _check_image_load(self, img_path: Path, errors: List[str]) -> None:
        """Check if an image can be loaded."""
        try:
            pygame.image.load(str(img_path))
        except Exception as e:
            errors.append(f"Image load failed: {img_path} ({e})")

    @safe_operation("check sound file", None, "WARNING")
    def _check_sound_file(self, snd_path: Path, errors: List[str]) -> None:
        """Check if a sound file is valid."""
        try:
            # Only check file exists and non-zero size; mixer may be unavailable in CI
            if not snd_path.exists() or snd_path.stat().st_size <= 0:
                errors.append(f"Sound invalid: {snd_path}")
        except Exception as e:
            errors.append(f"Sound check failed: {snd_path} ({e})")

    @safe_operation("check config file", None, "WARNING")
    def _check_config_file(self, cfg: Path, errors: List[str]) -> None:
        """Check if a config file can be parsed."""
        try:
            with open(str(cfg), "r", encoding="utf-8") as f:
                json.load(f)
        except FileNotFoundError:
            errors.append(f"Config missing: {cfg}")
        except Exception as e:
            errors.append(f"Config parse failed: {cfg} ({e})")

    @safe_operation("check fonts", None, "WARNING")
    def _check_fonts(self, counts: Dict[str, int], warnings: List[str]) -> None:
        """Check if fonts can be loaded."""
        fonts_dir = self.asset_root / "fonts"
        if fonts_dir.exists():
            for font_file in fonts_dir.glob("*.ttf"):
                counts["fonts_checked"] += 1
                try:
                    pygame.font.Font(str(font_file), 12)
                except Exception as e:
                    warnings.append(f"Font open failed: {font_file} ({e})")
        else:
            warnings.append(f"Fonts directory missing: {fonts_dir}")

    @safe_operation("check orphan assets", None, "WARNING")
    def _check_orphan_assets(self, counts: Dict[str, int], warnings: List[str]) -> None:
        """Check for orphan asset reports."""
        try:
            orphan_report = self.config_root / "build/cleanup/orphan_assets.json"
            if orphan_report.exists():
                data = json.loads(orphan_report.read_text(encoding="utf-8", errors="ignore"))
                orphan_list = data.get("orphan_assets", [])
                counts["orphan_assets_reported"] = len(orphan_list)
                if orphan_list:
                    sample = ", ".join(i.get("path", "?") for i in orphan_list[:10])
                    self.logger.info(
                        "AssetPreflight: %d orphan assets reported (sample: %s)",
                        len(orphan_list),
                        sample,
                    )
        except Exception as e:
            warnings.append(f"Orphan asset report read failed: {e}")

    def _collect_image_paths(self) -> List[Path]:
        """Collect all image file paths."""
        image_exts = {".png", ".jpg", ".jpeg"}
        paths: List[Path] = []
        if not self.asset_root.exists():
            return paths
        for root, _dirs, files in os.walk(self.asset_root):
            for f in files:
                p = Path(root) / f
                if p.suffix.lower() in image_exts:
                    paths.append(p)
        return paths

    def _collect_sound_paths(self) -> List[Path]:
        """Collect all sound file paths."""
        paths: List[Path] = []
        for sub in [self.asset_root.parent / "sounds/effects", self.asset_root.parent / "sounds/songs"]:
            if sub.exists():
                for root, _dirs, files in os.walk(sub):
                    for f in files:
                        paths.append(Path(root) / f)
        return paths

