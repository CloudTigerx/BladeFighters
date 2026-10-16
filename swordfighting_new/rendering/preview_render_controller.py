from __future__ import annotations

from typing import Any


Rect = Any


class PreviewRenderController:
    def __init__(self, *, pygame):
        self._pygame = pygame

    def draw_side_previews(
        self,
        client,
        snap: dict,
        *,
        preview_panel_width: int,
        preview_scale: float,
        cell_w: int,
        cell_h: int,
        margin: int,
        preview_label_offset_y: int,
        preview_piece_offset_y: int,
    ) -> None:
        pygame = self._pygame

        player_piece = snap['player'].get('next_piece')
        enemy_piece = snap['ai'].get('next_piece')
        enemy_has_board = bool(snap.get('enemy_has_board', True))

        def _panel_slots(panel_rect: Rect, side: str) -> tuple[Rect, Rect]:
            """Return (sword_slot, piece_slot) inside panel_rect.

            Keeping slots fixed prevents dragging the piece preview from shrinking
            the sword art (which is otherwise scaled to fit remaining space).
            """
            try:
                ui_scale = float(getattr(client, 'ui_scale', 1.0) or 1.0)
            except Exception:
                ui_scale = 1.0
            pad = max(2, int(round(4 * ui_scale)))
            gap = max(3, int(round(6 * ui_scale)))
            try:
                sword_w = int(round(float(panel_rect.width) * 0.46))
            except Exception:
                sword_w = int(max(28, panel_rect.width // 2))
            sword_w = max(28, min(int(panel_rect.width) - pad * 2 - gap - 28, int(sword_w)))
            sword_w = max(28, int(sword_w))

            if str(side).strip().lower() == 'right':
                sword_slot = pygame.Rect(int(panel_rect.right - pad - sword_w), int(panel_rect.top), int(sword_w), int(panel_rect.height))
                piece_left = int(panel_rect.left + pad)
                piece_right = int(sword_slot.left - gap)
                piece_slot = pygame.Rect(int(piece_left), int(panel_rect.top), max(1, int(piece_right - piece_left)), int(panel_rect.height))
            else:
                sword_slot = pygame.Rect(int(panel_rect.left + pad), int(panel_rect.top), int(sword_w), int(panel_rect.height))
                piece_left = int(sword_slot.right + gap)
                piece_right = int(panel_rect.right - pad)
                piece_slot = pygame.Rect(int(piece_left), int(panel_rect.top), max(1, int(piece_right - piece_left)), int(panel_rect.height))

            return (sword_slot, piece_slot)

        if player_piece:
            try:
                panel_left = int(client.left_preview_center_x - int(preview_panel_width) // 2)
                panel_right = int(client.left_preview_center_x + int(preview_panel_width) // 2)
                panel_rect = pygame.Rect(panel_left, 0, max(1, panel_right - panel_left), int(client.screen.get_height()))
            except Exception:
                panel_rect = pygame.Rect(0, 0, max(1, int(preview_panel_width)), int(client.screen.get_height()))

            sword_slot, piece_slot = _panel_slots(panel_rect, 'left')
            try:
                off = (getattr(client, '_preview_piece_offset_px', {}) or {}).get('left', (0, 0))
                off_x, off_y = int(off[0]), int(off[1])
            except Exception:
                off_x, off_y = (0, 0)
            cx = int(piece_slot.centerx + off_x)
            try:
                cx = int(self.clamp_preview_piece_center_x(
                    client,
                    player_piece,
                    cx,
                    piece_slot,
                    preview_scale=preview_scale,
                    cell_w=cell_w,
                    cell_h=cell_h,
                ))
            except Exception:
                cx = int(cx)
            pr = self.draw_preview_piece(
                client,
                player_piece,
                int(cx),
                offset=(0, int(off_y)),
                preview_scale=preview_scale,
                cell_w=cell_w,
                cell_h=cell_h,
                margin=margin,
                preview_piece_offset_y=preview_piece_offset_y,
            )
            try:
                client._last_preview_piece_rect['left'] = pr
            except Exception:
                pass
            try:
                self.draw_preview_sword_next_to_piece(
                    client,
                    getattr(client, '_equipped_sword_value', None),
                    pr,
                    panel_rect,
                    side='left',
                    sword_slot_rect=sword_slot,
                )
            except Exception:
                pass

        if enemy_has_board and enemy_piece:
            try:
                panel_left = int(client.right_preview_center_x - int(preview_panel_width) // 2)
                panel_right = int(client.right_preview_center_x + int(preview_panel_width) // 2)
                panel_rect = pygame.Rect(panel_left, 0, max(1, panel_right - panel_left), int(client.screen.get_height()))
            except Exception:
                panel_rect = pygame.Rect(0, 0, max(1, int(preview_panel_width)), int(client.screen.get_height()))

            sword_slot, piece_slot = _panel_slots(panel_rect, 'right')
            try:
                off = (getattr(client, '_preview_piece_offset_px', {}) or {}).get('right', (0, 0))
                off_x, off_y = int(off[0]), int(off[1])
            except Exception:
                off_x, off_y = (0, 0)
            cx = int(piece_slot.centerx + off_x)
            try:
                cx = int(self.clamp_preview_piece_center_x(
                    client,
                    enemy_piece,
                    cx,
                    piece_slot,
                    preview_scale=preview_scale,
                    cell_w=cell_w,
                    cell_h=cell_h,
                ))
            except Exception:
                cx = int(cx)
            pr = self.draw_preview_piece(
                client,
                enemy_piece,
                int(cx),
                offset=(0, int(off_y)),
                preview_scale=preview_scale,
                cell_w=cell_w,
                cell_h=cell_h,
                margin=margin,
                preview_piece_offset_y=preview_piece_offset_y,
            )
            try:
                client._last_preview_piece_rect['right'] = pr
            except Exception:
                pass
            try:
                self.draw_preview_sword_next_to_piece(
                    client,
                    getattr(client, '_enemy_sword_value', None),
                    pr,
                    panel_rect,
                    side='right',
                    sword_slot_rect=sword_slot,
                )
            except Exception:
                pass

    def clamp_preview_piece_center_x(
        self,
        client,
        piece,
        desired_center_x: int,
        panel_rect: Rect,
        *,
        preview_scale: float,
        cell_w: int,
        cell_h: int,
    ) -> int:
        """Keep the NEXT piece preview fully inside its preview panel.

        This prevents the preview from overlapping the board area at extreme UI scales.
        """
        preview_cell_w = int(cell_w * float(preview_scale))
        preview_cell_h = int(cell_h * float(preview_scale))
        try:
            ui_scale = float(getattr(client, 'ui_scale', 1.0) or 1.0)
        except Exception:
            ui_scale = 1.0
        preview_gap_x = max(0, int(round(1.0 * ui_scale)))
        preview_gap_y = max(4, int(round(preview_cell_h * 0.28)), int(round(10.0 * ui_scale)))
        step_x = max(1, int(preview_cell_w + preview_gap_x))
        step_y = max(1, int(preview_cell_h + preview_gap_y))

        positions = self.get_preview_positions(client, piece)
        min_x = min(p[0] for p in positions)
        max_x = max(p[0] for p in positions)
        piece_w = (max_x - min_x + 1) * step_x - preview_gap_x

        try:
            pad = max(2, int(round(3 * ui_scale)))
        except Exception:
            pad = 2
        min_cx = int(panel_rect.left + pad + (piece_w // 2))
        max_cx = int(panel_rect.right - pad - (piece_w // 2))
        if min_cx > max_cx:
            return int(panel_rect.centerx)
        return int(max(min_cx, min(int(desired_center_x), max_cx)))

    def draw_preview_label(
        self,
        client,
        center_x: int,
        text: str,
        *,
        margin: int,
        preview_label_offset_y: int,
    ) -> None:
        label = client.preview_font.render(text, True, (180, 180, 180))
        lx = int(center_x) - int(label.get_width()) // 2
        y0 = int(getattr(client, '_content_offset_y', 0) or 0)
        client.screen.blit(label, (int(lx), int(y0 + margin + preview_label_offset_y)))

    def draw_preview_piece(
        self,
        client,
        piece,
        center_x: int,
        *,
        offset: tuple[int, int] = (0, 0),
        preview_scale: float,
        cell_w: int,
        cell_h: int,
        margin: int,
        preview_piece_offset_y: int,
    ) -> Rect | None:
        pygame = self._pygame

        preview_cell_w = int(cell_w * float(preview_scale))
        preview_cell_h = int(cell_h * float(preview_scale))
        try:
            ui_scale = float(getattr(client, 'ui_scale', 1.0) or 1.0)
        except Exception:
            ui_scale = 1.0
        preview_gap_x = max(0, int(round(1.0 * ui_scale)))
        preview_gap_y = max(4, int(round(preview_cell_h * 0.28)), int(round(10.0 * ui_scale)))
        step_x = max(1, int(preview_cell_w + preview_gap_x))
        step_y = max(1, int(preview_cell_h + preview_gap_y))
        positions = self.get_preview_positions(client, piece)
        min_x = min(p[0] for p in positions)
        max_x = max(p[0] for p in positions)
        min_y = min(p[1] for p in positions)
        max_y = max(p[1] for p in positions)
        piece_w = (max_x - min_x + 1) * step_x - preview_gap_x
        try:
            ox, oy = int(offset[0]), int(offset[1])
        except Exception:
            ox, oy = (0, 0)
        start_x = int(center_x) - piece_w // 2 + int(ox)
        y0 = int(getattr(client, '_content_offset_y', 0) or 0)
        start_y = int(y0 + margin + preview_piece_offset_y + int(oy))
        min_draw_x = None
        min_draw_y = None
        max_draw_x2 = None
        max_draw_y2 = None
        for x, y, block in positions:
            draw_x = start_x + (x - min_x) * step_x
            draw_y = start_y + (y - min_y) * step_y
            rect = pygame.Rect(int(draw_x), int(draw_y), int(preview_cell_w), int(preview_cell_h))
            client._draw_block(rect, block)
            try:
                if min_draw_x is None or int(draw_x) < int(min_draw_x):
                    min_draw_x = int(draw_x)
                if min_draw_y is None or int(draw_y) < int(min_draw_y):
                    min_draw_y = int(draw_y)
                x2 = int(draw_x + preview_cell_w)
                y2 = int(draw_y + preview_cell_h)
                if max_draw_x2 is None or x2 > int(max_draw_x2):
                    max_draw_x2 = int(x2)
                if max_draw_y2 is None or y2 > int(max_draw_y2):
                    max_draw_y2 = int(y2)
            except Exception:
                pass

        try:
            if min_draw_x is not None and min_draw_y is not None and max_draw_x2 is not None and max_draw_y2 is not None:
                return pygame.Rect(int(min_draw_x), int(min_draw_y), int(max_draw_x2 - min_draw_x), int(max_draw_y2 - min_draw_y))
        except Exception:
            return None
        return None

    def draw_preview_sword_next_to_piece(
        self,
        client,
        sword_value: str | None,
        piece_rect: Rect | None,
        panel_rect: Rect,
        *,
        side: str,
        sword_slot_rect: Rect | None = None,
    ) -> None:
        pygame = self._pygame

        try:
            if str(side).strip().lower() in ('left', 'right'):
                client._last_preview_sword_rect[str(side).strip().lower()] = None
        except Exception:
            pass

        if piece_rect is None:
            return
        if sword_value is None or str(sword_value).strip() == '':
            return

        try:
            st = client._resolve_sword_type(sword_value)
        except Exception:
            return

        try:
            ui_scale = float(getattr(client, 'ui_scale', 1.0) or 1.0)
        except Exception:
            ui_scale = 1.0
        pad = max(2, int(round(4 * ui_scale)))
        gap = max(3, int(round(4 * ui_scale)))

        up_nudge = int(round(8 * ui_scale))
        top_y = int(piece_rect.top - up_nudge)
        try:
            base_h = int(round(float(piece_rect.height) * 1.55))
        except Exception:
            base_h = 180
        desired_h = max(96, min(520, int(base_h)))
        try:
            bottom_limit = int(client.screen.get_height()) - pad
        except Exception:
            bottom_limit = int(top_y + desired_h)
        available_h = int(bottom_limit - top_y)
        max_h = int(max(24, min(int(desired_h), int(available_h))))
        if max_h <= 24:
            return

        slot = None
        try:
            if sword_slot_rect is not None:
                slot = sword_slot_rect
        except Exception:
            slot = None
        if slot is None:
            if str(side).strip().lower() == 'right':
                box_left = int(piece_rect.right + gap)
                box_right = int(panel_rect.right - pad)
            else:
                box_left = int(panel_rect.left + pad)
                box_right = int(piece_rect.left - gap)
        else:
            box_left = int(slot.left)
            box_right = int(slot.right)

        max_w = int(box_right - box_left)
        if max_w <= 24:
            return

        try:
            scale = float(getattr(client, '_preview_sword_scale', 1.0) or 1.0)
        except Exception:
            scale = 1.0
        scale = max(0.30, min(2.50, float(scale)))

        # Apply per-weapon tuning in addition to the global scale.
        try:
            sword_id = str(getattr(st, 'value', st) or '').strip().lower()
        except Exception:
            sword_id = ''
        try:
            per_weapon = float((getattr(client, '_preview_sword_scale_by_weapon', {}) or {}).get(str(sword_id), 1.0) or 1.0)
        except Exception:
            per_weapon = 1.0
        scale = max(0.30, min(2.50, float(scale) * float(per_weapon)))

        img = None
        try:
            inv_img = client._get_weapon_art_scaled(st)
        except Exception:
            inv_img = None
        try:
            if inv_img is not None and int(inv_img.get_width()) <= int(max_w) and int(inv_img.get_height()) <= int(max_h):
                img = inv_img
        except Exception:
            img = None

        if img is None:
            img = client._get_weapon_art_scaled_preview(st, max_w=max_w, max_h=max_h)
        if img is None:
            return

        if abs(float(scale) - 1.0) > 1e-6:
            try:
                fitted_w = int(img.get_width())
                fitted_h = int(img.get_height())
            except Exception:
                fitted_w, fitted_h = (0, 0)

            # IMPORTANT: don't scale an already-scaled sword image again; it causes blur.
            # Re-scale from the trimmed raw PNG to the exact final size (cached by AssetManager).
            try:
                tw = max(8, int(round(float(fitted_w) * float(scale))))
                th = max(8, int(round(float(fitted_h) * float(scale))))
                tw = min(tw, int(client.screen.get_width() * 0.92))
                th = min(th, int(client.screen.get_height() * 0.92))
            except Exception:
                tw, th = (fitted_w, fitted_h)

            tuned = None
            try:
                tuned = client._get_weapon_art_scaled_preview_exact(st, target_w=int(tw), target_h=int(th))
            except Exception:
                tuned = None

            if tuned is not None:
                img = tuned

        try:
            anchor_x = int(box_left + (max_w // 2))
            anchor_y = int(top_y + (max_h // 2))

            try:
                off = (getattr(client, '_preview_sword_offset_px', {}) or {}).get(str(side).strip().lower(), (0, 0))
                ox, oy = int(off[0]), int(off[1])
            except Exception:
                ox, oy = (0, 0)
            anchor_x = int(anchor_x + ox)
            anchor_y = int(anchor_y + oy)

            x = int(anchor_x - (img.get_width() // 2))
            y = int(anchor_y - (img.get_height() // 2))

            x = max(0, min(int(client.screen.get_width() - img.get_width()), int(x)))
            y = max(0, min(int(client.screen.get_height() - img.get_height()), int(y)))
            client.screen.blit(img, (int(x), int(y)))

            try:
                sd = str(side).strip().lower()
                if sd in ('left', 'right'):
                    client._last_preview_sword_rect[sd] = pygame.Rect(int(x), int(y), int(img.get_width()), int(img.get_height()))
            except Exception:
                pass
        except Exception:
            return

    def get_preview_positions(self, client, piece):
        positions = [(0, 0, piece.blocks[0])]
        if hasattr(piece, 'blocks') and len(piece.blocks) == 2:
            positions.append((0, -1, piece.blocks[1]))
        return positions
