from __future__ import annotations

import os
from types import ModuleType

from swordfighting_new.ui_config import UIConfig


class UIScaleController:
    def __init__(self, *, pygame):
        self._pygame = pygame

    def recompute_ui_scale_and_assets(self, client, *, pygame_client_module: ModuleType) -> None:
        """Recompute UI scaling and reload any size-dependent assets.

        Notes:
        - This updates module-level scaled constants (CELL_W, etc) that the renderer uses.
        - We pass the `pygame_client` module in to avoid circular imports.
        """
        pygame = self._pygame
        m = pygame_client_module

        board = client.session.player.get_board()

        # Clear size-dependent caches (fonts and fitted text) before recomputing.
        try:
            (getattr(client, '_font_cache', None) or {}).clear()
        except Exception:
            pass
        try:
            (getattr(client, '_fitted_text_cache', None) or {}).clear()
        except Exception:
            pass
        try:
            (getattr(client, '_menu_button_state_scaled_cache', None) or {}).clear()
        except Exception:
            pass

        try:
            screen_w, screen_h = client.screen.get_size()
        except Exception:
            screen_w, screen_h = (3840, 2160)

        base_board_px_w = board.WIDTH * m.BASE_CELL_W + m.BASE_MARGIN * 2
        try:
            base_h_cells = int(getattr(board, 'VISIBLE_HEIGHT', board.HEIGHT) or board.HEIGHT)
        except Exception:
            base_h_cells = int(getattr(board, 'HEIGHT', 12) or 12)
        base_board_px_h = base_h_cells * m.BASE_CELL_H + m.BASE_MARGIN * 2
        try:
            base_hr = int(os.getenv('BF_SPAWN_HEADROOM_ROWS', '3') or '3')
        except Exception:
            base_hr = 3
        base_hr = max(0, min(6, int(base_hr)))
        has_ai = bool(getattr(getattr(client, 'session', None), 'ai', None) is not None)
        has_enemy_board = bool(getattr(getattr(client, 'session', None), 'enemy_has_board', True))
        if has_ai and has_enemy_board:
            base_total_w = base_board_px_w * 2 + m.BASE_BOARD_GAP + m.BASE_PREVIEW_PANEL_WIDTH * 2
        elif has_ai and (not has_enemy_board):
            base_enemy_panel_w = max(220, int(round(float(base_board_px_w) * 0.62)))
            base_total_w = m.BASE_PREVIEW_PANEL_WIDTH + base_board_px_w + m.BASE_BOARD_GAP + base_enemy_panel_w
        else:
            base_total_w = base_board_px_w + m.BASE_PREVIEW_PANEL_WIDTH * 2

        base_total_h = base_board_px_h + (base_hr * m.BASE_CELL_H)

        ui_scale_env = str(os.getenv('BF_UI_SCALE', 'auto') or 'auto').strip().lower()
        if ui_scale_env not in ('', 'auto'):
            try:
                ui_scale = float(ui_scale_env)
            except Exception:
                ui_scale = 1.0
        else:
            ui_scale = min(float(screen_w) / float(max(1, base_total_w)), float(screen_h) / float(max(1, base_total_h))) * 0.94

        ui_scale = max(0.45, float(ui_scale))

        m.CELL_W = max(10, int(round(m.BASE_CELL_W * ui_scale)))
        m.CELL_H = max(10, int(round(m.BASE_CELL_H * ui_scale)))
        m.MARGIN = max(2, int(round(m.BASE_MARGIN * ui_scale)))
        m.BOARD_GAP = max(12, int(round(m.BASE_BOARD_GAP * ui_scale)))
        m.PREVIEW_PANEL_WIDTH = max(80, int(round(m.BASE_PREVIEW_PANEL_WIDTH * ui_scale)))
        m.PREVIEW_LABEL_OFFSET_Y = max(6, int(round(m.BASE_PREVIEW_LABEL_OFFSET_Y * ui_scale)))
        m.PREVIEW_PIECE_OFFSET_Y = max(18, int(round(m.BASE_PREVIEW_PIECE_OFFSET_Y * ui_scale)))
        m.PREVIEW_STATS_OFFSET_Y = max(60, int(round(m.BASE_PREVIEW_STATS_OFFSET_Y * ui_scale)))

        # Recompute fonts used throughout the UI.
        client.ui_font = pygame.font.SysFont(None, max(14, int(round(20 * ui_scale))))
        client.preview_font = pygame.font.SysFont(None, max(12, int(round(16 * ui_scale))))
        client._menu_title_font_px = max(24, int(round(54 * ui_scale)))
        client._menu_button_font_px = max(18, int(round(40 * ui_scale)))
        client._menu_title_font = pygame.font.SysFont(None, int(client._menu_title_font_px))
        client._menu_button_font = pygame.font.SysFont(None, int(client._menu_button_font_px))

        try:
            client._show_grid = str(os.getenv('BF_SHOW_GRID', '0') or '0').strip().lower() in ('1', 'true', 'yes', 'on')
        except Exception:
            client._show_grid = False

        client.ui_scale = float(ui_scale)

        # Instance-owned snapshot of UI sizing (for modularization / extraction).
        try:
            client._ui = UIConfig.from_scaled_values(
                scale=client.ui_scale,
                cell_w=m.CELL_W,
                cell_h=m.CELL_H,
                margin=m.MARGIN,
                board_gap=m.BOARD_GAP,
                preview_panel_width=m.PREVIEW_PANEL_WIDTH,
                preview_label_offset_y=m.PREVIEW_LABEL_OFFSET_Y,
                preview_piece_offset_y=m.PREVIEW_PIECE_OFFSET_Y,
                preview_stats_offset_y=m.PREVIEW_STATS_OFFSET_Y,
            )
        except Exception:
            client._ui = UIConfig.from_scaled_values(
                scale=float(getattr(client, 'ui_scale', 1.0) or 1.0),
                cell_w=int(m.CELL_W),
                cell_h=int(m.CELL_H),
                margin=int(m.MARGIN),
                board_gap=int(m.BOARD_GAP),
                preview_panel_width=int(m.PREVIEW_PANEL_WIDTH),
                preview_label_offset_y=int(m.PREVIEW_LABEL_OFFSET_Y),
                preview_piece_offset_y=int(m.PREVIEW_PIECE_OFFSET_Y),
                preview_stats_offset_y=int(m.PREVIEW_STATS_OFFSET_Y),
            )

        client.board_px_w = board.WIDTH * m.CELL_W + m.MARGIN * 2
        try:
            h_cells = int(getattr(board, 'VISIBLE_HEIGHT', board.HEIGHT) or board.HEIGHT)
        except Exception:
            h_cells = int(getattr(board, 'HEIGHT', 12) or 12)
        client.board_px_h = h_cells * m.CELL_H + m.MARGIN * 2
        has_ai = bool(getattr(getattr(client, 'session', None), 'ai', None) is not None)
        has_enemy_board = bool(getattr(getattr(client, 'session', None), 'enemy_has_board', True))
        if has_ai and has_enemy_board:
            client.enemy_panel_px_w = int(client.board_px_w)
            content_w = client.board_px_w * 2 + m.BOARD_GAP + m.PREVIEW_PANEL_WIDTH * 2
        elif has_ai and (not has_enemy_board):
            client.enemy_panel_px_w = max(220, int(round(float(client.board_px_w) * 0.62)))
            content_w = m.PREVIEW_PANEL_WIDTH + client.board_px_w + m.BOARD_GAP + int(client.enemy_panel_px_w)
        else:
            client.enemy_panel_px_w = 0
            content_w = client.board_px_w + m.PREVIEW_PANEL_WIDTH * 2
        # Add some headroom above the boards so the spawn rows are visible.
        try:
            hr = int(os.getenv('BF_SPAWN_HEADROOM_ROWS', '3') or '3')
        except Exception:
            hr = 3
        client._spawn_headroom_rows = max(0, min(6, int(hr)))
        headroom_px = int(client._spawn_headroom_rows) * int(m.CELL_H)

        content_h = client.board_px_h + headroom_px
        x_pad = max(0, (int(screen_w) - int(content_w)) // 2)
        y_pad = max(0, (int(screen_h) - int(content_h)) // 2)

        if has_ai and has_enemy_board:
            client.player_offset_x = x_pad + m.PREVIEW_PANEL_WIDTH
            client.enemy_offset_x = x_pad + m.PREVIEW_PANEL_WIDTH + client.board_px_w + m.BOARD_GAP
            client.left_preview_center_x = x_pad + (m.PREVIEW_PANEL_WIDTH // 2)
            client.right_preview_center_x = x_pad + m.PREVIEW_PANEL_WIDTH + client.board_px_w + m.BOARD_GAP + client.board_px_w + (m.PREVIEW_PANEL_WIDTH // 2)
        elif has_ai and (not has_enemy_board):
            client.player_offset_x = x_pad + m.PREVIEW_PANEL_WIDTH
            client.enemy_offset_x = client.player_offset_x + client.board_px_w + m.BOARD_GAP
            client.left_preview_center_x = x_pad + (m.PREVIEW_PANEL_WIDTH // 2)
            client.right_preview_center_x = int(client.enemy_offset_x + (int(getattr(client, 'enemy_panel_px_w', 0) or 0) // 2))
        else:
            client.player_offset_x = x_pad + m.PREVIEW_PANEL_WIDTH
            client.enemy_offset_x = client.player_offset_x + client.board_px_w + m.BOARD_GAP
            client.left_preview_center_x = x_pad + (m.PREVIEW_PANEL_WIDTH // 2)
            client.right_preview_center_x = x_pad + m.PREVIEW_PANEL_WIDTH + client.board_px_w + (m.PREVIEW_PANEL_WIDTH // 2)
        client._content_offset_y = int(y_pad) + int(headroom_px)

        # Clear caches that are size dependent.
        try:
            client._strike_solid_scaled_cache = {}
        except Exception:
            pass
        try:
            client._weapon_img_scaled = {}
        except Exception:
            pass
        try:
            client._weapon_img_preview_scaled = {}
        except Exception:
            pass
        try:
            client._weapon_img_preview_scaled_tuned = {}
        except Exception:
            pass
        try:
            client._menu_last_size = None
            client._menu_buttons = []
            client._pause_buttons = []
        except Exception:
            pass

        # Reload any scaled assets.
        try:
            client._load_images()
        except Exception:
            pass
        try:
            client._load_explosion_sprites()
        except Exception:
            pass
        try:
            client._load_board_background()
        except Exception:
            pass
        try:
            client._load_menu_assets()
        except Exception:
            pass
