from __future__ import annotations


class SwordRenderController:
    def draw_horizontal_sword(self, client, sword_piece, offset_x: int, offset_y: int, board) -> None:
        if not hasattr(sword_piece, 'sword_rows') or not hasattr(sword_piece, 'sword_length'):
            self.draw_piece_fallback(client, sword_piece, offset_x, offset_y, board)
            return
        sword_blocks = self.calculate_sword_blocks(sword_piece)
        self.draw_sword_blocks(client, sword_blocks, sword_piece, offset_x, offset_y, board)

    def draw_piece_fallback(self, client, piece, offset_x: int, offset_y: int, board) -> None:
        for x, y, block in piece.get_block_positions():
            if 0 <= y < board.HEIGHT:
                rect = client._make_cell_rect(x, y, offset_x, offset_y)
                client._draw_block(rect, block)

    def calculate_sword_blocks(self, sword_piece) -> list[tuple[int, int]]:
        sword_blocks: list[tuple[int, int]] = []
        for row_offset in range(sword_piece.sword_rows):
            for col_offset in range(sword_piece.sword_length):
                block_x = sword_piece.x - col_offset if sword_piece.sword_from_right else sword_piece.x + col_offset
                block_y = sword_piece.y + row_offset
                sword_blocks.append((block_x, block_y))
        return sword_blocks

    def draw_sword_blocks(self, client, sword_blocks: list[tuple[int, int]], sword_piece, offset_x: int, offset_y: int, board) -> None:
        for block_x, block_y in sword_blocks:
            if 0 <= block_x < board.WIDTH and 0 <= block_y < board.HEIGHT:
                rect = client._make_cell_rect(block_x, block_y, offset_x, offset_y)
                client._draw_block(rect, sword_piece.blocks[0])
