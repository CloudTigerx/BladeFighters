#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

import pygame

from modules.asset_module.preflight import AssetPreflight
from modules.logging_module.logger import configure_logging, get_logger


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate asset preflight report")
    parser.add_argument("--root", required=True, help="Path to assets root (e.g., puzzleassets)")
    parser.add_argument("--out", default="assets_report.json", help="Report JSON output path")
    parser.add_argument("--log-level", default="INFO", help="Logging level")
    args = parser.parse_args()

    configure_logging(args.log_level)
    logger = get_logger("asset_report")

    pygame.init()

    preflight = AssetPreflight(asset_root=Path(args.root), logger=logger)
    report = preflight.run_checks()

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    logger.info(f"Asset report written to {out_path}")
    print(json.dumps({"ok": report.get("ok", False), "errors": len(report.get("errors", [])), "warnings": len(report.get("warnings", []))}))
    return 0 if report.get("ok", False) else 1


if __name__ == "__main__":
    raise SystemExit(main())

