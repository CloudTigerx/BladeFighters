"""process_sword_sprite.py

Small utility to normalize sword strike sprites:
- Hard-threshold alpha so no semi-transparent haze causes "box" artifacts in-engine.
- Force sword pixels to solid black (optional).
- Flip vertical sword (tip up) if needed.
- Generate a rotated horizontal variant.

Usage (PowerShell):
    python tools/process_sword_sprite.py \
    --in assets/sprinkle/verticalstrike.png \
    --out-vertical assets/sprinkle/verticalstrike_clean.png \
    --out-horizontal assets/sprinkle/horizontalstrike_clean.png \
    --flip-vertical \
    --alpha-threshold 32

Notes:
- This does NOT upscale/downscale; it preserves original resolution.
- If you want the sword slightly thicker in-game, do it by scaling at render time
  or regenerate the source sprite thicker.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Normalize sword strike sprites")
    p.add_argument("--in", dest="in_path", required=True, help="Input PNG path")
    p.add_argument("--out-vertical", dest="out_vertical", required=True, help="Output vertical PNG path")
    p.add_argument("--out-horizontal", dest="out_horizontal", required=True, help="Output horizontal PNG path")
    p.add_argument(
        "--alpha-threshold",
        type=int,
        default=32,
        help="Alpha cutoff: <= threshold becomes fully transparent (default 32)",
    )
    p.add_argument(
        "--flip-vertical",
        action="store_true",
        help="Flip the vertical sprite 180 degrees (use if the sword is upside down)",
    )
    p.add_argument(
        "--force-black",
        action="store_true",
        help="Force all non-transparent pixels to RGB(0,0,0) (keeps alpha)",
    )
    return p.parse_args()


def _harden_alpha(img: Image.Image, threshold: int) -> Image.Image:
    img = img.convert("RGBA")
    r, g, b, a = img.split()
    # Hard mask alpha
    a = a.point(lambda v: 255 if v > threshold else 0)
    return Image.merge("RGBA", (r, g, b, a))


def _force_black_rgb(img: Image.Image) -> Image.Image:
    img = img.convert("RGBA")
    r, g, b, a = img.split()
    # Where alpha is 0, RGB doesn't matter, but keep it consistent.
    z = r.point(lambda _: 0)
    return Image.merge("RGBA", (z, z, z, a))


def _print_alpha_stats(label: str, img: Image.Image) -> None:
    img = img.convert("RGBA")
    a = img.getchannel("A")
    hist = a.histogram()
    total = sum(hist)
    zero = hist[0]
    full = hist[255]
    mid = total - zero - full
    print(f"[{label}] size={img.size} alpha_zero={zero/total:.1%} alpha_full={full/total:.1%} alpha_mid={mid/total:.1%}")


def main() -> int:
    args = _parse_args()
    in_path = Path(args.in_path)
    out_v = Path(args.out_vertical)
    out_h = Path(args.out_horizontal)

    img = Image.open(in_path).convert("RGBA")
    _print_alpha_stats("input", img)

    img2 = _harden_alpha(img, int(args.alpha_threshold))
    if args.force_black:
        img2 = _force_black_rgb(img2)

    if args.flip_vertical:
        # Rotate 180 so tip-up if original is upside-down
        img2 = img2.rotate(180, expand=False)

    out_v.parent.mkdir(parents=True, exist_ok=True)
    img2.save(out_v)
    _print_alpha_stats("vertical", img2)

    # Horizontal: rotate 90 degrees clockwise so tip points right (assuming vertical tip-up)
    h_img = img2.rotate(-90, expand=False)
    out_h.parent.mkdir(parents=True, exist_ok=True)
    h_img.save(out_h)
    _print_alpha_stats("horizontal", h_img)

    print(f"Wrote: {out_v}")
    print(f"Wrote: {out_h}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
