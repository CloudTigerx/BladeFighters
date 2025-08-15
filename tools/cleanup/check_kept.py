#!/usr/bin/env python3
"""
Fail CI if any allowlisted modules/assets are present in the build quarantine plan
or if a file containing the keep marker was selected for quarantine.
"""
import json
from fnmatch import fnmatch
from pathlib import Path

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None

REPO_ROOT = Path(__file__).resolve().parents[2]
BUILD_DIR = REPO_ROOT / "build" / "cleanup"


def main() -> int:
    allow_path = REPO_ROOT / "tools/cleanup/allowlist.yaml"
    allow = {"assets": [], "modules": [], "comments_keep_marker": "KEEP:"}
    if allow_path.exists() and yaml is not None:
        allow = yaml.safe_load(allow_path.read_text(encoding="utf-8")) or allow

    marker = allow.get("comments_keep_marker", "KEEP:")
    asset_globs = allow.get("assets", []) or []
    module_globs = [m.replace(".", "/") for m in (allow.get("modules", []) or [])]

    # We only have executed quarantine actions; instead, check if any selected in manifest would violate allowlist
    violations = []
    # Look for latest graveyard batch manifest
    grave = REPO_ROOT / "graveyard"
    if grave.exists():
        batches = sorted([p for p in grave.iterdir() if p.is_dir()])
        if batches:
            latest = batches[-1]
            manifest = latest / "manifest.json"
            if manifest.exists():
                data = json.loads(manifest.read_text(encoding="utf-8"))
                for item in data.get("moved", []):
                    rel = item.get("original", "")
                    if any(fnmatch(rel, pat) for pat in asset_globs):
                        violations.append(f"Asset allowlisted but quarantined: {rel}")
                    if any(rel.startswith(glob + "/") or fnmatch(rel, glob + ".py") for glob in module_globs):
                        violations.append(f"Module allowlisted but quarantined: {rel}")
                    # keep marker check
                    src_path = REPO_ROOT / rel
                    if src_path.exists():
                        try:
                            src = src_path.read_text(encoding="utf-8", errors="ignore")
                            if marker and marker in src:
                                violations.append(f"Keep-marked file was quarantined: {rel}")
                        except Exception:
                            pass

    if violations:
        print("\n".join(violations))
        return 1
    print("No allowlist/keep-marker violations detected.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

