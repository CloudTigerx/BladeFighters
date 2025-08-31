"""pygame_client.py - Basic Pygame rendering window for Blade Fighters

Implements:
 - Spawn column above 4 (anchor x)
 - Up arrow = rotate counter-clockwise, Down arrow = rotate clockwise
 - Space = accelerated gravity while held (NOT instant hard drop)
 - Game over only if newly spawned piece overlaps occupied cells

Usage: python3 -m swordfighting_new.pygame_client
"""

import pygame
from swordfighting_new.mechanics.timing import DEFAULT_TIMING
from swordfighting_new.session import MatchSession

# Display constants
CELL_W = 40  # reduced from 70 for better fit on screen
CELL_H = 75  # reduced from 100 for better fit on screen
MARGIN = 4
BOARD_GAP = 72  # pixels between player & enemy boards

# Preview constants
PREVIEW_SCALE = 0.8
PREVIEW_LABEL_OFFSET_Y = 30
PREVIEW_PIECE_OFFSET_Y = 60

# Pull timing numbers from centralized timing config
TIMING = DEFAULT_TIMING
FPS = TIMING.target_fps

# Attack pacing configuration (tune to slow down attacks)
ATTACK_DELAY_FRAMES = 24  # frames to wait before delivering outbound or inbound garbage
BULK_GARBAGE_DELIVERY = True  # deliver inbound garbage all at once (evenly distributed stacks)

COLOR_MAP = {
    'red': (220, 50, 50),
    'blue': (50, 90, 200),
    'yellow': (230, 200, 40),
    'green': (40, 180, 80),
    'white': (255, 255, 255),  # for strike visual
}

# UI Colors
BG = (18, 18, 28)
GRID_LINE = (40, 40, 60)
BREAKER_OUTLINE = (255, 255, 255)
GARBAGE_COLOR = (120, 120, 120)
STRIKE_OUTLINE = (250, 180, 40)
SPRINKLE_COLOR = (170, 80, 220)
CGARBAGE_COLOR = (170, 170, 170)
DEFAULT_BLOCK_COLOR = (200, 200, 200)


