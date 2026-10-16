from __future__ import annotations

import os
from typing import Any


class EventController:
    def __init__(self, *, pygame: Any):
        self._pygame = pygame

    def handle_events(self, client: Any) -> None:
        for event in self._pygame.event.get():
            # Coin panel resize (drag bottom corners). Works in gameplay HUD and menus.
            try:
                if event.type == self._pygame.MOUSEBUTTONDOWN and int(getattr(event, 'button', 0) or 0) == 1:
                    try:
                        mx, my = int(event.pos[0]), int(event.pos[1])
                    except Exception:
                        mx, my = (0, 0)

                    try:
                        ui_scale = float(getattr(client, 'ui_scale', 1.0) or 1.0)
                    except Exception:
                        ui_scale = 1.0
                    corner_px = int(max(10, round(14 * ui_scale)))

                    # Determine which panel kind is currently visible.
                    try:
                        view = str(getattr(client, '_menu_view', '') or '').strip().lower()
                    except Exception:
                        view = ''
                    if str(getattr(client, 'state', '') or '') == 'game':
                        kind = 'hud'
                    elif view.startswith('story_'):
                        kind = 'story'
                    else:
                        kind = 'menu'

                    rects = getattr(client, '_last_coin_panel_rects', None) or {}
                    rect = rects.get(kind, None) if isinstance(rects, dict) else None

                    if rect is not None:
                        hit_corner = None
                        try:
                            # Bottom-left corner allows width+height; bottom-right height-only.
                            if abs(int(mx) - int(rect.left)) <= corner_px and abs(int(my) - int(rect.bottom)) <= corner_px:
                                hit_corner = 'bl'
                            elif abs(int(mx) - int(rect.right)) <= corner_px and abs(int(my) - int(rect.bottom)) <= corner_px:
                                hit_corner = 'br'
                        except Exception:
                            hit_corner = None

                        if hit_corner is not None:
                            try:
                                client._coin_panel_drag_active = True
                                client._coin_panel_drag_kind = str(kind)
                                client._coin_panel_drag_corner = str(hit_corner)
                                client._coin_panel_drag_start_pos = (int(mx), int(my))
                                client._coin_panel_drag_start_size = (int(rect.width), int(rect.height))
                                # Start from the currently displayed size.
                                try:
                                    if not isinstance(getattr(client, '_coin_panel_size_override', None), dict):
                                        client._coin_panel_size_override = {}
                                    client._coin_panel_size_override[str(kind)] = (int(rect.width), int(rect.height))
                                except Exception:
                                    pass

                                # Also store a resolution-relative override so proportions persist
                                # across window/fullscreen changes.
                                try:
                                    screen_w = int(client.screen.get_width())
                                    screen_h = int(client.screen.get_height())
                                except Exception:
                                    screen_w, screen_h = (0, 0)
                                if int(screen_w) > 0 and int(screen_h) > 0:
                                    try:
                                        if not isinstance(getattr(client, '_coin_panel_size_override_frac', None), dict):
                                            client._coin_panel_size_override_frac = {}
                                        fw = float(rect.width) / float(screen_w)
                                        fh = float(rect.height) / float(screen_h)
                                        fw = max(0.02, min(0.98, float(fw)))
                                        fh = max(0.02, min(0.98, float(fh)))
                                        client._coin_panel_size_override_frac[str(kind)] = (float(fw), float(fh))
                                    except Exception:
                                        pass
                            except Exception:
                                pass
                            continue

                if event.type == self._pygame.MOUSEMOTION and bool(getattr(client, '_coin_panel_drag_active', False)):
                    try:
                        mx, my = int(event.pos[0]), int(event.pos[1])
                    except Exception:
                        mx, my = (0, 0)
                    try:
                        sx, sy = tuple(getattr(client, '_coin_panel_drag_start_pos', (0, 0)))
                    except Exception:
                        sx, sy = (0, 0)
                    try:
                        sw, sh = tuple(getattr(client, '_coin_panel_drag_start_size', (0, 0)))
                    except Exception:
                        sw, sh = (0, 0)
                    dx = int(mx - int(sx))
                    dy = int(my - int(sy))

                    try:
                        kind = str(getattr(client, '_coin_panel_drag_kind', '') or '').strip().lower()
                    except Exception:
                        kind = ''
                    try:
                        corner = str(getattr(client, '_coin_panel_drag_corner', '') or '').strip().lower()
                    except Exception:
                        corner = ''

                    try:
                        screen_w = int(client.screen.get_width())
                        screen_h = int(client.screen.get_height())
                    except Exception:
                        screen_w, screen_h = (1920, 1080)

                    # Anchor is top-right; bottom-right corner can't sensibly adjust width without also changing margins.
                    if corner == 'bl':
                        nw = int(sw - dx)
                    else:
                        nw = int(sw)
                    nh = int(sh + dy)

                    nw = max(40, min(int(screen_w - 6), int(nw)))
                    nh = max(24, min(int(screen_h - 6), int(nh)))

                    try:
                        if not isinstance(getattr(client, '_coin_panel_size_override', None), dict):
                            client._coin_panel_size_override = {}
                        if kind in ('hud', 'menu', 'story'):
                            client._coin_panel_size_override[str(kind)] = (int(nw), int(nh))
                    except Exception:
                        pass

                    # Keep fractional overrides in sync.
                    if int(screen_w) > 0 and int(screen_h) > 0:
                        try:
                            if not isinstance(getattr(client, '_coin_panel_size_override_frac', None), dict):
                                client._coin_panel_size_override_frac = {}
                            if kind in ('hud', 'menu', 'story'):
                                fw = float(nw) / float(screen_w)
                                fh = float(nh) / float(screen_h)
                                fw = max(0.02, min(0.98, float(fw)))
                                fh = max(0.02, min(0.98, float(fh)))
                                client._coin_panel_size_override_frac[str(kind)] = (float(fw), float(fh))
                        except Exception:
                            pass
                    continue

                if event.type == self._pygame.MOUSEBUTTONUP and int(getattr(event, 'button', 0) or 0) == 1:
                    if bool(getattr(client, '_coin_panel_drag_active', False)):
                        try:
                            client._coin_panel_drag_active = False
                            client._coin_panel_drag_kind = None
                            client._coin_panel_drag_corner = None
                        except Exception:
                            pass
                        try:
                            client._persist_coin_panel_size_override()
                        except Exception:
                            pass
                        continue
            except Exception:
                pass

            # Keep a per-session set of held keycodes so key-hold mechanics
            # (like horizontal auto-repeat) work reliably.
            try:
                client._input.update_held_keycodes_from_event(client, event)
            except Exception:
                pass

            # Window resize: keep menus readable and prevent header overlap.
            try:
                is_resize = (event.type == self._pygame.VIDEORESIZE) or (
                    hasattr(self._pygame, 'WINDOWSIZECHANGED') and event.type == self._pygame.WINDOWSIZECHANGED
                )
            except Exception:
                is_resize = False

            if is_resize:
                # Ignore resize events during exclusive fullscreen.
                if not bool(getattr(client, '_fullscreen_enabled', False)):
                    try:
                        new_w = int(getattr(event, 'w', 0) or 0)
                        new_h = int(getattr(event, 'h', 0) or 0)
                    except Exception:
                        new_w, new_h = (0, 0)
                    if (new_w <= 0 or new_h <= 0):
                        try:
                            new_w, new_h = int(event.size[0]), int(event.size[1])
                        except Exception:
                            new_w, new_h = (0, 0)

                    if new_w > 0 and new_h > 0:
                        try:
                            flags = 0
                            try:
                                flags |= self._pygame.RESIZABLE
                            except Exception:
                                pass
                            # Keep SCALED opt-in via env.
                            try:
                                want_scaled = (
                                    str(os.getenv('BF_SCALED', '0') or '0').strip().lower() not in ('0', 'false', 'no', 'off')
                                )
                            except Exception:
                                want_scaled = False
                            if want_scaled:
                                try:
                                    flags |= self._pygame.SCALED
                                except Exception:
                                    pass
                            client.screen = self._pygame.display.set_mode((int(new_w), int(new_h)), flags)
                        except Exception:
                            pass

                        # Recompute layout so the board area remains centered and
                        # scales up/down with the new window size.
                        try:
                            client._recompute_ui_scale_and_assets()
                        except Exception:
                            pass

                        # Rebuild scaled menu assets and clear cached rects.
                        try:
                            client._rebuild_menu_scaled_assets()
                        except Exception:
                            pass
                        try:
                            client._menu_buttons = []
                            client._pause_buttons = []
                            client._menu_pause_buttons = []
                            client._menu_last_size = None
                        except Exception:
                            pass
                continue

            # Gameplay-only: allow dragging the sword art next to NEXT previews.
            # This is a tuning affordance; later we can lock the offsets.
            try:
                if str(getattr(client, 'state', '') or '') == 'game':
                    if event.type == self._pygame.KEYDOWN:
                        # Gameplay-only tuning: scale NEXT sword art so you can dial in perfect sizing.
                        # - Ctrl + '-'/'=' adjusts a GLOBAL multiplier.
                        # - Without Ctrl, '-'/'=' adjusts the PER-SWORD multiplier for the last-clicked side.
                        if event.key in (
                            self._pygame.K_MINUS,
                            self._pygame.K_KP_MINUS,
                            self._pygame.K_EQUALS,
                            self._pygame.K_PLUS,
                            self._pygame.K_KP_PLUS,
                        ):
                            try:
                                delta = -0.05 if event.key in (self._pygame.K_MINUS, self._pygame.K_KP_MINUS) else 0.05
                            except Exception:
                                delta = 0.0

                            try:
                                is_ctrl = bool(
                                    int(getattr(event, 'mod', 0) or 0)
                                    & int(getattr(self._pygame, 'KMOD_CTRL', 0) or 0)
                                )
                            except Exception:
                                is_ctrl = False

                            if is_ctrl:
                                try:
                                    cur = float(getattr(client, '_preview_sword_scale', 1.0) or 1.0)
                                except Exception:
                                    cur = 1.0
                                cur = max(0.30, min(2.50, float(cur) + float(delta)))
                                client._preview_sword_scale = float(cur)
                                try:
                                    client._persist_preview_sword_tuning()
                                except Exception:
                                    pass
                                try:
                                    print(f"[preview] sword GLOBAL scale = {float(client._preview_sword_scale):.2f}")
                                except Exception:
                                    pass
                                continue

                            # Per-sword scale (based on last selected side).
                            try:
                                side = str(getattr(client, '_preview_sword_tune_side', None) or 'left').strip().lower()
                            except Exception:
                                side = 'left'
                            if side not in ('left', 'right'):
                                side = 'left'

                            try:
                                sword_id = str(
                                    (
                                        getattr(client, '_equipped_sword_value', None)
                                        if side == 'left'
                                        else getattr(client, '_enemy_sword_value', None)
                                    )
                                    or ''
                                ).strip().lower()
                            except Exception:
                                sword_id = ''
                            if not sword_id:
                                sword_id = 'rusty_sword'

                            try:
                                cur = float((getattr(client, '_preview_sword_scale_by_weapon', {}) or {}).get(sword_id, 1.0) or 1.0)
                            except Exception:
                                cur = 1.0
                            cur = max(0.30, min(2.50, float(cur) + float(delta)))
                            try:
                                client._preview_sword_scale_by_weapon[str(sword_id)] = float(cur)
                            except Exception:
                                pass
                            try:
                                client._persist_preview_sword_tuning()
                            except Exception:
                                pass
                            try:
                                print(f"[preview] sword '{sword_id}' scale = {float(cur):.2f} (side={side})")
                            except Exception:
                                pass
                            continue

                    if event.type == self._pygame.MOUSEBUTTONDOWN and int(getattr(event, 'button', 0) or 0) == 1:
                        try:
                            mx, my = int(event.pos[0]), int(event.pos[1])
                        except Exception:
                            mx, my = 0, 0
                        hit_side = None
                        try:
                            lr = (getattr(client, '_last_preview_sword_rect', None) or {})
                            lrect = lr.get('left', None)
                            rrect = lr.get('right', None)
                            if lrect is not None and lrect.collidepoint((mx, my)):
                                hit_side = 'left'
                            elif rrect is not None and rrect.collidepoint((mx, my)):
                                hit_side = 'right'
                        except Exception:
                            hit_side = None

                        if hit_side is not None:
                            # Select which sword to tune for '-'/'='.
                            try:
                                client._preview_sword_tune_side = str(hit_side)
                            except Exception:
                                pass
                            # Prefer sword drag when clicking on the sword.
                            try:
                                client._preview_piece_drag_active = False
                                client._preview_piece_drag_side = None
                            except Exception:
                                pass
                            client._preview_sword_drag_active = True
                            client._preview_sword_drag_side = str(hit_side)
                            client._preview_sword_drag_start_pos = (int(mx), int(my))
                            try:
                                client._preview_sword_drag_start_offset = tuple(
                                    getattr(client, '_preview_sword_offset_px', {}).get(str(hit_side), (0, 0))
                                )
                            except Exception:
                                client._preview_sword_drag_start_offset = (0, 0)
                            continue

                        # If we didn't hit a sword, allow dragging the NEXT piece preview.
                        hit_piece_side = None
                        try:
                            pr = (getattr(client, '_last_preview_piece_rect', None) or {})
                            lpr = pr.get('left', None)
                            rpr = pr.get('right', None)
                            if lpr is not None and lpr.collidepoint((mx, my)):
                                hit_piece_side = 'left'
                            elif rpr is not None and rpr.collidepoint((mx, my)):
                                hit_piece_side = 'right'
                        except Exception:
                            hit_piece_side = None

                        if hit_piece_side is not None:
                            try:
                                client._preview_sword_drag_active = False
                                client._preview_sword_drag_side = None
                            except Exception:
                                pass
                            client._preview_piece_drag_active = True
                            client._preview_piece_drag_side = str(hit_piece_side)
                            client._preview_piece_drag_start_pos = (int(mx), int(my))
                            try:
                                client._preview_piece_drag_start_offset = tuple(
                                    getattr(client, '_preview_piece_offset_px', {}).get(str(hit_piece_side), (0, 0))
                                )
                            except Exception:
                                client._preview_piece_drag_start_offset = (0, 0)
                            continue

                    if event.type == self._pygame.MOUSEBUTTONUP and int(getattr(event, 'button', 0) or 0) == 1:
                        if bool(getattr(client, '_preview_sword_drag_active', False)):
                            client._preview_sword_drag_active = False
                            client._preview_sword_drag_side = None
                            try:
                                client._persist_preview_sword_tuning()
                            except Exception:
                                pass
                            continue
                        if bool(getattr(client, '_preview_piece_drag_active', False)):
                            client._preview_piece_drag_active = False
                            client._preview_piece_drag_side = None
                            try:
                                client._persist_preview_sword_tuning()
                            except Exception:
                                pass
                            continue

                    if event.type == self._pygame.MOUSEMOTION and bool(getattr(client, '_preview_sword_drag_active', False)):
                        side = str(getattr(client, '_preview_sword_drag_side', '') or '')
                        if side in ('left', 'right'):
                            try:
                                mx, my = int(event.pos[0]), int(event.pos[1])
                            except Exception:
                                mx, my = 0, 0
                            try:
                                sx, sy = tuple(getattr(client, '_preview_sword_drag_start_pos', (0, 0)))
                            except Exception:
                                sx, sy = (0, 0)
                            dx = int(mx - int(sx))
                            dy = int(my - int(sy))
                            try:
                                ox0, oy0 = tuple(getattr(client, '_preview_sword_drag_start_offset', (0, 0)))
                            except Exception:
                                ox0, oy0 = (0, 0)
                            try:
                                # Clamp to avoid completely losing it off-screen.
                                nx = max(-800, min(800, int(ox0) + int(dx)))
                                ny = max(-800, min(800, int(oy0) + int(dy)))
                                client._preview_sword_offset_px[str(side)] = (int(nx), int(ny))
                            except Exception:
                                pass
                            continue

                    if event.type == self._pygame.MOUSEMOTION and bool(getattr(client, '_preview_piece_drag_active', False)):
                        side = str(getattr(client, '_preview_piece_drag_side', '') or '')
                        if side in ('left', 'right'):
                            try:
                                mx, my = int(event.pos[0]), int(event.pos[1])
                            except Exception:
                                mx, my = 0, 0
                            try:
                                sx, sy = tuple(getattr(client, '_preview_piece_drag_start_pos', (0, 0)))
                            except Exception:
                                sx, sy = (0, 0)
                            dx = int(mx - int(sx))
                            dy = int(my - int(sy))
                            try:
                                ox0, oy0 = tuple(getattr(client, '_preview_piece_drag_start_offset', (0, 0)))
                            except Exception:
                                ox0, oy0 = (0, 0)
                            try:
                                # Clamp to avoid completely losing it off-screen.
                                nx = max(-800, min(800, int(ox0) + int(dx)))
                                ny = max(-800, min(800, int(oy0) + int(dy)))
                                client._preview_piece_offset_px[str(side)] = (int(nx), int(ny))
                            except Exception:
                                pass
                            continue
            except Exception:
                pass

            if event.type == self._pygame.QUIT:
                client.running = False
            elif client.state == 'strike_test':
                client._handle_strike_test_event(event)
            elif client.state == 'menu':
                try:
                    if client._menu.handle_menu_state_event(client, event):
                        continue
                except Exception:
                    pass
            elif client.state == 'pause':
                if event.type == self._pygame.KEYDOWN:
                    if client._event_is_action(event.key, 'pause') or client._event_is_action(event.key, 'ui_back'):
                        if str(getattr(client, '_pause_view', 'main') or 'main') == 'options':
                            client._pause_action('back')
                        else:
                            client._pause_action('resume')
                    elif client._event_is_action(event.key, 'ui_confirm'):
                        try:
                            idx = int(getattr(client, '_pause_selected', 0) or 0)
                        except Exception:
                            idx = 0
                        btns = getattr(client, '_pause_buttons', None) or client._build_pause_buttons()
                        if 0 <= idx < len(btns):
                            try:
                                client._ui_flash_button('pause', str(btns[idx].get('id')))
                            except Exception:
                                pass
                            client._pause_action(str(btns[idx].get('id')))
                    elif client._event_is_action(event.key, 'ui_up') or event.key == self._pygame.K_LEFT:
                        try:
                            btns = getattr(client, '_pause_buttons', None) or client._build_pause_buttons()
                            client._pause_selected = max(0, int(getattr(client, '_pause_selected', 0) or 0) - 1)
                        except Exception:
                            client._pause_selected = 0
                    elif client._event_is_action(event.key, 'ui_down') or event.key == self._pygame.K_RIGHT:
                        try:
                            btns = getattr(client, '_pause_buttons', None) or client._build_pause_buttons()
                            client._pause_selected = min(
                                max(0, len(btns) - 1),
                                int(getattr(client, '_pause_selected', 0) or 0) + 1,
                            )
                        except Exception:
                            client._pause_selected = 1
                elif event.type == self._pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if not getattr(client, '_pause_buttons', None):
                        client._pause_buttons = client._build_pause_buttons()
                    hit = client._pause_button_at(event.pos)
                    if hit is not None:
                        try:
                            client._pause_selected = int(hit)
                        except Exception:
                            client._pause_selected = 0
                        try:
                            b = client._pause_buttons[int(hit)]
                            try:
                                client._ui_flash_button('pause', str(b.get('id')))
                            except Exception:
                                pass
                            client._pause_action(str(b.get('id')))
                        except Exception:
                            pass
            elif client.state == 'postgame':
                if event.type == self._pygame.KEYDOWN:
                    if client._event_is_action(event.key, 'ui_back'):
                        client._postgame_action('menu')
                    elif client._event_is_action(event.key, 'ui_confirm') and event.key != self._pygame.K_SPACE:
                        try:
                            idx = int(getattr(client, '_postgame_selected', 0) or 0)
                        except Exception:
                            idx = 0
                        btns = getattr(client, '_postgame_buttons', None) or client._build_postgame_buttons()
                        if 0 <= idx < len(btns):
                            try:
                                client._ui_flash_button('postgame', str(btns[idx].get('id')))
                            except Exception:
                                pass
                            client._postgame_action(str(btns[idx].get('id')))
                    elif client._event_is_action(event.key, 'ui_up') or event.key == self._pygame.K_LEFT:
                        try:
                            btns = getattr(client, '_postgame_buttons', None) or client._build_postgame_buttons()
                            client._postgame_selected = max(0, int(getattr(client, '_postgame_selected', 0) or 0) - 1)
                        except Exception:
                            client._postgame_selected = 0
                    elif client._event_is_action(event.key, 'ui_down') or event.key == self._pygame.K_RIGHT:
                        try:
                            btns = getattr(client, '_postgame_buttons', None) or client._build_postgame_buttons()
                            client._postgame_selected = min(
                                max(0, len(btns) - 1),
                                int(getattr(client, '_postgame_selected', 0) or 0) + 1,
                            )
                        except Exception:
                            client._postgame_selected = 1
                elif event.type == self._pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if not getattr(client, '_postgame_buttons', None):
                        client._postgame_buttons = client._build_postgame_buttons()
                    hit = client._postgame_button_at(event.pos)
                    if hit is not None:
                        try:
                            client._postgame_selected = int(hit)
                        except Exception:
                            client._postgame_selected = 0
                        try:
                            b = client._postgame_buttons[int(hit)]
                            try:
                                client._ui_flash_button('postgame', str(b.get('id')))
                            except Exception:
                                pass
                            client._postgame_action(str(b.get('id')))
                        except Exception:
                            pass
            elif event.type == self._pygame.KEYDOWN:
                if client._event_is_action(event.key, 'pause'):
                    client._enter_pause()
                elif event.key == self._pygame.K_1:
                    client.cascade_tween_ms = max(0, client.cascade_tween_ms - 10)
                    try:
                        if os.getenv('BF_DEBUG_UI', '0') == '1':
                            print(f"[UI] Cascade tween = {client.cascade_tween_ms} ms")
                    except Exception:
                        pass
                elif event.key == self._pygame.K_2:
                    client.cascade_tween_ms = min(500, client.cascade_tween_ms + 10)
                    try:
                        if os.getenv('BF_DEBUG_UI', '0') == '1':
                            print(f"[UI] Cascade tween = {client.cascade_tween_ms} ms")
                    except Exception:
                        pass
                else:
                    # Tutorial finish/advance keys should work even if no piece is controllable.
                    if bool(getattr(client, '_tutorial_active', False)):
                        if client._event_is_action(event.key, 'ui_confirm'):
                            tstep = int(getattr(client, '_tutorial_step', 0) or 0)
                            # Step 5: player has seen inbound; proceed to finish prompt.
                            if tstep == 5:
                                client._tutorial_step = 6
                                continue
                            # Step 6: finish tutorial and return to academy.
                            if tstep >= 6:
                                try:
                                    client._complete_tutorial_and_return()
                                except Exception:
                                    pass
                                continue

                    # During the scripted combo drop, lock movement/rotation so it's deterministic.
                    if bool(getattr(client, '_tutorial_active', False)) and bool(getattr(client, '_tutorial_controls_locked', False)):
                        if (
                            client._event_is_action(event.key, 'move_left')
                            or client._event_is_action(event.key, 'move_right')
                            or client._event_is_action(event.key, 'rotate_ccw')
                            or client._event_is_action(event.key, 'rotate_cw')
                        ):
                            continue

                    piece = client.session.player.get_piece()
                    if piece is None or (not bool(getattr(piece, 'controllable', False))):
                        continue
                    mover = client.session.player.mover
                    if client._event_is_action(event.key, 'move_left'):
                        mover.move(piece, -1, 0)
                        try:
                            client._tutorial_progress['moved'] = True
                            client._advance_tutorial()
                        except Exception:
                            pass
                    elif client._event_is_action(event.key, 'move_right'):
                        mover.move(piece, 1, 0)
                        try:
                            client._tutorial_progress['moved'] = True
                            client._advance_tutorial()
                        except Exception:
                            pass
                    elif client._event_is_action(event.key, 'rotate_ccw'):
                        mover.rotate(piece, clockwise=False)
                        try:
                            client._tutorial_progress['rot_ccw'] = True
                            client._advance_tutorial()
                        except Exception:
                            pass
                    elif client._event_is_action(event.key, 'rotate_cw'):
                        mover.rotate(piece, clockwise=True)
                        try:
                            client._tutorial_progress['rot_cw'] = True
                            client._advance_tutorial()
                        except Exception:
                            pass
                    elif client._event_is_action(event.key, 'fast_fall'):
                        try:
                            client._input.apply_fast_fall_from_event(client, event)
                        except Exception:
                            client.fast = True
                            client._space_consumed = True
            elif event.type == self._pygame.KEYUP and client._event_is_action(getattr(event, 'key', None), 'fast_fall'):
                try:
                    client._input.apply_fast_fall_from_event(client, event)
                except Exception:
                    # Only release if no fast-fall key is still held (supports multi-bind).
                    try:
                        held = getattr(client, '_held_keycodes', None)
                        if not client._keys_pressed_action(held if held is not None else set(), 'fast_fall'):
                            client.fast = False
                            client._space_consumed = False
                    except Exception:
                        client.fast = False
                        client._space_consumed = False
