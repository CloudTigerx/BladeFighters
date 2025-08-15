#!/usr/bin/env python3
import json
import os
from pathlib import Path
from typing import Dict, Iterable, List, Set, Tuple
from fnmatch import fnmatch

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None


REPO_ROOT = Path(__file__).resolve().parents[2]
BUILD_DIR = REPO_ROOT / "build" / "cleanup"


ASSET_ROOTS = [
    REPO_ROOT / "puzzleassets",
    REPO_ROOT / "sounds",
    REPO_ROOT / "stories",
    REPO_ROOT / "fonts",  # optional top-level
]


TEXT_FILE_EXTS = {".py", ".json", ".md", ".toml", ".yaml", ".yml", ".txt", ".cfg", ".ini", ".csv", ".sh", ".bat"}
ASSET_EXTS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".mp3",
    ".wav",
    ".ogg",
    ".txt",
    ".json",
    ".ttf",
    ".otf",
}

EXCLUDE_DIRS = {".git", ".venv", "venv", "build", "dist", "__pycache__"}


def list_assets() -> List[Path]:
    assets: List[Path] = []
    for root in ASSET_ROOTS:
        if not root.exists():
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
            for fname in filenames:
                p = Path(dirpath) / fname
                if p.suffix.lower() in ASSET_EXTS:
                    assets.append(p)
    return assets


def list_reference_files() -> List[Path]:
    refs: List[Path] = []
    for dirpath, dirnames, filenames in os.walk(REPO_ROOT):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS and d not in {"puzzleassets", "sounds", "stories"}]
        for fname in filenames:
            p = Path(dirpath) / fname
            if p.suffix.lower() in TEXT_FILE_EXTS:
                refs.append(p)
    return refs


def load_allowlist() -> Dict:
    path = REPO_ROOT / "tools/cleanup/allowlist.yaml"
    if not path.exists() or yaml is None:
        return {"assets": [], "comments_keep_marker": "KEEP:"}
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        assets = data.get("assets", []) or []
        marker = data.get("comments_keep_marker", "KEEP:")
        return {"assets": assets, "comments_keep_marker": str(marker)}
    except Exception:
        return {"assets": [], "comments_keep_marker": "KEEP:"}


def load_corpus(files: Iterable[Path]) -> Dict[Path, str]:
    contents: Dict[Path, str] = {}
    for f in files:
        try:
            contents[f] = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            contents[f] = ""
    return contents


def find_references(assets: List[Path], corpus: Dict[Path, str]) -> Dict[Path, Set[Path]]:
    refs: Dict[Path, Set[Path]] = {}
    allow = load_allowlist()
    asset_globs = [pat for pat in allow.get("assets", [])]
    for asset in assets:
        filename = asset.name
        stem = asset.stem
        rel = asset.relative_to(REPO_ROOT).as_posix()
        keys = {filename, stem, rel}
        found_in: Set[Path] = set()
        # Always consider allowlisted assets as referenced
        if any(fnmatch(rel, pat) for pat in asset_globs):
            refs[asset] = {REPO_ROOT / "tools/cleanup/allowlist.yaml"}
            continue
        for fpath, text in corpus.items():
            if any(key in text for key in keys):
                found_in.add(fpath)
        refs[asset] = found_in
    return refs


def include_known_configs_in_corpus(corpus: Dict[Path, str]) -> None:
    # Include specific config and atlas files if they exist
    candidates = [
        REPO_ROOT / "puzzleassets" / "items_config.json",
        REPO_ROOT / "atlas.json",
    ]
    for p in candidates:
        if p.exists() and p not in corpus:
            try:
                corpus[p] = p.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                corpus[p] = ""


def rank_orphan(asset: Path, referenced_by: Set[Path]) -> str:
    # Simple heuristic: if never referenced anywhere, High
    if not referenced_by:
        return "High"
    # Otherwise considered used, not orphan
    return "Used"


def main() -> int:
    BUILD_DIR.mkdir(parents=True, exist_ok=True)

    assets = list_assets()
    reference_files = list_reference_files()
    corpus = load_corpus(reference_files)
    include_known_configs_in_corpus(corpus)

    refs = find_references(assets, corpus)

    orphan_entries = []
    for asset, locations in refs.items():
        rank = rank_orphan(asset, locations)
        if rank == "High":
            rel = asset.relative_to(REPO_ROOT).as_posix()
            orphan_entries.append(
                {
                    "path": rel,
                    "size_bytes": asset.stat().st_size if asset.exists() else None,
                    "ext": asset.suffix.lower(),
                    "rank": "High",
                }
            )

    report = {
        "repo_root": str(REPO_ROOT),
        "assets_scanned": len(assets),
        "orphan_assets": sorted(orphan_entries, key=lambda x: (x["rank"], x["path"])),
    }

    out_json_path = BUILD_DIR / "orphan_assets.json"
    out_json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    # Pretty text output
    print("Orphan Assets Report")
    print("---------------------")
    print(f"Scanned assets: {len(assets)}")
    print(f"Potential orphans (High confidence): {len(orphan_entries)}")
    for entry in report["orphan_assets"][:100]:
        print(f"[High] {entry['path']} ({entry['size_bytes']} bytes)")
    if len(report["orphan_assets"]) > 100:
        print(f"... and {len(report['orphan_assets']) - 100} more")
    print(f"\nSaved JSON report to: {out_json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

