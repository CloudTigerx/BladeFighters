# BLADE FIGHTERS!

We should aim for a modular architecture to make easier adjustments.

Similar games for quick context (this is **NOT** Tetris or Match-3):

* **Puyo Puyo**
* **Puzzle Pirates Sword Fighting**
* **Crystal Crisis**

---

## Tech

* **Hardware:** MacBook Pro (48GB), Windows PC with 4080 Super GPU for CUDA AI image generation, Intel i9 13900K CPU, 32GB DDR5
* **Libraries:** Pygame, \[others TBD]
* **Scaling:** Game client adapts to the device’s native resolution, even with OS scaling enabled (Mac + Windows). Expansion to iOS/Android planned.

---

## Grid System (Current Runtime)

* **Dimensions (doubled):** 12 wide × 24 high (classic baseline 6×12 → now scaled ×2 in both axes)
* **Boundaries:** Hard edges, top, and bottom; pieces cannot pass through.
* **Coordinates:**

  * Columns left to right: 0, 1, 2, 3, 4, 5
  * Rows bottom to top: 0 → 11
* **Spawn:** Pieces spawn above column 4, visible upon entry.
* **Piece Preview:** Displayed outside grid, top-left/right.

---

## Pieces

* **Colors:** Red, Blue, Green, Yellow
* **Breakers:** Same four colors, spawn at 25% chance, break matching colors.
* **Spawn Rules:**

  * Pieces spawn vertically, always attached (two total blocks per piece).
  * Next piece spawns only after current piece locks.
* **All players receive identical piece sequences.**

---

## Movement + Gravity

* **Gravity:** Global, applies to all pieces, breakers, clusters, sprinkles, and strikes. Nothing ignores gravity except the bottom boundary.
* **Controls:** Left, Right, Up, Down, Space (accelerate).

  * Down = clockwise rotation (around bottom piece)
  * Up = counter-clockwise rotation (around top piece)
* **Wall Flip:** When pressed against a wall, rotation may kick piece to adjacent column if possible.
* **Speed:**

  * Normal fall: 1600ms from spawn to bottom.
  * Space bar = 4× gravity multiplier (piece only).
  * Lock delay: 50ms.
* **Input:**

  * DAS (Delayed Auto-Shift): 150ms.
  * ARR (Auto-Repeat Rate): 50ms (left/right only).

---

## Clusters

* Defined as any formation ≥2×2 of the same color.
* Examples: 2×2, 3×4, 6×12, etc.
* **Glow when formed** (asset vs. rendering TBD).
* **Breaking:**

  * A breaker touching a cluster destroys the **entire cluster** as one piece.
  * Cascade spreads to adjacent same-color blocks.
  * Cascade checks up/down/left/right (no diagonals).
* **Piercing Rule:** Strikes **can pierce non-cluster blocks and sprinkles**, but **cannot pierce clusters**.

---

## Combo System

* Unlimited chain potential.
* Breakers trigger cascades, causing additional combos.
* Combos counted as 1×, 2×, 3× …

---

## Sprinkles (Garbage)

* **Formula:** `sprinkles = sum( floor(group_size / 2) * combo_index )`
* **Placement Pattern:** Alternates edge-to-center (Right: 6→1→5→2→3→4; Left: 1→6→2→5→3→4). Always ends at column 4. Prevents instakill.
* **Instakill Protection:** Sprinkles cannot rise above row 10 in column 4.
* **Wastage:** If column is full, sprinkles targeting it are wasted (do not reroute).
* **Lifecycle:**

  * Payload queued → delayed by 4 locks → appears as **Sprinkle**
  * On **next lock:** Sprinkle → **ColoredGarbage**
  * On **next lock:** ColoredGarbage → **NormalBlock(color)**
  * Transitions only occur on piece lock.

---

## Strikes (Swords)

Updated for doubled board (12×24) & clarified generation:

