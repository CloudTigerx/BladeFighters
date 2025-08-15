import io
import json
import os
import tempfile

import pygame

from utils.clock import FakeClock
from core.gfx.anim_player import AnimationPlayer


def make_dummy_sheet(path: str, frames):
    # Create a simple spritesheet with colored boxes
    w = max(f[2] for f in frames)
    h_total = sum(f[3] for f in frames)
    surf = pygame.Surface((w, h_total), pygame.SRCALPHA)
    y = 0
    colors = [(255, 0, 0, 255), (0, 255, 0, 255), (0, 0, 255, 255)]
    for i, (_name, _x, _y, fw, fh, _dur) in enumerate(frames):
        c = colors[i % len(colors)]
        rect = pygame.Rect(0, y, fw, fh)
        surf.fill(c, rect)
        y += fh
    pygame.image.save(surf, path)


def test_anim_player_variable_durations(tmp_path):
    pygame.init()
    try:
        clock = FakeClock(0)
        # Build minimal atlas on disk
        frames = [
            ("spark_0001", 0, 0, 8, 8, 50),
            ("spark_0002", 0, 8, 8, 8, 100),
            ("spark_0003", 0, 16, 8, 8, 150),
        ]
        sheet = tmp_path / "sheet.png"
        make_dummy_sheet(str(sheet), frames)
        atlas = {
            "sheet": sheet.name,
            "frames": [
                {"name": n, "x": x, "y": y, "w": w, "h": h, "duration_ms": d}
                for (n, x, y, w, h, d) in frames
            ],
            "anims": {"spark": ["spark_0001", "spark_0002", "spark_0003"]},
        }
        atlas_path = tmp_path / "atlas.json"
        with open(atlas_path, "w", encoding="utf-8") as f:
            json.dump(atlas, f)

        player = AnimationPlayer(clock)
        player.load(str(atlas_path))
        player.play("spark", rate=1.0, loop=False)

        # Frame 0 for 50ms
        player.update(clock.now_ms())
        assert player.current_index == 0
        clock.advance(49)
        player.update(clock.now_ms())
        assert player.current_index == 0
        clock.advance(1)
        player.update(clock.now_ms())
        assert player.current_index == 1

        # Frame 1 for 100ms
        clock.advance(99)
        player.update(clock.now_ms())
        assert player.current_index == 1
        clock.advance(1)
        player.update(clock.now_ms())
        assert player.current_index == 2

        # Frame 2 for 150ms then pause at end (loop=False)
        clock.advance(200)
        player.update(clock.now_ms())
        assert player.current_index == 2

        # Draw sanity
        surf = pygame.Surface((16, 16))
        player.draw(surf, 0, 0)
    finally:
        pygame.quit()

