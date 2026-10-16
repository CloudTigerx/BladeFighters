from __future__ import annotations

from typing import Any


class TrainingController:
    def __init__(self, *, pygame: Any):
        self._pygame = pygame

    # -----------------------------
    # Practice events
    # -----------------------------

    def start_practice_event(self, client: Any, kind: str) -> None:
        k = str(kind or '').strip().lower()
        if not k:
            return

        client._practice_active = True
        client._practice_kind = k
        client._practice_start_ms = int(self._pygame.time.get_ticks())
        client._practice_best_chain = 0
        client._practice_last_elapsed_ms = None

        # Always return to the exams submenu.
        client._practice_return_view = 'story_practice_exams'

        if k == 'speed_test':
            # Stopwatch: lose as quickly as possible.
            client._practice_duration_ms = 0
            client._start_match('mirror', None)
            return

        if k == 'boss_1v1':
            client._practice_duration_ms = 0
            # Story early boss should always use Rusty Sword.
            # Do not persist this as the user's global enemy sword preference.
            try:
                client._practice_prev_enemy_sword_value = str(getattr(client, '_enemy_sword_value', 'rusty_sword') or 'rusty_sword')
            except Exception:
                client._practice_prev_enemy_sword_value = 'rusty_sword'
            client._enemy_sword_value = 'rusty_sword'
            client._start_match('boss', None)
            return

        # Unknown practice kind -> cancel.
        client._practice_active = False
        client._practice_kind = None
        client._practice_duration_ms = 0

    def end_practice_to_story(self, client: Any, message: str) -> None:
        # Stop the game and return to story view with a status line.
        client._practice_active = False
        client._practice_kind = None
        client._practice_start_ms = 0
        client._practice_duration_ms = 0
        client._practice_best_chain = int(getattr(client, '_practice_best_chain', 0) or 0)

        # Restore enemy sword preference after boss practice.
        try:
            prev = getattr(client, '_practice_prev_enemy_sword_value', None)
        except Exception:
            prev = None
        if prev is not None:
            try:
                client._enemy_sword_value = str(prev)
            except Exception:
                pass
            try:
                client._practice_prev_enemy_sword_value = None
            except Exception:
                pass

        client.state = 'menu'
        client._menu_view = str(getattr(client, '_practice_return_view', 'story_practice_exams') or 'story_practice_exams')
        try:
            client._menu_selected = 0
        except Exception:
            pass
        client._menu_pause_active = False
        client._menu_pause_buttons = []
        client._set_menu_status(str(message or ''))
        client._last_snapshot = None

    def practice_tick(self, client: Any) -> None:
        if not bool(getattr(client, '_practice_active', False)):
            return
        if client.state != 'game':
            return

        kind = str(getattr(client, '_practice_kind', '') or '').strip().lower()
        now_ms = int(self._pygame.time.get_ticks())
        start_ms = int(getattr(client, '_practice_start_ms', 0) or 0)
        elapsed_ms = max(0, int(now_ms - start_ms))
        client._practice_last_elapsed_ms = int(elapsed_ms)

        # Track chain score live (only increases when a chain completes).
        try:
            snap = client._last_snapshot or {}
            sp = ((snap.get('scoring', {}) or {}).get('player', {}) or {})
            best = int(sp.get('max_chain', 0) or 0)
            if best > int(getattr(client, '_practice_best_chain', 0) or 0):
                client._practice_best_chain = int(best)
        except Exception:
            pass

        if kind not in ('speed_test', 'boss_1v1'):
            self.end_practice_to_story(client, 'Practice: removed')
            return

    def draw_practice_overlay(self, client: Any, snap: dict) -> None:
        if not bool(getattr(client, '_practice_active', False)):
            return
        if client.state not in ('game', 'pause', 'postgame'):
            return

        kind = str(getattr(client, '_practice_kind', '') or '').strip().lower()
        if not kind:
            return

        try:
            w = int(client.screen.get_width())
            h = int(client.screen.get_height())
        except Exception:
            return

        try:
            ui_scale = float(getattr(client, 'ui_scale', 1.0) or 1.0)
        except Exception:
            ui_scale = 1.0

        try:
            elapsed_ms = int(getattr(client, '_practice_last_elapsed_ms', None) or 0)
        except Exception:
            elapsed_ms = 0

        def fmt_ms(ms: int) -> str:
            ms = int(max(0, ms))
            sec = int(ms // 1000)
            m = int(sec // 60)
            s = int(sec % 60)
            return f"{m}:{s:02d}"

        title = 'Practice'
        lines: list[str] = []
        if kind == 'speed_test':
            title = 'Speed test'
            lines = [f"Time: {fmt_ms(elapsed_ms)}", 'Goal: defeat yourself']
        elif kind == 'boss_1v1':
            title = '1v1 (Boss)'
            lines = [f"Time: {fmt_ms(elapsed_ms)}"]
        else:
            lines = [f"Time: {fmt_ms(elapsed_ms)}"]

        try:
            pad = int(max(10, round(12 * ui_scale)))
            line_gap = int(max(2, round(6 * ui_scale)))
            font_title = self._pygame.font.SysFont(None, max(18, int(round(34 * ui_scale))))
            font_body = self._pygame.font.SysFont(None, max(16, int(round(26 * ui_scale))))
        except Exception:
            font_title = client.ui_font
            font_body = client.ui_font
            pad = 10
            line_gap = 4

        try:
            r_title = font_title.render(title, True, (245, 245, 245))
            r_lines = [font_body.render(t, True, (240, 220, 140)) for t in lines]
            panel_w = max([r_title.get_width()] + [r.get_width() for r in r_lines]) + 2 * pad
            panel_h = (
                r_title.get_height()
                + (line_gap if r_lines else 0)
                + sum(r.get_height() for r in r_lines)
                + max(0, len(r_lines) - 1) * line_gap
                + 2 * pad
            )
            x = int(w * 0.04)
            y = int(h * 0.06)
            panel = self._pygame.Surface((int(panel_w), int(panel_h)), flags=self._pygame.SRCALPHA)
            panel.fill((0, 0, 0, 150))
            client.screen.blit(panel, (x, y))
            self._pygame.draw.rect(client.screen, (255, 255, 255), self._pygame.Rect(x, y, panel_w, panel_h), width=2, border_radius=10)
            client.screen.blit(r_title, (int(x + pad), int(y + pad)))
            yy = int(y + pad + r_title.get_height() + (line_gap if r_lines else 0))
            for rr in r_lines:
                client.screen.blit(rr, (int(x + pad), yy))
                yy += int(rr.get_height() + line_gap)
        except Exception:
            pass

    # -----------------------------
    # Tutorial
    # -----------------------------

    def start_tutorial(self, client: Any) -> None:
        # Use mirror mode so the player can see attacks bounce back in a safe way.
        client._tutorial_active = True
        client._tutorial_step = 0
        client._tutorial_done = False
        client._tutorial_progress = {
            'moved': False,
            'rot_ccw': False,
            'rot_cw': False,
            'fast': False,
        }
        client._tutorial_hint_text = ''
        client._tutorial_cluster_setup_done = False
        client._tutorial_controls_locked = False
        client._tutorial_combo_chain_started = False
        client._tutorial_inbound_injected = False
        client._tutorial_fast_hold_start_ms = None
        client._start_match('mirror', None)

    def tutorial_step_text(self, client: Any) -> str:
        step = int(getattr(client, '_tutorial_step', 0) or 0)
        if bool(getattr(client, '_tutorial_done', False)):
            return 'Tutorial complete.'
        if step == 0:
            return 'Move the falling piece: press Left or Right. (You can also hold Left/Right to auto-move.)'
        if step == 1:
            return 'Rotate counter-clockwise: press Up.'
        if step == 2:
            return 'Rotate clockwise: press Down.'
        if step == 3:
            return 'Fall faster: press and hold Space.'
        if step == 4:
            return 'Scripted combo: hold Space to drop the breaker and clear a 2×2 cluster. (Controls are locked for this drop.)'
        if step == 5:
            # Provide a quick explanation of the two attack types plus live inbound status.
            try:
                inbound = getattr(client.session.player, 'inbound_handler', None)
                ps = int(getattr(inbound, 'pending_in_sprinkle', 0) or 0)
                pk = int(getattr(inbound, 'pending_in_strike', 0) or 0)
                d = int(getattr(inbound, 'inbound_delay', 0) or 0)
            except Exception:
                ps, pk, d = 0, 0, 0

            try:
                sc = (getattr(client.session, 'scoring', None) or None)
                sent_s = int(getattr(getattr(sc, 'player', None), 'sprinkles_sent', 0) or 0)
                sent_k = int(getattr(getattr(sc, 'player', None), 'strikes_sent', 0) or 0)
            except Exception:
                sent_s, sent_k = 0, 0

            return (
                'Attacks 101: STRIKE drops a compact sword/cluster. SPRINKLE scatters single blocks. '
                'Clears + chains generate attacks. In Mirror training, anything you send is reflected back to you. '
                f'Sent so far: strike={sent_k}, sprinkle={sent_s}. '
                f'Inbound queued: strike={pk}, sprinkle={ps}. Landing delay: {d} frames. '
                'Press Enter to continue.'
            )
        if step == 6:
            return 'All set. Press Enter to collect +25 Gold and return to the Academy.'
        return 'Press Enter to continue.'

    def advance_tutorial(self, client: Any) -> None:
        if not bool(getattr(client, '_tutorial_active', False)):
            return
        if bool(getattr(client, '_tutorial_done', False)):
            return

        step = int(getattr(client, '_tutorial_step', 0) or 0)
        prog = getattr(client, '_tutorial_progress', {}) or {}

        if step == 0 and bool(prog.get('moved', False)):
            client._tutorial_step = 1
            return
        if step == 1 and bool(prog.get('rot_ccw', False)):
            client._tutorial_step = 2
            return
        if step == 2 and bool(prog.get('rot_cw', False)):
            client._tutorial_step = 3
            return
        if step == 3 and bool(prog.get('fast', False)):
            client._tutorial_step = 4
            return

    def tutorial_configure_combo_stage(self, client: Any) -> None:
        """Reset the match and set up a deterministic 2×2 + small combo."""
        if bool(getattr(client, '_tutorial_cluster_setup_done', False)):
            return

        # Reset the session so the board is clean and predictable.
        try:
            client._enemy_style = 'mirror'
            client._boss_level = None
        except Exception:
            pass
        try:
            client._reset_session()
        except Exception:
            return

        # Lock controls for this scripted drop (player already learned movement earlier).
        client._tutorial_controls_locked = True
        client._tutorial_cluster_setup_done = True
        client._tutorial_inbound_injected = False
        client._tutorial_combo_chain_started = False

        # Board setup (y increases downward; y=11 is bottom).
        # Goal: player drops a red breaker piece in column 3, completing a red 2×2.
        # Then a blue breaker+normal collapse together to trigger a 2nd clear (small combo).
        try:
            from swordfighting_new.pieces.piece import Block, Piece
        except Exception:
            return

        try:
            board = client.session.player.get_board()
            board.clear()

            # Red 2×2 missing one cell at (3,10).
            board.set_piece(2, 11, Block('red', is_breaker=False))
            board.set_piece(2, 10, Block('red', is_breaker=False))
            board.set_piece(3, 11, Block('red', is_breaker=False))

            # Blue combo setup (kept OUT of column 3 so the red breaker can land).
            # We build red "scaffolding" in columns 4-5 that is connected to the
            # red clear (via the bottom row), so it will be removed in the first
            # chain pass. That drop makes the separated blue blocks fall and end up
            # adjacent, triggering a real follow-up clear (combo).
            #
            # Column 4: blue breaker sits on red supports at y>=7
            for yy in range(7, 12):
                board.set_piece(4, yy, Block('red', is_breaker=False))
            board.set_piece(4, 6, Block('blue', is_breaker=True))

            # Column 5: blue normal sits slightly higher so it is NOT adjacent at start
            for yy in range(6, 12):
                board.set_piece(5, yy, Block('red', is_breaker=False))
            board.set_piece(5, 5, Block('blue', is_breaker=False))
        except Exception:
            pass

        # Force the current piece to be a red breaker so the player only needs to fast-drop.
        try:
            forced = Piece([Block('red', is_breaker=True), Block('red', is_breaker=False)])
            forced.x = 3
            forced.y = -1
            forced.orientation = 0
            forced.controllable = True
            client.session.player.movement.current_piece = forced
        except Exception:
            pass

    def tutorial_tick(self, client: Any) -> None:
        if not bool(getattr(client, '_tutorial_active', False)):
            return
        if client.state != 'game':
            return

        step = int(getattr(client, '_tutorial_step', 0) or 0)

        # Step 3: require a short hold (not a tap) so the player actually experiences fast-fall.
        if step == 3:
            try:
                now_ms = int(self._pygame.time.get_ticks())
            except Exception:
                now_ms = 0
            try:
                prog = getattr(client, '_tutorial_progress', {}) or {}
            except Exception:
                prog = {}

            if bool(getattr(client, 'fast', False)):
                if getattr(client, '_tutorial_fast_hold_start_ms', None) is None:
                    client._tutorial_fast_hold_start_ms = int(now_ms)
                else:
                    held_ms = int(now_ms) - int(getattr(client, '_tutorial_fast_hold_start_ms', 0) or 0)
                    if held_ms >= 250 and not bool(prog.get('fast', False)):
                        try:
                            client._tutorial_progress['fast'] = True
                            self.advance_tutorial(client)
                        except Exception:
                            pass
            else:
                client._tutorial_fast_hold_start_ms = None

        # Configure the deterministic cluster/combo stage the first time we enter step 4.
        if step == 4:
            self.tutorial_configure_combo_stage(client)

            # Advance based on the real chain runner lifecycle rather than scoring.
            try:
                chain_active = bool(getattr(getattr(client.session, 'player', None).chain_runner, 'active', False))  # type: ignore
            except Exception:
                chain_active = False

            if chain_active:
                client._tutorial_combo_chain_started = True
            if bool(getattr(client, '_tutorial_combo_chain_started', False)) and (not chain_active):
                # Unlock controls after the scripted event resolves.
                client._tutorial_controls_locked = False
                client._tutorial_step = 5
                return

        if step == 5:
            # Ensure there is something inbound to see (in case the earlier clear generated none).
            try:
                inbound = getattr(client.session.player, 'inbound_handler', None)
                pending = int(getattr(inbound, 'pending_in_sprinkle', 0) or 0) + int(getattr(inbound, 'pending_in_strike', 0) or 0)
            except Exception:
                pending = 0

            if pending <= 0 and not bool(getattr(client, '_tutorial_inbound_injected', False)):
                try:
                    from swordfighting_new.attacks import Attack, AttackKind

                    client.session.player.receive_attacks([
                        Attack(AttackKind.STRIKE, 4, delay=0, meta={'tutorial': True, 'sword_shape': (2, 2)})
                    ])
                except Exception:
                    pass
                client._tutorial_inbound_injected = True

    def complete_tutorial_and_return(self, client: Any) -> None:
        # One-way completion: award once and return to the story academy screen.
        client._tutorial_active = False
        client._tutorial_done = False
        client._tutorial_step = 0
        client._tutorial_progress = {}
        client._tutorial_hint_text = ''
        client._tutorial_cluster_setup_done = False
        client._tutorial_controls_locked = False
        client._tutorial_combo_chain_started = False
        client._tutorial_inbound_injected = False

        # Reward (persisted).
        client._award_gold(25)

        # Story progression: tutorial complete -> enable the academy/menu2 cutscene.
        try:
            client._story_swift_tutorial_complete = True
            client._story_post_tutorial_step = 0
            client._persist_story_progress(
                tutorial_complete=True,
                player_name=str(getattr(client, '_story_player_name', '') or '') or None,
            )
        except Exception:
            pass

        # Return to academy/menu1.
        client.state = 'menu'
        client._menu_view = 'story_intro'
        client._set_menu_status('')
        client._last_snapshot = None

    def draw_tutorial_overlay(self, client: Any, *, preview_panel_width: int, margin: int) -> None:
        if not bool(getattr(client, '_tutorial_active', False)):
            return

        try:
            w = int(client.screen.get_width())
            h = int(client.screen.get_height())
        except Exception:
            return

        try:
            pad = int(max(10, round(14 * float(getattr(client, 'ui_scale', 1.0) or 1.0))))
            # Prefer the right-side preview panel area so we never cover the puzzle board.
            rx = int(getattr(client, 'enemy_offset_x', 0) or 0) + int(getattr(client, 'board_px_w', 0) or 0)
            ry = int(getattr(client, '_content_offset_y', 0) or 0)
            r_w = int(preview_panel_width)
            r_h = int(getattr(client, 'board_px_h', 0) or 0)

            # Fallback to the old bottom overlay if the right panel is too narrow.
            min_side_w = int(max(280, 260 * float(getattr(client, 'ui_scale', 1.0) or 1.0)))
            if r_w >= min_side_w and r_h >= 120:
                box_w = int(max(min_side_w, r_w - 2 * int(margin)))
                box_h = int(max(180, min(r_h, int(h * 0.48))))
                x = int(rx + int(margin))
                y = int(max(0, ry + int(margin)))
            else:
                box_w = int(max(520, w * 0.46))
                box_h = int(max(140, h * 0.22))
                x = int(w * 0.04)
                y = int(h - box_h - h * 0.04)

            rect = self._pygame.Rect(int(x), int(y), int(box_w), int(box_h))

            panel = self._pygame.Surface((int(rect.w), int(rect.h)), flags=self._pygame.SRCALPHA)
            panel.fill((0, 0, 0, 170))
            client.screen.blit(panel, (int(rect.x), int(rect.y)))
            self._pygame.draw.rect(client.screen, (255, 255, 255), rect, width=2, border_radius=10)

            title = client.ui_font.render('Tutorial', True, (245, 245, 245))
            client.screen.blit(title, (int(rect.x + pad), int(rect.y + pad)))

            msg = client._tutorial_step_text()
            lines = client._wrap_text(msg, client.ui_font, int(rect.w - 2 * pad))
            yy = int(rect.y + pad + title.get_height() + max(4, int(6 * float(getattr(client, 'ui_scale', 1.0) or 1.0))))
            for ln in lines[:6]:
                surf = client.ui_font.render(ln, True, (240, 220, 140))
                client.screen.blit(surf, (int(rect.x + pad), yy))
                yy += int(surf.get_height() + max(2, int(4 * float(getattr(client, 'ui_scale', 1.0) or 1.0))))

            hint = client.preview_font.render('Esc/P = Pause', True, (220, 220, 220))
            client.screen.blit(hint, (int(rect.right - pad - hint.get_width()), int(rect.bottom - pad - hint.get_height())))
        except Exception:
            pass
