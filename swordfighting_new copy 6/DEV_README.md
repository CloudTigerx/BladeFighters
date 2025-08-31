# Developer Guide (Blade Fighters WIP)

## Quick Start
```
make venv
make install
make run   # launch pygame client
```
If `make` is unavailable, mirror the commands manually.

## Test Suite
```
make test      # fast unit tests
make cov       # coverage (focus: breaker mechanics now ~80%)
```
All tests are now organized in `tests/` directory:
- `test_breakers.py` core activation + chaining
- `test_breakers_extra.py` rectangles, cohesion gravity, multi-pass stats
- `test_import_path_guard.py` ensures you're not importing a stale Trash copy
- `test_breaker_animation.py` (skipped unless progressive API restored)
- `test_cascade_*.py` cascade behavior tests
- `test_*_timing.py` timing-related tests

## Debug Scripts
Debug and demonstration scripts are in `debug/` directory:
- `debug_*.py` - Various debugging scripts for specific mechanics
- `cascade_timing_demo.py` - Cascade timing demonstrations
- Run from project root: `python debug/debug_cascade.py`

## Project Structure (trimmed)
```
core/board.py         Board grid abstraction
pieces/piece.py       Piece + Block models
mechanics/breaker.py  Breaker activation & gravity cascade
mechanics/chain_runner.py  (simplified) chain resolution driver
mechanics/gravity.py  Piece falling
mechanics/movement.py Lateral/rotation logic
fighters/player.py    Player controller (spawns pieces, handles locks)
fighters/ai.py        Simple AI opponent
attacks/              Attack pipeline (WIP)
```

## Common Dev Tasks
- Add a new mechanic: create module under `mechanics/` and add focused tests.
- Tune speeds: see `mechanics/timing.py` (env overrides supported via BF_* vars).
- Inspect board state: call `board.render_ascii()` in a debug REPL.

## Breaker Mechanics Overview
1. A breaker only fires if it has at least one same-color orthogonal neighbor.
2. It clears itself + the 4-direction flood from any matching neighbors.
3. Multiple breakers of same color in the same cluster merge naturally.
4. Garbage blocks never propagate the flood nor get cleared by it.
5. Between passes: full column compression (instant) occurs; adjacency changes may trigger new breakers.

## Progressive Animation (Experimental)
Earlier work introduced a wave-based progressive cascade (immediate breaker pop, delayed neighbors). That code was pared back in `chain_runner.py` but remnants (tests skipping) remain. To re-enable, reintroduce `begin_breaker_cascade()` path & animated states.

## Recommended Next Steps
- Add scoring tied to chain length & rectangle size.
- Implement outbound attack scheduling based on pass stats.
- Visual polish: flash breaker wave before clear.
- Expand tests to attacks + gravity edge cases (fast vs step).

## Making Changes Safely
1. Write / adjust a test to express the intended new behavior.
2. Run `make test` (fast) until green.
3. Use coverage (`make cov`) to see untouched logic; add tests if changing those areas.

## Troubleshooting
- Tests referencing Trash copy: run `pytest -k path_guard` to confirm import path.
- Pygame client crashes immediately: ensure virtualenv (`which python`) matches `.venv`.
- Breaker not clearing: print debug by instantiating `BreakerManager(board, debug=True)`.

## License / Attribution
(Placeholder) Internal prototype; not yet licensed for distribution.

---
Happy hacking.
