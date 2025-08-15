import pygame
from typing import Optional, List, Tuple


class InputTunerOverlay:
    """
    Lightweight in-game overlay to live-tune input repeat timings.
    - Toggle visibility via toggle()
    - update(events): handle key inputs for tuning
    - draw(surface): render the UI and diagnostics
    """

    PARAM_KEYS: List[Tuple[str, str]] = [
        # DAS/ARR functionality removed - no repeat timing parameters
    ]

    def __init__(self, clock, settings_service, input_handler, font: Optional[pygame.font.Font] = None, logger=None):
        self.clock = clock
        self.settings = settings_service
        self.input_handler = input_handler
        self.font = font
        self.logger = logger
        self.visible = False
        self._selected_index = 0
        self._last_adjust_ts = 0
        self._small_step = 5
        self._big_step = 25

        # Colors
        self._bg_color = (10, 10, 20, 180)
        self._panel_border = (90, 130, 240)
        self._text_color = (235, 235, 245)
        self._text_dim = (160, 170, 180)
        self._accent = (255, 200, 90)

    def toggle(self):
        self.visible = not self.visible
        if self.logger:
            try:
                msg = f"InputTunerOverlay {'ON' if self.visible else 'OFF'}"
                if callable(self.logger):
                    self.logger(msg)
                elif hasattr(self.logger, 'info'):
                    self.logger.info(msg)
            except Exception:
                pass

    def _clamp_and_apply(self, key: str, value: int) -> int:
        # DAS/ARR functionality removed - no timing parameters to apply
        return int(value)

    def _adjust_selected(self, delta: int):
        # DAS/ARR functionality removed - no parameters to adjust
        pass

    def update(self, events: List[object]) -> None:
        if not self.visible:
            return
        
        # If there are no parameters to adjust, just return
        if not self.PARAM_KEYS:
            return
            
        for e in events:
            if getattr(e, 'type', None) == pygame.KEYDOWN:
                k = getattr(e, 'key', None)
                # I/K move selection (up/down). J/L adjust (dec/inc). Hold Shift for big steps.
                if k == pygame.K_i:
                    self._selected_index = (self._selected_index - 1) % len(self.PARAM_KEYS)
                elif k == pygame.K_k:
                    self._selected_index = (self._selected_index + 1) % len(self.PARAM_KEYS)
                elif k == pygame.K_j:
                    step = self._big_step if (pygame.key.get_mods() & pygame.KMOD_SHIFT) else self._small_step
                    self._adjust_selected(-step)
                elif k == pygame.K_l:
                    step = self._big_step if (pygame.key.get_mods() & pygame.KMOD_SHIFT) else self._small_step
                    self._adjust_selected(step)

    def _get_font(self) -> pygame.font.Font:
        if self.font:
            return self.font
        try:
            return pygame.font.SysFont(None, 20)
        except Exception:
            return None

    def draw(self, surface: pygame.Surface) -> None:
        if not self.visible:
            return
        width, height = surface.get_width(), surface.get_height()
        panel_w, panel_h = min(520, max(360, width // 3)), min(420, height - 80)
        x, y = 20, 20

        # Panel background
        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel.fill(self._bg_color)
        surface.blit(panel, (x, y))
        pygame.draw.rect(surface, self._panel_border, pygame.Rect(x, y, panel_w, panel_h), 1, border_radius=8)

        font = self._get_font()
        line_y = y + 12
        line_x = x + 12

        # Title
        if font:
            title = font.render("Input Feel Tuner (F9)", True, self._accent)
            surface.blit(title, (line_x, line_y))
        line_y += 24

        # Current timings
        try:
            diag = self.input_handler.get_diagnostics()
        except Exception:
            diag = {'timings': {}, 'last_events': []}
        timings = diag.get('timings', {})
        for idx, (key, label) in enumerate(self.PARAM_KEYS):
            val = timings.get(key, self.settings.get(key, 0))
            marker = '>' if idx == self._selected_index else ' '
            text = f"{marker} {label}: {int(val)}"
            if font:
                color = self._accent if idx == self._selected_index else self._text_color
                surf = font.render(text, True, color)
                surface.blit(surf, (line_x, line_y))
            else:
                pygame.draw.rect(surface, (80, 180, 240) if idx == self._selected_index else (120, 120, 120), pygame.Rect(line_x, line_y, panel_w - 24, 18), 0)
            line_y += 22

        line_y += 6
        # Help text
        help_lines = [
            "I/K: select   J/L: adjust   Shift: big step",
            "Values persist immediately to settings",
        ]
        for t in help_lines:
            if font:
                surf = font.render(t, True, self._text_dim)
                surface.blit(surf, (line_x, line_y))
            line_y += 18

        # Recent events header
        line_y += 8
        if font:
            surface.blit(font.render("Recent key events:", True, self._text_color), (line_x, line_y))
        line_y += 20

        # Events list (most recent last)
        events = diag.get('last_events', [])[-10:]
        for ev in events:
            try:
                k = ev.get('key')
                t = ev.get('t')
                d = ev.get('delta')
                typ = ev.get('type')
                txt = f"{typ} key={k}  t={t}  +{d}ms"
                if font:
                    surface.blit(font.render(txt, True, self._text_dim), (line_x, line_y))
                else:
                    pygame.draw.rect(surface, (90, 90, 110), pygame.Rect(line_x, line_y, panel_w - 24, 14))
            except Exception:
                pass
            line_y += 16

