#!/usr/bin/env python3
import argparse
import datetime as _dt
import json
import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple


REPO_ROOT = Path(__file__).resolve().parents[2]
BUILD_DIR = REPO_ROOT / "build" / "cleanup"
GRAVEYARD_ROOT = REPO_ROOT / "graveyard"


def load_json(path: Path) -> Optional[dict]:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def rank_order_value(rank: str) -> int:
    table = {"High": 3, "Medium": 2, "Low": 1}
    return table.get(rank, 0)


def select_orphan_assets(orphan_report: dict, min_rank: str) -> List[dict]:
    if not orphan_report:
        return []
    threshold = rank_order_value(min_rank)
    items: List[dict] = []
    for entry in orphan_report.get("orphan_assets", []):
        if rank_order_value(entry.get("rank", "")) >= threshold:
            items.append(entry)
    return items


def select_dead_code_files(dead_code_report: dict, min_rank: str) -> List[Tuple[str, str]]:
    # Very conservative: only consider Vulture "High" items and move whole files
    # But only if the entire file is a standalone module (not a core reactor file)
    if not dead_code_report:
        return []
    threshold = rank_order_value(min_rank)
    files: Dict[str, str] = {}
    vulture = dead_code_report.get("vulture", {})
    for item in vulture.get("items", []):
        if rank_order_value(item.get("rank", "")) >= threshold:
            rel_file = item.get("file")
            if not rel_file:
                continue
            # Skip reactor files per policy
            if rel_file in ("core/puzzle_module.py", "modules/attack_module/attack_calculator.py"):
                continue
            files[rel_file] = "vulture-high"
    # Return unique files with reason
    return [(f, reason) for f, reason in files.items()]


def select_dead_fixtures(unused_tests_report: dict, min_rank: str) -> List[dict]:
    # Dead fixtures are High, but we do not move code lines; just record in tombstones
    if not unused_tests_report:
        return []
    return unused_tests_report.get("dead_fixtures", [])


def ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def move_preserving_tree(rel_path: str, batch_root: Path) -> Tuple[Path, Path]:
    src = REPO_ROOT / rel_path
    dst = batch_root / rel_path
    ensure_parent_dir(dst)
    shutil.move(str(src), str(dst))
    return src, dst


def write_tombstones(batch_root: Path, moves: List[Tuple[str, str]], assets: List[dict], dead_fixtures: List[dict]) -> None:
    tomb = batch_root / "TOMBSTONES.md"
    lines: List[str] = []
    lines.append("Quarantined items")
    lines.append("")
    lines.append("This directory is a quarantine for suspected dead code/assets. Items here should be reviewed; if CI stays green and usage is confirmed absent, they may be deleted in a follow-up PR.")
    lines.append("")

    if assets:
        lines.append("Assets moved (High confidence)")
        for a in assets:
            lines.append(f"- {a['path']} (reason: orphan asset, rank={a.get('rank')})")
        lines.append("")

    if moves:
        lines.append("Code files moved (High confidence)")
        for rel, reason in moves:
            lines.append(f"- {rel} (reason: {reason})")
        lines.append("")

    if dead_fixtures:
        lines.append("Dead fixtures (not moved)")
        for fx in dead_fixtures:
            lines.append(f"- {fx.get('file')}::{fx.get('fixture')}")
        lines.append("")

    tomb.write_text("\n".join(lines), encoding="utf-8")


def write_manifest_and_revert(batch_root: Path, moved_paths: List[Tuple[str, str]]) -> None:
    # moved_paths: list of (relpath, reason)
    manifest = {
        "moved": [
            {
                "original": rel,
                "graveyard": (batch_root / rel).relative_to(batch_root).as_posix(),
                "reason": reason,
            }
            for rel, reason in moved_paths
        ]
    }
    (batch_root / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    revert_py = batch_root / "revert.py"
    revert_py.write_text(
        """#!/usr/bin/env python3
import json
import shutil
from pathlib import Path

here = Path(__file__).resolve().parent
repo_root = here.parents[1]
manifest = json.loads((here / 'manifest.json').read_text(encoding='utf-8'))

for item in manifest.get('moved', []):
    rel = item['original']
    src = here / item['graveyard']
    dst = repo_root / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.exists():
        print(f'Restoring {rel}')
        shutil.move(str(src), str(dst))
    else:
        print(f'Source missing (already restored?): {src}')
""",
        encoding="utf-8",
    )
    os.chmod(revert_py, 0o755)


def main() -> int:
    parser = argparse.ArgumentParser(description="Quarantine suspected dead code/assets.")
    parser.add_argument("--apply", action="store_true", help="Perform moves instead of dry run")
    parser.add_argument("--keep-tests", action="store_true", help="Do not move any test files (always respected)")
    parser.add_argument("--min-rank", default="High", choices=["High", "Medium", "Low"], help="Minimum confidence to consider")
    args = parser.parse_args()

    dead_code = load_json(BUILD_DIR / "dead_code.json") or {}
    orphan_assets = load_json(BUILD_DIR / "orphan_assets.json") or {}
    unused_tests = load_json(BUILD_DIR / "unused_tests.json") or {}

    assets_to_move = select_orphan_assets(orphan_assets, args.min_rank)
    code_files_to_move = select_dead_code_files(dead_code, args.min_rank)

    timestamp = _dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    batch_root = GRAVEYARD_ROOT / timestamp

    planned_moves: List[Tuple[str, str]] = []  # (relpath, reason)
    for a in assets_to_move:
        planned_moves.append((a["path"], "orphan-asset"))
    for rel, reason in code_files_to_move:
        # Skip tests if requested
        if args.keep_tests and (rel.startswith("tests/") or "/tests/" in rel):
            continue
        planned_moves.append((rel, reason))

    if not planned_moves:
        print("No items to quarantine for the selected rank.")
        return 0

    print(f"Quarantine batch: {batch_root.relative_to(REPO_ROOT)}")
    for rel, reason in planned_moves:
        print(f"- {rel} ({reason})")

    if not args.apply:
        print("Dry run complete. Use --apply to perform the moves.")
        return 0

    # Apply moves
    batch_root.mkdir(parents=True, exist_ok=True)
    actually_moved: List[Tuple[str, str]] = []
    for rel, reason in planned_moves:
        src = REPO_ROOT / rel
        if not src.exists():
            print(f"Skip (missing): {rel}")
            continue
        move_preserving_tree(rel, batch_root)
        actually_moved.append((rel, reason))

    # Tombstones and revert
    write_tombstones(batch_root, actually_moved, assets_to_move, select_dead_fixtures(unused_tests, args.min_rank))
    write_manifest_and_revert(batch_root, actually_moved)

    print(f"Moved {len(actually_moved)} items to {batch_root.relative_to(REPO_ROOT)}")
    print(f"Revert script: {batch_root.relative_to(REPO_ROOT)}/revert.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

