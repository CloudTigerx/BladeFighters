"""settings_controller.py - Persisted settings / preferences glue for Blade Fighters.

Goal: keep PygameClient as orchestrator while extracting save-system interactions
(volume/fullscreen/keybinds/story progress/equipped swords/gold) into a dedicated
controller.

The controller intentionally uses best-effort try/except behavior to preserve the
runtime tolerance of the original monolithic implementation.
"""

from __future__ import annotations

from typing import Any

try:
    from swordfighting_new.save_system import GameSettings
except Exception:  # pragma: no cover
    GameSettings = None


class SettingsController:
    def load_saved_preferences(self, client: Any) -> dict[str, Any]:
        """Load preferences from the SaveManager attached to client.

        Returns a dict with keys:
          - saved_volume, saved_hmove_repeat_ms, saved_fullscreen
          - saved_gold, saved_story_tutorial_complete, saved_story_player_name
          - saved_keybinds, saved_equipped_sword, saved_enemy_sword
        """
        saved_volume = None
        saved_hmove_repeat_ms = None
        saved_fullscreen = None
        saved_gold = None
        saved_story_tutorial_complete = None
        saved_story_player_name = None
        saved_keybinds = None
        saved_equipped_sword = None
        saved_enemy_sword = None
        saved_preview_sword_scale = None
        saved_preview_sword_scale_by_weapon = None
        saved_preview_sword_offset_px = None
        saved_preview_piece_offset_px = None
        saved_coin_panel_pad_mult = None
        saved_coin_panel_icon_layout_cap_mult = None
        saved_coin_panel_size_override = None
        saved_coin_panel_size_override_frac = None

        try:
            sm = getattr(client, '_save_manager', None)
            if sm is not None and GameSettings is not None:
                save_data = sm.load()
                st = sm.get_settings()
                saved_volume = float(getattr(st, 'game_volume', 0.65) or 0.65)
                try:
                    saved_fullscreen = bool(getattr(st, 'fullscreen', False))
                except Exception:
                    saved_fullscreen = None
                try:
                    saved_hmove_repeat_ms = int(getattr(st, 'horizontal_move_repeat_ms', 70) or 70)
                except Exception:
                    saved_hmove_repeat_ms = None

                try:
                    prog = save_data.get('progress', {}) if isinstance(save_data, dict) else {}
                    if isinstance(prog, dict):
                        saved_gold = int(prog.get('gold', 0) or 0)
                        saved_story_tutorial_complete = bool(prog.get('story_swift_tutorial_complete', False))
                        try:
                            saved_story_player_name = str(prog.get('story_player_name', '') or '').strip() or None
                        except Exception:
                            saved_story_player_name = None

                        try:
                            saved_equipped_sword = str(prog.get('equipped_sword', '') or '').strip().lower() or None
                        except Exception:
                            saved_equipped_sword = None

                        try:
                            saved_enemy_sword = str(prog.get('enemy_sword', '') or '').strip().lower() or None
                        except Exception:
                            saved_enemy_sword = None

                    try:
                        controls = save_data.get('controls', {}) if isinstance(save_data, dict) else {}
                        if isinstance(controls, dict):
                            kb = controls.get('keybinds', None)
                            if isinstance(kb, dict):
                                saved_keybinds = dict(kb)
                    except Exception:
                        saved_keybinds = None

                    # UI tuning (preview sword sizing)
                    try:
                        ui = save_data.get('ui', {}) if isinstance(save_data, dict) else {}
                        if isinstance(ui, dict):
                            try:
                                saved_preview_sword_scale = float(ui.get('preview_sword_scale', None))
                            except Exception:
                                saved_preview_sword_scale = None
                            try:
                                raw = ui.get('preview_sword_scale_by_weapon', None)
                                if isinstance(raw, dict):
                                    saved_preview_sword_scale_by_weapon = dict(raw)
                            except Exception:
                                saved_preview_sword_scale_by_weapon = None

                            # Gameplay preview tuning (draggable offsets)
                            try:
                                raw_off = ui.get('preview_sword_offset_px', None)
                                if isinstance(raw_off, dict):
                                    saved_preview_sword_offset_px = dict(raw_off)
                            except Exception:
                                saved_preview_sword_offset_px = None
                            try:
                                raw_off2 = ui.get('preview_piece_offset_px', None)
                                if isinstance(raw_off2, dict):
                                    saved_preview_piece_offset_px = dict(raw_off2)
                            except Exception:
                                saved_preview_piece_offset_px = None

                            # Coin panel layout knobs (HUD/menu/story gold panels)
                            try:
                                saved_coin_panel_pad_mult = float(ui.get('coin_panel_pad_mult', None))
                            except Exception:
                                saved_coin_panel_pad_mult = None
                            try:
                                saved_coin_panel_icon_layout_cap_mult = float(ui.get('coin_panel_icon_layout_cap_mult', None))
                            except Exception:
                                saved_coin_panel_icon_layout_cap_mult = None

                            # Coin panel manual size overrides (drag-resize corners)
                            try:
                                raw_sz = ui.get('coin_panel_size_override', None)
                                if isinstance(raw_sz, dict):
                                    saved_coin_panel_size_override = dict(raw_sz)
                            except Exception:
                                saved_coin_panel_size_override = None

                            # Resolution-relative overrides (fractions of screen size).
                            try:
                                raw_frac = ui.get('coin_panel_size_override_frac', None)
                                if isinstance(raw_frac, dict):
                                    saved_coin_panel_size_override_frac = dict(raw_frac)
                            except Exception:
                                saved_coin_panel_size_override_frac = None
                    except Exception:
                        saved_preview_sword_scale = None
                        saved_preview_sword_scale_by_weapon = None
                        saved_preview_sword_offset_px = None
                        saved_preview_piece_offset_px = None
                        saved_coin_panel_pad_mult = None
                        saved_coin_panel_icon_layout_cap_mult = None
                        saved_coin_panel_size_override = None
                        saved_coin_panel_size_override_frac = None
                except Exception:
                    saved_gold = None
                    saved_story_tutorial_complete = None
                    saved_story_player_name = None
                    saved_keybinds = None
                    saved_equipped_sword = None
                    saved_enemy_sword = None
                    saved_preview_sword_scale = None
                    saved_preview_sword_scale_by_weapon = None
                    saved_preview_sword_offset_px = None
                    saved_preview_piece_offset_px = None
                    saved_coin_panel_pad_mult = None
                    saved_coin_panel_icon_layout_cap_mult = None
                    saved_coin_panel_size_override = None
                    saved_coin_panel_size_override_frac = None
        except Exception:
            saved_volume = None
            saved_hmove_repeat_ms = None
            saved_fullscreen = None
            saved_gold = None
            saved_story_tutorial_complete = None
            saved_story_player_name = None
            saved_keybinds = None
            saved_equipped_sword = None
            saved_enemy_sword = None
            saved_preview_sword_scale = None
            saved_preview_sword_scale_by_weapon = None
            saved_preview_sword_offset_px = None
            saved_preview_piece_offset_px = None
            saved_coin_panel_pad_mult = None
            saved_coin_panel_icon_layout_cap_mult = None
            saved_coin_panel_size_override = None
            saved_coin_panel_size_override_frac = None

        return {
            'saved_volume': saved_volume,
            'saved_hmove_repeat_ms': saved_hmove_repeat_ms,
            'saved_fullscreen': saved_fullscreen,
            'saved_gold': saved_gold,
            'saved_story_tutorial_complete': saved_story_tutorial_complete,
            'saved_story_player_name': saved_story_player_name,
            'saved_keybinds': saved_keybinds,
            'saved_equipped_sword': saved_equipped_sword,
            'saved_enemy_sword': saved_enemy_sword,
            'saved_preview_sword_scale': saved_preview_sword_scale,
            'saved_preview_sword_scale_by_weapon': saved_preview_sword_scale_by_weapon,
            'saved_preview_sword_offset_px': saved_preview_sword_offset_px,
            'saved_preview_piece_offset_px': saved_preview_piece_offset_px,
            'saved_coin_panel_pad_mult': saved_coin_panel_pad_mult,
            'saved_coin_panel_icon_layout_cap_mult': saved_coin_panel_icon_layout_cap_mult,
            'saved_coin_panel_size_override': saved_coin_panel_size_override,
            'saved_coin_panel_size_override_frac': saved_coin_panel_size_override_frac,
        }

    def persist_coin_panel_size_override(self, client: Any) -> None:
        sm = getattr(client, '_save_manager', None)
        if sm is None:
            return
        try:
            data = sm.load()
        except Exception:
            return
        if not isinstance(data, dict):
            return

        try:
            raw = getattr(client, '_coin_panel_size_override', {}) or {}
        except Exception:
            raw = {}

        try:
            raw_frac = getattr(client, '_coin_panel_size_override_frac', {}) or {}
        except Exception:
            raw_frac = {}

        cleaned: dict[str, list[int]] = {}
        if isinstance(raw, dict):
            for k, v in raw.items():
                try:
                    kk = str(k or '').strip().lower()
                except Exception:
                    kk = ''
                if kk not in ('hud', 'menu', 'story'):
                    continue
                try:
                    if isinstance(v, (list, tuple)) and len(v) >= 2:
                        w = int(v[0])
                        h = int(v[1])
                    else:
                        continue
                except Exception:
                    continue
                w = max(40, min(4096, int(w)))
                h = max(24, min(4096, int(h)))
                cleaned[kk] = [int(w), int(h)]

        cleaned_frac: dict[str, list[float]] = {}
        if isinstance(raw_frac, dict):
            for k, v in raw_frac.items():
                try:
                    kk = str(k or '').strip().lower()
                except Exception:
                    kk = ''
                if kk not in ('hud', 'menu', 'story'):
                    continue
                try:
                    if isinstance(v, (list, tuple)) and len(v) >= 2:
                        fw = float(v[0])
                        fh = float(v[1])
                    else:
                        continue
                except Exception:
                    continue
                fw = max(0.02, min(0.98, float(fw)))
                fh = max(0.02, min(0.98, float(fh)))
                cleaned_frac[kk] = [float(fw), float(fh)]

        try:
            ui = data.get('ui', {})
            if not isinstance(ui, dict):
                ui = {}
            ui['coin_panel_size_override'] = dict(cleaned)
            ui['coin_panel_size_override_frac'] = dict(cleaned_frac)
            data['ui'] = ui
            sm.save(data)
        except Exception:
            pass

    def persist_preview_sword_tuning(self, client: Any) -> None:
        sm = getattr(client, '_save_manager', None)
        if sm is None:
            return
        try:
            data = sm.load()
        except Exception:
            return
        if not isinstance(data, dict):
            return

        try:
            cur = float(getattr(client, '_preview_sword_scale', 1.0) or 1.0)
        except Exception:
            cur = 1.0
        cur = max(0.30, min(2.50, float(cur)))

        try:
            raw_map = getattr(client, '_preview_sword_scale_by_weapon', {}) or {}
        except Exception:
            raw_map = {}

        cleaned: dict[str, float] = {}
        if isinstance(raw_map, dict):
            for k, v in raw_map.items():
                try:
                    kk = str(k or '').strip().lower()
                except Exception:
                    kk = ''
                if not kk:
                    continue
                try:
                    vv = float(v)
                except Exception:
                    continue
                vv = max(0.30, min(2.50, float(vv)))
                cleaned[kk] = float(vv)

        # Draggable gameplay preview offsets (left/right) for sword + piece.
        def _clean_offsets(raw: Any) -> dict[str, list[int]]:
            out: dict[str, list[int]] = {}
            if not isinstance(raw, dict):
                return out
            for side in ('left', 'right'):
                try:
                    v = raw.get(side, None)
                except Exception:
                    v = None
                if not (isinstance(v, (list, tuple)) and len(v) >= 2):
                    continue
                try:
                    ox = int(v[0])
                    oy = int(v[1])
                except Exception:
                    continue
                ox = max(-800, min(800, int(ox)))
                oy = max(-800, min(800, int(oy)))
                out[str(side)] = [int(ox), int(oy)]
            return out

        try:
            raw_sword_off = getattr(client, '_preview_sword_offset_px', None)
        except Exception:
            raw_sword_off = None
        try:
            raw_piece_off = getattr(client, '_preview_piece_offset_px', None)
        except Exception:
            raw_piece_off = None
        cleaned_sword_off = _clean_offsets(raw_sword_off)
        cleaned_piece_off = _clean_offsets(raw_piece_off)

        try:
            ui = data.get('ui', {})
            if not isinstance(ui, dict):
                ui = {}
            ui['preview_sword_scale'] = float(cur)
            ui['preview_sword_scale_by_weapon'] = dict(cleaned)
            if cleaned_sword_off:
                ui['preview_sword_offset_px'] = dict(cleaned_sword_off)
            if cleaned_piece_off:
                ui['preview_piece_offset_px'] = dict(cleaned_piece_off)
            data['ui'] = ui
            sm.save(data)
        except Exception:
            pass

    def set_sfx_volume(self, client: Any, v: float) -> None:
        try:
            v = float(v)
        except Exception:
            v = float(getattr(client, '_sfx_volume', 0.65) or 0.65)
        v = max(0.0, min(1.0, float(v)))
        client._sfx_volume = float(v)
        try:
            getattr(client, '_audio', None).set_volume(float(getattr(client, '_sfx_volume', 0.65) or 0.65))
        except Exception:
            pass

    def set_horizontal_move_repeat_ms(self, client: Any, ms: int) -> None:
        try:
            ms = int(ms)
        except Exception:
            ms = int(getattr(client, '_horizontal_move_repeat_ms', 70) or 70)
        ms = max(30, min(250, int(ms)))
        client._horizontal_move_repeat_ms = int(ms)

    def toggle_sfx(self, client: Any) -> None:
        try:
            client._sfx_enabled = not bool(getattr(client, '_sfx_enabled', True))
        except Exception:
            client._sfx_enabled = True

        try:
            getattr(client, '_audio', None).set_enabled(bool(getattr(client, '_sfx_enabled', True)))
        except Exception:
            pass

    def persist_volume_preference(self, client: Any) -> None:
        sm = getattr(client, '_save_manager', None)
        if sm is None or GameSettings is None:
            return
        try:
            v = float(getattr(client, '_sfx_volume', 0.65) or 0.65)
        except Exception:
            v = 0.65
        v = max(0.0, min(1.0, float(v)))
        try:
            rep = int(getattr(client, '_horizontal_move_repeat_ms', 70) or 70)
        except Exception:
            rep = 70
        rep = max(30, min(250, int(rep)))
        try:
            fs = bool(getattr(client, '_fullscreen_enabled', False))
            sm.set_settings(GameSettings(game_volume=float(v), horizontal_move_repeat_ms=int(rep), fullscreen=bool(fs)))
        except Exception:
            pass

    def persist_controls_preference(self, client: Any) -> None:
        sm = getattr(client, '_save_manager', None)
        if sm is None:
            return
        try:
            data = sm.load()
        except Exception:
            return
        if not isinstance(data, dict):
            return
        try:
            controls = data.get('controls', {})
            if not isinstance(controls, dict):
                controls = {}
            controls['keybinds'] = {str(k): list(v) for k, v in (getattr(client, '_keybinds', {}) or {}).items()}
            data['controls'] = controls
            sm.save(data)
        except Exception:
            pass

    def persist_equipped_sword_preference(self, client: Any) -> None:
        sm = getattr(client, '_save_manager', None)
        if sm is None:
            return
        try:
            data = sm.load()
        except Exception:
            return
        if not isinstance(data, dict):
            return

        try:
            prog = data.get('progress', {})
            if not isinstance(prog, dict):
                prog = {}
            prog['equipped_sword'] = str(getattr(client, '_equipped_sword_value', 'rusty_sword') or 'rusty_sword').strip().lower()
            data['progress'] = prog
            sm.save(data)
        except Exception:
            pass

    def persist_enemy_sword_preference(self, client: Any) -> None:
        sm = getattr(client, '_save_manager', None)
        if sm is None:
            return
        try:
            data = sm.load()
        except Exception:
            return
        if not isinstance(data, dict):
            return

        try:
            prog = data.get('progress', {})
            if not isinstance(prog, dict):
                prog = {}
            prog['enemy_sword'] = str(getattr(client, '_enemy_sword_value', 'rusty_sword') or 'rusty_sword').strip().lower()
            data['progress'] = prog
            sm.save(data)
        except Exception:
            pass

    def award_gold(self, client: Any, amount: int) -> None:
        amt = int(amount or 0)
        if amt <= 0:
            return
        try:
            client._player_gold = int(getattr(client, '_player_gold', 0) or 0) + amt
        except Exception:
            client._player_gold = amt

        sm = getattr(client, '_save_manager', None)
        if sm is None:
            return
        try:
            data = sm.load()
            if not isinstance(data, dict):
                data = {}
            prog = data.get('progress')
            if not isinstance(prog, dict):
                prog = {}
            try:
                cur = int(prog.get('gold', 0) or 0)
            except Exception:
                cur = 0
            prog['gold'] = int(cur + amt)
            data['progress'] = prog
            sm.save(data)
        except Exception:
            pass

    def persist_story_progress(self, client: Any, tutorial_complete: bool | None = None, player_name: str | None = None) -> None:
        sm = getattr(client, '_save_manager', None)
        if sm is None:
            return
        try:
            data = sm.load()
            if not isinstance(data, dict):
                data = {}
            prog = data.get('progress')
            if not isinstance(prog, dict):
                prog = {}

            if tutorial_complete is not None:
                prog['story_swift_tutorial_complete'] = bool(tutorial_complete)

            if player_name is not None:
                nm = str(player_name or '').strip()
                if nm:
                    prog['story_player_name'] = nm

            data['progress'] = prog
            sm.save(data)
        except Exception:
            return
