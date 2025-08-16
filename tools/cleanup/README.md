Cleanup reporting tools (read-only)

Overview
These scripts generate read-only reports to help identify dead code, orphan assets, and unused tests/fixtures. They do not modify or delete anything.

What gets generated
- build/cleanup/dead_code.json: Combined vulture + AST heuristics for dead code.
- build/cleanup/orphan_assets.json: Assets with zero references found in code/config.
- build/cleanup/unused_tests.json: Tests not collected, skipped/xfail markers, and dead fixtures.

How to run
From the repository root:

```bash
python tools/cleanup/dead_code_report.py
python tools/cleanup/orphan_assets.py
python tools/cleanup/unused_tests.py
```

If you prefer make:

```bash
make cleanup-report
```

Quarantine workflow (safe, CI-gated)
1) Generate reports: `make cleanup-report`
2) Dry-run quarantine: `python tools/cleanup/quarantine.py --min-rank High`
3) Apply quarantine (moves assets/code to `graveyard/<date>/`):
   ```bash
   python tools/cleanup/quarantine.py --apply --keep-tests --min-rank High
   ```
   - A `TOMBSTONES.md` and `manifest.json` are created under the batch dir.
   - Use the generated `graveyard/<date>/revert.py` to restore if needed.
4) Commit on a `cleanup/*` branch and open a PR. CI will run full checks and attach artifacts.
5) After merge, repeat for `Medium` rank with manual review.

Optional dependencies
- vulture: Improves dead code detection if installed. Install via `pip install vulture`.
- pytest: Used to collect tests and detect dead fixtures. Install dev requirements: `pip install -r requirements-dev.txt`.

Interpreting the findings
- High: Strong indicator of being unused (e.g., vulture 90%+, orphan assets with zero references, dead fixtures).
- Medium: Likely unused but needs review (e.g., unreferenced functions/classes, modules never imported, tests not collected).
- Low: Verify manually (e.g., unreferenced constants, skip/xfail markers, config keys not seen in code).

Notes and false positives
- Dynamic imports, reflection, or string-based lookups can hide real usages.
- Assets referenced indirectly (procedural names, runtime discovery) may appear as orphans.
- Vulture and AST scans are conservative heuristics; always review before removal.
- Test collection heuristics approximate pytest node IDs and may under/over report in parametrize/class-based tests.

Next steps
Use these reports to drive targeted follow-up PRs where individual removals are proposed and reviewed. Do not remove items directly based on these reports without manual confirmation.

