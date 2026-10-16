from __future__ import annotations


class BoardViewController:
    def get_board_view(self, board) -> tuple[int, int]:
        """Return (view_y0, view_h) for rendering."""
        try:
            total_h = int(getattr(board, 'HEIGHT', 12) or 12)
        except Exception:
            total_h = 12
        try:
            view_h = int(getattr(board, 'VISIBLE_HEIGHT', total_h) or total_h)
        except Exception:
            view_h = total_h

        view_h = max(1, min(int(view_h), int(total_h)))
        if view_h >= total_h:
            return 0, int(total_h)

        try:
            y0 = int(getattr(board, 'default_view_y0', int(total_h - view_h)) or 0)
        except Exception:
            y0 = int(total_h - view_h)

        y0 = max(0, min(int(y0), int(total_h - view_h)))
        return int(y0), int(view_h)

    def snapshot_board(self, board, *, view_y0: int = 0, view_h: int | None = None):
        cells = {}
        id_map = {}
        blocks = {}

        try:
            total_h = int(getattr(board, 'HEIGHT', 12) or 12)
        except Exception:
            total_h = 12
        if view_h is None:
            view_h = int(getattr(board, 'VISIBLE_HEIGHT', total_h) or total_h)
        try:
            view_y0 = int(view_y0)
        except Exception:
            view_y0 = 0
        try:
            view_h = int(view_h)
        except Exception:
            view_h = total_h

        view_h = max(1, min(int(view_h), int(total_h)))
        view_y0 = max(0, min(int(view_y0), int(max(0, total_h - view_h))))

        for y in range(view_y0, view_y0 + view_h):
            for x in range(board.WIDTH):
                cell = board.get_piece(x, y)
                if cell != board.EMPTY and cell is not None:
                    sy = int(y - view_y0)
                    cells[(x, sy)] = cell
                    bid = id(cell)
                    id_map[bid] = (x, sy)
                    blocks[bid] = cell
        return {'cells': cells, 'id_map': id_map, 'blocks': blocks, 'view_y0': int(view_y0), 'view_h': int(view_h)}