* Generate from every cluster (rectangle) with size ≥ 2×2 (2×2 INCLUDED).
* One sword per rectangle per chain pass (multiple rectangles → multiple swords). No stacking in the same column within a payload: overlapping sword cells are wasted.
* Width cap: 3. Vertical length cap: 24. Horizontal effective length cap: 12 (board width). Horizontal converts to vertical if raw horizontal length ≥ 24 (2×BW).
* Formulas (strict variant chosen):
  * If H ≥ W → Vertical: `width_v = min(3, W)`, `length_v = min(H * N, 24)`.
  * Else (W > H) → Horizontal candidate: `rows_h = min(3, H)`, `length_h = W * N`.
    * If `length_h ≥ 24` convert vertical: `width_v = rows_h`, `length_v = min(length_h, 24)`.
    * Else keep horizontal: final geometry `(length_entered × rows_h)` where `length_entered = min(length_h, 12)`.
* Piercing: swords pierce empty cells, single non-cluster blocks, and sprinkles/garbage mid-lifecycle; they STOP at clusters (≥2×2). Blocked remainder is wasted (advanced reroute postponed).

---

## Payload Resolution (Simultaneous Strikes + Sprinkles)

**Rule:** Strikes are placed before sprinkles. Strikes define each column’s “floor.” Sprinkles fill only at/above this floor following edge-to-center order.

**Formula:**

* Let `H[c]` = pre-attack column height.
* Let `S[c]` = strike height in column `c`.
* After strikes: `H’[c] = H[c] + S[c]`.
* Garbage can only be placed at `rows ≥ H’[c]`.

Gravity and clears resolve after placement.

---

## Attack Timing

* Attacks are **delayed by 4 defender locks** (not frames).
* Payloads resolve FIFO at delay expiry, before the next spawn.

---

## Multiplayer Sync

* Players share **identical piece queues** generated by seeded RNG.
* **Buffer:** 10 pieces ahead.
* **Extension:** When cursor <3 from end, extend deterministically.
* **Desync Handling:** Server reseeds with `(seed, offset)` if drift occurs.

---

## Game Over

* **Condition:** Spawn collision = immediate game over.
* No extra “danger zone” above row 12.
* Multiplayer: last surviving player wins.

---

## Major Lessons (for development)

* **Logic before visuals.** Never fake mechanics with animations.
* **Resolutions matter.** Scale to native device res early.
* **Architecture:** Modular is maintainable; monolithic collapses.
* **Testing:** Integrate and test in small pieces, not massive rewrites.
* **AI:** Useful for theory and scaffolding, but eyes+hands verify truth.
* **RNG determinism:** Always seeded, split for pieces vs garbage.
* **Avoid:** Hard-coded heights (always use `board_height`), ambiguous timing, non-deterministic state changes, and strike stacking in one payload.

---

## To Do

* Flesh out cluster/strike mapping as formulas **and** retain tables for clarity.
* Add formal unit-test cases for:

  * Strike+sprinkle atomic resolution
  * Sprinkle placement patterns & wastage
  * Lifecycle transitions (Sprinkle→Garbage→Normal)
  * Attack delay D=4
  * Piece queue determinism
* Expand to XL boards later (parameterize width/height).

# Attacks & Mapping — Formula Spec (Blade Fighters)

This file replaces the big lookup tables with compact, parameterized formulas. Keep constants in `rules/params.py` so XL boards work without rewriting.

---

## Symbols & Parameters

* `W, H` — cluster width/height (cells)
* `N` — combo multiplier (1,2,3,...)
* `BH` — board height (classic: 12)
* `BW` — board width (classic: 6)
* `cap(x, lo, hi)` — clamp x into \[lo, hi]
* `min3(x)` — `min(x, 3)`

---

## Sprinkle (Garbage) Amount

Given a combo that breaks into steps with group sizes `G_i` and combo index `i` (1-based):

```
sprinkles = Σ_i floor(G_i / 2) * i
```

Notes:

* A breaker counts as 1 toward `G_i`.
* Sum over all combo steps; do not floor at the end—floor per step.

---

## Strike (Sword) Construction

We create a **sword** from the cluster shape `(W×H)` and combo `N`.

### 1) Decide orientation

* **Vertical** if `H ≥ W` (taller-or-square) → vertical mapping
* **Horizontal** if `W > H` (wider) → horizontal mapping (may convert to vertical later)

> Alternative rule you can toggle: “squares become vertical.” This matches your previous mapping style.

### 2) Vertical mapping (taller-or-square)

```
width_v  = min3(W)
length_v = cap(H * N, 1, BH)
Sword_v  = (width_v × length_v)
```

### 3) Horizontal mapping (wider)

Raw (before conversion):

