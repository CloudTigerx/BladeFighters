from __future__ import annotations


class StoryIntroController:
    def __init__(self, *, pygame):
        self._pygame = pygame

    def build_story_character_buttons(self, client) -> list[dict]:
        # 8 placeholder character tiles (2 rows x 4 cols) centered.
        w = int(client.screen.get_width())
        h = int(client.screen.get_height())
        cols = 4
        rows = 2

        tile = int(min(w * 0.14, h * 0.16))
        tile = max(60, min(180, tile))
        gap = max(14, int(round(tile * 0.20)))

        total_w = cols * tile + (cols - 1) * gap
        total_h = rows * tile + (rows - 1) * gap
        start_x = int((w - total_w) / 2)
        start_y = int(h * 0.34)
        start_y = min(start_y, int(h - total_h - h * 0.18))

        colors = [
            (255, 80, 80, 140),
            (80, 140, 255, 140),
            (255, 220, 80, 140),
            (80, 220, 140, 140),
            (200, 90, 255, 140),
            (255, 140, 80, 140),
            (110, 255, 240, 140),
            (230, 230, 230, 120),
        ]

        out: list[dict] = []
        idx = 0
        for r in range(rows):
            for c in range(cols):
                x = int(start_x + c * (tile + gap))
                y = int(start_y + r * (tile + gap))
                cid = f"char_{idx + 1}"
                out.append({'id': cid, 'rect': self._pygame.Rect(x, y, tile, tile), 'rgba': colors[idx % len(colors)]})
                idx += 1
        return out

    def start_story_intro_from_character(self, client, cid: str) -> None:
        client._story_selected_character = str(cid or '') or None
        if not bool(getattr(client, '_story_swift_tutorial_complete', False)):
            client._story_player_name = ''
            client._story_name_confirmed = False
        client._story_dialogue_step = 0
        client._story_post_tutorial_step = 0
        client._menu_pause_active = False
        client._menu_pause_buttons = []
        client._set_menu_status('')
        client._begin_menu_transition('story_intro', duration_ms=650)

    def handle_story_name_input(self, client, event) -> None:
        if bool(getattr(client, '_story_name_confirmed', False)):
            return
        try:
            if event.key == self._pygame.K_BACKSPACE:
                client._story_player_name = (client._story_player_name or '')[:-1]
                return
        except Exception:
            pass

        try:
            ch = getattr(event, 'unicode', '')
            if not ch:
                return
            # Basic printable guard.
            if ord(ch) < 32:
                return
        except Exception:
            return

        name = str(getattr(client, '_story_player_name', '') or '')
        if len(name) >= 16:
            return

        allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -_"  # simple
        if ch not in allowed:
            return
        client._story_player_name = name + ch

    def advance_story_intro(self, client) -> None:
        # If the swift tutorial is already completed, the story intro becomes
        # the post-tutorial academy cutscene.
        if bool(getattr(client, '_story_swift_tutorial_complete', False)):
            step = int(getattr(client, '_story_post_tutorial_step', 0) or 0)
            if step <= 0:
                # From menu1: "Behold the academy" -> fade to menu2.
                client._story_post_tutorial_step = 1
                client._set_menu_status('')
                client._begin_menu_transition('story_academy', duration_ms=650)
                return

            # If we're on menu2 and the action buttons are present, Enter should activate the primary one.
            view = str(getattr(client, '_menu_view', 'main') or 'main')
            if view == 'story_academy' and step == 1:
                client._on_menu_button('story_proceed_academy')
                return
            if view == 'story_academy' and step >= 2:
                client._on_menu_button('story_proceed_quarters')
                return
            return

        if not bool(getattr(client, '_story_name_confirmed', False)):
            nm = str(getattr(client, '_story_player_name', '') or '').strip()
            if not nm:
                client._set_menu_status('Please type your name first')
                return
            client._story_player_name = nm
            client._story_name_confirmed = True
            client._story_dialogue_step = 0
            client._set_menu_status('')
            # Persist story name for later story scenes.
            try:
                client._persist_story_progress(player_name=nm)
            except Exception:
                pass
            return

        try:
            client._story_dialogue_step = int(getattr(client, '_story_dialogue_step', 0) or 0) + 1
        except Exception:
            client._story_dialogue_step = 1

        # After a couple dialogue taps, start the tutorial and pop the board up.
        try:
            if int(getattr(client, '_story_dialogue_step', 0) or 0) >= 2:
                client._start_tutorial()
        except Exception:
            pass
