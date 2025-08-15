import json
import os
from typing import Dict, List, Optional, Callable

import pygame


class AnimationPlayer:
    def __init__(self, clock, on_frame: Optional[Callable[[str, int], None]] = None):
        self.clock = clock
        self.on_frame = on_frame
        self.sheet: Optional[pygame.Surface] = None
        self.frames: Dict[str, Dict] = {}
        self.anims: Dict[str, List[str]] = {}
        self.current_anim: Optional[str] = None
        self.current_index: int = 0
        self.loop: bool = True
        self.rate: float = 1.0
        self._last_advance_ms: int = 0
        self._paused: bool = False
        self._atlas_dir: Optional[str] = None

    def load(self, atlas_path: str) -> None:
        with open(atlas_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self._atlas_dir = os.path.dirname(os.path.abspath(atlas_path))
        sheet_file = data.get("sheet")
        sheet_path = os.path.join(self._atlas_dir, sheet_file)
        img = pygame.image.load(sheet_path)
        try:
            # convert_alpha requires a display surface; fallback when headless in tests
            self.sheet = img.convert_alpha()
        except Exception:
            self.sheet = img
        self.frames = {fr["name"]: fr for fr in data.get("frames", [])}
        self.anims = {k: list(v) for k, v in data.get("anims", {}).items()}

    def play(self, name: str, rate: float = 1.0, loop: bool = True) -> None:
        if name not in self.anims:
            self.current_anim = None
            return
        self.current_anim = name
        self.rate = float(rate)
        self.loop = bool(loop)
        self.current_index = 0
        self._last_advance_ms = int(self.clock.now_ms())
        if callable(self.on_frame):
            try:
                self.on_frame(name, self.current_index)
            except Exception:
                pass

    def pause(self) -> None:
        self._paused = True

    def resume(self) -> None:
        if self._paused:
            self._paused = False
            self._last_advance_ms = int(self.clock.now_ms())

    def update(self, now_ms: Optional[int] = None) -> None:
        if self.current_anim is None or self.sheet is None or self._paused:
            return
        if now_ms is None:
            now_ms = int(self.clock.now_ms())
        names = self.anims.get(self.current_anim, [])
        if not names:
            return
        current_name = names[self.current_index]
        fr = self.frames.get(current_name)
        if not fr:
            return
        duration = int(fr.get("duration_ms", 80))
        # Scale by rate (rate>1.0 is faster -> shorter duration)
        scaled = max(1, int(duration / max(0.001, self.rate)))
        if now_ms - self._last_advance_ms >= scaled:
            steps = (now_ms - self._last_advance_ms) // scaled
            new_index = self.current_index + int(steps)
            if new_index >= len(names):
                if self.loop:
                    new_index = new_index % len(names)
                else:
                    new_index = len(names) - 1
                    self._paused = True
            if new_index != self.current_index:
                self.current_index = new_index
                self._last_advance_ms = now_ms
                if callable(self.on_frame):
                    try:
                        self.on_frame(self.current_anim, self.current_index)
                    except Exception:
                        pass

    def draw(self, surface: pygame.Surface, x: int, y: int) -> None:
        if self.current_anim is None or self.sheet is None:
            return
        names = self.anims.get(self.current_anim, [])
        if not names:
            return
        name = names[self.current_index]
        fr = self.frames.get(name)
        if not fr:
            return
        rect = pygame.Rect(int(fr["x"]), int(fr["y"]), int(fr["w"]), int(fr["h"]))
        surface.blit(self.sheet, (int(x), int(y)), rect)

