Scoring
#Increase next-piece lookahead weight when board ≤5 tall; decrease when >8.
#Add 2-step gated lookahead (only when max height ≤4).
#Reward breaker “arming” under cover; penalize accidental single-block breaker pops.
#Prefer wide bases: add small reward for flattening local 3-column windows.

Planning/movement
#Wall-kick aware rotation micro-policy (rotate only when space exists; otherwise nudge, then rotate).
Early-cross check: if neighbor height diff >2, don’t attempt horizontal cross.
Soft cap per-column height (e.g., ≤H-2) with gentle penalty.

Defense/survival
Threat-aware switch: if inbound sprinkles mature ≤2 locks, raise survival weights.
Hard ban raising spawn column when height ≥ H-2.
Emergency clear: prioritize immediate clears when max height ≥ H-1.

Architecture
Extract helpers (edge_gain, lookahead, bumpiness, 2x2) to swordfighting_new/fighters/ai_helpers.py.
Centralize weights in a small config + BF_JESTER_WEIGHTS env override.
Keep JesterAI <300 lines; helpers unit-tested.

Observability
Add compact per-piece decision log (heights, choice, top 3 alternatives).
Seed + reproducible replay printer for stuck/KO cases.

Self-check:
Concrete, incremental items? Yes.
Covers scoring, control, safety, refactor? Yes.
Stays within minimal changes ethos? Yes.