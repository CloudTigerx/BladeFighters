# BLADE FIGHTERS - Complete Design Document

## Game Overview

**Blade Fighters** is a competitive puzzle fighting game inspired by Puyo Puyo, Puzzle Pirates Sword Fighting, and Crystal Crisis. This is **NOT** Tetris or a Match-3 game.

### Core Concept
Players build clusters of colored blocks, break them with special "breaker" pieces to create attacks (strikes and sprinkles), and send these attacks to opponents. The last player standing wins.

---

## Technical Architecture

### Hardware & Libraries
- **Hardware:** MacBook Pro (48GB), Windows PC with 4080 Super GPU, Intel i9 13900K CPU, 32GB DDR5
- **Libraries:** Pygame, NumPy, PyEE, Transitions, Pytest, Hypothesis, MyPy, Ruff, Black
- **Scaling:** Game adapts to native device resolution (Mac + Windows), planned expansion to iOS/Android

### Modular Design
- **Logic-driven:** Game mechanics drive animations, not the reverse
- **Event-based:** Logic emits events, renderer/UI listens
- **Deterministic:** Single match seed with split RNG streams (pieces vs garbage vs FX)
- **Testable:** Unit tests for all invariants and edge cases

---

## Grid System

### Dimensions & Coordinates
- **Board:** 6 columns × 12 rows
- **Columns:** Left to right: 0, 1, 2, 3, 4, 5
- **Rows:** Bottom to top: 0 → 11
- **Boundaries:** Hard edges, top, and bottom; pieces cannot pass through

### Spawn System
- **Spawn location:** Pieces spawn **above column 4** (not in column 4)
- **Visibility:** Pieces visible upon entry into the grid
- **Piece preview:** Displayed outside grid, top-left/right

---

## Pieces & Breakers

### Piece Types
- **Normal pieces:** 2-block vertical formations (always attached)
- **Breakers:** Same four colors, spawn at **25% chance**
- **Colors:** Red, Blue, Green, Yellow (values 1-4)

### Spawn Rules
- **2 total blocks spawn attached per piece**
- **Pieces spawn vertically** (2 blocks stacked)
- **Next piece spawns only after current piece locks**
- **All players receive identical piece sequences** (deterministic RNG)

### Breaker Mechanics
- **25% spawn chance** with normal pieces
- **Break same color blocks** when touching them
- **Trigger cascades** when blocks fall onto them
- **Count as 1 block** toward cluster size calculations

---

## Movement & Controls

### Basic Controls
- **Left/Right:** Move piece horizontally
- **Up:** Counter-clockwise rotation (around top piece)
- **Down:** Clockwise rotation (around bottom piece)
- **Space:** Accelerate piece (4x gravity multiplier)

### Movement Mechanics
- **Wall Flip:** When pressed against a wall, rotation may kick piece to adjacent column if possible
- **Gravity:** Global, applies to all pieces, breakers, clusters, sprinkles, and strikes
- **Lock delay:** 50ms before piece locks when it hits bottom

### Input System
- **DAS (Delayed Auto-Shift):** 150ms initial delay before auto-repeat
- **ARR (Auto-Repeat Rate):** 50ms repeat rate (left/right only, not space bar)
- **Rotation priority:** Can rotate while moving

### Timing
- **Normal fall:** 1600ms from spawn to bottom
- **Space acceleration:** 4x gravity multiplier (piece only)
- **Lock delay:** 50ms

---

## Clusters

### Definition
Clusters are any block formations of the same color with size **2×2 or larger**:
- **Examples:** 2×2, 2×3, 3×4, 6×12, etc.
- **All possible sizes:** 2×2 through 6×12 (see complete list in original README.MD)

### Cluster Behavior
- **Glow when formed** (asset vs. rendering TBD)
- **Break as whole pieces** when breaker touches them
- **Cascade spreads** from where cluster was to adjacent same-color blocks
- **Cascade direction:** Up/down/left/right (no diagonals)

### Cluster Detection
- **Minimum size:** 2×2 (4 blocks minimum)
- **Same color only:** All blocks in cluster must be same color
- **Connected adjacency:** Blocks must touch (not just same color)