class PygameClient:
    def __init__(self):
        pygame.init()
        self.session = MatchSession(
            timing=TIMING,
            attack_delay_frames=ATTACK_DELAY_FRAMES,
            bulk_delivery=BULK_GARBAGE_DELIVERY
        )
        self._space_consumed = True
        self.fast = False

        # Window sizing based on board dimensions
        board = self.session.player.get_board()
        self.single_board_width = board.WIDTH * CELL_W + MARGIN * 2
        total_width = self.single_board_width * 2 + BOARD_GAP
        height = board.HEIGHT * CELL_H + MARGIN * 2
        self.enemy_offset = self.single_board_width + BOARD_GAP

        self.screen = pygame.display.set_mode((total_width, height))
        pygame.display.set_caption("Blade Fighters Modular")
        self.clock = pygame.time.Clock()
        self.running = True

        # Cache fonts to avoid creating them every frame
        self.ui_font = pygame.font.SysFont(None, 20)
        self.preview_font = pygame.font.SysFont(None, 16)

    def _make_cell_rect(self, x, y, offset_x=0, offset_y=0):
        """Helper to create a cell rectangle at grid position (x, y)."""
        return pygame.Rect(offset_x + MARGIN + x * CELL_W, offset_y + MARGIN + y * CELL_H, CELL_W, CELL_H)

    # --- Main loop -------------------------------------------------
    def run(self):
        while self.running:
            self.handle_events()
            self.update_logic()
            self.draw()
            self.clock.tick(FPS)

    # --- Input -----------------------------------------------------
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif self.session.player.get_piece().controllable:
                    piece = self.session.player.get_piece()
                    mover = self.session.player.mover
                    if event.key == pygame.K_LEFT:
                        mover.move(piece, -1, 0)
                    elif event.key == pygame.K_RIGHT:
                        mover.move(piece, 1, 0)
                    elif event.key == pygame.K_UP:
                        mover.rotate(piece, clockwise=False)
                    elif event.key == pygame.K_DOWN:
                        mover.rotate(piece, clockwise=True)
                    elif event.key == pygame.K_SPACE and not self._space_consumed:
                        self.fast = True
                        self._space_consumed = True
            elif event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
                self.fast = False
                self._space_consumed = False

    def update_logic(self):
        """Update game logic with current input state."""
        # Build intents from current real-time state (fast flag toggled by space)
        intents = {
            'move': 0,
            'rotate_cw': False,
            'rotate_ccw': False,
            'fast': self.fast
        }
        # Movement & rotation are applied in handle_events directly on intents object; simplified here
        self.session.update(intents)

        # Check for game end condition
        if self.session.player.defeated or self.session.ai.defeated:
            self.running = False

    def draw(self):
        """Main rendering method."""
        self.screen.fill(BG)
        snap = self.session.snapshot()

        # Draw both boards
        self._draw_board(snap['player']['board'], snap['player']['piece'], snap['player']['garbage_fallers'], offset_x=0)
        self._draw_board(snap['ai']['board'], snap['ai']['piece'], snap['ai']['garbage_fallers'], offset_x=self.enemy_offset)

        # Draw piece preview in center between boards
        self._draw_piece_preview(snap)

        # Draw UI labels
        self._draw_ui_labels(snap)
        pygame.display.flip()

    def _draw_ui_labels(self, snap):
        """Draw player and enemy labels."""
        self.screen.blit(self.ui_font.render("Player", True, (220, 220, 220)), (MARGIN + 2, 2))
        enemy_title = "Enemy AI" + (" (KO)" if snap['ai']['defeated'] else "")
        self.screen.blit(self.ui_font.render(enemy_title, True, (220, 180, 180)), (self.enemy_offset + MARGIN + 2, 2))

    def _draw_board(self, board, falling_piece, extra_fallers, offset_x=0, offset_y=0):
        for y in range(board.HEIGHT):
            for x in range(board.WIDTH):
                rect = self._make_cell_rect(x, y, offset_x, offset_y)
                pygame.draw.rect(self.screen, GRID_LINE, rect, 1)
                cell = board.get_piece(x, y)
                if cell != board.EMPTY and cell is not None:
                    self._draw_block(rect, cell)
        if falling_piece is not None:
            for x, y, block in falling_piece.get_block_positions():
                if 0 <= y < board.HEIGHT:
                    rect = self._make_cell_rect(x, y, offset_x, offset_y)
                    self._draw_block(rect, block)
        for g in extra_fallers:
            # Special handling for horizontal swords
            if hasattr(g, 'horizontal_sword') and g.horizontal_sword:
                self._draw_horizontal_sword(g, offset_x, offset_y, board)
            else:
                for x, y, block in g.get_block_positions():
                    if 0 <= y < board.HEIGHT:
                        rect = self._make_cell_rect(x, y, offset_x, offset_y)
                        self._draw_block(rect, block)

    def _draw_block(self, rect, block):
        """Draw a single block with appropriate color and effects based on its state."""
        # Determine color based on attack_state lifecycle
        state = getattr(block, 'attack_state', None)

        if state == 'strike' or (state is None and getattr(block, 'is_strike', False)):
            # Always render strike stage white even if attack_state somehow missing
            color = COLOR_MAP['white']
        elif state == 'sprinkle':
            # Sprinkle phase: purple
            color = SPRINKLE_COLOR
        elif state == 'cgarbage':
            color = CGARBAGE_COLOR
        elif hasattr(block, 'is_garbage') and block.is_garbage:
            color = GARBAGE_COLOR
        elif hasattr(block, 'color'):
            color = COLOR_MAP.get(block.color, DEFAULT_BLOCK_COLOR)
        else:
            color = DEFAULT_BLOCK_COLOR

        # Draw main block
        base = rect.inflate(-2, -2)
        pygame.draw.rect(self.screen, color, base, border_radius=5)

        # Draw breaker effects
        if hasattr(block, 'is_breaker') and block.is_breaker:
            self._draw_breaker_effects(base, color)

        # Draw strike outline
        if state == 'strike' or (state is None and getattr(block, 'is_strike', False)):
            pygame.draw.rect(self.screen, STRIKE_OUTLINE, base, 2, border_radius=6)

    def _draw_breaker_effects(self, base_rect, base_color):
        """Draw the visual effects for breaker blocks."""
        r, g, b = base_color
        outline = (min(255, r + 60), min(255, g + 60), min(255, b + 60))
        pygame.draw.rect(self.screen, outline, base_rect, 2, border_radius=6)
        inner = base_rect.inflate(-6, -6)
        pygame.draw.rect(self.screen, (max(0, r - 30), max(0, g - 30), max(0, b - 30)), inner, border_radius=4)
        core = base_rect.inflate(-14, -14)
        pygame.draw.rect(self.screen, outline, core, border_radius=3)

    def _draw_horizontal_sword(self, sword_piece, offset_x, offset_y, board):
        """Draw a horizontal sword with all its blocks."""
        if not hasattr(sword_piece, 'sword_rows') or not hasattr(sword_piece, 'sword_length'):
            # Fallback to regular piece drawing
            self._draw_piece_fallback(sword_piece, offset_x, offset_y, board)
            return

        sword_blocks = self._calculate_sword_blocks(sword_piece)
        self._draw_sword_blocks(sword_blocks, sword_piece, offset_x, offset_y, board)

    def _draw_piece_fallback(self, piece, offset_x, offset_y, board):
        """Fallback drawing for pieces without sword attributes."""
        for x, y, block in piece.get_block_positions():
            if 0 <= y < board.HEIGHT:
                rect = self._make_cell_rect(x, y, offset_x, offset_y)
                self._draw_block(rect, block)

    def _calculate_sword_blocks(self, sword_piece):
        """Calculate all block positions for a horizontal sword."""
        sword_blocks = []
        for row_offset in range(sword_piece.sword_rows):
            for col_offset in range(sword_piece.sword_length):
                if sword_piece.sword_from_right:
                    block_x = sword_piece.x - col_offset
                else:
                    block_x = sword_piece.x + col_offset
                block_y = sword_piece.y + row_offset
                sword_blocks.append((block_x, block_y))
        return sword_blocks

    def _draw_sword_blocks(self, sword_blocks, sword_piece, offset_x, offset_y, board):
        """Draw each block of the horizontal sword."""
        for block_x, block_y in sword_blocks:
            # Only draw blocks that are actually on the board - no visibility outside board
            if 0 <= block_x < board.WIDTH and 0 <= block_y < board.HEIGHT:
                rect = self._make_cell_rect(block_x, block_y, offset_x, offset_y)
                # Use the sword piece's block for color/properties
                self._draw_block(rect, sword_piece.blocks[0])

    def _draw_piece_preview(self, snap):
        """Draw next piece preview in center between boards."""
        next_piece = snap.get('player', {}).get('next_piece')
        if not next_piece:
            return

        center_x = self.single_board_width + BOARD_GAP // 2
        self._draw_preview_label(center_x)
        self._draw_preview_piece(next_piece, center_x)

    def _draw_preview_label(self, center_x):
        """Draw the 'NEXT' label for piece preview."""
        label = self.preview_font.render("NEXT", True, (180, 180, 180))
        label_rect = label.get_rect()
        label_x = center_x - label_rect.width // 2
        self.screen.blit(label, (label_x, MARGIN + PREVIEW_LABEL_OFFSET_Y))

    def _draw_preview_piece(self, next_piece, center_x):
        """Draw the actual preview piece."""
        preview_cell_w = int(CELL_W * PREVIEW_SCALE)
        preview_cell_h = int(CELL_H * PREVIEW_SCALE)

        # Get piece positions for preview (use default orientation 0)
        positions = self._get_preview_positions(next_piece)

        # Calculate preview piece bounds
        min_x = min(pos[0] for pos in positions)
        max_x = max(pos[0] for pos in positions)
        min_y = min(pos[1] for pos in positions)
        max_y = max(pos[1] for pos in positions)

        piece_width = (max_x - min_x + 1) * preview_cell_w
        piece_height = (max_y - min_y + 1) * preview_cell_h

        # Center the piece in the preview area
        start_x = center_x - piece_width // 2
        start_y = MARGIN + PREVIEW_PIECE_OFFSET_Y

        # Draw each block of the preview piece
        for x, y, block in positions:
            draw_x = start_x + (x - min_x) * preview_cell_w
            draw_y = start_y + (y - min_y) * preview_cell_h
            rect = pygame.Rect(draw_x, draw_y, preview_cell_w, preview_cell_h)
            self._draw_block(rect, block)

    def _get_preview_positions(self, next_piece):
        """Calculate block positions for piece preview."""
        temp_x, temp_y, temp_orientation = 0, 0, 0
        positions = [(temp_x, temp_y, next_piece.blocks[0])]  # anchor first

        if len(next_piece.blocks) == 2:
            if temp_orientation == 0:
                positions.append((temp_x, temp_y - 1, next_piece.blocks[1]))
            elif temp_orientation == 1:
                positions.append((temp_x + 1, temp_y, next_piece.blocks[1]))
            elif temp_orientation == 2:
                positions.append((temp_x, temp_y + 1, next_piece.blocks[1]))
            elif temp_orientation == 3:
                positions.append((temp_x - 1, temp_y, next_piece.blocks[1]))

        return positions

if __name__ == "__main__":
    PygameClient().run()
