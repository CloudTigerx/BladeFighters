from __future__ import annotations

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert a PNG into a Windows .ico for PyInstaller.")
    parser.add_argument(
        "--input",
        default=str(Path("assets") / "menus" / "title_wordmark.png"),
        help="Path to input PNG (default: assets/menus/title_wordmark.png)",
    )
    parser.add_argument(
        "--output",
        default=str(Path("build") / "icon.ico"),
        help="Path to output .ico (default: build/icon.ico)",
    )
    parser.add_argument(
        "--sizes",
        default="256,128,64,48,32,24,16",
        help="Comma-separated square icon sizes to include (default: 256,128,64,48,32,24,16)",
    )
    args = parser.parse_args()

    in_path = Path(args.input)
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    sizes = []
    for part in str(args.sizes).split(","):
        part = part.strip()
        if not part:
            continue
        try:
            sizes.append(int(part))
        except ValueError:
            raise SystemExit(f"Invalid size: {part!r}")

    if not in_path.is_file():
        raise SystemExit(f"Input PNG not found: {in_path}")

    try:
        from PIL import Image
    except Exception as exc:  # pragma: no cover
        raise SystemExit(
            "Pillow is required. Install with: pip install pillow\n"
            f"Underlying error: {exc}"
        )

    img = Image.open(in_path)
    if img.mode not in ("RGBA", "RGB"):
        img = img.convert("RGBA")
    else:
        img = img.convert("RGBA")

    # For .ico, provide multiple sizes.
    ico_sizes = [(s, s) for s in sizes if s > 0]
    if not ico_sizes:
        raise SystemExit("No valid sizes specified")

    img.save(out_path, format="ICO", sizes=ico_sizes)
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