---

## Combo System

### Mechanics
- **Unlimited chain potential** (no cap on combos)
- **Breakers trigger cascades** causing additional combos
- **Combo counting:** 1×, 2×, 3×, etc.

### Cascade Process
1. Breaker touches cluster → entire cluster disappears instantly
2. Gravity applies to floating blocks
3. Blocks fall onto same-color breakers → 2× combo
4. Process repeats until no more matches

### Combo Timing
- **Space bar effect:** Only affects pieces traveling through grid
- **During breaking:** Space bar has no effect until new piece spawns
- **Reset:** Combo resets when no more matches occur

---

## Attack System

### Attack Types
1. **Sprinkles (Garbage):** Individual blocks sent to opponent
2. **Strikes (Swords):** Cluster-based attacks with specific dimensions

### Sprinkle Calculations
**Formula:** `sprinkles = Σ floor(group_size / 2) * combo_index`

**Process:**
1. Break combo into individual steps with group sizes G_i
2. For each step: `floor(G_i / 2) * combo_index`
3. Sum all results

**Example:** Single 3 blocks, double 4 blocks, triple 5 blocks
- Step 1: `floor(3/2) * 1 = 1 * 1 = 1`
- Step 2: `floor(4/2) * 2 = 2 * 2 = 4`  
- Step 3: `floor(5/2) * 3 = 2 * 3 = 6`
- **Total:** 1 + 4 + 6 = 11 sprinkles

### Sprinkle Placement
**Pattern alternation:** Right, left, right, left, right, left...

**Visual flow (6 columns numbered 1-6):**
- **Right attack:** 6 → 1 → 5 → 2 → 3 → 4
- **Left attack:** 1 → 6 → 2 → 5 → 3 → 4

**Rules:**
- **First sprinkle of game:** Always lands on the right
- **Column 4 cap:** Sprinkles cannot exceed row 10 in column 4
- **Wastage:** If column is full, sprinkles are wasted (not rerouted)
- **Entire attack assigned:** All sprinkles in same turn use same pattern

### Strike (Sword) Creation

#### Vertical Strikes (Taller or Square Clusters)
**Formula:**
- `width = min(cluster_width, 3)`
- `length = min(cluster_height × combo, board_height)`

**Examples:**
- 2×3 × 2 = 1×6 (width=1, length=min(6,12)=6)
- 4×5 × 3 = 3×12 (width=3, length=min(15,12)=12)

#### Horizontal Strikes (Wider Clusters)
**Formula:**
- `rows = min(cluster_height, 3)`
- `length = cluster_width × combo`

**Auto-convert to vertical if:**
- `length ≥ 2 × board_width` (≥12 on classic 6-wide)
- Or if at least half cannot enter screen

**Examples:**
- 5×2 × 2 = 6×2 (length=10 < 12, stays horizontal)
- 5×2 × 3 = 15×2 → 2×12 (length=15 ≥ 12, converts to vertical)

### Strike Placement Rules

#### Vertical Strike Rules (6 Rules)
1. **Obstacle Avoidance:** Right-handed check right first, left-handed check left first
2. **No Stacking:** Strikes cannot land on top of other strikes
3. **Column 4 Forced:** Only when no other columns available
4. **Top-Screen Collision:** Strikes blocked at row 12 move laterally
5. **Damage Maximization:** Strikes seek columns where they can land completely
6. **Wastage:** Strikes that cannot land anywhere are wasted

#### Horizontal Strike Rules
1. **No Gems:** Enter 2 rows below highest block on defending screen
2. **With Gems:** Enter 3 rows below bottom of lowest gem
3. **Forced Vertical:** If at least half cannot enter, convert to vertical

### Strike Drop Patterns
**Column pattern:** 2, 3, 4, 5, 6, 1 (looping)
**Handedness:** R, L, R, L, R, L (alternating)

**Examples with column 4 avoidance:**
- **1×4 pattern:** 2, 3, 5*, 5, 6, 1 (asterisk = moved to avoid col 4)
- **2×N pattern:** 2/3, 2/3*, 5/6*, 5/6, 1/2...
- **3×N pattern:** 1/2/3*, 1/2/3*, 1/2/3*...

