from __future__ import annotations

from typing import Any

from swordfighting_new.strike_test_harness import StrikeTestHarness


class StrikeTestController:
    def __init__(self, *, pygame: Any):
        self._pygame = pygame

    def enter_strike_test(
        self,
        client: Any,
        *,
        timing: Any,
        attack_delay_frames: int,
        bulk_delivery: bool,
    ) -> None:
        # Force gridlines visible in Strike Test for clarity.
        try:
            client._strike_prev_show_grid = bool(getattr(client, '_show_grid', False))
        except Exception:
            client._strike_prev_show_grid = None
        try:
            client._show_grid = True
        except Exception:
            pass
        try:
            client._strike_test = StrikeTestHarness(
                timing=timing,
                attack_delay_frames=int(attack_delay_frames),
                bulk_delivery=bool(bulk_delivery),
            )
        except Exception:
            client._strike_test = None
        client._strike_drag_spec = None
        client._strike_drag_active = False
        client._strike_drag_block = None
        client._strike_drag_origin = None
        client._strike_last_run_attacks = []
        client._strike_ui = {}
        client._strike_chain_len = 1
        client._strike_status_text = ''
        client.state = 'strike_test'

    def exit_strike_test(self, client: Any) -> None:
        try:
            if client._strike_prev_show_grid is not None:
                client._show_grid = bool(client._strike_prev_show_grid)
        except Exception:
            pass
        client._strike_prev_show_grid = None
        client._strike_test = None
        client._strike_drag_spec = None
        client._strike_drag_active = False
        client._strike_drag_block = None
        client._strike_drag_origin = None
        client._strike_last_run_attacks = []
        client._strike_ui = {}
        client._strike_chain_len = 1
        client._strike_status_text = ''
        client.state = 'menu'
        client._menu_view = 'main'

    def strike_test_run(self, client: Any) -> None:
        """Run a live breaker chain sim and immediately settle inbound output.

        This is intentionally gameplay-faithful: if no breaker triggers, the chain
        has 0 passes and generates no attacks.
        """
        if client._strike_test is None:
            client._strike_last_run_attacks = []
            client._strike_status_text = 'Strike Test not ready'
            return

        try:
            client._strike_last_run_attacks = list(client._strike_test.run_live(max_chain_frames=3600) or [])
            # Make the result obvious immediately: skip the inbound countdown.
            try:
                client._strike_test.output_inbound.inbound_delay = 0
            except Exception:
                pass
            # And settle the output so combo-scaled swords are fully visible.
            try:
                client._strike_test.settle(max_frames=800)
            except Exception:
                pass

            try:
                passes = int(getattr(client._strike_test, 'last_live_chain_passes', 0) or 0)
            except Exception:
                passes = 0
            n_attacks = 0
            try:
                n_attacks = int(len(client._strike_last_run_attacks))
            except Exception:
                n_attacks = 0

            if passes <= 0:
                client._strike_status_text = 'No chain: place a breaker adjacent to same-color blocks'
            else:
                client._strike_status_text = f'Ran chain: {passes} pass(es), {n_attacks} attack(s)'
        except Exception as e:
            client._strike_last_run_attacks = []
            # Keep error short so it fits UI; details can be reproduced via pytest.
            try:
                msg = str(e)
            except Exception:
                msg = 'unknown error'
            msg = (msg[:90] + '…') if len(msg) > 90 else msg
            client._strike_status_text = f'Run failed: {msg}'

    def _strike_test_palette_specs(self) -> list[tuple[str, str | None, bool]]:
        # (kind, color, breaker)
        return [
            ('empty', None, False),
            ('block', 'red', False),
            ('block', 'blue', False),
            ('block', 'yellow', False),
            ('block', 'green', False),
            ('block', 'red', True),
            ('block', 'blue', True),
            ('block', 'yellow', True),
            ('block', 'green', True),
        ]

    def _strike_test_spec_from_block(self, blk) -> tuple[str, str | None, bool] | None:
        if blk is None:
            return ('empty', None, False)
        try:
            color = getattr(blk, 'color', None)
        except Exception:
            color = None
        try:
            breaker = bool(getattr(blk, 'is_breaker', False))
        except Exception:
            breaker = False
        if not isinstance(color, str) or not color:
            return None
        return ('block', str(color), bool(breaker))

    def _strike_test_make_block(self, spec: tuple[str, str | None, bool]):
        kind, color, breaker = spec
        if kind == 'empty':
            return None
        try:
            from swordfighting_new.pieces.piece import Block
        except Exception:
            return None
        try:
            return Block(str(color), is_breaker=bool(breaker))
        except Exception:
            return None

    def _strike_test_cell_from_pos(
        self,
        board: Any,
        *,
        offset_x: int,
        offset_y: int,
        pos: Any,
        margin: int,
        cell_w: int,
        cell_h: int,
    ) -> tuple[int, int] | None:
        try:
            px, py = int(pos[0]), int(pos[1])
        except Exception:
            return None
        gx = px - int(offset_x) - int(margin)
        gy = py - int(offset_y) - int(margin)
        if gx < 0 or gy < 0:
            return None
        try:
            x = int(gx // max(1, int(cell_w)))
            y = int(gy // max(1, int(cell_h)))
        except Exception:
            return None
        try:
            if 0 <= x < int(board.WIDTH) and 0 <= y < int(board.HEIGHT):
                return (x, y)
        except Exception:
            return None
        return None

    def strike_test_rebuild_ui(
        self,
        client: Any,
        *,
        margin: int,
        cell_w: int,
        cell_h: int,
        preview_panel_width: int,
        board_gap: int,
    ) -> None:
        # Layout palette in the left preview panel and a single Run button below.
        ui: dict[str, Any] = {}
        w = int(client.screen.get_width())
        h = int(client.screen.get_height())
        ui['size'] = (int(w), int(h))

        # Always lay out TWO boards in Strike Test (input + output), regardless of
        # the current MatchSession enemy style (HP-mode vs Rubix).
        try:
            content_w = int(preview_panel_width) + int(client.board_px_w) * 2 + int(board_gap)
        except Exception:
            content_w = int(preview_panel_width) + int(6 * int(cell_w) + int(margin) * 2) * 2 + int(board_gap)
        x_pad = max(0, int((w - int(content_w)) // 2))
        input_ox = int(x_pad + int(preview_panel_width))
        output_ox = int(input_ox + int(client.board_px_w) + int(board_gap))
        y0 = int(getattr(client, '_content_offset_y', 0) or 0)

        ui['input_ox'] = int(input_ox)
        ui['output_ox'] = int(output_ox)
        ui['oy'] = int(y0)

        # Palette grid (2 cols) on the left panel.
        specs = self._strike_test_palette_specs()
        cols = 2
        cell_w = max(10, int(cell_w))
        cell_h = max(10, int(cell_h))
        gap = max(6, int(round(8 * float(getattr(client, 'ui_scale', 1.0) or 1.0))))

        panel_x = int(x_pad)
        pad_x = max(6, int(round(10 * float(getattr(client, 'ui_scale', 1.0) or 1.0))))
        start_x = int(panel_x + pad_x)
        start_y = int(y0 + int(margin) + max(8, int(round(10 * float(getattr(client, 'ui_scale', 1.0) or 1.0)))))

        tiles: list[dict[str, Any]] = []
        for i, spec in enumerate(specs):
            r = int(i // cols)
            c = int(i % cols)
            rx = int(start_x + c * (cell_w + gap))
            ry = int(start_y + r * (cell_h + gap))
            rect = self._pygame.Rect(rx, ry, cell_w, cell_h)
            tiles.append({'spec': spec, 'rect': rect})
        ui['palette'] = tiles

        # Run button (use menu button art if available).
        btn_img = getattr(client, '_menu_button_scaled', None)
        if btn_img is not None:
            bw, bh = int(btn_img.get_width()), int(btn_img.get_height())
        else:
            bw, bh = int(min(w * 0.28, 420)), max(56, int(round(72 * float(getattr(client, 'ui_scale', 1.0) or 1.0))))

        # Place the Run button off to the RIGHT, away from the boards.
        # Prefer sitting just to the right of the output board; if that doesn't fit,
        # clamp inside the screen with a margin.
        try:
            m2 = max(10, int(round(14 * float(getattr(client, 'ui_scale', 1.0) or 1.0))))
        except Exception:
            m2 = 14
        try:
            out_right = int(output_ox + int(client.board_px_w))
        except Exception:
            out_right = int(output_ox + 6 * int(cell_w) + int(margin) * 2)
        run_x = int(out_right + m2)
        if run_x + int(bw) > int(w) - m2:
            run_x = int(w - m2 - int(bw))
        # Vertically center next to the boards.
        try:
            run_y = int(y0 + int(client.board_px_h) / 2 - int(bh) / 2)
        except Exception:
            run_y = int(h - bh - m2)
        run_y = max(m2, min(int(h) - m2 - int(bh), int(run_y)))
        ui['run_rect'] = self._pygame.Rect(run_x, run_y, bw, bh)
        client._strike_ui = ui

    def handle_strike_test_event(
        self,
        client: Any,
        event: Any,
        *,
        margin: int,
        cell_w: int,
        cell_h: int,
        preview_panel_width: int,
        board_gap: int,
    ) -> None:
        # Esc/back exits to main menu.
        if event.type == self._pygame.KEYDOWN:
            try:
                if client._event_is_action(event.key, 'ui_back') or client._event_is_action(event.key, 'pause'):
                    self.exit_strike_test(client)
                    return
            except Exception:
                pass

            # Enter / confirm runs the live chain simulation.
            try:
                if client._event_is_action(event.key, 'ui_confirm'):
                    self.strike_test_run(client)
                    return
            except Exception:
                pass

        try:
            cur_sz = (int(client.screen.get_width()), int(client.screen.get_height()))
        except Exception:
            cur_sz = None
        try:
            ui_sz = (
                tuple(client._strike_ui.get('size'))
                if isinstance(getattr(client, '_strike_ui', None), dict) and client._strike_ui.get('size') is not None
                else None
            )
        except Exception:
            ui_sz = None

        if (not getattr(client, '_strike_ui', None)) or (cur_sz is not None and ui_sz != cur_sz):
            try:
                self.strike_test_rebuild_ui(
                    client,
                    margin=margin,
                    cell_w=cell_w,
                    cell_h=cell_h,
                    preview_panel_width=preview_panel_width,
                    board_gap=board_gap,
                )
            except Exception:
                client._strike_ui = {}

        if event.type == self._pygame.MOUSEBUTTONDOWN and int(getattr(event, 'button', 0) or 0) == 1:
            pos = getattr(event, 'pos', None)
            if pos is None:
                return

            # Run button
            try:
                rr = client._strike_ui.get('run_rect')
                if rr is not None and rr.collidepoint(pos):
                    self.strike_test_run(client)
                    return
            except Exception:
                pass

            # Palette pick
            try:
                for t in (client._strike_ui.get('palette', []) or []):
                    rect = t.get('rect')
                    if rect is not None and rect.collidepoint(pos):
                        client._strike_drag_spec = t.get('spec')
                        client._strike_drag_active = True
                        client._strike_drag_block = None
                        client._strike_drag_origin = None
                        return
            except Exception:
                pass

            # Pick up an existing block from the INPUT board so it can be moved.
            try:
                if client._strike_test is not None:
                    try:
                        input_ox = int(client._strike_ui.get('input_ox', client.player_offset_x) or client.player_offset_x)
                    except Exception:
                        input_ox = int(client.player_offset_x)
                    try:
                        oy = int(client._strike_ui.get('oy', getattr(client, '_content_offset_y', 0) or 0) or 0)
                    except Exception:
                        oy = int(getattr(client, '_content_offset_y', 0) or 0)

                    cell = self._strike_test_cell_from_pos(
                        client._strike_test.input_board,
                        offset_x=int(input_ox),
                        offset_y=int(oy),
                        pos=pos,
                        margin=margin,
                        cell_w=cell_w,
                        cell_h=cell_h,
                    )
                    if cell is not None:
                        x, y = int(cell[0]), int(cell[1])
                        blk = client._strike_test.input_board.get_piece(x, y)
                        if blk not in (None, client._strike_test.input_board.EMPTY):
                            spec = self._strike_test_spec_from_block(blk)
                            if spec is not None and spec[0] != 'empty':
                                # Remove from the board while dragging; if drop fails, we'll restore.
                                try:
                                    client._strike_test.input_board.set_piece(x, y, client._strike_test.input_board.EMPTY)
                                except Exception:
                                    pass
                                client._strike_drag_spec = spec
                                client._strike_drag_block = blk
                                client._strike_drag_origin = (x, y)
                                client._strike_drag_active = True
                                return
            except Exception:
                pass

        if event.type == self._pygame.MOUSEBUTTONUP and int(getattr(event, 'button', 0) or 0) == 1:
            if not bool(getattr(client, '_strike_drag_active', False)):
                return
            client._strike_drag_active = False

            if client._strike_test is None:
                client._strike_drag_spec = None
                return

            pos = getattr(event, 'pos', None)
            if pos is None:
                client._strike_drag_spec = None
                return

            # Snap placement onto the INPUT board.
            try:
                input_ox = int(client._strike_ui.get('input_ox', client.player_offset_x) or client.player_offset_x)
            except Exception:
                input_ox = int(client.player_offset_x)
            try:
                oy = int(client._strike_ui.get('oy', getattr(client, '_content_offset_y', 0) or 0) or 0)
            except Exception:
                oy = int(getattr(client, '_content_offset_y', 0) or 0)
            cell = self._strike_test_cell_from_pos(
                client._strike_test.input_board,
                offset_x=int(input_ox),
                offset_y=int(oy),
                pos=pos,
                margin=margin,
                cell_w=cell_w,
                cell_h=cell_h,
            )
            if cell is None:
                # Dropped out of bounds: if we picked up an existing block, restore it.
                try:
                    if client._strike_drag_block is not None and client._strike_drag_origin is not None:
                        ox, oy2 = client._strike_drag_origin
                        client._strike_test.input_board.set_piece(int(ox), int(oy2), client._strike_drag_block)
                except Exception:
                    pass
                client._strike_drag_spec = None
                client._strike_drag_block = None
                client._strike_drag_origin = None
                return
            x, y = int(cell[0]), int(cell[1])
            spec = client._strike_drag_spec
            drag_block = client._strike_drag_block
            drag_origin = client._strike_drag_origin

            client._strike_drag_spec = None
            client._strike_drag_block = None
            client._strike_drag_origin = None

            if not spec and drag_block is None:
                return

            # If we picked up a real block from the board, drop that exact object.
            if drag_block is not None:
                try:
                    client._strike_test.input_board.set_piece(x, y, drag_block)
                except Exception:
                    # If placement fails for any reason, try restoring to origin.
                    try:
                        if drag_origin is not None:
                            ox, oy2 = drag_origin
                            client._strike_test.input_board.set_piece(int(ox), int(oy2), drag_block)
                    except Exception:
                        pass
                return

            kind, _color, _breaker = spec
            if kind == 'empty':
                try:
                    client._strike_test.input_board.set_piece(x, y, client._strike_test.input_board.EMPTY)
                except Exception:
                    pass
                return

            blk = self._strike_test_make_block(spec)
            if blk is None:
                return
            try:
                client._strike_test.input_board.set_piece(x, y, blk)
            except Exception:
                pass

    def draw_strike_test(
        self,
        client: Any,
        *,
        bg: tuple[int, int, int],
        margin: int,
        cell_w: int,
        cell_h: int,
        preview_panel_width: int,
        board_gap: int,
    ) -> None:
        client.screen.fill(bg)
        client._now_ms = self._pygame.time.get_ticks()

        if client._strike_test is None:
            try:
                txt = client.ui_font.render('Strike Test failed to initialize', True, (240, 240, 240))
                client.screen.blit(txt, (int(client.screen.get_width() * 0.08), int(client.screen.get_height() * 0.10)))
            except Exception:
                pass
            return

        try:
            cur_sz = (int(client.screen.get_width()), int(client.screen.get_height()))
        except Exception:
            cur_sz = None
        try:
            ui_sz = (
                tuple(client._strike_ui.get('size'))
                if isinstance(getattr(client, '_strike_ui', None), dict) and client._strike_ui.get('size') is not None
                else None
            )
        except Exception:
            ui_sz = None

        if (not getattr(client, '_strike_ui', None)) or (cur_sz is not None and ui_sz != cur_sz):
            try:
                self.strike_test_rebuild_ui(
                    client,
                    margin=margin,
                    cell_w=cell_w,
                    cell_h=cell_h,
                    preview_panel_width=preview_panel_width,
                    board_gap=board_gap,
                )
            except Exception:
                client._strike_ui = {}

        try:
            input_ox = int(client._strike_ui.get('input_ox', client.player_offset_x) or client.player_offset_x)
        except Exception:
            input_ox = int(client.player_offset_x)
        try:
            output_ox = int(client._strike_ui.get('output_ox', client.enemy_offset_x) or client.enemy_offset_x)
        except Exception:
            output_ox = int(client.enemy_offset_x)
        y0 = int(client._strike_ui.get('oy', getattr(client, '_content_offset_y', 0) or 0) or 0)

        # Boards
        try:
            client._draw_board(client._strike_test.input_board, None, [], offset_x=int(input_ox), offset_y=y0)
        except Exception:
            pass
        try:
            fallers = list(getattr(getattr(client._strike_test, 'output_inbound', None), 'garbage_fallers', None) or [])
        except Exception:
            fallers = []
        try:
            client._draw_board(
                client._strike_test.output_board,
                None,
                fallers,
                offset_x=int(output_ox),
                offset_y=y0,
                draw_fallers_headroom=True,
            )
        except Exception:
            pass

        # Labels
        try:
            client.screen.blit(client.ui_font.render('Input', True, (220, 220, 220)), (int(input_ox + int(margin) + 2), int(y0 + 2)))
            client.screen.blit(client.ui_font.render('Output', True, (220, 220, 220)), (int(output_ox + int(margin) + 2), int(y0 + 2)))
        except Exception:
            pass

        # Palette
        try:
            for t in (client._strike_ui.get('palette', []) or []):
                rect = t.get('rect')
                spec = t.get('spec')
                if rect is None or not spec:
                    continue
                kind, _color, _breaker = spec
                if kind == 'empty':
                    self._pygame.draw.rect(client.screen, (70, 70, 95), rect, width=2, border_radius=6)
                    continue
                blk = self._strike_test_make_block(spec)
                if blk is None:
                    continue
                client._draw_block(rect, blk)

                # Selected highlight
                try:
                    if client._strike_drag_spec == spec:
                        self._pygame.draw.rect(
                            client.screen,
                            (255, 220, 120),
                            rect,
                            width=max(2, int(round(3 * float(getattr(client, 'ui_scale', 1.0) or 1.0)))),
                            border_radius=6,
                        )
                except Exception:
                    pass
        except Exception:
            pass

        # Run button
        rr = client._strike_ui.get('run_rect')
        if rr is not None:
            btn_img_normal = getattr(client, '_menu_button_scaled', None)
            btn_img_hover = getattr(client, '_menu_button_hover_scaled', None) or btn_img_normal
            btn_img_pressed = getattr(client, '_menu_button_pressed_scaled', None) or btn_img_hover or btn_img_normal
            try:
                mouse_pos = self._pygame.mouse.get_pos()
            except Exception:
                mouse_pos = (0, 0)
            try:
                mouse_down = bool(self._pygame.mouse.get_pressed()[0])
            except Exception:
                mouse_down = False
            hovered = False
            try:
                hovered = bool(rr.collidepoint(mouse_pos))
            except Exception:
                hovered = False
            pressed = bool(mouse_down and hovered)
            if btn_img_normal is None:
                self._pygame.draw.rect(client.screen, (40, 40, 60), rr, border_radius=12)
                self._pygame.draw.rect(client.screen, (180, 180, 200), rr, width=2, border_radius=12)
            else:
                src = btn_img_pressed if pressed else (btn_img_hover if hovered else btn_img_normal)
                client.screen.blit(src, (int(rr.x), int(rr.y)))
            try:
                client._blit_fitted_text(
                    'Run',
                    rr,
                    color=(255, 255, 255),
                    base_px=int(getattr(client, '_menu_button_font_px', 40) or 40),
                    max_lines=1,
                )
            except Exception:
                pass

            # Chain length label (so it’s obvious combo scaling is applied).
            try:
                passes = 0
                if client._strike_test is not None:
                    try:
                        passes = int(getattr(client._strike_test, 'last_live_chain_passes', 0) or 0)
                    except Exception:
                        passes = 0
                label = client.preview_font.render(f'Live chain passes: {passes}', True, (220, 220, 220))
                try:
                    ui_scale = float(getattr(client, 'ui_scale', 1.0) or 1.0)
                except Exception:
                    ui_scale = 1.0
                y_pass = int(rr.bottom + max(6, int(round(6 * ui_scale))))
                client.screen.blit(label, (int(rr.x), int(y_pass)))
            except Exception:
                pass

            # Last generated attack summary (helps verify combo scaling quickly).
            try:
                last = list(getattr(client, '_strike_last_run_attacks', None) or [])
            except Exception:
                last = []
            if last:
                try:
                    a0 = last[0]
                    meta = dict(getattr(a0, 'meta', None) or {})
                    shp = meta.get('sword_shape') or meta.get('horizontal_sword_shape')
                    p = meta.get('pass')
                    if shp is not None:
                        msg = f"Last: {getattr(a0, 'kind', 'atk')} shape={shp} pass={p}"
                    else:
                        msg = f"Last: {getattr(a0, 'kind', 'atk')} pass={p}"
                    ui_scale = float(getattr(client, 'ui_scale', 1.0) or 1.0)
                    y_msg = int(rr.bottom + max(6, int(round(6 * ui_scale))))
                    y_msg += max(18, int(round(18 * ui_scale)))
                    surf = client.preview_font.render(str(msg), True, (200, 200, 210))
                    client.screen.blit(surf, (int(rr.x), int(y_msg)))
                except Exception:
                    pass

            # Status line (so "Run" never feels like a no-op).
            try:
                msg = str(getattr(client, '_strike_status_text', '') or '')
            except Exception:
                msg = ''
            if msg:
                try:
                    y_msg = int(rr.bottom + max(6, int(round(6 * float(getattr(client, 'ui_scale', 1.0) or 1.0)))))
                    y_msg += max(36, int(round(36 * float(getattr(client, 'ui_scale', 1.0) or 1.0))))
                    surf = client.preview_font.render(msg, True, (200, 200, 210))
                    client.screen.blit(surf, (int(rr.x), int(y_msg)))
                except Exception:
                    pass
