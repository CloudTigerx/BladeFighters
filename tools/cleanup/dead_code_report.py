#!/usr/bin/env python3
import ast
import json
import os
import re
import shutil
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from fnmatch import fnmatch

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None


REPO_ROOT = Path(__file__).resolve().parents[2]
BUILD_DIR = REPO_ROOT / "build" / "cleanup"


PY_EXCLUDE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "build",
    "dist",
    "__pycache__",
}

TEST_DIR_HINTS = {"tests", "test", "tests_unit", "tests_integration"}


def is_test_path(path: Path) -> bool:
    parts = set(path.parts)
    if path.name.startswith("test_") or path.name.endswith("_test.py"):
        return True
    return any(h in parts for h in TEST_DIR_HINTS)


def iter_python_files(root: Path) -> List[Path]:
    files: List[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        # prune excluded dirs in-place for performance
        dirnames[:] = [d for d in dirnames if d not in PY_EXCLUDE_DIRS]
        for fname in filenames:
            if not fname.endswith(".py"):
                continue
            files.append(Path(dirpath) / fname)
    return files


class ModuleInfo(ast.NodeVisitor):
    def __init__(self, module_path: Path) -> None:
        self.module_path = module_path
        self.defined_functions: Set[str] = set()
        self.defined_classes: Set[str] = set()
        self.defined_constants: Set[str] = set()
        self.read_names: Set[str] = set()
        self.imports: Set[str] = set()
        self.errors: Optional[str] = None

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        if isinstance(getattr(node, "parent", None), ast.Module):
            self.defined_functions.add(node.name)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        if isinstance(getattr(node, "parent", None), ast.Module):
            self.defined_functions.add(node.name)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        if isinstance(getattr(node, "parent", None), ast.Module):
            self.defined_classes.add(node.name)
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        if isinstance(getattr(node, "parent", None), ast.Module):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id.isupper():
                    self.defined_constants.add(target.id)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if isinstance(getattr(node, "parent", None), ast.Module):
            target = node.target
            if isinstance(target, ast.Name) and target.id.isupper():
                self.defined_constants.add(target.id)
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        if isinstance(node.ctx, ast.Load):
            self.read_names.add(node.id)
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            if alias.name:
                self.imports.add(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        # record the module being imported from, e.g. package.sub
        if node.module:
            self.imports.add(node.module)
        self.generic_visit(node)


def add_parents(tree: ast.AST) -> None:
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            setattr(child, "parent", parent)


def analyze_module(path: Path) -> ModuleInfo:
    info = ModuleInfo(path)
    try:
        src = path.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(src, filename=str(path))
        add_parents(tree)
        info.visit(tree)
    except Exception as exc:  # pragma: no cover - best-effort
        info.errors = f"{type(exc).__name__}: {exc}"
    return info


def to_module_name(repo_root: Path, path: Path) -> str:
    rel = path.relative_to(repo_root)
    mod = ".".join(rel.with_suffix("").parts)
    return mod


def should_exclude_module_from_never_imported(mod_path: Path) -> bool:
    rel = mod_path.relative_to(REPO_ROOT)
    if rel.name == "__init__.py":
        return True
    parts = rel.parts
    if parts and parts[0] in ("tools",):
        return True
    if is_test_path(rel):
        return True
    if rel.as_posix() in ("main.py", "game_client.py"):
        return True
    return False


def run_vulture(repo_root: Path) -> Dict:
    if shutil.which("vulture") is None:
        return {"available": False, "items": []}

    cmd = [
        "vulture",
        str(repo_root),
        "--min-confidence",
        "60",
        "--sort-by-size",
    ]
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(repo_root),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
    except Exception as exc:  # pragma: no cover
        return {"available": False, "error": str(exc), "items": []}

    output = proc.stdout.strip()
    items = []
    # Typical line: path:line: message (confidence x%)
    line_re = re.compile(r"^(.*?):(\d+):\s*(.*?)(?:\s*\(confidence\s*(\d+)%\))?$")
    for line in output.splitlines():
        m = line_re.match(line.strip())
        if not m:
            continue
        fpath, lno, msg, conf = m.groups()
        confidence = int(conf) if conf else None
        severity = (
            "High" if confidence is not None and confidence >= 90 else
            "Medium" if confidence is not None and confidence >= 70 else
            "Low"
        )
        items.append(
            {
                "file": os.path.relpath(fpath, str(repo_root)),
                "line": int(lno),
                "message": msg,
                "confidence": confidence,
                "rank": severity,
            }
        )
    return {"available": True, "items": items, "raw_stdout": output, "raw_stderr": proc.stderr}


def load_allowlist(repo_root: Path) -> Dict:
    path = repo_root / "tools/cleanup/allowlist.yaml"
    if not path.exists() or yaml is None:
        return {"modules": [], "assets": [], "comments_keep_marker": "KEEP:"}
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        modules = data.get("modules", []) or []
        assets = data.get("assets", []) or []
        marker = data.get("comments_keep_marker", "KEEP:")
        return {"modules": modules, "assets": assets, "comments_keep_marker": str(marker)}
    except Exception:
        return {"modules": [], "assets": [], "comments_keep_marker": "KEEP:"}


def dotted_to_path_glob(pattern: str) -> str:
    # Convert dotted module globs to path-like globs
    return pattern.replace(".", "/")


def load_top_level_json_keys(repo_root: Path) -> Dict[str, Set[str]]:
    keys: Dict[str, Set[str]] = {}
    candidates = [
        repo_root / "game_settings.json",
        repo_root / "game_controls.json",
        repo_root / "ui_positions.json",
    ]
    for p in candidates:
        if p.exists():
            try:
                data = json.loads(p.read_text(encoding="utf-8", errors="ignore"))
                if isinstance(data, dict):
                    keys[p.name] = set(map(str, data.keys()))
            except Exception:
                pass
    return keys


def main() -> int:
    BUILD_DIR.mkdir(parents=True, exist_ok=True)

    py_files = iter_python_files(REPO_ROOT)

    # Analyze all python files
    module_infos: Dict[Path, ModuleInfo] = {}
    allow = load_allowlist(REPO_ROOT)
    keep_marker = allow.get("comments_keep_marker", "KEEP:")
    module_globs = [dotted_to_path_glob(pat) for pat in allow.get("modules", [])]

    for path in py_files:
        module_infos[path] = analyze_module(path)

    # Aggregate reads across all modules
    all_reads: Set[str] = set()
    for info in module_infos.values():
        all_reads |= info.read_names

    # Collect definitions
    unref_functions: List[Tuple[str, str]] = []  # (module, name)
    unref_classes: List[Tuple[str, str]] = []
    unref_constants: List[Tuple[str, str]] = []
    for path, info in module_infos.items():
        # Skip file if it contains keep marker
        try:
            src = path.read_text(encoding="utf-8", errors="ignore")
            if keep_marker and keep_marker in src:
                continue
        except Exception:
            pass
        # Skip modules matching allowlist globs
        rel_posix = path.relative_to(REPO_ROOT).as_posix()
        if any(fnmatch(rel_posix, glob + ".py") or rel_posix.startswith(glob + "/") for glob in module_globs):
            continue
        modname = to_module_name(REPO_ROOT, path)
        for fn in sorted(info.defined_functions):
            if fn not in all_reads and not is_test_path(path):
                unref_functions.append((modname, fn))
        for cls in sorted(info.defined_classes):
            if cls not in all_reads and not is_test_path(path):
                unref_classes.append((modname, cls))
        for const in sorted(info.defined_constants):
            if const not in all_reads and not is_test_path(path):
                unref_constants.append((modname, const))

    # Modules never imported
    imported_modules: Set[str] = set()
    for info in module_infos.values():
        imported_modules |= info.imports

    modules_candidates = []
    for path in py_files:
        if should_exclude_module_from_never_imported(path):
            continue
        # allowlist checks
        rel_posix = path.relative_to(REPO_ROOT).as_posix()
        if any(fnmatch(rel_posix, glob + ".py") or rel_posix.startswith(glob + "/") for glob in module_globs):
            continue
        try:
            src = path.read_text(encoding="utf-8", errors="ignore")
            if keep_marker and keep_marker in src:
                continue
        except Exception:
            pass
        modname = to_module_name(REPO_ROOT, path)
        is_imported = False
        # Consider imported if exact match or parent-package imported
        for imp in imported_modules:
            if modname == imp or modname.startswith(imp + "."):
                is_imported = True
                break
        if not is_imported:
            modules_candidates.append(modname)

    # Config keys never read (from top-level JSON files)
    json_keys = load_top_level_json_keys(REPO_ROOT)
    # Build corpus for string search (code + config)
    corpus_files: List[Path] = []
    for dirpath, dirnames, filenames in os.walk(REPO_ROOT):
        # Limit to text/code files
        dirnames[:] = [d for d in dirnames if d not in PY_EXCLUDE_DIRS and d not in {"puzzleassets", "sounds", "stories"}]
        for fname in filenames:
            if any(fname.endswith(ext) for ext in (".py", ".json", ".md", ".toml", ".yaml", ".yml", ".txt", ".ini", ".cfg", ".sh", ".bat")):
                corpus_files.append(Path(dirpath) / fname)

    corpus_texts: Dict[Path, str] = {}
    for f in corpus_files:
        try:
            corpus_texts[f] = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            corpus_texts[f] = ""

    def appears_anywhere(needle: str) -> bool:
        for text in corpus_texts.values():
            if needle in text:
                return True
        return False

    unused_json_keys: Dict[str, List[str]] = {}
    for cfg_name, keys in json_keys.items():
        unused = []
        for k in sorted(keys):
            # Search for the key name as a string
            if not appears_anywhere(k):
                unused.append(k)
        unused_json_keys[cfg_name] = unused

    # Vulture integration
    vulture_result = run_vulture(REPO_ROOT)

    # Build output JSON
    output = {
        "repo_root": str(REPO_ROOT),
        "vulture": vulture_result,
        "ast_scan": {
            "unreferenced_functions": [
                {"module": m, "name": n, "rank": "Medium"} for m, n in sorted(unref_functions)
            ],
            "unreferenced_classes": [
                {"module": m, "name": n, "rank": "Medium"} for m, n in sorted(unref_classes)
            ],
            "unreferenced_constants": [
                {"module": m, "name": n, "rank": "Low"} for m, n in sorted(unref_constants)
            ],
            "modules_never_imported": [
                {"module": m, "rank": "Medium"} for m in sorted(modules_candidates)
            ],
            "unused_config_keys": [
                {"file": cfg, "key": key, "rank": "Low"}
                for cfg, keys in unused_json_keys.items()
                for key in keys
            ],
        },
    }

    # Save JSON report
    out_json_path = BUILD_DIR / "dead_code.json"
    out_json_path.write_text(json.dumps(output, indent=2, sort_keys=False), encoding="utf-8")

    # Pretty text summary
    def print_section(title: str) -> None:
        print("\n" + title)
        print("-" * len(title))

    print_section("Dead Code Report (best-effort)")
    if output["vulture"].get("available"):
        items = output["vulture"].get("items", [])
        print(f"Vulture findings: {len(items)} issues")
        for it in items[:20]:
            conf = it.get("confidence")
            conf_str = f" ({conf}%)" if conf is not None else ""
            print(f"[{it['rank']}] {it['file']}:{it['line']}: {it['message']}{conf_str}")
        if len(items) > 20:
            print(f"... and {len(items) - 20} more")
    else:
        print("Vulture not available; skipped external analysis.")

    ast_scan = output["ast_scan"]
    print_section("Unreferenced functions (Medium)")
    for entry in ast_scan["unreferenced_functions"][:50]:
        print(f"{entry['module']}.{entry['name']}")
    if len(ast_scan["unreferenced_functions"]) > 50:
        print(f"... and {len(ast_scan['unreferenced_functions']) - 50} more")

    print_section("Unreferenced classes (Medium)")
    for entry in ast_scan["unreferenced_classes"][:50]:
        print(f"{entry['module']}.{entry['name']}")
    if len(ast_scan["unreferenced_classes"]) > 50:
        print(f"... and {len(ast_scan['unreferenced_classes']) - 50} more")

    print_section("Unreferenced constants (Low)")
    for entry in ast_scan["unreferenced_constants"][:50]:
        print(f"{entry['module']}.{entry['name']}")
    if len(ast_scan["unreferenced_constants"]) > 50:
        print(f"... and {len(ast_scan['unreferenced_constants']) - 50} more")

    print_section("Modules never imported (Medium)")
    for entry in ast_scan["modules_never_imported"][:50]:
        print(entry["module"]) 
    if len(ast_scan["modules_never_imported"]) > 50:
        print(f"... and {len(ast_scan['modules_never_imported']) - 50} more")

    print_section("Unused config keys (Low)")
    count_cfg = 0
    for entry in ast_scan["unused_config_keys"]:
        print(f"{entry['file']}: {entry['key']}")
        count_cfg += 1
        if count_cfg >= 50:
            break
    if len(ast_scan["unused_config_keys"]) > 50:
        print(f"... and {len(ast_scan['unused_config_keys']) - 50} more")

    print_section("Ranked Summary")
    ranked_counts = defaultdict(int)
    for item in output["vulture"].get("items", []):
        ranked_counts[item["rank"]] += 1
    for key in ("unreferenced_functions", "unreferenced_classes", "unreferenced_constants"):
        for entry in ast_scan[key]:
            ranked_counts[entry["rank"]] += 1
    for entry in ast_scan["modules_never_imported"]:
        ranked_counts[entry["rank"]] += 1
    for entry in ast_scan["unused_config_keys"]:
        ranked_counts[entry["rank"]] += 1
    print(f"High: {ranked_counts['High']}  Medium: {ranked_counts['Medium']}  Low: {ranked_counts['Low']}")

    print(f"\nSaved JSON report to: {out_json_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