### Piercing Rules
- **Strikes pierce:** Empty cells, single non-cluster blocks, and sprinkles
- **Strikes do NOT pierce:** Clusters (≥2×2)
- **Pathfinding:** If strike intersects cluster, must pathfind around according to handedness

---

## Attack Timing & Delivery

### Delivery Delay
- **Fixed delay:** D = 4 defender locks
- **When:** Attacker produces payload at lock k, lands on defender before lock k + D
- **FIFO:** Multiple payloads mature on same lock

### Attack Timing Decision
**4-turn delay** between attack sending and receiving (replaces piece-associated timing)

**Reasoning:**
- Simpler to implement
- Easier for players to understand
- Prevents newer players from getting overwhelmed
- Avoids "beating a dead horse" when players are at different speeds

### Payload Resolution (Simultaneous)
**Rule:** Strikes placed before sprinkles. Strikes define each column's "floor."

**Process:**
1. **Place strikes first** - define temporary floor: H'[c] = H[c] + S[c]
2. **Place sprinkles** - only at rows ≥ H'[c], following edge→center pattern
3. **Run gravity/clears** after both are placed

---

## Garbage Lifecycle

### State Machine (Defender-side)
At defender **lock** boundaries only:

```
Incoming → (after D locks) → Sprinkle → (next lock) → ColoredGarbage → (next lock) → NormalBlock(color)
```

**Transitions:**
- **Sprinkle:** Initial garbage state (white/neutral)
- **ColoredGarbage:** Colored but still garbage
- **NormalBlock:** Fully integrated into board

**No mid-fall transformations** - only at lock boundaries.

---

## Game Over Conditions

### Primary Condition
**Spawn collision = immediate game over**

**Process:**
1. Last piece is set
2. Piece can break if able
3. Gravity applies
4. If next piece spawn would hit existing piece → GAME OVER

