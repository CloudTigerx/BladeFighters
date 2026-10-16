from __future__ import annotations


class InputController:
    def __init__(self, *, pygame):
        self._pygame = pygame

    def update_held_keycodes_from_event(self, client, event) -> None:
        """Maintain `client._held_keycodes` based on KEYDOWN/KEYUP and focus-loss events."""
        pygame = self._pygame
        try:
            if event.type == pygame.KEYDOWN:
                try:
                    client._held_keycodes.add(int(getattr(event, 'key', 0) or 0))
                except Exception:
                    pass
            elif event.type == pygame.KEYUP:
                try:
                    client._held_keycodes.discard(int(getattr(event, 'key', 0) or 0))
                except Exception:
                    pass
            else:
                # If window focus is lost, clear to avoid stuck-held keys.
                try:
                    if hasattr(pygame, 'WINDOWFOCUSLOST') and event.type == pygame.WINDOWFOCUSLOST:
                        client._held_keycodes.clear()
                except Exception:
                    pass
        except Exception:
            pass

    def apply_fast_fall_from_event(self, client, event) -> None:
        """Apply fast-fall key semantics (press to enable, release when no binding is held).

        Mirrors the historical PygameClient behavior:
        - KEYDOWN fast_fall => client.fast=True and client._space_consumed=True
        - KEYUP fast_fall => release only if no fast_fall binding is still held (multi-bind support)
        """

        pygame = self._pygame
        try:
            if event.type == pygame.KEYDOWN and self.event_is_action(client, getattr(event, 'key', None), 'fast_fall'):
                try:
                    client.fast = True
                    client._space_consumed = True
                except Exception:
                    pass
            elif event.type == pygame.KEYUP and self.event_is_action(client, getattr(event, 'key', None), 'fast_fall'):
                try:
                    held = getattr(client, '_held_keycodes', None)
                    if not self.keys_pressed_action(client, held if held is not None else set(), 'fast_fall'):
                        client.fast = False
                        client._space_consumed = False
                except Exception:
                    try:
                        client.fast = False
                        client._space_consumed = False
                    except Exception:
                        pass
        except Exception:
            pass

    def reset_fast_fall_state(self, client) -> None:
        """Reset fast-fall flags (used after piece spawn/locks and session resets)."""
        try:
            client.fast = False
            client._space_consumed = False
        except Exception:
            pass

    def reset_horizontal_repeat_state(self, client, *, piece_id: int | None = None) -> None:
        try:
            client._horiz_piece_id = piece_id
            client._horiz_hold_dir = 0
            client._horiz_next_repeat_ms = 0
        except Exception:
            pass

    def apply_horizontal_auto_repeat(self, client, *, session, accepts_input: bool = True) -> None:
        """Apply per-frame horizontal auto-repeat when holding left/right."""
        if not bool(accepts_input):
            return

        pygame = self._pygame

        try:
            piece = session.player.get_piece()
            if piece is None or (not bool(getattr(piece, 'controllable', False))):
                return

            held = getattr(client, '_held_keycodes', None)
            if held is None:
                held = set()

            left = bool(self.keys_pressed_action(client, held, 'move_left'))
            right = bool(self.keys_pressed_action(client, held, 'move_right'))
            hold_dir = (-1 if (left and not right) else (1 if (right and not left) else 0))

            now_ms = int(pygame.time.get_ticks())

            # Reset timer if piece changed.
            pid = id(piece)
            if getattr(client, '_horiz_piece_id', None) != pid:
                self.reset_horizontal_repeat_state(client, piece_id=pid)

            if hold_dir == 0:
                try:
                    client._horiz_hold_dir = 0
                    client._horiz_next_repeat_ms = 0
                except Exception:
                    pass
                return

            if int(getattr(client, '_horiz_hold_dir', 0) or 0) != int(hold_dir):
                try:
                    client._horiz_hold_dir = int(hold_dir)
                    client._horiz_next_repeat_ms = int(now_ms + int(getattr(client, '_horizontal_move_initial_delay_ms', 160) or 160))
                except Exception:
                    pass
                return

            nxt = int(getattr(client, '_horiz_next_repeat_ms', 0) or 0)
            if nxt > 0 and now_ms >= nxt:
                mover = session.player.mover
                try:
                    mover.move(piece, int(hold_dir), 0)
                except Exception:
                    pass
                rep = int(getattr(client, '_horizontal_move_repeat_ms', 70) or 70)
                rep = max(30, min(250, int(rep)))
                try:
                    client._horiz_next_repeat_ms = int(now_ms + rep)
                except Exception:
                    pass
        except Exception:
            pass

    def build_default_keybinds(self) -> dict[str, list[int]]:
        pygame = self._pygame
        # Keys are pygame key constants (ints). Values are lists to allow multiple bindings.
        return {
            # UI / Menus
            'ui_up': [pygame.K_UP],
            'ui_down': [pygame.K_DOWN],
            'ui_confirm': [pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE],
            'ui_back': [pygame.K_ESCAPE],
            'pause': [pygame.K_ESCAPE, pygame.K_p],

            # Gameplay
            'move_left': [pygame.K_LEFT],
            'move_right': [pygame.K_RIGHT],
            'rotate_ccw': [pygame.K_UP],
            'rotate_cw': [pygame.K_DOWN],
            'fast_fall': [pygame.K_SPACE],
        }

    def normalize_keybinds(self, raw: dict | None, defaults: dict[str, list[int]]) -> dict[str, list[int]]:
        out: dict[str, list[int]] = {k: list(v) for k, v in (defaults or {}).items()}
        if not isinstance(raw, dict):
            return out
        for action, keys in raw.items():
            if str(action) not in out:
                continue
            try:
                if isinstance(keys, int):
                    out[str(action)] = [int(keys)]
                elif isinstance(keys, (list, tuple)):
                    kk: list[int] = []
                    for k in keys:
                        try:
                            kk.append(int(k))
                        except Exception:
                            pass
                    out[str(action)] = kk if kk else list(out[str(action)])
            except Exception:
                pass
        return out

    def action_keys(self, client, action: str) -> list[int]:
        action = str(action or '').strip()
        if not action:
            return []
        try:
            keys = (getattr(client, '_keybinds', {}) or {}).get(action, None)
            if isinstance(keys, list):
                out: list[int] = []
                for k in keys:
                    try:
                        out.append(int(k))
                    except Exception:
                        pass
                return out
        except Exception:
            pass
        try:
            return list((getattr(client, '_default_keybinds', {}) or {}).get(action, []))
        except Exception:
            return []

    def event_is_action(self, client, event_key: int, action: str) -> bool:
        try:
            return int(event_key) in set(self.action_keys(client, action))
        except Exception:
            return False

    def keys_pressed_action(self, client, keys_pressed, action: str) -> bool:
        """Return True if any key bound to `action` is currently held."""

        # Preferred path: our own held-key tracking (keycode-based).
        try:
            if isinstance(keys_pressed, (set, frozenset)):
                for k in self.action_keys(client, action):
                    try:
                        if int(k) in keys_pressed:
                            return True
                    except Exception:
                        continue
                return False
        except Exception:
            pass

        # Fallback: pygame.key.get_pressed() (scancode-indexed).
        try:
            n = len(keys_pressed)
        except Exception:
            n = 0
        try:
            for k in self.action_keys(client, action):
                try:
                    ki = int(k)
                except Exception:
                    continue
                try:
                    if 0 <= ki < n and bool(keys_pressed[ki]):
                        return True
                except Exception:
                    continue
        except Exception:
            pass
        return False

    def format_action_keys(self, client, action: str) -> str:
        pygame = self._pygame
        parts: list[str] = []
        for k in self.action_keys(client, action):
            try:
                nm = pygame.key.name(int(k))
                nm = str(nm)
                parts.append(nm.upper() if len(nm) == 1 else nm)
            except Exception:
                parts.append(str(k))
        return ' / '.join(parts) if parts else 'Unbound'

    def set_single_binding(self, client, action: str, keycode: int) -> None:
        action = str(action or '').strip()
        if not action:
            return
        try:
            keycode = int(keycode)
        except Exception:
            return

        kb = getattr(client, '_keybinds', None)
        if not isinstance(kb, dict):
            kb = {}

        # Unbind this key from any other action to prevent accidental duplicates.
        try:
            for a, keys in list(kb.items()):
                if str(a) == action or not isinstance(keys, list):
                    continue
                kb[str(a)] = [int(k) for k in keys if int(k) != int(keycode)]
        except Exception:
            pass

        kb[action] = [int(keycode)]
        client._keybinds = kb
