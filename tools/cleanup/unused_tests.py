#!/usr/bin/env python3
import ast
import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Tuple


REPO_ROOT = Path(__file__).resolve().parents[2]
BUILD_DIR = REPO_ROOT / "build" / "cleanup"


EXCLUDE_DIRS = {".git", ".venv", "venv", "build", "dist", "__pycache__"}


def list_test_files() -> List[Path]:
    test_files: List[Path] = []
    for dirpath, dirnames, filenames in os.walk(REPO_ROOT):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for fname in filenames:
            if not fname.endswith(".py"):
                continue
            p = Path(dirpath) / fname
            rel = p.relative_to(REPO_ROOT).as_posix()
            if "/tests/" in rel or rel.startswith("tests/"):
                if fname.startswith("test_") or fname.endswith("_test.py"):
                    test_files.append(p)
    return test_files


def collect_with_pytest() -> Tuple[Set[str], str, str]:
    if shutil.which("pytest") is None:
        return set(), "", ""
    cmd = [
        "pytest",
        "--collect-only",
        "-q",
    ]
    proc = subprocess.run(cmd, cwd=str(REPO_ROOT), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    collected_ids: Set[str] = set()
    # The quiet output is often one node id per line; ignore warnings/noise
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line or line.startswith("Pytest"):
            continue
        # Heuristically treat as node id if it contains '::' or ends with '.py'
        if "::" in line or line.endswith(".py"):
            collected_ids.add(line)
    return collected_ids, proc.stdout, proc.stderr


def parse_test_defs(test_files: List[Path]) -> Tuple[Set[str], Dict[str, List[str]], Dict[str, List[str]]]:
    node_ids: Set[str] = set()
    skipped_or_xfail: Dict[str, List[str]] = {}
    fixtures: Dict[str, List[str]] = {}

    for tf in test_files:
        try:
            src = tf.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(src, filename=str(tf))
        except Exception:
            continue

        # Detect fixtures
        local_fixtures: List[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # fixture?
                is_fixture = False
                if node.decorator_list:
                    for dec in node.decorator_list:
                        name = None
                        if isinstance(dec, ast.Attribute):
                            name = f"{getattr(dec.value, 'id', '')}.{dec.attr}"
                        elif isinstance(dec, ast.Name):
                            name = dec.id
                        elif isinstance(dec, ast.Call):
                            # e.g. @pytest.fixture(scope="module")
                            func = dec.func
                            if isinstance(func, ast.Attribute):
                                name = f"{getattr(func.value, 'id', '')}.{func.attr}"
                            elif isinstance(func, ast.Name):
                                name = func.id
                        if name in {"pytest.fixture", "fixture"}:
                            is_fixture = True
                if is_fixture:
                    local_fixtures.append(node.name)

        if local_fixtures:
            fixtures[tf.as_posix()] = local_fixtures

        # Detect test functions and markers
        rel = tf.relative_to(REPO_ROOT).as_posix()
        module_id_prefix = rel
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                node_id = f"{module_id_prefix}::{node.name}"
                node_ids.add(node_id)
                markers: List[str] = []
                for dec in node.decorator_list:
                    dec_str = ast.get_source_segment(src, dec) or ""
                    if re.search(r"pytest\.mark\.(skip|skipif)\b", dec_str):
                        markers.append("skip")
                    if re.search(r"pytest\.mark\.(xfail)\b", dec_str):
                        markers.append("xfail")
                if markers:
                    skipped_or_xfail[node_id] = markers
    return node_ids, skipped_or_xfail, fixtures


def dead_fixtures_with_pytest() -> Tuple[List[Dict], str, str]:
    if shutil.which("pytest") is None:
        return [], "", ""
    cmd = ["pytest", "--dead-fixtures", "-q"]
    proc = subprocess.run(cmd, cwd=str(REPO_ROOT), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    items: List[Dict] = []
    # Output lines often like: path::fixture_name
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line or line.startswith("===="):
            continue
        if "::" in line:
            path, fix = line.split("::", 1)
            items.append({"file": path, "fixture": fix})
    return items, proc.stdout, proc.stderr


def main() -> int:
    BUILD_DIR.mkdir(parents=True, exist_ok=True)

    test_files = list_test_files()
    collected_ids, collect_stdout, collect_stderr = collect_with_pytest()
    discovered_ids, skip_xfail, fixtures = parse_test_defs(test_files)

    # Tests present in repo but not in the collected ids (heuristic)
    not_collected = sorted([tid for tid in discovered_ids if not any(tid.endswith(c.split("::")[-1]) for c in collected_ids)])

    # Dead fixtures
    dead_fixtures, dead_stdout, dead_stderr = dead_fixtures_with_pytest()
    if not dead_fixtures and fixtures:
        # Fallback: fixtures that never appear in any test function parameters
        all_param_names: Set[str] = set()
        for tf in test_files:
            try:
                src = tf.read_text(encoding="utf-8", errors="ignore")
                tree = ast.parse(src, filename=str(tf))
            except Exception:
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                    for arg in node.args.args:
                        all_param_names.add(arg.arg)
        for file_path, fx in fixtures.items():
            for name in fx:
                if name not in all_param_names:
                    dead_fixtures.append({"file": file_path, "fixture": name})

    report = {
        "repo_root": str(REPO_ROOT),
        "collected_test_ids": sorted(collected_ids),
        "discovered_test_ids": sorted(discovered_ids),
        "tests_not_collected": not_collected,
        "skipped_or_xfail": skip_xfail,  # node id -> markers
        "dead_fixtures": dead_fixtures,
        "notes": {
            "collected_stdout": collect_stdout.strip(),
            "collected_stderr": collect_stderr.strip(),
            "dead_fixtures_stdout": dead_stdout.strip(),
            "dead_fixtures_stderr": dead_stderr.strip(),
        },
    }

    out_json_path = BUILD_DIR / "unused_tests.json"
    out_json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    # Pretty output
    print("Unused Tests Report")
    print("-------------------")
    print(f"Collected by pytest: {len(report['collected_test_ids'])}")
    print(f"Discovered via AST: {len(report['discovered_test_ids'])}")
    print(f"Not collected (heuristic): {len(report['tests_not_collected'])}")
    for tid in report["tests_not_collected"][:50]:
        print(f"[Medium] {tid}")
    if len(report["tests_not_collected"]) > 50:
        print(f"... and {len(report['tests_not_collected']) - 50} more")
    print(f"\nSkipped/XFail markers detected: {len(report['skipped_or_xfail'])}")
    for tid, markers in list(report["skipped_or_xfail"].items())[:50]:
        print(f"[Low] {tid}: {', '.join(markers)}")
    if len(report["skipped_or_xfail"]) > 50:
        print(f"... and {len(report['skipped_or_xfail']) - 50} more")
    print(f"\nDead fixtures: {len(report['dead_fixtures'])}")
    for item in report["dead_fixtures"][:50]:
        print(f"[High] {item['file']}::{item['fixture']}")
    if len(report["dead_fixtures"]) > 50:
        print(f"... and {len(report['dead_fixtures']) - 50} more")
    print(f"\nSaved JSON report to: {out_json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