### No Danger Zone
- **No extra "danger zone"** above row 12
- **Top behavior:** Pieces can be placed in row 11
- **Null pieces:** Top piece in row 12 becomes null (no effect, doesn't fall)

### Multiplayer
- **Format:** PvP, first to die loses
- **Other modes:** Tournament format planned for later

---

## Multiplayer Synchronization

### Piece Synchronization
- **Identical piece queues** for all players
- **Deterministic RNG:** Single match seed
- **Buffer:** 10 pieces ahead
- **Extension:** When cursor <3 from end, extend deterministically

### Desync Handling
- **Server reseeds** with (seed, offset) if drift occurs
- **Desync tolerance:** Faster players can get ahead, but must receive same pieces when caught up

### Attack Synchronization
- **Shared queues:** Both column pattern and handedness queues shared between opponents
- **Turn counting:** All attacks (strikes and sprinkles) count toward pattern advancement

---

## Data Model

### Cell Types
```python
class CellType(IntEnum):
    EMPTY = 0
    BLOCK = 1      # Normal colored block
    SPRINKLE = 2   # Initial garbage state
    CSPRINKLE = 3  # Colored sprinkles
    STRIKE = 9     # Attack strike
```

### Colors
```python
class Color(IntEnum):
    RED = 1
    BLUE = 2
    GREEN = 3
    YELLOW = 4
```

### Piece Model
```python
@dataclass
class Piece:
    col_top: int      # Column of top block
    row_top: int      # Row of top block
    vertical: bool    # True = vertical, False = horizontal
    color_top: Color  # Color of top block
    color_bottom: Color  # Color of bottom block
```

---

## Lock Boundary Order

**Engine tick contract:**
```
lock → produce_attacks → schedule(D=4) → apply matured payloads (strike→sprinkle) → gravity settle → match & clear → repeat
```

**Detailed process:**
1. **Lock piece** - place on board, emit PIECE_LOCKED
2. **Find clusters** - detect all ≥2×2 formations
3. **Produce attacks** - calculate sprinkles and strikes
4. **Schedule attacks** - queue with D=4 delay
5. **Apply matured payloads** - strike first, then sprinkles (atomic)
6. **Settle gravity** - drop floating blocks
7. **Match & clear** - resolve new matches, continue chains
8. **Repeat** - spawn next piece

---

## Implementation Priorities

### Session 1: Core Foundation (2-3 hours)
- [ ] `core/types.py` - CellType, Color enums
- [ ] `core/board.py` - Board API (in_bounds, get/set, column_heights, lowest_empty)
- [ ] `core/piece.py` - Piece model with rotation & wall-kick
- [ ] `core/gravity.py` - can_fall, lock functions
- [ ] Tests for above components

### Session 2: Logic Implementation
- [ ] `match/floodfill.py` - Cluster detection
- [ ] `attacks/producer.py` - Attack generation formulas
- [ ] Tests for cluster detection and attack formulas

### Session 3: Integration
- [ ] Wire producer into Engine after lock()
- [ ] Connect to existing payload scheduler
- [ ] Test complete attack flow

---

## Critical Invariants

1. **Strike first, then sprinkle** - Atomic payload resolution
2. **Edge→center sprinkle pattern** - Consistent placement order
3. **Column 4 cap** - No instakill with sprinkles
4. **D=4 delivery delay** - Fixed timing for all attacks
5. **Deterministic RNG** - Same pieces for all players
6. **No 1-wide strikes** - Minimum width = 2
7. **Lock boundary order** - All state changes at lock boundaries only

---

## Assets Required

### Block Assets
- `redblock.png`, `blueblock.png`, `greenblock.png`, `yellowblock.png`
- `redbreaker.png`, `bluebreaker.png`, `greenbreaker.png`, `yellowbreaker.png`

### Garbage Assets
- `redgarbage.png`, `bluegarbage.png`, `greengarbage.png`, `yellowgarbage.png`

### UI Assets
- `purple_scarlet1.png` (384×960)
- Menu backgrounds, buttons, fonts

### Effects
- Cluster glow effects (TBD: assets vs rendering)
- Strike/sprinkle visual effects
- Cascade breaking animations

### Weapon System
- **Attack colors** depend on equipped weapon
- **Strikes and sprinkles** turn into normal colored blocks based on weapon
- **Weapon system** affects attack appearance and color
- **Equipment system** planned for future implementation

---

## Settings & Options

### Required Settings
- **Control customization** - Rebind all controls
- **DAS/ARR values** - Adjustable timing
- **Hard drop** - Toggle on/off
- **Space acceleration** - Toggle on/off

### Future Settings
- **Sound volume** - Music and effects
- **Visual effects** - Particle effects, screen shake
- **Accessibility** - Color blind support, reduced motion

---

## Testing Strategy

### Unit Tests
- **Piece movement** - Falls until blocked, rotation near walls
- **Lock mechanics** - Places exactly two cells, updates column heights
- **Cluster detection** - Edge cases, minimum sizes
- **Attack formulas** - Worked examples from design
- **Payload resolution** - Strike→sprinkle atomic placement

### Integration Tests
- **Complete attack flow** - Lock → detect → produce → schedule → apply
- **Multiplayer sync** - Same pieces, same attacks
- **Game over conditions** - Spawn collision detection

### Performance Tests
- **Large boards** - XL board support
- **Long chains** - Unlimited combo potential
- **Network latency** - Multiplayer desync handling

---

## Future Expansions

### XL Boards
- **Parameterized dimensions** - Width/height configurable
- **Scaling formulas** - Attack calculations for different sizes
- **UI adaptation** - Responsive layouts

### Mobile Support
- **Touch controls** - Swipe gestures for movement
- **Screen adaptation** - Portrait/landscape modes
- **Performance optimization** - Battery efficiency

### Additional Game Modes
- **Tournament format** - Bracket system
- **Time attack** - Score-based competition
- **Puzzle mode** - Single-player challenges
- **Team battles** - 2v2, 3v3 formats

### Attack Color System
- **Strikes and sprinkles** turn into normal colored blocks
- **Colors depend on equipped weapon** (not random)
- **Weapon system** affects attack appearance and color