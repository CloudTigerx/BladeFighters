import random


class Block:
    def __init__(self, color, is_breaker: bool = False, is_garbage: bool = False, is_strike: bool = False, attack_state: str | None = None):
        self.color = color
        self.is_breaker = is_breaker
        self.is_garbage = is_garbage  # colored garbage (second-to-last stage)
        self.is_strike = is_strike    # initial strike stage visual
        # attack_state lifecycle (inbound attacks): 'strike' -> 'sprinkle' -> 'cgarbage' -> None
        self.attack_state = attack_state
        # marked for clearing by breaker system (will be removed during cascade)
        self.marked_for_clearing = False

    def __repr__(self):  # debug convenience
        if getattr(self, 'is_garbage', False):
            return f"G({self.color})"
        if getattr(self, 'is_strike', False):
            return f"S({self.color})"
        if self.is_breaker:
            return f"B({self.color})"
        return f"{self.color}"


class Piece:
    COLORS = ["red", "blue", "yellow", "green"]
    BREAKER_PROB = 0.25  # 25% chance each spawned block becomes a breaker

    def __init__(self, blocks=None):
        if blocks is not None:
            self.blocks = blocks
        else:
            self.blocks = []
            for _ in range(2):
                color = random.choice(self.COLORS)
                is_breaker = random.random() < self.BREAKER_PROB
                self.blocks.append(Block(color, is_breaker=is_breaker))
        # Optional relative offsets for arbitrary-shaped pieces.
        # If set, get_block_positions will use these offsets instead of the 1-2 block/orientation logic.
        self.block_offsets: list[tuple[int, int]] | None = None
        self.orientation = 0
        self.x = 3
        # Spawn ABOVE the visible board so pieces enter from above.
        # This avoids instant placement when the spawn column is tall and gives a short window to move/rotate.
        self.y = -1 if len(self.blocks) == 2 else 0
        self.controllable = True
        # Autonomous falling timing for split pieces
        self.autonomous_fall_timer = 0
        self.autonomous_fall_interval = 3  # frames between autonomous falls (matches timing config)
        # Horizontal sword attributes
        self.horizontal_sword = False
        self.target_x = None
        self.entry_delay = 0
        self.sword_rows = 1
        self.sword_length = 1
        self.sword_from_right = False
        self.sword_target_row = 0

    @classmethod
    def spawn_random(cls, x: int = 5):
        p = cls()
        if x < 0:
            x = 0
        p.x = x
        p.y = -1  # spawn above the grid
        p.orientation = 0
        p.controllable = True
        return p

    @classmethod
    def from_spec(cls, spec, x: int = 3):
        """Create a piece from a PieceSpec (colors + breaker flags).

        Spec duck-type expected attributes: color1, breaker1, color2, breaker2.
        """
        p = cls([
            Block(spec.color1, is_breaker=spec.breaker1),
            Block(spec.color2, is_breaker=spec.breaker2)
        ])
        p.x = x
        p.y = -1
        p.orientation = 0
        p.controllable = True
        return p

    @classmethod
    def single_block(cls, color, is_breaker: bool = False, is_garbage: bool = False, is_strike: bool = False, attack_state: str | None = None):
        p = cls([Block(color, is_breaker, is_garbage, is_strike, attack_state=attack_state)])
        p.y = 0  # spawn with anchor at row 0, single block visible
        p.controllable = True
        return p

    @classmethod
    def from_cells(cls, cells: list[tuple[int, int, Block]]):
        """Create an arbitrary-shaped piece from relative cells.

        Args:
            cells: List of (dx, dy, block) tuples relative to the piece anchor (x, y).
        """
        p = cls([block for _dx, _dy, block in cells])
        p.block_offsets = [(int(dx), int(dy)) for dx, dy, _block in cells]
        p.orientation = 0
        p.controllable = False
        return p

    def get_block_positions(self):
        if self.block_offsets is not None:
            return [
                (self.x + dx, self.y + dy, block)
                for (dx, dy), block in zip(self.block_offsets, self.blocks)
            ]
        positions = [(self.x, self.y, self.blocks[0])]  # anchor first
        if len(self.blocks) == 2:
            if self.orientation == 0:
                positions.append((self.x, self.y - 1, self.blocks[1]))
            elif self.orientation == 1:
                positions.append((self.x + 1, self.y, self.blocks[1]))
            elif self.orientation == 2:
                positions.append((self.x, self.y + 1, self.blocks[1]))
            elif self.orientation == 3:
                positions.append((self.x - 1, self.y, self.blocks[1]))
        return positions

    def __repr__(self):
        return (f"Piece({self.blocks}, o={self.orientation}, x={self.x}, "
                f"y={self.y}, ctl={self.controllable})")


# End
