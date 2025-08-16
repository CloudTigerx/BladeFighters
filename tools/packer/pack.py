#!/usr/bin/env python3
import argparse
import json
import os
from dataclasses import dataclass
from typing import List, Dict, Tuple

try:
    from PIL import Image
except Exception:
    Image = None  # Lazy error later if used


@dataclass
class FrameInfo:
    name: str
    img: "Image.Image"
    w: int
    h: int
    duration_ms: int


def group_name(filename: str) -> str:
    base = os.path.splitext(os.path.basename(filename))[0]
    # Group by prefix before last underscore
    parts = base.rsplit("_", 1)
    return parts[0] if len(parts) == 2 else base


def load_frames(input_dir: str) -> Tuple[List[FrameInfo], Dict[str, List[str]]]:
    if Image is None:
        raise RuntimeError("Pillow is required for the packer. Please install pillow.")
    frames: List[FrameInfo] = []
    anims: Dict[str, List[str]] = {}
    for fname in sorted(os.listdir(input_dir)):
        if not fname.lower().endswith(".png"):
            continue
        path = os.path.join(input_dir, fname)
        try:
            img = Image.open(path).convert("RGBA")
        except Exception:
            continue
        base = os.path.splitext(fname)[0]
        # Optional duration hint in filename: name_0001_80.png -> 80ms
        duration_ms = 80
        try:
            tail = base.rsplit("_", 1)[-1]
            if tail.isdigit():
                duration_ms = 80
            else:
                maybe_ms = tail
                if maybe_ms.isdigit():
                    duration_ms = int(maybe_ms)
        except Exception:
            duration_ms = 80
        frames.append(FrameInfo(name=base, img=img, w=img.width, h=img.height, duration_ms=int(duration_ms)))
        g = group_name(fname)
        anims.setdefault(g, []).append(base)
    return frames, anims


def pack_shelf(frames: List[FrameInfo], max_width: int = 2048) -> Tuple[Image.Image, Dict[str, Dict[str, int]]]:
    # Simple shelf packer: place images in rows until width exceeded
    x = 0
    y = 0
    row_h = 0
    placements: Dict[str, Dict[str, int]] = {}
    # Compute atlas size first pass
    atlas_w = 0
    total_h = 0
    for fr in frames:
        if x + fr.w > max_width:
            atlas_w = max(atlas_w, x)
            total_h += row_h
            x = 0
            row_h = 0
        placements[fr.name] = {"x": x, "y": total_h, "w": fr.w, "h": fr.h}
        x += fr.w
        row_h = max(row_h, fr.h)
    atlas_w = max(atlas_w, x)
    total_h += row_h
    if atlas_w <= 0 or total_h <= 0:
        atlas_w, total_h = 1, 1
    atlas = Image.new("RGBA", (atlas_w, total_h), (0, 0, 0, 0))
    # Second pass: paste
    for fr in frames:
        p = placements[fr.name]
        atlas.paste(fr.img, (p["x"], p["y"]))
    return atlas, placements


def main():
    parser = argparse.ArgumentParser(description="Pack sprites into a sheet and atlas")
    parser.add_argument("--in", dest="input", required=True, help="Input directory of PNG frames")
    parser.add_argument("--out", dest="output", required=True, help="Output directory")
    parser.add_argument("--sheet", dest="sheet_name", default="spritesheet.png", help="Output sheet file name")
    parser.add_argument("--atlas", dest="atlas_name", default="atlas.json", help="Output atlas json name")
    args = parser.parse_args()

    input_dir = os.path.abspath(args.input)
    output_dir = os.path.abspath(args.output)
    os.makedirs(output_dir, exist_ok=True)

    frames, anims = load_frames(input_dir)
    atlas_img, placements = pack_shelf(frames)

    sheet_path = os.path.join(output_dir, args.sheet_name)
    atlas_path = os.path.join(output_dir, args.atlas_name)
    atlas_img.save(sheet_path)

    frames_json = []
    for fr in frames:
        p = placements[fr.name]
        frames_json.append({
            "name": fr.name,
            "x": int(p["x"]),
            "y": int(p["y"]),
            "w": int(p["w"]),
            "h": int(p["h"]),
            "duration_ms": int(fr.duration_ms),
        })

    atlas = {
        "sheet": os.path.basename(sheet_path),
        "frames": frames_json,
        "anims": anims,
    }
    with open(atlas_path, "w", encoding="utf-8") as f:
        json.dump(atlas, f, indent=2)

    print(f"Wrote {sheet_path} and {atlas_path}")


if __name__ == "__main__":
    main()