```
rows_h   = min3(H)         # how many rows tall the horizontal band is
length_h = W * N           # how far it wants to enter from the side
```

**Auto-convert to vertical** if at least half cannot enter. A simple, board-agnostic rule:

```
if length_h ≥ 2 * BW:
    # Always vertical (≥12 on classic 6-wide)
    width_v  = rows_h
    length_v = cap(length_h, 1, BH)
    Sword = (width_v × length_v) vertical
else:
    # Keep horizontal, but it can only physically enter up to BW
    Sword = (length_entered × rows_h) horizontal, where length_entered = min(length_h, BW)
```

### 4) Global width cap

No sword (vertical **or** horizontal) may have width > 3:

```
width = min3(width)
```

(Already enforced above via `min3(W)` or `min3(H)`.)

---
## Strike Placement Rules (Detailed)

### Vertical Strike Placement (6 Rules)
1. **Obstacle Avoidance:** Right-handed strikes check right first, left-handed check left first
2. **No Stacking:** Strikes cannot land on top of other strikes
3. **Column 4 Forced Placement:** Only when no other columns available
4. **Top-Screen Collision:** Strikes blocked at row 12 move laterally
5. **Damage Maximization:** Strikes seek columns where they can land completely
6. **Wastage:** Strikes that cannot land anywhere are wasted

### Drop Patterns with Column 4 Avoidance
- **1×4 pattern:** `2,3,5*,5,6,1` (asterisk = moved to avoid col 4)
- **2×N pattern:** `2/3, 2/3*, 5/6*, 5/6, 1/2...`
- **3×N pattern:** `1/2/3*, 1/2/3*, 1/2/3*...`

### Horizontal Strike Rules
[Add the entrance height tables and side-switching logic from original README]
---

## Placement Queues & Handedness

Maintain two shared queues (advance both for every sword produced by any player in the match):

* **Column pattern index** (e.g., `2,3,4,5,6,1` looping)
* **Handedness** alternating `R, L, R, L, ...`

Apply your **column-4 avoidance** and **obstacle skirt** rules during actual placement, not during mapping. Mapping only defines sword geometry.

---

## Simultaneous Payload Resolution (same tick)

1. Place swords first, creating a temporary added height per column.
2. Define `H’[c] = H[c] + S[c]` where `S[c]` is newly added sword cells in column c.
3. Place sprinkles using simplified heuristic (Phase 1: least-filled columns / simple pass). They must land at rows ≥ `H’[c]`, respecting a doubled Column‑4 cap (row 22). Above-cap placements are wasted.
4. No sword column stacking in a single payload; overlap wastes cells.
5. Gravity & breaker evaluation run afterward; swords remain fixed until lifecycle advances on defender locks.

---

## Sprinkle Placement Pattern (Edge→Center)

* Right-start: `6 → 1 → 5 → 2 → 3 → 4`
* Left-start:  `1 → 6 → 2 → 5 → 3 → 4`
* First sprinkle of the **match** starts on the **right**.
* Column 4 cap: sprinkles may not exceed row cap in column 4 (classic: top of col4 ≤ row 10). Excess is **wasted**, never rerouted.

---

## Timing (Delivery Delay)

* Fixed delay **D = 4 defender locks**. When attacker produces a payload at attacker lock `k`, it lands on defender immediately **before** the defender’s lock `k + D`.
* FIFO if multiple payloads mature on the same lock.

---

## Garbage & Strike Lifecycle (Defender-side state machine)

Transform only on defender locks (frame-based timing currently; lock-based upgrade later).

Sprinkle Path (3 steps):
```
Incoming → Sprinkle (gray) → ColoredGarbage (tinted) → Normal(color)
```

Strike Path (4 steps):
```
Incoming → Strike(white) → StrikeSettled(gray) → StrikeColored(tinted) → Normal(color)
```

Final Normal uses placeholder single color (weapon system deferred).

---

## Piercing Rules

* **Strikes pierce**: empty cells, single non-cluster blocks, and sprinkles.
* **Strikes do NOT pierce**: clusters (≥2×2). If a strike would intersect a cluster during placement/entry, it must pathfind around according to handedness & avoidance rules; if impossible, that portion is wasted.

---

## Board Caps (parameterize!)

For 12×24 runtime:
* Vertical sword length cap: 24
* Horizontal max entry: 12
* Width cap: 3
* Column‑4 sprinkle height cap: 22 (double classic 10) (waste above)
* Horizontal→Vertical conversion threshold: length_h ≥ 24

---

## Worked Examples (Updated 12×24)

1. **2×2, N=3, BH=24**

* Taller-or-square → vertical
* `width_v = min3(2) = 2 → but square mapping prefers 1-wide tip?` Choose rule:

  * **Square→vertical (tip width by tier)** (classic feel): map `(2×2)` to `(1×4)` base, then `length_v = cap(2*N*2/2, 1, BH)` → simpler: use hard rule: `(2×2)*N → (1 × cap(4*N, 1, BH))` → `(1×12)` at N=3.
  * **Strict formula**: `width_v = min3(2)=2`, `length_v = cap(2*3,1,12)=6` → `(2×6)`

  Pick one style and keep it consistent. (Classic PP feels like the tip mapping; strict formula is easier to reason about.)

2. **4×5, N=2, BH=24**

* Taller (`H=5 ≥ W=4`) → vertical: `width_v=min3(4)=3`, `length_v=cap(5*2,1,12)=10` → **`3×10`**

3. **5×2, N=2, BW=12, BH=24**

* Wider → horizontal raw: `rows_h=min3(2)=2`, `length_h=5*2=10`
* Convert? `10 ≥ 2*BW (=12)` → **no** convert. Horizontal enters up to `min(10, 6)=6` → **`6×2`**

4. **5×2, N=3, BW=12**

5. **5×2, N=5, BW=12** (conversion) → length_h=25 ≥24 → vertical 2×24

6. **3×10, N=3** → vertical width 3, length min(30,24)=24 → 3×24

* `length_h=15 ≥ 12` → convert to vertical: `width_v=rows_h=2`, `length_v=cap(15,1,12)=12` → **`2×12`**

---

## Reference Pseudocode (12×24)

```python
def make_sword(W, H, N, BW=12, BH=24):
    def min3(x):
        return 3 if x > 3 else x

    if H >= W:  # vertical or square-as-vertical
        width_v  = min3(W)
        length_v = max(1, min(H * N, BH))
        return ("vertical", width_v, length_v)
    else:       # horizontal, may convert
        rows_h   = min3(H)
        length_h = W * N
  if length_h >= 2 * BW:  # conversion threshold (24 on 12-wide)
            width_v  = rows_h
            length_v = max(1, min(length_h, BH))
            return ("vertical", width_v, length_v)
        else:
            length_entered = min(length_h, BW)
            return ("horizontal", length_entered, rows_h)

---
## Phase Implementation Plan

Phase 1:
* Maintain current sprinkle formula (floor(s/2), min1) * combo index.
* Generate sword metadata per rectangle pass; place swords prior to sprinkles (simple least-filled heuristic, no pathfinding).
* Enforce no overlapping sword columns within payload; overlapping cells wasted.
* Represent swords as solid white strike blocks; static until next defender lock.

Phase 2:
* Advanced placement patterns (handedness paths, column 4 avoidance prioritization, obstacle skirts).
* True edge→center sprinkle pattern with direction alternation.
* Convert delivery delay & lifecycle progression to lock-count scheduling (D=4 locks).

Phase 3:
* Full strike lifecycle (white→gray→colored→normal) tied to defender locks.
* Weapon system driving final colors; waste tracking for future currency/XP.
* Piercing path reroute (attempt lateral adjustments before waste).

Phase 4:
* Visual telegraphs, animations, particle FX.
* Parameter module for scalable board sizes & caps.
* Unit tests for mixed payload resolution & lifecycle timing.
```

---

## Test Checklist (unit specs)

* Vertical: `(W,H,N)=(3,7,2) → (vertical, width=3, length=cap(14,1,BH))`
* Horizontal no-convert: `(5,2,2,BW=6) → (horizontal,6,2)`
* Horizontal convert: `(4,3,4,BW=6) → length_h=16 ≥ 12 → (vertical,3,cap(16,1,12)=12)`
* Piercing: strike pathfinds around clusters; wastes overflow if fully blocked.
* Payload atomicity: strikes placed first, sprinkles never below strike floors.
* Column-4 cap enforced; wastage allowed.
* Delivery delay D=4 at defender locks.
* Lifecycle transitions only at lock.

---

